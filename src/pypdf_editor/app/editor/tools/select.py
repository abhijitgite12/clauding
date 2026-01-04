"""Selection/pan tool for PDF viewing."""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QCursor

from .base import PDFBaseTool


class SelectTool(PDFBaseTool):
    """Tool for selecting and panning in the PDF."""

    def __init__(self):
        super().__init__()

    def cursor(self) -> QCursor:
        """Return arrow cursor for selection."""
        return QCursor(Qt.CursorShape.ArrowCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        """Handle mouse press - start potential selection."""
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

    def on_move(self, pos: QPointF, canvas):
        """Handle mouse move - update selection or prepare for text selection."""
        if not self._is_active:
            return
        # Selection rectangle could be drawn here for text selection

    def on_release(self, pos: QPointF, canvas, page_index: int):
        """Handle mouse release - finalize selection."""
        self._is_active = False
        self._start_pos = None
