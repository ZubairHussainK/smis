#!/usr/bin/env python3
"""
Material Design Icons for SMIS Application
Provides a comprehensive set of Material Design icons using Unicode symbols
and SVG paths for consistent UI design.
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MaterialIcons:
    """Material Design Icons using Unicode symbols and styled fonts."""
    
    # Navigation Icons
    DASHBOARD = "dashboard"
    PEOPLE = "people"
    PERSON = "person"
    SCHOOL = "school"
    ASSIGNMENT = "assignment"
    ASSESSMENT = "assessment"
    EVENT_NOTE = "event_note"
    ANALYTICS = "analytics"
    LOGOUT = "logout"
    SETTINGS = "settings"
    
    # UI Control Icons
    MENU = "menu"
    CLOSE = "close"
    EXPAND_MORE = "expand_more"
    EXPAND_LESS = "expand_less"
    CHEVRON_RIGHT = "chevron_right"
    CHEVRON_LEFT = "chevron_left"
    
    # Action Icons
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"
    SEARCH = "search"
    SAVE = "save"
    CANCEL = "cancel"
    
    # Status Icons
    CHECK_CIRCLE = "check_circle"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    
    # Theme Icons
    LIGHT_MODE = "light_mode"
    DARK_MODE = "dark_mode"
    
    # Unicode mappings for Material Design Icons
    ICON_MAP = {
        # Navigation
        "dashboard": "⚙",  # Dashboard icon
        "people": "👥",  # People/Students
        "person": "👤",  # Single person
        "school": "🏫",  # School building
        "assignment": "📝",  # Assignment/Student List
        "assessment": "📊",  # Reports/Analytics
        "event_note": "📅",  # Calendar/Attendance
        "analytics": "📈",  # Charts/Reports
    "logout": "⤴",  # Logout arrow
    "settings": "⚙",  # Settings gear
        
        # UI Controls
        "menu": "☰",  # Hamburger menu
        "close": "✕",  # Close X
        "expand_more": "⌄",  # Down chevron
        "expand_less": "⌃",  # Up chevron
        "chevron_right": "❯",  # Right chevron
        "chevron_left": "❮",  # Left chevron
        
        # Actions
        "add": "✚",  # Plus sign
        "edit": "✎",  # Edit pencil
        "delete": "🗑",  # Trash can
        "search": "🔍",  # Magnifying glass
        "save": "💾",  # Save disk
        "cancel": "⊘",  # Cancel circle
        
        # Status
        "check_circle": "✅",  # Green checkmark
        "error": "❌",  # Red X
        "warning": "⚠",  # Warning triangle
        "info": "ℹ",  # Info i
        
        # Theme
        "light_mode": "☀",  # Sun
        "dark_mode": "🌙",  # Moon
    }
    
    @classmethod
    def get_icon(cls, icon_name: str, size: int = 20, color: str = "#374151") -> QLabel:
        """
        Create a QLabel with Material Design icon.
        
        Args:
            icon_name: Name of the icon from ICON_MAP
            size: Size of the icon in pixels
            color: Color of the icon (CSS color)
            
        Returns:
            QLabel configured with the material icon
        """
        icon_label = QLabel()
        
        # Get the Unicode character for the icon
        icon_char = cls.ICON_MAP.get(icon_name, "●")  # Default to bullet if not found
        
        icon_label.setText(icon_char)
        icon_label.setFixedSize(size, size)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Apply Material Design styling
        font = QFont("Segoe UI Symbol", size - 4)  # Slightly smaller than container
        font.setWeight(QFont.Normal)
        icon_label.setFont(font)
        
        # Apply color styling
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background: transparent;
                border: none;
                font-family: 'Segoe UI Symbol', 'Material Icons', sans-serif;
                font-size: {size - 4}px;
            }}
        """)
        
        return icon_label
    
    @classmethod
    def get_icon_text(cls, icon_name: str) -> str:
        """Get the Unicode text for an icon."""
        return cls.ICON_MAP.get(icon_name, "●")
    
    @classmethod
    def create_themed_icon(cls, icon_name: str, size: int = 20, is_dark_mode: bool = False) -> QLabel:
        """
        Create a themed icon that adapts to light/dark mode.
        
        Args:
            icon_name: Name of the icon
            size: Size in pixels
            is_dark_mode: Whether to use dark mode colors
            
        Returns:
            QLabel with themed icon
        """
        color = "#e5e7eb" if is_dark_mode else "#374151"
        return cls.get_icon(icon_name, size, color)

class MaterialIconButton:
    """Helper class for creating buttons with Material Design icons."""
    
    @staticmethod
    def create_icon_button(icon_name: str, size: int = 40, is_dark_mode: bool = False) -> str:
        """
        Create CSS for a button with Material Design icon.
        
        Args:
            icon_name: Name of the icon
            size: Button size in pixels
            is_dark_mode: Whether to use dark mode colors
            
        Returns:
            CSS string for the button
        """
        icon_char = MaterialIcons.get_icon_text(icon_name)
        bg_color = "#374151" if not is_dark_mode else "#e5e7eb"
        text_color = "#ffffff" if not is_dark_mode else "#111827"
        hover_bg = "#4b5563" if not is_dark_mode else "#d1d5db"
        
        return f"""
            QPushButton {{
                background: {bg_color};
                border: none;
                border-radius: 8px;
                color: {text_color};
                font-size: {size // 2}px;
                font-weight: bold;
                font-family: 'Segoe UI Symbol', 'Material Icons', sans-serif;
                width: {size}px;
                height: {size}px;
                text-align: center;
            }}
            QPushButton:hover {{
                background: {hover_bg};
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                transform: scale(0.95);
            }}
        """

# Predefined icon configurations for common SMIS use cases
class SMISIcons:
    """Predefined icon configurations for SMIS application."""
    
    # Navigation icons for sidebar
    NAVIGATION = {
        "Dashboard": MaterialIcons.DASHBOARD,
        "Students": MaterialIcons.PEOPLE,
        "Student List": MaterialIcons.ASSIGNMENT,
        "Attendance": MaterialIcons.EVENT_NOTE,
        "Reports": MaterialIcons.ANALYTICS,
    }
    
    # Footer icons
    FOOTER = {
        "Logout": MaterialIcons.LOGOUT,
        "Light Mode": MaterialIcons.LIGHT_MODE,
        "Dark Mode": MaterialIcons.DARK_MODE,
    }
    
    # Menu control icons
    CONTROLS = {
        "Menu": MaterialIcons.MENU,
        "Close": MaterialIcons.CLOSE,
        "Expand": MaterialIcons.EXPAND_MORE,
        "Collapse": MaterialIcons.EXPAND_LESS,
    }
