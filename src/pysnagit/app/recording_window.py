"""Recording control window - macOS Big Sur+ style."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QComboBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QColor

from .recording.video import ScreenRecorder
from .recording.gif import GifCreator
from .styles import DARK_THEME, COLORS, MACOS_BIGSUR_THEME, MACOS_COLORS, MACOS_RADIUS
from .animations import AnimationManager


class RecordingControlWindow(QWidget):
    """Floating window for recording controls."""

    recording_finished = pyqtSignal(str)  # Output path

    def __init__(self, mode: str = "video", region: QRect = None, settings=None, parent=None):
        """Initialize recording controls.

        Args:
            mode: 'video' or 'gif'
            region: Screen region to record
            settings: Application settings
        """
        super().__init__(parent)
        self._mode = mode
        self._region = region
        self._settings = settings
        self._recorder = None
        self._countdown = 0
        self._elapsed = 0
        self._pulse_animation = None

        # Apply macOS Big Sur+ theme
        self.setStyleSheet(MACOS_BIGSUR_THEME)
        self._setup_ui()
        self._setup_shadow()
        self._setup_recorder()

    def _setup_shadow(self):
        """Add floating panel shadow effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

    def _setup_ui(self):
        """Set up the UI - macOS Big Sur+ floating panel style."""
        self.setWindowTitle("Recording")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )
        self.setFixedWidth(340)

        # macOS floating panel styling with translucent background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {MACOS_COLORS['bg_white']};
                border-radius: {MACOS_RADIUS['xlarge']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 28, 28, 28)

        # Mode indicator
        mode_text = "🎥 Video Recording" if self._mode == "video" else "🎞️ GIF Recording"
        mode_label = QLabel(mode_text)
        mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {MACOS_COLORS['primary']};
            background: transparent;
        """)
        layout.addWidget(mode_label)

        # Time display
        self._time_label = QLabel("00:00")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_label.setStyleSheet(f"""
            font-size: 52px;
            font-weight: 700;
            font-family: 'Consolas', 'Courier New', monospace;
            color: {MACOS_COLORS['text_primary']};
            background: transparent;
            padding: 20px 0;
        """)
        layout.addWidget(self._time_label)

        # Status label
        self._status_label = QLabel("Ready to record")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(f"""
            font-size: 13px;
            color: {MACOS_COLORS['text_secondary']};
            background: transparent;
        """)
        layout.addWidget(self._status_label)

        # Progress bar (for GIF encoding) - iOS style thin bar
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setMaximumHeight(6)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {MACOS_COLORS['bg_main']};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {MACOS_COLORS['primary']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self._progress)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self._record_btn = QPushButton("⏺ Record")
        self._record_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MACOS_COLORS['danger']};
                color: white;
                font-weight: 600;
                font-size: 14px;
                padding: 14px 28px;
                border-radius: {MACOS_RADIUS['large']};
                border: none;
            }}
            QPushButton:hover {{
                background-color: #FF5555;
            }}
            QPushButton:disabled {{
                background-color: {MACOS_COLORS['border']};
                color: {MACOS_COLORS['text_tertiary']};
            }}
        """)
        self._record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._record_btn.clicked.connect(self._toggle_recording)
        button_layout.addWidget(self._record_btn)

        self._pause_btn = QPushButton("⏸ Pause")
        self._pause_btn.setEnabled(False)
        self._pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MACOS_COLORS['bg_white']};
                color: {MACOS_COLORS['text_primary']};
                border: 2px solid {MACOS_COLORS['border']};
                font-weight: 600;
                font-size: 14px;
                padding: 14px 20px;
                border-radius: {MACOS_RADIUS['large']};
            }}
            QPushButton:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
                border-color: {MACOS_COLORS['primary']};
            }}
            QPushButton:disabled {{
                background-color: {MACOS_COLORS['bg_main']};
                color: {MACOS_COLORS['text_tertiary']};
                border-color: {MACOS_COLORS['border_light']};
            }}
        """)
        self._pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pause_btn.clicked.connect(self._toggle_pause)
        button_layout.addWidget(self._pause_btn)

        self._stop_btn = QPushButton("⏹ Stop")
        self._stop_btn.setEnabled(False)
        self._stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MACOS_COLORS['bg_white']};
                color: {MACOS_COLORS['text_primary']};
                border: 2px solid {MACOS_COLORS['border']};
                font-weight: 600;
                font-size: 14px;
                padding: 14px 20px;
                border-radius: {MACOS_RADIUS['large']};
            }}
            QPushButton:hover {{
                background-color: {MACOS_COLORS['bg_hover']};
                border-color: {MACOS_COLORS['danger']};
                color: {MACOS_COLORS['danger']};
            }}
            QPushButton:disabled {{
                background-color: {MACOS_COLORS['bg_main']};
                color: {MACOS_COLORS['text_tertiary']};
                border-color: {MACOS_COLORS['border_light']};
            }}
        """)
        self._stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_btn.clicked.connect(self._stop_recording)
        button_layout.addWidget(self._stop_btn)

        layout.addLayout(button_layout)

        # Timer for elapsed time
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)

        # Countdown timer
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._countdown_tick)

    def _setup_recorder(self):
        """Set up the appropriate recorder."""
        fps = self._settings.get("recording", "fps", 30) if self._settings else 30
        include_audio = self._settings.get("recording", "include_audio", True) if self._settings else True

        if self._mode == "video":
            self._recorder = ScreenRecorder(
                region=self._region,
                fps=fps,
                include_audio=include_audio
            )
            self._recorder.recording_started.connect(self._on_recording_started)
            self._recorder.recording_stopped.connect(self._on_recording_stopped)
            self._recorder.frame_captured.connect(self._on_frame_captured)

        else:  # gif
            self._recorder = GifCreator(
                region=self._region,
                fps=min(fps, 15)  # GIFs work better at lower fps
            )
            self._recorder.recording_started.connect(self._on_recording_started)
            self._recorder.recording_stopped.connect(self._on_recording_stopped)
            self._recorder.frame_captured.connect(self._on_frame_captured)
            self._recorder.encoding_progress.connect(self._on_encoding_progress)

    def set_region(self, region: QRect):
        """Set the recording region."""
        self._region = region
        if self._recorder:
            self._recorder.set_region(region)

    def _toggle_recording(self):
        """Toggle recording state."""
        if not self._recorder:
            return

        if self._recorder.is_recording():
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """Start recording with optional countdown."""
        countdown = 0
        if self._settings:
            countdown = self._settings.get("recording", "countdown_seconds", 3)

        if countdown > 0:
            self._countdown = countdown
            self._status_label.setText(f"Starting in {countdown}...")
            self._record_btn.setEnabled(False)
            self._countdown_timer.start(1000)
        else:
            self._do_start_recording()

    def _countdown_tick(self):
        """Handle countdown tick with scale animation."""
        self._countdown -= 1
        if self._countdown > 0:
            self._status_label.setText(f"Starting in {self._countdown}...")
            # Animate time label with scale pulse
            AnimationManager.pulse_animation(self._time_label, count=1, scale_to=1.1)
        else:
            self._countdown_timer.stop()
            self._do_start_recording()

    def _do_start_recording(self):
        """Actually start the recording."""
        self._recorder.start_recording()

    def _stop_recording(self):
        """Stop recording."""
        if self._recorder and self._recorder.is_recording():
            self._recorder.stop_recording()
            self._timer.stop()

    def _toggle_pause(self):
        """Toggle pause state."""
        if not self._recorder or not isinstance(self._recorder, ScreenRecorder):
            return

        if self._recorder.is_paused():
            self._recorder.resume_recording()
            self._pause_btn.setText("Pause")
            self._status_label.setText("Recording...")
            self._timer.start(1000)
        else:
            self._recorder.pause_recording()
            self._pause_btn.setText("Resume")
            self._status_label.setText("Paused")
            self._timer.stop()

    def _on_recording_started(self):
        """Handle recording started with pulsing animation."""
        self._status_label.setText("Recording...")
        self._record_btn.setText("⏺ Recording")
        self._record_btn.setEnabled(False)
        self._pause_btn.setEnabled(self._mode == "video")
        self._stop_btn.setEnabled(True)
        self._elapsed = 0
        self._timer.start(1000)

        # Start pulsing the record button to show it's active
        self._start_pulse_animation()

    def _on_recording_stopped(self, output_path: str):
        """Handle recording stopped."""
        self._status_label.setText("Saved!")
        self._record_btn.setText("⏺ Record")
        self._record_btn.setEnabled(True)
        self._pause_btn.setEnabled(False)
        self._stop_btn.setEnabled(False)
        self._timer.stop()

        # Stop pulsing animation
        self._stop_pulse_animation()

        self.recording_finished.emit(output_path)

    def _on_frame_captured(self, count: int):
        """Handle frame captured."""
        pass  # Could update UI with frame count

    def _on_encoding_progress(self, progress: int):
        """Handle GIF encoding progress."""
        self._progress.setVisible(True)
        self._progress.setValue(progress)
        self._status_label.setText(f"Encoding... {progress}%")

        if progress >= 100:
            self._progress.setVisible(False)

    def _update_time(self):
        """Update the time display with subtle pulse animation."""
        self._elapsed += 1
        minutes = self._elapsed // 60
        seconds = self._elapsed % 60
        self._time_label.setText(f"{minutes:02d}:{seconds:02d}")

        # Subtle pulse every second to show it's live
        AnimationManager.pulse_animation(self._time_label, count=1, scale_to=1.02)

    def _start_pulse_animation(self):
        """Start continuous pulsing animation on record button."""
        # Create a timer for continuous pulsing
        if not hasattr(self, '_pulse_timer'):
            self._pulse_timer = QTimer(self)
            self._pulse_timer.timeout.connect(self._pulse_record_button)
        self._pulse_timer.start(2000)  # Pulse every 2 seconds

    def _pulse_record_button(self):
        """Pulse the record button."""
        if self._recorder and self._recorder.is_recording():
            AnimationManager.pulse_animation(self._record_btn, count=1, scale_to=1.05)

    def _stop_pulse_animation(self):
        """Stop the pulsing animation."""
        if hasattr(self, '_pulse_timer'):
            self._pulse_timer.stop()

    def closeEvent(self, event):
        """Handle window close."""
        if self._recorder and self._recorder.is_recording():
            self._stop_recording()
        event.accept()
