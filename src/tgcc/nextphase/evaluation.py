"""Shared evaluation loop: calibrate on the pilot, evaluate on independent episodes."""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from tgcc.nextphase.gates import Gate, calibrate, grants, metrics, score
from tgcc.nextphase.stats import mean_ci
from tgcc.nextphase.streams import Episode


def run_gate(gate: Gate, episodes: Sequence[Episode], pilot: np.ndarray,
             method: str = "quantile", eps: float = 0.05, burn_in: int = 0,
             q: float = 0.05, thetas: dict | None = None) -> dict:
    th = thetas if thetas is not None else calibrate(
        gate.stats(pilot), method=method, eps=eps, burn_in=burn_in, q=q)
    per = []
    for ep in episodes:
        g = grants(gate.stats(ep.signals), th)
        per.append({**metrics(g, ep.compromise), "grants": g.astype(int).tolist()})
    return {"gate": gate.name, "thetas": th, "per_episode": per, "summary": summarize(per)}


def summarize(per: Sequence[dict]) -> dict:
    lat = [m["latency"] for m in per]
    finite = [x for x in lat if math.isfinite(x)]
    return {
        "oer": mean_ci([m["oer"] for m in per]),
        "fpr": mean_ci([m["fpr"] for m in per]),
        "latency": mean_ci(finite),
        "revoked_frac": float(len(finite) / max(len(lat), 1)),
        "n_episodes": len(per),
    }


def roc(gate: Gate, episodes: Sequence[Episode], pilot: np.ndarray,
        taus: np.ndarray | None = None) -> dict:
    """Pooled OER-vs-FPR curve over a common threshold multiplier tau."""
    th = calibrate(gate.stats(pilot), method="min", eps=0.0, burn_in=0)
    hon, sl = [], []
    for ep in episodes:
        s = score(gate.stats(ep.signals), th)
        hon.append(s[:ep.compromise])
        sl.append(s[ep.compromise:])
    hon_a, sl_a = np.concatenate(hon), np.concatenate(sl)
    if taus is None:
        taus = np.unique(np.concatenate([hon_a, sl_a, [0.0, np.inf]]))
    fpr = np.array([(hon_a < t).mean() for t in taus])
    oer = np.array([(sl_a >= t).mean() for t in taus])
    order = np.argsort(fpr)
    f, o = fpr[order], oer[order]
    # Area under the (FPR, 1-OER) curve = probability-style detection AUC.
    auc = float(np.trapezoid(1 - o, f)) if hasattr(np, "trapezoid") else float(np.trapz(1 - o, f))
    return {"fpr": f.tolist(), "oer": o.tolist(), "auc": auc,
            "hon_scores": hon_a.tolist(), "sl_scores": sl_a.tolist()}


def oer_at_fpr(curve: dict, target: float) -> float:
    """Lowest pooled OER achievable with pooled honest FPR <= target."""
    f, o = np.asarray(curve["fpr"]), np.asarray(curve["oer"])
    ok = f <= target + 1e-12
    return float(o[ok].min()) if ok.any() else 1.0
