"""N02 - Parameter sensitivity and coupling misspecification on REAL-LLM streams.

Reviewer issues
---------------
* 14qA W3/Q3 - the operating region (p=-6, c=0.35) was chosen on synthetic
  Bernoulli signals; report sensitivity on the real-LLM streams.
* eY9w W3 - sensitivity of forgetting factor, failure penalty, power-mean
  order and Hedge learning rate.
* RRLq W4 - how sensitive is the method to a wrongly specified trust structure
  (coupling matrix / layer ordering)?

All runs use the 15 independent E1 episodes of N01 per provider. Two protocols:
(a) recalibrate: Algorithm 2 re-run on the pilot for each setting (deployment);
(b) frozen: thresholds fixed at the nominal setting's calibration.
"""
from __future__ import annotations

from dataclasses import replace
from itertools import permutations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.nextphase.evaluation import run_gate
from tgcc.nextphase.gates import Gate, TGCCParams
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.responses import available_banks, load_bank, model_name, model_slug
from tgcc.nextphase.stats import fmt_ci
from tgcc.nextphase.streams import pilot_signals, qa_episodes
from tgcc.synergy import DEFAULT_COUPLING

EXP = "n02_real_stream_sensitivity"
NOM = TGCCParams()
GRID = {
    "p": [-1, -2, -4, -6, -8, -12, -20],
    "coupling_scale": [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.43],
    "gamma": [0.9, 0.95, 0.97, 0.985, 0.99, 0.995],
    "omega": [1.0, 1.5, 2.0, 3.0, 4.0, 6.0],
    "eta": [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0],
    "lam": [0.1, 0.25, 0.5, 0.75, 0.9],
}
HEAT_P = [-1, -2, -4, -6, -10, -20]
HEAT_C = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25]


def _summ(r):
    s = r["summary"]
    return {"oer": s["oer"], "fpr": s["fpr"], "latency": s["latency"],
            "revoked_frac": s["revoked_frac"]}


def _misspecified(rng: np.random.Generator) -> list[tuple[str, np.ndarray]]:
    out = [("default", DEFAULT_COUPLING),
           ("zero", np.zeros((5, 5))),
           ("uniform-0.5", np.tril(np.full((5, 5), 0.5), -1)),
           ("chain-only", np.diag(np.diag(DEFAULT_COUPLING, -1), -1)),
           ("full-1.0", np.tril(np.ones((5, 5)), -1)),
           ("transposed-order", np.tril(DEFAULT_COUPLING[::-1, ::-1].T, -1))]
    for k in range(20):
        out.append((f"random-{k}", np.tril(rng.uniform(0, 1, (5, 5)), -1)))
    return out


def run() -> dict:
    out = {}
    rng = np.random.default_rng(0)
    mats = _misspecified(rng)
    for provider in available_banks():
        bank = load_bank(provider)
        eps = qa_episodes(bank)
        pilot = pilot_signals(bank)
        nom = run_gate(Gate("TGCC", "tgcc", NOM), eps, pilot)
        th0 = nom["thetas"]
        oat = {}
        for k, vals in GRID.items():
            oat[k] = []
            for v in vals:
                g = Gate("TGCC", "tgcc", replace(NOM, **{k: v}))
                oat[k].append({"value": v,
                               "recal": _summ(run_gate(g, eps, pilot)),
                               "frozen": _summ(run_gate(g, eps, pilot, thetas=th0))})
        heat = {}
        for p in HEAT_P:
            for c in HEAT_C:
                for prereq in (True, False):
                    g = Gate("TGCC", "tgcc", replace(NOM, p=p, coupling_scale=c, prereq=prereq))
                    heat[f"{p}|{c}|{int(prereq)}"] = _summ(run_gate(g, eps, pilot))
        mis = {}
        for name, C in mats:
            for prereq in (True, False):
                g = Gate("TGCC", "tgcc", replace(NOM, coupling=tuple(map(tuple, C)), prereq=prereq))
                mis[f"{name}|{int(prereq)}"] = _summ(run_gate(g, eps, pilot))
        # wrong layer ORDER: feed the controller permuted signal columns (epistemic not first)
        order = {}
        for perm in list(permutations(range(5)))[::12]:
            sig_eps = [replace_signals(e, perm) for e in eps]
            g = Gate("TGCC", "tgcc", NOM)
            order[",".join(map(str, perm))] = _summ(run_gate(g, sig_eps, pilot[:, list(perm)]))
        out[provider] = {"nominal": _summ(nom), "thetas": th0, "one_at_a_time": oat,
                         "heatmap": heat, "misspecified_coupling": mis, "layer_order": order}
    return out


def replace_signals(ep, perm):
    from copy import copy
    e = copy(ep)
    e.signals = ep.signals[:, list(perm)]
    return e


def _figs(res) -> list[str]:
    names = []
    for provider, r in res.items():
        fig, axes = plt.subplots(2, 3, figsize=(14, 7))
        for ax, (k, rows) in zip(axes.flat, r["one_at_a_time"].items()):
            x = np.arange(len(rows))
            for proto, ls in (("recal", "-"), ("frozen", "--")):
                ax.plot(x, [z[proto]["oer"]["mean"] for z in rows], ls, marker="o", color="#c92a2a",
                        label=f"OER ({proto})")
                ax.plot(x, [z[proto]["fpr"]["mean"] for z in rows], ls, marker="s", color="#1971c2",
                        label=f"FPR ({proto})")
            ax.set_xticks(x)
            ax.set_xticklabels([str(z["value"]) for z in rows], fontsize=8)
            ax.set_title(k)
            ax.set_ylim(-0.03, 1.03)
        axes[0][0].legend(fontsize=7)
        fig.suptitle(f"{model_name(provider)}: one-at-a-time sensitivity on real-LLM streams")
        fig.tight_layout()
        p = figure_path(EXP, f"{model_slug(provider)}_oat.png")
        fig.savefig(p, dpi=130)
        plt.close(fig)
        names.append(p.name)

        fig, axes = plt.subplots(2, 2, figsize=(11, 8))
        for row, prereq in enumerate((1, 0)):
            for col, metric in enumerate(("oer", "fpr")):
                M = np.array([[r["heatmap"][f"{p}|{c}|{prereq}"][metric]["mean"] for c in HEAT_C]
                              for p in HEAT_P])
                ax = axes[row][col]
                im = ax.imshow(M, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")
                for i in range(len(HEAT_P)):
                    for j in range(len(HEAT_C)):
                        ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=8)
                ax.set_xticks(range(len(HEAT_C)))
                ax.set_xticklabels(HEAT_C)
                ax.set_yticks(range(len(HEAT_P)))
                ax.set_yticklabels(HEAT_P)
                ax.set_xlabel("coupling scale (x default C)")
                ax.set_ylabel("p")
                ax.set_title(f"{metric.upper()} ({'with' if prereq else 'without'} epistemic check)")
                fig.colorbar(im, ax=ax)
        fig.suptitle(f"{model_name(provider)}: p x c sweep on real-LLM streams (recalibrated)")
        fig.tight_layout()
        p = figure_path(EXP, f"{model_slug(provider)}_heatmap.png")
        fig.savefig(p, dpi=130)
        plt.close(fig)
        names.append(p.name)
    return names


def readme(res, figs) -> str:
    blocks = []
    for provider, r in res.items():
        lines = []
        for k, rows in r["one_at_a_time"].items():
            for z in rows:
                lines.append(f"| {k} | {z['value']} | {fmt_ci(z['recal']['oer'])} | {fmt_ci(z['recal']['fpr'])} "
                             f"| {fmt_ci(z['frozen']['oer'])} | {fmt_ci(z['frozen']['fpr'])} |")
        mis = r["misspecified_coupling"]
        rnd = [v for k, v in mis.items() if k.startswith("random") and k.endswith("|1")]
        rnd0 = [v for k, v in mis.items() if k.startswith("random") and k.endswith("|0")]
        ml = [f"| {k.split('|')[0]} | {'yes' if k.endswith('|1') else 'no'} | {fmt_ci(v['oer'])} | {fmt_ci(v['fpr'])} |"
              for k, v in mis.items() if not k.startswith("random")]
        for lab, arr in (("20 random C (range of means)", rnd), ("20 random C, no prereq", rnd0)):
            o = [v["oer"]["mean"] for v in arr]
            f = [v["fpr"]["mean"] for v in arr]
            ml.append(f"| {lab} | | {min(o):.2f}-{max(o):.2f} | {min(f):.2f}-{max(f):.2f} |")
        ol = [f"| {k} | {fmt_ci(v['oer'])} | {fmt_ci(v['fpr'])} |" for k, v in r["layer_order"].items()]
        n = r["nominal"]
        blocks.append(f"""### {model_name(provider)}
Nominal (p=-6, C=default, gamma=0.985, omega=3, eta=0.5, lambda=0.5): OER {fmt_ci(n['oer'])}, FPR {fmt_ci(n['fpr'])}.

**One-at-a-time** (a = recalibrated, b = frozen thresholds)

| Param | Value | OER (a) | FPR (a) | OER (b) | FPR (b) |
|---|---|---|---|---|---|
{chr(10).join(lines)}

**Coupling misspecification** (recalibrated)

| Coupling | Epistemic prereq | OER | FPR |
|---|---|---|---|
{chr(10).join(ml)}

**Layer order** (signal columns permuted; position 0 = layer treated as the universal prerequisite)

| Permutation | OER | FPR |
|---|---|---|
{chr(10).join(ol)}
""")
    f = "\n".join(f"![{x}](figures/{x})" for x in figs)
    return f"""# Parameter sensitivity and structure misspecification on real-LLM streams

## Method
15 independent E1 episodes per model. One-at-a-time sweeps of p, coupling
scale, gamma, omega, eta (Hedge learning rate), lambda (EWMA decay); a
p x coupling heatmap on the real streams with and without the epistemic check;
26 coupling matrices (default, zero, uniform, chain-only, full, reversed
order, 20 random lower-triangular); and permuted layer orders.
(a) recalibrated: Algorithm 2 re-run for each setting; (b) frozen: thresholds of the
nominal setting.

## Results
{chr(10).join(blocks)}

## Figures
{f}
"""


def main(argv=None) -> None:
    res = run()
    figs = _figs(res)
    write_results(EXP, {"providers": res, "figures": figs, "grid": GRID})
    write_readme(EXP, readme(res, figs))
    print("done", EXP)


if __name__ == "__main__":
    main()
