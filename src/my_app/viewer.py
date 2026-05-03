"""메인 윈도우 (Viewer) 모듈."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout, QWidget

from my_app.drop_zone import DropZone
from my_app.file_handler import FileFormat, FileInfo, FileValidationError, validate_file
from my_app.renderers import RenderError, render_file
from my_app.title_panel import TitlePanel


def clamp_pan_offset(
    pan_x: int,
    pan_y: int,
    rendered_w: int,
    rendered_h: int,
    viewport_w: int,
    viewport_h: int,
) -> tuple[int, int]:
    """Pan 오프셋을 경계 내로 제한한다."""
    max_offset_x = max(0, (rendered_w - viewport_w) // 2)
    max_offset_y = max(0, (rendered_h - viewport_h) // 2)
    clamped_x = max(-max_offset_x, min(pan_x, max_offset_x))
    clamped_y = max(-max_offset_y, min(pan_y, max_offset_y))
    return (clamped_x, clamped_y)


def compute_crop_rect(
    rendered_w: int,
    rendered_h: int,
    viewport_w: int,
    viewport_h: int,
    pan_x: int,
    pan_y: int,
) -> tuple[int, int, int, int]:
    """Crop 영역의 (x, y, width, height)를 계산한다."""
    crop_w = min(rendered_w, viewport_w)
    crop_h = min(rendered_h, viewport_h)
    crop_x = (rendered_w - crop_w) // 2 + pan_x
    crop_y = (rendered_h - crop_h) // 2 + pan_y
    return (crop_x, crop_y, crop_w, crop_h)


_FILE_FILTER = "이미지/문서 파일 (*.png *.jpg *.jpeg *.pdf *.svg *.md)"


class Viewer(QMainWindow):
    """메인 윈도우. TitlePanel과 DropZone을 포함한다."""

    ZOOM_STEP: float = 1.25
    MIN_ZOOM: float = 0.1
    MAX_ZOOM: float = 10.0
    DEFAULT_ZOOM: float = 1.0
    PAN_STEP: int = 50

    def __init__(self) -> None:
        """800x600 크기, 제목 설정, TitlePanel + DropZone 수직 배치."""
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle("SvgViewer")

        self._current_file_info: FileInfo | None = None
        self._zoom_level: float = self.DEFAULT_ZOOM
        self._rendering: bool = False
        self._pan_offset_x: int = 0
        self._pan_offset_y: int = 0
        self._drag_start_offset: tuple[int, int] = (0, 0)
        self._current_page: int = 1
        self._total_pages: int = 1

        # 위젯 생성
        self._title_panel = TitlePanel()
        self._drop_zone = DropZone()

        # QVBoxLayout으로 TitlePanel + DropZone 수직 배치
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._title_panel)
        layout.addWidget(self._drop_zone, 1)
        self.setCentralWidget(container)

        # 시그널 연결
        self._drop_zone.file_dropped.connect(self._on_file_dropped)
        self._drop_zone.zoom_requested.connect(self._on_zoom_requested)
        self._title_panel.zoom_in_clicked.connect(self.zoom_in)
        self._title_panel.zoom_out_clicked.connect(self.zoom_out)
        self._title_panel.open_clicked.connect(self._on_open_clicked)
        self._title_panel.zoom_reset_clicked.connect(self.zoom_reset)
        self._drop_zone.pan_started.connect(self._on_pan_started)
        self._drop_zone.pan_moved.connect(self._on_pan_moved)
        self._drop_zone.pan_finished.connect(self._on_pan_finished)
        self._title_panel.pan_up_clicked.connect(self._on_pan_up)
        self._title_panel.pan_down_clicked.connect(self._on_pan_down)
        self._title_panel.pan_left_clicked.connect(self._on_pan_left)
        self._title_panel.pan_right_clicked.connect(self._on_pan_right)
        self._title_panel.prev_page_clicked.connect(self._on_prev_page)
        self._title_panel.next_page_clicked.connect(self._on_next_page)

    # ------------------------------------------------------------------
    # 줌 메서드
    # ------------------------------------------------------------------

    def zoom_in(self) -> None:
        """줌 레벨을 ZOOM_STEP만큼 곱하여 확대한다. MAX_ZOOM을 초과하지 않는다."""
        if self._current_file_info is None:
            return
        self._zoom_level = min(self._zoom_level * self.ZOOM_STEP, self.MAX_ZOOM)
        self._apply_zoom()

    def zoom_out(self) -> None:
        """줌 레벨을 ZOOM_STEP으로 나누어 축소한다.

        MIN_ZOOM 미만으로 내려가지 않는다.
        """
        if self._current_file_info is None:
            return
        self._zoom_level = max(self._zoom_level / self.ZOOM_STEP, self.MIN_ZOOM)
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        """현재 줌 레벨로 콘텐츠를 다시 렌더링하고 줌 레이블을 갱신한다."""
        self._reset_pan_offset()
        self._title_panel.update_zoom_label(self._zoom_level)
        if self._current_file_info is not None:
            self._render_file(self._current_file_info)

    def _on_zoom_requested(self, delta: int) -> None:
        """DropZone의 zoom_requested 시그널 핸들러."""
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()

    def zoom_reset(self) -> None:
        """줌 레벨을 100%로, Pan 오프셋을 (0, 0)으로 초기화한다."""
        if self._current_file_info is None:
            return
        if (
            self._zoom_level == self.DEFAULT_ZOOM
            and self._pan_offset_x == 0
            and self._pan_offset_y == 0
        ):
            return
        self._zoom_level = self.DEFAULT_ZOOM
        self._apply_zoom()

    # ------------------------------------------------------------------
    # 파일 열기 다이얼로그
    # ------------------------------------------------------------------

    def _on_open_clicked(self) -> None:
        """파일 열기 다이얼로그를 표시하고 선택된 파일을 로드한다."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "파일 열기",
            "",
            _FILE_FILTER,
        )
        if file_path:
            self._on_file_dropped(file_path)

    # ------------------------------------------------------------------
    # Pan 메서드
    # ------------------------------------------------------------------

    def _reset_pan_offset(self) -> None:
        """Pan 오프셋을 (0, 0)으로 초기화한다."""
        self._pan_offset_x = 0
        self._pan_offset_y = 0

    def _clamp_pan_offset(self, rendered_size: QSize, viewport_size: QSize) -> None:
        """Pan 오프셋을 경계 내로 제한한다."""
        self._pan_offset_x, self._pan_offset_y = clamp_pan_offset(
            self._pan_offset_x,
            self._pan_offset_y,
            rendered_size.width(),
            rendered_size.height(),
            viewport_size.width(),
            viewport_size.height(),
        )

    def _crop_pixmap(self, pixmap: QPixmap, viewport_size: QSize) -> QPixmap:
        """전체 렌더링된 pixmap에서 pan_offset 기반으로 viewport 크기만큼 crop한다."""
        crop_x, crop_y, crop_w, crop_h = compute_crop_rect(
            pixmap.width(),
            pixmap.height(),
            viewport_size.width(),
            viewport_size.height(),
            self._pan_offset_x,
            self._pan_offset_y,
        )
        return pixmap.copy(crop_x, crop_y, crop_w, crop_h)

    def _apply_pan(self) -> None:
        """현재 pan_offset으로 콘텐츠를 다시 렌더링+crop하여 표시한다."""
        if self._current_file_info is not None:
            self._render_file(self._current_file_info)

    def _on_pan_started(self, x: int, y: int) -> None:
        """드래그 시작 위치와 현재 오프셋을 기록한다."""
        if self._current_file_info is None:
            return
        self._drag_start_offset = (self._pan_offset_x, self._pan_offset_y)
        self._drop_zone.setCursor(Qt.CursorShape.ClosedHandCursor)

    def _on_pan_moved(self, dx: int, dy: int) -> None:
        """드래그 이동량만큼 pan_offset을 갱신하고 _apply_pan을 호출한다."""
        if self._current_file_info is None:
            return
        self._pan_offset_x = self._drag_start_offset[0] + dx
        self._pan_offset_y = self._drag_start_offset[1] + dy
        self._apply_pan()

    def _on_pan_finished(self) -> None:
        """드래그 종료 처리. 커서를 복원한다."""
        self._drop_zone.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_pan_up(self) -> None:
        """pan_offset_y를 PAN_STEP만큼 감소시킨다."""
        if self._current_file_info is None:
            return
        self._pan_offset_y -= self.PAN_STEP
        self._apply_pan()

    def _on_pan_down(self) -> None:
        """pan_offset_y를 PAN_STEP만큼 증가시킨다."""
        if self._current_file_info is None:
            return
        self._pan_offset_y += self.PAN_STEP
        self._apply_pan()

    def _on_pan_left(self) -> None:
        """pan_offset_x를 PAN_STEP만큼 감소시킨다."""
        if self._current_file_info is None:
            return
        self._pan_offset_x -= self.PAN_STEP
        self._apply_pan()

    def _on_pan_right(self) -> None:
        """pan_offset_x를 PAN_STEP만큼 증가시킨다."""
        if self._current_file_info is None:
            return
        self._pan_offset_x += self.PAN_STEP
        self._apply_pan()

    # ------------------------------------------------------------------
    # 페이지 탐색 메서드
    # ------------------------------------------------------------------

    def _on_prev_page(self) -> None:
        """이전 페이지로 이동한다."""
        if self._current_file_info is None or self._current_page <= 1:
            return
        self._current_page -= 1
        self._zoom_level = self.DEFAULT_ZOOM
        self._reset_pan_offset()
        self._title_panel.update_zoom_label(self._zoom_level)
        self._title_panel.set_page_info(self._current_page, self._total_pages)
        self._render_file(self._current_file_info)

    def _on_next_page(self) -> None:
        """다음 페이지로 이동한다."""
        if self._current_file_info is None or self._current_page >= self._total_pages:
            return
        self._current_page += 1
        self._zoom_level = self.DEFAULT_ZOOM
        self._reset_pan_offset()
        self._title_panel.update_zoom_label(self._zoom_level)
        self._title_panel.set_page_info(self._current_page, self._total_pages)
        self._render_file(self._current_file_info)

    # ------------------------------------------------------------------
    # 파일 처리
    # ------------------------------------------------------------------

    def _on_file_dropped(self, file_path: str) -> None:
        """DropZone의 file_dropped 시그널 핸들러."""
        self._zoom_level = self.DEFAULT_ZOOM
        self._title_panel.update_zoom_label(self._zoom_level)
        self._reset_pan_offset()
        self._cleanup_previous()
        try:
            file_info = validate_file(file_path)
        except FileValidationError as e:
            self._drop_zone.show_error(str(e))
            return
        if file_info.format == FileFormat.PDF:
            from my_app.renderers import get_pdf_page_count

            self._total_pages = get_pdf_page_count(file_info.path)
            self._current_page = 1
            self._title_panel.set_page_info(1, self._total_pages)
        else:
            self._total_pages = 1
            self._current_page = 1
            self._title_panel.hide_page_nav()
        self._render_file(file_info)

    def _render_file(self, file_info: FileInfo) -> None:
        """FileInfo를 기반으로 줌 레벨이 적용된 크기로 렌더링한다."""
        self._rendering = True
        try:
            base_size: QSize = self._drop_zone.size()
            zoomed_size = QSize(
                int(base_size.width() * self._zoom_level),
                int(base_size.height() * self._zoom_level),
            )
            try:
                pixmap = render_file(file_info, zoomed_size, page=self._current_page)
            except RenderError as e:
                self._drop_zone.show_error(str(e))
                return
            self._current_file_info = file_info
            viewport_size = self._drop_zone.size()
            self._clamp_pan_offset(
                QSize(pixmap.width(), pixmap.height()), viewport_size
            )
            cropped = self._crop_pixmap(pixmap, viewport_size)
            self._drop_zone.display_pixmap(cropped)
        finally:
            self._rendering = False

    def _cleanup_previous(self) -> None:
        """이전 파일의 리소스를 해제한다."""
        self._current_file_info = None
        self._drop_zone.show_placeholder()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """윈도우 크기 변경 시 현재 줌 레벨을 유지하면서 재렌더링한다."""
        super().resizeEvent(event)
        if self._current_file_info is not None and not self._rendering:
            self._render_file(self._current_file_info)
