#!/usr/bin/env python3
"""Build ov-gfx-plugin standalone against a prepared OpenVINO install tree."""

from __future__ import annotations

import os
import platform
import shlex
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / ".ci" / "build"


def run(cmd: list[str]) -> None:
    print("+", shlex.join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def configure_args() -> list[str]:
    developer_package_dir = os.environ.get("OpenVINODeveloperPackage_DIR")
    if not developer_package_dir:
        raise RuntimeError("OpenVINODeveloperPackage_DIR must be set")

    args = [
        "cmake",
        "-S",
        str(REPO_ROOT),
        "-B",
        str(BUILD_DIR),
        "-G",
        "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DENABLE_TESTS=OFF",
        f"-DOpenVINODeveloperPackage_DIR={developer_package_dir}",
    ]
    if platform.system() == "Linux":
        args.append("-DGFX_ENABLE_METAL=OFF")
    return args


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    run(configure_args())
    run(["cmake", "--build", str(BUILD_DIR), "--parallel"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
