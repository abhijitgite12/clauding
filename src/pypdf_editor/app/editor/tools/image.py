"""Image insertion tool."""

from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QFileDialog, QGraphicsRectItem, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap

from .base import PDFBaseTool


class ImageTool(PDFBaseTool):
    """Tool for inserting images into PDF."""

    SUPPORTED_FORMATS = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"

    def __init__(self):
        super().__init__()
        self._image_path = None
        self._preview = None

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.CrossCursor)

    def on_press(self, pos: QPointF, canvas, page_index: int):
        # First, select an image file
        path, _ = QFileDialog.getOpenFileName(
            canvas,
            "Select Image",
            "",
            self.SUPPORTED_FORMATS
        )

        if not path:
            return

        self._image_path = path
        self._is_active = True
        self._start_pos = pos
        self._current_page = page_index

        # Show preview
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Scale preview
            scaled = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
            self._preview = QGraphicsPixmapItem(scaled)
            self._preview.setPos(pos)
            self._preview.setOpacity(0.7)
            canvas._scene.addItem(self._preview)

    def on_move(self, pos: QPointF, canvas):
        if not self._is_active:
            return

        if self._preview:
            self._preview.setPos(pos)

    def on_release(self, pos: QPointF, canvas, page_index: int):
        if not self._is_active:
            return

        if self._preview and self._preview.scene():
            canvas._scene.removeItem(self._preview)

        if self._image_path and canvas.document:
            page = canvas.document.get_page(page_index)
            if page:
                import fitz

                # Get image dimensions
                pixmap = QPixmap(self._image_path)
                width = min(pixmap.width(), 300)
                height = min(pixmap.height(), 300)

                # Scale to fit
                aspect = pixmap.width() / pixmap.height()
                if width / height > aspect:
                    width = height * aspect
                else:
                    height = width / aspect

                rect = fitz.Rect(
                    pos.x(), pos.y(),
                    pos.x() + width,
                    pos.y() + height
                )

                # Insert image
                page.insert_image(rect, filename=self._image_path)
                canvas.document._mark_modified()
                canvas.refresh()

        self._is_active = False
        self._start_pos = None
        self._image_path = None
        self._preview = None
