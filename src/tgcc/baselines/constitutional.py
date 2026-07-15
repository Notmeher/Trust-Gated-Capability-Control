"""Constitutional-AI-lite (Bai et al. 2022).

The published Constitutional-AI uses self-critique at *training* time; at
runtime this manifests as an average of layer signals with no coupling and no
adaptive weights.  We give it the same forgetting factor as TGCC to keep the
comparison fair.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tgcc.baselines.base import BaselineDecision
from tgcc.beta_belief import BetaBelief


@dataclass
class ConstitutionalLite:
    name: str = "constitutional_lite"
    theta: float = 0.55
    gamma: float = 0.985
    omega: float = 3.0

    def __post_init__(self) -> None:
        self._beliefs = [BetaBelief(gamma=self.gamma, omega=self.omega) for _ in range(5)]

    def observe(self, signals: np.ndarray) -> BaselineDecision:
        trusts = np.array([b.update(float(s)) for b, s in zip(self._beliefs, signals)])
        trust = float(np.mean(trusts))  # arithmetic mean, no coupling
        return BaselineDecision(grant=trust >= self.theta, trust=trust, debug={"mean_trust": trust})

    def reset(self) -> None:
        self._beliefs = [BetaBelief(gamma=self.gamma, omega=self.omega) for _ in range(5)]

    def prewarm(self, rho: float = 0.90, effective_count: float = 40.0) -> None:
        for b in self._beliefs:
            b.prewarm(rho, effective_count)
