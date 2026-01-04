"""PDF viewing canvas with QGraphicsView."""

from typing import Optional

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QBrush, QPen,
    QWheelEvent, QMouseEvent, QKeyEvent
)

from .pdf_document import PDFDocument
from ..utils.logger import get_logger

log = get_logger("pdf_canvas")


class PageItem(QGraphicsPixmapItem):
    """Graphics item representing a PDF page."""

    def __init__(self, pixmap: QPixmap, page_index: int, parent=None):
        super().__init__(pixmap, parent)
        self.page_index = page_index
        self.setAcceptHoverEvents(True)


class PDFCanvas(QGraphicsView):
    """Canvas for viewing and annotating PDF pages."""

    # Signals
    page_changed = pyqtSignal(int)  # current page index
    zoom_changed = pyqtSignal(float)  # zoom factor
    mouse_position = pyqtSignal(int, QPointF)  # page_index, position
    selection_changed = pyqtSignal(QRectF)  # selected area
    annotation_added = pyqtSignal(int, object)  # page_index, annotation

    # Zoom limits
    MIN_ZOOM = 0.1
    MAX_ZOOM = 10.0
    ZOOM_STEP = 1.25

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._document: Optional[PDFDocument] = None
        self._current_page = 0
        self._zoom_factor = 1.0
        self._page_items: list[PageItem] = []
        self._page_spacing = 20
        self._scroll_mode = "continuous"  # "continuous" or "single_page"
        self._current_tool = None
        self._is_panning = False
        self._pan_start = QPointF()
        self._selection_rect: Optional[QGraphicsRectItem] = None
        self._highlight_rects: list[QGraphicsRectItem] = []

        self._setup_view()

    def _setup_view(self):
        """Configure view settings."""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor(90, 90, 90)))
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)

    @property
    def document(self) -> Optional[PDFDocument]:
        return self._document

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def zoom_factor(self) -> float:
        return self._zoom_factor

    @property
    def page_count(self) -> int:
        return len(self._page_items)

    def set_document(self, document: PDFDocument):
        """Set the PDF document to display."""
        self._document = document
        self._current_page = 0
        self._zoom_factor = 1.0
        self._render_all_pages()
        self.fit_width()
        log.info(f"Set document with {document.page_count} pages")

    def _render_all_pages(self):
        """Render all pages of the document."""
        self._scene.clear()
        self._page_items.clear()
        self._highlight_rects.clear()

        if not self._document:
            return

        y_offset = self._page_spacing

        for i in range(self._document.page_count):
            pixmap = self._document.get_page_pixmap(i, self._zoom_factor)
            item = PageItem(pixmap, i)

            # Center horizontally
            x_offset = self._page_spacing

            item.setPos(x_offset, y_offset)
            self._scene.addItem(item)
            self._page_items.append(item)

            # Add page shadow effect
            shadow = QGraphicsRectItem(
                x_offset + 3,
                y_offset + 3,
                pixmap.width(),
                pixmap.height()
            )
            shadow.setBrush(QBrush(QColor(0, 0, 0, 30)))
            shadow.setPen(QPen(Qt.PenStyle.NoPen))
            shadow.setZValue(-1)
            self._scene.addItem(shadow)

            y_offset += pixmap.height() + self._page_spacing

        # Update scene rect
        self._scene.setSceneRect(self._scene.itemsBoundingRect().adjusted(
            -self._page_spacing, -self._page_spacing,
            self._page_spacing, self._page_spacing
        ))

    def refresh(self):
        """Refresh the current view."""
        self._render_all_pages()

    # Navigation
    def go_to_page(self, index: int):
        """Navigate to a specific page."""
        if 0 <= index < len(self._page_items):
            self._current_page = index
            self.centerOn(self._page_items[index])
            self.page_changed.emit(index)
            log.debug(f"Navigated to page {index}")

    def next_page(self):
        """Go to the next page."""
        if self._current_page < len(self._page_items) - 1:
            self.go_to_page(self._current_page + 1)

    def previous_page(self):
        """Go to the previous page."""
        if self._current_page > 0:
            self.go_to_page(self._current_page - 1)

    def first_page(self):
        """Go to the first page."""
        self.go_to_page(0)

    def last_page(self):
        """Go to the last page."""
        if self._page_items:
            self.go_to_page(len(self._page_items) - 1)

    # Zoom
    def set_zoom(self, factor: float):
        """Set zoom level."""
        factor = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))
        if factor != self._zoom_factor:
            self._zoom_factor = factor
            self._render_all_pages()
            self.zoom_changed.emit(factor)
            log.debug(f"Zoom set to {factor:.2f}")

    def zoom_in(self):
        """Zoom in by one step."""
        self.set_zoom(self._zoom_factor * self.ZOOM_STEP)

    def zoom_out(self):
        """Zoom out by one step."""
        self.set_zoom(self._zoom_factor / self.ZOOM_STEP)

    def fit_width(self):
        """Fit page width to view."""
        if not self._page_items:
            return

        # Get first page width at zoom 1.0
        if self._document:
            page_width, _ = self._document.get_page_size(0)
            view_width = self.viewport().width() - 40
            factor = view_width / page_width
            self.set_zoom(factor)

    def fit_page(self):
        """Fit entire page in view."""
        if not self._page_items:
            return

        if self._document:
            page_width, page_height = self._document.get_page_size(0)
            view_width = self.viewport().width() - 40
            view_height = self.viewport().height() - 40

            factor_w = view_width / page_width
            factor_h = view_height / page_height
            factor = min(factor_w, factor_h)
            self.set_zoom(factor)

    def actual_size(self):
        """Set zoom to 100%."""
        self.set_zoom(1.0)

    # Tool management
    def set_tool(self, tool):
        """Set the current annotation tool."""
        self._current_tool = tool
        if tool:
            self.setCursor(tool.cursor())
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # Search highlighting
    def highlight_search_results(self, results: list):
        """Highlight search results on the canvas."""
        # Clear existing highlights
        self.clear_search_highlights()

        for result in results:
            page_idx = result.page
            if page_idx < len(self._page_items):
                page_item = self._page_items[page_idx]
                rect = result.rect

                # Scale rect by zoom factor
                scaled_rect = QRectF(
                    rect.x0 * self._zoom_factor,
                    rect.y0 * self._zoom_factor,
                    rect.width * self._zoom_factor,
                    rect.height * self._zoom_factor
                )

                # Create highlight rect
                highlight = QGraphicsRectItem(scaled_rect, page_item)
                highlight.setBrush(QBrush(QColor(255, 255, 0, 100)))
                highlight.setPen(QPen(QColor(255, 200, 0), 1))
                self._highlight_rects.append(highlight)

    def clear_search_highlights(self):
        """Clear all search highlight rectangles."""
        for rect in self._highlight_rects:
            self._scene.removeItem(rect)
        self._highlight_rects.clear()

    def scroll_to_search_result(self, result):
        """Scroll to show a specific search result."""
        page_idx = result.page
        if page_idx < len(self._page_items):
            page_item = self._page_items[page_idx]
            rect = result.rect

            # Calculate scene position
            scene_x = page_item.x() + rect.x0 * self._zoom_factor
            scene_y = page_item.y() + rect.y0 * self._zoom_factor

            self.centerOn(scene_x, scene_y)
            self._current_page = page_idx
            self.page_changed.emit(page_idx)

    # Helper methods
    def _get_page_at_pos(self, scene_pos: QPointF) -> int:
        """Get page index at scene position."""
        for i, item in enumerate(self._page_items):
            if item.contains(scene_pos - item.pos()):
                return i
        return self._current_page

    def _get_page_coords(self, scene_pos: QPointF, page_index: int) -> QPointF:
        """Convert scene position to page coordinates."""
        if page_index < len(self._page_items):
            page_item = self._page_items[page_index]
            local_pos = scene_pos - page_item.pos()
            # Convert to PDF coordinates (unzoomed)
            return QPointF(
                local_pos.x() / self._zoom_factor,
                local_pos.y() / self._zoom_factor
            )
        return QPointF()

    # Event handlers
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zoom and scroll."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+Wheel
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Normal scroll
            super().wheelEvent(event)
            # Update current page based on scroll position
            self._update_current_page_from_scroll()

    def _update_current_page_from_scroll(self):
        """Update current page based on scroll position."""
        center = self.mapToScene(self.viewport().rect().center())
        page_idx = self._get_page_at_pos(center)
        if page_idx != self._current_page:
            self._current_page = page_idx
            self.page_changed.emit(page_idx)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Start panning
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton and self._current_tool:
            scene_pos = self.mapToScene(event.pos())
            page_idx = self._get_page_at_pos(scene_pos)
            page_pos = self._get_page_coords(scene_pos, page_idx)
            self._current_tool.on_press(page_pos, self, page_idx)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move."""
        if self._is_panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        elif self._current_tool:
            scene_pos = self.mapToScene(event.pos())
            page_idx = self._get_page_at_pos(scene_pos)
            page_pos = self._get_page_coords(scene_pos, page_idx)
            self.mouse_position.emit(page_idx, page_pos)
            self._current_tool.on_move(page_pos, self)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = False
            if self._current_tool:
                self.setCursor(self._current_tool.cursor())
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton and self._current_tool:
            scene_pos = self.mapToScene(event.pos())
            page_idx = self._get_page_at_pos(scene_pos)
            page_pos = self._get_page_coords(scene_pos, page_idx)
            self._current_tool.on_release(page_pos, self, page_idx)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key presses."""
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.zoom_in()
                return
        elif key == Qt.Key.Key_Minus:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.zoom_out()
                return
        elif key == Qt.Key.Key_0:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.actual_size()
                return
        elif key == Qt.Key.Key_PageDown:
            self.next_page()
            return
        elif key == Qt.Key.Key_PageUp:
            self.previous_page()
            return
        elif key == Qt.Key.Key_Home:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.first_page()
                return
        elif key == Qt.Key.Key_End:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.last_page()
                return

        super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Handle resize."""
        super().resizeEvent(event)
        # Could auto-fit here if desired
