"""UI package containing widgets, dialogs, and resources."""

from .main_window import MainWindow
from .resources import ensure_assets_loaded

__all__ = ["MainWindow", "ensure_assets_loaded"]
