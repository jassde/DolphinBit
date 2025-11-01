"""
Application Styles - Modern design system with consistent spacing, typography, and colors
"""
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt


# ============================================================================
# COLOR SCHEME - Modern Dark Theme with Purple-Blue Accents
# ============================================================================

class Colors:
    """Color palette for the application"""
    # Primary Colors
    PRIMARY = "#667eea"           # Purple-blue (main accent)
    PRIMARY_DARK = "#5568d3"      # Darker purple-blue
    PRIMARY_LIGHT = "#7c94ff"     # Lighter purple-blue
    
    # Secondary Colors
    SECONDARY = "#764ba2"         # Deep purple
    SECONDARY_LIGHT = "#9f7aea"   # Light purple
    
    # Accent Colors
    ACCENT = "#f093fb"            # Pink accent
    ACCENT_GRADIENT_START = "#667eea"
    ACCENT_GRADIENT_END = "#764ba2"
    
    # Semantic Colors
    SUCCESS = "#4facfe"           # Light blue (success)
    WARNING = "#f6d365"           # Yellow (warning)
    DANGER = "#fa709a"            # Pink-red (danger/delete)
    INFO = "#667eea"              # Blue (info)
    
    # Neutral Colors
    BACKGROUND = "#1a1d29"        # Main background (dark blue-gray)
    SURFACE = "#252936"           # Surface/card background
    SURFACE_HOVER = "#2d3142"     # Surface hover state
    SURFACE_ACTIVE = "#353849"    # Surface active state
    
    # Border & Divider
    BORDER = "rgba(255, 255, 255, 0.1)"
    BORDER_LIGHT = "rgba(255, 255, 255, 0.15)"
    DIVIDER = "rgba(255, 255, 255, 0.08)"
    
    # Text Colors
    TEXT_PRIMARY = "#ffffff"      # Primary text (white)
    TEXT_SECONDARY = "#b4b8d0"    # Secondary text (light gray-blue)
    TEXT_DISABLED = "#6b6f8a"     # Disabled text
    TEXT_INVERSE = "#1a1d29"      # Text on light backgrounds
    
    # Timeline Colors
    TIMELINE_BG = "#2d2d2d"
    TIMELINE_TRACK = "#3c3c3c"
    TIMELINE_IN_POINT = "#32cd32"  # Lime green
    TIMELINE_OUT_POINT = "#dc143c" # Crimson
    TIMELINE_SELECTION_START = "#6495ed"  # Cornflower blue
    TIMELINE_SELECTION_END = "#4169e1"    # Royal blue
    TIMELINE_PLAYHEAD = "#ffffff"
    
    # Video Player
    PLAYER_BG = "#1a1a1a"
    PLAYER_BORDER = "#444444"


# ============================================================================
# TYPOGRAPHY - Clear hierarchy with Segoe UI / SF Pro
# ============================================================================

class Typography:
    """Typography system with consistent font sizes and weights"""
    
    # Font Families
    FONT_FAMILY = "Segoe UI, SF Pro Display, -apple-system, system-ui, sans-serif"
    FONT_FAMILY_MONO = "Consolas, SF Mono, Monaco, Courier New, monospace"
    
    # Font Sizes
    H1_SIZE = 24  # Page titles
    H2_SIZE = 18  # Section headers
    H3_SIZE = 16  # Subsection headers
    H4_SIZE = 14  # Component labels
    BODY_SIZE = 13  # Default text
    SMALL_SIZE = 11  # Secondary info
    TINY_SIZE = 10  # Captions
    
    # Font Weights
    THIN = 200
    LIGHT = 300
    REGULAR = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700
    
    # Line Heights (multipliers)
    TIGHT = 1.2
    NORMAL = 1.5
    RELAXED = 1.8
    
    @staticmethod
    def get_font(size=13, weight=400, family=None):
        """Get a QFont with specified properties"""
        font = QFont(family or Typography.FONT_FAMILY)
        font.setPixelSize(size)
        font.setWeight(weight)
        return font


# ============================================================================
# SPACING - Consistent spacing scale
# ============================================================================

class Spacing:
    """Spacing scale for consistent layout"""
    XS = 4    # Extra small
    SM = 8    # Small
    MD = 16   # Medium (default)
    LG = 24   # Large
    XL = 32   # Extra large
    XXL = 48  # Extra extra large
    
    # Specific use cases
    PADDING_SMALL = SM
    PADDING_MEDIUM = MD
    PADDING_LARGE = LG
    
    MARGIN_SMALL = SM
    MARGIN_MEDIUM = MD
    MARGIN_LARGE = LG
    
    BORDER_RADIUS_SMALL = 4
    BORDER_RADIUS_MEDIUM = 6
    BORDER_RADIUS_LARGE = 12
    
    ICON_SMALL = 16
    ICON_MEDIUM = 24
    ICON_LARGE = 32


# ============================================================================
# SHADOWS - Depth and elevation
# ============================================================================

class Shadows:
    """Shadow definitions for depth"""
    SMALL = "0 2px 4px rgba(0, 0, 0, 0.2)"
    MEDIUM = "0 4px 8px rgba(0, 0, 0, 0.3)"
    LARGE = "0 8px 16px rgba(0, 0, 0, 0.4)"
    GLOW = "0 0 20px rgba(102, 126, 234, 0.3)"
    GLOW_ACTIVE = "0 0 30px rgba(102, 126, 234, 0.5)"


# ============================================================================
# PALETTE GENERATOR
# ============================================================================

def get_dark_palette():
    """Returns a dark color palette for the application"""
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(Colors.BACKGROUND))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(Colors.SURFACE))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Colors.SURFACE_HOVER))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Colors.SURFACE))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(Colors.SURFACE))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(Colors.DANGER))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(Colors.PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(Colors.PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Colors.TEXT_PRIMARY))
    
    return dark_palette


# ============================================================================
# MAIN STYLESHEET
# ============================================================================

def get_stylesheet():
    """Returns the main application stylesheet with modern design"""
    return f"""
        /* ========== GLOBAL ========== */
        QMainWindow {{
            background-color: {Colors.BACKGROUND};
        }}
        
        QWidget {{
            font-family: {Typography.FONT_FAMILY};
            font-size: {Typography.BODY_SIZE}px;
            color: {Colors.TEXT_PRIMARY};
        }}
        
        /* ========== BUTTONS ========== */
        QPushButton {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            color: {Colors.TEXT_PRIMARY};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-weight: {Typography.SEMIBOLD};
            font-size: {Typography.BODY_SIZE}px;
            min-width: 80px;
            min-height: 32px;
        }}
        
        QPushButton:hover {{
            background-color: {Colors.SURFACE_HOVER};
            border: 1px solid {Colors.BORDER_LIGHT};
        }}
        
        QPushButton:pressed {{
            background-color: {Colors.SURFACE_ACTIVE};
        }}
        
        QPushButton:disabled {{
            background-color: {Colors.SURFACE};
            color: {Colors.TEXT_DISABLED};
            border: 1px solid {Colors.DIVIDER};
        }}
        
        /* Primary Button Style */
        QPushButton[class="primary"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Colors.ACCENT_GRADIENT_START},
                stop:1 {Colors.ACCENT_GRADIENT_END});
            border: none;
            color: {Colors.TEXT_PRIMARY};
        }}
        
        QPushButton[class="primary"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Colors.PRIMARY_LIGHT},
                stop:1 {Colors.SECONDARY_LIGHT});
        }}
        
        /* ========== LIST WIDGETS ========== */
        QListWidget {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            color: {Colors.TEXT_PRIMARY};
            outline: none;
            padding: {Spacing.XS}px;
        }}
        
        QListWidget::item {{
            padding: {Spacing.SM}px {Spacing.MD}px;
            border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
            margin: {Spacing.XS}px 0px;
        }}
        
        QListWidget::item:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Colors.ACCENT_GRADIENT_START},
                stop:1 {Colors.ACCENT_GRADIENT_END});
            color: {Colors.TEXT_PRIMARY};
        }}
        
        QListWidget::item:hover {{
            background-color: {Colors.SURFACE_HOVER};
        }}
        
        /* ========== SLIDERS ========== */
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background: {Colors.SURFACE};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {Colors.PRIMARY};
            border: 2px solid {Colors.PRIMARY_DARK};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {Colors.PRIMARY_LIGHT};
            border: 2px solid {Colors.PRIMARY};
        }}
        
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Colors.ACCENT_GRADIENT_START},
                stop:1 {Colors.ACCENT_GRADIENT_END});
            border-radius: 3px;
        }}
        
        /* ========== CHECKBOXES ========== */
        QCheckBox {{
            color: {Colors.TEXT_PRIMARY};
            spacing: {Spacing.SM}px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
            background: {Colors.SURFACE};
        }}
        
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Colors.ACCENT_GRADIENT_START},
                stop:1 {Colors.ACCENT_GRADIENT_END});
            border: 2px solid {Colors.PRIMARY};
        }}
        
        QCheckBox::indicator:hover {{
            border: 2px solid {Colors.PRIMARY};
        }}
        
        /* ========== LINE EDITS ========== */
        QLineEdit {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            color: {Colors.TEXT_PRIMARY};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-size: {Typography.BODY_SIZE}px;
            selection-background-color: {Colors.PRIMARY};
        }}
        
        QLineEdit:focus {{
            border: 1px solid {Colors.PRIMARY};
            background-color: {Colors.SURFACE_HOVER};
        }}
        
        /* ========== COMBO BOXES ========== */
        QComboBox {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            color: {Colors.TEXT_PRIMARY};
            padding: {Spacing.SM}px {Spacing.MD}px;
            min-width: 100px;
            font-size: {Typography.BODY_SIZE}px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {Colors.PRIMARY};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {Colors.TEXT_SECONDARY};
            margin-right: {Spacing.SM}px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            color: {Colors.TEXT_PRIMARY};
            selection-background-color: {Colors.PRIMARY};
            padding: {Spacing.XS}px;
        }}
        
        /* ========== LABELS ========== */
        QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.BODY_SIZE}px;
        }}
        
        QLabel[class="header"] {{
            font-size: {Typography.H3_SIZE}px;
            font-weight: {Typography.BOLD};
            color: {Colors.TEXT_PRIMARY};
        }}
        
        QLabel[class="subheader"] {{
            font-size: {Typography.H4_SIZE}px;
            font-weight: {Typography.SEMIBOLD};
            color: {Colors.TEXT_SECONDARY};
        }}
        
        /* ========== PROGRESS BARS ========== */
        QProgressBar {{
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            background: {Colors.SURFACE};
            text-align: center;
            color: {Colors.TEXT_PRIMARY};
            font-weight: {Typography.SEMIBOLD};
            height: 24px;
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Colors.ACCENT_GRADIENT_START},
                stop:1 {Colors.ACCENT_GRADIENT_END});
            border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
        }}
        
        /* ========== SPLITTER ========== */
        QSplitter::handle {{
            background: {Colors.DIVIDER};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        /* ========== SCROLL BARS ========== */
        QScrollBar:vertical {{
            background: {Colors.SURFACE};
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {Colors.TEXT_DISABLED};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {Colors.TEXT_SECONDARY};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {Colors.SURFACE};
            height: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {Colors.TEXT_DISABLED};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {Colors.TEXT_SECONDARY};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* ========== TOOLTIPS ========== */
        QToolTip {{
            background-color: {Colors.SURFACE};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
            padding: {Spacing.XS}px {Spacing.SM}px;
            font-size: {Typography.SMALL_SIZE}px;
        }}
    """
