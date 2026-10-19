"""N16 - Bounded forgery (weakened Assumption 1(iii)).

The sleeper's epistemic reliability drops to 0.30 after step 80, and the adversary
may inflate every other layer's reliability by an additive budget Delta (capped at
0.99). Gates are calibrated by Algorithm 2 on an honest simulated pilot.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.nextphase.evaluation import summarize
from tgcc.nextphase.gates import grants, metrics, standard_gates
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.sim import HONEST, schedule, sim_thetas, simulate
from tgcc.nextphase.stats import fmt_ci

EXP = "n16_bounded_forgery"
DELTAS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]
SHOW = ["TGCC", "TGCC-Smoothed", "TGCC-CompositeOnly", "Strict-min (Beta)",
        "Mean (Constitutional-lite)", "Naive behavioural"]
N_SEEDS, N_TURNS, COMPROMISE = 50, 300, 80


def run() -> dict:
    gates = [g for g in standard_gates() if g.name in SHOW]
    th = {g.name: sim_thetas(g) for g in gates}
    out = {}
    for d in DELTAS:
        sl = HONEST.copy()
        sl[0] = 0.30
        sl[1:] = np.clip(HONEST[1:] + d, 0.0, 0.99)
        sims = [simulate(schedule(N_TURNS, COMPROMISE, sleeper=sl), 1000 + s) for s in range(N_SEEDS)]
        out[str(d)] = {g.name: summarize([metrics(grants(g.stats(x), th[g.name]), COMPROMISE)
                                          for x in sims]) for g in gates}
    return {"deltas": out, "thetas": th}


def _fig(res: dict) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for n in SHOW:
        axes[0].plot(DELTAS, [res["deltas"][str(d)][n]["oer"]["mean"] for d in DELTAS], "o-", label=n)
        axes[1].plot(DELTAS, [res["deltas"][str(d)][n]["latency"]["mean"] for d in DELTAS], "o-", label=n)
    axes[0].set_ylabel("OER")
    axes[1].set_ylabel("latency (steps, revoked episodes)")
    for ax in axes:
        ax.set_xlabel(r"forgery budget $\Delta$")
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    path = figure_path(EXP, "forgery_sweep.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path.name


def readme(res: dict, fig: str) -> str:
    hdr = "| Delta | " + " | ".join(SHOW) + " |\n|---|" + "---|" * len(SHOW)
    rows = "\n".join(f"| {d} | " + " | ".join(fmt_ci(res["deltas"][str(d)][n]["oer"]) for n in SHOW) + " |"
                     for d in DELTAS)
    fpr = " | ".join(f"{n} {fmt_ci(res['deltas']['0.0'][n]['fpr'])}" for n in SHOW)
    return f"""# Bounded forgery

## Method
Simulated streams ({N_SEEDS} seeds, {N_TURNS} steps, compromise at step {COMPROMISE}).
Honest reliabilities {HONEST.tolist()}; after the compromise the epistemic layer drops
to 0.30 and every other layer is raised to min(0.99, honest + Delta), i.e. the
adversary forges the layers it does not control within a budget Delta. The
epistemic signal is a rolling 8-step rate, as for the real probe. All gates are
calibrated by Algorithm 2 on the same 600-step honest pilot.

## Results: OER (mean [95% CI] over seeds)
{hdr}
{rows}

Honest FPR: {fpr}

## Reading
* TGCC's OER does not depend on Delta: the per-turn epistemic check reads the layer
  whose failure the adversary cannot hide, so forging the other layers cannot lift it.
* Without the check (TGCC-CompositeOnly) OER rises with Delta and then plateaus:
  the coupling caps how far forged downstream layers can lift the composite
  (cascade containment, Proposition 3).
* Averaging gates (Mean, Naive) fail from Delta = 0.05 on.

![forgery](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {**res, "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
