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

    def update_zoom_label(self, zoom_level: float) -> None:
        """줌 레이블을 백분율 형식(예: '100%')으로 갱신한다."""
        self._zoom_label.setText(f"{round(zoom_level * 100)}%")
