"""AgentGuard-lite (Koohestani 2025).

The published AgentGuard is a runtime verifier that gates each action based on
a monitor that inspects the *current* turn (not history).  We approximate it
with a per-turn threshold on the epistemic signal alone.  The controller has
no memory and therefore cannot compensate for early false positives.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tgcc.baselines.base import BaselineDecision


@dataclass
class AgentGuardLite:
    name: str = "agentguard_lite"
    theta: float = 0.55

    def observe(self, signals: np.ndarray) -> BaselineDecision:
        s = float(signals[0])  # epistemic
        return BaselineDecision(grant=s >= self.theta, trust=s, debug={"epistemic_now": s})

    def reset(self) -> None:
        pass
