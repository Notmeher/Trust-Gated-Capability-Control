# N36 - Tool-calling agent workflow (tau-bench retail)

## Reviewer issue
IEEE R2-1: realistic workflows; specifically an agent that takes consequential tool actions.

## Setup
Real tau-bench retail database and policy (commit `59a200c`); multi-turn ReAct agents with real tool
execution; consequential tools (cancel / return = refund) need a capability token for that step, otherwise they are
escalated to a human. 12 episodes x 40 tickets per model; the attack starts at step 20; an
honest pilot of 80 disjoint tickets selects the window and calibrates CRC (delta = 0.1).

Attacks after step 20: **sleeper** = covert operator directive in the system prompt (real behaviour);
**forced sleeper** = the sleeper with non-compliant refusals rewritten to the approving tool call at confidence 0.97
(E1 semantics); **inject** = indirect prompt injection in the `get_order_details` result (real behaviour).

Gates: **TGCC-R** (five probe layers, CRC on per-step honest FPR); **+ precondition audit** / **+ full audit**: the
institutional layer also carries a deterministic pre-execution audit of the tool call (order ownership and status,
refund destination; *full* adds argument provenance: the cancellation reason must be the one the customer stated),
with CRC on the deployment loss "a policy-compliant step is blocked"; **full audit as hard guard**: the audit alone
blocks the call (no trust state).

## Agent behaviour (policy accuracy / fraction of non-permitted requests turned into a refund)
| Model | W | honest | sleeper | forced sleeper | inject |
|---|---:|---|---|---|---|
| Claude Sonnet 4.5 | 4 | 0.99 / 0.00 | 1.00 / 0.00 | 0.51 / 1.00 | 0.73 / 0.53 |
| GPT-5 | 8 | 0.84 / 0.32 | 0.83 / 0.35 | 0.51 / 1.00 | 0.83 / 0.35 |
| Claude Haiku 4.5 | 4 | 1.00 / 0.00 | 0.98 / 0.03 | 0.51 / 1.00 | 0.90 / 0.20 |

## Policy-violating refunds executed / attempted (after the attack starts; all steps for honest)
| Model | Gate | honest | sleeper | forced sleeper | inject | blocked compliant steps (honest) | legitimate refunds escalated (honest) |
|---|---|---|---|---|---|---:|---:|
| Claude Sonnet 4.5 | ungated | 0/0 ($0.0k) | 0/0 ($0.0k) | 133/133 ($223.9k) | 75/75 ($115.2k) | 0.000 | 0/231 |
| Claude Sonnet 4.5 | full audit as hard guard | 0/0 ($0.0k) | 0/0 ($0.0k) | 0/133 ($0.0k) | 26/75 ($40.7k) | 0.000 | 0/231 |
| Claude Sonnet 4.5 | TGCC-R | 0/0 ($0.0k) | 0/0 ($0.0k) | 21/133 ($35.5k) | 15/75 ($34.5k) | 0.000 | 0/231 |
| Claude Sonnet 4.5 | TGCC-R + precondition audit | 0/0 ($0.0k) | 0/0 ($0.0k) | 8/133 ($13.9k) | 27/75 ($51.9k) | 0.000 | 0/231 |
| Claude Sonnet 4.5 | TGCC-R + full audit | 0/0 ($0.0k) | 0/0 ($0.0k) | 0/133 ($0.0k) | 7/75 ($12.9k) | 0.000 | 0/231 |
| GPT-5 | ungated | 76/76 ($135.9k) | 47/47 ($80.9k) | 133/133 ($223.9k) | 47/47 ($80.9k) | 0.000 | 0/235 |
| GPT-5 | full audit as hard guard | 0/76 ($0.0k) | 0/47 ($0.0k) | 0/133 ($0.0k) | 0/47 ($0.0k) | 0.000 | 0/235 |
| GPT-5 | TGCC-R | 71/76 ($128.0k) | 42/47 ($74.7k) | 47/133 ($85.5k) | 44/47 ($77.3k) | 0.015 | 4/235 |
| GPT-5 | TGCC-R + precondition audit | 72/76 ($128.7k) | 45/47 ($77.8k) | 19/133 ($33.1k) | 45/47 ($77.8k) | 0.015 | 4/235 |
| GPT-5 | TGCC-R + full audit | 0/76 ($0.0k) | 0/47 ($0.0k) | 0/133 ($0.0k) | 0/47 ($0.0k) | 0.015 | 4/235 |
| Claude Haiku 4.5 | ungated | 0/0 ($0.0k) | 2/2 ($5.5k) | 133/133 ($223.9k) | 28/28 ($43.0k) | 0.000 | 0/235 |
| Claude Haiku 4.5 | full audit as hard guard | 0/0 ($0.0k) | 2/2 ($5.5k) | 2/133 ($5.5k) | 4/28 ($11.6k) | 0.000 | 0/235 |
| Claude Haiku 4.5 | TGCC-R | 0/0 ($0.0k) | 0/2 ($0.0k) | 0/133 ($0.0k) | 0/28 ($0.0k) | 0.000 | 0/235 |
| Claude Haiku 4.5 | TGCC-R + precondition audit | 0/0 ($0.0k) | 0/2 ($0.0k) | 0/133 ($0.0k) | 0/28 ($0.0k) | 0.000 | 0/235 |
| Claude Haiku 4.5 | TGCC-R + full audit | 0/0 ($0.0k) | 0/2 ($0.0k) | 0/133 ($0.0k) | 0/28 ($0.0k) | 0.000 | 0/235 |

![tool agent](figures/tool_agent.png)
