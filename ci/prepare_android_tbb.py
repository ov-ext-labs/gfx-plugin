#!/usr/bin/env python3
"""Prepare an Android oneTBB build that matches the OpenVINO Android build flow."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE_ROOT = REPO_ROOT / ".ci" / "android-deps"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and export Android oneTBB for downstream OpenVINO builds.")
    parser.add_argument("--github-env", default=os.environ.get("GITHUB_ENV", ""))
    parser.add_argument("--cache-root", default=str(DEFAULT_CACHE_ROOT))
    parser.add_argument("--tbb-repo", default="https://github.com/uxlfoundation/oneTBB")
    parser.add_argument("--tbb-ref", default="v2022.3.0")
    parser.add_argument("--android-abi", default="arm64-v8a")
    parser.add_argument("--android-platform", default="36")
    parser.add_argument("--android-stl", default="c++_shared")
    return parser.parse_args()


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", shlex.join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=REPO_ROOT if cwd is None else cwd)


def append_env(github_env: Path, name: str, value: str) -> None:
    with github_env.open("a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def ensure_clone(source_dir: Path, repo: str, ref: str) -> None:
    if source_dir.exists():
        run(["git", "-C", str(source_dir), "fetch", "--tags", "origin"])
        run(["git", "-C", str(source_dir), "checkout", ref])
        return
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--branch", ref, "--depth", "1", repo, str(source_dir)])


def main() -> int:
    args = parse_args()
    android_ndk_root = os.environ.get("ANDROID_NDK_ROOT") or os.environ.get("ANDROID_NDK_HOME")
    if not android_ndk_root:
        raise RuntimeError("ANDROID_NDK_ROOT or ANDROID_NDK_HOME must be set before preparing Android oneTBB")
    if not args.github_env:
        raise RuntimeError("GITHUB_ENV must be set or passed through --github-env")

    cache_root = Path(args.cache_root).resolve()
    version_token = args.tbb_ref.lstrip("v")
    deps_root = cache_root / f"one-tbb-{version_token}"
    source_dir = deps_root / "src"
    build_dir = deps_root / "build"
    install_dir = deps_root / "install"
    toolchain_file = Path(android_ndk_root) / "build" / "cmake" / "android.toolchain.cmake"

    ensure_clone(source_dir, args.tbb_repo, args.tbb_ref)
    if not (install_dir / "lib" / "cmake" / "TBB").exists():
        build_dir.mkdir(parents=True, exist_ok=True)
        run(
            [
                "cmake",
                "-S",
                str(source_dir),
                "-B",
                str(build_dir),
                "-DCMAKE_BUILD_TYPE=Release",
                f"-DCMAKE_INSTALL_PREFIX={install_dir}",
                f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
                f"-DANDROID_ABI={args.android_abi}",
                f"-DANDROID_PLATFORM={args.android_platform}",
                f"-DANDROID_STL={args.android_stl}",
                "-DTBB_TEST=OFF",
                '-DCMAKE_SHARED_LINKER_FLAGS=-Wl,--undefined-version',
            ]
        )
        run(["cmake", "--build", str(build_dir), "--parallel"])
        run(["cmake", "--install", str(build_dir)])

    github_env = Path(args.github_env)
    env_map = {
        "OV_ANDROID_TBB_REPO": args.tbb_repo,
        "OV_ANDROID_TBB_REF": args.tbb_ref,
        "OV_ANDROID_TBB_SOURCE_DIR": str(source_dir),
        "OV_ANDROID_TBB_INSTALL_DIR": str(install_dir),
        "TBBROOT": str(install_dir),
        "TBB_DIR": str(install_dir / "lib" / "cmake" / "TBB"),
    }
    for key, value in env_map.items():
        print(f"{key}={value}")
        append_env(github_env, key, value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
