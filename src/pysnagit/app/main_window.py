"""Main application window - Snagit-inspired design."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QApplication, QMessageBox, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QAction, QKeySequence, QFont, QIcon, QPixmap, QPainter, QColor
from PIL import Image

from .system_tray import SystemTray
from .hotkeys import HotkeyManager
from .capture.screen import capture_full_screen
from .capture.region import RegionSelector, capture_selected_region
from .capture.window import capture_window, get_window_at_cursor
from .capture.scrolling import ScrollingCapture
from .utils.clipboard import copy_to_clipboard
from .utils.file_io import save_image, get_save_path, generate_filename
from .utils.settings import Settings
from .utils.logger import get_logger
from .utils.icon_loader import IconLoader
from .styles import DARK_THEME, COLORS, MACOS_BIGSUR_THEME, MACOS_COLORS, MACOS_RADIUS
from .animations import AnimationManager

log = get_logger("main_window")


class CaptureButton(QPushButton):
    """Large capture button with icon - macOS Big Sur+ style with shadow effects."""

    def __init__(self, icon_name: str, title: str, shortcut: str = "", primary: bool = False, parent=None):
        super().__init__(parent)
        self._primary = primary
        self._icon_name = icon_name
        self._shadow = None
        self._shadow_animation = None
        self._setup_ui(icon_name, title, shortcut, primary)
        self._setup_shadow()

    def _setup_shadow(self):
        """Add professional drop shadow effect."""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(20)
        self._shadow.setOffset(0, 4)
        if self._primary:
            self._shadow.setColor(QColor(0, 122, 255, 80))  # Blue tint shadow
        else:
            self._shadow.setColor(QColor(0, 0, 0, 30))  # Soft shadow
        self.setGraphicsEffect(self._shadow)

    def _setup_ui(self, icon_name: str, title: str, shortcut: str, primary: bool):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 28, 20, 28)

        # Icon - Professional sized icon with proper rendering
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Get icon with appropriate color
        if primary:
            icon_color = QColor(255, 255, 255)  # White for primary button
        else:
            icon_color = QColor(0, 122, 255)  # iOS blue for secondary buttons

        icon = IconLoader.get_icon(icon_name, size=48, color=icon_color)
        pixmap = icon.pixmap(QSize(48, 48))
        icon_label.setPixmap(pixmap)
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if primary:
            title_label.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 600;
                color: {MACOS_COLORS['text_light']};
                background: transparent;
            """)
        else:
            title_label.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 600;
                color: {MACOS_COLORS['text_primary']};
                background: transparent;
            """)
        layout.addWidget(title_label)

        # Shortcut
        if shortcut:
            short_label = QLabel(shortcut)
            short_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if primary:
                short_label.setStyleSheet(f"""
                    font-size: 11px;
                    color: rgba(255,255,255,0.7);
                    background: transparent;
                """)
            else:
                short_label.setStyleSheet(f"""
                    font-size: 11px;
                    color: {MACOS_COLORS['text_secondary']};
                    background: transparent;
                """)
            layout.addWidget(short_label)

        self.setMinimumSize(140, 130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # macOS Big Sur+ styling
        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MACOS_COLORS['primary']};
                    border: none;
                    border-radius: {MACOS_RADIUS['xlarge']};
                }}
                QPushButton:hover {{
                    background-color: {MACOS_COLORS['primary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {MACOS_COLORS['primary_dark']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MACOS_COLORS['bg_white']};
                    border: 1px solid {MACOS_COLORS['border_light']};
                    border-radius: {MACOS_RADIUS['xlarge']};
                }}
                QPushButton:hover {{
                    background-color: {MACOS_COLORS['bg_hover']};
                    border-color: {MACOS_COLORS['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {MACOS_COLORS['border_light']};
                }}
            """)

    def enterEvent(self, event):
        """Handle hover - animate shadow to lift effect."""
        super().enterEvent(event)
        if self._shadow:
            # Create animation for shadow blur radius
            self._shadow_animation = QPropertyAnimation(self._shadow, b"blurRadius")
            self._shadow_animation.setDuration(150)
            self._shadow_animation.setStartValue(self._shadow.blurRadius())
            self._shadow_animation.setEndValue(30)
            self._shadow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._shadow_animation.start()
            # Also increase shadow opacity
            if self._primary:
                self._shadow.setColor(QColor(0, 122, 255, 120))
            else:
                self._shadow.setColor(QColor(0, 0, 0, 50))

    def leaveEvent(self, event):
        """Handle hover end - return shadow to normal."""
        super().leaveEvent(event)
        if self._shadow:
            self._shadow_animation = QPropertyAnimation(self._shadow, b"blurRadius")
            self._shadow_animation.setDuration(150)
            self._shadow_animation.setStartValue(self._shadow.blurRadius())
            self._shadow_animation.setEndValue(20)
            self._shadow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._shadow_animation.start()
            # Return shadow opacity
            if self._primary:
                self._shadow.setColor(QColor(0, 122, 255, 80))
            else:
                self._shadow.setColor(QColor(0, 0, 0, 30))

    def mousePressEvent(self, event):
        """Handle press - quick shadow reduction for tactile feel."""
        if self._shadow:
            self._shadow.setBlurRadius(12)
            self._shadow.setOffset(0, 2)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle release - restore shadow."""
        if self._shadow:
            self._shadow.setBlurRadius(30 if self.underMouse() else 20)
            self._shadow.setOffset(0, 4)
        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    """Main application window with capture controls."""

    def __init__(self):
        super().__init__()
        log.info("Initializing MainWindow...")

        try:
            self._settings = Settings()
            log.debug("Settings loaded")

            self._region_selector = None
            self._current_image = None
            self._recording_mode = "video"
            self._has_shown_animation = False

            # Apply macOS Big Sur+ theme
            log.debug("Applying macOS Big Sur+ theme...")
            self.setStyleSheet(MACOS_BIGSUR_THEME)

            log.debug("Setting up UI...")
            self._setup_ui()

            log.debug("Setting up system tray...")
            self._setup_tray()

            log.debug("Setting up hotkeys...")
            self._setup_hotkeys()

            log.info("MainWindow initialized successfully")

        except Exception as e:
            log.error(f"Error initializing MainWindow: {e}", exc_info=True)
            raise

    def _setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle("PySnagit")
        self.setMinimumSize(640, 520)
        self.resize(640, 520)

        # Central widget
        central = QWidget()
        central.setStyleSheet(f"background-color: {MACOS_COLORS['bg_main']};")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header bar - translucent for macOS style
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {MACOS_COLORS['bg_white']};
                border-bottom: 1px solid {MACOS_COLORS['border_light']};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)

        # Logo/Title
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(2)

        title = QLabel("PySnagit")
        title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {MACOS_COLORS['primary']};
            background: transparent;
        """)
        logo_layout.addWidget(title)

        subtitle = QLabel("Screen Capture & Recording")
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {MACOS_COLORS['text_secondary']};
            background: transparent;
        """)
        logo_layout.addWidget(subtitle)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()

        # Settings button
        settings_btn = QPushButton()
        settings_btn.setFixedSize(40, 40)
        settings_icon = IconLoader.get_icon("settings", size=20, color=QColor(142, 142, 147))
        settings_btn.setIcon(settings_icon)
        settings_btn.setIconSize(QSize(20, 20))
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
            }}
        """)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self._show_settings)
        header_layout.addWidget(settings_btn)

        layout.addWidget(header)

        # Content area
        content = QWidget()
        content.setStyleSheet(f"background-color: {MACOS_COLORS['bg_main']};")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(24)
        content_layout.setContentsMargins(32, 32, 32, 24)

        # Section: Image Capture
        section1_label = QLabel("IMAGE CAPTURE")
        section1_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {MACOS_COLORS['text_secondary']};
            letter-spacing: 2px;
            background: transparent;
            padding-bottom: 8px;
        """)
        content_layout.addWidget(section1_label)

        # Capture buttons grid - increased spacing for macOS style
        capture_grid = QGridLayout()
        capture_grid.setSpacing(24)

        btn_region = CaptureButton("region", "Region", "Ctrl+Shift+R", primary=True)
        btn_region.clicked.connect(self._capture_region)
        capture_grid.addWidget(btn_region, 0, 0)

        btn_full = CaptureButton("fullscreen", "Full Screen", "Print")
        btn_full.clicked.connect(self._capture_full_screen)
        capture_grid.addWidget(btn_full, 0, 1)

        btn_window = CaptureButton("window", "Window", "Alt+Print")
        btn_window.clicked.connect(self._capture_window)
        capture_grid.addWidget(btn_window, 0, 2)

        btn_scrolling = CaptureButton("scrolling", "Scrolling", "Full page")
        btn_scrolling.clicked.connect(self._capture_scrolling)
        capture_grid.addWidget(btn_scrolling, 0, 3)

        content_layout.addLayout(capture_grid)

        # Section: Video
        section2_label = QLabel("VIDEO & GIF")
        section2_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {MACOS_COLORS['text_secondary']};
            letter-spacing: 2px;
            background: transparent;
            padding-top: 16px;
            padding-bottom: 8px;
        """)
        content_layout.addWidget(section2_label)

        # Recording buttons - increased spacing
        record_layout = QHBoxLayout()
        record_layout.setSpacing(24)

        btn_video = CaptureButton("video", "Video", "Ctrl+Shift+V")
        btn_video.clicked.connect(self._start_recording)
        record_layout.addWidget(btn_video)

        btn_gif = CaptureButton("gif", "GIF", "Ctrl+Shift+G")
        btn_gif.clicked.connect(self._start_gif)
        record_layout.addWidget(btn_gif)

        record_layout.addStretch(2)

        content_layout.addLayout(record_layout)
        content_layout.addStretch()

        layout.addWidget(content)

        # Status bar - macOS style
        status_bar = QFrame()
        status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {MACOS_COLORS['bg_white']};
                border-top: 1px solid {MACOS_COLORS['border_light']};
            }}
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(24, 14, 24, 14)

        self._status_icon = QLabel("")
        self._status_icon.setStyleSheet(f"color: {MACOS_COLORS['success']}; font-size: 14px; background: transparent;")
        status_layout.addWidget(self._status_icon)

        self._status_label = QLabel("Ready to capture")
        self._status_label.setStyleSheet(f"""
            color: {MACOS_COLORS['text_secondary']};
            font-size: 13px;
            background: transparent;
        """)
        status_layout.addWidget(self._status_label)
        status_layout.addStretch()

        # Version
        version_label = QLabel("v1.0")
        version_label.setStyleSheet(f"""
            color: {MACOS_COLORS['text_tertiary']};
            font-size: 11px;
            background: transparent;
        """)
        status_layout.addWidget(version_label)

        layout.addWidget(status_bar)

        # Menu bar
        self._setup_menu()

    def showEvent(self, event):
        """Show window (animations disabled due to opacity conflicts)."""
        super().showEvent(event)
        self._has_shown_animation = True

    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Image...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_image)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self._quit)
        file_menu.addAction(quit_action)

        # Capture menu
        capture_menu = menubar.addMenu("&Capture")

        full_action = QAction("&Full Screen", self)
        full_action.setShortcut("Print")
        full_action.triggered.connect(self._capture_full_screen)
        capture_menu.addAction(full_action)

        region_action = QAction("&Region", self)
        region_action.setShortcut("Ctrl+Shift+R")
        region_action.triggered.connect(self._capture_region)
        capture_menu.addAction(region_action)

        window_action = QAction("&Window", self)
        window_action.setShortcut("Alt+Print")
        window_action.triggered.connect(self._capture_window)
        capture_menu.addAction(window_action)

        scrolling_action = QAction("&Scrolling Capture", self)
        scrolling_action.triggered.connect(self._capture_scrolling)
        capture_menu.addAction(scrolling_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_tray(self):
        """Set up system tray icon."""
        self._tray = SystemTray(self)
        self._tray.capture_full_screen.connect(self._capture_full_screen)
        self._tray.capture_region.connect(self._capture_region)
        self._tray.capture_window.connect(self._capture_window)
        self._tray.capture_scrolling.connect(self._capture_scrolling)
        self._tray.start_recording.connect(self._start_recording)
        self._tray.start_gif.connect(self._start_gif)
        self._tray.open_editor.connect(self.show)
        self._tray.show_settings.connect(self._show_settings)
        self._tray.quit_app.connect(self._quit)
        self._tray.show()

    def _setup_hotkeys(self):
        """Set up global hotkeys."""
        self._hotkey_manager = HotkeyManager(self._settings, self)
        self._hotkey_manager.capture_full_screen.connect(self._capture_full_screen)
        self._hotkey_manager.capture_region.connect(self._capture_region)
        self._hotkey_manager.capture_window.connect(self._capture_window)
        self._hotkey_manager.start_recording.connect(self._start_recording)
        self._hotkey_manager.start_gif.connect(self._start_gif)
        self._hotkey_manager.start()

    def _capture_full_screen(self):
        log.info("Starting full screen capture...")
        self.hide()
        QTimer.singleShot(50, self._do_full_capture)  # Reduced from 200ms to 50ms

    def _do_full_capture(self):
        try:
            log.debug("Executing full screen capture")
            image = capture_full_screen()
            log.info(f"Full screen captured: {image.width}x{image.height}")
            self._handle_capture(image)
        except Exception as e:
            log.error(f"Full screen capture failed: {e}", exc_info=True)
            self._set_status(f"Capture failed: {e}", "error")

    def _capture_region(self):
        log.info("Starting region capture...")
        self.hide()
        QTimer.singleShot(50, self._show_region_selector)  # Reduced from 100ms to 50ms

    def _show_region_selector(self):
        try:
            log.debug("Showing region selector")
            self._region_selector = RegionSelector()
            self._region_selector.region_selected.connect(self._on_region_selected)
            self._region_selector.selection_cancelled.connect(self._on_selection_cancelled)
            self._region_selector.show()
        except Exception as e:
            log.error(f"Failed to show region selector: {e}", exc_info=True)

    def _on_region_selected(self, rect):
        try:
            log.info(f"Region selected: {rect.x()},{rect.y()} {rect.width()}x{rect.height()}")
            image = capture_selected_region(rect)
            log.info(f"Region captured: {image.width}x{image.height}")
            self._handle_capture(image)
        except Exception as e:
            log.error(f"Region capture failed: {e}", exc_info=True)
            self._set_status(f"Capture failed: {e}", "error")

    def _on_selection_cancelled(self):
        log.info("Capture cancelled by user")
        self._set_status("Capture cancelled", "warning")

    def _capture_window(self):
        log.info("Starting window capture...")
        self.hide()
        QTimer.singleShot(50, self._do_window_capture)  # Reduced from 200ms to 50ms

    def _do_window_capture(self):
        log.debug("Waiting for window selection...")
        self._tray.show_message("Window Capture", "Click on the window you want to capture")
        QTimer.singleShot(100, self._capture_window_at_cursor)  # Reduced from 500ms to 100ms

    def _capture_window_at_cursor(self):
        try:
            log.debug("Capturing window at cursor")
            image = capture_window()
            if image:
                log.info(f"Window captured: {image.width}x{image.height}")
                self._handle_capture(image)
            else:
                log.warning("No window captured")
                self._set_status("Failed to capture window", "error")
        except Exception as e:
            log.error(f"Window capture failed: {e}", exc_info=True)
            self._set_status(f"Capture failed: {e}", "error")

    def _capture_scrolling(self):
        log.info("Starting scrolling capture...")
        self.hide()
        try:
            hwnd = get_window_at_cursor()
            log.debug(f"Window handle: {hwnd}")
            if hwnd:
                self._tray.show_message("Scrolling Capture", "Capturing scrolling content...")
                capture = ScrollingCapture(hwnd)
                image = capture.capture()
                if image:
                    log.info(f"Scrolling capture complete: {image.width}x{image.height}")
                    self._handle_capture(image)
                else:
                    log.warning("Scrolling capture returned no image")
                    self._set_status("Failed to capture scrolling content", "error")
                    self.show()
            else:
                log.warning("No window found at cursor")
                self._set_status("No window found at cursor", "error")
                self.show()
        except Exception as e:
            log.error(f"Scrolling capture failed: {e}", exc_info=True)
            self._set_status(f"Capture failed: {e}", "error")
            self.show()

    def _start_recording(self):
        self.hide()
        self._recording_mode = "video"
        QTimer.singleShot(50, self._show_recording_region_selector)  # Reduced from 100ms to 50ms

    def _start_gif(self):
        self.hide()
        self._recording_mode = "gif"
        QTimer.singleShot(50, self._show_recording_region_selector)  # Reduced from 100ms to 50ms

    def _show_recording_region_selector(self):
        self._region_selector = RegionSelector()
        self._region_selector.region_selected.connect(self._on_recording_region_selected)
        self._region_selector.selection_cancelled.connect(self._on_selection_cancelled)
        self._region_selector.show()

    def _on_recording_region_selected(self, rect):
        from .recording_window import RecordingControlWindow
        self._recording_window = RecordingControlWindow(
            mode=self._recording_mode,
            region=rect,
            settings=self._settings
        )
        self._recording_window.recording_finished.connect(self._on_recording_finished)
        self._recording_window.show()

    def _on_recording_finished(self, output_path: str):
        self._set_status("Recording saved", "success")

    def _handle_capture(self, image: Image.Image):
        log.info(f"_handle_capture called with {image.width}x{image.height} image")
        try:
            self._current_image = image

            # Copy to clipboard
            log.info("Copying to clipboard...")
            if self._settings.get("capture", "auto_copy_clipboard", True):
                copy_to_clipboard(image)
                log.info("Clipboard copy completed")
                self._set_status(f"Captured {image.width}x{image.height} - Copied to clipboard", "success")
            else:
                self._set_status(f"Captured {image.width}x{image.height}", "success")

            # Open editor
            log.info("Opening editor...")
            self._open_editor(self._current_image)
        except Exception as e:
            log.error(f"Failed to handle capture: {e}", exc_info=True)
            self._set_status(f"Error handling capture: {e}", "error")
            self.show()

    def _open_editor(self, image: Image.Image):
        try:
            from .editor.editor_window import EditorWindow
            log.info(f"Opening editor with {image.width}x{image.height} image...")
            self._editor = EditorWindow(image, self._settings)
            self._editor.show()
            log.info("Editor opened successfully")
        except Exception as e:
            log.error(f"Failed to open editor: {e}", exc_info=True)
            self._set_status(f"Error opening editor: {e}", "error")
            self.show()

    def _open_image(self):
        from .utils.file_io import get_open_path, load_image
        path = get_open_path(self)
        if path:
            image = load_image(path)
            if image:
                self._open_editor(image)
            else:
                QMessageBox.warning(self, "Error", "Failed to load image")

    def _show_settings(self):
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self._settings, self)
        dialog.setStyleSheet(DARK_THEME)
        if dialog.exec():
            self._hotkey_manager.update_hotkeys()

    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About PySnagit")
        msg.setText(
            "<h2 style='color: #0066CC;'>PySnagit</h2>"
            "<p>Professional screen capture and annotation tool.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Region, full screen, and window capture</li>"
            "<li>Scrolling capture for long pages</li>"
            "<li>Image editor with annotations</li>"
            "<li>Video and GIF recording</li>"
            "</ul>"
            "<p style='color: #666;'>Version 1.0</p>"
        )
        msg.setStyleSheet(DARK_THEME)
        msg.exec()

    def _set_status(self, message: str, status_type: str = "info"):
        """Set status message with proper icons."""
        icons = {"success": "✓", "error": "✕", "warning": "⚠", "info": "ⓘ"}
        colors = {
            "success": MACOS_COLORS['success'],
            "error": MACOS_COLORS['danger'],
            "warning": MACOS_COLORS['warning'],
            "info": MACOS_COLORS['text_secondary']
        }
        self._status_icon.setText(icons.get(status_type, "ⓘ"))
        self._status_icon.setStyleSheet(f"color: {colors.get(status_type, MACOS_COLORS['text_secondary'])}; font-size: 14px; font-weight: bold; background: transparent;")
        self._status_label.setText(message)

        self._tray.show_message("PySnagit", message)

    def _quit(self):
        self._hotkey_manager.stop()
        self._tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._tray.show_message("PySnagit", "Application minimized to system tray")
