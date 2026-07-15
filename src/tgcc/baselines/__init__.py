"""Head-to-head baselines for W3."""

from tgcc.baselines.base import BaselineController, BaselineDecision
from tgcc.baselines.naive import NaiveBehavioral
from tgcc.baselines.eigentrust import EigenTrustLite
from tgcc.baselines.dynatrust import DynaTrustLite
from tgcc.baselines.agentguard import AgentGuardLite
from tgcc.baselines.constitutional import ConstitutionalLite

__all__ = [
    "BaselineController",
    "BaselineDecision",
    "NaiveBehavioral",
    "EigenTrustLite",
    "DynaTrustLite",
    "AgentGuardLite",
    "ConstitutionalLite",
]
