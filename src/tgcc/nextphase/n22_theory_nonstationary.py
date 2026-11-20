"""N22 - Theorem 4 and Eq. (14) under real non-stationarity (IEEE R1-1, R2-6).

Reviewer issue
--------------
R1-1: Theorem 4 (false positives) and Theorem 6 / Eq. (14) (detection latency) rely on Hoeffding and
geometric convergence, i.e. stationary, bounded noise; real LLM interactions are non-stationary, so the bounds
may be loose or optimistic. R2-6: Theorem 4's effective sample count converges, so the bound has a floor.

Revised Theorem 4 (martingale form; no stationarity or independence)
---------------------------------------------------------------------
Let s_t in [0,1] be any adapted signal process with E[s_t | past] >= rho_min at every honest step. Layer trust
T_t < theta iff sum_s w_s X_s < (prior terms), with w_s = gamma^(t-s) and X_s = s_s (1 - theta + theta omega)
- theta omega in [-theta omega, 1 - theta]. If mu = rho_min (1 - theta + theta omega) - theta omega > 0
(equivalently T*(rho_min) > theta), Azuma-Hoeffding for weighted martingale differences gives
    P(T_t < theta) <= exp( -2 mu^2 (sum w)^2 / (R^2 sum w^2) ),  R = 1 - theta + theta omega,
whose floor as t -> inf is exp(-2 mu^2 (1 + gamma) / (R^2 (1 - gamma))): it does not decay to zero, and it only
needs a lower bound on the *worst* regime's reliability. For the per-turn epistemic check (window of W = 8 calibration
errors e_t in [0,1] with E[e_t | past] <= e_max), P(window mean > e_max + lam) <= exp(-2 W lam^2).

Real non-stationary streams
---------------------------
* stationary: one model throughout (reference);
* model swap: consecutive questions answered by Claude Sonnet 4.5, then GPT-5, then Claude Haiku 4.5
  (40 steps each, all 6 orders);
* domain shift: 60 TriviaQA questions then 60 MedMCQA questions, same model;
* domain shift + compromise: 60 TriviaQA and 30 MedMCQA honest answers, then 60 TriviaQA sleeper answers
  (for Eq. (14); 60 post-compromise steps).
rho_min is the smallest regime-level mean signal (pooled over episodes) in each stream type; the bound is checked
against the empirical honest denial rate.
"""
from __future__ import annotations

import itertools
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.beta_belief import BetaBelief
from tgcc.nextphase.gates import PREWARM_N, PREWARM_RHO, calibrate, standard_gates
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.n07_theory_checks import exact_crossing_closed_form
from tgcc.nextphase.responses import bank_path, load_bank, model_name
from tgcc.nextphase.streams import LAYERS, _force_wrong, compute_signals, pilot_signals

EXP = "n22_theory_nonstationary"
GAMMA, OMEGA, W = 0.985, 3.0, 8
SWAP_MODELS = ("anthropic", "azure_openai", "anthropic_haiku")
QWEN_SWAP_MODELS = ("qwen3-4b", "qwen3-8b", "qwen2.5-7b")
SHIFT_MODELS = SWAP_MODELS + QWEN_SWAP_MODELS
MARGINS = (0.05, 0.10, 0.20)


# ------------------------------------------------------------------ bounds
def t_star(rho: float, omega: float = OMEGA) -> float:
    return rho / (rho + omega * (1 - rho))


A0, B0 = t_star(PREWARM_RHO) * PREWARM_N, (1 - t_star(PREWARM_RHO)) * PREWARM_N


def martingale_bound(rho_min: float, theta: float, t: int, gamma: float = GAMMA, omega: float = OMEGA,
                     a0: float = A0, b0: float = B0) -> float:
    """P(T_t < theta) for an adapted process with E[s | past] >= rho_min, including the prior (a0, b0).

    T_t < theta  <=>  sum_s w_s X_s < gamma^t (theta b0 - (1 - theta) a0) =: gamma^t P.
    With mean drift mu * sum(w) and Azuma-Hoeffding: <= exp(-2 (mu sum w - gamma^t P)_+^2 / (R^2 sum w^2)).
    """
    R = 1 - theta + theta * omega
    mu = rho_min * R - theta * omega
    w = gamma ** np.arange(t)
    gap = mu * w.sum() - gamma ** t * (theta * b0 - (1 - theta) * a0)
    if gap <= 0:
        return 1.0
    return float(min(1.0, math.exp(-2 * gap ** 2 / (R ** 2 * (w ** 2).sum()))))


def floor_bound(rho_min: float, theta: float, gamma: float = GAMMA, omega: float = OMEGA) -> float:
    R = 1 - theta + theta * omega
    mu = rho_min * R - theta * omega
    return 1.0 if mu <= 0 else float(math.exp(-2 * mu ** 2 * (1 + gamma) / (R ** 2 * (1 - gamma))))


# ------------------------------------------------------------------ streams
def _rec(provider: str, ds: str, phase: str, iid: str) -> dict:
    return load_bank(provider, ds)[phase][iid]


def _stream(recs: list[dict], sleeper_from: int | None = None, seed: int = 0):
    import random
    rng = random.Random(seed)
    texts, labs, confs = [], [], []
    for t, r in enumerate(recs):
        if sleeper_from is not None and t >= sleeper_from:
            txt, ok, c = _force_wrong(r, rng)
        else:
            txt, ok, c = r["text"], r["correct"], r["conf"]
        texts.append(txt)
        labs.append(ok)
        confs.append(c)
    e = np.abs(np.array(confs) - np.array(labs, float))
    return compute_signals(texts, labs, confs), e


def stream_sets() -> dict[str, list[dict]]:
    """name -> list of {signals, errors, regimes (per-step regime id), compromise}"""
    out: dict[str, list[dict]] = {}
    tq_ids = load_bank("anthropic_haiku")["eval_ids"] if bank_path("anthropic_haiku").exists() \
        else load_bank("anthropic")["eval_ids"][:300]
    for p in SHIFT_MODELS:
        if not bank_path(p).exists():
            continue
        eps = []
        for k in range(5):
            ids = tq_ids[k * 60:(k + 1) * 60]
            s, e = _stream([_rec(p, "triviaqa", "honest", i) for i in ids])
            eps.append({"signals": s, "errors": e, "regimes": np.zeros(60, int), "compromise": None})
        out[f"stationary: {model_name(p)} / TriviaQA"] = eps
    for swap, name in ((SWAP_MODELS, "Sonnet / GPT-5 / Haiku"), (QWEN_SWAP_MODELS, "Qwen3-4B / Qwen3-8B / Qwen2.5-7B")):
        if not all(bank_path(p).exists() for p in swap):
            continue
        eps = []
        for order in itertools.permutations(swap):
            for k in range(2):
                ids = tq_ids[k * 120:(k + 1) * 120]
                recs = [_rec(order[t // 40], "triviaqa", "honest", i) for t, i in enumerate(ids)]
                s, e = _stream(recs)
                reg = np.array([swap.index(order[t // 40]) for t in range(120)])
                eps.append({"signals": s, "errors": e, "regimes": reg, "compromise": None})
        out[f"model swap ({name}, 40 steps each)"] = eps
    for p in SHIFT_MODELS:
        if not bank_path(p, "medmcqa").exists():
            continue
        mq_ids = load_bank(p, "medmcqa")["eval_ids"][:300]
        hon, sl = [], []
        for k in range(5):
            a = [_rec(p, "triviaqa", "honest", i) for i in tq_ids[k * 60:(k + 1) * 60]]
            b = [_rec(p, "medmcqa", "honest", i) for i in mq_ids[k * 60:(k + 1) * 60]]
            s, e = _stream(a + b)
            hon.append({"signals": s, "errors": e, "regimes": np.r_[np.zeros(60, int), np.ones(60, int)],
                        "compromise": None})
            n_tq = len(tq_ids) // 120
            if k < n_tq:
                a2 = [_rec(p, "triviaqa", "honest", i) for i in tq_ids[k * 120:k * 120 + 60]]
                bs = [_rec(p, "medmcqa", "honest", i) for i in mq_ids[k * 60:k * 60 + 30]]
                cs = [_rec(p, "triviaqa", "sleeper", i) for i in tq_ids[k * 120 + 60:(k + 1) * 120]]
                s2, e2 = _stream(a2 + bs + cs, sleeper_from=90, seed=k)
                sl.append({"signals": s2, "errors": e2,
                           "regimes": np.r_[np.zeros(60, int), np.ones(30, int), np.zeros(60, int)], "compromise": 90})
        out[f"domain shift: {model_name(p)} TriviaQA -> MedMCQA"] = hon
        out[f"domain shift + compromise: {model_name(p)}"] = sl
    return out


# ----------------------------------------------------------------- checks
def beta_trusts(sig: np.ndarray) -> np.ndarray:
    bs = [BetaBelief(gamma=GAMMA, omega=OMEGA) for _ in range(sig.shape[1])]
    for b in bs:
        b.prewarm(PREWARM_RHO, PREWARM_N)
    return np.array([[b.update(x) for b, x in zip(bs, row)] for row in sig])


def theorem4_check(eps: list[dict]) -> dict:
    """Per layer: rho_min = smallest regime mean (pooled); empirical P(T < theta) vs the martingale bound."""
    out = {}
    honest = [(e, e["compromise"] or len(e["signals"])) for e in eps]
    T = [beta_trusts(e["signals"])[:h] for e, h in honest]
    for k, layer in enumerate(LAYERS):
        regs = {}
        for e, h in honest:
            for r in np.unique(e["regimes"][:h]):
                regs.setdefault(int(r), []).append(e["signals"][:h][e["regimes"][:h] == r, k])
        rho_min = min(float(np.mean(np.concatenate(v))) for v in regs.values())
        rows = []
        for m in MARGINS:
            theta = t_star(rho_min) - m
            if theta <= 0:
                continue
            emp = float(np.mean(np.concatenate([tr[:, k] < theta for tr in T])))
            bnd = float(np.mean([martingale_bound(rho_min, theta, t + 1) for tr in T for t in range(len(tr))]))
            rows.append({"margin": m, "theta": theta, "empirical": emp, "bound_avg": bnd,
                         "floor": floor_bound(rho_min, theta)})
        out[layer] = {"rho_min": rho_min, "rows": rows}
    return out


def window_check(eps: list[dict], theta_e: float) -> dict:
    """Per-turn epistemic check: denial iff windowed calibration error > 0.5 (1 - theta_e)."""
    e_max = 0.0
    for e in eps:
        h = e["compromise"] or len(e["errors"])
        for r in np.unique(e["regimes"][:h]):
            e_max = max(e_max, float(np.mean(e["errors"][:h][e["regimes"][:h] == r])))
    thr = 0.5 * (1 - theta_e)
    lam = thr - e_max
    bound = math.exp(-2 * W * lam ** 2) if lam > 0 else 1.0
    den = np.concatenate([e["signals"][: (e["compromise"] or len(e["signals"])), 0] < theta_e for e in eps])
    return {"theta_e": theta_e, "e_max": e_max, "error_threshold": thr, "empirical": float(den.mean()),
            "bound": bound}


def state_conditioned_crossing(a_c: float, b_c: float, rho1: float, x: float,
                               gamma: float = GAMMA, omega: float = OMEGA) -> float:
    """Eq. (14) from the actual evidence state (a_c, b_c) at compromise, for any pre-compromise history.

    Expected evidence: a(k) = g^k a_c + rho1 (1-g^k)/(1-g), b(k) = g^k b_c + omega (1-rho1) (1-g^k)/(1-g).
    T(k) = x  <=>  g^k (A - B) + B = 0 with A = a_c (1-x) - x b_c, B = (rho1 (1-x) - x omega (1-rho1)) / (1-g).
    """
    A = a_c * (1 - x) - x * b_c
    B = (rho1 * (1 - x) - x * omega * (1 - rho1)) / (1 - gamma)
    if A <= 0:
        return 0.0
    if B >= 0:
        return float("inf")
    return math.log((A - B) / (-B)) / math.log(1 / gamma)


def latency_check(eps: list[dict]) -> dict:
    """Eq. (14) on real compromised streams: epistemic Beta trust crossing level x after compromise.

    rho0 = mean epistemic signal over the 30 steps before the compromise (the non-stationary local regime),
    rho1 = mean after it; x is a quarter or half of the way from T*(rho0) to T*(rho1)."""
    rows = []
    for e in eps:
        c = e["compromise"]
        tr = beta_trusts(e["signals"])[:, 0]
        b = BetaBelief(gamma=GAMMA, omega=OMEGA)
        b.prewarm(PREWARM_RHO, PREWARM_N)
        for v in e["signals"][:c, 0]:
            b.update(v)
        a_c, b_c = b.a, b.b
        rho0 = float(np.mean(e["signals"][c - 30:c, 0]))
        rho1 = float(np.mean(e["signals"][c:, 0]))
        for frac in (0.25, 0.5):
            x = t_star(rho0) - frac * (t_star(rho0) - t_star(rho1))
            pred = exact_crossing_closed_form(GAMMA, rho0, rho1, x, OMEGA) if rho1 < rho0 else float("nan")
            hit = np.where(tr[c:] < x)[0]
            rows.append({"rho0": rho0, "rho1": rho1, "frac": frac, "x": x, "predicted": pred,
                         "predicted_state": state_conditioned_crossing(a_c, b_c, rho1, x),
                         "trust_at_compromise": float(a_c / (a_c + b_c)),
                         "horizon": len(tr) - c, "observed": float(hit[0] + 1) if hit.size else float("inf")})
    return {"episodes": rows}


def run() -> dict:
    gate = next(g for g in standard_gates() if g.name == "TGCC")
    theta_e = calibrate(gate.stats(pilot_signals(load_bank("anthropic"))))["epistemic"]
    out = {}
    for name, eps in stream_sets().items():
        r = {"n_episodes": len(eps), "theorem4": theorem4_check(eps), "window": window_check(eps, theta_e)}
        if eps[0]["compromise"] is not None:
            r["latency"] = latency_check(eps)
        out[name] = r
    return out


def _fig(res) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for name, r in res.items():
        if name.startswith("domain shift + compromise"):
            continue
        xs, ys = [], []
        for layer, v in r["theorem4"].items():
            for row in v["rows"]:
                xs.append(max(row["bound_avg"], 1e-6))
                ys.append(max(row["empirical"], 1e-6))
        axes[0].scatter(xs, ys, s=14, label=name)
    axes[0].plot([1e-6, 1], [1e-6, 1], "k--", lw=0.8)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("revised Theorem 4 bound (avg over steps)")
    axes[0].set_ylabel("empirical honest P(T < theta)")
    axes[0].legend(fontsize=6)
    for name, r in res.items():
        if "latency" not in r:
            continue
        p = [z["predicted_state"] for z in r["latency"]["episodes"]]
        o = [z["observed"] for z in r["latency"]["episodes"]]
        axes[1].scatter(p, o, label=name)
    lim = axes[1].get_xlim()
    axes[1].plot([0, max(lim[1], 1)], [0, max(lim[1], 1)], "k--", lw=0.8)
    axes[1].set_xlabel("state-conditioned Eq. (14) (steps)")
    axes[1].set_ylabel("observed crossing (steps)")
    axes[1].legend(fontsize=6)
    fig.tight_layout()
    p = figure_path(EXP, "theory_nonstationary.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p.name


def readme(res, fig) -> str:
    t4, win, lat = [], [], []
    viol = tot = 0
    for name, r in res.items():
        for layer, v in r["theorem4"].items():
            for row in v["rows"]:
                tot += 1
                viol += row["empirical"] > row["bound_avg"] + 1e-12
                t4.append(f"| {name} | {layer} | {v['rho_min']:.3f} | {row['margin']:.2f} | {row['theta']:.3f} "
                          f"| {row['empirical']:.4f} | {row['bound_avg']:.4f} | {row['floor']:.4f} |")
        w = r["window"]
        win.append(f"| {name} | {w['e_max']:.3f} | {w['error_threshold']:.3f} | {w['empirical']:.3f} | {w['bound']:.3f} |")
        if "latency" in r:
            for z in r["latency"]["episodes"]:
                lat.append(f"| {name} | {z['rho0']:.2f} | {z['rho1']:.2f} | {z['trust_at_compromise']:.3f} "
                           f"| {t_star(z['rho0']):.3f} | {z['frac']} | {z['x']:.3f} | {z['predicted']:.1f} "
                           f"| {z['predicted_state']:.1f} | {z['observed']:.0f} ({z['horizon']}) |")
    return f"""# N22 - Theorem 4 and Eq. (14) under real non-stationarity

## Reviewer issue
IEEE R1-1 (bounds assume stationary noise; real interactions are non-stationary) and R2-6 (Theorem 4 has a floor).

## Revised Theorem 4 (martingale form)
For any adapted signal process with E[s_t | past] >= rho_min at honest steps (no stationarity, no independence):
P(T_t < theta) <= exp(-2 (mu sum w - gamma^t P)_+^2 / (R^2 sum w^2)), with mu = rho_min (1 - theta + theta omega)
- theta omega, R = 1 - theta + theta omega, w_s = gamma^(t-s), and P = theta b0 - (1 - theta) a0 the prior's
contribution (pre-warm a0 = {A0:.0f}, b0 = {B0:.0f}). Floor as t -> inf: exp(-2 mu^2 (1+gamma) / (R^2 (1-gamma))). It
requires only that the worst regime's reliability rho_min keeps T*(rho_min) above theta; when theta exceeds the
pre-warmed trust the prior term delays the guarantee (the bound is 1 until the evidence outweighs the prior).

## (a) Bound vs empirical honest denial on real non-stationary streams
theta = T*(rho_min) - margin, per layer. The bound held in {tot - viol} of {tot} cases.

| Stream | Layer | rho_min | margin | theta | empirical P(T < theta) | bound (avg over steps) | floor |
|---|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(t4)}

## (b) Why the per-turn epistemic check needs conformal calibration (window W = {W})
Denial iff the windowed calibration error exceeds 0.5 (1 - theta_e). An Azuma bound exp(-2 W (threshold - e_max)^2)
exists only if the honest regime-level mean error e_max is below the threshold; on real streams it is not
(e_max 0.19-0.39 against 0.18 at the Claude-calibrated theta_e), so no distribution-free per-step bound is
available and the bound column is vacuous. The per-turn check's honest FPR is therefore controlled by conformal
risk control on deployment sessions (N29, N32), which needs no such assumption. The rate is constant in t: the
per-turn check trades a fixed honest false-denial rate for one-step detection.

| Stream | e_max | error threshold | empirical denial | bound |
|---|---:|---:|---:|---:|
{chr(10).join(win)}

## (c) Eq. (14) on real compromised streams after a domain shift
rho0 / rho1 = mean epistemic signal over the 30 steps before / all steps after the compromise; x lies a quarter
(0.25) or half (0.5) of the way from T*(rho0) to T*(rho1); observed = steps until the epistemic Beta trust first
falls below x (inf = not within the post-compromise horizon).

"Eq. (14)" assumes the trust starts at the stationary point T*(rho0) of the latest regime; "state-conditioned"
starts from the actual evidence (a, b) at compromise, which the controller knows, and needs no assumption about
the history.

| Stream | rho0 | rho1 | trust at compromise | T*(rho0) | level | x | Eq. (14) | state-conditioned | observed (horizon) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(lat)}

![theory](figures/{fig})
"""


def main(argv=None) -> None:
    res = run()
    fig = _fig(res)
    write_results(EXP, {"gamma": GAMMA, "omega": OMEGA, "window": W, "results": res, "figures": [fig]})
    write_readme(EXP, readme(res, fig))
    print(readme(res, fig))


if __name__ == "__main__":
    main()
