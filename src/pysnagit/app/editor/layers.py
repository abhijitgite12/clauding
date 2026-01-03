"""Layer management and undo/redo system."""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QGraphicsItem
from copy import deepcopy


class UndoStack:
    """Simple undo/redo stack for editor actions."""

    def __init__(self, max_size: int = 50):
        self._stack = []
        self._index = -1
        self._max_size = max_size

    def push(self, action: dict):
        """Push a new action onto the stack."""
        # Remove any actions after current index
        self._stack = self._stack[:self._index + 1]

        # Add new action
        self._stack.append(action)

        # Trim if too large
        if len(self._stack) > self._max_size:
            self._stack.pop(0)
        else:
            self._index = len(self._stack) - 1

    def undo(self) -> dict | None:
        """Get the action to undo."""
        if self._index >= 0:
            action = self._stack[self._index]
            self._index -= 1
            return action
        return None

    def redo(self) -> dict | None:
        """Get the action to redo."""
        if self._index < len(self._stack) - 1:
            self._index += 1
            return self._stack[self._index]
        return None

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._index >= 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._index < len(self._stack) - 1

    def clear(self):
        """Clear the stack."""
        self._stack.clear()
        self._index = -1


class LayerManager(QObject):
    """Manages annotation layers with undo/redo support."""

    layers_changed = pyqtSignal()
    can_undo_changed = pyqtSignal(bool)
    can_redo_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layers = []
        self._undo_stack = UndoStack()

    def add_layer(self, item: QGraphicsItem, record_undo: bool = True):
        """Add an annotation layer."""
        self._layers.append(item)

        if record_undo:
            self._undo_stack.push({
                'type': 'add',
                'item': item
            })
            self._emit_undo_signals()

        self.layers_changed.emit()

    def remove_layer(self, item: QGraphicsItem, record_undo: bool = True):
        """Remove an annotation layer."""
        if item in self._layers:
            index = self._layers.index(item)
            self._layers.remove(item)

            if record_undo:
                self._undo_stack.push({
                    'type': 'remove',
                    'item': item,
                    'index': index
                })
                self._emit_undo_signals()

            self.layers_changed.emit()

    def clear_layers(self, record_undo: bool = True):
        """Clear all layers."""
        if not self._layers:
            return

        if record_undo:
            self._undo_stack.push({
                'type': 'clear',
                'items': self._layers.copy()
            })
            self._emit_undo_signals()

        self._layers.clear()
        self.layers_changed.emit()

    def get_layers(self) -> list:
        """Get all layers."""
        return self._layers.copy()

    def undo(self, canvas) -> bool:
        """Undo the last action."""
        action = self._undo_stack.undo()
        if not action:
            return False

        if action['type'] == 'add':
            # Undo add = remove
            item = action['item']
            if item in self._layers:
                self._layers.remove(item)
                canvas.remove_annotation(item)

        elif action['type'] == 'remove':
            # Undo remove = add back
            item = action['item']
            index = action.get('index', len(self._layers))
            self._layers.insert(index, item)
            canvas.add_annotation(item)

        elif action['type'] == 'clear':
            # Undo clear = restore all
            for item in action['items']:
                self._layers.append(item)
                canvas.add_annotation(item)

        self._emit_undo_signals()
        self.layers_changed.emit()
        return True

    def redo(self, canvas) -> bool:
        """Redo the last undone action."""
        action = self._undo_stack.redo()
        if not action:
            return False

        if action['type'] == 'add':
            # Redo add = add again
            item = action['item']
            self._layers.append(item)
            canvas.add_annotation(item)

        elif action['type'] == 'remove':
            # Redo remove = remove again
            item = action['item']
            if item in self._layers:
                self._layers.remove(item)
                canvas.remove_annotation(item)

        elif action['type'] == 'clear':
            # Redo clear = clear again
            for item in self._layers.copy():
                self._layers.remove(item)
                canvas.remove_annotation(item)

        self._emit_undo_signals()
        self.layers_changed.emit()
        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._undo_stack.can_undo()

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._undo_stack.can_redo()

    def _emit_undo_signals(self):
        """Emit undo/redo availability signals."""
        self.can_undo_changed.emit(self.can_undo())
        self.can_redo_changed.emit(self.can_redo())
