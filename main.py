from __future__ import annotations

import faulthandler
import sys
from typing import Sequence

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.resources import ensure_assets_loaded

faulthandler.enable()


def run_app(argv: Sequence[str] | None = None) -> int:
    """Create the QApplication and show the main window."""
    ensure_assets_loaded()
    existing_app = QApplication.instance()
    app = existing_app or QApplication(list(argv) if argv is not None else sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


def main(argv: Sequence[str] | None = None) -> int:
    return run_app(argv)


if __name__ == "__main__":
    raise SystemExit(main())
