"""Helpers for writing ``results.json`` and ``README.md`` under ``final/``."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from tgcc.config import final_dir


def _to_native(x: Any) -> Any:
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, dict):
        return {str(k): _to_native(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_to_native(v) for v in x]
    if isinstance(x, float) and (x != x or x in (float("inf"), float("-inf"))):
        return str(x)
    return x


def write_results(experiment: str, payload: dict) -> Path:
    """Write ``final/<experiment>/results.json`` and return the path."""
    root = final_dir(experiment)
    out = root / "results.json"
    stamped = {
        "experiment": experiment,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    out.write_text(json.dumps(_to_native(stamped), indent=2), encoding="utf-8")
    return out


def write_readme(experiment: str, markdown: str) -> Path:
    root = final_dir(experiment)
    p = root / "README.md"
    p.write_text(markdown, encoding="utf-8")
    return p


def figure_path(experiment: str, name: str) -> Path:
    root = final_dir(experiment) / "figures"
    root.mkdir(parents=True, exist_ok=True)
    return root / name
