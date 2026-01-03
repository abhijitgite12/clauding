"""Animated button widget with smooth hover and press animations."""

from PyQt6.QtWidgets import QPushButton, QToolButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QRect, pyqtProperty
from PyQt6.QtGui import QCursor


class AnimatedButton(QPushButton):
    """QPushButton with smooth hover and press animations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hover_animation = None
        self._press_animation = None
        self._original_geometry = None
        self._is_animating = False

        # Enable mouse tracking for smooth hover effects
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def enterEvent(self, event):
        """Animate button on hover - scale to 1.02."""
        super().enterEvent(event)
        if not self._is_animating:
            self._animate_scale(1.02, duration=150)

    def leaveEvent(self, event):
        """Return button to normal size."""
        super().leaveEvent(event)
        if not self._is_animating:
            self._animate_scale(1.0, duration=150)

    def mousePressEvent(self, event):
        """Quick scale-down animation on press."""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_scale(0.97, duration=100)

    def mouseReleaseEvent(self, event):
        """Return to hover state on release."""
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            # Return to hover scale if mouse still over button
            if self.rect().contains(event.pos()):
                self._animate_scale(1.02, duration=100)
            else:
                self._animate_scale(1.0, duration=100)

    def _animate_scale(self, scale_factor: float, duration: int = 150):
        """
        Animate button scaling.

        Args:
            scale_factor: Target scale (1.0 = normal, 1.02 = slightly larger)
            duration: Animation duration in milliseconds
        """
        if self._hover_animation:
            self._hover_animation.stop()

        # Store original geometry on first animation
        if not self._original_geometry:
            self._original_geometry = self.geometry()

        # Calculate target geometry
        original = self._original_geometry
        center_x = original.center().x()
        center_y = original.center().y()

        target_width = int(original.width() * scale_factor)
        target_height = int(original.height() * scale_factor)
        target_x = center_x - target_width // 2
        target_y = center_y - target_height // 2
        target_geo = QRect(target_x, target_y, target_width, target_height)

        # Create animation
        self._hover_animation = QPropertyAnimation(self, b"geometry")
        self._hover_animation.setDuration(duration)
        self._hover_animation.setStartValue(self.geometry())
        self._hover_animation.setEndValue(target_geo)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_finished():
            self._is_animating = False

        self._hover_animation.finished.connect(on_finished)
        self._is_animating = True
        self._hover_animation.start()


class AnimatedToolButton(QToolButton):
    """QToolButton with smooth hover and press animations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hover_animation = None
        self._press_animation = None
        self._original_geometry = None
        self._is_animating = False

        # Enable mouse tracking for smooth hover effects
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def enterEvent(self, event):
        """Animate button on hover - scale to 1.05."""
        super().enterEvent(event)
        if not self._is_animating and not self.isCheckable():
            self._animate_scale(1.05, duration=150)

    def leaveEvent(self, event):
        """Return button to normal size."""
        super().leaveEvent(event)
        if not self._is_animating and not self.isCheckable():
            self._animate_scale(1.0, duration=150)

    def mousePressEvent(self, event):
        """Quick scale-down animation on press."""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_scale(0.95, duration=100)

    def mouseReleaseEvent(self, event):
        """Return to hover state on release."""
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            # Return to hover scale if mouse still over button and not checkable
            if self.rect().contains(event.pos()) and not self.isCheckable():
                self._animate_scale(1.05, duration=100)
            else:
                self._animate_scale(1.0, duration=100)

    def _animate_scale(self, scale_factor: float, duration: int = 150):
        """
        Animate button scaling.

        Args:
            scale_factor: Target scale (1.0 = normal, 1.05 = slightly larger)
            duration: Animation duration in milliseconds
        """
        if self._hover_animation:
            self._hover_animation.stop()

        # Store original geometry on first animation
        if not self._original_geometry:
            self._original_geometry = self.geometry()

        # Calculate target geometry
        original = self._original_geometry
        center_x = original.center().x()
        center_y = original.center().y()

        target_width = int(original.width() * scale_factor)
        target_height = int(original.height() * scale_factor)
        target_x = center_x - target_width // 2
        target_y = center_y - target_height // 2
        target_geo = QRect(target_x, target_y, target_width, target_height)

        # Create animation
        self._hover_animation = QPropertyAnimation(self, b"geometry")
        self._hover_animation.setDuration(duration)
        self._hover_animation.setStartValue(self.geometry())
        self._hover_animation.setEndValue(target_geo)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_finished():
            self._is_animating = False

        self._hover_animation.finished.connect(on_finished)
        self._is_animating = True
        self._hover_animation.start()
