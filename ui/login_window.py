"""Login window with enhanced security features."""
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLineEdit, QPushButton, QLabel, QFrame, QCheckBox,
                           QMessageBox, QProgressBar, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QCursor
from core.auth import get_auth_manager
from config.security import validate_password_strength
from utils.logger import log_security_event
from utils.material_icons import MaterialIcons
from ui.registration_window import RegistrationWindow
import sys
import os
from PyQt5.QtWidgets import QToolButton



class PasswordLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.password_visible = False
        self.setEchoMode(QLineEdit.Password)

        # Create toggle button
        self.eye_button = QToolButton(self)
        self.eye_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.eye_button.setStyleSheet("border: none; padding: 0px;")

        # Load icons
        self.eye_open_icon = QIcon("resources/icons/eye_open.svg")
        self.eye_off_icon = QIcon("resources/icons/eye_off.svg")

        # Default state
        self.eye_button.setIcon(self.eye_off_icon)

        # Connect click event
        self.eye_button.clicked.connect(self.toggle_password_visibility)

        # Position button initially
        self.update_eye_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_eye_position()



    def update_eye_position(self):
        """Place the eye button inside the line edit."""
        frame_width = self.style().pixelMetric(self.style().PM_DefaultFrameWidth)
        button_size = self.eye_button.sizeHint()
        right_margin = 6  # adjust space from right ed
        self.eye_button.move(
            self.width() - button_size.width() - frame_width,
            (self.height() - button_size.height()) // 2
        )
        self.eye_button.move(
            self.width() - button_size.width() - frame_width - right_margin,
            (self.height() - button_size.height()) // 2
        )

    def toggle_password_visibility(self):
        """Toggle password visibility when eye button is clicked."""
        if self.password_visible:
            self.setEchoMode(QLineEdit.Password)
            self.eye_button.setIcon(self.eye_off_icon)
            self.password_visible = False
        else:
            self.setEchoMode(QLineEdit.Normal)
            self.eye_button.setIcon(self.eye_open_icon)
            self.password_visible = True

                        
class LoginWorker(QThread):
    """Background worker for login operations to prevent UI blocking."""
    
    login_success = pyqtSignal(object)  # User object
    login_failed = pyqtSignal(str)  # Error message
    
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
    
    def run(self):
        """Perform login operation in background."""
        try:
            auth_manager = get_auth_manager()
            
            # Connect to auth manager signals
            auth_manager.user_logged_in.connect(self.login_success.emit)
            auth_manager.login_failed.connect(self.login_failed.emit)
            
            # Attempt login
            success = auth_manager.login(self.username, self.password)
            
            if not success:
                # If no specific error was emitted, emit generic error
                self.login_failed.emit("Login failed. Please check your credentials.")
                
        except Exception as e:
            self.login_failed.emit(f"Login error: {str(e)}")

class LoginWindow(QDialog):
    """Secure login window with enhanced features."""
    
    login_successful = pyqtSignal(object)  # User object
    
    def __init__(self):
        super().__init__()
        self.auth_manager = get_auth_manager()
        self.login_worker = None
        self.failed_attempts = 0
        self.max_attempts = 5
        self.lockout_time = 300  # 5 minutes
        self.is_locked = False
        
        self._init_ui()
        self._setup_connections()
        self._apply_styles()
        
        # Log security event
        log_security_event("login_window_opened")
    
    def _init_ui(self):
        """Initialize the login UI."""
        self.setWindowTitle("SMIS - Login")
        self.setFixedSize(480, 560)  # Reduced height since we removed show password checkbox
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Set application icon using helper function
        from utils.ui_helpers import set_app_icon
        set_app_icon(self)
        
        # Set application icon explicitly for the login window
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icons', 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Center window on screen
        self._center_window()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 10, 30, 15)  # Reduced top margin significantly
        main_layout.setSpacing(8)  # Further reduced spacing between sections
        
        # Header section
        self._create_header(main_layout)
        
        # Login form
        self._create_login_form(main_layout)
        
        # Security notice
        self._create_security_notice(main_layout)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)  # Standard height
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        self.status_label.setMinimumHeight(25)  # Standard height
        main_layout.addWidget(self.status_label)
    

    def _create_header(self, layout):
        """Create the header section."""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(2)  # Minimal spacing
        header_layout.setContentsMargins(0, 0, 0, 0)  # No margins on header
        
        
        logo_label = QLabel()

        # Resolve path correctly (go up one level from ui/)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.normpath(os.path.join(base_dir, "..", "resources", "logos", "Horizintal_logo.png"))

        pixmap = QPixmap(logo_path)
        if pixmap.isNull():
            print("❌ Image not loaded! Path:", logo_path)
        else:
            pixmap = pixmap.scaledToWidth(120, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)

                
        # Title
        title_label = QLabel("School Management Information System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("loginTitleLabel")
        # Subtitle
        subtitle_label = QLabel("Please sign in to continue")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("loginSubtitleLabel")
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_frame)
        
    def _create_login_form(self, layout):
        """Create the login form."""
        form_frame = QFrame()
        form_frame.setObjectName("loginForm")
        form_frame.setMinimumSize(420, 280)  # Further reduced form height to save space
        form_frame.setMaximumWidth(450)  # Standard width
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(8)  # Reduced spacing between form elements
        form_layout.setContentsMargins(15, 15, 15, 15)  # Reduced form margins
        form_frame.setObjectName("form_frame")
        
        # Username section
        username_label = QLabel("Username:")
        username_label.setObjectName("loginUsernameLabel")
        username_label.setMinimumHeight(18)
        username_label.setMaximumHeight(18)
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setObjectName("usernameInput")
        self.username_input.setMinimumHeight(32)  # Reduced input height
        self.username_input.setMaximumHeight(32)  
        self.username_input.setMinimumWidth(350)  # Standard width
        self.username_input.setMaximumWidth(400)  
        form_layout.addWidget(self.username_input)
        
        # Add spacing between sections
        form_layout.addSpacing(5)  # Minimal spacing
        
        # Password section
        password_label = QLabel("Password:")
        password_label.setObjectName("loginPasswordLabel")
        password_label.setMinimumHeight(18)
        password_label.setMaximumHeight(18)
        form_layout.addWidget(password_label)
        
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setObjectName("passwordInput")
        self.password_input.setMinimumHeight(32)  # Reduced input height
        self.password_input.setMaximumHeight(32)  
        self.password_input.setMinimumWidth(350)  # Standard width
        self.password_input.setMaximumWidth(400)  
        form_layout.addWidget(self.password_input)
        
        # Add spacing before remember me checkbox
        form_layout.addSpacing(5)  # Minimal spacing
        
        # Remember me checkbox
        self.remember_me_cb = QCheckBox("Remember me")
        self.remember_me_cb.setObjectName("loginRememberMeCB")
        self.remember_me_cb.setMinimumHeight(18)  # Reduced height
        form_layout.addWidget(self.remember_me_cb)
        
        # Add spacing before button
        form_layout.addSpacing(5)  # Minimal spacing
        
        # Login button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setDefault(True)
        self.login_btn.setMinimumHeight(36)  # Reduced button height
        self.login_btn.setMaximumHeight(36)  
        self.login_btn.setMinimumWidth(350)  # Standard width
        self.login_btn.setMaximumWidth(400)  
        form_layout.addWidget(self.login_btn)
        
        # Add spacing before forgot link
        form_layout.addSpacing(5)  # Minimal spacing
        
        # Forgot password link
        forgot_link = QLabel('<a href="#" style="color: #3498db; font-size: 12px; text-decoration: none;">Forgot password?</a>')
        forgot_link.setAlignment(Qt.AlignCenter)
        forgot_link.setObjectName("loginForgotLink")
        forgot_link.linkActivated.connect(self._show_forgot_password)
        form_layout.addWidget(forgot_link)
        
        # Registration link
        register_link = QLabel('<a href="#" style="color: #27ae60; font-size: 12px; text-decoration: none;">Don\'t have an account? Register here</a>')
        register_link.setAlignment(Qt.AlignCenter)
        register_link.setObjectName("loginRegisterLink")
        register_link.linkActivated.connect(self._show_registration)
        form_layout.addWidget(register_link)
        
        layout.addWidget(form_frame)
    
    def _create_security_notice(self, layout):
        """Create security notice section."""
        notice_frame = QFrame()
        notice_frame.setObjectName("securityNotice")
        notice_layout = QVBoxLayout(notice_frame)
        notice_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        
        notice_text = QLabel(
            "🔒 Your session is secure and encrypted.\n"
            "Do not share your login credentials with anyone."
        )
        notice_text.setAlignment(Qt.AlignCenter)
        notice_text.setWordWrap(True)
        notice_text.setMinimumHeight(35)  # Reduced height
        notice_text.setMaximumHeight(40)  # Set max height
        notice_text.setObjectName("loginSecurityNotice")
        
        notice_layout.addWidget(notice_text)
        layout.addWidget(notice_frame)
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.login_btn.clicked.connect(self._attempt_login)
        self.username_input.returnPressed.connect(self._attempt_login)
        self.password_input.returnPressed.connect(self._attempt_login)
        
        # Auth manager connections
        self.auth_manager.user_logged_in.connect(self._on_login_success)
        self.auth_manager.login_failed.connect(self._on_login_failed)
    
    def _apply_styles(self):
        """Load and apply styles from QSS file."""
        qss_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "resources", "stylelogin.qss"
        )
        qss_path = os.path.abspath(qss_path)
        
        print("🔎 Trying QSS path:", qss_path)
        
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                qss = f.read()
                self.setStyleSheet(qss)
                print("✅ QSS file loaded, length:", len(qss))
                print("Current stylesheet length:", len(self.styleSheet()))
        else:
            print(f"❌ QSS file not found: {qss_path}")


    
    def _center_window(self):
        """Center the window on screen."""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def _show_forgot_password(self):
        """Show forgot password dialog."""
        QMessageBox.information(
            self,
            "Forgot Password",
            "Please contact your system administrator to reset your password.\n\n"
            "For security reasons, password reset must be done manually."
        )
    
    def _show_registration(self):
        """Show registration window."""
        try:
            self.registration_window = RegistrationWindow()
            self.registration_window.registration_completed.connect(self._on_registration_completed)
            
            # Show as modal dialog
            result = self.registration_window.exec_()
            
        except Exception as e:
            logging.error(f"Error opening registration window: {e}")
            QMessageBox.warning(
                self,
                "Registration Error", 
                "Unable to open registration window. Please try again."
            )
    
    def _on_registration_completed(self, user_data):
        """Handle successful registration."""
        QMessageBox.information(
            self,
            "Registration Complete",
            f"Welcome {user_data['full_name']}!\n\n"
            f"Your account has been created successfully.\n"
            f"You can now login with username: {user_data['username']}"
        )
        # Optionally pre-fill the username field
        self.username_input.setText(user_data['username'])
    
    def _attempt_login(self):
        """Attempt to log in the user."""
        if self.is_locked:
            self._show_lockout_message()
            return
        
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username:
            self._show_error("Please enter your username.")
            return
        
        if not password:
            self._show_error("Please enter your password.")
            return
        
        # Disable UI and show progress
        self._set_login_state(True)
        
        # Log security event
        log_security_event("login_attempt", details={'username': username})
        
        # Start login worker
        self.login_worker = LoginWorker(username, password)
        self.login_worker.login_success.connect(self._on_login_success)
        self.login_worker.login_failed.connect(self._on_login_failed)
        self.login_worker.finished.connect(lambda: self._set_login_state(False))
        self.login_worker.start()
    
    def _set_login_state(self, logging_in):
        """Set UI state during login process."""
        self.login_btn.setEnabled(not logging_in)
        self.username_input.setEnabled(not logging_in)
        self.password_input.setEnabled(not logging_in)
        self.progress_bar.setVisible(logging_in)
        
        if logging_in:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText("Authenticating...")
            self.status_label.setVisible(True)
        else:
            self.progress_bar.setVisible(False)
            self.status_label.setVisible(False)
    
    @pyqtSlot(object)
    def _on_login_success(self, user):
        """Handle successful login."""
        self.failed_attempts = 0
        log_security_event("login_success", user.id)
        
        self.status_label.setText("Login successful! Loading application...")
        self.status_label.setStyleSheet("color: #27ae60;")
        
        # Emit success signal and close dialog
        QTimer.singleShot(1000, lambda: self._complete_login(user))
    
    @pyqtSlot(str)
    def _on_login_failed(self, error_message):
        """Handle failed login."""
        self.failed_attempts += 1
        
        log_security_event("login_failed", details={
            'username': self.username_input.text(),
            'attempt_number': self.failed_attempts,
            'error': error_message
        })
        
        if self.failed_attempts >= self.max_attempts:
            self._lock_interface()
        else:
            remaining = self.max_attempts - self.failed_attempts
            error_message += f"\\n{remaining} attempts remaining."
        
        self._show_error(error_message)
        self.password_input.clear()
        self.password_input.setFocus()
    
    def _complete_login(self, user):
        """Complete the login process."""
        self.login_successful.emit(user)
        self.accept()
    
    def _lock_interface(self):
        """Lock the interface after too many failed attempts."""
        self.is_locked = True
        self.login_btn.setEnabled(False)
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        
        self.status_label.setText(
            f"Too many failed attempts. Interface locked for {self.lockout_time // 60} minutes."
        )
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.status_label.setVisible(True)
        
        # Set timer to unlock interface
        QTimer.singleShot(self.lockout_time * 1000, self._unlock_interface)
        
        log_security_event("interface_locked", details={
            'failed_attempts': self.failed_attempts,
            'lockout_duration': self.lockout_time
        })
    
    def _unlock_interface(self):
        """Unlock the interface after lockout period."""
        self.is_locked = False
        self.failed_attempts = 0
        
        self.login_btn.setEnabled(True)
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        
        self.status_label.setText("Interface unlocked. You may try logging in again.")
        self.status_label.setStyleSheet("color: #27ae60;")
        
        QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))
        
        log_security_event("interface_unlocked")
    
    def _show_lockout_message(self):
        """Show lockout message."""
        QMessageBox.warning(
            self,
            "Interface Locked",
            f"The login interface is currently locked due to too many failed attempts.\\n"
            f"Please wait {self.lockout_time // 60} minutes before trying again."
        )
    
    def _show_error(self, message):
        """Show error message."""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #e74c3c;")
        self.status_label.setVisible(True)
        
        # Hide error message after 5 seconds
        QTimer.singleShot(5000, lambda: self.status_label.setVisible(False))
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.terminate()
            self.login_worker.wait()
        
        log_security_event("login_window_closed")
        event.accept()
