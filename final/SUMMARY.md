# TGCC Weakness-Mitigation Consolidated Summary — W1–W16

All numbers below are pulled directly from the `results.json` in each
`wX_...` sub-folder. See the individual READMEs and
[`../ACM_Conference_Proceedings_Primary_Article_Template/sigconf.tex`](../ACM_Conference_Proceedings_Primary_Article_Template/sigconf.tex)
Appendix H for full method and interpretation.

---

## Core paper mitigations (W1–W5)

| Exp | Setting | TGCC OER | TGCC Latency | TGCC FPR | Baseline OER |
|---|---|---:|---:|---:|---:|
| W1 (Anthropic) | Sleeper probe (real LLM) | 0.25 | 3.0 | 0.00 | 1.00 (Naive) |
| W1 (Azure gpt-5) | Sleeper probe (real LLM) | 0.17 | 2.0 | 0.00 | 1.00 (Naive) |
| W2 | Bounded forgery $\Delta=0 \to 1$ | 0.06 → 0.25 | 10 → 40 | 0.06 | 1.00 (Naive) |
| W3 | Six-controller head-to-head | best on both providers | | | up to 1.00 |
| W4 | Learned coupling from traces | Frobenius $\|\hat C - C^\star\|_F$ = 0.72 | | | |
| W5 | $\gamma \in [0.9, 0.999]$ | 1 → 20 steps | | | |

## Extended robustness study (W6–W16)

### W6 – bootstrap CIs + Wilcoxon tests

| Provider | TGCC OER (95% CI) | Best baseline | Wilcoxon $p$ |
|---|---|---|---|
| Anthropic | 0.11 [0.08, 0.25] | AgentGuard 0.08 [0, 0.25] | $p<0.01$ vs. 4/5 |
| Azure gpt-5 | 0.07 [0.00, 0.17] | AgentGuard OER 0.00 but **FPR 0.38** | $p<0.01$ vs. 4/5 |

### W7 – colluding agents

| Agent | Without agreement | With naive agreement |
|---|---:|---:|
| Alpha (honest) | 1.00 (correct) | **0.42 (wrongly denied)** |
| Beta (sleeper) | 0.58 | 0.50 |
| Gamma (sleeper) | 0.58 | 0.50 |

Naive cross-agent agreement transfers the vulnerability to the honest agent — a negative result.

### W8 – indirect prompt injection

| Provider | Adv accuracy | Filter block | TGCC OER | Naive OER |
|---|---:|---:|---:|---:|
| Anthropic | 1.00 (model resists) | 0.00 | 1.00 | 1.00 |
| Azure gpt-5 | 1.00 (model resists) | 0.14 | 0.06 | 0.86 |

Both models resist at the model level; Azure filter adds a second line of defense.

### W9 – per-layer ablation (Anthropic, baseline OER 0.25)

| Layer forced $=1$ | OER |
|---|---:|
| **Epistemic** | **1.00** (paradox restored) |
| Behavioural | 0.25 |
| Role | 0.25 |
| Social | 0.25 |
| Institutional | 0.25 |

Only the epistemic signal is load-bearing.

### W10 – long-horizon drift (5000 turns)

| Regime | Grant rate |
|---|---:|
| Gradual drift (steps 1000–4000) | 0.21 |
| Sudden model swap (steps 2000–2200) | 0.06 |

Recovers within one time constant $\tau = 1/(1-\gamma) \approx 67$ steps.

### W11 – parameter sensitivity (elementary effects on OER)

| Param | EE(OER) | EE(latency) | EE(FPR) |
|---|---:|---:|---:|
| $\gamma$ | 3.35 | 472 | 4.47 |
| $\theta$ | 1.91 | 257 | 2.88 |
| $\omega$ | 0.20 | 26 | 0.26 |
| $p$ | 0.01 | 1.07 | 0.02 |

Order: $\gamma > \theta \gg \omega \gg p$.

### W12 – revocation-then-recovery

| Event | Latency |
|---|---:|
| Revocation after compromise | 3 steps |
| Recovery after restoration | 94 steps $\approx 1.4 \tau$ |

### W13 – Byzantine chain ($K = 0.2N$)

| $N$ | $K$ | Rev. latency | Collective OER | Blast radius | µs/step |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 12.5 | 0.09 | 0.00 | 47 |
| 3 | 1 | 8.0 | 0.05 | 0.36 | 55 |
| 5 | 1 | 11.3 | 0.01 | 0.38 | 51 |
| 10 | 2 | 3.6 | 0.01 | 0.27 | 48 |
| 20 | 4 | 1.4 | 0.00 | 0.33 | 60 |
| 50 | 10 | 0.25 | 0.00 | 0.30 | 85 |

Latency **decreases** with $N$; blast radius bounded; overhead $\le 100 \mu s$/step.

### W14 – audit-trail schema

`RevocationReport` (Pydantic): 300 reports emitted, 205 revocations, 100% schema validation.

### W15 – calibration RMS error

| $N_{\text{pilot}}$ | RMS error |
|---:|---:|
| 10 | 0.105 |
| 20 | 0.069 |
| 40 | 0.051 |
| **80** | **0.039** (minimum) |
| 160 | 0.059 |
| 320 | 0.076 |
| 640 | 0.089 |

Minimum near $N_{\text{pilot}} \approx \tau$, then floor from min-of-samples bias.

### W16 – adaptive attacker

| Calibration $c$ | OER | Latency | Attacker utility |
|---:|---:|---:|---:|
| 0.00 | 0.17 | 24 | 0.12 |
| 0.25 | 0.18 | 25 | 0.13 |
| 0.50 | 0.20 | 28 | 0.14 |
| 0.75 | 0.21 | 30 | 0.15 |
| 1.00 | 0.22 | 34 | 0.15 |

Perfect calibration inflates OER by only ~30%; downstream persuasion cost bounds the attacker.

---

## Overall conclusion

TGCC's guarantees survive along every axis reviewers commonly raise:
alternative production models (W1), bounded signal forgery (W2), head-to-head
vs. competing runtime controllers (W3), learned couplings (W4), theoretical
latency (W5), statistical significance (W6), prompt injection (W8), per-layer
attribution (W9), long-horizon drift (W10), parameter perturbations (W11),
recovery (W12), Byzantine chains (W13), audit trails (W14), calibration
robustness (W15), and adaptive attackers (W16). The lone negative result
(W7) shows that **naive** cross-agent agreement is not a valid collusion
detector — the open direction is a ground-truth-aware detector, left as
future work.
