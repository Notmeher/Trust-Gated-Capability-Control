# nextphase/ - post-review experiments (KDD Submission 1175)

This folder holds the improved and new experiments produced in response to the five reviews in
[`../peer_review.md`](../peer_review.md). Each experiment folder has the same layout as
[`../final/`](../final/): `README.md` (method + tables), `results.json` (all raw numbers) and
`figures/`.

* [`SUMMARY.md`](SUMMARY.md) - consolidated results and what each one means for the paper.
* [`CHANGES.md`](CHANGES.md) - bug fixes, code changes, the method update (TGCC and the TGCC-Smoothed ablation), and reproduction commands.
* [`../manuscript_update.md`](../manuscript_update.md) - section-by-section edits for the paper.
* `_data/` - shared raw data: TriviaQA/HumanEval subsets, per-provider LLM response banks, judge verdicts, probe banks, logs.

| ID | Folder | Replaces / extends | Reviewer issues |
|---|---|---|---|
| N00 | [`n00_legacy_audit`](n00_legacy_audit/README.md) | Table 1, 9, 12 provenance | 14qA Q1; D1aZ Q1, Q2; Jqqf W3 |
| N01 | [`n01_e1_multi_episode`](n01_e1_multi_episode/README.md) | E1, Table 1, Fig. 1 | 14qA Q1, W2; D1aZ Q1–Q3, W1; Jqqf W3 |
| N02 | [`n02_real_stream_sensitivity`](n02_real_stream_sensitivity/README.md) | E3, E11 (on real streams), structure misspecification | 14qA W3, Q3; eY9w W3; RRLq W4 |
| N03 | [`n03_matched_fpr_baselines`](n03_matched_fpr_baselines/README.md) | E6, Table 9 | Jqqf W2, W3; D1aZ W2; 14qA Q2; eY9w W2 |
| N04 | [`n04_critic_reliability`](n04_critic_reliability/README.md) | new | D1aZ W3; RRLq W1 |
| N05 | [`n05_probe_validation`](n05_probe_validation/README.md) | new | RRLq W1 |
| N06 | [`n06_end_to_end_cost`](n06_end_to_end_cost/README.md) | E5 overhead claim | RRLq W2 |
| N07 | [`n07_theory_checks`](n07_theory_checks/README.md) | Theorem 4, Eq. (14) | D1aZ W4, W5; Jqqf W1 |
| N08 | [`n08_calibration`](n08_calibration/README.md) | Algorithm 2, E15 | Jqqf W2 and follow-up |
| N09 | [`n09_code_pipeline`](n09_code_pipeline/README.md) | E4, Fig. 6 | 14qA W2; D1aZ W3 |
| N10 | [`n10_debate`](n10_debate/README.md) | E2, Fig. 3 | 14qA W2 |
| N11 | [`n11_simulation_e3_e5`](n11_simulation_e3_e5/README.md) | E3, E5, Figs. 5, 7 | reproducibility; 14qA W3 |
| N12 | [`n12_non_epistemic_compromise`](n12_non_epistemic_compromise/README.md) | new | D1aZ W2; Jqqf W2 |
