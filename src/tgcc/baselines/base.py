"""Common interface for the W3 head-to-head baselines.

Each baseline is a lightweight scalar-trust controller that observes the same
per-layer signals TGCC observes and returns a grant decision for a single
high-risk capability.  The comparison is *runtime-only* - baselines see
identical inputs; only their aggregation and decision rules differ.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


@dataclass
class BaselineDecision:
    grant: bool
    trust: float
    debug: dict = field(default_factory=dict)


class BaselineController(Protocol):
    name: str

    def observe(self, signals: np.ndarray) -> BaselineDecision: ...
    def reset(self) -> None: ...
