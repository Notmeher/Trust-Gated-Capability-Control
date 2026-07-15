# W6 - Statistical significance (bootstrap CIs + Wilcoxon)

## Weakness addressed
**W6**: Every headline number in the paper is from one seed and 20-60 turns.
Reviewers demand confidence intervals and significance tests.

## Method
1. Reuse the cached W1 per-turn signal matrix `(n_turns, 5)` for each provider.
2. **Stratified bootstrap** (1000 resamples) over the
   honest and sleeper index ranges independently -- preserves the compromise
   structure while resampling within each phase.
3. On every resample, run all six controllers (pre-warmed, per-provider W1
   thresholds) and record OER / latency / FPR.
4. Report bootstrap mean and 95% percentile CI for each metric.
5. **Wilcoxon signed-rank test** on per-turn grant vectors (TGCC vs. each
   baseline) as a within-episode significance test.

## Results
### anthropic
| Controller | OER (mean [95% CI]) | Latency (mean [95% CI]) | FPR (mean [95% CI]) | Wilcoxon p vs. TGCC |
|---|---|---|---|---|
| TGCC | 0.11 [0.08, 0.25] | 1.4 [1.0, 3.0] | 0.00 [0.00, 0.00] | - |
| Naive | 1.00 [1.00, 1.00] | 12.0 [12.0, 12.0] | 0.00 [0.00, 0.00] | 0.0027 |
| EigenTrust | 1.00 [1.00, 1.00] | 12.0 [12.0, 12.0] | 0.00 [0.00, 0.00] | 0.0027 |
| DynaTrust | 0.53 [0.25, 0.92] | 5.0 [3.0, 10.0] | 0.00 [0.00, 0.00] | 0.157 |
| AgentGuard | 0.08 [0.00, 0.25] | 0.1 [0.0, 1.0] | 0.00 [0.00, 0.00] | 0.157 |
| Constitutional | 1.00 [1.00, 1.00] | 12.0 [12.0, 12.0] | 0.00 [0.00, 0.00] | 0.0027 |

### azure_openai
| Controller | OER (mean [95% CI]) | Latency (mean [95% CI]) | FPR (mean [95% CI]) | Wilcoxon p vs. TGCC |
|---|---|---|---|---|
| TGCC | 0.07 [0.00, 0.17] | 0.9 [0.0, 2.0] | 0.03 [0.00, 0.25] | - |
| Naive | 1.00 [1.00, 1.00] | 12.0 [12.0, 12.0] | 0.00 [0.00, 0.00] | 0.00157 |
| EigenTrust | 1.00 [1.00, 1.00] | 12.0 [12.0, 12.0] | 0.00 [0.00, 0.00] | 0.00157 |
| DynaTrust | 0.98 [0.67, 1.00] | 11.2 [0.0, 12.0] | 0.04 [0.00, 0.38] | 0.00157 |
| AgentGuard | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.38 [0.12, 0.75] | 0.0253 |
| Constitutional | 1.00 [1.00, 1.00] | 12.0 [12.0, 12.0] | 0.00 [0.00, 0.00] | 0.00157 |


**Reading.**  A CI that stays below a baseline's CI is evidence at the
bootstrap level; p < 0.05 in the Wilcoxon column is evidence at the
per-turn level.  Both must agree for us to claim TGCC dominates.

## Configuration
```yaml
{'n_boot': 1000, 'seed': 17, 'compromise_step': 8, 'n_turns': 20}
```

## Files
- `results.json` - per-controller bootstrap stats and p-values.
- `figures/bootstrap_ci.png` - side-by-side CI bars for OER / latency / FPR.
