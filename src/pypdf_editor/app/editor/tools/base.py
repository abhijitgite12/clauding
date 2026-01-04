"""Base class for PDF annotation tools."""

from abc import ABC, abstractmethod
from typing import Optional

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QCursor, QColor


class PDFBaseTool(ABC):
    """Abstract base class for PDF annotation tools."""

    def __init__(self):
        self._color: QColor = QColor(255, 0, 0)
        self._thickness: int = 2
        self._opacity: float = 1.0
        self._font_size: int = 12
        self._is_active: bool = False
        self._start_pos: Optional[QPointF] = None
        self._current_page: int = 0

    @property
    def color(self) -> QColor:
        return self._color

    def set_color(self, color: QColor):
        """Set the tool color."""
        self._color = color

    @property
    def thickness(self) -> int:
        return self._thickness

    def set_thickness(self, thickness: int):
        """Set the line thickness."""
        self._thickness = max(1, thickness)

    @property
    def opacity(self) -> float:
        return self._opacity

    def set_opacity(self, opacity: float):
        """Set the opacity (0.0 to 1.0)."""
        self._opacity = max(0.0, min(1.0, opacity))

    @property
    def font_size(self) -> int:
        return self._font_size

    def set_font_size(self, size: int):
        """Set the font size for text tools."""
        self._font_size = max(6, size)

    def cursor(self) -> QCursor:
        """Return the cursor to use when this tool is active."""
        return QCursor(Qt.CursorShape.CrossCursor)

    @abstractmethod
    def on_press(self, pos: QPointF, canvas, page_index: int):
        """Handle mouse press at position (in PDF coordinates)."""
        pass

    @abstractmethod
    def on_move(self, pos: QPointF, canvas):
        """Handle mouse move to position."""
        pass

    @abstractmethod
    def on_release(self, pos: QPointF, canvas, page_index: int):
        """Handle mouse release at position."""
        pass

    def on_cancel(self):
        """Cancel the current operation."""
        self._is_active = False
        self._start_pos = None

    def reset(self):
        """Reset tool state."""
        self._is_active = False
        self._start_pos = None
