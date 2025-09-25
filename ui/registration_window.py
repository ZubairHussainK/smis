import sys
import os
import re
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFrame, QMessageBox, QApplication, QAction, QProgressBar, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.auth import get_auth_manager
from core.exceptions import SMISException
from core.security_manager import SMISSecurityManager

class SimplePasswordInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        self.password_visible = False
        self.eye_action = QAction("👁", self)
        self.addAction(self.eye_action, QLineEdit.TrailingPosition)
        self.eye_action.triggered.connect(self._toggle_password_visibility)
    def _toggle_password_visibility(self):
        self.setEchoMode(QLineEdit.Normal if not self.password_visible else QLineEdit.Password)
        self.eye_action.setText("🙈" if not self.password_visible else "👁")
        self.password_visible = not self.password_visible

class KeyValidationThread(QThread):
    validation_complete = pyqtSignal(bool, str)
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key
    
    def run(self):
        try:
            # Initialize the security manager
            security_manager = SMISSecurityManager()
            
            # First check the new security manager validation
            if security_manager.validate_key_format(self.key) and security_manager.validate_key_checksum(self.key):
                self.validation_complete.emit(True, "✔️ Registration key validated successfully!")
                return
            
            # Fallback to old JSON validation system for backward compatibility
            keys_file = "active_keys.json"
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    active_keys = json.load(f)
                if self.key in active_keys:
                    key_data = active_keys[self.key]
                    if key_data.get('active', False) and not key_data.get('used', False):
                        expiry_str = key_data.get('expiry_date', '')
                        if expiry_str:
                            try:
                                expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                                if datetime.now() > expiry_date:
                                    self.validation_complete.emit(False, "❌ Registration key has expired.")
                                    return
                            except ValueError:
                                pass
                        self.validation_complete.emit(True, "✔️ Registration key validated successfully!")
                        return
                    else:
                        self.validation_complete.emit(False, "❌ Registration key is inactive or already used.")
                        return
            
            # If neither validation method succeeds
            self.validation_complete.emit(False, "❌ Invalid registration key.")
                
        except Exception as e:
            logging.error(f"Key validation error", exc_info=True)
            self.validation_complete.emit(False, "❌ Error validating registration key.")

class RegistrationWindow(QDialog):
    registration_completed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.auth_manager = get_auth_manager()
        self.validation_thread = None
        self.key_validated = False
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.setWindowTitle("SMIS - User Registration")
        self.setFixedSize(520, 620)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_form())
        main_layout.addWidget(self._create_buttons())
        main_layout.addWidget(self._create_security_notice())

        self.setLayout(main_layout)

    def _create_header(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        logo_path = os.path.abspath(os.path.join(__file__, "..", "..", "resources", "logos", "Horizintal_logo.png"))
        logo_label = QLabel(alignment=Qt.AlignCenter)
        pixmap = QPixmap(logo_path)
        if pixmap.isNull():
            logo_label.setText("SMIS")
        else:
            logo_label.setPixmap(pixmap.scaled(120, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # title_label = QLabel("Create New Account")
        # title_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel("Fill in your details to register for SMIS")
        subtitle_label.setContentsMargins(0, 6, 0, 6)
        subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(logo_label)
        #layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        return frame

    def _create_form(self):
        outer_frame = QFrame()
        outer_frame.setStyleSheet("QFrame { background-color: #f0f4f7; border-radius: 8px; }")
        layout = QVBoxLayout(outer_frame)
        layout.setContentsMargins(12,12,12,12)
        layout.setSpacing(10)

        self.username_input = self._create_input_field("Username:", "Choose a username")
        layout.addWidget(self.username_input)
        self.email_input = self._create_input_field("Email:", "Enter your email address")
        layout.addWidget(self.email_input)
        self.organization_input = self._create_input_field("Organization:", "Enter your organization name", "organizationInput")
        layout.addWidget(self.organization_input)
        self.password_input = self._create_input_field("Password:", "Enter your password", input_class=SimplePasswordInput)
        layout.addWidget(self.password_input)
        self.confirm_password_input = self._create_input_field("Confirm Password:", "Confirm your password", input_class=SimplePasswordInput)
        layout.addWidget(self.confirm_password_input)

        key_label = QLabel("Registration Key:")
        layout.addWidget(key_label)

        key_layout = QHBoxLayout()
        key_layout.setSpacing(2)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your registration key")
        self.validate_key_btn = QPushButton("Validate")
        self.validate_key_btn.clicked.connect(self.validate_key)
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(self.validate_key_btn)
        layout.addLayout(key_layout)

        self.key_status_label = QLabel("")
        layout.addWidget(self.key_status_label)

        self.validation_progress = QProgressBar()
        self.validation_progress.setVisible(False)
        self.validation_progress.setRange(0,0)
        self.validation_progress.setMaximumHeight(3)
        layout.addWidget(self.validation_progress)

        return outer_frame

    def _create_input_field(self, label_text, placeholder, input_object_name=None, input_class=QLineEdit):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)

        label = QLabel(label_text)
        input_field = input_class()
        if input_object_name:
            input_field.setObjectName(input_object_name)
        input_field.setPlaceholderText(placeholder)

        layout.addWidget(label)
        layout.addWidget(input_field)

        container.input_field = input_field
        return container

    def _create_buttons(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setSpacing(5)
        layout.setContentsMargins(0,0,0,0)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.register_btn = QPushButton("Register")
        self.register_btn.setEnabled(False)
        self.register_btn.clicked.connect(self._register_user)
        layout.addWidget(self.cancel_btn)
        layout.addStretch()
        layout.addWidget(self.register_btn)
        return frame

    def _create_security_notice(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0,0,0,0)
        notice = QLabel("🔒 Your registration data is secure and encrypted.\nPlease keep your registration key safe until account creation.")
        notice.setAlignment(Qt.AlignCenter)
        notice.setWordWrap(True)
        layout.addWidget(notice)
        return frame

    def validate_key(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Validation Error", "Please enter a registration key.")
            return

        self.validation_progress.setVisible(True)
        self.key_status_label.setText("Validating...")

        self.validation_thread = KeyValidationThread(key)
        self.validation_thread.validation_complete.connect(self._on_key_validation_complete)
        self.validation_thread.start()

    def _on_key_validation_complete(self, success, message):
        self.validation_progress.setVisible(False)
        self.key_status_label.setText(message)
        self.key_validated = success
        self.register_btn.setEnabled(success)
        
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
        password = self.password_input.input_field.text()
        confirm_password = self.confirm_password_input.input_field.text()

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
                'password': self.password_input.input_field.text(),
                'full_name': self.username_input.input_field.text().strip(),  # Use username as full name
                'email': self.email_input.input_field.text().strip(),
                'phone': "",  # Default empty phone
                'organization': self.organization_input.input_field.text().strip(),
                'role': "admin",  # First user is admin for fresh installation
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
                
                # Success message with clear instructions
                QMessageBox.information(self, "Registration Successful", 
                                      f"Account created successfully!\n\n"
                                      f"Username: {user_data['username']}\n"
                                      f"Organization: {user_data['organization']}\n\n"
                                      f"The application will now proceed to the login screen.\n"
                                      f"Please use your new credentials to login.")
                
                # Log successful registration
                logging.info(f"User registration successful: {user_data['username']}")
                
                # Emit registration completed signal first
                self.registration_completed.emit(user_data)
                
                # Then accept dialog (close with success)
                self.accept()
            else:
                QMessageBox.critical(self, "Registration Error", 
                                   "Failed to create user account. Please check if the username already exists or try again.")
                logging.error(f"User registration failed: {user_data['username']}")
                
        except Exception as e:
            logging.error(f"Registration error: {e}")
            QMessageBox.critical(self, "Registration Error", f"An error occurred during registration:\n{str(e)}")
            
    def _mark_key_as_used(self, key):
        """Mark the registration key as used using the security manager."""
        try:
            # Use the security manager to register the key properly
            security_manager = SMISSecurityManager()
            
            # Create user info for registration
            user_info = {
                'organization': self.organization_input.input_field.text().strip(),
                'contact_person': self.username_input.input_field.text().strip(),
                'email': self.email_input.input_field.text().strip()
            }
            
            # Register the key with the security manager
            success = security_manager.register_user(key, user_info)
            if success:
                logging.info(f"Registration key {key} registered successfully with security manager")
            else:
                logging.warning(f"Failed to register key {key} with security manager")
            
            # Also handle the old JSON system for backward compatibility
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
                    
                    logging.info(f"Registration key {key} marked as used in JSON file")
                        
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
