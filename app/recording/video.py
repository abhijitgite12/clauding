"""Screen recording functionality."""

import time
import threading
import tempfile
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QRect
import cv2
import numpy as np
import mss


class ScreenRecorder(QThread):
    """Records screen to video file."""

    # Signals
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str)  # Output path
    recording_paused = pyqtSignal()
    recording_resumed = pyqtSignal()
    frame_captured = pyqtSignal(int)  # Frame count
    error_occurred = pyqtSignal(str)

    def __init__(self, region: QRect = None, fps: int = 30, include_audio: bool = False):
        """Initialize recorder.

        Args:
            region: Screen region to capture (None for full screen)
            fps: Frames per second
            include_audio: Whether to capture system audio
        """
        super().__init__()
        self._region = region
        self._fps = fps
        self._include_audio = include_audio

        self._running = False
        self._paused = False
        self._output_path = None
        self._frame_count = 0
        self._writer = None
        self._audio_recorder = None

    def set_region(self, region: QRect):
        """Set the recording region."""
        self._region = region

    def set_fps(self, fps: int):
        """Set frames per second."""
        self._fps = max(1, min(60, fps))

    def start_recording(self, output_path: str = None):
        """Start recording."""
        if output_path:
            self._output_path = output_path
        else:
            # Generate temp file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._output_path = str(
                Path(tempfile.gettempdir()) / f"recording_{timestamp}.mp4"
            )

        self._running = True
        self._paused = False
        self._frame_count = 0
        self.start()

    def stop_recording(self):
        """Stop recording."""
        self._running = False
        self.wait()

    def pause_recording(self):
        """Pause recording."""
        self._paused = True
        self.recording_paused.emit()

    def resume_recording(self):
        """Resume recording."""
        self._paused = False
        self.recording_resumed.emit()

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._running

    def is_paused(self) -> bool:
        """Check if currently paused."""
        return self._paused

    def run(self):
        """Recording thread."""
        try:
            self._do_recording()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _do_recording(self):
        """Perform the actual recording."""
        with mss.mss() as sct:
            # Determine capture region
            if self._region:
                monitor = {
                    "left": self._region.x(),
                    "top": self._region.y(),
                    "width": self._region.width(),
                    "height": self._region.height()
                }
            else:
                monitor = sct.monitors[1]  # Primary monitor

            width = monitor["width"]
            height = monitor["height"]

            # Ensure dimensions are even (required by some codecs)
            width = width - (width % 2)
            height = height - (height % 2)

            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self._writer = cv2.VideoWriter(
                self._output_path,
                fourcc,
                self._fps,
                (width, height)
            )

            if not self._writer.isOpened():
                self.error_occurred.emit("Failed to create video file")
                return

            self.recording_started.emit()

            frame_interval = 1.0 / self._fps
            last_frame_time = time.time()

            while self._running:
                if self._paused:
                    time.sleep(0.1)
                    continue

                current_time = time.time()
                elapsed = current_time - last_frame_time

                if elapsed >= frame_interval:
                    # Capture frame
                    screenshot = sct.grab(monitor)

                    # Convert to numpy array
                    frame = np.array(screenshot)

                    # Convert BGRA to BGR (OpenCV format)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    # Resize if needed
                    if frame.shape[1] != width or frame.shape[0] != height:
                        frame = cv2.resize(frame, (width, height))

                    # Write frame
                    self._writer.write(frame)

                    self._frame_count += 1
                    self.frame_captured.emit(self._frame_count)

                    last_frame_time = current_time
                else:
                    # Sleep to avoid busy waiting
                    time.sleep(frame_interval - elapsed)

            # Cleanup
            self._writer.release()

            # Start audio recorder if needed
            if self._include_audio and self._audio_recorder:
                self._audio_recorder.stop()
                # TODO: Merge audio with video

            self.recording_stopped.emit(self._output_path)

    def get_output_path(self) -> str:
        """Get the output file path."""
        return self._output_path

    def get_frame_count(self) -> int:
        """Get the current frame count."""
        return self._frame_count

    def get_duration(self) -> float:
        """Get recording duration in seconds."""
        return self._frame_count / self._fps if self._fps > 0 else 0


class RecordingRegionSelector:
    """Helper to select recording region."""

    @staticmethod
    def select_region(callback):
        """Show region selector and call callback with selected region."""
        from ..capture.region import RegionSelector

        selector = RegionSelector()
        selector.region_selected.connect(callback)
        selector.show()
        return selector
