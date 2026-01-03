"""Animation utilities for PySnagit - macOS Big Sur+ smooth transitions."""

from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint, QRect,
    QAbstractAnimation, QParallelAnimationGroup, Qt, QTimer
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget
from PyQt6.QtGui import QColor


class AnimationManager:
    """Centralized animation system for smooth UI transitions."""

    # Animation durations (milliseconds)
    DURATION_QUICK = 150      # Quick interactions (hover, press)
    DURATION_NORMAL = 200     # Standard transitions
    DURATION_MEDIUM = 250     # Slides, longer transitions
    DURATION_SLOW = 300       # Window opens, complex animations

    # Easing curves for natural motion
    EASING_OUT = QEasingCurve.Type.OutCubic
    EASING_IN_OUT = QEasingCurve.Type.InOutQuad
    EASING_SPRING = QEasingCurve.Type.OutBack

    @staticmethod
    def fade_in(widget: QWidget, duration: int = None, on_finished=None) -> QPropertyAnimation:
        """
        Fade widget in from transparent to opaque.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms (default: DURATION_NORMAL)
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        if duration is None:
            duration = AnimationManager.DURATION_NORMAL

        # Create or get existing opacity effect
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        # Create animation
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(AnimationManager.EASING_OUT)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return animation

    @staticmethod
    def fade_out(widget: QWidget, duration: int = None, on_finished=None) -> QPropertyAnimation:
        """
        Fade widget out from opaque to transparent.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms (default: DURATION_NORMAL)
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        if duration is None:
            duration = AnimationManager.DURATION_NORMAL

        # Create or get existing opacity effect
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        # Create animation
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(AnimationManager.EASING_OUT)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return animation

    @staticmethod
    def slide_in(widget: QWidget, direction: str = "left", duration: int = None,
                 distance: int = 50, on_finished=None) -> QPropertyAnimation:
        """
        Slide widget in from specified direction.

        Args:
            widget: Widget to animate
            direction: "left", "right", "up", or "down"
            duration: Animation duration in ms (default: DURATION_MEDIUM)
            distance: Pixels to slide (default: 50)
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        if duration is None:
            duration = AnimationManager.DURATION_MEDIUM

        # Get current position
        current_pos = widget.pos()

        # Calculate start position based on direction
        start_pos = QPoint(current_pos)
        if direction == "left":
            start_pos.setX(current_pos.x() - distance)
        elif direction == "right":
            start_pos.setX(current_pos.x() + distance)
        elif direction == "up":
            start_pos.setY(current_pos.y() - distance)
        elif direction == "down":
            start_pos.setY(current_pos.y() + distance)

        # Create animation
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(AnimationManager.EASING_OUT)

        if on_finished:
            animation.finished.connect(on_finished)

        # Note: NOT adding parallel fade_in() - causes opacity effect conflicts

        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return animation

    @staticmethod
    def slide_out(widget: QWidget, direction: str = "right", duration: int = None,
                  distance: int = 50, on_finished=None) -> QPropertyAnimation:
        """
        Slide widget out in specified direction.

        Args:
            widget: Widget to animate
            direction: "left", "right", "up", or "down"
            duration: Animation duration in ms (default: DURATION_MEDIUM)
            distance: Pixels to slide (default: 50)
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        if duration is None:
            duration = AnimationManager.DURATION_MEDIUM

        # Get current position
        current_pos = widget.pos()

        # Calculate end position based on direction
        end_pos = QPoint(current_pos)
        if direction == "left":
            end_pos.setX(current_pos.x() - distance)
        elif direction == "right":
            end_pos.setX(current_pos.x() + distance)
        elif direction == "up":
            end_pos.setY(current_pos.y() - distance)
        elif direction == "down":
            end_pos.setY(current_pos.y() + distance)

        # Create animation
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(current_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(AnimationManager.EASING_IN_OUT)

        if on_finished:
            animation.finished.connect(on_finished)

        # Note: NOT adding parallel fade_out() - causes opacity effect conflicts

        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return animation

    @staticmethod
    def scale_in(widget: QWidget, duration: int = None, from_scale: float = 0.9,
                 on_finished=None) -> QPropertyAnimation:
        """
        Fade widget in (scale removed to prevent font rendering issues).

        Note: Geometry-based scaling causes Qt font point size calculation errors.
        Using opacity-only animation for compatibility.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms (default: DURATION_MEDIUM)
            from_scale: Ignored (kept for API compatibility)
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        if duration is None:
            duration = AnimationManager.DURATION_MEDIUM

        # Just use fade-in for safety (no geometry changes)
        return AnimationManager.fade_in(widget, duration, on_finished)

    @staticmethod
    def scale_out(widget: QWidget, duration: int = None, to_scale: float = 0.9,
                  on_finished=None) -> QPropertyAnimation:
        """
        Fade widget out (scale removed to prevent font rendering issues).

        Note: Geometry-based scaling causes Qt font point size calculation errors.
        Using opacity-only animation for compatibility.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms (default: DURATION_NORMAL)
            to_scale: Ignored (kept for API compatibility)
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        if duration is None:
            duration = AnimationManager.DURATION_NORMAL

        # Just use fade-out for safety (no geometry changes)
        return AnimationManager.fade_out(widget, duration, on_finished)

    @staticmethod
    def button_press_animation(widget: QWidget, scale_to: float = 0.95) -> None:
        """
        Subtle opacity feedback for button press (scale removed).

        Note: Geometry-based scaling causes Qt font issues.
        Use CSS :pressed state instead for visual feedback.

        Args:
            widget: Widget to animate
            scale_to: Ignored (kept for API compatibility)
        """
        # Quick opacity pulse for subtle feedback
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        # Quick dim and restore
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(100)
        animation.setStartValue(1.0)
        animation.setKeyValueAt(0.5, 0.7)
        animation.setEndValue(1.0)
        animation.setEasingCurve(AnimationManager.EASING_IN_OUT)
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    @staticmethod
    def pulse_animation(widget: QWidget, count: int = 1, scale_to: float = 1.05) -> None:
        """
        Pulse animation using opacity (scale removed to prevent font issues).

        Note: Geometry-based scaling causes Qt font point size calculation errors.
        Using opacity pulse for subtle feedback instead.

        Args:
            widget: Widget to animate
            count: Number of pulses (default: 1)
            scale_to: Ignored (kept for API compatibility)
        """
        def create_pulse():
            # Create or get existing opacity effect
            effect = widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)

            # Pulse animation: fade to 70% then back to 100%
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(AnimationManager.DURATION_QUICK * 2)
            animation.setStartValue(1.0)
            animation.setKeyValueAt(0.5, 0.7)
            animation.setEndValue(1.0)
            animation.setEasingCurve(AnimationManager.EASING_IN_OUT)
            animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        # Create pulses with delay
        for i in range(count):
            QTimer.singleShot(i * (AnimationManager.DURATION_QUICK * 2 + 100), create_pulse)
