"""Naive behavioural baseline (the paper's Naive condition)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from tgcc.baselines.base import BaselineDecision
from tgcc.beta_belief import BetaBelief


@dataclass
class NaiveBehavioral:
    """Grant iff behavioural-layer trust is above threshold.

    This is the vulnerable controller the paper's Theorem 3 defeats.
    """

    name: str = "naive_behavioral"
    theta: float = 0.55
    gamma: float = 0.985
    omega: float = 3.0
    _belief: BetaBelief = field(default_factory=lambda: BetaBelief())

    def __post_init__(self) -> None:
        self._belief = BetaBelief(gamma=self.gamma, omega=self.omega)

    def observe(self, signals: np.ndarray) -> BaselineDecision:
        # signals = [epistemic, behavioural, role, social, institutional]
        t = self._belief.update(float(signals[1]))
        return BaselineDecision(grant=t >= self.theta, trust=t, debug={"behavioural": t})

    def reset(self) -> None:
        self._belief = BetaBelief(gamma=self.gamma, omega=self.omega)

    def prewarm(self, rho: float = 0.90, effective_count: float = 40.0) -> None:
        self._belief.prewarm(rho, effective_count)
