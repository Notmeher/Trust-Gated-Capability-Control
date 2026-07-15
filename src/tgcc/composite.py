"""Generalized power-mean composite trust (Eq. 5, Theorem 1)."""
from __future__ import annotations

import numpy as np


def power_mean_composite(
    effective_trusts: np.ndarray,
    weights: np.ndarray,
    p: float = -6.0,
    eps: float = 1e-9,
) -> float:
    """Weighted power mean of order p<0 (Eq. 5).

    Phi_p = ( sum_l alpha_l * T~_l^p )^(1/p)

    We clip trusts away from 0 to avoid singularities for p<0.  A trust of 0
    with p<0 yields Phi = 0 (weakest-link limit), matching the theorem.
    """
    t = np.asarray(effective_trusts, dtype=float).clip(eps, 1.0)
    w = np.asarray(weights, dtype=float)
    w = w / max(w.sum(), eps)
    if p == 0:
        return float(np.exp(np.sum(w * np.log(t))))
    if np.any(t <= eps) and p < 0:
        return 0.0
    return float(np.sum(w * t ** p) ** (1.0 / p))


def slack_factor(weights: np.ndarray, p: float = -6.0, eps: float = 1e-9) -> float:
    """Kappa = (min_l alpha_l)^(1/p) (Eq. 7)."""
    w = np.asarray(weights, dtype=float)
    w = w / max(w.sum(), eps)
    return float(max(w.min(), eps) ** (1.0 / p))
