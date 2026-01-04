"""Page thumbnails sidebar panel."""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap

from .pdf_document import PDFDocument
from ..utils.logger import get_logger

log = get_logger("page_panel")


class PageThumbnailItem(QListWidgetItem):
    """List item representing a page thumbnail."""

    def __init__(self, page_index: int, thumbnail: QPixmap):
        super().__init__()
        self.page_index = page_index
        self.setIcon(QIcon(thumbnail))
        self.setText(f"Page {page_index + 1}")
        self.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setSizeHint(QSize(140, 180))


class PagePanel(QWidget):
    """Sidebar panel showing page thumbnails."""

    page_selected = pyqtSignal(int)  # page index
    page_delete_requested = pyqtSignal(int)
    page_rotate_requested = pyqtSignal(int, int)  # page index, degrees
    pages_reorder_requested = pyqtSignal(int, int)  # from, to

    THUMBNAIL_SIZE = 120

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
        header = QLabel("Pages")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #1C1C1E;
            padding: 4px 0;
        """)
        layout.addWidget(header)

        # Thumbnail list
        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(QSize(self.THUMBNAIL_SIZE, self.THUMBNAIL_SIZE))
        self._list.setSpacing(8)
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list.setStyleSheet("""
            QListWidget {
                background-color: #F5F5F7;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: white;
                border: 2px solid transparent;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item:selected {
                border-color: #007AFF;
                background-color: #E5F2FF;
            }
            QListWidget::item:hover:!selected {
                background-color: #F0F0F2;
            }
        """)

        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.model().rowsMoved.connect(self._on_rows_moved)

        layout.addWidget(self._list)

        self.setMinimumWidth(160)
        self.setMaximumWidth(200)

    def set_document(self, document: PDFDocument):
        """Set the PDF document and load thumbnails."""
        self._document = document
        self._load_thumbnails()

    def _load_thumbnails(self):
        """Load all page thumbnails."""
        self._list.clear()

        if not self._document:
            return

        for i in range(self._document.page_count):
            thumbnail = self._document.get_thumbnail(i, self.THUMBNAIL_SIZE)
            item = PageThumbnailItem(i, thumbnail)
            self._list.addItem(item)

        log.info(f"Loaded {self._document.page_count} thumbnails")

    def refresh(self):
        """Refresh the thumbnails."""
        self._load_thumbnails()

    def refresh_page(self, page_index: int):
        """Refresh a single page thumbnail."""
        if not self._document or page_index >= self._list.count():
            return

        thumbnail = self._document.get_thumbnail(page_index, self.THUMBNAIL_SIZE)
        item = self._list.item(page_index)
        if item:
            item.setIcon(QIcon(thumbnail))

    def set_current_page(self, page_index: int):
        """Set the currently selected page."""
        if 0 <= page_index < self._list.count():
            self._list.setCurrentRow(page_index)
            self._list.scrollToItem(self._list.item(page_index))

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle thumbnail click."""
        if isinstance(item, PageThumbnailItem):
            self.page_selected.emit(item.page_index)

    def _on_rows_moved(self, parent, start, end, destination, row):
        """Handle drag-drop reordering."""
        # Calculate the actual moved indices
        from_idx = start
        to_idx = row if row < start else row - 1

        if from_idx != to_idx:
            self.pages_reorder_requested.emit(from_idx, to_idx)
            log.debug(f"Requested page move: {from_idx} -> {to_idx}")

    def contextMenuEvent(self, event):
        """Show context menu for page operations."""
        from PyQt6.QtWidgets import QMenu

        item = self._list.itemAt(event.pos())
        if not item or not isinstance(item, PageThumbnailItem):
            return

        menu = QMenu(self)

        rotate_cw = menu.addAction("Rotate Clockwise")
        rotate_ccw = menu.addAction("Rotate Counter-Clockwise")
        menu.addSeparator()
        delete_action = menu.addAction("Delete Page")
        delete_action.setEnabled(self._list.count() > 1)

        action = menu.exec(event.globalPos())

        if action == rotate_cw:
            self.page_rotate_requested.emit(item.page_index, 90)
        elif action == rotate_ccw:
            self.page_rotate_requested.emit(item.page_index, -90)
        elif action == delete_action:
            self.page_delete_requested.emit(item.page_index)
