"""TGCC controller (Algorithm 1 in the paper).

Composes Beta beliefs, the synergy operator, adaptive weights, the power-mean
composite, and the grant rule (Definition 3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

from tgcc.beta_belief import BetaBelief
from tgcc.composite import power_mean_composite, slack_factor
from tgcc.hedge import HedgeWeights
from tgcc.synergy import DEFAULT_COUPLING, synergy_operator

# Canonical layer indices used throughout.
LAYER_NAMES = ("epistemic", "behavioral", "role", "social", "institutional")


@dataclass
class LayerState:
    trusts: np.ndarray
    effective: np.ndarray
    composite: float
    weights: np.ndarray
    kappa: float


@dataclass
class GrantSpec:
    """Per-capability policy.

    Attributes:
        name:          human-readable capability name (e.g. "write_to_ehr").
        theta:         composite threshold theta_c.
        prereq_layers: indices of prerequisite layers.
        theta_layer:   per-layer thresholds theta_{c,l} (same length as prereq_layers).
    """

    name: str
    theta: float
    prereq_layers: tuple[int, ...] = ()
    theta_layer: tuple[float, ...] = ()


@dataclass
class TGCCController:
    n_layers: int = 5
    p: float = -6.0
    gamma: float = 0.985
    omega: float = 3.0
    lam: float = 0.5
    eta: float = 0.5
    coupling: np.ndarray = field(default_factory=lambda: DEFAULT_COUPLING.copy())
    beliefs: list[BetaBelief] = field(default_factory=list)
    hedge: Optional[HedgeWeights] = None

    def __post_init__(self) -> None:
        if not self.beliefs:
            self.beliefs = [
                BetaBelief(gamma=self.gamma, omega=self.omega) for _ in range(self.n_layers)
            ]
        if self.hedge is None:
            self.hedge = HedgeWeights(n_layers=self.n_layers, lam=self.lam, eta=self.eta)
        if self.coupling.shape != (self.n_layers, self.n_layers):
            raise ValueError(
                f"coupling shape {self.coupling.shape} != ({self.n_layers}, {self.n_layers})"
            )

    # ------------------------------------------------------------------ step
    def step(
        self,
        signals: Sequence[float],
        layer_losses: Optional[Sequence[float]] = None,
    ) -> LayerState:
        """One controller step. Returns the resulting :class:`LayerState`."""
        if len(signals) != self.n_layers:
            raise ValueError(f"expected {self.n_layers} signals, got {len(signals)}")
        # 1) update Beta beliefs
        trusts = np.array([b.update(s) for b, s in zip(self.beliefs, signals)])
        # 2) synergy operator
        effective = synergy_operator(trusts, self.coupling)
        # 3) adaptive weights (Hedge) - default loss = 1 - trust for each layer
        losses = (
            np.asarray(layer_losses, dtype=float)
            if layer_losses is not None
            else 1.0 - trusts
        )
        weights = self.hedge.update(losses)
        # 4) composite
        phi = power_mean_composite(effective, weights, p=self.p)
        kappa = slack_factor(weights, p=self.p)
        return LayerState(
            trusts=trusts, effective=effective, composite=phi, weights=weights, kappa=kappa
        )

    # ------------------------------------------------------------------ grant
    @staticmethod
    def grant(state: LayerState, spec: GrantSpec) -> bool:
        """Definition 3 - trust-gated grant rule."""
        if state.composite < spec.theta:
            return False
        for k, ell in enumerate(spec.prereq_layers):
            if state.effective[ell] < spec.theta_layer[k]:
                return False
        return True

    # ------------------------------------------------------------------ pre-warm
    def prewarm(
        self,
        rhos: Sequence[float],
        effective_count: float = 40.0,
    ) -> None:
        """Seed all layers with priors of `effective_count` at the given reliabilities.

        Mitigation for warmup false-positives (L2, W5-related).
        """
        for belief, rho in zip(self.beliefs, rhos):
            belief.prewarm(rho, effective_count)
