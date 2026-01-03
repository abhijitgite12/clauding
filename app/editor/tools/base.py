"""Base class for editor tools."""

from abc import ABC, abstractmethod
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QCursor


class BaseTool(ABC):
    """Abstract base class for editor tools."""

    def __init__(self):
        self._color = None
        self._thickness = 3
        self._font_size = 14
        self._is_drawing = False
        self._start_pos = None

    def set_color(self, color):
        """Set the drawing color."""
        self._color = color

    def set_thickness(self, thickness: int):
        """Set the line thickness."""
        self._thickness = thickness

    def set_font_size(self, size: int):
        """Set the font size for text."""
        self._font_size = size

    def cursor(self) -> QCursor:
        """Return the cursor to use for this tool."""
        return QCursor(Qt.CursorShape.CrossCursor)

    @abstractmethod
    def on_press(self, pos: QPointF, canvas):
        """Handle mouse press."""
        pass

    @abstractmethod
    def on_move(self, pos: QPointF, canvas):
        """Handle mouse move."""
        pass

    @abstractmethod
    def on_release(self, pos: QPointF, canvas):
        """Handle mouse release."""
        pass

    def on_cancel(self):
        """Handle tool cancellation (e.g., Escape key)."""
        self._is_drawing = False
        self._start_pos = None
