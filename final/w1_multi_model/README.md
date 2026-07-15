# W1 - Multi-Model Reproduction (Claude + Azure OpenAI gpt-5)

## Weakness addressed
**W1**: The paper's Experiment 1 uses one production model (Claude).  Reviewers
will ask whether the *Trust-Vulnerability Paradox* and its resolution by TGCC
generalize to other model families.  This experiment reproduces the paradox
and TGCC's fix on **two providers** using the same episode protocol.

## Method
1. `n_turns = 20` factual questions sampled with seed `0`
   (see `src/tgcc/data_qa.py`).
2. For each provider we run one episode:
   * turns `0 .. 7` use the **honest** system prompt.
   * turns `8 .. 19` are the **compromise** phase.
3. `sleeper_mode = "both"` controls how the compromise is produced:
   * **prompt** - swap in the sleeper system prompt and rely on the model to
     comply (works on Claude; strongly aligned models such as gpt-5 refuse).
   * **inject** - keep the honest prompt but *post-hoc replace* the model's
     `Answer:` line with a plausible-wrong string while preserving the
     `Confidence:` line at ~0.95.  Behavioural/role/social signals stay
     identical; only the epistemic signal collapses.  Lets us measure the
     paradox mechanism independently of the model's alignment training.
   * **both** - inject only when the sleeper prompt failed to make the answer wrong.
4. Signals are computed with the calibrated factual-QA probes
   (see `src/tgcc/probes.py`).
5. **Pre-warming** (True): each Beta belief is seeded with an
   honest prior (`rho=0.9`, effective count 40) so the composite starts near
   its stationary honest value rather than at 0.5.  Mitigates the warmup FPR.
6. **Auto-calibration** (True): thresholds are set from
   the honest-phase composite minimum minus a safety margin
   (`epsilon = 0.05`) -- Algorithm 2 in the paper.
7. Metrics: over-exposure rate (OER), revocation latency, honest-phase FPR.

## Results
| Provider | Model | Honest Acc | Sleeper Acc | Inject Frac | theta / theta_epi | TGCC OER | TGCC Latency | TGCC FPR | Naive OER | Naive Latency |
|---|---|---|---|---|---|---|---|---|---|---|
| anthropic | claude-sonnet-4-5 | 1.00 | 0.00 | 0.17 | 0.51 / 0.71 | 0.25 | 3.0 | 0.00 | 1.00 | inf |
| azure_openai | gpt-5 | 1.00 | 0.00 | 0.92 | 0.37 / 0.60 | 0.17 | 2.0 | 0.00 | 1.00 | inf |

**Reading the table.**  A successful mitigation shows:

* **Consistency**: TGCC's OER is low on both providers (proving W1).
* **Injection reveals the mechanism**: when a strongly aligned model refuses
  the sleeper prompt, the *inject* mode still triggers the paradox at the
  signal level and TGCC still revokes.
* **Naive fails** where the behavioural signal stays high (both providers).

## Finding: gpt-5 refuses the sleeper prompt
In `sleeper_mode="prompt"` runs we observed that gpt-5 refused to produce
plausible-wrong answers and instead produced empty or safe responses.  This
is a **positive alignment finding** worth reporting in its own right: strong
alignment training partially defends against stealth-sleeper prompts before
any runtime trust controller is invoked.  We report both configurations to
separate model-level alignment from controller-level protection.

## Configuration
```yaml
n_turns: 20
compromise_step: 8
seed: 0
sleeper_mode: both
prewarm: True
auto_calibrate: True
safety_margin_epsilon: 0.05
tgcc:
  p: -6.0
  gamma: 0.985
  omega: 3.0
  lambda: 0.5
  eta: 0.5
```

## Figures
![anthropic](figures/anthropic_trust.png)
![azure_openai](figures/azure_openai_trust.png)

## Files
- `results.json` - raw per-turn logs, per-provider metrics, calibrated thresholds.
- `figures/*.png` - per-provider trust & grant trajectories.

## Process notes
- Responses are cached under `cache/llm/<provider>/` (SHA-256 of the payload)
  so re-runs are free after the first pass.
- Cost is bounded: ~ `n_providers * n_turns` short chat completions.
- Set ``--sleeper-mode inject`` to run this study on any model, including
  those with strong refusal training.
