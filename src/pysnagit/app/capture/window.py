"""Window capture functionality."""

import ctypes
from ctypes import wintypes
from PIL import Image
import mss

# Windows API functions
user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]


def get_window_at_cursor() -> int:
    """Get the window handle at the current cursor position."""
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return user32.WindowFromPoint(point)


def get_window_rect(hwnd: int) -> tuple[int, int, int, int]:
    """Get the window rectangle including shadow/borders.

    Returns:
        Tuple of (left, top, width, height)
    """
    rect = RECT()

    # Try DWM extended frame bounds first (more accurate)
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    result = dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(rect),
        ctypes.sizeof(rect)
    )

    if result != 0:
        # Fall back to regular window rect
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

    return (
        rect.left,
        rect.top,
        rect.right - rect.left,
        rect.bottom - rect.top
    )


def get_window_title(hwnd: int) -> str:
    """Get the window title."""
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buffer = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buffer, length)
    return buffer.value


def get_all_windows() -> list[dict]:
    """Get a list of all visible windows."""
    windows = []

    def enum_callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            title = get_window_title(hwnd)
            if title:  # Only include windows with titles
                left, top, width, height = get_window_rect(hwnd)
                if width > 0 and height > 0:
                    windows.append({
                        "hwnd": hwnd,
                        "title": title,
                        "left": left,
                        "top": top,
                        "width": width,
                        "height": height
                    })
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_int,
        ctypes.c_int
    )
    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)

    return windows


def capture_window(hwnd: int = None) -> Image.Image | None:
    """Capture a specific window.

    Args:
        hwnd: Window handle. If None, captures window at cursor.

    Returns:
        PIL Image of the captured window, or None if failed.
    """
    if hwnd is None:
        hwnd = get_window_at_cursor()

    if not hwnd or not user32.IsWindow(hwnd):
        return None

    left, top, width, height = get_window_rect(hwnd)

    if width <= 0 or height <= 0:
        return None

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


def bring_window_to_front(hwnd: int):
    """Bring a window to the foreground."""
    user32.SetForegroundWindow(hwnd)
