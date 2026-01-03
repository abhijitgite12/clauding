"""Editor toolbar with tool and color selection - macOS Big Sur+ style."""

from PyQt6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QPushButton,
    QColorDialog, QSpinBox, QLabel, QComboBox, QToolButton, QSlider,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QAction
from ..styles import MACOS_COLORS, MACOS_RADIUS
from ..animations import AnimationManager
from ..utils.icon_loader import IconLoader
from .quick_styles import QuickStylesPanel


class ColorButton(QPushButton):
    """Button that displays and selects a color - macOS Big Sur+ style with shadow."""

    color_changed = pyqtSignal(QColor)

    def __init__(self, color: QColor = QColor(255, 0, 0), parent=None):
        super().__init__(parent)
        self._color = color
        self._shadow = None
        self.setFixedSize(40, 40)  # Larger for macOS style
        self.clicked.connect(self._pick_color)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_icon()
        self._setup_shadow()

        # macOS styling with ring shadow
        self.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {MACOS_COLORS['border']};
                border-radius: {MACOS_RADIUS['medium']};
                background: transparent;
            }}
            QPushButton:hover {{
                border-color: {MACOS_COLORS['primary']};
            }}
        """)

    def _setup_shadow(self):
        """Add professional shadow effect."""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(12)
        self._shadow.setOffset(0, 2)
        self._shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(self._shadow)

    def color(self) -> QColor:
        return self._color

    def set_color(self, color: QColor):
        self._color = color
        self._update_icon()

    def _update_icon(self):
        """Update the button icon to show current color."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Draw color swatch with rounded corners
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(2, 2, 28, 28, 8, 8)
        painter.end()

        self.setIcon(QIcon(pixmap))

    def _pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self._color, self, "Select Color")
        if color.isValid():
            self._color = color
            self._update_icon()
            self.color_changed.emit(color)

    def enterEvent(self, event):
        """Handle hover - enhance shadow."""
        super().enterEvent(event)
        if self._shadow:
            self._shadow.setBlurRadius(18)
            self._shadow.setColor(QColor(0, 122, 255, 50))

    def leaveEvent(self, event):
        """Handle hover end - return shadow to normal."""
        super().leaveEvent(event)
        if self._shadow:
            self._shadow.setBlurRadius(12)
            self._shadow.setColor(QColor(0, 0, 0, 25))

    def mousePressEvent(self, event):
        """Handle press - reduce shadow for tactile feel."""
        if self._shadow:
            self._shadow.setBlurRadius(6)
            self._shadow.setOffset(0, 1)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle release - restore shadow."""
        if self._shadow:
            self._shadow.setBlurRadius(18 if self.underMouse() else 12)
            self._shadow.setOffset(0, 2)
        super().mouseReleaseEvent(event)


class EditorToolbar(QToolBar):
    """Toolbar for the image editor."""

    # Signals
    tool_selected = pyqtSignal(str)
    color_changed = pyqtSignal(QColor)
    thickness_changed = pyqtSignal(int)
    font_size_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__("Tools", parent)
        self._current_tool = None
        self._tool_buttons = {}
        self._quick_styles_panel = None
        self._quick_styles_btn = None

        self.setMovable(False)
        self._setup_tools()
        self._setup_quick_styles()

    def _setup_tools(self):
        """Set up toolbar buttons."""
        # Selection/Move tool
        self._add_tool_button("select", "Select", "Move and select annotations")

        self.addSeparator()

        # Drawing tools
        self._add_tool_button("arrow", "Arrow", "Draw arrows")
        self._add_tool_button("line", "Line", "Draw straight lines")
        self._add_tool_button("rect", "Rectangle", "Draw rectangles")
        self._add_tool_button("ellipse", "Ellipse", "Draw ellipses")
        self._add_tool_button("text", "Text", "Add text annotations")
        self._add_tool_button("highlight", "Highlight", "Highlight areas")
        self._add_tool_button("blur", "Blur", "Blur regions")
        self._add_tool_button("stamp", "Stamp", "Add stamps/icons")

        self.addSeparator()

        # Crop tool
        self._add_tool_button("crop", "Crop", "Crop the image")

        self.addSeparator()

        # Color picker - more compact
        color_label = QLabel("Color")
        color_label.setStyleSheet(f"""
            color: {MACOS_COLORS['text_secondary']};
            font-size: 11px;
            font-weight: 600;
            padding: 0 4px;
        """)
        self.addWidget(color_label)

        self._color_button = ColorButton(QColor(255, 0, 0))
        self._color_button.color_changed.connect(self.color_changed.emit)
        self.addWidget(self._color_button)

        self.addSeparator()

        # Line thickness - slider instead of spinbox for modern feel
        thickness_label = QLabel("Thickness")
        thickness_label.setStyleSheet(f"""
            color: {MACOS_COLORS['text_secondary']};
            font-size: 11px;
            font-weight: 600;
            padding: 0 4px;
        """)
        self.addWidget(thickness_label)

        # Thickness slider widget
        thickness_container = QWidget()
        thickness_layout = QHBoxLayout(thickness_container)
        thickness_layout.setContentsMargins(4, 0, 4, 0)
        thickness_layout.setSpacing(6)

        self._thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self._thickness_slider.setRange(1, 20)
        self._thickness_slider.setValue(3)
        self._thickness_slider.setFixedWidth(100)
        self._thickness_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: {MACOS_COLORS['border_light']};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {MACOS_COLORS['primary']};
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {MACOS_COLORS['primary_hover']};
            }}
        """)
        self._thickness_slider.valueChanged.connect(self.thickness_changed.emit)
        thickness_layout.addWidget(self._thickness_slider)

        self._thickness_value_label = QLabel("3")
        self._thickness_value_label.setStyleSheet(f"""
            color: {MACOS_COLORS['text_primary']};
            font-size: 12px;
            font-weight: 600;
            min-width: 20px;
        """)
        self._thickness_slider.valueChanged.connect(
            lambda v: self._thickness_value_label.setText(str(v))
        )
        thickness_layout.addWidget(self._thickness_value_label)

        self.addWidget(thickness_container)

        self.addSeparator()

        # Font size - compact spinbox
        font_label = QLabel("Font")
        font_label.setStyleSheet(f"""
            color: {MACOS_COLORS['text_secondary']};
            font-size: 11px;
            font-weight: 600;
            padding: 0 4px;
        """)
        self.addWidget(font_label)

        self._font_spin = QSpinBox()
        self._font_spin.setRange(8, 72)
        self._font_spin.setValue(14)
        self._font_spin.setFixedWidth(60)
        self._font_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 1px solid {MACOS_COLORS['border_light']};
                border-radius: {MACOS_RADIUS['small']};
                padding: 4px 8px;
                font-size: 12px;
            }}
            QSpinBox:hover {{
                border-color: {MACOS_COLORS['primary']};
            }}
        """)
        self._font_spin.valueChanged.connect(self.font_size_changed.emit)
        self.addWidget(self._font_spin)

    def _add_tool_button(self, tool_id: str, name: str, tooltip: str):
        """Add a professional icon-based tool button to the toolbar."""
        button = QToolButton()

        # Set icon from IconLoader
        icon = IconLoader.get_icon(tool_id, size=24, color=QColor(60, 60, 67))
        button.setIcon(icon)
        button.setIconSize(QSize(24, 24))

        # Tooltip with name and shortcut
        button.setToolTip(f"{name}\n{tooltip}")
        button.setCheckable(True)
        button.clicked.connect(lambda checked, t=tool_id: self._on_tool_clicked(t))

        # macOS-style button appearance
        button.setFixedSize(44, 44)
        button.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: {MACOS_RADIUS['medium']};
                padding: 8px;
            }}
            QToolButton:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
            }}
            QToolButton:checked {{
                background-color: {MACOS_COLORS['primary_ultra_light']};
                border: 2px solid {MACOS_COLORS['primary']};
            }}
            QToolButton:pressed {{
                background-color: {MACOS_COLORS['border_light']};
            }}
        """)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        self._tool_buttons[tool_id] = button
        self.addWidget(button)

    def _on_tool_clicked(self, tool_id: str):
        """Handle tool button click with smooth animation."""
        # Animate previously selected button back to normal
        if self._current_tool and self._current_tool in self._tool_buttons:
            prev_btn = self._tool_buttons[self._current_tool]
            # Just uncheck - QSS will handle the visual transition
            prev_btn.setChecked(False)

        # Uncheck all other buttons and check the selected one
        for tid, btn in self._tool_buttons.items():
            btn.setChecked(tid == tool_id)

        # Pulse animation disabled - causes opacity conflicts

        self._current_tool = tool_id
        self.tool_selected.emit(tool_id)

    def current_tool(self) -> str:
        """Get the currently selected tool ID."""
        return self._current_tool

    def current_color(self) -> QColor:
        """Get the current color."""
        return self._color_button.color()

    def current_thickness(self) -> int:
        """Get the current line thickness."""
        return self._thickness_slider.value()

    def current_font_size(self) -> int:
        """Get the current font size."""
        return self._font_spin.value()

    def set_color(self, color: QColor):
        """Set the current color."""
        self._color_button.set_color(color)

    def set_thickness(self, thickness: int):
        """Set the current thickness."""
        self._thickness_slider.setValue(thickness)

    def set_font_size(self, size: int):
        """Set the current font size."""
        self._font_spin.setValue(size)

    def select_tool(self, tool_id: str):
        """Programmatically select a tool."""
        if tool_id in self._tool_buttons:
            self._on_tool_clicked(tool_id)

    def _setup_quick_styles(self):
        """Set up Quick Styles panel and button."""
        self.addSeparator()

        # Quick Styles toggle button - professional design
        self._quick_styles_btn = QToolButton()
        styles_icon = IconLoader.get_icon("stamp", size=18, color=QColor(0, 122, 255))
        self._quick_styles_btn.setIcon(styles_icon)
        self._quick_styles_btn.setIconSize(QSize(18, 18))
        self._quick_styles_btn.setText(" Quick Styles")
        self._quick_styles_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._quick_styles_btn.setCheckable(True)
        self._quick_styles_btn.setToolTip("Show/hide quick style presets (one-click color & thickness)")
        self._quick_styles_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._quick_styles_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 1px solid {MACOS_COLORS['border_light']};
                border-radius: {MACOS_RADIUS['medium']};
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
                color: {MACOS_COLORS['text_primary']};
            }}
            QToolButton:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
                border-color: {MACOS_COLORS['primary']};
            }}
            QToolButton:checked {{
                background-color: {MACOS_COLORS['primary_ultra_light']};
                border-color: {MACOS_COLORS['primary']};
                color: {MACOS_COLORS['primary']};
            }}
        """)
        self._quick_styles_btn.clicked.connect(self._toggle_quick_styles)
        self.addWidget(self._quick_styles_btn)

    def _toggle_quick_styles(self, checked: bool):
        """Toggle Quick Styles panel visibility."""
        if not self._quick_styles_panel:
            # Create panel on first use
            self._quick_styles_panel = QuickStylesPanel(self.parent())
            self._quick_styles_panel.style_applied.connect(self._apply_quick_style)
            self._quick_styles_panel.setVisible(False)

            # Position panel to the right of the editor window
            if self.parent():
                parent_geo = self.parent().geometry()
                panel_x = parent_geo.width() - self._quick_styles_panel.width() - 20
                panel_y = 80  # Below toolbar
                self._quick_styles_panel.move(panel_x, panel_y)

        if checked:
            self._quick_styles_panel.show_panel()
        else:
            self._quick_styles_panel.hide_panel()

    def _apply_quick_style(self, style):
        """Apply a quick style to current tool."""
        # Update color and thickness
        self.set_color(style.color)
        self.set_thickness(style.thickness)

        # Emit signals
        self.color_changed.emit(style.color)
        self.thickness_changed.emit(style.thickness)

        # Pulse feedback disabled - causes opacity conflicts
