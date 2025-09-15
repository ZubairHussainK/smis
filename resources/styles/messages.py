"""
Message box styling and configuration for SMIS application.
Contains functions for showing various types of message boxes.
"""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from .constants import COLORS
from .utils import resource_path

def configure_message_box(icon_type, title, message, buttons):
    """
    Configure a message box with enhanced styling.
    
    Args:
        icon_type (str): Type of icon to use ('information', 'warning', 'error', 'question', 'critical', 'success')
        title (str): Title of the message box
        message (str): Message to display
        buttons (list): List of buttons to display
        
    Returns:
        QMessageBox: Configured message box
    """
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    # Configure buttons
    buttons_map = {
        "Ok": QMessageBox.Ok,
        "Cancel": QMessageBox.Cancel,
        "Yes": QMessageBox.Yes,
        "No": QMessageBox.No,
        "Save": QMessageBox.Save,
        "Discard": QMessageBox.Discard,
        "Apply": QMessageBox.Apply,
        "Close": QMessageBox.Close,
        "Reset": QMessageBox.Reset,
        "Help": QMessageBox.Help,
        "Open": QMessageBox.Open,
        "Abort": QMessageBox.Abort,
        "Retry": QMessageBox.Retry,
        "Ignore": QMessageBox.Ignore
    }
    
    button_flags = 0
    for button in buttons:
        if button in buttons_map:
            button_flags |= buttons_map[button]
    
    msg_box.setStandardButtons(button_flags)
    
    # Set icon based on type
    if icon_type == 'information':
        msg_box.setIcon(QMessageBox.Information)
    elif icon_type == 'warning':
        msg_box.setIcon(QMessageBox.Warning)
    elif icon_type == 'error':
        msg_box.setIcon(QMessageBox.Critical)
    elif icon_type == 'question':
        msg_box.setIcon(QMessageBox.Question)
    elif icon_type == 'critical':
        msg_box.setIcon(QMessageBox.Critical)
    elif icon_type == 'success':
        # Custom success icon - use information icon as base
        msg_box.setIcon(QMessageBox.Information)
        # If a custom success icon is available, we could set it here
        try:
            success_icon = QIcon(resource_path("resources/icons/success.png"))
            msg_box.setIconPixmap(success_icon.pixmap(64, 64))
        except:
            pass
    
    # Apply custom styling
    msg_box.setStyleSheet(f"""
        QMessageBox {{
            background-color: {COLORS['white']};
            border: 1px solid {COLORS['gray_300']};
            border-radius: 8px;
        }}
        QMessageBox QLabel {{
            color: {COLORS['gray_900']};
            font-size: 14px;
            margin: 12px 0;
        }}
        QMessageBox QPushButton {{
            min-width: 80px;
            min-height: 28px;
            border: 1px solid {COLORS['gray_300']};
            border-radius: 4px;
            padding: 4px 12px;
            background-color: {COLORS['white']};
            color: {COLORS['gray_900']};
        }}
        QMessageBox QPushButton:hover {{
            background-color: {COLORS['gray_100']};
            border-color: {COLORS['gray_400']};
        }}
        QMessageBox QPushButton:pressed {{
            background-color: {COLORS['gray_200']};
        }}
        QMessageBox QPushButton#qt_msgbox_buttonbox_button_0 {{  /* Default button */
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
            border-color: {COLORS['primary']};
        }}
        QMessageBox QPushButton#qt_msgbox_buttonbox_button_0:hover {{
            background-color: {COLORS['primary_dark']};
        }}
    """)
    
    return msg_box

def show_info_message(title, message):
    """
    Show an information message box.
    
    Args:
        title (str): Title of the message box
        message (str): Message to display
        
    Returns:
        int: Result of the message box (which button was pressed)
    """
    msg_box = configure_message_box('information', title, message, ["Ok"])
    
    # Center the message box
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    # Execute and return the result
    return msg_box.exec_()

def show_warning_message(title, message):
    """
    Show a warning message box.
    
    Args:
        title (str): Title of the message box
        message (str): Message to display
        
    Returns:
        int: Result of the message box (which button was pressed)
    """
    msg_box = configure_message_box('warning', title, message, ["Ok"])
    
    # Center the message box
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    # Execute and return the result
    return msg_box.exec_()

def show_error_message(title, message):
    """
    Show an error message box.
    
    Args:
        title (str): Title of the message box
        message (str): Message to display
        
    Returns:
        int: Result of the message box (which button was pressed)
    """
    msg_box = configure_message_box('error', title, message, ["Ok"])
    
    # Center the message box
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    # Execute and return the result
    return msg_box.exec_()

def show_question_message(title, message):
    """
    Show a question message box with Yes/No buttons.
    
    Args:
        title (str): Title of the message box
        message (str): Message to display
        
    Returns:
        int: Result of the message box (which button was pressed)
    """
    msg_box = configure_message_box('question', title, message, ["Yes", "No"])
    
    # Center the message box
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    # Execute and return the result
    return msg_box.exec_()

def show_critical_message(title, message):
    """
    Show a critical message box.
    
    Args:
        title (str): Title of the message box
        message (str): Message to display
        
    Returns:
        int: Result of the message box (which button was pressed)
    """
    msg_box = configure_message_box('critical', title, message, ["Ok"])
    
    # Center the message box
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    # Execute and return the result
    return msg_box.exec_()

def show_success_message(title, message):
    """
    Show a success message box.
    
    Args:
        title (str): Title of the message box
        message (str): Message to display
        
    Returns:
        int: Result of the message box (which button was pressed)
    """
    msg_box = configure_message_box('success', title, message, ["Ok"])
    
    # Center the message box
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    # Execute and return the result
    return msg_box.exec_()

def show_confirmation_message(title, message):
    """
    Show a confirmation message box with Yes/No buttons.
    
    Args:
        title (str): Title of the message box
        message (str): Message to display
        
    Returns:
        bool: True if Yes was clicked, False otherwise
    """
    return show_question_message(title, message) == QMessageBox.Yes

def show_save_confirmation(filename="file"):
    """
    Show a confirmation message for saving changes.
    
    Args:
        filename (str, optional): Name of the file being saved. Defaults to "file".
        
    Returns:
        bool: True if Yes was clicked, False otherwise
    """
    return show_confirmation_message("Save Changes?", f"Do you want to save changes to {filename}?")

def show_delete_confirmation(item_name="item"):
    """
    Show a confirmation message for deleting an item.
    
    Args:
        item_name (str, optional): Name of the item being deleted. Defaults to "item".
        
    Returns:
        bool: True if Yes was clicked, False otherwise
    """
    return show_confirmation_message("Confirm Deletion", f"Are you sure you want to delete this {item_name}?\n\nThis action cannot be undone.")