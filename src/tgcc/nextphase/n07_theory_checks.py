"""N07 - Numerical validation of Theorem 4 (false-positive floor) and Eq. (14) (detection latency).

(a) Monte-Carlo false-denial probability of an honest layer vs t against the bound
    L exp(-2 D^2 n(t)) and its floor L exp(-2 D^2/(1-gamma)); floor vs gamma.
(b) Expected-evidence crossing time vs the closed form of Eq. (14), a geometric-T
    approximation, and the stochastic mean crossing time.
"""
from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tgcc.beta_belief import BetaBelief
from tgcc.nextphase.io import figure_path, write_readme, write_results

EXP = "n07_theory_checks"


def honest_fp_curve(rho=0.9, omega=3.0, gamma=0.985, theta=0.6, T=800, M=20000, seed=0):
    rng = np.random.default_rng(seed)
    a = np.ones(M)
    b = np.ones(M)
    p = np.zeros(T)
    for t in range(T):
        s = (rng.random(M) < rho).astype(float)
        a = gamma * a + s
        b = gamma * b + omega * (1 - s)
        p[t] = np.mean(a / (a + b) < theta)
    t_star = BetaBelief.fixed_point(rho, omega)
    n = (1 - gamma ** np.arange(1, T + 1)) / (1 - gamma)
    bound = np.exp(-2 * (t_star - theta) ** 2 * n)
    floor = math.exp(-2 * (t_star - theta) ** 2 / (1 - gamma))
    return p, bound, floor, t_star


def stationary_fp(gamma, rho=0.9, omega=3.0, theta=0.6, M=20000, seed=1):
    burn = int(8 / (1 - gamma))
    rng = np.random.default_rng(seed)
    a, b = np.ones(M), np.ones(M)
    acc = []
    for t in range(burn + 400):
        s = (rng.random(M) < rho).astype(float)
        a = gamma * a + s
        b = gamma * b + omega * (1 - s)
        if t >= burn:
            acc.append(np.mean(a / (a + b) < theta))
    t_star = BetaBelief.fixed_point(rho, omega)
    return float(np.mean(acc)), math.exp(-2 * (t_star - theta) ** 2 / (1 - gamma))


def crossing(gamma, rho0, rho1, x, omega=3.0, stochastic=False, M=4000, seed=0):
    """Steps after compromise until layer trust < x, starting at the pre-compromise
    stationary evidence. Deterministic = expected-evidence recursion."""
    a0 = rho0 / (1 - gamma)
    b0 = omega * (1 - rho0) / (1 - gamma)
    if not stochastic:
        a, b = a0, b0
        for k in range(1, 100000):
            a = gamma * a + rho1
            b = gamma * b + omega * (1 - rho1)
            if a / (a + b) < x:
                return float(k)
        return float("inf")
    rng = np.random.default_rng(seed)
    a, b = np.full(M, a0), np.full(M, b0)
    hit = np.full(M, np.inf)
    for k in range(1, 5000):
        s = (rng.random(M) < rho1).astype(float)
        a = gamma * a + s
        b = gamma * b + omega * (1 - s)
        newly = (a / (a + b) < x) & ~np.isfinite(hit)
        hit[newly] = k
        if np.isfinite(hit).all():
            break
    return float(np.mean(hit))


def exact_crossing_closed_form(gamma, rho0, rho1, x, omega=3.0) -> float:
    """Closed form for the expected-evidence recursion started at the honest stationary point.

    With D_i = rho_i + omega (1 - rho_i) and u = gamma^k,
    T(k) = (u rho0 + (1-u) rho1) / (u D0 + (1-u) D1), so T(k) = x at
    k = ln[(rho0 - rho1 - x (D0 - D1)) / (x D1 - rho1)] / ln(1/gamma).
    Reduces to ln[(T0 - T*)/(x - T*)]/ln(1/gamma) when omega = 1.
    """
    d0 = rho0 + omega * (1 - rho0)
    d1 = rho1 + omega * (1 - rho1)
    return math.log((rho0 - rho1 - x * (d0 - d1)) / (x * d1 - rho1)) / math.log(1 / gamma)


def run() -> dict:
    p, bound, floor, t_star = honest_fp_curve()
    gammas = [0.9, 0.95, 0.97, 0.985, 0.99, 0.995, 0.998]
    stat = [stationary_fp(g) for g in gammas]
    rows = []
    for gamma in (0.95, 0.985, 0.995):
        for rho1 in (0.1, 0.3, 0.5):
            for x in (0.3, 0.45, 0.6):
                T0 = BetaBelief.fixed_point(0.9)
                Ts = BetaBelief.fixed_point(rho1)
                if not (Ts < x < T0):
                    continue
                exact = crossing(gamma, 0.9, rho1, x)
                stoch = crossing(gamma, 0.9, rho1, x, stochastic=True)
                approx = math.log((T0 - Ts) / (x - Ts)) / math.log(1 / gamma)
                exact_cf = exact_crossing_closed_form(gamma, 0.9, rho1, x)
                rows.append({"gamma": gamma, "rho_post": rho1, "x": x, "T0": T0, "T_star": Ts,
                             "exact_expected": exact, "stochastic_mean": stoch,
                             "geometric_approx": approx, "closed_form": exact_cf})
    return {"thm4": {"p_emp": p.tolist(), "bound": bound.tolist(), "floor": floor,
                     "t_star": t_star, "theta": 0.6, "rho": 0.9, "gamma": 0.985, "omega": 3.0,
                     "p_emp_last100": float(np.mean(p[-100:]))},
            "thm4_vs_gamma": [{"gamma": g, "empirical_stationary": s, "floor": f}
                              for g, (s, f) in zip(gammas, stat)],
            "eq14": rows}


def _figs(r) -> list[str]:
    th = r["thm4"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
    t = np.arange(1, len(th["p_emp"]) + 1)
    axes[0].semilogy(t, np.maximum(th["p_emp"], 1e-6), label=r"empirical $P(T_\ell < \theta)$")
    axes[0].semilogy(t, th["bound"], label=r"bound $\exp(-2\Delta^2 n_\ell(t))$")
    axes[0].axhline(th["floor"], ls="--", color="k",
                    label=rf"floor $\exp(-2\Delta^2/(1-\gamma))$ = {th['floor']:.3f}")
    axes[0].set_xlabel("step t")
    axes[0].set_title("Theorem 4: honest false-denial probability")
    axes[0].legend(fontsize=8)
    g = [z["gamma"] for z in r["thm4_vs_gamma"]]
    axes[1].semilogy(g, [max(z["empirical_stationary"], 1e-6) for z in r["thm4_vs_gamma"]], "o-",
                     label="empirical stationary rate")
    axes[1].semilogy(g, [z["floor"] for z in r["thm4_vs_gamma"]], "s--",
                     label=r"floor $\exp(-2\Delta^2/(1-\gamma))$")
    axes[1].set_xlabel(r"forgetting factor $\gamma$")
    axes[1].set_title("False-positive floor vs forgetting factor")
    axes[1].legend(fontsize=8)
    rows = r["eq14"]
    axes[2].plot([z["exact_expected"] for z in rows], [z["geometric_approx"] for z in rows], "o",
                 label="geometric-trajectory approximation")
    axes[2].plot([z["exact_expected"] for z in rows], [z["closed_form"] for z in rows], "^",
                 label="closed form, Eq. (14)")
    axes[2].plot([z["exact_expected"] for z in rows], [z["stochastic_mean"] for z in rows], "x",
                 label="stochastic mean")
    m = max(max(z["exact_expected"] for z in rows), max(z["geometric_approx"] for z in rows))
    axes[2].plot([0, m], [0, m], "k:", lw=1)
    axes[2].set_xlabel("crossing step (expected-evidence recursion)")
    axes[2].set_ylabel("predicted / simulated")
    axes[2].set_title("Detection latency, Eq. (14)")
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    p = figure_path(EXP, "theory_checks.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return [p.name]


def readme(r, figs) -> str:
    th = r["thm4"]
    g = "\n".join(f"| {z['gamma']} | {z['empirical_stationary']:.4f} | {z['floor']:.4f} |"
                  for z in r["thm4_vs_gamma"])
    e = "\n".join(
        f"| {z['gamma']} | {z['rho_post']} | {z['x']} | {z['exact_expected']:.0f} | {z['stochastic_mean']:.1f} "
        f"| {z['closed_form']:.1f} | {z['geometric_approx']:.1f} |"
        for z in r["eq14"])
    ratio = [z["geometric_approx"] / z["exact_expected"] for z in r["eq14"]]
    viol = [z for z in r["thm4_vs_gamma"] if z["empirical_stationary"] > z["floor"]]
    return f"""# Theory validation: Theorem 4 and Eq. (14)

## (a) Theorem 4: honest false-positive floor
Single honest layer, rho = {th['rho']}, omega = {th['omega']}, gamma = {th['gamma']},
fixed point T* = {th['t_star']:.3f}, per-layer threshold theta = {th['theta']}, 20,000 seeds.

* Floor L exp(-2 D^2/(1-gamma)) = **{th['floor']:.4f}** (per layer, L = 1).
* Empirical false-denial probability over the last 100 of 800 steps: **{th['p_emp_last100']:.4f}**;
  the probability converges to a positive stationary value.

| gamma | empirical stationary P(false denial) | floor |
|---|---:|---:|
{g}

{"The floor upper-bounds the empirical stationary rate for every gamma tested." if not viol else "Floor exceeded for gamma in " + str([z['gamma'] for z in viol]) + "."}
The bound converges geometrically (rate gamma) to L exp(-2 D^2/(1-gamma)); the floor
shrinks with a larger margin D or a forgetting factor closer to one, at the cost of
slower revocation (Eq. 14).

## (b) Eq. (14): expected detection latency
Under the pseudo-count update the trust is a ratio of two geometric sequences,
T(k) = (u rho0 + (1-u) rho1) / (u D0 + (1-u) D1) with u = gamma^k and
D_i = rho_i + omega (1 - rho_i). Solving T(k) = x gives

    k* = ln[(rho0 - rho1 - x (D0 - D1)) / (x D1 - rho1)] / ln(1/gamma),

which reduces to ln[(T0 - T*)/(x - T*)]/ln(1/gamma) (geometric-trajectory
approximation) when omega = 1.

| gamma | rho post | x = theta/kappa | recursion | stochastic mean | Eq. (14) | geometric approx. |
|---|---|---|---:|---:|---:|---:|
{e}

* Eq. (14) matches the expected-evidence recursion to within one step and the
  stochastic mean closely.
* The geometric-trajectory approximation over-predicts latency by a factor
  {min(ratio):.2f}-{max(ratio):.2f} at omega = 3, because each failure adds omega
  pseudo-counts.

![theory](figures/{figs[0]})
"""


def main(argv=None) -> None:
    r = run()
    figs = _figs(r)
    write_results(EXP, {**r, "figures": figs})
    write_readme(EXP, readme(r, figs))
    print(readme(r, figs))


if __name__ == "__main__":
    main()
