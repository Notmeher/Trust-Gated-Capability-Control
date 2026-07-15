"""W3: Head-to-head baseline comparison.

Reuses the W1 LLM episode (cached, so this is free once W1 has been run once)
and streams the *same* per-turn signals through every controller.

Baselines:
* Naive               - grant iff behavioural trust >= theta.
* EigenTrust-lite     - EMA of the arithmetic mean of the five signals.
* DynaTrust-lite      - dynamic scalar trust from mean & current min.
* AgentGuard-lite     - per-turn threshold on the epistemic signal.
* Constitutional-lite - unweighted Beta average of all five layers.
* **TGCC (ours)**     - the full controller.

Every stateful controller is pre-warmed with the same honest prior so that
the comparison is fair (fixes the warmup-FPR bias against multi-signal
controllers).  Per-provider thresholds are taken from W1's Algorithm 2
calibration unless overridden.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.baselines import (
    AgentGuardLite,
    ConstitutionalLite,
    DynaTrustLite,
    EigenTrustLite,
    NaiveBehavioral,
)
from tgcc.config import final_dir
from tgcc.controller import GrantSpec, TGCCController
from tgcc.metrics import summary
from tgcc.reporting import figure_path, write_readme, write_results

EXPERIMENT = "w3_baselines"


def _load_w1() -> dict:
    p = final_dir("w1_multi_model") / "results.json"
    if not p.exists():
        raise SystemExit(
            "W1 results not found. Run `python -m tgcc.experiments.w1_multi_model` first."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def _extract_signals(w1: dict) -> dict[str, np.ndarray]:
    """Per-provider (n_turns, 5) matrix of signals."""
    out: dict[str, np.ndarray] = {}
    for r in w1["providers"]:
        arr = np.array([t["signals"] for t in r["turns"]], dtype=float)
        out[r["provider"]] = arr
    return out


def _run_all(
    signals: np.ndarray,
    compromise_step: int,
    theta: float,
    theta_epistemic: float,
    prewarm: bool = True,
) -> dict[str, Any]:
    spec = GrantSpec(
        name="high_risk",
        theta=theta,
        prereq_layers=(0,),
        theta_layer=(theta_epistemic,),
    )
    tgcc_ctrl = TGCCController()
    naive_ctrl = NaiveBehavioral(theta=theta)
    eigen_ctrl = EigenTrustLite(theta=theta)
    dyna_ctrl = DynaTrustLite(theta=theta)
    guard_ctrl = AgentGuardLite(theta=theta_epistemic)
    const_ctrl = ConstitutionalLite(theta=theta)
    if prewarm:
        tgcc_ctrl.prewarm(rhos=[0.90] * 5, effective_count=40.0)
        naive_ctrl.prewarm()
        eigen_ctrl.prewarm()
        dyna_ctrl.prewarm()
        const_ctrl.prewarm()
    controllers = {
        "TGCC": ("tgcc", tgcc_ctrl),
        "Naive": ("naive", naive_ctrl),
        "EigenTrust-lite": ("eigentrust", eigen_ctrl),
        "DynaTrust-lite": ("dynatrust", dyna_ctrl),
        "AgentGuard-lite": ("agentguard", guard_ctrl),
        "Constitutional-lite": ("constitutional", const_ctrl),
    }
    results: dict[str, Any] = {}
    for label, (key, ctrl) in controllers.items():
        grants: list[bool] = []
        trust_trace: list[float] = []
        for row in signals:
            if key == "tgcc":
                st = ctrl.step(row.tolist())
                grants.append(TGCCController.grant(st, spec))
                trust_trace.append(st.composite)
            else:
                d = ctrl.observe(row)
                grants.append(d.grant)
                trust_trace.append(d.trust)
        results[label] = {
            "grants": grants,
            "trust": trust_trace,
            "metrics": summary(grants, compromise_step),
        }
    return results


def _plot(per_provider: dict, compromise_step: int) -> list[str]:
    saved: list[str] = []
    for provider, res in per_provider.items():
        controllers = {k: v for k, v in res.items() if not k.startswith("_")}
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
        for label, r in controllers.items():
            ax[0].plot(r["trust"], label=label, alpha=0.85)
        ax[0].axvline(compromise_step, color="red", linestyle=":", alpha=0.6, label="compromise")
        ax[0].set_ylim(0, 1.05)
        ax[0].set_xlabel("interaction step $t$")
        ax[0].set_ylabel("trust signal (native to each controller)")
        ax[0].set_title(f"Trust trajectories - {provider}")
        ax[0].legend(fontsize=7)
        labels = list(controllers.keys())
        oers = [controllers[l]["metrics"]["over_exposure_rate"] for l in labels]
        colors = ["#2a7f3f" if l == "TGCC" else "#a63a3a" for l in labels]
        ax[1].bar(labels, oers, color=colors)
        ax[1].set_ylabel("post-compromise OER")
        ax[1].set_title(f"OER - {provider}")
        ax[1].tick_params(axis="x", rotation=30, labelsize=8)
        for i, v in enumerate(oers):
            ax[1].text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=8)
        fig.tight_layout()
        out = figure_path(EXPERIMENT, f"{provider}_baselines.png")
        fig.savefig(out, dpi=130)
        plt.close(fig)
        saved.append(str(out.name))
    return saved


def _readme(payload: dict) -> str:
    section_bodies: list[str] = []
    for provider, res in payload["per_provider"].items():
        thresholds = res.get("_thresholds", {})
        theta = float(thresholds.get("theta", 0.0))
        theta_e = float(thresholds.get("theta_epistemic", 0.0))
        rows = []
        for name, r in res.items():
            if name.startswith("_"):
                continue
            m = r["metrics"]
            rows.append(
                f"| {name} | {m['over_exposure_rate']:.2f} | {m['revocation_latency']} | "
                f"{m['false_positive_rate']:.2f} |"
            )
        header = (
            "| Controller | OER | Latency | FPR |\n"
            "|---|---|---|---|\n"
        )
        section_bodies.append(
            f"### {provider} (theta={theta:.2f}, theta_epi={theta_e:.2f})\n"
            f"{header}{chr(10).join(rows)}\n\n"
            f"![{provider}](figures/{provider}_baselines.png)\n"
        )
    return f"""# W3 - Head-to-Head Baseline Comparison

## Weakness addressed
**W3**: The paper's E1 compares TGCC only against its own no-synergy ablation
and the naive gate.  Reviewers ask for a fair head-to-head against **competing
runtime trust controllers** on the same data.

## Method
1. Reuse the LLM episodes from W1 (cached responses) and extract the per-turn
   five-signal vectors.
2. Every stateful controller is **pre-warmed** with an honest prior
   (`rho=0.9`, effective count 40) so all methods start from a fair,
   post-warmup steady state (fairness fix).
3. Thresholds are taken **per provider** from W1's Algorithm 2 calibration
   (Section 7 of the paper), unless overridden by `--theta` / `--theta-epistemic`.
4. Stream signals through six controllers:
   - **TGCC** (ours) - Beta -> synergy -> Hedge -> composite -> grant.
   - **Naive** - behavioural trust only.
   - **EigenTrust-lite** - EMA of unweighted-mean signal (single scalar).
   - **DynaTrust-lite** - dynamic scalar mixing mean & current min.
   - **AgentGuard-lite** - runtime monitor on the epistemic signal only.
   - **Constitutional-lite** - Beta-smoothed arithmetic mean of all five layers.
5. Compute OER, revocation latency, honest-phase FPR for each.

All controllers see the **same signals** so the comparison isolates the
aggregation and decision rules.  TGCC's compositional cross-layer reasoning is
the only mechanism that turns a hidden epistemic collapse into a visible
composite failure.

## Results
{chr(10).join(section_bodies)}

**Reading the tables.**  A good runtime defense should have **low OER, small
latency, and low FPR**.  Scalar-trust methods (EigenTrust, DynaTrust,
Constitutional) tend to average away the epistemic collapse.  AgentGuard fires
early on the epistemic signal but has no memory (so it can oscillate).  TGCC
should dominate on OER + latency without a warmup-FPR penalty.

## Files
- `results.json` - per-provider grants, trust traces, and metrics.
- `figures/*_baselines.png` - trust trajectories and OER bar charts.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theta", type=float, default=None,
                        help="Override composite threshold; default: W1 per-provider calibration.")
    parser.add_argument("--theta-epistemic", type=float, default=None,
                        help="Override epistemic-prereq threshold; default: W1 per-provider calibration.")
    parser.add_argument("--prewarm", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    w1 = _load_w1()
    cfg = w1["config"]
    compromise_step = int(cfg["compromise_step"])
    signals_by_provider = _extract_signals(w1)

    per_provider_thresholds = {
        r["provider"]: {
            "theta": args.theta if args.theta is not None else r["grant_spec"]["theta"],
            "theta_epistemic": (
                args.theta_epistemic
                if args.theta_epistemic is not None
                else r["grant_spec"]["theta_epistemic"]
            ),
        }
        for r in w1["providers"]
    }

    per_provider: dict[str, Any] = {}
    for provider, sig in signals_by_provider.items():
        theta = per_provider_thresholds[provider]["theta"]
        theta_e = per_provider_thresholds[provider]["theta_epistemic"]
        print(f"[w3] provider={provider} shape={sig.shape} theta={theta:.2f} theta_epi={theta_e:.2f}")
        res = _run_all(sig, compromise_step, theta, theta_e, prewarm=args.prewarm)
        res["_thresholds"] = {"theta": theta, "theta_epistemic": theta_e}
        per_provider[provider] = res

    payload = {
        "config": {
            **cfg,
            "prewarm": args.prewarm,
            "theta_override": args.theta,
            "theta_epistemic_override": args.theta_epistemic,
        },
        "per_provider": per_provider,
    }
    _plot(per_provider, compromise_step)
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload))
    print(f"[w3] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
