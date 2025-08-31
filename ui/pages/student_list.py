"""Student list page UI implementation with complete database integration and export functionality."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QTableWidget, QFrame,
                           QMessageBox, QTableWidgetItem, QHeaderView, QLineEdit,
                           QGridLayout, QFileDialog, QSizePolicy)
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
        self.organization_combo = None
        self.province_combo = None
        self.district_combo = None
        self.union_council_combo = None
        self.nationality_combo = None
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
        """Create enhanced filter section with 3x3 grid layout including all filters."""
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
        
        # Create 3x3 grid layout for enhanced filters and search
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)
        filter_grid.setColumnStretch(0, 1)  # Equal column widths
        filter_grid.setColumnStretch(1, 1)
        
        styles = get_attendance_styles()
        
        # Create filter widgets - Basic 2x2 layout: School, Class, Section, Search
        self.school_combo = QComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        self.school_combo.setStyleSheet(styles['combobox_standard'])
        
        self.class_combo = QComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        self.class_combo.setStyleSheet(styles['combobox_standard'])
        
        self.section_combo = QComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        self.section_combo.setStyleSheet(styles['combobox_standard'])
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, phone...")
        self.search_input.setStyleSheet(styles['search_input'])
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)          # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)           # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)         # Row 2, Col 1
        filter_grid.addWidget(self.search_input, 1, 1)          # Row 2, Col 2
        filters_layout.addLayout(filter_grid)
        
        return filters_frame

    def _create_export_section(self):
        """Create export button section."""
        export_layout = QHBoxLayout()
        
        # Table information label - shows total records and filter status
        self.table_info_label = QLabel("Total: 0 records")
        self.table_info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray_600']};
                font-size: 14px;
                font-weight: 500;
                padding: 8px 15px;
                background: {COLORS['gray_100']};
                border-radius: 6px;
                border: 1px solid {COLORS['gray_200']};
                min-width: 700px;

            }}
        """)
        # Set size policy to expand horizontally
        self.table_info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Export button with modern styling
        self.export_btn = QPushButton("Export to Excel")
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
        
        export_layout.addWidget(self.table_info_label, 1)  # Add stretch factor to expand
        export_layout.addSpacing(10)  # Add 10px spacing between label and button
        export_layout.addWidget(self.export_btn)
        
        return export_layout

    def _create_table(self):
        """Create the students table with ALL database columns."""
        table = QTableWidget()
        
        # Define ALL non-audit columns with names instead of IDs - complete student information
        self.table_columns = [
            "ID", "Status", "Student ID", "Final Unique Codes",
            "Organization", "School Name", "Province", "District", "Union Council", "Nationality",
            "Registration Number", "Class Teacher Name",
            "Student Name", "Gender", "Date of Birth", "B-Form Number", 
            "Year of Admission", "Year of Admission Alt", "Class", "Section", "Address",
            "Father Name", "Father CNIC", "Father Phone",
            "Household Size",
            "Mother Name", "Mother DOB", "Mother Marital Status", "Mother ID Type", 
            "Mother CNIC", "Mother CNIC DOI", "Mother CNIC Exp", "Mother MWA",
            "Household Role", "Household Name", "HH Gender", "HH DOB", "Recipient Type",
            "Alternate Name", "Alternate DOB", "Alternate Marital Status", "Alternate ID Type",
            "Alternate CNIC", "Alternate CNIC DOI", "Alternate CNIC Exp", "Alternate MWA",
            "Alternate Relationship"
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
        """Load initial data for basic filters from database."""
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
            self._update_table_info()
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
        self._update_table_info()
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
            self._update_table_info()  # Update the info label
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
                
            # Map ALL non-audit database fields with proper name handling - using real names instead of IDs
            row_data = [
                str(student.get("id", "")),
                student.get("status", ""),
                student.get("student_id", ""),
                student.get("final_unique_codes", ""),
                student.get("organization_name", "N/A"),        # Real organization name from JOIN
                student.get("school_name", ""),                 # School name from JOIN
                student.get("province_name", "N/A"),            # Real province name from JOIN
                student.get("district_name", "N/A"),            # Real district name from JOIN
                student.get("union_council_name", "N/A"),       # Real union council name from JOIN
                student.get("nationality_name", "N/A"),         # Real nationality name from JOIN
                student.get("registration_number", ""),
                student.get("class_teacher_name", ""),
                student.get("student_name", ""),
                student.get("gender", ""),
                student.get("date_of_birth", ""),
                student.get("students_bform_number", ""),
                student.get("year_of_admission", ""),
                student.get("year_of_admission_alt", ""),
                student.get("class", ""),
                student.get("section", ""),
                student.get("address", ""),
                student.get("father_name", ""),
                student.get("father_cnic", ""),
                student.get("father_phone", ""),
                str(student.get("household_size", "")),
                student.get("mother_name", ""),
                student.get("mother_date_of_birth", ""),
                student.get("mother_marital_status", ""),
                student.get("mother_id_type", ""),
                student.get("mother_cnic", ""),
                student.get("mother_cnic_doi", ""),
                student.get("mother_cnic_exp", ""),
                str(student.get("mother_mwa", "")),
                student.get("household_role", ""),
                student.get("household_name", ""),
                student.get("hh_gender", ""),
                student.get("hh_date_of_birth", ""),
                student.get("recipient_type", ""),
                student.get("alternate_name", ""),
                student.get("alternate_date_of_birth", ""),
                student.get("alternate_marital_status", ""),
                student.get("alternate_id_type", ""),
                student.get("alternate_cnic", ""),
                student.get("alternate_cnic_doi", ""),
                student.get("alternate_cnic_exp", ""),
                str(student.get("alternate_mwa", "")),
                student.get("alternate_relationship_with_mother", "")
            ]
            
            for col_idx, value in enumerate(row_data):
                if col_idx < len(self.table_columns):  # Safety check
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
                # Use all loaded data - map to ALL non-audit database fields with proper real names
                for student in self.students_data:
                    student_data = {
                        "ID": str(student.get("id", "")),
                        "Status": student.get("status", ""),
                        "Student ID": student.get("student_id", ""),
                        "Final Unique Codes": student.get("final_unique_codes", ""),
                        "Organization": student.get("organization_name", "N/A"),        # Real organization name
                        "School Name": student.get("school_name", ""),
                        "Province": student.get("province_name", "N/A"),               # Real province name
                        "District": student.get("district_name", "N/A"),               # Real district name
                        "Union Council": student.get("union_council_name", "N/A"),     # Real union council name
                        "Nationality": student.get("nationality_name", "N/A"),         # Real nationality name
                        "Registration Number": student.get("registration_number", ""),
                        "Class Teacher Name": student.get("class_teacher_name", ""),
                        "Student Name": student.get("student_name", ""),
                        "Gender": student.get("gender", ""),
                        "Date of Birth": student.get("date_of_birth", ""),
                        "B-Form Number": student.get("students_bform_number", ""),
                        "Year of Admission": student.get("year_of_admission", ""),
                        "Year of Admission Alt": student.get("year_of_admission_alt", ""),
                        "Class": student.get("class", ""),
                        "Section": student.get("section", ""),
                        "Address": student.get("address", ""),
                        "Father Name": student.get("father_name", ""),
                        "Father CNIC": student.get("father_cnic", ""),
                        "Father Phone": student.get("father_phone", ""),
                        "Household Size": str(student.get("household_size", "")),
                        "Mother Name": student.get("mother_name", ""),
                        "Mother DOB": student.get("mother_date_of_birth", ""),
                        "Mother Marital Status": student.get("mother_marital_status", ""),
                        "Mother ID Type": student.get("mother_id_type", ""),
                        "Mother CNIC": student.get("mother_cnic", ""),
                        "Mother CNIC DOI": student.get("mother_cnic_doi", ""),
                        "Mother CNIC Exp": student.get("mother_cnic_exp", ""),
                        "Mother MWA": str(student.get("mother_mwa", "")),
                        "Household Role": student.get("household_role", ""),
                        "Household Name": student.get("household_name", ""),
                        "HH Gender": student.get("hh_gender", ""),
                        "HH DOB": student.get("hh_date_of_birth", ""),
                        "Recipient Type": student.get("recipient_type", ""),
                        "Alternate Name": student.get("alternate_name", ""),
                        "Alternate DOB": student.get("alternate_date_of_birth", ""),
                        "Alternate Marital Status": student.get("alternate_marital_status", ""),
                        "Alternate ID Type": student.get("alternate_id_type", ""),
                        "Alternate CNIC": student.get("alternate_cnic", ""),
                        "Alternate CNIC DOI": student.get("alternate_cnic_doi", ""),
                        "Alternate CNIC Exp": student.get("alternate_cnic_exp", ""),
                        "Alternate MWA": str(student.get("alternate_mwa", "")),
                        "Alternate Relationship": student.get("alternate_relationship_with_mother", "")
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

    def _update_table_info(self):
        """Update the table information label with current filter status and record count."""
        try:
            # Get current filter values
            current_school = self.school_combo.currentText()
            current_class = self.class_combo.currentText()
            current_section = self.section_combo.currentText()
            current_search = self.search_input.text().strip()
            
            # Count records
            total_records = self.student_table.rowCount()
            
            # Start with base text - always show total records
            info_text = f"Total: {total_records} records"
            
            # Build filter info only when filters are actually applied
            filter_parts = []
            
            # Add filter information only if not default/placeholder values
            if (current_school and 
                current_school not in ["All Schools", "Please Select School"]):
                filter_parts.append(f"School: {current_school}")
            
            if (current_class and 
                current_class not in ["All Classes", "Please Select Class"]):
                filter_parts.append(f"Class: {current_class}")
                
            if (current_section and 
                current_section not in ["All Sections", "Please Select Section"]):
                filter_parts.append(f"Section: {current_section}")
                
            if current_search:
                filter_parts.append(f"Search: '{current_search}'")
            
            # Only add filter info if there are active filters
            if filter_parts:
                filter_text = " | ".join(filter_parts)
                info_text += f" ({filter_text})"
            
            # Update label
            self.table_info_label.setText(info_text)
            
        except Exception as e:
            print(f"Error updating table info: {e}")
            self.table_info_label.setText(f"Total: {self.student_table.rowCount()} records")
