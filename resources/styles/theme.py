"""
Theme management for the SMIS application.
Contains functions for getting global styles, sidebar styles, and theme colors.
"""

import os
from .constants import (
    COLORS, FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD, FONT_BOLD,
    RADIUS,BUTTON_GRADIENT, BACKGROUND_GRADIENT, FOCUS_BORDER_COLOR, HOVER_BUTTON_COLOR, LABEL_BORDER_COLOR
)

def get_global_styles():
    """
    Return standardized global styles for all app components.
    
    Returns:
        dict: Dictionary of styles for different UI components
    """
    return {
        # Professional Button Styles with PyQt5 compatible design
        'button_primary': f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
                color: {COLORS['white']};
                border: none;
                border-radius: {RADIUS['md']};
                padding-top: 0px;
                padding-bottom: 0px;
                padding-left: 10px;
                padding-right: 10px;
                min-height: 32px;
                max-height: 32px;
                font-family: {FONT_SEMIBOLD};
                font-size: 12px;
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
                background: {COLORS['white']};
                color: {COLORS['gray_700']};
                border: 2px solid {COLORS['gray_300']};
                border-radius: {RADIUS['md']};
                padding-top: 0px;
                padding-bottom: 0px;
                padding-left: 10px;
                padding-right: 10px;
                min-height: 32px;
                max-height: 32px;
                font-family: {FONT_SEMIBOLD};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_light']};
                color: {COLORS['white']};
                border-color: {COLORS['primary_light']};
            }}
            QPushButton:pressed {{
                background: {COLORS['primary_dark']};
                color: {COLORS['white']};
                border-color: {COLORS['primary_dark']};
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_100']};
                color: {COLORS['gray_400']};

                border-color: {COLORS['gray_200']};
            }}
        """,
        'button_success': f"""
            QPushButton {{
                background: {COLORS['success']};
                color: {COLORS['white']};
                border: none;
                border-radius: {RADIUS['md']};
                padding-top: 0px;
                padding-bottom: 0px;
                padding-left: 10px;
                padding-right: 10px;
                min-height: 32px;
                max-height: 32px;
                font-family: {FONT_SEMIBOLD};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #0DA271; /* Slightly darker success */
            }}
            QPushButton:pressed {{
                background: #0B8A61; /* Even darker for press */
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_300']};
                color: {COLORS['gray_500']};
            }}
        """,
        'button_warning': f"""
            QPushButton {{
                background: {COLORS['warning']};
                color: {COLORS['white']};
                border: none;
                border-radius: {RADIUS['md']};
                padding-top: 0px;
                padding-bottom: 0px;
                padding-left: 10px;
                padding-right: 10px;
                min-height: 32px;
                max-height: 32px;
                font-family: {FONT_SEMIBOLD};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #E59009; /* Slightly darker warning */
            }}
            QPushButton:pressed {{
                background: #D58000; /* Even darker for press */
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_300']};
                color: {COLORS['gray_500']};
            }}
        """,
        'button_danger': f"""
            QPushButton {{
                background: {COLORS['danger']};
                color: {COLORS['white']};
                border: none;
                border-radius: {RADIUS['md']};
                padding: 0px;
                min-height: 22px;
                max-height: 22px;
                font-family: {FONT_SEMIBOLD};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #E02D2D; /* Slightly darker danger */
            }}
            QPushButton:pressed {{
                background: #D01F1F; /* Even darker for press */
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_300']};
                color: {COLORS['gray_500']};
            }}
        """,
        'input_standard': f"""
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit {{
                background-color: {COLORS['white']};
                color: {COLORS['gray_900']};
                border: 1px solid {COLORS['gray_300']};
                border-radius: {RADIUS['md']};
                padding: 4px 12px;
                min-height: 22px;
                max-height: 22px;
                selection-background-color: {COLORS['primary_light']};
                selection-color: {COLORS['white']};
                font-family: {FONT_REGULAR};
                font-size: 14px;
            }}
            QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover, QDateTimeEdit:hover {{
                border-color: {COLORS['gray_400']};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QDateTimeEdit:focus {{
                border-color: {COLORS['primary']};
                border-width: 2px;
            }}
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QDateEdit:disabled, QDateTimeEdit:disabled {{
                background-color: {COLORS['gray_100']};
                color: {COLORS['gray_500']};
                border-color: {COLORS['gray_200']};
            }}
        """,
       
    }

def get_attendance_styles():
    """
    Get specialized styles for the attendance module.
    
    Returns:
        dict: Dictionary of styles for attendance-related components
    """
    global_styles = get_global_styles()
    
    input_with_icon_style = f"""
        QLineEdit {{
            background-color: {COLORS['white']};
            color: {COLORS['gray_900']};
            border: 1px solid {COLORS['gray_300']};
            border-radius: {RADIUS['md']};
            padding: 4px 12px 4px 36px;
            min-height: 22px;
            max-height: 22px;
            font-family: {FONT_REGULAR};
            font-size: 14px;
            background-image: url("");
            background-position: left center;
            background-repeat: no-repeat;
            background-origin: content;
            background-clip: padding;
            background-position: 8px center;
        }}
        QLineEdit:hover {{
            border-color: {COLORS['gray_400']};
        }}
        QLineEdit:focus {{
            border-color: {COLORS['primary']};
            border-width: 2px;
        }}
        QLineEdit:disabled {{
            background-color: {COLORS['gray_100']};
            color: {COLORS['gray_500']};
            border-color: {COLORS['gray_200']};
        }}
    """
    
    spinbox_standard_style = f"""
        QSpinBox, QDoubleSpinBox {{
            background-color: {COLORS['white']};
            color: {COLORS['gray_900']};
            border: 1px solid {COLORS['gray_300']};
            border-radius: {RADIUS['md']};
            padding: 4px 12px;
            min-height: 22px;
            max-height: 22px;
            font-family: {FONT_REGULAR};
            font-size: 14px;
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {COLORS['gray_400']};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {COLORS['primary']};
            border-width: 2px;
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {COLORS['gray_300']};
            border-bottom: 1px solid {COLORS['gray_300']};
            border-top-right-radius: {RADIUS['md']};
            background: {COLORS['gray_100']};
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid {COLORS['gray_300']};
            border-bottom-right-radius: {RADIUS['md']};
            background: {COLORS['gray_100']};
        }}
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
            image: url("");
            width: 8px;
            height: 8px;
        }}
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
            image: url("");
            width: 8px;
            height: 8px;
        }}
    """
    
    checkbox_standard_style = f"""
        QCheckBox {{
            spacing: 8px;
            font-family: {FONT_REGULAR};
            font-size: 14px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {COLORS['gray_400']};
            border-radius: {RADIUS['sm']};
        }}
        QCheckBox::indicator:unchecked {{
            background-color: {COLORS['white']};
        }}
        QCheckBox::indicator:unchecked:hover {{
            border-color: {COLORS['primary']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
            image: url("");
        }}
        QCheckBox::indicator:checked:hover {{
            background-color: {COLORS['primary_dark']};
            border-color: {COLORS['primary_dark']};
        }}
        QCheckBox:disabled {{
            color: {COLORS['gray_400']};
        }}
        QCheckBox::indicator:disabled {{
            background-color: {COLORS['gray_100']};
            border-color: {COLORS['gray_300']};
        }}
    """
    
    label_info_style = f"""
        QLabel{{
            color: {COLORS['gray_600']};
            font-family: {FONT_REGULAR};
            font-size: 13px;
            padding: 2px 5px;
            background: transparent;
            border: none;
        }}
    """
    
    return {        
        'search_input': input_with_icon_style,
        'year_spinner': spinbox_standard_style,
        'checkbox_lock': checkbox_standard_style,
        'button_primary': global_styles['button_primary'],
        'button_secondary': global_styles['button_secondary'],
        'button_success': global_styles['button_success'],
        'button_warning': global_styles['button_warning'],
        'info_text': label_info_style.replace('QLabel', '').strip(),
    }

def get_sidebar_light_theme_style():
    """
    Get light theme sidebar style.
    
    Returns:
        str: CSS style for light theme sidebar
    """
    return """
        /* Light Theme Sidebar Styling */
        QFrame#sidebarFrame {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
            max-width: 250px;
            min-width: 250px;
        }
        
        /* School/User Info Area */
        QFrame#schoolInfoFrame {
            background-color: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            border-radius: 0px;
            padding: 12px;
            min-height: 80px;
        }
        
        /* School Name */
        QLabel#schoolNameLabel {
            color: #111827;
            font-size: 18px !important;
            font-weight: 700 !important;
            qproperty-alignment: AlignLeft;
        }
        
        /* User Role */
        QLabel#userRoleLabel {
            color: #6b7280;
            font-size: 12px !important;
            font-weight: normal !important;
            qproperty-alignment: AlignLeft;
        }
        
        /* Module Labels */
        QLabel#moduleTitleLabel {
            color: #4b5563;
            background-color: transparent;
            border: none;
            font-size: 14px !important;
            font-weight: 600;
            padding: 8px 16px;
            margin: 4px 8px;
        }
        
        /* Navigation Buttons */
        QPushButton.sidebarButton {
            background-color: transparent;
            color: #4b5563;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 2px 8px;
            text-align: left;
            font-size: 14px;
            font-weight: normal;
        }
        
        QPushButton.sidebarButton:hover {
            background-color: #f3f4f6;
            color: #1f2937;
        }
        
        QPushButton.sidebarButton:checked,
        QPushButton.sidebarButton:pressed {
            background-color: #e5e7eb;
            color: #111827;
            font-weight: bold;
        }
        
        /* Active Navigation Button */
        QPushButton.sidebarButtonActive {
            background-color: #dbeafe;
            color: #1e40af;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 2px 8px;
            text-align: left;
            font-size: 14px;
            font-weight: bold;
        }
        
        QPushButton.sidebarButtonActive:hover {
            background-color: #bfdbfe;
        }
        
        /* Logout Button */
        QPushButton#logoutButton {
            background-color: transparent;
            color: #ef4444;
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 8px;
            font-weight: bold;
        }
        
        QPushButton#logoutButton:hover {
            background-color: #fee2e2;
        }
        
        /* Version Label */
        QLabel#versionLabel {
            color: #9ca3af;
            font-size: 11px;
            qproperty-alignment: AlignCenter;
            padding: 4px;
        }
    """

def get_sidebar_dark_theme_style():
    """
    Get dark theme sidebar style.
    
    Returns:
        str: CSS style for dark theme sidebar
    """
    return """
        /* Dark Theme Sidebar Styling */
        QFrame#sidebarFrame {
            background-color: #1f2937;
            border-right: 1px solid #374151;
            max-width: 250px;
            min-width: 250px;
        }
        
        /* School/User Info Area */
        QFrame#schoolInfoFrame {
            background-color: #111827;
            border-bottom: 1px solid #374151;
            border-radius: 0px;
            padding: 12px;
            min-height: 80px;
        }
        
        /* School Name */
        QLabel#schoolNameLabel {
            color: #f9fafb;
            font-size: 18px !important;
            font-weight: 700 !important;
            qproperty-alignment: AlignLeft;
        }
        
        /* User Role */
        QLabel#userRoleLabel {
            color: #9ca3af;
            font-size: 12px !important;
            font-weight: normal !important;
            qproperty-alignment: AlignLeft;
        }
        
        /* Module Labels */
        QLabel#moduleTitleLabel {
            color: #d1d5db;
            background-color: transparent;
            border: none;
            font-size: 14px !important;
            font-weight: 600;
            padding: 8px 16px;
            margin: 4px 8px;
        }
        
        /* Navigation Buttons */
        QPushButton.sidebarButton {
            background-color: transparent;
            color: #e5e7eb;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 2px 8px;
            text-align: left;
            font-size: 14px;
            font-weight: normal;
        }
        
        QPushButton.sidebarButton:hover {
            background-color: #374151;
            color: #f9fafb;
        }
        
        QPushButton.sidebarButton:checked,
        QPushButton.sidebarButton:pressed {
            background-color: #4b5563;
            color: #f3f4f6;
            font-weight: bold;
        }
        
        /* Active Navigation Button */
        QPushButton.sidebarButtonActive {
            background-color: #1e40af;
            color: #dbeafe;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 2px 8px;
            text-align: left;
            font-size: 14px;
            font-weight: bold;
        }
        
        QPushButton.sidebarButtonActive:hover {
            background-color: #1e3a8a;
        }
        
        /* Logout Button */
        QPushButton#logoutButton {
            background-color: transparent;
            color: #ef4444;
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 8px;
            font-weight: bold;
        }
        
        QPushButton#logoutButton:hover {
            background-color: #7f1d1d;
        }
        
        /* Version Label */
        QLabel#versionLabel {
            color: #6b7280;
            font-size: 11px;
            qproperty-alignment: AlignCenter;
            padding: 4px;
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
    """
    Get current theme colors for consistent text color application.
    
    Returns:
        dict: Dictionary of theme colors
    """
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
    """
    Get modern sidebar stylesheet based on theme.
    
    Args:
        is_dark_mode (bool, optional): Whether to use dark mode. Defaults to False.
    
    Returns:
        str: CSS style for modern sidebar
    """
    if is_dark_mode:
        return get_sidebar_dark_theme_style()
    else:
        return get_sidebar_light_theme_style()

def get_modern_widget_styles():
    """
    Get comprehensive modern widget styles for forms and pages.
    Replaces inline styling with centralized theming.
    
    Returns:
        str: Complete CSS stylesheet for modern widget styling
    """
    return f"""
        QWidget {{
            background-color: #F1F5F9;
            color: {COLORS['gray_900']};
            font-family: {FONT_REGULAR};
        }}
        
        QGroupBox {{
            background-color: {COLORS['white']};
            border: 1px solid {COLORS['gray_300']};
            border-radius: 8px;
            margin-top: 10px;
            padding: 15px;
            font-weight: bold;
            color: {COLORS['gray_700']};
        }}
        
        QGroupBox::title {{
            color: {COLORS['primary']};
            font-family: {FONT_SEMIBOLD};
            padding: 0 10px;
            top: -7px;
        }}
        
        QLabel {{
            color: {COLORS['gray_700']};
            font-family: {FONT_REGULAR};
        }}
        
        /* Input field styles */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit {{
            background-color: {COLORS['white']};
            color: {COLORS['gray_900']};
            border: 1px solid {COLORS['gray_300']};
            border-radius: 6px;
            padding: 4px 12px;
            min-height: 22px;
            max-height: 22px;
            selection-background-color: {COLORS['primary_light']};
            selection-color: {COLORS['white']};
            font-family: {FONT_REGULAR};
            font-size: 14px;
        }}
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover, QDateTimeEdit:hover {{
            border-color: {COLORS['gray_400']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QDateTimeEdit:focus {{
            border-color: {COLORS['primary']};
            border-width: 2px;
        }}
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QDateEdit:disabled, QDateTimeEdit:disabled {{
            background-color: {COLORS['gray_100']};
            color: {COLORS['gray_500']};
            border-color: {COLORS['gray_200']};
        }}
        
        /* Default button style (secondary) */
        QPushButton {{
            background: {COLORS['white']};
            color: {COLORS['gray_700']};
            border: 2px solid {COLORS['gray_300']};
            border-radius: 6px;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 10px;
            padding-right: 10px;
            min-height: 32px;
            max-height: 32px;
            font-family: {FONT_SEMIBOLD};
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: {COLORS['primary_light']};
            color: {COLORS['white']};
            border-color: {COLORS['primary_light']};
        }}
        QPushButton:pressed {{
            background: {COLORS['primary_dark']};
            color: {COLORS['white']};
            border-color: {COLORS['primary_dark']};
        }}
        QPushButton:disabled {{
            background: {COLORS['gray_100']};
            color: {COLORS['gray_400']};
            border-color: {COLORS['gray_200']};
        }}
        
        /* Primary button style */
        QPushButton[class="primary"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
            color: {COLORS['white']};
            border: none;
            border-radius: 6px;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 10px;
            padding-right: 10px;
            min-height: 32px;
            max-height: 32px;
            font-family: {FONT_SEMIBOLD};
            font-size: 12px;
        }}
        QPushButton[class="primary"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
        }}
        QPushButton[class="primary"]:pressed {{
            background: {COLORS['primary_dark']};
        }}
        QPushButton[class="primary"]:disabled {{
            background: {COLORS['gray_300']};
            color: {COLORS['gray_500']};
        }}
        
        /* Success button style */
        QPushButton[class="success"] {{
            background: {COLORS['success']};
            color: {COLORS['white']};
            border: none;
            border-radius: 6px;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 10px;
            padding-right: 10px;
            min-height: 32px;
            max-height: 32px;
            font-family: {FONT_SEMIBOLD};
            font-size: 14px;
        }}
        QPushButton[class="success"]:hover {{
            background: #0DA271;
        }}
        QPushButton[class="success"]:pressed {{
            background: #0B8A61;
        }}
        QPushButton[class="success"]:disabled {{
            background: {COLORS['gray_300']};
            color: {COLORS['gray_500']};
        }}
        
        /* Warning button style */
        QPushButton[class="warning"] {{
            background: {COLORS['warning']};
            color: {COLORS['white']};
            border: none;
            border-radius: 6px;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 10px;
            padding-right: 10px;
            min-height: 32px;
            max-height: 32px;
            font-family: {FONT_SEMIBOLD};
            font-size: 14px;
        }}
        QPushButton[class="warning"]:hover {{
            background: #E59009;
        }}
        QPushButton[class="warning"]:pressed {{
            background: #D58000;
        }}
        QPushButton[class="warning"]:disabled {{
            background: {COLORS['gray_300']};
            color: {COLORS['gray_500']};
        }}
        
        /* Danger button style */
        QPushButton[class="danger"] {{
            background: {COLORS['danger']};
            color: {COLORS['white']};
            border: none;
            border-radius: 6px;
            padding: 0px;
            min-height: 22px;
            max-height: 22px;
            font-family: {FONT_SEMIBOLD};
            font-size: 14px;
        }}
        QPushButton[class="danger"]:hover {{
            background: #E02D2D;
        }}
        QPushButton[class="danger"]:pressed {{
            background: #D01F1F;
        }}
        QPushButton[class="danger"]:disabled {{
            background: {COLORS['gray_300']};
            color: {COLORS['gray_500']};
        }}
    """