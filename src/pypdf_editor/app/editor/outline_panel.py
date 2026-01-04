"""Outline/Bookmarks panel for PDF navigation."""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

from .pdf_document import PDFDocument, OutlineItem
from ..utils.logger import get_logger

log = get_logger("outline_panel")


class OutlineTreeItem(QTreeWidgetItem):
    """Tree item representing an outline entry."""

    def __init__(self, outline_item: OutlineItem):
        super().__init__()
        self.outline_item = outline_item
        self.setText(0, outline_item.title)
        self.setToolTip(0, f"Page {outline_item.page + 1}")


class OutlinePanel(QWidget):
    """Panel showing document outline/bookmarks."""

    item_selected = pyqtSignal(int)  # page index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._document: Optional[PDFDocument] = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QLabel("Outline")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #1C1C1E;
            padding: 4px 0;
        """)
        layout.addWidget(header)

        # Tree widget
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)
        self._tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: none;
                outline: none;
            }
            QTreeWidget::item {
                padding: 8px 4px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QTreeWidget::item:hover:!selected {
                background-color: #F0F0F2;
            }
        """)

        self._tree.itemClicked.connect(self._on_item_clicked)
        self._tree.itemDoubleClicked.connect(self._on_item_clicked)

        layout.addWidget(self._tree)

        # No outline message
        self._empty_label = QLabel("No outline available")
        self._empty_label.setStyleSheet("""
            color: #8E8E93;
            font-style: italic;
            padding: 20px;
        """)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label)

        self.setMinimumWidth(200)
        self.setMaximumWidth(300)

    def set_document(self, document: PDFDocument):
        """Set the PDF document and load outline."""
        self._document = document
        self._load_outline()

    def _load_outline(self):
        """Load the document outline."""
        self._tree.clear()

        if not self._document:
            self._show_empty()
            return

        outline = self._document.get_outline()
        if not outline:
            self._show_empty()
            return

        self._empty_label.hide()
        self._tree.show()

        # Build tree structure
        item_stack: list[tuple[int, QTreeWidgetItem]] = []

        for entry in outline:
            tree_item = OutlineTreeItem(entry)
            level = entry.level

            # Find parent
            while item_stack and item_stack[-1][0] >= level:
                item_stack.pop()

            if item_stack:
                parent = item_stack[-1][1]
                parent.addChild(tree_item)
            else:
                self._tree.addTopLevelItem(tree_item)

            item_stack.append((level, tree_item))

        # Expand first level
        for i in range(self._tree.topLevelItemCount()):
            self._tree.topLevelItem(i).setExpanded(True)

        log.info(f"Loaded {len(outline)} outline items")

    def _show_empty(self):
        """Show empty state."""
        self._tree.hide()
        self._empty_label.show()

    def refresh(self):
        """Refresh the outline."""
        self._load_outline()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle outline item click."""
        if isinstance(item, OutlineTreeItem):
            page_index = item.outline_item.page
            self.item_selected.emit(page_index)
            log.debug(f"Selected outline item: {item.outline_item.title} (page {page_index})")
