#!/usr/bin/env python3
"""Export GitHub Actions outputs from the ov-gfx-plugin CI config."""

from __future__ import annotations

import argparse
from pathlib import Path

from ci_config import DEFAULT_CONFIG_PATH, load_ci_config


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
    android = config["android"]
    tbb = android["tbb"]
    outputs = {
        "android_abi": android["abi"],
        "android_api_level": android["api_level"],
        "android_stl": android["stl"],
        "android_ndk_version": android["ndk_version"],
        "android_sdk_packages": " ".join(android["sdk_packages"]),
        "android_tbb_repo": tbb["repo"],
        "android_tbb_ref": tbb["ref"],
        "android_openvino_cmake_args": " ".join(
            [
                "-DCMAKE_TOOLCHAIN_FILE=${ANDROID_NDK_ROOT}/build/cmake/android.toolchain.cmake",
                f"-DANDROID_ABI={android['abi']}",
                f"-DANDROID_PLATFORM={android['api_level']}",
                f"-DANDROID_STL={android['stl']}",
                "-DTBBROOT=${OV_ANDROID_TBB_INSTALL_DIR}",
                "-DTBB_DIR=${OV_ANDROID_TBB_INSTALL_DIR}/lib/cmake/TBB",
                "-DENABLE_INTEL_CPU=OFF",
                "-DENABLE_INTEL_GPU=OFF",
                "-DENABLE_INTEL_NPU=OFF",
                "-DENABLE_PYTHON=OFF",
                "-DENABLE_JS=OFF",
                "-DENABLE_SAMPLES=OFF",
                "-DENABLE_TESTS=OFF",
                "-DENABLE_OV_ONNX_FRONTEND=OFF",
                "-DENABLE_OV_PADDLE_FRONTEND=OFF",
                "-DENABLE_OV_TF_FRONTEND=OFF",
                "-DENABLE_OV_TF_LITE_FRONTEND=OFF",
            ]
        ),
    }
    output_path = Path(args.github_output)
    for key, value in outputs.items():
        append_output(output_path, key, str(value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
