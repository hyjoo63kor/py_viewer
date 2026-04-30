"""파일 검증/로드 모듈."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

SUPPORTED_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".png", ".jpg", ".jpeg", ".pdf", ".svg"}
)
MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024  # 100MB


class FileFormat(Enum):
    """지원하는 파일 형식."""

    PNG = "png"
    JPG = "jpg"
    PDF = "pdf"
    SVG = "svg"


@dataclass(frozen=True)
class FileInfo:
    """검증된 파일 정보."""

    path: Path
    format: FileFormat
    size: int


class FileValidationError(Exception):
    """파일 검증 실패 시 발생하는 예외."""


def detect_format(file_path: Path) -> FileFormat:
    """파일 확장자를 기반으로 FileFormat을 결정한다.

    Raises:
        FileValidationError: 지원하지 않는 확장자
    """
    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise FileValidationError("지원하지 않는 파일 형식입니다")
    if ext == ".png":
        return FileFormat.PNG
    if ext in (".jpg", ".jpeg"):
        return FileFormat.JPG
    if ext == ".pdf":
        return FileFormat.PDF
    # ext == ".svg"
    return FileFormat.SVG


def validate_file(file_path: str) -> FileInfo:
    """파일 경로를 검증하고 FileInfo를 반환한다.

    Raises:
        FileValidationError: 지원하지 않는 형식, 크기 초과, 파일 없음 등
    """
    path = Path(file_path)
    try:
        file_size = path.stat().st_size
    except OSError:
        raise FileValidationError(f"파일을 읽을 수 없습니다: {path.name}") from None
    if file_size > MAX_FILE_SIZE:
        raise FileValidationError("파일 크기가 너무 큽니다 (최대 100MB)")
    file_format = detect_format(path)
    return FileInfo(path=path, format=file_format, size=file_size)
