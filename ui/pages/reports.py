"""Reports page UI implementation."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                           QPushButton, QTableWidget)
from datetime import datetime
from ui.styles.table_styles import apply_standard_table_style

class ReportsPage(QWidget):
    """Reports generation and export page."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """Initialize the reports UI components."""
        layout = QVBoxLayout()
        
        # Filters
        filter_layout = QFormLayout()
        
        self.class_filter = QComboBox()
        self.school_filter = QComboBox()
        self.month_filter = QComboBox()
        self.year_filter = QComboBox()
        self.period_filter = QComboBox()
        
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
        self.report_table = QTableWidget()
        # Apply standard table styling
        apply_standard_table_style(self.report_table)
        
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
        self.report_table.setRowCount(0)
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
