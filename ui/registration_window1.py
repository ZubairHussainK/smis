"""Registration window UI implementation with key validation."""
import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QFrame, QMessageBox, QTextEdit,
                           QApplication, QCheckBox,QAction, QProgressBar, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath, QRegion, QIcon
import logging
import requests
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.auth import get_auth_manager
from core.exceptions import SMISException


class SimplePasswordInput(QLineEdit):
    """Password input with inline show/hide eye button."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        self.setObjectName("passwordInputField")
        self.password_visible = False

        # Eye action (inside input field)
        self.eye_action = QAction("👁", self)
        self.addAction(self.eye_action, QLineEdit.TrailingPosition)  # right side
        self.eye_action.triggered.connect(self._toggle_password_visibility)

    def _toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.password_visible:
            self.setEchoMode(QLineEdit.Password)
            self.eye_action.setText("👁")
        else:
            self.setEchoMode(QLineEdit.Normal)
            self.eye_action.setText("🙈")
        self.password_visible = not self.password_visible

    def text(self):
        return super().text()

    def setText(self, value):
        super().setText(value)

    def setPlaceholderText(self, text):
        super().setPlaceholderText(text)


class KeyValidationThread(QThread):
    """Thread for validating registration keys from GitHub."""
    validation_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key
        
    def run(self):
        """Validate the registration key against local key file."""
        try:
            # Load local keys file
            keys_file = "active_keys.json"
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    active_keys = json.load(f)
                    
                # Check if key exists and is active
                if self.key in active_keys:
                    key_data = active_keys[self.key]
                    if key_data.get('active', False) and not key_data.get('used', False):
                        # Check expiry date
                        expiry_str = key_data.get('expiry_date', '')
                        if expiry_str:
                            from datetime import datetime
                            try:
                                expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                                if datetime.now() > expiry_date:
                                    self.validation_complete.emit(False, "Registration key has expired.")
                                    return
                            except ValueError:
                                pass  # If date parsing fails, continue with validation
                                
                        self.validation_complete.emit(True, "Registration key validated successfully!")
                    else:
                        self.validation_complete.emit(False, "Registration key is inactive or already used.")
                else:
                    self.validation_complete.emit(False, "Invalid registration key.")
            else:
                self.validation_complete.emit(False, "Key validation system not available.")
                
        except Exception as e:
            logging.error(f"Key validation error: {e}")
            self.validation_complete.emit(False, "Error validating registration key.")


class RegistrationWindow(QDialog):
    """Registration window with comprehensive user details and key validation."""
    
    registration_completed = pyqtSignal(dict)  # Emits user data when registration is complete
    
    def __init__(self):
        super().__init__()
        self.auth_manager = get_auth_manager()
        self.validation_thread = None
        self.init_ui()
        self.apply_styles()
            
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("SMIS - User Registration")
        self.setFixedSize(520, 620)  # Reduced height and width for better fit
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        
        # Main layout with proper spacing
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)  # Reduced top margin significantly
        main_layout.setSpacing(8)  # Reduced spacing
        
        # Header
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)
        
        # Registration form
        form_frame = self._create_form()
        main_layout.addWidget(form_frame)
        
        # Buttons
        button_frame = self._create_buttons()
        main_layout.addWidget(button_frame)
        
        # Security notice
        security_frame = self._create_security_notice()
        main_layout.addWidget(security_frame)
        
        self.setLayout(main_layout)
        
    def _create_header(self):
        """Create the header section."""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(3)  # Minimal spacing
        header_layout.setContentsMargins(0, 0, 0, 5)  # Very small bottom margin
        
        # --- Logo Path ---
        logo_path = os.path.abspath(
            os.path.join(__file__, "..", "..", "resources", "logos", "Horizintal_logo.png")
        )

        # --- Logo Label ---
        logo_label = QLabel(alignment=Qt.AlignCenter)
        pixmap = QPixmap(logo_path)

        if pixmap.isNull():
            print(f"❌ Logo not loaded, check path: {logo_path}")
            logo_label.setText("SMIS")  # fallback text
            logo_label.setObjectName("registrationLogoLabel")
        else:
            logo_label.setPixmap(pixmap.scaled(120, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # Title
        title_label = QLabel("Create New Account")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("registrationTitleLabel")
        # Subtitle
        subtitle_label = QLabel("Fill in your details to register for SMIS")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("registrationSubtitleLabel")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        return header_frame
        
    def _create_form(self):
        """Create the registration form."""
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_frame.setMinimumSize(460, 600)
        form_frame.setMaximumWidth(480)

        layout = QVBoxLayout(form_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)


        
        # Username
        self.username_input = self._create_input_field("Username:", "Choose a username")
        layout.addWidget(self.username_input)        
        # Email
        self.email_input = self._create_input_field("Email:", "Enter your email address")
        layout.addWidget(self.email_input)       
        # Organization
        self.organization_input = self._create_input_field("Organization:", "Enter your organization name",input_object_name="organizationInput")
        layout.addWidget(self.organization_input)
 
        
       # Password
        self.password_input = self._create_input_field("Password:", "Enter your password", input_object_name="passwordInput")
        layout.addWidget(self.password_input)
        
        # Confirm Password
        self.confirm_password_input = self._create_input_field("Confirm Password:", "Confirm your password", input_object_name="confirmPasswordInput")
        layout.addWidget(self.confirm_password_input)
  
        
            # Registration Key
        key_label = QLabel("Registration Key:")
        key_label.setObjectName("registrationKeyLabel")
        key_label.setMinimumHeight(14)
        key_label.setMaximumHeight(14)
        layout.addWidget(key_label)
            
        key_input_layout = QHBoxLayout()
        key_input_layout.setSpacing(8)
            
        self.key_input = QLineEdit()
        self.key_input.setObjectName("inputField")
        self.key_input.setPlaceholderText("Enter your registration key")
        
        self.validate_key_btn = QPushButton("Validate")
        self.validate_key_btn.setObjectName("validateButton")
        self.validate_key_btn.clicked.connect(self._validate_key)

        
        key_input_layout.addWidget(self.key_input)
        key_input_layout.addWidget(self.validate_key_btn)
        layout.addLayout(key_input_layout)
        
        # Key validation status
        self.key_status_label = QLabel("")
        self.key_status_label.setObjectName("keyStatusLabel")
        self.key_status_label.setMinimumHeight(12)
        layout.addWidget(self.key_status_label)
        
        # Progress bar for validation
        self.validation_progress = QProgressBar()
        self.validation_progress.setObjectName("validationProgress")
        self.validation_progress.setVisible(False)
        self.validation_progress.setRange(0, 0)  # Indeterminate progress
        self.validation_progress.setMaximumHeight(3)
        layout.addWidget(self.validation_progress)
        
        # Key validation flag
        self.key_validated = False
        
        return form_frame
        
    def _create_input_field(self, label_text, placeholder, input_object_name=None):
        label = QLabel(label_text)
        label.setObjectName("registrationInputLabel")

        input_field = QLineEdit()
        if input_object_name:
            input_field.setObjectName(input_object_name)
        input_field.setPlaceholderText(placeholder)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(label)
        layout.addWidget(input_field)
        container.input_field = input_field

        return container
            
    def _create_buttons(self):
        """Create the button layout with proper spacing."""
        button_frame = QFrame()
        layout = QHBoxLayout(button_frame)
        layout.setSpacing(12)  # Good spacing between buttons
        layout.setContentsMargins(0, 0, 0, 0)  # Reduced top margin
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.clicked.connect(self.reject)  # Use reject() for dialog
      
        
        # Register button
        self.register_btn = QPushButton("Register")
        self.register_btn.setObjectName("registerButton")
        self.register_btn.clicked.connect(self._register_user)
        self.register_btn.setEnabled(False)  # Disabled until key is validated

        
        layout.addWidget(self.cancel_btn)
        layout.addStretch()
        layout.addWidget(self.register_btn)
        
        return button_frame
        
    def _create_security_notice(self):
        """Create security notice section."""
        notice_frame = QFrame()
        notice_frame.setObjectName("securityNotice")
        notice_layout = QVBoxLayout(notice_frame)
        notice_layout.setContentsMargins(0, 0, 0, 0)
        
        notice_text = QLabel(
            "🔒 Your registration data is secure and encrypted.\n"
            "Please keep your registration key safe until account creation."
        )
        notice_text.setAlignment(Qt.AlignCenter)
        notice_text.setWordWrap(True)
        notice_text.setMinimumHeight(30)  # Reduced height
        notice_text.setMaximumHeight(35)
        notice_text.setObjectName("registrationNoticeLabel")
        
        notice_layout.addWidget(notice_text)
        return notice_frame
        
    def _validate_key(self):
        """Validate the registration key."""
        key = self.key_input.text().strip()
        
        if not key:
            self._show_key_status("Please enter a registration key.", False)
            return
            
        # Show progress
        self.validation_progress.setVisible(True)
        self.validate_key_btn.setEnabled(False)
        self.key_status_label.setText("Validating key...")
        self.key_status_label.setStyleSheet("color: #666;")
        
        # Start validation thread
        self.validation_thread = KeyValidationThread(key)
        self.validation_thread.validation_complete.connect(self._on_key_validation_complete)
        self.validation_thread.start()


    def _on_key_validation_complete(self, success, message):
        """Handle key validation completion."""
        self.validation_progress.setVisible(False)
        self.validate_key_btn.setEnabled(True)

        if self.validation_thread:
            self.validation_thread.deleteLater()
            self.validation_thread = None

        self.key_validated = success
        self.register_btn.setEnabled(success)

        self._show_key_status(message, success)

    def _show_key_status(self, message, success):
        """Show key validation status with color."""
        color = "#28a745" if success else "#dc3545"
        self.key_status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.key_status_label.setText(message)

   
    def _validate_form(self):
        """Validate the registration form."""
        errors = []

        # Required fields
        if not self.username_input.input_field.text().strip():
            errors.append("Username is required.")

        email = self.email_input.input_field.text().strip()
        if not email:
            errors.append("Email is required.")
        else:
            import re
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                errors.append("Please enter a valid email address.")

        if not self.organization_input.input_field.text().strip():
            errors.append("Organization is required.")

        # Password validation
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if not self.key_validated:
            errors.append("Please validate your registration key first.")

        return errors


    def _register_user(self):
        """Register the new user."""
        # Validate form
        errors = self._validate_form()
        if errors:
            QMessageBox.warning(self, "Registration Error", "\n".join(errors))
            return
            
        try:
            # Prepare user data
            user_data = {
                'username': self.username_input.input_field.text().strip(),
                'password': self.password_input.text(),
                'full_name': self.username_input.input_field.text().strip(),  # Use username as full name
                'email': self.email_input.input_field.text().strip(),
                'phone': "",  # Default empty phone
                'organization': self.organization_input.input_field.text().strip(),
                'role': "user",  # Default role
                'registration_key': self.key_input.text().strip()
            }
            
            # Check if username already exists
            if self.auth_manager.user_exists(user_data['username']):
                QMessageBox.warning(self, "Registration Error", "Username already exists. Please choose a different username.")
                return
                
            # Create user
            success = self.auth_manager.create_user(
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                full_name=user_data['full_name'],
                email=user_data['email'],
                phone=user_data['phone'],
                organization=user_data['organization']
            )
            
            if success:
                # Mark key as used (you would implement this in your key management system)
                self._mark_key_as_used(user_data['registration_key'])
                
                QMessageBox.information(self, "Registration Successful", 
                                      f"Account created successfully for {user_data['username']}!\n\n"
                                      f"You can now login with username: {user_data['username']}")
                
                # Emit registration completed signal
                self.registration_completed.emit(user_data)
                
                # Accept dialog (close with success)
                self.accept()
            else:
                QMessageBox.critical(self, "Registration Error", "Failed to create user account. Please try again.")
                
        except Exception as e:
            logging.error(f"Registration error: {e}")
            QMessageBox.critical(self, "Registration Error", f"An error occurred during registration: {str(e)}")
            
    def _mark_key_as_used(self, key):
        """Mark the registration key as used in local file."""
        try:
            keys_file = "active_keys.json"
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    active_keys = json.load(f)
                    
                if key in active_keys:
                    from datetime import datetime
                    active_keys[key]['used'] = True
                    active_keys[key]['used_date'] = datetime.now().isoformat()
                    
                    with open(keys_file, 'w') as f:
                        json.dump(active_keys, f, indent=2)
                        
                logging.info(f"Registration key {key} marked as used")
        except Exception as e:
            logging.error(f"Error marking key as used: {e}")
        
    def apply_styles(self):
        """Apply styles from stylelogin.qss for unified look."""
        qss_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "resources", "stylelogin.qss"
        )
        qss_path = os.path.normpath(qss_path)  # ✅ Windows/Linux safe
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

   


def main():
    """Test the registration window."""
    app = QApplication(sys.argv)
    
    window = RegistrationWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
