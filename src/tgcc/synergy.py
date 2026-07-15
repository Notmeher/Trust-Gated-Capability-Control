"""Cross-layer synergy operator (Eq. 3, Definition 2)."""
from __future__ import annotations

import numpy as np

# Default coupling matrix from Appendix B (Eq. 15).
# Rows are dependent layers, columns are prerequisite layers.
# Ordering: (0) epistemic, (1) behavioral, (2) role, (3) social, (4) institutional.
DEFAULT_COUPLING: np.ndarray = np.array(
    [
        [0.00, 0.00, 0.00, 0.00, 0.00],
        [0.70, 0.00, 0.00, 0.00, 0.00],
        [0.45, 0.65, 0.00, 0.00, 0.00],
        [0.35, 0.40, 0.60, 0.00, 0.00],
        [0.30, 0.30, 0.35, 0.55, 0.00],
    ],
    dtype=float,
)


def synergy_operator(trusts: np.ndarray, coupling: np.ndarray) -> np.ndarray:
    """Effective per-layer trust:

    T~_l = T_l * prod_{k<l} (1 - C_lk * (1 - T_k))            (Eq. 3)

    Accepts a general lower-triangular coupling matrix (not necessarily
    strictly hierarchical), which is why we allow arbitrary lower-triangular C.
    """
    trusts = np.asarray(trusts, dtype=float).clip(0.0, 1.0)
    C = np.asarray(coupling, dtype=float).clip(0.0, 1.0)
    L = trusts.shape[0]
    if C.shape != (L, L):
        raise ValueError(f"coupling shape {C.shape} does not match L={L}")
    # Enforce lower-triangular by construction (upper entries ignored).
    C_lower = np.tril(C, k=-1)
    effective = np.empty(L, dtype=float)
    for ell in range(L):
        prod = 1.0
        for k in range(ell):
            prod *= 1.0 - C_lower[ell, k] * (1.0 - trusts[k])
        effective[ell] = trusts[ell] * prod
    return effective


def cascade_bound(delta: float, kappa: float) -> float:
    """Proposition 3: if a universal prerequisite trust <= delta, composite <= kappa*delta."""
    return float(kappa * delta)
