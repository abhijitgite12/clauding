"""Text annotation tool."""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import QGraphicsTextItem, QInputDialog, QApplication
from PyQt6.QtGui import QFont, QColor, QCursor

from .base import BaseTool


class TextItem(QGraphicsTextItem):
    """Custom text item for annotations."""

    def __init__(self, text: str, pos: QPointF, color: QColor, font_size: int):
        super().__init__(text)
        self.setPos(pos)
        self.setDefaultTextColor(color)

        font = QFont("Arial", font_size)
        font.setBold(True)
        self.setFont(font)

        # Make selectable and movable
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)


class TextTool(BaseTool):
    """Tool for adding text annotations."""

    def __init__(self):
        super().__init__()
        self._pending_pos = None

    def cursor(self) -> QCursor:
        """Return text cursor."""
        return QCursor(Qt.CursorShape.IBeamCursor)

    def on_press(self, pos: QPointF, canvas):
        """Handle click - show text input dialog."""
        self._pending_pos = pos

    def on_move(self, pos: QPointF, canvas):
        """No preview for text tool."""
        pass

    def on_release(self, pos: QPointF, canvas):
        """Create text annotation."""
        if not self._pending_pos:
            return

        # Get the main window for the dialog parent
        parent = None
        for widget in QApplication.topLevelWidgets():
            if widget.isVisible():
                parent = widget
                break

        text, ok = QInputDialog.getText(
            parent,
            "Add Text",
            "Enter text:",
            text=""
        )

        if ok and text.strip():
            item = TextItem(
                text.strip(),
                self._pending_pos,
                self._color or QColor(255, 0, 0),
                self._font_size
            )
            canvas.add_annotation(item)

        self._pending_pos = None

    def on_cancel(self):
        """Cancel text addition."""
        super().on_cancel()
        self._pending_pos = None
