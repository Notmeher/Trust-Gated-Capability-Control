"""N08 - Threshold calibration (Algorithm 2): quantile rule vs min-of-pilot ablation.

Algorithm 2 sets theta = q-quantile(pilot after burn-in) - eps with q = delta and, if
fewer than 1 - delta of pilot steps are admitted, increases eps. The ablation uses the
pilot minimum, which can only decrease as the pilot grows (more honest data makes the
gate more permissive). Both are compared in simulation and on the real-LLM pilots.
"""
from __future__ import annotations

from dataclasses import replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.episodes import SimulationConfig, run_simulated_episode
from tgcc.nextphase.evaluation import run_gate
from tgcc.nextphase.gates import Gate, TGCCParams, calibrate, grants, metrics
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.responses import available_banks, load_bank, model_name
from tgcc.nextphase.stats import mean_ci
from tgcc.nextphase.streams import pilot_signals, qa_episodes

EXP = "n08_calibration"
PILOTS_SIM = [10, 20, 40, 80, 160, 320, 640]
PILOTS_REAL = [10, 20, 40, 80, 120]
METHODS = {"quantile (Algorithm 2)": dict(method="quantile", q=0.05),
           "min-of-pilot (ablation)": dict(method="min")}
GATE = Gate("TGCC", "tgcc", TGCCParams())


def _sim_eval_set(n=150):
    eps = []
    for s in range(n):
        cfg = SimulationConfig(n_turns=300, compromise_step=150, seed=50_000 + s)
        eps.append(run_simulated_episode(cfg))
    return eps


def sim() -> dict:
    evals = _sim_eval_set()
    ev_stats = [GATE.stats(e) for e in evals]
    out = {}
    for mname, kw in METHODS.items():
        rows = []
        for n in PILOTS_SIM:
            thc, fprs, oers, lats = [], [], [], []
            for seed in range(15):
                burn = int(np.ceil(1 / (1 - GATE.params.gamma)))
                cfg = SimulationConfig(n_turns=burn + n, compromise_step=burn + n + 1, seed=7_000 + seed)
                pil = run_simulated_episode(cfg)
                th = calibrate(GATE.stats(pil), eps=0.05, burn_in=burn, **kw)
                thc.append(th["composite"])
                m = [metrics(grants(st, th), 150) for st in ev_stats[:40]]
                fprs.append(np.mean([x["fpr"] for x in m]))
                oers.append(np.mean([x["oer"] for x in m]))
                lats.append(np.mean([min(x["latency"], 150) for x in m]))
            rows.append({"n_pilot": n, "theta_composite": mean_ci(thc), "theta_sd": float(np.std(thc)),
                         "fpr": mean_ci(fprs), "oer": mean_ci(oers), "latency": mean_ci(lats)})
        out[mname] = rows
    return out


def real() -> dict:
    out = {}
    for provider in available_banks():
        bank = load_bank(provider)
        eps = qa_episodes(bank)
        full = pilot_signals(bank)
        res = {}
        for mname, kw in METHODS.items():
            rows = []
            for n in PILOTS_REAL:
                th_list, oer, fpr = [], [], []
                for rep in range(10):
                    idx = np.random.default_rng(rep).permutation(len(full))[:n]
                    pil = full[np.sort(idx)]
                    th = calibrate(GATE.stats(pil), eps=0.05, burn_in=0, **kw)
                    r = run_gate(GATE, eps, pil, thetas=th)["summary"]
                    th_list.append(th["composite"])
                    oer.append(r["oer"]["mean"])
                    fpr.append(r["fpr"]["mean"])
                rows.append({"n_pilot": n, "theta_composite": mean_ci(th_list),
                             "oer": mean_ci(oer), "fpr": mean_ci(fpr)})
            res[mname] = rows
        out[provider] = res
    return out


def step5_demo() -> dict:
    """Admitted fraction of pilot steps as eps is decreased vs increased."""
    cfg = SimulationConfig(n_turns=200, compromise_step=201, seed=3)
    st = GATE.stats(run_simulated_episode(cfg))["composite"]
    base = float(np.quantile(st, 0.20))  # a deliberately too-high starting threshold
    rows = []
    for e in (0.05, 0.04, 0.03, 0.02, 0.01, 0.0):
        rows.append({"eps": e, "admitted": float(np.mean(st >= base - e))})
    wid = []
    for e in (0.05, 0.06, 0.07, 0.08, 0.10, 0.12):
        wid.append({"eps": e, "admitted": float(np.mean(st >= base - e))})
    return {"eps_decreased": rows, "eps_increased": wid}


def _figs(s, r) -> list[str]:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for m, rows in s.items():
        n = [z["n_pilot"] for z in rows]
        axes[0].semilogx(n, [z["theta_composite"]["mean"] for z in rows], "o-", label=m)
        axes[1].semilogx(n, [z["fpr"]["mean"] for z in rows], "o-", label=m)
        axes[2].semilogx(n, [z["latency"]["mean"] for z in rows], "o-", label=m)
    axes[0].set_title("calibrated composite threshold")
    axes[1].set_title("out-of-sample honest FPR")
    axes[2].set_title("revocation latency (steps)")
    for a in axes:
        a.set_xlabel("pilot length")
        a.legend(fontsize=8)
    fig.suptitle("Simulation: threshold calibration vs pilot length")
    fig.tight_layout()
    p1 = figure_path(EXP, "sim_calibration.png")
    fig.savefig(p1, dpi=130)
    plt.close(fig)
    names = [p1.name]
    if r:
        fig, axes = plt.subplots(1, len(r), figsize=(6 * len(r), 4), squeeze=False)
        for ax, (prov, res) in zip(axes[0], r.items()):
            for m, rows in res.items():
                n = [z["n_pilot"] for z in rows]
                ax.plot(n, [z["oer"]["mean"] for z in rows], "o-", label=f"OER {m}")
                ax.plot(n, [z["fpr"]["mean"] for z in rows], "s--", label=f"FPR {m}")
            ax.set_title(f"Real pilots: {model_name(prov)}")
            ax.set_xlabel("pilot length")
            ax.legend(fontsize=7)
        fig.tight_layout()
        p2 = figure_path(EXP, "real_calibration.png")
        fig.savefig(p2, dpi=130)
        plt.close(fig)
        names.append(p2.name)
    return names


def readme(s, r, d, figs) -> str:
    def tbl(rows, lat=True):
        return "\n".join(
            f"| {z['n_pilot']} | {z['theta_composite']['mean']:.3f} | {z['fpr']['mean']:.3f} "
            f"| {z['oer']['mean']:.3f} |" + (f" {z['latency']['mean']:.1f} |" if lat else "")
            for z in rows)
    sb = "\n\n".join(f"**{m}**\n\n| N_pilot | theta | FPR | OER | latency |\n|---|---:|---:|---:|---:|\n{tbl(rows)}"
                     for m, rows in s.items())
    rb = "\n\n".join(
        f"**{model_name(p)} - {m}**\n\n| N_pilot | theta | FPR | OER |\n|---|---:|---:|---:|\n{tbl(rows, lat=False)}"
        for p, res in r.items() for m, rows in res.items())
    dd = "\n".join(f"| {a['eps']} | {a['admitted']:.2f} | {b['eps']} | {b['admitted']:.2f} |"
                   for a, b in zip(d["eps_decreased"], d["eps_increased"]))
    f = "\n".join(f"![{x}](figures/{x})" for x in figs)
    return f"""# Threshold calibration (Algorithm 2)

## Method
Algorithm 2 sets theta = Q_q(pilot after burn-in) - eps with q = delta = 0.05 and
increases eps if fewer than 1 - delta of pilot steps are admitted. The threshold
converges to a population quantile (DKW inequality, effective sample size about
N(1 - gamma)), so the honest FPR targets delta. The min-of-pilot ablation
(theta = min(pilot) - eps) can only decrease as the pilot grows.

## Simulation (TGCC, honest pilots of length N after burn-in, 15 pilots per N,
evaluation on 40 independent 300-step sleeper episodes)
{sb}

## Real-LLM pilots (random N-step subsets of the 120-question pilot, 10 repeats,
evaluated on the 15 E1 episodes)
{rb}

## Admitted fraction of pilot steps as eps changes
| eps (decreasing) | admitted | eps (increasing) | admitted |
|---|---:|---|---:|
{dd}

{f}
"""


def main(argv=None) -> None:
    s = sim()
    r = real()
    d = step5_demo()
    figs = _figs(s, r)
    write_results(EXP, {"simulation": s, "real": r, "step5": d, "figures": figs})
    write_readme(EXP, readme(s, r, d, figs))
    print(readme(s, r, d, figs))


if __name__ == "__main__":
    main()
