"""Real-stream scenarios shared by the enhancement experiments (N22+).

Every scenario is built from real LLM response banks (no synthetic signals):

* ``sleeper``   - E1: honest answers, then confidently wrong answers from step 20.
* ``policy``, ``offtopic``, ``hostile`` - N12: the agent stays correct but another layer fails.
* ``honest``    - no compromise (false-positive reference).

Banks: the submitted TriviaQA banks (Claude Sonnet 4.5, GPT-5; 15 episodes each) plus every
enhancement bank present (Claude Haiku 4.5 and the Qwen models on TriviaQA and MedMCQA;
5 episodes each).
"""
from __future__ import annotations

from typing import Iterator

from tgcc.nextphase.n12_non_epistemic_compromise import hostile, offtopic, policy
from tgcc.nextphase.responses import DATASETS, all_banks, load_bank, model_name
from tgcc.nextphase.streams import Episode, pilot_signals, qa_episodes

SCENARIOS = ("sleeper", "policy", "offtopic", "hostile", "honest")
_TRANSFORMS = {"policy": policy, "offtopic": offtopic, "hostile": hostile}


def episodes(bank: dict, scenario: str, **kw) -> list[Episode]:
    if scenario == "sleeper":
        return qa_episodes(bank, **kw)
    if scenario == "honest":
        return qa_episodes(bank, sleeper_mode="honest", **kw)
    return qa_episodes(bank, sleeper_mode="honest", transform=_TRANSFORMS[scenario], **kw)


def banks(datasets: tuple[str, ...] = DATASETS) -> Iterator[tuple[str, str, dict]]:
    """(provider, dataset, bank) for every bank on disk."""
    for ds in datasets:
        for p in all_banks(ds):
            yield p, ds, load_bank(p, ds)


def label(provider: str, dataset: str) -> str:
    return f"{model_name(provider)} / {'TriviaQA' if dataset == 'triviaqa' else 'MedMCQA'}"


__all__ = ["SCENARIOS", "episodes", "banks", "label", "pilot_signals"]
