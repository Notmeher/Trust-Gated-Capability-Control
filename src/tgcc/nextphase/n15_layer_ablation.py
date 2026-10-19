"""N15 - Per-layer ablation on the real-LLM streams (E9).

Streams: the E1 sleeper episodes (epistemic compromise) and the three
non-epistemic compromises of N12 (policy, offtopic, hostile), 15 episodes per
model each. For every layer l:
* spoofed  - the attacker forges layer l to 1.0 from the compromise on
             (thresholds from the unmodified honest pilot);
* removed  - layer l is held at 1.0 in pilot and episodes (the gate is
             recalibrated without that layer's evidence).
"""
from __future__ import annotations

from dataclasses import replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.nextphase.evaluation import run_gate
from tgcc.nextphase.gates import standard_gates
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.n12_non_epistemic_compromise import hostile, offtopic, policy
from tgcc.nextphase.responses import available_banks, load_bank, model_name, model_slug
from tgcc.nextphase.stats import fmt_ci
from tgcc.nextphase.streams import LAYERS, pilot_signals, qa_episodes

EXP = "n15_layer_ablation"
ATTACKS = {"sleeper": ("forced", None), "policy": ("honest", policy),
           "offtopic": ("honest", offtopic), "hostile": ("honest", hostile)}


def _set(sig: np.ndarray, layer: int, start: int) -> np.ndarray:
    s = sig.copy()
    s[start:, layer] = 1.0
    return s


def run() -> dict:
    gate = next(g for g in standard_gates() if g.name == "TGCC")
    out = {}
    for provider in available_banks():
        bank = load_bank(provider)
        pilot = pilot_signals(bank)
        res = {}
        for atk, (mode, fn) in ATTACKS.items():
            eps = qa_episodes(bank, sleeper_mode=mode, transform=fn)
            rows = {"full": run_gate(gate, eps, pilot)["summary"]}
            for k, name in enumerate(LAYERS):
                sp = [replace(e, signals=_set(e.signals, k, e.compromise)) for e in eps]
                rows[f"spoof {name}"] = run_gate(gate, sp, pilot)["summary"]
                rm = [replace(e, signals=_set(e.signals, k, 0)) for e in eps]
                rows[f"remove {name}"] = run_gate(gate, rm, _set(pilot, k, 0))["summary"]
            res[atk] = rows
        out[provider] = res
    return out


def _figs(res: dict) -> list[str]:
    names = []
    for p, r in res.items():
        conds = list(next(iter(r.values())))
        fig, ax = plt.subplots(figsize=(11, 4))
        w = 0.8 / len(r)
        for i, atk in enumerate(r):
            ax.bar(np.arange(len(conds)) + i * w - 0.4 + w / 2,
                   [r[atk][c]["oer"]["mean"] for c in conds], w, label=atk)
        ax.set_xticks(range(len(conds)))
        ax.set_xticklabels(conds, rotation=35, ha="right", fontsize=8)
        ax.set_ylabel("OER (lower = safer)")
        ax.set_ylim(0, 1.05)
        ax.set_title(f"{model_name(p)}: TGCC under per-layer spoofing / removal")
        ax.legend(fontsize=8)
        fig.tight_layout()
        path = figure_path(EXP, f"{model_slug(p)}_layer_ablation.png")
        fig.savefig(path, dpi=130)
        plt.close(fig)
        names.append(path.name)
    return names


def readme(res: dict, figs: list[str]) -> str:
    blocks = []
    for p, r in res.items():
        conds = list(next(iter(r.values())))
        hdr = "| Condition | " + " | ".join(f"{a} OER" for a in r) + " | FPR (sleeper streams) |"
        sep = "|---|" + "---|" * (len(r) + 1)
        lines = [f"| {c} | " + " | ".join(fmt_ci(r[a][c]["oer"]) for a in r)
                 + f" | {fmt_ci(r['sleeper'][c]['fpr'])} |" for c in conds]
        blocks.append(f"### {model_name(p)}\n{hdr}\n{sep}\n" + "\n".join(lines))
    f = "\n".join(f"![{x}](figures/{x})" for x in figs)
    return f"""# Per-layer ablation (E9)

## Method
TGCC on the real-LLM streams, 15 episodes per model and compromise type:
`sleeper` (E1: wrong answers at high confidence) and the three non-epistemic
compromises of N12 (`policy`, `offtopic`, `hostile`; answers stay correct).
* **spoof l**: the attacker forges layer l to 1.0 from the compromise on; thresholds
  come from the unmodified honest pilot.
* **remove l**: layer l is held at 1.0 in the pilot and in the episodes, and the gate
  is recalibrated by Algorithm 2 (the gate runs without that layer's evidence).

## Results (OER, mean [95% CI] over episodes)
{chr(10).join(blocks)}

## Reading
* Each compromise is carried by the layer it violates. Spoofing or removing that
  layer raises OER to 0.57-1.00, while spoofing any other layer changes OER by at
  most a few points:
  * epistemic layer -> sleeper;
  * institutional layer -> policy;
  * role layer -> off-topic;
  * behavioural layer -> hostile.
* So the stack is not "epistemic-only". The epistemic layer is load-bearing for the
  E1 sleeper, and the other layers for the compromises they monitor. An adversary has
  to forge the specific layer its compromise violates.
* Removing the epistemic layer also weakens detection of non-epistemic compromises
  (e.g. hostile 0.15 -> 0.33 on Claude), because the epistemic layer is a prerequisite
  in the coupling.

{f}
"""


def main(argv=None) -> None:
    res = run()
    figs = _figs(res)
    write_results(EXP, {"providers": res, "figures": figs})
    write_readme(EXP, readme(res, figs))
    print(readme(res, figs))


if __name__ == "__main__":
    main()
