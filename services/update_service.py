"""
SMIS Auto-Updater System
========================
Checks for updates on application startup and handles automatic updates.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging
from version import __version__ as CURRENT_VERSION

import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging
from version import __version__ as CURRENT_VERSION

# Import configuration
try:
    from config.update_config import *
except ImportError:
    # Fallback configuration
    GITHUB_API_URL = "https://api.github.com/repos/ZubairHussainK/smis/releases/latest"
    ENCRYPT_KEY = "smis_secure_update_key_2024"
    UPDATE_CHECK_TIMEOUT = 10

class UpdateChecker:
    """Handles checking and installing updates for the SMIS application."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_version = CURRENT_VERSION
        
    def check_for_updates_on_startup(self):
        """
        Check for updates on application startup.
        Returns True if app should continue, False if update is being installed.
        """
        try:
            # Check internet connection first
            if not self.is_internet_available():
                self.logger.info("No internet connection. Skipping update check.")
                return True
            
            self.logger.info("Checking for updates...")
            
            # Get latest release info
            release_info = self.get_latest_release_info()
            if not release_info:
                self.logger.warning("Could not fetch release information.")
                return True
            
            # Compare versions
            if self.is_newer_version(release_info.get('tag_name', ''), self.current_version):
                return self.show_update_dialog(release_info)
            else:
                self.logger.info("Application is up to date.")
                return True
                
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return True  # Continue with app launch on error
    
    def is_internet_available(self):
        """Check if internet connection is available."""
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return True
        except urllib.error.URLError:
            return False
    
    def get_latest_release_info(self):
        """Fetch latest release information from GitHub API."""
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
        """Compare version numbers to determine if an update is available."""
        try:
            # Remove 'v' prefix if present
            latest = latest_version.lstrip('v').split('.')
            current = current_version.lstrip('v').split('.')
            
            # Pad with zeros to make equal length
            max_len = max(len(latest), len(current))
            latest.extend(['0'] * (max_len - len(latest)))
            current.extend(['0'] * (max_len - len(current)))
            
            # Convert to integers and compare
            for l, c in zip(latest, current):
                if int(l) > int(c):
                    return True
                elif int(l) < int(c):
                    return False
            
            return False  # Versions are equal
            
        except Exception as e:
            self.logger.error(f"Error comparing versions: {e}")
            return False
    
    def show_update_dialog(self, release_info):
        """Show update dialog and handle user choice."""
        try:
            # Create root window (hidden)
            root = tk.Tk()
            root.withdraw()
            
            # Show update dialog
            result = messagebox.askyesno(
                "Update Available",
                f"A new update is available!\n\n"
                f"Current Version: v{self.current_version}\n"
                f"Latest Version: {release_info.get('tag_name', 'Unknown')}\n\n"
                f"Do you want to download and install it?",
                icon='question'
            )
            
            root.destroy()
            
            if result:
                # User chose to update
                return self.download_and_install_update(release_info)
            else:
                # User chose to update later
                self.logger.info("User postponed update.")
                return True
                
        except Exception as e:
            self.logger.error(f"Error showing update dialog: {e}")
            return True
    
    def download_and_install_update(self, release_info):
        """Download and install the update."""
        try:
            # Find the encrypted installer asset
            asset = self.find_installer_asset(release_info.get('assets', []))
            if not asset:
                messagebox.showerror("Update Error", "Could not find installer in release assets.")
                return True
            
            # Show progress window
            progress_window = self.create_progress_window()
            
            def update_thread():
                try:
                    # Update progress
                    self.update_progress(progress_window, "Downloading update...", 10)
                    
                    # Download encrypted file
                    temp_dir = tempfile.gettempdir()
                    encrypted_path = os.path.join(temp_dir, asset['name'])
                    decrypted_path = os.path.join(temp_dir, asset['name'].replace('-encrypted', ''))
                    
                    self.download_file(asset['browser_download_url'], encrypted_path, progress_window)
                    
                    # Update progress
                    self.update_progress(progress_window, "Decrypting installer...", 80)
                    
                    # Decrypt the installer
                    if self.decrypt_file(encrypted_path, decrypted_path):
                        self.update_progress(progress_window, "Starting installation...", 90)
                        
                        # Close progress window
                        progress_window.destroy()
                        
                        # Run the installer
                        subprocess.Popen([decrypted_path, '/S'])  # Silent install
                        
                        # Exit current application
                        sys.exit(0)
                    else:
                        progress_window.destroy()
                        messagebox.showerror("Update Error", "Failed to decrypt installer.")
                        
                except Exception as e:
                    progress_window.destroy()
                    self.logger.error(f"Update error: {e}")
                    messagebox.showerror("Update Error", f"Error during update: {str(e)}")
            
            # Start update in separate thread
            thread = threading.Thread(target=update_thread)
            thread.daemon = True
            thread.start()
            
            return False  # Don't continue with app launch
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            messagebox.showerror("Update Error", f"Error downloading update: {str(e)}")
            return True
    
    def find_installer_asset(self, assets):
        """Find the encrypted installer asset from release assets."""
        for asset in assets:
            if asset['name'].endswith('-encrypted.exe'):
                return asset
        return None
    
    def create_progress_window(self):
        """Create and show a progress window."""
        window = tk.Tk()
        window.title("SMIS Update")
        window.geometry("400x100")
        window.resizable(False, False)
        
        # Center the window
        window.eval('tk::PlaceWindow . center')
        
        # Status label
        status_label = tk.Label(window, text="Initializing...", font=('Arial', 10))
        status_label.pack(pady=10)
        
        # Progress bar (using a simple label for now)
        progress_label = tk.Label(window, text="0%", font=('Arial', 8))
        progress_label.pack(pady=5)
        
        # Store references
        window.status_label = status_label
        window.progress_label = progress_label
        
        window.update()
        return window
    
    def update_progress(self, window, status, percentage):
        """Update progress window."""
        try:
            window.status_label.config(text=status)
            window.progress_label.config(text=f"{percentage}%")
            window.update()
        except:
            pass  # Window might be destroyed
    
    def download_file(self, url, file_path, progress_window):
        """Download file with progress updates."""
        try:
            def reporthook(block_num, block_size, total_size):
                if total_size > 0:
                    percentage = min(70, 10 + int((block_num * block_size / total_size) * 60))
                    self.update_progress(progress_window, "Downloading update...", percentage)
            
            urllib.request.urlretrieve(url, file_path, reporthook)
            
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            raise
    
    def decrypt_file(self, encrypted_path, decrypted_path):
        """Decrypt the downloaded installer file."""
        try:
            # Generate the same key as used in GitHub Actions
            key = self.derive_key(ENCRYPT_KEY)
            f = Fernet(key)
            
            # Read encrypted data
            with open(encrypted_path, 'rb') as file:
                encrypted_data = file.read()
            
            # Decrypt
            decrypted_data = f.decrypt(encrypted_data)
            
            # Write decrypted file
            with open(decrypted_path, 'wb') as file:
                file.write(decrypted_data)
            
            # Clean up encrypted file
            os.remove(encrypted_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            return False
    
    def derive_key(self, password):
        """Derive encryption key using the same method as GitHub Actions."""
        password_bytes = password.encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'smis_salt_2024',
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key


def check_for_updates_and_launch():
    """
    Main function to check for updates and launch the application.
    Call this from your main.py before starting the GUI.
    """
    updater = UpdateChecker()
    should_continue = updater.check_for_updates_on_startup()
    
    if should_continue:
        logging.info("Proceeding with application startup...")
        return True
    else:
        logging.info("Update is being installed. Exiting application.")
        return False


if __name__ == "__main__":
    # Test the updater
    logging.basicConfig(level=logging.INFO)
    
    if check_for_updates_and_launch():
        print("Application would start normally here.")
    else:
        print("Update is being installed.")