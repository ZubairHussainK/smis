"""Student list page UI implementation with complete database integration and export functionality."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QTableWidget, QFrame,
                           QMessageBox, QTableWidgetItem, QHeaderView, QLineEdit,
                           QGridLayout, QFileDialog)
from PyQt5.QtCore import Qt
from models.database import Database
from ui.styles.table_styles import apply_standard_table_style
from resources.style import COLORS, SPACING_MD, get_attendance_styles
import csv
import os
from datetime import datetime

class StudentListPage(QWidget):
    """Modern student list page with database integration and export functionality."""

    def __init__(self):
        super().__init__()
        # Initialize member variables
        self.student_table = None
        self.school_combo = None
        self.class_combo = None
        self.section_combo = None
        self.search_input = None
        self.export_btn = None
        self.db = Database()
        self.students_data = []  # Store current students data
        
        # Setup UI
        self._init_ui()
        
        # Wire filters to reload data
        self.school_combo.currentTextChanged.connect(self._on_filters_changed)
        self.class_combo.currentTextChanged.connect(self._on_filters_changed)
        self.section_combo.currentTextChanged.connect(self._on_filters_changed)
        self.search_input.textChanged.connect(self._on_search_changed)
        
        # Load initial data
        self._load_initial_data()
        
        # Initial load
        self._load_students()

    def _init_ui(self):
        """Initialize the modern student list page UI components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Create modern filter section (2x2 grid like attendance)
        filter_frame = self._create_filter_section()
        main_layout.addWidget(filter_frame)
        
        # Create export button section
        export_section = self._create_export_section()
        main_layout.addLayout(export_section)
        
        # Create table with all database headers
        self.student_table = self._create_table()
        main_layout.addWidget(self.student_table)
        
        self.setLayout(main_layout)

    def _create_filter_section(self):
        """Create modern filter section with 2x2 grid layout including search."""
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
        self.school_combo = QComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        self.school_combo.setStyleSheet(styles['combobox_standard'])
        
        # Row 1, Column 2: Class filter (with placeholder)
        self.class_combo = QComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        self.class_combo.setStyleSheet(styles['combobox_standard'])
        
        # Row 2, Column 1: Section filter (with placeholder)
        self.section_combo = QComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        self.section_combo.setStyleSheet(styles['combobox_standard'])
        
        # Row 2, Column 2: Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, phone...")
        self.search_input.setStyleSheet(styles['search_input'])
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)    # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)     # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)   # Row 2, Col 1
        filter_grid.addWidget(self.search_input, 1, 1)    # Row 2, Col 2
        
        filters_layout.addLayout(filter_grid)
        
        return filters_frame

    def _create_export_section(self):
        """Create export button section."""
        export_layout = QHBoxLayout()
        
        # Export button with modern styling
        self.export_btn = QPushButton("📊 Export to Excel")
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
            QPushButton:pressed {{
                background: {COLORS['primary_dark']};
                opacity: 0.9;
            }}
        """)
        self.export_btn.clicked.connect(self._export_data)
        
        export_layout.addStretch()
        export_layout.addWidget(self.export_btn)
        
        return export_layout

    def _create_table(self):
        """Create the students table with ALL database columns."""
        table = QTableWidget()
        
        # Define ALL columns from database schema - complete student information
        self.table_columns = [
            "🆔 Student ID", "👤 Student Name", "👨‍👦 Father Name", "� Mother Name", 
            "�📚 Class", "📝 Section", "📞 Father Phone", "� Mother Phone",
            "⚥ Gender", "🎂 Date of Birth", "🏠 Address", "📋 Registration No",
            "📄 B-Form No", "🪪 Father CNIC", "🪪 Mother CNIC", "� Household Size",
            "�📅 Admission Year", "👩‍🏫 Class Teacher", "🏫 School ID", "🏫 School Name",
            "📊 Status", "📝 Remarks", "💰 Fee Status", "📞 Emergency Contact",
            "� Medical Info", "🚌 Transport", "� Previous School", "🎯 Academic Performance",
            "🏆 Extra Activities", "� Created At", "📅 Updated At"
        ]
        
        table.setColumnCount(len(self.table_columns))
        table.setHorizontalHeaderLabels(self.table_columns)
        
        # Apply standard table styling
        apply_standard_table_style(table)
        
        # Set optimal column widths
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        
        # Set specific widths for better display
        table.setColumnWidth(0, 80)   # Student ID
        table.setColumnWidth(1, 150)  # Student Name
        table.setColumnWidth(2, 130)  # Father Name
        table.setColumnWidth(3, 130)  # Mother Name
        table.setColumnWidth(4, 60)   # Class
        table.setColumnWidth(5, 60)   # Section
        table.setColumnWidth(6, 110)  # Father Phone
        table.setColumnWidth(7, 110)  # Mother Phone
        table.setColumnWidth(8, 70)   # Gender
        table.setColumnWidth(9, 100)  # Date of Birth
        
        # Make table responsive
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        return table

    def _load_initial_data(self):
        """Load initial data for filters from database."""
        try:
            # Load schools
            schools = self.db.get_schools()
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_combo.addItem(school_name, school_id)
            print(f"📚 Loaded {len(schools)} schools in student list")
            
            # Load classes
            classes = self.db.get_classes()
            for class_name in classes:
                self.class_combo.addItem(class_name)
            print(f"📚 Loaded {len(classes)} classes in student list")
            
            # Load sections
            sections = self.db.get_sections()
            for section_name in sections:
                self.section_combo.addItem(section_name)
            print(f"📚 Loaded {len(sections)} sections in student list")
            
        except Exception as e:
            print(f"❌ Error loading initial data: {e}")

    def _on_filters_changed(self):
        """Handle filter changes and reload data."""
        self._load_students()

    def _on_search_changed(self, text):
        """Handle search input changes - filter current data."""
        if not text.strip():
            self._populate_table(self.students_data)
            return
        
        # Filter students based on search text
        filtered_students = []
        search_text = text.lower()
        
        for student in self.students_data:
            if (search_text in str(student.get("student_name", "")).lower() or 
                search_text in str(student.get("student_id", "")).lower() or
                search_text in str(student.get("father_name", "")).lower() or
                search_text in str(student.get("mother_name", "")).lower() or
                search_text in str(student.get("father_phone", "")).lower() or
                search_text in str(student.get("mother_phone", "")).lower() or
                search_text in str(student.get("registration_number", "")).lower()):
                filtered_students.append(student)
        
        self._populate_table(filtered_students)
        print(f"🔍 Search: '{text}' - Found {len(filtered_students)} students")

    def _load_students(self):
        """Load students from database using Database class methods."""
        try:
            # Get filter parameters
            school_filter = self.school_combo.currentText()
            class_filter = self.class_combo.currentText()
            section_filter = self.section_combo.currentText()
            
            # Convert filter values for database query
            school_id = None
            if school_filter not in ["Please Select School"]:
                current_index = self.school_combo.currentIndex()
                school_id = self.school_combo.itemData(current_index)
            
            class_name = None if class_filter == "Please Select Class" else class_filter
            section_name = None if section_filter == "Please Select Section" else section_filter
            
            print(f"📋 Loading students with filters: School ID={school_id}, Class={class_name}, Section={section_name}")
            
            # Use Database class method to get students
            result = self.db.get_students(
                school_id=school_id,
                class_name=class_name, 
                section=section_name,
                per_page=1000  # Get all students
            )
            
            students = result.get('students', [])
            self.students_data = students  # Store for search functionality
            
            self._populate_table(students)
            print(f"📚 Loaded {len(students)} students in student list")
            
        except Exception as e:
            print(f"❌ Error loading students: {e}")
            self.students_data = []
            self._populate_table([])

    def _populate_table(self, students):
        """Populate the table with student data from database."""
        self.student_table.setRowCount(len(students))
        
        for row_idx, student in enumerate(students):
            if not isinstance(student, dict):
                continue
                
            # Map ALL database fields to table columns - comprehensive data
            row_data = [
                student.get("student_id", ""),
                student.get("student_name", ""),
                student.get("father_name", ""),
                student.get("mother_name", ""),
                student.get("class", ""),  # Use 'class' field from database
                student.get("section", ""),
                student.get("father_phone", ""),
                student.get("mother_phone", ""),
                student.get("gender", ""),
                student.get("date_of_birth", ""),
                student.get("address", ""),
                student.get("registration_number", ""),
                student.get("students_bform_number", ""),
                student.get("father_cnic", ""),
                student.get("mother_cnic", ""),
                str(student.get("household_size", "")),
                str(student.get("year_of_admission", "")),
                student.get("class_teacher_name", ""),
                str(student.get("School_ID", "")),  # From database result
                student.get("school_name", ""),
                student.get("status", ""),
                student.get("remarks", ""),
                student.get("fee_status", ""),
                student.get("emergency_contact", ""),
                student.get("medical_info", ""),
                student.get("transport", ""),
                student.get("previous_school", ""),
                student.get("academic_performance", ""),
                student.get("extra_activities", ""),
                student.get("created_at", ""),
                student.get("updated_at", "")
            ]
            
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.student_table.setItem(row_idx, col_idx, item)

    def _export_data(self):
        """Export current table data (filtered or all) to Excel/CSV."""
        try:
            # Get current displayed data
            current_students = []
            
            # Check if search is active
            search_text = self.search_input.text().strip()
            if search_text:
                # Use filtered data
                for row in range(self.student_table.rowCount()):
                    student_data = {}
                    for col in range(self.student_table.columnCount()):
                        item = self.student_table.item(row, col)
                        header = self.table_columns[col]
                        student_data[header] = item.text() if item else ""
                    current_students.append(student_data)
            else:
                # Use all loaded data
                for student in self.students_data:
                    student_data = {
                        "🆔 Student ID": student.get("student_id", ""),
                        "👤 Student Name": student.get("student_name", ""),
                        "👨‍👦 Father Name": student.get("father_name", ""),
                        "👩 Mother Name": student.get("mother_name", ""),
                        "📚 Class": student.get("class", ""),
                        "📝 Section": student.get("section", ""),
                        "📞 Father Phone": student.get("father_phone", ""),
                        "📱 Mother Phone": student.get("mother_phone", ""),
                        "⚥ Gender": student.get("gender", ""),
                        "🎂 Date of Birth": student.get("date_of_birth", ""),
                        "🏠 Address": student.get("address", ""),
                        "📋 Registration No": student.get("registration_number", ""),
                        "📄 B-Form No": student.get("students_bform_number", ""),
                        "🪪 Father CNIC": student.get("father_cnic", ""),
                        "🪪 Mother CNIC": student.get("mother_cnic", ""),
                        "👥 Household Size": str(student.get("household_size", "")),
                        "📅 Admission Year": str(student.get("year_of_admission", "")),
                        "👩‍🏫 Class Teacher": student.get("class_teacher_name", ""),
                        "🏫 School ID": str(student.get("School_ID", "")),
                        "🏫 School Name": student.get("school_name", ""),
                        "📊 Status": student.get("status", ""),
                        "📝 Remarks": student.get("remarks", ""),
                        "💰 Fee Status": student.get("fee_status", ""),
                        "📞 Emergency Contact": student.get("emergency_contact", ""),
                        "🩺 Medical Info": student.get("medical_info", ""),
                        "🚌 Transport": student.get("transport", ""),
                        "📚 Previous School": student.get("previous_school", ""),
                        "🎯 Academic Performance": student.get("academic_performance", ""),
                        "🏆 Extra Activities": student.get("extra_activities", ""),
                        "📅 Created At": student.get("created_at", ""),
                        "📅 Updated At": student.get("updated_at", "")
                    }
                    current_students.append(student_data)
            
            if not current_students:
                QMessageBox.information(self, "Export", "No data to export!")
                return
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filter_info = ""
            
            # Add filter info to filename
            school_filter = self.school_combo.currentText()
            class_filter = self.class_combo.currentText()
            section_filter = self.section_combo.currentText()
            
            if school_filter != "Please Select School":
                filter_info += f"_{school_filter}"
            if class_filter != "Please Select Class":
                filter_info += f"_Class{class_filter}"
            if section_filter != "Please Select Section":
                filter_info += f"_Sec{section_filter}"
            if search_text:
                filter_info += f"_Search"
            
            default_filename = f"SMIS_Students{filter_info}_{timestamp}.csv"
            
            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Students Data",
                default_filename,
                "CSV Files (*.csv);;Excel Files (*.xlsx)"
            )
            
            if file_path:
                # Export to CSV
                if file_path.endswith('.csv'):
                    self._export_to_csv(current_students, file_path)
                else:
                    self._export_to_csv(current_students, file_path)  # Default to CSV
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Successfully exported {len(current_students)} student records to:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")

    def _export_to_csv(self, students_data, file_path):
        """Export students data to CSV file."""
        if not students_data:
            return
            
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = students_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for student in students_data:
                writer.writerow(student)

    def refresh_data(self):
        """Refresh the page data."""
        self._load_students()

    def get_current_filters(self):
        """Get current filter settings."""
        return {
            'school': self.school_combo.currentText(),
            'class': self.class_combo.currentText(),
            'section': self.section_combo.currentText(),
            'search': self.search_input.text()
        }

    def reset_filters(self):
        """Reset all filters to default state."""
        self.school_combo.setCurrentIndex(0)
        self.class_combo.setCurrentIndex(0)
        self.section_combo.setCurrentIndex(0)
        self.search_input.clear()
        self._load_students()

    def get_total_students_count(self):
        """Get total number of currently displayed students."""
        return self.student_table.rowCount()
