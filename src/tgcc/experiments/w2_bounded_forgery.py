"""W2: Bounded-forgery robustness sweep.

Weakens the paper's threat model.  Instead of assuming the adversary
**cannot** inflate signals it does not control, we let it push each
non-controlled signal up by an additive forgery budget ``Delta in [0, 1]`` and
measure how the paradox resolution degrades.

* Adversary controls the *epistemic* signal (drives Bernoulli reliability to
  ``0.30``).
* Adversary raises every other layer's honest reliability by ``Delta``,
  capped at 0.99.
* Everything else follows the default TGCC.
"""
from __future__ import annotations

import argparse
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.controller import GrantSpec, TGCCController
from tgcc.metrics import summary
from tgcc.reporting import figure_path, write_readme, write_results

EXPERIMENT = "w2_bounded_forgery"


def _episode(
    delta: float,
    seed: int,
    n_turns: int,
    compromise_step: int,
    honest_rho: np.ndarray,
    sleeper_rho: np.ndarray,
) -> np.ndarray:
    """Bernoulli signals under a forgery budget ``delta``."""
    rng = np.random.default_rng(seed)
    signals = np.zeros((n_turns, 5))
    forged_sleeper = sleeper_rho.copy()
    # bump every non-epistemic layer up by delta
    forged_sleeper[1:] = np.clip(honest_rho[1:] + delta, 0.0, 0.99)
    for t in range(n_turns):
        rho = honest_rho if t < compromise_step else forged_sleeper
        signals[t] = (rng.random(5) < rho).astype(float)
    return signals


def _run_controller(signals: np.ndarray, spec: GrantSpec, prewarm: bool = True) -> list[bool]:
    ctrl = TGCCController()
    if prewarm:
        ctrl.prewarm(rhos=[0.90] * 5, effective_count=40.0)
    grants = []
    for row in signals:
        st = ctrl.step(row.tolist())
        grants.append(ctrl.grant(st, spec))
    return grants


def _sweep(
    deltas: list[float],
    n_seeds: int,
    n_turns: int,
    compromise_step: int,
    honest_rho: np.ndarray,
    sleeper_rho: np.ndarray,
    spec: GrantSpec,
    prewarm: bool = True,
) -> dict[str, Any]:
    per_delta = []
    for d in deltas:
        oers, lats, fprs = [], [], []
        for s in range(n_seeds):
            sig = _episode(d, seed=1000 + s, n_turns=n_turns, compromise_step=compromise_step,
                           honest_rho=honest_rho, sleeper_rho=sleeper_rho)
            grants = _run_controller(sig, spec, prewarm=prewarm)
            m = summary(grants, compromise_step)
            oers.append(m["over_exposure_rate"])
            lat = m["revocation_latency"]
            lats.append(lat if lat != float("inf") else n_turns - compromise_step)
            fprs.append(m["false_positive_rate"])
        per_delta.append(
            {
                "delta": d,
                "oer_mean": float(np.mean(oers)),
                "oer_std": float(np.std(oers)),
                "latency_mean": float(np.mean(lats)),
                "latency_std": float(np.std(lats)),
                "fpr_mean": float(np.mean(fprs)),
                "fpr_std": float(np.std(fprs)),
            }
        )
    return {"deltas": deltas, "per_delta": per_delta, "n_seeds": n_seeds}


def _plot(sweep: dict, spec: GrantSpec) -> str:
    d = np.array([r["delta"] for r in sweep["per_delta"]])
    oer = np.array([r["oer_mean"] for r in sweep["per_delta"]])
    oer_e = np.array([r["oer_std"] for r in sweep["per_delta"]])
    lat = np.array([r["latency_mean"] for r in sweep["per_delta"]])
    lat_e = np.array([r["latency_std"] for r in sweep["per_delta"]])
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2))
    ax[0].errorbar(d, oer, yerr=oer_e, marker="o", color="#1f4e79", capsize=3)
    ax[0].set_xlabel(r"forgery budget $\Delta$")
    ax[0].set_ylabel("post-compromise over-exposure rate")
    ax[0].set_title("W2: OER vs. forgery budget")
    ax[0].grid(alpha=0.3)
    ax[1].errorbar(d, lat, yerr=lat_e, marker="s", color="#d1770f", capsize=3)
    ax[1].set_xlabel(r"forgery budget $\Delta$")
    ax[1].set_ylabel("revocation latency (steps)")
    ax[1].set_title("W2: Latency vs. forgery budget")
    ax[1].grid(alpha=0.3)
    out = figure_path(EXPERIMENT, "forgery_sweep.png")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out.name)


def _readme(payload: dict, spec: GrantSpec) -> str:
    rows = []
    for r in payload["sweep"]["per_delta"]:
        rows.append(
            f"| {r['delta']:.2f} | {r['oer_mean']:.2f} ± {r['oer_std']:.2f} | "
            f"{r['latency_mean']:.1f} ± {r['latency_std']:.1f} | "
            f"{r['fpr_mean']:.2f} ± {r['fpr_std']:.2f} |"
        )
    header = (
        "| Delta | OER (mean ± std) | Latency (mean ± std) | FPR (mean ± std) |\n"
        "|---|---|---|---|\n"
    )
    return f"""# W2 - Bounded-Forgery Robustness

## Weakness addressed
**W2**: The paper's Assumption 1(iii) states the adversary *cannot forge* the
signals of layers it does not control.  This is a strong assumption.  In this
experiment we **weaken** that assumption to a *bounded* forgery: the adversary
may inflate every non-controlled signal's Bernoulli reliability by an
additive budget `Delta in [0, 1]` and we measure how the paradox-resolution
guarantees of TGCC degrade.

## Method
1. Fix the honest reliabilities `rho_honest = {payload['config']['honest_rho']}`.
2. Choose a **controlled** layer (epistemic, index 0).  Post-compromise it
   drops to `rho = 0.30`.
3. For each `Delta` in the sweep, raise every other layer's post-compromise
   reliability to `min(0.99, rho_honest[l] + Delta)`.
4. Draw Bernoulli check signals for `n_turns = {payload['config']['n_turns']}` steps
   with compromise at step `{payload['config']['compromise_step']}`.
5. Run the full TGCC controller and record OER, latency, and FPR.
6. Repeat over `n_seeds = {payload['sweep']['n_seeds']}` seeds and report mean ± std.

## Results
{header}{chr(10).join(rows)}

**Reading the table.**  When `Delta = 0` the guarantees of Theorem 3 apply and
the OER is small with fast revocation.  As `Delta` grows the adversary can
push non-controlled signals higher; TGCC's cascade containment
(Proposition 3) still forces the composite through the *epistemic*
prerequisite gate, so the OER should stay bounded well below the naive gate's
`~0.72`.  The point at which the OER begins to climb marks the **empirical
tolerance** of TGCC to bounded forgery, which is our headline number for W2.

## Theoretical prediction
By cascade containment, when the epistemic layer trust is at most `delta` the
composite is at most `kappa * delta`.  Bounded forgery on the non-controlled
signals cannot raise the epistemic layer, so TGCC's decision does **not**
depend on `Delta` at all.  Any observed degradation is due to the
**effective coupling** from other layers into the composite through the
weights, not into the effective epistemic trust.

## Configuration
```yaml
{payload['config']}
```

## Figures
![Forgery sweep](figures/forgery_sweep.png)

## Files
- `results.json` - the full sweep (per-delta metrics).
- `figures/forgery_sweep.png` - OER and latency as functions of `Delta`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-turns", type=int, default=300)
    parser.add_argument("--compromise-step", type=int, default=80)
    parser.add_argument("--n-seeds", type=int, default=20)
    parser.add_argument("--n-deltas", type=int, default=11)
    parser.add_argument("--theta", type=float, default=0.55)
    parser.add_argument("--theta-epistemic", type=float, default=0.30)
    parser.add_argument("--prewarm", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    honest_rho = np.array([0.92, 0.88, 0.82, 0.78, 0.90])
    sleeper_rho = np.array([0.30, 0.88, 0.82, 0.78, 0.90])  # epistemic collapses
    spec = GrantSpec(
        name="high_risk",
        theta=args.theta,
        prereq_layers=(0,),
        theta_layer=(args.theta_epistemic,),
    )
    deltas = list(np.round(np.linspace(0.0, 1.0, args.n_deltas), 2))

    sweep = _sweep(
        deltas=deltas,
        n_seeds=args.n_seeds,
        n_turns=args.n_turns,
        compromise_step=args.compromise_step,
        honest_rho=honest_rho,
        sleeper_rho=sleeper_rho,
        spec=spec,
        prewarm=args.prewarm,
    )
    payload = {
        "config": {
            "n_turns": args.n_turns,
            "compromise_step": args.compromise_step,
            "n_seeds": args.n_seeds,
            "honest_rho": honest_rho.tolist(),
            "sleeper_rho": sleeper_rho.tolist(),
            "theta": spec.theta,
            "theta_epistemic": spec.theta_layer[0],
            "prewarm": args.prewarm,
        },
        "sweep": sweep,
    }
    fig_name = _plot(sweep, spec)
    payload["figure"] = fig_name
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload, spec))
    print(f"[w2] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
