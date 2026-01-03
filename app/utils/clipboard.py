"""Clipboard operations."""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QMimeData
from PIL import Image
import io


def copy_to_clipboard(image: Image.Image) -> bool:
    """Copy a PIL Image to the system clipboard."""
    try:
        # Convert PIL Image to QImage (safe conversion)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        data = image.tobytes('raw', 'RGBA')
        qimage = QImage(
            data,
            image.width,
            image.height,
            image.width * 4,  # bytes per line - CRITICAL for correctness
            QImage.Format.Format_RGBA8888
        )

        # Make a copy to prevent data corruption from garbage collection
        # This is ESSENTIAL for large images (like 3240x1822 scrolling captures)
        qimage = qimage.copy()

        clipboard = QApplication.clipboard()
        clipboard.setImage(qimage)
        return True
    except Exception:
        return False


def get_from_clipboard() -> Image.Image | None:
    """Get an image from the system clipboard."""
    try:
        clipboard = QApplication.clipboard()
        qimage = clipboard.image()

        if qimage.isNull():
            return None

        # Convert QImage to PIL Image
        qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimage.width()
        height = qimage.height()

        ptr = qimage.bits()
        ptr.setsize(qimage.sizeInBytes())

        return Image.frombytes('RGBA', (width, height), bytes(ptr), 'raw', 'RGBA')
    except Exception:
        return None


def copy_text_to_clipboard(text: str) -> bool:
    """Copy text to the system clipboard."""
    try:
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        return True
    except Exception:
        return False
