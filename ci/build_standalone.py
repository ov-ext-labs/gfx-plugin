#!/usr/bin/env python3
"""Build ov-gfx-plugin standalone against a prepared OpenVINO install tree."""

from __future__ import annotations

import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ov-gfx-plugin against a prepared OpenVINO install tree.")
    parser.add_argument("--target-platform", choices=("host", "android"), default="host")
    parser.add_argument("--android-abi", default="arm64-v8a")
    parser.add_argument("--android-platform", default="android-24")
    parser.add_argument("--android-stl", default="c++_shared")
    return parser.parse_args()


def configure_args(options: argparse.Namespace) -> list[str]:
    developer_package_dir = os.environ.get("OpenVINODeveloperPackage_DIR")
    if not developer_package_dir:
        raise RuntimeError("OpenVINODeveloperPackage_DIR must be set")

    cmake_args = [
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
    if options.target_platform == "android":
        android_ndk_root = os.environ.get("ANDROID_NDK_ROOT") or os.environ.get("ANDROID_NDK_HOME")
        if not android_ndk_root:
            raise RuntimeError("ANDROID_NDK_ROOT or ANDROID_NDK_HOME must be set for Android cross-builds")
        args_list = [
            f"-DCMAKE_TOOLCHAIN_FILE={Path(android_ndk_root) / 'build' / 'cmake' / 'android.toolchain.cmake'}",
            f"-DANDROID_ABI={options.android_abi}",
            f"-DANDROID_PLATFORM={options.android_platform}",
            f"-DANDROID_STL={options.android_stl}",
            "-DGFX_ENABLE_METAL=OFF",
        ]
        cmake_args.extend(args_list)
    elif platform.system() == "Linux":
        cmake_args.append("-DGFX_ENABLE_METAL=OFF")
    return cmake_args


def main() -> int:
    args = parse_args()
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    run(configure_args(args))
    run(["cmake", "--build", str(BUILD_DIR), "--parallel"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
