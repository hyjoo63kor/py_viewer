"""DropZone 위젯 모듈."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
    QMouseEvent,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

_PLACEHOLDER_TEXT = "파일을 여기에 드래그 앤 드롭하세요 (PNG, JPG, PDF, SVG, MD)"

_DEFAULT_STYLE = (
    "QLabel {"
    "  color: gray;"
    "  border: 2px dashed gray;"
    "  border-radius: 8px;"
    "  padding: 20px;"
    "}"
)

_DRAG_HOVER_STYLE = (
    "QLabel {"
    "  color: gray;"
    "  border: 2px solid #3399ff;"
    "  border-radius: 8px;"
    "  padding: 20px;"
    "}"
)

_ERROR_STYLE = (
    "QLabel {"
    "  color: red;"
    "  border: 2px dashed gray;"
    "  border-radius: 8px;"
    "  padding: 20px;"
    "}"
)


class DropZone(QLabel):
    """드래그 앤 드롭을 수신하고 파일 내용을 표시하는 위젯."""

    file_dropped = Signal(str)
    zoom_requested = Signal(int)
    pan_started = Signal(int, int)
    pan_moved = Signal(int, int)
    pan_finished = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """안내 메시지 표시, 드롭 활성화."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._drag_start_pos: QPoint | None = None
        self.show_placeholder()

    # ------------------------------------------------------------------
    # Drag & drop event handlers
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """드래그 진입 시 시각적 피드백 표시."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(_DRAG_HOVER_STYLE)
        else:
            super().dragEnterEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        """드래그 이탈 시 시각적 피드백 제거."""
        self.setStyleSheet(_DEFAULT_STYLE)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """드롭 시 첫 번째 파일 경로를 시그널로 전달."""
        self.setStyleSheet(_DEFAULT_STYLE)
        urls = event.mimeData().urls()
        if urls:
            file_path: str = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)

    # ------------------------------------------------------------------
    # Wheel event handler
    # ------------------------------------------------------------------

    def wheelEvent(self, event: QWheelEvent) -> None:
        """마우스 휠 이벤트를 zoom_requested 시그널로 전달한다."""
        self.zoom_requested.emit(event.angleDelta().y())

    # ------------------------------------------------------------------
    # Mouse pan event handlers
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """마우스 왼쪽 버튼 누름 시 pan_started 시그널을 emit한다."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
            pos = self._drag_start_pos
            self.pan_started.emit(pos.x(), pos.y())
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """드래그 중 pan_moved 시그널을 emit한다."""
        if self._drag_start_pos is not None:
            current = event.position().toPoint()
            dx = self._drag_start_pos.x() - current.x()
            dy = self._drag_start_pos.y() - current.y()
            self.pan_moved.emit(dx, dy)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """마우스 버튼 놓음 시 pan_finished 시그널을 emit한다."""
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._drag_start_pos is not None
        ):
            self._drag_start_pos = None
            self.pan_finished.emit()
        else:
            super().mouseReleaseEvent(event)

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def display_pixmap(self, pixmap: QPixmap) -> None:
        """QPixmap을 Display_Area에 표시한다."""
        self.clear()
        self.setStyleSheet("")
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def show_error(self, message: str) -> None:
        """오류 메시지를 Display_Area에 표시한다."""
        self.clear()
        self.setStyleSheet(_ERROR_STYLE)
        self.setText(message)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def show_placeholder(self) -> None:
        """안내 메시지를 표시한다."""
        self.clear()
        self.setStyleSheet(_DEFAULT_STYLE)
        self.setText(_PLACEHOLDER_TEXT)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
