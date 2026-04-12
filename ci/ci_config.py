#!/usr/bin/env python3
"""Load CI configuration for ov-gfx-plugin."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "ci_versions.json"


def load_ci_config(config_path: str | Path | None = None) -> dict[str, object]:
    path = DEFAULT_CONFIG_PATH if config_path is None else Path(config_path)
    return json.loads(path.read_text(encoding="utf-8"))
