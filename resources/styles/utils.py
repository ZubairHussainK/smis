"""
Utility functions for SMIS application styling.
Contains resource path resolution, shadow effects, and other styling utilities.
"""

import os
import sys
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and PyInstaller.
    
    Args:
        relative_path (str): Relative path to the resource
        
    Returns:
        str: Absolute path to the resource
    """
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running in normal Python environment
        return os.path.join(os.path.abspath("."), relative_path)

def applyShadow(widget, x_offset=0, y_offset=10, blur_radius=25, color=QColor(0, 0, 0, 100)):
    """
    Apply a drop shadow effect to a widget.
    
    Args:
        widget (QWidget): The widget to apply the shadow to
        x_offset (int): Horizontal offset of the shadow
        y_offset (int): Vertical offset of the shadow
        blur_radius (int): Blur radius of the shadow
        color (QColor): Color of the shadow
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(color)
    shadow.setOffset(x_offset, y_offset)
    widget.setGraphicsEffect(shadow)

def applyFonts(widget: QWidget, font_name: str = None, size: int = 12, bold: bool = True) -> None:
    """
    Apply custom fonts to a widget.
    
    Args:
        widget (QWidget): The widget to apply the font to
        font_name (str, optional): Name of the font. Defaults to None.
        size (int, optional): Size of the font. Defaults to 12.
        bold (bool, optional): Whether to make the font bold. Defaults to True.
    """
    font = QFont(font_name if font_name else widget.font().family(), size)
    font.setBold(bold)
    widget.setFont(font)

def set_widget_height(widget, height=28):
    """
    Set a fixed height for a widget.
    
    Args:
        widget (QWidget): The widget to set the height for
        height (int, optional): Height in pixels. Defaults to 28.
    """
    widget.setFixedHeight(height)

class LayoutUtils:
    """Utilities for layout management."""
    
    @staticmethod
    def apply_margins(layout, margins):
        """Apply margins to a layout."""
        layout.setContentsMargins(margins, margins, margins, margins)
        
    @staticmethod
    def apply_spacing(layout, spacing):
        """Apply spacing to a layout."""
        layout.setSpacing(spacing)
        
    @staticmethod
    def center_widget(widget, parent=None):
        """Center a widget relative to its parent."""
        if parent:
            geometry = parent.geometry()
            x = (geometry.width() - widget.width()) // 2
            y = (geometry.height() - widget.height()) // 2
            widget.move(x, y)