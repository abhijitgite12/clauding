"""Quick Styles - Pre-defined color and thickness combinations for fast annotation."""

from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
from ..styles import MACOS_COLORS, MACOS_RADIUS
from ..animations import AnimationManager


class QuickStyle:
    """Represents a pre-defined annotation style."""

    def __init__(self, name: str, color: QColor, thickness: int):
        """
        Create a quick style.

        Args:
            name: Display name of the style
            color: QColor for annotations
            thickness: Line thickness (1-20)
        """
        self.name = name
        self.color = color
        self.thickness = thickness


class QuickStyleButton(QPushButton):
    """Button displaying a quick style with color swatch and thickness preview."""

    style_selected = pyqtSignal(QuickStyle)

    def __init__(self, style: QuickStyle, parent=None):
        super().__init__(parent)
        self.style = style
        self._shadow = None

        self.setFixedSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: self.style_selected.emit(self.style))
        self._setup_shadow()

        # macOS Big Sur+ styling
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 2px solid {MACOS_COLORS['border_light']};
                border-radius: {MACOS_RADIUS['large']};
            }}
            QPushButton:hover {{
                border-color: {MACOS_COLORS['primary']};
                background-color: {MACOS_COLORS['primary_ultra_light']};
            }}
            QPushButton:pressed {{
                background-color: {MACOS_COLORS['primary_light']};
            }}
        """)

    def _setup_shadow(self):
        """Add professional shadow effect."""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(15)
        self._shadow.setOffset(0, 3)
        self._shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(self._shadow)

    def paintEvent(self, event):
        """Custom paint to show color circle and thickness line."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw color circle
        painter.setBrush(QBrush(self.style.color))
        painter.setPen(Qt.PenStyle.NoPen)
        circle_size = 32
        circle_x = (self.width() - circle_size) // 2
        circle_y = 15
        painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)

        # Draw thickness line preview
        pen = QPen(self.style.color)
        pen.setWidth(self.style.thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        line_y = circle_y + circle_size + 8
        line_start_x = 15
        line_end_x = self.width() - 15
        painter.drawLine(line_start_x, line_y, line_end_x, line_y)

        painter.end()

    def enterEvent(self, event):
        """Handle hover - enhance shadow."""
        super().enterEvent(event)
        if self._shadow:
            self._shadow.setBlurRadius(22)
            self._shadow.setOffset(0, 5)
            self._shadow.setColor(QColor(0, 122, 255, 40))

    def leaveEvent(self, event):
        """Handle hover end - return shadow to normal."""
        super().leaveEvent(event)
        if self._shadow:
            self._shadow.setBlurRadius(15)
            self._shadow.setOffset(0, 3)
            self._shadow.setColor(QColor(0, 0, 0, 20))

    def mousePressEvent(self, event):
        """Handle press - reduce shadow for tactile feel."""
        if self._shadow:
            self._shadow.setBlurRadius(8)
            self._shadow.setOffset(0, 1)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle release - restore shadow."""
        if self._shadow:
            if self.underMouse():
                self._shadow.setBlurRadius(22)
                self._shadow.setOffset(0, 5)
                self._shadow.setColor(QColor(0, 122, 255, 40))
            else:
                self._shadow.setBlurRadius(15)
                self._shadow.setOffset(0, 3)
                self._shadow.setColor(QColor(0, 0, 0, 20))
        super().mouseReleaseEvent(event)


class QuickStylesPanel(QWidget):
    """Panel containing pre-defined quick style buttons with floating effect."""

    style_applied = pyqtSignal(QuickStyle)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._shadow = None
        self._setup_ui()
        self._setup_shadow()

    def _setup_shadow(self):
        """Add floating shadow effect."""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(30)
        self._shadow.setOffset(0, 8)
        self._shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(self._shadow)

    def _setup_ui(self):
        """Set up the Quick Styles panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Panel styling - translucent card
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 1px solid {MACOS_COLORS['border_light']};
                border-radius: {MACOS_RADIUS['large']};
            }}
        """)

        # Title
        title = QLabel("Quick Styles")
        title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {MACOS_COLORS['text_primary']};
            background: transparent;
            border: none;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("One-click color and thickness presets")
        subtitle.setStyleSheet(f"""
            font-size: 11px;
            color: {MACOS_COLORS['text_secondary']};
            background: transparent;
            border: none;
            margin-bottom: 8px;
        """)
        layout.addWidget(subtitle)

        # Default Quick Styles
        default_styles = [
            QuickStyle("Thin Red", QColor(255, 107, 107), 2),
            QuickStyle("Medium Blue", QColor(0, 122, 255), 4),
            QuickStyle("Bold Green", QColor(81, 207, 102), 6),
            QuickStyle("Highlight", QColor(255, 224, 102), 8),
            QuickStyle("Thick Orange", QColor(255, 184, 77), 5),
            QuickStyle("Fine Purple", QColor(167, 139, 250), 2),
        ]

        # Create grid of style buttons (2 columns)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        col1_layout = QVBoxLayout()
        col1_layout.setSpacing(12)
        col2_layout = QVBoxLayout()
        col2_layout.setSpacing(12)

        for i, style in enumerate(default_styles):
            btn = QuickStyleButton(style)
            btn.style_selected.connect(self._on_style_selected)

            # Add name label below button
            style_container = QWidget()
            style_container.setStyleSheet("background: transparent; border: none;")
            container_layout = QVBoxLayout(style_container)
            container_layout.setSpacing(4)
            container_layout.setContentsMargins(0, 0, 0, 0)

            container_layout.addWidget(btn)

            name_label = QLabel(style.name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet(f"""
                font-size: 10px;
                color: {MACOS_COLORS['text_secondary']};
                background: transparent;
                border: none;
            """)
            container_layout.addWidget(name_label)

            # Add to appropriate column
            if i % 2 == 0:
                col1_layout.addWidget(style_container)
            else:
                col2_layout.addWidget(style_container)

        buttons_layout.addLayout(col1_layout)
        buttons_layout.addLayout(col2_layout)

        layout.addLayout(buttons_layout)
        layout.addStretch()

        # Set fixed width for the panel
        self.setFixedWidth(220)

    def _on_style_selected(self, style: QuickStyle):
        """Handle style selection."""
        self.style_applied.emit(style)

    def show_panel(self):
        """Show panel with slide-in animation."""
        self.setVisible(True)
        AnimationManager.slide_in(self, direction="right", duration=250, distance=30)

    def hide_panel(self):
        """Hide panel with slide-out animation."""
        AnimationManager.slide_out(self, direction="right", duration=250, distance=30)
        # Hide after animation completes
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(250, lambda: self.setVisible(False))
