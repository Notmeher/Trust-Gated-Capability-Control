# N32 - Revised TGCC configuration across model families and datasets

## Reviewer issues
IEEE R2-1 (more LLM families and independent datasets), with R2-3 (baselines), R2-5 (probes) and R2-7
(calibration). Extending the evaluation exposed three weaknesses of the nextphase configuration (see the module
docstring); each change below addresses one, and the table shows its effect.

## Configurations
* **A** nextphase TGCC (window 8; composite + epistemic; Algorithm 2 on the separate 120-item pilot).
* **B** A + epistemic window 16.
* **C** B + per-turn conjuncts on every layer (Definition 3 with req(c) = all layers; Bonferroni delta/K).
* **D = TGCC-R** C + conformal risk control on honest sessions from the deployment workload (stochastic
  conjuncts scaled, rule-based layer thresholds fixed); guarantee: E[per-step honest FPR] <= delta, shown for
  delta = 0.10 (D) and 0.20 (D').
* Baselines use D's calibration (delta = 0.10) and window. Empty outputs (provider filter) are removed.

20 random splits per bank; 10-step calibration sessions from 55% of the items; held-out honest sessions
for FPR and 60-step compromise episodes (compromise at step 20) for OER and latency.

| Stream | Gate | sleeper OER | policy OER | off-topic OER | hostile OER | sleeper latency | honest FPR |
|---|---|---:|---:|---:|---:|---:|---:|
| Claude Sonnet 4.5 / TriviaQA | A nextphase TGCC | 0.03 | 0.09 | 0.15 | 0.15 | 1.3 | 0.111 |
| Claude Sonnet 4.5 / TriviaQA | B + window 16 | 0.04 | 0.09 | 0.14 | 0.15 | 1.7 | 0.151 |
| Claude Sonnet 4.5 / TriviaQA | C + all-layer conjuncts | 0.04 | 0.00 | 0.00 | 0.00 | 1.8 | 0.147 |
| Claude Sonnet 4.5 / TriviaQA | D TGCC-R (CRC, delta=0.10) | 0.07 | 0.00 | 0.00 | 0.00 | 2.9 | 0.089 |
| Claude Sonnet 4.5 / TriviaQA | D' TGCC-R (CRC, delta=0.20) | 0.05 | 0.00 | 0.00 | 0.00 | 1.8 | 0.145 |
| Claude Sonnet 4.5 / TriviaQA | AgentGuard-lite | 0.07 | 0.98 | 0.98 | 0.98 | 2.9 | 0.089 |
| Claude Sonnet 4.5 / TriviaQA | Strict-min (Beta) | 0.12 | 0.11 | 0.20 | 0.15 | 4.6 | 0.057 |
| Claude Sonnet 4.5 / TriviaQA | Mean (Beta) | 0.81 | 0.22 | 0.46 | 0.58 | 32.3 | 0.001 |
| Claude Sonnet 4.5 / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 0.05 | 40.0 | 0.000 |
| GPT-5 / TriviaQA | A nextphase TGCC | 0.01 | 0.06 | 0.08 | 0.08 | 0.3 | 0.290 |
| GPT-5 / TriviaQA | B + window 16 | 0.01 | 0.06 | 0.09 | 0.08 | 0.5 | 0.316 |
| GPT-5 / TriviaQA | C + all-layer conjuncts | 0.02 | 0.00 | 0.00 | 0.00 | 0.8 | 0.265 |
| GPT-5 / TriviaQA | D TGCC-R (CRC, delta=0.10) | 0.08 | 0.00 | 0.00 | 0.00 | 3.1 | 0.081 |
| GPT-5 / TriviaQA | D' TGCC-R (CRC, delta=0.20) | 0.04 | 0.00 | 0.00 | 0.00 | 1.5 | 0.183 |
| GPT-5 / TriviaQA | AgentGuard-lite | 0.08 | 1.00 | 1.00 | 1.00 | 3.1 | 0.081 |
| GPT-5 / TriviaQA | Strict-min (Beta) | 0.12 | 0.17 | 0.33 | 0.27 | 4.7 | 0.010 |
| GPT-5 / TriviaQA | Mean (Beta) | 0.86 | 0.13 | 0.25 | 0.29 | 34.5 | 0.000 |
| GPT-5 / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 0.05 | 40.0 | 0.000 |
| Claude Haiku 4.5 / TriviaQA | A nextphase TGCC | 0.00 | 0.02 | 0.03 | 0.03 | 0.1 | 0.508 |
| Claude Haiku 4.5 / TriviaQA | B + window 16 | 0.00 | 0.02 | 0.02 | 0.02 | 0.1 | 0.524 |
| Claude Haiku 4.5 / TriviaQA | C + all-layer conjuncts | 0.01 | 0.00 | 0.00 | 0.00 | 0.2 | 0.452 |
| Claude Haiku 4.5 / TriviaQA | D TGCC-R (CRC, delta=0.10) | 0.61 | 0.00 | 0.00 | 0.00 | 22.0 | 0.044 |
| Claude Haiku 4.5 / TriviaQA | D' TGCC-R (CRC, delta=0.20) | 0.08 | 0.00 | 0.00 | 0.00 | 3.0 | 0.170 |
| Claude Haiku 4.5 / TriviaQA | AgentGuard-lite | 0.61 | 1.00 | 1.00 | 1.00 | 24.4 | 0.044 |
| Claude Haiku 4.5 / TriviaQA | Strict-min (Beta) | 0.05 | 0.08 | 0.13 | 0.11 | 2.0 | 0.059 |
| Claude Haiku 4.5 / TriviaQA | Mean (Beta) | 0.65 | 0.08 | 0.16 | 0.18 | 26.2 | 0.001 |
| Claude Haiku 4.5 / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 0.05 | 40.0 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | A nextphase TGCC | 0.53 | 0.43 | 0.94 | 0.67 | 21.1 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | B + window 16 | 0.09 | 0.42 | 0.92 | 0.66 | 3.8 | 0.095 |
| Claude Sonnet 4.5 / MedMCQA | C + all-layer conjuncts | 0.10 | 0.00 | 0.00 | 0.00 | 4.0 | 0.091 |
| Claude Sonnet 4.5 / MedMCQA | D TGCC-R (CRC, delta=0.10) | 0.56 | 0.00 | 0.00 | 0.00 | 22.4 | 0.035 |
| Claude Sonnet 4.5 / MedMCQA | D' TGCC-R (CRC, delta=0.20) | 0.10 | 0.00 | 0.00 | 0.00 | 4.0 | 0.091 |
| Claude Sonnet 4.5 / MedMCQA | AgentGuard-lite | 0.56 | 1.00 | 1.00 | 1.00 | 22.4 | 0.035 |
| Claude Sonnet 4.5 / MedMCQA | Strict-min (Beta) | 0.55 | 0.75 | 1.00 | 1.00 | 21.9 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | Mean (Beta) | 1.00 | 0.16 | 0.30 | 0.34 | 40.0 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 0.05 | 40.0 | 0.000 |
| GPT-5 / MedMCQA | A nextphase TGCC | 0.06 | 0.42 | 0.80 | 0.63 | 2.2 | 0.044 |
| GPT-5 / MedMCQA | B + window 16 | 0.09 | 0.41 | 0.79 | 0.63 | 3.5 | 0.078 |
| GPT-5 / MedMCQA | C + all-layer conjuncts | 0.10 | 0.00 | 0.00 | 0.00 | 4.0 | 0.061 |
| GPT-5 / MedMCQA | D TGCC-R (CRC, delta=0.10) | 0.37 | 0.00 | 0.00 | 0.00 | 15.0 | 0.042 |
| GPT-5 / MedMCQA | D' TGCC-R (CRC, delta=0.20) | 0.10 | 0.00 | 0.00 | 0.00 | 4.0 | 0.061 |
| GPT-5 / MedMCQA | AgentGuard-lite | 0.37 | 1.00 | 1.00 | 1.00 | 14.9 | 0.045 |
| GPT-5 / MedMCQA | Strict-min (Beta) | 0.63 | 0.83 | 1.00 | 1.00 | 25.2 | 0.000 |
| GPT-5 / MedMCQA | Mean (Beta) | 1.00 | 0.10 | 0.17 | 0.18 | 40.0 | 0.000 |
| GPT-5 / MedMCQA | Naive behavioural | 1.00 | 0.98 | 0.98 | 0.05 | 40.0 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | A nextphase TGCC | 0.05 | 0.61 | 0.97 | 0.89 | 2.1 | 0.085 |
| Claude Haiku 4.5 / MedMCQA | B + window 16 | 0.07 | 0.58 | 0.95 | 0.86 | 2.9 | 0.174 |
| Claude Haiku 4.5 / MedMCQA | C + all-layer conjuncts | 0.08 | 0.00 | 0.00 | 0.00 | 3.1 | 0.157 |
| Claude Haiku 4.5 / MedMCQA | D TGCC-R (CRC, delta=0.10) | 0.96 | 0.00 | 0.00 | 0.00 | 38.3 | 0.004 |
| Claude Haiku 4.5 / MedMCQA | D' TGCC-R (CRC, delta=0.20) | 0.18 | 0.00 | 0.00 | 0.00 | 7.1 | 0.135 |
| Claude Haiku 4.5 / MedMCQA | AgentGuard-lite | 0.96 | 1.00 | 1.00 | 1.00 | 38.3 | 0.004 |
| Claude Haiku 4.5 / MedMCQA | Strict-min (Beta) | 0.72 | 1.00 | 1.00 | 1.00 | 29.0 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | Mean (Beta) | 1.00 | 0.17 | 0.31 | 0.35 | 40.0 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 0.05 | 40.0 | 0.000 |

![revised](figures/revised_config.png)
