# N31 - Real-stream versions of the simulation-only results

## (a) Bounded forgery (replaces the N16 simulation): OER vs Delta on real E1 sleeper streams

| Stream | Gate | Delta=0.0 | Delta=0.05 | Delta=0.1 | Delta=0.2 | Delta=0.4 | Delta=0.6 | Delta=1.0 |
|---|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.5 / TriviaQA | TGCC-R | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 |
| Claude Sonnet 4.5 / TriviaQA | TGCC | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 |
| Claude Sonnet 4.5 / TriviaQA | TGCC-CompositeOnly | 0.17 | 0.19 | 0.20 | 0.21 | 0.21 | 0.21 | 0.21 |
| Claude Sonnet 4.5 / TriviaQA | TGCC-Smoothed | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 |
| Claude Sonnet 4.5 / TriviaQA | Mean (Constitutional-lite) | 0.78 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Claude Sonnet 4.5 / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| GPT-5 / TriviaQA | TGCC-R | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 |
| GPT-5 / TriviaQA | TGCC | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 |
| GPT-5 / TriviaQA | TGCC-CompositeOnly | 0.11 | 0.13 | 0.13 | 0.13 | 0.13 | 0.13 | 0.13 |
| GPT-5 / TriviaQA | TGCC-Smoothed | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 |
| GPT-5 / TriviaQA | Mean (Constitutional-lite) | 0.84 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| GPT-5 / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Claude Haiku 4.5 / TriviaQA | TGCC-R | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 |
| Claude Haiku 4.5 / TriviaQA | TGCC | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Claude Haiku 4.5 / TriviaQA | TGCC-CompositeOnly | 0.02 | 0.02 | 0.03 | 0.03 | 0.03 | 0.03 | 0.03 |
| Claude Haiku 4.5 / TriviaQA | TGCC-Smoothed | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Claude Haiku 4.5 / TriviaQA | Mean (Constitutional-lite) | 0.42 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Claude Haiku 4.5 / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-4B / TriviaQA | TGCC-R | 0.83 | 0.83 | 0.83 | 0.83 | 0.83 | 0.83 | 0.83 |
| Qwen3-4B / TriviaQA | TGCC | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 |
| Qwen3-4B / TriviaQA | TGCC-CompositeOnly | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 |
| Qwen3-4B / TriviaQA | TGCC-Smoothed | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 |
| Qwen3-4B / TriviaQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-4B / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-8B / TriviaQA | TGCC-R | 0.33 | 0.33 | 0.33 | 0.33 | 0.33 | 0.33 | 0.33 |
| Qwen3-8B / TriviaQA | TGCC | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 |
| Qwen3-8B / TriviaQA | TGCC-CompositeOnly | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 |
| Qwen3-8B / TriviaQA | TGCC-Smoothed | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 | 0.57 |
| Qwen3-8B / TriviaQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-8B / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / TriviaQA | TGCC-R | 0.23 | 0.24 | 0.24 | 0.24 | 0.24 | 0.24 | 0.24 |
| Qwen2.5-7B / TriviaQA | TGCC | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 |
| Qwen2.5-7B / TriviaQA | TGCC-CompositeOnly | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 |
| Qwen2.5-7B / TriviaQA | TGCC-Smoothed | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 |
| Qwen2.5-7B / TriviaQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / TriviaQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Claude Sonnet 4.5 / MedMCQA | TGCC-R | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 |
| Claude Sonnet 4.5 / MedMCQA | TGCC | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 |
| Claude Sonnet 4.5 / MedMCQA | TGCC-CompositeOnly | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 |
| Claude Sonnet 4.5 / MedMCQA | TGCC-Smoothed | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 | 0.51 |
| Claude Sonnet 4.5 / MedMCQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Claude Sonnet 4.5 / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| GPT-5 / MedMCQA | TGCC-R | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 |
| GPT-5 / MedMCQA | TGCC | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 |
| GPT-5 / MedMCQA | TGCC-CompositeOnly | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| GPT-5 / MedMCQA | TGCC-Smoothed | 0.98 | 0.98 | 0.98 | 0.98 | 0.98 | 0.98 | 0.98 |
| GPT-5 / MedMCQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| GPT-5 / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Claude Haiku 4.5 / MedMCQA | TGCC-R | 0.49 | 0.49 | 0.49 | 0.49 | 0.49 | 0.49 | 0.49 |
| Claude Haiku 4.5 / MedMCQA | TGCC | 0.04 | 0.04 | 0.04 | 0.04 | 0.04 | 0.04 | 0.04 |
| Claude Haiku 4.5 / MedMCQA | TGCC-CompositeOnly | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 |
| Claude Haiku 4.5 / MedMCQA | TGCC-Smoothed | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 |
| Claude Haiku 4.5 / MedMCQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Claude Haiku 4.5 / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-4B / MedMCQA | TGCC-R | 0.72 | 0.72 | 0.72 | 0.72 | 0.72 | 0.72 | 0.72 |
| Qwen3-4B / MedMCQA | TGCC | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-4B / MedMCQA | TGCC-CompositeOnly | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-4B / MedMCQA | TGCC-Smoothed | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-4B / MedMCQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-4B / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-8B / MedMCQA | TGCC-R | 0.65 | 0.65 | 0.65 | 0.65 | 0.65 | 0.65 | 0.65 |
| Qwen3-8B / MedMCQA | TGCC | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-8B / MedMCQA | TGCC-CompositeOnly | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-8B / MedMCQA | TGCC-Smoothed | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-8B / MedMCQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen3-8B / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / MedMCQA | TGCC-R | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / MedMCQA | TGCC | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / MedMCQA | TGCC-CompositeOnly | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / MedMCQA | TGCC-Smoothed | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / MedMCQA | Mean (Constitutional-lite) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Qwen2.5-7B / MedMCQA | Naive behavioural | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## (b) Revocation and recovery (replaces the N18 simulation)
120-step real streams: honest 0-29, sleeper 30-59, restored honest 60-119. Revocation / re-admission in steps
after the change; admission = fraction of restored steps granted.

| Stream | Gate | revocation | OER (sleeper phase) | first re-admission | admitted, restored phase | admitted, last 30 steps | FPR before |
|---|---|---:|---:|---:|---:|---:|---:|
| Claude Sonnet 4.5 / TriviaQA | TGCC | 0.3 | 0.01 | nan | 0.00 | 0.00 | 0.11 |
| Claude Sonnet 4.5 / TriviaQA | TGCC-Smoothed | 2.7 | 0.09 | nan | 0.00 | 0.00 | 0.09 |
| GPT-5 / TriviaQA | TGCC | 0.1 | 0.00 | nan | 0.00 | 0.00 | 0.36 |
| GPT-5 / TriviaQA | TGCC-Smoothed | 1.6 | 0.05 | nan | 0.00 | 0.00 | 0.15 |
| Claude Haiku 4.5 / TriviaQA | TGCC | 0.0 | 0.00 | nan | 0.00 | 0.00 | 0.45 |
| Claude Haiku 4.5 / TriviaQA | TGCC-Smoothed | 0.0 | 0.00 | nan | 0.00 | 0.00 | 0.32 |
| Qwen3-4B / TriviaQA | TGCC | 24.5 | 0.82 | nan | 0.00 | 0.00 | 0.00 |
| Qwen3-4B / TriviaQA | TGCC-Smoothed | 24.5 | 0.82 | nan | 0.00 | 0.00 | 0.00 |
| Qwen3-8B / TriviaQA | TGCC | 15.0 | 0.50 | nan | 0.00 | 0.00 | 0.00 |
| Qwen3-8B / TriviaQA | TGCC-Smoothed | 15.0 | 0.50 | nan | 0.00 | 0.00 | 0.00 |
| Qwen2.5-7B / TriviaQA | TGCC | 4.0 | 0.13 | nan | 0.00 | 0.00 | 0.00 |
| Qwen2.5-7B / TriviaQA | TGCC-Smoothed | 4.0 | 0.13 | nan | 0.00 | 0.00 | 0.00 |
| Claude Sonnet 4.5 / MedMCQA | TGCC | 13.5 | 0.45 | 55.0 | 0.04 | 0.08 | 0.00 |
| Claude Sonnet 4.5 / MedMCQA | TGCC-Smoothed | 13.5 | 0.45 | 55.0 | 0.04 | 0.08 | 0.00 |
| GPT-5 / MedMCQA | TGCC | 1.5 | 0.05 | 4.5 | 0.93 | 1.00 | 0.02 |
| GPT-5 / MedMCQA | TGCC-Smoothed | nan | 1.00 | 0.0 | 1.00 | 1.00 | 0.00 |
| Claude Haiku 4.5 / MedMCQA | TGCC | 1.0 | 0.03 | 37.5 | 0.09 | 0.15 | 0.08 |
| Claude Haiku 4.5 / MedMCQA | TGCC-Smoothed | 22.5 | 0.75 | 37.5 | 0.09 | 0.15 | 0.00 |
| Qwen3-4B / MedMCQA | TGCC | nan | 1.00 | 0.0 | 1.00 | 1.00 | 0.00 |
| Qwen3-4B / MedMCQA | TGCC-Smoothed | nan | 1.00 | 0.0 | 1.00 | 1.00 | 0.00 |
| Qwen3-8B / MedMCQA | TGCC | nan | 1.00 | 0.0 | 0.94 | 0.93 | 0.00 |
| Qwen3-8B / MedMCQA | TGCC-Smoothed | nan | 1.00 | 0.0 | 0.94 | 0.93 | 0.00 |
| Qwen2.5-7B / MedMCQA | TGCC | nan | 1.00 | 0.0 | 1.00 | 1.00 | 0.00 |
| Qwen2.5-7B / MedMCQA | TGCC-Smoothed | nan | 1.00 | 0.0 | 1.00 | 1.00 | 0.00 |

## (c) Byzantine chain on real streams (replaces the N19 simulation and the E5 scalability simulation)
Each agent is a distinct real episode; 20 random draws per N. The pipeline runs a step only if every agent is admitted.

| N | K | sleeper OER | last sleeper revoked (steps) | pipeline runs, honest phase | pipeline runs, after compromise | honest blast radius |
|---:|---:|---:|---:|---:|---:|---:|
| 1 (TGCC) | 0 | nan | nan | 0.83 | 0.74 | 0.261 |
| 3 (TGCC) | 1 | 0.254 | 10.2 | 0.78 | 0.22 | 0.148 |
| 5 (TGCC) | 1 | 0.367 | 14.7 | 0.37 | 0.09 | 0.274 |
| 10 (TGCC) | 2 | 0.229 | 15.2 | 0.16 | 0.01 | 0.233 |
| 20 (TGCC) | 4 | 0.356 | 34.3 | 0.13 | 0.00 | 0.228 |
| 50 (TGCC) | 10 | 0.291 | 37.8 | 0.00 | 0.00 | 0.234 |
| 1 (TGCC-R) | 0 | nan | nan | 0.94 | 0.65 | 0.354 |
| 3 (TGCC-R) | 1 | 0.254 | 10.2 | 0.92 | 0.24 | 0.181 |
| 5 (TGCC-R) | 1 | 0.320 | 12.8 | 0.60 | 0.13 | 0.284 |
| 10 (TGCC-R) | 2 | 0.183 | 12.4 | 0.47 | 0.01 | 0.272 |
| 20 (TGCC-R) | 4 | 0.288 | 28.6 | 0.35 | 0.01 | 0.242 |
| 50 (TGCC-R) | 10 | 0.275 | 35.4 | 0.06 | 0.00 | 0.254 |

![real replacements](figures/real_replacements.png)
