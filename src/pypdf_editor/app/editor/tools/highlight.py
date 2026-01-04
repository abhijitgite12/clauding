"""Text highlighting tool."""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QCursor, QColor, QPen
from PyQt6.QtWidgets import QGraphicsRectItem

from .base import PDFBaseTool


class HighlightTool(PDFBaseTool):
    """Tool for highlighting text in PDF."""

    # Preset highlight colors
    COLORS = {
        "yellow": QColor(255, 255, 0, 100),
        "green": QColor(144, 238, 144, 100),
        "blue": QColor(135, 206, 235, 100),
        "pink": QColor(255, 182, 193, 100),
        "orange": QColor(255, 165, 0, 100),
    }

    def __init__(self, color: str = "yellow"):
        super().__init__()
        self._highlight_color = self.COLORS.get(color, self.COLORS["yellow"])
        self._preview_rect = None
        self._color = self._highlight_color

    def set_highlight_color(self, color: str):
        """Set highlight color by name."""
        if color in self.COLORS:
            self._highlight_color = self.COLORS[color]
            self._color = self._highlight_color

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.IBeamCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        # Create preview rectangle
        self._preview_rect = QGraphicsRectItem()
        self._preview_rect.setBrush(self._highlight_color)
        self._preview_rect.setPen(QPen(Qt.PenStyle.NoPen))
        self._preview_rect.setOpacity(0.5)

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active or not self._start_pos:
            return

        # Update preview rectangle
        if self._preview_rect:
            rect = QRectF(self._start_pos, pos).normalized()
            # Constrain height for text-line highlighting
            rect.setHeight(min(rect.height(), 20))
            self._preview_rect.setRect(rect)

            if self._preview_rect.scene() is None:
                canvas._scene.addItem(self._preview_rect)

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        # Remove preview
        if self._preview_rect and self._preview_rect.scene():
            canvas._scene.removeItem(self._preview_rect)

        # Create actual highlight annotation
        if self._start_pos and canvas.document:
            rect = QRectF(self._start_pos, pos).normalized()
            if rect.width() > 5 and rect.height() > 2:
                # Convert color to PDF format (0-1 range)
                color = (
                    self._highlight_color.redF(),
                    self._highlight_color.greenF(),
                    self._highlight_color.blueF()
                )

                import fitz
                pdf_rect = fitz.Rect(
                    rect.x(), rect.y(),
                    rect.x() + rect.width(),
                    rect.y() + rect.height()
                )
                canvas.document.add_highlight(page_index, pdf_rect, color)
                canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview_rect = None


class UnderlineTool(PDFBaseTool):
    """Tool for underlining text."""

    def __init__(self):
        super().__init__()
        self._color = QColor(255, 0, 0)

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.IBeamCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

    def on_move(self, pos: QPointF, canvas):
        pass

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active or not self._start_pos:
            return

        if canvas.document:
            rect = QRectF(self._start_pos, pos).normalized()
            if rect.width() > 5:
                import fitz
                pdf_rect = fitz.Rect(
                    rect.x(), rect.y(),
                    rect.x() + rect.width(),
                    rect.y() + rect.height()
                )
                page = canvas.document.get_page(page_index)
                if page:
                    annot = page.add_underline_annot(pdf_rect)
                    annot.update()
                    canvas.document._mark_modified()
                    canvas.refresh()

        self._is_active = False
        self._start_pos = None


class StrikethroughTool(PDFBaseTool):
    """Tool for strikethrough text."""

    def __init__(self):
        super().__init__()
        self._color = QColor(255, 0, 0)

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.IBeamCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

    def on_move(self, pos: QPointF, canvas):
        pass

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active or not self._start_pos:
            return

        if canvas.document:
            rect = QRectF(self._start_pos, pos).normalized()
            if rect.width() > 5:
                import fitz
                pdf_rect = fitz.Rect(
                    rect.x(), rect.y(),
                    rect.x() + rect.width(),
                    rect.y() + rect.height()
                )
                page = canvas.document.get_page(page_index)
                if page:
                    annot = page.add_strikeout_annot(pdf_rect)
                    annot.update()
                    canvas.document._mark_modified()
                    canvas.refresh()

        self._is_active = False
        self._start_pos = None
