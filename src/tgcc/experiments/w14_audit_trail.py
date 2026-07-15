"""W14: Audit trail / revocation report schema.

A security controller must justify its decisions.  This experiment emits a
structured JSON "revocation report" whenever TGCC denies a capability,
listing which layer's effective trust crossed which threshold and by how
much.  Reports are validated against a Pydantic schema so that downstream
tools (SIEMs, compliance dashboards) can consume them safely.
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Optional

import numpy as np
from pydantic import BaseModel, Field

from tgcc.controller import GrantSpec, LAYER_NAMES, TGCCController
from tgcc.reporting import write_readme, write_results

EXPERIMENT = "w14_audit_trail"


class LayerBreakdown(BaseModel):
    name: str
    raw_trust: float = Field(ge=0.0, le=1.0)
    effective_trust: float = Field(ge=0.0, le=1.0)
    threshold: Optional[float] = None
    below_threshold: bool
    weight: float = Field(ge=0.0, le=1.0)


class RevocationReport(BaseModel):
    step: int
    capability: str
    composite: float = Field(ge=0.0, le=1.0)
    composite_threshold: float
    composite_below_threshold: bool
    responsible_layers: list[str]
    layers: list[LayerBreakdown]
    granted: bool


def _report(step: int, spec: GrantSpec, state, granted: bool) -> RevocationReport:
    layers = []
    for i, name in enumerate(LAYER_NAMES):
        threshold = None
        below = False
        if i in spec.prereq_layers:
            idx = spec.prereq_layers.index(i)
            threshold = spec.theta_layer[idx]
            below = float(state.effective[i]) < threshold
        layers.append(
            LayerBreakdown(
                name=name,
                raw_trust=float(state.trusts[i]),
                effective_trust=float(state.effective[i]),
                threshold=threshold,
                below_threshold=below,
                weight=float(state.weights[i]),
            )
        )
    composite_below = float(state.composite) < spec.theta
    responsible = [ell.name for ell in layers if ell.below_threshold]
    if composite_below and "composite" not in responsible:
        responsible.append("composite")
    return RevocationReport(
        step=step,
        capability=spec.name,
        composite=float(state.composite),
        composite_threshold=float(spec.theta),
        composite_below_threshold=composite_below,
        responsible_layers=responsible,
        layers=layers,
        granted=granted,
    )


def _episode(seed: int, n_turns: int, compromise_step: int) -> list[RevocationReport]:
    rng = np.random.default_rng(seed)
    honest = np.array([0.92, 0.88, 0.82, 0.78, 0.90])
    sleeper = np.array([0.30, 0.88, 0.82, 0.78, 0.90])
    ctrl = TGCCController()
    ctrl.prewarm([0.90] * 5, effective_count=40.0)
    spec = GrantSpec("write_to_ehr", theta=0.40, prereq_layers=(0,),
                     theta_layer=(0.25,))
    reports = []
    for t in range(n_turns):
        rho = honest if t < compromise_step else sleeper
        signals = (rng.random(5) < rho).astype(float)
        st = ctrl.step(signals.tolist())
        g = ctrl.grant(st, spec)
        reports.append(_report(t, spec, st, g))
    return reports


def _readme(payload: dict) -> str:
    sample = payload["sample_reports"][0]
    return f"""# W14 - Audit trail / revocation report

## Weakness addressed
**W14**: A security controller must justify its decisions.  Reviewers
demand a structured audit trail that downstream tools (SIEMs, compliance
dashboards, incident-response scripts) can consume without ad-hoc parsing.

## Method
Every TGCC decision is packaged as a `RevocationReport` (Pydantic model,
`src/tgcc/experiments/w14_audit_trail.py`).  Fields:

* `step` -- monotonic interaction step.
* `capability` -- the capability under consideration.
* `composite` / `composite_threshold` / `composite_below_threshold`.
* `responsible_layers` -- names of the layers below their thresholds,
  including a symbolic `"composite"` marker when the composite itself is
  below `theta_c`.
* `layers[]` -- full per-layer breakdown (raw trust, effective trust,
  threshold if any, Boolean `below_threshold`, adaptive weight).
* `granted` -- final Boolean decision.

The controller emits one report per step; consumers filter for
`granted == False` to obtain the revocation stream.

## Sample report (step {sample['step']})
```json
{json.dumps(sample, indent=2)}
```

## Coverage
* `{payload['stats']['total']}` reports emitted for a 300-step episode.
* `{payload['stats']['revocations']}` of them are revocations.
* Every report validates against the Pydantic schema (JSON schema
  auto-generated below).

## JSON schema (excerpt)
```json
{json.dumps(payload['schema'], indent=2)[:2000]}
```

## Files
- `results.json` - full report stream + schema + summary statistics.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--n-turns", type=int, default=300)
    parser.add_argument("--compromise-step", type=int, default=80)
    args = parser.parse_args()
    reports = _episode(args.seed, args.n_turns, args.compromise_step)
    reports_json = [r.model_dump() for r in reports]
    stats = {
        "total": len(reports),
        "revocations": int(sum(1 for r in reports if not r.granted)),
        "grants": int(sum(1 for r in reports if r.granted)),
    }
    payload = {
        "config": {"seed": args.seed, "n_turns": args.n_turns,
                   "compromise_step": args.compromise_step},
        "schema": RevocationReport.model_json_schema(),
        "sample_reports": reports_json[:5],
        "revocation_stream": [r for r in reports_json if not r["granted"]],
        "stats": stats,
    }
    write_results(EXPERIMENT, payload)
    write_readme(EXPERIMENT, _readme(payload))
    print(f"[w14] done -> final/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
