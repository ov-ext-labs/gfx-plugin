from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str) -> None:
    target = ROOT / path
    if not target.exists():
        raise SystemExit(f"Missing required path: {path}")


def require_gitmodules_entry(text: str, path: str, url: str) -> None:
    if path not in text or url not in text:
        raise SystemExit(f"Missing submodule entry for {path}")


def main() -> None:
    for path in [
        "CMakeLists.txt",
        "src/CMakeLists.txt",
        "docs/ARCHITECTURE.md",
        "config/ci_versions.json",
        "ci/ci_config.py",
        "ci/export_ci_config.py",
        "ci/prepare_android_tbb.py",
        "include/openvino/gfx_plugin/plugin.hpp",
        "ci/prepare_rpi_toolchain.py",
        "third_party/llvm-project",
        "third_party/Vulkan-Headers",
        "tools/gfx_rpi_vulkan_toolchain_builder.py",
    ]:
        require(path)

    gitmodules = (ROOT / ".gitmodules").read_text(encoding="utf-8")
    require_gitmodules_entry(
        gitmodules,
        "third_party/llvm-project",
        "https://github.com/llvm/llvm-project.git",
    )
    require_gitmodules_entry(
        gitmodules,
        "third_party/Vulkan-Headers",
        "https://github.com/KhronosGroup/Vulkan-Headers.git",
    )

    print("gfx-plugin repository layout looks valid")


if __name__ == "__main__":
    main()
