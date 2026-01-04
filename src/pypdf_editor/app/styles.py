"""Professional styling for PyPDF Editor - macOS Big Sur+ inspired."""

# macOS Big Sur+ Color Palette
MACOS_COLORS = {
    # Primary colors
    "primary": "#007AFF",
    "primary_hover": "#0051D5",
    "primary_dark": "#003D99",
    "primary_light": "#CCE5FF",
    "primary_ultra_light": "#E5F2FF",

    # Accent colors
    "accent_red": "#FF6B6B",
    "accent_orange": "#FFB84D",
    "accent_yellow": "#FFE066",
    "accent_green": "#51CF66",
    "accent_purple": "#A78BFA",
    "accent_pink": "#FF8FCF",

    # Backgrounds
    "bg_main": "#F5F5F7",
    "bg_white": "#FFFFFF",
    "bg_card": "#FFFFFF",
    "bg_elevated": "#FAFAFA",
    "bg_translucent": "rgba(255, 255, 255, 0.7)",
    "bg_translucent_dark": "rgba(40, 40, 43, 0.8)",
    "bg_hover": "#F0F0F2",
    "bg_selected": "#E5F2FF",
    "bg_canvas": "#5A5A5A",

    # Shadows
    "shadow_soft": "rgba(0, 0, 0, 0.05)",
    "shadow_medium": "rgba(0, 0, 0, 0.08)",
    "shadow_strong": "rgba(0, 0, 0, 0.12)",
    "shadow_floating": "rgba(0, 0, 0, 0.15)",

    # Borders
    "border": "#E5E5E7",
    "border_light": "#F0F0F2",
    "border_dark": "#D1D1D6",

    # Text
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

# PDF Highlight colors
HIGHLIGHT_COLORS = {
    "yellow": "#FFFF00",
    "green": "#90EE90",
    "blue": "#87CEEB",
    "pink": "#FFB6C1",
    "orange": "#FFA500",
    "purple": "#DDA0DD",
}

# Border radius values
MACOS_RADIUS = {
    "small": "8px",
    "medium": "12px",
    "large": "16px",
    "xlarge": "20px",
    "pill": "999px",
}

# Main theme stylesheet
THEME = f"""
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

QPushButton[class="primary"], QPushButton#primaryButton {{
    background-color: {MACOS_COLORS['primary']};
    color: {MACOS_COLORS['text_light']};
    border: none;
    font-weight: 600;
}}

QPushButton[class="primary"]:hover, QPushButton#primaryButton:hover {{
    background-color: {MACOS_COLORS['primary_hover']};
}}

/* ========== TOOL BUTTONS ========== */
QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: {MACOS_RADIUS['small']};
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

/* ========== LIST WIDGET (for thumbnails) ========== */
QListWidget {{
    background-color: {MACOS_COLORS['bg_main']};
    border: none;
    outline: none;
}}

QListWidget::item {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 2px solid transparent;
    border-radius: {MACOS_RADIUS['small']};
    margin: 4px;
    padding: 4px;
}}

QListWidget::item:selected {{
    border-color: {MACOS_COLORS['primary']};
    background-color: {MACOS_COLORS['primary_ultra_light']};
}}

QListWidget::item:hover:!selected {{
    background-color: {MACOS_COLORS['bg_hover']};
}}

/* ========== TREE WIDGET (for outline/bookmarks) ========== */
QTreeWidget {{
    background-color: {MACOS_COLORS['bg_white']};
    border: none;
    outline: none;
}}

QTreeWidget::item {{
    padding: 8px 4px;
    border-radius: {MACOS_RADIUS['small']};
}}

QTreeWidget::item:selected {{
    background-color: {MACOS_COLORS['primary']};
    color: {MACOS_COLORS['text_light']};
}}

QTreeWidget::item:hover:!selected {{
    background-color: {MACOS_COLORS['bg_hover']};
}}

/* ========== SPLITTER ========== */
QSplitter::handle {{
    background-color: {MACOS_COLORS['border_light']};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

/* ========== STATUS BAR ========== */
QStatusBar {{
    background-color: {MACOS_COLORS['bg_white']};
    border-top: 1px solid {MACOS_COLORS['border_light']};
    color: {MACOS_COLORS['text_secondary']};
    padding: 8px 16px;
    font-size: 12px;
}}

/* ========== GRAPHICS VIEW (PDF Canvas) ========== */
QGraphicsView {{
    background-color: {MACOS_COLORS['bg_canvas']};
    border: none;
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

/* ========== SPIN BOX ========== */
QSpinBox, QDoubleSpinBox {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 1px solid {MACOS_COLORS['border']};
    border-radius: {MACOS_RADIUS['small']};
    padding: 6px 10px;
    color: {MACOS_COLORS['text_primary']};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {MACOS_COLORS['primary']};
}}

/* ========== COMBO BOX ========== */
QComboBox {{
    background-color: {MACOS_COLORS['bg_white']};
    border: 1px solid {MACOS_COLORS['border']};
    border-radius: {MACOS_RADIUS['small']};
    padding: 8px 12px;
    padding-right: 30px;
    color: {MACOS_COLORS['text_primary']};
}}

QComboBox:hover {{
    border-color: {MACOS_COLORS['border_dark']};
}}

QComboBox:focus {{
    border-color: {MACOS_COLORS['primary']};
}}

QComboBox QAbstractItemView {{
    background-color: {MACOS_COLORS['bg_white']};
    border: none;
    border-radius: {MACOS_RADIUS['medium']};
    padding: 6px;
    selection-background-color: {MACOS_COLORS['primary']};
    selection-color: {MACOS_COLORS['text_light']};
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
"""
