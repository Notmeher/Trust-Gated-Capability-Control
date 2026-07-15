"""W6: Bootstrap confidence intervals + significance tests.

Uses the *cached* W1 signals — no additional LLM budget.  For each controller
we bootstrap over per-turn grants (1000 resamples) to produce 95% CIs on OER,
latency and FPR.  We also run Wilcoxon signed-rank tests comparing TGCC's
grant vector to each baseline's on a per-turn basis.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wilcoxon

from tgcc.baselines import (
    AgentGuardLite,
    ConstitutionalLite,
    DynaTrustLite,
    EigenTrustLite,
    NaiveBehavioral,
)
from tgcc.config import final_dir
from tgcc.controller import GrantSpec, TGCCController
from tgcc.reporting import figure_path, write_readme, write_results

EXPERIMENT = "w6_bootstrap_ci"


def _load_w1() -> dict:
    p = final_dir("w1_multi_model") / "results.json"
    if not p.exists():
        raise SystemExit("W1 results not found; run w1_multi_model first.")
    return json.loads(p.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ metrics
def _oer(grants: np.ndarray, k: int) -> float:
    tail = grants[k:]
    return float(tail.mean()) if tail.size else 0.0


def _latency(grants: np.ndarray, k: int, cap: int) -> float:
    tail = grants[k:]
    if tail.size == 0:
        return float(cap)
    if (~tail).any():
        return float(np.argmax(~tail))
    return float(cap)


def _fpr(grants: np.ndarray, k: int) -> float:
    head = grants[:k]
    return float((~head).mean()) if head.size else 0.0


def _run_controllers(signals: np.ndarray, spec: GrantSpec) -> dict[str, np.ndarray]:
    """Return grant vectors per controller (all pre-warmed)."""
    tgcc = TGCCController()
    tgcc.prewarm([0.90] * 5, effective_count=40.0)
    naive = NaiveBehavioral(theta=spec.theta); naive.prewarm()
    eigen = EigenTrustLite(theta=spec.theta); eigen.prewarm()
    dyna = DynaTrustLite(theta=spec.theta); dyna.prewarm()
    const = ConstitutionalLite(theta=spec.theta); const.prewarm()
    guard = AgentGuardLite(theta=spec.theta_layer[0])
    out: dict[str, list[bool]] = {k: [] for k in
        ("TGCC", "Naive", "EigenTrust", "DynaTrust", "AgentGuard", "Constitutional")}
    for row in signals:
        st = tgcc.step(row.tolist())
        out["TGCC"].append(TGCCController.grant(st, spec))
        out["Naive"].append(naive.observe(row).grant)
        out["EigenTrust"].append(eigen.observe(row).grant)
        out["DynaTrust"].append(dyna.observe(row).grant)
        out["AgentGuard"].append(guard.observe(row).grant)
        out["Constitutional"].append(const.observe(row).grant)
    return {k: np.asarray(v, dtype=bool) for k, v in out.items()}


# --------------------------------------------------------------- bootstrap
def _bootstrap(signals: np.ndarray, spec: GrantSpec, compromise_step: int,
               n_boot: int, seed: int) -> dict[str, Any]:
    """Stratified bootstrap over honest / sleeper indices."""
    rng = np.random.default_rng(seed)
    n = signals.shape[0]
    honest_idx = np.arange(compromise_step)
    sleeper_idx = np.arange(compromise_step, n)
    stats: dict[str, dict[str, list[float]]] = {}
    for b in range(n_boot):
        h_re = rng.choice(honest_idx, size=honest_idx.size, replace=True)
        s_re = rng.choice(sleeper_idx, size=sleeper_idx.size, replace=True)
        idx = np.concatenate([h_re, s_re])
        sig_b = signals[idx]
        grants = _run_controllers(sig_b, spec)
        for name, g in grants.items():
            d = stats.setdefault(name, {"oer": [], "latency": [], "fpr": []})
            d["oer"].append(_oer(g, compromise_step))
            d["latency"].append(_latency(g, compromise_step, cap=n - compromise_step))
            d["fpr"].append(_fpr(g, compromise_step))
    summary: dict[str, dict[str, Any]] = {}
    for name, d in stats.items():
        summary[name] = {}
        for metric, vs in d.items():
            arr = np.asarray(vs, dtype=float)
            summary[name][metric] = {
                "mean": float(arr.mean()),
                "std": float(arr.std()),
                "ci_low_95": float(np.percentile(arr, 2.5)),
                "ci_high_95": float(np.percentile(arr, 97.5)),
            }
    return summary


# --------------------------------------------------------------- significance
def _wilcoxon_vs_tgcc(grants_dict: dict[str, np.ndarray]) -> dict[str, float]:
    """Wilcoxon signed-rank on per-turn grant differences vs. TGCC.

    Returns two-sided p-value per baseline.  We map booleans to 0/1 first.
    """
    tgcc_g = grants_dict["TGCC"].astype(int)
    out: dict[str, float] = {}
    for name, g in grants_dict.items():
        if name == "TGCC":
            continue
        diff = tgcc_g - g.astype(int)
        if np.all(diff == 0):
            out[name] = 1.0
            continue
        try:
            _, p = wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
            out[name] = float(p)
        except ValueError:
            out[name] = float("nan")
    return out


# ------------------------------------------------------------------ plot
def _plot(payload: dict) -> str:
    providers = list(payload["per_provider"].keys())
    metrics = ("oer", "latency", "fpr")
    fig, axes = plt.subplots(len(providers), len(metrics),
                             figsize=(11.5, 3.4 * len(providers)),
                             squeeze=False)
    for i, provider in enumerate(providers):
        stats = payload["per_provider"][provider]["bootstrap"]
        names = list(stats.keys())
        for j, m in enumerate(metrics):
            means = [stats[n][m]["mean"] for n in names]
            lo = [stats[n][m]["ci_low_95"] for n in names]
            hi = [stats[n][m]["ci_high_95"] for n in names]
            err = np.array([np.array(means) - np.array(lo),
                            np.array(hi) - np.array(means)])
            colors = ["#2a7f3f" if n == "TGCC" else "#a63a3a" for n in names]
            axes[i, j].bar(names, means, yerr=err, capsize=3, color=colors)
            axes[i, j].set_title(f"{provider} - {m.upper()}")
            axes[i, j].tick_params(axis="x", rotation=30, labelsize=7)
            if m == "oer" or m == "fpr":
                axes[i, j].set_ylim(0, 1.05)
    fig.tight_layout()
    out = figure_path(EXPERIMENT, "bootstrap_ci.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out.name)


# ------------------------------------------------------------------ readme
def _readme(payload: dict) -> str:
    sections: list[str] = []
    for provider, res in payload["per_provider"].items():
        stats = res["bootstrap"]
        pvals = res["wilcoxon_p_vs_tgcc"]
        rows = []
        for name in stats:
            oer = stats[name]["oer"]
            lat = stats[name]["latency"]
            fpr = stats[name]["fpr"]
            p = pvals.get(name)
            p_str = f"{p:.3g}" if p is not None else "-"
            rows.append(
                f"| {name} | "
                f"{oer['mean']:.2f} [{oer['ci_low_95']:.2f}, {oer['ci_high_95']:.2f}] | "
                f"{lat['mean']:.1f} [{lat['ci_low_95']:.1f}, {lat['ci_high_95']:.1f}] | "
                f"{fpr['mean']:.2f} [{fpr['ci_low_95']:.2f}, {fpr['ci_high_95']:.2f}] | "
                f"{p_str} |"
            )
        header = (
            "| Controller | OER (mean [95% CI]) | Latency (mean [95% CI]) | "
            "FPR (mean [95% CI]) | Wilcoxon p vs. TGCC |\n"
            "|---|---|---|---|---|\n"
        )
        sections.append(f"### {provider}\n{header}{chr(10).join(rows)}\n")
    return f"""# W6 - Statistical significance (bootstrap CIs + Wilcoxon)

## Weakness addressed
**W6**: Every headline number in the paper is from one seed and 20-60 turns.
Reviewers demand confidence intervals and significance tests.

## Method
1. Reuse the cached W1 per-turn signal matrix `(n_turns, 5)` for each provider.
2. **Stratified bootstrap** ({payload['config']['n_boot']} resamples) over the
   honest and sleeper index ranges independently -- preserves the compromise
   structure while resampling within each phase.
3. On every resample, run all six controllers (pre-warmed, per-provider W1
   thresholds) and record OER / latency / FPR.
4. Report bootstrap mean and 95% percentile CI for each metric.
5. **Wilcoxon signed-rank test** on per-turn grant vectors (TGCC vs. each
   baseline) as a within-episode significance test.

## Results
{chr(10).join(sections)}

**Reading.**  A CI that stays below a baseline's CI is evidence at the
bootstrap level; p < 0.05 in the Wilcoxon column is evidence at the
per-turn level.  Both must agree for us to claim TGCC dominates.

## Configuration
```yaml
{payload['config']}
```

## Files
- `results.json` - per-controller bootstrap stats and p-values.
- `figures/bootstrap_ci.png` - side-by-side CI bars for OER / latency / FPR.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    w1 = _load_w1()
    cfg = w1["config"]
    per_provider: dict[str, Any] = {}
    for pr in w1["providers"]:
        provider = pr["provider"]
        signals = np.asarray([t["signals"] for t in pr["turns"]], dtype=float)
        spec = GrantSpec(name="high_risk",
                         theta=pr["grant_spec"]["theta"],
                         prereq_layers=(0,),
                         theta_layer=(pr["grant_spec"]["theta_epistemic"],))
        # Single-run grants for Wilcoxon
        grants = _run_controllers(signals, spec)
        pvals = _wilcoxon_vs_tgcc(grants)
        # Bootstrap CIs
        stats = _bootstrap(signals, spec, int(cfg["compromise_step"]),
                           n_boot=args.n_boot, seed=args.seed)
        per_provider[provider] = {
            "grants_single_run": {k: v.tolist() for k, v in grants.items()},
            "bootstrap": stats,
            "wilcoxon_p_vs_tgcc": pvals,
        }
        print(f"[w6] provider={provider} n_boot={args.n_boot} - done")

    payload = {
        "config": {
            "n_boot": args.n_boot,
            "seed": args.seed,
            "compromise_step": cfg["compromise_step"],
            "n_turns": cfg["n_turns"],
        },
        "per_provider": per_provider,
    }
    _plot(payload)
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload))
    print(f"[w6] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
