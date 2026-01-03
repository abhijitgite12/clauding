"""Scrolling window capture functionality."""

import time
import ctypes
from ctypes import wintypes
from PIL import Image
import mss

user32 = ctypes.windll.user32


class ScrollingCapture:
    """Captures scrolling content by stitching multiple screenshots."""

    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        self.images = []
        self._scroll_amount = 100  # pixels per scroll

    def capture(self, max_scrolls: int = 50) -> Image.Image | None:
        """Capture the full scrollable content.

        Args:
            max_scrolls: Maximum number of scroll operations

        Returns:
            Stitched PIL Image of the full content
        """
        from .window import get_window_rect, bring_window_to_front

        # Bring window to front
        bring_window_to_front(self.hwnd)
        time.sleep(0.05)  # Reduced from 0.2 to 0.05

        left, top, width, height = get_window_rect(self.hwnd)

        # Scroll to top first
        self._scroll_to_top()
        time.sleep(0.05)  # Reduced from 0.2 to 0.05

        previous_hash = None
        scroll_count = 0

        with mss.mss() as sct:
            while scroll_count < max_scrolls:
                # Capture current view
                region = {
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height
                }
                screenshot = sct.grab(region)
                img = Image.frombytes(
                    'RGB',
                    (screenshot.width, screenshot.height),
                    screenshot.rgb
                )

                # Check if content has changed (simple hash comparison)
                current_hash = hash(img.tobytes()[:10000])

                if current_hash == previous_hash:
                    # Reached end of content
                    break

                self.images.append(img)
                previous_hash = current_hash

                # Scroll down
                self._scroll_down()
                time.sleep(0.03)  # Reduced from 0.1 to 0.03
                scroll_count += 1

        if not self.images:
            return None

        return self._stitch_images()

    def _scroll_to_top(self):
        """Scroll the window to the top."""
        # Send Ctrl+Home to scroll to top
        VK_CONTROL = 0x11
        VK_HOME = 0x24

        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_HOME, 0, 0, 0)
        user32.keybd_event(VK_HOME, 0, 2, 0)  # Key up
        user32.keybd_event(VK_CONTROL, 0, 2, 0)  # Key up

    def _scroll_down(self):
        """Scroll the window down."""
        # Send Page Down
        VK_NEXT = 0x22  # Page Down
        user32.keybd_event(VK_NEXT, 0, 0, 0)
        user32.keybd_event(VK_NEXT, 0, 2, 0)

    def _stitch_images(self) -> Image.Image:
        """Stitch captured images into one tall image."""
        if len(self.images) == 1:
            return self.images[0]

        # Find overlap between consecutive images
        stitched_parts = [self.images[0]]

        for i in range(1, len(self.images)):
            prev_img = self.images[i - 1]
            curr_img = self.images[i]

            # Find the overlap by comparing bottom of prev with top of curr
            overlap = self._find_overlap(prev_img, curr_img)

            if overlap > 0:
                # Crop the overlapping part from current image
                cropped = curr_img.crop((0, overlap, curr_img.width, curr_img.height))
                stitched_parts.append(cropped)
            else:
                # No overlap found, just append (may have gaps)
                stitched_parts.append(curr_img)

        # Calculate total height
        total_height = sum(img.height for img in stitched_parts)
        width = stitched_parts[0].width

        # Create the final image
        result = Image.new('RGB', (width, total_height))

        y_offset = 0
        for img in stitched_parts:
            result.paste(img, (0, y_offset))
            y_offset += img.height

        return result

    def _find_overlap(self, img1: Image.Image, img2: Image.Image, max_overlap: int = None) -> int:
        """Find vertical overlap between two images.

        Compares the bottom of img1 with the top of img2.

        Returns:
            Number of overlapping pixels, or 0 if no overlap found.
        """
        if max_overlap is None:
            max_overlap = min(img1.height, img2.height) // 2

        # Sample a strip of pixels for comparison
        strip_height = 50
        sample_x = img1.width // 2
        sample_width = min(100, img1.width // 4)

        for overlap in range(strip_height, max_overlap, 10):
            # Get strips from bottom of img1 and top of img2
            y1 = img1.height - overlap
            strip1 = img1.crop((
                sample_x - sample_width // 2,
                y1,
                sample_x + sample_width // 2,
                y1 + strip_height
            ))

            strip2 = img2.crop((
                sample_x - sample_width // 2,
                0,
                sample_x + sample_width // 2,
                strip_height
            ))

            # Compare strips
            if self._images_match(strip1, strip2):
                return overlap

        return 0

    def _images_match(self, img1: Image.Image, img2: Image.Image, threshold: float = 0.95) -> bool:
        """Check if two images are similar enough (optimized with numpy)."""
        if img1.size != img2.size:
            return False

        # Fast comparison using numpy arrays (100x faster than pixel-by-pixel)
        import numpy as np
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Count matching pixels
        matching = np.sum(arr1 == arr2) / arr1.size

        return matching >= threshold
