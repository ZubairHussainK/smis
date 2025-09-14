"""
Custom Date Picker component with enhanced UI and behavior.

This module provides a customized date picker implementation with:
- Custom calendar widget with styled appearance
- Month and year selection dialogs
- Customized day headers with 3-letter abbreviations
- Circle highlighting for selected dates
- Custom positioning and styling
"""
import os
from PyQt5.QtWidgets import (QDateEdit, QCalendarWidget, QToolButton, QPushButton, 
                            QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                            QGridLayout, QSizePolicy, QDialog, QTableView)
from PyQt5.QtCore import Qt, QDate, QSize, QRect, QRectF, QPointF, QLocale, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QBrush, QColor, QFont, QPalette
from PyQt5.QtSvg import QSvgRenderer

# Constants
PRIMARY_COLOR = "#0175b6"      # Selection, hover, focus blue
SECONDARY_COLOR = "#6c757d"    # Secondary button gray
TEXT_COLOR = "#333333"         # Normal text
TEXT_LIGHT_COLOR = "#666666"   # Label text
BORDER_COLOR = "#cccccc"       # Input borders
LIGHTER_COLOR = "#ffffff"      # Input field background
DANGER_COLOR = "#dc3545"       # Cancel/delete red
SUCCESS_COLOR = "#28a745"      # Success green
DARK_COLOR = "#343a40"         # Dark buttons, titles
LIGHT_COLOR = "#f8f9fa"        # Background color
PLACEHOLDER_COLOR = "#999999"  # Placeholder text
TODAY_DATE_COLOR = "#fcac35"  # Today highlight color
# Path to resources directory
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources")


class MonthSelectionDialog(QDialog):
    """Dialog for selecting a month."""
    
    month_selected = pyqtSignal(int)  # Signal to emit when a month is selected
    
    def __init__(self, parent=None, current_month=1):
        """Initialize the month selection dialog."""
        super().__init__(parent)
        self.setWindowTitle("Select Month")
        self.setModal(True)
        self.setFixedSize(340, 210)  # Matched size with standard calendar popup
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        # Store the current month
        self.current_month = current_month
        self.selected_month = current_month
        
        # Add shadow effect
        self.setStyleSheet(f"""
            QDialog {{
                background-color: white;
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
        """)
        
        # Set up the UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI elements."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header container (blue bar)
        header_container = QFrame()
        header_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_container.setFixedHeight(36)  # Fixed compact height
        header_container.setStyleSheet(f"""
            QFrame {{
                background-color: {PRIMARY_COLOR};
                border-radius: 6px;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
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
        layout.addWidget(header_container)
        
        # Container frame for months grid
        months_container = QFrame()
        months_container.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 6px;
                border: none;
            }}
        """)
        months_container_layout = QVBoxLayout(months_container)
        months_container_layout.setContentsMargins(0, 0, 0, 0)
        months_container_layout.setSpacing(0)
        
        # Create grid for month buttons (3x4 grid - 3 rows, 4 columns)
        months_grid = QGridLayout()
        months_grid.setContentsMargins(0, 0, 0, 0)  # Minimal margins
        months_grid.setSpacing(5)  # Space between buttons
        
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
            
            # Set button style - highlight current month
            is_current = month_num == self.current_month
            if is_current:
                month_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {PRIMARY_COLOR};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        background-color: #0186d1;
                    }}
                    QPushButton:pressed {{
                        background-color: #015d8c;
                    }}
                """)
            else:
                month_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        color: {TEXT_COLOR};
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        background-color: #f0f0f0;
                        border: 1px solid #d0d0d0;
                    }}
                    QPushButton:pressed {{
                        background-color: #e8e8e8;
                    }}
                """)
            
            # Store the month number as a property
            month_btn.setProperty("month", month_num)
            
            # Connect button to slot with explicit month number
            month_btn.clicked.connect(lambda checked=False, m=month_num: self._on_month_selected(m))
            
            # Add to grid
            months_grid.addWidget(month_btn, row, col)
        
        # Add grid to container layout
        months_container_layout.addLayout(months_grid)
        
        # Add months container to main layout
        layout.addWidget(months_container)
        
    def _on_month_selected(self, month):
        """Handle month selection."""
        print(f"Month selected: {month}")  # Debug
        self.selected_month = month
        self.month_selected.emit(month)
        self.accept()
        
    def showEvent(self, event):
        """Position the dialog relative to the parent."""
        super().showEvent(event)
        if self.parent():
            # Position at the center of the parent
            parent_rect = self.parent().rect()
            parent_pos = self.parent().mapToGlobal(parent_rect.center())
            
            # Adjust position to center the dialog
            dialog_size = self.size()
            x_pos = int(parent_pos.x() - dialog_size.width() / 2)
            y_pos = int(parent_pos.y() - dialog_size.height() / 2)
            
            # Ensure dialog stays within screen bounds
            self.move(x_pos, y_pos)


class YearSelectionDialog(QDialog):
    """Dialog for selecting a year with grid view and navigation."""
    
    year_selected = pyqtSignal(int)  # Signal to emit when a year is selected
    
    def __init__(self, parent=None, current_year=None):
        """Initialize the year selection dialog."""
        super().__init__(parent)
        
        # If no year specified, use current year
        if current_year is None:
            from datetime import datetime
            current_year = datetime.now().year
            
        self.setWindowTitle("Select Year")
        self.setModal(True)
        self.setFixedSize(340, 210)  # Matched size with standard calendar popup
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        # Store the current year and set initial range
        self.current_year = current_year
        self.selected_year = current_year
        
        # Calculate the start year to show a clean decade (e.g., 1940-1949, 2020-2029)
        # First get the decade start (year with last digit as 0)
        decade_start = current_year - (current_year % 10)
        # Then we can adjust by 1 or 2 to get a nice 12-item range (e.g., 1944-1955)
        self.start_year = decade_start - 6
        
        # Add shadow effect and modern styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: white;
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            /* Modern scrollbar styling */
            QScrollBar:vertical {{
                border: none;
                background: #f0f0f0;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: #a0a0a0;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        # Set up the UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI elements."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header container (blue bar)
        header_container = QFrame()
        header_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_container.setFixedHeight(36)  # Fixed compact height
        header_container.setStyleSheet(f"""
            QFrame {{
                background-color: {PRIMARY_COLOR};
                border-radius: 6px;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
        """)
        
        # Header layout within container
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(2, 0, 2, 0)
        header_layout.setSpacing(0)
        
        # Previous years button
        self.prev_btn = QPushButton()
        self.prev_btn.setFixedSize(28, 28)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                border: none;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: #0186d1;
            }}
            QPushButton:pressed {{
                background-color: #015d8c;
            }}
        """)
        # Set icon from SVG file
        left_icon = QIcon(os.path.join(RESOURCES_PATH, "icons", "arrow_left.svg"))
        self.prev_btn.setIcon(left_icon)
        self.prev_btn.setIconSize(QSize(20, 20))
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
        
        # Next years button
        self.next_btn = QPushButton()
        self.next_btn.setFixedSize(28, 28)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                border: none;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: #0186d1;
            }}
            QPushButton:pressed {{
                background-color: #015d8c;
            }}
        """)
        # Set icon from SVG file
        right_icon = QIcon(os.path.join(RESOURCES_PATH, "icons", "arrow_right.svg"))
        self.next_btn.setIcon(right_icon)
        self.next_btn.setIconSize(QSize(20, 20))
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
        years_container.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 6px;
                border: none;
            }}
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
            
            # Set button style - highlight current year
            is_current = year == self.current_year
            if is_current:
                year_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {PRIMARY_COLOR};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                    }}
                    QPushButton:hover {{
                        background-color: #0186d1;
                    }}
                    QPushButton:pressed {{
                        background-color: #015d8c;
                    }}
                """)
            else:
                year_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        color: {TEXT_COLOR};
                        font-size: 14px;
                        padding: 0;
                        margin: 2px;
                    }}
                    QPushButton:hover {{
                        background-color: #f0f0f0;
                        border: 1px solid #d0d0d0;
                    }}
                    QPushButton:pressed {{
                        background-color: #e8e8e8;
                    }}
                """)
            
            # Store the year as a property
            year_btn.setProperty("year", year)
            
            # Connect button to slot
            year_btn.clicked.connect(lambda checked=False, y=year: self._on_year_selected(y))
            
            # Add to grid
            self.years_grid.addWidget(year_btn, row, col)
    
    def _on_year_selected(self, year):
        """Handle year selection."""
        print(f"Year selected: {year}")
        self.selected_year = year
        self.year_selected.emit(year)
        self.accept()
    
    def _show_prev_years(self):
        """Show previous set of years."""
        self.start_year -= 12
        self._update_years_grid()
    
    def _show_next_years(self):
        """Show next set of years."""
        self.start_year += 12
        self._update_years_grid()
    
    def showEvent(self, event):
        """Position the dialog relative to the parent."""
        super().showEvent(event)
        if self.parent():
            # Position at the center of the parent
            parent_rect = self.parent().rect()
            parent_pos = self.parent().mapToGlobal(parent_rect.center())
            
            # Adjust position to center the dialog
            dialog_size = self.size()
            x_pos = int(parent_pos.x() - dialog_size.width() / 2)
            y_pos = int(parent_pos.y() - dialog_size.height() / 2)
            
            # Ensure dialog stays within screen bounds
            self.move(x_pos, y_pos)


class CustomCalendarWidget(QCalendarWidget):
    """Custom calendar widget with month grid selection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(False)  # Hide the grid border
        self.setHorizontalHeaderFormat(self.ShortDayNames)  # Changed to ShortDayNames (3 letters)
        self.setVerticalHeaderFormat(self.NoVerticalHeader)
        self.setSelectionMode(self.SingleSelection)  # Ensure single selection mode
        
        # Set fixed size to ensure all days are visible - wider to fit all 7 days
        self.setMinimumWidth(360)  # Increased width for better display
        self.setFixedWidth(360)
        self.setMinimumHeight(280)
        
        # Apply comprehensive stylesheet for the calendar with strong selector overrides
        self.setStyleSheet("""
            /* Basic calendar styling */
            QCalendarWidget {
                background-color: white !important;
                border-radius: 8px !important;
                min-width: 380px !important;
                width: 380px !important;
            }
            
            QCalendarWidget QWidget {
                background-color: white !important;
            }
            
            /* Force transparent selection background for ALL selection states */
            QCalendarWidget QTableView::item:selected,
            QCalendarWidget QTableView::item:focus,
            QCalendarWidget QTableView::item:hover,
            QCalendarWidget QTableView::item:active,
            QCalendarWidget QAbstractItemView::item:selected,
            QCalendarWidget QAbstractItemView::item:focus,
            QCalendarWidget QAbstractItemView::item:hover,
            QCalendarWidget QAbstractItemView::item:active,
            QCalendarWidget QTableView::item,
            QCalendarWidget QAbstractItemView::item {
                background-color: transparent !important;
                border: none !important;
                selection-background-color: transparent !important;
                color: black !important;
                selection-color: black !important;
            }
            
            /* Style day headers to be white and bold */
            QCalendarWidget QHeaderView::section {
                background-color: white !important; /* Force white background for day headers */
                color: #333333 !important;
                font-weight: bold !important;
                border: none !important;
                padding: 6px !important;
                text-align: center !important;
            }
            
            /* Style day headers - Sunday (first column) and Saturday (last column) in red */
            QCalendarWidget QHeaderView::section:first,
            QCalendarWidget QHeaderView::section:last {
                color: red !important;
                background-color: white !important; /* Force white background */
            }
        """)
        
        # Connect to page change signal to maintain 5-row view and update header buttons
        # Make sure we only have one connection to avoid duplicates
        try:
            # First try to disconnect all existing connections
            while True:
                self.currentPageChanged.disconnect()
        except:
            # Once there are no more connections, we'll get an error
            pass
        
        # Now add a single connection
        self.currentPageChanged.connect(self._handle_page_changed)
        
        # Create a button to replace the month navigation
        self.create_custom_month_button()
        
        # Initialize the 5-row view and header styling
        QTimer.singleShot(0, self._setup_five_row_view)
        QTimer.singleShot(10, self._force_header_styling)
        QTimer.singleShot(20, self._create_header_label)
    
    def showEvent(self, event):
        """Handle the calendar widget being shown."""
        super().showEvent(event)
        print("Calendar widget shown successfully")
        # Create the custom month and year buttons
        QTimer.singleShot(50, self._create_header_label)
        # Set up the calendar view with 5 rows
        QTimer.singleShot(100, self._setup_five_row_view)
        # Force white background on headers
        QTimer.singleShot(150, self._force_header_styling)
        
    def _force_header_styling(self):
        """Force white background on calendar headers programmatically."""
        # Find the calendar table view
        calendar_view = self.findChild(QTableView, "qt_calendar_calendarview")
        if calendar_view:
            # Get horizontal header
            horizontal_header = calendar_view.horizontalHeader()
            if horizontal_header:
                # Set palette to force white background
                from PyQt5.QtGui import QPalette
                from PyQt5.QtCore import Qt
                
                palette = horizontal_header.palette()
                palette.setColor(QPalette.Button, Qt.white)
                palette.setColor(QPalette.ButtonText, Qt.black)
                palette.setColor(QPalette.Base, Qt.white)
                palette.setColor(QPalette.Background, Qt.white)
                palette.setColor(QPalette.Window, Qt.white)
                horizontal_header.setPalette(palette)
                
                # Apply white background stylesheet directly to header
                horizontal_header.setStyleSheet("""
                    QHeaderView {
                        background-color: white !important;
                    }
                    QHeaderView::section {
                        background-color: white !important;
                        color: #333333 !important;
                        font-weight: bold !important;
                        border: none !important;
                        padding: 6px !important;
                        text-align: center !important;
                    }
                    
                    QHeaderView::section:first {
                        color: red !important;
                        background-color: white !important;
                    }
                    
                    QHeaderView::section:last {
                        color: red !important;
                        background-color: white !important;
                    }
                """)
                
                # Force update
                horizontal_header.update()
                print("Header styling forced to white background with palette")
        
    def create_custom_month_button(self):
        """Create a custom month button in the navigation bar."""
        # Schedule multiple attempts to ensure header buttons are created properly
        QTimer.singleShot(0, self._create_header_label)
        QTimer.singleShot(50, self._create_header_label)
        QTimer.singleShot(200, self._create_header_label)  # Additional attempt after layout stabilizes
        
    def _create_header_label(self):
        """Create separate month and year buttons in the navigation bar."""
        nav_bar = self.findChild(QWidget, "qt_calendar_navigationbar")
        if not nav_bar:
            return
            
        # Cleanup existing custom buttons if any
        for button in nav_bar.findChildren(QPushButton):
            if hasattr(button, 'is_calendar_custom_button'):
                button.deleteLater()
            
        # Find the original month and year buttons
        month_button = self.findChild(QToolButton, "qt_calendar_monthbutton")
        year_button = self.findChild(QToolButton, "qt_calendar_yearbutton")
        
        # Find the navigation buttons (prev/next month)
        prev_month_button = self.findChild(QToolButton, "qt_calendar_prevmonth")
        next_month_button = self.findChild(QToolButton, "qt_calendar_nextmonth")
        
        # Set SVG icons for navigation buttons
        if prev_month_button and next_month_button:
            # Define icon paths
            left_svg_path = os.path.join(RESOURCES_PATH, "icons", "arrow_left.svg")
            right_svg_path = os.path.join(RESOURCES_PATH, "icons", "arrow_right.svg")
            
            # Create left arrow icon
            if os.path.exists(left_svg_path):
                left_pixmap = QPixmap(24, 24)
                left_pixmap.fill(Qt.transparent)
                left_painter = QPainter(left_pixmap)
                left_painter.setRenderHint(QPainter.Antialiasing)
                left_painter.setPen(QColor(TEXT_COLOR))
                left_painter.setBrush(QColor(TEXT_COLOR))
                left_svg = QSvgRenderer(left_svg_path)
                left_svg.render(left_painter)
                left_painter.end()
                prev_month_button.setIcon(QIcon(left_pixmap))
                prev_month_button.setIconSize(QSize(20, 20))
                
                # Add custom styling to make it more visible and clickable
                prev_month_button.setStyleSheet(f"""
                    QToolButton {{
                        background-color: transparent;
                        border: none;
                        padding: 8px;
                        min-width: 32px;
                        min-height: 32px;
                    }}
                    QToolButton:hover {{
                        background-color: #f0f0f0;
                        border-radius: 4px;
                    }}
                    QToolButton:pressed {{
                        background-color: #e0e0e0;
                    }}
                """)
            
            # Create right arrow icon
            if os.path.exists(right_svg_path):
                right_pixmap = QPixmap(24, 24)
                right_pixmap.fill(Qt.transparent)
                right_painter = QPainter(right_pixmap)
                right_painter.setRenderHint(QPainter.Antialiasing)
                right_painter.setPen(QColor(TEXT_COLOR))
                right_painter.setBrush(QColor(TEXT_COLOR))
                right_svg = QSvgRenderer(right_svg_path)
                right_svg.render(right_painter)
                right_painter.end()
                next_month_button.setIcon(QIcon(right_pixmap))
                next_month_button.setIconSize(QSize(20, 20))
                
                # Add custom styling to make it more visible
                next_month_button.setStyleSheet(f"""
                    QToolButton {{
                        background-color: transparent;
                        border: none;
                        padding: 5px;
                    }}
                    QToolButton:hover {{
                        background-color: #f0f0f0;
                        border-radius: 4px;
                    }}
                """)
        
        if month_button and year_button:
            # Hide original buttons
            month_button.setVisible(False)
            year_button.setVisible(False)
            
            # Create month button without icon
            self.custom_month_button = QPushButton(month_button.text(), nav_bar)
            
            # Create year button without icon
            self.custom_year_button = QPushButton(year_button.text(), nav_bar)
            
            # Apply consistent styling to both buttons
            button_style = f"""
                QPushButton {{
                    color: {TEXT_COLOR};
                    font-weight: bold;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                    padding: 6px 10px 6px 6px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: #f0f0f0;
                }}
                QPushButton:pressed {{
                    background-color: #e0e0e0;
                }}
            """
            
            self.custom_month_button.setStyleSheet(button_style)
            self.custom_year_button.setStyleSheet(button_style)
            
            self.custom_month_button.is_calendar_custom_button = True
            self.custom_year_button.is_calendar_custom_button = True
            
            # Calculate the total width needed for both buttons
            month_width = self.custom_month_button.sizeHint().width()
            year_width = self.custom_year_button.sizeHint().width()
            spacing = 10  # Space between buttons
            total_width = month_width + spacing + year_width
            
            # Calculate center position in the navigation bar
            nav_width = nav_bar.width()
            start_x = max(0, (nav_width - total_width) // 2)
            btn_height = month_button.height()
            
            # Position buttons centered in the navigation bar
            self.custom_month_button.setGeometry(start_x, 0, month_width, btn_height)
            self.custom_year_button.setGeometry(start_x + month_width + spacing, 0, year_width, btn_height)
            
            # Connect click events to appropriate handlers
            self.custom_month_button.clicked.connect(self.show_month_selection)
            self.custom_year_button.clicked.connect(self.show_year_selection)
            
            # Show the custom buttons
            self.custom_month_button.show()
            self.custom_year_button.show()
            
            # Install event filter on navigation bar to handle resizing
            nav_bar.installEventFilter(self)
                
        # Update buttons when the page changes
        try:
            self.currentPageChanged.disconnect(self._update_header_label)
        except:
            pass
        self.currentPageChanged.connect(self._update_month_year_buttons)
        
    def _update_month_year_buttons(self, year, month):
        """Update the month and year button text."""
        if hasattr(self, 'custom_month_button') and self.custom_month_button:
            month_name = QLocale().monthName(month)
            self.custom_month_button.setText(month_name)
            
            # Make sure button size is updated after text change
            self.custom_month_button.adjustSize()
            
        if hasattr(self, 'custom_year_button') and self.custom_year_button:
            self.custom_year_button.setText(str(year))
            
            # Make sure button size is updated after text change
            self.custom_year_button.adjustSize()
            
        # Recenter buttons after text update
        nav_bar = self.findChild(QWidget, "qt_calendar_navigationbar")
        if nav_bar and hasattr(self, 'custom_month_button') and hasattr(self, 'custom_year_button'):
            # Get button dimensions
            month_width = self.custom_month_button.sizeHint().width()
            year_width = self.custom_year_button.sizeHint().width()
            spacing = 10  # Space between buttons
            total_width = month_width + spacing + year_width
            
            # Calculate center position
            nav_width = nav_bar.width()
            start_x = max(0, (nav_width - total_width) // 2)
            btn_height = self.custom_month_button.height()
            
            # Reposition buttons
            self.custom_month_button.setGeometry(start_x, 0, month_width, btn_height)
            self.custom_year_button.setGeometry(start_x + month_width + spacing, 0, year_width, btn_height)
        
    def eventFilter(self, obj, event):
        """Handle resize events for the navigation bar to keep buttons centered."""
        if hasattr(self, 'custom_month_button') and hasattr(self, 'custom_year_button'):
            if event.type() == event.Resize:
                # Get navigation bar
                if obj == self.findChild(QWidget, "qt_calendar_navigationbar"):
                    # Recalculate button positions
                    nav_bar = obj
                    nav_width = nav_bar.width()
                    
                    # Get button dimensions
                    month_width = self.custom_month_button.sizeHint().width()
                    year_width = self.custom_year_button.sizeHint().width()
                    spacing = 10  # Space between buttons
                    total_width = month_width + spacing + year_width
                    
                    # Calculate center position
                    start_x = max(0, (nav_width - total_width) // 2)
                    btn_height = self.custom_month_button.height()
                    
                    # Reposition buttons
                    self.custom_month_button.setGeometry(start_x, 0, month_width, btn_height)
                    self.custom_year_button.setGeometry(start_x + month_width + spacing, 0, year_width, btn_height)
        
        # Continue normal event processing
        return super().eventFilter(obj, event)
    
    def _setup_five_row_view(self):
        """Configure the calendar to display only 5 rows with consistent column sizing."""
        # Find the calendar view (which is a QTableView)
        calendar_view = self.findChild(QTableView, "qt_calendar_calendarview")
        if not calendar_view:
            print("Calendar table view not found")
            return
            
        
        # First, ensure column widths are properly set for all 7 days of the week
        # Use a smaller column width to ensure all 7 days fit but not too tight
        column_width = 50  # Fixed width for each day column
        for col in range(7):
            calendar_view.setColumnWidth(col, column_width)
        
        # Get the first day of the current month
        current_year = self.yearShown()
        current_month = self.monthShown()
        first_day = QDate(current_year, current_month, 1)
        
        # Calculate the number of days in the month
        days_in_month = first_day.daysInMonth()
        
        # Hide the last rows if there are more than 5 rows
        row_count = calendar_view.model().rowCount()
        
        # Get the normal row height
        current_height = calendar_view.rowHeight(0)
        
        # Calculate extra height to distribute among the 5 rows
        extra_per_row = 0
        if row_count > 5:
            # If more than 5 rows, we need to add extra height to each visible row
            extra_total = calendar_view.rowHeight(5) * (row_count - 5)
            extra_per_row = extra_total // 5
        
        # Add additional spacing for better layout
        additional_spacing = 10  # Reduced spacing between rows for more compact display
        target_height = current_height + extra_per_row + additional_spacing
        
        # Apply consistent row heights to the first 5 rows
        for row in range(5):
            calendar_view.setRowHeight(row, target_height)
            
        # Hide rows beyond the 5th row
        for row in range(5, row_count):
            calendar_view.setRowHeight(row, 0)
            
        # Make sure table view has a fixed width that accommodates all columns properly
        total_width = column_width * 7 + 10  # Add a small buffer
        calendar_view.setFixedWidth(total_width)
        
        # Force the view to update
        calendar_view.update()
            
        # Make sure all days are visible by setting min column width
        for col in range(calendar_view.model().columnCount()):
            calendar_view.setColumnWidth(col, 40)  # Set fixed width for day columns
            
        # Apply styling to remove any grid lines
        calendar_view.setShowGrid(False)
        calendar_view.setStyleSheet("""
            QTableView {
                gridline-color: transparent !important;
                border: none !important;
                outline: none !important;
                background-color: white !important;
            }
            
            QTableView::item {
                border: none !important;
                padding: 2px !important;
                background-color: transparent !important;
            }
            
            QHeaderView::section {
                background-color: white !important; /* Force white background for day headers */
                color: #333333 !important;
                border: none !important;
                padding: 5px !important;
                font-weight: bold !important;
                border-bottom: none !important; /* Remove bottom border */
            }
            
            /* Style day headers - Sunday (first column) and Saturday (last column) in red */
            QHeaderView::section:first {
                color: red !important;
                background-color: white !important; /* Force white background */
            }
            
            QHeaderView::section:last {
                color: red !important;
                background-color: white !important; /* Force white background */
            }
        """)
    
    def _handle_page_changed(self, year, month):
        """Handle calendar page changes to maintain 5-row view and update header buttons."""
        # Static variable to track the last page to prevent duplicate handling
        if not hasattr(self, '_last_page_info'):
            self._last_page_info = {'page': (-1, -1), 'count': 0}
        
        # Track page changes but don't print debug messages
        if (year, month) != self._last_page_info['page']:
            self._last_page_info['page'] = (year, month)
            self._last_page_info['count'] = 0
        else:
            # Skip if we've already processed this page change
            self._last_page_info['count'] += 1
            if self._last_page_info['count'] > 2:
                # Don't process too many times
                return
            
        # Always set up the 5-row view and update buttons
        # Set up 5-row view
        QTimer.singleShot(50, self._setup_five_row_view)
        
        # Update custom month and year buttons
        QTimer.singleShot(60, lambda: self._update_month_year_buttons(year, month))
        
        # Re-apply header styling after page change
        QTimer.singleShot(70, self._force_header_styling)

    def paintCell(self, painter, rect, date):
        """Custom cell painting with circle highlight for selected dates."""
        # Save original painter state
        painter.save()
        
        # IMPORTANT: Clear the background completely to override any default styling
        # This removes the box highlight that Qt applies to selected dates
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(rect, Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        # Get date text
        day = date.day()
        text = str(day)
        
        # Check if this date belongs to the current month being shown
        current_month = self.monthShown()
        current_year = self.yearShown()
        
        # Draw cell background as pure white to ensure no other styling shows through
        painter.fillRect(rect, QColor(255, 255, 255))
        
        # If date is from another month, we'll still paint the background but not the text
        if date.month() != current_month or date.year() != current_year:
            # Don't draw dates from other months, but keep the white background
            painter.restore()
            return
        
        # Define the font and colors
        font = painter.font()
        font.setPointSize(9)  # Slightly smaller font size
        font.setBold(True)    # Make it bold
        painter.setFont(font)
        
        # Check if date is selected - force compare year, month, and day for reliability
        current_selected = self.selectedDate()
        is_selected = (date.year() == current_selected.year() and 
                       date.month() == current_selected.month() and 
                       date.day() == current_selected.day())
                       
        is_today = date == QDate.currentDate()
        
        # Calculate circle and text position - centered in the cell with increased size
        # Make circle size slightly larger to ensure it's visible
        circle_size = min(rect.width(), rect.height()) * 0.8  # Use 80% of cell size for better circles
        
        # Add minimum size guarantee to ensure circles are visible
        if circle_size < 30:  # Force minimum circle size
            circle_size = 30
            
        # Center the circle in the cell
        circle_x = rect.x() + (rect.width() - circle_size) / 2
        circle_y = rect.y() + (rect.height() - circle_size) / 2
        
        # Use QRectF for better anti-aliasing
        circle_rect = QRectF(circle_x, circle_y, circle_size, circle_size)
        text_rect = rect  # Use full rect for text centering
        
        # Draw selected date with only a circle (no box background)
        if is_selected:
            # Draw circle with selection color
            painter.setBrush(QColor(PRIMARY_COLOR))
            painter.setPen(Qt.NoPen)  # No outline
            painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother circles
            painter.drawEllipse(circle_rect)
            
            # Draw text in white - ensure good contrast with blue background
            painter.setPen(QColor(255, 255, 255))  # Explicit white color
        
        # Draw today's date with filled circle (similar to selected)
        elif is_today:
            # Fill with primary color (lighter to differentiate from selected)
            painter.setBrush(QColor(TODAY_DATE_COLOR))
            painter.setPen(Qt.NoPen)  # No outline
            painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother circles
            painter.drawEllipse(circle_rect)
          
            
            # Draw text in white
            painter.setPen(Qt.black)
        
        # Regular dates
        else:
            # Draw text in normal color
            painter.setPen(QColor(TEXT_COLOR))

        
        # Draw the date text
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        # Restore painter
        painter.restore()
    
    def show_month_selection(self):
        """Show custom month selection dialog."""
        print("Month button clicked - showing month selection dialog!")
        
        # Get current month
        current_month = self.monthShown()
        
        # Create month selection dialog
        month_dialog = MonthSelectionDialog(self, current_month)
        
        # Position the dialog below the month button rather than centered
        button_pos = self.mapToGlobal(self.rect().bottomLeft())
        # Calculate position - place it in the middle horizontally and lower vertically
        dialog_x = button_pos.x() + (self.width() - month_dialog.width()) // 2
        dialog_y = button_pos.y() + 25  # Move down from the calendar by 25px
        month_dialog.move(dialog_x, dialog_y)
        
        # Show the dialog and get result
        if month_dialog.exec_():
            selected_month = month_dialog.selected_month
            # Set the month on the calendar
            self.setCurrentPage(self.yearShown(), selected_month)
            print(f"Month changed to: {selected_month}")
            # Ensure 5-row view is maintained after month change
            QTimer.singleShot(100, self._setup_five_row_view)
    
    def show_year_selection(self):
        """Show custom year selection dialog."""
        print("Year button clicked - showing year selection dialog!")
        
        # Get current year
        current_year = self.yearShown()
        
        # Create year selection dialog
        year_dialog = YearSelectionDialog(self, current_year)
        
        # Position the dialog below the year button rather than centered
        button_pos = self.mapToGlobal(self.rect().bottomLeft())
        # Calculate position - place it in the middle horizontally and lower vertically
        dialog_x = button_pos.x() + (self.width() - year_dialog.width()) // 2
        dialog_y = button_pos.y() + 25  # Move down from the calendar by 25px
        year_dialog.move(dialog_x, dialog_y)
        
        # Show the dialog and get result
        if year_dialog.exec_():
            selected_year = year_dialog.selected_year
            # Set the year on the calendar
            self.setCurrentPage(selected_year, self.monthShown())
            print(f"Year changed to: {selected_year}")
            # Ensure 5-row view is maintained after year change
            QTimer.singleShot(100, self._setup_five_row_view)


class CustomDateEdit(QDateEdit):
    """Custom DateEdit with calendar icon and styling."""
    
    def __init__(self, parent=None, icon_only=False):
        """Initialize the custom date edit field."""
        super().__init__(parent)
        # Set object name for specific styling
        self.setObjectName("CustomDateEdit")
        self.icon_only = icon_only  # Flag to determine if we should show only the icon
        
        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())  # Initialize with current date
        self.setDisplayFormat("dd-MMM-yy")  # Format like 13-Sep-25
        self.setMinimumDate(QDate(1900, 1, 1))  # Reasonable minimum date
        self.setMaximumDate(QDate.currentDate().addYears(100))  # Allow up to 100 years in the future
        
        # Custom styles for DateEdit with extremely specific selectors
        if self.icon_only:
            # For icon-only mode, we hide the text edit part and only show the calendar button
            self.dateEditStyle = f"""
                QDateEdit#CustomDateEdit {{
                    border: none !important;
                    background-color: transparent !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                
                QDateEdit#CustomDateEdit::drop-down {{
                    border: none !important;
                    background-color: transparent !important;
                    width: 32px !important;
                    height: 32px !important;
                    subcontrol-origin: padding !important;
                    subcontrol-position: center !important;
                }}
            """
        else:
            # Standard style for normal date edit with text field
            self.dateEditStyle = f"""
                QDateEdit#CustomDateEdit {{
                    padding: 2px 10px !important;
                    border: 1px solid {BORDER_COLOR} !important;
                    border-radius: 6px !important;
                    font-size: 14px !important;
                    font-weight: bold !important;
                    background-color: white !important;
                    color: {TEXT_COLOR} !important;
                    min-height: 32px !important;
                    height: 32px !important;
                    margin: 0 !important;
            }}
            
            QDateEdit#CustomDateEdit::drop-down {{
                subcontrol-origin: padding !important;
                subcontrol-position: top right !important;
                width: 20px !important;
                border-left-width: 0px !important;
                background-color: transparent !important;
            }}
            
            /* Customize down-arrow based on mode */
            QDateEdit#CustomDateEdit::down-arrow {{
                width: 24px !important;
                height: 24px !important;
                image: url(":images/calendar.svg") !important;  
                background-color: transparent !important;
                border: none !important;
            }}
        """
        
        # Apply specific styling to ensure visibility
        self.setStyleSheet(self.dateEditStyle)
        
        # Set fixed height for consistency
        self.setMinimumHeight(32)
        self.setFixedHeight(32)
        
        # Create a custom calendar widget
        self._setup_custom_calendar()
        
        # Connect to popup signal to setup month button
        self.calendarWidget().activated.connect(self.calendar_date_selected)
        self.calendarWidget().clicked.connect(self.calendar_date_selected)
        
        # Use timer to ensure style is applied after all parent styles
        QTimer.singleShot(0, self.enforceStyle)
        QTimer.singleShot(100, self.enforceStyle)  # Apply again after a delay
        QTimer.singleShot(500, self.enforceStyle)  # Apply once more for good measure
        
    def enforceStyle(self):
        """Force the style to be applied again to overcome any style conflicts."""
        # Get the current object name or use a generic one
        object_name = self.objectName() if self.objectName() else "CustomDateEdit"
        
        # Create a highly specific style with !important flags
        specific_style = f"""
            QDateEdit#{object_name} {{
                padding: 2px 10px !important;
                border: 1px solid {BORDER_COLOR} !important;
                border-radius: 6px !important;
                font-size: 14px !important;
                font-weight: bold !important;
                background-color: white !important;
                color: {TEXT_COLOR} !important;
                min-height: 32px !important;
                height: 32px !important;
                margin: 0 !important;
                min-width: 180px !important;
            }}
            
            QDateEdit#{object_name}::drop-down {{
                subcontrol-origin: padding !important;
                subcontrol-position: top right !important;
                width: 20px !important;
                border-left-width: 0px !important;
                background-color: transparent !important;
            }}
            
            /* Hide the default drop-down button completely */
            QDateEdit#{object_name}::down-arrow {{
                width: 0px !important;
                height: 0px !important;
                background-color: transparent !important;
                border: none !important;
            }}
        """
        
        # Apply the style
        self.setStyleSheet(specific_style)
        
        # Force the calendar widget to also apply its styling
        if hasattr(self, 'calendar_widget'):
            calendar = self.calendar_widget
            if calendar:
                # Force the 5-row view setup when style is enforced
                QTimer.singleShot(0, calendar._setup_five_row_view)
                QTimer.singleShot(50, calendar._force_header_styling)
                
    def showEvent(self, event):
        """Handle the widget being shown."""
        super().showEvent(event)
        # Re-apply styles when shown
        QTimer.singleShot(0, self.enforceStyle)
        QTimer.singleShot(50, self.enforceStyle)
        
    def showPopup(self):
        """Override to position calendar popup lower and ensure proper styling."""
        # Ensure the calendar is properly styled before showing
        if hasattr(self, 'calendar_widget'):
            # Pre-apply styling first
            self.calendar_widget._setup_five_row_view()
            self.calendar_widget._force_header_styling()
            self.calendar_widget._create_header_label()
            
            # Ensure calendar has proper width - wider to fit all 7 days
            self.calendar_widget.setMinimumWidth(360)
            self.calendar_widget.setFixedWidth(360)
            self.calendar_widget.setMinimumHeight(280)
        
        # Show the calendar popup
        super().showPopup()
        
        # Move the popup down after it appears
        calendar_popup = self.findChild(QCalendarWidget)
        if calendar_popup:
            # Get calendar popup position
            pos = calendar_popup.pos()
            
            # For icon-only mode, center the calendar under the icon
            if hasattr(self, 'icon_only') and self.icon_only:
                # Center horizontally under the icon
                pos.setX(pos.x() - (360 - self.width()) // 2)
                # Move down a bit more for icon-only mode
                calendar_popup.move(pos.x(), pos.y() + 35)
            else:
                # Standard positioning for regular date edit
                calendar_popup.move(pos.x(), pos.y() + 50)
            
            # Ensure proper size after display - wider to fit all 7 days
            calendar_popup.setMinimumWidth(360)  # Increased width for better display
            calendar_popup.setFixedWidth(360)
            calendar_popup.setMinimumHeight(280)
            
            # Scheduler multiple rounds of styling enforcement
            if hasattr(self, 'calendar_widget'):
                # Apply styling at staggered intervals for optimal rendering
                QTimer.singleShot(0, self.calendar_widget._setup_five_row_view)
                QTimer.singleShot(50, self.calendar_widget._force_header_styling)
                QTimer.singleShot(100, self.calendar_widget._create_header_label)
                QTimer.singleShot(150, self.calendar_widget._setup_five_row_view)
                self.calendar_widget._force_header_styling()
                self.calendar_widget._create_header_label()
                
                # Apply again after short delays to overcome style cascading
                QTimer.singleShot(10, self.calendar_widget._setup_five_row_view)
                QTimer.singleShot(20, self.calendar_widget._force_header_styling)
                QTimer.singleShot(30, self.calendar_widget._create_header_label)
                QTimer.singleShot(100, self.calendar_widget._setup_five_row_view)
                QTimer.singleShot(150, self.calendar_widget._force_header_styling)
                QTimer.singleShot(200, self.calendar_widget._create_header_label)

    def _setup_custom_calendar(self):
        """Set up the custom calendar widget."""
        # Create our custom calendar
        self.calendar_widget = CustomCalendarWidget(self)
        
        # Set calendar properties
        self.calendar_widget.activated.connect(self.calendar_date_selected)
        self.calendar_widget.clicked.connect(self.calendar_date_selected)
        
        # Apply white background styling to the calendar widget with comprehensive selection overrides
        self.calendar_widget.setStyleSheet("""
            QCalendarWidget {
                background-color: white !important;
                border: 1px solid #cccccc !important;
                border-radius: 8px !important;
                min-height: 280px !important;
                min-width: 300px !important;
                width: 320px !important;
                selection-background-color: transparent !important;
            }
            
            /* Completely disable ALL selection styling in table cells */
            QCalendarWidget QTableView::item:selected,
            QCalendarWidget QTableView::item:focus,
            QCalendarWidget QTableView::item:active,
            QCalendarWidget QTableView::item:hover,
            QCalendarWidget QAbstractItemView::item:selected,
            QCalendarWidget QAbstractItemView::item:focus,
            QCalendarWidget QAbstractItemView::item:hover,
            QCalendarWidget QAbstractItemView::item:active {
                background-color: transparent !important;
                border: none !important;
                outline: none !important;
                color: black !important;
            }
            
            /* Ensure ALL table cells have transparent background */
            QCalendarWidget QTableView,
            QCalendarWidget QTableView::item,
            QCalendarWidget QTableView::section,
            QCalendarWidget QAbstractItemView,
            QCalendarWidget QAbstractItemView::item,
            QCalendarWidget QAbstractItemView::section {
                background-color: transparent !important;
                selection-background-color: transparent !important;
            }
            
            QCalendarWidget QWidget {
                background-color: white !important;
            }
            
            /* Calendar navigation bar styling */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: white !important;
            }
            
            /* Ensure calendar view cells have enough spacing */
            QCalendarWidget QTableView::item {
                padding: 4px !important;
                margin: 2px !important;
            }
        """)
        
        # Set it as the calendar widget
        self.setCalendarWidget(self.calendar_widget)
        
        # Configure popup properties
        self.calendar_widget.currentPageChanged.connect(
            lambda y, m: QTimer.singleShot(0, self.calendar_widget._setup_five_row_view)
        )
        
    def calendar_date_selected(self, date):
        """Handle calendar date selection and close popup."""
        # Set the date in the editor
        self.setDate(date)
        
        # Explicitly set the selected date in the calendar widget
        self.calendar_widget.setSelectedDate(date)
        
        # Force a single update after a short delay
        QTimer.singleShot(30, self.calendar_widget.update)
        
    def paintEvent(self, event):
        """Custom paint to draw calendar icon."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw calendar icon
        rect = self.rect()
        dropdown_width = 40  # Increased from 30 to 40 for more space
        dropdown_x = rect.width() - dropdown_width
        
        # Position for the icon - added more right padding
        icon_x = dropdown_x + 5  # Adjusted for SVG icon positioning
        icon_y = rect.height() / 2 - 12  # Adjusted for SVG icon vertical centering
        
        # Draw calendar icon using SVG
        svg_renderer = QSvgRenderer(os.path.join(RESOURCES_PATH, "icons", "calendar_month.svg"))
        svg_renderer.render(painter, QRectF(icon_x, icon_y, 24, 24))
