"""Arrow annotation tool."""

import math
from PyQt6.QtCore import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsItemGroup
from PyQt6.QtGui import QPen, QBrush, QPolygonF, QColor

from .base import BaseTool


class ArrowItem(QGraphicsItemGroup):
    """Graphics item for an arrow annotation."""

    def __init__(self, start: QPointF, end: QPointF, color: QColor, thickness: int):
        super().__init__()

        self._start = start
        self._end = end
        self._color = color
        self._thickness = thickness

        self._create_arrow()

    def _create_arrow(self):
        """Create the arrow graphics."""
        # Line
        line = QGraphicsLineItem(QLineF(self._start, self._end))
        pen = QPen(self._color, self._thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line.setPen(pen)
        self.addToGroup(line)

        # Arrowhead
        arrow_size = max(10, self._thickness * 3)
        angle = math.atan2(
            self._end.y() - self._start.y(),
            self._end.x() - self._start.x()
        )

        p1 = self._end
        p2 = QPointF(
            self._end.x() - arrow_size * math.cos(angle - math.pi / 6),
            self._end.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        p3 = QPointF(
            self._end.x() - arrow_size * math.cos(angle + math.pi / 6),
            self._end.y() - arrow_size * math.sin(angle + math.pi / 6)
        )

        arrowhead = QGraphicsPolygonItem(QPolygonF([p1, p2, p3]))
        arrowhead.setPen(QPen(self._color, 1))
        arrowhead.setBrush(QBrush(self._color))
        self.addToGroup(arrowhead)

    def update_end(self, end: QPointF):
        """Update the arrow end point."""
        self._end = end

        # Remove existing items
        for item in self.childItems():
            self.removeFromGroup(item)

        self._create_arrow()


# Need Qt import for PenCapStyle
from PyQt6.QtCore import Qt


class ArrowTool(BaseTool):
    """Tool for drawing arrow annotations."""

    def __init__(self):
        super().__init__()
        self._current_arrow = None

    def on_press(self, pos: QPointF, canvas):
        """Start drawing an arrow."""
        self._is_drawing = True
        self._start_pos = pos

        # Create preview arrow
        self._current_arrow = ArrowItem(
            pos, pos,
            self._color or QColor(255, 0, 0),
            self._thickness
        )
        canvas.add_annotation(self._current_arrow)

    def on_move(self, pos: QPointF, canvas):
        """Update arrow preview."""
        if self._is_drawing and self._current_arrow:
            self._current_arrow.update_end(pos)

    def on_release(self, pos: QPointF, canvas):
        """Finish drawing the arrow."""
        if self._is_drawing:
            self._is_drawing = False

            # Only keep if arrow has meaningful length
            if self._start_pos and self._current_arrow:
                length = math.sqrt(
                    (pos.x() - self._start_pos.x()) ** 2 +
                    (pos.y() - self._start_pos.y()) ** 2
                )
                if length < 5:
                    # Too short, remove it
                    canvas.remove_annotation(self._current_arrow)

            self._current_arrow = None
            self._start_pos = None

    def on_cancel(self):
        """Cancel arrow drawing."""
        super().on_cancel()
        self._current_arrow = None
