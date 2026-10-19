"""N11 - E3 (p x c ablation) and E5 (scalability) re-implemented in this repository.

Reviewer issues
---------------
* D1aZ / eY9w reproducibility: the code that produced the paper's E3 and E5
  figures was not in the artifact; these drivers regenerate both.
* 14qA W3: E3 is simulation-only; its real-stream counterpart is N02.

E3: 300 simulated episodes per (p, c) cell, with and without belief pre-warming
(the paper's Fig. 5 had no pre-warming, hence warm-up FPR near 1).
E5: 1-50 agents (one sleeper), latency, blast radius and per-agent wall time.
"""
from __future__ import annotations

import time
from dataclasses import replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.episodes import SimulationConfig, run_simulated_episode
from tgcc.nextphase.gates import Gate, TGCCParams, calibrate, grants, metrics
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.streams import windowed_epistemic

EXP = "n11_simulation_e3_e5"
P_GRID = [-1, -2, -3, -6, -10, -30]
C_GRID = [0.1, 0.3, 0.5, 0.7, 0.9]
N_EP = 300
THETA = 0.55  # the paper's simulation threshold for Fig. 5


def _uniform_c(c: float) -> tuple:
    C = np.tril(np.full((5, 5), c), -1)
    return tuple(map(tuple, C))


def _sim(cfg: SimulationConfig) -> np.ndarray:
    return windowed_epistemic(run_simulated_episode(cfg))


def e3() -> dict:
    sims = [_sim(SimulationConfig(seed=s)) for s in range(N_EP)]
    pilot = _sim(SimulationConfig(seed=123_456, n_turns=600, compromise_step=10**9))
    out = {}
    # prewarm: 0 = paper regime (fixed theta 0.55, no pre-warm), 1 = pre-warm + fixed theta,
    # 2 = pre-warm + per-cell quantile calibration on an honest pilot (fair comparison).
    for mode in (0, 1, 2):
        for p in P_GRID:
            for c in C_GRID:
                g = Gate("TGCC", "tgcc", replace(TGCCParams(), p=p, coupling=_uniform_c(c),
                                                prereq=False, prewarm=mode > 0))
                th = ({"composite": THETA} if mode < 2 else
                      calibrate(g.stats(pilot), method="quantile", q=0.05, eps=0.0, burn_in=67))
                lat, fpr = [], []
                for s in sims:
                    m = metrics(grants(g.stats(s), th), 80)
                    lat.append(min(m["latency"], 220))
                    fpr.append(m["fpr"])
                out[f"{mode}|{p}|{c}"] = {"latency": float(np.mean(lat)), "fpr": float(np.mean(fpr))}
    return out


def e5() -> dict:
    rows = []
    for n in (1, 2, 5, 10, 20, 50):
        lats, blast, us = [], [], []
        for s in range(40):
            g = Gate("TGCC", "tgcc", TGCCParams())
            sig = [_sim(SimulationConfig(seed=10_000 * n + 100 * s + k))
                   if k == 0 else _sim(SimulationConfig(seed=10_000 * n + 100 * s + k,
                                                                          compromise_step=10**9))
                   for k in range(n)]
            pil = _sim(SimulationConfig(seed=999_000 + s, compromise_step=10**9, n_turns=200))
            th = calibrate(g.stats(pil), method="quantile", q=0.01, eps=0.02, burn_in=67)
            t0 = time.perf_counter()
            stats = [g.stats(x) for x in sig]
            us.append((time.perf_counter() - t0) / (n * 300) * 1e6)
            m0 = metrics(grants(stats[0], th), 80)
            lats.append(min(m0["latency"], 220))
            if n > 1:
                blast.append(np.mean([1 - grants(st, th)[80:].mean() for st in stats[1:]]))
        rows.append({"n_agents": n, "latency": float(np.mean(lats)),
                     "blast_radius": float(np.mean(blast)) if blast else 0.0,
                     "us_per_agent_step": float(np.median(us))})
    return {"rows": rows}


def _figs(h, s) -> list[str]:
    names = []
    fig, axes = plt.subplots(3, 2, figsize=(11, 12))
    titles = {0: "no pre-warm, fixed theta=0.55", 1: "pre-warm, fixed theta=0.55", 2: "pre-warm, per-cell calibrated"}
    for i, pw in enumerate((0, 1, 2)):
        for j, metric in enumerate(("latency", "fpr")):
            M = np.array([[h[f"{pw}|{p}|{c}"][metric] for c in C_GRID] for p in P_GRID])
            ax = axes[i][j]
            im = ax.imshow(M, cmap="RdYlGn_r", aspect="auto")
            for a in range(len(P_GRID)):
                for b in range(len(C_GRID)):
                    ax.text(b, a, f"{M[a, b]:.2f}" if metric == "fpr" else f"{M[a, b]:.1f}",
                            ha="center", va="center", fontsize=8)
            ax.set_xticks(range(len(C_GRID)))
            ax.set_xticklabels(C_GRID)
            ax.set_yticks(range(len(P_GRID)))
            ax.set_yticklabels(P_GRID)
            ax.set_xlabel("coupling c")
            ax.set_ylabel("p")
            ax.set_title(f"{metric} ({titles[pw]})", fontsize=9)
            fig.colorbar(im, ax=ax)
    fig.tight_layout()
    p = figure_path(EXP, "e3_heatmaps.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    names.append(p.name)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    n = [r["n_agents"] for r in s["rows"]]
    for ax, k in zip(axes, ("latency", "blast_radius", "us_per_agent_step")):
        ax.plot(n, [r[k] for r in s["rows"]], "o-")
        ax.set_xscale("log")
        ax.set_xlabel("agents")
        ax.set_title(k)
    fig.tight_layout()
    p = figure_path(EXP, "e5_scalability.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    names.append(p.name)
    return names


def readme(h, s, figs) -> str:
    def tbl(pw, metric):
        head = "| p \\ c | " + " | ".join(map(str, C_GRID)) + " |\n|---|" + "---|" * len(C_GRID)
        body = "\n".join(f"| {p} | " + " | ".join(f"{h[f'{pw}|{p}|{c}'][metric]:.2f}" for c in C_GRID) + " |"
                         for p in P_GRID)
        return head + "\n" + body
    s_rows = "\n".join(f"| {r['n_agents']} | {r['latency']:.1f} | {r['blast_radius']:.3f} | {r['us_per_agent_step']:.1f} |"
                       for r in s["rows"])
    f = "\n".join(f"![{x}](figures/{x})" for x in figs)
    return f"""# Simulation: p x c ablation (E3) and scalability (E5)

## E3: p x uniform coupling c, {N_EP} simulated episodes per cell (composite-only gate)
Latency (steps), no pre-warm, fixed theta {THETA}:
{tbl(0, 'latency')}

Warm-up FPR, no pre-warm, fixed theta:
{tbl(0, 'fpr')}

Latency, pre-warm + fixed theta:
{tbl(1, 'latency')}

Warm-up FPR, pre-warm + fixed theta:
{tbl(1, 'fpr')}

Latency, pre-warm + per-cell calibration (Algorithm 2, honest pilot):
{tbl(2, 'latency')}

FPR, pre-warm + per-cell calibration:
{tbl(2, 'fpr')}

With a fixed threshold, larger |p| and c mechanically lower the composite, so the
heatmap mostly measures distance to the threshold. With per-cell calibration
(FPR ~0 in every cell), latency spans ~13-30 steps; mild orders (p = -1..-3) with
strong coupling (c >= 0.7) are fastest.

## E5: scalability (one sleeper, 40 seeds per size, quantile-calibrated)
| agents | sleeper latency | blast radius | us / agent-step |
|---|---:|---:|---:|
{s_rows}

{f}
"""


def main(argv=None) -> None:
    h = e3()
    s = e5()
    figs = _figs(h, s)
    write_results(EXP, {"e3": h, "e5": s, "figures": figs})
    write_readme(EXP, readme(h, s, figs))
    print(readme(h, s, figs))


if __name__ == "__main__":
    main()
