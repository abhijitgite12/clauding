"""Settings dialog for application configuration."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QCheckBox, QSpinBox, QComboBox, QLineEdit,
    QPushButton, QLabel, QFileDialog, QKeySequenceEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence


class SettingsDialog(QDialog):
    """Settings configuration dialog."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._changes = {}

        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # General tab
        tabs.addTab(self._create_general_tab(), "General")

        # Capture tab
        tabs.addTab(self._create_capture_tab(), "Capture")

        # Editor tab
        tabs.addTab(self._create_editor_tab(), "Editor")

        # Recording tab
        tabs.addTab(self._create_recording_tab(), "Recording")

        # Hotkeys tab
        tabs.addTab(self._create_hotkeys_tab(), "Hotkeys")

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Start minimized
        self._start_minimized = QCheckBox()
        layout.addRow("Start minimized to tray:", self._start_minimized)

        # Start with Windows
        self._start_with_windows = QCheckBox()
        layout.addRow("Start with Windows:", self._start_with_windows)

        # Save directory
        dir_layout = QHBoxLayout()
        self._save_dir = QLineEdit()
        self._save_dir.setReadOnly(True)
        dir_layout.addWidget(self._save_dir)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_save_dir)
        dir_layout.addWidget(browse_btn)

        layout.addRow("Default save directory:", dir_layout)

        # Theme
        self._theme = QComboBox()
        self._theme.addItems(["System", "Light", "Dark"])
        layout.addRow("Theme:", self._theme)

        return widget

    def _create_capture_tab(self) -> QWidget:
        """Create capture settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Include cursor
        self._include_cursor = QCheckBox()
        layout.addRow("Include cursor in captures:", self._include_cursor)

        # Capture delay
        self._capture_delay = QSpinBox()
        self._capture_delay.setRange(0, 10)
        self._capture_delay.setSuffix(" seconds")
        layout.addRow("Capture delay:", self._capture_delay)

        # Auto copy to clipboard
        self._auto_copy = QCheckBox()
        layout.addRow("Auto copy to clipboard:", self._auto_copy)

        # Default format
        self._default_format = QComboBox()
        self._default_format.addItems(["PNG", "JPEG", "BMP"])
        layout.addRow("Default save format:", self._default_format)

        return widget

    def _create_editor_tab(self) -> QWidget:
        """Create editor settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Default thickness
        self._default_thickness = QSpinBox()
        self._default_thickness.setRange(1, 20)
        layout.addRow("Default line thickness:", self._default_thickness)

        # Default font size
        self._default_font_size = QSpinBox()
        self._default_font_size.setRange(8, 72)
        layout.addRow("Default font size:", self._default_font_size)

        # Default font
        self._default_font = QComboBox()
        self._default_font.addItems(["Arial", "Times New Roman", "Courier New", "Segoe UI"])
        layout.addRow("Default font:", self._default_font)

        return widget

    def _create_recording_tab(self) -> QWidget:
        """Create recording settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # FPS
        self._recording_fps = QSpinBox()
        self._recording_fps.setRange(10, 60)
        layout.addRow("Recording FPS:", self._recording_fps)

        # Include audio
        self._include_audio = QCheckBox()
        layout.addRow("Include audio:", self._include_audio)

        # Countdown
        self._countdown = QSpinBox()
        self._countdown.setRange(0, 10)
        self._countdown.setSuffix(" seconds")
        layout.addRow("Countdown before recording:", self._countdown)

        # Output format
        self._video_format = QComboBox()
        self._video_format.addItems(["MP4", "AVI", "MKV"])
        layout.addRow("Video format:", self._video_format)

        return widget

    def _create_hotkeys_tab(self) -> QWidget:
        """Create hotkeys settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Capture hotkeys
        capture_group = QGroupBox("Capture Hotkeys")
        capture_layout = QFormLayout(capture_group)

        self._hotkey_full = QKeySequenceEdit()
        capture_layout.addRow("Full screen:", self._hotkey_full)

        self._hotkey_region = QKeySequenceEdit()
        capture_layout.addRow("Region:", self._hotkey_region)

        self._hotkey_window = QKeySequenceEdit()
        capture_layout.addRow("Window:", self._hotkey_window)

        layout.addWidget(capture_group)

        # Recording hotkeys
        record_group = QGroupBox("Recording Hotkeys")
        record_layout = QFormLayout(record_group)

        self._hotkey_video = QKeySequenceEdit()
        record_layout.addRow("Video recording:", self._hotkey_video)

        self._hotkey_gif = QKeySequenceEdit()
        record_layout.addRow("GIF recording:", self._hotkey_gif)

        layout.addWidget(record_group)

        layout.addStretch()

        return widget

    def _load_settings(self):
        """Load current settings into the UI."""
        # General
        self._start_minimized.setChecked(
            self._settings.get("general", "start_minimized", False)
        )
        self._start_with_windows.setChecked(
            self._settings.get("general", "start_with_windows", False)
        )
        self._save_dir.setText(
            self._settings.get("general", "save_directory", "")
        )

        theme = self._settings.get("general", "theme", "system")
        index = {"system": 0, "light": 1, "dark": 2}.get(theme, 0)
        self._theme.setCurrentIndex(index)

        # Capture
        self._include_cursor.setChecked(
            self._settings.get("capture", "include_cursor", True)
        )
        self._capture_delay.setValue(
            self._settings.get("capture", "delay_seconds", 0)
        )
        self._auto_copy.setChecked(
            self._settings.get("capture", "auto_copy_clipboard", True)
        )

        fmt = self._settings.get("capture", "default_save_format", "png").upper()
        self._default_format.setCurrentText(fmt)

        # Editor
        self._default_thickness.setValue(
            self._settings.get("editor", "default_thickness", 3)
        )
        self._default_font_size.setValue(
            self._settings.get("editor", "default_font_size", 14)
        )
        self._default_font.setCurrentText(
            self._settings.get("editor", "default_font", "Arial")
        )

        # Recording
        self._recording_fps.setValue(
            self._settings.get("recording", "fps", 30)
        )
        self._include_audio.setChecked(
            self._settings.get("recording", "include_audio", True)
        )
        self._countdown.setValue(
            self._settings.get("recording", "countdown_seconds", 3)
        )

        # Hotkeys
        hotkeys = self._settings.get_category("hotkeys")
        self._hotkey_full.setKeySequence(QKeySequence(hotkeys.get("full_screen", "Print")))
        self._hotkey_region.setKeySequence(QKeySequence(hotkeys.get("region", "Ctrl+Shift+R")))
        self._hotkey_window.setKeySequence(QKeySequence(hotkeys.get("window", "Alt+Print")))
        self._hotkey_video.setKeySequence(QKeySequence(hotkeys.get("recording", "Ctrl+Shift+V")))
        self._hotkey_gif.setKeySequence(QKeySequence(hotkeys.get("gif", "Ctrl+Shift+G")))

    def _browse_save_dir(self):
        """Open directory browser."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Save Directory",
            self._save_dir.text()
        )
        if dir_path:
            self._save_dir.setText(dir_path)

    def _save(self):
        """Save settings and close dialog."""
        # General
        self._settings.set("general", "start_minimized", self._start_minimized.isChecked())
        self._settings.set("general", "start_with_windows", self._start_with_windows.isChecked())
        self._settings.set("general", "save_directory", self._save_dir.text())
        self._settings.set("general", "theme", ["system", "light", "dark"][self._theme.currentIndex()])

        # Capture
        self._settings.set("capture", "include_cursor", self._include_cursor.isChecked())
        self._settings.set("capture", "delay_seconds", self._capture_delay.value())
        self._settings.set("capture", "auto_copy_clipboard", self._auto_copy.isChecked())
        self._settings.set("capture", "default_save_format", self._default_format.currentText().lower())

        # Editor
        self._settings.set("editor", "default_thickness", self._default_thickness.value())
        self._settings.set("editor", "default_font_size", self._default_font_size.value())
        self._settings.set("editor", "default_font", self._default_font.currentText())

        # Recording
        self._settings.set("recording", "fps", self._recording_fps.value())
        self._settings.set("recording", "include_audio", self._include_audio.isChecked())
        self._settings.set("recording", "countdown_seconds", self._countdown.value())

        # Hotkeys
        self._settings.set("hotkeys", "full_screen", self._hotkey_full.keySequence().toString())
        self._settings.set("hotkeys", "region", self._hotkey_region.keySequence().toString())
        self._settings.set("hotkeys", "window", self._hotkey_window.keySequence().toString())
        self._settings.set("hotkeys", "recording", self._hotkey_video.keySequence().toString())
        self._settings.set("hotkeys", "gif", self._hotkey_gif.keySequence().toString())

        self._settings.save()
        self.accept()
