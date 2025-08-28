"""Student management controller implementation."""
import logging
from PyQt5.QtWidgets import QMessageBox
from models.database import Database
from ui.pages.student import StudentPage
from ui.pages.student_list import StudentListPage

class StudentController:
    """Controller for managing student operations."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.db = Database()
        
        # Create views
        self.student_page = StudentPage()
        self.student_list_page = StudentListPage()
        
        # Connect signals
        self._connect_signals()
        
        # Initial data load
        self.refresh_data()

    def _connect_signals(self):
        """Connect all signals for student management."""
        # Student List Page signals
        self.student_list_page.view_btn.clicked.connect(self._view_student)
        self.student_list_page.edit_btn.clicked.connect(self._edit_student)
        self.student_list_page.delete_btn.clicked.connect(self._delete_student)
        
        # Filter change signals
        self.student_list_page.school_combo.currentTextChanged.connect(self._apply_filters)
        self.student_list_page.class_combo.currentTextChanged.connect(self._apply_filters)
        self.student_list_page.section_combo.currentTextChanged.connect(self._apply_filters)
        
        # Student Page signals
        self.student_page.save_btn.clicked.connect(self._save_student)
        self.student_page.cancel_btn.clicked.connect(self._cancel_student)

    def refresh_data(self):
        """Refresh the student list data."""
        try:
            # Clear existing data
            self.student_list_page.clear_table()
            
            # Get filter values
            filters = self.student_list_page.get_filters()
            
            # Get filtered students from database
            students = self.db.get_students(
                school=filters["school"] if filters["school"] != "All Schools" else None,
                class_name=filters["class"] if filters["class"] != "All Classes" else None,
                section=filters["section"] if filters["section"] != "All Sections" else None
            )
            
            # Add students to table
            for student in students:
                self.student_list_page.add_student_to_table(student)
                
        except Exception as e:
            logging.error(f"Error refreshing student data: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to load student data: {e}")

    def _apply_filters(self):
        """Apply the current filters and refresh the data."""
        self.refresh_data()

    def _view_student(self):
        """View the selected student details."""
        student = self.student_list_page.get_selected_student()
        if student:
            # Show student details in read-only mode
            self.student_page.set_data(student)
            self.student_page.set_readonly(True)
            self.main_window.show_page(self.student_page)

    def _edit_student(self):
        """Edit the selected student."""
        student = self.student_list_page.get_selected_student()
        if student:
            # Show student details in edit mode
            self.student_page.set_data(student)
            self.student_page.set_readonly(False)
            self.main_window.show_page(self.student_page)

    def save_student(self):
        """Save or update student data."""
        try:
            data = self.view.get_form_data()

            # Validate required fields
            if not data["S#"]:
                QMessageBox.warning(self.view, "Error", "S# is required!")
                return
            if not data["Name"]:
                QMessageBox.warning(self.view, "Error", "Name is required!")
                return

            # Save to database
            if self.db.student_exists(data["S#"]):
                self.db.update_student(data)
                msg = "Student updated successfully!"
            else:
                self.db.save_student(data)
                msg = "Student added successfully!"

            QMessageBox.information(self.view, "Success", msg)
            self.refresh_data()
            self.view.hide_form()

        except Exception as e:
            logging.error(f"Error saving student: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def refresh_data(self):
        """Refresh the student table and filters."""
        try:
            self.view.progress_bar.setVisible(True)
            self.view.progress_bar.setValue(0)

            # Get all students and update filters
            students = self.db.get_all_students()
            
            # Update filter options
            schools = sorted(list(set(s["School Name"] for s in students if s["School Name"])))
            classes = sorted(list(set(s["Class 2025"] for s in students if s["Class 2025"])))
            sections = sorted(list(set(s["Section"] for s in students if s["Section"])))

            # Update filter comboboxes
            self.view.school_filter.clear()
            self.view.class_filter.clear()
            self.view.section_filter.clear()
            
            self.view.school_filter.addItems(["All"] + schools)
            self.view.class_filter.addItems(["All"] + classes)
            self.view.section_filter.addItems(["All"] + sections)

            # Apply filters
            self.apply_filters()
            
            self.view.progress_bar.setVisible(False)

        except Exception as e:
            logging.error(f"Error refreshing data: {e}")
            self.view.progress_bar.setVisible(False)
            QMessageBox.critical(self.view, "Error", str(e))

    def apply_filters(self):
        """Apply current filters to the student table."""
        try:
            school = self.view.school_filter.currentText()
            class_name = self.view.class_filter.currentText()
            section = self.view.section_filter.currentText()

            # Get filtered students
            filters = {}
            if school != "All":
                filters["School Name"] = school
            if class_name != "All":
                filters["Class 2025"] = class_name
            if section != "All":
                filters["Section"] = section

            students = self.db.get_filtered_students(filters)

            # Update table
            self.view.student_table.setRowCount(len(students))
            for row, student in enumerate(students):
                for col, value in enumerate(student.values()):
                    self.view.student_table.setItem(row, col, QTableWidgetItem(str(value)))

        except Exception as e:
            logging.error(f"Error applying filters: {e}")
            QMessageBox.critical(self.view, "Error", str(e))

    def on_selection_change(self):
        """Handle student selection changes."""
        self.view.edit_btn.setEnabled(len(self.view.student_table.selectedItems()) > 0)
