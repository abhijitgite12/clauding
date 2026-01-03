"""Icon loader for PySnagit - provides professional icons throughout the app."""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QStyle, QApplication
from PyQt6.QtCore import Qt, QSize


class IconLoader:
    """Centralized icon management for professional UI."""

    # Icon mapping - maps our icon names to Qt standard icons or custom rendering
    _ICON_MAP = {
        # Capture modes
        "region": QStyle.StandardPixmap.SP_FileDialogDetailedView,
        "fullscreen": QStyle.StandardPixmap.SP_ComputerIcon,
        "window": QStyle.StandardPixmap.SP_DirIcon,
        "scrolling": QStyle.StandardPixmap.SP_ArrowDown,
        "video": QStyle.StandardPixmap.SP_MediaPlay,
        "gif": QStyle.StandardPixmap.SP_FileIcon,

        # Editor tools
        "select": QStyle.StandardPixmap.SP_ArrowForward,
        "arrow": QStyle.StandardPixmap.SP_ArrowRight,
        "line": QStyle.StandardPixmap.SP_TitleBarShadeButton,
        "rectangle": QStyle.StandardPixmap.SP_FileDialogDetailedView,
        "ellipse": QStyle.StandardPixmap.SP_DialogApplyButton,
        "text": QStyle.StandardPixmap.SP_FileDialogContentsView,
        "highlight": QStyle.StandardPixmap.SP_DirIcon,
        "blur": QStyle.StandardPixmap.SP_BrowserReload,
        "stamp": QStyle.StandardPixmap.SP_FileIcon,
        "crop": QStyle.StandardPixmap.SP_TitleBarMaxButton,

        # Actions
        "copy": QStyle.StandardPixmap.SP_FileDialogInfoView,
        "save": QStyle.StandardPixmap.SP_DialogSaveButton,
        "close": QStyle.StandardPixmap.SP_DialogCloseButton,
        "settings": QStyle.StandardPixmap.SP_FileDialogDetailedView,
    }

    # Custom SVG-like icons using Unicode symbols and custom rendering
    _UNICODE_ICONS = {
        "region": "⬚",      # Selection box
        "fullscreen": "🖥",  # Desktop
        "window": "🪟",      # Window
        "scrolling": "📜",   # Scroll
        "video": "🎥",       # Video camera
        "gif": "🎞",        # Film
        "select": "↖",      # Pointer
        "arrow": "➜",       # Arrow
        "line": "—",        # Line
        "rectangle": "▭",   # Rectangle
        "ellipse": "○",     # Circle
        "text": "A",        # Text
        "highlight": "🖍",  # Highlighter
        "blur": "◌",        # Blur
        "stamp": "★",       # Star
        "crop": "✂",        # Scissors
        "copy": "📋",       # Clipboard
        "save": "💾",       # Save
        "settings": "⚙",    # Gear
    }

    @staticmethod
    def get_icon(name: str, size: int = 24, color: QColor = None) -> QIcon:
        """
        Get an icon by name.

        Args:
            name: Icon identifier (e.g., "region", "arrow", "save")
            size: Icon size in pixels (default 24)
            color: Optional color to tint the icon

        Returns:
            QIcon object
        """
        # Try Unicode symbol first (better looking)
        if name in IconLoader._UNICODE_ICONS:
            return IconLoader._create_text_icon(
                IconLoader._UNICODE_ICONS[name],
                size,
                color or QColor(60, 60, 67)
            )

        # Fallback to Qt standard icons
        if name in IconLoader._ICON_MAP:
            style = QApplication.style()
            return style.standardIcon(IconLoader._ICON_MAP[name])

        # Default fallback
        return QIcon()

    @staticmethod
    def _create_text_icon(text: str, size: int, color: QColor) -> QIcon:
        """Create an icon from a Unicode character."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Set font
        font = painter.font()
        font.setPixelSize(int(size * 0.7))
        font.setBold(True)
        painter.setFont(font)

        # Draw text centered
        painter.setPen(color)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def create_simple_shape_icon(shape: str, size: int, color: QColor) -> QIcon:
        """
        Create a simple geometric shape icon.

        Args:
            shape: "circle", "rectangle", "line", "arrow"
            size: Icon size
            color: Shape color
        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(color)
        painter.setBrush(color)

        margin = size // 6

        if shape == "circle":
            painter.drawEllipse(margin, margin, size - 2*margin, size - 2*margin)
        elif shape == "rectangle":
            painter.drawRect(margin, margin, size - 2*margin, size - 2*margin)
        elif shape == "line":
            painter.drawLine(margin, size // 2, size - margin, size // 2)
        elif shape == "arrow":
            # Simple arrow pointing right
            mid_y = size // 2
            painter.drawLine(margin, mid_y, size - margin, mid_y)
            painter.drawLine(size - margin - size//4, mid_y - size//6, size - margin, mid_y)
            painter.drawLine(size - margin - size//4, mid_y + size//6, size - margin, mid_y)

        painter.end()
        return QIcon(pixmap)
