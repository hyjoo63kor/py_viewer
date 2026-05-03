"""Viewer 상단에 배치되는 줌 컨트롤 패널 모듈."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class TitlePanel(QWidget):
    """Viewer 상단에 배치되는 줌 컨트롤 패널.

    안내 문구, 줌 버튼(+/-), 줌 레이블을 수평으로 배치한다.
    """

    open_clicked = Signal()
    zoom_in_clicked = Signal()
    zoom_out_clicked = Signal()
    zoom_reset_clicked = Signal()
    pan_up_clicked = Signal()
    pan_down_clicked = Signal()
    pan_left_clicked = Signal()
    pan_right_clicked = Signal()
    prev_page_clicked = Signal()
    next_page_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """안내 문구, 줌 버튼, 줌 레이블을 포함하는 수평 레이아웃을 구성한다."""
        super().__init__(parent)

        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # 왼쪽: 열기 버튼
        self._open_button = QPushButton("열기")
        self._open_button.setFixedWidth(40)
        layout.addWidget(self._open_button)

        # 안내 문구
        self._info_label = QLabel("마우스 휠로 줌인/줌아웃 가능")
        layout.addWidget(self._info_label)

        # 가운데: stretch spacer
        layout.addStretch()

        # 방향 버튼
        self._pan_left_button = QPushButton("◀")
        self._pan_left_button.setFixedWidth(30)
        layout.addWidget(self._pan_left_button)

        self._pan_up_button = QPushButton("▲")
        self._pan_up_button.setFixedWidth(30)
        layout.addWidget(self._pan_up_button)

        self._pan_down_button = QPushButton("▼")
        self._pan_down_button.setFixedWidth(30)
        layout.addWidget(self._pan_down_button)

        self._pan_right_button = QPushButton("▶")
        self._pan_right_button.setFixedWidth(30)
        layout.addWidget(self._pan_right_button)

        # 페이지 네비게이션 위젯
        self._prev_button = QPushButton("◁")
        self._prev_button.setFixedWidth(30)
        layout.addWidget(self._prev_button)

        self._page_label = QLabel("")
        layout.addWidget(self._page_label)

        self._next_button = QPushButton("▷")
        self._next_button.setFixedWidth(30)
        layout.addWidget(self._next_button)

        # 초기 상태: 숨김
        self._prev_button.setVisible(False)
        self._page_label.setVisible(False)
        self._next_button.setVisible(False)

        # 오른쪽: 줌 컨트롤
        self._zoom_out_button = QPushButton("-")
        self._zoom_out_button.setFixedWidth(30)
        layout.addWidget(self._zoom_out_button)

        self._zoom_label = QLabel("100%")
        layout.addWidget(self._zoom_label)

        self._zoom_in_button = QPushButton("+")
        self._zoom_in_button.setFixedWidth(30)
        layout.addWidget(self._zoom_in_button)

        self._zoom_reset_button = QPushButton("리셋")
        self._zoom_reset_button.setFixedWidth(40)
        layout.addWidget(self._zoom_reset_button)

        # 시그널 연결
        self._open_button.clicked.connect(self.open_clicked)
        self._zoom_in_button.clicked.connect(self.zoom_in_clicked)
        self._zoom_out_button.clicked.connect(self.zoom_out_clicked)
        self._zoom_reset_button.clicked.connect(self.zoom_reset_clicked)
        self._pan_up_button.clicked.connect(self.pan_up_clicked)
        self._pan_down_button.clicked.connect(self.pan_down_clicked)
        self._pan_left_button.clicked.connect(self.pan_left_clicked)
        self._pan_right_button.clicked.connect(self.pan_right_clicked)
        self._prev_button.clicked.connect(self.prev_page_clicked)
        self._next_button.clicked.connect(self.next_page_clicked)

    def update_zoom_label(self, zoom_level: float) -> None:
        """줌 레이블을 백분율 형식(예: '100%')으로 갱신한다."""
        self._zoom_label.setText(f"{round(zoom_level * 100)}%")

    def set_page_info(self, current: int, total: int) -> None:
        """페이지 정보를 갱신하고 네비게이션 위젯의 표시/숨김을 제어한다."""
        if total <= 1:
            self.hide_page_nav()
            return
        self._prev_button.setVisible(True)
        self._page_label.setVisible(True)
        self._next_button.setVisible(True)
        self._page_label.setText(f"{current}/{total}")
        self._prev_button.setEnabled(current > 1)
        self._next_button.setEnabled(current < total)

    def hide_page_nav(self) -> None:
        """페이지 네비게이션 위젯을 숨긴다."""
        self._prev_button.setVisible(False)
        self._page_label.setVisible(False)
        self._next_button.setVisible(False)
