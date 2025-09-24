"""
SMIS Update Integration
======================
Easy integration of update checking into your main SMIS application.
"""

import logging
from PyQt5.QtCore import QTimer
from services.pyqt_updater import check_for_updates_with_gui
from config.update_config import AUTO_CHECK_ON_STARTUP


class UpdateIntegration:
    """Integration class for adding update checking to SMIS."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.update_timer = None
    
    def setup_update_checking(self):
        """Setup automatic update checking."""
        try:
            if AUTO_CHECK_ON_STARTUP:
                # Check for updates 5 seconds after the main window is shown
                # This gives the application time to fully load
                self.update_timer = QTimer()
                self.update_timer.singleShot(5000, self.check_for_updates)
                
                self.logger.info("Update checking scheduled for 5 seconds after startup")
            
        except Exception as e:
            self.logger.error(f"Error setting up update checking: {e}")
    
    def check_for_updates(self):
        """Check for updates and show dialog if available."""
        try:
            self.logger.info("Checking for updates...")
            check_for_updates_with_gui(self.main_window)
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
    
    def manual_update_check(self):
        """Manual update check triggered by user."""
        try:
            self.logger.info("Manual update check requested")
            check_for_updates_with_gui(self.main_window)
            
        except Exception as e:
            self.logger.error(f"Error in manual update check: {e}")


def integrate_updates_into_main_window(main_window):
    """
    Integrate update checking into the main window.
    Call this from your main window's __init__ method.
    
    Args:
        main_window: Your main PyQt5 window instance
    """
    try:
        integration = UpdateIntegration(main_window)
        integration.setup_update_checking()
        
        # Store the integration object so it doesn't get garbage collected
        main_window._update_integration = integration
        
        return integration
        
    except Exception as e:
        logging.error(f"Error integrating updates: {e}")
        return None


def add_update_menu_item(menu_bar, integration):
    """
    Add 'Check for Updates' menu item to your application.
    
    Args:
        menu_bar: QMenuBar instance
        integration: UpdateIntegration instance
    """
    try:
        from PyQt5.QtWidgets import QAction
        from PyQt5.QtGui import QKeySequence
        
        # Find or create Help menu
        help_menu = None
        for action in menu_bar.actions():
            if action.text().lower() == 'help':
                help_menu = action.menu()
                break
        
        if not help_menu:
            help_menu = menu_bar.addMenu('Help')
        
        # Add separator if menu has items
        if help_menu.actions():
            help_menu.addSeparator()
        
        # Add update check action
        update_action = QAction('Check for Updates...', menu_bar.parent())
        update_action.setShortcut(QKeySequence('Ctrl+U'))
        update_action.triggered.connect(integration.manual_update_check)
        
        help_menu.addAction(update_action)
        
        logging.info("Update menu item added to Help menu")
        
    except Exception as e:
        logging.error(f"Error adding update menu item: {e}")


def add_update_button_to_toolbar(toolbar, integration):
    """
    Add update check button to toolbar.
    
    Args:
        toolbar: QToolBar instance
        integration: UpdateIntegration instance
    """
    try:
        from PyQt5.QtWidgets import QAction
        from PyQt5.QtGui import QIcon
        
        update_action = QAction('Check Updates', toolbar.parent())
        update_action.setToolTip('Check for application updates')
        
        # Try to set an icon (optional)
        try:
            update_action.setIcon(QIcon.fromTheme('system-software-update'))
        except:
            pass
        
        update_action.triggered.connect(integration.manual_update_check)
        toolbar.addAction(update_action)
        
        logging.info("Update button added to toolbar")
        
    except Exception as e:
        logging.error(f"Error adding update button: {e}")


# Example usage for your main window:
"""
# In your main window class __init__ method:

def __init__(self):
    super().__init__()
    self.setupUi()
    
    # Add update integration
    from services.update_integration import integrate_updates_into_main_window, add_update_menu_item
    
    integration = integrate_updates_into_main_window(self)
    if integration:
        add_update_menu_item(self.menubar, integration)

# That's it! Your application now has automatic update checking.
"""