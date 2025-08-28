"""
Test Configuration and Utilities.

Common test utilities and configuration for the SMIS test suite.
"""

import sys
import os
import logging
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

# Add project root to Python path for testing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Disable Qt warnings during testing
os.environ['QT_LOGGING_RULES'] = '*=false'

class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.students = [
            {"s_no": "001", "name": "Ahmed Ali", "class_2025": "Class 5", "section": "A"},
            {"s_no": "002", "name": "Fatima Khan", "class_2025": "Class 5", "section": "A"},
            {"s_no": "003", "name": "Hassan Ahmed", "class_2025": "Class 6", "section": "B"},
        ]
        self.attendance = {}
    
    def get_students(self, page=1, per_page=500):
        """Mock get_students method."""
        return {"students": self.students}
    
    def get_attendance(self, student_id=None):
        """Mock get_attendance method."""
        return self.attendance.get(str(student_id), [])
    
    def mark_attendance(self, student_id, date, status):
        """Mock mark_attendance method."""
        if str(student_id) not in self.attendance:
            self.attendance[str(student_id)] = []
        
        # Remove existing record for the date
        self.attendance[str(student_id)] = [
            record for record in self.attendance[str(student_id)]
            if record.get('date') != date
        ]
        
        # Add new record
        self.attendance[str(student_id)].append({
            'date': date,
            'status': status
        })
        return True

def get_test_student_data() -> Dict[str, Any]:
    """Get sample student data for testing."""
    return {
        "id": "001",
        "roll": "001",
        "name": "Test Student",
        "class": "Class 5",
        "section": "A"
    }

def create_mock_qt_app():
    """Create a mock Qt application for testing."""
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QDate
    
    if not QApplication.instance():
        app = QApplication([])
        return app
    return QApplication.instance()

class TestConstants:
    """Test constants and configuration."""
    
    SAMPLE_DATES = [
        "2025-08-01",  # Friday
        "2025-08-02",  # Saturday  
        "2025-08-03",  # Sunday (weekend)
        "2025-08-04",  # Monday
        "2025-08-05",  # Tuesday
    ]
    
    VALID_STATUSES = [
        "Present",
        "Absent",
        "Late",
        "Excused",
        "Holiday"
    ]
    
    INVALID_STATUSES = [
        "Unknown",
        "Maybe",
        "",
        None
    ]
