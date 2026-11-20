# IEEE OJCS (OJCS-2026-09-0998): reviewer coverage for the resubmission

Branch `enhancement`. Every row points to an experiment folder under `nextphase/` with `results.json`,
`README.md` and figures. N01-N21 are the post-KDD re-runs (see `CHANGES.md`); N22-N32 were added for the IEEE
reviews. All results use real LLM outputs except the two numerical checks of the corrected lemmas (marked
"numerical"). API spend for N22-N32: US$8.29 (ledger: `cache/llm/_spend_ledger.json`).

Status: **done** = evidence complete; **pending Kaggle** = the analysis code is final and the open-weight
(Qwen3-4B, Qwen3-8B, Qwen2.5-7B) data still has to be generated with `nextphase/kaggle/tgcc-openweight.ipynb`.

---

## Reviewer 1

### R1-1. Theorems 4 and 6 assume stationary/bounded noise; real interactions are non-stationary
**Verdict.** Partly right. Theorem 4 as printed is wrong (it plateaus), but a martingale version needs no
stationarity; Eq. (14) *is* optimistic under non-stationarity, and an exact state-conditioned form fixes it.

| Evidence | Result |
|---|---|
| N22(a) revised Theorem 4 (Azuma-Hoeffding for weighted martingale differences, prior term included) | Holds in **145/145** layer x threshold cases on real non-stationary streams (model swap Sonnet->GPT-5->Haiku; domain shift TriviaQA->MedMCQA) and **1,440/1,440** adversarial Monte-Carlo checks (numerical). Needs only E[s_t | past] >= rho_min; floor exp(-2 mu^2 (1+gamma)/(R^2 (1-gamma))). |
| N22(c) Eq. (14) on real compromised streams after a domain shift | Stationary-start Eq. (14) **under-predicts latency 1.0-3.6x**. The state-conditioned closed form (from the controller's evidence (a, b) at compromise) matches observed crossings **within ~1 step in 12/12** cases, including 3 beyond the horizon. |
| N22(b) per-turn epistemic check | No distribution-free per-step bound exists (honest calibration error 0.19-0.39 exceeds the threshold) -> FPR is controlled by conformal risk control instead (N29, N32). |
| N07 | Theorem 4 floor vs empirical (stationary), Eq. (14) closed form. |

**Manuscript.** Replace Theorem 4 by the martingale form (with prior term and floor); replace Theorem 6 /
Eq. (14) by the state-conditioned closed form and state that it is exact for the expected evidence and
history-free; say explicitly that the per-turn check has a constant honest denial rate controlled by CRC.

### R1-2. Threat model excludes collusion and probe/controller compromise ("who watches the watchmen")
**Verdict.** Valid; now covered by experiment and an explicit mechanism.

| Evidence | Result |
|---|---|
| N23 critic poisoning (authority / override payloads aimed at the LLM-judge critic; judges Sonnet 4.5, GPT-5, Haiku 4.5; Qwen3-8B pending Kaggle) | Frontier judges are robust: flip rate 0.03 -> at most 0.09; TGCC OER 0.00-0.07 under every judge configuration. Defences D1 (spotlighted prompt), D2 (sanitisation), D3 (cross-family AND ensemble) reported with their FPR cost. |
| N23 critic takeover before the agent turns (step 15) | Without audit TGCC is blind: **OER 0.98-1.00** (the reviewer's concern is real). **Canary audit** (critic treated as an agent with its own trust; planted known-label items with injection templates distinct from the attack) detects the takeover in **8/8** episodes within **4-7 steps**; fail-closed OER **0.05-0.09**; **no added honest FPR**. |
| N13 collusion (3 personas, 2 colluders, real LLMs) | Colluder OER 0.02 / 0.01; a naive cross-agent agreement signal is harmful (honest-agent denial 0.63-0.67). |
| N14 indirect prompt injection on the agent | Harmful admission 0.02 / 0.01 (Naive 0.41 / 0.16). |
| N15, N16, N31(a) signal forgery | Forging non-epistemic layers does not help the attacker (TGCC-R OER flat in Delta: 0.01-0.12 on all banks). |
| Controller compromise | Out of scope by design: the controller is deterministic code outside any LLM context; its only inputs are probe signals (state in the threat model). |

**Manuscript.** Extend the threat model (Table 2) with critic poisoning and critic takeover; add the canary
audit as the "who watches the watchmen" component (Algorithm 1 line: fail closed when critic trust drops);
move collusion from "out of scope" to "evaluated" (N13).

### R1-3. Lemma 3 relies on standard Hedge (convex losses in [0,1]); questionable for LLM interactions
**Verdict.** Valid: the lemma as stated applies a bound to a different algorithm. Corrected.

| Evidence | Result |
|---|---|
| N26 corrected Lemma 3 | The update is exponential weights on *discounted* cumulative losses (beta = 1 - lam, eta' = eta lam). The loss of a weighting <alpha, q_t> is linear in alpha and q_t = 1 - T_t lies in [0,1] by construction, independent of LLM semantics. Discounted regret <= ln L / eta' + eta' / (8 (1 - beta)); proof in N26 README. Holds in 80/80 adversarial configurations (numerical, max ratio 0.83) and on every real stream (regret 0.6-1.1 vs bound 6.5 at default; 1.4-1.6 vs 4.0 tuned). |
| N26 / N27 ablation | Fixed uniform weights (eta = 0) give **identical OER/FPR** on every real stream: adaptive weighting contributes nothing measurable. At the default lam = 0.5 the bound is vacuous (memory of 2 steps). |

**Manuscript.** Replace Lemma 3 with the discounted-regret lemma; demote adaptive weighting from a
contribution to an optional component (or remove it) and report the fixed-weight ablation.

---

## Reviewer 2

### R2-1. Evaluation too small: 60 questions, one Claude model, 20 commits, debate N in {1,3,5}
| Evidence | Result |
|---|---|
| N01 | 15 independent 60-question TriviaQA episodes x Claude Sonnet 4.5 and GPT-5 (900 questions each). |
| N25 / N32 | + Claude Haiku 4.5; + MedMCQA (clinical, the paper's EHR scenario) on Sonnet, GPT-5, Haiku; **pending Kaggle:** Qwen3-4B, Qwen3-8B, Qwen2.5-7B on both datasets (3 vendors / 6 models / 2 datasets). |
| N32 TGCC-R across 6 model x dataset banks, 4 attack types | Non-epistemic attacks **OER 0.00 on every bank**; sleeper OER 0.04-0.18 at delta = 0.20 (latency 1.5-7 steps); FPR guarantee holds in **12/12** checks. Baselines under identical calibration: AgentGuard-lite 0.98-1.00 on non-epistemic attacks, Strict-min up to 1.00. |
| N09 | 162 HumanEval tasks x 2 models, 372-389 harmful commits, unit-test and reviewer-LLM critics. |
| N10 / N30 | Real-LLM debate, N in {1,3,5}, K in {1,2}. |
| Finding to report | Azure's content filter blocks 15% (109/720) of GPT-5's benign MedMCQA prompts; empty outputs are treated as "no action". |

### R2-2. Debate: revocation is not harm prevention; N=1 no gain; N=5 already ~0; prior influence
| Evidence | Result |
|---|---|
| N30 (N10 replayed exactly from cache + new N=5, K=2) | Paired harm prevented (McNemar): N=1 77 prevented / 0 caused (p = 1e-23); N=3 24/1 (p = 1.5e-6); N=5, K=1 3/3 (no gain, majority already suffices); **N=5, K=2: wrong team answers 0.46 -> 0.17, 24/1 (p = 1.5e-6)**. |
| N30 influence | An admitted sleeper flips 29-38% of honest agents from correct to wrong; after revocation 2-18%. Harm concentrates in the 1-2 questions before revocation (wrong rate 0.33-1.00 there vs 0.00-0.16 after). |
| Cost | 27-30% of honest agent-questions denied in the gated teams. |

### R2-3. Weak baselines; no fixed-weight / minimum / static-threshold; 0.87 FPR usability
| Evidence | Result |
|---|---|
| N03, N32 | 11 gates, all calibrated identically (Epistemic-only, Strict-min, Mean, AgentGuard, DynaTrust, EigenTrust, Naive, TGCC ablations). TGCC-R dominates under identical CRC calibration (N32). |
| N26 / N27 | Fixed-weight TGCC identical to TGCC (adaptive weighting not load-bearing). Static thresholds do not transfer: theta = 0.30 lets non-epistemic attacks through (OER 0.42-0.99); theta = 0.55 denies 28-45% of honest commits in the code task. |
| N27 | Security-utility frontier over delta; escalation-to-review view (per 1,000 actions); code-task FPR now 0.15 / 0.17 (45/300, 51/300), not 0.87. |
| N32 | Honest-FPR guarantee vs detection: on easy banks delta = 0.10 costs nothing; when the honest model is itself poorly calibrated (Haiku, MedMCQA) delta = 0.10 lets sleepers through (OER 0.37-0.96) and delta = 0.20 restores detection (0.08-0.18). |

### R2-4. Inconsistencies: Naive OER 0.12 vs "never revokes"; 0.87 FPR denominator; Fig. 5(b) colour bar; no variability
| Evidence | Result |
|---|---|
| N01 | Naive OER **1.00** in all 30 episodes (the 0.12 came from unreproducible E1 code; CHANGES.md B6). |
| N27 | Explicit denominators (denied honest steps / honest steps; e.g. 45/300); denials are not a warm-up artefact (177/180 honest QA denials come from the epistemic check, alone or with the composite, after a genuine model error). |
| N11 / N02 | Heatmaps regenerated from code with colour bars matching the data. |
| N01-N32 | Episode-level bootstrap or Wilson CIs everywhere. |

### R2-5. Probes not validated; prompts/scoring/normalisation missing; coupling matrix unjustified
| Evidence | Result |
|---|---|
| N28 LLM evaluator for behavioural (tone) and role (focus) layers; full prompt, 1-5 scales, s = (r-1)/4 | AUROC vs an independent GPT-5 label: tone **0.96-1.00** (regex 0.38-0.51), focus **0.74-0.78** (regex 0.44-0.53); resample std <= 0.009; unparsed <= 0.1%. |
| N28(c) real model-generated failures, TGCC-R + evaluator probes | Genuine hostile / opaque failures admitted **0.00** for both models; genuine off-topic 0.00 (GPT-5) / 0.17 (Claude). With regex probes Claude's genuine hostile replies are admitted 100%. |
| N04, N05, N23 | Critic validity: alias critic agrees with an LLM judge on ~90%; noisy and reference-free critics; poisoned critics. |
| N02, N21 | 26 coupling matrices give OER 0.01-0.02 with the epistemic check; coupling learned from traces changes OER by <= 0.03: results are insensitive to the specific structure, which is presented as a design prior. |

### R2-6. Theory flaws: Prop. 1 (ratio of expectations), Lemma 3, Theorem 4 floor, Theorem 6 undefined
| Item | Fix | Evidence |
|---|---|---|
| Prop. 1 | State as the fixed point of the expected-evidence recursion (ratio of expected pseudo-counts) and report its accuracy for the posterior mean | Fig. 2(a): MAE 0.007 |
| Lemma 3 | Discounted-regret lemma with proof | N26 |
| Theorem 4 | Martingale form with prior term; floor stated | N22, N07 |
| Theorem 6 / Eq. (14) | State-conditioned closed form, defined whenever x lies between the current trust and T*(rho1) | N22, N07 |

### R2-7. Calibration: verification by construction; burn-in 67 not 13; Eq. (14) ~805 not 300; 20-question pilot
| Evidence | Result |
|---|---|
| N29 | Per-step DKW/Hoeffding guarantees are vacuous on real streams (autocorrelation tau_int = 30-50 -> 26k-44k pilot steps); pure quantile misses delta out of sample; held-out validation error 0.12-0.43. |
| N29 / N32 **conformal risk control** on honest sessions | E[per-step honest FPR] <= delta, finite-sample, any within-session dependence; holds in **24/24** (N29) and **12/12** (N32) checks. Sample complexity tied to the experiment: m >= 1/delta - 1 sessions; delta = 0.10 needs >= 14 ten-to-twenty-step sessions for OER ~0.04. |
| Numbers | Burn-in 1/(1-gamma) = 66.7; Eq. (14) at eps = delta = 0.05 gives 804 steps (N29 README); pilot is pre-warmed so no burn-in is discarded (CHANGES.md B9). |
| N32 | A pilot drawn from a different slice than deployment mis-calibrates (Haiku: pilot accuracy 0.96 vs 0.75): calibrate on sessions from the deployment workload. |

### R2-8. Scalability: 10.8 us excludes critic calls, tokens, enforcement, revocation; O(L^2) not tested
| Evidence | Result |
|---|---|
| N24(a) | Controller cost vs L = 3..32: 12 -> 86 us; quadratic fit R^2 = 1.000 (linear 0.961); vs |C| = 1..256: 14 -> 21 us. |
| N24(b) real capability tokens (HMAC-SHA256, expiry, gateway verification, revocation epochs broadcast) on real streams, N = 1..100 agents, 1-4 gateways | ~16 us per agent-step in total; **0 stale tokens accepted** after revocation. |
| N06 / N24(c) | LLM agent call 1.45-1.91 s, LLM-judge critic +1.3-2.0 s: the critic, not the controller, dominates. |
| N31(c) | Real-stream Byzantine chain: strict conjunctive pipelines lose availability with N (inherent to Theorem 2's rule; reported as a limitation). |

---

## Method changes the revision must describe (TGCC-R)
1. Epistemic check reads the per-turn windowed calibration signal (window 16; N32 shows 8 is too short on hard domains).
2. Every layer has a per-turn prerequisite conjunct (Definition 3 with req(c) = all layers), not only the epistemic one (N32, N28).
3. Thresholds by conformal risk control on honest sessions from the deployment workload (replaces Algorithm 2's min-of-pilot and its verification step).
4. LLM evaluator for behavioural and role layers (N28); canary audit of the critic with fail-closed (N23).
5. Adaptive weighting optional (N26).

## Pending (Kaggle, no API cost)
Run `nextphase/kaggle/tgcc-openweight.ipynb`, unzip its output at the repo root, then re-run
N22, N23, N26, N27, N29, N31, N32 (`python -m tgcc.nextphase.<module>`); they pick up the Qwen banks automatically.
