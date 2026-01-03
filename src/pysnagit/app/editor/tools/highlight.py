"""Highlight/marker tool."""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QBrush, QColor

from .base import BaseTool


class HighlightItem(QGraphicsRectItem):
    """Semi-transparent highlight rectangle."""

    def __init__(self, rect: QRectF, color: QColor):
        super().__init__(rect)

        # Create semi-transparent fill
        highlight_color = QColor(color)
        highlight_color.setAlpha(80)

        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(highlight_color))


class HighlightTool(BaseTool):
    """Tool for highlighting areas."""

    def __init__(self):
        super().__init__()
        self._current_item = None

    def on_press(self, pos: QPointF, canvas):
        """Start highlighting."""
        self._is_drawing = True
        self._start_pos = pos

        color = self._color or QColor(255, 255, 0)  # Default yellow
        self._current_item = HighlightItem(QRectF(pos, pos), color)
        canvas.add_annotation(self._current_item)

    def on_move(self, pos: QPointF, canvas):
        """Update highlight area."""
        if not self._is_drawing or not self._current_item:
            return

        rect = QRectF(
            min(self._start_pos.x(), pos.x()),
            min(self._start_pos.y(), pos.y()),
            abs(pos.x() - self._start_pos.x()),
            abs(pos.y() - self._start_pos.y())
        )
        self._current_item.setRect(rect)

    def on_release(self, pos: QPointF, canvas):
        """Finish highlighting."""
        if self._is_drawing:
            self._is_drawing = False

            # Check if area is too small
            if self._start_pos and self._current_item:
                width = abs(pos.x() - self._start_pos.x())
                height = abs(pos.y() - self._start_pos.y())
                if width < 5 and height < 5:
                    canvas.remove_annotation(self._current_item)

            self._current_item = None
            self._start_pos = None

    def on_cancel(self):
        """Cancel highlighting."""
        super().on_cancel()
        self._current_item = None
