"""Student list page UI implementation with complete database integration and export functionality."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame,
                           QMessageBox, QTableWidgetItem, QHeaderView, QLineEdit,
                           QGridLayout, QFileDialog, QSizePolicy, QCheckBox,
                           QAbstractItemView)
from ui.components.custom_table import SMISTable
from ui.components.custom_combo_box import CustomComboBox
from PyQt5.QtCore import Qt
from models.database import Database
# No need to import apply_standard_table_style as we're using SMISTable
from resources.styles import COLORS, SPACING_MD, get_attendance_styles, get_global_styles, get_modern_widget_styles
from resources.styles.messages import (
    show_info_message, show_warning_message, show_error_message, 
    show_critical_message, show_success_message, show_confirmation_message, 
    show_delete_confirmation
)
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
        self.status_filter_combo = None
        self.export_btn = None
        self.status_combo = None
        self.update_status_btn = None
        self.db = Database()
        self.students_data = []  # Store current students data
        self.selected_students = set()  # Store selected student IDs
        
        # Setup UI
        self._init_ui()
        
        # Wire filters to reload data
        self.school_combo.currentTextChanged.connect(self._on_filters_changed)
        self.class_combo.currentTextChanged.connect(self._on_filters_changed)
        self.section_combo.currentTextChanged.connect(self._on_filters_changed)
        self.status_filter_combo.currentTextChanged.connect(self._on_filters_changed)
        # Search input connection is already added in _create_filter_section
        
        # Load initial data
        self._load_initial_data()
        
        # Initial load
        self._load_students()

    def apply_modern_styles(self):
        """Apply centralized modern styles from theme.py"""
        self.setStyleSheet(get_modern_widget_styles())

    def _init_ui(self):
        """Initialize the modern student list page UI components."""
        # Apply centralized modern styles
        self.apply_modern_styles()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Create modern filter section (2x2 grid like attendance)
        filter_frame = self._create_filter_section()
        main_layout.addWidget(filter_frame)
        
        # Create export button section
        export_section = self._create_export_section()
        main_layout.addLayout(export_section)
        
        table_frame = QFrame()
        #table_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 8px;")
        table_frame_layout = QVBoxLayout(table_frame)
        table_frame_layout.setSpacing(8)

        # Create table with all database headers
        self.student_table = self._create_table()
        table_frame_layout.addWidget(self.student_table)

        main_layout.addWidget(table_frame)
        
        # Pagination is handled by SMISTable, no need for separate pagination controls
        
        self.setLayout(main_layout)

    def _create_filter_section(self):
        """Create enhanced filter section with 3x3 grid layout including all filters."""
        filters_frame = QFrame()
        filters_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 8px;")
        
        filters_layout = QVBoxLayout(filters_frame)
        filters_layout.setSpacing(8)
        
        # Create 3x3 grid layout for enhanced filters
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)
        filter_grid.setColumnStretch(0, 1)  # Equal column widths
        filter_grid.setColumnStretch(1, 1)
        
        styles = get_attendance_styles()
        
        # Create filter widgets - Basic 2x2 layout: School, Class, Section, Status
        self.school_combo = CustomComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        
        self.class_combo = CustomComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        
        self.section_combo = CustomComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        
        self.status_filter_combo = CustomComboBox()
        self.status_filter_combo.addItems([
            "All Status", "Active", "Fail", "Drop", "Duplicate", "Graduated"
        ])
        # CustomComboBox has its own styling
        
        # Add search input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, or phone...")
        self.search_input.textChanged.connect(self._on_filters_changed)
        
        # Add widgets to grid: 3x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)          # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)           # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)         # Row 2, Col 1
        filter_grid.addWidget(self.status_filter_combo, 1, 1)   # Row 2, Col 2
        filter_grid.addWidget(self.search_input, 2, 0, 1, 2)    # Row 3, Col 1-2 (span 2 columns)
        filters_layout.addLayout(filter_grid)
        
        return filters_frame

    def _create_export_section(self):
        """Create export and status update section."""
        export_layout = QHBoxLayout()
        
        # Table information label - shows total records and filter status
        self.table_info_label = QLabel("Total: 0 records")
        # Set size policy to expand horizontally
        self.table_info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Status update combo box
        self.status_combo = CustomComboBox()
        self.status_combo.addItems([
            "Select Status", "Active", "Drop", "Duplicate", "Fail", "Graduated"
        ])
        
        # Update Status button using global styles
        self.update_status_btn = QPushButton("Update Status")
        styles = get_global_styles()
        self.update_status_btn.setStyleSheet(styles['button_success'])
        self.update_status_btn.clicked.connect(self._update_selected_status)
        self.update_status_btn.setEnabled(False)  # Initially disabled
        
        # Export button using global styles
        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.setStyleSheet(styles['button_primary'])
        self.export_btn.clicked.connect(self._export_data)
        
        export_layout.addWidget(self.table_info_label, 1)  # Add stretch factor to expand
        export_layout.addSpacing(10)
        export_layout.addWidget(self.status_combo)
        export_layout.addSpacing(5)
        export_layout.addWidget(self.update_status_btn)
        export_layout.addSpacing(10)
        export_layout.addWidget(self.export_btn)
        
        return export_layout


    def _create_table(self):
        """Create the students table with ALL database columns and checkboxes."""
        table = SMISTable(self)

        # Define ALL non-audit columns with names instead of IDs - complete student information
        self.table_columns = [
            "✔", "ID", "Status", "Student ID", "Final Unique Codes",
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

        # Setup table with checkbox column using SMISTable functionality
        table.setup_with_headers(self.table_columns, checkbox_column=0)
        
        # Set ID column for selection tracking (Student ID is at index 3)
        table.set_id_column(3)
        
        # Selection behavior - SMISTable handles checkbox synchronization
        table.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.table.setSelectionMode(QAbstractItemView.MultiSelection)
        
        # Connect to SMISTable selection changed signal
        table.selectionChanged.connect(self._on_selection_changed)
        
        # Store selected student IDs for persistent selection
        self.selected_students = set()

        return table

    # Pagination section is no longer needed as SMISTable provides built-in pagination



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
        self.current_page = 1  # Reset to first page when filters change
        self._load_students()



    def _load_students(self):
        """Load students from database using Database class methods."""
        try:
            # Get filter parameters
            school_filter = self.school_combo.currentText()
            class_filter = self.class_combo.currentText()
            section_filter = self.section_combo.currentText()
            status_filter = self.status_filter_combo.currentText()
            
            # Convert filter values for database query
            school_id = None
            if school_filter not in ["Please Select School"]:
                current_index = self.school_combo.currentIndex()
                school_id = self.school_combo.itemData(current_index)
            
            class_name = None if class_filter == "Please Select Class" else class_filter
            section_name = None if section_filter == "Please Select Section" else section_filter
            status_name = None if status_filter == "All Status" else status_filter
            
            print(f"Loading students with filters: School ID={school_id}, Class={class_name}, Section={section_name}, Status={status_name}")
            
            # Get all students for the table - SMISTable will handle pagination
            result = self.db.get_students(
                school_id=school_id,
                class_name=class_name, 
                section=section_name,
                status=status_name
            )
            
            students = result.get('students', [])
            
            self.students_data = students  # Store all student data for search functionality
            
            self._populate_table(students)
            print(f"📚 Loaded {len(students)} students in student list")
            
        except Exception as e:
            print(f"❌ Error loading students: {e}")
            self.students_data = []
            self._populate_table([])

    def _populate_table(self, students):
        """Populate the table with student data using SMISTable data loading."""
        # Prepare data for SMISTable
        table_data = []
        
        for student in students:
            if not isinstance(student, dict):
                continue
            
            # Map ALL non-audit database fields with proper name handling - using real names instead of IDs
            # Note: Index 0 is for checkbox (placeholder), data columns start from index 1
            row_data = [
                "",                                             # Index 0: Checkbox placeholder (handled by SMISTable)
                str(student.get("id", "")),                     # Index 1: ID column
                student.get("status", ""),                      # Index 2: Status column  
                student.get("student_id", ""),                  # Index 3: Student ID column
                student.get("final_unique_codes", ""),          # Index 4: Final Unique Codes
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
            
            table_data.append(row_data)
        
        # Load data into SMISTable (it will handle checkboxes automatically)
        self.student_table.load_data(table_data)
        
        # Update button state based on selection
        self._update_button_states()
        
        # Update table info
        self._update_table_info()

    def _on_selection_changed(self, selected_ids):
        """Handle selection changes from SMISTable."""
        # Update our internal selected_students set
        self.selected_students = set(selected_ids)
        
        print(f"📋 Selection changed: {len(selected_ids)} students selected")
        for student_id in selected_ids:
            print(f"✅ Selected student: {student_id}")
        
        # Update button states and table info
        self._update_button_states()
        self._update_table_info()

    def _update_button_states(self):
        """Update button states based on selection."""
        has_selection = len(self.selected_students) > 0
        self.update_status_btn.setEnabled(has_selection)

    def _update_selected_status(self):
        """Update status for selected students."""
        try:
            if not self.selected_students:
                show_warning_message("No Selection", "Please select students to update status.")
                return
            
            selected_status = self.status_combo.currentText()
            if selected_status == "Select Status":
                show_warning_message("No Status Selected", "Please select a status to update.")
                return
            
            # Confirm the action
            count = len(self.selected_students)
            student_list = ", ".join(list(self.selected_students)[:5])
            if count > 5:
                student_list += f" and {count - 5} more"
            
            if show_confirmation_message(
                "Confirm Status Update",
                f"Are you sure you want to update status to '{selected_status}' for {count} student(s)?\n\nStudents: {student_list}"
            ):
                # Update database - pass list of student IDs as expected by the database method
                student_ids_list = list(self.selected_students)
                
                try:
                    # Use the correct method signature with all student IDs at once
                    success = self.db.update_student_status(
                        student_ids=student_ids_list,
                        new_status=selected_status,
                        user_id=1,  # You may want to get this from current user session
                        username="admin",  # You may want to get this from current user session
                        user_phone=None
                    )
                    
                    if success:
                        show_success_message(
                            "Status Updated",
                            f"Successfully updated status to '{selected_status}' for {count} student(s)."
                        )
                        
                        print(f"✅ Updated status for {count} students to {selected_status}")
                        
                        # Store the updated student IDs to maintain selection after reload
                        updated_student_ids = student_ids_list.copy()
                        
                        # Reset status filter combo to "All Status" to show updated records
                        self.status_filter_combo.setCurrentText("All Status")
                        
                        # Reset status update combo to "Select Status"
                        self.status_combo.setCurrentText("Select Status")
                        
                        # Reload data to reflect the status changes
                        self._load_students()
                        
                        # Restore selection for the updated records so user can see what was updated
                        self.student_table.set_selected_rows(updated_student_ids)
                        
                        # Update our internal selection tracking
                        self.selected_students = set(updated_student_ids)
                        
                        # Update button states based on restored selection
                        self._update_button_states()
                    else:
                        show_warning_message("Update Failed", "Failed to update student status. Please check the logs for details.")
                        
                except Exception as e:
                    show_critical_message("Database Error", f"An error occurred while updating status: {e}")
                    print(f"❌ Database error in status update: {e}")
                    
        except Exception as e:
            show_critical_message("Error", f"An unexpected error occurred: {e}")
            print(f"❌ Error in status update: {e}")

    def _export_data(self):
        """Export current table data (filtered or all) to Excel/CSV."""
        try:
            # Get current displayed data
            current_students = []
            
            # Check if search is active
            search_text = self.search_input.text().strip()
            if search_text:
                # Use filtered data
                for row in range(self.student_table.table.rowCount()):
                    student_data = {}
                    for col in range(self.student_table.table.columnCount()):
                        item = self.student_table.table.item(row, col)
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
                show_info_message("Export", "No data to export!")
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
                
                show_success_message("Export Successful", 
                                      f"Successfully exported {len(current_students)} student records to:\n{file_path}")
                
        except Exception as e:
            show_critical_message("Export Error", f"Failed to export data: {e}")

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
        self.status_filter_combo.setCurrentIndex(0)
        self.search_input.clear()
        self._load_students()

    def get_total_students_count(self):
        """Get total number of currently displayed students."""
        return self.student_table.table.rowCount()

    def _update_table_info(self):
        """Update the table information label with current filter status and record count."""
        try:
            # Get current filter values
            current_school = self.school_combo.currentText()
            current_class = self.class_combo.currentText()
            current_section = self.section_combo.currentText()
            current_status = self.status_filter_combo.currentText()
            
            # Count records
            total_records = self.student_table.table.rowCount()
            
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
                
            if (current_status and 
                current_status not in ["All Status"]):
                filter_parts.append(f"Status: {current_status}")
            
            # Only add filter info if there are active filters
            if filter_parts:
                filter_text = " | ".join(filter_parts)
                info_text += f" ({filter_text})"
            
            # Update label
            self.table_info_label.setText(info_text)
            
        except Exception as e:
            print(f"Error updating table info: {e}")
            self.table_info_label.setText(f"Total: {self.student_table.table.rowCount()} records")
