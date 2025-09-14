from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget, QMessageBox, QApplication
from PyQt5.QtGui import QColor, QFont, QIcon, QFontDatabase
from PyQt5.QtCore import Qt
import os
import sys



# Define constants for colors and gradients - Primary styling constants
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
BUTTON_HEIGHT = "38px"
INPUT_HEIGHT = "38px"
LABEL_HEIGHT = "32px"
COMBOBOX_HEIGHT = "38px"

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
    'primary': '#2563EB',      # Professional Blue
    'primary_light': '#3B82F6', # Lighter Blue
    'primary_dark': '#1D4ED8',  # Darker Blue
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
MARGIN_SECTION = f"{SPACING_LG}"                 # 16px - between sections

# Global Component Styles - Applied across entire application
def get_global_styles():
    """Return standardized global styles for all app components."""
    return {
        # Professional Button Styles with PyQt5 compatible design
        'button_primary': f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
                color: {COLORS['white']};
                border: none;
                border-radius: {RADIUS['md']};
                padding: {SPACING_MD} {SPACING_XL};
                margin: {MARGIN_COMPONENT};
                font-family: {FONT_SEMIBOLD};
                font-weight: 600;
                font-size: 14px;
                min-height: 32px;
                max-height: 32px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
            }}
            QPushButton:pressed {{
                background: {COLORS['primary_dark']};
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_300']};
                color: {COLORS['gray_500']};
            }}
        """,
        
        'button_secondary': f"""
            QPushButton {{
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: {PADDING_COMPONENT};
                margin: {MARGIN_COMPONENT};
                font-weight: 600;
                font-size: 14px;
                font-family: {FONT_SEMIBOLD};
                min-height: {BUTTON_HEIGHT};
                max-height: {BUTTON_HEIGHT};
            }}
            QPushButton:hover {{
                background-color: #4B5563;
            }}
            QPushButton:pressed {{
                background-color: #374151;
            }}
        """,
        
        'button_outline': f"""
            QPushButton {{
                background-color: transparent;
                color: #3B82F6;
                border: 2px solid #3B82F6;
                border-radius: 8px;
                padding: {SPACING_SM} {SPACING_MD};
                margin: {MARGIN_COMPONENT};
                font-weight: 500;
                font-size: 14px;
                font-family: {FONT_MEDIUM};
                min-height: {BUTTON_HEIGHT};
                max-height: {BUTTON_HEIGHT};
            }}
            QPushButton:hover {{
                background-color: #3B82F6;
                color: white;
            }}
            QPushButton:pressed {{
                background-color: #2563EB;
            }}
        """,
        
        'button_success': f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                font-family: {FONT_SEMIBOLD};
                min-height: {BUTTON_HEIGHT};
                max-height: {BUTTON_HEIGHT};
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """,
        
        'button_warning': f"""
            QPushButton {{
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                font-family: {FONT_SEMIBOLD};
                min-height: {BUTTON_HEIGHT};
                max-height: {BUTTON_HEIGHT};
            }}
            QPushButton:hover {{
                background-color: #B91C1C;
            }}
            QPushButton:pressed {{
                background-color: #991B1B;
            }}
        """,
        
        # Professional Input Styles with PyQt5 compatible design
        'input_standard': f"""
            QLineEdit {{
                border: 2px solid {COLORS['gray_200']};
                border-radius: {RADIUS['lg']};
                padding: {SPACING_MD} {SPACING_LG};
                margin: {MARGIN_COMPONENT};
                background-color: {COLORS['white']};
                color: {COLORS['gray_800']};
                font-size: 14px;
                font-family: {FONT_REGULAR};
                min-height: 44px;
                max-height: 44px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
                background-color: {COLORS['white']};
            }}
            QLineEdit:hover {{
                border-color: {COLORS['gray_300']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['gray_400']};
            }}
        """,
        
        'input_with_icon': f"""
            QLineEdit {{
                border: 2px solid {COLORS['gray_200']};
                border-radius: {RADIUS['lg']};
                padding: {SPACING_MD} {SPACING_LG} {SPACING_MD} 44px;
                margin: {MARGIN_COMPONENT};
                background-color: white;
                color: #2C3E50;
                font-size: 14px;
                font-family: {FONT_REGULAR};
                min-height: {INPUT_HEIGHT};
                max-height: {INPUT_HEIGHT};
            }}
            QLineEdit:focus {{
                border-color: #3B82F6;
                outline: none;
                background-color: #FEFEFE;
            }}
            QLineEdit:hover {{
                border-color: #D1D5DB;
            }}
        """,
        
        # ComboBox Styles with standardized spacing
        'combobox_standard': f"""
            QComboBox {{
                background-color: #F5F5F5;
                color: #444444; /* Lighter black for dropdown text */
                border: 2px solid {LABEL_BORDER_COLOR};
                border-radius: 5px;
                padding: 5px;
                font-size: 12px; /* Standard font size */
            }}
            QComboBox:disabled {{
                background-color: #E0E0E0;
                border: 2px solid #B0B0B0;
                color: #888888;
            }}
            QComboBox:focus {{
                border: 2px solid {FOCUS_BORDER_COLOR};
            }}
            QComboBox::drop-down {{
                border-left: 1px solid {LABEL_BORDER_COLOR};
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: url({icon_path.replace("\\", "/")});
                width: 15px;
                height: 15px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                border-radius: 0px;
                selection-background-color: {PRIMARY_COLOR};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 5px;
                color: #444444; /* Lighter black for dropdown items */
                font-size: 14px; /* Standard font size */
                font-weight: normal; /* Reduced boldness for dropdown items */
                text-align: left;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {PRIMARY_COLOR};
                color: #FFFFFF; /* White text for selected items */
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #E0E0E0;
                color: #444444;
            }}
        """,
        
        'combobox_with_icon': f"""
            QComboBox {{
                background-color: #F5F5F5;
                color: #444444; /* Lighter black for dropdown text */
                border: 2px solid {LABEL_BORDER_COLOR};
                border-radius: 5px;
                padding: 5px 5px 5px 35px;
                font-size: 12px; /* Standard font size */
            }}
            QComboBox:disabled {{
                background-color: #E0E0E0;
                border: 2px solid #B0B0B0;
                color: #888888;
            }}
            QComboBox:focus {{
                border: 2px solid {FOCUS_BORDER_COLOR};
            }}
            QComboBox::drop-down {{
                border-left: 1px solid {LABEL_BORDER_COLOR};
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: url({icon_path.replace("\\", "/")});
                width: 15px;
                height: 15px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                border-radius: 0px;
                selection-background-color: {PRIMARY_COLOR};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 5px;
                color: #444444; /* Lighter black for dropdown items */
                font-size: 14px; /* Standard font size */
                font-weight: normal; /* Reduced boldness for dropdown items */
                text-align: left;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {PRIMARY_COLOR};
                color: #FFFFFF; /* White text for selected items */
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #E0E0E0;
                color: #444444;
            }}
        """,
        
        # SpinBox Styles
        'spinbox_standard': f"""
            QSpinBox {{
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: {FONT_REGULAR};
                color: #2C3E50;
                min-height: {INPUT_HEIGHT};
                max-height: {INPUT_HEIGHT};
            }}
            QSpinBox:focus {{
                border-color: #3B82F6;
                outline: none;
            }}
            QSpinBox:hover {{
                border-color: #D1D5DB;
            }}
            QSpinBox:read-only {{
                background-color: #F9FAFB;
                color: #6B7280;
            }}
        """,
        
        # Label Styles
        'label_standard': f"""
            QLabel {{
                color: #374151;
                font-size: 14px;
                font-family: {FONT_REGULAR};
                min-height: {LABEL_HEIGHT};
            }}
        """,
        
        'label_heading': f"""
            QLabel {{
                color: #111827;
                font-size: 18px;
                font-family: {FONT_SEMIBOLD};
                font-weight: 600;
                min-height: 32px;
            }}
        """,
        
        'label_subheading': f"""
            QLabel {{
                color: #374151;
                font-size: 16px;
                font-family: {FONT_MEDIUM};
                font-weight: 500;
                min-height: 28px;
            }}
        """,
        
        'label_info': f"""
            QLabel {{
                color: #6B7280;
                font-size: 12px;
                font-family: {FONT_REGULAR};
                font-style: italic;
                min-height: 24px;
            }}
        """,
        
        # CheckBox Styles
        'checkbox_standard': f"""
            QCheckBox {{
                color: #374151;
                font-size: 14px;
                font-family: {FONT_REGULAR};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #E5E7EB;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: #3B82F6;
                border-color: #3B82F6;
            }}
            QCheckBox::indicator:hover {{
                border-color: #3B82F6;
            }}
        """,
        
        # Table Styles
        'table_standard': f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #F3F4F6;
                font-family: {FONT_REGULAR};
                font-size: 14px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #F3F4F6;
            }}
            QHeaderView::section {{
                background-color: #F9FAFB;
                color: #374151;
                font-size: 14px;
                font-family: {FONT_MEDIUM};
                font-weight: 500;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
            }}
        """,

        
        # Calendar Styles with Saturday as working day
        'calendar_standard': f"""
            QCalendarWidget {{
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                font-family: {FONT_REGULAR};
            }}
            QCalendarWidget QWidget {{
                alternate-background-color: white;
                background-color: white;
            }}
            QCalendarWidget QToolButton {{
                background-color: white;
                color: #111827;
                font-family: {FONT_MEDIUM};
                font-weight: 500;
                height: 36px;
                min-width: 36px;
                border: none;
                border-radius: 4px;
                padding: 0 8px;
                margin: 2px;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: white;
                selection-background-color: #2563EB;
            }}
            /* Saturday as working day - normal color */
            QCalendarWidget QAbstractItemView:enabled QTableCornerButton::section {{
                background-color: white;
            }}
            /* Sunday as weekend - red background */
            QCalendarWidget QTableView {{
                gridline-color: #E5E7EB;
            }}
        """
    }

# Attendance Page Specific Styles - Backward compatibility
def get_attendance_styles():
    """Return attendance page styles using global styles."""
    global_styles = get_global_styles()
    return {
        'combobox_standard': global_styles['combobox_with_icon'],
        'combobox_month': global_styles['combobox_with_icon'],
        'combobox_with_icon': global_styles['combobox_with_icon'],
        'combobox_status': global_styles['combobox_standard'],
        'search_input': global_styles['input_with_icon'],
        'year_spinner': global_styles['spinbox_standard'],
        'checkbox_lock': global_styles['checkbox_standard'],
        'button_outline': global_styles['button_outline'],
        'button_primary': global_styles['button_primary'],
        'button_secondary': global_styles['button_secondary'],
        'button_success': global_styles['button_success'],
        'button_warning': global_styles['button_warning'],
        'info_text': global_styles['label_info'].replace('QLabel', '').strip(),
        'table_modern': global_styles['table_standard'],
        'calendar_modern': global_styles['calendar_standard']
    }

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running in normal Python environment
        return os.path.join(os.path.abspath("."), relative_path)

# Path to the icon
icon_path = resource_path("resources/expand_arrow.png")


def applyShadow(widget, x_offset=0, y_offset=10, blur_radius=25, color=QColor(0, 0, 0, 100)):
    """Apply drop shadow effect to a widget."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setOffset(x_offset, y_offset)
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)


def setAppStyle(window):
    """Apply the global application style to a window or widget."""
    global_styles = get_global_styles()
    
    window.setStyleSheet(f"""
        QWidget {{
            background: {BACKGROUND_GRADIENT};
            border-radius: 20px;
            font-family: {FONT_REGULAR};
        }}
        
        QWidget#mainContent {{
            background: white;
            border-radius: 20px;
            margin: 10px;
        }}
        
        /* Global Button Styles */
        QPushButton {{
            background-color: #3B82F6;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 14px;
            font-family: {FONT_SEMIBOLD};
            min-height: {BUTTON_HEIGHT};
            max-height: {BUTTON_HEIGHT};
        }}
        QPushButton:hover {{
            background-color: #2563EB;
        }}
        QPushButton:pressed {{
            background-color: #1D4ED8;
        }}
        
        /* Global Input Styles */
        QLineEdit {{
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 8px 15px;
            background-color: white;
            color: #2C3E50;
            font-size: 14px;
            font-family: {FONT_REGULAR};
            min-height: {INPUT_HEIGHT};
            max-height: {INPUT_HEIGHT};
        }}
        QLineEdit:focus {{
            border-color: #3B82F6;
            outline: none;
            background-color: #FEFEFE;
        }}
        QLineEdit:hover {{
            border-color: #D1D5DB;
        }}
        
        /* Global ComboBox Styles */
        QComboBox {{
            background-color: #F5F5F5;
            color: #444444; /* Lighter black for dropdown text */
            border: 2px solid {LABEL_BORDER_COLOR};
            border-radius: 5px;
            padding: 5px;
            font-size: 12px; /* Standard font size */
        }}
        QComboBox:disabled {{
            background-color: #E0E0E0;
            border: 2px solid #B0B0B0;
            color: #888888;
        }}
        QComboBox:focus {{
            border: 2px solid {FOCUS_BORDER_COLOR};
        }}
        QComboBox::drop-down {{
            border-left: 1px solid {LABEL_BORDER_COLOR};
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: url({icon_path.replace("\\", "/")});
            width: 15px;
            height: 15px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #FFFFFF;
            border-radius: 0px;
            selection-background-color: {PRIMARY_COLOR};
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 5px;
            color: #444444; /* Lighter black for dropdown items */
            font-size: 14px; /* Standard font size */
            font-weight: normal; /* Reduced boldness for dropdown items */
            text-align: left;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: {PRIMARY_COLOR};
            color: #FFFFFF; /* White text for selected items */
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: #E0E0E0;
            color: #444444;
        }}
        
        /* Global SpinBox Styles */
        QSpinBox {{
            background-color: white;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            font-family: {FONT_REGULAR};
            color: #2C3E50;
            min-height: {INPUT_HEIGHT};
            max-height: {INPUT_HEIGHT};
        }}
        QSpinBox:focus {{
            border-color: #3B82F6;
            outline: none;
        }}
        QSpinBox:hover {{
            border-color: #D1D5DB;
        }}
        QSpinBox:read-only {{
            background-color: #F9FAFB;
            color: #6B7280;
        }}
        
        /* Global Label Styles - EXCLUDING SIDEBAR */
        QLabel:not(#sidebarNavTitle):not(#sidebarNavIcon) {{
            color: #374151;
            font-size: 14px;
            font-family: {FONT_REGULAR};
            min-height: {LABEL_HEIGHT};
            background-color: transparent;
        }}
        
        /* Headings */
        QLabel#heading {{
            color: #111827;
            background-color: transparent;
            font-size: {HEADING_SIZE};
            font-family: {FONT_BOLD};
            padding: 10px 0px;
        }}

        QLabel#subheading {{
            color: #374151;
            background-color: transparent;
            font-size: {SUBHEADING_SIZE};
            font-family: {FONT_SEMIBOLD};
            padding: 8px 0px;
        }}
        
        /* Global CheckBox Styles */
        QCheckBox {{
            color: #374151;
            font-size: 14px;
            font-family: {FONT_REGULAR};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 2px solid #E5E7EB;
            background-color: white;
        }}
        QCheckBox::indicator:checked {{
            background-color: #3B82F6;
            border-color: #3B82F6;
        }}
        QCheckBox::indicator:hover {{
            border-color: #3B82F6;
        }}

        /* Global Radio Button Styles */
        QRadioButton {{
            background-color: transparent;
            color: #374151;
            font-size: 14px;
            font-family: {FONT_REGULAR};
            padding: 5px 0px;
        }}

        /* Global Table Styles */
        QTableWidget {{
            background-color: white;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            gridline-color: #F3F4F6;
            font-family: {FONT_REGULAR};
            font-size: 14px;
        }}
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid #F3F4F6;
        }}
        QHeaderView::section {{
            background-color: #F9FAFB;
            color: #374151;
            font-size: 14px;
            font-family: {FONT_MEDIUM};
            font-weight: 500;
            padding: 10px 8px;
            border: none;
            border-bottom: 2px solid #E5E7EB;
        }}

        /* Global Scrollbar Styles */
        QScrollBar:vertical {{
            border: none;
            background: #EFEFF1;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {PRIMARY_COLOR};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: #EFEFF1;
            height: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {PRIMARY_COLOR};
            min-width: 20px;
            border-radius: 5px;
        }}

        /* Links */
        QLabel#link {{ 
            color: {PRIMARY_COLOR};
            background-color: transparent;
            font-size: {SMALL_TEXT_SIZE};
            font-family: {FONT_MEDIUM};
            text-decoration: underline;
        }}
    """)




def applyFonts(widget: QWidget, font_name: str = None, size: int = 12, bold: bool = True) -> None:
    if not isinstance(widget, QWidget):
        raise TypeError("The provided object is not a valid QWidget.")
    
    font = QFont(font_name or "Segoe UI", size)
    font.setBold(bold)
    widget.setFont(font)


def set_widget_height(widget):
    """Sets the standard height for buttons, labels, and comboboxes."""
    widget.setFixedHeight(35)


# Helper function to configure the QMessageBox with the icon
def configure_message_box(icon_type, title, message, buttons):
    msg_box = QMessageBox()
    msg_box.setIcon(icon_type)
    
    # Get the directory of the current file (style.py)
    base_dir = os.path.dirname(__file__)
    icon_path = os.path.join(base_dir, 'app_icon.svg')

    # Check if the icon file exists and set it
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        msg_box.setWindowIcon(app_icon)
    else:
        # Fallback to ico file
        icon_path = os.path.join(base_dir, 'icon.ico')
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            msg_box.setWindowIcon(app_icon)
    
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(buttons)
    
    # Apply clean modern styling to message box - Complete fix for borders and corners
    msg_box.setStyleSheet(f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
            padding: {SPACING_XL};
            font-family: {FONT_REGULAR};
            font-size: 14px;
            color: {COLORS['gray_800']};
            min-width: 400px;
            max-width: 600px;
        }}
        
        QMessageBox * {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox QWidget {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox > QWidget {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox QLabel {{
            background-color: {COLORS['white']};
            color: {COLORS['gray_800']};
            font-family: {FONT_REGULAR};
            font-size: 14px;
            padding: {SPACING_MD};
            margin: 0px;
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox QLabel#qt_msgbox_label {{
            font-weight: 500;
            font-size: 15px;
            color: {COLORS['gray_900']};
            padding: {SPACING_LG} {SPACING_MD};
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
            color: {COLORS['white']};
            border: none;
            border-radius: {RADIUS['md']};
            padding: {SPACING_SM} {SPACING_LG};
            margin: {SPACING_XS};
            font-family: {FONT_SEMIBOLD};
            font-weight: 600;
            font-size: 13px;
            min-width: 70px;
            min-height: 28px;
            max-height: 28px;
        }}
        
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
        }}
        
        QMessageBox QPushButton:pressed {{
            background: {COLORS['primary_dark']};
        }}
        
        QMessageBox QPushButton:default {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
        }}
        
        QMessageBox QPushButton:default:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
        }}
        
        QMessageBox QPushButton[text="No"], QMessageBox QPushButton[text="&No"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['gray_400']}, stop:1 {COLORS['gray_600']});
        }}
        
        QMessageBox QPushButton[text="No"]:hover, QMessageBox QPushButton[text="&No"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #FF4444, stop:1 #CC0000);
        }}
        
        QMessageBox QPushButton[text="Cancel"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['gray_400']}, stop:1 {COLORS['gray_600']});
        }}
        
        QMessageBox QPushButton[text="Cancel"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #FF4444, stop:1 #CC0000);
        }}
        
        QMessageBox QLabel#qt_msgboxex_icon_label {{
            padding: {SPACING_LG};
            margin: 0px;
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox QFrame {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox QDialogButtonBox {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        
        QMessageBox QVBoxLayout {{
            background-color: {COLORS['white']};
        }}
        
        QMessageBox QHBoxLayout {{
            background-color: {COLORS['white']};
        }}
        
        QMessageBox QGridLayout {{
            background-color: {COLORS['white']};
        }}
    """)
    
    # Apply shadow effect for modern look
    applyShadow(msg_box, 0, 8, 25, QColor(0, 0, 0, 40))
    
    return msg_box

# Message functions with enhanced styling
def show_info_message(title, message):
    """Show info message dialog with clean styling."""
    msg_box = configure_message_box(QMessageBox.Information, title, message, QMessageBox.Ok)
    
    # Apply clean info styling without borders - Let base handle No/Cancel buttons
    info_style = f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['info']}, stop:1 #0891B2);
        }}
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #22D3EE, stop:1 {COLORS['info']});
        }}
    """
    msg_box.setStyleSheet(msg_box.styleSheet() + info_style)
    msg_box.exec_()

def show_warning_message(title, message):
    """Show warning message dialog with clean styling."""
    msg_box = configure_message_box(QMessageBox.Warning, title, message, QMessageBox.Ok)
    
    # Apply clean warning styling without borders - Let base handle No/Cancel buttons
    warning_style = f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['warning']}, stop:1 #D97706);
        }}
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #FCD34D, stop:1 {COLORS['warning']});
        }}
    """
    msg_box.setStyleSheet(msg_box.styleSheet() + warning_style)
    msg_box.exec_()

def show_error_message(title, message):
    """Show error message dialog with clean styling."""
    msg_box = configure_message_box(QMessageBox.Critical, title, message, QMessageBox.Ok)
    
    # Apply clean error styling without borders - Let base handle No/Cancel buttons
    error_style = f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['danger']}, stop:1 #DC2626);
        }}
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #F87171, stop:1 {COLORS['danger']});
        }}
    """
    msg_box.setStyleSheet(msg_box.styleSheet() + error_style)
    msg_box.exec_()

def show_question_message(title, message):
    """Show question message dialog with clean styling."""
    msg_box = configure_message_box(QMessageBox.Question, title, message, QMessageBox.Yes | QMessageBox.No)
    
    # Apply clean question styling without borders - Only style Yes button, let base handle No
    question_style = f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        QMessageBox QPushButton[text="Yes"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
        }}
        QMessageBox QPushButton[text="Yes"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
        }}
    """
    msg_box.setStyleSheet(msg_box.styleSheet() + question_style)
    return msg_box.exec_()

def show_critical_message(title, message):
    """Show critical message dialog with modern dark red styling."""
    msg_box = configure_message_box(QMessageBox.Critical, title, message, QMessageBox.Ok)
    
    # Apply critical-specific styling
    critical_style = f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: 3px solid #991B1B;
            border-radius: {RADIUS['xl']};
        }}
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #DC2626, stop:1 #991B1B);
        }}
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #EF4444, stop:1 #DC2626);
        }}
        QMessageBox QLabel#qt_msgbox_label {{
            color: #991B1B;
            font-weight: 600;
        }}
    """
    msg_box.setStyleSheet(msg_box.styleSheet() + critical_style)
    msg_box.exec_()

def show_success_message(title, message):
    """Show success message dialog with clean blue styling."""
    msg_box = configure_message_box(QMessageBox.Information, title, message, QMessageBox.Ok)
    
    # Apply clean success styling without borders - Let base handle No/Cancel buttons
    success_style = f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: none;
            border-radius: 0px;
        }}
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
        }}
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
        }}
    """
    msg_box.setStyleSheet(msg_box.styleSheet() + success_style)
    msg_box.exec_()

# Global Layout Utility Functions for Consistent Spacing
class LayoutUtils:
    """Utility class for consistent spacing across all layouts."""
    
    @staticmethod
    def set_layout_spacing(layout, spacing_type='normal'):
        """Set consistent spacing for layouts."""
        if spacing_type == 'tight':
            layout.setSpacing(int(SPACING_XS.replace('px', '')))
            layout.setContentsMargins(int(SPACING_XS.replace('px', '')), 
                                    int(SPACING_XS.replace('px', '')), 
                                    int(SPACING_XS.replace('px', '')), 
                                    int(SPACING_XS.replace('px', '')))
        elif spacing_type == 'normal':
            layout.setSpacing(int(SPACING_SM.replace('px', '')))
            layout.setContentsMargins(int(SPACING_LG.replace('px', '')), 
                                    int(SPACING_LG.replace('px', '')), 
                                    int(SPACING_LG.replace('px', '')), 
                                    int(SPACING_LG.replace('px', '')))
        elif spacing_type == 'section':
            layout.setSpacing(int(SPACING_MD.replace('px', '')))
            layout.setContentsMargins(int(SPACING_LG.replace('px', '')), 
                                    int(SPACING_LG.replace('px', '')), 
                                    int(SPACING_LG.replace('px', '')), 
                                    int(SPACING_LG.replace('px', '')))
        elif spacing_type == 'page':
            layout.setSpacing(int(SPACING_LG.replace('px', '')))
            layout.setContentsMargins(int(SPACING_XXL.replace('px', '')), 
                                    int(SPACING_XXL.replace('px', '')), 
                                    int(SPACING_XXL.replace('px', '')), 
                                    int(SPACING_XXL.replace('px', '')))
    
    @staticmethod
    def get_spacing_value(spacing_type):
        """Get spacing value as integer for programmatic use."""
        spacing_map = {
            'xs': int(SPACING_XS.replace('px', '')),
            'sm': int(SPACING_SM.replace('px', '')),
            'md': int(SPACING_MD.replace('px', '')),
            'lg': int(SPACING_LG.replace('px', '')),
            'xl': int(SPACING_XL.replace('px', '')),
            'xxl': int(SPACING_XXL.replace('px', ''))
        }
        return spacing_map.get(spacing_type, spacing_map['sm'])
    
    @staticmethod
    def get_padding_tuple(padding_type='normal'):
        """Get padding as tuple for widget.setContentsMargins()."""
        if padding_type == 'tight':
            value = int(SPACING_XS.replace('px', ''))
        elif padding_type == 'normal':
            value = int(SPACING_SM.replace('px', ''))
        elif padding_type == 'section':
            value = int(SPACING_LG.replace('px', ''))
        elif padding_type == 'page':
            value = int(SPACING_XXL.replace('px', ''))
        else:
            value = int(SPACING_SM.replace('px', ''))
        
        return (value, value, value, value)

# Utility Functions - Legacy compatibility and additional helpers
def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running in normal Python environment
        return os.path.join(os.path.abspath("."), relative_path)

def applyShadow(widget, x_offset=0, y_offset=10, blur_radius=25, color=QColor(0, 0, 0, 100)):
    """Apply drop shadow effect to a widget."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setOffset(x_offset, y_offset)
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)

def set_widget_height(widget, height=35):
    """Sets the standard height for buttons, labels, and comboboxes."""
    widget.setFixedHeight(height)

# Additional message utility functions for backward compatibility
def show_confirmation_message(title, message):
    """Show confirmation dialog with Yes/No options."""
    return show_question_message(title, message)

def show_save_confirmation(filename="file"):
    """Show save confirmation dialog."""
    return show_question_message(
        "Save Changes", 
        f"Do you want to save changes to {filename}?"
    )

def show_delete_confirmation(item_name="item"):
    """Show delete confirmation dialog."""
    msg_box = configure_message_box(
        QMessageBox.Warning, 
        "Confirm Delete", 
        f"Are you sure you want to delete {item_name}? This action cannot be undone.",
        QMessageBox.Yes | QMessageBox.No
    )
    
    # Apply delete-specific styling - Only style Yes button, let base handle No
    delete_style = f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: 2px solid {COLORS['danger']};
            border-radius: {RADIUS['xl']};
        }}
        QMessageBox QPushButton[text="Yes"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['danger']}, stop:1 #DC2626);
        }}
        QMessageBox QPushButton[text="Yes"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #F87171, stop:1 {COLORS['danger']});
        }}
        QMessageBox QLabel#qt_msgbox_label {{
            color: {COLORS['danger']};
            font-weight: 500;
        }}
    """
    msg_box.setStyleSheet(msg_box.styleSheet() + delete_style)
    return msg_box.exec_()

def configure_calendar_weekend_format(calendar_widget):
    """Configure calendar to show only Sunday as weekend and disable Sunday selection."""
    from PyQt5.QtGui import QTextCharFormat
    from PyQt5.QtCore import Qt
    
    # Create format for Sunday (weekend) - disabled appearance
    weekend_format = QTextCharFormat()
    weekend_format.setBackground(QColor('#f9fafb'))  # Light gray background
    weekend_format.setForeground(QColor('#d1d5db'))  # Gray text
    
    # Create format for working days (Monday-Saturday)
    working_format = QTextCharFormat()
    working_format.setBackground(QColor('#ffffff'))  # White background
    working_format.setForeground(QColor('#374151'))  # Dark gray text
    
    # Apply format to all days
    # Note: In PyQt5, day 1 = Monday, day 7 = Sunday
    for day in range(1, 8):
        if day == 7:  # Sunday - disabled weekend format
            calendar_widget.setWeekdayTextFormat(day, weekend_format)
        else:  # Monday-Saturday (working days)
            calendar_widget.setWeekdayTextFormat(day, working_format)
    
    # Disable date selection for Sundays (if the calendar supports it)
    try:
        # Connect to selectionChanged signal to block Sunday selection
        def on_selection_changed():
            selected_date = calendar_widget.selectedDate()
            if selected_date.dayOfWeek() == 7:  # Sunday
                # Find next working day (Monday)
                next_working_day = selected_date.addDays(1)
                calendar_widget.setSelectedDate(next_working_day)
                
                # Show warning message
                from PyQt5.QtWidgets import QMessageBox
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Sunday Blocked")
                msg.setText("Sunday is a weekend day and cannot be selected.\n\nAutomatically moved to next working day.")
                msg.exec_()
        
        calendar_widget.selectionChanged.connect(on_selection_changed)
    except:
        pass  # If connection fails, just continue with visual formatting

# Sidebar Styles - Modern Professional Design
def get_sidebar_light_theme_style():
    """Get light theme stylesheet for ModernSidebar."""
    return """
        /* Light Theme - Clean Modern Design */
        ModernSidebar {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }
        
        /* Header */
        QFrame#headerFrame {
            background-color: #ffffff;
            border: none;
            border-bottom: 1px solid #f3f4f6;
        }
        
        /* Logo */
        QLabel#logoLabel {
            background-color: #6366f1;
            color: white;
            border-radius: 20px;
            font-size: 16px;
            font-weight: bold;
        }
        
        /* Brand Text */
        QLabel#brandTitle {
            color: #111827;
            font-size: 18px !important;
            font-weight: 700 !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
        }
        
        QLabel#brandSubtitle {
            color: #6b7280;
            font-size: 12px !important;
            font-weight: normal !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
        }
        
        /* Organization Logos */
        QLabel#orgLogoExpanded {
            background-color: #f8fafc;
            color: #6366f1;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px !important;
            font-weight: 600 !important;
            font-family: 'Segoe UI', sans-serif;
            padding: 0px 0px 0px 16px; /* Only left padding matches navButton */
            margin: 0px 0px 0px 1px;  /* Only left margin matches navButton */
            qproperty-alignment: 'AlignCenter';
        }
        
        QLabel#orgLogoCollapsed {
            background-color: #f8fafc;
            color: #6366f1;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            font-size: 18px !important;
            font-weight: bold !important;
            font-family: 'Segoe UI', sans-serif;
            padding: 0px 0px 0px 16px; /* Only left padding matches navButton */
            margin: 0px 0px 0px 1px;  /* Only left margin matches navButton */
            qproperty-alignment: 'AlignCenter';
            min-width: 32px;
            max-width: 32px;
            min-height: 32px;
            max-height: 32px;
        }
        
        /* SMIS Branding */
        QLabel#smisTitle {
            color: #1e293b;
            font-size: 24px !important;
            font-weight: bold !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
            qproperty-alignment: 'AlignCenter';
            letter-spacing: 2px;
        }
        
        QLabel#smisSubtitle {
            color: #64748b;
            font-size: 12px !important;
            font-weight: normal !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
            qproperty-alignment: 'AlignCenter';
        }
        
        /* Menu Button - Smaller to prevent overlap */
        QPushButton#menuBtn {
            background-color: transparent;
            color: #6b7280;
            border: none;
            border-radius: 6px;
            font-size: 12px;
            padding: 4px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
        }
        
        QPushButton#menuBtn:hover {
            background-color: #f3f4f6;
            color: #374151;
        }
        
        /* Search */
        QFrame#searchContainer {
            background-color: #ffffff;
            border: none;
        }
        
        QLineEdit#searchInput {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 13px;
            color: #111827;
        }
        
        QLineEdit#searchInput:focus {
            border-color: #6366f1;
            background-color: #ffffff;
        }
        
        QLineEdit#searchInput::placeholder {
            color: #9ca3af;
        }
        
        /* Navigation */
        QFrame#navContainer {
            background-color: #ffffff;
            border: none;
        }
        
        QPushButton#navButton {
            background-color: transparent;
            border: none;
            border-radius: 10px;
            text-align: left;
            padding: 0px;
            margin: 1px 0px;
            min-height: 44px !important;
            max-height: 44px !important;
            height: 44px !important;
        }
        
        QPushButton#navButton:hover {
            background-color: #f3f4f6;
        }
        
        QPushButton#navButton[selected="true"] {
            background-color: #6366f1;
        }
        
        QPushButton#navButton[selected="true"] QLabel#navIcon {
            color: white;
        }
        
        QPushButton#navButton[selected="true"] QLabel#navTitle {
            color: white;
            font-weight: 600;
        }
        
        QLabel#navIcon {
            color: #6b7280;
            font-size: 16px !important;
            font-weight: normal !important;
        }
        
        QLabel#navTitle {
            color: #374151;
            font-size: 14px !important;
            font-weight: bold !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
        }
        
        /* SIDEBAR-SPECIFIC STYLES (isolated from global conflicts) */
        QLabel#sidebarNavIcon {
            color: #6b7280 !important;
            font-size: 16px !important;
            font-weight: normal !important;
            font-family: 'Poppins', sans-serif !important;
            min-height: auto !important;
            background-color: transparent !important;
        }
        
        QLabel#sidebarNavTitle {
            color: #374151 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            font-family: 'Poppins', sans-serif !important;
            margin: 0px !important;
            padding: 0px 8px !important;
            min-height: 44px !important;
            max-height: 44px !important;
            height: 44px !important;
            background-color: transparent !important;
            qproperty-alignment: 'AlignVCenter | AlignLeft' !important;
            text-align: left !important;
            vertical-align: middle !important;
            line-height: 44px !important;
        }
        
        /* Footer */
        QFrame#footerFrame {
            background-color: #ffffff;
            border: none;
            border-top: 1px solid #f3f4f6;
            margin: 0px;
            padding: 8px 0px;
            min-height: 110px !important;
            max-height: 110px !important;
            height: 110px !important;
        }
    """

def get_sidebar_dark_theme_style():
    """Get dark theme stylesheet for ModernSidebar."""
    return """
        /* Dark Theme - Modern Design */
        ModernSidebar {
            background-color: #1f2937;
            border-right: 1px solid #374151;
        }
        
        /* Header */
        QFrame#headerFrame {
            background-color: #1f2937;
            border: none;
            border-bottom: 1px solid #374151;
        }
        
        /* Logo */
        QLabel#logoLabel {
            background-color: #6366f1;
            color: white;
            border-radius: 20px;
            font-size: 16px;
            font-weight: bold;
        }
        
        /* Brand Text */
        QLabel#brandTitle {
            color: #f9fafb;
            font-size: 18px !important;
            font-weight: bold !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
        }
        
        QLabel#brandSubtitle {
            color: #9ca3af;
            font-size: 12px !important;
            font-weight: normal !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
        }
        
        /* Organization Logos */
        QLabel#orgLogoExpanded {
            background-color: #374151;
            color: #6366f1;
            border: 1px solid #4b5563;
            border-radius: 8px;
            font-size: 14px !important;
            font-weight: 600 !important;
            font-family: 'Segoe UI', sans-serif;
            padding: 8px 12px;
            margin: 0px;  /* No margins - logo at top */
            qproperty-alignment: 'AlignCenter';
        }
        
        QLabel#orgLogoCollapsed {
            background-color: #374151;
            color: #6366f1;
            border: 1px solid #4b5563;
            border-radius: 6px;
            font-size: 18px !important;
            font-weight: bold !important;
            font-family: 'Segoe UI', sans-serif;
            padding: 6px;
            margin: 0px;  /* No margins - logo at top */
            qproperty-alignment: 'AlignCenter';
            min-width: 32px;
            max-width: 32px;
            min-height: 32px;
            max-height: 32px;
        }
        
        /* SMIS Branding */
        QLabel#smisTitle {
            color: #f9fafb;
            font-size: 24px !important;
            font-weight: bold !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
            qproperty-alignment: 'AlignCenter';
            letter-spacing: 2px;
        }
        
        QLabel#smisSubtitle {
            color: #9ca3af;
            font-size: 12px !important;
            font-weight: normal !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
            qproperty-alignment: 'AlignCenter';
        }
        
        /* Menu Button - Smaller to prevent overlap */
        QPushButton#menuBtn {
            background-color: transparent;
            color: #9ca3af;
            border: none;
            border-radius: 6px;
            font-size: 12px;
            padding: 4px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
        }
        
        QPushButton#menuBtn:hover {
            background-color: #374151;
            color: #f3f4f6;
        }
        
        /* Search */
        QFrame#searchContainer {
            background-color: #1f2937;
            border: none;
        }
        
        QLineEdit#searchInput {
            background-color: #374151;
            border: 1px solid #4b5563;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 13px;
            color: #f9fafb;
        }
        
        QLineEdit#searchInput:focus {
            border-color: #6366f1;
            background-color: #4b5563;
        }
        
        QLineEdit#searchInput::placeholder {
            color: #6b7280;
        }
        
        /* Navigation */
        QFrame#navContainer {
            background-color: #1f2937;
            border: none;
        }
        
        QPushButton#navButton {
            background-color: transparent;
            border: none;
            border-radius: 10px;
            text-align: left;
            padding: 0px;
            margin: 1px 0px;
            min-height: 44px !important;
            max-height: 44px !important;
            height: 44px !important;
        }
        
        QPushButton#navButton:hover {
            background-color: #374151;
        }
        
        QPushButton#navButton[selected="true"] {
            background-color: #6366f1;
        }
        
        QPushButton#navButton[selected="true"] QLabel#navIcon {
            color: white;
        }
        
        QPushButton#navButton[selected="true"] QLabel#navTitle {
            color: white;
            font-weight: 600;
        }
        
        QLabel#navIcon {
            color: #9ca3af;
            font-size: 16px !important;
            font-weight: normal !important;
        }
        
        QLabel#navTitle {
            color: #e5e7eb;
            font-size: 14px !important;
            font-weight: bold !important;
            font-family: 'Segoe UI', sans-serif;
            margin: 0px;
            padding: 0px;
        }
        
        /* SIDEBAR-SPECIFIC STYLES (isolated from global conflicts) */
        QLabel#sidebarNavIcon {
            color: #9ca3af !important;
            font-size: 16px !important;
            font-weight: normal !important;
            font-family: 'Poppins', sans-serif !important;
            min-height: auto !important;
            background-color: transparent !important;
        }
        
        QLabel#sidebarNavTitle {
            color: #e5e7eb !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            font-family: 'Poppins', sans-serif !important;
            margin: 0px !important;
            padding: 0px 8px !important;
            min-height: 44px !important;
            max-height: 44px !important;
            height: 44px !important;
            background-color: transparent !important;
            qproperty-alignment: 'AlignVCenter | AlignLeft' !important;
            text-align: left !important;
            vertical-align: middle !important;
            line-height: 44px !important;
        }
        
        /* Footer */
        QFrame#footerFrame {
            background-color: #1f2937;
            border: none;
            border-top: 1px solid #374151;
            margin: 0px;
            padding: 8px 0px;
            min-height: 110px !important;
            max-height: 110px !important;
            height: 110px !important;
        }
    """

def get_current_theme_colors():
    """Get current theme colors for consistent text color application."""
    try:
        # Determine dark mode via environment flag; default to light theme
        is_dark = os.getenv('SMIS_DARK_MODE', 'false').lower() in ('1', 'true', 'yes')
        if is_dark:
            return {
                'text_primary': '#e5e7eb',
                'text_secondary': '#9ca3af',
                'background': '#1f2937',
                'surface': '#374151'
            }
        else:
            return {
                'text_primary': '#374151',
                'text_secondary': '#6b7280',
                'background': '#ffffff',
                'surface': '#f9fafb'
            }
    except:
        # Fallback to light theme colors
        return {
            'text_primary': '#374151',
            'text_secondary': '#6b7280',
            'background': '#ffffff',
            'surface': '#f9fafb'
        }

def get_sidebar_modern_style(is_dark_mode=False):
    """Get modern sidebar stylesheet based on theme."""
    if is_dark_mode:
        return get_sidebar_dark_theme_style()
    else:
        return get_sidebar_light_theme_style()

# Export all important functions and constants
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
    'get_global_styles', 'get_attendance_styles',
    # Sidebar styling functions
    'get_sidebar_light_theme_style', 'get_sidebar_dark_theme_style', 'get_sidebar_modern_style',
    'get_current_theme_colors',
    # Constants
    'PRIMARY_COLOR', 'BUTTON_GRADIENT', 'BACKGROUND_GRADIENT', 'FOCUS_BORDER_COLOR',
    'HOVER_BUTTON_COLOR', 'LABEL_BORDER_COLOR', 'COLORS', 'FONT_REGULAR', 'FONT_MEDIUM',
    'FONT_SEMIBOLD', 'FONT_BOLD', 'BUTTON_HEIGHT', 'INPUT_HEIGHT', 'LABEL_HEIGHT', 'COMBOBOX_HEIGHT',
    'SHADOWS', 'RADIUS', 'SPACING_XS', 'SPACING_SM', 'SPACING_MD', 'SPACING_LG', 'SPACING_XL', 'SPACING_XXL'
]
