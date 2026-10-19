# N00 - Audit of submitted real-LLM streams and E1 number reconciliation

## Defects found in the submitted pipeline (fixed in this phase)
1. **Empty gpt-5 outputs.** gpt-5 is a reasoning model; with max_completion_tokens=200 and
   no reasoning_effort it spent the budget on hidden reasoning and returned empty text.
   Fix: reasoning_effort="minimal" (models.py). nextphase gpt-5 banks: 2 empty of 1,920.
2. **Empty answers scored correct.** answer_matches("") was True. Fix: empty never matches;
   reverse containment needs >= 3 characters (probes.py). nextphase uses a TriviaQA
   normalized-alias matcher (datasets.py).
3. **Baselines shared TGCC's thresholds** in W3/W6 (unfair to scalar baselines). Fix: every
   gate calibrated by the same Algorithm 2 on the same pilot (N03).
4. **In-sample FPR.** W1 calibrated thresholds on the honest prefix of the evaluated
   episode, so FPR = 0 by construction. Fix: separate 120-question pilot (N01).

## Submitted W1 streams
| Provider | turns | empty answers | empty scored correct | honest empty |
|---|---:|---:|---:|---:|
| anthropic | 20 | 0 | 0 | 0/8 |
| azure_openai | 20 | 3 | 3 | 3/8 |

## LLM cache shipped with the submission
| Provider | entries | empty text |
|---|---:|---:|
| anthropic | 5121 | 0 |
| azure_openai | 5073 | 61 |

## Reconciliation of the E1 numbers questioned by reviewers
| Number in paper | What it actually is | Superseded by |
|---|---|---|
| Table 1 / Fig. 1 E1 TGCC 0.17, NoSyn 0.72, Naive 0.12 (60 Q, compromise 20) | Produced by E1 code that is not in the artifact; not reproducible. Naive 0.12 is inconsistent with a gate that never revokes (latency = inf => OER = 1.00). | N01 (15 independent 60-Q episodes per provider) |
| Table 9 / Table 8 E6 TGCC 0.11 [0.08, 0.25] (Claude), 0.07 (gpt-5) | Bootstrap MEAN over resamples of the single 20-turn W1 episode (compromise 8), not the E1 episode; gpt-5 stream affected by findings 1-2. | N01 across-episode CIs; N03 for baselines |
| Table 12 E9 baseline TGCC OER 0.25 (Claude) | Point estimate of the same single 20-turn W1 episode (12 post-compromise steps). | N01 / N03 |
