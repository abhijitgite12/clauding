"""Text annotation tools."""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QCursor, QColor, QPen
from PyQt6.QtWidgets import QInputDialog, QGraphicsRectItem

from .base import PDFBaseTool


class TextBoxTool(PDFBaseTool):
    """Tool for adding free text annotations."""

    def __init__(self):
        super().__init__()
        self._color = QColor(0, 0, 0)
        self._font_size = 12
        self._preview_rect = None

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.IBeamCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        # Create preview rectangle
        self._preview_rect = QGraphicsRectItem()
        self._preview_rect.setPen(QPen(Qt.GlobalColor.blue))
        self._preview_rect.setBrush(QColor(200, 200, 255, 50))

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active or not self._start_pos:
            return

        if self._preview_rect:
            rect = QRectF(self._start_pos, pos).normalized()
            self._preview_rect.setRect(rect)

            if self._preview_rect.scene() is None:
                canvas._scene.addItem(self._preview_rect)

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        # Remove preview
        if self._preview_rect and self._preview_rect.scene():
            canvas._scene.removeItem(self._preview_rect)

        # Get text from user
        if self._start_pos and canvas.document:
            rect = QRectF(self._start_pos, pos).normalized()
            if rect.width() > 20 and rect.height() > 10:
                text, ok = QInputDialog.getMultiLineText(
                    canvas,
                    "Add Text",
                    "Enter text:",
                    ""
                )
                if ok and text:
                    import fitz
                    pdf_rect = fitz.Rect(
                        rect.x(), rect.y(),
                        rect.x() + rect.width(),
                        rect.y() + rect.height()
                    )
                    color = (
                        self._color.redF(),
                        self._color.greenF(),
                        self._color.blueF()
                    )
                    canvas.document.add_freetext(
                        page_index,
                        pdf_rect,
                        text,
                        fontsize=self._font_size,
                        color=color
                    )
                    canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview_rect = None


class StickyNoteTool(PDFBaseTool):
    """Tool for adding sticky note comments."""

    NOTE_COLORS = {
        "yellow": (1, 1, 0),
        "green": (0, 1, 0),
        "blue": (0, 0, 1),
        "red": (1, 0, 0),
    }

    def __init__(self, color: str = "yellow"):
        super().__init__()
        self._note_color = self.NOTE_COLORS.get(color, self.NOTE_COLORS["yellow"])

    def set_note_color(self, color: str):
        """Set note color by name."""
        if color in self.NOTE_COLORS:
            self._note_color = self.NOTE_COLORS[color]

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

    def on_move(self, pos: QPointF, canvas):
        pass

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        # Get comment from user
        if canvas.document:
            text, ok = QInputDialog.getMultiLineText(
                canvas,
                "Add Comment",
                "Enter your comment:",
                ""
            )
            if ok and text:
                import fitz
                pdf_rect = fitz.Rect(
                    pos.x(), pos.y(),
                    pos.x() + 20, pos.y() + 20
                )
                canvas.document.add_text_annotation(
                    page_index,
                    pdf_rect,
                    text,
                    color=self._note_color
                )
                canvas.refresh()

        self._is_active = False
        self._start_pos = None
