"""renderers 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPixmap

from my_app.file_handler import FileFormat, FileInfo
from my_app.renderers import (
    RenderError,
    render_file,
    render_image,
    render_pdf,
    render_svg,
    scale_pixmap,
)

# ---------------------------------------------------------------------------
# scale_pixmap 단위 테스트
# ---------------------------------------------------------------------------


class TestScalePixmap:
    """scale_pixmap 함수 단위 테스트."""

    def test_smaller_than_display_scales_up(self) -> None:
        """원본이 display_size보다 작으면 확대하여 display_size에 맞춘다."""
        img = QImage(100, 80, QImage.Format.Format_RGB888)
        img.fill(0)
        pixmap = QPixmap.fromImage(img)

        result = scale_pixmap(pixmap, QSize(800, 600))

        # 종횡비(100:80 = 5:4)를 유지하면서 800x600에 맞게 확대
        # 폭 기준: 800, 높이 = 800 * 80/100 = 640 > 600 → 높이 기준으로 스케일
        # 높이 기준: 600, 폭 = 600 * 100/80 = 750
        assert result.width() == 750
        assert result.height() == 600

    def test_larger_than_display_scales_down(self) -> None:
        """원본이 display_size보다 크면 축소한다."""
        img = QImage(1600, 1200, QImage.Format.Format_RGB888)
        img.fill(0)
        pixmap = QPixmap.fromImage(img)

        result = scale_pixmap(pixmap, QSize(800, 600))

        assert result.width() <= 800
        assert result.height() <= 600

    def test_preserves_aspect_ratio(self) -> None:
        """종횡비를 유지하면서 축소한다."""
        img = QImage(2000, 1000, QImage.Format.Format_RGB888)
        img.fill(0)
        pixmap = QPixmap.fromImage(img)

        result = scale_pixmap(pixmap, QSize(800, 600))

        original_ratio = 2000 / 1000
        result_ratio = result.width() / result.height()
        assert abs(original_ratio - result_ratio) < 0.02


# ---------------------------------------------------------------------------
# render_image 단위 테스트
# ---------------------------------------------------------------------------


class TestRenderImage:
    """render_image 함수 단위 테스트."""

    def test_render_png_success(self, tmp_path: Path) -> None:
        """PNG 파일 렌더링 성공 테스트."""
        png_path = tmp_path / "test.png"
        img = QImage(200, 150, QImage.Format.Format_RGB888)
        img.fill(0)
        img.save(str(png_path), "PNG")

        result = render_image(png_path, QSize(800, 600))

        assert not result.isNull()
        # 200x150 (4:3) → 800x600에 맞게 확대, 종횡비 유지
        assert result.width() == 800
        assert result.height() == 600

    def test_render_jpg_success(self, tmp_path: Path) -> None:
        """JPG 파일 렌더링 성공 테스트."""
        jpg_path = tmp_path / "test.jpg"
        img = QImage(200, 150, QImage.Format.Format_RGB888)
        img.fill(0)
        img.save(str(jpg_path), "JPEG")

        result = render_image(jpg_path, QSize(800, 600))

        assert not result.isNull()

    def test_render_corrupted_image_raises(self, tmp_path: Path) -> None:
        """손상된 이미지 파일에 대해 RenderError를 발생시킨다."""
        bad_path = tmp_path / "bad.png"
        bad_path.write_bytes(b"not a real image")

        with pytest.raises(RenderError, match="이미지 파일이 손상되었습니다"):
            render_image(bad_path, QSize(800, 600))


# ---------------------------------------------------------------------------
# render_svg 단위 테스트
# ---------------------------------------------------------------------------


class TestRenderSvg:
    """render_svg 함수 단위 테스트."""

    def test_render_svg_success(self, tmp_path: Path) -> None:
        """SVG 파일 렌더링 성공 테스트."""
        svg_path = tmp_path / "test.svg"
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
            '<rect width="100" height="100" fill="red"/>'
            "</svg>"
        )
        svg_path.write_text(svg_content, encoding="utf-8")

        result = render_svg(svg_path, QSize(800, 600))

        assert not result.isNull()

    def test_render_invalid_svg_raises(self, tmp_path: Path) -> None:
        """손상된 SVG 파일에 대해 RenderError를 발생시킨다."""
        bad_svg = tmp_path / "bad.svg"
        bad_svg.write_text("not valid svg at all", encoding="utf-8")

        with pytest.raises(RenderError, match="SVG 파일을 열 수 없습니다"):
            render_svg(bad_svg, QSize(800, 600))


# ---------------------------------------------------------------------------
# render_pdf 단위 테스트
# ---------------------------------------------------------------------------


class TestRenderPdf:
    """render_pdf 함수 단위 테스트."""

    def test_render_corrupted_pdf_raises(self, tmp_path: Path) -> None:
        """손상된 PDF 파일에 대해 RenderError를 발생시킨다."""
        bad_pdf = tmp_path / "bad.pdf"
        bad_pdf.write_bytes(b"not a real pdf")

        with pytest.raises(RenderError, match="PDF 파일을 열 수 없습니다"):
            render_pdf(bad_pdf, QSize(800, 600))


# ---------------------------------------------------------------------------
# render_file 디스패치 테스트
# ---------------------------------------------------------------------------


class TestRenderFile:
    """render_file 디스패치 함수 테스트."""

    def test_dispatches_png(self, tmp_path: Path) -> None:
        """PNG FileInfo에 대해 render_image를 호출한다."""
        png_path = tmp_path / "test.png"
        img = QImage(50, 50, QImage.Format.Format_RGB888)
        img.fill(0)
        img.save(str(png_path), "PNG")

        file_info = FileInfo(path=png_path, format=FileFormat.PNG, size=100)
        result = render_file(file_info, QSize(800, 600))

        assert not result.isNull()

    def test_dispatches_svg(self, tmp_path: Path) -> None:
        """SVG FileInfo에 대해 render_svg를 호출한다."""
        svg_path = tmp_path / "test.svg"
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">'
            '<circle cx="25" cy="25" r="20" fill="blue"/>'
            "</svg>"
        )
        svg_path.write_text(svg_content, encoding="utf-8")

        file_info = FileInfo(path=svg_path, format=FileFormat.SVG, size=100)
        result = render_file(file_info, QSize(800, 600))

        assert not result.isNull()
