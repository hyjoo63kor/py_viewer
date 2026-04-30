"""공통 테스트 fixture."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp_cls() -> type[QApplication]:
    """pytest-qt에서 사용할 QApplication 클래스를 반환한다."""
    return QApplication


@pytest.fixture(autouse=True)
def _ensure_qapp(qapp: QApplication) -> None:
    """모든 테스트에서 QApplication 인스턴스를 보장한다."""


@pytest.fixture()
def tmp_file(tmp_path: Path) -> Path:
    """임시 테스트 파일 경로를 반환한다."""
    return tmp_path / "test_file"
