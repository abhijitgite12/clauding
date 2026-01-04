"""OCR modules."""

from .ocr_engine import OCREngine, TESSERACT_AVAILABLE
from .ocr_dialog import OCRDialog, OCRWorker

__all__ = [
    "OCREngine",
    "TESSERACT_AVAILABLE",
    "OCRDialog",
    "OCRWorker",
]
