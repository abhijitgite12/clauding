"""Stamp/icon tool."""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import QGraphicsTextItem, QMenu, QApplication
from PyQt6.QtGui import QFont, QColor, QCursor

from .base import BaseTool


# Common stamps/emojis
STAMPS = {
    "Checkmark": "\u2713",
    "X Mark": "\u2717",
    "Star": "\u2605",
    "Arrow Right": "\u2192",
    "Arrow Left": "\u2190",
    "Arrow Up": "\u2191",
    "Arrow Down": "\u2193",
    "Warning": "\u26A0",
    "Info": "\u2139",
    "Question": "?",
    "Exclamation": "!",
    "Number 1": "\u2776",
    "Number 2": "\u2777",
    "Number 3": "\u2778",
    "Number 4": "\u2779",
    "Number 5": "\u277A",
    "Circle": "\u25CF",
    "Square": "\u25A0",
    "Triangle": "\u25B2",
    "Diamond": "\u25C6",
}


class StampItem(QGraphicsTextItem):
    """A stamp/icon annotation."""

    def __init__(self, symbol: str, pos: QPointF, color: QColor, size: int):
        super().__init__(symbol)
        self.setPos(pos.x() - size / 2, pos.y() - size / 2)
        self.setDefaultTextColor(color)

        font = QFont("Segoe UI Symbol", size)
        self.setFont(font)

        # Make movable
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)


class StampTool(BaseTool):
    """Tool for adding stamp/icon annotations."""

    def __init__(self):
        super().__init__()
        self._selected_stamp = STAMPS["Checkmark"]
        self._pending_pos = None

    def cursor(self) -> QCursor:
        """Return stamp cursor."""
        return QCursor(Qt.CursorShape.PointingHandCursor)

    def set_stamp(self, stamp_name: str):
        """Set the current stamp."""
        if stamp_name in STAMPS:
            self._selected_stamp = STAMPS[stamp_name]

    def get_available_stamps(self) -> dict:
        """Get available stamps."""
        return STAMPS.copy()

    def on_press(self, pos: QPointF, canvas):
        """Show stamp selection menu or place stamp."""
        self._pending_pos = pos

    def on_move(self, pos: QPointF, canvas):
        """No preview for stamp tool."""
        pass

    def on_release(self, pos: QPointF, canvas):
        """Place the stamp."""
        if not self._pending_pos:
            return

        # Create stamp at position
        item = StampItem(
            self._selected_stamp,
            self._pending_pos,
            self._color or QColor(255, 0, 0),
            self._font_size * 2  # Stamps are larger
        )
        canvas.add_annotation(item)

        self._pending_pos = None

    def on_cancel(self):
        """Cancel stamp placement."""
        super().on_cancel()
        self._pending_pos = None

    def show_stamp_menu(self, pos, parent=None) -> str | None:
        """Show a menu to select a stamp."""
        menu = QMenu(parent)

        for name, symbol in STAMPS.items():
            action = menu.addAction(f"{symbol}  {name}")
            action.setData(name)

        action = menu.exec(pos)
        if action:
            return action.data()
        return None
