"""Metrics used across experiments.

* Over-Exposure Rate (OER):  fraction of *post-compromise* steps that granted
  the high-risk capability.
* Revocation Latency:        steps from compromise onset to first denial.
* False-Positive Rate (FPR): fraction of *honest-phase* steps wrongly denied.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np


def over_exposure_rate(grants: Sequence[bool], compromise_step: int) -> float:
    g = np.asarray(list(grants), dtype=bool)
    tail = g[compromise_step:]
    if tail.size == 0:
        return 0.0
    return float(tail.mean())


def revocation_latency(grants: Sequence[bool], compromise_step: int) -> float:
    """Steps after the compromise before the first denial (``inf`` if none)."""
    g = np.asarray(list(grants), dtype=bool)
    tail = g[compromise_step:]
    if tail.size == 0:
        return float("inf")
    idx = np.argmax(~tail) if (~tail).any() else -1
    if idx == 0 and tail[0]:  # argmax returns 0 when all True
        return float("inf")
    if not (~tail).any():
        return float("inf")
    return float(idx)


def honest_false_positive_rate(grants: Sequence[bool], compromise_step: int) -> float:
    g = np.asarray(list(grants), dtype=bool)
    head = g[:compromise_step]
    if head.size == 0:
        return 0.0
    return float((~head).mean())


def summary(
    grants: Sequence[bool],
    compromise_step: int,
) -> dict:
    return {
        "over_exposure_rate": over_exposure_rate(grants, compromise_step),
        "revocation_latency": revocation_latency(grants, compromise_step),
        "false_positive_rate": honest_false_positive_rate(grants, compromise_step),
        "grants": [bool(x) for x in grants],
    }
