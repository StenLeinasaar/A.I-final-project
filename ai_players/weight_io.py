"""JSON weight checkpoint I/O for linear Q-learning / SARSA agents.

Checkpoints are versioned and must match FEATURE_DIM from feature_utils.
Old text logs (q_weights_alpha*_0, sarsa_weights_*, weights_0, …) are obsolete
and incompatible with FEATURE_DIM=26 — do not load them.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from glob import glob
from typing import Any, Iterable, List, Optional, Sequence, Union

from feature_utils import FEATURE_DIM, FEATURE_NAMES

FORMAT_VERSION = 1

WeightsLike = Union[Sequence[float], Iterable[float]]


def _filename_slug(algorithm: str) -> str:
    """Filesystem slug: q_learning / sarsa (JSON algorithm field still uses q-learning)."""
    algo = _normalize_algorithm(algorithm)
    return "q_learning" if algo == "q-learning" else algo


def default_checkpoint_path(algorithm: str, alpha: float) -> str:
    """Return path relative to Game_logic cwd: weights/{algo}_alpha{alpha}.json."""
    slug = _filename_slug(algorithm)
    alpha_str = _format_alpha(alpha)
    return os.path.join("weights", f"{slug}_alpha{alpha_str}.json")


def save_checkpoint(
    path: str,
    weights: WeightsLike,
    *,
    algorithm: str,
    alpha: float,
    gamma: float = 1.0,
    epsilon: float = 0.0,
    games_trained: int = 0,
    feature_names: Optional[List[str]] = None,
    also_history: bool = True,
) -> str:
    """Write a JSON checkpoint. Overwrites ``path``; optionally copies under history/."""
    weights_list = [float(w) for w in weights]
    if len(weights_list) != FEATURE_DIM:
        raise ValueError(
            f"Cannot save checkpoint: expected FEATURE_DIM={FEATURE_DIM} weights, "
            f"got {len(weights_list)}"
        )

    algo = _normalize_algorithm(algorithm)
    payload = {
        "format_version": FORMAT_VERSION,
        "feature_dim": FEATURE_DIM,
        "algorithm": algo,
        "alpha": float(alpha),
        "gamma": float(gamma),
        "epsilon": float(epsilon),
        "games_trained": int(games_trained),
        "weights": weights_list,
        "feature_names": list(feature_names) if feature_names is not None else list(FEATURE_NAMES),
    }

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")

    if also_history:
        history_dir = os.path.join(directory or "weights", "history")
        os.makedirs(history_dir, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = os.path.splitext(os.path.basename(path))[0]
        history_path = os.path.join(history_dir, f"{base}_{stamp}.json")
        with open(history_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
            fh.write("\n")

    return path


def load_checkpoint(path: str) -> dict:
    """Load and validate a checkpoint. Raises ValueError on format/dim mismatch."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError(f"Checkpoint {path!r} is not a JSON object")

    version = data.get("format_version")
    if version != FORMAT_VERSION:
        raise ValueError(
            f"Unsupported checkpoint format_version={version!r} in {path!r} "
            f"(expected {FORMAT_VERSION}). Old text weight logs are obsolete."
        )

    feature_dim = data.get("feature_dim")
    if feature_dim != FEATURE_DIM:
        raise ValueError(
            f"Checkpoint feature_dim={feature_dim} does not match current "
            f"FEATURE_DIM={FEATURE_DIM} ({path!r}). Pre-FEATURE_DIM=26 logs are "
            f"incompatible — retrain and save a new JSON checkpoint."
        )

    weights = data.get("weights")
    if not isinstance(weights, list) or len(weights) != FEATURE_DIM:
        got = len(weights) if isinstance(weights, list) else type(weights).__name__
        raise ValueError(
            f"Checkpoint weights length mismatch in {path!r}: expected "
            f"{FEATURE_DIM}, got {got}"
        )

    data["weights"] = [float(w) for w in weights]
    data["algorithm"] = _normalize_algorithm(data.get("algorithm", "q-learning"))
    return data


def find_auto_checkpoint(algorithm: str, weights_dir: str = "weights") -> Optional[str]:
    """Pick a default checkpoint under weights/ for the given algorithm, if any.

    Prefers the conventional ``{algo}_alpha*.json`` name; otherwise the newest
    matching ``{algo}*.json`` by mtime.
    """
    algo = _normalize_algorithm(algorithm)
    slug = _filename_slug(algo)
    if not os.path.isdir(weights_dir):
        return None

    preferred = sorted(glob(os.path.join(weights_dir, f"{slug}_alpha*.json")))
    # Prefer alpha0.3 for q-learning and alpha0.2 for sarsa when present
    preferred_alphas = {
        "q-learning": "alpha0.3",
        "sarsa": "alpha0.2",
    }
    hint = preferred_alphas.get(algo)
    if hint:
        for path in preferred:
            if hint in os.path.basename(path):
                return path
    if preferred:
        return preferred[0]

    candidates = sorted(
        glob(os.path.join(weights_dir, f"{slug}*.json")),
        key=lambda p: os.path.getmtime(p),
        reverse=True,
    )
    return candidates[0] if candidates else None


def _normalize_algorithm(algorithm: str) -> str:
    value = (algorithm or "").strip().lower().replace("_", "-")
    if value in ("q", "qlearning", "q-learning", "ai"):
        return "q-learning"
    if value in ("sarsa",):
        return "sarsa"
    raise ValueError(f"Unknown algorithm {algorithm!r}; expected 'q-learning' or 'sarsa'")


def _format_alpha(alpha: float) -> str:
    text = f"{float(alpha):.10f}".rstrip("0").rstrip(".")
    return text if text else "0"
