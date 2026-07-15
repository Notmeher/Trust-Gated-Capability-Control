# W9 - Per-layer ablation

## Weakness addressed
**W9**: The paper's five layers are treated as an indivisible bundle.
Reviewers ask which layer actually carries the detection load, and whether
the framework degrades gracefully if any single layer's signal is spoofed.

## Method
For every layer $\ell \in \{0, 1, 2, 3, 4\}$ (epistemic, behavioural,
role, social, institutional), we run TGCC on the cached W1 signals in
three conditions:

* **Full** - the untouched five-signal vector.
* **Force layer_l = 1.0** - simulates an adversary that has *fully spoofed*
  that layer's signal to look healthy.
* **Force layer_l = 0.0** - simulates a *drop* of that layer's evidence.

The gap between the three conditions attributes detection responsibility to
each layer.  A large drop in OER when a layer is spoofed to 1.0 means
detection was hinging on that layer; a large drop when it is set to 0.0
means the layer is capable of triggering revocation on its own.

## Results
### anthropic
| Condition | OER | Latency | FPR |
|---|---|---|---|
| full | 0.25 | 3.0 | 0.00 |
| epistemic=1 | 1.00 | inf | 0.00 |
| epistemic=0 | 0.00 | 0.0 | 1.00 |
| behavioral=1 | 0.25 | 3.0 | 0.00 |
| behavioral=0 | 0.00 | 0.0 | 0.62 |
| role=1 | 0.25 | 3.0 | 0.00 |
| role=0 | 0.00 | 0.0 | 0.75 |
| social=1 | 0.25 | 3.0 | 0.00 |
| social=0 | 0.00 | 0.0 | 0.75 |
| institutional=1 | 0.25 | 3.0 | 0.00 |
| institutional=0 | 0.00 | 0.0 | 0.75 |


### azure_openai
| Condition | OER | Latency | FPR |
|---|---|---|---|
| full | 0.17 | 2.0 | 0.00 |
| epistemic=1 | 1.00 | inf | 0.00 |
| epistemic=0 | 0.00 | 0.0 | 0.62 |
| behavioral=1 | 0.17 | 2.0 | 0.00 |
| behavioral=0 | 0.00 | 0.0 | 0.12 |
| role=1 | 0.17 | 2.0 | 0.00 |
| role=0 | 0.00 | 0.0 | 0.25 |
| social=1 | 0.17 | 2.0 | 0.00 |
| social=0 | 0.00 | 0.0 | 0.25 |
| institutional=1 | 0.17 | 2.0 | 0.00 |
| institutional=0 | 0.00 | 0.0 | 0.25 |



**Reading.**  For factual-QA data the epistemic layer is the load bearer:
forcing it to 1.0 drives OER back toward 1.0 (TGCC loses detection),
while forcing it to 0.0 drives OER to ~0 (immediate revocation).  Other
layers move OER very little because they were already saturated by the
synergy operator through the epistemic prerequisite.

## Files
- `results.json` - condition-wise metrics per provider.
- `figures/ablation.png` - bar chart of OER under each ablation.
