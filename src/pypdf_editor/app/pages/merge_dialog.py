"""Dialog for merging multiple PDFs."""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QFileDialog,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt

from ..editor.pdf_document import PDFDocument
from ..utils.file_io import get_save_path
from ..utils.logger import get_logger

log = get_logger("merge_dialog")


class PDFListItem(QListWidgetItem):
    """List item for a PDF file."""

    def __init__(self, path: str):
        super().__init__()
        self.file_path = path
        self.setText(Path(path).name)
        self.setToolTip(path)


class MergeDialog(QDialog):
    """Dialog for merging multiple PDF files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Merge PDFs")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Instructions
        instructions = QLabel(
            "Add PDF files to merge. Drag to reorder. "
            "Files will be merged in the order shown."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #8E8E93;")
        layout.addWidget(instructions)

        # File list
        self._file_list = QListWidget()
        self._file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._file_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E5E5E7;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F2;
            }
            QListWidget::item:selected {
                background-color: #E5F2FF;
            }
        """)
        layout.addWidget(self._file_list)

        # Add/Remove buttons
        btn_row = QHBoxLayout()

        add_btn = QPushButton("Add Files...")
        add_btn.clicked.connect(self._add_files)
        btn_row.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_selected)
        btn_row.addWidget(remove_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

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

        self._merge_btn = QPushButton("Merge")
        self._merge_btn.setObjectName("primaryButton")
        self._merge_btn.clicked.connect(self._do_merge)
        self._merge_btn.setEnabled(False)
        dialog_btns.addWidget(self._merge_btn)

        layout.addLayout(dialog_btns)

    def _add_files(self):
        """Add PDF files to the list."""
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDFs to Merge",
            "",
            "PDF Files (*.pdf)"
        )

        for path in paths:
            # Check if already added
            exists = False
            for i in range(self._file_list.count()):
                item = self._file_list.item(i)
                if isinstance(item, PDFListItem) and item.file_path == path:
                    exists = True
                    break

            if not exists:
                self._file_list.addItem(PDFListItem(path))

        self._update_merge_button()

    def _remove_selected(self):
        """Remove selected files from the list."""
        for item in self._file_list.selectedItems():
            self._file_list.takeItem(self._file_list.row(item))
        self._update_merge_button()

    def _clear_all(self):
        """Clear all files from the list."""
        self._file_list.clear()
        self._update_merge_button()

    def _update_merge_button(self):
        """Update merge button state."""
        self._merge_btn.setEnabled(self._file_list.count() >= 2)

    def _do_merge(self):
        """Perform the merge operation."""
        if self._file_list.count() < 2:
            return

        # Get output path
        output_path = get_save_path(
            self,
            default_name="merged.pdf"
        )

        if not output_path:
            return

        # Collect file paths in order
        paths = []
        for i in range(self._file_list.count()):
            item = self._file_list.item(i)
            if isinstance(item, PDFListItem):
                paths.append(item.file_path)

        # Show progress
        self._progress.setMaximum(len(paths))
        self._progress.setValue(0)
        self._progress.show()

        # Perform merge
        try:
            if PDFDocument.merge_pdfs(paths, str(output_path)):
                QMessageBox.information(
                    self,
                    "Success",
                    f"PDFs merged successfully!\n\nSaved to: {output_path}"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to merge PDFs."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error merging PDFs:\n{e}"
            )
        finally:
            self._progress.hide()

    def add_file(self, path: str):
        """Add a file to the merge list."""
        self._file_list.addItem(PDFListItem(path))
        self._update_merge_button()
