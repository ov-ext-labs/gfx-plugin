#!/usr/bin/env python3
"""Load and normalize CI configuration for ov-gfx-plugin."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "ci_versions.json"


def load_ci_config(config_path: str | Path | None = None) -> dict[str, Any]:
    path = DEFAULT_CONFIG_PATH if config_path is None else Path(config_path)
    return json.loads(path.read_text(encoding="utf-8"))


def get_platform_entries(config: dict[str, Any]) -> list[dict[str, Any]]:
    entries = config.get("platforms")
    if not isinstance(entries, list) or not entries:
        raise ValueError("CI config must define a non-empty 'platforms' list")
    return entries


def get_platform_config(
    config: dict[str, Any],
    *,
    platform_key: str | None = None,
    target_platform: str | None = None,
) -> dict[str, Any]:
    entries = get_platform_entries(config)
    if platform_key:
        for entry in entries:
            if entry.get("key") == platform_key:
                return entry
        raise ValueError(f"Unknown CI platform key: {platform_key}")
    if target_platform:
        matches = [entry for entry in entries if entry.get("target_platform") == target_platform]
        if len(matches) != 1:
            raise ValueError(
                f"Expected exactly one CI platform for target_platform={target_platform!r}, found {len(matches)}"
            )
        return matches[0]
    raise ValueError("Either platform_key or target_platform must be provided")


def join_shell_args(items: list[str]) -> str:
    return " ".join(str(item) for item in items)


def default_build_command(target_platform: str) -> str:
    if target_platform == "host":
        return "python3 ci/build_standalone.py"
    return f"python3 ci/build_standalone.py --target-platform {target_platform}"


def build_openvino_cmake_args(defaults: dict[str, Any], platform: dict[str, Any]) -> str:
    openvino_defaults = defaults["openvino"]
    platform_openvino = platform.get("openvino", {})
    args = list(openvino_defaults.get("cmake_args_common", []))
    if platform.get("target_platform") == "android":
        android = platform["android"]
        args.extend(
            [
                "-DCMAKE_TOOLCHAIN_FILE=${ANDROID_NDK_ROOT}/build/cmake/android.toolchain.cmake",
                f"-DANDROID_ABI={android['abi']}",
                f"-DANDROID_PLATFORM={android['api_level']}",
                f"-DANDROID_STL={android['stl']}",
                "-DTBBROOT=${OV_ANDROID_TBB_INSTALL_DIR}",
                "-DTBB_DIR=${OV_ANDROID_TBB_INSTALL_DIR}/lib/cmake/TBB",
            ]
        )
    args.extend(platform_openvino.get("cmake_args", []))
    return join_shell_args(args)


def build_workflow_matrix(config: dict[str, Any]) -> list[dict[str, str]]:
    defaults = config["defaults"]
    openvino_defaults = defaults["openvino"]
    matrix: list[dict[str, str]] = []
    for platform in get_platform_entries(config):
        platform_openvino = platform.get("openvino", {})
        packages = list(openvino_defaults.get("ubuntu_packages_common", []))
        packages.extend(platform_openvino.get("ubuntu_packages", []))
        entry = {
            "name": str(platform["key"]),
            "job_name": str(platform["job_name"]),
            "runs_on": str(platform["runs_on"]),
            "target_platform": str(platform["target_platform"]),
            "submodules": str(platform.get("submodules", defaults["submodules"])),
            "validation_command": str(platform.get("validation_command", defaults["validation_command"])),
            "test_command": str(platform.get("test_command", defaults["test_command"])),
            "dependency_setup_command": str(platform.get("dependency_setup_command", "")),
            "build_command": str(platform.get("build_command", default_build_command(str(platform["target_platform"])))),
            "openvino_repo": str(platform_openvino.get("repo", openvino_defaults["repo"])),
            "openvino_ref": str(platform_openvino.get("ref", openvino_defaults["ref"])),
            "openvino_submodules": str(platform_openvino.get("submodules", openvino_defaults["submodules"])),
            "openvino_ubuntu_packages": join_shell_args(packages),
            "openvino_cmake_args": build_openvino_cmake_args(defaults, platform),
            "android_ndk_version": "",
            "android_sdk_packages": "",
        }
        if platform.get("target_platform") == "android":
            android = platform["android"]
            entry["android_ndk_version"] = str(android["ndk_version"])
            entry["android_sdk_packages"] = join_shell_args(list(android["sdk_packages"]))
        matrix.append(entry)
    return matrix
