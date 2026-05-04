"""프로젝트 캐시 및 빌드 산출물을 제거하는 스크립트."""

from __future__ import annotations

import shutil
from pathlib import Path

TARGETS = [
    # Python 캐시
    "**/__pycache__",
    "**/*.pyc",
    # mypy 캐시
    ".mypy_cache",
    # pytest 캐시
    ".pytest_cache",
    # ruff 캐시
    ".ruff_cache",
    # PyInstaller 빌드 산출물
    "build",
    "dist",
    # hypothesis 캐시
    ".hypothesis",
]


def clean() -> None:
    """TARGETS에 해당하는 파일/디렉토리를 삭제한다."""
    root = Path.cwd()
    venv_dir = root / ".venv"
    removed: list[str] = []

    for pattern in TARGETS:
        for path in sorted(root.glob(pattern)):
            # .venv 내부는 건드리지 않는다
            if venv_dir in path.parents or path == venv_dir:
                continue
            rel = path.relative_to(root)
            if path.is_dir():
                shutil.rmtree(path)
                removed.append(f"  removed dir:  {rel}")
            elif path.is_file():
                path.unlink()
                removed.append(f"  removed file: {rel}")

    if removed:
        print(f"Cleaned {len(removed)} item(s):")
        for line in removed:
            print(line)
    else:
        print("Nothing to clean.")


if __name__ == "__main__":
    clean()
