"""Icon loading utilities for PyPDF Editor."""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path


class IconLoader:
    """Utility class for loading and caching icons."""

    _cache: dict[str, QIcon] = {}
    _icon_dir: Path | None = None

    @classmethod
    def set_icon_directory(cls, path: Path):
        """Set the directory to load icons from."""
        cls._icon_dir = path

    @classmethod
    def get_icon(
        cls,
        name: str,
        size: int = 24,
        color: QColor | str | None = None
    ) -> QIcon:
        """Get an icon by name, optionally with a custom color."""
        cache_key = f"{name}_{size}_{color}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        icon = cls._load_icon(name, size, color)
        cls._cache[cache_key] = icon
        return icon

    @classmethod
    def _load_icon(cls, name: str, size: int, color: QColor | str | None) -> QIcon:
        """Load an icon from file or create a placeholder."""
        if cls._icon_dir:
            svg_path = cls._icon_dir / f"{name}.svg"
            png_path = cls._icon_dir / f"{name}.png"

            if svg_path.exists():
                return cls._load_svg(svg_path, size, color)
            elif png_path.exists():
                return QIcon(str(png_path))

        # Return empty icon if not found
        return QIcon()

    @classmethod
    def _load_svg(cls, path: Path, size: int, color: QColor | str | None) -> QIcon:
        """Load an SVG icon with optional color tinting."""
        renderer = QSvgRenderer(str(path))
        if not renderer.isValid():
            return QIcon()

        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        if color:
            if isinstance(color, str):
                color = QColor(color)
            pixmap = cls._tint_pixmap(pixmap, color)

        return QIcon(pixmap)

    @classmethod
    def _tint_pixmap(cls, pixmap: QPixmap, color: QColor) -> QPixmap:
        """Apply a color tint to a pixmap."""
        tinted = QPixmap(pixmap.size())
        tinted.fill(Qt.GlobalColor.transparent)

        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), color)
        painter.end()

        return tinted

    @classmethod
    def clear_cache(cls):
        """Clear the icon cache."""
        cls._cache.clear()
