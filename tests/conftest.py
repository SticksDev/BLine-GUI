from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session", autouse=True)
def qt_core_app():
    """Ensure QSettings and other QtCore classes can initialize during tests."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app
