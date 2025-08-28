"""Student list page UI implementation."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QTableWidget, QFrame,
                           QMessageBox, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from models.database import Database
from ui.styles.table_styles import apply_standard_table_style

class StudentListPage(QWidget):
    """Student list page showing filtered student records."""

    def __init__(self):
        super().__init__()
        # Initialize member variables
        self.student_table = None
        self.school_combo = None
        self.class_combo = None
        self.section_combo = None
        self.view_btn = None
        self.edit_btn = None
        self.delete_btn = None
        self.db = Database()
        
        # Setup UI
        self._init_ui()
        
        # Wire filters to reload data
        self.school_combo.currentTextChanged.connect(self._load_students)
        self.class_combo.currentTextChanged.connect(self._load_students)
        self.section_combo.currentTextChanged.connect(self._load_students)
        
        # Initial load
        self._load_students()

    def _init_ui(self):
        """Initialize the student list page UI components."""
        main_layout = QVBoxLayout()
        
        # Create filter section
        filter_layout = self._create_filter_section()
        main_layout.addLayout(filter_layout)
        
        # Create action buttons with functionality
        action_layout = QHBoxLayout()
        self.view_btn = QPushButton("👁️ View Details")
        self.edit_btn = QPushButton("✏️ Edit Student")
        self.delete_btn = QPushButton("🗑️ Delete Student")
        self.add_btn = QPushButton("➕ Add New Student")
        
        self.view_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        
        # Connect button actions
        self.view_btn.clicked.connect(self._view_student)
        self.edit_btn.clicked.connect(self._edit_student)
        self.delete_btn.clicked.connect(self._delete_student)
        self.add_btn.clicked.connect(self._add_student)
        
        action_layout.addWidget(self.add_btn)
        action_layout.addWidget(self.view_btn)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Create table
        self.student_table = self._create_table()
        # Handle double-click to open details
        self.student_table.itemDoubleClicked.connect(self._on_double_click)
        main_layout.addWidget(self.student_table)
        
        self.setLayout(main_layout)

    def _create_filter_section(self):
        """Create the filter section with dropdowns."""
        filter_layout = QHBoxLayout()
        
        # School filter
        school_layout = QVBoxLayout()
        school_label = QLabel("Select School:")
        self.school_combo = QComboBox()
        self.school_combo.addItems(["All Schools", "School 1", "School 2", "School 3"])
        school_layout.addWidget(school_label)
        school_layout.addWidget(self.school_combo)
        filter_layout.addLayout(school_layout)
        
        # Class filter
        class_layout = QVBoxLayout()
        class_label = QLabel("Select Class:")
        self.class_combo = QComboBox()
        self.class_combo.addItems(["All Classes", "Kachi", "Paki", "1", "2", "3", "4", "5"])
        class_layout.addWidget(class_label)
        class_layout.addWidget(self.class_combo)
        filter_layout.addLayout(class_layout)
        
        # Section filter
        section_layout = QVBoxLayout()
        section_label = QLabel("Select Section:")
        self.section_combo = QComboBox()
        self.section_combo.addItems(["All Sections", "A", "B", "C", "D"])
        section_layout.addWidget(section_label)
        section_layout.addWidget(self.section_combo)
        filter_layout.addLayout(section_layout)
        
        filter_layout.addStretch()
        return filter_layout

    def _create_table(self):
        """Create the students table with complete database columns."""
        table = QTableWidget()
        
        # Define columns to show from database
        self.table_columns = [
            "🆔 Student ID", "👤 Student Name", "👨‍👦 Father Name", "📚 Class", "📝 Section",
            "📞 Phone", "⚥ Gender", "🎂 Date of Birth", "🏠 Address", "📋 Registration No",
            "📄 B-Form No", "📅 Admission Year", "👩‍🏫 Class Teacher", "👩 Mother Name", 
            "🪪 Mother CNIC", "👥 Household Size", "📊 Status"
        ]
        
        table.setColumnCount(len(self.table_columns))
        table.setHorizontalHeaderLabels(self.table_columns)
        
        # Apply standard table styling
        apply_standard_table_style(table)
        
        # Enable/disable action buttons based on selection
        table.itemSelectionChanged.connect(self._on_selection_changed)
        return table

    def _load_students(self):
        """Fetch students from the database and populate the table."""
        try:
            # Use direct database connection for complete student data
            import sqlite3
            conn = sqlite3.connect('school.db')
            cursor = conn.cursor()
            
            # Get filter values
            school = self.school_combo.currentText() if self.school_combo else "All Schools"
            class_name = self.class_combo.currentText() if self.class_combo else "All Classes"
            section = self.section_combo.currentText() if self.section_combo else "All Sections"
            
            # Build query with filters (exclude deleted students)
            query = '''
                SELECT 
                    student_id, student_name, father_name, class_name, section,
                    father_phone, gender, date_of_birth, address, registration_number,
                    students_bform_number, year_of_admission, class_teacher_name,
                    mother_name, mother_cnic, household_size, status
                FROM students 
                WHERE (is_deleted = 0 OR is_deleted IS NULL)
            '''
            params = []
            
            # Add filters if not "All"
            if school != "All Schools":
                query += " AND school_id = ?"
                params.append(1)  # Default school ID for now
                
            if class_name != "All Classes":
                query += " AND class_name = ?"
                params.append(class_name)
                
            if section != "All Sections":
                query += " AND section = ?"
                params.append(section)
            
            query += " ORDER BY student_id"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            students = []
            for row in rows:
                student = {
                    "student_id": row[0],
                    "student_name": row[1], 
                    "father_name": row[2],
                    "class_name": row[3],
                    "section": row[4],
                    "father_phone": row[5],
                    "gender": row[6],
                    "date_of_birth": row[7],
                    "address": row[8],
                    "registration_number": row[9],
                    "students_bform_number": row[10],
                    "year_of_admission": row[11],
                    "class_teacher_name": row[12],
                    "mother_name": row[13],
                    "mother_cnic": row[14],
                    "household_size": row[15],
                    "status": row[16]
                }
                students.append(student)
                
            self._populate_table(students)
            print(f"📚 Loaded {len(students)} students in student list")
            
        except Exception as e:
            print(f"Error loading students: {e}")
            self._populate_table([])

    def _populate_table(self, students):
        """Populate the table with student data from database."""
        self.student_table.setRowCount(len(students))
        
        for row_idx, student in enumerate(students):
            if not isinstance(student, dict):
                continue
                
            # Map database fields to table columns
            row_data = [
                student.get("student_id", ""),
                student.get("student_name", ""),
                student.get("father_name", ""),
                student.get("class_name", ""),
                student.get("section", ""),
                student.get("father_phone", ""),
                student.get("gender", ""),
                student.get("date_of_birth", ""),
                student.get("address", ""),
                student.get("registration_number", ""),
                student.get("students_bform_number", ""),
                student.get("year_of_admission", ""),
                student.get("class_teacher_name", ""),
                student.get("mother_name", ""),
                student.get("mother_cnic", ""),
                str(student.get("household_size", "")),
                student.get("status", "")
            ]
            
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.student_table.setItem(row_idx, col_idx, item)

    def _on_selection_changed(self):
        """Enable/disable action buttons based on table selection."""
        has_selection = len(self.student_table.selectedItems()) > 0
        self.view_btn.setEnabled(has_selection)
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def _on_double_click(self, item):
        """Open a details dialog for the selected student."""
        row = item.row()
        
        # Get student details from current row
        def get_val(col_idx):
            cell = self.student_table.item(row, col_idx)
            return cell.text() if cell else ""
            
        details = (
            f"Student ID: {get_val(0)}\n"
            f"Name: {get_val(1)}\n"
            f"Father Name: {get_val(2)}\n"
            f"Class: {get_val(3)}  Section: {get_val(4)}\n"
            f"Phone: {get_val(5)}\n"
            f"Gender: {get_val(6)}\n"
            f"Date of Birth: {get_val(7)}\n"
            f"Address: {get_val(8)}\n"
            f"Registration No: {get_val(9)}\n"
            f"B-Form No: {get_val(10)}\n"
            f"Admission Year: {get_val(11)}\n"
            f"Class Teacher: {get_val(12)}\n"
            f"Mother Name: {get_val(13)}\n"
            f"Mother CNIC: {get_val(14)}\n"
            f"Household Size: {get_val(15)}\n"
            f"Status: {get_val(16)}\n"
        )
        QMessageBox.information(self, "Student Details", details)

    def refresh_data(self):
        """Refresh the page data."""
        self._load_students()

    def get_selected_student(self):
        """Get the currently selected student data."""
        selected_row = self.student_table.currentRow()
        if selected_row >= 0:
            return {
                self.table_columns[col]: self.student_table.item(selected_row, col).text()
                for col in range(self.student_table.columnCount())
                if self.student_table.item(selected_row, col)
            }
        return None
    
    def _view_student(self):
        """View detailed information about selected student."""
        selected_row = self.student_table.currentRow()
        if selected_row >= 0:
            item = self.student_table.item(selected_row, 0)  # Get first column item
            self._on_double_click(item)
    
    def _edit_student(self):
        """Edit the selected student."""
        selected_data = self.get_selected_student()
        if selected_data:
            student_id = selected_data.get("Student ID", "")
            QMessageBox.information(self, "Edit Student", 
                                  f"Edit functionality for student {student_id} will be implemented here.\n"
                                  "This will open the student form with pre-filled data.")
    
    def _delete_student(self):
        """Delete the selected student."""
        selected_data = self.get_selected_student()
        if selected_data:
            student_id = selected_data.get("Student ID", "")
            student_name = selected_data.get("Student Name", "")
            
            reply = QMessageBox.question(self, "Confirm Delete",
                                       f"Are you sure you want to delete student:\n"
                                       f"{student_name} (ID: {student_id})?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                try:
                    import sqlite3
                    conn = sqlite3.connect('school.db')
                    cursor = conn.cursor()
                    
                    # Soft delete - set is_deleted = 1
                    cursor.execute("UPDATE students SET is_deleted = 1 WHERE student_id = ?", (student_id,))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Student Deleted", 
                                          f"Student {student_name} has been deleted successfully.")
                    self._load_students()  # Refresh the list
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete student: {e}")
    
    def _add_student(self):
        """Add a new student."""
        QMessageBox.information(self, "Add Student", 
                              "Add new student functionality will be implemented here.\n"
                              "This will open the student form for new student entry.")
