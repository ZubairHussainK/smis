"""Enhanced application settings and constants."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_app_data_dir():
    """Get the application data directory for storing database and files."""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable
        # Use AppData directory for user data
        app_data = os.path.join(os.environ.get('APPDATA', ''), 'SMIS')
    else:
        # Running from source
        app_data = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure directory exists
    os.makedirs(app_data, exist_ok=True)
    return app_data

class Config:
    """Main configuration class."""
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Get application data directory
    APP_DATA_DIR = get_app_data_dir()
    
    # Database - Use absolute path in AppData for installed version
    DATABASE_PATH = os.path.join(APP_DATA_DIR, "school.db")
    DATABASE_BACKUP_PATH = os.path.join(APP_DATA_DIR, "backups")
    BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    ENCRYPTION_ENABLED = os.getenv('ENCRYPTION_ENABLED', 'True').lower() == 'true'
    
    # UI Settings
    WINDOW_TITLE = "School Management Information System"
    WINDOW_GEOMETRY = (100, 100, 1200, 800)
    THEME = os.getenv('THEME', 'modern')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_MAX_SIZE = int(os.getenv('LOG_FILE_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # Performance
    MAX_RECORDS_PER_PAGE = int(os.getenv('MAX_RECORDS_PER_PAGE', '50'))
    CACHE_TIMEOUT_SECONDS = int(os.getenv('CACHE_TIMEOUT_SECONDS', '300'))
    
    # Features
    ENABLE_AUDIT_LOG = os.getenv('ENABLE_AUDIT_LOG', 'True').lower() == 'true'
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'
    AUTO_BACKUP = os.getenv('AUTO_BACKUP', 'True').lower() == 'true'

# Student Fields Configuration
STUDENT_FIELDS = [
    "S#", "Name", "Mobile Number", "Organization", "BEMIS", "School Name",
    "Type of School", "UC", "B-Form Number", "Year of Admission",
    "Father's CNIC", "Father's Contact", "Guardian's Address", "Date of Birth",
    "Registration Number", "Gender", "Class Teacher", "S# as per Register",
    "Class 2025", "Section", "Father's Name", "Class Status",
    "Verification Status", "Status", "Remarks"
]

# Required fields for data validation
REQUIRED_STUDENT_FIELDS = ["S#", "Name", "School Name", "Class 2025", "Section"]

# Field validation patterns
VALIDATION_PATTERNS = {
    "mobile": r"^(\+92|0)?[0-9]{10}$",
    "cnic": r"^[0-9]{5}-[0-9]{7}-[0-9]$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
}

# Keyboard shortcuts
SHORTCUTS = {
    "save": "Ctrl+S",
    "new": "Ctrl+N",
    "delete": "Delete",
    "refresh": "F5",
    "print": "Ctrl+P",
    "logout": "Ctrl+L",
    "search": "Ctrl+F",
    "backup": "Ctrl+B"
}

# User roles and permissions
USER_ROLES = {
    'admin': {
        'permissions': ['create', 'read', 'update', 'delete', 'backup', 'user_management'],
        'description': 'Full system access'
    },
    'teacher': {
        'permissions': ['create', 'read', 'update', 'attendance'],
        'description': 'Student and attendance management'
    },
    'staff': {
        'permissions': ['read', 'attendance'],
        'description': 'View and mark attendance only'
    },
    'viewer': {
        'permissions': ['read'],
        'description': 'Read-only access'
    }
}

# Database connection settings
DATABASE_CONFIG = {
    'timeout': 30,
    'check_same_thread': False,
    'isolation_level': None
}
