#!/usr/bin/env python3
"""Export GitHub Actions outputs from the ov-gfx-plugin CI config."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ci_config import DEFAULT_CONFIG_PATH, build_workflow_matrix, load_ci_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export CI config values to a GitHub output file.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--github-output", required=True)
    return parser.parse_args()


def append_output(path: Path, name: str, value: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> int:
    args = parse_args()
    config = load_ci_config(args.config)
    outputs = {
        "matrix": json.dumps(build_workflow_matrix(config), separators=(",", ":")),
    }
    output_path = Path(args.github_output)
    for key, value in outputs.items():
        append_output(output_path, key, value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
