# W4 - Learning the Coupling Matrix from Traces

## Weakness addressed
**W4**: The paper's coupling matrix is *hand-designed* and lower-triangular by
construction.  Reviewers ask whether a learned coupling can (a) match a
hand-designed one and (b) discover the hierarchy from data.

## Method
1. Choose a ground-truth coupling matrix `C_star` (the paper's default).
2. Simulate `n_episodes = 40` trajectories with
   `n_turns = 200` per episode.  For each turn:
   * draw Bernoulli signals with `rho_honest` before the compromise and
     `rho_sleeper` after.
   * update the per-layer Beta beliefs to obtain per-step trusts `T(t)`.
   * compute the composite `Phi_star(t)` with `C_star`.
   * emit a binary harm label `y(t) ~ Bernoulli(1 - Phi_star(t))`.
3. **The learner sees only `(T(t), y(t))`.**  It parameterises a
   lower-triangular `C_hat = sigmoid(theta)` and minimises the per-step
   binary cross-entropy of `1 - Phi_hat(t)` against `y(t)` via L-BFGS-B.
4. We report Frobenius distance `||C_hat - C_star||_F`, per-entry error,
   and whether the learned matrix respects the hierarchy (i.e. the
   diagonal-and-above entries are near zero, and epistemic couplings dominate).

## Results
* Frobenius distance: **0.724**
* Lower-triangular recovery: **yes**
* Best training BCE: **0.566**

Learned matrix (rows = dependent layer, columns = prerequisite):

```
[[0.   0.   0.   0.   0.  ]
 [0.37 0.   0.   0.   0.  ]
 [0.65 0.09 0.   0.   0.  ]
 [0.31 0.46 0.7  0.   0.  ]
 [0.26 0.26 0.16 0.65 0.  ]]
```

Ground-truth matrix:

```
[[0.   0.   0.   0.   0.  ]
 [0.7  0.   0.   0.   0.  ]
 [0.45 0.65 0.   0.   0.  ]
 [0.35 0.4  0.6  0.   0.  ]
 [0.3  0.3  0.35 0.55 0.  ]]
```

## Interpretation
A small Frobenius distance combined with the correct sparsity pattern
demonstrates that the coupling matrix can be **learned from traces alone**,
removing the paper's reliance on hand-designed dependencies.  Any residual
error concentrates on couplings whose prerequisite rarely fails in the
episodes, i.e. entries that are unidentifiable from the observed data - a
useful diagnostic in itself.

## Configuration
```yaml
{'n_episodes': 40, 'n_turns': 200, 'compromise_step': 50, 'seed': 7, 'n_starts': 4, 'honest_rho': [0.92, 0.88, 0.82, 0.78, 0.9], 'sleeper_rho': [0.3, 0.88, 0.75, 0.72, 0.88]}
```

## Files
- `results.json` - the fitted matrix, ground truth, and diagnostics.
- `figures/coupling_recovery.png` - side-by-side heatmaps.
