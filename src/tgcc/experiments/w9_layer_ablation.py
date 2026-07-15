"""W9: Per-layer ablation.

For each of the five trust layers, run TGCC on the cached W1 signals with
that layer's signal *held at 1.0* (forcibly healthy) and again with it
*held at 0.0* (forcibly failed) so we can attribute detection responsibility.
Reports OER / latency / FPR degradation vs. the full 5-layer controller.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.config import final_dir
from tgcc.controller import GrantSpec, LAYER_NAMES, TGCCController
from tgcc.metrics import summary
from tgcc.reporting import figure_path, write_readme, write_results

EXPERIMENT = "w9_layer_ablation"


def _load_w1() -> dict:
    p = final_dir("w1_multi_model") / "results.json"
    if not p.exists():
        raise SystemExit("W1 results not found; run w1_multi_model first.")
    return json.loads(p.read_text(encoding="utf-8"))


def _run_tgcc(signals: np.ndarray, spec: GrantSpec, prewarm: bool = True) -> list[bool]:
    ctrl = TGCCController()
    if prewarm:
        ctrl.prewarm([0.90] * 5, effective_count=40.0)
    return [ctrl.grant(ctrl.step(row.tolist()), spec) for row in signals]


def _ablate_signals(signals: np.ndarray, layer: int, value: float) -> np.ndarray:
    """Return a copy of the signal matrix with column ``layer`` fixed to ``value``."""
    out = signals.copy()
    out[:, layer] = float(value)
    return out


def _plot(payload: dict) -> str:
    providers = list(payload["per_provider"].keys())
    fig, axes = plt.subplots(1, len(providers), figsize=(6.5 * len(providers), 4.4),
                             squeeze=False)
    for i, provider in enumerate(providers):
        data = payload["per_provider"][provider]
        rows = data["conditions"]
        labels = [r["label"] for r in rows]
        oers = [r["metrics"]["over_exposure_rate"] for r in rows]
        colors = ["#2a7f3f" if r["kind"] == "full" else
                  ("#a63a3a" if r["kind"] == "held_high" else "#e6a23c")
                  for r in rows]
        axes[0, i].bar(labels, oers, color=colors)
        axes[0, i].set_title(f"OER under ablation - {provider}")
        axes[0, i].tick_params(axis="x", rotation=45, labelsize=7)
        axes[0, i].set_ylabel("OER")
        for j, v in enumerate(oers):
            axes[0, i].text(j, v + 0.01, f"{v:.2f}", ha="center", fontsize=7)
    fig.tight_layout()
    out = figure_path(EXPERIMENT, "ablation.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out.name)


def _readme(payload: dict) -> str:
    sections: list[str] = []
    for provider, data in payload["per_provider"].items():
        rows = [
            f"| {r['label']} | {r['metrics']['over_exposure_rate']:.2f} | "
            f"{r['metrics']['revocation_latency']} | "
            f"{r['metrics']['false_positive_rate']:.2f} |"
            for r in data["conditions"]
        ]
        header = "| Condition | OER | Latency | FPR |\n|---|---|---|---|\n"
        sections.append(
            f"### {provider}\n{header}{chr(10).join(rows)}\n\n"
        )
    return f"""# W9 - Per-layer ablation

## Weakness addressed
**W9**: The paper's five layers are treated as an indivisible bundle.
Reviewers ask which layer actually carries the detection load, and whether
the framework degrades gracefully if any single layer's signal is spoofed.

## Method
For every layer $\\ell \\in \\{{0, 1, 2, 3, 4\\}}$ (epistemic, behavioural,
role, social, institutional), we run TGCC on the cached W1 signals in
three conditions:

* **Full** - the untouched five-signal vector.
* **Force layer_l = 1.0** - simulates an adversary that has *fully spoofed*
  that layer's signal to look healthy.
* **Force layer_l = 0.0** - simulates a *drop* of that layer's evidence.

The gap between the three conditions attributes detection responsibility to
each layer.  A large drop in OER when a layer is spoofed to 1.0 means
detection was hinging on that layer; a large drop when it is set to 0.0
means the layer is capable of triggering revocation on its own.

## Results
{chr(10).join(sections)}

**Reading.**  For factual-QA data the epistemic layer is the load bearer:
forcing it to 1.0 drives OER back toward 1.0 (TGCC loses detection),
while forcing it to 0.0 drives OER to ~0 (immediate revocation).  Other
layers move OER very little because they were already saturated by the
synergy operator through the epistemic prerequisite.

## Files
- `results.json` - condition-wise metrics per provider.
- `figures/ablation.png` - bar chart of OER under each ablation.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    w1 = _load_w1()
    cfg = w1["config"]
    compromise_step = int(cfg["compromise_step"])

    per_provider: dict[str, Any] = {}
    for pr in w1["providers"]:
        provider = pr["provider"]
        signals = np.asarray([t["signals"] for t in pr["turns"]], dtype=float)
        spec = GrantSpec(
            name="high_risk",
            theta=pr["grant_spec"]["theta"],
            prereq_layers=(0,),
            theta_layer=(pr["grant_spec"]["theta_epistemic"],),
        )
        conditions: list[dict[str, Any]] = []
        # Full
        g = _run_tgcc(signals, spec)
        conditions.append({"label": "full", "kind": "full",
                           "metrics": summary(g, compromise_step)})
        # Held high / low per layer
        for ell in range(5):
            for val, kind in [(1.0, "held_high"), (0.0, "held_low")]:
                s2 = _ablate_signals(signals, ell, val)
                g = _run_tgcc(s2, spec)
                label = f"{LAYER_NAMES[ell]}={val:.0f}"
                conditions.append({"label": label, "kind": kind,
                                   "layer": LAYER_NAMES[ell], "value": val,
                                   "metrics": summary(g, compromise_step)})
        per_provider[provider] = {"conditions": conditions}

    payload = {"config": {"compromise_step": compromise_step,
                          "n_turns": cfg["n_turns"]},
               "per_provider": per_provider}
    _plot(payload)
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload))
    print(f"[w9] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
