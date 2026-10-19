"""N00 - Audit of the submitted (final/) real-LLM streams and metric reconciliation.

Reviewer issues
---------------
* 14qA Q1, D1aZ Q1/Q2, Jqqf W3 - inconsistent E1 numbers (Naive 0.12 vs 1.00;
  TGCC 0.17 / 0.11 / 0.25).

Findings recorded here (from final/w1_multi_model/results.json and the LLM cache):
1. gpt-5 returned EMPTY text for most cached W1 calls (reasoning tokens consumed the
   max_completion_tokens budget).
2. probes.answer_matches("") returned True (empty string is a substring of every
   reference), so empty answers were scored CORRECT.
Both are fixed in this phase; every nextphase result uses the fixed code.
"""
from __future__ import annotations

import glob
import json

from tgcc.config import repo_root
from tgcc.nextphase.io import write_readme, write_results
from tgcc.probes import parse_answer

EXP = "n00_legacy_audit"


def run() -> dict:
    root = repo_root()
    w1 = json.loads((root / "final/w1_multi_model/results.json").read_text(encoding="utf-8"))
    prov = {}
    for p in w1["providers"]:
        turns = p["turns"]
        empty = [t for t in turns if not (t.get("answer") or "").strip()]
        prov[p["provider"]] = {
            "turns": len(turns),
            "empty_answers": len(empty),
            "empty_scored_correct": sum(1 for t in empty if t.get("correct")),
            "honest_turns": sum(1 for t in turns if t["phase"] == "honest"),
            "honest_empty": sum(1 for t in empty if t["phase"] == "honest"),
            "injected_sleeper_turns": sum(1 for t in turns if t.get("injected")),
            "reported_metrics": {k: p.get(k) for k in ("tgcc", "naive") if k in p},
        }
    cache = {}
    for name in ("anthropic", "azure_openai"):
        files = glob.glob(str(root / f"cache/llm/{name}/*.json"))
        texts = [json.loads(open(f, encoding="utf-8").read()).get("text", "") for f in files]
        cache[name] = {"entries": len(files), "empty": sum(1 for t in texts if not t.strip())}
    from tgcc.probes import answer_matches
    return {
        "w1_streams": prov,
        "llm_cache": cache,
        "matcher_check": {"answer_matches('', ['Paris']) after fix": answer_matches("", ["Paris"]),
                          "parse_answer('') ": parse_answer("")},
        "reconciliation": [
            {"paper": "Table 1 / Fig. 1 E1 TGCC 0.17, NoSyn 0.72, Naive 0.12 (60 Q, compromise 20)",
             "status": "Produced by E1 code that is not in the artifact; not reproducible. Naive 0.12 is "
                       "inconsistent with a gate that never revokes (latency = inf => OER = 1.00).",
             "replacement": "N01 (15 independent 60-Q episodes per provider)"},
            {"paper": "Table 9 / Table 8 E6 TGCC 0.11 [0.08, 0.25] (Claude), 0.07 (gpt-5)",
             "status": "Bootstrap MEAN over resamples of the single 20-turn W1 episode (compromise 8), "
                       "not the E1 episode; gpt-5 stream affected by findings 1-2.",
             "replacement": "N01 across-episode CIs; N03 for baselines"},
            {"paper": "Table 12 E9 baseline TGCC OER 0.25 (Claude)",
             "status": "Point estimate of the same single 20-turn W1 episode (12 post-compromise steps).",
             "replacement": "N01 / N03"},
        ],
    }


def readme(r) -> str:
    rows = "\n".join(f"| {p} | {v['turns']} | {v['empty_answers']} | {v['empty_scored_correct']} | {v['honest_empty']}/{v['honest_turns']} |"
                     for p, v in r["w1_streams"].items())
    c = "\n".join(f"| {p} | {v['entries']} | {v['empty']} |" for p, v in r["llm_cache"].items())
    rec = "\n".join(f"| {x['paper']} | {x['status']} | {x['replacement']} |" for x in r["reconciliation"])
    return f"""# N00 - Audit of submitted real-LLM streams and E1 number reconciliation

## Defects found in the submitted pipeline (fixed in this phase)
1. **Empty gpt-5 outputs.** gpt-5 is a reasoning model; with max_completion_tokens=200 and
   no reasoning_effort it spent the budget on hidden reasoning and returned empty text.
   Fix: reasoning_effort="minimal" (models.py). nextphase gpt-5 banks: 2 empty of 1,920.
2. **Empty answers scored correct.** answer_matches("") was True. Fix: empty never matches;
   reverse containment needs >= 3 characters (probes.py). nextphase uses a TriviaQA
   normalized-alias matcher (datasets.py).
3. **Baselines shared TGCC's thresholds** in W3/W6 (unfair to scalar baselines). Fix: every
   gate calibrated by the same Algorithm 2 on the same pilot (N03).
4. **In-sample FPR.** W1 calibrated thresholds on the honest prefix of the evaluated
   episode, so FPR = 0 by construction. Fix: separate 120-question pilot (N01).

## Submitted W1 streams
| Provider | turns | empty answers | empty scored correct | honest empty |
|---|---:|---:|---:|---:|
{rows}

## LLM cache shipped with the submission
| Provider | entries | empty text |
|---|---:|---:|
{c}

## Reconciliation of the E1 numbers questioned by reviewers
| Number in paper | What it actually is | Superseded by |
|---|---|---|
{rec}
"""


def main(argv=None) -> None:
    r = run()
    write_results(EXP, r)
    write_readme(EXP, readme(r))
    print(readme(r))


if __name__ == "__main__":
    main()
