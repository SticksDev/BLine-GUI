"""Helpers for registering Qt resource files in one place."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

_RESOURCE_MODULE: ModuleType | None = None


def ensure_assets_loaded() -> None:
    """Import the generated PySide resource file once."""
    global _RESOURCE_MODULE
    if _RESOURCE_MODULE is not None:
        return
    module = import_module("assets_rc")
    _RESOURCE_MODULE = module
