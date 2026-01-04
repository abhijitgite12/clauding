"""Dialog for splitting PDF into multiple files."""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QRadioButton, QButtonGroup,
    QLineEdit, QProgressBar, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt

from ..editor.pdf_document import PDFDocument
from ..utils.logger import get_logger

log = get_logger("split_dialog")


class SplitDialog(QDialog):
    """Dialog for splitting a PDF file."""

    def __init__(self, document: PDFDocument, parent=None):
        super().__init__(parent)
        self._document = document
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Split PDF")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Document info
        info = QLabel(f"Document: {self._document.filename}")
        info.setStyleSheet("font-weight: bold;")
        layout.addWidget(info)

        pages_info = QLabel(f"Total pages: {self._document.page_count}")
        pages_info.setStyleSheet("color: #8E8E93;")
        layout.addWidget(pages_info)

        layout.addSpacing(10)

        # Split mode selection
        mode_label = QLabel("Split mode:")
        mode_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(mode_label)

        self._mode_group = QButtonGroup(self)

        # Split every N pages
        every_n_row = QHBoxLayout()
        self._every_n_radio = QRadioButton("Split every")
        self._every_n_radio.setChecked(True)
        self._mode_group.addButton(self._every_n_radio, 0)
        every_n_row.addWidget(self._every_n_radio)

        self._pages_spin = QSpinBox()
        self._pages_spin.setMinimum(1)
        self._pages_spin.setMaximum(self._document.page_count)
        self._pages_spin.setValue(1)
        every_n_row.addWidget(self._pages_spin)

        every_n_row.addWidget(QLabel("page(s)"))
        every_n_row.addStretch()
        layout.addLayout(every_n_row)

        # Split into N files
        into_n_row = QHBoxLayout()
        self._into_n_radio = QRadioButton("Split into")
        self._mode_group.addButton(self._into_n_radio, 1)
        into_n_row.addWidget(self._into_n_radio)

        self._files_spin = QSpinBox()
        self._files_spin.setMinimum(2)
        self._files_spin.setMaximum(self._document.page_count)
        self._files_spin.setValue(2)
        into_n_row.addWidget(self._files_spin)

        into_n_row.addWidget(QLabel("equal files"))
        into_n_row.addStretch()
        layout.addLayout(into_n_row)

        # Split by page ranges
        ranges_row = QHBoxLayout()
        self._ranges_radio = QRadioButton("Custom ranges:")
        self._mode_group.addButton(self._ranges_radio, 2)
        ranges_row.addWidget(self._ranges_radio)
        layout.addLayout(ranges_row)

        self._ranges_input = QLineEdit()
        self._ranges_input.setPlaceholderText("e.g., 1-3, 4-6, 7-10")
        self._ranges_input.setEnabled(False)
        layout.addWidget(self._ranges_input)

        # Connect radio buttons to enable/disable inputs
        self._every_n_radio.toggled.connect(
            lambda c: self._pages_spin.setEnabled(c)
        )
        self._into_n_radio.toggled.connect(
            lambda c: self._files_spin.setEnabled(c)
        )
        self._ranges_radio.toggled.connect(
            lambda c: self._ranges_input.setEnabled(c)
        )

        layout.addSpacing(10)

        # Output directory
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output folder:"))

        self._output_path = QLineEdit()
        self._output_path.setReadOnly(True)
        self._output_path.setPlaceholderText("Select output folder...")
        output_row.addWidget(self._output_path)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_output)
        output_row.addWidget(browse_btn)

        layout.addLayout(output_row)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.hide()
        layout.addWidget(self._progress)

        # Dialog buttons
        dialog_btns = QHBoxLayout()
        dialog_btns.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_btns.addWidget(cancel_btn)

        self._split_btn = QPushButton("Split")
        self._split_btn.setObjectName("primaryButton")
        self._split_btn.clicked.connect(self._do_split)
        dialog_btns.addWidget(self._split_btn)

        layout.addLayout(dialog_btns)

    def _browse_output(self):
        """Browse for output directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder"
        )
        if path:
            self._output_path.setText(path)

    def _do_split(self):
        """Perform the split operation."""
        output_dir = self._output_path.text()
        if not output_dir:
            QMessageBox.warning(
                self,
                "No Output Folder",
                "Please select an output folder."
            )
            return

        mode = self._mode_group.checkedId()

        try:
            self._progress.show()

            if mode == 0:
                # Split every N pages
                pages_per_file = self._pages_spin.value()
                result = self._document.split_by_pages(output_dir, pages_per_file)

            elif mode == 1:
                # Split into N equal files
                num_files = self._files_spin.value()
                total_pages = self._document.page_count
                pages_per_file = max(1, total_pages // num_files)
                result = self._document.split_by_pages(output_dir, pages_per_file)

            else:
                # Custom ranges - parse and split
                ranges_text = self._ranges_input.text()
                result = self._split_by_ranges(output_dir, ranges_text)

            if result:
                QMessageBox.information(
                    self,
                    "Success",
                    f"PDF split into {len(result)} files!\n\n"
                    f"Saved to: {output_dir}"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to split PDF."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error splitting PDF:\n{e}"
            )
        finally:
            self._progress.hide()

    def _split_by_ranges(self, output_dir: str, ranges_text: str) -> list[str]:
        """Split PDF by custom page ranges."""
        import fitz

        output_paths = []
        ranges = self._parse_ranges(ranges_text)

        for i, (start, end) in enumerate(ranges, 1):
            indices = list(range(start - 1, end))  # Convert to 0-based
            pdf_bytes = self._document.extract_pages(indices)

            if pdf_bytes:
                name = self._document.path.stem if self._document.path else "split"
                out_file = Path(output_dir) / f"{name}_pages_{start}-{end}.pdf"
                out_file.write_bytes(pdf_bytes)
                output_paths.append(str(out_file))

        return output_paths

    def _parse_ranges(self, text: str) -> list[tuple[int, int]]:
        """Parse page ranges from text like '1-3, 4-6, 7-10'."""
        ranges = []
        for part in text.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-', 1)
                ranges.append((int(start.strip()), int(end.strip())))
            elif part.isdigit():
                page = int(part)
                ranges.append((page, page))
        return ranges
