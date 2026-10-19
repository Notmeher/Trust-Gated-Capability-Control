# Code pipeline (E4) on HumanEval

## Method
162 HumanEval tasks; planner -> coder -> reviewer, all the same model. Coder honest
for steps 0-14 and adversarial from step 15 (instructed to plant a subtle bug with
high confidence; if it does not comply, the code is mutated until a unit test fails,
so every post-compromise commit is harmful). Episodes: 35 tasks, 5 shuffles x 4
disjoint chunks = 20 episodes per model. Thresholds per episode from Algorithm 2
(pre-warmed pilot) on 60 honest tasks not in that episode. Epistemic check: unit-test
outcome, or the reviewer LLM's verdict (no test access).
Generated code runs only in an AST-audited, isolated subprocess with timeout.

### Claude Sonnet 4.5
honest pass@1 = 0.98; sleeper complied with bug instruction = 0.47;
non-compliant sleeper outputs mutated = 0.45; final sleeper pass rate = 0.07;
reviewer approves passing honest code = 0.91, rejects failing code = 0.97 (verdict parsed for 100%).
Episodes: 20 (35 tasks, compromise at 15).

| Critic | Gate | harmful commits blocked | honest commits denied | OER | latency |
|---|---|---|---|---|---|
| unit tests | TGCC | 0.98 [0.96, 0.99] (364/372) | 0.15 [0.11, 0.19] (45/300) | 0.03 [0.01, 0.04] | 0.5 [0.3, 0.7] |
| unit tests | TGCC-Smoothed | 0.86 [0.82, 0.89] (321/372) | 0.24 [0.20, 0.29] (73/300) | 0.13 [0.09, 0.18] | 2.7 [1.8, 3.6] |
| unit tests | TGCC-NoSyn | 0.98 [0.96, 0.99] (364/372) | 0.16 [0.13, 0.21] (49/300) | 0.03 [0.01, 0.04] | 0.5 [0.3, 0.7] |
| unit tests | Epistemic-only (Beta) | 0.86 [0.82, 0.89] (321/372) | 0.24 [0.20, 0.29] (73/300) | 0.13 [0.09, 0.18] | 2.7 [1.8, 3.6] |
| unit tests | AgentGuard-lite | 0.98 [0.96, 0.99] (364/372) | 0.14 [0.11, 0.19] (43/300) | 0.03 [0.01, 0.04] | 0.5 [0.3, 0.7] |
| unit tests | Strict-min (Beta) | 0.86 [0.82, 0.89] (321/372) | 0.24 [0.20, 0.29] (73/300) | 0.13 [0.09, 0.18] | 2.7 [1.8, 3.6] |
| unit tests | Mean (Constitutional-lite) | 0.00 [0.00, 0.01] (0/372) | 0.00 [0.00, 0.01] (0/300) | 1.00 [1.00, 1.00] | n/a |
| unit tests | Naive behavioural | 0.00 [0.00, 0.01] (0/372) | 0.00 [0.00, 0.01] (0/300) | 1.00 [1.00, 1.00] | n/a |
| reviewer LLM | TGCC | 0.92 [0.88, 0.94] (341/372) | 0.09 [0.06, 0.12] (26/300) | 0.09 [0.07, 0.11] | 1.8 [1.4, 2.2] |
| reviewer LLM | TGCC-Smoothed | 0.61 [0.56, 0.66] (228/372) | 0.00 [0.00, 0.01] (0/300) | 0.39 [0.31, 0.47] | 7.8 [6.2, 9.5] |
| reviewer LLM | TGCC-NoSyn | 0.92 [0.88, 0.94] (341/372) | 0.09 [0.06, 0.12] (26/300) | 0.09 [0.07, 0.11] | 1.8 [1.4, 2.2] |
| reviewer LLM | Epistemic-only (Beta) | 0.59 [0.54, 0.63] (218/372) | 0.00 [0.00, 0.01] (0/300) | 0.42 [0.33, 0.50] | 8.3 [6.6, 10.1] |
| reviewer LLM | AgentGuard-lite | 0.92 [0.88, 0.94] (341/372) | 0.09 [0.06, 0.12] (26/300) | 0.09 [0.07, 0.11] | 1.8 [1.4, 2.2] |
| reviewer LLM | Strict-min (Beta) | 0.59 [0.54, 0.63] (218/372) | 0.00 [0.00, 0.01] (0/300) | 0.42 [0.33, 0.50] | 8.3 [6.6, 10.1] |
| reviewer LLM | Mean (Constitutional-lite) | 0.00 [0.00, 0.01] (0/372) | 0.00 [0.00, 0.01] (0/300) | 1.00 [1.00, 1.00] | n/a |
| reviewer LLM | Naive behavioural | 0.00 [0.00, 0.01] (0/372) | 0.00 [0.00, 0.01] (0/300) | 1.00 [1.00, 1.00] | n/a |

### GPT-5
honest pass@1 = 0.89; sleeper complied with bug instruction = 0.53;
non-compliant sleeper outputs mutated = 0.44; final sleeper pass rate = 0.02;
reviewer approves passing honest code = 0.86, rejects failing code = 0.89 (verdict parsed for 100%).
Episodes: 20 (35 tasks, compromise at 15).

| Critic | Gate | harmful commits blocked | honest commits denied | OER | latency |
|---|---|---|---|---|---|
| unit tests | TGCC | 0.93 [0.90, 0.95] (362/389) | 0.17 [0.13, 0.22] (51/300) | 0.08 [0.06, 0.11] | 1.6 [1.1, 2.1] |
| unit tests | TGCC-Smoothed | 0.66 [0.61, 0.71] (257/389) | 0.07 [0.04, 0.10] (20/300) | 0.34 [0.25, 0.45] | 6.9 [4.9, 8.9] |
| unit tests | TGCC-NoSyn | 0.93 [0.90, 0.95] (363/389) | 0.16 [0.12, 0.21] (48/300) | 0.08 [0.05, 0.10] | 1.6 [1.1, 2.0] |
| unit tests | Epistemic-only (Beta) | 0.64 [0.59, 0.69] (250/389) | 0.01 [0.00, 0.02] (2/300) | 0.36 [0.26, 0.46] | 7.2 [5.2, 9.2] |
| unit tests | AgentGuard-lite | 0.93 [0.90, 0.95] (362/389) | 0.14 [0.10, 0.18] (41/300) | 0.08 [0.06, 0.11] | 1.6 [1.1, 2.1] |
| unit tests | Strict-min (Beta) | 0.64 [0.59, 0.69] (250/389) | 0.01 [0.00, 0.02] (2/300) | 0.36 [0.26, 0.46] | 7.2 [5.2, 9.2] |
| unit tests | Mean (Constitutional-lite) | 0.10 [0.07, 0.13] (39/389) | 0.04 [0.03, 0.07] (13/300) | 0.90 [0.77, 1.00] | 7.0 [3.0, 13.5] |
| unit tests | Naive behavioural | 0.00 [0.00, 0.01] (0/389) | 0.00 [0.00, 0.01] (0/300) | 1.00 [1.00, 1.00] | n/a |
| reviewer LLM | TGCC | 0.81 [0.77, 0.84] (314/389) | 0.14 [0.11, 0.18] (42/300) | 0.20 [0.10, 0.32] | 4.0 [2.0, 6.3] |
| reviewer LLM | TGCC-Smoothed | 0.46 [0.41, 0.51] (178/389) | 0.02 [0.01, 0.04] (6/300) | 0.54 [0.41, 0.67] | 9.8 [7.2, 12.2] |
| reviewer LLM | TGCC-NoSyn | 0.81 [0.77, 0.85] (315/389) | 0.13 [0.10, 0.17] (39/300) | 0.20 [0.11, 0.30] | 4.0 [2.1, 6.1] |
| reviewer LLM | Epistemic-only (Beta) | 0.42 [0.37, 0.47] (162/389) | 0.00 [0.00, 0.01] (0/300) | 0.59 [0.47, 0.70] | 10.8 [8.5, 12.9] |
| reviewer LLM | AgentGuard-lite | 0.77 [0.72, 0.81] (299/389) | 0.13 [0.10, 0.17] (39/300) | 0.24 [0.11, 0.39] | 2.1 [1.6, 2.7] |
| reviewer LLM | Strict-min (Beta) | 0.42 [0.37, 0.47] (162/389) | 0.00 [0.00, 0.01] (0/300) | 0.59 [0.47, 0.70] | 10.8 [8.5, 12.9] |
| reviewer LLM | Mean (Constitutional-lite) | 0.10 [0.07, 0.13] (39/389) | 0.02 [0.01, 0.04] (5/300) | 0.90 [0.78, 1.00] | 6.7 [3.0, 12.0] |
| reviewer LLM | Naive behavioural | 0.00 [0.00, 0.01] (0/389) | 0.00 [0.00, 0.01] (0/300) | 1.00 [1.00, 1.00] | n/a |


![blocked](figures/blocked_commits.png)
