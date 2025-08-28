"""Attendance controller implementation."""
import logging
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate
from models.database import Database

class AttendanceController:
    """Controller for attendance management operations."""

    def __init__(self, view):
        self.view = view
        self.db = Database()
        self._connect_signals()

    def _connect_signals(self):
        """Connect controller to view signals."""
        self.view.search_input.textChanged.connect(self.search_students)
        self.view.calendar.selectionChanged.connect(self.update_attendance_display)
        self.view.apply_all_dates.clicked.connect(self.apply_to_all_dates)
        self.view.apply_week.clicked.connect(self.apply_to_current_week)
        self.view.apply_mondays.clicked.connect(self.apply_to_mondays)
        self.view.mark_holiday.clicked.connect(self.mark_holiday)

    def search_students(self):
        """Search for students based on input."""
        try:
            query = self.view.search_input.text().strip()
            
            if not query:
                self.view.search_results.setRowCount(0)
                return
                
            if len(query) < 2:
                return  # Wait for more characters
            
            # Search database
            students = self.db.search_students(query)
            
            # Update results table
            self.view.search_results.setRowCount(len(students))
            for row, student in enumerate(students):
                self.view.search_results.setItem(row, 0, QTableWidgetItem(student["S#"]))
                self.view.search_results.setItem(row, 1, QTableWidgetItem(student["Name"]))

        except Exception as e:
            logging.error(f"Error searching students: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def update_attendance_display(self):
        """Update attendance display for selected student and date."""
        try:
            student = self.view.get_selected_student()
            if not student:
                return

            date = self.view.get_selected_date()
            attendance = self.db.get_attendance(
                student["s_no"],
                date.month(),
                date.year()
            )

            # Update attendance table
            self.view.attendance_table.setRowCount(len(attendance))
            for row, (date, status) in enumerate(attendance):
                self.view.attendance_table.setItem(row, 0, QTableWidgetItem(date))
                self.view.attendance_table.setItem(row, 1, QTableWidgetItem(status))

        except Exception as e:
            logging.error(f"Error updating attendance display: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def apply_to_all_dates(self):
        """Apply selected status to all dates in the month."""
        try:
            student = self.view.get_selected_student()
            if not student:
                QMessageBox.warning(self.view, "Warning", "Please select a student!")
                return

            status = self.view.get_selected_status()
            date = self.view.get_selected_date()
            
            # Apply status to all dates in the month
            for day in range(1, date.daysInMonth() + 1):
                current_date = QDate(date.year(), date.month(), day)
                self.db.set_attendance(
                    student["s_no"],
                    current_date.toString(Qt.ISODate),
                    status
                )

            self.update_attendance_display()
            QMessageBox.information(self.view, "Success", "Attendance updated for all dates!")

        except Exception as e:
            logging.error(f"Error applying attendance to all dates: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def apply_to_current_week(self):
        """Apply selected status to current week."""
        try:
            student = self.view.get_selected_student()
            if not student:
                QMessageBox.warning(self.view, "Warning", "Please select a student!")
                return

            status = self.view.get_selected_status()
            date = self.view.get_selected_date()
            
            # Get start of week
            start_date = date.addDays(-date.dayOfWeek() + 1)
            
            # Apply status to week
            for i in range(7):
                current_date = start_date.addDays(i)
                self.db.set_attendance(
                    student["s_no"],
                    current_date.toString(Qt.ISODate),
                    status
                )

            self.update_attendance_display()
            QMessageBox.information(self.view, "Success", "Attendance updated for the week!")

        except Exception as e:
            logging.error(f"Error applying attendance to week: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def apply_to_mondays(self):
        """Apply selected status to all Mondays in the month."""
        try:
            student = self.view.get_selected_student()
            if not student:
                QMessageBox.warning(self.view, "Warning", "Please select a student!")
                return

            status = self.view.get_selected_status()
            date = self.view.get_selected_date()
            
            # Apply status to all Mondays
            for day in range(1, date.daysInMonth() + 1):
                current_date = QDate(date.year(), date.month(), day)
                if current_date.dayOfWeek() == 1:  # Monday
                    self.db.set_attendance(
                        student["s_no"],
                        current_date.toString(Qt.ISODate),
                        status
                    )

            self.update_attendance_display()
            QMessageBox.information(self.view, "Success", "Attendance updated for all Mondays!")

        except Exception as e:
            logging.error(f"Error applying attendance to Mondays: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def mark_holiday(self):
        """Mark selected date as holiday for all students."""
        try:
            date = self.view.get_selected_date()
            
            reply = QMessageBox.question(
                self.view,
                "Confirm Holiday",
                f"Mark {date.toString()} as holiday for all students?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Get all students and mark holiday
                students = self.db.get_all_students()
                for student in students:
                    self.db.set_attendance(
                        student["S#"],
                        date.toString(Qt.ISODate),
                        "Holiday"
                    )
                
                self.update_attendance_display()
                QMessageBox.information(self.view, "Success", "Holiday marked successfully!")

        except Exception as e:
            logging.error(f"Error marking holiday: {e}")
            QMessageBox.critical(self.view, "Error", str(e))
