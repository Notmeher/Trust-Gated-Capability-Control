"""N35 - Proposition 1 on real streams (IEEE R2-6).

Reviewer issue
--------------
R2-6: Proposition 1 uses the ratio of expected Beta pseudo-counts, which does not establish the expected value of
the random trust estimate itself.

What is measured (real honest streams; every bank; every layer)
---------------------------------------------------------------
For a long honest stream (the honest answers to the pilot and evaluation items, in order) the Beta belief is run with
gamma = 0.985, omega = 3 from the pre-warmed prior. After a burn-in of 3 / (1 - gamma) = 200 steps:
* rho_hat  = mean layer signal;  T*(rho_hat) = rho_hat / (rho_hat + omega (1 - rho_hat))   (Proposition 1);
* E[T]     = time average of the posterior mean a / (a + b)       (the quantity the reviewer asks about);
* E[a]/E[a+b] = ratio of the time-averaged pseudo-counts            (what the proof computes).
The gap E[T] - E[a]/E[a+b] is compared with its second-order (delta-method) value
    -Cov(a, n) / E[n]^2 + E[a] Var(n) / E[n]^3,   n = a + b,
which shrinks as O(1 - gamma) because the pseudo-counts average about 1/(1 - gamma) observations.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.beta_belief import BetaBelief
from tgcc.nextphase.gates import PREWARM_N, PREWARM_RHO
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.scenarios import banks, label
from tgcc.nextphase.streams import LAYERS, compute_signals

EXP = "n35_prop1_real"
GAMMA, OMEGA = 0.985, 3.0
BURN = int(3 / (1 - GAMMA))


def t_star(rho: float) -> float:
    return rho / (rho + OMEGA * (1 - rho))


def honest_stream(bank: dict) -> np.ndarray:
    recs = [bank["pilot"][i] for i in bank["pilot_ids"]] + [bank["honest"][i] for i in bank["eval_ids"]]
    recs = [r for r in recs if (r["text"] or "").strip()]
    return compute_signals([r["text"] for r in recs], [r["correct"] for r in recs], [r["conf"] for r in recs])


def layer_stats(x: np.ndarray) -> dict:
    b = BetaBelief(gamma=GAMMA, omega=OMEGA)
    b.prewarm(PREWARM_RHO, PREWARM_N)
    A, B = [], []
    for v in x:
        b.update(float(v))
        A.append(b.a)
        B.append(b.b)
    A, B = np.array(A)[BURN:], np.array(B)[BURN:]
    n = A + B
    rho = float(np.mean(x[BURN:]))
    et = float(np.mean(A / n))
    ratio = float(np.mean(A) / np.mean(n))
    delta = float(-np.cov(A, n)[0, 1] / np.mean(n) ** 2 + np.mean(A) * np.var(n) / np.mean(n) ** 3)
    return {"rho_hat": rho, "T_star": t_star(rho), "E_T": et, "ratio_of_means": ratio,
            "gap": et - ratio, "delta_method_gap": delta, "abs_err_prop1": abs(et - t_star(rho)),
            "steps": int(len(A))}


def run() -> dict:
    out = {}
    for p, ds, bank in banks():
        s = honest_stream(bank)
        if len(s) <= BURN + 50:
            continue
        out[label(p, ds)] = {LAYERS[k]: layer_stats(s[:, k]) for k in range(5)}
    return out


def _fig(res) -> str:
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for b, r in res.items():
        ax[0].scatter([v["T_star"] for v in r.values()], [v["E_T"] for v in r.values()], s=18, label=b)
        ax[1].scatter([v["delta_method_gap"] for v in r.values()], [v["gap"] for v in r.values()], s=18)
    ax[0].plot([0, 1], [0, 1], "k--", lw=0.8)
    ax[0].set_xlabel("Proposition 1: T*(rho_hat)")
    ax[0].set_ylabel("measured E[T] (time average)")
    ax[0].legend(fontsize=6)
    lim = max(1e-4, max(abs(v["gap"]) for r in res.values() for v in r.values()) * 1.2)
    ax[1].plot([-lim, lim], [-lim, lim], "k--", lw=0.8)
    ax[1].set_xlabel("delta-method gap")
    ax[1].set_ylabel("E[a/(a+b)] - E[a]/E[a+b]")
    fig.tight_layout()
    p = figure_path(EXP, "prop1_real.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p.name


def readme(res, fig) -> str:
    rows = []
    for b, r in res.items():
        for layer, v in r.items():
            rows.append(f"| {b} | {layer} | {v['steps']} | {v['rho_hat']:.3f} | {v['T_star']:.4f} | {v['E_T']:.4f} "
                        f"| {v['abs_err_prop1']:.4f} | {v['gap']:+.5f} | {v['delta_method_gap']:+.5f} |")
    errs = [v["abs_err_prop1"] for r in res.values() for v in r.values()]
    gaps = [abs(v["gap"]) for r in res.values() for v in r.values()]
    return f"""# N35 - Proposition 1 on real streams

## Reviewer issue
IEEE R2-6: Proposition 1 uses the ratio of expected pseudo-counts, not the expected trust.

## Result
On every layer of every real honest stream (after a {BURN}-step burn-in), the expected trust E[T] = E[a/(a+b)]
is within **{max(errs):.4f}** of the closed form T*(rho_hat) (mean {np.mean(errs):.4f}); the "ratio of expectations"
gap the reviewer points to is at most **{max(gaps):.5f}** and follows its second-order (delta-method) value. The
revised proposition states T* as the fixed point of the expected-evidence recursion and bounds the gap by the
delta-method term, which is O(1 - gamma).

| Stream | Layer | steps | rho_hat | T*(rho_hat) | E[T] | abs. error | E[a/n] - E[a]/E[n] | delta-method |
|---|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

![prop1](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {"gamma": GAMMA, "omega": OMEGA, "burn_in": BURN, "results": res, "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
