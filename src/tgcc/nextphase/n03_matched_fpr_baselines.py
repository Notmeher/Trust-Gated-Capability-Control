"""N03 - Head-to-head at matched honest-agent admission (FPR), incl. epistemic-only.

Reviewer issues
---------------
* Jqqf W2 / D1aZ W2 - compare with epistemic-only and verifier-based gating at
  matched honest admission rates.
* 14qA Q2 - strict-minimum aggregator vs power mean.
* eY9w W2 / Jqqf W3 - real baselines, each calibrated by the same procedure
  (the old W3 reused TGCC's thresholds for every baseline, which is unfair).

Two views:
1. Operating point: every gate calibrated with Algorithm 2 on the same pilot.
2. Threshold-free: pooled OER-vs-FPR curve over a common threshold multiplier,
   detection AUC and OER at FPR <= {0, 5, 10}%.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.nextphase.evaluation import oer_at_fpr, roc, run_gate
from tgcc.nextphase.gates import standard_gates
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.responses import available_banks, load_bank, model_name, model_slug
from tgcc.nextphase.stats import fmt_ci
from tgcc.nextphase.streams import pilot_signals, qa_episodes

EXP = "n03_matched_fpr_baselines"
TARGETS = (0.0, 0.05, 0.10)


def run() -> dict:
    out = {}
    for provider in available_banks():
        bank = load_bank(provider)
        eps = qa_episodes(bank)
        pilot = pilot_signals(bank)
        rows = {}
        for g in standard_gates():
            op = run_gate(g, eps, pilot)
            cv = roc(g, eps, pilot)
            rows[g.name] = {
                "operating_point": op["summary"],
                "thetas": op["thetas"],
                "auc": cv["auc"],
                "oer_at_fpr": {str(t): oer_at_fpr(cv, t) for t in TARGETS},
                "curve": {"fpr": cv["fpr"], "oer": cv["oer"]},
            }
        out[provider] = rows
    return out


def _fig(res) -> list[str]:
    names = []
    for provider, rows in res.items():
        fig, ax = plt.subplots(figsize=(6.4, 5))
        for n, r in rows.items():
            ls = "-" if n.startswith("TGCC") else "--"
            ax.step(r["curve"]["fpr"], r["curve"]["oer"], where="post", ls=ls,
                    label=f"{n} (AUC {r['auc']:.3f})")
        ax.set_xlabel("honest FPR (pooled)")
        ax.set_ylabel("post-compromise OER (pooled)")
        ax.set_xlim(-0.01, 0.5)
        ax.set_title(f"{model_name(provider)}: OER vs FPR, 15 episodes")
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        p = figure_path(EXP, f"{model_slug(provider)}_oer_vs_fpr.png")
        fig.savefig(p, dpi=130)
        plt.close(fig)
        names.append(p.name)
    return names


def readme(res, figs) -> str:
    blocks = []
    for provider, rows in res.items():
        t1 = "\n".join(
            f"| {n} | {fmt_ci(r['operating_point']['oer'])} | {fmt_ci(r['operating_point']['fpr'])} "
            f"| {r['auc']:.3f} | " + " | ".join(f"{r['oer_at_fpr'][str(t)]:.2f}" for t in TARGETS) + " |"
            for n, r in rows.items())
        blocks.append(f"""### {model_name(provider)}
| Gate | OER @Alg.2 | FPR @Alg.2 | detection AUC | OER@FPR<=0 | OER@FPR<=0.05 | OER@FPR<=0.10 |
|---|---|---|---:|---:|---:|---:|
{t1}
""")
    f = "\n".join(f"![{x}](figures/{x})" for x in figs)
    return f"""# Baselines at matched honest-agent admission

## Method
Same 15 independent E1 episodes per model. Gates:
TGCC; ablations TGCC-Smoothed (epistemic check on the Beta-smoothed trust),
TGCC-NoSyn (no coupling), TGCC-CompositeOnly (no epistemic check);
**Epistemic-only (Beta)** = the same Beta belief/forgetting/prewarm on the epistemic
layer alone; **Strict-min (Beta)** over the five layer trusts; Mean
(Constitutional-lite); Naive behavioural; AgentGuard-lite (memoryless per-turn
epistemic signal); EigenTrust-lite; DynaTrust-lite.

* Operating point: each gate calibrated by Algorithm 2 on the SAME honest pilot.
* Threshold-free: each gate's decision statistic is normalized by its pilot
  minimum and swept with a common multiplier; pooled honest FPR vs pooled OER.
  Detection AUC = area under (FPR, 1 - OER). OER@FPR<=x = best OER with honest
  FPR at most x (matched admission).

## Results
{chr(10).join(blocks)}

## Figures
{f}
"""


def main(argv=None) -> None:
    res = run()
    figs = _fig(res)
    write_results(EXP, {"providers": res, "figures": figs, "targets": TARGETS})
    write_readme(EXP, readme(res, figs))
    print(readme(res, figs))


if __name__ == "__main__":
    main()
