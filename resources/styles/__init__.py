"""
SMIS Application Styling Module

This module provides styling, theming, and UI utilities for the SMIS application.
The module is organized into multiple files to improve maintainability:

- constants.py: Color definitions, spacing, sizing, fonts, and other constants
- utils.py: Utility functions like resource path resolution and shadow effects
- theme.py: Global styles, sidebar styles, and theme colors
- widgets.py: Widget-specific styling like calendar configuration
- messages.py: Message box styling and configuration

Most commonly used functions and constants are exposed at the module level
for backward compatibility.
"""

# Import constants
from .constants import (
    # Colors and gradients
    PRIMARY_COLOR, BUTTON_GRADIENT, BACKGROUND_GRADIENT, FOCUS_BORDER_COLOR,
    HOVER_BUTTON_COLOR, LABEL_BORDER_COLOR, COLORS,
    
    # Font sizes and families
    HEADING_SIZE, SUBHEADING_SIZE, BUTTON_SIZE, LABEL_SIZE, INPUT_SIZE, SMALL_TEXT_SIZE,
    FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD, FONT_BOLD, FONT_ICONS, FONT_ICONS_SIZE,
    
    # Element heights
    BUTTON_HEIGHT, INPUT_HEIGHT, LABEL_HEIGHT, COMBOBOX_HEIGHT,
    
    # Shadows and radius
    SHADOWS, RADIUS,
    
    # Spacing
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL,
    PADDING_COMPONENT, PADDING_SECTION, PADDING_PAGE, MARGIN_COMPONENT
)

# Import utility functions
from .utils import (
    resource_path, applyShadow, applyFonts, set_widget_height, LayoutUtils
)

# Import theme functions
from .theme import (
    get_global_styles, get_attendance_styles, 
    get_sidebar_light_theme_style, get_sidebar_dark_theme_style, 
    get_sidebar_modern_style, get_current_theme_colors, get_modern_widget_styles
)

# Import widget styling functions
from .widgets import configure_calendar_weekend_format

# Import message box functions
from .messages import (
    configure_message_box, show_info_message, show_warning_message,
    show_error_message, show_question_message, show_critical_message,
    show_success_message, show_confirmation_message, show_save_confirmation,
    show_delete_confirmation
)

# Define a function to apply global app style
def setAppStyle(app):
    """
    Apply global styles to the entire application.
    
    Args:
        app (QApplication): The PyQt application instance
    """
    # Get global styles
    styles = get_global_styles()
    
    # Apply to QApplication
    app.setStyleSheet(f"""
        /* Global Application Styles */
        QWidget {{
            font-family: {FONT_REGULAR};
            font-size: 14px;
            color: {COLORS['gray_900']};
        }}
        
        /* Button Styles */
        QPushButton {{
            {styles['button_secondary'].replace('QPushButton {', '').strip()}
        }}
        
        QPushButton.primary {{
            {styles['button_primary'].replace('QPushButton {', '').strip()}
        }}
        
        QPushButton.success {{
            {styles['button_success'].replace('QPushButton {', '').strip()}
        }}
        
        QPushButton.warning {{
            {styles['button_warning'].replace('QPushButton {', '').strip()}
        }}
        
        QPushButton.danger {{
            {styles['button_danger'].replace('QPushButton {', '').strip()}
        }}
        
        /* Input Styles */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            {styles['input_standard'].replace('QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit {', '').strip()}
        }}
        
       
    """)

# List all exports
__all__ = [
    # Core styling functions
    'setAppStyle', 'applyFonts', 'configure_message_box', 'show_info_message',
    # Calendar functions
    'configure_calendar_weekend_format',
    # Layout functions
    'LayoutUtils',
    # Utility functions
    'applyShadow', 'set_widget_height', 'resource_path',
    # Message functions - Enhanced styling
    'show_warning_message', 'show_error_message', 'show_question_message', 
    'show_critical_message', 'show_success_message', 'show_confirmation_message',
    'show_save_confirmation', 'show_delete_confirmation',
    # Style utilities
    'get_global_styles', 'get_attendance_styles', 'get_modern_widget_styles',
    # Sidebar styling functions
    'get_sidebar_light_theme_style', 'get_sidebar_dark_theme_style', 'get_sidebar_modern_style',
    'get_current_theme_colors',
    # Constants
    'PRIMARY_COLOR', 'BUTTON_GRADIENT', 'BACKGROUND_GRADIENT', 'FOCUS_BORDER_COLOR',
    'HOVER_BUTTON_COLOR', 'LABEL_BORDER_COLOR', 'COLORS', 'FONT_REGULAR', 'FONT_MEDIUM',
    'FONT_SEMIBOLD', 'FONT_BOLD', 'BUTTON_HEIGHT', 'INPUT_HEIGHT', 'LABEL_HEIGHT', 'COMBOBOX_HEIGHT',
    'SHADOWS', 'RADIUS', 'SPACING_XS', 'SPACING_SM', 'SPACING_MD', 'SPACING_LG', 'SPACING_XL', 'SPACING_XXL'
]