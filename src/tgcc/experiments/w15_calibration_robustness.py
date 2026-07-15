"""W15: Threshold-calibration robustness.

Empirical curve for Theorem 5.  We simulate honest pilots of varying length
`N_pilot`, then measure how far the calibrated theta drifts from the true
honest fixed-point composite.  The theorem says the RMS error should decay
as O(1 / sqrt(N_pilot)); we plot that curve and its confidence band.
"""
from __future__ import annotations

import argparse
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.controller import GrantSpec, TGCCController
from tgcc.reporting import figure_path, write_readme, write_results

EXPERIMENT = "w15_calibration_robustness"


def _true_theta(honest_rho: np.ndarray, gamma: float, n_ref: int = 5000) -> float:
    """Ground-truth honest-phase composite: burn-in + a long observation."""
    rng = np.random.default_rng(0)
    ctrl = TGCCController(gamma=gamma)
    ctrl.prewarm([0.90] * 5, effective_count=40.0)
    spec = GrantSpec("dummy", theta=0.0, prereq_layers=(0,), theta_layer=(0.0,))
    comps = []
    for _ in range(n_ref):
        signals = (rng.random(5) < honest_rho).astype(float)
        st = ctrl.step(signals.tolist())
        comps.append(st.composite)
    return float(np.mean(comps[500:]))


def _pilot_estimate(honest_rho: np.ndarray, gamma: float, n_pilot: int,
                    burn_in: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    ctrl = TGCCController(gamma=gamma)
    ctrl.prewarm([0.90] * 5, effective_count=40.0)
    spec = GrantSpec("dummy", theta=0.0, prereq_layers=(0,), theta_layer=(0.0,))
    comps = []
    for _ in range(n_pilot):
        signals = (rng.random(5) < honest_rho).astype(float)
        st = ctrl.step(signals.tolist())
        comps.append(st.composite)
    after_burn = comps[burn_in:]
    return float(min(after_burn)) if after_burn else float(min(comps))


def _sweep(honest_rho: np.ndarray, gamma: float, pilots: list[int],
           n_seeds: int) -> tuple[float, list[dict[str, Any]]]:
    true_theta = _true_theta(honest_rho, gamma)
    burn_in = int(np.ceil(1.0 / (1.0 - gamma)))
    rows = []
    for n in pilots:
        errs = []
        for s in range(n_seeds):
            est = _pilot_estimate(honest_rho, gamma, n, burn_in, seed=1000 + s)
            errs.append(true_theta - est)
        arr = np.array(errs)
        rows.append({
            "n_pilot": int(n),
            "burn_in": int(burn_in),
            "mean_error": float(arr.mean()),
            "std_error": float(arr.std()),
            "rms_error": float(np.sqrt((arr ** 2).mean())),
        })
    return true_theta, rows


def _plot(payload: dict) -> str:
    rows = payload["sweep"]
    n = np.array([r["n_pilot"] for r in rows])
    rms = np.array([r["rms_error"] for r in rows])
    # Fit 1/sqrt(n) trend for reference
    ref = rms[0] * np.sqrt(n[0]) / np.sqrt(n)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.loglog(n, rms, marker="o", color="#a63a3a", label="empirical RMS")
    ax.loglog(n, ref, linestyle="--", color="black",
              label=r"$1/\sqrt{N_{\rm pilot}}$ trend")
    ax.set_xlabel(r"$N_{\rm pilot}$")
    ax.set_ylabel("RMS error in calibrated $\\theta$")
    ax.set_title("W15: calibration RMS error vs. pilot length")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = figure_path(EXPERIMENT, "calibration_rms.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out.name)


def _readme(payload: dict) -> str:
    rows = payload["sweep"]
    tbl = "\n".join(
        f"| {r['n_pilot']} | {r['burn_in']} | {r['mean_error']:.4f} | "
        f"{r['std_error']:.4f} | {r['rms_error']:.4f} |"
        for r in rows
    )
    return f"""# W15 - Calibration-robustness curve

## Weakness addressed
**W15**: Theorem 5 gives a sample-complexity bound for Algorithm 2, but no
experiment measures the actual convergence rate of the calibrated threshold.

## Method
1. Estimate a reference "true" honest composite `theta_true` by running the
   controller for 5000 steps.
2. For each `N_pilot in {payload['config']['pilots']}`, run
   `n_seeds = {payload['config']['n_seeds']}` independent pilots.  For each,
   drop the first `burn_in = ceil(1/(1-gamma))` steps and take the *minimum*
   composite over the remaining pilot (as Algorithm 2 prescribes).
3. Report the mean error `theta_true - theta_hat`, its standard deviation,
   and the RMS error.

## Results

Reference `theta_true = {payload['true_theta']:.4f}` (5000-step average).

| N_pilot | Burn-in | Mean error | Std error | RMS error |
|---|---|---|---|---|
{tbl}

## Reading
Theorem 5 predicts an `O(1/sqrt(N_pilot))` decay of the empirical minimum
around its expectation.  The log-log plot below should show a slope close
to -0.5; a shallower slope indicates residual bias from the finite
burn-in, and a steeper slope indicates variance-reducing dependence
between the pilot samples (from the forgetting factor).

## Figures
![Calibration robustness](figures/calibration_rms.png)

## Files
- `results.json` - per-pilot mean / std / RMS error.
- `figures/calibration_rms.png` - log-log RMS-error curve.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-seeds", type=int, default=15)
    parser.add_argument("--gamma", type=float, default=0.985)
    args = parser.parse_args()
    honest_rho = np.array([0.92, 0.88, 0.82, 0.78, 0.90])
    pilots = [10, 20, 40, 80, 160, 320, 640]
    true_theta, sweep = _sweep(honest_rho, args.gamma, pilots, args.n_seeds)
    payload = {
        "config": {"n_seeds": args.n_seeds, "gamma": args.gamma,
                   "pilots": pilots,
                   "honest_rho": honest_rho.tolist()},
        "true_theta": true_theta,
        "sweep": sweep,
    }
    _plot(payload)
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload))
    print(f"[w15] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
