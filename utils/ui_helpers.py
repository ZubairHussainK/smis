"""Helper utilities for UI components."""
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget

def set_app_icon(widget: QWidget) -> None:
    """
    Set the application icon for any widget (window or dialog).
    
    Args:
        widget: The widget (window or dialog) to set the icon for
    """
    try:
        # Try to find the icon file in resources/icons
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(module_dir, 'resources', 'icons', 'icon.ico')
        
        # Fallback to app_icon.ico if icon.ico is not found
        if not os.path.exists(icon_path):
            icon_path = os.path.join(module_dir, 'resources', 'icons', 'app_icon.ico')
            
        # Set the icon if any of the files exist
        if os.path.exists(icon_path):
            widget.setWindowIcon(QIcon(icon_path))
            return True
        return False
    except Exception as e:
        # Don't crash the application if there's an error with the icon
        print(f"Error setting application icon: {e}")
        return False