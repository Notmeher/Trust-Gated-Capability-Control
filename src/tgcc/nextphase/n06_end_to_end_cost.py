"""N06 - End-to-end cost of trust signals (latency and tokens), not just controller compute.

Reviewer issue
--------------
RRLq W2 - the 10.8 us/agent figure excludes obtaining the trust signals; some
signals need an extra LLM critic call. End-to-end latency and token overhead.

Per agent step we decompose:
  agent LLM call | critic (alias match OR LLM judge call) | 4 heuristic probes |
  TGCC controller update.
LLM latencies/tokens are the measured values stored with each cached response
(original wall-clock of the API call, not cache-hit time).
"""
from __future__ import annotations

import json
import time

import numpy as np

from tgcc.controller import TGCCController
from tgcc.nextphase.datasets import tqa_match
from tgcc.nextphase.io import data_root, write_readme, write_results
from tgcc.nextphase.n04_critic_reliability import judge_path
from tgcc.nextphase.responses import PROVIDERS, available_banks, load_bank, model_name
from tgcc.probes import BehavioralProbe, InstitutionalProbe, RoleProbe, SocialProbe

EXP = "n06_end_to_end_cost"


def _q(x):
    x = np.asarray([v for v in x if v is not None], dtype=float)
    return {"median": float(np.median(x)), "p90": float(np.quantile(x, 0.9)), "mean": float(x.mean()),
            "n": int(x.size)} if x.size else {"median": float("nan"), "p90": float("nan"), "mean": float("nan"), "n": 0}


def micro(bank) -> dict:
    recs = list(bank["honest"].values())[:300]
    t0 = time.perf_counter()
    for r in recs:
        tqa_match(r["answer"], r["answers"])
    match_us = (time.perf_counter() - t0) / len(recs) * 1e6
    probes = (BehavioralProbe(), RoleProbe(), SocialProbe(), InstitutionalProbe())
    t0 = time.perf_counter()
    for r in recs:
        probes[0].score(r["text"]); probes[1].score(r["text"], []); probes[2].score(r["text"]); probes[3].score(r["text"])
    probe_us = (time.perf_counter() - t0) / len(recs) * 1e6
    ctrl = TGCCController()
    sig = np.random.default_rng(0).random((2000, 5))
    t0 = time.perf_counter()
    for s in sig:
        ctrl.step(list(s))
    ctrl_us = (time.perf_counter() - t0) / len(sig) * 1e6
    return {"alias_match_us": match_us, "probes_us": probe_us, "controller_us": ctrl_us}


def run() -> dict:
    out = {}
    for p in available_banks():
        bank = load_bank(p)
        recs = list(bank["honest"].values()) + list(bank["sleeper"].values())
        agent = {"latency_ms": _q([r["latency_ms"] for r in recs]),
                 "in_tokens": _q([r["in_tokens"] for r in recs]),
                 "out_tokens": _q([r["out_tokens"] for r in recs])}
        judges = {}
        for j in PROVIDERS:
            path = judge_path(j, p)
            if path.exists():
                v = list(json.loads(path.read_text(encoding="utf-8")).values())
                judges[j] = {"latency_ms": _q([x["latency_ms"] for x in v]),
                             "in_tokens": _q([x["in_tokens"] for x in v]),
                             "out_tokens": _q([x["out_tokens"] for x in v])}
        m = micro(bank)
        e2e = {"reference_critic_ms": agent["latency_ms"]["median"]
               + (m["alias_match_us"] + m["probes_us"] + m["controller_us"]) / 1000}
        for j, jj in judges.items():
            e2e[f"llm_judge_{model_name(j)}_ms"] = agent["latency_ms"]["median"] + jj["latency_ms"]["median"] \
                + (m["probes_us"] + m["controller_us"]) / 1000
            tot_agent = agent["in_tokens"]["mean"] + agent["out_tokens"]["mean"]
            tot_judge = jj["in_tokens"]["mean"] + jj["out_tokens"]["mean"]
            e2e[f"token_overhead_{model_name(j)}"] = tot_judge / tot_agent
        code = data_root() / f"code_bank_{p}.json"
        code_cost = None
        if code.exists():
            cb = json.loads(code.read_text(encoding="utf-8"))
            T = list(cb["tasks"].values())
            code_cost = {"coder_ms": _q([t[ph]["latency_ms"] for t in T for ph in ("honest", "sleeper")]),
                         "reviewer_ms": _q([t[ph]["review_ms"] for t in T for ph in ("honest", "sleeper")]),
                         "planner_ms": _q([t["plan_ms"] for t in T])}
        out[p] = {"model": bank["model"], "agent_call": agent, "judge_call": judges,
                  "microbench_us": m, "end_to_end_per_step": e2e, "code_pipeline": code_cost}
    return out


def readme(res) -> str:
    blocks = []
    for p, r in res.items():
        a, m, e = r["agent_call"], r["microbench_us"], r["end_to_end_per_step"]
        jl = "\n".join(f"| LLM judge call ({model_name(j)}) | {v['latency_ms']['median']:.0f} ms (p90 {v['latency_ms']['p90']:.0f}) "
                       f"| {v['in_tokens']['mean']:.0f} in / {v['out_tokens']['mean']:.0f} out |"
                       for j, v in r["judge_call"].items())
        el = "\n".join(f"| {k} | {v:.1f}{'' if k.startswith('token') else ' ms'} |" for k, v in e.items())
        cc = ""
        if r["code_pipeline"]:
            c = r["code_pipeline"]
            cc = (f"\nCode pipeline: planner {c['planner_ms']['median']:.0f} ms, coder {c['coder_ms']['median']:.0f} ms, "
                  f"reviewer {c['reviewer_ms']['median']:.0f} ms (medians); unit-test critic runs in a subprocess (~50-100 ms).\n")
        blocks.append(f"""### {model_name(p)}
| Component | Latency | Tokens |
|---|---|---|
| agent LLM call | {a['latency_ms']['median']:.0f} ms (p90 {a['latency_ms']['p90']:.0f}) | {a['in_tokens']['mean']:.0f} in / {a['out_tokens']['mean']:.0f} out |
{jl}
| alias-match critic | {m['alias_match_us']:.1f} us | 0 |
| 4 heuristic probes | {m['probes_us']:.1f} us | 0 |
| TGCC controller step | {m['controller_us']:.1f} us | 0 |

End-to-end per agent step (median agent call + critic + probes + controller):

| Quantity | Value |
|---|---|
{el}
{cc}""")
    return f"""# End-to-end cost of obtaining trust signals

The controller step costs microseconds; the dominant cost is the critic. With a
reference-based check (string match, unit tests) the overhead over the agent call is
negligible. A reference-free LLM-judge critic adds a second LLM call per step
(latency and token overhead below), roughly doubling per-step cost.

{chr(10).join(blocks)}
"""


def main(argv=None) -> None:
    res = run()
    write_results(EXP, {"providers": res})
    write_readme(EXP, readme(res))
    print(readme(res))


if __name__ == "__main__":
    main()
