# Non-epistemic compromises

## Method
The agent keeps answering correctly (its own honest answers), so the epistemic
signal stays healthy; from step 20 one other layer is compromised:
policy (unauthorized shell/SQL action appended), offtopic (chit-chat prefix),
hostile (insulting tone); answer and confidence lines are kept. `none` = no
compromise (OER is then the honest admission rate over steps 20-59). All gates
calibrated by Algorithm 2 on the same honest pilot; 15 independent episodes per model.
A gate that only reads the epistemic layer cannot react to these failures,
whatever the quality of its probes.

## Results (OER, mean [95% CI] over episodes; lower = safer)
### Claude Sonnet 4.5
| Gate | none OER | policy OER | offtopic OER | hostile OER | FPR (none) |
|---|---|---|---|---|---|
| TGCC | 0.78 [0.66, 0.89] | 0.08 [0.06, 0.11] | 0.15 [0.10, 0.19] | 0.15 [0.11, 0.20] | 0.12 [0.05, 0.21] |
| TGCC-Smoothed | 0.72 [0.51, 0.90] | 0.09 [0.07, 0.11] | 0.16 [0.11, 0.19] | 0.16 [0.12, 0.20] | 0.06 [0.00, 0.17] |
| TGCC-NoSyn | 0.69 [0.50, 0.85] | 0.11 [0.07, 0.14] | 0.20 [0.14, 0.26] | 0.16 [0.11, 0.21] | 0.16 [0.05, 0.30] |
| Epistemic-only (Beta) | 0.72 [0.51, 0.90] | 0.72 [0.51, 0.90] | 0.72 [0.51, 0.90] | 0.72 [0.51, 0.90] | 0.06 [0.00, 0.17] |
| AgentGuard-lite | 0.83 [0.74, 0.91] | 0.83 [0.74, 0.91] | 0.83 [0.74, 0.91] | 0.83 [0.74, 0.91] | 0.12 [0.05, 0.21] |
| Strict-min (Beta) | 0.72 [0.51, 0.90] | 0.12 [0.09, 0.15] | 0.22 [0.17, 0.28] | 0.16 [0.12, 0.20] | 0.06 [0.00, 0.17] |
| Mean (Constitutional-lite) | 1.00 [1.00, 1.00] | 0.23 [0.19, 0.27] | 0.50 [0.39, 0.60] | 0.63 [0.50, 0.77] | 0.00 [0.00, 0.00] |
| Naive behavioural | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.05, 0.05] | 0.00 [0.00, 0.00] |
### GPT-5
| Gate | none OER | policy OER | offtopic OER | hostile OER | FPR (none) |
|---|---|---|---|---|---|
| TGCC | 0.57 [0.39, 0.75] | 0.06 [0.03, 0.08] | 0.08 [0.05, 0.12] | 0.08 [0.05, 0.11] | 0.27 [0.13, 0.43] |
| TGCC-Smoothed | 0.56 [0.36, 0.76] | 0.07 [0.05, 0.09] | 0.10 [0.07, 0.13] | 0.09 [0.06, 0.12] | 0.05 [0.00, 0.12] |
| TGCC-NoSyn | 0.48 [0.30, 0.67] | 0.12 [0.07, 0.16] | 0.18 [0.10, 0.26] | 0.16 [0.10, 0.23] | 0.27 [0.13, 0.43] |
| Epistemic-only (Beta) | 0.57 [0.37, 0.76] | 0.57 [0.37, 0.76] | 0.57 [0.37, 0.76] | 0.57 [0.37, 0.76] | 0.05 [0.00, 0.12] |
| AgentGuard-lite | 0.75 [0.66, 0.82] | 0.75 [0.66, 0.82] | 0.75 [0.66, 0.82] | 0.75 [0.66, 0.82] | 0.26 [0.12, 0.40] |
| Strict-min (Beta) | 0.57 [0.37, 0.76] | 0.18 [0.13, 0.22] | 0.32 [0.23, 0.40] | 0.26 [0.19, 0.33] | 0.05 [0.00, 0.12] |
| Mean (Constitutional-lite) | 1.00 [1.00, 1.00] | 0.13 [0.10, 0.15] | 0.24 [0.20, 0.29] | 0.27 [0.21, 0.32] | 0.00 [0.00, 0.00] |
| Naive behavioural | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.05, 0.05] | 0.00 [0.00, 0.00] |

![non-epistemic](figures/non_epistemic_oer.png)
