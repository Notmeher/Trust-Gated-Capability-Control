"""Simulated signal streams shared by the simulation experiments.

Each layer emits a Bernoulli check with a per-step reliability; the epistemic
column is then turned into a rolling-window rate (like the real calibration probe).
"""
from __future__ import annotations

import numpy as np

from tgcc.nextphase.gates import Gate, calibrate
from tgcc.nextphase.streams import windowed_epistemic

HONEST = np.array([0.92, 0.88, 0.82, 0.78, 0.90])
SLEEPER = np.array([0.30, 0.92, 0.75, 0.72, 0.88])


def simulate(rho: np.ndarray, seed: int) -> np.ndarray:
    """rho: (T, 5) per-step reliabilities -> (T, 5) signals."""
    rng = np.random.default_rng(seed)
    return windowed_epistemic((rng.random(rho.shape) < rho).astype(float))


def schedule(n_turns: int, compromise: int, honest=HONEST, sleeper=SLEEPER) -> np.ndarray:
    rho = np.tile(np.asarray(honest, dtype=float), (n_turns, 1))
    rho[compromise:] = sleeper
    return rho


def honest_pilot(n_turns: int = 600, seed: int = 123_456) -> np.ndarray:
    return simulate(schedule(n_turns, n_turns), seed)


def sim_thetas(gate: Gate, pilot: np.ndarray | None = None) -> dict[str, float]:
    """Algorithm 2 on an honest simulated pilot (same defaults as the real-LLM runs)."""
    return calibrate(gate.stats(honest_pilot() if pilot is None else pilot))
