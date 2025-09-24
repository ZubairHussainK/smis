# SMIS Update Configuration
# ========================
# This file contains configuration for the SMIS auto-update system

# GitHub Repository Information
GITHUB_OWNER = "ZubairHussainK"
GITHUB_REPO = "smis"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

# Update Settings
UPDATE_CHECK_TIMEOUT = 10  # seconds
AUTO_CHECK_ON_STARTUP = True
SILENT_UPDATES = False

# Encryption Settings
# This key should match the ENCRYPT_KEY secret in GitHub Actions
# Change this to match your actual encryption key
ENCRYPT_KEY = "smis_secure_update_key_2024"

# Update Channels
# stable: Only stable releases
# beta: Include pre-releases
UPDATE_CHANNEL = "stable"

# Download Settings
TEMP_DOWNLOAD_DIR = "temp"
INSTALLER_NAME_PATTERN = "*-encrypted.exe"

# Logging
UPDATE_LOG_LEVEL = "INFO"
UPDATE_LOG_FILE = "logs/updates.log"

# UI Settings
SHOW_UPDATE_NOTIFICATIONS = True
SHOW_UPDATE_PROGRESS = True
REMEMBER_UPDATE_CHOICE = False  # Remember "Skip this version"

# Installation Settings
SILENT_INSTALL = True  # Use /S flag for NSIS installer
RESTART_AFTER_UPDATE = True
BACKUP_BEFORE_UPDATE = True

# Network Settings
CONNECTION_TIMEOUT = 10
DOWNLOAD_TIMEOUT = 300  # 5 minutes
MAX_DOWNLOAD_RETRIES = 3

# Security Settings
VERIFY_SIGNATURES = True  # Future feature
CHECK_HASH = True  # Future feature
ALLOW_DOWNGRADE = False

# Advanced Settings
DEBUG_MODE = False
SKIP_VERSION_CHECK = False  # For testing
FORCE_UPDATE_CHECK = False  # For testing