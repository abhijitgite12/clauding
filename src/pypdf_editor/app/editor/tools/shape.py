"""Shape annotation tools (rectangle, ellipse, line, arrow)."""

import math
from PyQt6.QtCore import QPointF, QRectF, QLineF, Qt
from PyQt6.QtGui import QCursor, QColor, QPen
from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsPolygonItem
)
from PyQt6.QtGui import QPolygonF

from .base import PDFBaseTool


class RectangleTool(PDFBaseTool):
    """Tool for drawing rectangles."""

    def __init__(self):
        super().__init__()
        self._color = QColor(255, 0, 0)
        self._thickness = 2
        self._filled = False
        self._preview = None

    def set_filled(self, filled: bool):
        self._filled = filled

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        self._preview = QGraphicsRectItem()
        pen = QPen(self._color, self._thickness)
        self._preview.setPen(pen)
        if self._filled:
            fill_color = QColor(self._color)
            fill_color.setAlpha(50)
            self._preview.setBrush(fill_color)
        canvas._scene.addItem(self._preview)

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active or not self._start_pos:
            return

        if self._preview:
            rect = QRectF(self._start_pos, pos).normalized()
            self._preview.setRect(rect)

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        if self._preview and self._preview.scene():
            canvas._scene.removeItem(self._preview)

        if self._start_pos and canvas.document:
            rect = QRectF(self._start_pos, pos).normalized()
            if rect.width() > 5 and rect.height() > 5:
                page = canvas.document.get_page(page_index)
                if page:
                    import fitz
                    pdf_rect = fitz.Rect(
                        rect.x(), rect.y(),
                        rect.x() + rect.width(),
                        rect.y() + rect.height()
                    )
                    color = (self._color.redF(), self._color.greenF(), self._color.blueF())

                    annot = page.add_rect_annot(pdf_rect)
                    annot.set_colors(stroke=color)
                    if self._filled:
                        annot.set_colors(stroke=color, fill=color)
                    annot.set_border(width=self._thickness)
                    annot.update()
                    canvas.document._mark_modified()
                    canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview = None


class EllipseTool(PDFBaseTool):
    """Tool for drawing ellipses/circles."""

    def __init__(self):
        super().__init__()
        self._color = QColor(255, 0, 0)
        self._thickness = 2
        self._filled = False
        self._preview = None

    def set_filled(self, filled: bool):
        self._filled = filled

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        self._preview = QGraphicsEllipseItem()
        pen = QPen(self._color, self._thickness)
        self._preview.setPen(pen)
        if self._filled:
            fill_color = QColor(self._color)
            fill_color.setAlpha(50)
            self._preview.setBrush(fill_color)
        canvas._scene.addItem(self._preview)

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active or not self._start_pos:
            return

        if self._preview:
            rect = QRectF(self._start_pos, pos).normalized()
            self._preview.setRect(rect)

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        if self._preview and self._preview.scene():
            canvas._scene.removeItem(self._preview)

        if self._start_pos and canvas.document:
            rect = QRectF(self._start_pos, pos).normalized()
            if rect.width() > 5 and rect.height() > 5:
                page = canvas.document.get_page(page_index)
                if page:
                    import fitz
                    pdf_rect = fitz.Rect(
                        rect.x(), rect.y(),
                        rect.x() + rect.width(),
                        rect.y() + rect.height()
                    )
                    color = (self._color.redF(), self._color.greenF(), self._color.blueF())

                    # PyMuPDF doesn't have direct ellipse, use circle annot
                    annot = page.add_circle_annot(pdf_rect)
                    annot.set_colors(stroke=color)
                    if self._filled:
                        annot.set_colors(stroke=color, fill=color)
                    annot.set_border(width=self._thickness)
                    annot.update()
                    canvas.document._mark_modified()
                    canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview = None


class LineTool(PDFBaseTool):
    """Tool for drawing straight lines."""

    def __init__(self):
        super().__init__()
        self._color = QColor(255, 0, 0)
        self._thickness = 2
        self._preview = None

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        self._preview = QGraphicsLineItem()
        pen = QPen(self._color, self._thickness)
        self._preview.setPen(pen)
        canvas._scene.addItem(self._preview)

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active or not self._start_pos:
            return

        if self._preview:
            self._preview.setLine(QLineF(self._start_pos, pos))

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        if self._preview and self._preview.scene():
            canvas._scene.removeItem(self._preview)

        if self._start_pos and canvas.document:
            page = canvas.document.get_page(page_index)
            if page:
                import fitz
                start = fitz.Point(self._start_pos.x(), self._start_pos.y())
                end = fitz.Point(pos.x(), pos.y())
                color = (self._color.redF(), self._color.greenF(), self._color.blueF())

                annot = page.add_line_annot(start, end)
                annot.set_colors(stroke=color)
                annot.set_border(width=self._thickness)
                annot.update()
                canvas.document._mark_modified()
                canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview = None


class ArrowTool(PDFBaseTool):
    """Tool for drawing arrows."""

    def __init__(self):
        super().__init__()
        self._color = QColor(255, 0, 0)
        self._thickness = 2
        self._preview_line = None
        self._preview_head = None

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        pen = QPen(self._color, self._thickness)

        self._preview_line = QGraphicsLineItem()
        self._preview_line.setPen(pen)
        canvas._scene.addItem(self._preview_line)

        self._preview_head = QGraphicsPolygonItem()
        self._preview_head.setPen(pen)
        self._preview_head.setBrush(self._color)
        canvas._scene.addItem(self._preview_head)

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active or not self._start_pos:
            return

        if self._preview_line:
            self._preview_line.setLine(QLineF(self._start_pos, pos))

        if self._preview_head:
            self._preview_head.setPolygon(self._create_arrowhead(self._start_pos, pos))

    def _create_arrowhead(self, start: QPointF, end: QPointF) -> QPolygonF:
        """Create arrowhead polygon."""
        arrow_size = 15
        angle = math.atan2(end.y() - start.y(), end.x() - start.x())

        p1 = end
        p2 = QPointF(
            end.x() - arrow_size * math.cos(angle - math.pi / 6),
            end.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        p3 = QPointF(
            end.x() - arrow_size * math.cos(angle + math.pi / 6),
            end.y() - arrow_size * math.sin(angle + math.pi / 6)
        )

        return QPolygonF([p1, p2, p3])

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        if self._preview_line and self._preview_line.scene():
            canvas._scene.removeItem(self._preview_line)
        if self._preview_head and self._preview_head.scene():
            canvas._scene.removeItem(self._preview_head)

        if self._start_pos and canvas.document:
            page = canvas.document.get_page(page_index)
            if page:
                import fitz
                start = fitz.Point(self._start_pos.x(), self._start_pos.y())
                end = fitz.Point(pos.x(), pos.y())
                color = (self._color.redF(), self._color.greenF(), self._color.blueF())

                annot = page.add_line_annot(start, end)
                annot.set_colors(stroke=color)
                annot.set_border(width=self._thickness)
                # Set line ending to arrow
                annot.set_line_ends(fitz.PDF_ANNOT_LE_NONE, fitz.PDF_ANNOT_LE_CLOSED_ARROW)
                annot.update()
                canvas.document._mark_modified()
                canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview_line = None
        self._preview_head = None
