"""Trust-Gated Capability Control (TGCC).

Weakness-mitigation experiments (W1-W5) for the paper
"Trust-Gated Capability Control: An Operational Framework for Breaking the
Trust-Vulnerability Paradox in Multi-Agent LLM Systems".
"""

from tgcc.controller import TGCCController, LayerState
from tgcc.beta_belief import BetaBelief
from tgcc.synergy import synergy_operator, DEFAULT_COUPLING
from tgcc.composite import power_mean_composite
from tgcc.hedge import HedgeWeights

__all__ = [
    "TGCCController",
    "LayerState",
    "BetaBelief",
    "synergy_operator",
    "DEFAULT_COUPLING",
    "power_mean_composite",
    "HedgeWeights",
]
