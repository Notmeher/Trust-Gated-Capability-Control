"""Output helpers rooted at ``<repo>/nextphase/``."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from tgcc.config import repo_root


def _to_native(x: Any) -> Any:
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, dict):
        return {str(k): _to_native(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_to_native(v) for v in x]
    if isinstance(x, float) and (x != x or x in (float("inf"), float("-inf"))):
        return str(x)
    return x


def nextphase_root() -> Path:
    root = repo_root() / "nextphase"
    root.mkdir(parents=True, exist_ok=True)
    return root


def exp_dir(experiment: str) -> Path:
    root = nextphase_root() / experiment
    (root / "figures").mkdir(parents=True, exist_ok=True)
    return root


def data_root() -> Path:
    """Shared raw data (LLM response banks, datasets) used by several experiments."""
    root = nextphase_root() / "_data"
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_results(experiment: str, payload: dict) -> Path:
    out = exp_dir(experiment) / "results.json"
    stamped = {
        "experiment": experiment,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    out.write_text(json.dumps(_to_native(stamped), indent=2), encoding="utf-8")
    return out


def write_readme(experiment: str, markdown: str) -> Path:
    p = exp_dir(experiment) / "README.md"
    p.write_text(markdown, encoding="utf-8")
    return p


def figure_path(experiment: str, name: str) -> Path:
    return exp_dir(experiment) / "figures" / name


def read_results(experiment: str) -> dict:
    return json.loads((exp_dir(experiment) / "results.json").read_text(encoding="utf-8"))
