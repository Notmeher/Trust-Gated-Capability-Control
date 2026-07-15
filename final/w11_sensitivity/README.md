# W11 - Controller parameter sensitivity

## Weakness addressed
**W11**: Are TGCC's headline numbers brittle under small parameter perturbations?

## Method
1. Fix the paper's recommended operating point:
   `theta=0.40`, `gamma=0.985`, `omega=3`, `p=-6`.
2. For each parameter independently, sweep it over `[0.8 x, 0.9 x, x, 1.1 x, 1.2 x]`
   holding the others fixed.
3. Simulate a stealth-sleeper compromise (n_turns=200, compromise at 60),
   `n_seeds = 15` seeds per point.
4. Report the Morris-style elementary effect: max-abs metric change divided
   by max-abs parameter change.

## Elementary effects (higher = more sensitive)

| Parameter | on OER | on latency | on FPR |
|---|---|---|---|
| theta | 1.91 | 257 | 2.88 |
| gamma | 3.35 | 472 | 4.47 |
| omega | 0.196 | 26.4 | 0.257 |
| p | 0.0075 | 1.07 | 0.0171 |

## Per-sweep detail
### theta
| value | OER | latency | FPR |
|---|---|---|---|
| 0.320 | 0.31 ± 0.08 | 41.5 ± 12.4 | 0.00 ± 0.01 |
| 0.360 | 0.16 ± 0.09 | 21.3 ± 13.3 | 0.02 ± 0.05 |
| 0.400 | 0.09 ± 0.07 | 11.4 ± 8.8 | 0.06 ± 0.11 |
| 0.440 | 0.02 ± 0.03 | 2.7 ± 4.4 | 0.24 ± 0.24 |
| 0.480 | 0.00 ± 0.01 | 0.4 ± 1.0 | 0.46 ± 0.28 |

### gamma
| value | OER | latency | FPR |
|---|---|---|---|
| 0.950 | 0.02 ± 0.02 | 2.1 ± 3.0 | 0.24 ± 0.19 |
| 0.970 | 0.04 ± 0.04 | 5.2 ± 5.6 | 0.13 ± 0.16 |
| 0.985 | 0.09 ± 0.07 | 11.4 ± 8.8 | 0.06 ± 0.11 |
| 0.993 | 0.13 ± 0.08 | 16.7 ± 11.1 | 0.05 ± 0.10 |
| 0.998 | 0.18 ± 0.10 | 24.7 ± 14.5 | 0.03 ± 0.07 |

### omega
| value | OER | latency | FPR |
|---|---|---|---|
| 2.000 | 0.39 ± 0.08 | 53.1 ± 10.3 | 0.00 ± 0.00 |
| 2.500 | 0.19 ± 0.08 | 25.0 ± 12.5 | 0.01 ± 0.03 |
| 3.000 | 0.09 ± 0.07 | 11.4 ± 8.8 | 0.06 ± 0.11 |
| 3.500 | 0.01 ± 0.02 | 1.7 ± 3.1 | 0.29 ± 0.26 |
| 4.000 | 0.00 ± 0.01 | 0.3 ± 0.8 | 0.51 ± 0.30 |

### p
| value | OER | latency | FPR |
|---|---|---|---|
| -10.000 | 0.06 ± 0.06 | 6.7 ± 6.8 | 0.15 ± 0.18 |
| -8.000 | 0.07 ± 0.06 | 8.9 ± 8.4 | 0.11 ± 0.15 |
| -6.000 | 0.09 ± 0.07 | 11.4 ± 8.8 | 0.06 ± 0.11 |
| -4.000 | 0.10 ± 0.07 | 13.2 ± 8.9 | 0.04 ± 0.08 |
| -2.000 | 0.12 ± 0.06 | 15.3 ± 8.9 | 0.01 ± 0.03 |


## Reading
* If any elementary effect > 5, the controller is dangerously brittle in
  that parameter.  A well-behaved controller has all effects at O(1).

## Files
- `results.json` - full sweep with per-metric mean +/- std.
- `figures/sensitivity.png` - metric curves per parameter.
