"""
SMIS PyQt5 Update Manager
========================
PyQt5-based update manager with native GUI integration.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import subprocess
import threading
import logging
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QProgressBar, QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from version import __version__ as CURRENT_VERSION

# Import configuration
try:
    from config.update_config import *
except ImportError:
    # Fallback configuration
    GITHUB_API_URL = "https://api.github.com/repos/ZubairHussainK/smis/releases/latest"
    ENCRYPT_KEY = "smis_secure_update_key_2024"
    UPDATE_CHECK_TIMEOUT = 10


class UpdateWorker(QThread):
    """Worker thread for downloading and installing updates."""
    
    progress_updated = pyqtSignal(str, int)
    update_completed = pyqtSignal(bool, str)
    
    def __init__(self, release_info):
        super().__init__()
        self.release_info = release_info
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Download and install the update."""
        try:
            # Find installer asset
            asset = self.find_installer_asset()
            if not asset:
                self.update_completed.emit(False, "Could not find installer in release assets.")
                return
            
            # Download
            self.progress_updated.emit("Downloading update...", 10)
            temp_dir = tempfile.gettempdir()
            encrypted_path = os.path.join(temp_dir, asset['name'])
            decrypted_path = os.path.join(temp_dir, asset['name'].replace('-encrypted', ''))
            
            self.download_file(asset['browser_download_url'], encrypted_path)
            
            # Decrypt
            self.progress_updated.emit("Decrypting installer...", 80)
            if not self.decrypt_file(encrypted_path, decrypted_path):
                self.update_completed.emit(False, "Failed to decrypt installer.")
                return
            
            # Install
            self.progress_updated.emit("Starting installation...", 95)
            subprocess.Popen([decrypted_path, '/S'])
            
            self.progress_updated.emit("Installation started", 100)
            self.update_completed.emit(True, "Update installation started successfully.")
            
        except Exception as e:
            self.logger.error(f"Update error: {e}")
            self.update_completed.emit(False, f"Error during update: {str(e)}")
    
    def find_installer_asset(self):
        """Find the encrypted installer asset."""
        for asset in self.release_info.get('assets', []):
            if asset['name'].endswith('-encrypted.exe'):
                return asset
        return None
    
    def download_file(self, url, file_path):
        """Download file with progress updates."""
        def reporthook(block_num, block_size, total_size):
            if total_size > 0:
                percentage = min(70, 10 + int((block_num * block_size / total_size) * 60))
                self.progress_updated.emit("Downloading update...", percentage)
        
        urllib.request.urlretrieve(url, file_path, reporthook)
    
    def decrypt_file(self, encrypted_path, decrypted_path):
        """Decrypt the installer file."""
        try:
            key = self.derive_key(ENCRYPT_KEY)
            f = Fernet(key)
            
            with open(encrypted_path, 'rb') as file:
                encrypted_data = file.read()
            
            decrypted_data = f.decrypt(encrypted_data)
            
            with open(decrypted_path, 'wb') as file:
                file.write(decrypted_data)
            
            os.remove(encrypted_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            return False
    
    def derive_key(self, password):
        """Derive encryption key."""
        password_bytes = password.encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'smis_salt_2024',
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key


class UpdateDialog(QDialog):
    """Update notification and progress dialog."""
    
    def __init__(self, release_info, parent=None):
        super().__init__(parent)
        self.release_info = release_info
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("SMIS Update Available")
        self.setFixedSize(450, 200)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Update Available")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Version info
        version_text = (
            f"Current Version: v{CURRENT_VERSION}\n"
            f"Latest Version: {self.release_info.get('tag_name', 'Unknown')}\n\n"
            f"Do you want to download and install the update?"
        )
        version_label = QLabel(version_text)
        version_label.setWordWrap(True)
        layout.addWidget(version_label)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label (hidden initially)
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Update Now")
        self.update_button.clicked.connect(self.start_update)
        button_layout.addWidget(self.update_button)
        
        self.later_button = QPushButton("Later")
        self.later_button.clicked.connect(self.reject)
        button_layout.addWidget(self.later_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def start_update(self):
        """Start the update process."""
        # Hide buttons and show progress
        self.update_button.setVisible(False)
        self.later_button.setVisible(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        
        # Start worker thread
        self.worker = UpdateWorker(self.release_info)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.update_completed.connect(self.update_finished)
        self.worker.start()
    
    def update_progress(self, status, percentage):
        """Update progress display."""
        self.status_label.setText(status)
        self.progress_bar.setValue(percentage)
    
    def update_finished(self, success, message):
        """Handle update completion."""
        if success:
            QMessageBox.information(
                self,
                "Update Complete",
                "Update installation started. The application will restart automatically."
            )
            # Exit the application
            QApplication.instance().quit()
            sys.exit(0)
        else:
            QMessageBox.critical(self, "Update Error", message)
            self.reject()


class PyQtUpdateChecker:
    """PyQt5-based update checker with native GUI integration."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.current_version = CURRENT_VERSION
    
    def check_for_updates_silent(self):
        """Check for updates silently without UI."""
        try:
            if not self.is_internet_available():
                return None
            
            release_info = self.get_latest_release_info()
            if not release_info:
                return None
            
            if self.is_newer_version(release_info.get('tag_name', ''), self.current_version):
                return release_info
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return None
    
    def show_update_dialog(self, release_info):
        """Show update dialog and handle user choice."""
        try:
            dialog = UpdateDialog(release_info, self.parent)
            result = dialog.exec_()
            
            return result == QDialog.Accepted
            
        except Exception as e:
            self.logger.error(f"Error showing update dialog: {e}")
            return False
    
    def is_internet_available(self):
        """Check internet connection."""
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return True
        except urllib.error.URLError:
            return False
    
    def get_latest_release_info(self):
        """Get latest release info from GitHub."""
        try:
            req = urllib.request.Request(
                GITHUB_API_URL,
                headers={'User-Agent': 'SMIS-Updater'}
            )
            
            with urllib.request.urlopen(req, timeout=UPDATE_CHECK_TIMEOUT) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
                
        except Exception as e:
            self.logger.error(f"Error fetching release info: {e}")
            return None
    
    def is_newer_version(self, latest_version, current_version):
        """Compare version numbers."""
        try:
            latest = latest_version.lstrip('v').split('.')
            current = current_version.lstrip('v').split('.')
            
            max_len = max(len(latest), len(current))
            latest.extend(['0'] * (max_len - len(latest)))
            current.extend(['0'] * (max_len - len(current)))
            
            for l, c in zip(latest, current):
                if int(l) > int(c):
                    return True
                elif int(l) < int(c):
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error comparing versions: {e}")
            return False


def check_for_updates_with_gui(parent=None):
    """
    Check for updates with PyQt5 GUI integration.
    Call this from your main window after it's shown.
    """
    try:
        checker = PyQtUpdateChecker(parent)
        release_info = checker.check_for_updates_silent()
        
        if release_info:
            checker.show_update_dialog(release_info)
            
    except Exception as e:
        logging.error(f"Error in GUI update check: {e}")


if __name__ == "__main__":
    # Test the PyQt updater
    app = QApplication(sys.argv)
    
    checker = PyQtUpdateChecker()
    release_info = checker.check_for_updates_silent()
    
    if release_info:
        dialog = UpdateDialog(release_info)
        dialog.exec_()
    else:
        print("No updates available")
    
    app.quit()