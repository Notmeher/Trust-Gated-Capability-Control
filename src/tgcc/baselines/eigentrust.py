"""EigenTrust-lite (Kamvar et al. 2003) adapted for a single-agent stream.

The full EigenTrust algorithm is peer-to-peer; here we use the *scalar*
aggregation it induces: a single reputation value combining all layers as an
unweighted mean, with the same forgetting factor.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tgcc.baselines.base import BaselineDecision


@dataclass
class EigenTrustLite:
    name: str = "eigentrust_lite"
    theta: float = 0.55
    gamma: float = 0.985
    _trust: float = 0.5

    def observe(self, signals: np.ndarray) -> BaselineDecision:
        # Unweighted mean of the five signals.
        s = float(np.mean(np.asarray(signals, dtype=float)))
        # Exponential moving average.
        self._trust = self.gamma * self._trust + (1.0 - self.gamma) * s
        return BaselineDecision(grant=self._trust >= self.theta, trust=self._trust, debug={"mean_signal": s})

    def reset(self) -> None:
        self._trust = 0.5

    def prewarm(self, initial_trust: float = 0.75) -> None:
        self._trust = float(initial_trust)
