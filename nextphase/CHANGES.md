# CHANGES - post-review experiment phase

This file lists every code change, bug fix, and new experiment made after the KDD
reviews (see `../peer_review.md`). Each experiment writes to its own folder with
`results.json`, `README.md` and `figures/`.

The submitted-version drivers (`src/tgcc/experiments/w1–w16`, `baselines/`, `metrics.py`,
`scripts/`, `main.py`) and their outputs (`final/`) were removed from the working tree once every
experiment had been re-implemented here. They remain in git history at commit `9f4232fb`.

## 1. Bugs found in the submitted pipeline (all fixed)

| # | Bug | Effect on submitted results | Fix |
|---|---|---|---|
| B1 | gpt-5 is a reasoning model. With `max_completion_tokens=200` and no `reasoning_effort`, it spent the budget on hidden reasoning and returned **empty text** (61 of the 5,073 cached gpt-5 calls, and 3 of the 8 honest W1 turns). | gpt-5 columns of W1/W3/W6/W8/W9 (Tables 8, 9, 11, 12) were computed partly on empty outputs. | `models.py`: optional `reasoning_effort` (`"minimal"` for gpt-5) and a `reasoning_tokens` field in the metadata. The new gpt-5 banks have 2 empty outputs out of 1,920. |
| B2 | `answer_matches("", refs)` returned **True**, because the empty string is a substring of every reference. | Empty gpt-5 answers were scored correct, which inflated honest-phase epistemic trust. | `probes.py`: an empty answer never matches, and reverse containment needs at least 3 characters. The new experiments use a TriviaQA normalized-alias matcher (`nextphase/datasets.py::tqa_match`). |
| B3 | In W3/W6 all baselines used **TGCC's calibrated thresholds**. | Scalar baselines (EigenTrust, Constitutional) were forced to OER = 1.00, which is unfair to them. | Every gate is calibrated with the same Algorithm 2 on the same pilot (`nextphase/gates.py`, N03). |
| B4 | W1 calibrated on the honest prefix of the episode it then evaluated. | FPR = 0 by construction (in-sample). | A separate 120-question honest pilot, disjoint from all evaluation items (N01). |
| B5 | Algorithm 2 step 5 ("shrink ε if fewer than 1−δ pilot steps are admitted") has the wrong direction, and the min-of-pilot estimator gets more permissive the more honest data it sees. | This is the calibration concern Jqqf raised. | `gates.calibrate`: quantile estimator with a step 5 that widens ε (N08). |
| B6 | The E1–E5 drivers (Table 1, Figs. 1, 3, 5, 6, 7) are **not in the artifact**. | The numbers cannot be reproduced; Naive OER 0.12 conflicts with "never revokes". | Re-implemented: N01 (E1), N09 (E4), N10 (E2), N11 (E3, E5). |
| B7 | The Anthropic client could not use workspace-unscoped keys, and an Anthropic output-filter error (400) crashed runs. | n/a | `config.py` reads an optional `ANTHROPIC_WORKSPACE_ID`, sent as a header. `models.py` treats `anthropic.BadRequestError` as a filtered (empty) response, like Azure. |
| B8 | Tenacity only retried `httpx` errors. | Rate limits aborted long runs. | `models.py` also retries OpenAI/Anthropic rate-limit, connection, timeout and 5xx errors (8 attempts). |
| B9 | Algorithm 2 drops a burn-in of ⌈1/(1−γ)⌉ steps, but Appendix H pre-warms the beliefs, so deployment starts in the same transient that was excluded from calibration. | Honest agents are denied during the first steps (up to 95% denial on steps 0–2 in the code pipeline). | When beliefs are pre-warmed, the pilot runs from the same pre-warmed state and keeps all steps (burn-in 0). Burn-in is only used without pre-warming (N08 simulation). |

## 1a. Where the disputed submitted numbers came from (for the response letter)

| Number in the submitted PDF | What it actually was | Replaced by |
|---|---|---|
| Table 1 / Fig. 1: E1 TGCC 0.17, TGCC-NoSyn 0.72, Naive 0.12 | Produced by E1 code that was not in the artifact (B6), so it cannot be reproduced. Naive 0.12 contradicts a gate that never revokes (latency ∞ means OER 1.00). | N01 |
| Table 8 / Table 9 (E6): TGCC 0.11 [0.08, 0.25] Claude, 0.07 GPT-5 | Bootstrap mean over resamples of the single 20-turn W1 episode (compromise at step 8), not the E1 episode. The GPT-5 stream was affected by B1 and B2. | N01 across-episode CIs, N03 |
| Table 12 (E9): TGCC 0.25 Claude | Point estimate on the same single 20-turn W1 episode (12 post-compromise steps). | N01, N15 |
| "4.2×" (0.17 vs 0.72) | Ratio of the unreproducible Table 1 values. | Deleted; coupling's effect is shown in N12 |
| "Superior to all baselines" vs AgentGuard OER | Baselines shared TGCC's thresholds (B3). | N03: TGCC ties AgentGuard-lite on E1, wins on N12 and N09 |

Submitted W1 streams: Claude 0 empty answers; GPT-5 3 empty answers out of 20, all scored correct
(3 of 8 honest turns). Submitted LLM cache: 61 of 5,073 GPT-5 entries were empty.

## 1b. Method as evaluated in nextphase (single proposed method)

All `nextphase/` experiments evaluate **one** proposed method, called **TGCC** everywhere
(figures, tables, READMEs). It differs from the submitted version in two places:

1. **Epistemic check.** The epistemic prerequisite conjunct of the grant rule reads the per-turn
   epistemic probe signal (the rolling-window calibration score). The composite keeps Beta memory,
   coupling and Hedge weights. Default: `TGCCParams(prereq_raw=True)` in `nextphase/gates.py`.
2. **Algorithm 2.** θ = δ-quantile of the pre-warmed honest pilot − ε (δ = 0.05, ε = 0.05);
   ε is increased if fewer than 1−δ pilot steps are admitted.

Ablations reported alongside:
- **TGCC-Smoothed**: the epistemic check reads the Beta-smoothed effective trust. This is the
  submitted design.
- **TGCC-NoSyn**: no coupling.
- **TGCC-CompositeOnly**: no epistemic check.
- **Min-of-pilot calibration**: in N04 and N08.

Why: N03 and N09 show that the Beta-smoothed check is slow (latency 3–7 steps). N12 shows that the
composite is what catches non-epistemic compromises.

Simulations (N07c, N08, N11, N16, N18, N19) feed the simulated Bernoulli epistemic outcomes through the same
rolling-window form as the real probe (`streams.windowed_epistemic`, `sim.py`).

## 2. New infrastructure (`src/tgcc/nextphase/`)

| Module | Purpose |
|---|---|
| `io.py` | Output helpers rooted at `nextphase/` |
| `datasets.py` | Downloads TriviaQA (rc.nocontext validation) and HumanEval through the HF datasets-server JSON API, plus the TriviaQA alias matcher |
| `responses.py` | Per-item response banks: each question is answered once per provider and phase (honest, sleeper, pilot) and cached |
| `streams.py` | Builds independent episodes from disjoint item subsets; optional critic noise and post-compromise transforms |
| `gates.py` | One gate interface for TGCC, its ablations and 7 baselines; Algorithm 2 (min / quantile, corrected step 5); metrics |
| `evaluation.py` | Calibrate on the pilot, evaluate on episodes, episode-level CIs, pooled OER-vs-FPR curves |
| `stats.py` | Episode-bootstrap CIs and Wilson intervals |
| `sandbox.py` | AST audit plus isolated `python -I` subprocess with timeout for LLM-written code (N09) |
| `sim.py` | Simulated signal streams and honest simulated pilot shared by the simulation experiments |

Data in `nextphase/_data/`:
- TriviaQA subset: 1,196 items, of which 900 are evaluation items and 120 are pilot items.
- HumanEval: 164 tasks, 162 used.
- Response banks per provider.
- LLM-judge verdicts.
- Probe banks.
- Code banks.

All LLM calls are disk-cached under `cache/llm/`.

## 3. New and re-done experiments

| ID | Folder | Reviewer issues | What changed |
|---|---|---|---|
| N01 | `n01_e1_multi_episode` | 14qA Q1, W2; D1aZ Q1–Q3, W1; Jqqf W3 | E1 re-run: 15 disjoint 60-question episodes per provider, out-of-sample pilot calibration, a single metric definition, and a per-conjunct denial breakdown (why coupling did or did not matter) |
| N02 | `n02_real_stream_sensitivity` | 14qA W3, Q3; eY9w W3; RRLq W4 | Sweeps on the real streams of p, coupling scale, γ, ω, η and λ (recalibrated and frozen thresholds); an E3-style p×c heatmap on real streams; 26 coupling matrices; permuted layer order |
| N03 | `n03_matched_fpr_baselines` | Jqqf W2, W3; D1aZ W2; 14qA Q2; eY9w W2 | 11 gates, including Epistemic-only (Beta) and Strict-min, each calibrated identically; OER at matched honest FPR, plus detection AUC |
| N04 | `n04_critic_reliability` | D1aZ W3; RRLq W1 | Critic noise (symmetric, missed-error, false-alarm) and a reference-free LLM judge (self and cross) as the epistemic critic |
| N05 | `n05_probe_validation` | RRLq W1 | Probe validity on LLM-generated labelled failure modes, resampling stability, and agreement between the alias-matcher critic and an LLM judge |
| N06 | `n06_end_to_end_cost` | RRLq W2 | Per-step latency and token cost, including the critic call |
| N07 | `n07_theory_checks` | D1aZ W4, W5; Jqqf W1 | Checks the Theorem 4 floor numerically. Shows Eq. (14) is undefined as printed, and that the reviewer's fix over-predicts by 1.2–2.1×. Derives a new exact closed form. Adds a gate-level latency sweep over γ and δ. |
| N08 | `n08_calibration` | Jqqf W2 and follow-up | Quantile vs min-of-pilot calibration (simulation and real pilots); effect of changing ε on the admitted fraction |
| N09 | `n09_code_pipeline` | 14qA W2; D1aZ W3 | E4 on HumanEval: 162 tasks × 2 providers, 20 episodes each, Wilson CIs, and a reviewer-LLM critic in place of unit tests |
| N10 | `n10_debate` | 14qA W2 | E2 with real LLMs: heterogeneous Claude/gpt-5 teams N ∈ {1, 3, 5}, two 60-question series each, gated vs ungated |
| N11 | `n11_simulation_e3_e5` | Reproducibility; 14qA W3 | E3 and E5 regenerated from code in this repo; E3 also with per-cell calibration |
| N12 | `n12_non_epistemic_compromise` | D1aZ W2; Jqqf W2 | Compromises that leave the epistemic layer healthy (policy, off-topic, hostile): where the multi-layer stack matters |
| N13 | `n13_collusion` | E7 | Real-LLM collusion: 3 personas × 5 TriviaQA episodes per model, TriviaQA matcher, per-agent pilots, team-level outcome |
| N14 | `n14_prompt_injection` | E8 | Real-LLM injection on all 900 questions per model, GPT-5 with `reasoning_effort`, harmful-admission metric |
| N15 | `n15_layer_ablation` | E9; D1aZ W2 | Spoof/remove each layer on the real E1 and N12 streams |
| N16 | `n16_bounded_forgery` | Assumption 1(iii) | Bounded forgery with calibrated gates and baselines |
| N17 | `n17_adaptive_attacker` | E16; Remark 4 | Attack rate × confidence knob on the real streams; attacker-utility metric |
| N18 | `n18_long_horizon_recovery` | E10, E12 | Drift and recovery with calibrated gates, 20–50 seeds |
| N19 | `n19_byzantine_chain` | E13; Theorem 2 | 20% sleepers, N = 1–50, chain availability and blast radius |
| N20 | `n20_audit_trail` | E14 | Per-step decision reports for the two-conjunct grant rule on the real streams |
| N21 | `n21_learned_coupling` | RRLq W4 | Coupling fitted from traces and used in the gate on the real streams |

## 3a. Submitted experiments → revision

Every submitted experiment was re-implemented and re-run with the method of §1b, the fixes of §1
and identical calibration. None of the old numbers is reused.

| Submitted driver | Paper | Revision | What changed in the design |
|---|---|---|---|
| w1_multi_model | E1 (and the E6 / E9 streams) | N01 | 15 disjoint 60-question TriviaQA episodes per model. w1 was a single 20-turn episode on the built-in question set; the paper's 60-question E1 code was not in the artifact |
| (not in artifact) | E2 | N10 | Real-LLM heterogeneous teams |
| (not in artifact) | E3 | N11 + N02 | Also per-cell calibration; real-stream heatmap |
| (not in artifact) | E4 | N09 | 162 HumanEval tasks × 2 models, 20 episodes; reviewer-LLM critic |
| (not in artifact) | E5 | N11 + N06 | Same simulation; real end-to-end cost |
| w2_bounded_forgery | (not in PDF) | N16 | Calibrated gates and baselines |
| w3_baselines | H.1 / Table 9 | N03 | Baselines calibrated identically; matched-FPR comparison |
| w4_learned_coupling | (not in PDF) | N21 | Fitted C also used in the gate on real streams |
| w5_latency_sweep | (not in PDF) | N07(c) | Gate-level latency vs γ, δ next to the exact Eq. (14) |
| w6_bootstrap_ci | E6 | N01 + N03 | Across-episode CIs instead of resampling one stream; Wilcoxon tests dropped |
| w7_collusion | E7 | N13 | New LLM calls, 5 × 60 TriviaQA questions per model, team-level outcome |
| w8_prompt_injection | E8 | N14 | 900 questions per model; GPT-5 empty-output bug fixed |
| w9_layer_ablation | E9 | N15 | Real E1 streams plus the three non-epistemic compromises |
| w10_long_horizon | E10 | N18 | 20 seeds, calibrated gates |
| w11_sensitivity | E11 | N02 | On real streams instead of simulation |
| w12_recovery | E12 | N18 | 50 seeds |
| w13_byzantine_chain | E13 | N19 | 20 seeds per N; chain availability |
| w14_audit_trail | E14 | N20 | Conjunct-level reports on real streams |
| w15_calibration_robustness | E15 | N08 | Quantile vs min-of-pilot; real pilots |
| w16_adaptive_attacker | E16 | N17 | Real streams; attack rate × confidence; attacker utility |

New in the revision (no submitted counterpart): N04, N05, N06, N07(a, b), N12.

## 4. How to reproduce

```powershell
.\.venv\Scripts\python.exe -m tgcc.nextphase.responses                     # QA banks (API)
.\.venv\Scripts\python.exe -m tgcc.nextphase.n01_e1_multi_episode
.\.venv\Scripts\python.exe -m tgcc.nextphase.n02_real_stream_sensitivity
.\.venv\Scripts\python.exe -m tgcc.nextphase.n03_matched_fpr_baselines
.\.venv\Scripts\python.exe -m tgcc.nextphase.n04_critic_reliability --collect   # judge calls (API)
.\.venv\Scripts\python.exe -m tgcc.nextphase.n05_probe_validation               # API
.\.venv\Scripts\python.exe -m tgcc.nextphase.n06_end_to_end_cost
.\.venv\Scripts\python.exe -m tgcc.nextphase.n07_theory_checks
.\.venv\Scripts\python.exe -m tgcc.nextphase.n08_calibration
.\.venv\Scripts\python.exe -m tgcc.nextphase.n09_code_pipeline --collect        # API + sandbox
.\.venv\Scripts\python.exe -m tgcc.nextphase.n10_debate                         # API
.\.venv\Scripts\python.exe -m tgcc.nextphase.n11_simulation_e3_e5
.\.venv\Scripts\python.exe -m tgcc.nextphase.n12_non_epistemic_compromise
.\.venv\Scripts\python.exe -m tgcc.nextphase.n13_collusion                      # API
.\.venv\Scripts\python.exe -m tgcc.nextphase.n14_prompt_injection               # API
.\.venv\Scripts\python.exe -m tgcc.nextphase.n15_layer_ablation
.\.venv\Scripts\python.exe -m tgcc.nextphase.n16_bounded_forgery
.\.venv\Scripts\python.exe -m tgcc.nextphase.n17_adaptive_attacker
.\.venv\Scripts\python.exe -m tgcc.nextphase.n18_long_horizon_recovery
.\.venv\Scripts\python.exe -m tgcc.nextphase.n19_byzantine_chain
.\.venv\Scripts\python.exe -m tgcc.nextphase.n20_audit_trail
.\.venv\Scripts\python.exe -m tgcc.nextphase.n21_learned_coupling
```

With the cache present, every step except the first run of the API steps runs offline and is deterministic. The exception is the temperature-1 resamples in N05, which are stored in `_data/probe_bank_*.json`.

---

## 5. Enhancement phase for the IEEE OJCS reviews (branch `enhancement`)

Reviewer mapping and results: [IEEE_REVIEW_COVERAGE.md](IEEE_REVIEW_COVERAGE.md). N01-N21 re-run unchanged
(byte-identical results apart from timestamps and last-digit float rounding).

### Code changes
| File | Change |
|---|---|
| `models.py` | Claude Haiku 4.5 provider (`anthropic_haiku`); open-weight providers (`qwen3-4b`, `qwen3-8b`, `qwen2.5-7b`) served by `nextphase/hf_backend.py` on Kaggle and read from the cache elsewhere (`CacheMiss` otherwise); `SpendLedger` hard cap on new API spend (`TGCC_BUDGET_USD`, default 10). |
| `nextphase/hf_backend.py` | Batched transformers engine: thread-safe queue, per-request token budgets, Qwen3 thinking disabled. |
| `nextphase/datasets.py` | MedMCQA (non-dental, single-answer) loader, MCQ matcher, format-stating MCQ prompt; retrying HF rows fetcher. |
| `nextphase/responses.py` | Per-dataset banks (`qa_bank_<dataset>_<provider>.json`), 300-item subsets for new banks; `available_banks()` unchanged so N01-N21 stay reproducible; `all_banks()` for N22+. |
| `nextphase/streams.py` | MCQ-aware sleeper forcing (a confidently stated wrong option). |
| `nextphase/gates.py` | `TGCCParams.prereq_all`: a per-turn conjunct on every layer (TGCC-R). |
| `nextphase/scenarios.py`, `tokens.py` | Shared real-stream scenarios; HMAC capability tokens, gateway, revocation bus (N24). |
| `nextphase/kaggle/` | Notebook generator and notebook for the Qwen data (TALA pattern: clone branch with the `github_token` secret). |

### Issues found and fixed in this phase
| # | Issue | Fix |
|---|---|---|
| E1 | On MedMCQA, Claude Sonnet ignored the system prompt's two-line format and reasoned at length (132/300 answers truncated before any `Answer:` line). | The MCQ user prompt restates the format; the partial run was discarded (cache entries deleted). |
| E2 | Concurrent identical judge prompts were sent before the first was cached (duplicate spend). | N23 groups jobs by prompt. |
| E3 | Theorem 4 bound without the prior term is invalid when theta exceeds the pre-warmed trust. | Prior term added (N22). |
| E4 | CRC over a common scale for all conjuncts degenerates (deterministic layers forced to be lenient). | Nested family scales only the stochastic conjuncts (N32). |

### TGCC-R everywhere, evaluator poisoning (follow-up)
| File | Change |
|---|---|
| `nextphase/tgcc_r.py` | Shared revised method: pilot-selected epistemic window, all-layer conjuncts, two-stage nested CRC (`crc_thresholds`, `calibrate_pilot`), empty outputs not observed (`mode`). |
| `nextphase/streams.py` | `epistemic_window` / `signal_mode` scoped settings (defaults unchanged, so N01-N21 are byte-identical). |
| N09, N13, N14, N23, N26-N32 | TGCC-R rows (original TGCC kept as reference). N30 re-run with TGCC-R agents (new round-2 calls). |
| `nextphase/n33_evaluator_poisoning.py` | New: payloads aimed at the LLM evaluator, defences D1-D3, canary audit with evaluator takeover. Qwen3-8B evaluator added to the Kaggle notebook. |

| # | Issue | Fix |
|---|---|---|
| E5 | A fixed 16-step window is too slow for reliable critics (code, TriviaQA) and an 8-step window too noisy on MedMCQA. | Window selected from the honest pilot alone (smallest W with pilot 2.5% tail >= 0.2). |
| E6 | CRC silently fell back to fully permissive thresholds when the rule-based layers alone exceeded delta on small pilots. | Two-stage nested family (stochastic thresholds first, then rule-based). |
| E7 | GPT-5's content-filtered (empty) outputs dragged the rule-based thresholds to 0. | Empty outputs are not observations in TGCC-R. |
| E8 | N33 canary criterion counted neutral-tone honest replies as failures (slow takeover detection). | Pass criteria on the evaluator's own scale (honest >= neutral, failure <= neutral). |

### Remaining reviewer items (follow-up 2)
| File | Change |
|---|---|
| `nextphase/n34_coupling_structure_tgcc_r.py` | R2-5: 29 coupling matrices (incl. one learned from real traces of the other dataset), layer orders and no-composite ablation under TGCC-R. |
| `nextphase/n35_prop1_real.py` | R2-6: Proposition 1 and the ratio-of-expectations gap on 30 real honest streams, with the delta-method gap. |
| `nextphase/n36_tool_agent.py` | R2-1: tau-bench retail tool-calling agent (real DB/policy, real tool execution) with sleeper, forced-sleeper and tool-result injection; TGCC-R with a deterministic tool-call audit; CRC on the loss "a policy-compliant step is blocked". |
| `nextphase/n37_controller_compromise.py`, `tokens.py` | R1-2: probe-authenticated append-only log (`SignedLog`), quorum gateway (`QuorumGateway`); independent replay verifiers against forged grants, tampered thresholds, tampered log and collusion. |

| # | Issue | Fix |
|---|---|---|
| E9 | tau-bench order ids carry a `#` prefix that agents drop, so every lookup failed. | Order ids are normalised in the tool and the checker. |
| E10 | With per-step honest FPR as the CRC loss, an honest agent that itself violates policy (GPT-5, 14% of tickets) forces the audit threshold to 0. | N36 calibrates the audited configurations on "a compliant step is blocked". |

### Open-weight models (Kaggle run)
| File | Change |
|---|---|
| `nextphase/_data/qa_bank_*qwen*.json`, `poison_*_qwen3-8b.json` | Qwen3-4B, Qwen3-8B, Qwen2.5-7B banks (TriviaQA, MedMCQA) and the Qwen3-8B critic / evaluator outputs from the Kaggle notebook; N22-N35 and N37 re-run with them. |
| `nextphase/kaggle/` | No Hugging Face token is used (public models); any injected token is removed (an expired token made the Hub return 401). |
| `nextphase/n22_theory_nonstationary.py` | Qwen models in the stationary and domain-shift streams, plus a Qwen model-swap stream. |
| `nextphase/tgcc_r.py`, `n32_revised_config.py` | `qualifying_windows`: pre-deployment epistemic qualification from the honest pilot; N32 reports it (fails for exactly the six Qwen banks). |

| # | Issue | Fix |
|---|---|---|
| E11 | N34's layer-order test permuted the signal columns, which also relabelled the epistemic probe as a rule-based conjunct (CRC then zeroed all rule-based thresholds on Qwen2.5-7B / MedMCQA). | Layer order now permutes only the synergy hierarchy of the composite; each conjunct stays attached to its probe. |
| E12 | On open-weight models the honest agent is confidently wrong too often for the epistemic layer to separate it from a sleeper (sleeper OER 0.32-1.00); stricter thresholds deny 0.45-0.97 of honest steps. | Reported as a limitation; TGCC-R flags it before deployment from the pilot (`qualifying_windows`). |
