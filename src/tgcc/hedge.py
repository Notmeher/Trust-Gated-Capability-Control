"""Failure-grounded adaptive weighting (Hedge / multiplicative weights).

Implements Equations (9)-(10) and Lemma 3.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class HedgeWeights:
    """Exponentially weighted layer-loss estimator + soft-max weights."""

    n_layers: int
    lam: float = 0.5     # EWMA decay lambda in [0,1]
    eta: float = 0.5     # Hedge learning rate
    r_hat: np.ndarray = field(default_factory=lambda: np.zeros(0))

    def __post_init__(self) -> None:
        if self.r_hat.size == 0:
            self.r_hat = np.zeros(self.n_layers, dtype=float)

    def update(self, layer_losses: np.ndarray) -> np.ndarray:
        """Update loss estimates and return the new weights (Eq. 9 & 10)."""
        q = np.asarray(layer_losses, dtype=float).clip(0.0, 1.0)
        if q.shape[0] != self.n_layers:
            raise ValueError(f"expected {self.n_layers} losses, got {q.shape[0]}")
        self.r_hat = (1.0 - self.lam) * self.r_hat + self.lam * q
        # Numerical-stable soft-max.
        z = self.eta * self.r_hat
        z = z - z.max()
        w = np.exp(z)
        w = w / w.sum()
        return w

    @property
    def weights(self) -> np.ndarray:
        z = self.eta * self.r_hat
        z = z - z.max()
        w = np.exp(z)
        return w / w.sum()

    def reset(self) -> None:
        self.r_hat[:] = 0.0
