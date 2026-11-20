"""TGCC-R: the revised method used throughout the IEEE revision.

* Epistemic check on a calibration window chosen from the honest pilot alone (``select_window``): the smallest
  W in ``WINDOWS`` whose pilot 2.5% tail of the epistemic signal is at least ``MARGIN`` (= honest windowed
  calibration error below 0.4 even in its worst windows), so honest agents stay clearly separated from the ~0
  signal of a confidently wrong agent. Noisy domains get a longer window, reliable critics a shorter one.
* A per-turn prerequisite conjunct on every layer (Definition 3 with req(c) = all layers), plus the composite.
* Thresholds by conformal risk control (CRC): base thresholds are Algorithm 2 (Bonferroni over the K conjuncts)
  on a reference pool. A nested one-parameter family u in [0, 2] loosens them in two stages: for u in [1, 2]
  the stochastic conjuncts (composite, epistemic) are scaled by u - 1 while the rule-based layer conjuncts keep
  their base value; for u in [0, 1] the stochastic ones are 0 and the rule-based ones are scaled by u. The
  largest u with (m * risk + 1)/(m + 1) <= delta on m honest calibration sessions guarantees
  E[per-step honest FPR] <= delta for sessions exchangeable with the calibration sessions.

``calibrate_pilot`` applies CRC to an experiment's single honest pilot: its first half is the reference pool
and its second half is cut into short sessions (so the reference family is fixed before calibration).
"""
from __future__ import annotations

import numpy as np

from tgcc.nextphase.gates import Gate, TGCCParams, calibrate, grants

NAME = "TGCC-R"
WINDOWS = (4, 8, 12, 16, 24)
MARGIN = 0.2
WINDOW = 16          # used only where no pilot is available to select from
DELTA = 0.10
STOCHASTIC = ("composite", "epistemic", "trust")


def gate(name: str = NAME, **overrides) -> Gate:
    return Gate(name, "tgcc", TGCCParams(prereq_all=True, **overrides))


def base_thresholds(gate_: Gate, pool: np.ndarray) -> dict:
    ps = gate_.stats(pool)
    return calibrate(ps, q=0.05 / len(ps), delta=0.05 / len(ps))


def qualifying_windows(pilot_epistemic: dict[int, np.ndarray], margin: float = MARGIN, q: float = 0.025) -> list[int]:
    """Windows whose honest pilot epistemic signal has its q-quantile >= margin. If none qualifies, the honest agent
    is itself too often confidently wrong for the epistemic layer to separate it from a sleeper: TGCC-R still gates
    the other layers, but reports before deployment that sleeper detection is not supported for this agent."""
    return [W for W in sorted(pilot_epistemic)
            if np.asarray(pilot_epistemic[W], float).size and np.quantile(pilot_epistemic[W], q) >= margin]


def select_window(pilot_epistemic: dict[int, np.ndarray], margin: float = MARGIN, q: float = 0.025) -> int:
    """Smallest window whose honest pilot epistemic signal has its q-quantile >= margin (pilot-only rule)."""
    for W in sorted(pilot_epistemic):
        x = np.asarray(pilot_epistemic[W], float)
        if x.size and np.quantile(x, q) >= margin:
            return W
    return max(pilot_epistemic)


def _family(base: dict, u: float) -> dict:
    if u >= 1.0:
        return {k: ((u - 1.0) * v if k in STOCHASTIC else v) for k, v in base.items()}
    return {k: (0.0 if k in STOCHASTIC else u * v) for k, v in base.items()}


def crc_thresholds(gate_: Gate, sessions: list[np.ndarray], pool: np.ndarray, delta: float = DELTA) -> dict | None:
    m = len(sessions)
    if m == 0 or 1.0 / (m + 1) > delta:
        return None
    base = base_thresholds(gate_, pool)
    S = [gate_.stats(s) for s in sessions if len(s)]
    best = _family(base, 0.0)
    for u in np.linspace(0.0, 2.0, 401):
        th = _family(base, u)
        risk = np.mean([np.mean(~grants(x, th)) for x in S])
        if (m * risk + 1.0) / (m + 1) <= delta:
            best = th
        else:
            break
    return best


def calibrate_pilot(gate_: Gate, pilot: np.ndarray, delta: float = DELTA, session_len: int = 2) -> dict:
    """CRC on a single pilot: first half = reference pool, second half = sessions of ``session_len`` steps."""
    half = len(pilot) // 2
    pool, rest = pilot[:half], pilot[half:]
    sessions = [rest[i:i + session_len] for i in range(0, len(rest) - session_len + 1, session_len)]
    th = crc_thresholds(gate_, sessions, pool, delta)
    if th is None:  # too few sessions for this delta: fall back to the base (Algorithm 2) thresholds
        th = base_thresholds(gate_, pool)
    return th


def mode(window: int):
    """Signal settings of a TGCC-R run: the given epistemic window, and empty outputs are not observations."""
    from tgcc.nextphase.streams import signal_mode

    return signal_mode(window, True)


def choose_window(build_pilot) -> int:
    """``build_pilot()`` returns the honest pilot signals under the current settings; returns the selected W."""
    pil = {}
    for W in WINDOWS:
        with mode(W):
            pil[W] = build_pilot()[:, 0]
    return select_window(pil)
