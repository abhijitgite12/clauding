"""Dialog for extracting pages from PDF."""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt

from ..editor.pdf_document import PDFDocument
from ..utils.file_io import get_save_path
from ..utils.logger import get_logger

log = get_logger("extract_dialog")


class PageCheckItem(QListWidgetItem):
    """List item with checkbox for page selection."""

    def __init__(self, page_index: int):
        super().__init__()
        self.page_index = page_index
        self.setText(f"Page {page_index + 1}")
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(Qt.CheckState.Unchecked)


class ExtractDialog(QDialog):
    """Dialog for extracting selected pages to a new PDF."""

    def __init__(self, document: PDFDocument, parent=None):
        super().__init__(parent)
        self._document = document
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Extract Pages")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Instructions
        instructions = QLabel(
            "Select pages to extract into a new PDF file."
        )
        instructions.setStyleSheet("color: #8E8E93;")
        layout.addWidget(instructions)

        # Select all / none buttons
        select_row = QHBoxLayout()

        select_all = QPushButton("Select All")
        select_all.clicked.connect(self._select_all)
        select_row.addWidget(select_all)

        select_none = QPushButton("Select None")
        select_none.clicked.connect(self._select_none)
        select_row.addWidget(select_none)

        select_row.addStretch()

        self._count_label = QLabel("0 pages selected")
        self._count_label.setStyleSheet("color: #8E8E93;")
        select_row.addWidget(self._count_label)

        layout.addLayout(select_row)

        # Page list
        self._page_list = QListWidget()
        self._page_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E5E5E7;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F2;
            }
        """)
        self._page_list.itemChanged.connect(self._update_count)

        # Add page items
        for i in range(self._document.page_count):
            self._page_list.addItem(PageCheckItem(i))

        layout.addWidget(self._page_list)

        # Options
        self._delete_after = QCheckBox("Delete pages from original after extraction")
        layout.addWidget(self._delete_after)

        # Dialog buttons
        dialog_btns = QHBoxLayout()
        dialog_btns.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_btns.addWidget(cancel_btn)

        self._extract_btn = QPushButton("Extract")
        self._extract_btn.setObjectName("primaryButton")
        self._extract_btn.clicked.connect(self._do_extract)
        self._extract_btn.setEnabled(False)
        dialog_btns.addWidget(self._extract_btn)

        layout.addLayout(dialog_btns)

    def _select_all(self):
        """Select all pages."""
        for i in range(self._page_list.count()):
            item = self._page_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)

    def _select_none(self):
        """Deselect all pages."""
        for i in range(self._page_list.count()):
            item = self._page_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

    def _get_selected_indices(self) -> list[int]:
        """Get list of selected page indices."""
        indices = []
        for i in range(self._page_list.count()):
            item = self._page_list.item(i)
            if isinstance(item, PageCheckItem):
                if item.checkState() == Qt.CheckState.Checked:
                    indices.append(item.page_index)
        return indices

    def _update_count(self):
        """Update the selected count label."""
        count = len(self._get_selected_indices())
        self._count_label.setText(f"{count} page{'s' if count != 1 else ''} selected")
        self._extract_btn.setEnabled(count > 0)

    def _do_extract(self):
        """Perform the extraction."""
        indices = self._get_selected_indices()
        if not indices:
            return

        # Get output path
        default_name = f"{self._document.filename.replace('.pdf', '')}_extracted.pdf"
        output_path = get_save_path(
            self,
            default_name=default_name
        )

        if not output_path:
            return

        try:
            # Extract pages
            pdf_bytes = self._document.extract_pages(indices)

            if pdf_bytes:
                Path(output_path).write_bytes(pdf_bytes)

                # Optionally delete from original
                if self._delete_after.isChecked():
                    # Delete in reverse order to maintain indices
                    for idx in sorted(indices, reverse=True):
                        self._document.delete_page(idx)

                QMessageBox.information(
                    self,
                    "Success",
                    f"Extracted {len(indices)} pages!\n\nSaved to: {output_path}"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to extract pages."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error extracting pages:\n{e}"
            )

    def select_page(self, page_index: int):
        """Pre-select a specific page."""
        if 0 <= page_index < self._page_list.count():
            item = self._page_list.item(page_index)
            item.setCheckState(Qt.CheckState.Checked)
