"""Reports page UI implementation."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout,
                           QPushButton)
from ui.components.custom_combo_box import CustomComboBox
from datetime import datetime
from models.database import Database
from ui.components.custom_table import SMISTable

class ReportsPage(QWidget):
    """Reports generation and export page."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self._init_ui()

    def _init_ui(self):
        """Initialize the reports UI components."""
        layout = QVBoxLayout()
        
        # Filters
        filter_layout = QFormLayout()
        
        self.class_filter = CustomComboBox()
        self.class_filter.addItem("All Classes")  # Default option
        self.school_filter = CustomComboBox()
        self.school_filter.addItem("All Schools")  # Default option
        self.month_filter = CustomComboBox()
        self.year_filter = CustomComboBox()
        self.period_filter = CustomComboBox()
        
        # Load filter data from database
        self._load_schools_data()
        self._load_classes_data()
        
        # Set up filter options
        current_year = datetime.now().year
        self.month_filter.addItems(["All"] + [str(i).zfill(2) for i in range(1, 13)])
        self.year_filter.addItems(["All"] + [str(i) for i in range(current_year-5, current_year+6)])
        self.period_filter.addItems([
            "Student-wise",
            "Class-wise",
            "School-wise",
            "Quarterly",
            "Bi-Annual",
            "Yearly"
        ])
        
        filter_layout.addRow("Class:", self.class_filter)
        filter_layout.addRow("School:", self.school_filter)
        filter_layout.addRow("Month:", self.month_filter)
        filter_layout.addRow("Year:", self.year_filter)
        filter_layout.addRow("Report Type:", self.period_filter)
        
        # Buttons
        self.generate_btn = QPushButton("Generate Report")
        self.export_btn = QPushButton("Export to Excel")
        
        # Report table
        self.report_table = SMISTable(self)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.report_table)
        self.setLayout(layout)
        
        self._connect_signals()

    def _connect_signals(self):
        """Connect all signals to slots."""
        self.generate_btn.clicked.connect(self.on_generate)
        self.export_btn.clicked.connect(self.on_export)

    def refresh_data(self):
        """Refresh the page data."""
        self.report_table.table.setRowCount(0)
        self.class_filter.setCurrentIndex(0)
        self.school_filter.setCurrentIndex(0)
        self.month_filter.setCurrentIndex(0)
        self.year_filter.setCurrentIndex(0)
        self.period_filter.setCurrentIndex(0)

    def on_generate(self):
        """Handle generate report button click."""
        pass  # Will be implemented in ReportsController

    def on_export(self):
        """Handle export to Excel button click."""
        pass  # Will be implemented in ReportsController

    def get_filters(self):
        """Get current filter values."""
        return {
            'class': self.class_filter.currentText(),
            'school': self.school_filter.currentText(),
            'month': self.month_filter.currentText(),
            'year': self.year_filter.currentText(),
            'period': self.period_filter.currentText()
        }

    def _load_schools_data(self):
        """Load schools from database and populate school filter."""
        try:
            schools = self.db.get_schools()
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_filter.addItem(school_name, school_id)
            print(f"📚 Loaded {len(schools)} schools in reports page")
        except Exception as e:
            print(f"❌ Error loading schools: {e}")

    def _load_classes_data(self, school_id=None):
        """Load classes from database and populate class filter."""
        try:
            classes = self.db.get_classes(school_id)
            for class_name in classes:
                self.class_filter.addItem(class_name)
            print(f"📚 Loaded {len(classes)} classes in reports page")
        except Exception as e:
            print(f"❌ Error loading classes: {e}")
