"""Environment configuration - Anthropic + Azure OpenAI clients.

Reads the .env at repo root.  Never logs secrets.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env", override=False)


@dataclass(frozen=True)
class AnthropicCfg:
    api_key: str
    model: str = "claude-sonnet-4-5"


@dataclass(frozen=True)
class AzureOpenAICfg:
    api_key: str
    endpoint: str
    api_version: str
    deployment: str
    model: str


def _require(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"missing required env var {name!r}")
    return v.strip('"').strip("'")


def anthropic_cfg() -> AnthropicCfg:
    return AnthropicCfg(
        api_key=_require("ANTHROPIC_API_KEY"),
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5").strip('"').strip("'"),
    )


def azure_openai_cfg() -> AzureOpenAICfg:
    return AzureOpenAICfg(
        api_key=_require("AZURE_OPENAI_API_KEY"),
        endpoint=_require("AZURE_OPENAI_ENDPOINT"),
        api_version=_require("AZURE_OPENAI_API_VERSION"),
        deployment=_require("AZURE_OPENAI_DEPLOYMENT"),
        model=os.getenv("AZURE_OPENAI_MODEL", "gpt-5").strip('"').strip("'"),
    )


def repo_root() -> Path:
    return _ROOT


def results_dir(sub: str = "") -> Path:
    root = _ROOT / "results"
    if sub:
        root = root / sub
    root.mkdir(parents=True, exist_ok=True)
    return root


def cache_dir(sub: str = "") -> Path:
    root = _ROOT / "cache"
    if sub:
        root = root / sub
    root.mkdir(parents=True, exist_ok=True)
    return root


def final_dir(experiment: str = "") -> Path:
    """Root of the deliverables tree ``<repo>/final/<experiment>/``.

    Each experiment writes ``results.json``, ``README.md`` and ``figures/*.png``
    inside its own subdirectory.
    """
    root = _ROOT / "final"
    if experiment:
        root = root / experiment
    root.mkdir(parents=True, exist_ok=True)
    (root / "figures").mkdir(parents=True, exist_ok=True) if experiment else None
    return root


def data_dir() -> Path:
    root = _ROOT / "data"
    root.mkdir(parents=True, exist_ok=True)
    return root
