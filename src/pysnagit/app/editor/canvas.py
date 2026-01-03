"""Image editor canvas with zoom, pan, and annotation support."""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import (
    QPixmap, QImage, QPainter, QColor, QPen, QBrush,
    QWheelEvent, QMouseEvent, QKeyEvent
)
from PIL import Image
import numpy as np


class EditorCanvas(QGraphicsView):
    """Canvas for viewing and editing images."""

    # Signals
    mouse_pressed = pyqtSignal(QPointF)  # Image coordinates
    mouse_moved = pyqtSignal(QPointF)
    mouse_released = pyqtSignal(QPointF)
    zoom_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._image_item = None
        self._pil_image = None
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0

        self._is_panning = False
        self._pan_start = QPointF()

        self._current_tool = None
        self._annotations = []

        self._setup_view()

    def _setup_view(self):
        """Configure view settings."""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor(64, 64, 64)))

    def set_image(self, image: Image.Image):
        """Set the image to display and edit (optimized conversion)."""
        try:
            # Store reference without copying (saves memory)
            self._pil_image = image

            # Convert PIL to QPixmap (safe conversion)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Keep data reference alive to prevent garbage collection
            self._image_data = image.tobytes('raw', 'RGBA')
            qimage = QImage(
                self._image_data,
                image.width,
                image.height,
                image.width * 4,  # bytes per line
                QImage.Format.Format_RGBA8888
            )
            # Make a copy to avoid data corruption
            qimage = qimage.copy()
            pixmap = QPixmap.fromImage(qimage)

            # Clear and add to scene
            self._scene.clear()
            self._image_item = QGraphicsPixmapItem(pixmap)
            self._scene.addItem(self._image_item)
            self._scene.setSceneRect(self._image_item.boundingRect())

            # Re-add annotations
            for annotation in self._annotations:
                self._scene.addItem(annotation)

            # Fit in view
            self.fit_in_view()
        except Exception as e:
            print(f"Error setting image: {e}")
            import traceback
            traceback.print_exc()

    def get_image(self) -> Image.Image:
        """Get the current image with all annotations rendered."""
        if self._pil_image is None:
            return None

        # Render scene to image
        scene_rect = self._scene.sceneRect()
        image = QImage(
            int(scene_rect.width()),
            int(scene_rect.height()),
            QImage.Format.Format_RGBA8888
        )
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._scene.render(painter)
        painter.end()

        # Convert to PIL
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())

        return Image.frombytes('RGBA', (width, height), bytes(ptr), 'raw', 'RGBA')

    def fit_in_view(self):
        """Fit the image in the view."""
        if self._image_item:
            self.fitInView(self._image_item, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom_factor = self.transform().m11()
            self.zoom_changed.emit(self._zoom_factor)

    def set_zoom(self, factor: float):
        """Set absolute zoom factor."""
        factor = max(self._min_zoom, min(self._max_zoom, factor))
        self.resetTransform()
        self.scale(factor, factor)
        self._zoom_factor = factor
        self.zoom_changed.emit(self._zoom_factor)

    def zoom_in(self):
        """Zoom in."""
        self.set_zoom(self._zoom_factor * 1.25)

    def zoom_out(self):
        """Zoom out."""
        self.set_zoom(self._zoom_factor / 1.25)

    def set_tool(self, tool):
        """Set the current editing tool."""
        self._current_tool = tool
        if tool:
            self.setCursor(tool.cursor())
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def add_annotation(self, item):
        """Add an annotation item to the scene."""
        self._annotations.append(item)
        self._scene.addItem(item)

    def remove_annotation(self, item):
        """Remove an annotation from the scene."""
        if item in self._annotations:
            self._annotations.remove(item)
            self._scene.removeItem(item)

    def clear_annotations(self):
        """Remove all annotations."""
        for item in self._annotations:
            self._scene.removeItem(item)
        self._annotations.clear()

    def _to_image_coords(self, pos: QPointF) -> QPointF:
        """Convert view coordinates to image coordinates."""
        return self.mapToScene(pos.toPoint())

    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom with mouse wheel."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Scroll
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Start panning
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton and self._current_tool:
            # Tool action
            image_pos = self._to_image_coords(QPointF(event.pos()))
            self.mouse_pressed.emit(image_pos)
            self._current_tool.on_press(image_pos, self)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move."""
        if self._is_panning:
            # Pan the view
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        elif self._current_tool:
            image_pos = self._to_image_coords(QPointF(event.pos()))
            self.mouse_moved.emit(image_pos)
            self._current_tool.on_move(image_pos, self)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = False
            if self._current_tool:
                self.setCursor(self._current_tool.cursor())
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton and self._current_tool:
            image_pos = self._to_image_coords(QPointF(event.pos()))
            self.mouse_released.emit(image_pos)
            self._current_tool.on_release(image_pos, self)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press."""
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key.Key_0:
            self.fit_in_view()
        elif event.key() == Qt.Key.Key_1:
            self.set_zoom(1.0)
        else:
            super().keyPressEvent(event)
