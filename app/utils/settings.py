"""Application settings management."""

import json
from pathlib import Path
from PyQt6.QtCore import QStandardPaths


class Settings:
    """Manages application settings persistence."""

    DEFAULT_SETTINGS = {
        "hotkeys": {
            "full_screen": "Print",
            "region": "Ctrl+Shift+R",
            "window": "Alt+Print",
            "recording": "Ctrl+Shift+V",
            "gif": "Ctrl+Shift+G"
        },
        "capture": {
            "include_cursor": True,
            "delay_seconds": 0,
            "auto_copy_clipboard": True,
            "default_save_format": "png"
        },
        "editor": {
            "default_color": "#FF0000",
            "default_thickness": 3,
            "default_font_size": 14,
            "default_font": "Arial"
        },
        "recording": {
            "fps": 30,
            "include_audio": True,
            "countdown_seconds": 3,
            "output_format": "mp4"
        },
        "general": {
            "start_minimized": False,
            "start_with_windows": False,
            "save_directory": "",
            "theme": "system"
        }
    }

    def __init__(self):
        self._settings = self.DEFAULT_SETTINGS.copy()
        self._config_path = self._get_config_path()
        self.load()

    def _get_config_path(self) -> Path:
        """Get the configuration file path."""
        config_dir = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        ))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.json"

    def load(self):
        """Load settings from disk."""
        if self._config_path.exists():
            try:
                with open(self._config_path, 'r') as f:
                    saved = json.load(f)
                    self._deep_update(self._settings, saved)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults on error

    def save(self):
        """Save settings to disk."""
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except IOError:
            pass

    def _deep_update(self, base: dict, update: dict):
        """Recursively update nested dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, category: str, key: str, default=None):
        """Get a setting value."""
        return self._settings.get(category, {}).get(key, default)

    def set(self, category: str, key: str, value):
        """Set a setting value."""
        if category not in self._settings:
            self._settings[category] = {}
        self._settings[category][key] = value
        self.save()

    def get_category(self, category: str) -> dict:
        """Get all settings in a category."""
        return self._settings.get(category, {}).copy()

    def get_save_directory(self) -> Path:
        """Get the save directory, defaulting to Pictures."""
        save_dir = self.get("general", "save_directory")
        if save_dir:
            return Path(save_dir)
        return Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        ))
