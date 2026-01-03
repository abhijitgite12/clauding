"""GIF creation from screen recording."""

import time
from pathlib import Path
from datetime import datetime
import tempfile
from PyQt6.QtCore import QThread, pyqtSignal, QRect
import mss
from PIL import Image
import imageio


class GifCreator(QThread):
    """Records screen and creates an animated GIF."""

    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str)  # Output path
    frame_captured = pyqtSignal(int)  # Frame count
    encoding_progress = pyqtSignal(int)  # Progress percentage
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        region: QRect = None,
        fps: int = 10,
        max_duration: float = 30.0
    ):
        """Initialize GIF creator.

        Args:
            region: Screen region to capture
            fps: Frames per second (GIFs work well with 10-15 fps)
            max_duration: Maximum recording duration in seconds
        """
        super().__init__()
        self._region = region
        self._fps = min(fps, 30)  # Cap GIF fps
        self._max_duration = max_duration

        self._running = False
        self._frames = []
        self._output_path = None

    def set_region(self, region: QRect):
        """Set recording region."""
        self._region = region

    def start_recording(self, output_path: str = None):
        """Start GIF recording."""
        if output_path:
            self._output_path = output_path
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._output_path = str(
                Path(tempfile.gettempdir()) / f"recording_{timestamp}.gif"
            )

        self._frames = []
        self._running = True
        self.start()

    def stop_recording(self):
        """Stop recording and create GIF."""
        self._running = False
        self.wait()

    def run(self):
        """Recording and encoding thread."""
        try:
            self._capture_frames()
            if self._frames:
                self._create_gif()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _capture_frames(self):
        """Capture frames for the GIF."""
        with mss.mss() as sct:
            if self._region:
                monitor = {
                    "left": self._region.x(),
                    "top": self._region.y(),
                    "width": self._region.width(),
                    "height": self._region.height()
                }
            else:
                monitor = sct.monitors[1]

            self.recording_started.emit()

            frame_interval = 1.0 / self._fps
            start_time = time.time()
            last_frame_time = start_time

            while self._running:
                current_time = time.time()

                # Check max duration
                if current_time - start_time >= self._max_duration:
                    break

                elapsed = current_time - last_frame_time
                if elapsed >= frame_interval:
                    # Capture frame
                    screenshot = sct.grab(monitor)
                    frame = Image.frombytes(
                        'RGB',
                        (screenshot.width, screenshot.height),
                        screenshot.rgb
                    )

                    # Resize if too large (GIFs should be smaller)
                    max_size = 800
                    if frame.width > max_size or frame.height > max_size:
                        ratio = max_size / max(frame.width, frame.height)
                        new_size = (int(frame.width * ratio), int(frame.height * ratio))
                        frame = frame.resize(new_size, Image.Resampling.LANCZOS)

                    self._frames.append(frame)
                    self.frame_captured.emit(len(self._frames))

                    last_frame_time = current_time
                else:
                    time.sleep(frame_interval - elapsed)

    def _create_gif(self):
        """Create GIF from captured frames."""
        if not self._frames:
            self.error_occurred.emit("No frames captured")
            return

        # Convert to optimized palette
        optimized_frames = []
        total = len(self._frames)

        for i, frame in enumerate(self._frames):
            # Convert to palette mode for smaller file size
            optimized = frame.convert('P', palette=Image.Palette.ADAPTIVE, colors=256)
            optimized_frames.append(optimized)
            self.encoding_progress.emit(int((i + 1) / total * 50))

        # Calculate frame duration in milliseconds
        duration = int(1000 / self._fps)

        # Save GIF
        imageio.mimsave(
            self._output_path,
            [frame.convert('RGB') for frame in self._frames],
            duration=duration / 1000,  # imageio uses seconds
            loop=0  # Infinite loop
        )

        self.encoding_progress.emit(100)
        self.recording_stopped.emit(self._output_path)

    def get_output_path(self) -> str:
        """Get output file path."""
        return self._output_path

    def get_frame_count(self) -> int:
        """Get current frame count."""
        return len(self._frames)


class GifOptimizer:
    """Utilities for optimizing GIF files."""

    @staticmethod
    def optimize(input_path: str, output_path: str = None, colors: int = 128) -> str:
        """Optimize a GIF file for smaller size.

        Args:
            input_path: Path to input GIF
            output_path: Path for optimized GIF (defaults to input with _optimized suffix)
            colors: Number of colors in palette (fewer = smaller)

        Returns:
            Path to optimized GIF
        """
        if not output_path:
            p = Path(input_path)
            output_path = str(p.parent / f"{p.stem}_optimized{p.suffix}")

        # Read GIF
        frames = imageio.mimread(input_path)

        # Optimize each frame
        optimized = []
        for frame in frames:
            img = Image.fromarray(frame)
            img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=colors)
            optimized.append(img.convert('RGB'))

        # Get original duration
        reader = imageio.get_reader(input_path)
        meta = reader.get_meta_data()
        duration = meta.get('duration', 100) / 1000

        # Save optimized
        imageio.mimsave(output_path, optimized, duration=duration, loop=0)

        return output_path

    @staticmethod
    def resize(input_path: str, output_path: str = None, max_size: int = 480) -> str:
        """Resize a GIF to reduce file size.

        Args:
            input_path: Path to input GIF
            output_path: Path for resized GIF
            max_size: Maximum dimension (width or height)

        Returns:
            Path to resized GIF
        """
        if not output_path:
            p = Path(input_path)
            output_path = str(p.parent / f"{p.stem}_small{p.suffix}")

        frames = imageio.mimread(input_path)
        resized = []

        for frame in frames:
            img = Image.fromarray(frame)
            if img.width > max_size or img.height > max_size:
                ratio = max_size / max(img.width, img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            resized.append(img)

        reader = imageio.get_reader(input_path)
        meta = reader.get_meta_data()
        duration = meta.get('duration', 100) / 1000

        imageio.mimsave(output_path, resized, duration=duration, loop=0)

        return output_path
