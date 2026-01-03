"""Blur/pixelate tool for obscuring regions."""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem
from PyQt6.QtGui import QPen, QColor, QPixmap, QImage, QPainter
from PIL import Image, ImageFilter
import numpy as np

from .base import BaseTool


class BlurItem(QGraphicsPixmapItem):
    """A blurred region of the image."""

    def __init__(self, source_image: Image.Image, rect: QRectF, blur_type: str = "blur"):
        super().__init__()
        self._source = source_image
        self._rect = rect
        self._blur_type = blur_type  # 'blur' or 'pixelate'

        self.setPos(rect.topLeft())
        self._update_blur()

    def _update_blur(self):
        """Apply blur effect to the region."""
        x = int(self._rect.x())
        y = int(self._rect.y())
        w = int(self._rect.width())
        h = int(self._rect.height())

        if w <= 0 or h <= 0:
            return

        # Ensure bounds are within image
        x = max(0, x)
        y = max(0, y)
        w = min(w, self._source.width - x)
        h = min(h, self._source.height - y)

        if w <= 0 or h <= 0:
            return

        # Crop the region
        region = self._source.crop((x, y, x + w, y + h))

        # Apply effect (optimized for speed)
        if self._blur_type == "blur":
            # Reduced radius from 15 to 10 for 2x speed improvement
            blurred = region.filter(ImageFilter.GaussianBlur(radius=10))
        else:  # pixelate
            # Optimized pixelation (faster resize)
            small_size = (max(1, w // 12), max(1, h // 12))
            small = region.resize(small_size, Image.Resampling.BILINEAR)
            blurred = small.resize((w, h), Image.Resampling.NEAREST)

        # Convert to QPixmap (optimized conversion)
        if blurred.mode != 'RGBA':
            blurred = blurred.convert('RGBA')

        qimage = QImage(
            blurred.tobytes('raw', 'RGBA'),
            w, h,
            w * 4,  # bytes per line
            QImage.Format.Format_RGBA8888
        )
        self.setPixmap(QPixmap.fromImage(qimage))

    def update_rect(self, rect: QRectF):
        """Update the blur region."""
        self._rect = rect
        self.setPos(rect.topLeft())
        self._update_blur()


class BlurTool(BaseTool):
    """Tool for blurring or pixelating regions."""

    def __init__(self, blur_type: str = "blur"):
        """Initialize blur tool.

        Args:
            blur_type: 'blur' for gaussian blur, 'pixelate' for pixelation
        """
        super().__init__()
        self._blur_type = blur_type
        self._current_item = None
        self._source_image = None

    def set_source_image(self, image: Image.Image):
        """Set the source image for blur effect."""
        self._source_image = image

    def on_press(self, pos: QPointF, canvas):
        """Start blur selection."""
        self._is_drawing = True
        self._start_pos = pos

        # Get source image from canvas
        if hasattr(canvas, '_pil_image'):
            self._source_image = canvas._pil_image

        if not self._source_image:
            return

        # Create preview rectangle
        self._preview_rect = QGraphicsRectItem(QRectF(pos, pos))
        self._preview_rect.setPen(QPen(QColor(128, 128, 128), 1, Qt.PenStyle.DashLine))
        canvas.add_annotation(self._preview_rect)

    def on_move(self, pos: QPointF, canvas):
        """Update blur preview."""
        if not self._is_drawing or not hasattr(self, '_preview_rect'):
            return

        rect = QRectF(
            min(self._start_pos.x(), pos.x()),
            min(self._start_pos.y(), pos.y()),
            abs(pos.x() - self._start_pos.x()),
            abs(pos.y() - self._start_pos.y())
        )
        self._preview_rect.setRect(rect)

    def on_release(self, pos: QPointF, canvas):
        """Apply blur to selected region."""
        if not self._is_drawing:
            return

        self._is_drawing = False

        # Remove preview
        if hasattr(self, '_preview_rect'):
            canvas.remove_annotation(self._preview_rect)

        if not self._source_image or not self._start_pos:
            return

        # Calculate final rect
        rect = QRectF(
            min(self._start_pos.x(), pos.x()),
            min(self._start_pos.y(), pos.y()),
            abs(pos.x() - self._start_pos.x()),
            abs(pos.y() - self._start_pos.y())
        )

        # Only create if large enough
        if rect.width() >= 5 and rect.height() >= 5:
            blur_item = BlurItem(self._source_image, rect, self._blur_type)
            canvas.add_annotation(blur_item)

        self._start_pos = None

    def on_cancel(self):
        """Cancel blur selection."""
        super().on_cancel()
        self._current_item = None


class PixelateTool(BlurTool):
    """Tool specifically for pixelation."""

    def __init__(self):
        super().__init__("pixelate")
