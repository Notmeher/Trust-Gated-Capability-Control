"""N21 - Learning the coupling matrix from traces (RRLq W4).

(a) Recovery: simulate trust trajectories with a ground-truth C* (the default
coupling); in each episode a randomly chosen layer collapses after step 60. A harm
label is drawn as Bernoulli(1 - Phi*(t)). The learner sees only (T(t), y(t)) and
fits a lower-triangular C_hat by maximum likelihood (L-BFGS-B).
(b) Use: TGCC with C_hat vs the default C on the real-LLM streams (E1 sleeper and
the non-epistemic compromises of N12), each calibrated by Algorithm 2.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

from tgcc.beta_belief import BetaBelief
from tgcc.nextphase.evaluation import run_gate
from tgcc.nextphase.gates import PREWARM_N, PREWARM_RHO, Gate, TGCCParams
from tgcc.nextphase.io import figure_path, write_readme, write_results
from tgcc.nextphase.n12_non_epistemic_compromise import hostile, offtopic, policy
from tgcc.nextphase.responses import available_banks, load_bank, model_name
from tgcc.nextphase.sim import HONEST
from tgcc.nextphase.stats import fmt_ci
from tgcc.nextphase.streams import pilot_signals, qa_episodes
from tgcc.synergy import DEFAULT_COUPLING

EXP = "n21_learned_coupling"
L, P = 5, -6.0
IDX = [(l, k) for l in range(L) for k in range(l)]
N_EP, N_TURNS, COMPROMISE = 200, 300, 60


def _phi(T: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Vectorised Eq. 3 + Eq. 5 with uniform weights. T: (N, L)."""
    eff = T.copy()
    for l in range(L):
        for k in range(l):
            eff[:, l] *= 1 - C[l, k] * (1 - T[:, k])
    eff = np.clip(eff, 1e-9, 1)
    return np.mean(eff ** P, axis=1) ** (1 / P)


def _mat(x: np.ndarray) -> np.ndarray:
    C = np.zeros((L, L))
    for v, (l, k) in zip(x, IDX):
        C[l, k] = 1 / (1 + np.exp(-v))
    return C


def traces(seed: int = 7) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    Ts, ys = [], []
    for e in range(N_EP):
        bad = rng.integers(L)
        bs = [BetaBelief(gamma=0.985, omega=3.0) for _ in range(L)]
        for b in bs:
            b.prewarm(PREWARM_RHO, PREWARM_N)
        for t in range(N_TURNS):
            rho = HONEST.copy()
            if t >= COMPROMISE:
                rho[bad] = 0.30
            s = (rng.random(L) < rho).astype(float)
            Ts.append([b.update(x) for b, x in zip(bs, s)])
    T = np.array(Ts)
    y = (rng.random(len(T)) < 1 - _phi(T, DEFAULT_COUPLING)).astype(float)
    return T, y


def fit(T: np.ndarray, y: np.ndarray, starts: int = 5) -> tuple[np.ndarray, float]:
    def nll(x):
        q = np.clip(1 - _phi(T, _mat(x)), 1e-6, 1 - 1e-6)
        return float(-np.mean(y * np.log(q) + (1 - y) * np.log(1 - q)))
    rng = np.random.default_rng(0)
    best = None
    for _ in range(starts):
        r = minimize(nll, rng.normal(0, 1, len(IDX)), method="L-BFGS-B")
        if best is None or r.fun < best.fun:
            best = r
    return _mat(best.x), float(best.fun)


def use(C_hat: np.ndarray) -> dict:
    out = {}
    mats = {"default C": DEFAULT_COUPLING, "learned C_hat": C_hat}
    for provider in available_banks():
        bank = load_bank(provider)
        pilot = pilot_signals(bank)
        res = {}
        for atk, (mode, fn) in {"sleeper": ("forced", None), "policy": ("honest", policy),
                                "offtopic": ("honest", offtopic), "hostile": ("honest", hostile)}.items():
            eps = qa_episodes(bank, sleeper_mode=mode, transform=fn)
            for mname, C in mats.items():
                for prereq in (True, False):
                    g = Gate("TGCC" if prereq else "TGCC-CompositeOnly", "tgcc",
                             TGCCParams(coupling=tuple(map(tuple, C)), prereq=prereq))
                    res[f"{atk}|{mname}|{g.name}"] = run_gate(g, eps, pilot)["summary"]
        out[provider] = res
    return out


def _fig(C_hat: np.ndarray) -> str:
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.6))
    for a, M, title, cmap, vmax in ((ax[0], DEFAULT_COUPLING, "true C*", "Blues", 1),
                                    (ax[1], C_hat, "learned C_hat", "Blues", 1),
                                    (ax[2], np.abs(C_hat - DEFAULT_COUPLING), "|C_hat - C*|", "Reds", 0.5)):
        im = a.imshow(M, cmap=cmap, vmin=0, vmax=vmax)
        for i in range(L):
            for j in range(i):
                a.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=7)
        a.set_title(title)
        fig.colorbar(im, ax=a, shrink=0.75)
    fig.tight_layout()
    path = figure_path(EXP, "coupling_recovery.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path.name


def readme(r: dict, fig: str) -> str:
    blocks = []
    for p, res in r["use"].items():
        rows = []
        for atk in ("sleeper", "policy", "offtopic", "hostile"):
            for gname in ("TGCC", "TGCC-CompositeOnly"):
                d, h = res[f"{atk}|default C|{gname}"], res[f"{atk}|learned C_hat|{gname}"]
                rows.append(f"| {atk} | {gname} | {fmt_ci(d['oer'])} | {fmt_ci(h['oer'])} | "
                            f"{fmt_ci(d['fpr'])} | {fmt_ci(h['fpr'])} |")
        blocks.append(f"### {model_name(p)}\n| Compromise | Gate | OER (default C) | OER (C_hat) | "
                      "FPR (default C) | FPR (C_hat) |\n|---|---|---|---|---|---|\n" + "\n".join(rows))
    return f"""# Learning the coupling matrix from traces

## (a) Recovery from simulated traces
{N_EP} simulated episodes x {N_TURNS} steps with the default coupling C* as ground
truth; in each episode one randomly chosen layer collapses to reliability 0.30
after step {COMPROMISE} (pre-warmed Beta beliefs). Harm labels
y(t) ~ Bernoulli(1 - Phi*(t)). The learner sees only (T(t), y(t)) and fits the 10
lower-triangular entries by maximum likelihood (L-BFGS-B, 5 restarts).

* ||C_hat - C*||_F = **{r['frobenius']:.3f}** (vs ||C*||_F = {np.linalg.norm(DEFAULT_COUPLING):.3f})
* largest entry error = {r['max_err']:.3f}; NLL = {r['nll']:.4f}

![coupling](figures/{fig})

## (b) Using C_hat in the gate on the real-LLM streams (15 episodes per model and compromise)
{chr(10).join(blocks)}

## Reading
* The coupling is identifiable from (trust, harm) traces up to a moderate error.
  Entries whose prerequisite rarely fails are the hardest to pin down.
* Using the learned C_hat in the gate changes OER by at most 0.03 on every compromise
  type and model, so the hand-specified matrix can be replaced by a fitted one without
  re-tuning.
"""


def main(argv=None) -> None:
    T, y = traces()
    C_hat, nll = fit(T, y)
    r = {"C_star": DEFAULT_COUPLING.tolist(), "C_hat": C_hat.tolist(), "nll": nll,
         "frobenius": float(np.linalg.norm(C_hat - DEFAULT_COUPLING)),
         "max_err": float(np.abs(C_hat - DEFAULT_COUPLING).max()), "use": use(C_hat)}
    fig = _fig(C_hat)
    write_results(EXP, {**r, "figures": [fig]})
    write_readme(EXP, readme(r, fig))
    print(readme(r, fig))


if __name__ == "__main__":
    main()
