"""Professional Snagit-inspired styling for PySnagit."""

# Snagit-inspired color palette (similar to TechSmith's design language)
COLORS = {
    # Primary brand colors
    "primary": "#0066CC",           # Snagit blue
    "primary_hover": "#0077EE",
    "primary_dark": "#004499",
    "primary_light": "#E6F2FF",

    # Accent colors
    "accent": "#FF6B00",            # Orange accent
    "accent_hover": "#FF8533",
    "success": "#28A745",
    "secondary": "#28A745",         # Alias for success
    "danger": "#DC3545",
    "danger_hover": "#E04555",
    "warning": "#FFC107",

    # Light theme backgrounds
    "bg_main": "#F5F5F5",
    "bg_white": "#FFFFFF",
    "bg_card": "#FFFFFF",
    "bg_toolbar": "#FAFAFA",
    "bg_hover": "#E8E8E8",
    "bg_selected": "#E6F2FF",
    "bg_sidebar": "#2D2D2D",
    "bg_elevated": "#FAFAFA",       # For toolbars
    "bg_dark": "#2D2D2D",           # Dark backgrounds

    # Text colors
    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "text_muted": "#999999",
    "text_light": "#FFFFFF",

    # Borders
    "border": "#D0D0D0",
    "border_light": "#E5E5E5",
    "border_dark": "#B0B0B0",

    # Shadows
    "shadow": "rgba(0, 0, 0, 0.1)",
}

# macOS Big Sur+ Color Palette - Soft, modern colors with pastels
MACOS_COLORS = {
    # Primary colors (softer than original)
    "primary": "#007AFF",           # iOS blue (softer)
    "primary_hover": "#0051D5",
    "primary_dark": "#003D99",
    "primary_light": "#CCE5FF",
    "primary_ultra_light": "#E5F2FF",

    # Accent colors (pastel-ified)
    "accent_red": "#FF6B6B",
    "accent_orange": "#FFB84D",
    "accent_yellow": "#FFE066",
    "accent_green": "#51CF66",
    "accent_purple": "#A78BFA",
    "accent_pink": "#FF8FCF",

    # Backgrounds with blur simulation
    "bg_main": "#F5F5F7",           # Lighter, more iOS-like
    "bg_white": "#FFFFFF",
    "bg_card": "#FFFFFF",
    "bg_elevated": "#FAFAFA",
    "bg_translucent": "rgba(255, 255, 255, 0.7)",  # For blur panels
    "bg_translucent_dark": "rgba(40, 40, 43, 0.8)",
    "bg_hover": "#F0F0F2",
    "bg_selected": "#E5F2FF",

    # Soft shadows (Big Sur style)
    "shadow_soft": "rgba(0, 0, 0, 0.05)",
    "shadow_medium": "rgba(0, 0, 0, 0.08)",
    "shadow_strong": "rgba(0, 0, 0, 0.12)",
    "shadow_floating": "rgba(0, 0, 0, 0.15)",

    # Minimal borders
    "border": "#E5E5E7",
    "border_light": "#F0F0F2",
    "border_dark": "#D1D1D6",

    # Text (softer blacks)
    "text_primary": "#1C1C1E",
    "text_secondary": "#8E8E93",
    "text_tertiary": "#C7C7CC",
    "text_light": "#FFFFFF",

    # Status colors
    "success": "#51CF66",
    "danger": "#FF6B6B",
    "warning": "#FFE066",
    "info": "#007AFF",
}

# Border radius values for macOS Big Sur+ style
MACOS_RADIUS = {
    "small": "8px",
    "medium": "12px",
    "large": "16px",
    "xlarge": "20px",
    "pill": "999px",
}

SNAGIT_THEME = f"""
/* ========== MAIN WINDOW ========== */
QMainWindow {{
    background-color: {COLORS['bg_main']};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}}

/* ========== MENU BAR ========== */
QMenuBar {{
    background-color: {COLORS['bg_white']};
    border-bottom: 1px solid {COLORS['border_light']};
    padding: 2px 8px;
    font-size: 13px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 2px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

QMenu {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 6px;
}}

QMenu::item {{
    padding: 10px 40px 10px 16px;
    border-radius: 4px;
    margin: 2px 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_light']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border_light']};
    margin: 6px 12px;
}}

/* ========== BUTTONS ========== */
QPushButton {{
    background-color: {COLORS['bg_white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['border_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['border']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_muted']};
    border-color: {COLORS['border_light']};
}}

/* Primary Button Style */
QPushButton[class="primary"], QPushButton#primaryButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_light']};
    border: none;
    font-weight: 600;
}}

QPushButton[class="primary"]:hover, QPushButton#primaryButton:hover {{
    background-color: {COLORS['primary_hover']};
}}

/* Danger Button Style */
QPushButton[class="danger"] {{
    background-color: {COLORS['danger']};
    color: {COLORS['text_light']};
    border: none;
}}

QPushButton[class="danger"]:hover {{
    background-color: {COLORS['danger_hover']};
}}

/* ========== TOOL BUTTONS ========== */
QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    color: {COLORS['text_primary']};
    font-weight: 500;
    font-size: 13px;
}}

QToolButton:hover {{
    background-color: {COLORS['bg_hover']};
}}

QToolButton:pressed {{
    background-color: {COLORS['border']};
}}

QToolButton:checked {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_light']};
}}

/* ========== TOOLBARS ========== */
QToolBar {{
    background-color: {COLORS['bg_white']};
    border-bottom: 1px solid {COLORS['border_light']};
    padding: 6px 12px;
    spacing: 6px;
}}

QToolBar::separator {{
    background-color: {COLORS['border']};
    width: 1px;
    margin: 6px 8px;
}}

/* ========== LABELS ========== */
QLabel {{
    background-color: transparent;
    color: {COLORS['text_primary']};
}}

/* ========== INPUT FIELDS ========== */
QLineEdit {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 14px;
    color: {COLORS['text_primary']};
    font-size: 13px;
    selection-background-color: {COLORS['primary']};
}}

QLineEdit:focus {{
    border-color: {COLORS['primary']};
    border-width: 2px;
    padding: 9px 13px;
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_muted']};
}}

/* ========== SPIN BOX ========== */
QSpinBox {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
}}

QSpinBox:focus {{
    border-color: {COLORS['primary']};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {COLORS['bg_main']};
    border: none;
    width: 24px;
    border-radius: 4px;
    margin: 2px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLORS['bg_hover']};
}}

/* ========== COMBO BOX ========== */
QComboBox {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 14px;
    padding-right: 30px;
    color: {COLORS['text_primary']};
    min-width: 140px;
}}

QComboBox:hover {{
    border-color: {COLORS['border_dark']};
}}

QComboBox:focus {{
    border-color: {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 12px;
}}

QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 6px;
    selection-background-color: {COLORS['primary']};
    selection-color: {COLORS['text_light']};
}}

/* ========== CHECK BOX ========== */
QCheckBox {{
    spacing: 10px;
    color: {COLORS['text_primary']};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['bg_white']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

/* ========== SCROLL BARS ========== */
QScrollBar:vertical {{
    background-color: {COLORS['bg_main']};
    width: 14px;
    border-radius: 7px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 5px;
    min-height: 40px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['border_dark']};
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_main']};
    height: 14px;
    border-radius: 7px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border']};
    border-radius: 5px;
    min-width: 40px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['border_dark']};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    width: 0;
    height: 0;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

/* ========== TAB WIDGET ========== */
QTabWidget::pane {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
    padding: 16px;
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 12px 24px;
    margin-right: 4px;
    border-bottom: 3px solid transparent;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    color: {COLORS['primary']};
    border-bottom-color: {COLORS['primary']};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['text_primary']};
    background-color: {COLORS['bg_hover']};
}}

/* ========== GROUP BOX ========== */
QGroupBox {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
    margin-top: 20px;
    padding: 20px;
    font-weight: 600;
}}

QGroupBox::title {{
    color: {COLORS['text_primary']};
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    background-color: {COLORS['bg_white']};
}}

/* ========== STATUS BAR ========== */
QStatusBar {{
    background-color: {COLORS['bg_white']};
    border-top: 1px solid {COLORS['border_light']};
    color: {COLORS['text_secondary']};
    padding: 6px 16px;
    font-size: 12px;
}}

/* ========== PROGRESS BAR ========== */
QProgressBar {{
    background-color: {COLORS['bg_main']};
    border: none;
    border-radius: 6px;
    height: 10px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 6px;
}}

/* ========== DIALOG ========== */
QDialog {{
    background-color: {COLORS['bg_main']};
}}

QMessageBox {{
    background-color: {COLORS['bg_white']};
}}

QMessageBox QLabel {{
    color: {COLORS['text_primary']};
}}

/* ========== GRAPHICS VIEW (Editor Canvas) ========== */
QGraphicsView {{
    background-color: #404040;
    border: none;
}}

/* ========== TOOLTIPS ========== */
QToolTip {{
    background-color: {COLORS['bg_sidebar']};
    color: {COLORS['text_light']};
    border: none;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 12px;
}}

/* ========== FRAMES ========== */
QFrame {{
    background-color: transparent;
}}

QFrame#cardFrame {{
    background-color: {COLORS['bg_white']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 12px;
}}
"""

# Keep dark theme as an option
DARK_THEME = SNAGIT_THEME  # Use Snagit theme as default

# macOS Big Sur+ Theme - Modern, soft design with larger radii and translucent elements
MACOS_BIGSUR_THEME = f"""
/* ========== MAIN WINDOW ========== */
QMainWindow {{
    background-color: {MACOS_COLORS['bg_main']};
}}

QWidget {{
    background-color: transparent;
    color: {MACOS_COLORS['text_primary']};
    font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
    font-size: 13px;
}}

/* ========== MENU BAR ========== */
QMenuBar {{
    background-color: {MACOS_COLORS['bg_white']};
    border-bottom: 1px solid {MACOS_COLORS['border_light']};
    padding: 2px 8px;
    font-size: 13px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 12px;
    border-radius: {MACOS_RADIUS['small']};
    margin: 2px;
}}

QMenuBar::item:selected {{
    background-color: {MACOS_COLORS['bg_hover']};
}}

QMenu {{
    background-color: {MACOS_COLORS['bg_white']};
    border: none;
    border-radius: {MACOS_RADIUS['medium']};
    padding: 8px;
}}

QMenu::item {{
    padding: 10px 40px 10px 16px;
    border-radius: {MACOS_RADIUS['small']};
    margin: 2px 4px;
}}

QMenu::item:selected {{
    background-color: {MACOS_COLORS['primary']};
    color: {MACOS_COLORS['text_light']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {MACOS_COLORS['border_light']};
    margin: 8px 12px;
}}

/* ========== BUTTONS ========== */
QPushButton {{
    background-color: {MACOS_COLORS['bg_white']};
    color: {MACOS_COLORS['text_primary']};
    border: 1px solid {MACOS_COLORS['border']};
    border-radius: {MACOS_RADIUS['medium']};
    padding: 10px 20px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {MACOS_COLORS['bg_hover']};
    border-color: {MACOS_COLORS['border_dark']};
}}

QPushButton:pressed {{
    background-color: {MACOS_COLORS['border']};
}}

QPushButton:disabled {{
    background-color: {MACOS_COLORS['bg_main']};
    color: {MACOS_COLORS['text_tertiary']};
    border-color: {MACOS_COLORS['border_light']};
}}

/* Primary Button Style */
QPushButton[class="primary"], QPushButton#primaryButton {{
    background-color: {MACOS_COLORS['primary']};
    color: {MACOS_COLORS['text_light']};
    border: none;
    font-weight: 600;
}}

QPushButton[class="primary"]:hover, QPushButton#primaryButton:hover {{
    background-color: {MACOS_COLORS['primary_hover']};
}}

/* Danger Button Style */
QPushButton[class="danger"] {{
    background-color: {MACOS_COLORS['danger']};
    color: {MACOS_COLORS['text_light']};
    border: none;
}}

QPushButton[class="danger"]:hover {{
    background-color: #FF5555;
}}

/* ========== TOOL BUTTONS ========== */
QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: {MACOS_RADIUS['pill']};
    padding: 8px 14px;
    color: {MACOS_COLORS['text_primary']};
    font-weight: 500;
    font-size: 13px;
}}

QToolButton:hover {{
    background-color: {MACOS_COLORS['bg_hover']};
}}

QToolButton:pressed {{
    background-color: {MACOS_COLORS['border']};
}}

QToolButton:checked {{
    background-color: {MACOS_COLORS['primary_light']};
    color: {MACOS_COLORS['primary']};
}}

/* ========== TOOLBARS ========== */
QToolBar {{
    background-color: {MACOS_COLORS['bg_white']};
    border-bottom: 1px solid {MACOS_COLORS['border_light']};
    padding: 8px 12px;
    spacing: 8px;
}}

QToolBar::separator {{
    background-color: {MACOS_COLORS['border_light']};
    width: 1px;
    margin: 8px;
}}

/* ========== LABELS ========== */
QLabel {{
    background-color: transparent;
    color: {MACOS_COLORS['text_primary']};
}}

/* ========== INPUT FIELDS ========== */
QLineEdit {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 1px solid {MACOS_COLORS['border']};
    border-radius: {MACOS_RADIUS['medium']};
    padding: 10px 14px;
    color: {MACOS_COLORS['text_primary']};
    font-size: 13px;
    selection-background-color: {MACOS_COLORS['primary']};
}}

QLineEdit:focus {{
    border-color: {MACOS_COLORS['primary']};
    border-width: 2px;
    padding: 9px 13px;
}}

QLineEdit:disabled {{
    background-color: {MACOS_COLORS['bg_main']};
    color: {MACOS_COLORS['text_tertiary']};
}}

/* ========== SPIN BOX ========== */
QSpinBox {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 1px solid {MACOS_COLORS['border']};
    border-radius: {MACOS_RADIUS['medium']};
    padding: 8px 12px;
    color: {MACOS_COLORS['text_primary']};
}}

QSpinBox:focus {{
    border-color: {MACOS_COLORS['primary']};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {MACOS_COLORS['bg_main']};
    border: none;
    width: 24px;
    border-radius: {MACOS_RADIUS['small']};
    margin: 2px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {MACOS_COLORS['bg_hover']};
}}

/* ========== COMBO BOX ========== */
QComboBox {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 1px solid {MACOS_COLORS['border']};
    border-radius: {MACOS_RADIUS['medium']};
    padding: 10px 14px;
    padding-right: 30px;
    color: {MACOS_COLORS['text_primary']};
    min-width: 140px;
}}

QComboBox:hover {{
    border-color: {MACOS_COLORS['border_dark']};
}}

QComboBox:focus {{
    border-color: {MACOS_COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {MACOS_COLORS['bg_white']};
    border: none;
    border-radius: {MACOS_RADIUS['medium']};
    padding: 6px;
    selection-background-color: {MACOS_COLORS['primary']};
    selection-color: {MACOS_COLORS['text_light']};
}}

/* ========== CHECK BOX ========== */
QCheckBox {{
    spacing: 10px;
    color: {MACOS_COLORS['text_primary']};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: {MACOS_RADIUS['small']};
    border: 2px solid {MACOS_COLORS['border']};
    background-color: {MACOS_COLORS['bg_white']};
}}

QCheckBox::indicator:hover {{
    border-color: {MACOS_COLORS['primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {MACOS_COLORS['primary']};
    border-color: {MACOS_COLORS['primary']};
}}

/* ========== SCROLL BARS ========== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 12px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {MACOS_COLORS['border']};
    border-radius: 6px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {MACOS_COLORS['border_dark']};
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 12px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {MACOS_COLORS['border']};
    border-radius: 6px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {MACOS_COLORS['border_dark']};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    width: 0;
    height: 0;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

/* ========== TAB WIDGET ========== */
QTabWidget::pane {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 1px solid {MACOS_COLORS['border_light']};
    border-radius: {MACOS_RADIUS['large']};
    padding: 16px;
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {MACOS_COLORS['text_secondary']};
    padding: 12px 24px;
    margin-right: 4px;
    border-bottom: 3px solid transparent;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    color: {MACOS_COLORS['primary']};
    border-bottom-color: {MACOS_COLORS['primary']};
}}

QTabBar::tab:hover:!selected {{
    color: {MACOS_COLORS['text_primary']};
    background-color: {MACOS_COLORS['bg_hover']};
}}

/* ========== GROUP BOX ========== */
QGroupBox {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 1px solid {MACOS_COLORS['border_light']};
    border-radius: {MACOS_RADIUS['large']};
    margin-top: 20px;
    padding: 20px;
    font-weight: 600;
}}

QGroupBox::title {{
    color: {MACOS_COLORS['text_primary']};
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    background-color: {MACOS_COLORS['bg_white']};
}}

/* ========== STATUS BAR ========== */
QStatusBar {{
    background-color: {MACOS_COLORS['bg_white']};
    border-top: 1px solid {MACOS_COLORS['border_light']};
    color: {MACOS_COLORS['text_secondary']};
    padding: 8px 16px;
    font-size: 12px;
}}

/* ========== PROGRESS BAR ========== */
QProgressBar {{
    background-color: {MACOS_COLORS['bg_main']};
    border: none;
    border-radius: {MACOS_RADIUS['pill']};
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {MACOS_COLORS['primary']};
    border-radius: {MACOS_RADIUS['pill']};
}}

/* ========== DIALOG ========== */
QDialog {{
    background-color: {MACOS_COLORS['bg_main']};
}}

QMessageBox {{
    background-color: {MACOS_COLORS['bg_white']};
}}

QMessageBox QLabel {{
    color: {MACOS_COLORS['text_primary']};
}}

/* ========== GRAPHICS VIEW (Editor Canvas) ========== */
QGraphicsView {{
    background-color: #484848;
    border: none;
}}

/* ========== TOOLTIPS ========== */
QToolTip {{
    background-color: {MACOS_COLORS['bg_translucent_dark']};
    color: {MACOS_COLORS['text_light']};
    border: none;
    border-radius: {MACOS_RADIUS['small']};
    padding: 10px 14px;
    font-size: 12px;
}}

/* ========== FRAMES ========== */
QFrame {{
    background-color: transparent;
}}

QFrame#cardFrame {{
    background-color: {MACOS_COLORS['bg_white']};
    border: none;
    border-radius: {MACOS_RADIUS['xlarge']};
}}
"""

# Icon mappings
ICONS = {
    "full_screen": "",
    "region": "",
    "window": "",
    "scrolling": "",
    "video": "",
    "gif": "",
    "copy": "",
    "save": "",
    "settings": "",
}
