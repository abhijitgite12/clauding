"""Redaction/whiteout tool."""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QCursor, QColor, QPen
from PyQt6.QtWidgets import QGraphicsRectItem, QMessageBox

from .base import PDFBaseTool


class RedactTool(PDFBaseTool):
    """Tool for redacting/whiteout content."""

    def __init__(self):
        super().__init__()
        self._color = QColor(0, 0, 0)  # Black redaction
        self._preview = None

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        self._preview = QGraphicsRectItem()
        self._preview.setBrush(QColor(0, 0, 0, 150))
        self._preview.setPen(QPen(Qt.PenStyle.NoPen))
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
                # Confirm redaction (it's permanent)
                result = QMessageBox.question(
                    canvas,
                    "Confirm Redaction",
                    "Redaction permanently removes content. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if result == QMessageBox.StandardButton.Yes:
                    page = canvas.document.get_page(page_index)
                    if page:
                        import fitz
                        pdf_rect = fitz.Rect(
                            rect.x(), rect.y(),
                            rect.x() + rect.width(),
                            rect.y() + rect.height()
                        )

                        # Add redaction annotation
                        annot = page.add_redact_annot(pdf_rect)
                        annot.update()

                        # Apply the redaction (permanently removes content)
                        page.apply_redactions()

                        canvas.document._mark_modified()
                        canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview = None


class WhiteoutTool(PDFBaseTool):
    """Tool for whiteout (covers content without removing)."""

    def __init__(self):
        super().__init__()
        self._preview = None

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        self._preview = QGraphicsRectItem()
        self._preview.setBrush(QColor(255, 255, 255))
        self._preview.setPen(QPen(Qt.PenStyle.NoPen))
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

                    # Add white filled rectangle
                    annot = page.add_rect_annot(pdf_rect)
                    annot.set_colors(stroke=(1, 1, 1), fill=(1, 1, 1))
                    annot.update()
                    canvas.document._mark_modified()
                    canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._preview = None
