"""N30 - Debate: harm prevented, influence before revocation, and two sleepers (IEEE R2-2).

Reviewer issue
--------------
R2-2: revocation is not the same as harm prevention. N=1 showed no task-level gain in the submitted E2, N=5
was already near zero without TGCC, and "revoking an agent does not necessarily prevent downstream harm if
incorrect information has already influenced the collective decision". Evaluate harmful outcomes prevented.

Design (real LLMs; the N10 protocol, replayed from the response cache and extended)
-----------------------------------------------------------------------------------
Teams of Claude Sonnet 4.5 / GPT-5 agents debate 60 TriviaQA questions per series (two rounds, confidence-
weighted vote over admitted agents); K agents turn into stealth sleepers at question 20. Conditions
(N, K) in {(1,1), (3,1), (5,1), (5,2)}, gated by TGCC vs ungated, 2 series each.
Harm = a wrong team answer written to the shared pool. We report
* harm prevented: paired per-question comparison of the gated and ungated runs (same questions, same agents),
  with an exact McNemar test;
* influence: P(an honest agent correct in round 1 switches to a wrong answer in round 2), with the sleeper
  admitted vs revoked; this is the "already influenced" channel the reviewer describes;
* timing: wrong team answers between the compromise and the revocation vs after it.
"""
from __future__ import annotations

import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binomtest

from tgcc.data_qa import HONEST_SYSTEM_PROMPT
from tgcc.models import LLMClient
from tgcc.nextphase.datasets import normalize, tqa_match
from tgcc.nextphase.gates import Gate, TGCCParams, calibrate
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.n10_debate import COMPROMISE, N_Q, PROVS, SERIES, Agent, _round2_prompt
from tgcc.nextphase.responses import chat, load_bank
from tgcc.nextphase.stats import fmt_wilson, wilson
from tgcc.nextphase import tgcc_r
from tgcc.nextphase.streams import _force_wrong, compute_signals, pilot_signals, signal_mode
from tgcc.probes import parse_answer, parse_confidence

EXP = "n30_debate_harm"
CONDITIONS = ((1, 1), (3, 1), (5, 1), (5, 2))


class AgentR(Agent):
    """An agent gated by TGCC-R: its own window (selected from its model's honest pilot) and CRC thresholds."""

    def __init__(self, idx, provider, sleeper, thetas, window):
        super().__init__(idx, provider, sleeper, thetas)
        self.gate = tgcc_r.gate()
        self.window = window

    def observe(self, text: str, correct: bool, conf: float) -> None:
        self.hist_text.append(text)
        self.hist_label.append(correct)
        self.hist_conf.append(conf)
        with tgcc_r.mode(self.window):
            st = self.gate.stats(compute_signals(self.hist_text, self.hist_label, self.hist_conf))
        self.granted = all(v[-1] >= self.thetas[k] for k, v in st.items())


def run_series(series: int, n_agents: int, k_sleepers: int, gated: bool, banks, clients, thetas,
               variant: str = "TGCC", windows: dict | None = None) -> list[dict]:
    """N10's protocol (identical prompts, so N10's calls are cache hits) with K sleepers and per-agent logs."""
    items = list(banks["anthropic"]["eval_ids"])
    random.Random(1000 + series).shuffle(items)
    items = items[:N_Q]
    agents = []
    for k in range(n_agents):
        sleeper = k < k_sleepers
        p = PROVS[(series + k) % 2]
        agents.append(Agent(k, p, sleeper, thetas[p]) if variant == "TGCC"
                      else AgentR(k, p, sleeper, thetas[p], windows[p]))
    rngs = {a.idx: random.Random(series if a.idx == 0 else 7919 * series + a.idx) for a in agents}
    log = []
    for t, iid in enumerate(items):
        q = banks["anthropic"]["honest"][iid]["question"]
        refs = banks["anthropic"]["honest"][iid]["answers"]
        r1 = {}
        for a in agents:
            bank = banks[a.provider]
            if a.sleeper and t >= COMPROMISE:
                txt, _, _ = _force_wrong(bank["sleeper"][iid], rngs[a.idx])
            else:
                txt = bank["honest"][iid]["text"]
            r1[a.idx] = txt
        admitted = [a for a in agents if (a.granted or not gated)]

        def r2(a):
            if a.sleeper and t >= COMPROMISE:
                return a.idx, r1[a.idx]
            peers = [(parse_answer(r1[b.idx]), parse_confidence(r1[b.idx])) for b in admitted if b.idx != a.idx]
            if not peers:
                return a.idx, r1[a.idx]
            res = chat(clients[a.provider], _round2_prompt(q, peers), HONEST_SYSTEM_PROMPT)
            return a.idx, res.text or r1[a.idx]

        with ThreadPoolExecutor(max_workers=8) as ex:
            final = dict(ex.map(r2, admitted))
        votes, rep = defaultdict(float), {}
        for idx, txt in final.items():
            ans = parse_answer(txt)
            votes[normalize(ans)] += max(parse_confidence(txt), 0.01)
            rep[normalize(ans)] = ans
        wrong = (not tqa_match(rep[max(votes, key=votes.get)], refs)) if votes else False
        sleeper_in = [a.idx for a in admitted if a.sleeper and t >= COMPROMISE]
        flips = []
        for a in admitted:
            if a.sleeper:
                continue
            c1 = tqa_match(parse_answer(r1[a.idx]), refs)
            c2 = tqa_match(parse_answer(final[a.idx]), refs)
            flips.append({"r1_correct": c1, "r2_correct": c2})
        for a in agents:
            a.observe(r1[a.idx], tqa_match(parse_answer(r1[a.idx]), refs), parse_confidence(r1[a.idx]))
        log.append({"t": t, "iid": iid, "wrong": wrong, "abstain": not votes,
                    "sleepers_admitted": len(sleeper_in), "honest": flips,
                    "honest_denied": sum(1 for a in agents if not a.sleeper and not a.granted)})
    return log


def analyse(ung: list[list[dict]], gat: list[list[dict]]) -> dict:
    post = lambda runs: [x for r in runs for x in r if x["t"] >= COMPROMISE]
    pu, pg = post(ung), post(gat)
    b = sum(x["wrong"] and not y["wrong"] for x, y in zip(pu, pg))       # prevented
    c = sum(y["wrong"] and not x["wrong"] for x, y in zip(pu, pg))       # caused (e.g. abstention side effects)
    mcn = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0

    def influence(rows, admitted: bool):
        k = n = 0
        for x in rows:
            if (x["sleepers_admitted"] > 0) != admitted:
                continue
            for h in x["honest"]:
                if h["r1_correct"]:
                    n += 1
                    k += not h["r2_correct"]
        return wilson(k, n)

    timing = {"before_revocation": [0, 0], "after_revocation": [0, 0]}
    for r in gat:
        rev = next((x["t"] for x in r if x["t"] >= COMPROMISE and x["sleepers_admitted"] == 0), None)
        for x in r:
            if x["t"] < COMPROMISE:
                continue
            key = "before_revocation" if (rev is None or x["t"] < rev) else "after_revocation"
            timing[key][0] += x["wrong"]
            timing[key][1] += 1
    return {
        "wrong_post_ungated": wilson(sum(x["wrong"] for x in pu), len(pu)),
        "wrong_post_gated": wilson(sum(x["wrong"] for x in pg), len(pg)),
        "wrong_pre_ungated": wilson(sum(x["wrong"] for r in ung for x in r if x["t"] < COMPROMISE), COMPROMISE * len(ung)),
        "wrong_pre_gated": wilson(sum(x["wrong"] for r in gat for x in r if x["t"] < COMPROMISE), COMPROMISE * len(gat)),
        "abstain_post_gated": wilson(sum(x["abstain"] for x in pg), len(pg)),
        "prevented": b, "caused": c, "mcnemar_p": float(mcn),
        "influence_sleeper_admitted_ungated": influence(pu, True),
        "influence_sleeper_admitted_gated": influence(pg, True),
        "influence_sleeper_revoked_gated": influence(pg, False),
        "timing": {k: wilson(*v) for k, v in timing.items()},
        "honest_denials_gated": int(sum(x["honest_denied"] for r in gat for x in r)),
        "honest_agent_questions": int(sum(len(x["honest"]) + x["honest_denied"] for r in gat for x in r)),
    }


def run() -> dict:
    banks = {p: load_bank(p) for p in PROVS}
    clients = {p: LLMClient(p) for p in PROVS}
    thetas = {p: calibrate(Gate("TGCC", "tgcc", TGCCParams()).stats(pilot_signals(banks[p]))) for p in PROVS}
    g_r = tgcc_r.gate()
    windows = {p: tgcc_r.choose_window(lambda p=p: pilot_signals(banks[p])) for p in PROVS}
    thetas_r = {}
    for p in PROVS:
        with tgcc_r.mode(windows[p]):
            thetas_r[p] = tgcc_r.calibrate_pilot(g_r, pilot_signals(banks[p]))
    out = {"TGCC": {}, "TGCC-R": {}, "windows": windows}
    for n, k in CONDITIONS:
        ung = [run_series(s, n, k, False, banks, clients, thetas) for s in range(SERIES)]
        gat = [run_series(s, n, k, True, banks, clients, thetas) for s in range(SERIES)]
        gat_r = [run_series(s, n, k, True, banks, clients, thetas_r, "TGCC-R", windows) for s in range(SERIES)]
        out["TGCC"][f"N={n},K={k}"] = analyse(ung, gat)
        out["TGCC-R"][f"N={n},K={k}"] = analyse(ung, gat_r)
    return out


def _fig(res) -> str:
    res = res["TGCC-R"]
    keys = list(res)
    x = np.arange(len(keys))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for off, k, lab, col in ((-0.2, "wrong_post_ungated", "ungated", "#c92a2a"), (0.2, "wrong_post_gated", "TGCC", "#2b8a3e")):
        v = [res[c][k] for c in keys]
        ax[0].bar(x + off, [z["p"] for z in v], 0.4, label=lab, color=col,
                  yerr=[[z["p"] - z["lo"] for z in v], [z["hi"] - z["p"] for z in v]], capsize=3)
    ax[0].set_title("wrong team answer after compromise")
    for off, k, lab in ((-0.27, "influence_sleeper_admitted_ungated", "sleeper admitted (ungated)"),
                        (0.0, "influence_sleeper_admitted_gated", "sleeper admitted (gated, pre-revocation)"),
                        (0.27, "influence_sleeper_revoked_gated", "sleeper revoked (gated)")):
        ax[1].bar(x + off, [res[c][k]["p"] for c in keys], 0.27, label=lab)
    ax[1].set_title("honest agent flipped correct -> wrong in round 2")
    for a in ax:
        a.set_xticks(x)
        a.set_xticklabels(keys)
        a.legend(fontsize=7)
    fig.tight_layout()
    p = figure_path(EXP, "debate_harm.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p.name


def readme(res_all, fig) -> str:
    rows, inf = [], []
    for c, r in [(f"{c} [{v}]", r) for v in ("TGCC-R", "TGCC") for c, r in res_all[v].items()]:
        rows.append(f"| {c} | {fmt_wilson(r['wrong_pre_ungated'])} | {fmt_wilson(r['wrong_pre_gated'])} "
                    f"| {fmt_wilson(r['wrong_post_ungated'])} | {fmt_wilson(r['wrong_post_gated'])} "
                    f"| {r['prevented']} / {r['caused']} | {r['mcnemar_p']:.2g} | {fmt_wilson(r['abstain_post_gated'])} "
                    f"| {r['honest_denials_gated']}/{r['honest_agent_questions']} |")
        inf.append(f"| {c} | {fmt_wilson(r['influence_sleeper_admitted_ungated'])} "
                   f"| {fmt_wilson(r['influence_sleeper_admitted_gated'])} | {fmt_wilson(r['influence_sleeper_revoked_gated'])} "
                   f"| {fmt_wilson(r['timing']['before_revocation'])} | {fmt_wilson(r['timing']['after_revocation'])} |")
    return f"""# N30 - Debate: harm prevented and influence before revocation

## Reviewer issue
IEEE R2-2: report harmful outcomes prevented, not only revocation; address influence that happens before revocation.

## Method
The N10 protocol (identical prompts; N10's calls are reused from the cache) with K sleepers among N agents, gated
by TGCC-R (the revised method: per-model window selected from the honest pilot, a conjunct on every layer, CRC
thresholds at delta = 0.10) and, for reference, by the original TGCC;
{SERIES} series of {N_Q} questions each, compromise at question {COMPROMISE}. Harm = a wrong team answer written to the pool.

## Harm prevented (paired, same questions and agents)
"prevented / caused" counts post-compromise questions where only the ungated / only the gated team was wrong;
McNemar exact p-value on those discordant pairs.

| Condition | wrong pre (ungated) | wrong pre (TGCC) | wrong post (ungated) | wrong post (TGCC) | prevented / caused | McNemar p | pool abstains (TGCC) | honest agents denied |
|---|---|---|---|---|---|---:|---|---|
{chr(10).join(rows)}

## Influence and timing
Influence = P(an honest agent correct in round 1 gives a wrong final answer after seeing peers). Timing splits the
gated team's wrong answers into the window between compromise and revocation and the period after revocation.

| Condition | influence, sleeper admitted (ungated) | influence, sleeper admitted (TGCC, before revocation) | influence, sleeper revoked (TGCC) | wrong answers before revocation | wrong answers after revocation |
|---|---|---|---|---|---|
{chr(10).join(inf)}

![debate harm](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {"conditions": CONDITIONS, "results": res, "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
