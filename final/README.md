# TGCC — Weakness Mitigations (Final Deliverables, W1–W16)

Sixteen post-hoc experiments that address reviewer-facing weaknesses in the
paper *"Trust-Gated Capability Control: An Operational Framework for Breaking
the Trust–Vulnerability Paradox in Multi-Agent LLM Systems"*.

Each sub-folder contains:

- `README.md` — method, results table, figures, configuration, process notes.
- `results.json` — raw numbers (per-turn signals, grants, metrics, sweeps).
- `figures/*.png` — plots (regenerated deterministically from `results.json`).

See [`SUMMARY.md`](SUMMARY.md) for a consolidated one-page table.

## Priority 1 — reviewer must-haves

| Folder | Addresses | One-line summary |
|---|---|---|
| [`w1_multi_model/`](w1_multi_model/README.md) | W1 single-model reproduction | Claude + Azure gpt-5 with prewarming and Algorithm-2 auto-calibration. |
| [`w2_bounded_forgery/`](w2_bounded_forgery/README.md) | W2 non-forgery assumption | OER $\le 0.25$ even for $\Delta = 1$. |
| [`w3_baselines/`](w3_baselines/README.md) | W3 self-ablation only | Head-to-head vs. Naive / EigenTrust / DynaTrust / AgentGuard / Constitutional. |
| [`w4_learned_coupling/`](w4_learned_coupling/README.md) | W4 hand-designed coupling | L-BFGS-B recovers the lower-triangular hierarchy. |
| [`w5_latency_sweep/`](w5_latency_sweep/README.md) | W5 log-latency claim | Empirical latency scales with $1/(1-\gamma)$; Hedge accelerates by ~10×. |
| [`w6_bootstrap_ci/`](w6_bootstrap_ci/README.md) | W6 statistical significance | Bootstrap CIs + Wilcoxon $p<0.01$ vs. 4/5 baselines. |
| [`w7_collusion/`](w7_collusion/README.md) | W7 colluding adversaries | Per-agent TGCC works; **naive agreement signal actively hurts**. |
| [`w8_prompt_injection/`](w8_prompt_injection/README.md) | W8 prompt injection | Both models resist; Azure filter blocks 14%. |

## Priority 2 — sharpens the paper

| Folder | Addresses | One-line summary |
|---|---|---|
| [`w9_layer_ablation/`](w9_layer_ablation/README.md) | W9 per-layer attribution | Epistemic is the sole load-bearing layer for detection. |
| [`w10_long_horizon/`](w10_long_horizon/README.md) | W10 long-horizon drift | 5000-turn episode with gradual + sudden non-stationarity; tracks within 1 time constant. |
| [`w11_sensitivity/`](w11_sensitivity/README.md) | W11 parameter sensitivity | Order $\gamma > \theta \gg \omega \gg p$; $p$ is nearly inert. |
| [`w12_recovery/`](w12_recovery/README.md) | W12 recovery mechanism | Recovery latency $\approx 1.4 \tau$; automatic re-authorisation. |

## Priority 3 — extra polish

| Folder | Addresses | One-line summary |
|---|---|---|
| [`w13_byzantine_chain/`](w13_byzantine_chain/README.md) | W13 Byzantine chains | Latency decreases with $N$; blast radius bounded; overhead flat. |
| [`w14_audit_trail/`](w14_audit_trail/README.md) | W14 auditable decisions | Pydantic-validated `RevocationReport` per step. |
| [`w15_calibration_robustness/`](w15_calibration_robustness/README.md) | W15 calibration robustness | RMS-error minimum at $N_{\text{pilot}} \approx 80 \approx \tau$. |
| [`w16_adaptive_attacker/`](w16_adaptive_attacker/README.md) | W16 adaptive attacker | Perfect calibration only inflates OER by ~30%. |

## Reproducing

```powershell
# LLM-touching (use cached responses after first pass)
uv run python -m tgcc.experiments.w1_multi_model
uv run python -m tgcc.experiments.w7_collusion
uv run python -m tgcc.experiments.w8_prompt_injection

# Depends on W1
uv run python -m tgcc.experiments.w3_baselines
uv run python -m tgcc.experiments.w6_bootstrap_ci
uv run python -m tgcc.experiments.w9_layer_ablation

# Simulation only
uv run python -m tgcc.experiments.w2_bounded_forgery
uv run python -m tgcc.experiments.w4_learned_coupling
uv run python -m tgcc.experiments.w5_latency_sweep
uv run python -m tgcc.experiments.w10_long_horizon
uv run python -m tgcc.experiments.w11_sensitivity
uv run python -m tgcc.experiments.w12_recovery
uv run python -m tgcc.experiments.w13_byzantine_chain
uv run python -m tgcc.experiments.w14_audit_trail
uv run python -m tgcc.experiments.w15_calibration_robustness
uv run python -m tgcc.experiments.w16_adaptive_attacker
```

## Providers

- **Anthropic Claude** (`claude-sonnet-4-5`) via `anthropic` SDK.
- **Azure OpenAI (`gpt-5`)** via `openai` SDK's `AzureOpenAI` client.
- No models are downloaded — everything runs against hosted APIs.

## Paper integration

The results in this folder appear in the paper as
**Appendix H (Extended Robustness Study)**, sections H.1–H.11, in
[`../ACM_Conference_Proceedings_Primary_Article_Template/sigconf.tex`](../ACM_Conference_Proceedings_Primary_Article_Template/sigconf.tex).
The main paper (§1–§11, Appendices A–G) is untouched.
