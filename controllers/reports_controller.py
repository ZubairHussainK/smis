"""Reports controller implementation."""
import logging
import pandas as pd
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt
from models.database import Database

class ReportsController:
    """Controller for reports generation and export."""

    def __init__(self, view):
        self.view = view
        self.db = Database()
        self._connect_signals()

    def _connect_signals(self):
        """Connect controller to view signals."""
        self.view.generate_btn.clicked.connect(self.generate_report)
        self.view.export_btn.clicked.connect(self.export_to_excel)

    def generate_report(self):
        """Generate report based on selected filters."""
        try:
            filters = self.view.get_filters()
            
            # Get report data based on type
            if filters['period'] == "Student-wise":
                data = self.generate_student_report(filters)
            elif filters['period'] == "Class-wise":
                data = self.generate_class_report(filters)
            elif filters['period'] == "School-wise":
                data = self.generate_school_report(filters)
            elif filters['period'] == "Quarterly":
                data = self.generate_quarterly_report(filters)
            elif filters['period'] == "Bi-Annual":
                data = self.generate_biannual_report(filters)
            else:  # Yearly
                data = self.generate_yearly_report(filters)

            # Update table
            self.update_report_table(data)

        except Exception as e:
            logging.error(f"Error generating report: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def export_to_excel(self):
        """Export current report to Excel."""
        try:
            if self.view.report_table.rowCount() == 0:
                QMessageBox.warning(self.view, "Warning", "No data to export!")
                return

            # Get table data
            data = []
            headers = []
            for col in range(self.view.report_table.columnCount()):
                headers.append(self.view.report_table.horizontalHeaderItem(col).text())
            
            for row in range(self.view.report_table.rowCount()):
                row_data = []
                for col in range(self.view.report_table.columnCount()):
                    item = self.view.report_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)

            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                "Save Report",
                "",
                "Excel Files (*.xlsx)"
            )

            if file_path:
                # Export to Excel
                df.to_excel(file_path, index=False)
                QMessageBox.information(self.view, "Success", "Report exported successfully!")

        except Exception as e:
            logging.error(f"Error exporting report: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def generate_student_report(self, filters):
        """Generate student-wise report."""
        return self.db.get_student_report(filters)

    def generate_class_report(self, filters):
        """Generate class-wise report."""
        return self.db.get_class_report(filters)

    def generate_school_report(self, filters):
        """Generate school-wise report."""
        return self.db.get_school_report(filters)

    def generate_quarterly_report(self, filters):
        """Generate quarterly report."""
        return self.db.get_quarterly_report(filters)

    def generate_biannual_report(self, filters):
        """Generate bi-annual report."""
        return self.db.get_biannual_report(filters)

    def generate_yearly_report(self, filters):
        """Generate yearly report."""
        return self.db.get_yearly_report(filters)

    def update_report_table(self, data):
        """Update the report table with data."""
        if not data:
            self.view.report_table.setRowCount(0)
            return

        # Set up table
        headers = list(data[0].keys())
        self.view.report_table.setColumnCount(len(headers))
        self.view.report_table.setHorizontalHeaderLabels(headers)
        self.view.report_table.setRowCount(len(data))

        # Fill data
        for row, record in enumerate(data):
            for col, (key, value) in enumerate(record.items()):
                self.view.report_table.setItem(row, col, QTableWidgetItem(str(value)))
