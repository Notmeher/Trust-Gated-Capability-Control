"""N34 - Coupling structure under TGCC-R: misspecified, learned from real data, and layer order (IEEE R2-5).

Reviewer issue
--------------
R2-5: the coupling matrix (Eq. 9) is specified by hand; the sweep only varies its overall strength and does not
validate the specific dependency structure. N02 / N21 answered this for the original TGCC; here for TGCC-R.

Design (real streams; 6 model x dataset banks; sleeper + three non-epistemic compromises + honest)
-----------------------------------------------------------------------------------------------
* 26 matrices from N02 (default, zero = no synergy, uniform 0.5, chain-only, all-ones, transposed order, 20 random).
* C learned from simulation (N21) and **C learned from real traces**: the maximum-likelihood fit of N21 on per-layer
  Beta trusts from the real streams, labelled by whether the step is compromised. To avoid leakage the matrix
  fitted on one dataset's banks is used on the other dataset's banks (TriviaQA <-> MedMCQA).
* Layer order: the signal columns are permuted (epistemic no longer first) with the default matrix.
* TGCC-R without the composite conjunct, to measure how much the composite (hence the matrix) contributes.
Every variant uses TGCC-R's pilot-selected window and CRC calibration (delta = 0.10) on the bank's pilot.
"""
from __future__ import annotations

import json
from itertools import permutations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.controller import TGCCController
from tgcc.nextphase import tgcc_r
from tgcc.nextphase.evaluation import run_gate
from tgcc.nextphase.gates import PREWARM_N, PREWARM_RHO
from tgcc.nextphase.io import exp_dir, figure_path, write_readme, write_results
from tgcc.nextphase.n02_real_stream_sensitivity import _misspecified
from tgcc.nextphase.n21_learned_coupling import fit
from tgcc.nextphase.scenarios import SCENARIOS, banks, episodes, label, pilot_signals
from tgcc.synergy import DEFAULT_COUPLING

EXP = "n34_coupling_structure_tgcc_r"
ATTACKS = ("sleeper", "policy", "offtopic", "hostile")


def _tup(C) -> tuple:
    return tuple(map(tuple, np.asarray(C, float)))


def real_traces(dataset: str) -> tuple[np.ndarray, np.ndarray]:
    """Per-layer Beta trusts and compromise labels from every real stream of one dataset."""
    Ts, ys = [], []
    for p, ds, bank in banks((dataset,)):
        W = tgcc_r.choose_window(lambda: pilot_signals(bank))
        with tgcc_r.mode(W):
            for sc in SCENARIOS:
                for e in episodes(bank, sc):
                    ctrl = TGCCController()
                    ctrl.prewarm([PREWARM_RHO] * 5, PREWARM_N)
                    for t, s in enumerate(e.signals):
                        Ts.append(ctrl.step(list(s)).trusts)
                        bad = sc != "honest" and t >= e.compromise and (sc != "sleeper" or not e.correct[t])
                        ys.append(float(bad))
    return np.array(Ts), np.array(ys)


def learned_matrices() -> dict[str, np.ndarray]:
    out = {}
    for ds in ("triviaqa", "medmcqa"):
        T, y = real_traces(ds)
        if len(T):
            C, nll = fit(T, y)
            out[ds] = C
    p = exp_dir("n21_learned_coupling") / "results.json"
    if p.exists():
        out["simulation"] = np.array(json.loads(p.read_text(encoding="utf-8"))["C_hat"])
    return out


def run() -> dict:
    mats = dict(_misspecified(np.random.default_rng(0)))
    learned = learned_matrices()
    out = {"learned": {k: v.tolist() for k, v in learned.items()}, "banks": {}}
    for p, ds, bank in banks():
        W = tgcc_r.choose_window(lambda: pilot_signals(bank))
        with tgcc_r.mode(W):
            pil = pilot_signals(bank)
            eps = {sc: episodes(bank, sc) for sc in SCENARIOS}
        variants = {f"matrix: {n}": C for n, C in mats.items()}
        other = "medmcqa" if ds == "triviaqa" else "triviaqa"
        if other in learned:
            variants[f"matrix: learned from real {other} traces"] = learned[other]
        if "simulation" in learned:
            variants["matrix: learned from simulation (N21)"] = learned["simulation"]
        res = {}

        def evaluate(g, ep_map, pilot):
            th = tgcc_r.calibrate_pilot(g, pilot)
            return {sc: run_gate(g, ep_map[sc], pilot, thetas=th)["summary"] for sc in SCENARIOS}

        for name, C in variants.items():
            res[name] = evaluate(tgcc_r.gate(coupling=_tup(C)), eps, pil)
        res["TGCC-R without composite"] = evaluate(tgcc_r.gate(composite=False), eps, pil)
        for perm in list(permutations(range(5)))[::12]:
            if perm == (0, 1, 2, 3, 4):
                continue
            ep_p = {sc: [_perm(e, perm) for e in v] for sc, v in eps.items()}
            res[f"layer order {''.join(map(str, perm))}"] = evaluate(tgcc_r.gate(), ep_p, pil[:, list(perm)])
        out["banks"][label(p, ds)] = {"window": W, "variants": res}
    return out


def _perm(ep, perm):
    from copy import copy
    e = copy(ep)
    e.signals = ep.signals[:, list(perm)]
    return e


def _summary(res) -> dict:
    """Per bank: range over the matrix variants of OER per attack and of FPR."""
    out = {}
    for b, r in res["banks"].items():
        v = r["variants"]
        mats = [k for k in v if k.startswith("matrix:")]
        orders = [k for k in v if k.startswith("layer order")]
        out[b] = {
            grp: {m: (min(v[k][m if m == "honest" else m]["fpr" if m == "honest" else "oer"]["mean"] for k in ks),
                      max(v[k][m]["fpr" if m == "honest" else "oer"]["mean"] for k in ks))
                  for m in (*ATTACKS, "honest")}
            for grp, ks in (("matrices", mats), ("layer orders", orders))}
    return out


def _fig(res) -> str:
    keys = list(res["banks"])
    fig, axes = plt.subplots(1, len(ATTACKS) + 1, figsize=(20, 0.45 * len(keys) + 2.5), sharey=True)
    for ax, m in zip(axes, (*ATTACKS, "honest")):
        metric = "fpr" if m == "honest" else "oer"
        for i, k in enumerate(keys):
            v = res["banks"][k]["variants"]
            vals = [v[n][m][metric]["mean"] for n in v if n.startswith("matrix:")]
            ax.scatter(vals, [i] * len(vals), s=12, alpha=0.6, color="tab:blue")
            ax.scatter([v["matrix: default"][m][metric]["mean"]], [i], marker="*", s=120, color="k")
            ax.scatter([v["TGCC-R without composite"][m][metric]["mean"]], [i], marker="x", s=60, color="tab:red")
        ax.set_title(f"{m}: {'FPR' if m == 'honest' else 'OER'}")
        ax.set_xlim(-0.02, 1.02)
    axes[0].set_yticks(range(len(keys)))
    axes[0].set_yticklabels(keys, fontsize=7)
    axes[0].invert_yaxis()
    fig.suptitle("dots: 29 coupling matrices; star: default; x: TGCC-R without composite", fontsize=9)
    fig.tight_layout()
    p = figure_path(EXP, "coupling_tgcc_r.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p.name


def readme(res, fig) -> str:
    summ = _summary(res)
    rows = []
    for b, s in summ.items():
        v = res["banks"][b]["variants"]
        d, nc = v["matrix: default"], v["TGCC-R without composite"]
        lr = next((k for k in v if "learned from real" in k), None)
        cell = lambda r: " / ".join(f"{r[m]['oer']['mean']:.2f}" for m in ATTACKS) + f" / {r['honest']['fpr']['mean']:.2f}"
        rng = lambda g: " / ".join(f"{s[g][m][0]:.2f}-{s[g][m][1]:.2f}" for m in (*ATTACKS, "honest"))
        rows.append(f"| {b} | {res['banks'][b]['window']} | {cell(d)} | {cell(v[lr]) if lr else 'n/a'} | {cell(nc)} "
                    f"| {rng('matrices')} | {rng('layer orders')} |")
    lm = []
    for k, C in res["learned"].items():
        C = np.array(C)
        lm.append(f"**{k}**\n\n| | " + " | ".join(f"k={j}" for j in range(5)) + " |\n|---|" + "---|" * 5 + "\n" +
                  "\n".join(f"| l={i} | " + " | ".join(f"{C[i, j]:.2f}" if j < i else "-" for j in range(5)) + " |"
                            for i in range(5)))
    return f"""# N34 - Coupling structure under TGCC-R

## Reviewer issue
IEEE R2-5: the coupling matrix is hand-specified; the sweep only varied its overall strength.

## Method
TGCC-R (pilot-selected window, all-layer conjuncts, CRC delta = 0.10) on every real bank, with 26 matrices from N02,
the matrix learned in simulation (N21), a matrix **learned from real traces of the other dataset** (no leakage),
permuted layer orders, and TGCC-R without its composite conjunct. Cells: OER sleeper / policy / off-topic / hostile
/ honest FPR.

| Bank | window | default C | C learned from real data | without composite | range over 29 matrices | range over layer orders |
|---|---:|---|---|---|---|---|
{chr(10).join(rows)}

## Matrices learned from real traces (maximum likelihood, rows = dependent layer l, columns = prerequisite k)
Layers: 0 epistemic, 1 behavioural, 2 role, 3 social, 4 institutional.

{chr(10).join(lm)}

![coupling](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {"results": res, "summary": _summary(res), "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
