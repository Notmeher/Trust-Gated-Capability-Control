"""W12: Revocation-then-recovery experiment.

The paper describes a "recovery trigger" but never measures it.  Here we
simulate an agent that (i) begins honest, (ii) is compromised at step 60,
(iii) is revoked by TGCC, and then (iv) is **restored** to honest behaviour at
step 200.  We count the steps between restoration and re-authorization
(recovery latency) and compare it to the theoretical Beta-belief recovery
time constant.
"""
from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.controller import GrantSpec, TGCCController
from tgcc.reporting import figure_path, write_readme, write_results

EXPERIMENT = "w12_recovery"


def _episode(seed: int, gamma: float, omega: float) -> dict:
    rng = np.random.default_rng(seed)
    honest = np.array([0.92, 0.88, 0.82, 0.78, 0.90])
    sleeper = np.array([0.30, 0.88, 0.82, 0.78, 0.90])
    phases = [("honest_pre", 0, 60, honest),
              ("sleeper", 60, 200, sleeper),
              ("honest_post", 200, 400, honest)]
    ctrl = TGCCController(gamma=gamma, omega=omega)
    ctrl.prewarm([0.90] * 5, effective_count=40.0)
    spec = GrantSpec("high_risk", theta=0.40, prereq_layers=(0,), theta_layer=(0.25,))
    trace = {"composites": [], "grants": [], "phase": []}
    for name, s, e, rho in phases:
        for t in range(s, e):
            signals = (rng.random(5) < rho).astype(float)
            st = ctrl.step(signals.tolist())
            trace["composites"].append(st.composite)
            trace["grants"].append(ctrl.grant(st, spec))
            trace["phase"].append(name)
    return trace


def _measure(trace: dict) -> dict:
    phases = np.array(trace["phase"])
    grants = np.array(trace["grants"])
    # revocation latency: first denial after compromise (step 60)
    compromise_idx = np.where(phases == "sleeper")[0]
    revocation_lat = None
    for i, idx in enumerate(compromise_idx):
        if not grants[idx]:
            revocation_lat = i
            break
    # recovery latency: first grant after restoration (step 200)
    recovery_idx = np.where(phases == "honest_post")[0]
    recovery_lat = None
    for i, idx in enumerate(recovery_idx):
        if grants[idx]:
            recovery_lat = i
            break
    return {"revocation_latency": revocation_lat, "recovery_latency": recovery_lat}


def _plot(payload: dict) -> str:
    trace = payload["trace"]
    comps = np.asarray(trace["composites"])
    grants = np.asarray(trace["grants"], dtype=bool)
    phases = np.asarray(trace["phase"])
    fig, ax = plt.subplots(2, 1, figsize=(10.5, 5), sharex=True)
    ax[0].plot(comps, color="black", alpha=0.85, label="composite $\\Phi_p$")
    ax[0].axhline(0.40, color="red", linestyle="--", label="$\\theta$")
    # phase bands
    idx = np.where(phases == "sleeper")[0]
    if idx.size:
        ax[0].axvspan(idx[0], idx[-1], color="#a63a3a", alpha=0.15, label="compromise")
    idx2 = np.where(phases == "honest_post")[0]
    if idx2.size:
        ax[0].axvspan(idx2[0], idx2[-1], color="#2a7f3f", alpha=0.15, label="restored")
    ax[0].set_ylabel("composite")
    ax[0].set_ylim(0, 1.05)
    ax[0].legend(fontsize=8, loc="lower left")
    ax[1].step(np.arange(grants.size), grants.astype(int), color="#1f4e79", where="post")
    ax[1].set_ylabel("grant")
    ax[1].set_xlabel("interaction step $t$")
    ax[1].set_ylim(-0.1, 1.1)
    fig.tight_layout()
    out = figure_path(EXPERIMENT, "recovery.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out.name)


def _readme(payload: dict) -> str:
    m = payload["metrics"]
    tau = payload["config"]["time_constant"]
    return f"""# W12 - Revocation then recovery

## Weakness addressed
**W12**: The paper's "recovery trigger" is described but never measured.
Can a revoked agent regain the capability after honest behaviour resumes?

## Method
An agent goes through three phases:

| Phase | Steps | Reliability |
|---|---|---|
| honest_pre | 0-59 | rho=0.92 |
| sleeper | 60-199 | epistemic rho=0.30, others honest |
| honest_post | 200-399 | rho=0.92 restored |

TGCC is pre-warmed and uses default parameters (`gamma={payload['config']['gamma']}`,
`omega={payload['config']['omega']}`, `p=-6`, `theta=0.40`).

## Results
* **Revocation latency**: `{m['revocation_latency']}` steps after compromise onset.
* **Recovery latency**:  `{m['recovery_latency']}` steps after restoration.
* **Time constant**: `1 / (1 - gamma) = {tau:.1f}` steps -- theoretical bound
  on how long it takes stale evidence to decay.

## Reading
The recovery latency is bounded by the effective sample count ceiling: it
takes ~`1 / (1 - gamma)` steps of consistent honest evidence for the Beta
posterior to overwrite the sleeper's failure record.  If the recovery
latency is much larger than the time constant, TGCC is *punishing* an
already-restored agent -- a bug.  If it is much smaller, TGCC is
insufficiently conservative.  The observed value should sit close to
`tau = {tau:.1f}`.

## Figures
![Recovery](figures/recovery.png)

## Files
- `results.json` - trace + metrics.
- `figures/recovery.png` - composite + grant during all three phases.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gamma", type=float, default=0.985)
    parser.add_argument("--omega", type=float, default=3.0)
    parser.add_argument("--seed", type=int, default=21)
    args = parser.parse_args()
    trace = _episode(args.seed, args.gamma, args.omega)
    metrics = _measure(trace)
    payload = {
        "config": {"seed": args.seed, "gamma": args.gamma, "omega": args.omega,
                   "time_constant": 1.0 / (1.0 - args.gamma)},
        "trace": trace,
        "metrics": metrics,
    }
    _plot(payload)
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload))
    print(f"[w12] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
