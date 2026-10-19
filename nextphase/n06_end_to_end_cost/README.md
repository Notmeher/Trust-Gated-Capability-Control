# End-to-end cost of obtaining trust signals

The controller step costs microseconds; the dominant cost is the critic. With a
reference-based check (string match, unit tests) the overhead over the agent call is
negligible. A reference-free LLM-judge critic adds a second LLM call per step
(latency and token overhead below), roughly doubling per-step cost.

### Claude Sonnet 4.5
| Component | Latency | Tokens |
|---|---|---|
| agent LLM call | 1450 ms (p90 1891) | 120 in / 21 out |
| LLM judge call (Claude Sonnet 4.5) | 1270 ms (p90 1779) | 108 in / 20 out |
| LLM judge call (GPT-5) | 2013 ms (p90 2721) | 102 in / 22 out |
| alias-match critic | 23.0 us | 0 |
| 4 heuristic probes | 36.4 us | 0 |
| TGCC controller step | 90.4 us | 0 |

End-to-end per agent step (median agent call + critic + probes + controller):

| Quantity | Value |
|---|---|
| reference_critic_ms | 1449.8 ms |
| llm_judge_Claude Sonnet 4.5_ms | 2719.6 ms |
| token_overhead_Claude Sonnet 4.5 | 0.9 |
| llm_judge_GPT-5_ms | 3463.2 ms |
| token_overhead_GPT-5 | 0.9 |

Code pipeline: planner 3486 ms, coder 4466 ms, reviewer 1209 ms (medians); unit-test critic runs in a subprocess (~50-100 ms).

### GPT-5
| Component | Latency | Tokens |
|---|---|---|
| agent LLM call | 1909 ms (p90 2600) | 111 in / 22 out |
| LLM judge call (Claude Sonnet 4.5) | 1393 ms (p90 1970) | 106 in / 22 out |
| LLM judge call (GPT-5) | 1991 ms (p90 2736) | 100 in / 22 out |
| alias-match critic | 46.1 us | 0 |
| 4 heuristic probes | 35.0 us | 0 |
| TGCC controller step | 80.9 us | 0 |

End-to-end per agent step (median agent call + critic + probes + controller):

| Quantity | Value |
|---|---|
| reference_critic_ms | 1909.6 ms |
| llm_judge_Claude Sonnet 4.5_ms | 3302.5 ms |
| token_overhead_Claude Sonnet 4.5 | 1.0 |
| llm_judge_GPT-5_ms | 3900.2 ms |
| token_overhead_GPT-5 | 0.9 |

Code pipeline: planner 2838 ms, coder 3845 ms, reviewer 1869 ms (medians); unit-test critic runs in a subprocess (~50-100 ms).

