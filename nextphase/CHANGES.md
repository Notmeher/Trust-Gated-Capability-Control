# CHANGES - post-review experiment phase

This file lists every code change, bug fix, and new experiment made after the KDD
reviews (see `../peer_review.md`). Each new experiment writes to its own folder,
in the same layout as `final/`: `results.json`, `README.md` and `figures/`.
`final/` is left unchanged as the record of the submitted results.

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

Simulations (N08, N11) feed the simulated Bernoulli epistemic outcomes through the same
rolling-window form as the real probe (`streams.windowed_epistemic`).

The module `n08_calibration_fix.py` was renamed to `n08_calibration.py`; its output folder is now
`nextphase/n08_calibration/`.

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
| N00 | `n00_legacy_audit` | 14qA Q1; D1aZ Q1, Q2; Jqqf W3 | Audit of the submitted streams (B1, B2) and where each disputed E1 number comes from |
| N01 | `n01_e1_multi_episode` | 14qA Q1, W2; D1aZ Q1–Q3, W1; Jqqf W3 | E1 re-run: 15 disjoint 60-question episodes per provider, out-of-sample pilot calibration, a single metric definition, and a per-conjunct denial breakdown (why coupling did or did not matter) |
| N02 | `n02_real_stream_sensitivity` | 14qA W3, Q3; eY9w W3; RRLq W4 | Sweeps on the real streams of p, coupling scale, γ, ω, η and λ (recalibrated and frozen thresholds); an E3-style p×c heatmap on real streams; 26 coupling matrices; permuted layer order |
| N03 | `n03_matched_fpr_baselines` | Jqqf W2, W3; D1aZ W2; 14qA Q2; eY9w W2 | 11 gates, including Epistemic-only (Beta) and Strict-min, each calibrated identically; OER at matched honest FPR, plus detection AUC |
| N04 | `n04_critic_reliability` | D1aZ W3; RRLq W1 | Critic noise (symmetric, missed-error, false-alarm) and a reference-free LLM judge (self and cross) as the epistemic critic |
| N05 | `n05_probe_validation` | RRLq W1 | Probe validity on LLM-generated labelled failure modes, resampling stability, and agreement between the alias-matcher critic and an LLM judge |
| N06 | `n06_end_to_end_cost` | RRLq W2 | Per-step latency and token cost, including the critic call |
| N07 | `n07_theory_checks` | D1aZ W4, W5; Jqqf W1 | Checks the Theorem 4 floor numerically. Shows Eq. (14) is undefined as printed, and that the reviewer's fix over-predicts by 1.2–2.1×. Derives a new exact closed form. |
| N08 | `n08_calibration` | Jqqf W2 and follow-up | Quantile vs min-of-pilot calibration (simulation and real pilots); effect of changing ε on the admitted fraction |
| N09 | `n09_code_pipeline` | 14qA W2; D1aZ W3 | E4 on HumanEval: 162 tasks × 2 providers, 20 episodes each, Wilson CIs, and a reviewer-LLM critic in place of unit tests |
| N10 | `n10_debate` | 14qA W2 | E2 with real LLMs: heterogeneous Claude/gpt-5 teams N ∈ {1, 3, 5}, two 60-question series each, gated vs ungated |
| N11 | `n11_simulation_e3_e5` | Reproducibility; 14qA W3 | E3 and E5 regenerated from code in this repo; E3 also with per-cell calibration |
| N12 | `n12_non_epistemic_compromise` | D1aZ W2; Jqqf W2 | Compromises that leave the epistemic layer healthy (policy, off-topic, hostile): where the multi-layer stack matters |

## 4. How to reproduce

```powershell
.\.venv\Scripts\python.exe -m tgcc.nextphase.responses                     # QA banks (API)
.\.venv\Scripts\python.exe -m tgcc.nextphase.n00_legacy_audit
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
```

With the cache present, every step except the first run of the API steps runs offline and is deterministic. The exception is the temperature-1 resamples in N05, which are stored in `_data/probe_bank_*.json`.
