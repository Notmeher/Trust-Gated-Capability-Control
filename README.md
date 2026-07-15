# Trust-Gated Capability Control (TGCC)

**An Operational Framework for Breaking the Trust–Vulnerability Paradox in Multi-Agent LLM Systems**

> ⚠️ **Under double-blind review at KDD 2027.** Author identity is intentionally omitted from this repository. Reviewers should use the anonymized mirror:
> <https://anonymous.4open.science/r/Trust-Gated-Capability-Control-AE81/>

---

## Overview

Layered trust models for multi-agent LLM systems remain largely conceptual: they describe *which* dimensions of trust matter but do not specify *how* trust at different layers combines, *how* layer importance adapts at runtime, or *how* trust should govern what an agent is permitted to do.

This repository operationalizes a five-layer trust stack (epistemic → behavioural → role → social → institutional) into a runtime controller — **Trust-Gated Capability Control (TGCC)** — with provable guarantees:

- **Paradox resolution** (Theorem 3): TGCC breaks the Trust-Vulnerability Paradox at the operator level.
- **Logarithmic revocation latency** (Corollary 1): $O(\log_{1/\gamma}(1/\epsilon))$ steps to contain a compromise.
- **Exponentially decaying honest false-positive rate** (Theorem 4).
- **Constant per-agent overhead** in collective size (Proposition 5): $O(L^2 + |\mathcal{C}|)$ per step, independent of interaction history.

## Repository layout

```
├── ACM_Conference_Proceedings_Primary_Article_Template/
│   ├── sigconf.tex          # main paper (LaTeX, ACM sigconf, anonymized)
│   ├── reference.bib        # bibliography
│   ├── ACM-Reference-Format.bst
│   └── figures/             # figures compiled into the PDF
├── src/tgcc/                # implementation
│   ├── beta_belief.py       # Beta-belief update (Eq. 1)
│   ├── synergy.py           # cross-layer synergy operator (Eq. 3)
│   ├── composite.py         # weighted power-mean composite (Eq. 5)
│   ├── hedge.py             # failure-grounded adaptive weighting (Eqs. 9–10)
│   ├── controller.py        # TGCC runtime loop (Algorithm 1)
│   ├── probes.py            # per-layer check-signal probes
│   ├── baselines/           # Naive, EigenTrust, DynaTrust, AgentGuard, Constitutional
│   ├── experiments/         # w1–w16 experiment drivers
│   ├── metrics.py           # OER / latency / FPR
│   └── reporting.py         # figure and results.json emission
├── final/                   # published per-experiment READMEs + results.json + figures
│   ├── SUMMARY.md           # consolidated results table
│   ├── w1_multi_model/          # E1: real-LLM epistemic calibration probe
│   ├── w2_bounded_forgery/      # W2: bounded-forgery adversary
│   ├── w3_baselines/            # E-baseline: head-to-head vs. 5 controllers
│   ├── w4_learned_coupling/     # W4: coupling matrix learned from traces
│   ├── w5_latency_sweep/        # W5: forgetting-factor sweep
│   ├── w6_bootstrap_ci/         # E6: stratified bootstrap + Wilcoxon
│   ├── w7_collusion/            # E7: colluding adversaries
│   ├── w8_prompt_injection/     # E8: indirect prompt injection
│   ├── w9_layer_ablation/       # E9: per-layer detection attribution
│   ├── w10_long_horizon/        # E10: 5000-turn drift
│   ├── w11_sensitivity/         # E11: controller-parameter sensitivity
│   ├── w12_recovery/            # E12: revocation-then-recovery
│   ├── w13_byzantine_chain/     # E13: Byzantine multi-agent chains
│   ├── w14_audit_trail/         # E14: RevocationReport JSON schema
│   ├── w15_calibration_robustness/  # E15: pilot-length RMS error
│   └── w16_adaptive_attacker/   # E16: calibrated-confidence attacker
├── scripts/                 # diagnostic helpers (diag_w1.py, diag_w5.py, ...)
├── main.py                  # smoke-test entry point
├── pyproject.toml           # uv package definition
└── uv.lock
```

## Installation

Requires Python 3.12 and [`uv`](https://github.com/astral-sh/uv):

```bash
pip install uv
uv sync
```

For the real-LLM experiments (W1, W3, W8) create a `.env` at the repo root:

```
ANTHROPIC_API_KEY=sk-ant-...
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-5
```

Simulation-only experiments (W2, W4, W5, W7, W9–W16) require no API keys and run offline.

## Reproducing the paper's experiments

Each experiment writes `results.json` and `figures/*.png` into its `final/wX_*/` folder.

### Console scripts

```bash
uv run tgcc-w1        # E1: real-LLM epistemic calibration probe (Claude + gpt-5)
uv run tgcc-w2        # W2: bounded forgery
uv run tgcc-w3        # baselines: head-to-head vs. 5 controllers
uv run tgcc-w4        # W4: learned coupling
uv run tgcc-w5        # W5: latency sweep
```

### Extended robustness study (E6–E16)

```bash
uv run python -m tgcc.experiments.w6_bootstrap_ci
uv run python -m tgcc.experiments.w7_collusion
uv run python -m tgcc.experiments.w8_prompt_injection
uv run python -m tgcc.experiments.w9_layer_ablation
uv run python -m tgcc.experiments.w10_long_horizon
uv run python -m tgcc.experiments.w11_sensitivity
uv run python -m tgcc.experiments.w12_recovery
uv run python -m tgcc.experiments.w13_byzantine_chain
uv run python -m tgcc.experiments.w14_audit_trail
uv run python -m tgcc.experiments.w15_calibration_robustness
uv run python -m tgcc.experiments.w16_adaptive_attacker
```

Real-LLM runs (W1, W3, W8) are cached: on repeat invocations the cached responses are reused so downstream figures are deterministic.

## Headline results

| Experiment | Setting | TGCC OER | Baseline OER |
|---|---|---:|---:|
| E1 (Claude) | Real-LLM sleeper probe | **0.25** (latency 3) | 1.00 (Naive) |
| E1 (gpt-5) | Real-LLM sleeper probe | **0.17** (latency 2) | 1.00 (Naive) |
| E6 (Claude, 1000-boot) | Bootstrap 95% CI | **0.11 [0.08, 0.25]** | 0.53–1.00 |
| E6 (gpt-5, 1000-boot)  | Bootstrap 95% CI | **0.07 [0.00, 0.17]** | 0.53–1.00 |
| E7 | 3-persona collusion | catches both sleepers | naive agreement wrongly denies the honest agent (OER 0.42) |
| E8 (gpt-5) | Indirect prompt injection | **0.06** | 0.86 |
| E9 | Per-layer ablation | epistemic is the sole load-bearing signal | — |
| E13 (N=50, K=10) | Byzantine chain | **0.00** | — |
| E16 (perfect calibration) | Adaptive attacker | 0.17 → **0.22** | attacker confidence collapses to ρ ≈ 0.30 |

Full table with bootstrap CIs and Wilcoxon $p$-values in [`final/SUMMARY.md`](final/SUMMARY.md).

## Paper

Full LaTeX source is in [`ACM_Conference_Proceedings_Primary_Article_Template/sigconf.tex`](ACM_Conference_Proceedings_Primary_Article_Template/sigconf.tex) (main body + Appendices A–H, 23 pages). To compile:

```bash
cd ACM_Conference_Proceedings_Primary_Article_Template
pdflatex sigconf.tex
bibtex sigconf
pdflatex sigconf.tex
pdflatex sigconf.tex
```

The `anonymous` document-class option hides authors during review; strip it (and replace the placeholder `\acmDOI/\acmISBN/\copyrightyear`) for the camera-ready.

## Citation

The BibTeX entry will be added upon acceptance.

## License

The paper text is under submission to KDD 2027. Code is released for review reproducibility; a permissive open-source license will be applied to the camera-ready release.
