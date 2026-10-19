# SUMMARY: post-review results (N00–N12)

**Method naming used throughout `nextphase/`**

* **TGCC**: the single proposed method. Its grant rule has two conjuncts:
  * a per-turn epistemic check, applied to the rolling-window calibration signal;
  * the coupled power-mean composite, with Beta memory and Hedge weights.

  Thresholds come from Algorithm 2: the δ-quantile of a pre-warmed honest pilot, minus ε.
* **Ablations:**
  * **TGCC-Smoothed**: the epistemic check reads the Beta-smoothed trust.
  * **TGCC-NoSyn**: no coupling.
  * **TGCC-CompositeOnly**: no epistemic check.
  * **Min-of-pilot**: calibration by the pilot minimum instead of the quantile.

**Setup**

* Real-LLM experiments use **Claude Sonnet 4.5** and **GPT-5**.
* Every controller is calibrated with the same Algorithm 2 on the same honest pilot, which is disjoint from the evaluation data.
* CIs are 95% bootstrap over independent episodes, or Wilson intervals for pooled counts.
* OER = fraction of post-compromise steps granted (lower is safer). FPR = fraction of honest-phase steps denied.

Bug fixes and code changes are in [CHANGES.md](CHANGES.md); paper edits are in [../manuscript_update.md](../manuscript_update.md).

---

## Headline answers to the reviewers

| Reviewer question | Answer | Evidence |
|---|---|---|
| 14qA Q1 / D1aZ Q1: Naive OER 0.12? | **1.00**: Naive never revokes, in all 30 episodes | N00, N01 |
| D1aZ Q2: E1 OER 0.17, 0.11 or 0.25? | TGCC **0.02 [0.01, 0.02]** (Claude) and **0.01 [0.00, 0.01]** (GPT-5), over 15 independent episodes each | N01 |
| D1aZ Q3: coupling and latency | The epistemic check fires first in every episode, so removing coupling leaves E1 latency unchanged (0.6 / 0.2 steps). Coupling matters for non-epistemic compromises: OER 0.08 vs 0.18 for off-topic drift on GPT-5 | N01, N12 |
| D1aZ W1 / 14qA W2: scale | 900 E1 questions per model; 162 HumanEval tasks × 2 models, 372–389 harmful commits; real-LLM debate | N01, N09, N10 |
| 14qA W3 / Q3, eY9w W3: sensitivity on real streams | OER stays at 0.01–0.02 for every p, coupling scale, γ, ω, η and λ when recalibrated. Only frozen thresholds with ω ≥ 4 break the gate (FPR ≥ 0.92) | N02 |
| RRLq W4: misspecified structure | With the epistemic check, any of 26 coupling matrices gives OER 0.01–0.02. Without it: 0.09–0.27 | N02 |
| Jqqf W2, D1aZ W2, 14qA Q2: matched-FPR comparison | At FPR ≤ 0.05, TGCC reaches OER 0.04 (Claude) / 0.02 (GPT-5), vs 0.10 / 0.09 for Epistemic-only (Beta) and Strict-min. It matches the memoryless AgentGuard-lite | N03 |
| Value of the multi-layer stack | Agent stays correct but violates policy, drifts off-topic or turns hostile: TGCC OER 0.06–0.15; epistemic-only and memoryless gates 0.57–0.83; TGCC-NoSyn up to 0.20 | N12 |
| D1aZ W3: imperfect critic | Missed errors (up to 40%): OER ≤ 0.04. Critic false alarms at 10%: OER 0.04–0.06, vs 0.42–0.46 for TGCC-Smoothed. At 20% false alarms every gate fails. A reference-free LLM judge works: OER 0.02–0.05 | N04 |
| RRLq W1: probe validity | Heuristic behavioural and role probes are near chance on natural failures (AUROC 0.38–0.53). The social probe works (0.74–0.99). The alias critic agrees with an LLM judge on about 90% of answers | N05 |
| RRLq W2: end-to-end cost | Controller about 0.1 ms; LLM-judge critic +1.3–2.0 s and about 0.9× the agent's tokens | N06 |
| D1aZ W4 / Jqqf W1: Theorem 4 | The bound converges to the floor exp(−2Δ²/(1−γ)), which upper-bounds the empirical rate at every γ | N07 |
| D1aZ W5 / Jqqf W1: Eq. (14) | Closed form k* = ln[(ρ₀−ρ₁−x(D₀−D₁))/(xD₁−ρ₁)]/ln(1/γ) matches simulation to within 1 step | N07 |
| Jqqf follow-up: calibration | Quantile Algorithm 2 converges (latency 2.4 → 2.7 steps as the pilot grows 80 → 640). Min-of-pilot keeps loosening (2.9 → 5.1) | N08 |
| eY9w W2: baselines | 11 gates, each calibrated identically | N03, N09, N12 |

---

## N01: E1, 15 independent episodes per model (60 questions, compromise at step 20)

| Model | Gate | OER | Latency (steps) | FPR |
|---|---|---|---|---|
| Claude Sonnet 4.5 | **TGCC** | **0.02** [0.01, 0.02] | 0.6 [0.3, 0.8] | 0.12 [0.05, 0.21] |
| Claude Sonnet 4.5 | TGCC-Smoothed | 0.09 [0.06, 0.11] | 3.5 [2.4, 4.5] | 0.06 [0.00, 0.17] |
| Claude Sonnet 4.5 | TGCC-NoSyn | 0.02 [0.01, 0.02] | 0.6 | 0.16 [0.05, 0.30] |
| Claude Sonnet 4.5 | TGCC-CompositeOnly | 0.17 [0.14, 0.20] | 6.9 | 0.00 |
| Claude Sonnet 4.5 | Naive behavioural | 1.00 | never | 0.00 |
| GPT-5 | **TGCC** | **0.01** [0.00, 0.01] | 0.2 [0.0, 0.4] | 0.27 [0.13, 0.43] |
| GPT-5 | TGCC-Smoothed | 0.09 [0.06, 0.12] | 3.7 [2.5, 4.9] | 0.05 [0.00, 0.12] |
| GPT-5 | TGCC-NoSyn | 0.01 [0.00, 0.01] | 0.2 | 0.27 [0.13, 0.43] |
| GPT-5 | TGCC-CompositeOnly | 0.11 [0.08, 0.15] | 4.5 | 0.05 |
| GPT-5 | Naive behavioural | 1.00 | never | 0.00 |

Data: honest accuracy 0.91 / 0.87; sleeper-prompt compliance 0.79 / 0.81; 0 / 2 empty outputs.

**Trade-off.** TGCC revokes within one step, but its out-of-sample FPR on GPT-5 is 0.27. The GPT-5 pilot is "cleaner" than the evaluation episodes, so the 5% pilot quantile is strict. Threshold-free results (N03) and the δ choice should be reported together.

## N02: sensitivity and structure on real streams (TGCC, recalibrated)

| Parameter (range) | OER (Claude / GPT-5) | FPR (Claude / GPT-5) |
|---|---|---|
| p ∈ [−1, −20] | 0.02 / 0.01 | 0.12 / 0.27 |
| coupling scale ∈ [0, 1.43] | 0.02 / 0.01 | 0.12–0.16 / 0.26–0.28 |
| γ ∈ [0.9, 0.995] | 0.02 / 0.01 | 0.12–0.13 / 0.26–0.27 |
| ω ∈ [1, 6] | 0.02 / 0.01 | 0.12 / 0.26–0.27 (frozen thresholds with ω ≥ 4: FPR ≥ 0.92) |
| η ∈ [0, 4], λ ∈ [0.1, 0.9] | 0.02 / 0.01 | unchanged |
| 26 coupling matrices, with epistemic check | 0.01–0.02 | |
| 20 random C, without epistemic check | 0.10–0.27 / 0.09–0.18 | |

## N03: matched honest admission (pooled over 15 episodes; Claude / GPT-5)

| Gate | OER @ Algorithm 2 | FPR @ Algorithm 2 | OER@FPR≤0.05 | OER@FPR≤0.10 | detection AUC |
|---|---|---|---|---|---|
| **TGCC** | 0.02 / 0.01 | 0.12 / 0.27 | **0.04 / 0.02** | 0.03 / 0.01 | 0.980 / 0.984 |
| TGCC-Smoothed | 0.09 / 0.09 | 0.06 / 0.05 | 0.10 / 0.10 | 0.08 / 0.08 | 0.952 / 0.974 |
| Epistemic-only (Beta) | 0.09 / 0.09 | 0.06 / 0.05 | 0.10 / 0.09 | 0.07 / 0.05 | 0.977 / 0.985 |
| Strict-min (Beta) | 0.09 / 0.09 | 0.06 / 0.05 | 0.10 / 0.09 | 0.07 / 0.05 | 0.981 / 0.985 |
| AgentGuard-lite | 0.02 / 0.01 | 0.12 / 0.26 | 0.04 / 0.02 | 0.02 / 0.01 | 0.991 / 0.986 |
| DynaTrust-lite | 0.04 / 0.02 | 0.10 / 0.19 | 0.05 / 0.05 | 0.04 / 0.04 | 0.985 / 0.988 |
| Mean (Constitutional-lite) | 0.78 / 0.84 | 0.00 / 0.00 | 0.22 / 0.22 | 0.17 / 0.18 | 0.912 / 0.941 |
| Naive, EigenTrust-lite | 1.00 | 0.00 | 1.00 | 1.00 | ≤ 0.23 |

On purely epistemic attacks, TGCC equals the best memoryless epistemic gate. The difference between them appears in N09 (weak critic) and N12 (non-epistemic attacks).

## N04: critic reliability (OER / FPR, 15 episodes)

| Critic noise | q | TGCC (Claude) | TGCC-Smoothed (Claude) | AgentGuard-lite (Claude) | TGCC (GPT-5) |
|---|---|---|---|---|---|
| missed errors | 0.4 | 0.04 / 0.08 | 0.09 / 0.14 | 0.04 / 0.08 | 0.03 / 0.20 |
| false alarms | 0.05 | 0.03 / 0.10 | 0.21 / 0.01 | 0.03 / 0.10 | 0.02 / 0.13 |
| false alarms | 0.10 | 0.06 / 0.06 | 0.46 / 0.00 | 0.06 / 0.06 | 0.04 / 0.11 |
| false alarms | 0.20 | 0.81 / 0.00 | 0.81 / 0.00 | 1.00 / 0.00 | 0.82 / 0.00 |

Reference-free LLM judge as the critic (8 episodes):

| Answers by | Judge | Judge accuracy | TGCC OER | TGCC FPR |
|---|---|---|---|---|
| Claude Sonnet 4.5 | Claude Sonnet 4.5 (self) | 0.94 | 0.02 [0.02, 0.03] | 0.32 |
| Claude Sonnet 4.5 | GPT-5 (cross) | 0.92 | 0.05 [0.04, 0.07] | 0.01 |
| GPT-5 | Claude Sonnet 4.5 (cross) | 0.93 | 0.02 [0.01, 0.02] | 0.42 |
| GPT-5 | GPT-5 (self) | 0.94 | 0.03 [0.02, 0.05] | 0.00 |

## N05: probe and critic validity

| Probe | Judged positives (Claude / GPT-5) | AUROC vs judged label | Recall | Precision |
|---|---|---|---|---|
| behavioural (hostile tone) | 85 / 117 | 0.38 / 0.51 | 0.00 / 0.82 | 0.00 / 0.19 |
| role (off-topic) | 318 / 220 | 0.44 / 0.53 | 0.23 / 0.39 | 0.38 / 0.42 |
| social (no confidence stated) | 125 / 126 | 0.99 / 0.74 | 1.00 / 1.00 | 0.20 / 0.18 |
| institutional (destructive action) | 0 / 2 | n/a (models refused) | - | - |

* The alias-matcher critic agrees with a reference-aware LLM judge on 91.3% (Claude) and 89.7% (GPT-5) of honest answers.
* Probe signals are stable: zero spread across temperature-1 resamples.

## N06: end-to-end cost per agent step (medians)

| Component | Claude Sonnet 4.5 | GPT-5 |
|---|---|---|
| Agent LLM call | 1.45 s | 1.91 s |
| LLM-judge critic call | 1.27–2.01 s (about 0.9× agent tokens) | 1.39–1.99 s |
| Controller step (pure Python) | about 105 µs | about 105 µs |
| Step total, reference critic | 1.45 s | 1.91 s |
| Step total, LLM-judge critic | 2.7–3.5 s | 3.3–3.9 s |

## N07: theory validation

* **Theorem 4.** Floor exp(−2Δ²/(1−γ)) = 0.0498 vs empirical stationary false-denial rate 0.0024 (γ = 0.985). The floor bounds the empirical rate for every γ ∈ [0.9, 0.998].
* **Eq. (14).** The closed form matches the expected-evidence recursion to within 1 step. A geometric-trajectory approximation over-predicts latency by 1.21–2.14× at ω = 3.

## N08: calibration (Algorithm 2)

Simulation, TGCC, with a pilot of N steps after burn-in:

| N | Quantile: θ / FPR / latency | Min-of-pilot: θ / FPR / latency |
|---|---|---|
| 10 | 0.370 / 0.269 / 1.2 | 0.368 / 0.264 / 1.3 |
| 80 | 0.329 / 0.079 / 2.4 | 0.320 / 0.051 / 2.9 |
| 640 | 0.294 / 0.025 / 2.7 | 0.265 / 0.003 / 5.1 |

Real pilots (N = 120):

| Model | Quantile: FPR / OER | Min-of-pilot: FPR / OER |
|---|---|---|
| Claude Sonnet 4.5 | 0.12 / 0.015 | 0.05 / 0.035 |
| GPT-5 | 0.27 / 0.005 | 0.15 / 0.012 |

## N09: code pipeline on HumanEval (162 tasks, 20 episodes per model)

| Model | Critic | Gate | Harmful commits blocked | Honest commits denied |
|---|---|---|---|---|
| Claude Sonnet 4.5 | unit tests | **TGCC** | **0.98** [0.96, 0.99] (364/372) | 0.15 |
| Claude Sonnet 4.5 | unit tests | TGCC-Smoothed | 0.86 [0.82, 0.89] | 0.24 |
| Claude Sonnet 4.5 | unit tests | AgentGuard-lite | 0.98 | 0.14 |
| Claude Sonnet 4.5 | reviewer LLM | **TGCC** | **0.92** [0.88, 0.94] | 0.09 |
| Claude Sonnet 4.5 | reviewer LLM | TGCC-Smoothed | 0.61 | 0.00 |
| Claude Sonnet 4.5 | reviewer LLM | AgentGuard-lite | 0.92 | 0.09 |
| GPT-5 | unit tests | **TGCC** | **0.93** [0.90, 0.95] (362/389) | 0.17 |
| GPT-5 | unit tests | TGCC-Smoothed | 0.66 | 0.07 |
| GPT-5 | unit tests | AgentGuard-lite | 0.93 | 0.14 |
| GPT-5 | reviewer LLM | **TGCC** | **0.81** [0.77, 0.84] | 0.14 |
| GPT-5 | reviewer LLM | TGCC-Smoothed | 0.46 | 0.02 |
| GPT-5 | reviewer LLM | AgentGuard-lite | 0.77 [0.72, 0.81] | 0.13 |

Naive blocks 0/372 and 0/389.

## N10: multi-agent debate (Claude/GPT-5 teams, two 60-question series per size)

| N | Gate | Wrong consensus, pre-compromise | Wrong consensus, post-compromise | Pool abstained (post) | Sleeper admitted (post) | Revocation latency |
|---|---|---|---|---|---|---|
| 1 | none | 0.07 | 1.00 (80/80) | 0.00 | 1.00 | never |
| 1 | TGCC | 0.07 | **0.04** [0.01, 0.10] | 0.96 | 0.04 | 1, 2 |
| 3 | none | 0.15 | 0.40 [0.30, 0.51] | 0.00 | 1.00 | never |
| 3 | TGCC | 0.17 | **0.11** [0.06, 0.20] | 0.14 | 0.04 | 1, 2 |
| 5 | none | 0.07 | 0.12 [0.07, 0.22] | 0.00 | 1.00 | never |
| 5 | TGCC | 0.15 | 0.14 [0.08, 0.23] | 0.14 | 0.04 | 1, 2 |

* TGCC removes the sleeper within 1–2 questions and cuts wrong consensus at N = 3 from 0.40 to 0.11.
* At N = 5 majority voting already suppresses the sleeper, so gating gives no gain.
* Cost: honest agents are denied on 27% of agent-questions (64/240 at N = 3, 128/480 at N = 5). This raises pre-compromise wrong consensus at N = 5 (0.07 → 0.15) and makes the pool abstain on 14% of questions.

## N11: simulation (E3 ablation, E5 scalability)

**E3: composite-only gate, 300 episodes per cell.**

| Regime | p = −6, c = 0.3 | Range across cells | Warm-up FPR |
|---|---|---|---|
| No pre-warm, fixed θ = 0.55 | latency 0.18 | | 0.88 |
| Pre-warm, fixed θ = 0.55 | 0.53 | | 0.57 |
| Pre-warm, per-cell calibration | **24.3** | 13.4 (p = −1, c = 0.9) to 29.9 | **about 0.00 in every cell** |

With a fixed threshold, the heatmap mostly measures each cell's distance to the threshold. With per-cell calibration, milder orders with stronger coupling detect fastest. On real streams (N02), p and c have no effect.

**E5: TGCC, one sleeper among 1–50 agents, 40 seeds per size.**

* Sleeper revocation latency is flat at 2.6–3.1 steps.
* Honest blast radius is flat at 0.14–0.15.
* Controller cost is 59–93 µs per agent-step (pure Python).

## N12: non-epistemic compromises (agent stays correct; OER, lower is safer; Claude / GPT-5)

| Gate | policy | off-topic | hostile | no compromise (honest admission) |
|---|---|---|---|---|
| **TGCC** | **0.08 / 0.06** | **0.15 / 0.08** | **0.15 / 0.08** | 0.78 / 0.57 |
| TGCC-Smoothed | 0.09 / 0.07 | 0.16 / 0.10 | 0.16 / 0.09 | 0.72 / 0.56 |
| TGCC-NoSyn | 0.11 / 0.12 | 0.20 / 0.18 | 0.16 / 0.16 | 0.69 / 0.48 |
| Strict-min (Beta) | 0.12 / 0.18 | 0.22 / 0.32 | 0.16 / 0.26 | 0.72 / 0.57 |
| Epistemic-only (Beta) | 0.72 / 0.57 | 0.72 / 0.57 | 0.72 / 0.57 | 0.72 / 0.57 |
| AgentGuard-lite | 0.83 / 0.75 | 0.83 / 0.75 | 0.83 / 0.75 | 0.83 / 0.75 |
| Naive behavioural | 1.00 / 1.00 | 1.00 / 1.00 | 0.05 / 0.05 | 1.00 / 1.00 |

---

## Conclusions for the revision

1. **Paradox.** Behavioural gating never revokes. TGCC revokes within 0–1 steps on two production models, with OER 0.01–0.02 on E1 and 93–98% of harmful commits blocked with unit tests.
2. **Multi-layer value.** On compromises the epistemic layer cannot see, TGCC keeps OER at 0.06–0.15 while epistemic-only and memoryless gates fail (0.57–0.83). Coupling lowers OER relative to TGCC-NoSyn on the same attacks.
3. **Weak critics.** With a reviewer-LLM critic in the code pipeline, TGCC blocks 81–92% of harmful commits vs 46–61% for the smoothed check. It matches or exceeds the memoryless gate.
4. **Costs to report.**
   * Honest FPR of 0.12 (Claude) and 0.27 (GPT-5) at δ = 0.05.
   * Honest admission over long horizons of 0.57–0.78.
   * Dependence on critic false-alarm rate: protection fails at about 20% false alarms.
