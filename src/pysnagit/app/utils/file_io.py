"""File I/O operations for images and videos."""

from pathlib import Path
from datetime import datetime
from PIL import Image
from PyQt6.QtWidgets import QFileDialog


def generate_filename(prefix: str = "capture", extension: str = "png") -> str:
    """Generate a timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def save_image(
    image: Image.Image,
    path: Path | str | None = None,
    format: str = "PNG",
    quality: int = 95
) -> Path | None:
    """Save a PIL Image to disk."""
    try:
        if path is None:
            return None

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs = {}
        if format.upper() in ('JPEG', 'JPG'):
            save_kwargs['quality'] = quality
            if image.mode == 'RGBA':
                image = image.convert('RGB')
        elif format.upper() == 'PNG':
            save_kwargs['compress_level'] = 6

        image.save(path, format=format, **save_kwargs)
        return path
    except Exception:
        return None


def load_image(path: Path | str) -> Image.Image | None:
    """Load an image from disk."""
    try:
        return Image.open(path).copy()
    except Exception:
        return None


def get_save_path(
    parent=None,
    default_name: str = "",
    filters: str = "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*.*)"
) -> Path | None:
    """Show a save file dialog and return the selected path."""
    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Save Image",
        default_name,
        filters
    )
    return Path(path) if path else None


def get_open_path(
    parent=None,
    filters: str = "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
) -> Path | None:
    """Show an open file dialog and return the selected path."""
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Open Image",
        "",
        filters
    )
    return Path(path) if path else None
