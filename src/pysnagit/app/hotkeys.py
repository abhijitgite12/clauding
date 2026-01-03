"""Global hotkey handling."""

import keyboard
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class HotkeyListener(QThread):
    """Background thread for listening to global hotkeys."""

    hotkey_triggered = pyqtSignal(str)

    def __init__(self, hotkeys: dict[str, str]):
        """Initialize with hotkey mappings.

        Args:
            hotkeys: Dict mapping action names to key combinations
        """
        super().__init__()
        self._hotkeys = hotkeys
        self._running = True
        self._registered_hotkeys = []

    def run(self):
        """Start listening for hotkeys."""
        for action, key_combo in self._hotkeys.items():
            try:
                keyboard.add_hotkey(
                    key_combo,
                    lambda a=action: self.hotkey_triggered.emit(a),
                    suppress=False
                )
                self._registered_hotkeys.append(key_combo)
            except Exception:
                pass  # Skip invalid hotkeys

        # Keep thread alive
        while self._running:
            self.msleep(100)

    def stop(self):
        """Stop listening for hotkeys."""
        self._running = False
        for key_combo in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(key_combo)
            except Exception:
                pass
        self._registered_hotkeys.clear()

    def update_hotkeys(self, hotkeys: dict[str, str]):
        """Update hotkey bindings."""
        # Remove old hotkeys
        for key_combo in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(key_combo)
            except Exception:
                pass
        self._registered_hotkeys.clear()

        # Register new hotkeys
        self._hotkeys = hotkeys
        for action, key_combo in self._hotkeys.items():
            try:
                keyboard.add_hotkey(
                    key_combo,
                    lambda a=action: self.hotkey_triggered.emit(a),
                    suppress=False
                )
                self._registered_hotkeys.append(key_combo)
            except Exception:
                pass


class HotkeyManager(QObject):
    """Manages global hotkeys for the application."""

    # Signals for different capture modes
    capture_full_screen = pyqtSignal()
    capture_region = pyqtSignal()
    capture_window = pyqtSignal()
    start_recording = pyqtSignal()
    start_gif = pyqtSignal()

    def __init__(self, settings=None, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._listener = None

    def start(self):
        """Start listening for hotkeys."""
        hotkeys = self._get_hotkey_config()
        self._listener = HotkeyListener(hotkeys)
        self._listener.hotkey_triggered.connect(self._on_hotkey)
        self._listener.start()

    def stop(self):
        """Stop listening for hotkeys."""
        if self._listener:
            self._listener.stop()
            self._listener.wait()
            self._listener = None

    def update_hotkeys(self):
        """Reload hotkeys from settings."""
        if self._listener:
            hotkeys = self._get_hotkey_config()
            self._listener.update_hotkeys(hotkeys)

    def _get_hotkey_config(self) -> dict[str, str]:
        """Get hotkey configuration from settings."""
        if self._settings:
            return self._settings.get_category("hotkeys")

        # Default hotkeys
        return {
            "full_screen": "Print",
            "region": "Ctrl+Shift+R",
            "window": "Alt+Print",
            "recording": "Ctrl+Shift+V",
            "gif": "Ctrl+Shift+G"
        }

    def _on_hotkey(self, action: str):
        """Handle hotkey trigger."""
        signal_map = {
            "full_screen": self.capture_full_screen,
            "region": self.capture_region,
            "window": self.capture_window,
            "recording": self.start_recording,
            "gif": self.start_gif
        }

        signal = signal_map.get(action)
        if signal:
            signal.emit()
