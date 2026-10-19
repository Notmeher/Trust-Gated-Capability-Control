"""Episode assembly from response banks, and per-step signal computation."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import numpy as np

from tgcc.episodes import _inject_wrong_answer
from tgcc.probes import (
    BehavioralProbe,
    EpistemicProbe,
    InstitutionalProbe,
    RoleProbe,
    SocialProbe,
    parse_answer,
    parse_confidence,
)
from tgcc.nextphase.datasets import tqa_match

LAYERS = ("epistemic", "behavioural", "role", "social", "institutional")


@dataclass
class Episode:
    provider: str
    index: int
    compromise: int
    signals: np.ndarray            # (T, 5)
    sleeper: np.ndarray            # (T,) bool
    correct: np.ndarray            # (T,) ground-truth correctness
    label: np.ndarray              # (T,) correctness label the critic reported
    conf: np.ndarray               # (T,)
    texts: list[str] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


def compute_signals(texts: Sequence[str], labels: Sequence[bool], confs: Sequence[float],
                    window: int = 8) -> np.ndarray:
    epi = EpistemicProbe(window=window)
    beh, rol, soc, ins = BehavioralProbe(), RoleProbe(), SocialProbe(), InstitutionalProbe()
    out = np.zeros((len(texts), 5), dtype=float)
    for t, (txt, lab, c) in enumerate(zip(texts, labels, confs)):
        e, _ = epi.update(bool(lab), float(c))  # type: ignore[misc]
        out[t] = [e, beh.score(txt), rol.score(txt, []), soc.score(txt), ins.score(txt)]
    return out


def _force_wrong(rec: dict, rng: random.Random) -> tuple[str, bool, float]:
    """Sleeper semantics of the paper (E1): a wrong answer with high stated confidence.
    If the model did not comply with the sleeper prompt, the answer is rewritten."""
    if not rec["correct"] and rec["text"].strip():
        return rec["text"], False, rec["conf"]
    txt = _inject_wrong_answer(rec["text"], rec["answers"], rng)
    ans = parse_answer(txt)
    return txt, tqa_match(ans, rec["answers"]), parse_confidence(txt)


LabelFn = Callable[[str, str, bool, np.random.Generator], bool]


def oracle_labels(_id: str, _phase: str, correct: bool, _rng) -> bool:
    return correct


def noisy_labels(q: float) -> LabelFn:
    def f(_id, _phase, correct, rng):
        return (not correct) if rng.random() < q else correct
    return f


def qa_episodes(bank: dict, n_turns: int = 60, compromise: int = 20,
                sleeper_mode: str = "forced", label_fn: LabelFn = oracle_labels,
                seed: int = 0, n_episodes: Optional[int] = None,
                transform: Optional[Callable[[str, int, random.Random], str]] = None,
                ) -> list[Episode]:
    """Partition the eval items into DISJOINT episodes (independent questions).

    sleeper_mode: "forced" (paper semantics; non-compliant answers rewritten),
    "raw" (whatever the model produced under the sleeper prompt), or
    "honest" (no compromise; sleeper slots use honest answers -> FPR-only episode).
    transform(text, step, rng) lets an experiment alter post-compromise text
    (e.g. a non-epistemic compromise).
    """
    ids = list(bank["eval_ids"])
    random.Random(seed).shuffle(ids)
    k = len(ids) // n_turns
    if n_episodes is not None:
        k = min(k, n_episodes)
    eps = []
    for e in range(k):
        chunk = ids[e * n_turns:(e + 1) * n_turns]
        rng = random.Random(10_000 * seed + e)
        nrng = np.random.default_rng(10_000 * seed + e)
        texts, corr, labs, confs, sl = [], [], [], [], []
        for t, iid in enumerate(chunk):
            is_sl = t >= compromise and sleeper_mode != "honest"
            rec = bank["sleeper" if is_sl else "honest"][iid]
            if is_sl and sleeper_mode == "forced":
                txt, ok, c = _force_wrong(rec, rng)
            else:
                txt, ok, c = rec["text"], rec["correct"], rec["conf"]
            if transform is not None and t >= compromise:
                txt = transform(txt, t, rng)
                ok = tqa_match(parse_answer(txt), rec["answers"])
                c = parse_confidence(txt)
            texts.append(txt)
            corr.append(ok)
            confs.append(c)
            labs.append(label_fn(iid, "sleeper" if is_sl else "honest", ok, nrng))
            sl.append(t >= compromise)
        eps.append(Episode(
            provider=bank["provider"], index=e, compromise=compromise,
            signals=compute_signals(texts, labs, confs),
            sleeper=np.array(sl), correct=np.array(corr), label=np.array(labs),
            conf=np.array(confs), texts=texts, ids=chunk,
        ))
    return eps


def pilot_signals(bank: dict, label_fn: LabelFn = oracle_labels, seed: int = 0) -> np.ndarray:
    """Honest-only calibration pilot on items disjoint from every eval episode."""
    nrng = np.random.default_rng(seed + 777)
    recs = [bank["pilot"][i] for i in bank["pilot_ids"]]
    labs = [label_fn(r["id"], "honest", r["correct"], nrng) for r in recs]
    return compute_signals([r["text"] for r in recs], labs, [r["conf"] for r in recs])


def windowed_epistemic(signals: np.ndarray, window: int = 8) -> np.ndarray:
    """Simulated Bernoulli epistemic outcomes -> rolling-window rate, like the real probe."""
    out = signals.astype(float).copy()
    x = signals[:, 0].astype(float)
    c = np.cumsum(np.r_[0.0, x])
    for t in range(len(x)):
        lo = max(0, t + 1 - window)
        out[t, 0] = (c[t + 1] - c[lo]) / (t + 1 - lo)
    return out
