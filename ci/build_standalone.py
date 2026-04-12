#!/usr/bin/env python3
"""Build ov-gfx-plugin standalone against a prepared OpenVINO install tree."""

from __future__ import annotations

import argparse
import os
import platform
import shlex
import subprocess
from pathlib import Path

from ci_config import load_ci_config


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / ".ci" / "build"


def run(cmd: list[str]) -> None:
    print("+", shlex.join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ov-gfx-plugin against a prepared OpenVINO install tree.")
    parser.add_argument("--target-platform", choices=("host", "android", "rpi"), default="host")
    parser.add_argument("--config", default="")
    parser.add_argument("--android-abi", default="")
    parser.add_argument("--android-platform", default="")
    parser.add_argument("--android-stl", default="")
    parser.add_argument("--toolchain-file", default="")
    return parser.parse_args()


def configure_args(options: argparse.Namespace) -> list[str]:
    developer_package_dir = os.environ.get("OpenVINODeveloperPackage_DIR")
    if not developer_package_dir:
        raise RuntimeError("OpenVINODeveloperPackage_DIR must be set")
    openvino_dir = os.environ.get("OpenVINO_DIR")

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
    if openvino_dir:
        cmake_args.append(f"-DOpenVINO_DIR={openvino_dir}")
    if options.target_platform == "android":
        config = load_ci_config(options.config or None)["android"]
        android_abi = options.android_abi or str(config["abi"])
        android_platform = options.android_platform or str(config["api_level"])
        android_stl = options.android_stl or str(config["stl"])
        android_ndk_root = os.environ.get("ANDROID_NDK_ROOT") or os.environ.get("ANDROID_NDK_HOME")
        if not android_ndk_root:
            raise RuntimeError("ANDROID_NDK_ROOT or ANDROID_NDK_HOME must be set for Android cross-builds")
        args_list = [
            f"-DCMAKE_TOOLCHAIN_FILE={Path(android_ndk_root) / 'build' / 'cmake' / 'android.toolchain.cmake'}",
            f"-DANDROID_ABI={android_abi}",
            f"-DANDROID_PLATFORM={android_platform}",
            f"-DANDROID_STL={android_stl}",
            "-DGFX_ENABLE_METAL=OFF",
        ]
        cmake_args.extend(args_list)
    elif options.target_platform == "rpi":
        toolchain_file = options.toolchain_file or os.environ.get("GFX_RPI_TOOLCHAIN_FILE")
        if not toolchain_file:
            raise RuntimeError("GFX_RPI_TOOLCHAIN_FILE or --toolchain-file must be set for Raspberry Pi cross-builds")
        cmake_args.extend(
            [
                f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
                "-DGFX_ENABLE_METAL=OFF",
                "-DGFX_DEFAULT_BACKEND=vulkan",
            ]
        )
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
