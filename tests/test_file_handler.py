"""file_handler 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from my_app.file_handler import (
    FileFormat,
    FileValidationError,
    detect_format,
    validate_file,
)

# ---------------------------------------------------------------------------
# detect_format 단위 테스트
# ---------------------------------------------------------------------------


class TestDetectFormat:
    """detect_format 함수 단위 테스트."""

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("image.png", FileFormat.PNG),
            ("image.jpg", FileFormat.JPG),
            ("image.jpeg", FileFormat.JPG),
            ("document.pdf", FileFormat.PDF),
            ("graphic.svg", FileFormat.SVG),
        ],
    )
    def test_supported_extensions(self, filename: str, expected: FileFormat) -> None:
        """각 지원 형식에 대해 올바른 FileFormat을 반환한다."""
        assert detect_format(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename",
        ["image.PNG", "image.Jpg", "image.JPEG", "doc.PDF", "graphic.SVG"],
    )
    def test_case_insensitive(self, filename: str) -> None:
        """대소문자 혼합 확장자를 올바르게 처리한다."""
        result = detect_format(Path(filename))
        assert isinstance(result, FileFormat)

    @pytest.mark.parametrize(
        "filename",
        ["file.txt", "file.bmp", "file.gif", "file.doc", "file"],
    )
    def test_unsupported_extension_raises(self, filename: str) -> None:
        """지원하지 않는 확장자에 대해 FileValidationError를 발생시킨다."""
        with pytest.raises(FileValidationError, match="지원하지 않는 파일 형식입니다"):
            detect_format(Path(filename))


# ---------------------------------------------------------------------------
# validate_file 단위 테스트
# ---------------------------------------------------------------------------


class TestValidateFile:
    """validate_file 함수 단위 테스트."""

    def test_valid_file(self, tmp_path: Path) -> None:
        """유효한 파일에 대해 FileInfo를 반환한다."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        result = validate_file(str(test_file))

        assert result.format == FileFormat.PNG
        assert result.path == test_file
        assert result.size > 0

    def test_nonexistent_file_raises(self) -> None:
        """존재하지 않는 파일에 대해 FileValidationError를 발생시킨다."""
        with pytest.raises(FileValidationError, match="파일을 읽을 수 없습니다"):
            validate_file("/nonexistent/path/file.png")

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        """지원하지 않는 형식에 대해 FileValidationError를 발생시킨다."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        with pytest.raises(FileValidationError, match="지원하지 않는 파일 형식입니다"):
            validate_file(str(test_file))
