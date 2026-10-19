# Trust-Gated Capability Control (TGCC)

**An Operational Framework for Breaking the Trust–Vulnerability Paradox in Multi-Agent LLM Systems**

> ⚠️ **Under double-blind review.** Author identity is intentionally omitted from this repository. Reviewers should use the anonymized mirror:
> <https://anonymous.4open.science/r/Trust-Gated-Capability-Control-AE81/>

## Overview

TGCC turns a five-layer trust stack (epistemic → behavioural → role → social → institutional) into a
runtime controller that grants or revokes capabilities. It combines:

* Beta beliefs per layer;
* a cross-layer synergy (coupling) operator;
* Hedge adaptive weights;
* a power-mean composite.

A capability is granted only if both of these hold:

* the composite is at or above θ_c;
* a per-turn epistemic check is at or above θ_{c,1}.

Thresholds come from Algorithm 2: the δ-quantile of a pre-warmed honest pilot, minus ε.

## Repository layout

```
├── src/tgcc/
│   ├── beta_belief.py, synergy.py, composite.py, hedge.py, controller.py   # the controller
│   ├── probes.py            # per-layer check-signal probes
│   ├── models.py, config.py # cached LLM client (Claude Sonnet 4.5, GPT-5)
│   ├── data_qa.py, episodes.py
│   └── nextphase/           # all experiments (N01–N21) + shared infrastructure
├── nextphase/               # results: one folder per experiment (README.md, results.json, figures/)
│   ├── README.md            # experiment index
│   ├── SUMMARY.md           # consolidated results
│   ├── CHANGES.md           # bug fixes, method definition, reproduction commands
│   └── _data/               # datasets and LLM response banks used by the experiments
├── cache/llm/               # disk cache of every LLM call used by the experiments
├── manuscript_update.md     # section-by-section revision plan for the paper
├── peer_review.md           # reviews
└── 1175_Trust_Gated_Capability_Co.pdf
```

## Installation

Requires Python 3.12 and [`uv`](https://github.com/astral-sh/uv):

```bash
uv sync
```

API keys are only needed to make *new* LLM calls. With `cache/llm/` and `nextphase/_data/` present,
every experiment runs offline. For new calls, create a `.env` at the repo root:

```
ANTHROPIC_API_KEY=...
ANTHROPIC_WORKSPACE_ID=...        # optional
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-5
```

## Reproducing the experiments

```bash
python -m tgcc.nextphase.n01_e1_multi_episode     # E1
python -m tgcc.nextphase.n02_real_stream_sensitivity
...
python -m tgcc.nextphase.n21_learned_coupling
```

The full ordered list is in [nextphase/CHANGES.md](nextphase/CHANGES.md#4-how-to-reproduce), and the
mapping from experiments to the paper is in [nextphase/README.md](nextphase/README.md).

## Headline results (Claude Sonnet 4.5 / GPT-5)

| Experiment | TGCC | Reference |
|---|---|---|
| E1 sleeper, 15 episodes per model (N01) | OER 0.02 / 0.01, latency 0.6 / 0.2 steps | Naive behavioural OER 1.00 |
| Non-epistemic compromise (N12) | OER 0.06–0.15 | Epistemic-only / memoryless 0.57–0.83 |
| HumanEval, reviewer-LLM critic (N09) | 92% / 81% harmful commits blocked | TGCC-Smoothed 61% / 46% |
| Prompt injection (N14) | harmful admission 0.02 / 0.01 | Naive 0.41 / 0.16 |
| Collusion (N13) | colluder OER 0.02 / 0.01 | majority vote: wrong team answer 1.00 |

See [nextphase/SUMMARY.md](nextphase/SUMMARY.md) for all results with confidence intervals.

## License

The paper is under review. Code is released for review reproducibility; a permissive open-source
license will be applied to the camera-ready release.
