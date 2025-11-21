from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QScrollArea


class PersistentScrollArea(QScrollArea):
    """Scroll area that remembers and restores its scroll position across updates."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_scroll_value = 0
        self._suppress_scroll_events = False
        self._preserve_scroll = False
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

    def _on_scroll_changed(self, value: int) -> None:
        if not self._suppress_scroll_events:
            self._last_scroll_value = value

    def set_scroll_preserved_widget(self, widget) -> None:
        current_scroll = self.verticalScrollBar().value()
        self.setWidget(widget)
        QTimer.singleShot(0, lambda: self.verticalScrollBar().setValue(current_scroll))

    def begin_scroll_preservation(self) -> None:
        self._preserve_scroll = True
        self._last_scroll_value = self.verticalScrollBar().value()

    def end_scroll_preservation(self) -> None:
        self._preserve_scroll = False
        self.restore_scroll_position()

    def restore_scroll_position(self) -> bool:
        current_value = self.verticalScrollBar().value()
        if current_value != self._last_scroll_value:
            self._suppress_scroll_events = True
            self.verticalScrollBar().setValue(self._last_scroll_value)
            self._suppress_scroll_events = False
            QTimer.singleShot(0, self._force_restore_scroll)
            return True
        return False

    def _force_restore_scroll(self) -> None:
        if self._preserve_scroll:
            return
        current_value = self.verticalScrollBar().value()
        if current_value != self._last_scroll_value:
            self.verticalScrollBar().setValue(self._last_scroll_value)
