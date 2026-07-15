# W7 - Colluding agents

## Weakness addressed
**W7**: The paper marks colluding adversaries as out of scope, but reviewers
view this as a hole because collusion is the canonical multi-agent attack.

## Method
1. Three personas of the same LLM answer the same 20 factual questions
   (Analyst Alpha, Beta, Gamma).  Alpha is honest; **Beta and Gamma are
   colluding sleepers** who inject the *same* wrong answer with high
   stated confidence after step 8.
2. Each persona runs its own pre-warmed TGCC controller with the paper's
   default parameters.
3. We add a **cross-agent agreement signal** on the role layer:
   `s_agree(i) = fraction_{j != i} 1[answer_i == answer_j]`.  When
   collusion produces two-thirds majority for the wrong answer, the honest
   agent looks *isolated* on the role layer; when it produces one-third
   majority, both sleepers look isolated.

## Results (mean OER across 3 seeds)

| Agent (role) | Without agreement signal | With agreement signal |
|---|---|---|
| analyst_alpha(honest) | 1.00 ± 0.00 | 0.42 ± 0.00 |
| analyst_beta(sleeper) | 0.58 ± 0.00 | 0.50 ± 0.00 |
| analyst_gamma(sleeper) | 0.58 ± 0.00 | 0.50 ± 0.00 |

## Reading
* The **without-agreement** column is the paper's baseline TGCC applied
  independently per agent -- it should already reduce OER on both
  sleepers via the epistemic-layer signal alone.
* The **with-agreement** column adds the cross-agent consistency signal.
  It should push the *sleeper* OERs lower without inflating the *honest*
  agent's OER; this is the collusion-detection gain.

## Figures
![Collusion](figures/collusion.png)

## Files
- `results.json` - per-seed per-agent traces + aggregate metrics.
- `figures/collusion.png` - OER per agent, with/without agreement.
