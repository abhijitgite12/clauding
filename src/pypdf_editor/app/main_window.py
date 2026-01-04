"""Main launcher window for PyPDF Editor."""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

from .styles import THEME, MACOS_COLORS
from .utils.settings import Settings
from .utils.file_io import get_open_path
from .utils.logger import get_logger

log = get_logger("main_window")


class RecentFileItem(QListWidgetItem):
    """List item for recent files."""

    def __init__(self, path: str):
        super().__init__()
        self.file_path = path
        p = Path(path)
        self.setText(p.name)
        self.setToolTip(path)


class MainWindow(QMainWindow):
    """Main launcher window."""

    file_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = Settings()
        self._editor_windows = []

        self._setup_ui()
        self.setStyleSheet(THEME)

    def _setup_ui(self):
        """Set up the UI."""
        self.setWindowTitle("PyPDF Editor")
        self.setMinimumSize(600, 500)
        self.resize(700, 550)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Header
        header = QLabel("PyPDF Editor")
        header.setFont(QFont("", 28, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {MACOS_COLORS['text_primary']};")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        subtitle = QLabel("Professional PDF editing made simple")
        subtitle.setStyleSheet(f"color: {MACOS_COLORS['text_secondary']}; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(20)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Open file button
        open_btn = QPushButton("Open PDF")
        open_btn.setObjectName("primaryButton")
        open_btn.setMinimumSize(180, 50)
        open_btn.setFont(QFont("", 14, QFont.Weight.Medium))
        open_btn.clicked.connect(self._open_file)
        button_layout.addStretch()
        button_layout.addWidget(open_btn)

        # Create new button
        new_btn = QPushButton("Create New")
        new_btn.setMinimumSize(180, 50)
        new_btn.setFont(QFont("", 14, QFont.Weight.Medium))
        new_btn.clicked.connect(self._create_new)
        button_layout.addWidget(new_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        main_layout.addSpacing(20)

        # Recent files section
        recent_frame = QFrame()
        recent_frame.setObjectName("cardFrame")
        recent_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {MACOS_COLORS['bg_white']};
                border: 1px solid {MACOS_COLORS['border_light']};
                border-radius: 16px;
                padding: 20px;
            }}
        """)

        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(20, 20, 20, 20)
        recent_layout.setSpacing(12)

        recent_header = QLabel("Recent Files")
        recent_header.setFont(QFont("", 16, QFont.Weight.Bold))
        recent_header.setStyleSheet(f"color: {MACOS_COLORS['text_primary']};")
        recent_layout.addWidget(recent_header)

        self._recent_list = QListWidget()
        self._recent_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 8px;
            }}
            QListWidget::item:selected {{
                background-color: {MACOS_COLORS['primary']};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {MACOS_COLORS['bg_hover']};
            }}
        """)
        self._recent_list.setMinimumHeight(200)
        self._recent_list.itemDoubleClicked.connect(self._on_recent_clicked)
        recent_layout.addWidget(self._recent_list)

        self._load_recent_files()

        main_layout.addWidget(recent_frame)
        main_layout.addStretch()

    def _load_recent_files(self):
        """Load recent files from settings."""
        self._recent_list.clear()
        recent = self._settings.get_recent_files()

        if not recent:
            empty_item = QListWidgetItem("No recent files")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._recent_list.addItem(empty_item)
            return

        for path in recent:
            if Path(path).exists():
                item = RecentFileItem(path)
                self._recent_list.addItem(item)

    def _open_file(self):
        """Open file dialog."""
        path = get_open_path(self)
        if path:
            self._open_editor(str(path))

    def _create_new(self):
        """Create a new PDF (placeholder for now)."""
        log.info("Create new PDF requested")
        # For now, just open an empty editor
        # In Phase 4, this will create a blank PDF
        self._open_editor(None)

    def _on_recent_clicked(self, item: QListWidgetItem):
        """Handle recent file click."""
        if isinstance(item, RecentFileItem):
            self._open_editor(item.file_path)

    def _open_editor(self, path: Optional[str]):
        """Open the editor window."""
        from .editor import EditorWindow

        editor = EditorWindow(path, self)
        editor.document_closed.connect(lambda: self._on_editor_closed(editor))
        editor.show()
        self._editor_windows.append(editor)

        if path:
            self._settings.add_recent_file(path)
            self._load_recent_files()
            self.file_opened.emit(path)

        log.info(f"Opened editor for: {path or 'new document'}")

    def _on_editor_closed(self, editor):
        """Handle editor window closed."""
        if editor in self._editor_windows:
            self._editor_windows.remove(editor)

    def open_pdf(self, path: str):
        """Open a PDF file (called from main.py)."""
        if Path(path).exists():
            self._open_editor(path)
