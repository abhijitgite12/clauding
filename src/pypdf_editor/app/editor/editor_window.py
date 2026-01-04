"""Main PDF Editor window."""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox, QFileDialog, QStatusBar,
    QLabel, QDockWidget, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QColor

from .pdf_document import PDFDocument
from .pdf_canvas import PDFCanvas
from .page_panel import PagePanel
from .outline_panel import OutlinePanel
from .search_panel import SearchPanel
from .toolbar import PDFToolbar
from .tools import (
    PDFBaseTool, SelectTool, HighlightTool, UnderlineTool, StrikethroughTool,
    TextBoxTool, StickyNoteTool, DrawingTool, EraserTool,
    RectangleTool, EllipseTool, LineTool, ArrowTool,
    StampTool, RedactTool, WhiteoutTool, ImageTool
)
from ..forms.form_handler import FormHandler
from ..forms.form_widgets import FormPanel
from ..pages.merge_dialog import MergeDialog
from ..pages.split_dialog import SplitDialog
from ..pages.extract_dialog import ExtractDialog
from ..ocr.ocr_dialog import OCRDialog
from ..styles import THEME
from ..utils.settings import Settings
from ..utils.file_io import get_open_path, get_save_path
from ..utils.logger import get_logger

log = get_logger("editor_window")


class EditorWindow(QMainWindow):
    """Main PDF Editor window."""

    document_opened = pyqtSignal(str)  # path
    document_closed = pyqtSignal()

    def __init__(self, pdf_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._document = PDFDocument()
        self._settings = Settings()
        self._form_handler: Optional[FormHandler] = None
        self._current_tool: Optional[PDFBaseTool] = None
        self._tools: dict[str, PDFBaseTool] = {}

        self._setup_tools()
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()

        # Apply theme
        self.setStyleSheet(THEME)

        # Set default tool
        self._set_tool("select")

        # Open file if provided
        if pdf_path:
            self.open_file(pdf_path)

    def _setup_tools(self):
        """Initialize all annotation tools."""
        self._tools = {
            "select": SelectTool(),
            "highlight": HighlightTool(),
            "underline": UnderlineTool(),
            "strikethrough": StrikethroughTool(),
            "textbox": TextBoxTool(),
            "sticky_note": StickyNoteTool(),
            "drawing": DrawingTool(),
            "eraser": EraserTool(),
            "rectangle": RectangleTool(),
            "ellipse": EllipseTool(),
            "line": LineTool(),
            "arrow": ArrowTool(),
            "stamp": StampTool(),
            "redact": RedactTool(),
            "whiteout": WhiteoutTool(),
            "image": ImageTool(),
        }

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("PyPDF Editor")
        self.setMinimumSize(1200, 800)

        # Restore window geometry
        if self._settings.get("general", "start_maximized", True):
            self.showMaximized()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        self._toolbar = PDFToolbar()
        self.addToolBar(self._toolbar)

        # Content area with splitter
        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left sidebar - Page thumbnails
        self._page_panel = PagePanel()
        self._splitter.addWidget(self._page_panel)

        # Center - PDF Canvas
        self._canvas = PDFCanvas()
        self._splitter.addWidget(self._canvas)

        # Right sidebar with tabs
        self._right_sidebar = QTabWidget()
        self._right_sidebar.setTabPosition(QTabWidget.TabPosition.North)

        # Outline panel tab
        self._outline_panel = OutlinePanel()
        self._right_sidebar.addTab(self._outline_panel, "Outline")

        # Form panel tab
        self._form_panel = FormPanel()
        self._right_sidebar.addTab(self._form_panel, "Forms")

        self._splitter.addWidget(self._right_sidebar)

        # Set splitter sizes (sidebar, canvas, sidebar)
        self._splitter.setSizes([180, 700, 250])
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setStretchFactor(2, 0)

        main_layout.addWidget(self._splitter)

        # Search panel dock
        self._search_dock = QDockWidget("Search", self)
        self._search_dock.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)
        self._search_panel = SearchPanel()
        self._search_dock.setWidget(self._search_panel)
        self._search_dock.hide()
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self._search_dock)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._page_label = QLabel("Page: 0 / 0")
        self._status_bar.addWidget(self._page_label)

        self._tool_label = QLabel("Tool: Select")
        self._status_bar.addWidget(self._tool_label)

        self._zoom_label = QLabel("Zoom: 100%")
        self._status_bar.addPermanentWidget(self._zoom_label)

    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Merge/Split/Extract actions
        merge_action = QAction("Merge PDFs...", self)
        merge_action.triggered.connect(self._show_merge_dialog)
        file_menu.addAction(merge_action)

        split_action = QAction("Split PDF...", self)
        split_action.triggered.connect(self._show_split_dialog)
        file_menu.addAction(split_action)

        extract_action = QAction("Extract Pages...", self)
        extract_action.triggered.connect(self._show_extract_dialog)
        file_menu.addAction(extract_action)

        file_menu.addSeparator()

        close_action = QAction("Close", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        find_action = QAction("Find...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._toggle_search)
        edit_menu.addAction(find_action)

        # View menu
        view_menu = menubar.addMenu("View")

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._canvas.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._canvas.zoom_out)
        view_menu.addAction(zoom_out_action)

        view_menu.addSeparator()

        fit_width_action = QAction("Fit Width", self)
        fit_width_action.triggered.connect(self._canvas.fit_width)
        view_menu.addAction(fit_width_action)

        fit_page_action = QAction("Fit Page", self)
        fit_page_action.triggered.connect(self._canvas.fit_page)
        view_menu.addAction(fit_page_action)

        actual_size_action = QAction("Actual Size", self)
        actual_size_action.setShortcut("Ctrl+0")
        actual_size_action.triggered.connect(self._canvas.actual_size)
        view_menu.addAction(actual_size_action)

        view_menu.addSeparator()

        toggle_pages_action = QAction("Show Pages", self)
        toggle_pages_action.setCheckable(True)
        toggle_pages_action.setChecked(True)
        toggle_pages_action.triggered.connect(
            lambda checked: self._page_panel.setVisible(checked)
        )
        view_menu.addAction(toggle_pages_action)

        toggle_sidebar_action = QAction("Show Sidebar", self)
        toggle_sidebar_action.setCheckable(True)
        toggle_sidebar_action.setChecked(True)
        toggle_sidebar_action.triggered.connect(
            lambda checked: self._right_sidebar.setVisible(checked)
        )
        view_menu.addAction(toggle_sidebar_action)

        # Page menu
        page_menu = menubar.addMenu("Page")

        rotate_cw_action = QAction("Rotate Clockwise", self)
        rotate_cw_action.triggered.connect(lambda: self._rotate_current_page(90))
        page_menu.addAction(rotate_cw_action)

        rotate_ccw_action = QAction("Rotate Counter-Clockwise", self)
        rotate_ccw_action.triggered.connect(lambda: self._rotate_current_page(-90))
        page_menu.addAction(rotate_ccw_action)

        page_menu.addSeparator()

        delete_page_action = QAction("Delete Page", self)
        delete_page_action.triggered.connect(self._delete_current_page)
        page_menu.addAction(delete_page_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        ocr_action = QAction("OCR - Extract Text...", self)
        ocr_action.triggered.connect(self._show_ocr_dialog)
        tools_menu.addAction(ocr_action)

        tools_menu.addSeparator()

        # Tool selection submenu
        select_tool_menu = tools_menu.addMenu("Annotation Tools")

        tool_actions = [
            ("Select", "select", "V"),
            ("Highlight", "highlight", "H"),
            ("Underline", "underline", "U"),
            ("Text Box", "textbox", "T"),
            ("Sticky Note", "sticky_note", "N"),
            ("Drawing", "drawing", "D"),
            ("Rectangle", "rectangle", "R"),
            ("Stamp", "stamp", "S"),
        ]

        for name, tool_id, shortcut in tool_actions:
            action = QAction(name, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(lambda checked, tid=tool_id: self._set_tool(tid))
            select_tool_menu.addAction(action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self):
        """Connect signals between components."""
        # Toolbar signals
        self._toolbar.open_requested.connect(self.open_file_dialog)
        self._toolbar.save_requested.connect(self.save_file)
        self._toolbar.zoom_changed.connect(self._canvas.set_zoom)
        self._toolbar.fit_width_requested.connect(self._canvas.fit_width)
        self._toolbar.fit_page_requested.connect(self._canvas.fit_page)
        self._toolbar.page_changed.connect(self._canvas.go_to_page)
        self._toolbar.tool_selected.connect(self._set_tool)
        self._toolbar.color_changed.connect(self._on_color_changed)
        self._toolbar.search_requested.connect(self._toggle_search)

        # Canvas signals
        self._canvas.page_changed.connect(self._on_page_changed)
        self._canvas.zoom_changed.connect(self._on_zoom_changed)

        # Page panel signals
        self._page_panel.page_selected.connect(self._canvas.go_to_page)
        self._page_panel.page_rotate_requested.connect(self._rotate_page)
        self._page_panel.page_delete_requested.connect(self._delete_page)

        # Outline panel signals
        self._outline_panel.item_selected.connect(self._canvas.go_to_page)

        # Search panel signals
        self._search_panel.search_requested.connect(self._do_search)
        self._search_panel.result_selected.connect(self._go_to_search_result)
        self._search_panel.close_requested.connect(lambda: self._search_dock.hide())

        # Form panel signals
        self._form_panel.field_changed.connect(self._on_form_field_changed)

        # Document signals
        self._document.document_modified.connect(self._on_document_modified)
        self._document.page_count_changed.connect(self._on_page_count_changed)

    def _set_tool(self, tool_id: str):
        """Set the current annotation tool."""
        if tool_id in self._tools:
            self._current_tool = self._tools[tool_id]
            self._canvas.set_tool(self._current_tool)
            self._toolbar.set_current_tool(tool_id)
            self._tool_label.setText(f"Tool: {tool_id.replace('_', ' ').title()}")
            log.debug(f"Tool set: {tool_id}")

    def _on_color_changed(self, color: QColor):
        """Handle color change from toolbar."""
        if self._current_tool:
            self._current_tool.set_color(color)

    def open_file_dialog(self):
        """Show open file dialog."""
        path = get_open_path(self)
        if path:
            self.open_file(str(path))

    def open_file(self, path: str):
        """Open a PDF file."""
        if not self._check_save_changes():
            return

        if self._document.open(path):
            self._canvas.set_document(self._document)
            self._page_panel.set_document(self._document)
            self._outline_panel.set_document(self._document)
            self._toolbar.set_page_count(self._document.page_count)

            # Set up form handler
            self._form_handler = FormHandler(self._document)
            self._form_panel.set_form_handler(self._form_handler)

            self._update_title()
            self._settings.add_recent_file(path)
            self.document_opened.emit(path)
            log.info(f"Opened: {path}")
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file:\n{path}"
            )

    def save_file(self):
        """Save the current file."""
        if not self._document.is_open:
            return

        if self._document.path:
            if self._document.save():
                self._update_title()
                self._status_bar.showMessage("Saved", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to save file")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save file with a new name."""
        if not self._document.is_open:
            return

        path = get_save_path(
            self,
            default_name=self._document.filename
        )
        if path:
            if self._document.save(str(path)):
                self._update_title()
                self._settings.add_recent_file(str(path))
                self._status_bar.showMessage("Saved", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to save file")

    def _check_save_changes(self) -> bool:
        """Check if there are unsaved changes. Returns True to proceed."""
        if not self._document.is_modified:
            return True

        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Do you want to save changes before closing?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )

        if result == QMessageBox.StandardButton.Save:
            self.save_file()
            return not self._document.is_modified
        elif result == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def _update_title(self):
        """Update window title."""
        title = "PyPDF Editor"
        if self._document.is_open:
            title = f"{self._document.filename} - {title}"
            if self._document.is_modified:
                title = f"*{title}"
        self.setWindowTitle(title)

    def _on_page_changed(self, page: int):
        """Handle page change."""
        self._toolbar.set_current_page(page)
        self._page_panel.set_current_page(page)
        self._page_label.setText(
            f"Page: {page + 1} / {self._document.page_count}"
        )

    def _on_zoom_changed(self, factor: float):
        """Handle zoom change."""
        self._toolbar.set_zoom(factor)
        self._zoom_label.setText(f"Zoom: {int(factor * 100)}%")

    def _on_document_modified(self):
        """Handle document modification."""
        self._update_title()

    def _on_page_count_changed(self, count: int):
        """Handle page count change."""
        self._toolbar.set_page_count(count)
        self._page_panel.refresh()
        self._canvas.refresh()

    def _on_form_field_changed(self, field, value):
        """Handle form field value change."""
        log.debug(f"Form field changed: {field.name} = {value}")
        self._document.mark_modified()

    def _rotate_current_page(self, degrees: int):
        """Rotate the current page."""
        self._rotate_page(self._canvas.current_page, degrees)

    def _rotate_page(self, page: int, degrees: int):
        """Rotate a specific page."""
        self._document.rotate_page(page, degrees)
        self._canvas.refresh()
        self._page_panel.refresh_page(page)

    def _delete_current_page(self):
        """Delete the current page."""
        self._delete_page(self._canvas.current_page)

    def _delete_page(self, page: int):
        """Delete a specific page."""
        if self._document.page_count <= 1:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete the last page."
            )
            return

        result = QMessageBox.question(
            self,
            "Delete Page",
            f"Are you sure you want to delete page {page + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self._document.delete_page(page)

    def _toggle_search(self):
        """Toggle search panel visibility."""
        if self._search_dock.isVisible():
            self._search_dock.hide()
        else:
            self._search_dock.show()
            self._search_panel.focus_search()

    def _do_search(self, query: str, options: dict):
        """Perform search in document."""
        if not self._document.is_open:
            return

        results = self._document.search(query, options.get("case_sensitive", False))
        self._search_panel.show_results(results)

    def _go_to_search_result(self, page: int, rect):
        """Navigate to a search result."""
        self._canvas.go_to_page(page)
        # Highlight the result on the canvas
        self._canvas.highlight_rect(rect)

    def _undo(self):
        """Undo last action."""
        # TODO: Implement undo stack
        log.debug("Undo requested")

    def _redo(self):
        """Redo last action."""
        # TODO: Implement redo stack
        log.debug("Redo requested")

    def _show_merge_dialog(self):
        """Show merge PDFs dialog."""
        dialog = MergeDialog(self)
        if self._document.is_open and self._document.path:
            dialog.add_file(str(self._document.path))
        dialog.exec()

    def _show_split_dialog(self):
        """Show split PDF dialog."""
        if not self._document.is_open:
            QMessageBox.warning(self, "No Document", "Please open a PDF first.")
            return

        dialog = SplitDialog(self._document, self)
        dialog.exec()

    def _show_extract_dialog(self):
        """Show extract pages dialog."""
        if not self._document.is_open:
            QMessageBox.warning(self, "No Document", "Please open a PDF first.")
            return

        dialog = ExtractDialog(self._document, self)
        dialog.select_page(self._canvas.current_page)
        dialog.exec()

    def _show_ocr_dialog(self):
        """Show OCR dialog."""
        if not self._document.is_open:
            QMessageBox.warning(self, "No Document", "Please open a PDF first.")
            return

        dialog = OCRDialog(self._document, self)
        dialog.exec()

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About PyPDF Editor",
            "PyPDF Editor\n\n"
            "A professional PDF editing tool.\n\n"
            "Features:\n"
            "- View and navigate PDFs\n"
            "- Annotations: highlight, underline, text, shapes, stamps\n"
            "- Page operations: rotate, delete, merge, split, extract\n"
            "- Form filling\n"
            "- OCR text extraction\n\n"
            "Built with PyQt6 and PyMuPDF"
        )

    def closeEvent(self, event):
        """Handle window close."""
        if self._check_save_changes():
            self._document.close()
            self.document_closed.emit()
            event.accept()
        else:
            event.ignore()
