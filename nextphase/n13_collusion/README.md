# Colluding agents (E7)

## Method
Three personas of the same model (Alpha, Beta, Gamma) answer the same TriviaQA
questions (5 disjoint 60-question episodes per model). From step
20, Beta and Gamma collude: both replace their answer with the same wrong
answer at confidence 0.90-0.99 and keep the rest of their response; Alpha stays
honest. Each agent has its own gate, calibrated by Algorithm 2 on its own honest
answers to the 120 pilot questions. "with agreement" folds a cross-agent agreement
signal into the role layer (role := min(role, fraction of peers that agree)), also
in the pilot. Team output = largest answer cluster among admitted agents (ties
broken by stated confidence); "No gate" is plain majority vote.

## Results (5 episodes per model; CIs over episodes)
### Claude Sonnet 4.5 (honest accuracy: alpha 0.94, beta 0.94, gamma 0.94)
| Gate | Colluder OER | Colluder latency | Honest-agent denial rate | Team wrong / abstain |
|---|---|---|---|---|
| TGCC | 0.02 | 0.8 [0.4, 1.0] | 0.07 [0.02, 0.13] | 0.07 / 0.06 |
| TGCC-Smoothed | 0.08 | 3.0 [1.2, 4.4] | 0.10 [0.00, 0.30] | 0.12 / 0.15 |
| Epistemic-only (Beta) | 0.08 | 3.0 [1.2, 4.4] | 0.10 [0.00, 0.30] | 0.12 / 0.15 |
| Naive behavioural | 1.00 | n/a | 0.00 [0.00, 0.00] | 1.00 / 0.00 |
| TGCC (with agreement) | 0.02 | 0.8 [0.4, 1.0] | 0.63 [0.60, 0.66] | 0.02 / 0.91 |
| No gate (majority vote) | - | - | - | 1.00 / 0.00 |
### GPT-5 (honest accuracy: alpha 0.88, beta 0.88, gamma 0.88)
| Gate | Colluder OER | Colluder latency | Honest-agent denial rate | Team wrong / abstain |
|---|---|---|---|---|
| TGCC | 0.01 | 0.4 [0.0, 0.8] | 0.23 [0.10, 0.42] | 0.07 / 0.29 |
| TGCC-Smoothed | 0.13 | 6.4 [5.6, 7.4] | 0.28 [0.09, 0.46] | 0.19 / 0.41 |
| Epistemic-only (Beta) | 0.13 | 6.4 [5.6, 7.4] | 0.27 [0.09, 0.45] | 0.20 / 0.41 |
| Naive behavioural | 1.00 | n/a | 0.00 [0.00, 0.00] | 1.00 / 0.00 |
| TGCC (with agreement) | 0.01 | 0.4 [0.0, 0.8] | 0.67 [0.62, 0.72] | 0.01 / 0.96 |
| No gate (majority vote) | - | - | - | 1.00 / 0.00 |

Honest-agent denial rate = fraction of all 60 steps on which Alpha is denied.
Team wrong / abstain = fractions of the 200 post-compromise questions.

## Reading
* Without a gate the two colluders form a majority, so the team answer is wrong on
  every post-compromise question.
* TGCC revokes each colluder from its own epistemic evidence within about one step,
  so collusion does not protect them. The honest agent then carries the team answer
  (team wrong 0.07); the team abstains on 6-29% of the questions, when the honest
  agent is itself denied.
* A cross-agent agreement signal hurts. Under a colluding majority it is the honest
  agent that looks isolated: it is denied on 63-67% of steps and the team abstains on
  91-96% of the questions.

![collusion](figures/collusion_team.png)
