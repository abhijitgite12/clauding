"""Search panel for finding text in PDF."""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from .pdf_document import PDFDocument, SearchResult
from ..utils.logger import get_logger

log = get_logger("search_panel")


class SearchResultItem(QListWidgetItem):
    """List item representing a search result."""

    def __init__(self, result: SearchResult, context: str = ""):
        super().__init__()
        self.result = result
        self.setText(f"Page {result.page + 1}: {context[:50]}...")
        self.setToolTip(f"Page {result.page + 1}")


class SearchPanel(QWidget):
    """Panel for searching text in PDF."""

    result_selected = pyqtSignal(int, object)  # page, rect
    search_requested = pyqtSignal(str, dict)  # query, options
    search_completed = pyqtSignal(list)  # list of SearchResult
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._document: Optional[PDFDocument] = None
        self._results: list[SearchResult] = []
        self._current_index = -1
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QLabel("Search")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #1C1C1E;
            padding: 4px 0;
        """)
        layout.addWidget(header)

        # Search input
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search text...")
        self._search_input.returnPressed.connect(self._do_search)
        search_row.addWidget(self._search_input)

        self._search_btn = QPushButton("Find")
        self._search_btn.clicked.connect(self._do_search)
        search_row.addWidget(self._search_btn)

        layout.addLayout(search_row)

        # Options
        self._case_sensitive = QCheckBox("Case sensitive")
        layout.addWidget(self._case_sensitive)

        # Navigation
        nav_row = QHBoxLayout()
        self._prev_btn = QPushButton("Previous")
        self._prev_btn.clicked.connect(self._go_previous)
        self._prev_btn.setEnabled(False)
        nav_row.addWidget(self._prev_btn)

        self._next_btn = QPushButton("Next")
        self._next_btn.clicked.connect(self._go_next)
        self._next_btn.setEnabled(False)
        nav_row.addWidget(self._next_btn)

        layout.addLayout(nav_row)

        # Results count
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("color: #8E8E93;")
        layout.addWidget(self._count_label)

        # Results list
        self._results_list = QListWidget()
        self._results_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #E5E5E7;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F2;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
        """)
        self._results_list.itemClicked.connect(self._on_result_clicked)
        layout.addWidget(self._results_list)

        self.setMinimumWidth(250)
        self.setMaximumWidth(350)

    def set_document(self, document: PDFDocument):
        """Set the document to search."""
        self._document = document
        self._clear_results()

    def _do_search(self):
        """Perform the search."""
        query = self._search_input.text().strip()
        if not query:
            return

        options = {
            "case_sensitive": self._case_sensitive.isChecked()
        }

        # Emit signal for external handling
        self.search_requested.emit(query, options)
        log.info(f"Search requested for '{query}'")

    def _clear_results(self):
        """Clear search results."""
        self._results = []
        self._current_index = -1
        self._results_list.clear()
        self._count_label.setText("")
        self._update_navigation()

    def _update_navigation(self):
        """Update navigation button states."""
        has_results = len(self._results) > 0
        self._prev_btn.setEnabled(has_results and self._current_index > 0)
        self._next_btn.setEnabled(
            has_results and self._current_index < len(self._results) - 1
        )

    def _go_next(self):
        """Go to next search result."""
        if self._current_index < len(self._results) - 1:
            self._current_index += 1
            self._results_list.setCurrentRow(self._current_index)
            result = self._results[self._current_index]
            self.result_selected.emit(result.page, result.rect)
            self._update_navigation()

    def _go_previous(self):
        """Go to previous search result."""
        if self._current_index > 0:
            self._current_index -= 1
            self._results_list.setCurrentRow(self._current_index)
            result = self._results[self._current_index]
            self.result_selected.emit(result.page, result.rect)
            self._update_navigation()

    def _on_result_clicked(self, item: QListWidgetItem):
        """Handle result item click."""
        if isinstance(item, SearchResultItem):
            self._current_index = self._results_list.row(item)
            self.result_selected.emit(item.result.page, item.result.rect)
            self._update_navigation()

    def clear(self):
        """Clear the search."""
        self._search_input.clear()
        self._clear_results()

    def focus_search(self):
        """Focus the search input."""
        self._search_input.setFocus()
        self._search_input.selectAll()

    def show_results(self, results: list):
        """Display search results from external search."""
        self._clear_results()
        self._results = results

        for result in results:
            query = self._search_input.text()
            item = SearchResultItem(result, query)
            self._results_list.addItem(item)

        count = len(results)
        self._count_label.setText(f"{count} result{'s' if count != 1 else ''} found")
        self._update_navigation()

        if results:
            self._current_index = 0
            self._results_list.setCurrentRow(0)
