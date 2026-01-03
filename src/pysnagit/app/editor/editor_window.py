"""Main editor window."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QLabel, QFileDialog, QMessageBox, QToolBar, QToolButton,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QColor
from PIL import Image

from PyQt6.QtCore import QTimer

from .canvas import EditorCanvas
from .toolbar import EditorToolbar
from .layers import LayerManager
from .layer_panel import LayerPanel
from .tools.arrow import ArrowTool
from .tools.shape import RectTool, EllipseTool, LineTool
from .tools.text import TextTool
from .tools.highlight import HighlightTool
from .tools.blur import BlurTool, PixelateTool
from .tools.crop import CropTool
from .tools.stamp import StampTool
from ..utils.clipboard import copy_to_clipboard
from ..utils.file_io import save_image, get_save_path, generate_filename
from ..utils.icon_loader import IconLoader
from ..styles import DARK_THEME, COLORS, MACOS_BIGSUR_THEME, MACOS_COLORS, MACOS_RADIUS
from ..animations import AnimationManager
from ..capture.screen import capture_full_screen
from ..capture.region import RegionSelector, capture_selected_region
from ..capture.window import capture_window


class EditorWindow(QMainWindow):
    """Image editor window with annotation tools."""

    def __init__(self, image: Image.Image = None, settings=None, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._layer_manager = LayerManager(self)
        self._tools = {}
        self._current_tool = None
        self._region_selector = None
        self._has_shown_animation = False

        # Apply macOS Big Sur+ theme
        self.setStyleSheet(MACOS_BIGSUR_THEME)

        self._setup_ui()
        self._setup_tools()
        self._setup_menu()
        self._setup_connections()

        if image:
            self.set_image(image)

    def _setup_ui(self):
        """Set up the editor UI."""
        self.setWindowTitle("PySnagit Editor")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)

        # Central widget with horizontal layout for canvas + layer panel
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Capture toolbar (top) - macOS style with polish
        capture_toolbar = QToolBar("Capture")
        capture_toolbar.setMovable(False)
        capture_toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {MACOS_COLORS['bg_white']};
                border-bottom: 1px solid {MACOS_COLORS['border_light']};
                padding: 8px 16px;
                spacing: 12px;
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {MACOS_RADIUS['medium']};
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 500;
                color: {MACOS_COLORS['text_primary']};
            }}
            QToolButton:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
                border-color: {MACOS_COLORS['border_light']};
            }}
            QToolButton:pressed {{
                background-color: {MACOS_COLORS['border_light']};
            }}
        """)

        # Full Screen button
        btn_new_full = QToolButton()
        btn_new_full.setIcon(IconLoader.get_icon("fullscreen", size=18, color=QColor(60, 60, 67)))
        btn_new_full.setIconSize(QSize(18, 18))
        btn_new_full.setText(" Full Screen")
        btn_new_full.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn_new_full.setToolTip("Capture full screen (Print)")
        btn_new_full.clicked.connect(self._new_full_capture)
        btn_new_full.setCursor(Qt.CursorShape.PointingHandCursor)
        capture_toolbar.addWidget(btn_new_full)

        # Region button
        btn_new_region = QToolButton()
        btn_new_region.setIcon(IconLoader.get_icon("region", size=18, color=QColor(60, 60, 67)))
        btn_new_region.setIconSize(QSize(18, 18))
        btn_new_region.setText(" Region")
        btn_new_region.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn_new_region.setToolTip("Capture region (Ctrl+Shift+R)")
        btn_new_region.clicked.connect(self._new_region_capture)
        btn_new_region.setCursor(Qt.CursorShape.PointingHandCursor)
        capture_toolbar.addWidget(btn_new_region)

        # Window button
        btn_new_window = QToolButton()
        btn_new_window.setIcon(IconLoader.get_icon("window", size=18, color=QColor(60, 60, 67)))
        btn_new_window.setIconSize(QSize(18, 18))
        btn_new_window.setText(" Window")
        btn_new_window.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn_new_window.setToolTip("Capture window (Alt+Print)")
        btn_new_window.clicked.connect(self._new_window_capture)
        btn_new_window.setCursor(Qt.CursorShape.PointingHandCursor)
        capture_toolbar.addWidget(btn_new_window)

        capture_toolbar.addSeparator()

        # Copy button - primary style
        btn_copy = QToolButton()
        btn_copy.setIcon(IconLoader.get_icon("copy", size=18, color=QColor(0, 122, 255)))
        btn_copy.setIconSize(QSize(18, 18))
        btn_copy.setText(" Copy")
        btn_copy.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn_copy.setToolTip("Copy to clipboard (Ctrl+C)")
        btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.setStyleSheet(f"""
            QToolButton {{
                background-color: {MACOS_COLORS['primary_ultra_light']};
                border: 1px solid {MACOS_COLORS['primary']};
                border-radius: {MACOS_RADIUS['medium']};
                padding: 6px 14px;
                font-weight: 600;
                color: {MACOS_COLORS['primary']};
            }}
            QToolButton:hover {{
                background-color: {MACOS_COLORS['primary_light']};
            }}
            QToolButton:pressed {{
                background-color: {MACOS_COLORS['primary']};
                color: white;
            }}
        """)
        capture_toolbar.addWidget(btn_copy)

        # Save button - primary style
        btn_save = QToolButton()
        btn_save.setIcon(IconLoader.get_icon("save", size=18, color=QColor(255, 255, 255)))
        btn_save.setIconSize(QSize(18, 18))
        btn_save.setText(" Save")
        btn_save.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn_save.setToolTip("Save image (Ctrl+S)")
        btn_save.clicked.connect(self._save_as)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QToolButton {{
                background-color: {MACOS_COLORS['primary']};
                border: none;
                border-radius: {MACOS_RADIUS['medium']};
                padding: 6px 14px;
                font-weight: 600;
                color: white;
            }}
            QToolButton:hover {{
                background-color: {MACOS_COLORS['primary_hover']};
            }}
            QToolButton:pressed {{
                background-color: {MACOS_COLORS['primary_dark']};
            }}
        """)
        capture_toolbar.addWidget(btn_save)

        self.addToolBar(capture_toolbar)

        # Editor toolbar
        self._toolbar = EditorToolbar(self)
        self.addToolBar(self._toolbar)

        # Content area: Canvas + Layer Panel
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Canvas
        self._canvas = EditorCanvas(self)
        content_layout.addWidget(self._canvas, stretch=1)

        # Layer Panel (right side)
        self._layer_panel = LayerPanel(self)
        self._layer_panel.undo_requested.connect(self._undo)
        self._layer_panel.redo_requested.connect(self._redo)
        content_layout.addWidget(self._layer_panel)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._zoom_label = QLabel("100%")
        self._status_bar.addPermanentWidget(self._zoom_label)

        self._size_label = QLabel("")
        self._status_bar.addPermanentWidget(self._size_label)

    def _setup_tools(self):
        """Initialize annotation tools."""
        self._tools = {
            "select": None,  # Selection tool (no drawing)
            "arrow": ArrowTool(),
            "line": LineTool(),
            "rect": RectTool(),
            "ellipse": EllipseTool(),
            "text": TextTool(),
            "highlight": HighlightTool(),
            "blur": BlurTool(),
            "crop": CropTool(),
            "stamp": StampTool(),
        }

    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New capture options
        new_full_action = QAction("New &Full Screen Capture", self)
        new_full_action.setShortcut("Print")
        new_full_action.triggered.connect(self._new_full_capture)
        file_menu.addAction(new_full_action)

        new_region_action = QAction("New &Region Capture", self)
        new_region_action.setShortcut("Ctrl+Shift+R")
        new_region_action.triggered.connect(self._new_region_capture)
        file_menu.addAction(new_region_action)

        new_window_action = QAction("New &Window Capture", self)
        new_window_action.setShortcut("Alt+Print")
        new_window_action.triggered.connect(self._new_window_capture)
        file_menu.addAction(new_window_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        copy_action = QAction("&Copy to Clipboard", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy_to_clipboard)
        file_menu.addAction(copy_action)

        file_menu.addSeparator()

        close_action = QAction("&Close", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        self._undo_action = undo_action

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        self._redo_action = redo_action

        edit_menu.addSeparator()

        clear_action = QAction("&Clear All Annotations", self)
        clear_action.triggered.connect(self._clear_annotations)
        edit_menu.addAction(clear_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._canvas.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._canvas.zoom_out)
        view_menu.addAction(zoom_out_action)

        fit_action = QAction("&Fit in View", self)
        fit_action.setShortcut("Ctrl+0")
        fit_action.triggered.connect(self._canvas.fit_in_view)
        view_menu.addAction(fit_action)

        actual_action = QAction("&Actual Size", self)
        actual_action.setShortcut("Ctrl+1")
        actual_action.triggered.connect(lambda: self._canvas.set_zoom(1.0))
        view_menu.addAction(actual_action)

    def _setup_connections(self):
        """Set up signal connections."""
        # Toolbar signals
        self._toolbar.tool_selected.connect(self._on_tool_selected)
        self._toolbar.color_changed.connect(self._on_color_changed)
        self._toolbar.thickness_changed.connect(self._on_thickness_changed)
        self._toolbar.font_size_changed.connect(self._on_font_size_changed)

        # Canvas signals
        self._canvas.zoom_changed.connect(self._on_zoom_changed)

        # Layer manager signals
        self._layer_manager.can_undo_changed.connect(
            lambda can: self._undo_action.setEnabled(can)
        )
        self._layer_manager.can_redo_changed.connect(
            lambda can: self._redo_action.setEnabled(can)
        )

        # Update layer panel when undo/redo state changes
        self._layer_manager.can_undo_changed.connect(self._layer_panel.set_undo_enabled)
        self._layer_manager.can_redo_changed.connect(self._layer_panel.set_redo_enabled)

    def showEvent(self, event):
        """Show window (animations disabled due to opacity conflicts)."""
        super().showEvent(event)
        self._has_shown_animation = True

    def set_image(self, image: Image.Image):
        """Set the image to edit."""
        self._canvas.set_image(image)
        self._size_label.setText(f"{image.width} x {image.height}")

    def _on_tool_selected(self, tool_id: str):
        """Handle tool selection."""
        tool = self._tools.get(tool_id)
        self._current_tool = tool

        if tool:
            # Apply current settings to tool
            tool.set_color(self._toolbar.current_color())
            tool.set_thickness(self._toolbar.current_thickness())
            tool.set_font_size(self._toolbar.current_font_size())

        self._canvas.set_tool(tool)
        self._status_bar.showMessage(f"Tool: {tool_id.title()}")

    def _on_color_changed(self, color: QColor):
        """Handle color change."""
        if self._current_tool:
            self._current_tool.set_color(color)

    def _on_thickness_changed(self, thickness: int):
        """Handle thickness change."""
        if self._current_tool:
            self._current_tool.set_thickness(thickness)

    def _on_font_size_changed(self, size: int):
        """Handle font size change."""
        if self._current_tool:
            self._current_tool.set_font_size(size)

    def _on_zoom_changed(self, factor: float):
        """Handle zoom level change."""
        self._zoom_label.setText(f"{int(factor * 100)}%")

    def _save(self):
        """Save the image."""
        self._save_as()

    def _save_as(self):
        """Save the image with a file dialog."""
        image = self._canvas.get_image()
        if not image:
            return

        default_name = generate_filename("capture", "png")
        path = get_save_path(
            self,
            default_name,
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*.*)"
        )

        if path:
            # Determine format from extension
            ext = path.suffix.lower()
            if ext in ('.jpg', '.jpeg'):
                fmt = 'JPEG'
            else:
                fmt = 'PNG'

            result = save_image(image, path, fmt)
            if result:
                self._status_bar.showMessage(f"Saved to {path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to save image")

    def _copy_to_clipboard(self):
        """Copy the image to clipboard."""
        image = self._canvas.get_image()
        if image and copy_to_clipboard(image):
            self._status_bar.showMessage("Copied to clipboard")
        else:
            self._status_bar.showMessage("Failed to copy to clipboard")

    def _undo(self):
        """Undo last action."""
        if self._layer_manager.undo(self._canvas):
            self._status_bar.showMessage("Undo")

    def _redo(self):
        """Redo last undone action."""
        if self._layer_manager.redo(self._canvas):
            self._status_bar.showMessage("Redo")

    def _clear_annotations(self):
        """Clear all annotations."""
        self._canvas.clear_annotations()
        self._layer_manager.clear_layers()
        self._status_bar.showMessage("Cleared all annotations")

    def _new_full_capture(self):
        """Capture full screen and load into editor."""
        self.hide()
        QTimer.singleShot(200, self._do_full_capture)

    def _do_full_capture(self):
        """Perform full screen capture."""
        image = capture_full_screen()
        self._load_new_capture(image)

    def _new_region_capture(self):
        """Capture region and load into editor."""
        self.hide()
        QTimer.singleShot(100, self._show_region_selector)

    def _show_region_selector(self):
        """Show region selection overlay."""
        self._region_selector = RegionSelector()
        self._region_selector.region_selected.connect(self._on_region_selected)
        self._region_selector.selection_cancelled.connect(self._on_capture_cancelled)
        self._region_selector.show()

    def _on_region_selected(self, rect):
        """Handle region selection."""
        image = capture_selected_region(rect)
        self._load_new_capture(image)

    def _on_capture_cancelled(self):
        """Handle capture cancellation."""
        self.show()
        self._status_bar.showMessage("Capture cancelled")

    def _new_window_capture(self):
        """Capture window and load into editor."""
        self.hide()
        QTimer.singleShot(500, self._do_window_capture)

    def _do_window_capture(self):
        """Perform window capture."""
        image = capture_window()
        if image:
            self._load_new_capture(image)
        else:
            self.show()
            self._status_bar.showMessage("Failed to capture window")

    def _load_new_capture(self, image: Image.Image):
        """Load a new capture into the editor."""
        # Clear existing annotations
        self._canvas.clear_annotations()
        self._layer_manager.clear_layers()

        # Set new image
        self.set_image(image)

        # Copy to clipboard
        copy_to_clipboard(image)

        # Show window
        self.show()
        self._status_bar.showMessage(f"Captured {image.width}x{image.height} - Copied to clipboard")
