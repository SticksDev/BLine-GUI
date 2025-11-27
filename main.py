from __future__ import annotations

import faulthandler
import sys
from typing import Sequence

from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

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
    fusion_style = QStyleFactory.create("Fusion")
    if fusion_style is not None:
        app.setStyle(fusion_style)
    else:
        app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(17, 17, 17))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(28, 28, 28))
    palette.setColor(QPalette.AlternateBase, QColor(38, 38, 38))
    palette.setColor(QPalette.ToolTipBase, QColor(42, 42, 42))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(43, 43, 43))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.PlaceholderText, QColor(150, 150, 150))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(115, 115, 115))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(115, 115, 115))

    app.setPalette(palette)
    app.setStyleSheet(DARK_STYLE_SHEET)


def run_app(argv: Sequence[str] | None = None) -> int:
    """Create the QApplication and show the main window."""
    ensure_assets_loaded()
    existing_app = QApplication.instance()
    app = existing_app or QApplication(list(argv) if argv is not None else sys.argv)

    set_dark_theme(app)

    window = MainWindow()
    window.show()
    return app.exec()


def main(argv: Sequence[str] | None = None) -> int:
    return run_app(argv)


if __name__ == "__main__":
    raise SystemExit(main())
