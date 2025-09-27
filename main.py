import sys
import logging
import os
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont

# Robust dotenv import with fallback
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    # Fallback when dotenv is not available
    def load_dotenv():
        """Fallback function when python-dotenv is not available"""
        pass
    DOTENV_AVAILABLE = False

try:
    # Import Qt constants properly for Pylance
    from PyQt5.QtCore import Qt
    from PyQt5 import QtCore
    from PyQt5.QtGui import QColor
    # Define constants for better type checking
    AA_EnableHighDpiScaling = getattr(Qt, 'AA_EnableHighDpiScaling', 0x1000000)
    AA_UseHighDpiPixmaps = getattr(Qt, 'AA_UseHighDpiPixmaps', 0x2000000)
except ImportError:
    # Fallback values
    from PyQt5.QtGui import QColor
    AA_EnableHighDpiScaling = 0x1000000
    AA_UseHighDpiPixmaps = 0x2000000


# Load environment variables first (if available)
try:
    load_dotenv()
    if DOTENV_AVAILABLE:
        logging.info("Environment variables loaded successfully")
    else:
        logging.info("Running without dotenv support")
except Exception as e:
    logging.warning(f"Could not load environment variables: {e}")

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import version information
from version import __version__, VERSION_FULL

# CRITICAL: Import security system FIRST
from core.security_manager import secure_app_startup, register_application

# Only import other modules if security check passes
def import_app_modules():
    """Import application modules only after security validation."""
    global MainWindow, LoginWindow, Database, setup_logging, log_security_event
    global log_audit_event, setup_fonts, Config, get_auth_manager
    global get_backup_manager, SMISException, handle_exception
    
    from ui.main_window import MainWindow
    from ui.login_window import LoginWindow
    from models.database import Database
    from utils.logger import setup_logging, log_security_event, log_audit_event
    from utils.fonts import setup_fonts
    from core.auth import get_auth_manager
    from services.backup_service import get_backup_manager
    from core.exceptions import SMISException, handle_exception

    # Import config with proper error handling for PyInstaller
    try:
        from config.settings import Config
        print(f"✅ Config loaded successfully from: {Config.CONFIG_DIR}")
    except ImportError as e:
        print(f"❌ Config import error: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        if hasattr(sys, '_MEIPASS'):
            print(f"PyInstaller temp path: {sys._MEIPASS}")
        raise

logger = logging.getLogger(__name__)


class SMISApplication:
    
    def __init__(self) -> None:

        """Initialize the SMIS application."""
        # Type annotations for better IDE support
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        self.current_user: Optional[Dict[str, Any]] = None
        self.auth_manager = None
        self.backup_manager = None
        
        logger.info("SMISApplication instance created")
        
    def initialize(self) -> bool:

        try:
            # Set up logging first
            setup_logging()
            logger.info(f"Starting {VERSION_FULL}")
            
            # Log application startup
            log_security_event("application_startup")
            
            # Set Qt attributes before creating QApplication
            QApplication.setAttribute(AA_EnableHighDpiScaling)  # type: ignore
            QApplication.setAttribute(AA_UseHighDpiPixmaps)  # type: ignore
            
            # Create Qt application
            self.app = QApplication(sys.argv)
            self.app.setStyle('Fusion')
            self.app.setApplicationName("School Management Information System")
            self.app.setApplicationVersion(__version__)
            self.app.setOrganizationName("SMIS")
            
            # Setup fonts
            setup_fonts()
            
            # Set application icon
            self._set_application_icon()
            
            # Initialize core services
            self._initialize_services()
            
            # Initialize database
            db = Database()
            
            # Start backup service
            self.backup_manager = get_backup_manager()
            if Config.AUTO_BACKUP:
                self.backup_manager.start_scheduled_backups()
            
            # Initialize authentication
            self.auth_manager = get_auth_manager()
            
            return True
            
        except Exception as e:
            error = handle_exception(e, "Application initialization")
            logging.error(f"Application initialization failed: {error}")
            if hasattr(self, 'app') and self.app:
                QMessageBox.critical(None, "Initialization Error", str(error))
            return False
    
    def _set_application_icon(self):
        """Set application icon."""
        try:
            # Try different icon file formats with priority on icon.ico
            icon_paths = [
                os.path.join(os.path.dirname(__file__), 'resources', 'icons', 'icon.ico'),
                os.path.join(os.path.dirname(__file__), 'resources', 'icons', 'app_icon.ico'),
                os.path.join(os.path.dirname(__file__), 'resources', 'icons', 'app_icon.svg'),
                os.path.join(os.path.dirname(__file__), 'resources', 'app_icon.svg'),
            ]
            
            icon_loaded = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.app.setWindowIcon(QIcon(icon_path))  # type: ignore
                    icon_loaded = True
                    break
            
            if not icon_loaded:
                # Create a simple default icon if file not found
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setFont(QFont("Arial", 20))
                painter.drawText(pixmap.rect(), Qt.AlignCenter, "📚")
                painter.end()
                self.app.setWindowIcon(QIcon(pixmap))  # type: ignore
        except Exception as e:
            logging.warning(f"Could not set application icon: {e}")
    def _initialize_services(self):
        """Initialize application services."""
        try:
            # Set up global exception handler
            sys.excepthook = self._global_exception_handler
            
            logging.info("Core services initialized successfully")
            
        except Exception as e:
            raise SMISException(f"Failed to initialize services: {e}")
    
    def _global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler for unhandled exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = f"Unhandled exception: {exc_type.__name__}: {exc_value}"
        logging.critical(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        
        # Log security event for critical errors
        log_security_event("unhandled_exception", details={
            'exception_type': exc_type.__name__,
            'exception_message': str(exc_value)
        })
        
        # Show error dialog to user
        if self.app:
            QMessageBox.critical(
                None,
                "Critical Error",
                f"A critical error occurred:\\n\\n{error_msg}\\n\\n"
                f"The application will attempt to continue, but please restart "
                f"as soon as possible and report this error."
            )
    
    def show_login_window(self):
        """Show login window and handle authentication."""
        try:
            login_window = LoginWindow()
            login_window.login_successful.connect(self._on_login_successful)
            
            result = login_window.exec_()
            
            if result == LoginWindow.Rejected:
                # User closed login window
                log_security_event("login_cancelled")
                return False
            
            return True
            
        except Exception as e:
            error = handle_exception(e, "Login window")
            logging.error(f"Login window error: {error}")
            QMessageBox.critical(None, "Login Error", str(error))
            return False
    
    def _on_login_successful(self, user):
        """Handle successful login and show main window."""
        try:
            self.current_user = user
            
            # Log successful authentication
            log_audit_event("user_login", user.id, "session", details={
                'login_time': user.last_login.isoformat() if user.last_login else None
            })
            
            # Create and show main window
            self._show_main_window()
            
        except Exception as e:
            error = handle_exception(e, "Post-login setup")
            logging.error(f"Post-login setup failed: {error}")
            QMessageBox.critical(None, "Application Error", str(error))
    
    def _show_main_window(self):
        """Create and show the main application window."""
        try:
            # Prevent multiple main window creation
            if hasattr(self, 'main_window') and self.main_window:
                logging.warning("Main window already exists, skipping creation")
                return
                
            # Import and apply styles
            from resources.styles import setAppStyle
            
            # Create main window
            self.main_window = MainWindow()
            
            # Set current user context
            self.main_window.set_current_user(self.current_user)
            
            # Apply styles
            setAppStyle(self.main_window)
            
            # Connect window close event to cleanup
            self.main_window.closeEvent = self._on_main_window_close
            
            # Show window
            self.main_window.show()
            
            logging.info(f"Main window opened for user: {self.current_user.username}")  # type: ignore
            
        except Exception as e:
            error = handle_exception(e, "Main window creation")
            logging.error(f"Main window creation failed: {error}")
            QMessageBox.critical(None, "Application Error", str(error))
    
    def _on_main_window_close(self, event):
        """Handle main window close event."""
        try:
            # Log user logout
            if self.current_user:
                log_audit_event("user_logout", self.current_user.id, "session")  # type: ignore
                
                # Logout from auth manager
                self.auth_manager.logout()  # type: ignore
            
            # Stop backup service
            if self.backup_manager:
                self.backup_manager.stop_scheduled_backups()
            
            # Log application shutdown
            log_security_event("application_shutdown")
            
            event.accept()
            
        except Exception as e:
            logging.error(f"Error during application shutdown: {e}")
            event.accept()  # Accept anyway to prevent hanging

    def run(self):
        """Run the application."""
        try:
            if not self.initialize():
                return 1
            
            # Debug: Print current configuration paths
            from config.settings import Config
            print(f"🗂️  App Data Directory: {Config.APP_DATA_DIR}")
            print(f"🗄️  Database Path: {Config.DATABASE_PATH}")
            print(f"📁 Database Exists: {os.path.exists(Config.DATABASE_PATH)}")
            
            # Check if this is first time user (no users exist)
            if self._is_first_time_user():
                print("🆕 First time user detected - showing registration window")
                if not self.show_registration_window():
                    return 1
            else:
                print("👤 Existing users found - proceeding to login")
            
            # Show login window
            if not self.show_login_window():
                return 1
            
            # Run application event loop
            return self.app.exec_()  # type: ignore
            
        except Exception as e:
            error = handle_exception(e, "Application runtime")
            logging.critical(f"Application runtime error: {error}")
            if self.app:
                QMessageBox.critical(None, "Critical Error", str(error))
            return 1
    
    def _is_first_time_user(self):
        """Check if this is the first time the application is being run (no users exist and no license)."""
        try:
            # Import here to avoid circular imports
            from models.database import Database
            from config.settings import Config
            from core.security_manager import SMISSecurityManager
            
            # Check if database file exists at the configured path
            if not os.path.exists(Config.DATABASE_PATH):
                logging.info(f"Database file not found at {Config.DATABASE_PATH}, treating as first time user")
                return True
            
            # Check if any users exist in the database
            db = Database()
            db.cursor.execute("SELECT COUNT(*) FROM users")
            user_count = db.cursor.fetchone()[0]
            
            # Additionally check if license data exists
            security_manager = SMISSecurityManager()
            stored_key = security_manager.load_stored_key()
            has_license = stored_key is not None
            
            logging.info(f"Found {user_count} users in database at {Config.DATABASE_PATH}")
            logging.info(f"License data exists: {has_license}")
            
            # Return True if no users exist AND no license data (truly fresh install)
            is_first_time = (user_count == 0) and (not has_license)
            
            if is_first_time:
                logging.info("🔄 Fresh installation detected - will show registration")
            else:
                logging.info("👤 Existing installation detected - will show login")
                
            return is_first_time
            
        except Exception as e:
            logging.error(f"Error checking first time user status: {e}")
            # If there's an error, assume it's first time to allow registration
            return True
    
    def show_registration_window(self):
        """Show registration window for first-time users."""
        try:
            from ui.registration_window import RegistrationWindow
            
            # Show welcome message
            QMessageBox.information(
                None,
                "Welcome to SMIS!",
                "Welcome to School Management Information System!\n\n"
                "This appears to be your first time running the application.\n"
                "Please register your first administrator account to get started.\n\n"
                "You'll be able to create additional users after login."
            )
            
            self.registration_window = RegistrationWindow()
            self.registration_window.setWindowTitle("SMIS - First Time Setup")
            
            # Connect registration success signal - use the correct signal name
            if hasattr(self.registration_window, 'registration_completed'):
                self.registration_window.registration_completed.connect(self._on_registration_successful)
            elif hasattr(self.registration_window, 'registration_successful'):
                self.registration_window.registration_successful.connect(self._on_registration_successful)
            
            result = self.registration_window.exec_()
            
            if result == RegistrationWindow.Rejected:
                # User closed registration window
                log_security_event("first_time_registration_cancelled")
                QMessageBox.warning(
                    None,
                    "Registration Required",
                    "Registration is required for first-time setup.\n"
                    "The application will now exit."
                )
                return False
            
            # If registration was successful, return True to continue to login
            return True
            
        except Exception as e:
            error = handle_exception(e, "Registration window")
            logging.error(f"Registration window error: {error}")
            QMessageBox.critical(None, "Registration Error", str(error))
            return False
    
    def _on_registration_successful(self, user_data=None):
        """Handle successful registration for first-time users."""
        try:
            log_security_event("first_time_registration_completed")
            logging.info("First-time user registration completed successfully")
            
            # Show success message
            QMessageBox.information(
                None,
                "Registration Successful!",
                "Your administrator account has been created successfully!\n\n"
                "The application will now proceed to the login screen.\n"
                "Please login with your new credentials to continue."
            )
            
            # Force close the registration window properly
            if hasattr(self, 'registration_window'):
                self.registration_window.close()
                
        except Exception as e:
            logging.error(f"Error handling registration success: {e}")

def _is_new_installation():
    """Check if this is a new installation (no users exist in database)."""
    try:
        # Check if database file exists first
        db_path = os.path.join(os.path.dirname(__file__), 'school.db')
        if not os.path.exists(db_path):
            return True
            
        # Also check if license key exists
        from core.security_manager import SMISSecurityManager
        security_manager = SMISSecurityManager()
        key_data = security_manager.load_stored_key()
        if not key_data:
            return True
            
        # Check users in database
        import_app_modules()
        from models.database import Database
        db = Database()
        db.cursor.execute("SELECT COUNT(*) FROM users")
        user_count = db.cursor.fetchone()[0]
        return user_count == 0
    except Exception:
        # If there's any error, assume it's a new installation
        return True

def main():
    """
    Main application entry point with security validation and update checking.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # STEP 1: Check license status and handle fresh installations
        print("🔐 SMIS Security Validation")
        print("=" * 40)
        
        from core.security_manager import SMISSecurityManager
        security_manager = SMISSecurityManager()
        
        # Check if we have a valid license
        has_license = security_manager.verify_license()
        
        if has_license:
            print("✅ License verified successfully")
        else:
            # Check if this is a fresh installation
            is_fresh = _is_new_installation()
            
            if is_fresh:
                print("🆕 Fresh installation detected")
                print("Registration is required to continue")
                print("The application will open the registration window...")
                
                # Import modules for registration window
                import_app_modules()
                
                # Create registration window
                app_temp = QApplication(sys.argv)
                from ui.registration_window import RegistrationWindow
                reg_window = RegistrationWindow()
                
                if reg_window.exec_() == reg_window.Accepted:
                    print("✅ Registration successful! Please restart the application.")
                    return 0
                else:
                    print("❌ Registration cancelled or failed")
                    return 1
            else:
                # Existing installation without valid license
                print("\n❌ SECURITY CHECK FAILED")
                print("This application requires a valid license key.")
                print("\nOptions:")
                print("1. Register with a new key: python main.py register")
                print("2. Get a key from: https://github.com/ZubairHussainK/smis-key-generator")
                print("\nApplication will now exit.")
                return 1
        
        print("Loading application modules...")
        
        # STEP 3: Import modules only after security validation
        import_app_modules()
        
        # STEP 4: Initialize application normally
        app = SMISApplication()
        return app.run()
        
    except KeyboardInterrupt:
        print("\n❌ Application interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Critical application error: {e}")
        try:
            logging.critical(f"Fatal application error: {e}")
        except:
            pass
        return 1


def handle_registration():
    """Handle application registration."""
    print("SMIS Registration System")
    print("=" * 40)
    print("This will register your copy of SMIS with a valid license key.")
    print("You can get a key from: https://github.com/ZubairHussainK/smis-key-generator")
    print("Supported formats: Enhanced keys (25-char) or SMIS keys (24-char)")
    print()
    
    if register_application():
        print("\nRegistration completed successfully!")
        print("You can now run the application normally.")
        print("Command: python main.py")
    else:
        print("\nRegistration failed.")
        print("Please ensure you have a valid key and try again.")

def handle_reset():
    """Handle fresh installation reset."""
    print("🔄 SMIS Fresh Installation Reset")
    print("=" * 50)
    print("⚠️  WARNING: This will permanently delete:")
    print("   • All license and registration data")
    print("   • All student records and database")
    print("   • All application settings")
    print("   • All attendance records")
    print()
    
    response = input("Are you sure you want to reset everything? (type 'RESET' to confirm): ")
    if response != 'RESET':
        print("❌ Reset cancelled")
        return False
    
    try:
        # Import security manager
        from core.security_manager import SMISSecurityManager
        from config.settings import Config
        import shutil
        
        print("\n🔄 Resetting license data...")
        security_manager = SMISSecurityManager()
        security_manager.reset_license_data()
        
        print("🔄 Removing database...")
        if os.path.exists(Config.DATABASE_PATH):
            os.remove(Config.DATABASE_PATH)
            print("✅ Database removed")
        
        print("🔄 Removing AppData directory...")
        if os.path.exists(Config.APP_DATA_DIR):
            shutil.rmtree(Config.APP_DATA_DIR)
            print("✅ AppData directory removed")
        
        print("\n✅ Fresh installation reset completed!")
        print("🔄 Next time you run SMIS, it will show registration page.")
        print("💡 Restart the application to begin fresh setup.")
        return True
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False

# Make the main function available for import
__all__ = ['main']

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['register', 'reg', '-r', '--register']:
            handle_registration()
            sys.exit(0)
        elif sys.argv[1].lower() in ['reset', '--reset', '-reset']:
            handle_reset()
            sys.exit(0)
        elif sys.argv[1].lower() in ['help', '-h', '--help']:
            print("SMIS - School Management Information System")
            print("=" * 50)
            print("Usage:")
            print("  python main.py           # Run application")
            print("  python main.py register  # Register with license key")
            print("  python main.py help      # Show this help")
            print()
            print("Get your license key from:")
            print("https://github.com/ZubairHussainK/smis-key-generator")
            sys.exit(0)
    
    # Normal application startup
    sys.exit(main())
