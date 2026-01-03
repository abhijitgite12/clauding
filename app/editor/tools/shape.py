"""Shape annotation tools (rectangle, ellipse, line)."""

from PyQt6.QtCore import QPointF, QRectF, QLineF, Qt
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtGui import QPen, QBrush, QColor

from .base import BaseTool


class ShapeTool(BaseTool):
    """Tool for drawing shape annotations."""

    def __init__(self, shape_type: str = "rect"):
        """Initialize with shape type: 'rect', 'ellipse', or 'line'."""
        super().__init__()
        self._shape_type = shape_type
        self._current_item = None

    def on_press(self, pos: QPointF, canvas):
        """Start drawing a shape."""
        self._is_drawing = True
        self._start_pos = pos

        color = self._color or QColor(255, 0, 0)
        pen = QPen(color, self._thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        if self._shape_type == "rect":
            self._current_item = QGraphicsRectItem(QRectF(pos, pos))
            self._current_item.setPen(pen)
            self._current_item.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        elif self._shape_type == "ellipse":
            self._current_item = QGraphicsEllipseItem(QRectF(pos, pos))
            self._current_item.setPen(pen)
            self._current_item.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        elif self._shape_type == "line":
            self._current_item = QGraphicsLineItem(QLineF(pos, pos))
            self._current_item.setPen(pen)

        if self._current_item:
            canvas.add_annotation(self._current_item)

    def on_move(self, pos: QPointF, canvas):
        """Update shape preview."""
        if not self._is_drawing or not self._current_item:
            return

        if self._shape_type in ("rect", "ellipse"):
            rect = QRectF(
                min(self._start_pos.x(), pos.x()),
                min(self._start_pos.y(), pos.y()),
                abs(pos.x() - self._start_pos.x()),
                abs(pos.y() - self._start_pos.y())
            )
            self._current_item.setRect(rect)

        elif self._shape_type == "line":
            self._current_item.setLine(QLineF(self._start_pos, pos))

    def on_release(self, pos: QPointF, canvas):
        """Finish drawing the shape."""
        if self._is_drawing:
            self._is_drawing = False

            # Check if shape is too small
            if self._start_pos and self._current_item:
                width = abs(pos.x() - self._start_pos.x())
                height = abs(pos.y() - self._start_pos.y())

                if self._shape_type == "line":
                    length = (width ** 2 + height ** 2) ** 0.5
                    if length < 5:
                        canvas.remove_annotation(self._current_item)
                else:
                    if width < 5 and height < 5:
                        canvas.remove_annotation(self._current_item)

            self._current_item = None
            self._start_pos = None

    def on_cancel(self):
        """Cancel shape drawing."""
        super().on_cancel()
        self._current_item = None


class RectTool(ShapeTool):
    """Rectangle drawing tool."""

    def __init__(self):
        super().__init__("rect")


class EllipseTool(ShapeTool):
    """Ellipse drawing tool."""

    def __init__(self):
        super().__init__("ellipse")


class LineTool(ShapeTool):
    """Line drawing tool."""

    def __init__(self):
        super().__init__("line")
