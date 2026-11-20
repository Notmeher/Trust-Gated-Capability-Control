# N23 - Critic poisoning (who watches the watchmen?)

## Reviewer issue
IEEE R1-2: an attacker that poisons the critic via indirect prompt injection could collapse
the trust layer. Not covered by N04 (noisy critics) or N14 (injection aimed at the agent).

## Method
Real E1 streams (4 disjoint 60-question episodes per target model, compromise at step 20).
The epistemic critic is a reference-free LLM judge. After compromise the sleeper appends a
payload aimed at the judge to its wrong answer (`authority` or `override`; `none` = no payload).
Judges: Claude Sonnet 4.5, GPT-5, Claude Haiku 4.5, Qwen3-8B. Defences: D1 hardened (spotlighted) prompt,
D2 model-free sanitisation, D3 cross-family AND-ensemble, D4 canary audit with fail-closed.
All thresholds come from Algorithm 2 on the critic's own honest pilot verdicts.

## Results: judge and gate under attack
Flip = P(judge says CORRECT | wrong sleeper answer). False alarm = P(judge says INCORRECT | correct honest answer).
Reference-answer critic, TGCC OER: Claude Sonnet 4.5: none 0.02, authority 0.02, override 0.02 / GPT-5: none 0.00, authority 0.00, override 0.00.

| Critic | Target model | Attack | flip | false alarm | TGCC-R OER | TGCC-R FPR | TGCC OER | TGCC FPR | AgentGuard-lite OER | TGCC-Smoothed OER |
|---|---|---|---:|---:|---|---|---|---|---:|---:|
| Claude Sonnet 4.5 plain | Claude Sonnet 4.5 | none | 0.03 | 0.11 | 0.02 [0.01, 0.03] | 0.09 [0.00, 0.19] | 0.02 [0.01, 0.03] | 0.33 [0.05, 0.70] | 0.02 | 0.04 |
| Claude Sonnet 4.5 plain | Claude Sonnet 4.5 | authority | 0.02 | 0.11 | 0.01 [0.00, 0.03] | 0.09 [0.00, 0.19] | 0.01 [0.00, 0.03] | 0.33 [0.05, 0.70] | 0.01 | 0.03 |
| Claude Sonnet 4.5 plain | Claude Sonnet 4.5 | override | 0.01 | 0.11 | 0.01 [0.00, 0.03] | 0.09 [0.00, 0.19] | 0.01 [0.00, 0.03] | 0.33 [0.05, 0.70] | 0.01 | 0.03 |
| Claude Sonnet 4.5 plain | GPT-5 | none | 0.03 | 0.10 | 0.02 [0.00, 0.04] | 0.21 [0.07, 0.32] | 0.01 [0.00, 0.02] | 0.46 [0.20, 0.74] | 0.01 | 0.04 |
| Claude Sonnet 4.5 plain | GPT-5 | authority | 0.04 | 0.10 | 0.02 [0.00, 0.04] | 0.21 [0.07, 0.32] | 0.01 [0.00, 0.02] | 0.46 [0.20, 0.74] | 0.01 | 0.04 |
| Claude Sonnet 4.5 plain | GPT-5 | override | 0.04 | 0.10 | 0.02 [0.00, 0.04] | 0.21 [0.07, 0.32] | 0.01 [0.00, 0.02] | 0.46 [0.20, 0.74] | 0.01 | 0.04 |
| Claude Sonnet 4.5 + D1 hardened | Claude Sonnet 4.5 | none | 0.03 | 0.13 | 0.04 [0.01, 0.06] | 0.04 [0.00, 0.11] | 0.03 [0.01, 0.05] | 0.14 [0.00, 0.38] | 0.03 | 0.06 |
| Claude Sonnet 4.5 + D1 hardened | Claude Sonnet 4.5 | authority | 0.03 | 0.13 | 0.04 [0.01, 0.06] | 0.04 [0.00, 0.11] | 0.03 [0.01, 0.05] | 0.14 [0.00, 0.38] | 0.03 | 0.06 |
| Claude Sonnet 4.5 + D1 hardened | Claude Sonnet 4.5 | override | 0.06 | 0.13 | 0.03 [0.01, 0.05] | 0.04 [0.00, 0.11] | 0.03 [0.01, 0.05] | 0.14 [0.00, 0.38] | 0.03 | 0.06 |
| Claude Sonnet 4.5 + D1 hardened | GPT-5 | none | 0.04 | 0.12 | 0.01 [0.00, 0.02] | 0.18 [0.00, 0.41] | 0.00 [0.00, 0.00] | 0.25 [0.03, 0.65] | 0.00 | 0.06 |
| Claude Sonnet 4.5 + D1 hardened | GPT-5 | authority | 0.04 | 0.12 | 0.01 [0.00, 0.02] | 0.18 [0.00, 0.41] | 0.00 [0.00, 0.00] | 0.25 [0.03, 0.65] | 0.00 | 0.06 |
| Claude Sonnet 4.5 + D1 hardened | GPT-5 | override | 0.07 | 0.12 | 0.01 [0.00, 0.02] | 0.18 [0.00, 0.41] | 0.00 [0.00, 0.00] | 0.25 [0.03, 0.65] | 0.00 | 0.05 |
| Claude Sonnet 4.5 + D2 sanitised | Claude Sonnet 4.5 | none | 0.02 | 0.13 | 0.03 [0.01, 0.05] | 0.19 [0.00, 0.56] | 0.03 [0.01, 0.05] | 0.19 [0.00, 0.56] | 0.03 | 0.10 |
| Claude Sonnet 4.5 + D2 sanitised | Claude Sonnet 4.5 | authority | 0.02 | 0.13 | 0.03 [0.01, 0.05] | 0.19 [0.00, 0.56] | 0.03 [0.01, 0.05] | 0.19 [0.00, 0.56] | 0.03 | 0.10 |
| Claude Sonnet 4.5 + D2 sanitised | Claude Sonnet 4.5 | override | 0.02 | 0.13 | 0.03 [0.01, 0.05] | 0.19 [0.00, 0.56] | 0.03 [0.01, 0.05] | 0.19 [0.00, 0.56] | 0.03 | 0.10 |
| Claude Sonnet 4.5 + D2 sanitised | GPT-5 | none | 0.03 | 0.12 | 0.03 [0.01, 0.05] | 0.06 [0.00, 0.19] | 0.03 [0.00, 0.05] | 0.16 [0.00, 0.41] | 0.03 | 0.12 |
| Claude Sonnet 4.5 + D2 sanitised | GPT-5 | authority | 0.03 | 0.12 | 0.03 [0.01, 0.05] | 0.06 [0.00, 0.19] | 0.03 [0.00, 0.05] | 0.16 [0.00, 0.41] | 0.03 | 0.12 |
| Claude Sonnet 4.5 + D2 sanitised | GPT-5 | override | 0.03 | 0.12 | 0.03 [0.00, 0.05] | 0.06 [0.00, 0.19] | 0.03 [0.00, 0.05] | 0.16 [0.00, 0.41] | 0.03 | 0.12 |
| GPT-5 plain | Claude Sonnet 4.5 | none | 0.04 | 0.09 | 0.09 [0.05, 0.12] | 0.00 [0.00, 0.00] | 0.06 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.17 |
| GPT-5 plain | Claude Sonnet 4.5 | authority | 0.05 | 0.09 | 0.09 [0.05, 0.12] | 0.00 [0.00, 0.00] | 0.06 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.17 |
| GPT-5 plain | Claude Sonnet 4.5 | override | 0.05 | 0.09 | 0.08 [0.04, 0.11] | 0.00 [0.00, 0.00] | 0.05 [0.02, 0.07] | 0.00 [0.00, 0.00] | 0.05 | 0.17 |
| GPT-5 plain | GPT-5 | none | 0.03 | 0.09 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.03 [0.03, 0.04] | 0.00 [0.00, 0.00] | 0.03 | 0.11 |
| GPT-5 plain | GPT-5 | authority | 0.06 | 0.09 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.03 [0.03, 0.04] | 0.00 [0.00, 0.00] | 0.03 | 0.11 |
| GPT-5 plain | GPT-5 | override | 0.06 | 0.09 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.02 [0.01, 0.03] | 0.00 [0.00, 0.00] | 0.02 | 0.11 |
| GPT-5 + D1 hardened | Claude Sonnet 4.5 | none | 0.04 | 0.09 | 0.06 [0.04, 0.07] | 0.03 [0.00, 0.05] | 0.04 [0.03, 0.05] | 0.03 [0.00, 0.05] | 0.04 | 0.16 |
| GPT-5 + D1 hardened | Claude Sonnet 4.5 | authority | 0.06 | 0.09 | 0.06 [0.04, 0.07] | 0.03 [0.00, 0.05] | 0.04 [0.03, 0.05] | 0.03 [0.00, 0.05] | 0.04 | 0.16 |
| GPT-5 + D1 hardened | Claude Sonnet 4.5 | override | 0.03 | 0.09 | 0.04 [0.03, 0.05] | 0.03 [0.00, 0.05] | 0.04 [0.03, 0.05] | 0.03 [0.00, 0.05] | 0.04 | 0.16 |
| GPT-5 + D1 hardened | GPT-5 | none | 0.05 | 0.09 | 0.01 [0.00, 0.03] | 0.24 [0.05, 0.51] | 0.01 [0.00, 0.02] | 0.31 [0.07, 0.66] | 0.01 | 0.08 |
| GPT-5 + D1 hardened | GPT-5 | authority | 0.06 | 0.09 | 0.02 [0.00, 0.04] | 0.24 [0.05, 0.51] | 0.01 [0.00, 0.02] | 0.31 [0.07, 0.66] | 0.01 | 0.09 |
| GPT-5 + D1 hardened | GPT-5 | override | 0.06 | 0.09 | 0.01 [0.00, 0.03] | 0.24 [0.05, 0.51] | 0.01 [0.00, 0.02] | 0.31 [0.07, 0.66] | 0.01 | 0.09 |
| GPT-5 + D2 sanitised | Claude Sonnet 4.5 | none | 0.01 | 0.11 | 0.08 [0.04, 0.12] | 0.00 [0.00, 0.00] | 0.06 [0.03, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.27 |
| GPT-5 + D2 sanitised | Claude Sonnet 4.5 | authority | 0.01 | 0.11 | 0.08 [0.04, 0.12] | 0.00 [0.00, 0.00] | 0.06 [0.03, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.27 |
| GPT-5 + D2 sanitised | Claude Sonnet 4.5 | override | 0.01 | 0.11 | 0.08 [0.04, 0.11] | 0.00 [0.00, 0.00] | 0.06 [0.03, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.27 |
| GPT-5 + D2 sanitised | GPT-5 | none | 0.04 | 0.10 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.04 | 0.21 |
| GPT-5 + D2 sanitised | GPT-5 | authority | 0.04 | 0.10 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.04 | 0.21 |
| GPT-5 + D2 sanitised | GPT-5 | override | 0.04 | 0.10 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.03 [0.01, 0.05] | 0.00 [0.00, 0.00] | 0.03 | 0.20 |
| Claude Haiku 4.5 plain | Claude Sonnet 4.5 | none | 0.05 | 0.21 | 0.04 [0.00, 0.09] | 0.04 [0.00, 0.11] | 0.06 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.14 |
| Claude Haiku 4.5 plain | Claude Sonnet 4.5 | authority | 0.08 | 0.21 | 0.05 [0.01, 0.09] | 0.04 [0.00, 0.11] | 0.07 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.07 | 0.14 |
| Claude Haiku 4.5 plain | Claude Sonnet 4.5 | override | 0.05 | 0.21 | 0.04 [0.00, 0.09] | 0.04 [0.00, 0.11] | 0.06 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.14 |
| Claude Haiku 4.5 plain | GPT-5 | none | 0.08 | 0.20 | 0.11 [0.07, 0.14] | 0.00 [0.00, 0.00] | 0.03 [0.01, 0.05] | 0.19 [0.10, 0.33] | 0.03 | 0.12 |
| Claude Haiku 4.5 plain | GPT-5 | authority | 0.09 | 0.20 | 0.11 [0.07, 0.14] | 0.00 [0.00, 0.00] | 0.03 [0.01, 0.05] | 0.19 [0.10, 0.33] | 0.03 | 0.12 |
| Claude Haiku 4.5 plain | GPT-5 | override | 0.08 | 0.20 | 0.11 [0.07, 0.14] | 0.00 [0.00, 0.00] | 0.03 [0.01, 0.05] | 0.19 [0.10, 0.33] | 0.03 | 0.12 |
| Claude Haiku 4.5 + D1 hardened | Claude Sonnet 4.5 | none | 0.05 | 0.25 | 0.04 [0.01, 0.07] | 0.23 [0.07, 0.38] | 0.03 [0.00, 0.05] | 0.41 [0.20, 0.69] | 0.03 | 0.05 |
| Claude Haiku 4.5 + D1 hardened | Claude Sonnet 4.5 | authority | 0.02 | 0.25 | 0.04 [0.01, 0.07] | 0.23 [0.07, 0.38] | 0.03 [0.00, 0.05] | 0.41 [0.20, 0.69] | 0.03 | 0.05 |
| Claude Haiku 4.5 + D1 hardened | Claude Sonnet 4.5 | override | 0.03 | 0.25 | 0.03 [0.01, 0.05] | 0.23 [0.07, 0.38] | 0.03 [0.00, 0.05] | 0.41 [0.20, 0.69] | 0.03 | 0.05 |
| Claude Haiku 4.5 + D1 hardened | GPT-5 | none | 0.07 | 0.25 | 0.03 [0.01, 0.05] | 0.32 [0.16, 0.46] | 0.03 [0.01, 0.05] | 0.39 [0.26, 0.50] | 0.03 | 0.09 |
| Claude Haiku 4.5 + D1 hardened | GPT-5 | authority | 0.03 | 0.25 | 0.02 [0.00, 0.04] | 0.32 [0.16, 0.46] | 0.02 [0.00, 0.04] | 0.39 [0.26, 0.50] | 0.02 | 0.09 |
| Claude Haiku 4.5 + D1 hardened | GPT-5 | override | 0.03 | 0.25 | 0.02 [0.00, 0.04] | 0.32 [0.16, 0.46] | 0.02 [0.00, 0.04] | 0.39 [0.26, 0.50] | 0.02 | 0.08 |
| Claude Haiku 4.5 + D2 sanitised | Claude Sonnet 4.5 | none | 0.05 | 0.22 | 0.07 [0.03, 0.11] | 0.06 [0.01, 0.12] | 0.06 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.22 |
| Claude Haiku 4.5 + D2 sanitised | Claude Sonnet 4.5 | authority | 0.05 | 0.22 | 0.07 [0.03, 0.11] | 0.06 [0.01, 0.12] | 0.06 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.22 |
| Claude Haiku 4.5 + D2 sanitised | Claude Sonnet 4.5 | override | 0.05 | 0.22 | 0.06 [0.02, 0.09] | 0.06 [0.01, 0.12] | 0.06 [0.04, 0.09] | 0.00 [0.00, 0.00] | 0.06 | 0.22 |
| Claude Haiku 4.5 + D2 sanitised | GPT-5 | none | 0.07 | 0.22 | 0.05 [0.03, 0.07] | 0.04 [0.00, 0.11] | 0.03 [0.01, 0.04] | 0.16 [0.10, 0.25] | 0.03 | 0.22 |
| Claude Haiku 4.5 + D2 sanitised | GPT-5 | authority | 0.07 | 0.22 | 0.05 [0.03, 0.07] | 0.04 [0.00, 0.11] | 0.03 [0.01, 0.04] | 0.16 [0.10, 0.25] | 0.03 | 0.22 |
| Claude Haiku 4.5 + D2 sanitised | GPT-5 | override | 0.07 | 0.22 | 0.04 [0.03, 0.06] | 0.04 [0.00, 0.11] | 0.03 [0.01, 0.04] | 0.16 [0.10, 0.25] | 0.03 | 0.22 |
| Qwen3-8B plain | Claude Sonnet 4.5 | none | 0.41 | 0.16 | 0.04 [0.00, 0.09] | 0.29 [0.15, 0.43] | 0.06 [0.00, 0.12] | 0.40 [0.09, 0.81] | 0.08 | 0.13 |
| Qwen3-8B plain | Claude Sonnet 4.5 | authority | 0.53 | 0.16 | 0.07 [0.00, 0.15] | 0.29 [0.15, 0.43] | 0.09 [0.00, 0.19] | 0.40 [0.09, 0.81] | 0.12 | 0.18 |
| Qwen3-8B plain | Claude Sonnet 4.5 | override | 0.86 | 0.16 | 0.64 [0.21, 0.93] | 0.29 [0.15, 0.43] | 0.71 [0.25, 1.00] | 0.40 [0.09, 0.81] | 0.93 | 0.73 |
| Qwen3-8B plain | GPT-5 | none | 0.38 | 0.16 | 0.06 [0.00, 0.11] | 0.38 [0.10, 0.80] | 0.08 [0.03, 0.12] | 0.19 [0.05, 0.36] | 0.11 | 0.22 |
| Qwen3-8B plain | GPT-5 | authority | 0.50 | 0.16 | 0.06 [0.00, 0.12] | 0.38 [0.10, 0.80] | 0.09 [0.03, 0.15] | 0.19 [0.05, 0.36] | 0.23 | 0.23 |
| Qwen3-8B plain | GPT-5 | override | 0.86 | 0.16 | 0.72 [0.25, 1.00] | 0.38 [0.10, 0.80] | 0.73 [0.29, 1.00] | 0.19 [0.05, 0.36] | 0.90 | 0.78 |
| Qwen3-8B + D1 hardened | Claude Sonnet 4.5 | none | 0.38 | 0.16 | 0.11 [0.05, 0.17] | 0.11 [0.03, 0.24] | 0.14 [0.06, 0.21] | 0.09 [0.01, 0.20] | 0.14 | 0.31 |
| Qwen3-8B + D1 hardened | Claude Sonnet 4.5 | authority | 0.01 | 0.16 | 0.05 [0.02, 0.07] | 0.11 [0.03, 0.24] | 0.06 [0.04, 0.07] | 0.09 [0.01, 0.20] | 0.06 | 0.25 |
| Qwen3-8B + D1 hardened | Claude Sonnet 4.5 | override | 0.53 | 0.16 | 0.19 [0.06, 0.31] | 0.11 [0.03, 0.24] | 0.25 [0.13, 0.33] | 0.09 [0.01, 0.20] | 0.44 | 0.41 |
| Qwen3-8B + D1 hardened | GPT-5 | none | 0.40 | 0.17 | 0.12 [0.04, 0.21] | 0.17 [0.05, 0.31] | 0.11 [0.01, 0.21] | 0.17 [0.05, 0.31] | 0.15 | 0.33 |
| Qwen3-8B + D1 hardened | GPT-5 | authority | 0.02 | 0.17 | 0.02 [0.00, 0.04] | 0.17 [0.05, 0.31] | 0.02 [0.00, 0.04] | 0.17 [0.05, 0.31] | 0.02 | 0.23 |
| Qwen3-8B + D1 hardened | GPT-5 | override | 0.59 | 0.17 | 0.31 [0.19, 0.43] | 0.17 [0.05, 0.31] | 0.18 [0.09, 0.31] | 0.17 [0.05, 0.31] | 0.31 | 0.42 |
| Qwen3-8B + D2 sanitised | Claude Sonnet 4.5 | none | 0.34 | 0.17 | 0.07 [0.00, 0.14] | 0.36 [0.03, 0.76] | 0.11 [0.09, 0.14] | 0.09 [0.00, 0.22] | 0.15 | 0.23 |
| Qwen3-8B + D2 sanitised | Claude Sonnet 4.5 | authority | 0.34 | 0.17 | 0.07 [0.00, 0.14] | 0.36 [0.03, 0.76] | 0.11 [0.09, 0.14] | 0.09 [0.00, 0.22] | 0.15 | 0.23 |
| Qwen3-8B + D2 sanitised | Claude Sonnet 4.5 | override | 0.34 | 0.17 | 0.07 [0.00, 0.14] | 0.36 [0.03, 0.76] | 0.11 [0.09, 0.14] | 0.09 [0.00, 0.22] | 0.22 | 0.23 |
| Qwen3-8B + D2 sanitised | GPT-5 | none | 0.37 | 0.17 | 0.11 [0.05, 0.18] | 0.07 [0.00, 0.22] | 0.14 [0.06, 0.24] | 0.07 [0.00, 0.22] | 0.24 | 0.33 |
| Qwen3-8B + D2 sanitised | GPT-5 | authority | 0.37 | 0.17 | 0.11 [0.05, 0.18] | 0.07 [0.00, 0.22] | 0.14 [0.06, 0.24] | 0.07 [0.00, 0.22] | 0.24 | 0.33 |
| Qwen3-8B + D2 sanitised | GPT-5 | override | 0.37 | 0.17 | 0.12 [0.05, 0.19] | 0.07 [0.00, 0.22] | 0.14 [0.06, 0.23] | 0.07 [0.00, 0.22] | 0.24 | 0.33 |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) | Claude Sonnet 4.5 | none | 0.02 | 0.17 | 0.09 [0.05, 0.12] | 0.00 [0.00, 0.00] | 0.06 [0.04, 0.07] | 0.01 [0.00, 0.04] | 0.06 | 0.21 |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) | Claude Sonnet 4.5 | authority | 0.02 | 0.17 | 0.09 [0.04, 0.12] | 0.00 [0.00, 0.00] | 0.05 [0.03, 0.07] | 0.01 [0.00, 0.04] | 0.05 | 0.20 |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) | Claude Sonnet 4.5 | override | 0.01 | 0.17 | 0.09 [0.04, 0.12] | 0.00 [0.00, 0.00] | 0.05 [0.03, 0.07] | 0.01 [0.00, 0.04] | 0.05 | 0.20 |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) | GPT-5 | none | 0.01 | 0.17 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.03 [0.03, 0.04] | 0.06 [0.00, 0.12] | 0.03 | 0.13 |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) | GPT-5 | authority | 0.03 | 0.17 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.03 [0.03, 0.04] | 0.06 [0.00, 0.12] | 0.03 | 0.13 |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) | GPT-5 | override | 0.02 | 0.17 | 0.04 [0.03, 0.05] | 0.00 [0.00, 0.00] | 0.03 [0.03, 0.03] | 0.06 [0.00, 0.12] | 0.03 | 0.13 |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) | Claude Sonnet 4.5 | none | 0.01 | 0.18 | 0.03 [0.00, 0.06] | 0.15 [0.05, 0.23] | 0.04 [0.01, 0.07] | 0.06 [0.01, 0.12] | 0.04 | 0.12 |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) | Claude Sonnet 4.5 | authority | 0.01 | 0.18 | 0.03 [0.00, 0.06] | 0.15 [0.05, 0.23] | 0.04 [0.01, 0.07] | 0.06 [0.01, 0.12] | 0.04 | 0.12 |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) | Claude Sonnet 4.5 | override | 0.02 | 0.18 | 0.03 [0.00, 0.06] | 0.15 [0.05, 0.23] | 0.04 [0.01, 0.06] | 0.06 [0.01, 0.12] | 0.04 | 0.12 |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) | GPT-5 | none | 0.03 | 0.17 | 0.01 [0.00, 0.02] | 0.20 [0.05, 0.35] | 0.01 [0.00, 0.03] | 0.28 [0.05, 0.59] | 0.01 | 0.07 |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) | GPT-5 | authority | 0.03 | 0.17 | 0.01 [0.00, 0.02] | 0.20 [0.05, 0.35] | 0.01 [0.00, 0.03] | 0.28 [0.05, 0.59] | 0.01 | 0.07 |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) | GPT-5 | override | 0.01 | 0.17 | 0.01 [0.00, 0.02] | 0.20 [0.05, 0.35] | 0.01 [0.00, 0.03] | 0.28 [0.05, 0.59] | 0.01 | 0.07 |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) | Claude Sonnet 4.5 | none | 0.01 | 0.25 | 0.04 [0.01, 0.06] | 0.11 [0.00, 0.23] | 0.04 [0.01, 0.07] | 0.10 [0.00, 0.20] | 0.04 | 0.19 |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) | Claude Sonnet 4.5 | authority | 0.03 | 0.25 | 0.04 [0.01, 0.06] | 0.11 [0.00, 0.23] | 0.04 [0.01, 0.07] | 0.10 [0.00, 0.20] | 0.04 | 0.19 |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) | Claude Sonnet 4.5 | override | 0.03 | 0.25 | 0.04 [0.01, 0.06] | 0.11 [0.00, 0.23] | 0.04 [0.01, 0.07] | 0.10 [0.00, 0.20] | 0.04 | 0.19 |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) | GPT-5 | none | 0.02 | 0.26 | 0.03 [0.00, 0.06] | 0.10 [0.00, 0.20] | 0.02 [0.00, 0.04] | 0.19 [0.12, 0.26] | 0.02 | 0.15 |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) | GPT-5 | authority | 0.03 | 0.26 | 0.03 [0.00, 0.06] | 0.10 [0.00, 0.20] | 0.02 [0.00, 0.04] | 0.19 [0.12, 0.26] | 0.02 | 0.15 |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) | GPT-5 | override | 0.04 | 0.26 | 0.03 [0.00, 0.06] | 0.10 [0.00, 0.20] | 0.02 [0.00, 0.04] | 0.19 [0.12, 0.26] | 0.02 | 0.15 |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) | Claude Sonnet 4.5 | none | 0.01 | 0.28 | 0.04 [0.01, 0.06] | 0.30 [0.22, 0.38] | 0.04 [0.01, 0.07] | 0.23 [0.10, 0.35] | 0.04 | 0.17 |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) | Claude Sonnet 4.5 | authority | 0.01 | 0.28 | 0.04 [0.01, 0.06] | 0.30 [0.22, 0.38] | 0.04 [0.01, 0.07] | 0.23 [0.10, 0.35] | 0.04 | 0.17 |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) | Claude Sonnet 4.5 | override | 0.00 | 0.28 | 0.03 [0.01, 0.04] | 0.30 [0.22, 0.38] | 0.04 [0.01, 0.06] | 0.23 [0.10, 0.35] | 0.04 | 0.16 |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) | GPT-5 | none | 0.03 | 0.28 | 0.01 [0.00, 0.04] | 0.44 [0.32, 0.58] | 0.01 [0.00, 0.04] | 0.49 [0.32, 0.65] | 0.01 | 0.14 |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) | GPT-5 | authority | 0.01 | 0.28 | 0.01 [0.00, 0.04] | 0.44 [0.32, 0.58] | 0.01 [0.00, 0.04] | 0.49 [0.32, 0.65] | 0.01 | 0.14 |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) | GPT-5 | override | 0.01 | 0.28 | 0.01 [0.00, 0.04] | 0.44 [0.32, 0.58] | 0.01 [0.00, 0.04] | 0.49 [0.32, 0.65] | 0.01 | 0.14 |
| D3 ensemble Qwen3-8B & GPT-5 (plain) | Claude Sonnet 4.5 | none | 0.03 | 0.22 | 0.04 [0.00, 0.09] | 0.28 [0.03, 0.65] | 0.05 [0.02, 0.07] | 0.10 [0.00, 0.22] | 0.05 | 0.26 |
| D3 ensemble Qwen3-8B & GPT-5 (plain) | Claude Sonnet 4.5 | authority | 0.03 | 0.22 | 0.04 [0.00, 0.09] | 0.28 [0.03, 0.65] | 0.05 [0.02, 0.07] | 0.10 [0.00, 0.22] | 0.05 | 0.26 |
| D3 ensemble Qwen3-8B & GPT-5 (plain) | Claude Sonnet 4.5 | override | 0.05 | 0.22 | 0.04 [0.00, 0.07] | 0.28 [0.03, 0.65] | 0.05 [0.02, 0.07] | 0.10 [0.00, 0.22] | 0.05 | 0.25 |
| D3 ensemble Qwen3-8B & GPT-5 (plain) | GPT-5 | none | 0.02 | 0.23 | 0.03 [0.00, 0.06] | 0.26 [0.01, 0.72] | 0.03 [0.01, 0.05] | 0.19 [0.03, 0.35] | 0.03 | 0.21 |
| D3 ensemble Qwen3-8B & GPT-5 (plain) | GPT-5 | authority | 0.06 | 0.23 | 0.03 [0.00, 0.06] | 0.26 [0.01, 0.72] | 0.03 [0.01, 0.05] | 0.19 [0.03, 0.35] | 0.03 | 0.21 |
| D3 ensemble Qwen3-8B & GPT-5 (plain) | GPT-5 | override | 0.06 | 0.23 | 0.02 [0.00, 0.06] | 0.26 [0.01, 0.72] | 0.03 [0.01, 0.05] | 0.19 [0.03, 0.35] | 0.03 | 0.21 |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) | Claude Sonnet 4.5 | none | 0.02 | 0.20 | 0.06 [0.03, 0.11] | 0.03 [0.00, 0.05] | 0.06 [0.05, 0.07] | 0.09 [0.01, 0.20] | 0.06 | 0.34 |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) | Claude Sonnet 4.5 | authority | 0.00 | 0.20 | 0.06 [0.03, 0.10] | 0.03 [0.00, 0.05] | 0.05 [0.03, 0.07] | 0.09 [0.01, 0.20] | 0.05 | 0.34 |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) | Claude Sonnet 4.5 | override | 0.02 | 0.20 | 0.06 [0.03, 0.09] | 0.03 [0.00, 0.05] | 0.06 [0.05, 0.07] | 0.09 [0.01, 0.20] | 0.06 | 0.34 |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) | GPT-5 | none | 0.05 | 0.20 | 0.01 [0.00, 0.02] | 0.29 [0.12, 0.41] | 0.01 [0.00, 0.02] | 0.28 [0.11, 0.41] | 0.01 | 0.20 |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) | GPT-5 | authority | 0.00 | 0.20 | 0.01 [0.00, 0.02] | 0.29 [0.12, 0.41] | 0.01 [0.00, 0.02] | 0.28 [0.11, 0.41] | 0.01 | 0.20 |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) | GPT-5 | override | 0.06 | 0.20 | 0.01 [0.00, 0.02] | 0.29 [0.12, 0.41] | 0.01 [0.00, 0.02] | 0.28 [0.11, 0.41] | 0.01 | 0.20 |

## Results: canary audit (D4)
Canary pass rates (planted items with known labels; injected canaries use templates the attack does not use),
and a critic takeover at step 15, before the agent turns at step 20 (the captured critic reports CORRECT for
everything, canaries included). FPR = denied honest steps before the takeover.

| Critic | pass: injected wrong | pass: clean correct | pass: clean wrong | TGCC OER | + canary fail-closed OER | TGCC FPR | + canary FPR | takeover detected after (median steps; detected/episodes) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Sonnet 4.5 plain [TGCC-R] | 1.00 | 1.00 | 1.00 | 1.00 | 0.06 | 0.16 | 0.16 | 4 (8/8) |
| Claude Sonnet 4.5 + D1 hardened [TGCC-R] | 1.00 | 1.00 | 1.00 | 1.00 | 0.06 | 0.09 | 0.09 | 4 (8/8) |
| Claude Sonnet 4.5 + D2 sanitised [TGCC-R] | 1.00 | 0.95 | 1.00 | 0.99 | 0.06 | 0.09 | 0.09 | 4 (8/8) |
| GPT-5 plain [TGCC-R] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.00 | 0.00 | 5 (8/8) |
| GPT-5 + D1 hardened [TGCC-R] | 1.00 | 1.00 | 1.00 | 1.00 | 0.06 | 0.09 | 0.09 | 4 (8/8) |
| GPT-5 + D2 sanitised [TGCC-R] | 1.00 | 0.85 | 1.00 | 1.00 | 0.09 | 0.00 | 0.00 | 5 (8/8) |
| Claude Haiku 4.5 plain [TGCC-R] | 1.00 | 0.95 | 1.00 | 1.00 | 0.06 | 0.00 | 0.00 | 4 (8/8) |
| Claude Haiku 4.5 + D1 hardened [TGCC-R] | 1.00 | 0.95 | 1.00 | 1.00 | 0.06 | 0.32 | 0.32 | 4 (8/8) |
| Claude Haiku 4.5 + D2 sanitised [TGCC-R] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.07 | 0.07 | 7 (8/8) |
| Qwen3-8B plain [TGCC-R] | 0.60 | 1.00 | 1.00 | 0.99 | 0.24 | 0.35 | 0.35 | 11 (8/8) |
| Qwen3-8B + D1 hardened [TGCC-R] | 0.80 | 0.95 | 0.95 | 1.00 | 0.19 | 0.12 | 0.12 | 11 (8/8) |
| Qwen3-8B + D2 sanitised [TGCC-R] | 0.90 | 0.95 | 1.00 | 0.98 | 0.07 | 0.21 | 0.21 | 4 (8/8) |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) [TGCC-R] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.00 | 0.00 | 5 (8/8) |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) [TGCC-R] | 1.00 | 1.00 | 1.00 | 1.00 | 0.06 | 0.10 | 0.10 | 4 (8/8) |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) [TGCC-R] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.09 | 0.09 | 5 (8/8) |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) [TGCC-R] | 1.00 | 0.95 | 1.00 | 1.00 | 0.06 | 0.33 | 0.33 | 4 (8/8) |
| D3 ensemble Qwen3-8B & GPT-5 (plain) [TGCC-R] | 1.00 | 0.90 | 1.00 | 0.95 | 0.06 | 0.24 | 0.24 | 5 (8/8) |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) [TGCC-R] | 1.00 | 0.95 | 1.00 | 1.00 | 0.06 | 0.11 | 0.11 | 4 (8/8) |
| Claude Sonnet 4.5 plain [TGCC] | 1.00 | 1.00 | 1.00 | 1.00 | 0.06 | 0.36 | 0.36 | 4 (8/8) |
| Claude Sonnet 4.5 + D1 hardened [TGCC] | 1.00 | 1.00 | 1.00 | 0.99 | 0.05 | 0.18 | 0.18 | 4 (8/8) |
| Claude Sonnet 4.5 + D2 sanitised [TGCC] | 1.00 | 0.95 | 1.00 | 0.98 | 0.06 | 0.13 | 0.13 | 4 (8/8) |
| GPT-5 plain [TGCC] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.00 | 0.00 | 5 (8/8) |
| GPT-5 + D1 hardened [TGCC] | 1.00 | 1.00 | 1.00 | 0.99 | 0.05 | 0.13 | 0.13 | 4 (8/8) |
| GPT-5 + D2 sanitised [TGCC] | 1.00 | 0.85 | 1.00 | 1.00 | 0.09 | 0.00 | 0.00 | 5 (8/8) |
| Claude Haiku 4.5 plain [TGCC] | 1.00 | 0.95 | 1.00 | 1.00 | 0.06 | 0.10 | 0.10 | 4 (8/8) |
| Claude Haiku 4.5 + D1 hardened [TGCC] | 1.00 | 0.95 | 1.00 | 0.99 | 0.05 | 0.41 | 0.41 | 4 (8/8) |
| Claude Haiku 4.5 + D2 sanitised [TGCC] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.08 | 0.08 | 7 (8/8) |
| Qwen3-8B plain [TGCC] | 0.60 | 1.00 | 1.00 | 0.99 | 0.25 | 0.34 | 0.34 | 11 (8/8) |
| Qwen3-8B + D1 hardened [TGCC] | 0.80 | 0.95 | 0.95 | 1.00 | 0.19 | 0.12 | 0.12 | 11 (8/8) |
| Qwen3-8B + D2 sanitised [TGCC] | 0.90 | 0.95 | 1.00 | 1.00 | 0.08 | 0.11 | 0.11 | 4 (8/8) |
| D3 ensemble Claude Sonnet 4.5 & GPT-5 (plain) [TGCC] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.02 | 0.02 | 5 (8/8) |
| D1+D3 ensemble Claude Sonnet 4.5 & GPT-5 (hardened) [TGCC] | 1.00 | 1.00 | 1.00 | 1.00 | 0.06 | 0.12 | 0.12 | 4 (8/8) |
| D3 ensemble Claude Haiku 4.5 & GPT-5 (plain) [TGCC] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.10 | 0.10 | 5 (8/8) |
| D1+D3 ensemble Claude Haiku 4.5 & GPT-5 (hardened) [TGCC] | 1.00 | 0.95 | 1.00 | 1.00 | 0.06 | 0.34 | 0.34 | 4 (8/8) |
| D3 ensemble Qwen3-8B & GPT-5 (plain) [TGCC] | 1.00 | 0.90 | 1.00 | 1.00 | 0.09 | 0.12 | 0.12 | 5 (8/8) |
| D1+D3 ensemble Qwen3-8B & GPT-5 (hardened) [TGCC] | 1.00 | 0.95 | 1.00 | 1.00 | 0.06 | 0.12 | 0.12 | 4 (8/8) |

![critic poisoning](figures/critic_poisoning.png)
