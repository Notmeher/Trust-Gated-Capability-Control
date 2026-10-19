"""N19 - Byzantine multi-agent chain (E13), simulated.

N agents, K = max(1, round(0.2 N)) of them sleepers compromised at step 60
(200 steps, 20 seeds per N). Each agent has its own gate (Algorithm 2 on an honest
pilot). Weakest-link chain: the pipeline acts only if every agent is admitted.
"""
from __future__ import annotations

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.nextphase.gates import grants, standard_gates
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.sim import schedule, sim_thetas, simulate
from tgcc.nextphase.stats import fmt_ci, mean_ci

EXP = "n19_byzantine_chain"
NS = [1, 3, 5, 10, 20, 50]
SHOW = ["TGCC", "TGCC-Smoothed"]
N_SEEDS, N_TURNS, COMPROMISE = 20, 200, 60


def _first_denial(g: np.ndarray) -> float:
    i = np.where(~g[COMPROMISE:])[0]
    return float(i[0]) if i.size else float(N_TURNS - COMPROMISE)


def run() -> dict:
    gates = [g for g in standard_gates() if g.name in SHOW]
    th = {g.name: sim_thetas(g) for g in gates}
    out = {}
    for g in gates:
        rows = []
        for n in NS:
            k = max(1, round(0.2 * n))
            acc = {m: [] for m in ("first", "all", "sleeper_oer", "chain_oer", "chain_avail", "blast", "us")}
            for s in range(N_SEEDS):
                rng = np.random.default_rng(7000 + 100 * n + s)
                bad = set(rng.choice(n, size=k, replace=False).tolist())
                X = [simulate(schedule(N_TURNS, COMPROMISE if i in bad else N_TURNS), 10**6 * n + 1000 * s + i)
                     for i in range(n)]
                t0 = time.perf_counter()
                G = [grants(g.stats(x), th[g.name]) for x in X]
                acc["us"].append((time.perf_counter() - t0) / (n * N_TURNS) * 1e6)
                G = np.array(G)
                lat = [_first_denial(G[i]) for i in bad]
                acc["first"].append(min(lat))
                acc["all"].append(max(lat))
                acc["sleeper_oer"].append(float(G[list(bad), COMPROMISE:].mean()))
                chain = G.all(axis=0)
                acc["chain_oer"].append(float(chain[COMPROMISE:].mean()))
                acc["chain_avail"].append(float(chain[:COMPROMISE].mean()))
                hon = [i for i in range(n) if i not in bad]
                acc["blast"].append(float((~G[hon, COMPROMISE:]).mean()) if hon else 0.0)
            rows.append({"n": n, "k": k, **{m: mean_ci(v) for m, v in acc.items()}})
        out[g.name] = rows
    return {"rows": out, "thetas": th}


def _fig(res: dict) -> str:
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.6))
    keys = [("all", "latency until all sleepers revoked"), ("sleeper_oer", "sleeper OER"),
            ("blast", "honest-agent denial (blast radius)"), ("chain_avail", "chain availability before compromise")]
    for ax, (k, title) in zip(axes, keys):
        for n, rows in res["rows"].items():
            ax.plot(NS, [r[k]["mean"] for r in rows], "o-", label=n)
        ax.set_xscale("log")
        ax.set_xlabel("agents N")
        ax.set_title(title, fontsize=9)
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    path = figure_path(EXP, "byzantine_chain.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path.name


def readme(res: dict, fig: str) -> str:
    blocks = []
    for n, rows in res["rows"].items():
        body = "\n".join(
            f"| {r['n']} | {r['k']} | {fmt_ci(r['first'], 1)} | {fmt_ci(r['all'], 1)} | {fmt_ci(r['sleeper_oer'])} | "
            f"{fmt_ci(r['chain_oer'])} | {fmt_ci(r['blast'])} | {fmt_ci(r['chain_avail'])} | {r['us']['mean']:.0f} |"
            for r in rows)
        blocks.append(f"### {n}\n| N | K | First sleeper revoked | All sleepers revoked | Sleeper OER | "
                      "Chain OER | Blast radius | Chain availability (pre) | us / agent-step |\n"
                      "|---|---|---|---|---|---|---|---|---|\n" + body)
    return f"""# Byzantine multi-agent chain (E13)

## Method
Simulated chain of N agents ({N_SEEDS} seeds per N, {N_TURNS} steps). K = max(1, round(0.2 N))
randomly chosen agents become sleepers at step {COMPROMISE} (epistemic reliability 0.30).
Each agent has its own gate, calibrated by Algorithm 2 on the same honest simulated pilot.
* Chain OER: fraction of post-compromise steps on which every agent (sleepers included) is admitted.
* Blast radius: post-compromise denial rate of the honest agents.
* Chain availability: fraction of pre-compromise steps on which every agent is admitted
  (weakest-link pipeline).

## Results (mean [95% CI] over seeds)
{chr(10).join(blocks)}

## Reading
* Per-sleeper detection does not degrade with team size: sleeper OER stays at
  0.02 for TGCC from N = 1 to 50, and the last sleeper is revoked within about 3-6 steps.
* Gates are per agent, so the honest agents' denial rate (blast radius) stays at the
  per-agent honest FPR (0.00-0.03) whatever N is.
* A strict weakest-link pipeline loses availability as N grows (0.97 -> 0.25 at N = 50),
  because some honest agent is falsely denied at almost every step. Large teams
  should route around denied agents rather than halt.

![chain](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {**res, "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
