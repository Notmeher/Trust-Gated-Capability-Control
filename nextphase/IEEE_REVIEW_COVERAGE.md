# IEEE OJCS (OJCS-2026-09-0998): reviewer coverage for the resubmission

Branch `enhancement`. Every row points to an experiment folder under `nextphase/` (`results.json`, `README.md`,
figures). N01-N21 are the post-KDD re-runs (`CHANGES.md` §1-4); N22-N33 were added for the IEEE reviews (§5).
All results use real LLM outputs, except the numerical checks of the corrected lemmas (marked "numerical").
API spend for N22-N33: about US$11.8 (ledger: `cache/llm/_spend_ledger.json`, cumulative).

**Pending Kaggle (no API cost):** Qwen3-4B, Qwen3-8B, Qwen2.5-7B banks (R2-1) and the Qwen3-8B judge and evaluator
(R1-2). Run `nextphase/kaggle/tgcc-openweight.ipynb`, unzip its output at the repo root, then re-run N22, N23,
N26, N27, N29, N31, N32, N33.

---

## The revised method: TGCC-R (`src/tgcc/nextphase/tgcc_r.py`)
Every headline experiment reports TGCC-R; the original TGCC is kept as a reference row.

1. **Epistemic window chosen from the honest pilot alone:** the smallest W in {4, 8, 12, 16, 24} whose pilot 2.5%
   tail of the epistemic signal is >= 0.2. Reliable critics / easy domains get short windows (W = 4 on TriviaQA
   and with unit tests), noisy domains longer ones (W = 12-16 on MedMCQA).
2. **A per-turn conjunct on every layer** (Definition 3 with req(c) = all layers) plus the composite.
3. **Conformal risk control (CRC)** over a two-stage nested threshold family: E[per-step honest FPR] <= delta for
   sessions exchangeable with the calibration sessions, finite-sample, any within-session dependence.
4. **Empty outputs are not observations** (e.g. provider content-filter refusals: the step repeats its previous signals).
5. **LLM evaluator** (Claude Haiku 4.5) for the behavioural and role layers (N28).
6. **Canary audits** of the critic (N23) and the evaluator (N33), failing closed when the auditor's trust drops.
7. Adaptive (Hedge) weighting is optional: fixed weights give identical results (N26).

---

## Reviewer 1

### R1-1. Theorems 4 and 6 assume stationary/bounded noise
| Evidence | Result |
|---|---|
| N22(a) revised Theorem 4 (Azuma-Hoeffding for weighted martingale differences, prior term included) | Holds in **145/145** cases on real non-stationary streams (model swap Sonnet->GPT-5->Haiku; domain shift TriviaQA->MedMCQA) and **1,440/1,440** adversarial Monte-Carlo checks (numerical). Needs only E[s_t \| past] >= rho_min; plateau stated. |
| N22(c) Eq. (14) after a real domain shift | The stationary-start Eq. (14) **under-predicts latency 1.0-3.6x** (the reviewer is right). A state-conditioned closed form from the controller's evidence at compromise matches observed crossings **within ~1 step in 12/12** cases. |
| N22(b), N29, N32 | No distribution-free per-step bound exists for the windowed check on real streams; its FPR is controlled by CRC instead (holds in every check). |

**Manuscript:** martingale Theorem 4; state-conditioned Theorem 6; per-turn check controlled by CRC.

### R1-2. Threat model: collusion, poisoned probes ("critic **or evaluator**"), controller
| Evidence | Result |
|---|---|
| N23 critic poisoning (authority / override payloads; judges Sonnet 4.5, GPT-5, Haiku 4.5; Qwen3-8B pending) | Frontier judges resist (flip rate 0.03 -> at most 0.09). **TGCC-R OER 0.01-0.11** across all judge configurations and payloads (honest FPR 0.00-0.44, highest for the Haiku-hardened critics; TGCC up to 0.46). |
| N23 critic takeover before the agent turns | Without audit: OER **0.99-1.00**. **Canary audit** detects the takeover in **8/8** episodes within **4-7 steps**; fail-closed OER **0.06-0.09**; no added honest FPR. |
| N33 evaluator poisoning (fake ratings / override payloads on real hostile and off-topic replies; evaluators Haiku 4.5, GPT-5; Qwen3-8B pending) | Payloads do not inflate scores (equal or lower); the hardened prompt turns a payload into a red flag (tone 0.02-0.09). **TGCC-R admits 0.00-0.04 of genuine failures** under every payload and defence, honest FPR 0.02. |
| N33 evaluator takeover before the agent fails | Without audit: genuine failures admitted **1.00 / 0.88** (Claude replies). Canary audit (canary rate 0.5): detected **96/96**, median **6 steps**, admitted **0.04-0.06**. The audit also qualifies evaluators: GPT-5 passes only 68% of canaries (it misses 74-87% of genuine off-topic replies) and should not be the focus evaluator. |
| N13 collusion (3 personas, 2 colluders, real LLMs) | TGCC-R colluder OER **0.02-0.03**, honest agent wrongly denied 0.03 / 0.07; a naive agreement signal is harmful (0.63-0.67). |
| N14 indirect prompt injection on the agent | TGCC-R harmful admission **0.04 / 0.04** at honest FPR 0.05 / 0.11 (Naive 0.41 / 0.16). |
| N16, N31(a) signal forgery | TGCC-R OER flat in the forgery budget Delta. |
| N37 controller compromise (real E1 sleeper episodes, all 6 banks; controller compromised from step 20) | The controller is deterministic, so independent verifier replicas replay it from an append-only log authenticated with the probes' keys; the tool gateway needs a quorum of signatures on each grant. Controller-only: forged grants / tampered thresholds execute **all** harmful actions. With one honest verifier (2-of-2, 2-of-3) harmful actions executed equal the **uncompromised** controller's (e.g. 12/600 Sonnet TriviaQA); replay disagreements **0**; honest actions unchanged; a verifier refuses at the first step the honest controller would deny (median 0-20 steps). Log rewriting fails the probe MACs (detected **in every episode**, fail-closed). Controller + 1 colluding verifier defeats 2-of-3, not 3-of-3. Overhead ~16 us per step. |

### R1-3. Lemma 3 relies on standard Hedge
| Evidence | Result |
|---|---|
| N26 corrected Lemma 3 | Exponential weights on discounted cumulative losses; loss <alpha, q_t> linear, q_t in [0,1] by construction. Discounted regret <= ln L / eta' + eta' / (8 (1 - beta)); proof in N26. Holds in 80/80 adversarial configurations (numerical) and on every real stream. |
| N26 / N27 ablation | Fixed uniform weights give **identical** OER/FPR for TGCC and TGCC-R on every stream: adaptive weighting is optional. |

---

## Reviewer 2

### R2-1. Scale and generality
| Evidence | Result |
|---|---|
| Models / datasets | Claude Sonnet 4.5, GPT-5, Claude Haiku 4.5 (API); Qwen3-4B, Qwen3-8B, Qwen2.5-7B (pending Kaggle). TriviaQA (900 / 300 questions), MedMCQA (clinical, 300), HumanEval (162 tasks). |
| N32 TGCC-R across 6 model x dataset banks, 4 attack types | Non-epistemic attacks **OER 0.00 on every bank** (AgentGuard-lite 0.95-1.00). Sleeper: TriviaQA OER 0.01-0.02 (latency 0.6-0.8) at delta = 0.10 for Sonnet/GPT-5; at delta = 0.20 every bank 0.01-0.16. CRC guarantee holds in **12/12**. |
| N09 code pipeline (TGCC-R, delta = 0.20) | 89-99% of harmful commits blocked with unit tests, 82-83% with a reviewer LLM; honest FPR 0.05-0.15. |
| Realistic workflows | QA agent, planner-coder-reviewer pipeline with sandboxed execution (N09), multi-agent debate (N30), collusion (N13), Byzantine chains (N31). |
| N36 tool-calling agent (real tau-bench retail DB + policy; multi-turn ReAct with real tool execution; Sonnet 4.5, GPT-5, Haiku 4.5; refunds need a capability token) | Real attacks: indirect prompt injection in the tool result turns 53% / 35% / 20% of non-permitted requests into refunds; covert sleeper directive 0% / 35% / 3%; forced sleeper (E1) 100%. **TGCC-R + full tool audit** executes **0-7** of 47-133 violating refunds per attack (Sonnet injection: ungated 75, audit alone 26, TGCC-R alone 15, combined **7**); blocks 0-1.5% of compliant honest steps, escalates 0-4 of ~235 legitimate refunds; ~5 us per token. **Limitation:** honest GPT-5 itself violates the refund policy on 32% of non-permitted requests at confidence 0.94, so behaviour-change detection alone (TGCC-R without the audit) misses it (71/76 executed); a deterministic tool-argument audit as a layer signal closes the gap. |
| Reported limitation | When the honest model is itself poorly calibrated (Haiku, MedMCQA) a 10% honest-FPR guarantee costs sleeper detection (OER 0.37-0.96); delta = 0.20 restores it. Azure's filter blocks 15% of GPT-5's MedMCQA prompts. |

### R2-2. Debate: harm prevented, not revocation
| Evidence | Result (TGCC-R) |
|---|---|
| N30 paired harm prevented (McNemar) | N=1: 76 prevented / 0 caused (p = 3e-23); N=3: 23/1 (p = 3e-6); N=5, K=1: 3/4 (no gain); **N=5, K=2: wrong 0.47 -> 0.21, 22/1 (p = 6e-6)**. |
| N30 influence before revocation | An admitted sleeper flips 29-39% of honest agents from correct to wrong; after revocation 6-19%; harm concentrates in the questions before revocation. |
| Cost | Honest agent-questions denied **16-19%** (TGCC: 27-30%); pool abstains 5% (TGCC: 14%). |

### R2-3. Baselines and security-utility trade-off
| Evidence | Result |
|---|---|
| N03, N27, N32 | 11+ gates under identical calibration (Epistemic-only, Strict-min, Mean, AgentGuard, DynaTrust, EigenTrust, Naive, static thresholds, fixed weights, TGCC ablations). |
| N27 static thresholds | theta = 0.30 lets non-epistemic attacks through (OER 0.42-0.99); theta = 0.55 denies 28-45% of honest commits. |
| N26 / N27 fixed weights | Identical to adaptive. |
| N27 frontier, escalation view; N29 / N32 | OER vs honest FPR over delta; per-1,000-action escalation costs; code-task FPR now 0.05-0.15 (not 0.87). |

### R2-4. Inconsistencies
| Item | Resolution |
|---|---|
| Naive OER 0.12 | **1.00** in all 30 episodes (N01). |
| 0.87 FPR | Explicit denominators everywhere (e.g. 33/300); denials follow genuine model errors (177/180), not warm-up (N27). |
| Fig. 5(b) colour bar | Heatmaps regenerated from code (N11, N02). |
| Variability | Episode-level bootstrap or Wilson CIs throughout. |

### R2-5. Probe validation, prompts, coupling matrix
| Evidence | Result |
|---|---|
| N28 LLM evaluator (full prompt, 1-5 scales, s = (r-1)/4) | AUROC vs an independent label: tone **0.96-1.00** (regex 0.38-0.51), focus **0.74-0.78** (regex 0.44-0.53); resample std <= 0.009. |
| N28(c) real failures, TGCC-R + evaluator | Genuine hostile, off-topic and opaque failures admitted **0.00** for both models (regex probes: 1.00 for Claude's hostile replies). |
| N04, N05, N23, N33 | Critic and evaluator reliability, noise, poisoning, audits. |
| N02, N21 | 26 coupling matrices / learned coupling change OER by <= 0.03 (original TGCC). |
| N34 coupling structure under TGCC-R (6 real banks; 26 N02 matrices, N21 matrix, matrix **learned from real traces of the other dataset**, permuted layer orders, no composite) | Non-epistemic attacks OER **0.00** for every matrix and order. Sleeper OER range over 29 matrices: 0.01-0.02 (TriviaQA), 0.08-0.09 (GPT-5 MedMCQA), 0.28-0.34 (Sonnet MedMCQA), 0.49-0.67 (Haiku MedMCQA); honest FPR moves only where the pilot is non-representative (Haiku TriviaQA 0.39-0.65). Removing the composite leaks the sleeper on MedMCQA (OER 1.00): the composite matters, its exact matrix does not. The real-data matrix puts weight only on epistemic -> behavioural / role / institutional (0.67-1.00), supporting epistemic as the common prerequisite. |

### R2-6. Theory
| Item | Fix | Evidence |
|---|---|---|
| Prop. 1 | Fixed point of the expected-evidence recursion; gap E[a/(a+b)] - E[a]/E[a+b] bounded by its delta-method term, O(1 - gamma) | Simulated: MAE 0.007 (Fig. 2a). **N35 real streams** (30 layer x bank streams): \|E[T] - T*(rho_hat)\| max 0.023, mean 0.003; ratio-of-expectations gap <= 0.0075 and matches the delta-method term within 0.0004 |
| Lemma 3 | Discounted-regret lemma with proof | N26 |
| Theorem 4 | Martingale form with prior term and plateau | N22, N07 |
| Theorem 6 / Eq. (14) | State-conditioned closed form | N22, N07 |

### R2-7. Calibration
| Evidence | Result |
|---|---|
| N29 | Per-step DKW bounds vacuous on real streams (tau_int = 30-50); pure quantile misses delta; held-out validation error 0.12-0.43. |
| N29 / N32 TGCC-R with CRC | Guarantee holds in **48/48** (N29) and **12/12** (N32) settings. Sample size: delta = 0.10 needs about 24 ten-step honest sessions (OER 0.02-0.04 on TriviaQA); delta = 0.20 about 14; at least 1/delta - 1 sessions always. |
| Numbers | Burn-in 66.7 steps; Eq. (14) 804 steps; pre-warmed pilot, no burn-in. Calibrate on sessions from the deployment workload (a non-representative pilot slice mis-calibrates: Haiku). |

### R2-8. Scalability and complexity
| Evidence | Result |
|---|---|
| N24(a) | Controller cost vs L = 3..32: 12 -> 86 us, quadratic fit R^2 = 1.000 (linear 0.961); vs \|C\| = 1..256: 14 -> 21 us. |
| N24(b) real capability tokens | ~16 us per agent-step (controller, HMAC token, gateway check, revocation broadcast), N = 1..100, 1-4 gateways; **0 stale tokens accepted**. |
| N06 / N24(c) | LLM agent call 1.45-1.91 s; LLM critic or evaluator +1.3-2.0 s; the probes, not the controller, dominate. |
| N31(c) | Conjunctive pipelines lose availability with N (inherent to Theorem 2's rule; reported as a limitation). |
