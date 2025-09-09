"""Student list page UI implementation with complete database integration and export functionality."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QTableWidget, QFrame,
                           QMessageBox, QTableWidgetItem, QHeaderView, QLineEdit,
                           QGridLayout, QFileDialog, QSizePolicy, QCheckBox)
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
        self.status_filter_combo = None
        self.export_btn = None
        self.status_combo = None
        self.update_status_btn = None
        self.db = Database()
        self.students_data = []  # Store current students data
        self.selected_students = set()  # Store selected student IDs
        
        # Pagination variables
        self.current_page = 1
        self.records_per_page = 30
        self.total_records = 0
        self.total_pages = 0
        
        # Setup UI
        self._init_ui()
        
        # Wire filters to reload data
        self.school_combo.currentTextChanged.connect(self._on_filters_changed)
        self.class_combo.currentTextChanged.connect(self._on_filters_changed)
        self.section_combo.currentTextChanged.connect(self._on_filters_changed)
        self.status_filter_combo.currentTextChanged.connect(self._on_filters_changed)
        
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
        
        # Create pagination controls
        pagination_layout = self._create_pagination_section()
        main_layout.addLayout(pagination_layout)
        
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
        
        # Create 3x3 grid layout for enhanced filters
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)
        filter_grid.setColumnStretch(0, 1)  # Equal column widths
        filter_grid.setColumnStretch(1, 1)
        
        styles = get_attendance_styles()
        
        # Create filter widgets - Basic 2x2 layout: School, Class, Section, Status
        self.school_combo = QComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        self.school_combo.setStyleSheet(styles['combobox_standard'])
        
        self.class_combo = QComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        self.class_combo.setStyleSheet(styles['combobox_standard'])
        
        self.section_combo = QComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        self.section_combo.setStyleSheet(styles['combobox_standard'])
        
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems([
            "All Status", "Active", "Fail", "Drop", "Duplicate", "Graduated"
        ])
        self.status_filter_combo.setStyleSheet(styles['combobox_standard'])
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)          # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)           # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)         # Row 2, Col 1
        filter_grid.addWidget(self.status_filter_combo, 1, 1)   # Row 2, Col 2
        filters_layout.addLayout(filter_grid)
        
        return filters_frame

    def _create_export_section(self):
        """Create export and status update section."""
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
                min-width: 500px;
            }}
        """)
        # Set size policy to expand horizontally
        self.table_info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Status update combo box
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Select Status", "Active", "Drop", "Duplicate", "Fail", "Graduated"
        ])
        self.status_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['gray_50']};
                border: 2px solid {COLORS['gray_200']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                min-height: 20px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
        """)
        
        # Update Status button
        self.update_status_btn = QPushButton("Update Status")
        self.update_status_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['success']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 36px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: #16A34A;
            }}
            QPushButton:pressed {{
                background: #15803D;
                opacity: 0.9;
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_300']};
                color: {COLORS['gray_500']};
            }}
        """)
        self.update_status_btn.clicked.connect(self._update_selected_status)
        self.update_status_btn.setEnabled(False)  # Initially disabled
        
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
                min-width: 120px;
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
        export_layout.addSpacing(10)
        export_layout.addWidget(self.status_combo)
        export_layout.addSpacing(5)
        export_layout.addWidget(self.update_status_btn)
        export_layout.addSpacing(10)
        export_layout.addWidget(self.export_btn)
        
        return export_layout

    def _create_table(self):
        """Create the students table with ALL database columns and checkboxes."""
        table = QTableWidget()
        
        # Define ALL non-audit columns with names instead of IDs - complete student information
        # Add checkbox column at the beginning
        self.table_columns = [
            "✔ Select All", "ID", "Status", "Student ID", "Final Unique Codes",
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
        
        # Change selection behavior to allow multiple selections
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.MultiSelection)
        
        # Add select all functionality to header
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.sectionClicked.connect(self._on_header_clicked)
        
        # Set specific widths for better display
        table.setColumnWidth(0, 100)  # Select All checkbox
        table.setColumnWidth(1, 80)   # ID
        table.setColumnWidth(2, 80)   # Status
        table.setColumnWidth(3, 120)  # Student ID
        table.setColumnWidth(4, 150)  # Student Name
        table.setColumnWidth(5, 130)  # Father Name
        table.setColumnWidth(6, 130)  # Mother Name
        table.setColumnWidth(7, 60)   # Class
        table.setColumnWidth(8, 60)   # Section
        table.setColumnWidth(9, 110)  # Father Phone
        table.setColumnWidth(10, 110) # Mother Phone
        table.setColumnWidth(11, 70)  # Gender
        table.setColumnWidth(12, 100) # Date of Birth
        
        # Make table responsive
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Store selected student IDs for persistent selection
        self.selected_students = set()
        
        return table

    def _create_pagination_section(self):
        """Create pagination controls section."""
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(10)
        
        # Records info label
        self.records_info_label = QLabel("Showing 0 - 0 of 0 records")
        self.records_info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray_600']};
                font-family: 'Poppins';
                font-size: 13px;
                font-weight: 500;
                padding: 8px 0;
            }}
        """)
        
        # Records per page combo
        records_per_page_layout = QHBoxLayout()
        records_per_page_layout.setSpacing(5)
        
        records_label = QLabel("Records per page:")
        records_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray_600']};
                font-family: 'Poppins';
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        
        self.records_per_page_combo = QComboBox()
        self.records_per_page_combo.addItems(["10", "20", "30", "50", "100"])
        self.records_per_page_combo.setCurrentText("30")  # Default to 30
        self.records_per_page_combo.setStyleSheet(f"""
            QComboBox {{
                background: white;
                color: {COLORS['gray_700']};
                border: 2px solid {COLORS['gray_300']};
                border-radius: 6px;
                padding: 6px 12px;
                font-family: 'Poppins';
                font-size: 13px;
                min-width: 60px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {COLORS['gray_500']};
                margin-right: 6px;
            }}
        """)
        self.records_per_page_combo.currentTextChanged.connect(self._on_records_per_page_changed)
        
        records_per_page_layout.addWidget(records_label)
        records_per_page_layout.addWidget(self.records_per_page_combo)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(5)
        
        # First page button
        self.first_btn = QPushButton("❮❮")
        self.first_btn.setToolTip("First Page")
        self.first_btn.clicked.connect(self._go_to_first_page)
        
        # Previous page button
        self.prev_btn = QPushButton("❮")
        self.prev_btn.setToolTip("Previous Page")
        self.prev_btn.clicked.connect(self._go_to_previous_page)
        
        # Page info label
        self.page_info_label = QLabel("Page 1 of 1")
        self.page_info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray_700']};
                font-family: 'Poppins';
                font-size: 13px;
                font-weight: 600;
                padding: 8px 12px;
                min-width: 80px;
                text-align: center;
            }}
        """)
        
        # Next page button
        self.next_btn = QPushButton("❯")
        self.next_btn.setToolTip("Next Page")
        self.next_btn.clicked.connect(self._go_to_next_page)
        
        # Last page button
        self.last_btn = QPushButton("❯❯")
        self.last_btn.setToolTip("Last Page")
        self.last_btn.clicked.connect(self._go_to_last_page)
        
        # Style navigation buttons
        nav_button_style = f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Poppins';
                font-size: 13px;
                font-weight: 600;
                min-width: 40px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
            QPushButton:pressed {{
                background: {COLORS['primary_dark']};
                opacity: 0.9;
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_300']};
                color: {COLORS['gray_500']};
            }}
        """
        
        for btn in [self.first_btn, self.prev_btn, self.next_btn, self.last_btn]:
            btn.setStyleSheet(nav_button_style)
        
        nav_layout.addWidget(self.first_btn)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_info_label)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.last_btn)
        
        # Add everything to main pagination layout
        pagination_layout.addWidget(self.records_info_label)
        pagination_layout.addStretch()
        pagination_layout.addLayout(records_per_page_layout)
        pagination_layout.addSpacing(20)
        pagination_layout.addLayout(nav_layout)
        
        return pagination_layout

    def _on_header_clicked(self, logical_index):
        """Handle header clicks for Select All functionality."""
        if logical_index == 0:  # First column (Select All)
            self._toggle_select_all()

    def _toggle_select_all(self):
        """Toggle selection of all visible students."""
        # Check if all visible students are currently selected
        visible_student_ids = set()
        for row in range(self.student_table.rowCount()):
            checkbox_widget = self.student_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    # Get student_id from the row data
                    student_id_item = self.student_table.item(row, 3)  # Student ID column
                    if student_id_item:
                        student_id = student_id_item.text()
                        visible_student_ids.add(student_id)
        
        # Check if all visible students are selected
        all_selected = visible_student_ids.issubset(self.selected_students)
        
        if all_selected:
            # Deselect all visible students
            for student_id in visible_student_ids:
                self.selected_students.discard(student_id)
            action = "Deselected"
        else:
            # Select all visible students
            self.selected_students.update(visible_student_ids)
            action = "Selected"
        
        # Update all checkboxes
        for row in range(self.student_table.rowCount()):
            checkbox_widget = self.student_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    student_id_item = self.student_table.item(row, 3)
                    if student_id_item:
                        student_id = student_id_item.text()
                        is_selected = student_id in self.selected_students
                        checkbox.blockSignals(True)  # Prevent signal loops
                        checkbox.setChecked(is_selected)
                        checkbox.blockSignals(False)
                        
                        # Update tick label visibility
                        if hasattr(checkbox, 'tick_label'):
                            if is_selected:
                                checkbox.tick_label.show()
                            else:
                                checkbox.tick_label.hide()
        
        print(f"📋 {action} all {len(visible_student_ids)} visible students")
        self._update_button_states()
        self._update_table_info()

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

    # Pagination methods
    def _on_records_per_page_changed(self):
        """Handle records per page change."""
        self.records_per_page = int(self.records_per_page_combo.currentText())
        self.current_page = 1  # Reset to first page
        self._load_students()

    def _go_to_first_page(self):
        """Go to first page."""
        self.current_page = 1
        self._load_students()

    def _go_to_previous_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_students()

    def _go_to_next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_students()

    def _go_to_last_page(self):
        """Go to last page."""
        self.current_page = self.total_pages
        self._load_students()

    def _update_pagination_controls(self):
        """Update pagination controls state and labels."""
        # Update page info
        self.page_info_label.setText(f"Page {self.current_page} of {self.total_pages}")
        
        # Update records info
        start_record = (self.current_page - 1) * self.records_per_page + 1
        end_record = min(self.current_page * self.records_per_page, self.total_records)
        self.records_info_label.setText(f"Showing {start_record} - {end_record} of {self.total_records} records")
        
        # Enable/disable navigation buttons
        self.first_btn.setEnabled(self.current_page > 1)
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        self.last_btn.setEnabled(self.current_page < self.total_pages)

    def _load_students(self):
        """Load students from database using Database class methods with pagination."""
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
            
            print(f"📋 Loading students with filters: School ID={school_id}, Class={class_name}, Section={section_name}, Status={status_name}")
            
            # First get total count for pagination
            total_result = self.db.get_students(
                school_id=school_id,
                class_name=class_name, 
                section=section_name,
                status=status_name,
                per_page=999999  # Get all for count
            )
            
            all_students = total_result.get('students', [])
            self.total_records = len(all_students)
            self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
            
            # Ensure current page is valid
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            
            # Get paginated students
            start_index = (self.current_page - 1) * self.records_per_page
            end_index = start_index + self.records_per_page
            students = all_students[start_index:end_index]
            
            self.students_data = students  # Store current page for search functionality
            
            self._populate_table(students)
            self._update_table_info()  # Update the info label
            self._update_pagination_controls()  # Update pagination controls
            print(f"📚 Loaded {len(students)} students in student list (Page {self.current_page} of {self.total_pages})")
            
        except Exception as e:
            print(f"❌ Error loading students: {e}")
            self.students_data = []
            self.total_records = 0
            self.total_pages = 1
            self._populate_table([])
            self._update_pagination_controls()

    def _populate_table(self, students):
        """Populate the table with student data from database and checkboxes."""
        from PyQt5.QtWidgets import QCheckBox, QWidget, QHBoxLayout
        from PyQt5.QtCore import Qt
        
        self.student_table.setRowCount(len(students))
        
        for row_idx, student in enumerate(students):
            if not isinstance(student, dict):
                continue
                
            student_id = student.get("student_id", "")
            
            # Create checkbox for selection
            # Create a custom checkbox with visible tick
            checkbox_widget = QWidget()
            checkbox_widget.setFixedSize(22, 22)
            
            # Create checkbox
            checkbox = QCheckBox(checkbox_widget)
            checkbox.setFixedSize(22, 22)
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 3px;
                    border: 2px solid #374151;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background: white;
                    border-color: #374151;
                }
                QCheckBox::indicator:hover {
                    border-color: #374151;
                }
            """)
            
            # Create a label for the tick symbol that will overlay the checkbox
            tick_label = QLabel("✔", checkbox_widget)
            tick_label.setFixedSize(22, 22)
            tick_label.setAlignment(Qt.AlignCenter)
            tick_label.setStyleSheet("""
                QLabel {
                    color: #374151;
                    font-size: 14px;
                    font-weight: 900;
                    font-family: 'Segoe UI Symbol', 'Arial Unicode MS', 'Segoe UI', sans-serif;
                    background: transparent;
                    border: none;
                }
            """)
            tick_label.move(0, 0)  # Position the label on top of checkbox
            
            # Initially hide the tick if not selected
            if student_id in self.selected_students:
                checkbox.setChecked(True)
                tick_label.show()
            else:
                tick_label.hide()
            
            # Store reference to tick label for later use
            checkbox.tick_label = tick_label
            
            # Connect checkbox signal
            checkbox.stateChanged.connect(lambda state, sid=student_id: self._on_checkbox_changed(state, sid))
            
            self.student_table.setCellWidget(row_idx, 0, checkbox_widget)
            
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
            
            # Start from column 1 (skip checkbox column)
            for col_idx, value in enumerate(row_data):
                if col_idx + 1 < len(self.table_columns):  # Safety check
                    item = QTableWidgetItem(str(value))
                    self.student_table.setItem(row_idx, col_idx + 1, item)
        
        # Update button state based on selection
        self._update_button_states()

    def _on_checkbox_changed(self, state, student_id):
        """Handle checkbox state changes for persistent selection."""
        from PyQt5.QtCore import Qt
        
        # Find the checkbox that triggered this
        checkbox = self.sender()
        
        if state == Qt.Checked:
            self.selected_students.add(student_id)
            if hasattr(checkbox, 'tick_label'):
                checkbox.tick_label.show()
            print(f"✅ Selected student: {student_id}")
        else:
            self.selected_students.discard(student_id)
            if hasattr(checkbox, 'tick_label'):
                checkbox.tick_label.hide()
            print(f"❌ Deselected student: {student_id}")
        
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
                QMessageBox.warning(self, "No Selection", "Please select students to update status.")
                return
            
            selected_status = self.status_combo.currentText()
            if selected_status == "Select Status":
                QMessageBox.warning(self, "No Status Selected", "Please select a status to update.")
                return
            
            # Confirm the action
            count = len(self.selected_students)
            student_list = ", ".join(list(self.selected_students)[:5])
            if count > 5:
                student_list += f" and {count - 5} more"
            
            reply = QMessageBox.question(
                self, 
                "Confirm Status Update",
                f"Are you sure you want to update status to '{selected_status}' for {count} student(s)?\n\nStudents: {student_list}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
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
                        QMessageBox.information(
                            self, 
                            "Status Updated",
                            f"Successfully updated status to '{selected_status}' for {count} student(s)."
                        )
                        
                        print(f"✅ Updated status for {count} students to {selected_status}")
                        
                        # Reset status filter combo to "All Status" 
                        self.status_filter_combo.setCurrentText("All Status")
                        
                        # Reset status update combo to "Select Status"
                        self.status_combo.setCurrentText("Select Status")
                        
                        # Clear selection and reload data
                        self.selected_students.clear()
                        self._load_students()
                        self._update_button_states()
                    else:
                        QMessageBox.warning(self, "Update Failed", "Failed to update student status. Please check the logs for details.")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Database Error", f"An error occurred while updating status: {e}")
                    print(f"❌ Database error in status update: {e}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
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
            current_status = self.status_filter_combo.currentText()
            
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
            self.table_info_label.setText(f"Total: {self.student_table.rowCount()} records")
