"""Uniform gate interface for TGCC, its ablations and all baselines.

Every gate maps a signal matrix (T, 5) to a dict of named per-step statistics.
A capability is granted at step t iff stat_k(t) >= theta_k for every k.
Thresholds come from an honest pilot (Algorithm 2) so every controller is
calibrated by the SAME procedure on the SAME pilot (fair comparison).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Optional

import numpy as np

from tgcc.beta_belief import BetaBelief
from tgcc.controller import GrantSpec, TGCCController
from tgcc.synergy import DEFAULT_COUPLING

PREWARM_RHO = 0.90
PREWARM_N = 40.0


@dataclass(frozen=True)
class TGCCParams:
    p: float = -6.0
    gamma: float = 0.985
    omega: float = 3.0
    eta: float = 0.5
    lam: float = 0.5
    coupling_scale: float = 1.0
    coupling: Optional[tuple] = None   # full matrix override (tuple of tuples)
    prereq: bool = True                # epistemic prerequisite conjunct
    prereq_raw: bool = True            # False = Beta-smoothed prerequisite (TGCC-Smoothed ablation)
    composite: bool = True             # composite conjunct
    prewarm: bool = True

    def matrix(self) -> np.ndarray:
        C = np.array(self.coupling, dtype=float) if self.coupling is not None else DEFAULT_COUPLING
        return np.clip(C * self.coupling_scale, 0.0, 1.0)


def _beta_trusts(signals: np.ndarray, gamma: float, omega: float, prewarm: bool) -> np.ndarray:
    bs = [BetaBelief(gamma=gamma, omega=omega) for _ in range(signals.shape[1])]
    if prewarm:
        for b in bs:
            b.prewarm(PREWARM_RHO, PREWARM_N)
    out = np.zeros_like(signals, dtype=float)
    for t in range(signals.shape[0]):
        out[t] = [b.update(s) for b, s in zip(bs, signals[t])]
    return out


@dataclass
class Gate:
    name: str
    kind: str
    params: TGCCParams = field(default_factory=TGCCParams)

    def stats(self, signals: np.ndarray) -> dict[str, np.ndarray]:
        P = self.params
        if self.kind == "tgcc":
            ctrl = TGCCController(p=P.p, gamma=P.gamma, omega=P.omega, eta=P.eta,
                                  lam=P.lam, coupling=P.matrix())
            if P.prewarm:
                ctrl.prewarm([PREWARM_RHO] * 5, PREWARM_N)
            comp, epi = [], []
            for s in signals:
                st = ctrl.step(list(s))
                comp.append(st.composite)
                epi.append(st.effective[0])
            out = {}
            if P.composite:
                out["composite"] = np.array(comp)
            if P.prereq:
                out["epistemic"] = signals[:, 0].astype(float) if P.prereq_raw else np.array(epi)
            return out
        if self.kind in ("epi_beta", "min_beta", "mean_beta", "naive"):
            T = _beta_trusts(signals, P.gamma, P.omega, P.prewarm)
            return {
                "epi_beta": {"trust": T[:, 0]},
                "min_beta": {"trust": T.min(axis=1)},
                "mean_beta": {"trust": T.mean(axis=1)},
                "naive": {"trust": T[:, 1]},
            }[self.kind]
        if self.kind == "agentguard":
            return {"trust": signals[:, 0].astype(float)}
        if self.kind == "eigentrust":
            x, out = 0.75, []
            for s in signals:
                x = P.gamma * x + (1 - P.gamma) * float(np.mean(s))
                out.append(x)
            return {"trust": np.array(out)}
        if self.kind == "dynatrust":
            x, out = 0.75, []
            for s in signals:
                x = 0.7 * x + 0.3 * (0.5 * float(np.min(s)) + 0.5 * float(np.mean(s)))
                out.append(x)
            return {"trust": np.array(out)}
        raise ValueError(self.kind)


def standard_gates(params: TGCCParams = TGCCParams()) -> list[Gate]:
    return [
        Gate("TGCC", "tgcc", params),
        Gate("TGCC-Smoothed", "tgcc", replace(params, prereq_raw=False)),
        Gate("TGCC-NoSyn", "tgcc", replace(params, coupling_scale=0.0)),
        Gate("TGCC-CompositeOnly", "tgcc", replace(params, prereq=False)),
        Gate("TGCC-NoSyn-CompositeOnly", "tgcc", replace(params, coupling_scale=0.0, prereq=False)),
        Gate("Epistemic-only (Beta)", "epi_beta", params),
        Gate("Strict-min (Beta)", "min_beta", params),
        Gate("Mean (Constitutional-lite)", "mean_beta", params),
        Gate("Naive behavioural", "naive", params),
        Gate("AgentGuard-lite", "agentguard", params),
        Gate("EigenTrust-lite", "eigentrust", params),
        Gate("DynaTrust-lite", "dynatrust", params),
    ]


# ------------------------------------------------------------- calibration
def calibrate(pilot_stats: dict[str, np.ndarray], method: str = "quantile", eps: float = 0.05,
              q: float = 0.05, burn_in: int = 0, delta: float = 0.05) -> dict[str, float]:
    """Algorithm 2 (threshold calibration on an honest pilot).

    method="quantile" : theta = q-quantile(pilot after burn-in) - eps
    method="min"      : theta = min(pilot after burn-in) - eps (min-of-pilot ablation)
    If fewer than 1-delta of pilot steps are admitted, eps is widened.
    """
    th = {}
    for k, v in pilot_stats.items():
        x = np.asarray(v[burn_in:] if len(v) > burn_in else v, dtype=float)
        base = float(np.min(x)) if method == "min" else float(np.quantile(x, q))
        e = eps
        while True:
            theta = max(0.0, base - e)
            if np.mean(x >= theta) >= 1 - delta or theta == 0.0:
                break
            e += 0.01
        th[k] = theta
    return th


def grants(stats: dict[str, np.ndarray], thetas: dict[str, float], tau: float = 1.0) -> np.ndarray:
    g = None
    for k, v in stats.items():
        ok = v >= tau * thetas[k]
        g = ok if g is None else (g & ok)
    return g


def score(stats: dict[str, np.ndarray], thetas: dict[str, float]) -> np.ndarray:
    """grant(tau) == score >= tau, for ROC sweeps over a common multiplier."""
    return np.min(np.vstack([v / max(thetas[k], 1e-9) for k, v in stats.items()]), axis=0)


def metrics(g: np.ndarray, compromise: int) -> dict:
    g = np.asarray(g, dtype=bool)
    tail, head = g[compromise:], g[:compromise]
    denied = np.where(~tail)[0]
    return {
        "oer": float(tail.mean()) if tail.size else 0.0,
        "latency": float(denied[0]) if denied.size else float("inf"),
        "fpr": float((~head).mean()) if head.size else 0.0,
    }


def which_conjunct(stats: dict[str, np.ndarray], thetas: dict[str, float]) -> list[str]:
    """Per-step reason for denial: '', 'composite', 'epistemic', or 'both'."""
    keys = list(stats)
    out = []
    for t in range(len(next(iter(stats.values())))):
        bad = [k for k in keys if stats[k][t] < thetas[k]]
        out.append("" if not bad else ("both" if len(bad) > 1 else bad[0]))
    return out
