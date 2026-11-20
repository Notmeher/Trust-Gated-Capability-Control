"""Unified LLM client wrapping Anthropic Claude and Azure OpenAI (gpt-5).

Both providers expose a single `chat()` method returning a `ChatResult`.
Responses are disk-cached under ``cache/llm/`` to keep experiments cheap
and reproducible; the cache key includes model id, prompt, and system.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import anthropic
import httpx
import openai
from anthropic import Anthropic
from openai import AzureOpenAI, BadRequestError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import os
import threading

from tgcc.config import (
    AnthropicCfg,
    AzureOpenAICfg,
    anthropic_cfg,
    anthropic_haiku_cfg,
    azure_openai_cfg,
    budget_usd,
    cache_dir,
)

# Open-weight models. They are generated on Kaggle (TGCC_LOCAL_BACKEND=transformers) and are
# read from the disk cache everywhere else, so they never cost API money.
OPEN_MODELS: dict[str, str] = {
    "qwen3-4b": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen3-8b": "Qwen/Qwen3-8B",
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
}

# USD per million tokens (input, output). Reasoning tokens are billed as output.
PRICES: dict[str, tuple[float, float]] = {
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "gpt-5": (1.25, 10.0),
}


class BudgetExceeded(RuntimeError):
    pass


class CacheMiss(RuntimeError):
    pass


class SpendLedger:
    """Process-safe enough for our use: one experiment process at a time, many threads."""

    _lock = threading.Lock()

    def __init__(self) -> None:
        self.path = cache_dir("llm") / "_spend_ledger.json"

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {"spent_usd": 0.0, "calls": 0, "by_model": {}}

    def reserve(self, model: str, est_in: int, max_out: int) -> None:
        pin, pout = PRICES.get(model, (15.0, 75.0))
        worst = (est_in * pin + max_out * pout) / 1e6
        with self._lock:
            led = self._load()
            if led["spent_usd"] + worst > budget_usd():
                raise BudgetExceeded(
                    f"API budget cap reached: spent ${led['spent_usd']:.2f} of ${budget_usd():.2f} "
                    f"(set TGCC_BUDGET_USD to raise it)")

    def record(self, model: str, tok_in: Optional[int], tok_out: Optional[int]) -> None:
        pin, pout = PRICES.get(model, (15.0, 75.0))
        cost = ((tok_in or 0) * pin + (tok_out or 0) * pout) / 1e6
        with self._lock:
            led = self._load()
            led["spent_usd"] += cost
            led["calls"] += 1
            m = led["by_model"].setdefault(model, {"calls": 0, "usd": 0.0})
            m["calls"] += 1
            m["usd"] += cost
            self.path.write_text(json.dumps(led, indent=1), encoding="utf-8")


LEDGER = SpendLedger()


@dataclass
class ChatResult:
    text: str
    model: str
    provider: str
    latency_ms: float
    cache_hit: bool = False
    filtered: bool = False
    meta: dict[str, Any] = field(default_factory=dict)


class _DiskCache:
    def __init__(self, name: str) -> None:
        self.root = cache_dir(f"llm/{name}")

    def _key(self, payload: dict) -> Path:
        blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        h = hashlib.sha256(blob).hexdigest()
        return self.root / f"{h}.json"

    def get(self, payload: dict) -> Optional[dict]:
        p = self._key(payload)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def set(self, payload: dict, result: dict) -> None:
        p = self._key(payload)
        try:
            p.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


_RETRY = dict(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type((
        httpx.HTTPError, TimeoutError, ConnectionError,
        openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError,
        openai.InternalServerError,
        anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.APITimeoutError,
        anthropic.InternalServerError,
    )),
    reraise=True,
)


class LLMClient:
    """Provider-agnostic wrapper. Instantiate one per provider."""

    def __init__(self, provider: str) -> None:
        self.provider = provider
        self._cache = _DiskCache(provider)
        if provider in ("anthropic", "anthropic_haiku"):
            self.cfg: AnthropicCfg = anthropic_cfg() if provider == "anthropic" else anthropic_haiku_cfg()
            headers = ({"anthropic-workspace-id": self.cfg.workspace_id}
                       if self.cfg.workspace_id else None)
            self._anthropic = Anthropic(api_key=self.cfg.api_key, default_headers=headers)
            self.model = self.cfg.model
        elif provider == "azure_openai":
            self.cfg: AzureOpenAICfg = azure_openai_cfg()  # type: ignore[assignment]
            self._azure = AzureOpenAI(
                api_key=self.cfg.api_key,
                api_version=self.cfg.api_version,
                azure_endpoint=self.cfg.endpoint,
            )
            self.model = self.cfg.deployment
        elif provider in OPEN_MODELS:
            self.model = OPEN_MODELS[provider]
            self._engine = None
            if os.getenv("TGCC_LOCAL_BACKEND") == "transformers":
                from tgcc.nextphase.hf_backend import get_engine
                self._engine = get_engine(self.model)
        else:
            raise ValueError(f"unknown provider {provider!r}")

    # ------------------------------------------------------------------ chat
    def chat(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 400,
        temperature: Optional[float] = 0.0,
        use_cache: bool = True,
        reasoning_effort: Optional[str] = None,
    ) -> ChatResult:
        payload = {
            "provider": self.provider,
            "model": self.model,
            "system": system or "",
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        # Only keyed when set, so pre-existing cache entries keep their hashes.
        if reasoning_effort is not None and self.provider == "azure_openai":
            payload["reasoning_effort"] = reasoning_effort
        if use_cache:
            cached = self._cache.get(payload)
            if cached is not None:
                return ChatResult(
                    text=cached["text"],
                    model=cached["model"],
                    provider=self.provider,
                    latency_ms=cached.get("latency_ms", 0.0),
                    cache_hit=True,
                    filtered=bool(cached.get("filtered", False)),
                    meta=cached.get("meta", {}),
                )
        t0 = time.perf_counter()
        filtered = False
        if self.provider in OPEN_MODELS:
            if self._engine is None:
                raise CacheMiss(
                    f"{self.provider}: response not in cache/llm/{self.provider}. Open-weight models are "
                    "generated by the Kaggle notebook (nextphase/kaggle/); download its cache first.")
            text, meta = self._engine.generate(system or "", prompt, max_tokens, temperature)
        else:
            LEDGER.reserve(self.model, (len(prompt) + len(system or "")) // 3 + 16, max_tokens)
            try:
                if self.provider in ("anthropic", "anthropic_haiku"):
                    text, meta = self._call_anthropic(prompt, system, max_tokens, temperature)
                else:
                    text, meta = self._call_azure(prompt, system, max_tokens, temperature,
                                                  reasoning_effort)
            except (BadRequestError, anthropic.BadRequestError) as e:
                # Azure content filter (or other 400 issues): treat as an empty
                # refusal so downstream metrics degrade gracefully.
                filtered = True
                text = ""
                meta = {"error_status": 400,
                        "content_filter": "prompt" in str(e).lower() or "jailbreak" in str(e).lower(),
                        "error_message": str(e)[:400]}
            LEDGER.record(self.model, meta.get("input_tokens", meta.get("prompt_tokens")),
                          meta.get("output_tokens", meta.get("completion_tokens")))
        dt = (time.perf_counter() - t0) * 1000.0
        if use_cache:
            self._cache.set(payload, {"text": text, "model": self.model,
                                      "latency_ms": dt, "filtered": filtered,
                                      "meta": meta})
        return ChatResult(text=text, model=self.model, provider=self.provider,
                          latency_ms=dt, filtered=filtered, meta=meta)

    # ------------------------------------------------------- provider glue
    @retry(**_RETRY)
    def _call_anthropic(
        self, prompt: str, system: Optional[str], max_tokens: int, temperature: Optional[float]
    ) -> tuple[str, dict]:
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        if system:
            kwargs["system"] = system
        if temperature is not None:
            kwargs["temperature"] = float(temperature)
        resp = self._anthropic.messages.create(**kwargs)
        # Concatenate all text content blocks.
        parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        text = "".join(parts).strip()
        meta = {
            "input_tokens": getattr(resp.usage, "input_tokens", None),
            "output_tokens": getattr(resp.usage, "output_tokens", None),
            "stop_reason": resp.stop_reason,
        }
        return text, meta

    @retry(**_RETRY)
    def _call_azure(
        self, prompt: str, system: Optional[str], max_tokens: int, temperature: Optional[float],
        reasoning_effort: Optional[str] = None,
    ) -> tuple[str, dict]:
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        kwargs: dict[str, Any] = dict(
            model=self.model,
            messages=messages,
            max_completion_tokens=max_tokens,
        )
        if reasoning_effort is not None:
            kwargs["reasoning_effort"] = reasoning_effort
        # gpt-5 rejects `temperature` in some deployments; only send when non-default.
        if temperature is not None and abs(temperature - 1.0) > 1e-9:
            try:
                resp = self._azure.chat.completions.create(temperature=float(temperature), **kwargs)
            except Exception:
                resp = self._azure.chat.completions.create(**kwargs)
        else:
            resp = self._azure.chat.completions.create(**kwargs)
        text = (resp.choices[0].message.content or "").strip()
        details = getattr(resp.usage, "completion_tokens_details", None)
        meta = {
            "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
            "completion_tokens": getattr(resp.usage, "completion_tokens", None),
            "reasoning_tokens": getattr(details, "reasoning_tokens", None) if details else None,
            "finish_reason": resp.choices[0].finish_reason,
        }
        return text, meta


# ---------------------------------------------------------------- helpers
def make_client(provider: str) -> LLMClient:
    """Convenience factory."""
    return LLMClient(provider)


def available_providers() -> list[str]:
    """Return providers whose credentials are present in the environment."""
    import os

    out: list[str] = []
    if os.getenv("ANTHROPIC_API_KEY"):
        out.append("anthropic")
    if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
        out.append("azure_openai")
    return out
