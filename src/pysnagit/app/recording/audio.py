"""Audio capture for screen recording."""

import wave
import tempfile
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class AudioRecorder(QThread):
    """Records system/microphone audio."""

    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str)  # Output path
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        sample_rate: int = 44100,
        channels: int = 2,
        chunk_size: int = 1024
    ):
        super().__init__()
        self._sample_rate = sample_rate
        self._channels = channels
        self._chunk_size = chunk_size

        self._running = False
        self._output_path = None
        self._audio = None
        self._stream = None

    def start_recording(self, output_path: str = None):
        """Start audio recording."""
        if not PYAUDIO_AVAILABLE:
            self.error_occurred.emit("PyAudio not available")
            return

        if output_path:
            self._output_path = output_path
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._output_path = str(
                Path(tempfile.gettempdir()) / f"audio_{timestamp}.wav"
            )

        self._running = True
        self.start()

    def stop_recording(self):
        """Stop audio recording."""
        self._running = False
        self.wait()

    def run(self):
        """Recording thread."""
        try:
            self._do_recording()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _do_recording(self):
        """Perform audio recording."""
        self._audio = pyaudio.PyAudio()

        # Open audio stream
        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=self._channels,
            rate=self._sample_rate,
            input=True,
            frames_per_buffer=self._chunk_size
        )

        # Open wave file
        wave_file = wave.open(self._output_path, 'wb')
        wave_file.setnchannels(self._channels)
        wave_file.setsampwidth(self._audio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(self._sample_rate)

        self.recording_started.emit()

        while self._running:
            data = self._stream.read(self._chunk_size, exception_on_overflow=False)
            wave_file.writeframes(data)

        # Cleanup
        self._stream.stop_stream()
        self._stream.close()
        self._audio.terminate()
        wave_file.close()

        self.recording_stopped.emit(self._output_path)

    def get_output_path(self) -> str:
        """Get output file path."""
        return self._output_path

    @staticmethod
    def is_available() -> bool:
        """Check if audio recording is available."""
        return PYAUDIO_AVAILABLE

    @staticmethod
    def get_input_devices() -> list[dict]:
        """Get list of available input devices."""
        if not PYAUDIO_AVAILABLE:
            return []

        devices = []
        audio = pyaudio.PyAudio()

        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })

        audio.terminate()
        return devices
