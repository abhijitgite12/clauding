"""Full screen capture functionality."""

import mss
import mss.tools
from PIL import Image


def capture_full_screen(monitor: int = 0) -> Image.Image:
    """Capture the entire screen.

    Args:
        monitor: Monitor index (0 for all monitors, 1+ for specific monitor)

    Returns:
        PIL Image of the captured screen
    """
    with mss.mss() as sct:
        if monitor == 0:
            # Capture all monitors combined
            screenshot = sct.grab(sct.monitors[0])
        else:
            # Capture specific monitor
            if monitor < len(sct.monitors):
                screenshot = sct.grab(sct.monitors[monitor])
            else:
                screenshot = sct.grab(sct.monitors[1])

        # Convert to PIL Image
        return Image.frombytes(
            'RGB',
            (screenshot.width, screenshot.height),
            screenshot.rgb
        )


def get_monitor_count() -> int:
    """Get the number of available monitors."""
    with mss.mss() as sct:
        return len(sct.monitors) - 1  # First entry is "all monitors"


def get_monitor_info() -> list[dict]:
    """Get information about all monitors."""
    with mss.mss() as sct:
        monitors = []
        for i, mon in enumerate(sct.monitors[1:], start=1):
            monitors.append({
                "index": i,
                "left": mon["left"],
                "top": mon["top"],
                "width": mon["width"],
                "height": mon["height"]
            })
        return monitors


def capture_region(left: int, top: int, width: int, height: int) -> Image.Image:
    """Capture a specific region of the screen.

    Args:
        left: X coordinate of top-left corner
        top: Y coordinate of top-left corner
        width: Width of the region
        height: Height of the region

    Returns:
        PIL Image of the captured region
    """
    with mss.mss() as sct:
        region = {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }
        screenshot = sct.grab(region)
        return Image.frombytes(
            'RGB',
            (screenshot.width, screenshot.height),
            screenshot.rgb
        )
