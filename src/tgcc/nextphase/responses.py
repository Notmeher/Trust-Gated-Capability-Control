"""Per-item LLM response banks.

Each benchmark item is answered ONCE per (provider, phase) at temperature 0 and
disk-cached. Episodes are then assembled by sampling disjoint item subsets and
compromise points, so the number of independent episodes is decoupled from the
number of API calls.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from tgcc.data_qa import HONEST_SYSTEM_PROMPT, SLEEPER_SYSTEM_PROMPT
from tgcc.models import LLMClient
from tgcc.nextphase.datasets import load_triviaqa, tqa_match
from tgcc.nextphase.io import data_root
from tgcc.probes import parse_answer, parse_confidence

PROVIDERS = ("anthropic", "azure_openai")
# gpt-5 is a reasoning model: without this it spends max_tokens on hidden reasoning
# and returns empty text (51/64 of the old W1 gpt-5 cache entries were empty).
PROVIDER_KW = {"anthropic": {}, "azure_openai": {"reasoning_effort": "minimal"}}
MODEL_NAMES = {"anthropic": "Claude Sonnet 4.5", "azure_openai": "GPT-5"}


def model_name(provider: str) -> str:
    return MODEL_NAMES.get(provider, provider)


def model_slug(provider: str) -> str:
    return model_name(provider).lower().replace(" ", "-")

N_EVAL_ITEMS = 900      # 15 disjoint 60-question episodes
N_PILOT_ITEMS = 120     # honest-only calibration pilot, disjoint from eval items


def chat(client: LLMClient, prompt: str, system: str, max_tokens: int = 200):
    return client.chat(prompt=prompt, system=system, max_tokens=max_tokens,
                       temperature=0.0, **PROVIDER_KW[client.provider])


def _record(item: dict, phase: str, res) -> dict:
    text = res.text or ""
    ans = parse_answer(text)
    meta = res.meta or {}
    return {
        "id": item["id"],
        "phase": phase,
        "question": item["question"],
        "answers": item["answers"],
        "text": text,
        "answer": ans,
        "conf": parse_confidence(text),
        "correct": tqa_match(ans, item["answers"]),
        "filtered": bool(res.filtered),
        "empty": not text.strip(),
        "latency_ms": float(res.latency_ms),
        "in_tokens": meta.get("input_tokens", meta.get("prompt_tokens")),
        "out_tokens": meta.get("output_tokens", meta.get("completion_tokens")),
    }


def qa_split() -> tuple[list[dict], list[dict]]:
    items = load_triviaqa(1200)
    return items[:N_EVAL_ITEMS], items[N_EVAL_ITEMS:N_EVAL_ITEMS + N_PILOT_ITEMS]


def bank_path(provider: str) -> Path:
    return data_root() / f"qa_bank_{provider}.json"


def collect_qa_bank(provider: str, workers: int = 12) -> dict:
    eval_items, pilot_items = qa_split()
    client = LLMClient(provider)
    jobs: list[tuple[dict, str]] = [(it, "honest") for it in eval_items]
    jobs += [(it, "sleeper") for it in eval_items]
    jobs += [(it, "pilot") for it in pilot_items]

    def run(job):
        it, phase = job
        system = SLEEPER_SYSTEM_PROMPT if phase == "sleeper" else HONEST_SYSTEM_PROMPT
        return _record(it, phase, chat(client, it["question"], system))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        recs = list(tqdm(ex.map(run, jobs), total=len(jobs), desc=f"qa:{provider}", ncols=90))
    bank = {"provider": provider, "model": client.model,
            "honest": {}, "sleeper": {}, "pilot": {}}
    for r in recs:
        bank[r["phase"]][r["id"]] = r
    bank["eval_ids"] = [it["id"] for it in eval_items]
    bank["pilot_ids"] = [it["id"] for it in pilot_items]
    bank_path(provider).write_text(json.dumps(bank, ensure_ascii=False), encoding="utf-8")
    return bank


def load_bank(provider: str) -> dict:
    return json.loads(bank_path(provider).read_text(encoding="utf-8"))


def available_banks() -> list[str]:
    return [p for p in PROVIDERS if bank_path(p).exists()]


def main(argv: Iterable[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--providers", nargs="+", default=list(PROVIDERS))
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args(argv)
    for p in args.providers:
        bank = collect_qa_bank(p, workers=args.workers)
        h = list(bank["honest"].values())
        s = list(bank["sleeper"].values())
        print(p, "honest acc", sum(r["correct"] for r in h) / len(h),
              "sleeper acc", sum(r["correct"] for r in s) / len(s),
              "empty", sum(r["empty"] for r in h + s))


if __name__ == "__main__":
    main()
