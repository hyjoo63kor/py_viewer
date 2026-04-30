"""파일 렌더링 모듈."""

from __future__ import annotations

from pathlib import Path

import fitz  # type: ignore[import-untyped]
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from my_app.file_handler import FileFormat, FileInfo


class RenderError(Exception):
    """렌더링 실패 시 발생하는 예외."""


def scale_pixmap(pixmap: QPixmap, display_size: QSize) -> QPixmap:
    """QPixmap을 종횡비를 유지하면서 display_size에 맞게 스케일링한다.

    display_size가 원본보다 크면 확대, 작으면 축소한다.
    Qt.AspectRatioMode.KeepAspectRatio를 사용한다.
    """
    return pixmap.scaled(
        display_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def render_image(file_path: Path, display_size: QSize) -> QPixmap:
    """PNG/JPG 이미지를 로드하고 display_size에 맞게 축소한 QPixmap을 반환한다."""
    pixmap = QPixmap(str(file_path))
    if pixmap.isNull():
        raise RenderError(f"이미지 파일이 손상되었습니다: {file_path.name}")
    return scale_pixmap(pixmap, display_size)


def render_pdf(file_path: Path, display_size: QSize) -> QPixmap:
    """PDF 첫 페이지를 이미지로 변환하고 축소한 QPixmap을 반환한다."""
    try:
        doc: fitz.Document = fitz.open(str(file_path))
        page = doc[0]
        pix: fitz.Pixmap = page.get_pixmap()

        fmt = QImage.Format.Format_RGB888
        if pix.alpha:
            fmt = QImage.Format.Format_RGBA8888

        qimage = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            fmt,
        )
        pixmap = QPixmap.fromImage(qimage)
        doc.close()
    except Exception as exc:
        raise RenderError("PDF 파일을 열 수 없습니다") from exc

    return scale_pixmap(pixmap, display_size)


def render_svg(file_path: Path, display_size: QSize) -> QPixmap:
    """SVG를 display_size에 맞게 벡터 품질로 직접 렌더링한다.

    SVG는 벡터 포맷이므로 줌된 크기로 직접 렌더링하여
    확대 시에도 선명한 품질을 유지한다.
    """
    renderer = QSvgRenderer(str(file_path))
    if not renderer.isValid():
        raise RenderError("SVG 파일을 열 수 없습니다")

    default_size = renderer.defaultSize()
    if default_size.isEmpty():
        default_size = display_size

    # 종횡비를 유지하면서 display_size에 맞는 렌더링 크기 계산
    scaled = default_size.scaled(
        display_size, Qt.AspectRatioMode.KeepAspectRatio
    )

    pixmap = QPixmap(scaled)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return pixmap


def render_file(file_info: FileInfo, display_size: QSize) -> QPixmap:
    """FileInfo에 따라 적절한 렌더러를 호출하여 QPixmap을 반환한다.

    Raises:
        RenderError: 렌더링 실패 시
    """
    if file_info.format in (FileFormat.PNG, FileFormat.JPG):
        return render_image(file_info.path, display_size)
    if file_info.format == FileFormat.PDF:
        return render_pdf(file_info.path, display_size)
    # FileFormat.SVG
    return render_svg(file_info.path, display_size)
