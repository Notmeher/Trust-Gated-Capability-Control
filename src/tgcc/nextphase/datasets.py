"""Public benchmark loaders (TriviaQA, HumanEval) via the HF datasets-server JSON API.

The JSON rows API needs no ``datasets``/``pyarrow`` install and works through
the corporate proxy. Downloads are cached under ``nextphase/_data/``.
"""
from __future__ import annotations

import json
import re
import string
import urllib.request
from pathlib import Path

from tgcc.nextphase.io import data_root

_ROWS = "https://datasets-server.huggingface.co/rows?dataset={ds}&config={cfg}&split={split}&offset={off}&length={n}"


def _fetch_rows(ds: str, cfg: str, split: str, total: int, page: int = 100) -> list[dict]:
    rows: list[dict] = []
    off = 0
    while off < total:
        n = min(page, total - off)
        url = _ROWS.format(ds=ds, cfg=cfg, split=split, off=off, n=n)
        with urllib.request.urlopen(url, timeout=120) as r:
            blob = json.loads(r.read())
        got = [x["row"] for x in blob["rows"]]
        if not got:
            break
        rows.extend(got)
        off += len(got)
    return rows


# ---------------------------------------------------------------- TriviaQA
def load_triviaqa(n_raw: int = 1200) -> list[dict]:
    """First ``n_raw`` rows of TriviaQA rc.nocontext/validation, filtered to short answers.

    Returns items ``{id, question, answers, keywords, domain}`` compatible with
    the legacy QA format; ``answers`` holds all (normalized) aliases.
    """
    path = data_root() / f"triviaqa_rc_nocontext_val_{n_raw}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raw = _fetch_rows("mandarjoshi/trivia_qa", "rc.nocontext", "validation", n_raw)
    items = []
    for r in raw:
        q = r["question"].strip()
        a = r["answer"]
        aliases = sorted({*a.get("normalized_aliases", []), a.get("normalized_value", "")} - {""})
        if not aliases or len(q) > 220 or len(a.get("value", "")) > 40:
            continue
        items.append({
            "id": r["question_id"],
            "question": q,
            "answers": aliases,
            "value": a.get("value", ""),
            "keywords": [],
            "domain": "trivia",
        })
    path.write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
    return items


_ARTICLES = re.compile(r"\b(a|an|the)\b")
_PUNCT = str.maketrans({c: " " for c in string.punctuation})


def normalize(s: str) -> str:
    s = (s or "").lower().translate(_PUNCT)
    s = _ARTICLES.sub(" ", s)
    return " ".join(s.split())


def tqa_match(candidate: str, aliases: list[str]) -> bool:
    """TriviaQA-style match: normalized exact match, or an alias appearing as a
    whole-word span inside the candidate (handles "Ross Bagdasarian (David Seville)")."""
    c = normalize(candidate)
    if not c:
        return False
    padded = f" {c} "
    for al in aliases:
        a = normalize(al)
        if not a:
            continue
        if c == a or f" {a} " in padded:
            return True
    return False


# --------------------------------------------------------------- HumanEval
def load_humaneval() -> list[dict]:
    path = data_root() / "humaneval.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    rows = _fetch_rows("openai/openai_humaneval", "openai_humaneval", "test", 164)
    path.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return rows


def dataset_path(name: str) -> Path:
    return data_root() / name
