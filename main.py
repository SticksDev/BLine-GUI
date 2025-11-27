from __future__ import annotations

import faulthandler
import sys
from typing import Sequence

from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from typing import cast

from ui.main_window import MainWindow
from ui.resources import ensure_assets_loaded

faulthandler.enable()


DARK_STYLE_SHEET = """
QMainWindow,
QWidget#mainCentralWidget {
    background-color: #111111;
    color: #f0f0f0;
}

QMenuBar,
QMenu,
QToolBar,
QStatusBar {
    background-color: #1b1b1b;
    color: #f0f0f0;
}

QMenu::item:selected {
    background-color: #2a82da;
    color: #000000;
}
"""


def set_dark_theme(app: QApplication) -> None:
    """Apply a dark theme to the application."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(17, 17, 17))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(28, 28, 28))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(38, 38, 38))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(150, 150, 150))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(115, 115, 115))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(115, 115, 115))

    app.setPalette(palette)
    app.setStyleSheet(DARK_STYLE_SHEET)


def run_app(argv: Sequence[str] | None = None) -> int:
    """Create the QApplication and show the main window."""
    ensure_assets_loaded()
    existing_app = QApplication.instance()
    app = existing_app or QApplication(list(argv) if argv is not None else sys.argv)

    set_dark_theme(cast(QApplication, app))

    window = MainWindow()
    window.show()
    return app.exec()


def main(argv: Sequence[str] | None = None) -> int:
    return run_app(argv)


if __name__ == "__main__":
    raise SystemExit(main())
