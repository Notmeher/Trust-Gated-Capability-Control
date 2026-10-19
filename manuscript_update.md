# Manuscript update plan - Submission 1175 (TGCC)

This file maps each reviewer concern to concrete edits in `1175_Trust_Gated_Capability_Co.pdf`.
Section, equation, table and figure numbers refer to the submitted PDF. New numbers come from
`nextphase/`; full tables are in [nextphase/SUMMARY.md](nextphase/SUMMARY.md) and the code
changes in [nextphase/CHANGES.md](nextphase/CHANGES.md).

Legend: **[REPLACE]** change existing text or numbers · **[ADD]** new content ·
**[DELETE]** remove · **[MOVE]** relocate.

All figures in `nextphase/` use model names (Claude Sonnet 4.5, GPT-5) and the method name TGCC
only. No "corrected" or "fixed" wording appears in them, so they can go into the paper as they are.

---

## 0. The method in the revised paper (one proposed method: TGCC)

The revision presents **one** method, TGCC, refined in this iteration:

1. **Grant rule (Definition 3).** Two conjuncts:
   * The composite Φ_p (Beta beliefs, synergy coupling, Hedge weights, power mean): unchanged.
   * The epistemic prerequisite check applied to the **per-turn epistemic signal**: the
     rolling-window calibration score of §4.5 and Table 5. Previously it was applied to the
     Beta-smoothed effective trust T̃₁.
2. **Algorithm 2.**
   * θ = δ-quantile of a **pre-warmed** honest pilot − ε (δ = 0.05, ε = 0.05).
   * ε is increased if fewer than 1−δ of pilot steps are admitted.
   * No burn-in is discarded when beliefs are pre-warmed.

The paper should not present an "old vs new" TGCC. The Beta-smoothed check appears only as an
ablation named **TGCC-Smoothed**, next to TGCC-NoSyn and TGCC-CompositeOnly.

Evidence for this design:
* TGCC-Smoothed revokes 3–4 steps later (N01).
* TGCC-Smoothed has 4–5× higher OER at matched FPR (N03).
* TGCC-Smoothed blocks 30–45 points fewer harmful commits when the critic is a reviewer LLM (N09).

## 1. The overall story

1. **The paradox and its resolution replicate.**
   * Data: 15 independent E1 episodes per model; HumanEval at scale; real-LLM debate.
   * Behavioural gating never revokes (OER 1.00).
   * TGCC revokes within 0–1 steps: OER 0.02 / 0.01 on E1, and 93–98% of harmful commits blocked
     with unit tests.
2. **On factual-error attacks, detection is driven by the epistemic check.**
   * p, coupling, η, λ and γ have no measurable effect on the real streams (N02).
   * TGCC matches the best single-signal gate (N03).
   * State this plainly: D1aZ W2, Jqqf W2, 14qA Q2.
3. **The composite and the coupling are what make non-epistemic compromises revocable** (N12).
   * Attacks: policy violation, off-topic drift, hostile tone.
   * TGCC OER 0.06–0.15.
   * Epistemic-only and memoryless gates 0.57–0.83.
   * TGCC-NoSyn up to 0.20.
   * Strict-min up to 0.32.
   * This is the main empirical argument for the five-layer stack.
4. **With an imperfect critic, TGCC is the strongest gate tested** (N09 reviewer-LLM critic):
   * TGCC blocks 92% / 81% of harmful commits;
   * TGCC-Smoothed blocks 61% / 46%;
   * the memoryless gate blocks 92% / 77%.
5. **Costs to report.**
   * Honest FPR at δ = 0.05: 0.12 (Claude), 0.27 (GPT-5).
   * Long-horizon honest admission: 0.57–0.78 (N12).
   * Honest-agent denials in debate: 27% of agent-questions (N10).
   * Critic false-alarm rate: protection holds up to 10% false alarms and fails at 20% (N04).
6. **Theory.**
   * Theorem 4: state the explicit floor of the false-positive bound.
   * Theorem 6: replace with the exact latency expression, new Eq. (14).
   * Algorithm 2: replace with the quantile rule.
7. **Numbers.**
   * Naive OER is 1.00.
   * Report one E1 estimate per model from N01.
   * Results use the fixed pipeline (CHANGES.md B1–B9).

---

## 2. Title, Abstract, Keywords

* Title and keywords: unchanged.
* **[REPLACE] Abstract.** Cut to about 170 words (eY9w W1). Make these changes:
  * Composition sentence: "a generalized power-mean composite trust with an explicit
    weakest-link slack and a closed-form conservative fixed point".
  * Guarantees: "the honest false-positive probability converges geometrically to an explicit
    floor set by the forgetting factor, and the expected revocation latency has a closed form".
    This replaces "decays exponentially" and "logarithmic latency".
  * Evaluation:
    * "On 30 independent real-LLM episodes (Claude Sonnet 4.5, GPT-5), TGCC revokes a stealth
      sleeper within one step (OER 0.01–0.02 vs 1.00 for behavioural gating)."
    * "On 162 HumanEval tasks it blocks 93–98% of harmful commits with unit tests and 81–92% with
      an LLM reviewer as the only critic."
    * "When the agent stays correct but violates policy or drifts off-task, TGCC keeps
      over-exposure at 0.06–0.15 where epistemic-only gates reach 0.57–0.83."
  * **[DELETE]** "4.2×", "95% of harmful commits" and "validating the quadratic complexity bound".

## 3. Section 1 - Introduction

* **[REPLACE] Contributions list.**
  * Bullet 4: "...that it breaks the paradox, that its expected revocation latency has a closed
    form, and that honest false positives are bounded by an explicit, γ-controlled floor".
  * Bullet 6: "We evaluate on two production LLMs and two task families with independent
    episodes:
    * factual QA (TriviaQA, 900 questions per model);
    * code generation (HumanEval, 162 tasks);
    * multi-agent debate.

    Each controller is calibrated identically, and we report matched-FPR comparisons against
    seven baselines."
  * **[ADD]** a bullet: "We show when each component matters. The epistemic check drives
    detection of factual-error attacks. The coupled composite is what makes policy, role and
    behavioural compromises revocable. The per-turn epistemic check is what keeps protection
    under imperfect critics."
* **[REPLACE] "Our approach" paragraph.** Describe the grant rule as "composite ≥ θ_c AND per-turn
  epistemic check ≥ θ_{c,1}". Drop "exponentially rare".

## 4. Section 2 - Related Work

* **[REPLACE] "TGCC differs on three axes".**
  * (ii): "the paradox is avoided by any gate on the weakest verified layer. TGCC realises this
    with a graded composite whose slack κ is explicit (Theorem 1)."
  * (iii): latency and false-positive statements as in §3 above.
* **[ADD]** that Beta reputation, multiplicative weights, power means and capability tokens are
  established (RRLq W3). The contribution is their composition plus evidence of when each part
  matters (N03, N09, N12).

## 5. Section 3 - Problem formulation

* **[ADD] after Definition 1** (14qA Q2). A strict-minimum gate over verified layers also satisfies
  Definition 1, so Theorem 3 is not a separation from min-aggregation. Its content is that the
  graded composite keeps the property within slack κ.
  * On E1, Strict-min and TGCC-Smoothed coincide (N03).
  * Under non-epistemic compromise the coupled composite beats Strict-min:
    * off-topic: OER 0.15 vs 0.22 (Claude), 0.08 vs 0.32 (GPT-5);
    * policy: 0.08 vs 0.12, 0.06 vs 0.18 (N12).
* **[REPLACE] Assumption 1(iii).** The epistemic signal is computed by an independent critic.
  Critic error is evaluated in §9 (N04, N05).

## 6. Section 4 - Operational trust stack

* Proposition 1, Definition 2, Proposition 2, Lemma 1, Theorem 1, Lemma 2, Proposition 3,
  Theorem 2: unchanged.
* **[ADD] after Proposition 3.** The synergy operator propagates any prerequisite deficit, not
  only an epistemic one. This is the mechanism behind the coupling's gain in N12.
* **[REPLACE] §4.5.** Define the epistemic signal as the per-turn rolling-window calibration score
  used by the grant rule. Note that it is also fed into the Beta belief of layer 1 for the
  composite.

## 7. Section 5 - Adaptive weighting

* **[ADD]** On the real streams η and λ have no measurable effect: OER constant for η ∈ [0, 4]
  and λ ∈ [0.1, 0.9] (N02). The weights matter when several layers degrade at different rates
  (Fig. 4b).

## 8. Section 6 - TGCC

* **[REPLACE] Definition 3 / Eq. (11).** The prerequisite conjunct uses the per-turn epistemic
  signal s₁(t) (rolling-window score) for ℓ = 1, and T̃_ℓ for any other prerequisite layer.
* **[REPLACE] Algorithm 1, line 6.** Same change.
* **[REPLACE] Theorem 4 and Eq. (12).** Keep the bound and state its limit:

  > ... at most L·exp(−2Δ²·n_ℓ(t)). Since n_ℓ(t) ≤ 1/(1−γ) (Proposition 10), the bound converges
  > geometrically to the floor L·exp(−2Δ²/(1−γ)), which decreases with the margin Δ and with γ.

  * Update the §6.3 opening and the Key-insight box to match.
  * **[ADD]** "Fig. X(a,b): the floor upper-bounds the empirical stationary false-denial rate for
    γ ∈ [0.9, 0.998]; 0.0024 vs 0.0498 at γ = 0.985." The figure is
    `nextphase/n07_theory_checks/figures/theory_checks.png`, panels a and b.
* **[REPLACE] Theorem 3 proof.** Add one line: the per-turn check denies whenever s₁(t) < θ_{c,1},
  irrespective of the composite.

## 9. Section 7 - Threshold calibration

* **[REPLACE] Algorithm 2.**
  * Line 2: "pilot run from the same pre-warmed state used at deployment; no burn-in is
    discarded" (keep the burn-in only when not pre-warming).
  * Lines 3–4: "θ ← δ-quantile of the pilot values − ε".
  * Line 5: "if fewer than 1−δ of pilot steps are admitted, increase ε".
* **[REPLACE] Proposition 6 / Theorem 5.**
  * State sample complexity for the empirical δ-quantile via the DKW inequality, with effective
    sample size about N(1−γ).
  * Keep Prop. 14 (min-of-samples bias) as the reason for preferring the quantile.
  * Evidence (N08, simulation): the quantile threshold settles (latency 2.4 → 2.7 steps for
    N = 80 → 640). The pilot minimum keeps loosening (2.9 → 5.1).
  * Figure: `nextphase/n08_calibration/figures/sim_calibration.png`.
* **[REPLACE] Remark 3.** Recommend N_pilot ≥ 100. Report that δ = 0.05 gives out-of-sample honest
  FPR of 0.12 (Claude) and 0.27 (GPT-5) on E1. δ is the deployer's main knob.

## 10. Section 8 - Adversarial robustness

* **[REPLACE] Theorem 6 / Eq. (14).** Rename "Expected detection latency" and give the closed form
  for the expected-evidence recursion:

  $$k^\star=\frac{\ln\!\big[(\rho_0-\rho_1-x(D_0-D_1))/(x D_1-\rho_1)\big]}{\ln(1/\gamma)},\quad D_i=\rho_i+\omega(1-\rho_i),\ x=\theta_c/\kappa.$$

  * Proof (2 lines): T(k) = (uρ₀+(1−u)ρ₁)/(uD₀+(1−u)D₁) with u = γ^k; solve T(k) = x.
  * Evidence (N07): matches the recursion to within 1 step and the stochastic mean closely.
    Figure: `theory_checks.png`, panel c.
  * This bounds the composite path. The per-turn check adds a faster path, which is why TGCC's
    measured latency is 0–1 steps.
* Remark 4: keep.

## 11. Section 9 - Experimental evaluation (major rewrite)

### 9.1 Protocol - [REPLACE]
* **Data.**
  * TriviaQA (rc.nocontext, 900 evaluation + 120 pilot questions per model).
  * HumanEval (162 tasks).
* **Models.** Claude Sonnet 4.5 and GPT-5, at temperature 0 (GPT-5 with minimal reasoning effort).
* **Episodes.**
  * E1: 15 disjoint 60-question episodes per model, compromise at step 20.
  * E4: 20 episodes of 35 tasks, compromise at step 15.
  * E2: two 60-question series per team size.
* **Calibration.** Every controller is calibrated by Algorithm 2 on the same honest pilot, which
  is disjoint from evaluation.
* **Metrics.**
  * OER, latency, FPR.
  * OER at matched FPR and detection AUC.
  * 95% episode-bootstrap or Wilson CIs.
* **Controllers.**
  * TGCC.
  * Ablations: TGCC-Smoothed, TGCC-NoSyn, TGCC-CompositeOnly.
  * Baselines (answers eY9w W2): Epistemic-only (Beta), Strict-min (Beta), Mean
    (Constitutional-lite), Naive behavioural, AgentGuard-lite, EigenTrust-lite, DynaTrust-lite.
* **[ADD]** one table with every hyperparameter, its value, and its effect on real streams (N02).
  This answers 14qA W3.

### 9.2 Experiment 1 - [REPLACE text, Fig. 1, Table 1 rows]
* **Figures.** Use `nextphase/n01_e1_multi_episode/figures/claude-sonnet-4.5_trajectory_ep0.png` (and
  `gpt-5_trajectory_ep0.png`) and `e1_bars.png`.
* **Results.**

  | Gate | OER (Claude / GPT-5) | Latency | FPR (Claude / GPT-5) |
  |---|---|---|---|
  | TGCC | 0.02 [0.01, 0.02] / 0.01 [0.00, 0.01] | 0.6 / 0.2 steps | 0.12 / 0.27 |
  | TGCC-Smoothed | 0.09 / 0.09 | 3.5 / 3.7 steps | |
  | TGCC-CompositeOnly | 0.17 / 0.11 | | |
  | Naive | 1.00 | never revokes | |

* **D1aZ Q3.** The epistemic check produces the first denial in every episode, so removing the
  coupling does not change E1 latency. The coupling's contribution is shown in §9.4 (N12).

### 9.3 Experiment 2 - debate [REPLACE with N10]
* Heterogeneous Claude/GPT-5 teams, N ∈ {1, 3, 5}, two 60-question series each.
* TGCC revokes the sleeper within 1–2 questions.
* Post-compromise wrong consensus:

  | Team size | Ungated | TGCC |
  |---|---|---|
  | N = 1 | 1.00 | 0.04 |
  | N = 3 | 0.40 | 0.11 |
  | N = 5 | 0.12 | 0.14 (majority voting already suffices) |

* **Report the cost.** Honest agents are denied on 27% of agent-questions, and the pool abstains
  on 14% of questions.
* Figure: `nextphase/n10_debate/figures/debate.png`.

### 9.4 Experiments 3–5 + non-epistemic compromises - [REPLACE / ADD]
* **E3.** Report N11, simulation with per-cell calibration, and N02, the real-stream heatmap: the
  controller is insensitive to p and c once calibrated. Figures:
  `nextphase/n02_real_stream_sensitivity/figures/*_heatmap.png` and
  `nextphase/n11_simulation_e3_e5/figures/e3_heatmaps.png`.
* **E4 (N09).** Blocked harmful commits:

  | Gate | Unit-test critic (Claude / GPT-5) | Reviewer-LLM critic (Claude / GPT-5) |
  |---|---|---|
  | TGCC | 98% (364/372) / 93% (362/389) | 92% / 81% |
  | TGCC-Smoothed | 86% / 66% | 61% / 46% |
  | AgentGuard-lite | | 92% / 77% |
  | Naive | 0% | 0% |

  Honest commits denied by TGCC: 9–17%. Figure: `nextphase/n09_code_pipeline/figures/blocked_commits.png`.
* **[ADD] Non-epistemic compromises (N12).** The agent stays correct while appending
  unauthorized actions, drifting off-topic, or turning hostile.

  | Gate | OER (Claude / GPT-5) |
  |---|---|
  | TGCC | 0.08–0.15 / 0.06–0.08 |
  | TGCC-NoSyn | up to 0.20 / 0.18 |
  | Strict-min | up to 0.22 / 0.32 |
  | Epistemic-only and memoryless gates | 0.57–0.83 |

  Figure: `nextphase/n12_non_epistemic_compromise/figures/non_epistemic_oer.png`.
* **E5.** From N11 and N06:
  * Sleeper latency is flat at 2.6–3.1 steps for 1–50 agents.
  * Honest blast radius is 0.14–0.15, also flat.
  * Controller cost is 59–93 µs per agent-step in pure Python. End-to-end cost is dominated by the
    LLM and critic calls (N06).
  * Replace "10.8 μs ... validating the quadratic bound" with these numbers.
  * Figure: `nextphase/n11_simulation_e3_e5/figures/e5_scalability.png`.

### 9.5 Consolidated findings and Table 1 - [REPLACE]
* **New Table 1**, all with CIs:
  * E1: TGCC / TGCC-Smoothed / TGCC-NoSyn / Epistemic-only / AgentGuard / Naive.
  * E1 non-epistemic (N12).
  * E4 with both critics.
  * E2.
  * E5.
* **[DELETE]** "The synergy operator is necessary ... fourfold reduction". **[REPLACE]** with the
  three-part finding of §1 above.

### 9.6 Extended robustness - [REPLACE]
* **Matched-FPR comparison (N03).** At FPR ≤ 0.05:
  * TGCC OER 0.04 / 0.02;
  * TGCC-Smoothed 0.10 / 0.10;
  * Epistemic-only and Strict-min 0.10 / 0.09;
  * AgentGuard-lite 0.04 / 0.02;
  * DynaTrust-lite 0.05 / 0.05.

  Figure: `nextphase/n03_matched_fpr_baselines/figures/*_oer_vs_fpr.png`.
* **Critic reliability (N04).**
  * Missed critic errors up to 40%: OER ≤ 0.04.
  * Critic false alarms at 10%: TGCC OER 0.04–0.06 vs 0.42–0.46 for TGCC-Smoothed.
  * At 20% false alarms every gate fails (OER ≥ 0.81).
  * A reference-free LLM judge (accuracy 0.92–0.94) as the critic gives OER 0.02–0.05, with FPR
    0.00–0.42 depending on the judge.

  Figure: `nextphase/n04_critic_reliability/figures/critic_noise.png`.
* **Probe validity (N05).**
  * The social probe detects missing confidence (AUROC 0.74–0.99).
  * The regex behavioural and role probes are near chance on natural failures (AUROC 0.38–0.53).
  * The models refused to produce policy violations.

  Present the heuristic probes as placeholders and recommend LLM-judge probes for deployment.
  Figure: `nextphase/n05_probe_validation/figures/probe_modes.png`.
* **End-to-end cost (N06).**
  * Controller about 0.1 ms per step (pure Python).
  * Agent call 1.45–1.91 s.
  * LLM-judge critic +1.3–2.0 s and about 0.9× the agent's tokens.
* **Keep** E7, E8, E10, E12, E13, E14 and E16 as they are, or move them to the appendix.
* **Replace** E6 with N01 and N03, E11 with N02, and E15 with N08.

## 12. Section 10 - Deployment

* **[ADD]** a checklist:
  1. Choose a critic and measure its false-alarm rate. Keep it below about 10% (N04).
  2. Run a pre-warmed honest pilot of at least 100 interactions. Calibrate with Algorithm 2 and
     choose δ for the acceptable honest FPR.
  3. Recalibrate whenever ω or γ change (N02).
  4. Replace the heuristic probes with validated ones (N05).

## 13. Section 11 - Discussion, limitations, conclusion

* **[REPLACE]** the guarantees sentence, as in the abstract.
* **[ADD] Limitations:**
  1. Critic false alarms above about 10% defeat any epistemic gate (N04).
  2. The heuristic probes are weak on natural failures (N05).
  3. Honest FPR at δ = 0.05 is 0.12–0.27, and long-horizon honest admission is 0.57–0.78. A
     single honest error can trigger a denial.
  4. In debate, gating gives no gain at N = 5, where majority voting suffices (N10).
  5. The coupling matrix is hand-specified. With the epistemic check, any lower-triangular C gives
     the same E1 result; without it, OER spans 0.09–0.27 (N02).
* **[ADD]** a short theorem-to-evidence table (eY9w W4):

  | Theorem | Evidence |
  |---|---|
  | Thm 3 | N01, N12 |
  | Thm 4 | N07(a) |
  | Thm 6 / Eq. 14 | N07(b) |
  | Thm 5 / Alg. 2 | N08 |
  | Thm 2 | N10, N11 |
  | Prop. 5 | N06 |

## 14. Ethics and artifact

* The anonymized repository must include `src/tgcc/nextphase/`, `nextphase/` and the LLM cache.
* State that generated code ran only in an AST-audited, isolated subprocess.

## 15. Appendices

* **App. B.** Add the worked example for a role-layer deficit (the N12 mechanism).
* **App. E.**
  * Replace Table 7 with the N02 real-stream table.
  * Replace Fig. 5 with the calibrated E3 heatmaps (N11) and the real-stream heatmaps (N02).
  * Insert the updated Algorithm 2.
* **App. G.** Add the proofs of the new Eq. (14) and the Theorem 4 floor.
* **App. H.**
  * Replace H.1 / Table 9 with N03.
  * H.4 / Table 12: baseline OER is now the N01 value.
  * Replace H.6 / Table 13 / Fig. 13 with N02.
  * Replace H.10 / Table 16 / Fig. 16 with N08.
  * **[ADD]** sections: critic reliability (N04), probe validation (N05), non-epistemic
    compromises (N12), end-to-end cost (N06).
* **Table 8.** Regenerate from `nextphase/SUMMARY.md`.

## 16. Presentation (RRLq W5, eY9w W1/W4, Jqqf W4)

* Merge §4.4 into §4.3, §5 into §4, and §8 into §6, for about 8 sections.
* Move Propositions 7–15 into one "Supporting results" appendix.
* One hyperparameter table in §9.1.
* One naming scheme: E1–E5 for main experiments, R1–R8 for robustness.
