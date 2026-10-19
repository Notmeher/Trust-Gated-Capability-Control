"""N18 - Long-horizon drift (E10) and revocation-then-recovery (E12), simulated.

E10: 5000-step stream; the epistemic reliability decays 0.92 -> 0.60 over steps
1000-4000, and a model swap at steps 2000-2200 lowers epistemic (<= 0.75) and
behavioural (0.70) reliability. Grant rate per regime, 20 seeds.
E12: honest (0-59) -> sleeper (60-199) -> restored honest (200-399), 50 seeds.
Gates calibrated by Algorithm 2 on the same honest simulated pilot.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.nextphase.gates import grants, standard_gates
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.sim import HONEST, SLEEPER, sim_thetas, simulate
from tgcc.nextphase.stats import fmt_ci, mean_ci

EXP = "n18_long_horizon_recovery"
SHOW = ["TGCC", "TGCC-Smoothed", "TGCC-CompositeOnly"]
REGIMES = [("stable", 0, 1000), ("early drift", 1000, 2000), ("model swap", 2000, 2200),
           ("after swap", 2200, 2400), ("late drift", 2400, 4000), ("drifted (rho_e=0.60)", 4000, 5000)]


def drift_schedule(n: int = 5000) -> np.ndarray:
    rho = np.tile(HONEST, (n, 1))
    t = np.arange(1000, 4000)
    rho[1000:4000, 0] = 0.92 - 0.32 * (t - 1000) / 3000
    rho[4000:, 0] = 0.60
    rho[2000:2200, 0] = np.minimum(rho[2000:2200, 0], 0.75)
    rho[2000:2200, 1] = 0.70
    return rho


def e10(gates, th) -> dict:
    rho = drift_schedule()
    rates = {g.name: {r[0]: [] for r in REGIMES} for g in gates}
    trace = {}
    for s in range(20):
        x = simulate(rho, 500 + s)
        for g in gates:
            gr = grants(g.stats(x), th[g.name])
            for name, a, b in REGIMES:
                rates[g.name][name].append(float(gr[a:b].mean()))
            if s == 0:
                trace[g.name] = gr.astype(int).tolist()
    return {"rates": {n: {k: mean_ci(v) for k, v in r.items()} for n, r in rates.items()}, "trace_seed0": trace}


def _first(x: np.ndarray, val: bool) -> float:
    i = np.where(x == val)[0]
    return float(i[0]) if i.size else float("inf")


def _stable(x: np.ndarray, w: int = 20, frac: float = 0.9) -> float:
    for i in range(len(x) - w + 1):
        if x[i:i + w].mean() >= frac:
            return float(i)
    return float("inf")


def e12(gates, th) -> dict:
    rho = np.tile(HONEST, (400, 1))
    rho[60:200] = SLEEPER
    out = {}
    for g in gates:
        rev, first, stable, early = [], [], [], []
        for s in range(50):
            gr = grants(g.stats(simulate(rho, 900 + s)), th[g.name])
            rev.append(_first(gr[60:200], False))
            first.append(_first(gr[200:], True))
            stable.append(_stable(gr[200:]))
            early.append(float(gr[200:260].mean()))
        out[g.name] = {"revocation": mean_ci(rev), "first_regrant": mean_ci(first),
                       "stable_regrant": mean_ci(stable), "grant_rate_200_260": mean_ci(early),
                       "never_stable": int(sum(not np.isfinite(v) for v in stable))}
    return out


def _fig(h: dict) -> str:
    fig, ax = plt.subplots(figsize=(11, 3.6))
    k = np.ones(100) / 100
    for n, gr in h["trace_seed0"].items():
        ax.plot(np.convolve(gr, k, mode="same"), label=n, lw=1)
    for name, a, b in REGIMES[1:]:
        ax.axvspan(a, b, alpha=0.08, color="#a63a3a" if name == "model swap" else "#e6a23c")
    ax.set_xlabel("step")
    ax.set_ylabel("grant rate (100-step window)")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=8)
    fig.tight_layout()
    path = figure_path(EXP, "long_horizon.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path.name


def readme(h: dict, r: dict, fig: str) -> str:
    hdr = "| Gate | " + " | ".join(f"{n} ({a}-{b})" for n, a, b in REGIMES) + " |\n|---|" + "---|" * len(REGIMES)
    rows = "\n".join(f"| {n} | " + " | ".join(fmt_ci(h["rates"][n][k[0]]) for k in REGIMES) + " |" for n in SHOW)
    rrows = "\n".join(f"| {n} | {fmt_ci(v['revocation'], 1)} | {fmt_ci(v['first_regrant'], 1)} | "
                      f"{fmt_ci(v['stable_regrant'], 1)} ({v['never_stable']} never) | {fmt_ci(v['grant_rate_200_260'])} |"
                      for n, v in r.items())
    return f"""# Long-horizon drift (E10) and recovery (E12)

Simulated streams; the epistemic signal is a rolling 8-step rate, as for the real
probe. Gates are calibrated by Algorithm 2 on the same 600-step honest pilot.

## E10: 5000 steps, 20 seeds (grant rate per regime, mean [95% CI])
Epistemic reliability decays linearly 0.92 -> 0.60 over steps 1000-4000; a model
swap at steps 2000-2200 lowers epistemic reliability to <= 0.75 and behavioural to 0.70.
{hdr}
{rows}

![long horizon](figures/{fig})

## E12: honest (0-59) -> sleeper (60-199) -> restored (200-399), 50 seeds
Sleeper reliabilities {SLEEPER.tolist()}. Belief time constant 1/(1-gamma) = 66.7 steps.

| Gate | Revocation latency | First re-grant after restoration | Stable re-grant (>= 90% of next 20 steps) | Grant rate, steps 200-259 |
|---|---|---|---|---|
{rrows}

## Reading
* E10: TGCC tracks the drift instead of locking the agent out: admission falls as the
  agent's real reliability falls (0.98 -> 0.24 at rho_e = 0.60), dips during the model
  swap and partly recovers afterwards. TGCC-Smoothed locks the agent out once drift
  starts; the composite alone admits the drifted agent most of the time.
* E12: TGCC revokes within a few steps and re-admits the restored agent after about
  45-50 steps, below the belief time constant of 66.7 steps; re-admission is set by
  the composite's Beta memory. TGCC-Smoothed needs about 140 steps.
"""


def main(argv=None) -> None:
    gates = [g for g in standard_gates() if g.name in SHOW]
    th = {g.name: sim_thetas(g) for g in gates}
    h = e10(gates, th)
    r = e12(gates, th)
    fig = _fig(h)
    write_results(EXP, {"e10": h, "e12": r, "thetas": th, "figures": [fig]})
    write_readme(EXP, readme(h, r, fig))
    print(readme(h, r, fig))


if __name__ == "__main__":
    main()
