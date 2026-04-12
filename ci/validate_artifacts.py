#!/usr/bin/env python3
"""Validate standalone gfx-plugin build artifacts."""

from __future__ import annotations

import platform
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / ".ci" / "build"
OUTPUT_ROOTS = (
    BUILD_DIR,
    REPO_ROOT / "bin",
)


def expected_library_names() -> list[str]:
    system = platform.system()
    if system == "Windows":
        return ["openvino_gfx_plugin.dll"]
    if system == "Darwin":
        return ["libopenvino_gfx_plugin.so", "libopenvino_gfx_plugin.dylib"]
    return ["libopenvino_gfx_plugin.so"]


def main() -> int:
    for expected_name in expected_library_names():
        for root in OUTPUT_ROOTS:
            if not root.exists():
                continue
            matches = sorted(root.rglob(expected_name))
            if matches:
                print(f"Validated {matches[0]}")
                return 0
    names = ", ".join(expected_library_names())
    roots = ", ".join(str(root) for root in OUTPUT_ROOTS)
    raise FileNotFoundError(f"No expected artifact ({names}) found under any of: {roots}")


if __name__ == "__main__":
    raise SystemExit(main())
