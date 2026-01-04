"""OCR dialog for text extraction from scanned pages."""

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QProgressBar, QTextEdit,
    QCheckBox, QSpinBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from .ocr_engine import OCREngine, TESSERACT_AVAILABLE
from ..editor.pdf_document import PDFDocument
from ..utils.logger import get_logger

log = get_logger("ocr_dialog")


class OCRWorker(QThread):
    """Worker thread for OCR processing."""

    progress = pyqtSignal(int, int)  # current, total
    page_completed = pyqtSignal(int, str)  # page_index, text
    finished = pyqtSignal(dict)  # {page: text}
    error = pyqtSignal(str)

    def __init__(self, engine: OCREngine, document: PDFDocument, pages: list[int]):
        super().__init__()
        self._engine = engine
        self._document = document
        self._pages = pages
        self._cancelled = False

    def run(self):
        results = {}
        total = len(self._pages)

        for i, page_idx in enumerate(self._pages):
            if self._cancelled:
                break

            self.progress.emit(i + 1, total)

            try:
                page = self._document.get_page(page_idx)
                if page:
                    text = self._engine.extract_text_from_page(page)
                    results[page_idx] = text
                    self.page_completed.emit(page_idx, text)
            except Exception as e:
                self.error.emit(f"Error on page {page_idx + 1}: {e}")

        self.finished.emit(results)

    def cancel(self):
        self._cancelled = True


class OCRDialog(QDialog):
    """Dialog for OCR text extraction."""

    def __init__(self, document: PDFDocument, parent=None):
        super().__init__(parent)
        self._document = document
        self._engine = OCREngine()
        self._worker: Optional[OCRWorker] = None
        self._results: dict[int, str] = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("OCR - Text Recognition")
        self.setMinimumSize(500, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Check if OCR is available
        if not TESSERACT_AVAILABLE:
            warning = QLabel(
                "Tesseract OCR is not installed.\n\n"
                "To use OCR features, install Tesseract:\n"
                "• Windows: Download from github.com/UB-Mannheim/tesseract/wiki\n"
                "• macOS: brew install tesseract\n"
                "• Linux: sudo apt install tesseract-ocr"
            )
            warning.setStyleSheet("""
                background-color: #FFF3CD;
                border: 1px solid #FFE69C;
                border-radius: 8px;
                padding: 16px;
                color: #856404;
            """)
            warning.setWordWrap(True)
            layout.addWidget(warning)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.reject)
            layout.addWidget(close_btn)
            return

        # Settings group
        settings_group = QGroupBox("OCR Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Language selection
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Language:"))

        self._lang_combo = QComboBox()
        self._lang_combo.addItems([
            "English (eng)",
            "French (fra)",
            "German (deu)",
            "Spanish (spa)",
            "Italian (ita)",
            "Portuguese (por)",
            "Dutch (nld)",
            "Russian (rus)",
            "Chinese Simplified (chi_sim)",
            "Chinese Traditional (chi_tra)",
            "Japanese (jpn)",
            "Korean (kor)",
        ])
        lang_row.addWidget(self._lang_combo)
        lang_row.addStretch()
        settings_layout.addLayout(lang_row)

        # Page range
        pages_row = QHBoxLayout()
        pages_row.addWidget(QLabel("Pages:"))

        self._all_pages = QCheckBox("All pages")
        self._all_pages.setChecked(True)
        self._all_pages.toggled.connect(self._toggle_page_range)
        pages_row.addWidget(self._all_pages)

        pages_row.addWidget(QLabel("From:"))
        self._from_spin = QSpinBox()
        self._from_spin.setMinimum(1)
        self._from_spin.setMaximum(self._document.page_count)
        self._from_spin.setValue(1)
        self._from_spin.setEnabled(False)
        pages_row.addWidget(self._from_spin)

        pages_row.addWidget(QLabel("To:"))
        self._to_spin = QSpinBox()
        self._to_spin.setMinimum(1)
        self._to_spin.setMaximum(self._document.page_count)
        self._to_spin.setValue(self._document.page_count)
        self._to_spin.setEnabled(False)
        pages_row.addWidget(self._to_spin)

        pages_row.addStretch()
        settings_layout.addLayout(pages_row)

        # Detect scanned pages option
        self._detect_scanned = QCheckBox("Only process scanned/image pages")
        self._detect_scanned.setChecked(True)
        settings_layout.addWidget(self._detect_scanned)

        layout.addWidget(settings_group)

        # Progress
        self._progress_label = QLabel("Ready to start OCR")
        self._progress_label.setStyleSheet("color: #8E8E93;")
        layout.addWidget(self._progress_label)

        self._progress = QProgressBar()
        self._progress.hide()
        layout.addWidget(self._progress)

        # Results
        results_label = QLabel("Extracted Text:")
        results_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(results_label)

        self._results_text = QTextEdit()
        self._results_text.setReadOnly(True)
        self._results_text.setPlaceholderText("OCR results will appear here...")
        layout.addWidget(self._results_text)

        # Buttons
        btn_layout = QHBoxLayout()

        self._copy_btn = QPushButton("Copy Text")
        self._copy_btn.clicked.connect(self._copy_text)
        self._copy_btn.setEnabled(False)
        btn_layout.addWidget(self._copy_btn)

        btn_layout.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self._cancel_ocr)
        self._cancel_btn.hide()
        btn_layout.addWidget(self._cancel_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        self._start_btn = QPushButton("Start OCR")
        self._start_btn.setObjectName("primaryButton")
        self._start_btn.clicked.connect(self._start_ocr)
        btn_layout.addWidget(self._start_btn)

        layout.addLayout(btn_layout)

    def _toggle_page_range(self, all_pages: bool):
        """Toggle page range inputs."""
        self._from_spin.setEnabled(not all_pages)
        self._to_spin.setEnabled(not all_pages)

    def _get_pages_to_process(self) -> list[int]:
        """Get list of page indices to process."""
        if self._all_pages.isChecked():
            pages = list(range(self._document.page_count))
        else:
            start = self._from_spin.value() - 1
            end = self._to_spin.value()
            pages = list(range(start, end))

        # Filter to scanned pages if option is checked
        if self._detect_scanned.isChecked():
            scanned = []
            for idx in pages:
                page = self._document.get_page(idx)
                if page and self._engine.is_page_scanned(page):
                    scanned.append(idx)
            return scanned

        return pages

    def _get_language_code(self) -> str:
        """Extract language code from combo selection."""
        text = self._lang_combo.currentText()
        # Extract code from "English (eng)" format
        start = text.find('(')
        end = text.find(')')
        if start >= 0 and end > start:
            return text[start + 1:end]
        return "eng"

    def _start_ocr(self):
        """Start the OCR process."""
        pages = self._get_pages_to_process()

        if not pages:
            QMessageBox.information(
                self,
                "No Pages",
                "No pages to process. If 'Only process scanned pages' is checked, "
                "no scanned pages were detected."
            )
            return

        # Set language
        lang = self._get_language_code()
        self._engine.set_language(lang)

        # Update UI
        self._start_btn.setEnabled(False)
        self._cancel_btn.show()
        self._progress.setMaximum(len(pages))
        self._progress.setValue(0)
        self._progress.show()
        self._results_text.clear()
        self._results = {}

        # Start worker
        self._worker = OCRWorker(self._engine, self._document, pages)
        self._worker.progress.connect(self._on_progress)
        self._worker.page_completed.connect(self._on_page_completed)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

        self._progress_label.setText(f"Processing {len(pages)} pages...")

    def _cancel_ocr(self):
        """Cancel the OCR process."""
        if self._worker:
            self._worker.cancel()
            self._worker.wait()
        self._on_finished(self._results)

    def _on_progress(self, current: int, total: int):
        """Update progress."""
        self._progress.setValue(current)
        self._progress_label.setText(f"Processing page {current} of {total}...")

    def _on_page_completed(self, page_idx: int, text: str):
        """Handle completed page."""
        self._results[page_idx] = text

        # Append to results
        self._results_text.append(f"--- Page {page_idx + 1} ---\n")
        self._results_text.append(text if text else "(No text found)")
        self._results_text.append("\n\n")

    def _on_finished(self, results: dict):
        """Handle OCR completion."""
        self._results = results
        self._start_btn.setEnabled(True)
        self._cancel_btn.hide()
        self._progress.hide()
        self._copy_btn.setEnabled(bool(results))

        total_text = sum(len(t) for t in results.values())
        self._progress_label.setText(
            f"Completed! Extracted {total_text} characters from {len(results)} pages."
        )

        log.info(f"OCR completed: {len(results)} pages processed")

    def _on_error(self, error: str):
        """Handle OCR error."""
        log.error(f"OCR error: {error}")
        self._results_text.append(f"\nError: {error}\n")

    def _copy_text(self):
        """Copy extracted text to clipboard."""
        from PyQt6.QtWidgets import QApplication
        text = self._results_text.toPlainText()
        QApplication.clipboard().setText(text)
        self._progress_label.setText("Text copied to clipboard!")
