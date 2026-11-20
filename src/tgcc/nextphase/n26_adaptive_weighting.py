"""N26 - Adaptive layer weighting: what the guarantee is, and whether it matters (IEEE R1-3, R2-3, R2-6).

Reviewer issues
---------------
* R1-3 / R2-6: Lemma 3 applies the standard Hedge regret bound to an EWMA + softmax update without
  showing the conditions hold (bounded, convex losses; the update rule itself).
* R2-3: no fixed-weight baseline isolates the contribution of adaptive weighting.

What the update is
------------------
r_t = (1 - lam) r_{t-1} + lam q_t and alpha_t = softmax(eta r_t) with q_t = 1 - T_t in [0,1]^L.
Unrolled, r_t = lam * G_t with G_t = sum_s beta^{t-s} q_s and beta = 1 - lam, so
alpha_t = softmax(eta' G_t), eta' = eta * lam: exponential weights on *discounted* cumulative
layer losses. The "loss" of a weighting is <alpha, q_t>: linear in alpha (so convex) and in [0,1]
by construction, whatever the semantics of the layer.

Corrected Lemma 3 (discounted regret; proof in the README): if p_t = softmax(eta' * beta * G_{t-1})
is the weighting formed before q_t is seen, then for every horizon T and every layer i
    sum_t beta^{T-t} q_{t,i} - sum_t beta^{T-t} <p_t, q_t> <= ln L / eta' + eta' / (8 (1 - beta)).
No stationarity, independence or convexity assumption is needed beyond q_t in [0,1]. With
eta' = sqrt(8 (1-beta) ln L) the bound is sqrt(ln L / (2 (1-beta))), i.e. an average discounted
regret of sqrt((1-beta) ln L / 2) per unit of effective horizon 1/(1-beta).

Experiment (real streams only)
------------------------------
(a) Discounted regret of the weighting on every real stream, against the bound, for the default
    (lam = eta = 0.5) and a theory-tuned setting (lam = 0.05, eta' optimal).
(b) Gate ablation on every scenario and bank: TGCC (default), TGCC-FixedW (eta = 0: uniform
    weights), TGCC-TunedHedge (lam = 0.05, theory eta'). All calibrated by Algorithm 2.
"""
from __future__ import annotations

import math
from dataclasses import replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.controller import TGCCController
from tgcc.nextphase.evaluation import run_gate
from tgcc.nextphase.gates import PREWARM_N, PREWARM_RHO, Gate, TGCCParams
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.scenarios import SCENARIOS, banks, episodes, label, pilot_signals
from tgcc.nextphase import tgcc_r
from tgcc.nextphase.stats import fmt_ci
from tgcc.nextphase.streams import epistemic_window

EXP = "n26_adaptive_weighting"
L = 5
TUNED_LAM = 0.05


def eta_prime_opt(lam: float) -> float:
    return math.sqrt(8 * lam * math.log(L))          # 1 - beta = lam


def bound(eta_p: float, lam: float) -> float:
    return math.log(L) / eta_p + eta_p / (8 * lam) if eta_p > 0 else float("inf")


SETTINGS = {
    "default (lam=0.5, eta=0.5)": (0.5, 0.5),
    f"tuned (lam={TUNED_LAM}, eta'=opt)": (TUNED_LAM, eta_prime_opt(TUNED_LAM) / TUNED_LAM),
}


def gates() -> list[Gate]:
    base = TGCCParams()
    lam, eta = SETTINGS[f"tuned (lam={TUNED_LAM}, eta'=opt)"]
    return [
        Gate("TGCC", "tgcc", base),
        Gate("TGCC-FixedW", "tgcc", replace(base, eta=0.0)),
        Gate("TGCC-TunedHedge", "tgcc", replace(base, lam=lam, eta=eta)),
    ]


def layer_losses(signals: np.ndarray) -> np.ndarray:
    """q_t = 1 - T_t, the per-layer losses the controller feeds to its weighting."""
    ctrl = TGCCController()
    ctrl.prewarm([PREWARM_RHO] * L, PREWARM_N)
    return np.array([1.0 - ctrl.step(list(s)).trusts for s in signals])


def discounted_regret(q: np.ndarray, lam: float, eta: float) -> dict:
    """Max over t of the discounted regret of the predictive weighting p_t (formed before q_t)."""
    beta, eta_p = 1.0 - lam, eta * lam
    G = np.zeros(L)
    alg = 0.0
    best = []
    worst = 0.0
    for qt in q:
        z = eta_p * beta * G
        p = np.exp(z - z.max())
        p /= p.sum()
        alg = beta * alg + float(p @ qt)
        G = beta * G + qt
        r = float(G.max() - alg)
        worst = max(worst, r)
        best.append(r)
    return {"max_regret": worst, "bound": bound(eta_p, lam), "horizon": 1.0 / lam,
            "max_regret_per_horizon": worst * lam}


def run() -> dict:
    out = {"regret": {}, "gates": {}}
    gs = gates()
    for provider, ds, bank in banks():
        key = label(provider, ds)
        pil = pilot_signals(bank)
        out["regret"][key] = {}
        out["gates"][key] = {}
        for sc in SCENARIOS:
            eps = episodes(bank, sc)
            out["regret"][key][sc] = {
                name: max((discounted_regret(layer_losses(e.signals), lam, eta) for e in eps),
                          key=lambda d: d["max_regret"])
                for name, (lam, eta) in SETTINGS.items()}
            out["gates"][key][sc] = {g.name: run_gate(g, eps, pil)["summary"] for g in gs}
        # TGCC-R with adaptive vs fixed (uniform) weights, same window and CRC calibration.
        W = tgcc_r.choose_window(lambda: pilot_signals(bank))
        with tgcc_r.mode(W):
            pil_r = pilot_signals(bank)
            eps_r = {sc: episodes(bank, sc) for sc in SCENARIOS}
        for g in (tgcc_r.gate(), tgcc_r.gate("TGCC-R-FixedW", eta=0.0)):
            th = tgcc_r.calibrate_pilot(g, pil_r)
            for sc in SCENARIOS:
                out["gates"][key][sc][g.name] = run_gate(g, eps_r[sc], pil_r, thetas=th)["summary"]
    return out


def _fig(res) -> str:
    keys = list(res["gates"])
    scs = [s for s in SCENARIOS if s != "honest"]
    names = ["TGCC-R", "TGCC-R-FixedW", *[g.name for g in gates()]]
    fig, axes = plt.subplots(1, len(scs) + 1, figsize=(4.2 * (len(scs) + 1), 0.35 * len(keys) + 2.6),
                             sharey=True)
    y = np.arange(len(keys))
    for ax, sc in zip(axes, scs + ["honest"]):
        metric = "fpr" if sc == "honest" else "oer"
        for i, n in enumerate(names):
            ax.barh(y + (i - 2) * 0.16, [res["gates"][k][sc][n][metric]["mean"] for k in keys],
                    height=0.16, label=n)
        ax.set_title(f"{sc}: {'FPR' if sc == 'honest' else 'OER'}")
        ax.set_xlim(0, 1)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(keys, fontsize=7)
    axes[0].invert_yaxis()
    axes[-1].legend(fontsize=7)
    fig.tight_layout()
    p = figure_path(EXP, "weighting_ablation.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p.name


PROOF = r"""
**Proof of the corrected Lemma 3.** Let G_t = beta G_{t-1} + q_t, G_0 = 0, and
Phi_t = (1/eta') ln sum_i exp(eta' G_{t,i}). Write p_t = softmax(eta' beta G_{t-1}). Then

eta' Phi_t = LSE(eta' beta G_{t-1}) + ln sum_i p_{t,i} exp(eta' q_{t,i})
           <= LSE(eta' beta G_{t-1}) + eta' <p_t, q_t> + eta'^2 / 8          (Hoeffding's lemma, q in [0,1])
           <= beta * eta' Phi_{t-1} + (1 - beta) ln L + eta' <p_t, q_t> + eta'^2 / 8,

using sum_i e^{beta x_i} <= (sum_i e^{x_i})^beta L^{1-beta} (Hoelder). Unrolling from eta' Phi_0 = ln L
and using eta' Phi_T >= eta' max_i G_{T,i}:
max_i sum_t beta^{T-t} q_{t,i} - sum_t beta^{T-t} <p_t, q_t> <= ln L / eta' + eta' (1 - beta^T) / (8 (1 - beta)).
Only q_t in [0,1]^L is used: no stationarity, independence or convexity beyond linearity of <p, q>.
"""


def readme(res, fig) -> str:
    reg = []
    for k, r in res["regret"].items():
        for sc, by in r.items():
            reg.append(f"| {k} | {sc} | " + " | ".join(
                f"{v['max_regret']:.2f} / {v['bound']:.2f} (horizon {v['horizon']:.0f})" for v in by.values()) + " |")
    names = ["TGCC-R", "TGCC-R-FixedW", *[g.name for g in gates()]]
    gl = []
    for k, r in res["gates"].items():
        for n in names:
            gl.append(f"| {k} | {n} | " + " | ".join(fmt_ci(r[sc][n]["oer"]) for sc in SCENARIOS if sc != "honest")
                      + f" | {fmt_ci(r['honest'][n]['fpr'])} |")
    return f"""# N26 - Adaptive layer weighting

## Reviewer issues
IEEE R1-3 and R2-6 (Lemma 3 applies standard Hedge to an EWMA + softmax update without justification) and
R2-3 (no fixed-weight baseline isolates adaptive weighting).

## The update and the corrected lemma
The weighting is exponential weights on *discounted* cumulative layer losses q_t = 1 - T_t in [0,1]^L,
with discount beta = 1 - lam and effective rate eta' = eta * lam. The loss of a weighting, <alpha, q_t>,
is linear in alpha and bounded in [0,1] by construction, so no convexity or boundedness assumption about
the semantics of LLM interactions is needed, and no stationarity is assumed.

Discounted regret of the predictive weighting p_t: at most ln L / eta' + eta' / (8 (1 - beta)).
{PROOF}
## (a) Measured discounted regret on real streams
Cells: worst-case (over episodes and time) discounted regret / bound. The effective horizon is 1/(1-beta),
so regret below the horizon means the weighting tracks the most-failing layer.

| Stream | Scenario | {' | '.join(SETTINGS)} |
|---|---|{'---|' * len(SETTINGS)}
{chr(10).join(reg)}

At the default lam = 0.5 the memory is two steps and the bound (about 6.5) exceeds the horizon, so the
guarantee is formally valid but uninformative; the tuned setting gives a non-vacuous bound.

## (b) Does adaptive weighting matter? (OER per compromise; FPR on honest streams)

| Stream | Gate | {' | '.join(f'{s} OER' for s in SCENARIOS if s != 'honest')} | honest FPR |
|---|---|{'---|' * len(SCENARIOS)}
{chr(10).join(gl)}

![ablation](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {"settings": SETTINGS, "results": res, "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
