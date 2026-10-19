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

## Master change map (every element of the submitted PDF)

Read this table top to bottom while editing the PDF. "§x" in the last column points to the detailed
instructions further down in this file. Figure paths are relative to `nextphase/`.

### A. Main text

| PDF element | Action | Evidence / new figure | Details |
|---|---|---|---|
| Title, keywords | KEEP | - | §2 |
| Abstract | REPLACE (about 170 words, new numbers, no "decays exponentially" / "logarithmic") | N01, N09, N12 | §2 |
| §1 Introduction: contributions, "Our approach" | REPLACE bullets 4 and 6, ADD "when each component matters" bullet | N01, N09, N12, N15 | §3 |
| §2 Related work: "TGCC differs on three axes" | REPLACE (ii) and (iii); ADD established-components sentence | N03, N09, N12 | §4 |
| §3.3 Threat model, Assumption 1(iii) | REPLACE (independent critic; critic error evaluated) | N04, N05, N16 | §5 |
| §3.4 after Definition 1 | ADD min-aggregator remark (14qA Q2) | N03, N12 | §5 |
| §4.1–4.4 (Prop. 1–3, Thm 1–2, Lemmas 1–2) | KEEP; ADD remark after Prop. 3 | N12, N15 | §6 |
| §4.5 Layer signals | REPLACE (per-turn epistemic signal) | - | §6 |
| §5 Adaptive weighting | ADD η, λ insensitivity remark | N02 | §7 |
| §6.1 Definition 3, Eq. (11), Algorithm 1 line 6 | REPLACE (per-turn epistemic conjunct) | N01 | §8 |
| §6.2 Theorem 3 proof | ADD one line | - | §8 |
| §6.3 Theorem 4, Eq. (12), opening, Key-insight box | REPLACE (geometric convergence to a floor) | N07(a): `n07_theory_checks/figures/theory_checks.png` | §8 |
| §7 Algorithm 2 (pointer), Prop. 6 / Thm 5, Remark 3 | REPLACE (quantile rule, DKW, N_pilot ≥ 100) | N08: `n08_calibration/figures/sim_calibration.png` | §9 |
| §8 Theorem 6 / Eq. (14) | REPLACE (exact closed form) | N07(b), N07(c): `n07_theory_checks/figures/gate_latency_sweep.png` | §10 |
| §8 Remark 4 (E16 numbers 0.17 → 0.22, ρ ≈ 0.30) | REPLACE numbers with N17 | N17 | §10 |
| §9 intro ("five experiments") | REPLACE: E1–E5 plus robustness study, two task families | - | §11 |
| §9.1 Protocol, baselines, metrics ("three conditions") | REPLACE | all | §11 9.1 |
| §9.2 E1 text + Figure 1 | REPLACE | N01: `n01_e1_multi_episode/figures/claude-sonnet-4.5_trajectory_ep0.png`, `e1_bars.png` | §11 9.2 |
| §9.3 E2 text (+ Figure 3 in App. E) | REPLACE | N10: `n10_debate/figures/debate.png` | §11 9.3 |
| §9.4 E3 / E4 / E5 text | REPLACE | N11, N02, N09, N06 | §11 9.4 |
| §9.4 non-epistemic compromises | ADD (new paragraph + figure) | N12: `n12_non_epistemic_compromise/figures/non_epistemic_oer.png` | §11 9.4 |
| §9.5 Consolidated findings + Table 1 | REPLACE | N01, N09, N10, N11, N12 | §11 9.5 |
| §9.6 Extended robustness paragraph | REPLACE | N03–N06, N13–N21 | §11 9.6 |
| §10 Deployment | ADD checklist | N02, N04, N05 | §12 |
| §11 Discussion: guarantees sentence | REPLACE | N07 | §13 |
| §11 "Open directions: learning the coupling matrix ... colluding adversaries are out of scope" | REPLACE: both are now evaluated (N21, N13); keep multi-hop chains and game-theoretic analysis as open | N13, N21 | §13 |
| §11 Limitations, theorem-to-evidence table | ADD | N04, N05, N10, N17, N19 | §13 |
| Ethics statement ("E1–E16 harnesses, per-turn logs") | REPLACE with "experiment drivers N01–N21, response banks and LLM cache" | - | §14 |

### B. Appendices, tables and figures

| PDF element | Action | Evidence / new figure | Details |
|---|---|---|---|
| App. A, Table 2 (adversary taxonomy): colluding adversaries "out of scope" | REPLACE row: evaluated, per-agent gating suffices, agreement signals backfire | N13 | §15 |
| App. A, Table 3 (positioning) | KEEP; optionally add the AgentGuard/Strict-min comparison column | N03 | - |
| App. B worked example | ADD role-layer deficit example | N12 | §15 |
| App. C, Table 4 | KEEP | - | - |
| App. D, Table 5 (probe specification) | REPLACE epistemic row (per-turn rolling-window score used by the grant rule); ADD note that heuristic probes are placeholders | N05 | §15 |
| Table 6 (notation) | ADD s₁(t), δ (pilot quantile), θ_{c,1} as a threshold on s₁ | - | §15 |
| App. E intro ("parameter design guide used to select ... p = −6, c ≈ 0.35") | REPLACE: operating point is not critical once calibrated | N02 | §15 |
| Algorithm 2 (full) | REPLACE (lines 2–5) | N08 | §9 |
| Table 7 (parameter design guide) | REPLACE with real-stream sensitivity table | N02: `n02_real_stream_sensitivity/figures/*_oat.png` | §15 |
| App. F clinical example ("sets the write threshold a small margin below that minimum") | REPLACE with the quantile rule; mention the per-turn epistemic check | - | §15 |
| Figure 2 (simulated single-sleeper dynamics, old grant rule) | DELETE (the real-LLM trajectory of new Fig. 1 shows the same mechanism) or KEEP as an illustration with a caption that it shows the composite only | N01 | §15 |
| Figure 3 (E2 debate) | REPLACE | `n10_debate/figures/debate.png` | §11 9.3 |
| Figure 4 (fixed point, Hedge weights) | KEEP (Prop. 1 and Prop. 4 are unchanged) | see open item 2 below | - |
| Figure 5 (E3 heatmaps) | REPLACE | `n11_simulation_e3_e5/figures/e3_heatmaps.png` + `n02_real_stream_sensitivity/figures/*_heatmap.png` | §11 9.4 |
| App. G deferred proofs | ADD proofs of Eq. (14) and the Theorem 4 floor | N07 | §15 |
| Figure 6 (E4 code pipeline) | REPLACE | `n09_code_pipeline/figures/blocked_commits.png` | §11 9.4 |
| Figure 7 (E5 scalability) | REPLACE | `n11_simulation_e3_e5/figures/e5_scalability.png` | §11 9.4 |
| Table 8 (extended headline numbers) | REPLACE, one row per H subsection below | SUMMARY.md N13–N21 | §15 |
| App. H intro ("eleven additional experiments", "observed minimum minus ε") | REPLACE: list the new set; calibration = quantile rule; pre-warm with no burn-in | - | §15 |
| H.1 E6 bootstrap, Table 9, Figure 8 | REPLACE with across-episode CIs and matched-FPR baselines (Wilcoxon tests dropped) | N01, N03: `n03_matched_fpr_baselines/figures/*_oer_vs_fpr.png` | §11 9.6 |
| H.2 E7 collusion, Table 10, Figure 9 | REPLACE | N13: `n13_collusion/figures/collusion_team.png` | §11 9.6 |
| H.3 E8 prompt injection, Table 11, Figure 10 | REPLACE | N14: `n14_prompt_injection/figures/prompt_injection.png` | §11 9.6 |
| H.4 E9 layer ablation, Table 12, Figure 11 | REPLACE | N15: `n15_layer_ablation/figures/*_layer_ablation.png` | §11 9.6 |
| H.5 E10 long horizon, Figure 12 | REPLACE | N18: `n18_long_horizon_recovery/figures/long_horizon.png` | §11 9.6 |
| H.6 E11 sensitivity, Table 13, Figure 13 | REPLACE (real streams) | N02: `n02_real_stream_sensitivity/figures/*_oat.png` | §15 |
| H.7 E12 recovery, Figure 14 | REPLACE (table instead of a single-seed trace) | N18 | §11 9.6 |
| H.8 E13 Byzantine chain, Table 14, Figure 15 | REPLACE | N19: `n19_byzantine_chain/figures/byzantine_chain.png` | §11 9.6 |
| H.9 E14 audit trail, Table 15 | REPLACE schema (conjunct-level fields) | N20 (schema in `n20_audit_trail/README.md`) | §11 9.6 |
| H.10 E15 calibration robustness, Table 16, Figure 16 | REPLACE | N08: `n08_calibration/figures/sim_calibration.png`, `real_calibration.png` | §15 |
| H.11 E16 adaptive attacker, Table 17, Figure 17 | REPLACE | N17: `n17_adaptive_attacker/figures/*_adaptive_attacker.png` | §11 9.6 |
| H.12 Summary ("E7 proves the negative result ...") | REPLACE (new findings list; E7 negative result now concerns agreement signals only) | SUMMARY.md conclusions | §15 |
| NEW H.13 Critic reliability | ADD | N04: `n04_critic_reliability/figures/critic_noise.png` | §11 9.6 |
| NEW H.14 Probe and critic validity | ADD | N05: `n05_probe_validation/figures/probe_modes.png` | §11 9.6 |
| NEW H.15 Non-epistemic compromises (full table) | ADD | N12 | §11 9.4 |
| NEW H.16 End-to-end cost | ADD | N06 | §11 9.6 |
| NEW H.17 Bounded forgery (Assumption 1(iii) relaxed) | ADD (not in submitted PDF) | N16: `n16_bounded_forgery/figures/forgery_sweep.png` | §11 9.6 |
| NEW H.18 Learned coupling | ADD (not in submitted PDF) | N21: `n21_learned_coupling/figures/coupling_recovery.png` | §11 9.6 |
| NEW H.19 Gate latency vs γ, δ | ADD (or put into App. G next to the Eq. (14) proof) | N07(c) | §10 |

### C. Experiment ID mapping (submitted → revision)

| Submitted | Revision | | Submitted | Revision |
|---|---|---|---|---|
| E1 | N01 | | E9 | N15 |
| E2 | N10 | | E10 | N18 |
| E3 | N11 + N02 | | E11 | N02 |
| E4 | N09 | | E12 | N18 |
| E5 | N11 + N06 | | E13 | N19 |
| E6 | N01 + N03 | | E14 | N20 |
| E7 | N13 | | E15 | N08 |
| E8 | N14 | | E16 | N17 |

New in the revision: N04, N05, N06, N07, N12, N16, N21. The paper can keep the E-numbers;
the N-IDs only name folders in the artifact.

### D. Reviewer coverage checklist

| Reviewer point | Status | Where in the revised paper | Evidence |
|---|---|---|---|
| 14qA W1 / Q1: Naive OER 0.12 lower than TGCC | Done | Table 1, §9.2 | N01: Naive 1.00, TGCC 0.02 / 0.01 |
| 14qA W2: experiments too small | Done for E1, E4, E7, E8; partial for E2 (see open item 1) | §9.1–9.4, App. H | N01 (900 Q × 2 models), N09 (162 tasks, 372–389 harmful commits), N10, N13, N14 |
| 14qA W2: E3/E5 are simulations | Done | §9.4, App. E | N02 (real-stream sensitivity/heatmap), N06 (real cost) |
| 14qA W3 / Q3: parameters chosen on synthetic data | Done | §9.1 parameter table, Table 7, H.6 | N02 |
| 14qA Q2: Definition 1 vs min-aggregation | Done | §3.4 remark | N03, N12 |
| D1aZ W1: one episode; bootstrap of one stream | Done | §9.1, H.1 | N01 (15 independent episodes / model), N09, N13 |
| D1aZ W2: E9 says only the epistemic layer matters | Done | §1 story, §9.4, H.4 | N12, N15 |
| D1aZ W3: oracle critic; noisy critic | Done | §3.3, H.13, H.14, §11 limitations | N04 (noise, reference-free LLM judge), N05, N09 (reviewer-LLM critic) |
| D1aZ W3: "if the critic exists, gate on it directly" | Done (text) | §11 discussion: TGCC adds memory (N18), multi-layer coverage (N12, N15), robustness to a weak critic (N09) and to critic false alarms (N04) over a raw critic gate | N04, N09, N12, N15, N18 |
| D1aZ W4: Theorem 4 floor | Done | §6.3, abstract, contributions, Key insight, conclusion | N07(a) |
| D1aZ W5: Eq. (14) ill-posed | Done | §8, App. G | N07(b), N07(c) |
| D1aZ W6: code and data | Done | Ethics statement | repository |
| D1aZ Q1: Naive OER | Done | Table 1 | N01 |
| D1aZ Q2: 0.17 vs 0.11 vs 0.25 | Done | Table 1 and App. H use N01 only; explanation in the response letter | CHANGES.md §1c |
| D1aZ Q3: coupling latency 7 vs 29 | Done | §9.2 (per-conjunct denial breakdown) | N01, N12 |
| RRLq W1: signal reliability | Done | H.13, H.14, App. D | N04, N05 |
| RRLq W2: end-to-end cost | Done | §9.4 E5 text, H.16 | N06 |
| RRLq W3: limited novelty | Done (text) | §2 | N03, N09, N12 |
| RRLq W4: predefined structure | Done | §11 limitations, H.6, H.18 | N02 (26 matrices, permuted order), N21 |
| RRLq W5 / eY9w W1 / Jqqf W4: organization, long abstract | Done (text) | §16 of this file | - |
| eY9w W2: no real baselines | Done | §9.1, H.1 | N03 (7 baselines, identical calibration), N09, N12, N14 |
| eY9w W3: sensitivity of γ, ω, p, η | Done | H.6, Table 7 | N02 |
| eY9w W4: no clear conclusion | Done | §9.5 findings, §11 theorem-to-evidence table | SUMMARY.md conclusions |
| Jqqf W1: Theorem 4, Eq. (14) | Done | §6.3, §8, App. G | N07 |
| Jqqf W2: calibration direction | Done | §7, Algorithm 2 | N08 |
| Jqqf W2: epistemic-only / verifier gating at matched admission | Done | H.1 | N03 (Epistemic-only, AgentGuard-lite at FPR ≤ 0.05 / 0.10) |
| Jqqf W3: Naive OER mismatch; AgentGuard vs "superior to all" | Done | Table 1, §9.6: state that TGCC ties AgentGuard-lite on E1 and wins on N12 / N09 | N01, N03, N09, N12 |
| Jqqf W4: main text vs appendix inconsistencies | Done | All numbers come from `nextphase/` only; regenerate Table 8 | SUMMARY.md |

### E. Open items (not covered by the current experiments)

1. **E2 debate scale.** N10 has two 60-question series per team size (Wilson CIs). This is real-LLM
   but still modest for 14qA W2; more series need new API calls.
2. **Figure 4 has no generator in the repository.** Propositions 1 and 4 are unchanged, so the
   figure stays valid, but a reproducibility-minded reviewer may ask for its script.
3. **Proof text.** N07 checks the Theorem 4 floor and the Eq. (14) closed form numerically; the
   App. G proofs themselves must be written in the manuscript.
4. **Review-period rule.** KDD does not allow PDF changes during review. This plan is for the
   revised version; any rebuttal stays within 2,500 characters per response.

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
   * Per-layer ablation on real streams (N15): each compromise is carried by the layer it
     violates. Spoofing that layer raises OER to 0.57–1.00.
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
  * **[ADD]** Gate-level sweep (N07c, simulation):
    * TGCC latency is 1.7–4.5 steps for every γ ∈ [0.9, 0.999].
    * The composite alone takes 12–158 steps, growing with γ and δ.

    Figure: `nextphase/n07_theory_checks/figures/gate_latency_sweep.png`.
* **[REPLACE] Remark 4.** Delete "perfect calibration raises OER only from 0.17 to ≈ 0.22 while
  attacker confidence collapses to ρ ≈ 0.30". Replace with the N17 evidence: lowering confidence on
  wrong answers evades the epistemic check, but the attacker's utility (granted wrong answers at
  confidence ≥ 0.5) drops to 0. A stealth sleeper gets 0.00–0.02. Low-rate attacks are the
  residual gap.

## 11. Section 9 - Experimental evaluation (major rewrite)

* **[REPLACE] Section intro** ("We evaluate the framework with five experiments ..."): the
  evaluation has E1–E5 on two task families (TriviaQA, HumanEval) plus multi-agent debate, and a
  robustness study (§9.6, App. H). Every controller is calibrated by the same Algorithm 2.
* **[REPLACE] §9.1** "We compare three conditions throughout: TGCC, TGCC-NoSyn, Naive" with the
  controller list below.

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
  | N = 5 | 0.12 | 0.12 (majority voting already suffices) |

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
  * Controller cost is about 57–93 µs per agent-step in pure Python. End-to-end cost is dominated by the
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
* **Replace** E6 with N01 and N03, E11 with N02, and E15 with N08.
* **[REPLACE] E7-E16 with the re-run experiments.** These can stay in the main text in short form or
  move to App. H; all use the same TGCC and Algorithm 2.
  * **E7 collusion (N13).** Three personas of each model; two collude on the same wrong answer.
    * Majority vote without a gate: the team answer is wrong on 100% of post-compromise questions.
    * TGCC: colluder OER 0.02 / 0.01, team answer wrong on 7%.
    * A cross-agent agreement signal backfires: the honest agent is denied on 63-67% of steps.

    Figure: `nextphase/n13_collusion/figures/collusion_team.png`.
  * **E8 prompt injection (N14).** 900 questions per model. The injection is followed on 21% /
    30%, and GPT-5's provider filter blocks 22%.
    * Harmful admission rate: TGCC 0.02 / 0.01, AgentGuard-lite 0.02 / 0.01,
      TGCC-Smoothed 0.06 / 0.04, Naive 0.41 / 0.16.

    Figure: `nextphase/n14_prompt_injection/figures/prompt_injection.png`.
  * **E9 layer ablation (N15)**, on real streams. **[REPLACE]** "only the epistemic signal is
    load-bearing". Each compromise is carried by the layer it violates; spoofing that layer raises
    OER to 0.57-1.00:
    * epistemic -> sleeper;
    * institutional -> policy;
    * role -> off-topic;
    * behavioural -> hostile.

    Figure: `nextphase/n15_layer_ablation/figures/*_layer_ablation.png`.
  * **E10 long horizon (N18).** TGCC admission tracks real reliability: 0.98 when stable, 0.58
    during the model swap, 0.24 at rho_e = 0.60. TGCC-Smoothed locks the agent out. Figure:
    `nextphase/n18_long_horizon_recovery/figures/long_horizon.png`.
  * **E12 recovery (N18).** TGCC revokes in 2.6 steps and re-admits after 43 steps (stable after
    49), below the 66.7-step time constant.
  * **E13 Byzantine chain (N19).** 20% sleepers, N = 1-50:
    * sleeper OER 0.02 at every N;
    * the last sleeper is revoked within 3-6 steps;
    * blast radius 0.00-0.03;
    * a strict weakest-link chain falls to 25% availability at N = 50.

    Figure: `nextphase/n19_byzantine_chain/figures/byzantine_chain.png`.
  * **E14 audit trail (N20).** Each step emits a schema-validated report naming the denying
    conjunct with value, threshold and margin. Of the denials, 19-21% come from the epistemic
    check alone and the rest from both conjuncts.
  * **E16 adaptive attacker (N17)**, on real streams with attack rate x confidence:
    * a stealth sleeper gets utility 0.00-0.02 (Naive 1.00);
    * lowering confidence on wrong answers evades the check but drives utility to 0 (Remark 4);
    * low-rate (10%) attacks keep utility 0.01-0.05 (Naive 0.17-0.21). State this as a limitation.

    Figure: `nextphase/n17_adaptive_attacker/figures/*_adaptive_attacker.png`.
  * **App. H.17 [ADD], bounded forgery (N16).** Not in the submitted PDF. Forging the
    uncontrolled layers by Delta in [0, 1] leaves TGCC at OER 0.02. TGCC-CompositeOnly plateaus at
    0.35, and Mean and Naive fail from Delta = 0.05.
  * **App. H.18 [ADD], learned coupling (N21).** Not in the submitted PDF. C can be fitted from
    traces (||C_hat - C*||_F = 0.57). Using C_hat changes real-stream OER by at most 0.03.

## 12. Section 10 - Deployment

* **[ADD]** a checklist:
  1. Choose a critic and measure its false-alarm rate. Keep it below about 10% (N04).
  2. Run a pre-warmed honest pilot of at least 100 interactions. Calibrate with Algorithm 2 and
     choose δ for the acceptable honest FPR.
  3. Recalibrate whenever ω or γ change (N02).
  4. Replace the heuristic probes with validated ones (N05).

## 13. Section 11 - Discussion, limitations, conclusion

* **[REPLACE]** the guarantees sentence, as in the abstract.
* **[REPLACE]** "Open directions include learning the coupling matrix from traces, multi-hop trust
  chains, and a game-theoretic attacker–defender analysis; colluding adversaries and controller
  compromise are out of scope". Learned coupling (N21) and colluding agents (N13) are now
  evaluated. Keep multi-hop chains, game-theoretic analysis and controller compromise as open.
* **[ADD] Why not gate on the critic directly** (D1aZ W3). A raw critic gate is the
  AgentGuard-lite baseline. It ties TGCC on E1 (N03), but:
  * it fails on compromises the critic cannot see (OER 0.75–0.83 vs 0.06–0.15, N12);
  * it has no memory, so it re-admits after any lucky answer (N18 shows TGCC tracks drift and
    recovery);
  * TGCC matches or exceeds it with a weak reviewer-LLM critic (N09).

  TGCC's value is the combination, not the epistemic check alone.
* **[ADD] Limitations:**
  1. Critic false alarms above about 10% defeat any epistemic gate (N04).
  2. The heuristic probes are weak on natural failures (N05).
  3. Honest FPR at δ = 0.05 is 0.12–0.27, and long-horizon honest admission is 0.57–0.78. A
     single honest error can trigger a denial.
  4. In debate, gating gives no gain at N = 5, where majority voting suffices (N10).
  5. The coupling matrix is hand-specified. With the epistemic check, any lower-triangular C gives
     the same E1 result; without it, OER spans 0.09–0.27 (N02). C can also be fitted from traces
     with no loss of protection (N21).
  6. Low-rate attacks hidden in the model's natural error rate are only partly caught (N17).
  7. A strict weakest-link pipeline loses availability as the team grows (25% at N = 50, N19).
     Large teams should route around denied agents instead of halting.
* **[ADD]** a short theorem-to-evidence table (eY9w W4):

  | Theorem | Evidence |
  |---|---|
  | Thm 3 | N01, N12, N15 |
  | Thm 4 | N07(a) |
  | Thm 6 / Eq. 14 | N07(b), N07(c) |
  | Thm 5 / Alg. 2 | N08 |
  | Thm 2 | N10, N11, N19 |
  | Prop. 3 (cascade containment) | N16 |
  | Prop. 5 | N06 |

## 14. Ethics and artifact

* The anonymized repository must include `src/tgcc/nextphase/`, `nextphase/` and the LLM cache.
* **[REPLACE]** "(source, E1–E16 harnesses, per-turn logs)" with "(source, drivers for every
  experiment, LLM response banks and the cached LLM calls, so every result reruns offline)".
* State that generated code ran only in an AST-audited, isolated subprocess.

## 15. Appendices

* **App. A, Table 2.** Colluding adversaries: change "out of scope" to "evaluated (App. H.2):
  per-agent gating revokes colluders; cross-agent agreement signals backfire".
* **App. B.** Add the worked example for a role-layer deficit (the N12 mechanism).
* **App. D, Table 5.** Epistemic row: the grant rule reads the per-turn rolling-window score s₁(t).
  Add a note that the behavioural, role and institutional probes are heuristic placeholders (N05).
* **Table 6 (notation).** Add s₁(t), the pilot quantile δ, and θ_{c,1} as the threshold on s₁(t).
* **App. E intro.** Replace "the parameter design guide used to select the operating point" with
  "the operating point is not critical once thresholds are calibrated (N02)".
* **App. F (clinical example).** Replace "sets the write threshold a small margin below that
  minimum" with the quantile rule, and add that the per-turn epistemic check denies the write as
  soon as the verifier disagrees.
* **Figure 2.** Delete, or keep as an illustration with a caption saying it shows the composite
  path only (the new Fig. 1 shows the full rule on real data).
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
  * Replace the E7–E10, E12–E14 and E16 appendix sections with N13–N20 (§9.6).
  * **[ADD]** bounded forgery (N16) and learned coupling (N21) as new sections; neither is in the
    submitted PDF.
  * **H intro.** Replace "eleven additional experiments (E6–E16)" with the new list, and "set to
    the observed minimum minus ε" with the quantile rule (pre-warmed pilot, no burn-in).
  * **H.12 Summary.** Replace with the robustness conclusions of `nextphase/SUMMARY.md`. The E7
    negative result now concerns agreement signals only: per-agent gating does revoke colluders.
* **Table 8.** Regenerate from `nextphase/SUMMARY.md`, one row per H subsection:

  | Exp. | Headline (Claude / GPT-5) |
  |---|---|
  | E6 → across-episode CIs, matched FPR | TGCC OER 0.02 [0.01, 0.02] / 0.01 [0.00, 0.01]; at FPR ≤ 0.05: 0.04 / 0.02 |
  | E7 collusion | colluder OER 0.02 / 0.01; team answer wrong 0.07 vs 1.00 for majority vote; agreement signal denies the honest agent 63–67% |
  | E8 prompt injection | harmful admission 0.02 / 0.01 vs Naive 0.41 / 0.16 |
  | E9 layer ablation | each compromise is carried by the layer it violates (spoofed OER 0.57–1.00) |
  | E10 drift | admission 0.98 → 0.24 as reliability drifts 0.92 → 0.60 |
  | E11 sensitivity | OER 0.01–0.02 for every p, c, γ, ω, η, λ when recalibrated |
  | E12 recovery | revocation 2.6 steps; re-admission 43 steps (stable 49) |
  | E13 Byzantine chain | sleeper OER 0.02 for N = 1–50; blast radius 0.00–0.03 |
  | E14 audit trail | 1,800 schema-valid reports, identical to the gate's decisions |
  | E15 calibration | quantile rule converges (latency 2.4 → 2.7 steps); min-of-pilot loosens (2.9 → 5.1) |
  | E16 adaptive attacker | stealth utility 0.00–0.02 (Naive 1.00); self-flagging utility 0; low-rate 0.01–0.05 |
  | Critic reliability | OER ≤ 0.06 up to 10% false alarms; fails at 20% |
  | Bounded forgery | TGCC OER 0.02 for every Δ |
  | Learned coupling | OER change ≤ 0.03 with fitted C |

## 16. Presentation (RRLq W5, eY9w W1/W4, Jqqf W4)

* Merge §4.4 into §4.3, §5 into §4, and §8 into §6, for about 8 sections.
* Move Propositions 7–15 into one "Supporting results" appendix.
* One hyperparameter table in §9.1.
* One naming scheme: E1–E5 for main experiments, R1–R8 for robustness.
