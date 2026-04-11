#!/usr/bin/env python3
"""Build and export the Raspberry Pi Vulkan cross-toolchain bundle for CI."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / ".ci" / "toolchains" / "rpi-vulkan"
TOOLCHAIN_BUILDER = REPO_ROOT / "tools" / "gfx_rpi_vulkan_toolchain_builder.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare the Raspberry Pi Vulkan toolchain bundle for CI.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--sysroot-profile", default="rpi5-bookworm")
    parser.add_argument("--github-env", default=os.environ.get("GITHUB_ENV", ""))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def run(cmd: list[str], *, dry_run: bool) -> None:
    print("+", shlex.join(cmd), flush=True)
    if dry_run:
        return
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def append_env(github_env: Path, name: str, value: str, *, dry_run: bool) -> None:
    print(f"{name}={value}")
    if dry_run:
        return
    with github_env.open("a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    toolchain_file = output_dir / "cmake" / "gfx-rpi-vulkan-aarch64.toolchain.cmake"
    sysroot_dir = output_dir / "sysroot"

    command = [
        "python3",
        str(TOOLCHAIN_BUILDER),
        "--output-dir",
        str(output_dir),
        "--sysroot-profile",
        args.sysroot_profile,
    ]
    if args.dry_run:
        command.append("--dry-run")
    run(command, dry_run=args.dry_run)

    if args.github_env:
        github_env = Path(args.github_env)
        append_env(github_env, "GFX_RPI_TOOLCHAIN_ROOT", str(output_dir), dry_run=args.dry_run)
        append_env(github_env, "GFX_RPI_TOOLCHAIN_FILE", str(toolchain_file), dry_run=args.dry_run)
        append_env(github_env, "GFX_RPI_SYSROOT_DIR", str(sysroot_dir), dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
