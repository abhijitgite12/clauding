"""OCR engine for text extraction - Phase 6 placeholder."""

from typing import Optional
from pathlib import Path

from ..utils.logger import get_logger

log = get_logger("ocr_engine")

# Check if pytesseract is available
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    log.warning("pytesseract not available. OCR features disabled.")


class OCREngine:
    """OCR engine using Tesseract."""

    def __init__(self, language: str = "eng"):
        self._language = language
        self._available = TESSERACT_AVAILABLE

    @property
    def is_available(self) -> bool:
        """Check if OCR is available."""
        return self._available

    def set_language(self, language: str):
        """Set OCR language (e.g., 'eng', 'fra', 'deu')."""
        self._language = language

    def extract_text_from_image(self, image) -> str:
        """Extract text from a PIL Image."""
        if not self._available:
            log.error("OCR not available")
            return ""

        try:
            text = pytesseract.image_to_string(image, lang=self._language)
            return text.strip()
        except Exception as e:
            log.error(f"OCR failed: {e}")
            return ""

    def is_page_scanned(self, page) -> bool:
        """Check if a PDF page appears to be scanned (image-based)."""
        # A page is likely scanned if it has images but little/no text
        if not page:
            return False

        text = page.get_text().strip()
        images = page.get_images()

        # Heuristic: if page has images but very little text, likely scanned
        if len(images) > 0 and len(text) < 50:
            return True
        return False

    def extract_text_from_page(self, page, dpi: int = 300) -> str:
        """Extract text from a PDF page using OCR."""
        if not self._available:
            return ""

        try:
            # Render page to image
            import fitz
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Run OCR
            text = self.extract_text_from_image(img)
            return text
        except Exception as e:
            log.error(f"Page OCR failed: {e}")
            return ""
