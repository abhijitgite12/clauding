"""Stamp annotation tool."""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QCursor, QColor
from PyQt6.QtWidgets import QMenu

from .base import PDFBaseTool


class StampTool(PDFBaseTool):
    """Tool for adding stamp annotations."""

    # Predefined stamps
    STAMPS = {
        "Approved": {"text": "APPROVED", "color": (0, 0.5, 0)},
        "Rejected": {"text": "REJECTED", "color": (0.8, 0, 0)},
        "Draft": {"text": "DRAFT", "color": (0.5, 0.5, 0.5)},
        "Final": {"text": "FINAL", "color": (0, 0, 0.5)},
        "Confidential": {"text": "CONFIDENTIAL", "color": (0.8, 0, 0)},
        "For Review": {"text": "FOR REVIEW", "color": (0.8, 0.5, 0)},
        "Void": {"text": "VOID", "color": (0.8, 0, 0)},
        "Completed": {"text": "COMPLETED", "color": (0, 0.5, 0)},
        "Checkmark": {"text": "✓", "color": (0, 0.5, 0)},
        "X Mark": {"text": "✗", "color": (0.8, 0, 0)},
    }

    def __init__(self, stamp_name: str = "Approved"):
        super().__init__()
        self._current_stamp = stamp_name
        self._stamp_size = 100

    def set_stamp(self, name: str):
        """Set the current stamp type."""
        if name in self.STAMPS:
            self._current_stamp = name

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

        if canvas.document and self._current_stamp in self.STAMPS:
            stamp = self.STAMPS[self._current_stamp]
            page = canvas.document.get_page(page_index)

            if page:
                import fitz

                # Create stamp rectangle centered on click
                half_size = self._stamp_size / 2
                rect = fitz.Rect(
                    pos.x() - half_size,
                    pos.y() - half_size / 3,
                    pos.x() + half_size,
                    pos.y() + half_size / 3
                )

                # Add as freetext with border
                annot = page.add_freetext_annot(
                    rect,
                    stamp["text"],
                    fontsize=18,
                    fontname="helv",
                    text_color=stamp["color"],
                    align=fitz.TEXT_ALIGN_CENTER,
                    border_color=stamp["color"],
                )
                annot.set_border(width=2)
                annot.update()
                canvas.document._mark_modified()
                canvas.refresh()

        self._is_active = False
        self._start_pos = None

    @classmethod
    def get_stamp_names(cls) -> list[str]:
        """Get list of available stamp names."""
        return list(cls.STAMPS.keys())
