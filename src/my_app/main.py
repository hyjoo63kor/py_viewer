"""애플리케이션 진입점."""

import sys

from PySide6.QtWidgets import QApplication

from my_app.viewer import Viewer


def main() -> None:
    """QApplication을 생성하고 Viewer 윈도우를 표시한다."""
    app = QApplication(sys.argv)
    viewer = Viewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
