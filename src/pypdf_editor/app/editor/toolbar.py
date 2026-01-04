"""PDF Editor toolbar."""

from PyQt6.QtWidgets import (
    QToolBar, QToolButton, QWidget, QHBoxLayout,
    QLabel, QSpinBox, QComboBox, QSizePolicy, QMenu,
    QButtonGroup, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor

from ..utils.logger import get_logger

log = get_logger("toolbar")


class ZoomWidget(QWidget):
    """Widget for zoom controls."""

    zoom_changed = pyqtSignal(float)
    fit_width_requested = pyqtSignal()
    fit_page_requested = pyqtSignal()

    ZOOM_LEVELS = [25, 50, 75, 100, 125, 150, 200, 300, 400]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)

        # Zoom out button
        self._zoom_out = QToolButton()
        self._zoom_out.setText("-")
        self._zoom_out.setToolTip("Zoom Out (Ctrl+-)")
        self._zoom_out.clicked.connect(self._on_zoom_out)
        layout.addWidget(self._zoom_out)

        # Zoom combo
        self._zoom_combo = QComboBox()
        self._zoom_combo.setEditable(True)
        self._zoom_combo.setMinimumWidth(80)
        for level in self.ZOOM_LEVELS:
            self._zoom_combo.addItem(f"{level}%", level)
        self._zoom_combo.addItem("Fit Width", "fit_width")
        self._zoom_combo.addItem("Fit Page", "fit_page")
        self._zoom_combo.setCurrentIndex(3)  # 100%
        self._zoom_combo.currentIndexChanged.connect(self._on_combo_changed)
        self._zoom_combo.lineEdit().returnPressed.connect(self._on_custom_zoom)
        layout.addWidget(self._zoom_combo)

        # Zoom in button
        self._zoom_in = QToolButton()
        self._zoom_in.setText("+")
        self._zoom_in.setToolTip("Zoom In (Ctrl++)")
        self._zoom_in.clicked.connect(self._on_zoom_in)
        layout.addWidget(self._zoom_in)

    def set_zoom(self, factor: float):
        """Set the displayed zoom level."""
        percent = int(factor * 100)
        # Find matching item or set custom text
        for i in range(self._zoom_combo.count()):
            if self._zoom_combo.itemData(i) == percent:
                self._zoom_combo.setCurrentIndex(i)
                return
        self._zoom_combo.setEditText(f"{percent}%")

    def _on_zoom_in(self):
        current = self._get_current_percent()
        for level in self.ZOOM_LEVELS:
            if level > current:
                self.zoom_changed.emit(level / 100)
                return

    def _on_zoom_out(self):
        current = self._get_current_percent()
        for level in reversed(self.ZOOM_LEVELS):
            if level < current:
                self.zoom_changed.emit(level / 100)
                return

    def _get_current_percent(self) -> int:
        text = self._zoom_combo.currentText().replace("%", "")
        try:
            return int(text)
        except ValueError:
            return 100

    def _on_combo_changed(self, index: int):
        data = self._zoom_combo.itemData(index)
        if data == "fit_width":
            self.fit_width_requested.emit()
        elif data == "fit_page":
            self.fit_page_requested.emit()
        elif isinstance(data, int):
            self.zoom_changed.emit(data / 100)

    def _on_custom_zoom(self):
        text = self._zoom_combo.currentText().replace("%", "")
        try:
            percent = int(text)
            percent = max(10, min(1000, percent))
            self.zoom_changed.emit(percent / 100)
        except ValueError:
            pass


class PageNavigator(QWidget):
    """Widget for page navigation."""

    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page_count = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)

        # Previous button
        self._prev = QToolButton()
        self._prev.setText("<")
        self._prev.setToolTip("Previous Page (Page Up)")
        self._prev.clicked.connect(self._on_prev)
        layout.addWidget(self._prev)

        # Page spinbox
        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setMaximum(1)
        self._page_spin.setMinimumWidth(60)
        self._page_spin.valueChanged.connect(self._on_page_changed)
        layout.addWidget(self._page_spin)

        # Total pages label
        self._total_label = QLabel("/ 1")
        layout.addWidget(self._total_label)

        # Next button
        self._next = QToolButton()
        self._next.setText(">")
        self._next.setToolTip("Next Page (Page Down)")
        self._next.clicked.connect(self._on_next)
        layout.addWidget(self._next)

    def set_page_count(self, count: int):
        """Set the total page count."""
        self._page_count = count
        self._page_spin.setMaximum(max(1, count))
        self._total_label.setText(f"/ {count}")
        self._update_buttons()

    def set_current_page(self, page: int):
        """Set the current page (0-based index)."""
        self._page_spin.blockSignals(True)
        self._page_spin.setValue(page + 1)
        self._page_spin.blockSignals(False)
        self._update_buttons()

    def _update_buttons(self):
        current = self._page_spin.value()
        self._prev.setEnabled(current > 1)
        self._next.setEnabled(current < self._page_count)

    def _on_prev(self):
        if self._page_spin.value() > 1:
            self._page_spin.setValue(self._page_spin.value() - 1)

    def _on_next(self):
        if self._page_spin.value() < self._page_count:
            self._page_spin.setValue(self._page_spin.value() + 1)

    def _on_page_changed(self, value: int):
        self.page_changed.emit(value - 1)  # Emit 0-based index
        self._update_buttons()


class PDFToolbar(QToolBar):
    """Main toolbar for PDF editor."""

    # File signals
    open_requested = pyqtSignal()
    save_requested = pyqtSignal()
    save_as_requested = pyqtSignal()
    print_requested = pyqtSignal()

    # View signals
    zoom_changed = pyqtSignal(float)
    fit_width_requested = pyqtSignal()
    fit_page_requested = pyqtSignal()
    page_changed = pyqtSignal(int)

    # Tool signals
    tool_selected = pyqtSignal(str)
    color_changed = pyqtSignal(object)  # QColor

    # Search signal
    search_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self._current_color = QColor(255, 255, 0)  # Yellow default
        self._tool_buttons = {}
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._setup_ui()

    def _setup_ui(self):
        """Set up toolbar components."""
        # File actions
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip("Open PDF (Ctrl+O)")
        open_action.triggered.connect(self.open_requested.emit)
        self.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setToolTip("Save (Ctrl+S)")
        save_action.triggered.connect(self.save_requested.emit)
        self.addAction(save_action)

        self.addSeparator()

        # Page navigator
        self._page_nav = PageNavigator()
        self._page_nav.page_changed.connect(self.page_changed.emit)
        self.addWidget(self._page_nav)

        self.addSeparator()

        # Zoom controls
        self._zoom_widget = ZoomWidget()
        self._zoom_widget.zoom_changed.connect(self.zoom_changed.emit)
        self._zoom_widget.fit_width_requested.connect(self.fit_width_requested.emit)
        self._zoom_widget.fit_page_requested.connect(self.fit_page_requested.emit)
        self.addWidget(self._zoom_widget)

        self.addSeparator()

        # Search button
        search_btn = QToolButton()
        search_btn.setText("Search")
        search_btn.setToolTip("Search (Ctrl+F)")
        search_btn.clicked.connect(self.search_requested.emit)
        self.addWidget(search_btn)

        self.addSeparator()

        # Tool buttons
        self._add_tool_button("select", "Select", "Selection and pan tool (V)", True)

        self.addSeparator()

        # Highlight tools dropdown
        highlight_btn = self._create_menu_button("Highlight", [
            ("highlight", "Highlight"),
            ("underline", "Underline"),
            ("strikethrough", "Strikethrough"),
        ])
        self.addWidget(highlight_btn)

        # Text tools dropdown
        text_btn = self._create_menu_button("Text", [
            ("textbox", "Text Box"),
            ("sticky_note", "Sticky Note"),
        ])
        self.addWidget(text_btn)

        # Drawing tools dropdown
        draw_btn = self._create_menu_button("Draw", [
            ("drawing", "Pen"),
            ("eraser", "Eraser"),
        ])
        self.addWidget(draw_btn)

        # Shape tools dropdown
        shape_btn = self._create_menu_button("Shapes", [
            ("rectangle", "Rectangle"),
            ("ellipse", "Ellipse"),
            ("line", "Line"),
            ("arrow", "Arrow"),
        ])
        self.addWidget(shape_btn)

        # Stamp button
        self._add_tool_button("stamp", "Stamp", "Add stamp annotation")

        # Image button
        self._add_tool_button("image", "Image", "Insert image")

        self.addSeparator()

        # Redact tools dropdown
        redact_btn = self._create_menu_button("Redact", [
            ("redact", "Redact (Black)"),
            ("whiteout", "Whiteout"),
        ])
        self.addWidget(redact_btn)

        self.addSeparator()

        # Color picker
        self._color_btn = QToolButton()
        self._color_btn.setText("Color")
        self._color_btn.setToolTip("Select annotation color")
        self._color_btn.clicked.connect(self._pick_color)
        self._update_color_button()
        self.addWidget(self._color_btn)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

    def _add_tool_button(self, tool_id: str, text: str, tooltip: str, checked: bool = False):
        """Add a checkable tool button."""
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.clicked.connect(lambda: self._on_tool_clicked(tool_id))
        self._button_group.addButton(btn)
        self._tool_buttons[tool_id] = btn
        self.addWidget(btn)
        return btn

    def _create_menu_button(self, text: str, items: list[tuple[str, str]]) -> QToolButton:
        """Create a dropdown menu button for tools."""
        btn = QToolButton()
        btn.setText(text)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(btn)
        for tool_id, label in items:
            action = menu.addAction(label)
            action.triggered.connect(lambda checked, tid=tool_id: self._on_tool_clicked(tid))

        btn.setMenu(menu)
        return btn

    def _on_tool_clicked(self, tool_id: str):
        """Handle tool selection."""
        # Uncheck other buttons
        for tid, btn in self._tool_buttons.items():
            btn.setChecked(tid == tool_id)

        self.tool_selected.emit(tool_id)
        log.debug(f"Tool selected: {tool_id}")

    def _pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self._current_color, self, "Select Color")
        if color.isValid():
            self._current_color = color
            self._update_color_button()
            self.color_changed.emit(color)

    def _update_color_button(self):
        """Update color button appearance."""
        self._color_btn.setStyleSheet(
            f"background-color: {self._current_color.name()}; "
            f"border: 1px solid #999; border-radius: 4px; padding: 4px 8px;"
        )

    def set_page_count(self, count: int):
        """Set the total page count."""
        self._page_nav.set_page_count(count)

    def set_current_page(self, page: int):
        """Set the current page (0-based)."""
        self._page_nav.set_current_page(page)

    def set_zoom(self, factor: float):
        """Set the zoom level display."""
        self._zoom_widget.set_zoom(factor)

    def set_current_tool(self, tool_id: str):
        """Set the currently selected tool."""
        for tid, btn in self._tool_buttons.items():
            btn.setChecked(tid == tool_id)

    def get_current_color(self) -> QColor:
        """Get the currently selected color."""
        return self._current_color
