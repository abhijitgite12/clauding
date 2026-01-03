"""System tray integration."""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import pyqtSignal, QObject, Qt


class SystemTray(QObject):
    """System tray icon with menu."""

    # Signals for menu actions
    capture_full_screen = pyqtSignal()
    capture_region = pyqtSignal()
    capture_window = pyqtSignal()
    capture_scrolling = pyqtSignal()
    start_recording = pyqtSignal()
    start_gif = pyqtSignal()
    open_editor = pyqtSignal()
    show_settings = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tray = QSystemTrayIcon(parent)
        self._tray.setIcon(self._create_icon())
        self._tray.setToolTip("PySnagit - Screen Capture Tool")

        self._setup_menu()

        self._tray.activated.connect(self._on_activated)

    def _create_icon(self) -> QIcon:
        """Create the tray icon."""
        # Create a modern camera icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background circle
        painter.setBrush(QColor(99, 102, 241))  # Indigo
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 56, 56)

        # Camera body
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(16, 24, 32, 22, 4, 4)

        # Camera top
        painter.drawRoundedRect(24, 18, 16, 8, 2, 2)

        # Lens
        painter.setBrush(QColor(99, 102, 241))
        painter.drawEllipse(24, 28, 16, 16)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(28, 32, 8, 8)

        painter.end()

        return QIcon(pixmap)

    def _setup_menu(self):
        """Set up the context menu."""
        menu = QMenu()

        # Capture options
        capture_menu = menu.addMenu("Capture")

        action_full = QAction("Full Screen", self)
        action_full.setShortcut("Print")
        action_full.triggered.connect(self.capture_full_screen.emit)
        capture_menu.addAction(action_full)

        action_region = QAction("Region", self)
        action_region.setShortcut("Ctrl+Shift+R")
        action_region.triggered.connect(self.capture_region.emit)
        capture_menu.addAction(action_region)

        action_window = QAction("Window", self)
        action_window.setShortcut("Alt+Print")
        action_window.triggered.connect(self.capture_window.emit)
        capture_menu.addAction(action_window)

        action_scrolling = QAction("Scrolling Capture", self)
        action_scrolling.triggered.connect(self.capture_scrolling.emit)
        capture_menu.addAction(action_scrolling)

        menu.addSeparator()

        # Recording options
        record_menu = menu.addMenu("Record")

        action_video = QAction("Screen Recording", self)
        action_video.setShortcut("Ctrl+Shift+V")
        action_video.triggered.connect(self.start_recording.emit)
        record_menu.addAction(action_video)

        action_gif = QAction("GIF Recording", self)
        action_gif.setShortcut("Ctrl+Shift+G")
        action_gif.triggered.connect(self.start_gif.emit)
        record_menu.addAction(action_gif)

        menu.addSeparator()

        # Editor
        action_editor = QAction("Open Editor...", self)
        action_editor.triggered.connect(self.open_editor.emit)
        menu.addAction(action_editor)

        menu.addSeparator()

        # Settings
        action_settings = QAction("Settings...", self)
        action_settings.triggered.connect(self.show_settings.emit)
        menu.addAction(action_settings)

        menu.addSeparator()

        # Quit
        action_quit = QAction("Quit", self)
        action_quit.triggered.connect(self.quit_app.emit)
        menu.addAction(action_quit)

        self._tray.setContextMenu(menu)

    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_editor.emit()

    def show(self):
        """Show the tray icon."""
        self._tray.show()

    def hide(self):
        """Hide the tray icon."""
        self._tray.hide()

    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show a notification message."""
        self._tray.showMessage(title, message, icon, 3000)
