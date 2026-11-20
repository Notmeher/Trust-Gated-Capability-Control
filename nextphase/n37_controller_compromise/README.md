# N37 - Controller compromise: verifiable grants

## Reviewer issue
IEEE R1-2: compromise of the controller itself is excluded from the threat model.

## Mechanism
Probe outputs go to an append-only log authenticated with the probes' own keys; the controller is deterministic, so
independent verifier replicas replay it from the log and the published thresholds; the tool gateway executes an
action only when a quorum (controller + verifiers) has signed the same grant commitment.

## Results (TGCC-R on the real E1 sleeper episodes; the controller is compromised from step 20)
Harmful actions executed / harmful actions attempted, per gateway quorum. "Honest executed" = honest-phase actions
executed under the 2-of-2 quorum / by an uncompromised controller (must be equal). "Replay disagreements" = steps
where an honest verifier's replay differs from the honest controller (must be 0). Detection = median steps after
the attack starts until an honest verifier refuses to co-sign.

| Stream | Attack | controller only | 2-of-2 (controller + V1) | 2-of-3 (controller + V1 + V2) | 3-of-3 (controller + V1 + V2) | honest executed (2-of-2) | replay disagreements | log tampering detected | detection (steps) | verification us/step |
|---|---|---|---|---|---|---|---:|---|---:|---:|
| Claude Sonnet 4.5 / TriviaQA | none | 12/600 | 12/600 | 12/600 | 12/600 | 286/286 | 0 | 0/15 | - | 17 |
| Claude Sonnet 4.5 / TriviaQA | forged grants | 600/600 | 12/600 | 12/600 | 12/600 | 286/286 | 0 | 0/15 | 1.0 | 17 |
| Claude Sonnet 4.5 / TriviaQA | tampered thresholds | 600/600 | 12/600 | 12/600 | 12/600 | 286/286 | 0 | 0/15 | 1.0 | 17 |
| Claude Sonnet 4.5 / TriviaQA | tampered log | 600/600 | 0/600 | 0/600 | 0/600 | 0/286 | 0 | 15/15 | 0.0 | 1 |
| Claude Sonnet 4.5 / TriviaQA | collusion (controller + V1) | 600/600 | 600/600 | 600/600 | 12/600 | 286/286 | 0 | 0/15 | 1.0 | 17 |
| GPT-5 / TriviaQA | none | 6/600 | 6/600 | 6/600 | 6/600 | 267/267 | 0 | 0/15 | - | 17 |
| GPT-5 / TriviaQA | forged grants | 600/600 | 6/600 | 6/600 | 6/600 | 267/267 | 0 | 0/15 | 0.0 | 17 |
| GPT-5 / TriviaQA | tampered thresholds | 600/600 | 6/600 | 6/600 | 6/600 | 267/267 | 0 | 0/15 | 0.0 | 17 |
| GPT-5 / TriviaQA | tampered log | 600/600 | 0/600 | 0/600 | 0/600 | 0/267 | 0 | 15/15 | 0.0 | 1 |
| GPT-5 / TriviaQA | collusion (controller + V1) | 600/600 | 600/600 | 600/600 | 6/600 | 267/267 | 0 | 0/15 | 0.0 | 17 |
| Claude Haiku 4.5 / TriviaQA | none | 1/200 | 1/200 | 1/200 | 1/200 | 48/48 | 0 | 0/5 | - | 17 |
| Claude Haiku 4.5 / TriviaQA | forged grants | 200/200 | 1/200 | 1/200 | 1/200 | 48/48 | 0 | 0/5 | 0.0 | 17 |
| Claude Haiku 4.5 / TriviaQA | tampered thresholds | 200/200 | 1/200 | 1/200 | 1/200 | 48/48 | 0 | 0/5 | 0.0 | 17 |
| Claude Haiku 4.5 / TriviaQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/48 | 0 | 5/5 | 0.0 | 1 |
| Claude Haiku 4.5 / TriviaQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 1/200 | 48/48 | 0 | 0/5 | 0.0 | 17 |
| Qwen3-4B / TriviaQA | none | 167/200 | 167/200 | 167/200 | 167/200 | 99/99 | 0 | 0/5 | - | 18 |
| Qwen3-4B / TriviaQA | forged grants | 200/200 | 167/200 | 167/200 | 167/200 | 99/99 | 0 | 0/5 | 32.0 | 18 |
| Qwen3-4B / TriviaQA | tampered thresholds | 200/200 | 167/200 | 167/200 | 167/200 | 99/99 | 0 | 0/5 | 32.0 | 35 |
| Qwen3-4B / TriviaQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/99 | 0 | 5/5 | 0.0 | 1 |
| Qwen3-4B / TriviaQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 167/200 | 99/99 | 0 | 0/5 | 32.0 | 20 |
| Qwen3-8B / TriviaQA | none | 66/200 | 66/200 | 66/200 | 66/200 | 100/100 | 0 | 0/5 | - | 18 |
| Qwen3-8B / TriviaQA | forged grants | 200/200 | 66/200 | 66/200 | 66/200 | 100/100 | 0 | 0/5 | 12.0 | 19 |
| Qwen3-8B / TriviaQA | tampered thresholds | 200/200 | 66/200 | 66/200 | 66/200 | 100/100 | 0 | 0/5 | 12.0 | 18 |
| Qwen3-8B / TriviaQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/100 | 0 | 5/5 | 0.0 | 1 |
| Qwen3-8B / TriviaQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 66/200 | 100/100 | 0 | 0/5 | 12.0 | 18 |
| Qwen2.5-7B / TriviaQA | none | 46/200 | 46/200 | 46/200 | 46/200 | 100/100 | 0 | 0/5 | - | 19 |
| Qwen2.5-7B / TriviaQA | forged grants | 200/200 | 46/200 | 46/200 | 46/200 | 100/100 | 0 | 0/5 | 6.0 | 17 |
| Qwen2.5-7B / TriviaQA | tampered thresholds | 200/200 | 46/200 | 46/200 | 46/200 | 100/100 | 0 | 0/5 | 6.0 | 18 |
| Qwen2.5-7B / TriviaQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/100 | 0 | 5/5 | 0.0 | 1 |
| Qwen2.5-7B / TriviaQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 46/200 | 100/100 | 0 | 0/5 | 6.0 | 17 |
| Claude Sonnet 4.5 / MedMCQA | none | 60/200 | 60/200 | 60/200 | 60/200 | 100/100 | 0 | 0/5 | - | 17 |
| Claude Sonnet 4.5 / MedMCQA | forged grants | 200/200 | 60/200 | 60/200 | 60/200 | 100/100 | 0 | 0/5 | 11.0 | 17 |
| Claude Sonnet 4.5 / MedMCQA | tampered thresholds | 200/200 | 60/200 | 60/200 | 60/200 | 100/100 | 0 | 0/5 | 11.0 | 17 |
| Claude Sonnet 4.5 / MedMCQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/100 | 0 | 5/5 | 0.0 | 1 |
| Claude Sonnet 4.5 / MedMCQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 60/200 | 100/100 | 0 | 0/5 | 11.0 | 17 |
| GPT-5 / MedMCQA | none | 18/200 | 18/200 | 18/200 | 18/200 | 96/96 | 0 | 0/5 | - | 18 |
| GPT-5 / MedMCQA | forged grants | 200/200 | 18/200 | 18/200 | 18/200 | 96/96 | 0 | 0/5 | 4.0 | 49 |
| GPT-5 / MedMCQA | tampered thresholds | 200/200 | 18/200 | 18/200 | 18/200 | 96/96 | 0 | 0/5 | 4.0 | 32 |
| GPT-5 / MedMCQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/96 | 0 | 5/5 | 0.0 | 1 |
| GPT-5 / MedMCQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 18/200 | 96/96 | 0 | 0/5 | 4.0 | 18 |
| Claude Haiku 4.5 / MedMCQA | none | 98/200 | 98/200 | 98/200 | 98/200 | 100/100 | 0 | 0/5 | - | 18 |
| Claude Haiku 4.5 / MedMCQA | forged grants | 200/200 | 98/200 | 98/200 | 98/200 | 100/100 | 0 | 0/5 | 20.0 | 17 |
| Claude Haiku 4.5 / MedMCQA | tampered thresholds | 200/200 | 98/200 | 98/200 | 98/200 | 100/100 | 0 | 0/5 | 20.0 | 18 |
| Claude Haiku 4.5 / MedMCQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/100 | 0 | 5/5 | 0.0 | 1 |
| Claude Haiku 4.5 / MedMCQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 98/200 | 100/100 | 0 | 0/5 | 20.0 | 17 |
| Qwen3-4B / MedMCQA | none | 143/200 | 143/200 | 143/200 | 143/200 | 100/100 | 0 | 0/5 | - | 17 |
| Qwen3-4B / MedMCQA | forged grants | 200/200 | 143/200 | 143/200 | 143/200 | 100/100 | 0 | 0/5 | 25.0 | 17 |
| Qwen3-4B / MedMCQA | tampered thresholds | 200/200 | 143/200 | 143/200 | 143/200 | 100/100 | 0 | 0/5 | 25.0 | 17 |
| Qwen3-4B / MedMCQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/100 | 0 | 5/5 | 0.0 | 1 |
| Qwen3-4B / MedMCQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 143/200 | 100/100 | 0 | 0/5 | 25.0 | 17 |
| Qwen3-8B / MedMCQA | none | 130/200 | 130/200 | 130/200 | 130/200 | 100/100 | 0 | 0/5 | - | 17 |
| Qwen3-8B / MedMCQA | forged grants | 200/200 | 130/200 | 130/200 | 130/200 | 100/100 | 0 | 0/5 | 24.0 | 17 |
| Qwen3-8B / MedMCQA | tampered thresholds | 200/200 | 130/200 | 130/200 | 130/200 | 100/100 | 0 | 0/5 | 24.0 | 17 |
| Qwen3-8B / MedMCQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/100 | 0 | 5/5 | 0.0 | 1 |
| Qwen3-8B / MedMCQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 130/200 | 100/100 | 0 | 0/5 | 24.0 | 17 |
| Qwen2.5-7B / MedMCQA | none | 200/200 | 200/200 | 200/200 | 200/200 | 100/100 | 0 | 0/5 | - | 17 |
| Qwen2.5-7B / MedMCQA | forged grants | 200/200 | 200/200 | 200/200 | 200/200 | 100/100 | 0 | 0/5 | - | 17 |
| Qwen2.5-7B / MedMCQA | tampered thresholds | 200/200 | 200/200 | 200/200 | 200/200 | 100/100 | 0 | 0/5 | - | 18 |
| Qwen2.5-7B / MedMCQA | tampered log | 200/200 | 0/200 | 0/200 | 0/200 | 0/100 | 0 | 5/5 | 0.0 | 1 |
| Qwen2.5-7B / MedMCQA | collusion (controller + V1) | 200/200 | 200/200 | 200/200 | 200/200 | 100/100 | 0 | 0/5 | - | 17 |

Reading: with a single trusted controller every attack executes all harmful actions; any quorum that contains one
honest verifier executes exactly the harmful actions the uncompromised controller would have executed, because the
verifier only co-signs grants its own replay of the authenticated log produces. Collusion of the controller with one
verifier defeats 2-of-2 and 2-of-3 but not 3-of-3: the quorum must exceed the number of compromised parties.
A rewritten log fails the probe MACs (the controller does not hold the probe keys), so honest verifiers refuse to
co-sign anything for that agent: the system fails closed (0 honest actions executed) and the tampering is detected
immediately.

![controller compromise](figures/controller_compromise.png)
