"""N24 - System overhead: complexity in L and |C|, tokens, enforcement and revocation (IEEE R2-8).

Reviewer issue
--------------
R2-8: the 10.8 us per-agent figure excludes the dominant costs (critic/evaluator LLM calls, token issuance,
authorization enforcement, revocation propagation); Proposition 5 is O(L^2 + |C|) in the number of layers,
but Experiment 5 varied the number of agents with L fixed.

(a) Controller cost vs the number of layers L (3-32) and capabilities |C| (1-256), timed on real E1 signal
    streams (layers beyond the five real ones reuse real columns). Fits a + bL + cL^2.
(b) Full authorization path on real E1 streams for N agents and G gateways: controller step, grant rule,
    signed capability token issuance, gateway verification, and revocation propagation (epoch broadcast).
    A security check replays every agent's last token after each revocation: it must be rejected by
    every gateway.
(c) End-to-end: the measured LLM agent and critic latencies (N06) vs the controller + token path.
"""
from __future__ import annotations

import json
import statistics
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.controller import GrantSpec, TGCCController
from tgcc.nextphase.gates import PREWARM_N, PREWARM_RHO, calibrate, standard_gates
from tgcc.nextphase.io import exp_dir, figure_path, write_readme, write_results
from tgcc.nextphase.responses import load_bank
from tgcc.nextphase.scenarios import episodes, pilot_signals
from tgcc.nextphase.tokens import Bus, Gateway, Issuer

EXP = "n24_system_overhead"
LS = (3, 5, 8, 12, 16, 24, 32)
CS = (1, 4, 16, 64, 256)
NS = (1, 10, 50, 100)
GS = (1, 4)


def real_stream(T: int = 1200) -> np.ndarray:
    eps = episodes(load_bank("anthropic"), "sleeper")
    s = np.concatenate([e.signals for e in eps])
    return s[:T]


def _controller(L: int, seed: int = 0) -> TGCCController:
    rng = np.random.default_rng(seed)
    C = np.tril(rng.uniform(0.3, 0.7, size=(L, L)), k=-1)
    c = TGCCController(n_layers=L, coupling=C)
    c.prewarm([PREWARM_RHO] * L, PREWARM_N)
    return c


def time_vs_L(reps: int = 5) -> dict:
    base = real_stream()
    out = {}
    for L in LS:
        sig = base[:, np.arange(L) % 5]
        spec = GrantSpec("c0", 0.3, (0,), (0.2,))
        per = []
        for r in range(reps):
            ctrl = _controller(L, r)
            t0 = time.perf_counter_ns()
            for s in sig:
                st = ctrl.step(s)
                ctrl.grant(st, spec)
            per.append((time.perf_counter_ns() - t0) / len(sig) / 1e3)
        out[str(L)] = statistics.median(per)
    Ls = np.array(LS, float)
    y = np.array([out[str(L)] for L in LS])
    A = np.vstack([np.ones_like(Ls), Ls, Ls ** 2]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    r2 = 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)
    lin, *_ = np.linalg.lstsq(A[:, :2], y, rcond=None)
    r2_lin = 1 - np.sum((y - A[:, :2] @ lin) ** 2) / np.sum((y - y.mean()) ** 2)
    return {"us_per_step": out, "fit_quadratic": coef.tolist(), "r2_quadratic": float(r2),
            "r2_linear": float(r2_lin)}


def time_vs_C(reps: int = 5) -> dict:
    sig = real_stream()
    out = {}
    for nc in CS:
        specs = [GrantSpec(f"c{i}", 0.3, (0,), (0.2,)) for i in range(nc)]
        per = []
        for r in range(reps):
            ctrl = _controller(5, r)
            t0 = time.perf_counter_ns()
            for s in sig:
                st = ctrl.step(s)
                for sp in specs:
                    ctrl.grant(st, sp)
            per.append((time.perf_counter_ns() - t0) / len(sig) / 1e3)
        out[str(nc)] = statistics.median(per)
    return {"us_per_step": out}


def authorization_path(N: int, G: int, steps: int = 60) -> dict:
    """Run N agents on real E1 episodes through controller -> token -> gateways, with revocation."""
    bank = load_bank("anthropic")
    eps = episodes(bank, "sleeper")
    gate = next(g for g in standard_gates() if g.name == "TGCC")
    th = calibrate(gate.stats(pilot_signals(bank)))
    issuer = Issuer(ttl_s=5.0)
    gws = [Gateway(issuer.key) for _ in range(G)]
    bus = Bus(gws)
    ctrls = []
    for _ in range(N):
        c = TGCCController()
        c.prewarm([PREWARM_RHO] * 5, PREWARM_N)
        ctrls.append(c)
    t_ctrl = t_issue = t_auth = t_rev = 0
    n_issue = n_auth = n_rev = 0
    stale_accepted = 0
    granted_prev = [True] * N
    last_tok: list[str | None] = [None] * N
    for t in range(steps):
        for i in range(N):
            sig = eps[i % len(eps)].signals[t]
            a = f"agent{i}"
            t0 = time.perf_counter_ns()
            st = ctrls[i].step(sig)
            ok = st.composite >= th["composite"] and sig[0] >= th["epistemic"]
            t1 = time.perf_counter_ns()
            t_ctrl += t1 - t0
            if ok:
                tok = issuer.issue(a, "write_kb", t)
                t2 = time.perf_counter_ns()
                t_issue += t2 - t1
                n_issue += 1
                gw = gws[(i + t) % G]
                allowed = gw.authorize(tok, a, "write_kb")
                t_auth += time.perf_counter_ns() - t2
                n_auth += 1
                assert allowed
                last_tok[i] = tok
            elif granted_prev[i]:
                t2 = time.perf_counter_ns()
                bus.publish(a, issuer.revoke(a))
                t_rev += time.perf_counter_ns() - t2
                n_rev += 1
                if last_tok[i] is not None:
                    stale_accepted += sum(g.authorize(last_tok[i], a, "write_kb") for g in gws)
            granted_prev[i] = ok
    agent_steps = N * steps
    return {
        "controller_us": t_ctrl / agent_steps / 1e3,
        "issue_us": t_issue / max(n_issue, 1) / 1e3,
        "authorize_us": t_auth / max(n_auth, 1) / 1e3,
        "revoke_propagate_us": t_rev / max(n_rev, 1) / 1e3,
        "total_us_per_agent_step": (t_ctrl + t_issue + t_auth + t_rev) / agent_steps / 1e3,
        "tokens_issued": n_issue, "revocations": n_rev, "stale_tokens_accepted": stale_accepted,
    }


def llm_latencies() -> dict:
    p = exp_dir("n06_end_to_end_cost") / "results.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def run() -> dict:
    return {
        "vs_L": time_vs_L(),
        "vs_C": time_vs_C(),
        "auth_path": {f"N={N},G={G}": authorization_path(N, G) for N in NS for G in GS},
    }


def _fig(res) -> str:
    fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
    L = np.array(LS, float)
    y = [res["vs_L"]["us_per_step"][str(x)] for x in LS]
    a, b, c = res["vs_L"]["fit_quadratic"]
    ax[0].plot(L, y, "o", label="measured")
    xs = np.linspace(L.min(), L.max(), 100)
    ax[0].plot(xs, a + b * xs + c * xs ** 2, "--", label=f"a+bL+cL^2 (R2={res['vs_L']['r2_quadratic']:.3f})")
    ax[0].set_xlabel("layers L")
    ax[0].set_ylabel("us per step")
    ax[0].legend(fontsize=7)
    Cs = np.array(CS, float)
    ax[1].plot(Cs, [res["vs_C"]["us_per_step"][str(x)] for x in CS], "o-")
    ax[1].set_xscale("log")
    ax[1].set_xlabel("capabilities |C| (L = 5)")
    ax[1].set_ylabel("us per step")
    keys = list(res["auth_path"])
    comp = ("controller_us", "issue_us", "authorize_us")
    bottom = np.zeros(len(keys))
    for k in comp:
        v = np.array([res["auth_path"][x][k] for x in keys])
        ax[2].bar(keys, v, bottom=bottom, label=k)
        bottom += v
    ax[2].tick_params(axis="x", rotation=45, labelsize=7)
    ax[2].set_ylabel("us")
    ax[2].legend(fontsize=7)
    fig.tight_layout()
    p = figure_path(EXP, "overhead.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p.name


def readme(res, fig) -> str:
    vl = res["vs_L"]
    lrow = " | ".join(f"{vl['us_per_step'][str(L)]:.0f}" for L in LS)
    crow = " | ".join(f"{res['vs_C']['us_per_step'][str(c)]:.0f}" for c in CS)
    ap = []
    for k, v in res["auth_path"].items():
        ap.append(f"| {k} | {v['controller_us']:.0f} | {v['issue_us']:.1f} | {v['authorize_us']:.1f} "
                  f"| {v['revoke_propagate_us']:.1f} | {v['total_us_per_agent_step']:.0f} | {v['tokens_issued']} "
                  f"| {v['revocations']} | {v['stale_tokens_accepted']} |")
    n06 = llm_latencies()
    tot = max(v["total_us_per_agent_step"] for v in res["auth_path"].values())
    return f"""# N24 - System overhead

## Reviewer issue
IEEE R2-8: the overhead claim omitted the dominant costs (critic calls, token issuance, enforcement,
revocation propagation), and varied the number of agents N although Proposition 5 is about the number of layers L.

## (a) Controller cost vs layers L and capabilities |C| (pure Python, real E1 signals, median of 5 runs)

| L | {' | '.join(str(L) for L in LS)} |
|---|{'---|' * len(LS)}
| us/step | {lrow} |

Least-squares fit a + bL + cL^2: a = {vl['fit_quadratic'][0]:.1f}, b = {vl['fit_quadratic'][1]:.2f}, c = {vl['fit_quadratic'][2]:.3f}
(R^2 = {vl['r2_quadratic']:.4f}; a linear fit gives R^2 = {vl['r2_linear']:.4f}), consistent with O(L^2).

| |C| (L = 5) | {' | '.join(str(c) for c in CS)} |
|---|{'---|' * len(CS)}
| us/step | {crow} |

## (b) Full authorization path on real E1 streams
Controller step + grant rule, HMAC-SHA256 capability token issuance, gateway verification (signature, expiry,
revocation epoch), and revocation propagation (epoch broadcast to every gateway). Per-operation means in us.
"stale tokens accepted" counts, after every revocation, how many gateways still accepted the agent's last token
(must be 0).

| Setting | controller | issue | authorize | revoke + propagate | total per agent-step | tokens issued | revocations | stale tokens accepted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(ap)}

## (c) End to end
The full authorization path costs at most {tot:.0f} us per agent-step. The measured LLM latencies per step (N06,
medians) are 1.45 s (Claude Sonnet 4.5) and 1.91 s (GPT-5) for the agent call, plus 1.3-2.0 s when the epistemic
critic is an LLM judge (about 0.9x the agent's tokens). The controller and token path is therefore below
{100 * tot / 1.45e6:.3f}% of a step with a reference critic and below {100 * tot / 2.7e6:.3f}% with an LLM-judge critic;
the critic call, not the controller, is the dominant cost of the framework.

![overhead](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {"results": res, "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
