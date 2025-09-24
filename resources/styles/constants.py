"""
Constants module for styling the SMIS application.
Contains all color definitions, spacing, sizing, fonts, and other constants.
"""

# Primary styling constants
PRIMARY_COLOR = "rgb(16, 137, 211)"
BUTTON_GRADIENT = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgb(16, 137, 211), stop:1 rgb(18, 177, 209))"
BACKGROUND_GRADIENT = "qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgb(255, 255, 255), stop:1 rgb(244, 247, 251))"
FOCUS_BORDER_COLOR = "#12B1D1"
HOVER_BUTTON_COLOR = "rgb(16, 137, 211)"
LABEL_BORDER_COLOR = "#EFEFF1"

# Font sizes
HEADING_SIZE = "24px"
SUBHEADING_SIZE = "20px"
BUTTON_SIZE = "14px"
LABEL_SIZE = "14px"
INPUT_SIZE = "14px"
SMALL_TEXT_SIZE = "12px"

# Element heights - Standardized across entire app
BUTTON_HEIGHT = "28px"
INPUT_HEIGHT = "28px"
LABEL_HEIGHT = "28px"
COMBOBOX_HEIGHT = "28px"

# Font families
FONT_REGULAR = "Poppins"
FONT_MEDIUM = "Poppins Medium"
FONT_SEMIBOLD = "Poppins SemiBold"
FONT_BOLD = "Poppins Bold"

# Icon fonts for Material Design icons
FONT_ICONS = "'Segoe UI Symbol', 'Material Icons', 'Segoe UI Emoji', sans-serif"
FONT_ICONS_SIZE = "16px"

# Professional Color Palette
COLORS = {
    'primary': '#0874b4',      # Professional Blue
    'primary_light': "#2988D6", # Lighter Blue
    'primary_dark': '#0668a0',  # Darker Blue
    'secondary': '#64748B',     # Slate Gray
    'success': '#10B981',       # Emerald Green
    'warning': '#F59E0B',       # Amber
    'danger': '#EF4444',        # Red
    'info': '#06B6D4',          # Cyan
    'light': '#F8FAFC',         # Very Light Gray
    'dark': '#0F172A',          # Very Dark Blue
    'white': '#FFFFFF',
    'gray_50': '#F9FAFB',
    'gray_100': '#F3F4F6',
    'gray_200': '#E5E7EB',
    'gray_300': '#D1D5DB',
    'gray_400': '#9CA3AF',
    'gray_500': '#6B7280',
    'gray_600': '#4B5563',
    'gray_700': '#374151',
    'gray_800': '#1F2937',
    'gray_900': '#111827'
}

# Professional Shadows
SHADOWS = {
    'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
}

# Professional Border Radius
RADIUS = {
    'none': '0px',
    'sm': '4px',
    'md': '8px',
    'lg': '12px',
    'xl': '16px',
    '2xl': '20px',
    'full': '9999px'
}

# Global Spacing System - Standardized across entire app
SPACING_XS = "4px"    # Extra small - for tight elements
SPACING_SM = "8px"    # Small - default component spacing  
SPACING_MD = "12px"   # Medium - section spacing
SPACING_LG = "16px"   # Large - page margins
SPACING_XL = "20px"   # Extra large - major sections
SPACING_XXL = "24px"  # Extra extra large - page padding

# Layout spacing shortcuts
PADDING_COMPONENT = f"{SPACING_SM} {SPACING_LG}"  # 8px 16px - for buttons/inputs
PADDING_SECTION = f"{SPACING_LG}"                # 16px - for sections
PADDING_PAGE = f"{SPACING_XXL}"                  # 24px - for main containers
MARGIN_COMPONENT = f"{SPACING_XS}"               # 4px - between related components