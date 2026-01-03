"""Crop tool."""

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QBrush, QColor, QCursor

from .base import BaseTool


class CropOverlay(QGraphicsRectItem):
    """Overlay showing the crop area."""

    def __init__(self, scene_rect: QRectF):
        super().__init__(scene_rect)
        self._crop_rect = QRectF()
        self._scene_rect = scene_rect

        # Dark overlay
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(QColor(0, 0, 0, 150)))

    def set_crop_rect(self, rect: QRectF):
        """Set the crop selection rectangle."""
        self._crop_rect = rect
        self.update()

    def paint(self, painter, option, widget):
        """Custom paint to show crop area as transparent."""
        # Fill the entire area with dark overlay
        painter.fillRect(self._scene_rect, QColor(0, 0, 0, 150))

        # Cut out the crop area (make it transparent)
        if not self._crop_rect.isEmpty():
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self._crop_rect, Qt.GlobalColor.transparent)

            # Draw crop border
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.PenStyle.DashLine))
            painter.drawRect(self._crop_rect)

            # Draw corner handles
            handle_size = 8
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(0, 0, 0), 1))

            corners = [
                self._crop_rect.topLeft(),
                self._crop_rect.topRight(),
                self._crop_rect.bottomLeft(),
                self._crop_rect.bottomRight()
            ]

            for corner in corners:
                painter.drawRect(
                    int(corner.x() - handle_size / 2),
                    int(corner.y() - handle_size / 2),
                    handle_size,
                    handle_size
                )


class CropTool(BaseTool):
    """Tool for cropping the image."""

    def __init__(self):
        super().__init__()
        self._overlay = None
        self._crop_rect = QRectF()

    def cursor(self) -> QCursor:
        """Return crop cursor."""
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas):
        """Start crop selection."""
        self._is_drawing = True
        self._start_pos = pos
        self._crop_rect = QRectF()

        # Create overlay
        if hasattr(canvas, '_scene'):
            scene_rect = canvas._scene.sceneRect()
            self._overlay = CropOverlay(scene_rect)
            canvas._scene.addItem(self._overlay)

    def on_move(self, pos: QPointF, canvas):
        """Update crop preview."""
        if not self._is_drawing or not self._overlay:
            return

        self._crop_rect = QRectF(
            min(self._start_pos.x(), pos.x()),
            min(self._start_pos.y(), pos.y()),
            abs(pos.x() - self._start_pos.x()),
            abs(pos.y() - self._start_pos.y())
        )
        self._overlay.set_crop_rect(self._crop_rect)

    def on_release(self, pos: QPointF, canvas):
        """Finish crop selection - apply crop."""
        if not self._is_drawing:
            return

        self._is_drawing = False

        # Remove overlay
        if self._overlay and hasattr(canvas, '_scene'):
            canvas._scene.removeItem(self._overlay)
            self._overlay = None

        # Apply crop if valid
        if self._crop_rect.width() >= 10 and self._crop_rect.height() >= 10:
            self._apply_crop(canvas)

        self._start_pos = None

    def _apply_crop(self, canvas):
        """Apply the crop to the image."""
        if not hasattr(canvas, '_pil_image') or not canvas._pil_image:
            return

        # Get crop bounds
        x = int(max(0, self._crop_rect.x()))
        y = int(max(0, self._crop_rect.y()))
        right = int(min(canvas._pil_image.width, self._crop_rect.right()))
        bottom = int(min(canvas._pil_image.height, self._crop_rect.bottom()))

        if right <= x or bottom <= y:
            return

        # Crop the image
        cropped = canvas._pil_image.crop((x, y, right, bottom))

        # Clear annotations (they're relative to old image)
        canvas.clear_annotations()

        # Set new image
        canvas.set_image(cropped)

    def on_cancel(self):
        """Cancel crop selection."""
        super().on_cancel()
        self._crop_rect = QRectF()

    def get_crop_rect(self) -> QRectF:
        """Get the current crop rectangle."""
        return self._crop_rect
