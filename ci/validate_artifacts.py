#!/usr/bin/env python3
"""Validate standalone ov-gfx-plugin build artifacts."""

from __future__ import annotations

import platform
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / ".ci" / "build"


def expected_library_name() -> str:
    if platform.system() == "Windows":
        return "openvino_gfx_plugin.dll"
    return "libopenvino_gfx_plugin.so"


def main() -> int:
    matches = sorted(BUILD_DIR.rglob(expected_library_name()))
    if not matches:
        raise FileNotFoundError(f"No {expected_library_name()} artifact found under {BUILD_DIR}")
    print(f"Validated {matches[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
