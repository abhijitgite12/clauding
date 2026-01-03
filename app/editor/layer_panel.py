"""Visual layer panel for the editor - shows annotation layers with thumbnails."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor
from ..styles import MACOS_COLORS, MACOS_RADIUS
from ..utils.icon_loader import IconLoader


class LayerItem(QWidget):
    """Individual layer item widget with thumbnail and controls."""

    delete_clicked = pyqtSignal(int)  # layer index
    visibility_toggled = pyqtSignal(int, bool)  # layer index, visible

    def __init__(self, layer_index: int, layer_name: str, visible: bool = True, parent=None):
        super().__init__(parent)
        self.layer_index = layer_index
        self._visible = visible
        self._setup_ui(layer_name)

    def _setup_ui(self, layer_name: str):
        """Set up the layer item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Visibility toggle button
        self._visibility_btn = QToolButton()
        eye_icon = IconLoader.get_icon("text", size=16, color=QColor(142, 142, 147))
        self._visibility_btn.setIcon(eye_icon)
        self._visibility_btn.setIconSize(QSize(16, 16))
        self._visibility_btn.setFixedSize(24, 24)
        self._visibility_btn.setCheckable(True)
        self._visibility_btn.setChecked(self._visible)
        self._visibility_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
            }}
            QToolButton:checked {{
                background-color: {MACOS_COLORS['primary_ultra_light']};
            }}
        """)
        self._visibility_btn.clicked.connect(
            lambda checked: self.visibility_toggled.emit(self.layer_index, checked)
        )
        layout.addWidget(self._visibility_btn)

        # Layer name
        name_label = QLabel(layer_name)
        name_label.setStyleSheet(f"""
            color: {MACOS_COLORS['text_primary']};
            font-size: 12px;
            background: transparent;
        """)
        layout.addWidget(name_label)

        layout.addStretch()

        # Delete button
        delete_btn = QToolButton()
        delete_icon = IconLoader.get_icon("close", size=14, color=QColor(255, 59, 48))
        delete_btn.setIcon(delete_icon)
        delete_btn.setIconSize(QSize(14, 14))
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background-color: rgba(255, 59, 48, 0.1);
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.layer_index))
        layout.addWidget(delete_btn)

        # Item styling
        self.setStyleSheet(f"""
            LayerItem {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 1px solid {MACOS_COLORS['border_light']};
                border-radius: {MACOS_RADIUS['small']};
            }}
            LayerItem:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
                border-color: {MACOS_COLORS['primary']};
            }}
        """)


class LayerPanel(QWidget):
    """Panel showing all annotation layers with undo/redo controls."""

    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    layer_deleted = pyqtSignal(int)
    layer_visibility_changed = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layers = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the layer panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title = QLabel("Layers")
        title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {MACOS_COLORS['text_primary']};
            background: transparent;
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Undo button
        self._undo_btn = QToolButton()
        undo_icon = IconLoader.get_icon("arrow", size=16, color=QColor(0, 122, 255))
        self._undo_btn.setIcon(undo_icon)
        self._undo_btn.setIconSize(QSize(16, 16))
        self._undo_btn.setFixedSize(32, 32)
        self._undo_btn.setToolTip("Undo (Ctrl+Z)")
        self._undo_btn.setEnabled(False)
        self._undo_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 1px solid {MACOS_COLORS['border_light']};
                border-radius: {MACOS_RADIUS['small']};
            }}
            QToolButton:hover:enabled {{
                background-color: {MACOS_COLORS['bg_hover']};
                border-color: {MACOS_COLORS['primary']};
            }}
            QToolButton:disabled {{
                opacity: 0.4;
            }}
        """)
        self._undo_btn.clicked.connect(self.undo_requested.emit)
        header_layout.addWidget(self._undo_btn)

        # Redo button
        self._redo_btn = QToolButton()
        redo_icon = IconLoader.get_icon("arrow", size=16, color=QColor(0, 122, 255))
        self._redo_btn.setIcon(redo_icon)
        self._redo_btn.setIconSize(QSize(16, 16))
        self._redo_btn.setFixedSize(32, 32)
        self._redo_btn.setToolTip("Redo (Ctrl+Y)")
        self._redo_btn.setEnabled(False)
        self._redo_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 1px solid {MACOS_COLORS['border_light']};
                border-radius: {MACOS_RADIUS['small']};
            }}
            QToolButton:hover:enabled {{
                background-color: {MACOS_COLORS['bg_hover']};
                border-color: {MACOS_COLORS['primary']};
            }}
            QToolButton:disabled {{
                opacity: 0.4;
            }}
        """)
        self._redo_btn.clicked.connect(self.redo_requested.emit)
        header_layout.addWidget(self._redo_btn)

        layout.addLayout(header_layout)

        # Layer list
        self._layer_list = QWidget()
        self._layer_list_layout = QVBoxLayout(self._layer_list)
        self._layer_list_layout.setSpacing(6)
        self._layer_list_layout.setContentsMargins(0, 0, 0, 0)
        self._layer_list_layout.addStretch()

        layout.addWidget(self._layer_list)
        layout.addStretch()

        # Panel styling
        self.setStyleSheet(f"""
            LayerPanel {{
                background-color: {MACOS_COLORS['bg_main']};
                border-left: 1px solid {MACOS_COLORS['border_light']};
            }}
        """)

        self.setFixedWidth(250)

    def add_layer(self, layer_name: str, visible: bool = True):
        """Add a new layer to the panel."""
        layer_index = len(self._layers)
        layer_item = LayerItem(layer_index, layer_name, visible)
        layer_item.delete_clicked.connect(self.layer_deleted.emit)
        layer_item.visibility_toggled.connect(self.layer_visibility_changed.emit)

        self._layers.append(layer_item)

        # Insert at the top (most recent first)
        self._layer_list_layout.insertWidget(0, layer_item)

    def remove_layer(self, layer_index: int):
        """Remove a layer from the panel."""
        if 0 <= layer_index < len(self._layers):
            layer_item = self._layers[layer_index]
            self._layer_list_layout.removeWidget(layer_item)
            layer_item.deleteLater()
            self._layers.pop(layer_index)

            # Re-index remaining layers
            for i, item in enumerate(self._layers):
                item.layer_index = i

    def clear_layers(self):
        """Clear all layers."""
        for layer_item in self._layers:
            self._layer_list_layout.removeWidget(layer_item)
            layer_item.deleteLater()
        self._layers.clear()

    def set_undo_enabled(self, enabled: bool):
        """Enable/disable undo button."""
        self._undo_btn.setEnabled(enabled)

    def set_redo_enabled(self, enabled: bool):
        """Enable/disable redo button."""
        self._redo_btn.setEnabled(enabled)

    def get_layer_count(self) -> int:
        """Get the number of layers."""
        return len(self._layers)
