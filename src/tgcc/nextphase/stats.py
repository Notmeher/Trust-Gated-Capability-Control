"""Small statistics helpers: episode-level CIs and Wilson intervals."""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np


def mean_ci(values: Sequence[float], n_boot: int = 4000, seed: int = 0,
            alpha: float = 0.05) -> dict:
    """Mean with a percentile-bootstrap CI over independent units (episodes)."""
    x = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if x.size == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    if x.size == 1:
        return {"mean": float(x[0]), "lo": float(x[0]), "hi": float(x[0]), "n": 1}
    rng = np.random.default_rng(seed)
    boots = x[rng.integers(0, x.size, size=(n_boot, x.size))].mean(axis=1)
    return {
        "mean": float(x.mean()),
        "lo": float(np.quantile(boots, alpha / 2)),
        "hi": float(np.quantile(boots, 1 - alpha / 2)),
        "n": int(x.size),
    }


def wilson(k: int, n: int, z: float = 1.96) -> dict:
    if n == 0:
        return {"p": float("nan"), "lo": float("nan"), "hi": float("nan"), "k": k, "n": n}
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return {"p": p, "lo": max(0.0, centre - half), "hi": min(1.0, centre + half), "k": k, "n": n}


def fmt_ci(d: dict, digits: int = 2) -> str:
    if d.get("n", 0) == 0 or not np.isfinite(d["mean"]):
        return "n/a"
    return f"{d['mean']:.{digits}f} [{d['lo']:.{digits}f}, {d['hi']:.{digits}f}]"


def fmt_wilson(d: dict, digits: int = 2) -> str:
    if d["n"] == 0:
        return "n/a"
    return f"{d['p']:.{digits}f} [{d['lo']:.{digits}f}, {d['hi']:.{digits}f}] ({d['k']}/{d['n']})"
