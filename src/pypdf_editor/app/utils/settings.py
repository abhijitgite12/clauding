"""Application settings management for PyPDF Editor."""

import json
from pathlib import Path
from PyQt6.QtCore import QStandardPaths


class Settings:
    """Manages application settings persistence."""

    DEFAULT_SETTINGS = {
        "viewer": {
            "zoom_mode": "fit_width",
            "scroll_mode": "continuous",
            "sidebar_visible": True,
            "show_thumbnails": True,
            "show_outline": True
        },
        "annotations": {
            "highlight_color": "#FFFF00",
            "text_color": "#000000",
            "default_thickness": 2,
            "default_font": "Helvetica",
            "default_font_size": 12
        },
        "editor": {
            "auto_save": False,
            "auto_save_interval": 300,
            "confirm_before_close": True
        },
        "ocr": {
            "language": "eng",
            "auto_detect_scanned": True
        },
        "general": {
            "recent_files": [],
            "max_recent_files": 10,
            "save_directory": "",
            "theme": "system",
            "start_maximized": True
        }
    }

    def __init__(self):
        self._settings = self._deep_copy(self.DEFAULT_SETTINGS)
        self._config_path = self._get_config_path()
        self.load()

    def _deep_copy(self, obj):
        """Deep copy a nested dict/list structure."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(i) for i in obj]
        return obj

    def _get_config_path(self) -> Path:
        """Get the configuration file path."""
        config_dir = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )) / "PyPDFEditor"
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
        """Get the save directory, defaulting to Documents."""
        save_dir = self.get("general", "save_directory")
        if save_dir:
            return Path(save_dir)
        return Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        ))

    def add_recent_file(self, path: str):
        """Add a file to the recent files list."""
        recent = self.get("general", "recent_files", [])
        # Remove if already exists
        if path in recent:
            recent.remove(path)
        # Add to front
        recent.insert(0, path)
        # Trim to max size
        max_files = self.get("general", "max_recent_files", 10)
        recent = recent[:max_files]
        self.set("general", "recent_files", recent)

    def get_recent_files(self) -> list:
        """Get the list of recent files."""
        return self.get("general", "recent_files", [])
