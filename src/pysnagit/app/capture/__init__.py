"""Screen capture modules."""

from .screen import capture_full_screen
from .region import RegionSelector
from .window import capture_window
from .scrolling import ScrollingCapture

__all__ = ['capture_full_screen', 'RegionSelector', 'capture_window', 'ScrollingCapture']
