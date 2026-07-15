"""DynaTrust-lite (Li et al. 2026).

The full DynaTrust maintains a per-pair dynamic trust graph; we abstract it
as a *scalar* trust that reacts strongly to the minimum recent signal (the
"weakest observation") but is still a single number, so it is blind to
per-layer failures hidden behind healthy layers.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tgcc.baselines.base import BaselineDecision


@dataclass
class DynaTrustLite:
    name: str = "dynatrust_lite"
    theta: float = 0.55
    lam: float = 0.3
    _trust: float = 0.7

    def observe(self, signals: np.ndarray) -> BaselineDecision:
        s = np.asarray(signals, dtype=float)
        # Emphasise the current weakest signal, mixed with the mean.
        current = 0.5 * float(s.min()) + 0.5 * float(s.mean())
        self._trust = (1.0 - self.lam) * self._trust + self.lam * current
        return BaselineDecision(grant=self._trust >= self.theta, trust=self._trust, debug={"scalar": current})

    def reset(self) -> None:
        self._trust = 0.7

    def prewarm(self, initial_trust: float = 0.75) -> None:
        self._trust = float(initial_trust)
