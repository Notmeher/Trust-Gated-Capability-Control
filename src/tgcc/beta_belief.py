"""Beta-belief per-layer trust with forgetting factor and asymmetric penalty.

Implements Eq. (1) and Proposition 1 from the paper.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BetaBelief:
    """Per-layer Beta posterior with forgetting.

    Pseudo-count update (Eq. 1):
        a <- gamma * a + s
        b <- gamma * b + omega * (1 - s)

    Trust is the posterior mean T = a / (a + b).
    """

    a: float = 1.0
    b: float = 1.0
    gamma: float = 0.985
    omega: float = 3.0

    def update(self, signal: float) -> float:
        s = max(0.0, min(1.0, float(signal)))
        self.a = self.gamma * self.a + s
        self.b = self.gamma * self.b + self.omega * (1.0 - s)
        return self.trust

    @property
    def trust(self) -> float:
        denom = self.a + self.b
        return self.a / denom if denom > 0 else 0.0

    @property
    def effective_sample_count(self) -> float:
        return self.a + self.b

    @staticmethod
    def fixed_point(rho: float, omega: float = 3.0) -> float:
        """Closed-form fixed point T* = rho / (rho + omega*(1-rho)) (Eq. 2)."""
        rho = max(0.0, min(1.0, float(rho)))
        return rho / (rho + omega * (1.0 - rho)) if (rho + omega * (1.0 - rho)) > 0 else 0.0

    def prewarm(self, rho: float, effective_count: float) -> None:
        """Seed the belief with a prior of effective size ``effective_count`` at fixed point rho.

        Used for offline pre-warming (mitigation for L2/W5 warmup FPR).
        """
        t_star = self.fixed_point(rho, self.omega)
        n = max(1.0, float(effective_count))
        self.a = t_star * n
        self.b = (1.0 - t_star) * n
