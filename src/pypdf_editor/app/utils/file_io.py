"""File I/O operations for PDFs."""

from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog


def generate_filename(prefix: str = "document", extension: str = "pdf") -> str:
    """Generate a timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def get_save_path(
    parent=None,
    default_name: str = "",
    filters: str = "PDF Files (*.pdf);;All Files (*.*)"
) -> Path | None:
    """Show a save file dialog and return the selected path."""
    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Save PDF",
        default_name,
        filters
    )
    return Path(path) if path else None


def get_open_path(
    parent=None,
    filters: str = "PDF Files (*.pdf);;All Files (*.*)"
) -> Path | None:
    """Show an open file dialog and return the selected path."""
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Open PDF",
        "",
        filters
    )
    return Path(path) if path else None


def get_open_paths(
    parent=None,
    filters: str = "PDF Files (*.pdf);;All Files (*.*)"
) -> list[Path]:
    """Show an open file dialog for multiple files."""
    paths, _ = QFileDialog.getOpenFileNames(
        parent,
        "Open PDFs",
        "",
        filters
    )
    return [Path(p) for p in paths] if paths else []


def get_directory(
    parent=None,
    title: str = "Select Directory"
) -> Path | None:
    """Show a directory selection dialog."""
    path = QFileDialog.getExistingDirectory(
        parent,
        title,
        ""
    )
    return Path(path) if path else None
