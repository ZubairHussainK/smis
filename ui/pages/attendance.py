import sys
import os
import logging

# Add project root to Python path for direct execution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

# Import unittest.mock for standalone mode mocking
if __name__ == "__main__":
    from unittest.mock import MagicMock

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QFrame, QLineEdit,
                           QTableWidget, QTableWidgetItem, QSplitter, QScrollArea,
                           QGridLayout, QSpacerItem, QSizePolicy, QCheckBox, QHeaderView,
                           QDialog, QSpinBox)
# Fix imports for both direct execution and normal imports
try:
    from ui.components.custom_combo_box import CustomComboBox
except ImportError:
    from components.custom_combo_box import CustomComboBox
    
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QIcon

# Import styling and calendar functions - handle both direct execution and normal imports
try:
    from resources.styles import (get_attendance_styles, 
                               show_info_message, COLORS, SPACING_MD, SPACING_LG)
    from models.database import Database
    from ui.components.custom_table import SMISTable
except ImportError:
    # Fallback imports when running directly
    from resources.styles import (get_attendance_styles, 
                               show_info_message, COLORS, SPACING_MD, SPACING_LG)
    from models.database import Database
    from components.custom_table import SMISTable

# We're implementing ModernCalendarWidget directly in this file, so it should be available
CALENDAR_AVAILABLE = True
print("✅ ModernCalendarWidget loaded successfully with responsive sizing")

# Define month/year selection dialogs
class MonthSelectionDialog(QDialog):
    """Dialog for selecting a month."""
    
    def __init__(self, parent=None, current_month=1):
        """Initialize the month selection dialog."""
        super().__init__(parent)
        self.setWindowTitle("Select Month")
        self.setModal(True)
        self.setFixedSize(340, 210)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        # Set application icon
        from utils.ui_helpers import set_app_icon
        set_app_icon(self)
        
        # Store the current month
        self.current_month = current_month
        self.selected_month = current_month
        
        # Add enhanced shadow effect and rounded corners
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid rgba(209, 213, 219, 0.8);
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Set up the UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI elements."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header container (blue bar) - enhanced with gradient
        header_container = QFrame()
        header_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_container.setFixedHeight(40)
        header_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                              stop:0 #0175b6, stop:1 #0ea5e9);
                border-radius: 6px 6px 0px 0px;
                border: none;
                padding: 0px;
                margin: 0px;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Header layout within container
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(2, 0, 2, 0)
        header_layout.setSpacing(0)
        
        # Get current month name
        month_names = ["", "January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
        current_month_name = month_names[self.current_month] if 1 <= self.current_month <= 12 else ""
        
        # Header label - show selected month name
        header = QLabel(f"{current_month_name}")
        header.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 0px;
        """)
        header.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header)
        
        # Add header container to main layout
        main_layout.addWidget(header_container)
        
        # Container frame for months grid
        months_container = QFrame()
        months_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: none;
            }
        """)
        months_container_layout = QVBoxLayout(months_container)
        months_container_layout.setContentsMargins(0, 0, 0, 0)
        months_container_layout.setSpacing(0)
        
        # Create grid for month buttons (3x4 grid - 3 rows, 4 columns)
        months_grid = QGridLayout()
        months_grid.setContentsMargins(0, 0, 0, 0)
        months_grid.setSpacing(5)
        
        # Month names - abbreviated with fixed width
        month_data = [
            ("Jan", 1), ("Feb", 2), ("Mar", 3), ("Apr", 4),
            ("May", 5), ("Jun", 6), ("Jul", 7), ("Aug", 8),
            ("Sep", 9), ("Oct", 10), ("Nov", 11), ("Dec", 12)
        ]
        
        # Create buttons for each month
        for i, (month_name, month_num) in enumerate(month_data):
            row = i // 4
            col = i % 4
            
            # Create button with month name
            month_btn = QPushButton(month_name)
            
            # Fixed dimensions to prevent text cut-off
            month_btn.setFixedSize(60, 40)
            month_btn.setCursor(Qt.PointingHandCursor)
            
            # Set button style - highlight current month with enhanced circle design
            is_current = month_num == self.current_month
            if is_current:
                month_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0175b6;
                        color: white;
                        border: 3px solid #38bdf8;
                        border-radius: 20px;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #0186d1;
                        border: 3px solid #7dd3fc;
                    }
                    QPushButton:pressed {
                        background-color: #015d8c;
                        border: 3px solid #38bdf8;
                    }
                """)
            else:
                month_btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 20px;
                        color: #333333;
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #f0f9ff;
                        border: 1px solid #bae6fd;
                        color: #0175b6;
                    }
                    QPushButton:pressed {
                        background-color: #e0f2fe;
                        border: 1px solid #7dd3fc;
                    }
                """)
            
            # Connect button to slot with explicit month number
            month_btn.clicked.connect(lambda checked=False, m=month_num: self._on_month_selected(m))
            
            # Add to grid
            months_grid.addWidget(month_btn, row, col)
        
        # Add grid to container layout
        months_container_layout.addLayout(months_grid)
        
        # Add container to main layout
        main_layout.addWidget(months_container)
    
    def _on_month_selected(self, month):
        """Handle month selection."""
        print(f"Month selected: {month}")
        self.selected_month = month
        self.accept()


class YearSelectionDialog(QDialog):
    """Dialog for selecting a year."""
    
    def __init__(self, parent=None, current_year=2025):
        """Initialize the year selection dialog."""
        super().__init__(parent)
        self.setWindowTitle("Select Year")
        self.setModal(True)
        self.setFixedSize(340, 240)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        # Set application icon
        from utils.ui_helpers import set_app_icon
        set_app_icon(self)
        
        # Store the current year and calculate range
        self.current_year = current_year
        self.selected_year = current_year
        self.start_year = (current_year // 12) * 12
        
        # Add enhanced shadow effect and rounded corners
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid rgba(209, 213, 219, 0.8);
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Set up the UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI elements."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header container (blue bar) - enhanced with gradient
        header_container = QFrame()
        header_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_container.setFixedHeight(40)
        header_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                              stop:0 #0175b6, stop:1 #0ea5e9);
                border-radius: 6px 6px 0px 0px;
                border: none;
                padding: 0px;
                margin: 0px;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Header layout within container
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(2, 0, 2, 0)
        header_layout.setSpacing(0)
        
        # Previous years button - enhanced with circular design
        self.prev_btn = QPushButton()
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Set icon or text for prev button
        self.prev_btn.setText("<")
        self.prev_btn.clicked.connect(self._show_prev_years)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        
        # Header label
        year_range_text = f"{self.start_year} - {self.start_year + 11}"
        self.header_label = QLabel(year_range_text)
        self.header_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 0px;
        """)
        self.header_label.setAlignment(Qt.AlignCenter)
        
        # Next years button - enhanced with circular design
        self.next_btn = QPushButton()
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Set icon or text for next button
        self.next_btn.setText(">")
        self.next_btn.clicked.connect(self._show_next_years)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        
        # Add elements to header layout
        header_layout.addWidget(self.prev_btn)
        header_layout.addWidget(self.header_label, 1)  # 1 = stretch factor
        header_layout.addWidget(self.next_btn)
        
        # Add header container to main layout
        layout.addWidget(header_container)
        
        # Container frame for the years grid
        years_container = QFrame()
        years_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: none;
            }
        """)
        years_container_layout = QVBoxLayout(years_container)
        years_container_layout.setContentsMargins(0, 0, 0, 0)
        years_container_layout.setSpacing(0)
        
        # Create grid for year buttons (3x4 grid = 12 years)
        self.years_grid = QGridLayout()
        self.years_grid.setContentsMargins(0, 0, 0, 0)
        self.years_grid.setSpacing(5)  # Optimized spacing for the grid
        
        # Update the grid with years
        self._update_years_grid()
        
        # Add grid to container layout
        years_container_layout.addLayout(self.years_grid)
        
        # Add years container to main layout
        layout.addWidget(years_container)
        
    def _update_years_grid(self):
        """Update the grid with the current range of years."""
        # Clear existing buttons first
        while self.years_grid.count():
            item = self.years_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Update the header label with nicer formatting
        year_range_text = f"{self.start_year} - {self.start_year + 11}"
        self.header_label.setText(year_range_text)
        
        # Create buttons for each year in range
        for i in range(12):
            row = i // 4
            col = i % 4
            
            year = self.start_year + i
            
            # Create button with year
            year_btn = QPushButton(str(year))
            
            # Fixed dimensions to prevent text cut-off
            year_btn.setFixedSize(60, 40)
            year_btn.setCursor(Qt.PointingHandCursor)
            
            # Set button style - highlight current year with enhanced circle design
            is_current = year == self.current_year
            if is_current:
                year_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0175b6;
                        color: white;
                        border:none;
                        border-radius: 20px;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background-color: #0186d1;
                        border: 3px solid #7dd3fc;
                    }
                    QPushButton:pressed {
                        background-color: #015d8c;
                        border: 3px solid #38bdf8;
                    }
                """)
            else:
                year_btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: border:none;;
                        border-radius: 20px;
                        color: #333333;
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background-color: #f0f9ff;
                        border: 1px solid #bae6fd;
                        color: #0175b6;
                    }
                    QPushButton:pressed {
                        background-color: #e0f2fe;
                        border: 1px solid #7dd3fc;
                    }
                """)
            
            # Connect button to slot
            year_btn.clicked.connect(lambda checked=False, y=year: self._on_year_selected(y))
            
            # Add to grid
            self.years_grid.addWidget(year_btn, row, col)
    
    def _on_year_selected(self, year):
        """Handle year selection."""
        print(f"Year selected: {year}")
        self.selected_year = year
        self.accept()
    
    def _show_prev_years(self):
        """Show previous set of years."""
        self.start_year -= 12
        self._update_years_grid()
    
    def _show_next_years(self):
        """Show next set of years."""
        self.start_year += 12
        self._update_years_grid()

# ModernCalendarWidget - Direct implementation 
class ModernCalendarWidget(QWidget):
    """Custom calendar widget with compact modern design - no separate footer buttons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self._attendance_data = {}
        self.current_date = QDate.currentDate()
        self.selected_date = QDate.currentDate()
        self.setFocusPolicy(Qt.StrongFocus)  # Allow keyboard focus
        
        self._setup_ui()
        self._setup_signals()
        self._update_display()
        
        # Enable focus and key events - critical for keyboard shortcuts
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure calendar can receive keyboard focus
        self.setFocusProxy(None)  # Don't delegate focus to children
        self.setAttribute(Qt.WA_AcceptDrops, False)  # We don't need drops
        self.setAttribute(Qt.WA_KeyCompression, False)  # Handle all key events
        
    def _setup_ui(self):
        """Setup the responsive modern calendar UI with flexible layout."""
        # Set responsive sizing to use available space
        self.setMinimumSize(400, 300)  # Minimum size for readability
        # Remove maximum size to allow expansion
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Expanding size policy
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Zero margins for maximum space
        layout.setSpacing(0)
        
        # Apply main calendar styling with enhanced design
        self.setStyleSheet("""
            ModernCalendarWidget {
                background: white;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
                
            }
        """)
        
        # Single unified calendar container
        self.calendar_container = QFrame()
        self.calendar_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                margin: 0px;
                border: none;
                min-width: 400px;
                min-height: 300px;
            }
        """)
        
        # Single container layout - no nested layouts
        container_layout = QVBoxLayout(self.calendar_container)
        container_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins
        container_layout.setSpacing(0)  # No extra spacing
        
        # Header section (month/year selectors)
        self._create_header_section(container_layout)
        
        # Calendar body
        self._create_calendar_body(container_layout)
        
        layout.addWidget(self.calendar_container)
        
    def _create_header_section(self, parent_layout):
        """Create the header with properly visible month/year selectors."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid #e2e8f0;
                min-height: 30px;
                max-height: 30px;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)  # Better margins for visibility
        header_layout.setSpacing(12)  # Better spacing between dropdowns
        
        # Store the months list for reference
        self.months = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
                      
        # Month button that shows selection dialog when clicked
        self.month_button = QPushButton(self.months[self.current_date.month() - 1])
        self.month_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: #111827;
                font-weight: 500;
                min-height: 32px;
                max-height: 32px;
                padding-top: 0px;
                padding-bottom: 0px;
                padding-left: 16px; 
                padding-right: 16px;
                text-align: center;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #f3f4f6;
            }
        """)
        self.month_button.setCursor(Qt.PointingHandCursor)
        self.month_button.clicked.connect(self.show_month_selection)
        
        # Year button that shows selection dialog when clicked
        self.year_button = QPushButton(str(self.current_date.year()))
        self.year_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: #111827;
                font-weight: 500;
                min-height: 32px;
                max-height: 32px;
                padding-top: 0px;
                padding-bottom: 0px;
                padding-left: 16px; 
                padding-right: 16px;
                text-align: center;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #f3f4f6;
            }
        """)
        self.year_button.setCursor(Qt.PointingHandCursor)
        self.year_button.clicked.connect(self.show_year_selection)
        
        # Add the buttons to the header layout
        header_layout.addWidget(self.month_button)
        header_layout.addWidget(self.year_button)
        
        # Add the header to parent layout
        parent_layout.addWidget(header)
        
    def show_month_selection(self):
        """Show month selection dialog."""
        print("Month button clicked - showing month selection dialog")
        
        # Create and show the month selection dialog
        dialog = MonthSelectionDialog(self, self.current_date.month())
        
        # Position the dialog below the calendar
        button_pos = self.month_button.mapToGlobal(self.month_button.rect().bottomLeft())
        dialog_x = button_pos.x()
        dialog_y = button_pos.y() + 5
        dialog.move(dialog_x, dialog_y)
        
        # Show the dialog and handle the result
        if dialog.exec_():
            selected_month = dialog.selected_month
            self.month_button.setText(self.months[selected_month - 1])
            self.current_date = QDate(self.current_date.year(), selected_month, 1)
            
            # Preserve selected day if possible, or use the 1st if day is invalid for the new month
            day = min(self.selected_date.day(), self.current_date.daysInMonth())
            self.selected_date = QDate(self.current_date.year(), selected_month, day)
            
            self._update_display()
            
            # Notify parent of date change
            if self.parent_widget and hasattr(self.parent_widget, 'on_modern_calendar_date_changed'):
                self.parent_widget.on_modern_calendar_date_changed()
    
    def show_year_selection(self):
        """Show year selection dialog."""
        print("Year button clicked - showing year selection dialog")
        
        # Create and show the year selection dialog
        dialog = YearSelectionDialog(self, self.current_date.year())
        
        # Position the dialog below the calendar
        button_pos = self.year_button.mapToGlobal(self.year_button.rect().bottomLeft())
        dialog_x = button_pos.x()
        dialog_y = button_pos.y() + 5
        dialog.move(dialog_x, dialog_y)
        
        # Show the dialog and handle the result
        if dialog.exec_():
            selected_year = dialog.selected_year
            self.year_button.setText(str(selected_year))
            self.current_date = QDate(selected_year, self.current_date.month(), 1)
            
            # Preserve selected day if possible, or use the 1st if day is invalid 
            day = min(self.selected_date.day(), self.current_date.daysInMonth())
            self.selected_date = QDate(selected_year, self.current_date.month(), day)
            
            self._update_display()
            
            # Notify parent of date change
            if self.parent_widget and hasattr(self.parent_widget, 'on_modern_calendar_date_changed'):
                self.parent_widget.on_modern_calendar_date_changed()
    
    def on_month_changed(self, month_name):
        """Handle month selection change."""
        try:
            months = ["January", "February", "March", "April", "May", "June", 
                     "July", "August", "September", "October", "November", "December"]
            month_index = months.index(month_name) + 1
            
            # Update current date and refresh calendar
            new_date = QDate(self.current_date.year(), month_index, 1)
            self.current_date = new_date
            
            # Update the selected date to be in the new month too
            day = min(self.selected_date.day(), new_date.daysInMonth())
            self.selected_date = QDate(self.current_date.year(), month_index, day)
            
            self._update_display()
            print(f"📅 Month changed to: {month_name}")
            
            # Notify parent of date change
            if self.parent_widget and hasattr(self.parent_widget, 'on_modern_calendar_date_changed'):
                self.parent_widget.on_modern_calendar_date_changed()
        except Exception as e:
            print(f"❌ Month change failed: {e}")
    
    def on_year_changed(self, year):
        """Handle year selection change."""
        try:
            # Update current date and refresh calendar
            new_date = QDate(year, self.current_date.month(), 1)
            self.current_date = new_date
            
            # Update the selected date to be in the new year too
            day = min(self.selected_date.day(), new_date.daysInMonth())
            self.selected_date = QDate(year, self.current_date.month(), day)
            
            self._update_display()
            print(f"📅 Year changed to: {year}")
            
            # Notify parent of date change
            if self.parent_widget and hasattr(self.parent_widget, 'on_modern_calendar_date_changed'):
                self.parent_widget.on_modern_calendar_date_changed()
        except Exception as e:
            print(f"❌ Year change failed: {e}")
        
    def _create_calendar_body(self, parent_layout):
        """Create the compact calendar body."""
        body = QFrame()
        body.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
      
        body_layout.setSpacing(0)
        
        # Day headers
        self._create_day_headers(body_layout)
        
        # Date grid
        self._create_date_grid(body_layout)
        
        parent_layout.addWidget(body)
        
    def _create_day_headers(self, parent_layout):
        """Create compact day name headers with proper spacing."""
        days_frame = QFrame()
        days_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                min-height: 32px;
                max-height: 32px;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Use grid layout to match the date grid below exactly
        days_layout = QGridLayout(days_frame)
        days_layout.setContentsMargins(0, 0, 0, 0)
        days_layout.setHorizontalSpacing(2)  # Match date grid spacing
        days_layout.setVerticalSpacing(0)
        
        day_abbrevs = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        for i, abbrev in enumerate(day_abbrevs):
            day_label = QLabel(abbrev)
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setFixedSize(32, 28)  # Match date button size
            day_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            
            # Only highlight Sunday as weekend (index 6)
            if i == 6:  # Sunday only
                day_label.setStyleSheet("""
                    QLabel {
                        color: #dc2626;
                        font-weight: 700;
                        font-size: 12px;
                        text-align: center;
                        border: none;
                        background: transparent;
                        min-width: 32px;
                        max-width: 32px;
                        width: 32px;
                    }
                """)
            else:  # Monday to Saturday are working days
                day_label.setStyleSheet("""
                    QLabel {
                        color: #374151;
                        font-weight: 700;
                        font-size: 12px;
                        text-align: center;
                        border: none;
                        background: transparent;
                        min-width: 32px;
                        max-width: 32px;
                        width: 32px;
                    }
                """)
            
            # Add to grid layout at row 0, column i with center alignment
            days_layout.addWidget(day_label, 0, i, Qt.AlignCenter)
            
        parent_layout.addWidget(days_frame)
        
    def _create_date_grid(self, parent_layout):
        """Create a properly spaced date grid to prevent number overlap."""
        dates_frame = QFrame()
        dates_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Single grid layout with zero margins and minimal spacing
        self.dates_layout = QGridLayout(dates_frame)
        self.dates_layout.setContentsMargins(0, 0, 0, 0)  # Zero margins as requested
        self.dates_layout.setHorizontalSpacing(2)  # Minimal horizontal spacing
        self.dates_layout.setVerticalSpacing(2)  # Minimal vertical spacing
        
        # Create properly sized date buttons with adequate space for numbers
        self.date_buttons = []
        for week in range(6):
            week_buttons = []
            for day in range(7):
                btn = QPushButton()
                btn.setFixedSize(32, 32)  # Optimal size for date numbers without overlap
                btn.clicked.connect(lambda checked, w=week, d=day: self._on_date_clicked(w, d))
                self._style_date_button(btn)
                # Add to grid with proper alignment
                self.dates_layout.addWidget(btn, week, day, Qt.AlignCenter)
                week_buttons.append(btn)
            self.date_buttons.append(week_buttons)
            
        parent_layout.addWidget(dates_frame)
        
    def _style_date_button(self, button, state="normal"):
        """Apply enhanced styling to date button with proper non-overlapping circular design."""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 18px;
                font-weight: 700;
                font-size: 13px;
                background: transparent;
                color: #1f2937;
                width: 36px;
                height: 36px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                text-align: center;
                padding: 0px;
                margin: 0px;
            }
        """
        
        # Check if this button is for today's date
        is_today = button.property("is_today") == True
        today_border = "border: 3px solid #dc2626;" if is_today else "border: none;"
        
        if state == "normal":
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    background: transparent;
                    color: #1f2937;
                    {today_border}
                }}
                QPushButton:hover {{
                    background: #e0f2fe;
                    color: #0c4a6e;
                    border-radius: 18px;
                }}
            """)
        elif state == "grey":
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    color: #d1d5db;
                    font-weight: 500;
                    font-size: 12px;
                    {today_border}
                }}
                QPushButton:hover {{
                    background: #f3f4f6;
                    color: #9ca3af;
                    border-radius: 18px;
                }}
            """)
        elif state == "selected":
            # Strong selected state that works with and without focus - with pronounced circular border
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    background: #0175b6;
                    color: white;
                    {today_border}
                    border-radius: 18px;
                    font-weight: 800;
                    font-size: 14px;
                    margin: 0px;
                    padding: 0px;
                    /* Add subtle outer glow effect */
                    box-shadow: 0 0 8px #60a5fa;
                }}
                QPushButton:hover {{
                    background: #0070af;
                    color: white;
                }}
            """)
        elif state == "today":
            button.setStyleSheet(base_style + """
                QPushButton {
                    background: transparent;
                    color: #1f2937;
                    border: 3px solid #dc2626;
                    border-radius: 18px;
                    font-weight: 800;
                    margin: 0px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background: #ef4444;
                    color: white;
                }
            """)
        elif state == "attendance_present":
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    background: #059669;
                    color: white;
                    {today_border}
                    border-radius: 18px;
                    font-weight: 800;
                    margin: 0px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: #10b981;
                }}
            """)
        elif state == "attendance_absent":
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    background: #d97706;
                    color: white;
                    {today_border}
                    border-radius: 18px;
                    font-weight: 800;
                    margin: 0px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: #f59e0b;
                }}
            """)
        elif state == "attendance_late":
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    background: #7c3aed;
                    color: white;
                    {today_border}
                    border-radius: 18px;
                    font-weight: 800;
                    margin: 0px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: #8b5cf6;
                }}
            """)
        elif state == "attendance_holiday":
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    background: #0ea5e9;  /* Sky blue for holidays */
                    color: white;
                    {today_border}
                    border-radius: 18px;
                    font-weight: 800;
                }}
            """)
        elif state == "sunday_disabled":
            button.setStyleSheet(base_style + f"""
                QPushButton {{
                    background: #f9fafb;
                    color: #d1d5db;
                    {today_border}
                    border:none;
                    border-radius: 18px;
                    font-weight: 400;
                    opacity: 0.5;
                    }}
                )
            QPushButton:hover {{
                background: #f9fafb;
                color: #d1d5db;
                border: none;
                border-radius: 18px;
                cursor: not-allowed;
            }}
        """)
        
    def _setup_signals(self):
        """Setup signal connections."""
        # No need to connect signals here as we've connected them directly in _create_header_section
        pass
        
    def _update_display(self):
        """Update the calendar display for current month/year."""
        # Use the current_date's month and year, which are set through the buttons
        year = self.current_date.year()
        month = self.current_date.month()
        
        # Get first day of month and calculate calendar grid
        first_day = QDate(year, month, 1)
        days_in_month = first_day.daysInMonth()
        start_weekday = first_day.dayOfWeek() - 1  # Convert to 0-6 (Mon-Sun)
        
        # Clear all buttons first
        for week in self.date_buttons:
            for btn in week:
                btn.setText("")
                btn.setVisible(False)
                
        # Track which positions are filled
        filled_positions = set()
                
        # Previous month dates (grey)
        if start_weekday > 0:
            prev_month = first_day.addMonths(-1)
            prev_days = prev_month.daysInMonth()
            for i in range(start_weekday):
                day_num = prev_days - start_weekday + i + 1
                btn = self.date_buttons[0][i]
                btn.setText(str(day_num))
                btn.setVisible(True)
                btn.setProperty("text-align", "center")
                self._style_date_button(btn, "grey")
                filled_positions.add((0, i))
                
                # Current month dates
        date_counter = 1
        for week in range(6):
            for day in range(7):
                # Skip if position already filled with previous month date
                if (week, day) in filled_positions:
                    continue
                
                # Stop if we've placed all dates for this month
                if date_counter > days_in_month:
                    break
                    
                btn = self.date_buttons[week][day]
                btn.setText(str(date_counter))
                btn.setVisible(True)
                
                # Ensure text is centered
                btn.setProperty("text-align", "center")
                
                # Store the week and day position for this date in a property for later reference
                btn.setProperty("date_week", week)
                btn.setProperty("date_day", day)
                btn.setProperty("date_value", date_counter)                # Check if this is today, selected, or has attendance data
                current_date = QDate(year, month, date_counter)
                date_str = current_date.toString("yyyy-MM-dd")
                day_of_week = current_date.dayOfWeek()  # 1=Monday, 7=Sunday
                
                # Check if this is today's date
                is_today = current_date == QDate.currentDate()
                
                # Debug: Only print when we have attendance data and checking August 1-2
                has_attendance = self.parent_widget and self.parent_widget.attendance_data and date_str in self.parent_widget.attendance_data
                
                # Apply styling based on attendance data and status
                if current_date == self.selected_date and self.selected_date.isValid():
                    # Apply selected styling 
                    self._style_date_button(btn, "selected")
                    btn.setProperty("focused", self.hasFocus())
                    # For today's date add border
                    if is_today:
                        btn.setStyleSheet(btn.styleSheet().replace("border: none", "border: 3px solid #dc2626"))
                elif self.parent_widget and date_str in self.parent_widget.attendance_data:
                    # Apply attendance status styling
                    status = self.parent_widget.attendance_data[date_str].lower()
                    print(f"📅 Calendar styling date {date_str} with status: {status}")
                    if status == "present":
                        self._style_date_button(btn, "attendance_present")
                    elif status == "absent":
                        self._style_date_button(btn, "attendance_absent")
                    elif status == "late":
                        self._style_date_button(btn, "attendance_late")
                    elif status == "excused" or status == "leave":
                        self._style_date_button(btn, "attendance_late")  # Use purple for excused/leave
                    elif status == "holiday":
                        self._style_date_button(btn, "attendance_holiday")  # Add new style for holiday
                    else:
                        print(f"⚠️ Unknown status: {status}")
                        self._style_date_button(btn, "normal")
                    # For today's date add border
                    if is_today:
                        btn.setStyleSheet(btn.styleSheet().replace("border: none", "border: 3px solid #dc2626"))
                elif day_of_week == 7:  # Sunday - apply locked/disabled styling 
                    self._style_date_button(btn, "sunday_disabled")
                    btn.setToolTip(f"{current_date.toString('MMM dd, yyyy')}\n🔒 Sunday - Weekend (Locked)")
                    # For today's date add border
                    if is_today:
                        btn.setStyleSheet(btn.styleSheet().replace("border: none", "border: 3px solid #dc2626"))
                elif is_today:
                    # Today with no other special status
                    self._style_date_button(btn, "today")
                else:
                    # Regular working day
                    self._style_date_button(btn, "normal")
                
                filled_positions.add((week, day))
                date_counter += 1
                
        # Next month dates (grey) - fill remaining empty slots
        next_day_counter = 1
        for week in range(6):
            for day in range(7):
                # Skip if position already filled
                if (week, day) in filled_positions:
                    continue
                    
                btn = self.date_buttons[week][day]
                btn.setText(str(next_day_counter))
                btn.setVisible(True)
                btn.setProperty("text-align", "center")
                self._style_date_button(btn, "grey")
                next_day_counter += 1
                    
    def _on_month_changed(self):
        """Handle month change."""
        # Update the month button text
        if hasattr(self, 'month_button'):
            month_idx = self.current_date.month() - 1
            if 0 <= month_idx < len(self.months):
                self.month_button.setText(self.months[month_idx])
        
        self._update_display()
        # Notify parent of month change
        if self.parent_widget and hasattr(self.parent_widget, 'on_modern_calendar_date_changed'):
            self.parent_widget.on_modern_calendar_date_changed()
        
    def _on_year_changed(self):
        """Handle year change."""
        # Update the year button text
        if hasattr(self, 'year_button'):
            self.year_button.setText(str(self.current_date.year()))
        
        self._update_display()
        # Notify parent of year change
        if self.parent_widget and hasattr(self.parent_widget, 'on_modern_calendar_date_changed'):
            self.parent_widget.on_modern_calendar_date_changed()
            
    def keyPressEvent(self, event):
        """Handle keyboard navigation in calendar."""
        year = self.current_date.year()
        month = self.current_date.month()
        current_day = self.selected_date.day()
        
        if event.key() == Qt.Key_Left:
            # Move left one day
            new_date = self.selected_date.addDays(-1)
            if new_date.month() != month:
                # If day goes to previous month, update buttons
                self.current_date = QDate(new_date.year(), new_date.month(), 1)
                self.month_button.setText(self.months[new_date.month() - 1])
                self.year_button.setText(str(new_date.year()))
                self.selected_date = new_date
            else:
                self.selected_date = new_date
            self._update_display()
            event.accept()
            return True
            
        elif event.key() == Qt.Key_Right:
            # Move right one day
            new_date = self.selected_date.addDays(1)
            if new_date.month() != month:
                # If day goes to next month, update buttons
                self.current_date = QDate(new_date.year(), new_date.month(), 1)
                self.month_button.setText(self.months[new_date.month() - 1])
                self.year_button.setText(str(new_date.year()))
                self.selected_date = new_date
            else:
                self.selected_date = new_date
            self._update_display()
            event.accept()
            return True
            
        elif event.key() == Qt.Key_Up:
            # Move up one week
            new_date = self.selected_date.addDays(-7)
            if new_date.month() != month:
                # If week goes to previous month, update buttons
                self.current_date = QDate(new_date.year(), new_date.month(), 1)
                self.month_button.setText(self.months[new_date.month() - 1])
                self.year_button.setText(str(new_date.year()))
                self.selected_date = new_date
            else:
                self.selected_date = new_date
            self._update_display()
            event.accept()
            return True
            
        elif event.key() == Qt.Key_Down:
            # Move down one week
            new_date = self.selected_date.addDays(7)
            if new_date.month() != month:
                # If week goes to next month, update buttons
                self.current_date = QDate(new_date.year(), new_date.month(), 1)
                self.month_button.setText(self.months[new_date.month() - 1])
                self.year_button.setText(str(new_date.year()))
                self.selected_date = new_date
            else:
                self.selected_date = new_date
            self._update_display()
            event.accept()
            return True
            
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Select current date with Enter key
            if self.selected_date.dayOfWeek() == 7:  # Sunday
                # Block Sunday selection - show warning message
                from resources.styles import show_warning_message
                show_warning_message(
                    "Sunday Locked", 
                    "Sunday is a weekend day and cannot be selected for attendance.\n\nPlease select a working day (Monday-Saturday)."
                )
            else:
                # Notify parent of date selection
                if self.parent_widget and hasattr(self.parent_widget, 'on_date_clicked'):
                    self.parent_widget.on_date_clicked(self.selected_date)
            event.accept()
            return True
            
        # Let parent handle other keys
        return super().keyPressEvent(event)
        
    def _on_date_clicked(self, week, day):
        """Handle date button click - Block Sunday selection."""
        btn = self.date_buttons[week][day]
        if not btn.isVisible() or btn.styleSheet().find("#c5c8ca") != -1:  # Grey date
            return
            
        day_num = int(btn.text())
        year = self.current_date.year()
        month = self.current_date.month()
        
        # Create the date to check if it's Sunday
        clicked_date = QDate(year, month, day_num)
        
        # Block Sunday selection - show warning message
        if clicked_date.dayOfWeek() == 7:  # Sunday
            from resources.styles import show_warning_message
            show_warning_message(
                "Sunday Locked", 
                "Sunday is a weekend day and cannot be selected for attendance.\n\nPlease select a working day (Monday-Saturday)."
            )
            return
        
        self.selected_date = clicked_date
        self._update_display()
        
        # Make sure the calendar keeps focus after clicking a date
        self.setFocus()
        
        # Notify parent
        if self.parent_widget and hasattr(self.parent_widget, 'on_date_clicked'):
            self.parent_widget.on_date_clicked(self.selected_date)
        
        # Also notify using the modern method for compatibility
        if self.parent_widget and hasattr(self.parent_widget, 'on_modern_calendar_date_changed'):
            self.parent_widget.on_modern_calendar_date_changed()
            
    # Compatibility methods
    def selectedDate(self):
        """Return currently selected date for compatibility."""
        if hasattr(self, 'selected_date') and self.selected_date.isValid():
            return self.selected_date
        # Fallback to current month's first date if no date selected
        year = self.current_date.year()
        month = self.current_date.month()
        return QDate(year, month, 1)
        
    def setSelectedDate(self, date):
        """Set selected date - Block Sunday selection."""
        # Block Sunday selection
        if date.dayOfWeek() == 7:  # Sunday
            # If trying to set Sunday, find the next working day (Monday)
            while date.dayOfWeek() == 7:
                date = date.addDays(1)
            
        # Store the actual selected date
        self.selected_date = date
        
        # Update month/year buttons to match the selected date
        self.current_date = QDate(date.year(), date.month(), 1)
        self.year_button.setText(str(date.year()))
        self.month_button.setText(self.months[date.month() - 1])
        
        # Update the display
        self._update_display()
        
    def setFocus(self, reason=None):
        super().setFocus()
        
    def mousePressEvent(self, event):
        """Handle mouse click to set focus on calendar."""
        # Set focus to this widget when clicked
        self.setFocus()
        print("🖱️ Calendar clicked - focus set to calendar")
        super().mousePressEvent(event)
        
    def focusInEvent(self, event):
        """Handle when calendar gains focus."""
        super().focusInEvent(event)
        print("🎯 Calendar focused for keyboard navigation")
        
        # Ensure we have a selected date and it's visible
        if not hasattr(self, 'selected_date') or not self.selected_date.isValid():
            # Set to current date, but skip Sunday
            current = QDate.currentDate()
            if current.dayOfWeek() == 7:  # If today is Sunday, move to Monday
                current = current.addDays(1)
            self.selected_date = current
            
        # Make sure the selected date is visible in current month view
        self.current_date = QDate(self.selected_date.year(), self.selected_date.month(), 1)
        self.year_button.setText(str(self.selected_date.year()))
        self.month_button.setText(self.months[self.selected_date.month() - 1])
        
        # Update display to show the selected date properly
        self._update_display()
        
    def focusOutEvent(self, event):
        """Handle when calendar loses focus."""
        super().focusOutEvent(event)
        
        # Refresh display to remove focus indicators if needed
        self._update_display()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for attendance marking."""
        # First check if we have a student selected
        if not (self.parent_widget and self.parent_widget.selected_student):
            print(f"🚫 No student selected - ignoring key event")
            return  # Don't process any keys if no student selected
            
        # Check if we're in edit mode
        if not (hasattr(self.parent_widget, 'edit_mode') and self.parent_widget.edit_mode):
            print(f"🔒 Not in edit mode - only arrow keys will work")
            
        # Get the actual currently selected date from the UI
        current_selected_date = self.selectedDate()
        
        key = event.key()
        print(f"🔄 Calendar processing key: {key}")
        print(f"🔄 Calendar keyPress - current selected date: {current_selected_date.toString('yyyy-MM-dd')}")
        
        # Handle Return/Enter key to ensure date selection is confirmed
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            # Force update of selected date and refresh display
            self._update_display()
            
            # Notify parent that a date was clicked/selected
            if self.parent_widget and hasattr(self.parent_widget, 'on_date_clicked'):
                self.parent_widget.on_date_clicked(current_selected_date)
            print(f"📅 Date selection confirmed with Enter key: {current_selected_date.toString('yyyy-MM-dd')}")
            event.accept()
            return
        
        # Handle arrow keys for date navigation (allow across months)
        if key == Qt.Key_Left:
            print(f"⬅️ Left arrow pressed")
            new_date = current_selected_date.addDays(-1)
            print(f"⬅️ Moving to: {new_date.toString('yyyy-MM-dd')}")
            self.setSelectedDate(new_date)
            event.accept()
            return
        elif key == Qt.Key_Right:
            print(f"➡️ Right arrow pressed")
            new_date = current_selected_date.addDays(1)
            print(f"➡️ Moving to: {new_date.toString('yyyy-MM-dd')}")
            self.setSelectedDate(new_date)
            event.accept()
            return
        elif key == Qt.Key_Up:
            print(f"⬆️ Up arrow pressed")
            new_date = current_selected_date.addDays(-7)
            print(f"⬆️ Moving to: {new_date.toString('yyyy-MM-dd')}")
            self.setSelectedDate(new_date)
            event.accept()
            return
        elif key == Qt.Key_Down:
            print(f"⬇️ Down arrow pressed")
            new_date = current_selected_date.addDays(7)
            print(f"⬇️ Moving to: {new_date.toString('yyyy-MM-dd')}")
            self.setSelectedDate(new_date)
            event.accept()
            return
        
        # Handle attendance shortcuts
        current_date_for_attendance = self.selectedDate()
        date_str = current_date_for_attendance.toString("yyyy-MM-dd")
        
        status = None
        if key == Qt.Key_P:  # Present
            status = "Present"
        elif key == Qt.Key_A:  # Absent
            status = "Absent"
        elif key == Qt.Key_L:  # Late
            status = "Late"
        elif key == Qt.Key_E:  # Excused
            status = "Excused"
        elif key == Qt.Key_H:  # Holiday
            status = "Holiday"
        
        if status:
            # Check if we're in edit mode before allowing attendance changes
            if not (hasattr(self.parent_widget, 'edit_mode') and self.parent_widget.edit_mode):
                print(f"🔒 Attendance is read-only. Press 'Edit Mode' button to modify attendance.")
                event.accept()
                return
                
            # Update attendance data for the selected date
            self.parent_widget.attendance_data[date_str] = status
            
            # Mark as having unsaved changes
            self.parent_widget.has_unsaved_changes = True
            self.parent_widget.update_submit_button_style()
            
            # Update calendar display for the selected date
            self.parent_widget.update_calendar_date(current_date_for_attendance, status)
            
            # Refresh the calendar visual display immediately
            self._update_display()
            
            # Print confirmation for the user
            print(f"✅ Set attendance status: {status} for {date_str}")
            
            return

class AttendancePage(QWidget):
    """Main attendance page with modern 2-column layout."""
    
    def __init__(self):
        super().__init__()
        # No window title or geometry for embedded page
        
        # Initialize database connection with error handling for standalone mode
        try:
            self.db = Database()
        except Exception as e:
            print(f"Warning: Database initialization failed: {e}")
            print("Creating mock database for standalone mode")
            from unittest.mock import MagicMock
            self.db = MagicMock()
            self.db.cursor = MagicMock()
            self.db.cursor.execute = MagicMock(return_value=None)
            self.db.cursor.fetchall = MagicMock(return_value=[])
        
        # Initialize data
        self.students_data = []
        self.selected_student = None
        self.attendance_data = {}
        self.has_unsaved_changes = False
        self.edit_mode = False  # Track if we're in edit mode
        self.saved_attendance = {}  # Store saved attendance from database
        
        self.setup_ui()
        
        # Set up global key event handling
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Load student data from database
        self.load_students_from_database()
        
    def showEvent(self, event):
        """Reset filters when page is shown."""
        super().showEvent(event)
        if hasattr(self, 'school_combo'):  # Ensure UI is initialized
            self.reset_filters()
    
    def reset_filters(self):
        """Reset all filters to default state."""
        try:
            print("🔄 Resetting attendance filters to default state")
            
            # Temporarily disconnect signals to prevent cascading calls
            self.school_combo.currentTextChanged.disconnect()
            self.class_combo.currentTextChanged.disconnect() 
            self.section_combo.currentTextChanged.disconnect()
            
            # Reset school combo to placeholder
            self.school_combo.setCurrentIndex(0)
            
            # Clear and reset class combo with placeholder
            self.class_combo.clear()
            self.class_combo.addItem("Please Select Class")
            
            # Clear and reset section combo with placeholder  
            self.section_combo.clear()
            self.section_combo.addItem("Please Select Section")
            
            # Reconnect signals
            self.school_combo.currentTextChanged.connect(self.on_school_changed)
            self.class_combo.currentTextChanged.connect(self.on_class_changed)
            self.section_combo.currentTextChanged.connect(self.on_filters_changed)
            
            # Reload schools data and refresh
            self.load_schools_data()
            self.load_classes_data()
            self.load_sections_data()
            
            # Load all students (no filters)
            self.load_students_from_database()
            
            # Reset calendar and attendance data
            self.reset_calendar_state()
            
            print("✅ Filters reset successfully")
            
        except Exception as e:
            print(f"❌ Error resetting filters: {e}")
            import traceback
            traceback.print_exc()
    
    def reset_calendar_state(self):
        """Reset calendar to current date and clear attendance data."""
        try:
            print("📅 Resetting calendar state")
            
            # Clear attendance data
            self.attendance_data = {}
            self.selected_student = None
            self.has_unsaved_changes = False
            self.edit_mode = False
            self.saved_attendance = {}
            
            # Reset calendar to current date if available
            if hasattr(self, 'calendar'):
                current_date = QDate.currentDate()
                self.calendar.current_date = current_date
                self.calendar.selected_date = current_date
                
                # Clear calendar's attendance data
                if hasattr(self.calendar, '_attendance_data'):
                    self.calendar._attendance_data = {}
                
                # Update calendar display
                if hasattr(self.calendar, '_update_display'):
                    self.calendar._update_display()
                    
                print(f"📅 Calendar reset to current date: {current_date.toString('yyyy-MM-dd')}")
            
            # Clear student selection in table
            if hasattr(self, 'students_table'):
                self.students_table.table.clearSelection()
                
            print("✅ Calendar state reset successfully")
            
        except Exception as e:
            print(f"❌ Error resetting calendar state: {e}")
            import traceback
            traceback.print_exc()
        
    def load_students_from_database(self, school_id=None, class_name=None, section_name=None):
        """Load students from database with optional filters."""
        try:
            # Get students using the proper database method with pagination - only active students
            result = self.db.get_students(page=1, per_page=20, status="Active")
            
            # Handle different return formats from database
            if isinstance(result, dict):
                students_list = result.get('students', [])
            else:
                students_list = result or []
            
            self.students_data = []
            
            for student in students_list:
                # Handle both dict and object formats
                if hasattr(student, 'get'):
                    student_dict = student
                else:
                    student_dict = dict(student) if hasattr(student, 'keys') else {}
                
                # Convert database format to internal format - using correct field names
                student_data = {
                    "id": str(student_dict.get("student_id", "")),
                    "roll": str(student_dict.get("student_id", "")),
                    "name": str(student_dict.get("student_name", "")),
                    "class": str(student_dict.get("class", "")),
                    "section": str(student_dict.get("section", "")),
                    "school": str(student_dict.get("school_name", "")),
                    "school_id": str(student_dict.get("school_id", "")),
                    "gender": str(student_dict.get("gender", "")),
                    "phone": str(student_dict.get("father_phone", "")),
                    "father": str(student_dict.get("father_name", ""))
                }
                
                # Apply filters if provided
                if school_id is not None and str(student_data.get("school_id", "")) != str(school_id):
                    continue
                if class_name is not None and student_data.get("class", "") != class_name:
                    continue
                if section_name is not None and student_data.get("section", "") != section_name:
                    continue
                
                # Only add students with valid ID and name
                if student_data["id"] and student_data["name"]:
                    self.students_data.append(student_data)
            
            print(f"📚 Loaded {len(self.students_data)} students from database with filters: school_id={school_id}, class={class_name}, section={section_name}")
            self.refresh_table_data()
            
        except Exception as e:
            logging.error(f"Error loading students from database: {e}")
            import traceback
            traceback.print_exc()
            # Clear data instead of using dummy data
            self.students_data = []
            print("❌ Failed to load student data from database")
            self.refresh_table_data()
        
    def refresh_data(self):
        """Refresh attendance data - compatibility method for main window."""
        print("🔄 Attendance data refreshed")
        self.load_students_from_database()
        self.refresh_table_data()
        
    def toggle_edit_mode(self):
        """Toggle between view and edit mode for attendance."""
        # Check current button text to determine state
        current_text = self.edit_btn.text()
        
        if current_text == "Edit Existing Attendance":
            # Switch from view mode to edit mode (for existing attendance)
            self.edit_mode = True
            self.edit_btn.setText("Cancel Edit")
            self.edit_btn.setStyleSheet(self.get_button_style('secondary'))
            self.submit_btn.setEnabled(True)
            
            # Enable all attendance marking UI elements
            self.status_combo.setEnabled(True)
            
            # Find and enable action buttons
            if hasattr(self, 'findChild'):
                apply_btn = self.findChild(QPushButton, "apply_status_btn")
                if apply_btn:
                    apply_btn.setEnabled(True)
            
            print("Edit mode enabled - Existing attendance can be modified")
            
        elif current_text == "Cancel Edit":
            # Switch back to view mode
            self.edit_mode = False
            self.edit_btn.setText("Edit Existing Attendance")
            self.edit_btn.setStyleSheet(self.get_button_style('warning'))
            self.submit_btn.setEnabled(False)
            
            # Disable all attendance marking UI elements
            self.status_combo.setEnabled(False)
            self.status_combo.setCurrentIndex(0)
            
            # Find and disable action buttons
            if hasattr(self, 'findChild'):
                apply_btn = self.findChild(QPushButton, "apply_status_btn")
                if apply_btn:
                    apply_btn.setEnabled(False)
            
            self.has_unsaved_changes = False
            print("View mode enabled - Attendance is read-only")
            
        else:
            # Original toggle logic for new attendance marking
            self.edit_mode = not self.edit_mode
            
            if self.edit_mode:
                self.edit_btn.setText("View Mode")
                self.edit_btn.setStyleSheet(self.get_button_style('warning'))
                self.submit_btn.setEnabled(True)
                print("Edit mode enabled - Attendance can be modified")
            else:
                self.edit_btn.setText("Mark Attendance")
                self.edit_btn.setStyleSheet(self.get_button_style('primary'))
                self.submit_btn.setEnabled(False)
                self.has_unsaved_changes = False
                print("View mode enabled - Attendance is read-only")
            
        # Refresh calendar to update edit mode state
        if hasattr(self, 'calendar') and self.selected_student:
            self.update_calendar_edit_mode()
            
    def get_button_style(self, style_type):
        """Get button style based on type."""
        # Get styles from theme
        styles = get_attendance_styles()
        
        # Map the requested style type to the appropriate style from theme
        if style_type == 'primary':
            return styles['button_primary']
        elif style_type == 'secondary':
            return styles['button_secondary']
        elif style_type == 'warning':
            return styles['button_warning']
        elif style_type == 'success':
            return styles['button_success']
        else:
            return styles['button_secondary']
        
    def check_attendance_exists_for_month(self, student_id, month, year):
        """Check if student has any attendance marked for the specified month/year."""
        try:
            # Get all attendance records for this student
            attendance_records = self.db.get_attendance(student_id=student_id)
            
            # Check if any record exists for the specified month/year
            for record in attendance_records:
                record_date = record['date']  # Format: 'YYYY-MM-DD'
                try:
                    record_year, record_month, _ = record_date.split('-')
                    if int(record_year) == year and int(record_month) == month:
                        return True
                except ValueError:
                    continue
            
            return False
        except Exception as e:
            print(f"❌ Error checking attendance for month: {e}")
            return False

    def load_saved_attendance(self, student_id):
        """Load saved attendance for a student from database for current month/year."""
        try:
            # Get current month and year from calendar
            current_date = self.calendar.selectedDate() if hasattr(self, 'calendar') else QDate.currentDate()
            current_month = current_date.month()
            current_year = current_date.year()
            
            # Get all attendance records for this student
            attendance_records = self.db.get_attendance(student_id=student_id)
            self.saved_attendance = {}
            
            # First, filter records for current month/year only
            current_month_records = {}
            all_months_with_records = set()
            
            for record in attendance_records:
                date_str = record['date']
                try:
                    # Parse date and check if it's in current month/year
                    date_parts = date_str.split('-')
                    if len(date_parts) == 3:
                        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                        
                        # Track all months that have records
                        all_months_with_records.add(f"{month}/{year}")
                        
                        # If it matches current month/year, add to current records
                        if year == current_year and month == current_month:
                            status = record['status']
                            current_month_records[date_str] = status
                            
                except (ValueError, IndexError):
                    continue
            
            # Set the current month records
            self.saved_attendance = current_month_records
            
            # Show information about records found
            if len(current_month_records) > 0:
                print(f"Loaded {len(current_month_records)} saved attendance records for student {student_id} (Month: {current_month}/{current_year})")
            else:
                if all_months_with_records:
                    months_list = sorted(list(all_months_with_records))
                    print(f"No records found for student {student_id} in {current_month}/{current_year}. Records exist in: {', '.join(months_list)}")
                else:
                    print(f"No attendance records found for student {student_id} in any month")
                    
            return self.saved_attendance
            
        except Exception as e:
            print(f"❌ Error loading saved attendance: {e}")
            self.saved_attendance = {}
            return {}
            
    def update_calendar_edit_mode(self):
        """Update calendar to reflect current edit mode."""
        if hasattr(self, 'calendar') and hasattr(self.calendar, 'set_edit_mode'):
            self.calendar.set_edit_mode(self.edit_mode)
        print(f"🔄 Calendar updated for {'edit' if self.edit_mode else 'view'} mode")
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for attendance marking."""
        # Check if this is an attendance shortcut key
        key = event.key()
        attendance_keys = [Qt.Key_P, Qt.Key_A, Qt.Key_L, Qt.Key_E, Qt.Key_H]
        arrow_keys = [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]
        enter_key = Qt.Key_Return
        
        focused_widget = self.focusWidget()
        calendar_focused = (focused_widget == self.calendar if hasattr(self, 'calendar') else False)
        table_focused = (focused_widget == self.students_table.table if hasattr(self, 'students_table') else False)
        
        print(f"🎯 Current focus: {focused_widget.__class__.__name__ if focused_widget else 'None'}")
        
        # Handle Enter key specially for calendar
        if key == enter_key and calendar_focused and hasattr(self.calendar, 'selectedDate'):
            # When Enter is pressed on calendar, trigger selection of the current date
            selected_date = self.calendar.selectedDate()
            # Force selection of this date
            if hasattr(self.calendar, 'setSelectedDate'):
                self.calendar.setSelectedDate(selected_date)
                print(f"📅 Date confirmed with Enter key: {selected_date.toString('dd/MM/yyyy')}")
            # Update display to highlight the selected date
            if hasattr(self.calendar, '_update_display'):
                self.calendar._update_display()
            event.accept()
            return
        
        # Handle arrow key navigation based on current focus
        if key in arrow_keys:
            if table_focused:
                # Let table handle arrow navigation (QTableWidget built-in behavior)
                print(f"📋 Table has focus - letting table handle arrow navigation")
                super().keyPressEvent(event)
                return
            elif calendar_focused:
                # Let calendar handle arrow navigation
                print(f"📅 Calendar has focus - letting calendar handle arrow navigation")
                super().keyPressEvent(event)
                return
            else:
                # No relevant widget focused - ignore arrow keys
                print(f"❌ No relevant widget focused - ignoring arrow key")
                event.ignore()
                return
        
        # Handle attendance shortcuts (P, A, L, E, H) - work from anywhere when student is selected AND in edit mode
        if key in attendance_keys and self.selected_student:
            # Check if we're in edit mode
            if not self.edit_mode:
                print(f"🔒 Attendance is read-only. Press 'Edit Mode' button to modify attendance.")
                event.accept()
                return
                
            # Get current selected date from calendar
            if hasattr(self.calendar, 'selectedDate'):
                selected_date = self.calendar.selectedDate()
            else:
                selected_date = QDate.currentDate()
            
            status = None
            if key == Qt.Key_P:
                status = "Present"
            elif key == Qt.Key_A:
                status = "Absent"
            elif key == Qt.Key_L:
                status = "Late"
            elif key == Qt.Key_E:
                status = "Excused"
            elif key == Qt.Key_H:
                status = "Holiday"
            
            if status:
                # Update attendance data for this date
                self.update_calendar_date(selected_date, status)
                self.has_unsaved_changes = True
                self.update_submit_button_style()
                
                student_name = self.selected_student["name"]
                print(f"⌨️ Keyboard shortcut: {student_name} -> {status} on {selected_date.toString('dd/MM/yyyy')}")
                
                # If it's a ModernCalendarWidget, tell it to refresh its display
                if hasattr(self.calendar, '_update_display'):
                    self.calendar._update_display()
                
                # Keep focus on calendar for continued navigation
                if hasattr(self.calendar, 'setFocus'):
                    self.calendar.setFocus()
                
                # Accept the event to prevent further processing
                event.accept()
                return
        
        # For all other keys, pass to parent but don't let arrow keys through
        if key not in arrow_keys:
            super().keyPressEvent(event)
        else:
            # Arrow keys should be consumed here, don't pass to parent
            event.accept()
        
    def eventFilter(self, obj, event):
        """Filter events to prevent calendar clicks from affecting other widgets."""
        from PyQt5.QtCore import QEvent
        
        # Handle students table mouse events
        if obj == self.students_table.table:
            if event.type() == QEvent.MouseButtonPress:
                # Ensure table gets focus and clear other widget focuses
                self.students_table.table.setFocus(Qt.MouseFocusReason)
                
                # Clear focus from calendar and other widgets
                if hasattr(self, 'calendar'):
                    self.calendar.clearFocus()
                
                # Clear focus from action widgets
                self.status_combo.clearFocus()
                action_buttons = self.findChildren(QPushButton)
                for btn in action_buttons:
                    btn.clearFocus()
                    
                print("🖱️ Student table clicked - focus set to table")
                
                # Let the table handle the click normally
                return False
        
        # Handle calendar mouse events
        elif obj == self.calendar:
            if event.type() == QEvent.MouseButtonPress:
                # Ensure calendar gets focus and clear other widget focuses
                self.calendar.setFocus(Qt.MouseFocusReason)
                
                # Clear focus from student table and other widgets
                self.students_table.table.clearFocus()
                self.status_combo.clearFocus()
                
                # Clear focus from action buttons
                action_buttons = self.findChildren(QPushButton)
                for btn in action_buttons:
                    btn.clearFocus()
                
                print("🖱️ Calendar clicked - focus set to calendar")
                
                # Let calendar handle the click normally
                return False
                
            elif event.type() == QEvent.KeyPress:
                # Ensure calendar processes its own key events
                key = event.key()
                arrow_keys = [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]
                attendance_keys = [Qt.Key_P, Qt.Key_A, Qt.Key_L, Qt.Key_E, Qt.Key_H]
                
                if key in arrow_keys:
                    # Arrow keys are always allowed for navigation
                    print(f"🔄 Calendar processing key: {key}")
                    return False  # Allow the calendar to process the event
                elif key in attendance_keys:
                    # Attendance keys only allowed in edit mode
                    if not self.edit_mode:
                        print(f"🔒 Attendance key {key} blocked - read-only mode")
                        return True  # Block the event
                    # Let calendar handle attendance keys in edit mode
                    print(f"🔄 Calendar processing key: {key}")
                    return False  # Allow the calendar to process the event
                    # Let calendar handle these keys directly
                    print(f"� Calendar processing key: {key}")
                    return False  # Allow the calendar to process the event
        
        # Pass other events to parent
        return super().eventFilter(obj, event)
        
    def setup_ui(self):
        """Setup the complete attendance layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Main content splitter (2 columns) - Full page
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background: #e5e7eb;
                width: 2px;
            }
            QSplitter::handle:hover {
                background: #9ca3af;
            }
        """)
        
        # Left Column - Student Search & Filters
        left_column = self.create_left_column()
        
        # Right Column - Calendar & Actions
        right_column = self.create_right_column()
        
        # Add to splitter
        main_splitter.addWidget(left_column)
        main_splitter.addWidget(right_column)
        
        # Set splitter proportions (40% left, 60% right)
        main_splitter.setSizes([480, 720])
        
        # Set stretch factors to maintain proportions
        main_splitter.setStretchFactor(0, 2)  # Left column stretch factor
        main_splitter.setStretchFactor(1, 3)  # Right column stretch factor
        
        # Prevent collapsing
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        
        main_layout.addWidget(main_splitter)
        
    def create_left_column(self):
        """Create the left column with student search and filters."""
        left_frame = QFrame()
        left_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        
        # Set size policy to maintain proportions
        left_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(left_frame)
        layout.setSpacing(8)
        
        # Filters section (now includes search in 2x2 grid)
        self.create_filters_section(layout)
        
        # Students table
        self.create_students_table(layout)
        
        return left_frame
        
    def create_filters_section(self, parent_layout):
        """Create the filters section with 2x2 grid layout including search."""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        filters_layout = QVBoxLayout(filters_frame)
        filters_layout.setSpacing(8)
        
        # Create 2x2 grid layout for filters and search
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)
        filter_grid.setColumnStretch(0, 1)  # Equal column widths
        filter_grid.setColumnStretch(1, 1)
        
        styles = get_attendance_styles()
        
        # Row 1, Column 1: School filter (with placeholder)
        self.school_combo = CustomComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        self.load_schools_data()  # Load from database
        self.school_combo.currentTextChanged.connect(self.on_school_changed)
        
        # Row 1, Column 2: Class filter (with placeholder)
        self.class_combo = CustomComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        self.load_classes_data()  # Load from database
        self.class_combo.currentTextChanged.connect(self.on_class_changed)
        
        # Row 2, Column 1: Section filter (with placeholder)
        self.section_combo = CustomComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        self.load_sections_data()  # Load from database
        self.section_combo.currentTextChanged.connect(self.on_filters_changed)
        
        # Row 2, Column 2: Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, roll number...")
        self.search_input.setStyleSheet(styles['search_input'])
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)    # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)     # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)   # Row 2, Col 1
        filter_grid.addWidget(self.search_input, 1, 1)    # Row 2, Col 2
        
        filters_layout.addLayout(filter_grid)
        
        parent_layout.addWidget(filters_frame)

    def create_students_table(self, parent_layout):
        """Create a fresh new students table using SMISTable and size columns by header text only."""
        # Create fresh SMISTable component with built-in pagination and styling
        self.students_table = SMISTable(show_pagination=True)  # or False if you don't want pagination

        # Set object names (keeps your existing style protection)
        self.students_table.setObjectName("AttendanceStudentsTable")
        self.students_table.table.setObjectName("AttendanceTableWidget")

        # Configure table structure
        headers = ["Student ID", "Student Name", "Father Name", "Class", "Section"]
        # If you had a checkbox column, pass its index as second arg; here we have none
        self.students_table.setup_with_headers(headers, checkbox_column=None)

        # Ensure rows start empty
        self.students_table.table.setRowCount(0)

        # --- Resize columns based on header text only ---
        table = self.students_table.table
        header = table.horizontalHeader()

        # We'll switch to Interactive so we can set widths manually after measurement
        header.setSectionResizeMode(QHeaderView.Interactive)

        # Use header's font metrics to measure header text width and add padding
        fm = header.fontMetrics()
        padding = 24  # tweak this if you want more/less space around header text

        for col in range(table.columnCount()):
            text = headers[col] if col < len(headers) else ""
            width = fm.horizontalAdvance(text) + padding
            table.setColumnWidth(col, width)

        # Keep last section stretch if you prefer remaining space filled (optional)
        # header.setStretchLastSection(True)  # already set inside setup_with_headers()

        # Add table widget to provided parent layout
        parent_layout.addWidget(self.students_table)

        protection_css = """
            /* Create complete isolation barrier with specific object names */
            QWidget#AttendanceStudentsTable * {
                /* Reset any potential inherited properties */
                font-family: inherit !important;
                font-size: inherit !important;
                font-weight: inherit !important;
                padding: inherit !important;
                margin: inherit !important;
                border: inherit !important;
                background-color: inherit !important;
                color: inherit !important;
                width: auto !important;  /* Remove any fixed width */
                height: auto !important; /* Remove any fixed height */
            }
            
            /* Reset table sizes to let component handle it */
            QTableWidget#AttendanceTableWidget QHeaderView::section {
                width: auto !important;
                height: auto !important;
                min-width: auto !important;
                min-height: auto !important;
                max-width: none !important;
                max-height: none !important;
            }
        """
        
        # Apply protection stylesheet at widget level to create style barrier
        self.students_table.setStyleSheet(protection_css)
        
        # Enable table navigation
        self.students_table.table.setFocusPolicy(Qt.StrongFocus)
        
        # Connect table selection events
        self.students_table.table.itemSelectionChanged.connect(self.on_student_selected)
        
        # Install event filter for proper event handling
        self.students_table.table.installEventFilter(self)
        
        # Load and populate data
        self.refresh_table_data()
        
        # Add table directly to layout (no wrapper frames)
        parent_layout.addWidget(self.students_table)
        
    def refresh_table_data(self):
        """Refresh table with current data and update pagination."""
        if not hasattr(self, 'students_table'):
            return
            
        # Clear existing rows
        self.students_table.table.setRowCount(0)
        
        # Populate with fresh data
        if self.students_data:
            self.students_table.table.setRowCount(len(self.students_data))
            
            for row, student in enumerate(self.students_data):
                # Create table items for each column
                self.students_table.table.setItem(row, 0, QTableWidgetItem(str(student.get("id", ""))))
                self.students_table.table.setItem(row, 1, QTableWidgetItem(str(student.get("name", ""))))
                self.students_table.table.setItem(row, 2, QTableWidgetItem(str(student.get("father", ""))))
                self.students_table.table.setItem(row, 3, QTableWidgetItem(str(student.get("class", ""))))
                self.students_table.table.setItem(row, 4, QTableWidgetItem(str(student.get("section", ""))))
        
        # Update pagination with correct count
        if hasattr(self.students_table, 'pagination') and self.students_table.pagination:
            self.students_table.pagination.set_total_items(len(self.students_data))
            
        # Ensure table styling is applied properly
        self.students_table.table.repaint()
            
        print(f"📊 Table refreshed with {len(self.students_data)} students")
        
    def create_right_column(self):
        """Create the right column with calendar and actions."""
        right_frame = QFrame()
        right_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        
        # Set size policy to maintain proportions  
        right_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(right_frame)
        layout.setSpacing(8)  # Reduced spacing for more calendar space
        layout.setContentsMargins(4, 4, 4, 4)  # Reduced margins for more space
        
        # Row 1: Calendar (takes most space - 65%)
        calendar_widget = self.create_calendar_row_widget()
        layout.addWidget(calendar_widget, stretch=5)  # Give 60% space to calendar
        
        # Row 2: Attendance Actions (increased - 35%)
        actions_widget = self.create_actions_row_widget()
        layout.addWidget(actions_widget, stretch=5)  # Give 40% space to actions (increased from 20%)
        
        return right_frame
        
    def create_calendar_row_widget(self):
        """Create the calendar row widget and return it."""
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        
        # Set size policy to expand and fill available space
        calendar_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setSpacing(4)  # Reduced spacing
        calendar_layout.setContentsMargins(4, 4, 4, 4)  # Reduced margins for more calendar space
        
        # Calendar widget
        if CALENDAR_AVAILABLE:
            try:
                self.calendar = ModernCalendarWidget(self)  # Pass self as parent
                # Remove fixed size to use all available space
                self.calendar.setMinimumSize(400, 300)  # Set minimum size only
                self.calendar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow expansion
                self.calendar.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
                
                # Connect date selection signal if available
                if hasattr(self.calendar, 'selectionChanged') and hasattr(self.calendar.selectionChanged, 'connect'):
                    self.calendar.selectionChanged.connect(self.on_modern_calendar_date_changed)
                elif hasattr(self.calendar, 'clicked') and hasattr(self.calendar.clicked, 'connect'):
                    self.calendar.clicked.connect(self.on_calendar_date_selected)
                elif hasattr(self.calendar, 'currentPageChanged') and hasattr(self.calendar.currentPageChanged, 'connect'):
                    self.calendar.currentPageChanged.connect(self.on_modern_calendar_date_changed)
                
                # Set up proper focus and event handling for the ModernCalendarWidget
                self.calendar.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
                
                # Install event filter to handle mouse events properly  
                self.calendar.installEventFilter(self)
                
                calendar_layout.addWidget(self.calendar)
                
                # Don't automatically focus calendar - let user click to focus
                print("✅ ModernCalendarWidget loaded successfully with responsive sizing")
            except Exception as e:
                print(f"❌ ModernCalendarWidget failed to load: {e}")
                # Create enhanced fallback calendar
                self.create_fallback_calendar(calendar_layout)
        else:
            print("📅 Creating fallback calendar placeholder")
            # Create enhanced fallback calendar
            self.create_fallback_calendar(calendar_layout)
        
        return calendar_frame
        
    def create_actions_row_widget(self):
        """Create the attendance actions row widget and return it."""
        actions_frame = QFrame()
        actions_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        
        # Set size policy to allow more flexibility and expansion
        actions_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        actions_frame.setMaximumHeight(400)  # Significantly increased for better proportion (was 280)
        actions_frame.setMinimumHeight(300)  # Added minimum height for consistency
        
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(12)  # Increased spacing for better layout
        actions_layout.setContentsMargins(12, 12, 12, 12)  # Increased margins for better visual balance
        
        # Current selection info (compact)
        self.selection_info = QLabel("👤 No student selected")
        self.selection_info.setStyleSheet(f"""
            QLabel {{
                background: white;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 6px;
                padding: 8px;
                color: {COLORS['gray_600']};
                font-weight: 500;
                font-size: 12px;
            }}
        """)
        actions_layout.addWidget(self.selection_info)
        
        # Status selection with equal sizing
        status_layout = QHBoxLayout()
        
        self.status_combo = CustomComboBox()
        self.status_combo.addItems(["Select Status", "Present", "Absent", "Late", "Excused", "Leave", "Holiday"])
        self.status_combo.setFocusPolicy(Qt.ClickFocus)  # Only accept focus on explicit click
        
        styles = get_attendance_styles()
        # Let CustomComboBox handle its own dimensions
        
        # Apply status button 
        apply_status_btn = QPushButton("Apply")
        apply_status_btn.setObjectName("apply_status_btn")  # Set object name for finding later
        apply_status_btn.setStyleSheet(styles['button_success'])
        # Let button handle its own dimensions
        apply_status_btn.setFocusPolicy(Qt.ClickFocus)  # Only accept focus on explicit click
        apply_status_btn.clicked.connect(self.apply_status)
        
        status_layout.addWidget(self.status_combo)
        status_layout.addWidget(apply_status_btn)
        
        actions_layout.addLayout(status_layout)
        
        # Original action buttons in 2x2 grid with compact dimensions
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(8)
        buttons_grid.setContentsMargins(0, 0, 0, 0)
        
        current_week_btn = QPushButton("Active Week")
        current_week_btn.setStyleSheet(styles['button_secondary'])
        # Let button handle its own dimensions
        current_week_btn.setFocusPolicy(Qt.ClickFocus)  # Only accept focus on explicit click
        current_week_btn.clicked.connect(lambda: self.bulk_action("Active Week"))
        
        current_month_btn = QPushButton("Active Month")
        current_month_btn.setStyleSheet(styles['button_secondary'])
        # Let button handle its own dimensions
        current_month_btn.setFocusPolicy(Qt.ClickFocus)  # Only accept focus on explicit click
        current_month_btn.clicked.connect(lambda: self.bulk_action("Active Month"))

        mark_holiday_btn = QPushButton("Mark Holiday")
        mark_holiday_btn.setStyleSheet(styles['button_secondary'])
        # Let button handle its own dimensions
        mark_holiday_btn.setFocusPolicy(Qt.ClickFocus)  # Only accept focus on explicit click
        # First select Holiday status and then call bulk_action
        mark_holiday_btn.clicked.connect(lambda: [
            self.status_combo.setCurrentText("Holiday"), 
            self.bulk_action("Holiday")
        ])
        
        clear_all_btn = QPushButton("Clear")
        clear_all_btn.setStyleSheet(styles['button_warning'])
        # Let button handle its own dimensions
        clear_all_btn.setFocusPolicy(Qt.ClickFocus)  # Only accept focus on explicit click
        clear_all_btn.clicked.connect(self.reset_data)
        
        # Add buttons to grid (2x2) with equal heights
        buttons_grid.addWidget(current_week_btn, 0, 0)
        buttons_grid.addWidget(current_month_btn, 0, 1)
        buttons_grid.addWidget(mark_holiday_btn, 1, 0)
        buttons_grid.addWidget(clear_all_btn, 1, 1)
        
        # Set fixed dimensions for the button grid to prevent expansion
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_grid)
        # Let widget handle its own dimensions
        
        actions_layout.addWidget(buttons_widget)
        
        # Submit and Edit buttons - Main action buttons
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(10)
        
        # Edit button - Toggle edit mode
        self.edit_btn = QPushButton("Edit Mode")
        self.edit_btn.setStyleSheet(styles['button_secondary'])
        # Let button handle its own dimensions
        self.edit_btn.setFocusPolicy(Qt.ClickFocus)
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        
        # Submit button - Save attendance
        self.submit_btn = QPushButton("Submit Attendance")
        self.submit_btn.setStyleSheet(styles['button_primary'])
        # Let button handle its own dimensions
        self.submit_btn.setFocusPolicy(Qt.ClickFocus)
        self.submit_btn.clicked.connect(self.save_attendance)
        self.submit_btn.setEnabled(False)  # Initially disabled until edit mode
        
        buttons_container.addWidget(self.edit_btn)
        buttons_container.addWidget(self.submit_btn)
        
        actions_layout.addLayout(buttons_container)
        
        return actions_frame
        
    def create_fallback_calendar(self, parent_layout):
        """Create a fallback calendar widget that looks realistic."""
        from PyQt5.QtWidgets import QCalendarWidget
        from PyQt5.QtCore import QDate
        
        # Create a standard QCalendarWidget as fallback
        fallback_calendar = QCalendarWidget()
        # Remove fixed size to use all available space
        fallback_calendar.setMinimumSize(400, 300)  # Set minimum size only
        fallback_calendar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow expansion
        
        # Style the fallback calendar to match our design
        fallback_calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background: white;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                font-size: 12px;
                color: {COLORS['gray_700']};
            }}
            QCalendarWidget QAbstractItemView {{
                background: white;
                selection-background-color: #3b82f6;
                selection-color: white;
                border: none;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                color: {COLORS['gray_700']};
                background: white;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background: {COLORS['gray_50']};
                border-bottom: 1px solid {COLORS['gray_200']};
            }}
            QCalendarWidget QToolButton {{
                background: transparent;
                border: none;
                color: {COLORS['gray_700']};
                font-weight: 500;
                padding: 4px;
                margin: 2px;
            }}
            QCalendarWidget QToolButton:hover {{
                background: {COLORS['gray_100']};
                border-radius: 4px;
            }}
            QCalendarWidget QSpinBox {{
                background: white;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 12px;
            }}
        """)
        
        # Set current date and connect selection
        fallback_calendar.setSelectedDate(QDate.currentDate())
        fallback_calendar.clicked.connect(self.on_calendar_date_selected)
        fallback_calendar.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
        
        # Add info label about fallback
        info_label = QLabel("📅 Standard Calendar (Fallback Mode)")
        info_label.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['gray_50']};
                color: {COLORS['gray_600']};
                border: 1px solid {COLORS['gray_200']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
                margin: 2px 0px;
            }}
        """)
        info_label.setAlignment(Qt.AlignCenter)
        
        parent_layout.addWidget(info_label)
        parent_layout.addWidget(fallback_calendar)
        
        # Store reference but don't auto-focus
        self.calendar = fallback_calendar
        
        # Install event filter to handle mouse events properly
        self.calendar.installEventFilter(self)
        
        print("✅ Fallback calendar widget created successfully")
        
    def ensure_calendar_focus_only(self):
        """Set focus to calendar for navigation without enabling attendance changes."""
        from PyQt5.QtCore import QTimer
        
        def focus_calendar():
            if hasattr(self.calendar, 'setFocus'):
                self.calendar.setFocus()
                self.calendar.activateWindow()
                print("🎯 Calendar focused (read-only mode)")
        
        # Only focus if user explicitly requested it
        # focus_calendar()
        QTimer.singleShot(50, focus_calendar)

    def on_calendar_date_selected(self, date):
        """Handle calendar date selection."""
        selected_date = date.toString("dddd, MMMM d, yyyy")
        print(f"📅 Date selected: {selected_date}")
        
        # Check if we're in read-only mode
        if not self.edit_mode:
            print(f"📖 Read-only mode: Date selection blocked for {selected_date}")
            # Still allow focus for navigation but don't process attendance changes
            self.ensure_calendar_focus_only()
            return
        
        # Use QTimer to ensure focus is set after all events are processed
        from PyQt5.QtCore import QTimer
        
        def ensure_calendar_focus():
            if hasattr(self.calendar, 'setFocus'):
                self.calendar.setFocus()
                self.calendar.activateWindow()
                print("🎯 Calendar focused for keyboard navigation")
        
        # Set focus immediately and then again after a short delay
        ensure_calendar_focus()
        QTimer.singleShot(50, ensure_calendar_focus)  # 50ms delay
        
        # Prevent any dropdown from being activated
        self.status_combo.clearFocus()
        
        # Clear focus from all buttons to prevent accidental activation
        action_buttons = self.findChildren(QPushButton)
        for btn in action_buttons:
            btn.clearFocus()
        
        if hasattr(self, 'selection_info'):
            current_text = self.selection_info.text()
            if "Selected:" in current_text:
                # Update with date info
                self.selection_info.setText(f"{current_text} | 📅 {date.toString('dd/MM/yyyy')}")
    
    def on_modern_calendar_date_changed(self):
        """Handle modern calendar date selection and month changes."""
        if hasattr(self.calendar, 'selectedDate'):
            date = self.calendar.selectedDate()
            selected_date = date.toString("dddd, MMMM d, yyyy")
            print(f"📅 Date selected: {selected_date}")
            
            # Update selection info text
            if hasattr(self, 'selection_info'):
                if hasattr(self, 'selected_student') and self.selected_student:
                    student_name = self.selected_student.get('name', '')
                    self.selection_info.setText(f"Selected: {student_name} | 📅 {date.toString('dd/MM/yyyy')}")
                else:
                    self.selection_info.setText(f"📅 {date.toString('dd/MM/yyyy')}")
                print(f"📅 Selection info updated for date: {date.toString('dd/MM/yyyy')}")
            
            # Check if month/year changed and reload attendance if needed
            current_month = date.month()
            current_year = date.year()
            
            # Check if we have a selected student and if month/year changed
            if (hasattr(self, 'selected_student') and self.selected_student and 
                hasattr(self, 'last_displayed_month') and hasattr(self, 'last_displayed_year')):
                
                if (current_month != self.last_displayed_month or 
                    current_year != self.last_displayed_year):
                    
                    print(f"📅 Month changed from {self.last_displayed_month}/{self.last_displayed_year} to {current_month}/{current_year}")
                    
                    # Reload attendance for selected student for new month/year
                    student_id = self.selected_student.get("id", self.selected_student.get("roll"))
                    # Convert roll to proper student_id if needed
                    if hasattr(self, 'current_student_id'):
                        student_id = self.current_student_id
                    
                    self.load_saved_attendance(student_id)
                    
                    # Update mode based on new month/year attendance data
                    has_attendance_in_new_month = self.check_attendance_exists_for_month(
                        student_id, current_month, current_year
                    )
                    
                    if has_attendance_in_new_month:
                        # Read-only mode: Attendance already marked for this month (but allow editing)
                        self.edit_mode = False
                        self.edit_btn.setText("Edit Existing Attendance")
                        self.edit_btn.setStyleSheet(self.get_button_style('warning'))
                        self.edit_btn.setEnabled(True)  # Keep enabled so user can choose to edit
                        self.submit_btn.setEnabled(False)
                        
                        # Disable all attendance marking UI elements initially
                        self.status_combo.setEnabled(False)
                        self.status_combo.setCurrentIndex(0)
                        
                        print(f"📖 Switched to view mode for {current_month}/{current_year} (can edit if needed)")
                    else:
                        # Edit mode: No attendance marked for this month
                        self.edit_mode = True
                        self.edit_btn.setText("Mark Attendance")
                        self.edit_btn.setStyleSheet(self.get_button_style('primary'))
                        self.edit_btn.setEnabled(True)
                        self.submit_btn.setEnabled(True)
                        
                        # Enable all attendance marking UI elements
                        self.status_combo.setEnabled(True)
                        
                        print(f"✏️ Switched to edit mode for {current_month}/{current_year}")
                    
                    self.update_calendar_with_saved_attendance()
                    print(f"🔄 Refreshed attendance for {self.selected_student.get('name')} for new month/year")
            
            # Update selection info with new active week/month
            if self.selected_student:
                self.update_selection_info()
            
            # Update last displayed month/year
            self.last_displayed_month = current_month
            self.last_displayed_year = current_year
            
            # Use QTimer to ensure focus is set after all events are processed
            from PyQt5.QtCore import QTimer
            
            def ensure_calendar_focus():
                if hasattr(self.calendar, 'setFocus'):
                    self.calendar.setFocus()
                    self.calendar.activateWindow()
                    print("🎯 Calendar focused for keyboard navigation")
            
            # Set focus immediately and then again after a short delay
            ensure_calendar_focus()
            QTimer.singleShot(50, ensure_calendar_focus)  # 50ms delay
            
            # Prevent any dropdown from being activated
            self.status_combo.clearFocus()
            
            # Clear focus from all buttons to prevent accidental activation
            action_buttons = self.findChildren(QPushButton)
            for btn in action_buttons:
                btn.clearFocus()
            
            if hasattr(self, 'selection_info'):
                current_text = self.selection_info.text()
                if "Selected:" in current_text:
                    # Update with date info
                    self.selection_info.setText(f"{current_text} | 📅 {date.toString('dd/MM/yyyy')}")
        
    def load_schools_data(self):
        """Load schools from database and populate school combo."""
        try:
            # Clear existing items except placeholder
            while self.school_combo.count() > 1:
                self.school_combo.removeItem(self.school_combo.count() - 1)
                
            schools = self.db.get_schools()
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_combo.addItem(school_name, school_id)
            print(f"📚 Loaded {len(schools)} schools from database")
        except Exception as e:
            print(f"❌ Error loading schools: {e}")
            # Add some default options if database fails
            self.school_combo.addItems(["Primary School", "Secondary School"])

    def load_classes_data(self, school_id=None):
        """Load classes from database and populate class combo."""
        try:
            # Clear existing items except placeholder
            while self.class_combo.count() > 1:
                self.class_combo.removeItem(self.class_combo.count() - 1)
                
            classes = self.db.get_classes(school_id)
            for class_name in classes:
                self.class_combo.addItem(class_name)
            print(f"📚 Loaded {len(classes)} classes from database")
        except Exception as e:
            print(f"❌ Error loading classes: {e}")
            # Add some default options if database fails
            self.class_combo.addItems(["9", "10", "11", "12"])

    def load_sections_data(self, school_id=None, class_name=None):
        """Load sections from database and populate section combo."""
        try:
            # Clear existing items except placeholder
            while self.section_combo.count() > 1:
                self.section_combo.removeItem(self.section_combo.count() - 1)
                
            sections = self.db.get_sections(school_id, class_name)
            for section_name in sections:
                self.section_combo.addItem(section_name)
            print(f"📚 Loaded {len(sections)} sections from database")
        except Exception as e:
            print(f"❌ Error loading sections: {e}")
            # Add some default options if database fails
            self.section_combo.addItems(["A", "B", "C"])

    def on_school_changed(self, school_name):
        """Handle school selection change."""
        if school_name == "Please Select School":
            school_id = None
        else:
            # Get school ID from combo data
            current_index = self.school_combo.currentIndex()
            school_id = self.school_combo.itemData(current_index)
        
        print(f"🏫 School changed to: {school_name} (ID: {school_id})")
        
        # Reload classes and sections for selected school
        self.load_classes_data(school_id)
        self.load_sections_data(school_id)
        
        # Apply filters
        self.on_filters_changed()

    def on_class_changed(self, class_name):
        """Handle class selection change."""
        # Get current school
        school_id = None
        if self.school_combo.currentText() not in ["Please Select School"]:
            current_index = self.school_combo.currentIndex()
            school_id = self.school_combo.itemData(current_index)
        
        # Reload sections for selected school and class
        if class_name == "Please Select Class":
            class_name = None
        
        print(f"📚 Class changed to: {class_name}")
        self.load_sections_data(school_id, class_name)
        
        # Apply filters
        self.on_filters_changed()

    def on_search_changed(self, text):
        """Handle search input changes with clean table refresh."""
        # If search is empty, reload all data
        if not text.strip():
            self.refresh_table_data()
            return
            
        # Filter students based on search text
        filtered_students = []
        search_text = text.lower().strip()
        
        for student in self.students_data:
            if (search_text in student.get("name", "").lower() or 
                search_text in student.get("id", "").lower() or
                search_text in student.get("class", "").lower() or
                search_text in student.get("section", "").lower()):
                filtered_students.append(student)
        
        # Temporarily update students_data for display
        original_data = self.students_data
        self.students_data = filtered_students
        self.refresh_table_data()
        self.students_data = original_data  # Restore original data
            
        print(f"🔍 Search: '{text}' - Found {len(filtered_students)} students")
        
    def on_filters_changed(self):
        """Handle filter changes with database-driven filtering."""
        school_filter = self.school_combo.currentText()
        class_filter = self.class_combo.currentText()
        section_filter = self.section_combo.currentText()
        
        print(f"Filters changed: School={school_filter}, Class={class_filter}, Section={section_filter}")
        
        # Get filter parameters for database query
        school_id = None
        if school_filter not in ["Please Select School"]:
            current_index = self.school_combo.currentIndex()
            school_id = self.school_combo.itemData(current_index)
        
        class_name = None if class_filter == "Please Select Class" else class_filter
        section_name = None if section_filter == "Please Select Section" else section_filter
        
        # Reload students data with filters applied at database level
        self.load_students_from_database(school_id=school_id, class_name=class_name, section_name=section_name)
        
        print(f"📊 Database filtering applied • School ID: {school_id}, Class: {class_name}, Section: {section_name}")
        
    def on_student_selected(self):
        """Handle student selection."""
        try:
            # Since we're using SingleSelection mode now, only one row can be selected
            # Get the current selected row
            current_row = self.students_table.table.currentRow()
            if current_row < 0 or current_row >= len(self.students_data):
                return
                
            # Safely get item text
            id_item = self.students_table.table.item(current_row, 0)
            name_item = self.students_table.table.item(current_row, 1)
            
            if not id_item or not name_item:
                return
                
            student_id = id_item.text()  # Student ID column
            name = name_item.text()  # Student Name column
            
            # Find student data by matching the student ID
            self.selected_student = None
            self.current_student_id = None
            
            # Get the student data for this row directly
            if 0 <= current_row < len(self.students_data):
                self.selected_student = self.students_data[current_row]
                self.current_student_id = student_id  # Set the current_student_id from the table
            
            if self.selected_student:
                # Update calendar with attendance data for this student
                self.update_calendar_with_saved_attendance()
                
                # Update selection info with active week and month only
                self.update_selection_info()
                print(f"👤 Student selected: {name} (Roll: {student_id}")
                
                # Keep focus on the table for better keyboard navigation
                # This fixes the focus issue where arrows were affecting calendar instead of table
                QTimer.singleShot(10, lambda: self.students_table.table.setFocus())
                print(f"🎯 Student table has focus - use arrow keys to navigate students")
        except Exception as e:
            print(f"⚠️ Student selection error: {e}")
            import traceback
            traceback.print_exc()
            
            # Load saved attendance for this student
            student_db_id = self.selected_student.get("id", student_id)
            
            # Remove old roll_to_id_map as we now use Student_ID directly
            self.current_student_id = student_db_id
            print(f"🔗 Using Student_ID: {student_db_id}")
                
            # Load saved attendance for this student
            self.load_saved_attendance(self.current_student_id)
            
            # Determine mode based on current month/year attendance data
            current_date = self.calendar.selectedDate() if hasattr(self, 'calendar') else QDate.currentDate()
            current_month = current_date.month()
            current_year = current_date.year()
            
            # Check if student has any attendance marked in current month/year
            has_attendance_in_current_month = self.check_attendance_exists_for_month(
                self.current_student_id, current_month, current_year
            )
            
            if has_attendance_in_current_month:
                # Read-only mode: Attendance already marked for this month (but allow editing)
                self.edit_mode = False
                self.edit_btn.setText("Edit Existing Attendance")
                self.edit_btn.setStyleSheet(self.get_button_style('warning'))  # Orange color for edit existing
                self.edit_btn.setEnabled(True)  # Keep enabled so user can choose to edit
                self.submit_btn.setEnabled(False)
                
                # Disable all attendance marking UI elements initially
                self.status_combo.setEnabled(False)
                self.status_combo.setCurrentIndex(0)  # Reset to "Select Status"
                
                # Find and disable action buttons initially
                if hasattr(self, 'findChild'):
                    apply_btn = self.findChild(QPushButton, "apply_status_btn")
                    if apply_btn:
                        apply_btn.setEnabled(False)
                
                print(f"📖 Read-only mode: {name} has attendance marked for {current_month}/{current_year}")
            else:
                # Edit mode: No attendance marked for this month, allow direct marking
                self.edit_mode = True
                self.edit_btn.setText("Mark Attendance")
                self.edit_btn.setStyleSheet(self.get_button_style('primary'))
                self.edit_btn.setEnabled(True)
                self.submit_btn.setEnabled(True)
                
                # Enable all attendance marking UI elements
                self.status_combo.setEnabled(True)
                
                # Find and enable action buttons
                if hasattr(self, 'findChild'):
                    apply_btn = self.findChild(QPushButton, "apply_status_btn")
                    if apply_btn:
                        apply_btn.setEnabled(True)
                
                print(f"✏️ Edit mode: {name} can mark attendance for {current_month}/{current_year}")
            
            # Clear current attendance data and load saved data
            self.attendance_data = {}
            
            # Update calendar with saved attendance (read-only mode)
            if hasattr(self, 'calendar'):
                # Initialize month/year tracking for the current calendar view
                current_date = self.calendar.selectedDate() if hasattr(self.calendar, 'selectedDate') else QDate.currentDate()
                self.last_displayed_month = current_date.month()
                self.last_displayed_year = current_date.year()
                print(f"📅 Initialized month/year tracking: {self.last_displayed_month}/{self.last_displayed_year}")
                
                self.update_calendar_with_saved_attendance()
                
                # Keep focus on student table after selection
                # User can manually click calendar when they want to navigate dates
                self.students_table.table.setFocus()
                print("📅 Calendar updated with attendance data, table keeps focus")
            if hasattr(self, 'calendar') and hasattr(self.calendar, 'setFocus'):
                # Use a short delay to ensure the selection is complete
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(100, lambda: self.calendar.setFocus(Qt.OtherFocusReason))
                print("🎯 Calendar will receive focus for keyboard navigation")
                
    def update_selection_info(self):
        """Update the selection info label with student ID, active week and active month only."""
        if not self.selected_student:
            self.selection_info.setText("👤 No student selected")
            return
            
        # Get student ID
        student_id = self.selected_student.get("id", "N/A")
        
        # Get current calendar date for active week/month calculation
        current_date = QDate.currentDate()
        if hasattr(self, 'calendar') and hasattr(self.calendar, 'selectedDate'):
            selected_date = self.calendar.selectedDate()
            if selected_date.isValid():
                current_date = selected_date
        
        # Calculate active month
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        active_month = month_names[current_date.month() - 1]
        
        # Calculate active week (week number in the month)
        first_day_of_month = QDate(current_date.year(), current_date.month(), 1)
        days_from_start = first_day_of_month.daysTo(current_date)
        active_week = (days_from_start // 7) + 1
        
        # Format: Student ID | Active Month | Week X
        info_text = f"🆔 ID: {student_id} | 📅 {active_month} | 📅 Week {active_week}"
        self.selection_info.setText(info_text)
        
    def update_calendar_with_saved_attendance(self):
        """Update calendar to show saved attendance data from database."""
        if not hasattr(self, 'current_student_id') or self.current_student_id is None:
            print("❌ No current student selected")
            return
            
        try:
            print(f"🔍 Loading attendance for student {self.current_student_id}")
            
            # Get attendance records for current student from database
            attendance_records = self.db.get_attendance(student_id=self.current_student_id)
            print(f"📊 Raw attendance_records from DB: {attendance_records}")
            print(f"📊 Type of attendance_records: {type(attendance_records)}")
            
            # Convert to calendar format
            saved_attendance = {}
            for record in attendance_records:
                print(f"🔍 Processing record: {record}")
                date_str = record['date']  # Assuming format: 'YYYY-MM-DD'
                status = record['status']
                saved_attendance[date_str] = status
                self.attendance_data[date_str] = status
                print(f"   Added: {date_str} = {status}")
            
            print(f"📅 Final attendance_data: {self.attendance_data}")
            print(f"📅 Number of attendance records: {len(saved_attendance)}")
            
            if hasattr(self, 'calendar'):
                # If ModernCalendarWidget has specific methods, use them
                if hasattr(self.calendar, 'load_saved_attendance'):
                    self.calendar.load_saved_attendance(saved_attendance, edit_mode=False)
                    print(f"📅 Calendar loaded with {len(saved_attendance)} saved attendance records via load_saved_attendance")
                
                # Update calendar's internal attendance data (for ModernCalendarWidget)
                if hasattr(self.calendar, 'attendance_data'):
                    self.calendar.attendance_data = self.attendance_data.copy()
                    print(f"📅 Updated calendar's internal attendance_data with {len(saved_attendance)} records")
                    
                # Set parent_widget reference so calendar can access attendance_data
                if hasattr(self.calendar, 'parent_widget'):
                    self.calendar.parent_widget = self
                    print(f"🔗 Set calendar parent_widget reference for attendance access")
                    print(f"🔍 self.attendance_data at parent_widget set: {self.attendance_data}")
                    print(f"🔍 Calendar can access: {hasattr(self, 'attendance_data')}")
                    print(f"🔍 Calendar parent set: {self.calendar.parent_widget is not None}")
                    if hasattr(self.calendar.parent_widget, 'attendance_data'):
                        print(f"🔍 parent_widget.attendance_data: {self.calendar.parent_widget.attendance_data}")
                    
                    
                # Force calendar display refresh to apply attendance styling
                if hasattr(self.calendar, '_update_display'):
                    self.calendar._update_display()
                    print(f"🎨 Forced calendar visual refresh to show attendance styling")
                elif hasattr(self.calendar, 'refresh_calendar'):
                    self.calendar.refresh_calendar()
                    print(f"🔄 Refreshed calendar display")
                elif hasattr(self.calendar, 'update'):
                    self.calendar.update()
                    print(f"🔄 Updated calendar widget")
                    
        except Exception as e:
            print(f"❌ Error updating calendar: {e}")
            import traceback
            traceback.print_exc()
            # Also try to update individual date displays
            for date_str, status in self.saved_attendance.items():
                try:
                    # Parse date string
                    year, month, day = map(int, date_str.split('-'))
                    date_obj = QDate(year, month, day)
                    
                    # Update visual display if method exists
                    if hasattr(self.calendar, 'update_attendance_display'):
                        self.calendar.update_attendance_display(date_obj, status)
                        
                except (ValueError, AttributeError):
                    continue
                    
            print(f"📅 Loaded {len(self.saved_attendance)} saved attendance records to calendar with visual update")
            
    def apply_status(self):
        """Apply selected status to selected student."""
        if not self.selected_student:
            show_info_message("No Selection", "Please select a student first.")
            return
        
        # Check if we're in read-only mode (but now allow edit via button)
        if not self.edit_mode:
            show_info_message("Edit Mode Required", "Click 'Edit Existing Attendance' button to modify attendance.")
            return
            
        status = self.status_combo.currentText()
        if status == "Select Status":
            show_info_message("No Status", "Please select an attendance status.")
            return
            
        # Map status text to appropriate value
        status_mapping = {
            "Present": "present",
            "Absent": "absent",
            "Late": "late", 
            "Leave": "leave",
            "Holiday": "holiday"
        }
        
        # Get standardized status value (defaults to lowercase version if not in mapping)
        status_value = status_mapping.get(status, status.lower())
        
        # Get currently selected date from calendar
        if hasattr(self.calendar, 'selectedDate'):
            selected_date = self.calendar.selectedDate()
        else:
            selected_date = QDate.currentDate()
        
        # Store the selected status in the attendance data (ensure we're using the correct status)
        date_str = selected_date.toString("yyyy-MM-dd")
        self.attendance_data[date_str] = status_value  # Use the mapped status value
        
        # Update attendance data
        self.update_calendar_date(selected_date, status_value)  # Pass the correct status value
        self.has_unsaved_changes = True
        self.update_submit_button_style()
        
        # Ensure calendar gets focus again for keyboard navigation
        if hasattr(self.calendar, 'setFocus'):
            self.calendar.setFocus()
        
        student_name = self.selected_student["name"]
        show_info_message("Status Applied", f"✅ Applied {status} to {student_name} for {selected_date.toString('dd/MM/yyyy')}")
        print(f"✅ Status Applied: {student_name} -> {status_value} on {selected_date.toString('dd/MM/yyyy')}")
            
    def bulk_action(self, action_type):
        """Perform bulk attendance action."""
        if not self.selected_student:
            show_info_message("No Selection", "Please select a student first.")
            return
        
        # Check if we're in read-only mode
        if not self.edit_mode:
            show_info_message("Read-Only Mode", "This student's attendance is already marked for this month.\nBulk actions are not allowed in read-only mode.")
            return
            
        # Get the selected status from dropdown
        status = self.status_combo.currentText()
        if action_type != "Holiday" and status == "Select Status":
            show_info_message("No Status", "Please select an attendance status first.")
            return
            
        # Map status text to appropriate value
        status_mapping = {
            "Present": "present",
            "Absent": "absent",
            "Late": "late", 
            "Leave": "leave",
            "Excused": "leave",  # Treat Excused as Leave
            "Holiday": "holiday"
        }
        
        # Get standardized status value (defaults to lowercase version if not in mapping)
        status_value = status_mapping.get(status, status.lower()) if action_type != "Holiday" else "holiday"
        print(f"🔍 Bulk action using status: {status} (mapped to {status_value})")
        
        student_name = self.selected_student["name"]
        count = 0
        
        if action_type == "Active Week":
            # Get selected date from calendar, or current date if none selected
            if hasattr(self.calendar, 'selectedDate'):
                selected_date = self.calendar.selectedDate()
            else:
                selected_date = QDate.currentDate()
            
            # Get the week of the selected date (Monday to Saturday)
            monday = selected_date.addDays(-(selected_date.dayOfWeek() - 1))  # Get Monday of selected week
            
            for i in range(6):  # Monday to Saturday
                work_date = monday.addDays(i)
                # Include all days in selected week regardless of month
                self.update_calendar_date(work_date, status_value)  # Use selected status
                count += 1
            
            week_start = monday.toString('dd/MM/yyyy')
            week_end = monday.addDays(5).toString('dd/MM/yyyy')
            show_info_message("Bulk Action", f"📊 Applied {status} status to {student_name} for selected week ({week_start} to {week_end})")
            print(f"👥 Bulk action: {student_name} -> {status} for active week ({count} days): {week_start} to {week_end}")
            
        elif action_type == "Active Month":
            # Get selected date from calendar, or current date if none selected
            if hasattr(self.calendar, 'selectedDate'):
                selected_date = self.calendar.selectedDate()
            else:
                selected_date = QDate.currentDate()
            
            # Get all working days in the selected date's month (Monday to Saturday)
            first_day = QDate(selected_date.year(), selected_date.month(), 1)
            last_day = QDate(selected_date.year(), selected_date.month(), first_day.daysInMonth())
            
            current_date = first_day
            while current_date <= last_day:
                # Only mark working days (Monday=1 to Saturday=6)
                if current_date.dayOfWeek() <= 6:
                    self.update_calendar_date(current_date, status_value)  # Use selected status
                    count += 1
                current_date = current_date.addDays(1)
            
            month_name = selected_date.toString('MMMM yyyy')
            show_info_message("Bulk Action", f"📊 Applied {status} status to {student_name} for {month_name} ({count} working days)")
            print(f"👥 Bulk action: {student_name} -> {status} for active month ({count} working days): {month_name}")
            
        elif action_type == "Holiday":
            # Get currently selected date
            if hasattr(self.calendar, 'selectedDate'):
                selected_date = self.calendar.selectedDate()
                self.update_calendar_date(selected_date, "holiday")  # Always use lowercase "holiday"
                show_info_message("Holiday Marked", f"📅 Marked {selected_date.toString('dd/MM/yyyy')} as Holiday")
                print(f"🏖️ Holiday marked: {selected_date.toString('dd/MM/yyyy')}")
            else:
                show_info_message("No Date", "Please select a date first.")
        
        # Mark as having unsaved changes
        if count > 0:
            self.has_unsaved_changes = True
            self.update_submit_button_style()
        
    def save_attendance(self):
        """Save attendance data to database and prepare for next student."""
        if not self.selected_student:
            show_info_message("No Student", "Please select a student first.")
            return
            
        if not self.has_unsaved_changes or not self.attendance_data:
            show_info_message("No Changes", "📝 No attendance changes to save!")
            print("📝 No changes to save")
            return
            
        try:
            # Use current_student_id which is correctly retrieved during student selection
            student_id = self.current_student_id
            saved_count = 0
            
            # Save each attendance record to database
            for date_str, status in self.attendance_data.items():
                try:
                    self.db.mark_attendance(student_id, date_str, status)
                    saved_count += 1
                except Exception as e:
                    print(f"❌ Error saving attendance for {date_str}: {e}")
            
            current_student = self.selected_student["name"]
            show_info_message("Data Saved", f"💾 Saved {saved_count} attendance records for {current_student}!\n\n✨ Attendance successfully saved to database.")
            print(f"💾 Saved {saved_count} attendance records for {current_student}")
            
            # Update saved attendance data with new records
            self.saved_attendance.update(self.attendance_data)
            
            # Reset edit mode and prepare for viewing
            self.edit_mode = False
            self.edit_btn.setText("Edit Mode")
            self.edit_btn.setStyleSheet(self.get_button_style('secondary'))
            self.submit_btn.setEnabled(False)
            self.has_unsaved_changes = False
            
            # Clear current edits and reload saved data
            self.attendance_data = {}
            self.update_calendar_with_saved_attendance()
            
            print("✅ Attendance saved successfully and switched to view mode")
            
        except Exception as e:
            show_info_message("Save Error", f"❌ Error saving attendance: {str(e)}")
            print(f"❌ Error saving attendance: {e}")
    
    def prepare_for_next_student(self):
        """Prepare the interface for marking attendance for the next student."""
        # Clear selected student
        self.selected_student = None
        self.selection_info.setText("👤 No student selected")
        
        # Reset status dropdown
        self.status_combo.setCurrentIndex(0)  # Reset to "Select Status"
        
        # Reset unsaved changes flag
        self.has_unsaved_changes = False
        
        # Reset submit button style
        styles = get_attendance_styles()
        submit_buttons = self.findChildren(QPushButton)
        for btn in submit_buttons:
            if "Save" in btn.text() or "Submit" in btn.text():
                btn.setStyleSheet(styles['button_primary'])
                btn.setText("Submit Attendance")
                break
        
        # Refresh calendar display
        if hasattr(self.calendar, '_update_display'):
            self.calendar._update_display()
            print("🔄 Calendar refreshed for next student")
        
        # Clear attendance data from calendar
        self.clear_calendar_attendance_data()
        
        # Clear student selection in table
        if hasattr(self, 'student_table'):
            self.student_table.clearSelection()
        
        print("✨ Ready for next student attendance marking")
    
    def clear_calendar_attendance_data(self):
        """Clear attendance data from calendar display."""
        # Clear local attendance data
        self.attendance_data.clear()
        
        # Clear calendar's attendance data if it exists
        if hasattr(self.calendar, '_attendance_data'):
            self.calendar._attendance_data.clear()
        
        # Refresh calendar to clear visual status indicators
        if hasattr(self.calendar, '_update_display'):
            self.calendar._update_display()
            print("🧹 Calendar attendance data cleared")
        
    def reset_data(self):
        """Reset all attendance data and interface."""
        # Check if we're in read-only mode
        if not self.edit_mode:
            show_info_message("Read-Only Mode", "Cannot reset data in read-only mode.\nThis student's attendance is already marked for this month.")
            return
        
        # Clear attendance data
        self.attendance_data.clear()
        
        # Clear student selection and reset interface
        self.prepare_for_next_student()
        
        # Also clear search and filters
        self.search_input.clear()
        self.class_combo.setCurrentIndex(0)
        self.section_combo.setCurrentIndex(0)
        
        show_info_message("Data Reset", "🔄 All attendance data has been reset!\n\n✨ Ready to start fresh attendance marking.")
        print("🔄 Reset all data")
    
    def on_date_clicked(self, selected_date):
        """Handle calendar date selection."""
        selected_date_str = selected_date.toString("dddd, MMMM d, yyyy")
        print(f"📅 Date selected: {selected_date_str}")
        
        # Update selection info with new active week/month based on selected date
        if self.selected_student:
            self.update_selection_info()
        
        print(f"📅 Selection info updated for date: {selected_date.toString('dd/MM/yyyy')}")
    
    def update_calendar_date(self, date, status):
        """Update calendar date with attendance status."""
        date_str = date.toString("yyyy-MM-dd")
        
        # Standardize status values
        status_mapping = {
            "Present": "present",
            "PRESENT": "present",
            "present": "present",
            "Absent": "absent", 
            "ABSENT": "absent",
            "absent": "absent",
            "Late": "late",
            "LATE": "late", 
            "late": "late",
            "Leave": "leave",
            "LEAVE": "leave",
            "leave": "leave",
            "Excused": "leave",  # Treat Excused as Leave
            "EXCUSED": "leave",
            "excused": "leave",
            "Holiday": "holiday",
            "HOLIDAY": "holiday",
            "holiday": "holiday"
        }
        
        # Validate status to ensure it's not None or empty
        if not status:
            print(f"⚠️ Warning: Empty status provided for date {date_str}")
            status = "present"  # Default to present if status is empty
        else:
            # Convert status to standard form
            status = status_mapping.get(status, status.lower())
            
        print(f"🔧 update_calendar_date called with date={date_str}, original status={status}")
        print(f"🔧 Standardized status={status}")
        
        # Ensure we're setting the correct status, not always "Present"
        self.attendance_data[date_str] = status
        
        print(f"📊 Attendance data updated: {date_str} = {status}")
        print(f"📊 Total attendance records: {len(self.attendance_data)}")
        
        # Also update the ModernCalendarWidget's internal attendance data with the correct status
        if hasattr(self.calendar, '_attendance_data'):
            self.calendar._attendance_data[date_str] = status  # Use the standardized status
            print(f"📅 Updated ModernCalendarWidget attendance data: {date_str} = {status}")
            
            # Force calendar to refresh
            if hasattr(self.calendar, '_update_display'):
                self.calendar._update_display()
                print(f"🔄 Forced calendar display refresh")
        
        if self.selected_student:
            student_name = self.selected_student["name"]
            print(f"✅ Updated {student_name}: {date.toString('dd/MM/yyyy')} -> {status}")
            
            # Update status dropdown to reflect the change
            status_items = ["Select Status", "Present", "Absent", "Late", "Excused", "Holiday"]
            if status in status_items:
                self.status_combo.setCurrentText(status)
        else:
            print(f"✅ Updated attendance: {date.toString('dd/MM/yyyy')} -> {status}")
        
        # Refresh calendar visual display if it has the method
        if hasattr(self.calendar, '_update_display'):
            print("🔄 Refreshing ModernCalendarWidget display...")
            self.calendar._update_display()
        elif hasattr(self.calendar, 'update'):
            print("🔄 Refreshing standard calendar display...")
            self.calendar.update()
        else:
            print("⚠️ Calendar doesn't have refresh method")
    
    def update_submit_button_style(self):
        """Update submit button style to indicate unsaved changes."""
        if self.has_unsaved_changes:
            # Change button style to indicate unsaved changes
            styles = get_attendance_styles()
            modified_style = styles['button_primary'].replace('#3B82F6', '#DC2626')  # Change to red
            
            # Find the submit button and update its style
            submit_buttons = self.findChildren(QPushButton)
            for btn in submit_buttons:
                if "Submit" in btn.text():
                    btn.setStyleSheet(modified_style)


# ============================================================================
# STANDALONE RUN CODE - For development/testing only
# This section allows running this page directly for testing
# To be removed when integrating with the main application
# ============================================================================
if __name__ == "__main__":
    # Import necessary modules
    from PyQt5.QtWidgets import QApplication, QMainWindow
    
    # Ensure project root is in path (already done at the top of the file)
    print(f"Running in standalone mode from: {os.path.abspath(__file__)}")
    print(f"Project root: {project_root}")
    print("Python path includes:", sys.path[0])
    
    class StandaloneWindow(QMainWindow):
        """Simple standalone window to test the Attendance page."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("SMIS - Attendance Test")
            self.setGeometry(100, 100, 1200, 800)
            
            # Set application icon
            from utils.ui_helpers import set_app_icon
            set_app_icon(self)
            
            # Create attendance page as central widget
            # AttendancePage doesn't accept a parent parameter
            self.attendance_page = AttendancePage()
            self.setCentralWidget(self.attendance_page)
            
            # Set dummy current user for testing
            self.attendance_page.current_user = {
                "id": 1, 
                "name": "Test User",
                "username": "testuser", 
                "role": "admin"
            }
            
            # Setup test data and handle database initialization
            try:
                # Mock database methods if needed
                if hasattr(self.attendance_page, 'db'):
                    print("Patching database for standalone mode...")
                    
                    # Setup dummy student data
                    self.attendance_page.students_data = [
                        {"id": 1, "name": "Ali Ahmed", "roll_no": "001", "class": "10", "section": "A"},
                        {"id": 2, "name": "Sara Khan", "roll_no": "002", "class": "10", "section": "A"},
                        {"id": 3, "name": "Usman Ali", "roll_no": "003", "class": "10", "section": "B"},
                        {"id": 4, "name": "Ayesha Malik", "roll_no": "004", "class": "9", "section": "A"},
                        {"id": 5, "name": "Bilal Hassan", "roll_no": "005", "class": "9", "section": "B"}
                    ]
                    
                    # Override database-dependent methods to use our dummy data
                    if hasattr(self.attendance_page, 'load_students_from_database'):
                        original_load = self.attendance_page.load_students_from_database
                        self.attendance_page.load_students_from_database = lambda: None  # Do nothing
                        
                    # Refresh the UI with our test data
                    if hasattr(self.attendance_page, 'filter_students'):
                        self.attendance_page.filter_students()
                
                # Initialize the page with any necessary data
                if hasattr(self.attendance_page, 'init_data'):
                    self.attendance_page.init_data()
            except Exception as e:
                print(f"Warning: Could not initialize test data: {e}")
                import traceback
                traceback.print_exc()
                # Continue anyway
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Apply basic styling
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #f8fafc;
            color: #111827;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)
    
    # Setup exception handling for better debugging
    def exception_hook(exc_type, exc_value, traceback_obj):
        """Global exception handler for better error reporting"""
        import traceback
        print("\n" + "="*80)
        print("❌ EXCEPTION OCCURRED")
        print("-"*80)
        traceback.print_exception(exc_type, exc_value, traceback_obj)
        print("="*80)
        
        # Continue with normal exception handling
        sys.__excepthook__(exc_type, exc_value, traceback_obj)
    
    # Set exception hook
    sys.excepthook = exception_hook
    
    # Create and show window
    print("\n🚀 Running Attendance Page in standalone mode")
    print("⚠️  THIS IS FOR DEVELOPMENT/TESTING ONLY")
    print("============================================")
    
    try:
        window = StandaloneWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"❌ Failed to start standalone mode: {e}")
        import traceback
        traceback.print_exc()
