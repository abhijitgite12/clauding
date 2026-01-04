"""Widgets for displaying and editing PDF form fields."""

from typing import Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QComboBox, QTextEdit,
    QScrollArea, QFrame, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from .form_handler import FormHandler, FormField
from ..utils.logger import get_logger

log = get_logger("form_widgets")


class FormFieldWidget(QWidget):
    """Base widget for a form field."""

    value_changed = pyqtSignal(object, object)  # field, new_value

    def __init__(self, field: FormField, parent=None):
        super().__init__(parent)
        self.field = field
        self._setup_ui()

    def _setup_ui(self):
        """Override in subclasses."""
        pass

    def get_value(self) -> Any:
        """Get the current value."""
        return None

    def set_value(self, value: Any):
        """Set the value."""
        pass


class TextFieldWidget(FormFieldWidget):
    """Widget for text input fields."""

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)

        # Label
        label = QLabel(self.field.name or "Text Field")
        label.setStyleSheet("font-weight: 500; color: #1C1C1E;")
        layout.addWidget(label)

        # Input
        self._input = QLineEdit()
        self._input.setText(str(self.field.value or ""))
        self._input.textChanged.connect(self._on_changed)
        layout.addWidget(self._input)

    def _on_changed(self, text: str):
        self.value_changed.emit(self.field, text)

    def get_value(self) -> str:
        return self._input.text()

    def set_value(self, value: Any):
        self._input.setText(str(value or ""))


class TextAreaWidget(FormFieldWidget):
    """Widget for multi-line text fields."""

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)

        label = QLabel(self.field.name or "Text Area")
        label.setStyleSheet("font-weight: 500; color: #1C1C1E;")
        layout.addWidget(label)

        self._input = QTextEdit()
        self._input.setPlainText(str(self.field.value or ""))
        self._input.setMaximumHeight(100)
        self._input.textChanged.connect(self._on_changed)
        layout.addWidget(self._input)

    def _on_changed(self):
        self.value_changed.emit(self.field, self._input.toPlainText())

    def get_value(self) -> str:
        return self._input.toPlainText()

    def set_value(self, value: Any):
        self._input.setPlainText(str(value or ""))


class CheckboxWidget(FormFieldWidget):
    """Widget for checkbox fields."""

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)

        self._checkbox = QCheckBox(self.field.name or "Checkbox")
        self._checkbox.setChecked(bool(self.field.value))
        self._checkbox.stateChanged.connect(self._on_changed)
        layout.addWidget(self._checkbox)
        layout.addStretch()

    def _on_changed(self, state: int):
        checked = state == Qt.CheckState.Checked.value
        self.value_changed.emit(self.field, checked)

    def get_value(self) -> bool:
        return self._checkbox.isChecked()

    def set_value(self, value: Any):
        self._checkbox.setChecked(bool(value))


class ComboBoxWidget(FormFieldWidget):
    """Widget for dropdown/choice fields."""

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)

        label = QLabel(self.field.name or "Selection")
        label.setStyleSheet("font-weight: 500; color: #1C1C1E;")
        layout.addWidget(label)

        self._combo = QComboBox()
        # Add options if available
        # For now, add the current value
        if self.field.value:
            self._combo.addItem(str(self.field.value))
        self._combo.currentTextChanged.connect(self._on_changed)
        layout.addWidget(self._combo)

    def _on_changed(self, text: str):
        self.value_changed.emit(self.field, text)

    def get_value(self) -> str:
        return self._combo.currentText()

    def set_value(self, value: Any):
        index = self._combo.findText(str(value))
        if index >= 0:
            self._combo.setCurrentIndex(index)


class FormPanel(QWidget):
    """Panel showing all form fields in a document."""

    field_changed = pyqtSignal(object, object)  # field, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self._form_handler = None
        self._field_widgets: list[FormFieldWidget] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header = QLabel("Form Fields")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #1C1C1E;
            padding: 4px 0;
        """)
        layout.addWidget(header)

        # Scroll area for fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self._fields_container = QWidget()
        self._fields_layout = QVBoxLayout(self._fields_container)
        self._fields_layout.setContentsMargins(0, 0, 0, 0)
        self._fields_layout.setSpacing(8)
        self._fields_layout.addStretch()

        scroll.setWidget(self._fields_container)
        layout.addWidget(scroll)

        # No fields message
        self._empty_label = QLabel("No form fields found")
        self._empty_label.setStyleSheet("color: #8E8E93; font-style: italic;")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label)

        # Buttons
        btn_layout = QHBoxLayout()

        self._save_btn = QPushButton("Save Form Data")
        self._save_btn.clicked.connect(self._save_form)
        self._save_btn.hide()
        btn_layout.addWidget(self._save_btn)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.clicked.connect(self._reset_form)
        self._reset_btn.hide()
        btn_layout.addWidget(self._reset_btn)

        layout.addLayout(btn_layout)

        self.setMinimumWidth(250)
        self.setMaximumWidth(350)

    def set_form_handler(self, handler: FormHandler):
        """Set the form handler and load fields."""
        self._form_handler = handler
        self._load_fields()

    def _load_fields(self):
        """Load form fields from the handler."""
        # Clear existing widgets
        for widget in self._field_widgets:
            widget.deleteLater()
        self._field_widgets.clear()

        if not self._form_handler:
            self._show_empty()
            return

        fields = self._form_handler.get_all_fields()
        if not fields:
            self._show_empty()
            return

        self._empty_label.hide()
        self._save_btn.show()
        self._reset_btn.show()

        # Create widgets for each field
        for field in fields:
            widget = self._create_field_widget(field)
            if widget:
                widget.value_changed.connect(self._on_field_changed)
                # Insert before the stretch
                self._fields_layout.insertWidget(
                    self._fields_layout.count() - 1,
                    widget
                )
                self._field_widgets.append(widget)

        log.info(f"Loaded {len(fields)} form fields")

    def _create_field_widget(self, field: FormField) -> FormFieldWidget:
        """Create appropriate widget for field type."""
        # Field types: 0=unknown, 1=pushbutton, 2=checkbox, 3=radiobutton,
        #              4=text, 5=listbox, 6=combobox, 7=signature

        if field.field_type == 2:  # Checkbox
            return CheckboxWidget(field)
        elif field.field_type == 3:  # Radio
            return CheckboxWidget(field)  # Treat as checkbox for now
        elif field.field_type in (5, 6):  # List/Combo
            return ComboBoxWidget(field)
        else:  # Default to text
            return TextFieldWidget(field)

    def _show_empty(self):
        """Show empty state."""
        self._empty_label.show()
        self._save_btn.hide()
        self._reset_btn.hide()

    def _on_field_changed(self, field: FormField, value: Any):
        """Handle field value change."""
        if self._form_handler:
            self._form_handler.set_field_value(field, value)
        self.field_changed.emit(field, value)

    def _save_form(self):
        """Save all form data."""
        for widget in self._field_widgets:
            value = widget.get_value()
            if self._form_handler:
                self._form_handler.set_field_value(widget.field, value)
        log.info("Form data saved")

    def _reset_form(self):
        """Reset form to original values."""
        self._load_fields()

    def refresh(self):
        """Refresh the form fields."""
        self._load_fields()
