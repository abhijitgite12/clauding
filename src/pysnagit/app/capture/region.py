"""Region selection overlay for screen capture - macOS Big Sur+ style."""

from PyQt6.QtWidgets import QWidget, QApplication, QRubberBand
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QCursor, QScreen, QFont
from PIL import Image
import mss
from ..styles import MACOS_COLORS
from ..animations import AnimationManager


class RegionSelector(QWidget):
    """Full-screen overlay for selecting a region to capture."""

    region_selected = pyqtSignal(QRect)
    selection_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._start_pos = None
        self._current_pos = None
        self._rubber_band = None
        self._is_selecting = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up the overlay UI."""
        # Cover all screens
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Get combined geometry of all screens
        screens = QApplication.screens()
        if screens:
            combined = screens[0].geometry()
            for screen in screens[1:]:
                combined = combined.united(screen.geometry())
            self.setGeometry(combined)

    def showEvent(self, event):
        """Handle show event (fade-in disabled due to opacity conflicts)."""
        super().showEvent(event)
        # Ensure we capture mouse
        self.grabMouse()
        self.grabKeyboard()

    def hideEvent(self, event):
        """Handle hide event."""
        self.releaseMouse()
        self.releaseKeyboard()
        super().hideEvent(event)

    def paintEvent(self, event):
        """Paint the overlay with macOS Big Sur+ styling."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # If selecting, draw the clear selection area
        if self._start_pos and self._current_pos:
            selection = self._get_selection_rect()

            # Clear the selection area (make it transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection, Qt.GlobalColor.transparent)

            # Draw border around selection - macOS style with softer blue and rounded corners
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # Parse macOS primary color (#007AFF)
            primary_color = QColor(0, 122, 255)
            pen = QPen(primary_color, 3)
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            # Draw rectangle with rounded corners
            painter.drawRoundedRect(selection, 8, 8)

            # Draw dimensions with pill-shaped translucent background
            dims = f"{selection.width()} × {selection.height()}"

            # Set up font
            font = QFont("Segoe UI", 12)
            font.setWeight(QFont.Weight.Medium)
            painter.setFont(font)

            # Calculate text size for background pill
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(dims)
            text_height = fm.height()

            # Position above selection, centered
            pill_padding = 12
            pill_width = text_width + pill_padding * 2
            pill_height = text_height + pill_padding
            pill_x = selection.center().x() - pill_width // 2
            pill_y = selection.top() - pill_height - 10

            # Draw pill background
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(40, 40, 43, 200))  # Translucent dark
            painter.drawRoundedRect(pill_x, pill_y, pill_width, pill_height, pill_height // 2, pill_height // 2)

            # Draw text
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(
                pill_x + pill_padding,
                pill_y + pill_padding + fm.ascent(),
                dims
            )

    def mousePressEvent(self, event):
        """Handle mouse press - start selection."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = event.pos()
            self._current_pos = event.pos()
            self._is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move - update selection."""
        if self._is_selecting:
            self._current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release - complete selection."""
        if event.button() == Qt.MouseButton.LeftButton and self._is_selecting:
            self._is_selecting = False
            selection = self._get_selection_rect()

            if selection.width() > 5 and selection.height() > 5:
                # Emit the selection in screen coordinates
                global_rect = QRect(
                    self.mapToGlobal(selection.topLeft()),
                    selection.size()
                )
                self.region_selected.emit(global_rect)

            self.hide()
            self._reset()

    def keyPressEvent(self, event):
        """Handle key press - escape cancels."""
        if event.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.hide()
            self._reset()

    def _get_selection_rect(self) -> QRect:
        """Get the normalized selection rectangle."""
        if not self._start_pos or not self._current_pos:
            return QRect()

        return QRect(
            min(self._start_pos.x(), self._current_pos.x()),
            min(self._start_pos.y(), self._current_pos.y()),
            abs(self._current_pos.x() - self._start_pos.x()),
            abs(self._current_pos.y() - self._start_pos.y())
        )

    def _reset(self):
        """Reset selection state."""
        self._start_pos = None
        self._current_pos = None
        self._is_selecting = False


def capture_selected_region(rect: QRect) -> Image.Image:
    """Capture the selected region.

    Args:
        rect: QRect in screen coordinates

    Returns:
        PIL Image of the captured region
    """
    with mss.mss() as sct:
        region = {
            "left": rect.x(),
            "top": rect.y(),
            "width": rect.width(),
            "height": rect.height()
        }
        screenshot = sct.grab(region)
        return Image.frombytes(
            'RGB',
            (screenshot.width, screenshot.height),
            screenshot.rgb
        )
