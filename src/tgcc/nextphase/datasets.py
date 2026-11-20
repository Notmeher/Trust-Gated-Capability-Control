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


def _get_json(url: str, attempts: int = 6) -> dict:
    import time
    import urllib.error

    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.loads(r.read())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if i == attempts - 1 or (code is not None and code < 500 and code != 429):
                raise
            time.sleep(2 ** i)
    raise RuntimeError("unreachable")


def _fetch_rows(ds: str, cfg: str, split: str, total: int, page: int = 100) -> list[dict]:
    rows: list[dict] = []
    off = 0
    while off < total:
        n = min(page, total - off)
        url = _ROWS.format(ds=ds, cfg=cfg, split=split, off=off, n=n)
        blob = _get_json(url)
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


# ---------------------------------------------------------------- MedMCQA
LETTERS = "ABCD"


def load_medmcqa(n_raw: int = 1200) -> list[dict]:
    """First ``n_raw`` rows of MedMCQA/validation: single-answer, non-dental (clinical) questions.

    Items carry ``options`` (A-D), the ``gold`` letter, and ``answers`` = aliases of the
    correct option (letter and text) so the shared QA tooling can use them.
    """
    path = data_root() / f"medmcqa_val_{n_raw}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raw = _fetch_rows("openlifescienceai/medmcqa", "default", "validation", n_raw)
    items = []
    for r in raw:
        opts = [str(r.get(k) or "").strip() for k in ("opa", "opb", "opc", "opd")]
        cop = r.get("cop")
        if r.get("choice_type") != "single" or not isinstance(cop, int) or not 0 <= cop < 4:
            continue
        if (r.get("subject_name") or "").strip().lower() == "dental":
            continue
        if any(not o for o in opts) or len({normalize(o) for o in opts}) < 4 or len(r["question"]) > 400:
            continue
        gold = LETTERS[cop]
        items.append({
            "id": r["id"],
            "question": r["question"].strip(),
            "options": dict(zip(LETTERS, opts)),
            "gold": gold,
            "answers": [gold, opts[cop]],
            "keywords": [],
            "domain": r.get("subject_name") or "medicine",
            "kind": "mcq",
        })
    path.write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
    return items


def mcq_prompt(item: dict) -> str:
    opts = "\n".join(f"{k}) {v}" for k, v in item["options"].items())
    # The format is restated here because on clinical MCQs some models otherwise reason at length and
    # never reach an Answer line within the token budget.
    return (f"{item['question']}\n{opts}\n"
            "Choose the single best option. Do not explain your reasoning. Reply in EXACTLY this two-line "
            "format and nothing else:\nAnswer: <letter>) <option text>\nConfidence: <decimal in [0,1]>")


_LETTER = re.compile(r"^\W*\(?([A-D])(?:\)|\.|:|\s|$)", re.I)


def mcq_choice(candidate: str, options: dict) -> str:
    """The option letter a free-text answer picks, or '' if it picks none or several."""
    c = (candidate or "").strip()
    m = _LETTER.match(c)
    if m:
        return m.group(1).upper()
    nc = normalize(c)
    if not nc:
        return ""
    hits = [k for k, v in options.items() if normalize(v) and (normalize(v) == nc or f" {normalize(v)} " in f" {nc} ")]
    return hits[0] if len(hits) == 1 else ""


def mcq_match(candidate: str, item: dict) -> bool:
    return mcq_choice(candidate, item["options"]) == item["gold"]


def dataset_path(name: str) -> Path:
    return data_root() / name
