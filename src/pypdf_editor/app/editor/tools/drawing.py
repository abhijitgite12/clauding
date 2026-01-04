"""Freehand drawing tool."""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QCursor, QColor, QPen
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui import QPainterPath

from .base import PDFBaseTool


class DrawingTool(PDFBaseTool):
    """Freehand pen/pencil drawing tool."""

    def __init__(self):
        super().__init__()
        self._color = QColor(255, 0, 0)
        self._thickness = 2
        self._points = []
        self._preview_path = None

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index
        self._points = [pos]

        # Create preview path
        self._preview_path = QGraphicsPathItem()
        pen = QPen(self._color, self._thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self._preview_path.setPen(pen)

        path = QPainterPath()
        path.moveTo(pos)
        self._preview_path.setPath(path)
        canvas._scene.addItem(self._preview_path)

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active:
            return

        self._points.append(pos)

        # Update preview path
        if self._preview_path:
            path = self._preview_path.path()
            path.lineTo(pos)
            self._preview_path.setPath(path)

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        # Remove preview
        if self._preview_path and self._preview_path.scene():
            canvas._scene.removeItem(self._preview_path)

        # Create ink annotation
        if len(self._points) > 1 and canvas.document:
            page = canvas.document.get_page(page_index)
            if page:
                import fitz
                # Convert points to fitz format
                ink_list = [[fitz.Point(p.x(), p.y()) for p in self._points]]

                annot = page.add_ink_annot(ink_list)
                color = (
                    self._color.redF(),
                    self._color.greenF(),
                    self._color.blueF()
                )
                annot.set_colors(stroke=color)
                annot.set_border(width=self._thickness)
                annot.update()
                canvas.document._mark_modified()
                canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._points = []
        self._preview_path = None


class EraserTool(PDFBaseTool):
    """Tool for erasing annotations."""

    def __init__(self):
        super().__init__()

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._current_page = page_index
        self._erase_at(pos, canvas, page_index)

    def on_move(self, pos: QPointF, canvas):
        if self._is_active:
            self._erase_at(pos, canvas, self._current_page)

    def on_release(self, pos: QPointF, canvas, page_index: int):
        self._is_active = False

    def _erase_at(self, pos: QPointF, canvas, page_index: int):
        """Erase annotations at position."""
        if not canvas.document:
            return

        page = canvas.document.get_page(page_index)
        if not page:
            return

        import fitz
        point = fitz.Point(pos.x(), pos.y())

        # Check each annotation
        for annot in page.annots():
            if annot.rect.contains(point):
                page.delete_annot(annot)
                canvas.document._mark_modified()
                canvas.refresh()
                break
