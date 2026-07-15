"""W11: Controller parameter sensitivity.

Perturb each of the four core parameters (theta, gamma, omega, p) by +/- 20 %
around the paper's recommended operating point and record OER / latency / FPR
on a fixed simulated compromise.  Reports a one-at-a-time sensitivity index
(Morris-style elementary effect) per parameter.
"""
from __future__ import annotations

import argparse
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.controller import GrantSpec, TGCCController
from tgcc.metrics import summary
from tgcc.reporting import figure_path, write_readme, write_results

EXPERIMENT = "w11_sensitivity"


def _simulate(theta: float, gamma: float, omega: float, p: float,
              seed: int, n_turns: int, compromise_step: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    honest_rho = np.array([0.92, 0.88, 0.82, 0.78, 0.90])
    sleeper_rho = np.array([0.30, 0.88, 0.82, 0.78, 0.90])
    ctrl = TGCCController(gamma=gamma, omega=omega, p=p)
    ctrl.prewarm([0.90] * 5, effective_count=40.0)
    spec = GrantSpec("high_risk", theta=theta, prereq_layers=(0,),
                     theta_layer=(theta * 0.6,))
    grants = []
    for t in range(n_turns):
        rho = honest_rho if t < compromise_step else sleeper_rho
        signals = (rng.random(5) < rho).astype(float)
        st = ctrl.step(signals.tolist())
        grants.append(ctrl.grant(st, spec))
    return summary(grants, compromise_step)


def _sweep(base: dict[str, float], param: str, values: list[float],
           n_seeds: int, n_turns: int, compromise_step: int) -> list[dict[str, Any]]:
    rows = []
    for v in values:
        cfg = dict(base); cfg[param] = v
        oer, lat, fpr = [], [], []
        for s in range(n_seeds):
            m = _simulate(**cfg, seed=1000 + s, n_turns=n_turns,
                          compromise_step=compromise_step)
            oer.append(m["over_exposure_rate"])
            lat_val = m["revocation_latency"]
            lat.append(lat_val if lat_val != float("inf") else n_turns - compromise_step)
            fpr.append(m["false_positive_rate"])
        rows.append({
            "value": float(v),
            "oer_mean": float(np.mean(oer)), "oer_std": float(np.std(oer)),
            "latency_mean": float(np.mean(lat)), "latency_std": float(np.std(lat)),
            "fpr_mean": float(np.mean(fpr)), "fpr_std": float(np.std(fpr)),
        })
    return rows


def _elementary_effect(sweep: list[dict[str, Any]], metric: str) -> float:
    """Max-abs difference in the metric divided by the max-abs difference in
    the parameter value (Morris-style elementary effect).
    """
    values = np.array([r["value"] for r in sweep])
    means = np.array([r[f"{metric}_mean"] for r in sweep])
    if values.max() == values.min():
        return 0.0
    return float((means.max() - means.min()) / (values.max() - values.min()))


def _plot(payload: dict) -> str:
    params = list(payload["sweeps"].keys())
    fig, axes = plt.subplots(1, len(params), figsize=(3.7 * len(params), 3.7),
                             squeeze=False)
    for i, name in enumerate(params):
        rows = payload["sweeps"][name]
        v = np.array([r["value"] for r in rows])
        oer = np.array([r["oer_mean"] for r in rows])
        lat = np.array([r["latency_mean"] for r in rows])
        ax = axes[0, i]
        ax.plot(v, oer, marker="o", color="#a63a3a", label="OER")
        ax.set_ylabel("OER", color="#a63a3a")
        ax2 = ax.twinx()
        ax2.plot(v, lat, marker="s", color="#1f4e79", label="latency")
        ax2.set_ylabel("latency (steps)", color="#1f4e79")
        ax.set_xlabel(name)
        ax.set_title(name)
    fig.tight_layout()
    out = figure_path(EXPERIMENT, "sensitivity.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out.name)


def _readme(payload: dict) -> str:
    ee = payload["elementary_effects"]
    ee_rows = [f"| {k} | {v['oer']:.3g} | {v['latency']:.3g} | {v['fpr']:.3g} |"
               for k, v in ee.items()]
    sweep_sections: list[str] = []
    for name, rows in payload["sweeps"].items():
        table = "\n".join(
            f"| {r['value']:.3f} | {r['oer_mean']:.2f} ± {r['oer_std']:.2f} | "
            f"{r['latency_mean']:.1f} ± {r['latency_std']:.1f} | "
            f"{r['fpr_mean']:.2f} ± {r['fpr_std']:.2f} |"
            for r in rows
        )
        sweep_sections.append(
            f"### {name}\n"
            "| value | OER | latency | FPR |\n|---|---|---|---|\n"
            f"{table}\n"
        )
    return f"""# W11 - Controller parameter sensitivity

## Weakness addressed
**W11**: Are TGCC's headline numbers brittle under small parameter perturbations?

## Method
1. Fix the paper's recommended operating point:
   `theta=0.40`, `gamma=0.985`, `omega=3`, `p=-6`.
2. For each parameter independently, sweep it over `[0.8 x, 0.9 x, x, 1.1 x, 1.2 x]`
   holding the others fixed.
3. Simulate a stealth-sleeper compromise (n_turns=200, compromise at 60),
   `n_seeds = {payload['config']['n_seeds']}` seeds per point.
4. Report the Morris-style elementary effect: max-abs metric change divided
   by max-abs parameter change.

## Elementary effects (higher = more sensitive)

| Parameter | on OER | on latency | on FPR |
|---|---|---|---|
{chr(10).join(ee_rows)}

## Per-sweep detail
{chr(10).join(sweep_sections)}

## Reading
* If any elementary effect > 5, the controller is dangerously brittle in
  that parameter.  A well-behaved controller has all effects at O(1).

## Files
- `results.json` - full sweep with per-metric mean +/- std.
- `figures/sensitivity.png` - metric curves per parameter.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-seeds", type=int, default=15)
    parser.add_argument("--n-turns", type=int, default=200)
    parser.add_argument("--compromise-step", type=int, default=60)
    args = parser.parse_args()

    base = {"theta": 0.40, "gamma": 0.985, "omega": 3.0, "p": -6.0}
    sweeps: dict[str, list[dict[str, Any]]] = {}
    for name, span in [
        ("theta", [0.32, 0.36, 0.40, 0.44, 0.48]),
        ("gamma", [0.95, 0.97, 0.985, 0.993, 0.998]),
        ("omega", [2.0, 2.5, 3.0, 3.5, 4.0]),
        ("p", [-10.0, -8.0, -6.0, -4.0, -2.0]),
    ]:
        sweeps[name] = _sweep(base, name, span, args.n_seeds,
                              args.n_turns, args.compromise_step)
    ee = {name: {m: _elementary_effect(rows, m) for m in ("oer", "latency", "fpr")}
          for name, rows in sweeps.items()}
    payload = {
        "config": {"n_seeds": args.n_seeds, "n_turns": args.n_turns,
                   "compromise_step": args.compromise_step,
                   "base": base},
        "sweeps": sweeps,
        "elementary_effects": ee,
    }
    _plot(payload)
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload))
    print(f"[w11] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
