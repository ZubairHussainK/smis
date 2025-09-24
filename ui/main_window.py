"""Main window UI implementation with professional design and security."""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
                           QListWidget, QStatusBar, QLabel, QFrame, QMenuBar, QMenu, QAction,
                           QMessageBox, QDialog, QShortcut)
from PyQt5.QtCore import Qt, QEvent, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QKeySequence
import logging
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from config.settings import Config, SHORTCUTS
from version import __version__, VERSION_SHORT
from ui.pages.dashboard import DashboardPage
from ui.pages.student import StudentPage
from ui.pages.student_list import StudentListPage
from ui.pages.attendance import AttendancePage
from ui.pages.reports import ReportsPage
from ui.components.sidebar import ModernSidebar
from core.auth import get_auth_manager
from utils.logger import log_audit_event, log_security_event
from services.backup_service import get_backup_manager

class MainWindow(QMainWindow):
    """Main application window with enhanced security and user management."""
    
    # Signals
    user_logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_user = None
        self.auth_manager = get_auth_manager()
        self.backup_manager = get_backup_manager()
        
        try:
            self.setWindowTitle(f"{Config.WINDOW_TITLE} v{__version__}")
            self.setGeometry(*Config.WINDOW_GEOMETRY)
            
            # Set window size policy to prevent unwanted resizing
            self.setMinimumSize(1000, 700)  # Minimum reasonable size
            self.resize(1200, 800)  # Default size
            
            # Allow fullscreen but prevent random resizing
            self.setWindowState(Qt.WindowNoState)
            
            self._init_ui()
            
            # Initialize persistent protection system
            self._setup_persistent_protection()
            self._create_menu_bar()
            self._setup_status_bar()
            self._setup_shortcuts()
            self._load_stylesheet()
            
            # Install event filter on sidebar to prevent unwanted arrow key navigation
            self.sidebar.installEventFilter(self)
            
            # Setup session timeout timer
            self._setup_session_timeout()
            
            logging.debug("MainWindow initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing MainWindow: {e}")
            raise

    def set_current_user(self, user):
        """Set the current user and update UI accordingly."""
        self.current_user = user
        self._update_ui_for_user()
        
        # Pass current user to all pages that support it
        if hasattr(self, 'student_page') and hasattr(self.student_page, 'set_current_user'):
            self.student_page.set_current_user(user)
        if hasattr(self, 'student_list_page') and hasattr(self.student_list_page, 'set_current_user'):
            self.student_list_page.set_current_user(user)
        # Add other pages as needed
        
        # Log the session start
        log_audit_event("session_started", user.id, "application")
    
    def _update_ui_for_user(self):
        """Update UI elements based on current user permissions."""
        if not self.current_user:
            return
        
        # Update window title with user info and version
        base_title = f"{Config.WINDOW_TITLE} v{__version__}"
        title = f"{base_title} - {self.current_user.full_name or self.current_user.username}"
        if self.current_user.role:
            title += f" ({self.current_user.role.title()})"
        self.setWindowTitle(title)
        
        # Update sidebar with user info
        if hasattr(self.sidebar, 'update_user_info'):
            self.sidebar.update_user_info(self.current_user)
        
        # Update menu bar based on permissions
        self._update_menu_permissions()
        
        # Update status bar - show user info with version
        user_info = f"User: {self.current_user.username} | Role: {self.current_user.role.title()} | v{__version__}"
        self.user_label.setText(user_info)
    
    def _create_menu_bar(self):
        """Create enhanced menu bar with user management."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('&File')
        
        # Backup actions (admin only)
        self.backup_action = QAction('&Create Backup', self)
        self.backup_action.setShortcut(QKeySequence(SHORTCUTS['backup']))
        self.backup_action.triggered.connect(self._create_backup)
        file_menu.addAction(self.backup_action)
        
        self.restore_action = QAction('&Restore from Backup', self)
        self.restore_action.triggered.connect(self._restore_backup)
        file_menu.addAction(self.restore_action)
        
        file_menu.addSeparator()
        
        # Import/Export actions
        self.import_action = QAction('&Import Data', self)
        self.import_action.triggered.connect(self._import_data)
        file_menu.addAction(self.import_action)
        
        self.export_action = QAction('&Export Data', self)
        self.export_action.triggered.connect(self._export_data)
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # User Menu
        user_menu = menubar.addMenu('&User')
        
        # Change password
        change_password_action = QAction('&Change Password', self)
        change_password_action.triggered.connect(self._change_password)
        user_menu.addAction(change_password_action)
        
        # User management (admin only)
        self.user_management_action = QAction('&Manage Users', self)
        self.user_management_action.triggered.connect(self._manage_users)
        user_menu.addAction(self.user_management_action)
        
        user_menu.addSeparator()
        
        # Logout action
        logout_action = QAction('&Logout', self)
        logout_action.setShortcut(QKeySequence(SHORTCUTS['logout']))
        logout_action.triggered.connect(self._logout)
        user_menu.addAction(logout_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu('&Tools')
        
        # Data integrity check
        self.integrity_check_action = QAction('&Data Integrity Check', self)
        self.integrity_check_action.triggered.connect(self._run_integrity_check)
        tools_menu.addAction(self.integrity_check_action)
        
        # Activity log viewer (admin only)
        self.activity_log_action = QAction('&View Activity Log', self)
        self.activity_log_action.triggered.connect(self._view_activity_log)
        tools_menu.addAction(self.activity_log_action)
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _update_menu_permissions(self):
        """Update menu items based on user permissions."""
        if not self.current_user:
            return
        
        # Admin-only actions
        admin_actions = [
            self.backup_action,
            self.restore_action,
            self.user_management_action,
            self.activity_log_action
        ]
        
        is_admin = self.current_user.has_permission('user_management')
        for action in admin_actions:
            action.setVisible(is_admin)
        
        # Check other permissions
        has_backup_permission = self.current_user.has_permission('backup')
        self.backup_action.setVisible(has_backup_permission)
        self.restore_action.setVisible(has_backup_permission)
        
        has_data_management = self.current_user.has_permission('create') or self.current_user.has_permission('update')
        self.integrity_check_action.setVisible(has_data_management)
    
    def _setup_session_timeout(self):
        """Setup session timeout mechanism."""
        from config.security import SecurityConfig
        
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self._handle_session_timeout)
        
        # Set timeout (convert minutes to milliseconds)
        timeout_ms = SecurityConfig.SESSION_TIMEOUT_MINUTES * 60 * 1000
        self.session_timer.start(timeout_ms)
        
        # Reset timer on user activity
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filter events to reset session timeout on user activity."""
        # Reset session timer on user activity
        if event.type() in [QEvent.KeyPress, QEvent.MouseButtonPress, QEvent.MouseMove]:
            if hasattr(self, 'session_timer'):
                from config.security import SecurityConfig
                timeout_ms = SecurityConfig.SESSION_TIMEOUT_MINUTES * 60 * 1000
                self.session_timer.start(timeout_ms)
        
        return super().eventFilter(obj, event)
    
    def _handle_session_timeout(self):
        """Handle session timeout."""
        log_security_event("session_timeout", self.current_user.id if self.current_user else None)
        
        QMessageBox.warning(
            self,
            "Session Timeout",
            "Your session has timed out for security reasons. You will be logged out."
        )
        
        self._logout()
    
    def _create_backup(self):
        """Create database backup."""
        try:
            if not self.current_user.has_permission('backup'):
                QMessageBox.warning(self, "Permission Denied", "You don't have permission to create backups.")
                return
            
            backup_path = self.backup_manager.create_backup()
            
            log_audit_event("backup_created", self.current_user.id, "database", backup_path)
            
            QMessageBox.information(
                self,
                "Backup Created",
                f"Database backup created successfully:\\n{backup_path}"
            )
            
        except Exception as e:
            logging.error(f"Backup creation failed: {e}")
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup:\\n{str(e)}")
    
    def _restore_backup(self):
        """Restore from backup."""
        # Implementation would include file dialog to select backup
        QMessageBox.information(self, "Restore Backup", "Backup restore functionality will be implemented.")
    
    def _import_data(self):
        """Import data from external source."""
        QMessageBox.information(self, "Import Data", "Data import functionality will be implemented.")
    
    def _export_data(self):
        """Export data to external format."""
        QMessageBox.information(self, "Export Data", "Data export functionality will be implemented.")
    
    def _change_password(self):
        """Change user password."""
        QMessageBox.information(self, "Change Password", "Password change functionality will be implemented.")
    
    def _manage_users(self):
        """Manage users (admin only)."""
        if not self.current_user.has_permission('user_management'):
            QMessageBox.warning(self, "Permission Denied", "You don't have permission to manage users.")
            return
        
        QMessageBox.information(self, "Manage Users", "User management interface will be implemented.")
    
    def _run_integrity_check(self):
        """Run data integrity check."""
        try:
            from models.database import Database
            db = Database()
            results = db.run_data_integrity_check()
            
            log_audit_event("integrity_check_run", self.current_user.id, "database")
            
            message = f"Data Integrity Check Results:\\n\\n"
            message += f"Passed: {results['passed']}\\n"
            message += f"Failed: {results['failed']}\\n"
            message += f"Warnings: {results['warnings']}\\n\\n"
            
            for check in results['checks']:
                status_icon = "✓" if check['status'] == 'passed' else "✗" if check['status'] == 'failed' else "⚠"
                message += f"{status_icon} {check['name']}: {check['details']}\\n"
            
            QMessageBox.information(self, "Data Integrity Check", message)
            
        except Exception as e:
            logging.error(f"Integrity check failed: {e}")
            QMessageBox.critical(self, "Integrity Check Error", f"Failed to run integrity check:\\n{str(e)}")
    
    def _view_activity_log(self):
        """View activity log (admin only)."""
        if not self.current_user.has_permission('user_management'):
            QMessageBox.warning(self, "Permission Denied", "You don't have permission to view activity logs.")
            return
        
        QMessageBox.information(self, "Activity Log", "Activity log viewer will be implemented.")
    
    def _logout(self):
        """Logout current user."""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.current_user:
                log_audit_event("user_logout_requested", self.current_user.id, "session")
            
            self.auth_manager.logout()
            self.close()
    
    def _show_about(self):
        """Show about dialog."""
        from version import __version__, __app_name__, __build_date__, __author__
        
        QMessageBox.about(
            self,
            "About SMIS",
            f"{__app_name__}\\n"
            f"Version {__version__}\\n"
            f"Build Date: {__build_date__}\\n\\n"
            f"A comprehensive school management solution with enhanced security features.\\n\\n"
            f"Developed by: {__author__}\\n\\n"
            f"Current User: {self.current_user.username if self.current_user else 'Unknown'}\\n"
            f"Role: {self.current_user.role.title() if self.current_user else 'Unknown'}"
        )
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        from PyQt5.QtWidgets import QShortcut
        
        # Refresh shortcut
        refresh_shortcut = QShortcut(QKeySequence(SHORTCUTS['refresh']), self)
        refresh_shortcut.activated.connect(self._refresh_current_page)
        
        # Search shortcut
        search_shortcut = QShortcut(QKeySequence(SHORTCUTS['search']), self)
        search_shortcut.activated.connect(self._focus_search)
    
    def _refresh_current_page(self):
        """Refresh the current page."""
        current_widget = self.content_stack.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
    
    def _focus_search(self):
        """Focus on search input if available."""
        current_widget = self.content_stack.currentWidget()
        if hasattr(current_widget, 'focus_search'):
            current_widget.focus_search()

    def _init_ui(self):
        """Initialize the main UI components."""
        try:
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QHBoxLayout(main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # Create enhanced modern sidebar
            self.sidebar = ModernSidebar()
            self.sidebar.setObjectName("ModernSidebar")
            self.sidebar.page_changed.connect(self._switch_page)
            self.sidebar.theme_changed.connect(self._on_theme_changed)
            self.sidebar.logout_requested.connect(self._handle_logout)

            # Professional Content Area
            content_container = QFrame()
            content_container.setObjectName("contentContainer")
            content_container.setStyleSheet("""
                QFrame#contentContainer {
                    background-color: #F8FAFC;
                    border: none;
                }
            """)
            content_layout = QVBoxLayout(content_container)
            content_layout.setContentsMargins(0, 0, 0, 0)

            self.content_stack = QStackedWidget()
            self.content_stack.setStyleSheet("""
                QStackedWidget {
                    background-color: #F8FAFC;
                    border: none;
                }
            """)

            # Initialize pages
            from ui.pages.mother_reg import MotherRegPage
            from ui.pages.settings import SettingsPage
            self.dashboard_page = DashboardPage()
            self.student_page = StudentPage()
            self.student_list_page = StudentListPage()
            self.mother_reg_page = MotherRegPage()
            self.attendance_page = AttendancePage()
            self.reports_page = ReportsPage()
            self.settings_page = SettingsPage()
            # Add pages to stack
            self.content_stack.addWidget(self.dashboard_page)
            self.content_stack.addWidget(self.student_page)
            self.content_stack.addWidget(self.student_list_page)
            self.content_stack.addWidget(self.mother_reg_page)
            self.content_stack.addWidget(self.attendance_page)
            self.content_stack.addWidget(self.reports_page)
            self.content_stack.addWidget(self.settings_page)

            content_layout.addWidget(self.content_stack)

            main_layout.addWidget(self.sidebar)
            main_layout.addWidget(content_container)

            # Set initial page
            self.content_stack.setCurrentIndex(0)
        except Exception as e:
            logging.error(f"Error in _init_ui: {e}")
            raise

    def _switch_page(self, index):
        """Switch to the selected page from the sidebar."""
        # Map sidebar index to content_stack index
        # Dashboard, Students, Student List, Mother Reg, Attendance, Reports, Settings
        if index == 6:  # Settings
            self.content_stack.setCurrentWidget(self.settings_page)
        elif index == 0:
            self.content_stack.setCurrentWidget(self.dashboard_page)
        elif index == 1:
            self.content_stack.setCurrentWidget(self.student_page)
        elif index == 2:
            self.content_stack.setCurrentWidget(self.student_list_page)
        elif index == 3:
            self.content_stack.setCurrentWidget(self.mother_reg_page)
        elif index == 4:
            self.content_stack.setCurrentWidget(self.attendance_page)
        elif index == 5:
            self.content_stack.setCurrentWidget(self.reports_page)

    def _setup_status_bar(self):
        """Set up the status bar with user information and version."""
        try:
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            
            # Add user label to right side of status bar (will include version after login)
            self.user_label = QLabel(f"Not logged in | v{__version__}")
            self.user_label.setStyleSheet("QLabel { color: #333; font-weight: bold; padding: 2px 8px; }")
            self.status_bar.addPermanentWidget(self.user_label)
            
            self.status_bar.showMessage("Ready")
        except Exception as e:
            logging.error(f"Error setting up status bar: {e}")
            raise

    def _load_stylesheet(self):
        """Apply the application stylesheet without interfering with sidebar."""
        try:
            # Apply normal global styles
            from resources.styles import setAppStyle
            setAppStyle(self)
            
            # Let sidebar handle its own styling completely
            print("✅ Global styles applied - sidebar manages its own fonts")
            
            logging.debug("Styles applied successfully - sidebar is self-managed")
        except Exception as e:
            logging.error(f"Error applying styles: {e}")
            pass
    
    def _setup_persistent_protection(self):
        """Setup minimal sidebar protection that doesn't interfere with sidebar's own protection."""
        try:
            print("🔒 Setting up MINIMAL sidebar protection system...")
            
            # No aggressive timers - let the sidebar handle its own protection
            # Just set up a fallback protection that runs very infrequently
            self.fallback_protection_timer = QTimer()
            self.fallback_protection_timer.timeout.connect(self._fallback_sidebar_protection)
            
            # Run fallback protection every 10 seconds (very infrequent)
            self.fallback_protection_timer.start(10000)  # 10 seconds interval
            
            print("✅ MINIMAL protection system ACTIVATED!")
            
        except Exception as e:
            print(f"⚠️ Error setting up minimal protection: {e}")
            
    def _fallback_sidebar_protection(self):
        """Minimal fallback protection that runs infrequently."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar and self.sidebar.isVisible():
                # Only ensure sidebar still has its style - don't force updates
                if not self.sidebar.styleSheet():
                    self.sidebar.setStyleSheet(self.sidebar._get_modern_style())
        except Exception as e:
            pass  # Silent failure for fallback protection
            
    def _nuclear_sidebar_protection(self):
        """Nuclear-level sidebar protection against global style interference."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar and self.sidebar.isVisible():
                # FORCE sidebar to use only its own styles
                self.sidebar.setStyleSheet(self.sidebar._get_modern_style())
                
                # FORCE all labels to maintain their font sizes
                self.sidebar._refresh_font_sizes()
                
                # FORCE complete style reapplication
                self.sidebar._apply_theme()
                
                # FORCE update cycles to make changes stick
                self.sidebar.update()
                self.sidebar.repaint()
                
                # FORCE update all child widgets too
                for child in self.sidebar.findChildren(QLabel):
                    child.update()
                    child.repaint()
                    
        except (RuntimeError, AttributeError):
            pass

    def _ultra_nuclear_sidebar_protection(self):
        """Simplified sidebar protection for theme changes."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar and self.sidebar.isVisible():
                # Let the sidebar handle its own protection - just a minimal backup
                if not self.sidebar.styleSheet():
                    self.sidebar.setStyleSheet(self.sidebar._get_modern_style())
                    
        except (RuntimeError, AttributeError) as e:
            pass

    def _switch_page(self, index):
        """Switch between different pages in the stack."""
        try:
            # Check for unsaved changes before switching (example for student page)
            if (index == 1 and 
                hasattr(self.student_page, 'has_unsaved_changes') and 
                self.student_page.has_unsaved_changes()):
                self.sidebar.setCurrentRow(self.content_stack.currentIndex())
                return
            self.content_stack.setCurrentIndex(index)
            # Refresh page data if needed
            if index == 1:
                self.student_page.refresh_data()
            elif index == 2:
                self.student_list_page.refresh_data()
            elif index == 3:
                if hasattr(self, 'mother_reg_page') and hasattr(self.mother_reg_page, 'refresh_data'):
                    self.mother_reg_page.refresh_data()
            elif index == 4:
                self.attendance_page.refresh_data()
            elif index == 5:
                self.reports_page.refresh_data()
        except Exception as e:
            logging.error(f"Error switching page: {e}")
            raise

    def eventFilter(self, obj, event):
        """Filter events to prevent unwanted sidebar navigation and reset session timeout."""
        # Reset session timer on general user activity
        if event.type() in [QEvent.KeyPress, QEvent.MouseButtonPress, QEvent.MouseMove]:
            if hasattr(self, 'session_timer'):
                from config.security import SecurityConfig
                timeout_ms = SecurityConfig.SESSION_TIMEOUT_MINUTES * 60 * 1000
                self.session_timer.start(timeout_ms)

        if obj == self.sidebar and event.type() == QEvent.KeyPress:
            # If we're on the attendance page and arrow keys are pressed,
            # ignore them to prevent sidebar navigation
            if (self.content_stack.currentIndex() == 4 and  # Attendance page index
                event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]):
                # Check if focus is within the attendance page
                current_widget = self.focusWidget()
                if current_widget and hasattr(self.attendance_page, 'calendar'):
                    attendance_widgets = [
                        self.attendance_page,
                        self.attendance_page.calendar,
                        self.attendance_page.students_table,
                        self.attendance_page.search_input
                    ]
                    # Check if any parent of current widget is in attendance page
                    widget = current_widget
                    while widget:
                        if widget in attendance_widgets:
                            return True  # Block the event from reaching sidebar
                        widget = widget.parent()
        
        # For all other events, use default behavior
        return super().eventFilter(obj, event)
    
    def _on_theme_changed(self, is_dark_mode):
        """Handle theme change from sidebar."""
        print(f"🎯 Theme change detected: {'Dark' if is_dark_mode else 'Light'} mode")
        
        # Store current sidebar state
        sidebar_expanded = False
        if hasattr(self, 'sidebar') and self.sidebar:
            current_width = self.sidebar.width()
            sidebar_expanded = (current_width >= (self.sidebar.expanded_width - 10))
        
        # Apply theme to the entire application
        if is_dark_mode:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
            
        # Let sidebar handle its own theme changes
        print("✅ Theme applied - sidebar manages its own updates")
        
        # Restore visibility state
        if sidebar_expanded:
            QTimer.singleShot(100, self._safe_sidebar_show_text)
        else:
            QTimer.singleShot(100, self._safe_sidebar_hide_text)
                
    def _safe_sidebar_style_refresh(self):
        """Safely refresh sidebar style."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar.isVisible():
                self.sidebar.setStyleSheet(self.sidebar._get_modern_style())
        except (RuntimeError, AttributeError):
            pass
            
    def _safe_sidebar_font_refresh(self):
        """Safely refresh sidebar fonts."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar.isVisible():
                self.sidebar._refresh_font_sizes()
        except (RuntimeError, AttributeError):
            pass
            
    def _safe_sidebar_apply_theme(self):
        """Safely apply sidebar theme."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar.isVisible():
                self.sidebar._apply_theme()
        except (RuntimeError, AttributeError):
            pass
            
    def _safe_sidebar_show_text(self):
        """Safely show sidebar text elements."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar.isVisible():
                self.sidebar._show_text_elements()
        except (RuntimeError, AttributeError):
            pass
            
    def _safe_sidebar_hide_text(self):
        """Safely hide sidebar text elements."""
        try:
            if hasattr(self, 'sidebar') and self.sidebar.isVisible():
                self.sidebar._hide_text_elements()
        except (RuntimeError, AttributeError):
            pass
            
    def _apply_dark_theme(self):
        """Apply dark theme to the main window."""
        # Update main window styling for dark theme - don't interfere with sidebar
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1f2937;
                color: #f9fafb;
            }
            /* Only style content container frames */
            QFrame#contentContainer {
                background-color: #1f2937;
                border: none;
            }
            QStackedWidget {
                background-color: #1f2937;
                border: none;
            }
            /* Avoid affecting any sidebar components */
            QFrame[objectName="ModernSidebar"] * {
                /* Let sidebar handle its own styling */
            }
        """)
        
    def _apply_light_theme(self):
        """Apply light theme to the main window."""
        # Update main window styling for light theme - don't interfere with sidebar
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #111827;
            }
            /* Only style content container frames */
            QFrame#contentContainer {
                background-color: #ffffff;
                border: none;
            }
            QStackedWidget {
                background-color: #F8FAFC;
                border: none;
            }
            /* Avoid affecting any sidebar components */
            QFrame[objectName="ModernSidebar"] * {
                /* Let sidebar handle its own styling */
            }
        """)
        
    def _handle_logout(self):
        """Handle logout request from sidebar."""
        reply = QMessageBox.question(
            self, 
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.user_logout_requested.emit()
            
    def closeEvent(self, event):
        """Clean up persistent protection timers on close."""
        try:
            print("🛑 Stopping persistent protection timers...")
            
            # Stop all protection timers
            if hasattr(self, 'persistent_protection_timer'):
                self.persistent_protection_timer.stop()
                
            if hasattr(self, 'emergency_protection_timer'):
                self.emergency_protection_timer.stop()
                
            print("✅ Protection timers stopped successfully")
            
        except Exception as e:
            print(f"⚠️ Error stopping protection timers: {e}")
            
        # Call parent close event
        super().closeEvent(event)
