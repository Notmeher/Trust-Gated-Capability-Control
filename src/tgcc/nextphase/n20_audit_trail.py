"""N20 - Audit trail (E14): one schema-validated decision report per step.

Runs TGCC on the real E1 sleeper episodes and emits, for every step, which
conjunct (per-turn epistemic check, composite) denied the capability, by how much,
and the per-layer state (signal, Beta trust, effective trust, Hedge weight),
together with the agent's answer and the critic's verdict.
"""
from __future__ import annotations

import json
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field

from tgcc.controller import TGCCController
from tgcc.nextphase.gates import PREWARM_N, PREWARM_RHO, calibrate, grants, standard_gates
from tgcc.nextphase.io import write_readme, write_results
from tgcc.nextphase.responses import available_banks, load_bank, model_name
from tgcc.nextphase.streams import LAYERS, pilot_signals, qa_episodes
from tgcc.probes import parse_answer

EXP = "n20_audit_trail"
CAPABILITY = "high_risk_action"


class LayerState(BaseModel):
    name: str
    signal: float = Field(ge=0.0, le=1.0)
    trust: float = Field(ge=0.0, le=1.0)
    effective_trust: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)


class Conjunct(BaseModel):
    name: str
    value: float
    threshold: float
    margin: float
    passed: bool


class DecisionReport(BaseModel):
    episode: int
    step: int
    capability: str
    granted: bool
    denied_by: list[str]
    conjuncts: list[Conjunct]
    layers: list[LayerState]
    answer: str
    stated_confidence: float = Field(ge=0.0, le=1.0)
    critic_correct: bool
    agent_compromised: Optional[bool] = None


def reports(ep, th: dict) -> list[DecisionReport]:
    gate = next(g for g in standard_gates() if g.name == "TGCC")
    P = gate.params
    ctrl = TGCCController(p=P.p, gamma=P.gamma, omega=P.omega, eta=P.eta, lam=P.lam, coupling=P.matrix())
    ctrl.prewarm([PREWARM_RHO] * 5, PREWARM_N)
    out = []
    for t, s in enumerate(ep.signals):
        st = ctrl.step(list(s))
        cj = [Conjunct(name=k, value=float(v), threshold=float(th[k]), margin=float(v - th[k]), passed=bool(v >= th[k]))
              for k, v in (("composite", st.composite), ("epistemic", s[0]))]
        out.append(DecisionReport(
            episode=ep.index, step=t, capability=CAPABILITY, granted=all(c.passed for c in cj),
            denied_by=[c.name for c in cj if not c.passed], conjuncts=cj,
            layers=[LayerState(name=n, signal=float(s[i]), trust=float(st.trusts[i]),
                               effective_trust=float(st.effective[i]), weight=float(st.weights[i]))
                    for i, n in enumerate(LAYERS)],
            answer=parse_answer(ep.texts[t]), stated_confidence=float(ep.conf[t]),
            critic_correct=bool(ep.label[t]), agent_compromised=bool(ep.sleeper[t])))
    return out


def run() -> dict:
    gate = next(g for g in standard_gates() if g.name == "TGCC")
    out = {}
    for provider in available_banks():
        bank = load_bank(provider)
        th = calibrate(gate.stats(pilot_signals(bank)))
        eps = qa_episodes(bank)
        reps = [r for ep in eps for r in reports(ep, th)]
        # Consistency check: the report decisions equal the gate's decisions.
        ref = np.concatenate([grants(gate.stats(ep.signals), th) for ep in eps])
        assert np.array_equal(ref, np.array([r.granted for r in reps]))
        den = [r for r in reps if not r.granted]
        first = [next((r for r in reps if r.episode == ep.index and r.agent_compromised and not r.granted), None)
                 for ep in eps]
        out[provider] = {
            "thetas": th,
            "n_reports": len(reps),
            "n_denials": len(den),
            "denied_by": {k: sum(1 for r in den if r.denied_by == k.split("+"))
                          for k in ("epistemic", "composite", "composite+epistemic")},
            "first_revocations": [r.model_dump() for r in first if r is not None],
            "denial_stream_ep0": [r.model_dump() for r in den if r.episode == 0],
            "all_valid": all(isinstance(DecisionReport.model_validate(r.model_dump()), DecisionReport) for r in reps),
        }
    return out


def readme(res: dict) -> str:
    blocks = []
    for p, r in res.items():
        d = r["denied_by"]
        blocks.append(f"### {model_name(p)}\n"
                      f"{r['n_reports']} reports (15 episodes x 60 steps), {r['n_denials']} denials: "
                      f"epistemic check only {d['epistemic']}, composite only {d['composite']}, "
                      f"both {d['composite+epistemic']}. All reports validate against the schema: {r['all_valid']}.\n\n"
                      "First revocation after the compromise (episode 0):\n```json\n"
                      + json.dumps(r["first_revocations"][0], indent=2) + "\n```")
    schema = json.dumps(DecisionReport.model_json_schema(), indent=2)
    return f"""# Audit trail (E14)

## Method
TGCC runs on the real E1 sleeper episodes (15 per model) and emits one
`DecisionReport` per step (Pydantic schema below): the decision, which conjunct
denied it (per-turn epistemic check and/or composite) with value, threshold and
margin, the per-layer state (signal, Beta trust, effective trust, Hedge weight),
the agent's answer and stated confidence, and the critic's verdict. A consistency
check asserts that every report's decision equals the gate's decision.

## Results
{chr(10).join(blocks)}

## Schema
```json
{schema}
```
"""


def main(argv=None) -> None:
    res = run()
    write_results(EXP, {"providers": res, "schema": DecisionReport.model_json_schema()})
    write_readme(EXP, readme(res))
    print(readme(res)[:3000])


if __name__ == "__main__":
    main()
