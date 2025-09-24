"""Student management page UI implementation."""
from turtle import back
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QGridLayout, 
                           QLineEdit, QMessageBox, QHeaderView,
                           QScrollArea, QTableWidgetItem, QSplitter, QTextEdit,
                           QGroupBox, QFormLayout, QCheckBox,
                           QSpinBox, QDialog, QDialogButtonBox,
                           QAbstractItemView, QAbstractScrollArea, QSizePolicy)

import main
from ui.components.custom_combo_box import CustomComboBox
from ui.components.custom_table import SMISTable
from ui.components.custom_date_picker import CustomDateEdit
from ui.components.form_components import FormModel, InputField, FormLabel, create_form_field_with_label
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QRegExpValidator
from models.database import Database
from resources.styles import (
    COLORS, RADIUS, SPACING_SM, FONT_MEDIUM, FONT_REGULAR, FOCUS_BORDER_COLOR,
    get_attendance_styles, get_global_styles, get_modern_widget_styles,
    show_info_message, show_warning_message, show_error_message, show_critical_message,
    show_success_message, show_confirmation_message, show_delete_confirmation
)

class StudentPage(QWidget):
    """Modern Student management page with enhanced features."""
    
    # Signals
    student_added = pyqtSignal(dict)
    student_updated = pyqtSignal(dict)
    student_deleted = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Initialize member variables
        self.student_fields = {}
        self.school_combo = None
        self.class_combo = None
        self.section_combo = None
        self.save_btn = None
        self.close_btn = None
        self._needs_layout_recreation = False
        self.students_table = None
        self.search_input = None
        self.form_frame = None
        self.current_student_id = None
        self.is_editing = False
        self.current_user = None  # Add current user tracking
        
        # Form management variables
        self.form_dialog = None
        self.form_created = False
        
        # Field categories for conditional logic
        self.mother_fields = ['mother_name', 'mother_date_of_birth', 'mother_marital_status', 
                             'mother_id_type', 'mother_cnic', 'mother_cnic_doi', 'mother_cnic_exp', 'mother_mwa']
        self.household_fields = ['household_role', 'household_name', 'hh_gender', 'hh_date_of_birth']
        self.alternate_fields = ['alternate_name', 'alternate_date_of_birth', 'alternate_marital_status',
                                'alternate_id_type', 'alternate_cnic', 'alternate_cnic_doi', 
                                'alternate_cnic_exp', 'alternate_mwa', 'alternate_relationship_with_mother']
        
        # Initialize database
        self.db = Database()
        
        # Setup UI
        self._init_ui()
        self._load_data()
        self._connect_signals()

    def set_current_user(self, user):
        """Set the current user for this page."""
        self.current_user = user

    def apply_modern_styles(self):
        """Apply centralized modern styles from theme.py"""
        self.setStyleSheet(get_modern_widget_styles())
        
        # Apply button styles programmatically after widgets are created
        QTimer.singleShot(100, self._apply_button_styles)
    
    def _apply_button_styles(self):
        """Apply button styles to all buttons programmatically"""
        # Find all buttons and apply appropriate styles
        for button in self.findChildren(QPushButton):
            if hasattr(button, 'property') and button.property("class"):
                # Style is already applied via CSS class
                continue
            else:
                # Apply default button style by refreshing the stylesheet
                button.style().unpolish(button)
                button.style().polish(button)

    def _init_ui(self):
        """Initialize the modern student management UI."""
        # Apply centralized modern styles
        self.apply_modern_styles()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        # Main content with splitter for responsive design
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Student list and filters
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Student form
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (55% left, 45% right - more space for form)
        # Use QTimer to set sizes after widgets are properly created
        QTimer.singleShot(100, lambda: splitter.setSizes([int(splitter.width() * 0.50), int(splitter.width() * 0.50)]))
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        main_layout.addWidget(splitter)
        
        # Initially hide the form
        self.form_frame.setVisible(False)

    def _create_left_panel(self):
        """Create the left panel with filters and student list."""
        left_panel = QFrame()
        
        # Set size policy to expand in both directions
        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        panel_layout = QVBoxLayout(left_panel)
        panel_layout.setContentsMargins(15, 10, 15, 10)
        panel_layout.setSpacing(0)
        
        # Filters section
        filters_frame = QFrame()
        filters_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 8px;")
        
        filters_layout = QVBoxLayout(filters_frame)

        filters_layout.setSpacing(8)
        
        # Create 2x2 grid layout for basic filters and search
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)
        filter_grid.setColumnStretch(0, 1)  # Equal column widths
        filter_grid.setColumnStretch(1, 1)
        
        styles = get_attendance_styles()
        
        # Row 1, Column 1: School filter (with placeholder)
        self.school_combo = CustomComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        self._load_schools_data()  # Load from database
        # CustomComboBox has its own styling
        self.school_combo.currentTextChanged.connect(self._on_school_changed)
        
        # Row 1, Column 2: Class filter (with placeholder)
        self.class_combo = CustomComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        self._load_classes_data()  # Load from database
        # CustomComboBox has its own styling
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        
        # Row 2, Column 1: Section filter (with placeholder)
        self.section_combo = CustomComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        self._load_sections_data()  # Load from database
        # CustomComboBox has its own styling
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        
        # Row 2, Column 2: Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, roll number, or phone...")
        self.search_input.textChanged.connect(self._apply_filters)
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)    # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)     # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)   # Row 2, Col 1
        filter_grid.addWidget(self.search_input, 1, 1)    # Row 2, Col 2
        
        filters_layout.addLayout(filter_grid)
        
        # Students table
        table_group = QGroupBox()
        
        table_layout = QVBoxLayout(table_group)
        
        # Create student table with custom implementation
        self.students_table = SMISTable(self)
        self.students_table.table.setColumnCount(5)
        self.students_table.table.setHorizontalHeaderLabels([
            "Student ID", "Student Name", "Father Name", "Class", "Section"
        ])
        
        # Set row height for comfortable reading
        self.students_table.table.verticalHeader().setDefaultSectionSize(35)
        
        # Auto resize columns for 5 columns only
        header = self.students_table.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Student Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Father Name
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Class
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Section
        
        table_layout.addWidget(self.students_table)
        
        # Table actions
        table_actions = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setProperty("class", "warning")
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setProperty("class", "danger")
        
        self.view_details_btn = QPushButton("View Details")
        self.view_details_btn.setEnabled(False)

        self.add_new_btn = QPushButton("Add Student")
        self.add_new_btn.setProperty("class", "success")

        self.refresh_btn = QPushButton("Refresh")

        table_actions.addWidget(self.edit_btn)
        table_actions.addWidget(self.delete_btn)
        table_actions.addWidget(self.view_details_btn)
        table_actions.addWidget(self.add_new_btn)
        table_actions.addWidget(self.refresh_btn)
        table_actions.addStretch()
        
        table_layout.addLayout(table_actions)
        
        # Add to panel
        panel_layout.addWidget(filters_frame)
        panel_layout.addWidget(table_group, 1)
        
        return left_panel
    
    def _create_right_panel(self):
        """Create the right panel with student form."""
        self.form_frame = QFrame()
        # Set size policy to expand in both directions
        self.form_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return self.form_frame
    
    def _load_data(self):
        """Load student data from database using Database class."""
        try:
            # Get filter parameters
            school_filter = self.school_combo.currentText() if hasattr(self, 'school_combo') else None
            class_filter = self.class_combo.currentText() if hasattr(self, 'class_combo') else None
            section_filter = self.section_combo.currentText() if hasattr(self, 'section_combo') else None
            
            # Convert filter values for database query
            school_id = None
            if school_filter and school_filter != "Please Select School":
                current_index = self.school_combo.currentIndex()
                school_id = self.school_combo.itemData(current_index)
            
            class_name = None if class_filter == "Please Select Class" else class_filter
            section = None if section_filter == "Please Select Section" else section_filter
            
            print(f"Loading students with filters: School ID={school_id}, Class={class_name}, Section={section}")
            
            # Get students using Database class method - only active students
            students_data = self.db.get_students(school_id=school_id, class_name=class_name, section=section, status="Active")
            
            # Convert to format expected by table
            students = []
            # Check if we got paginated results or direct list
            if isinstance(students_data, dict) and 'students' in students_data:
                student_list = students_data['students']
            elif isinstance(students_data, dict) and 'data' in students_data:
                student_list = students_data['data']
            else:
                student_list = students_data if students_data else []
                
            for student in student_list:
                # Handle both dict and sqlite3.Row objects
                if hasattr(student, 'keys'):  # dict-like object
                    student_record = {
                        "id": student.get("student_id", "") if hasattr(student, 'get') else student["student_id"],
                        "name": student.get("student_name", "") if hasattr(student, 'get') else student["student_name"],
                        "father_name": student.get("father_name", "") if hasattr(student, 'get') else student["father_name"],
                        "class": student.get("class", "N/A") if hasattr(student, 'get') else student.get("class", "N/A"),
                        "section": student.get("section", "N/A") if hasattr(student, 'get') else student.get("section", "N/A"),
                        "phone": student.get("father_phone", "N/A") if hasattr(student, 'get') else student.get("father_phone", "N/A"),
                        # Store full student data for editing
                        "_full_data": dict(student) if hasattr(student, 'keys') else student
                    }
                    students.append(student_record)
                else:
                    print(f"Warning: Unexpected student data type: {type(student)}")
            
            self._populate_table(students)
            print(f"📚 Loaded {len(students)} students from database")
            
        except Exception as e:
            print(f"Error loading student data: {e}")
            import traceback
            traceback.print_exc()
            show_warning_message("Data Load Error", f"Failed to load student data: {str(e)}")
            # Fallback to empty table
            self._populate_table([])
    
    def _get_schools_from_database(self):
        """Fetch schools from database for combo box."""
        try:
            schools = self.db.get_schools()
            return schools  # Return the full school objects with id and name
        except Exception as e:
            print(f"Error fetching schools: {e}")
            return []  # Return empty list instead of dummy data
    
    def _get_organizations_from_database(self):
        """Fetch organizations from database for combo box."""
        try:
            # Get organizations from database if exists, or return empty
            organizations = self.db.get_organizations() if hasattr(self.db, 'get_organizations') else []
            return organizations
        except Exception as e:
            print(f"Error fetching organizations: {e}")
            return []  # Return empty list instead of dummy data
    
    def _get_provinces_from_database(self):
        """Fetch provinces from database for combo box."""
        try:
            # Get provinces from database if exists
            provinces = self.db.get_provinces() if hasattr(self.db, 'get_provinces') else []
            if not provinces:
                # Use standard Pakistani provinces as fallback only if no database data
                provinces = ["Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan", "Gilgit-Baltistan", "Azad Kashmir", "Islamabad Capital Territory"]
            return provinces
        except Exception as e:
            print(f"Error fetching provinces: {e}")
            return []  # Return empty list instead of dummy data
    
    def _get_districts_from_database(self):
        """Fetch districts from database for combo box."""
        try:
            # Get districts from database if exists
            districts = self.db.get_districts() if hasattr(self.db, 'get_districts') else []
            return districts
        except Exception as e:
            print(f"Error fetching districts: {e}")
            return []  # Return empty list instead of dummy data
    
    def _get_union_councils_from_database(self):
        """Fetch union councils from database for combo box."""
        try:
            # Get union councils from database if exists
            union_councils = self.db.get_union_councils() if hasattr(self.db, 'get_union_councils') else []
            return union_councils
        except Exception as e:
            print(f"Error fetching union councils: {e}")
            return []  # Return empty list instead of dummy data
    
    def _get_nationalities_from_database(self):
        """Fetch nationalities from database for combo box."""
        try:
            # Get nationalities from database if exists
            nationalities = self.db.get_nationalities() if hasattr(self.db, 'get_nationalities') else []
            if not nationalities:
                # Use standard nationalities as fallback only if no database data
                nationalities = ["Pakistani", "Indian", "Afghan", "Bangladeshi", "Sri Lankan", "Chinese", "American", "British", "Other"]
            return nationalities
        except Exception as e:
            print(f"Error fetching nationalities: {e}")
            return []  # Return empty list instead of dummy data
    
    def _populate_table(self, students):
        """Populate the students table with data and improved styling."""
        self.students_table.table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # Student ID with smaller font
            id_item = QTableWidgetItem(str(student["id"]))  # Keep original ID format
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFont(QFont('Poppins', 8))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.table.setItem(row, 0, id_item)
            
            # Student Name with smaller font
            name_item = QTableWidgetItem(student["name"].title())
            name_item.setFont(QFont('Poppins', 8))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.table.setItem(row, 1, name_item)
            
            # Father Name with smaller font
            father_name_item = QTableWidgetItem(student.get("father_name", "N/A").title())
            father_name_item.setFont(QFont('Poppins', 8))
            father_name_item.setFlags(father_name_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.table.setItem(row, 2, father_name_item)
            
            # Class with smaller font
            class_item = QTableWidgetItem(student["class"])
            class_item.setTextAlignment(Qt.AlignCenter)
            class_item.setFont(QFont('Poppins', 8))
            class_item.setFlags(class_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.table.setItem(row, 3, class_item)
            
            # Section with smaller font
            section_item = QTableWidgetItem(student["section"])
            section_item.setTextAlignment(Qt.AlignCenter)
            section_item.setFont(QFont('Poppins', 8))
            section_item.setFlags(section_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.table.setItem(row, 4, section_item)
    
    def _connect_signals(self):
        """Connect all signals to their handlers."""
        # Header buttons
        self.add_new_btn.clicked.connect(self._show_add_form)
        self.refresh_btn.clicked.connect(self._refresh_data)
        
        # Filter changes - use specific handlers for dropdowns
        self.search_input.textChanged.connect(self._apply_filters)
        self.school_combo.currentTextChanged.connect(self._on_school_changed)
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        
        # Table selection
        self.students_table.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.students_table.table.itemDoubleClicked.connect(self._on_double_click)
        
        # Action buttons
        self.edit_btn.clicked.connect(self._edit_student)
        self.delete_btn.clicked.connect(self._delete_student)
        self.view_details_btn.clicked.connect(self._view_details)
    
    def _show_add_form(self):
        """Show the form for adding a new student."""
        try:
            # Reset editing state
            self.is_editing = False
            self.current_student_id = None
            
            # Close any existing form dialog to prevent crashes
            if hasattr(self, 'form_dialog') and self.form_dialog:
                try:
                    self.form_dialog.close()
                    self.form_dialog.deleteLater()
                except:
                    pass
                self.form_dialog = None
            
            # Check if form_frame exists
            if not hasattr(self, 'form_frame') or not self.form_frame:
                show_critical_message("Error", "Form frame not available.")
                return
            
            # Hide form if already visible and reset
            if self.form_frame.isVisible():
                self.form_frame.setVisible(False)
                self._clear_form_safely()
            
            # Create fresh form using single page layout
            self._show_form("Add Student")
            
            # Show the form
            self.form_frame.setVisible(True)
            
            # For new forms, don't clear fields immediately - let defaults show
            # Field clearing will happen when user clicks Reset button if needed
            
        except Exception as e:
            show_critical_message("Error", f"Failed to open Add Student form:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _clear_form_safely(self):
        """Safely clear form layout and widgets."""
        try:
            if self.form_frame and self.form_frame.layout():
                # Clear widget references
                self.student_fields.clear()
                
                # Remove and delete layout
                layout = self.form_frame.layout()
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                # Remove layout
                self.form_frame.setLayout(None)
                layout.deleteLater()
                
                self.form_created = False
                
        except Exception as e:
            print(f"Error clearing form safely: {e}")
    
    def _cleanup_form_layout(self):
        """Properly cleanup existing form layout and all widgets."""
        try:
            if not self.form_frame:
                return
                
            current_layout = self.form_frame.layout()
            if not current_layout:
                return  # Nothing to cleanup
                
            print("🧹 Starting form layout cleanup...")
            
            # First, hide the form to prevent visual glitches
            self.form_frame.setVisible(False)
            
            # Recursively delete all child widgets and layouts
            def delete_layout_items(layout_item):
                try:
                    if layout_item.layout():
                        # It's a layout - recursively delete its items
                        child_layout = layout_item.layout()
                        while child_layout.count():
                            child_item = child_layout.takeAt(0)
                            if child_item:
                                delete_layout_items(child_item)
                        child_layout.deleteLater()
                    elif layout_item.widget():
                        # It's a widget - delete it
                        widget = layout_item.widget()
                        if widget:
                            # Disconnect all signals from this widget
                            try:
                                widget.blockSignals(True)
                            except:
                                pass
                            widget.setParent(None)
                            widget.deleteLater()
                except Exception as item_error:
                    print(f"Warning: Error deleting layout item: {item_error}")
            
            # Delete all items in the main layout
            while current_layout.count():
                item = current_layout.takeAt(0)
                if item:
                    delete_layout_items(item)
            
            # Clear the layout from widget safely
            try:
                self.form_frame.setLayout(None)
            except Exception as layout_clear_error:
                print(f"Warning: Could not clear layout: {layout_clear_error}")
                # Try alternative approach
                try:
                    # Create a dummy layout and set it, then remove it
                    from PyQt5.QtWidgets import QVBoxLayout
                    dummy_layout = QVBoxLayout()
                    self.form_frame.setLayout(dummy_layout)
                    self.form_frame.setLayout(None)
                    dummy_layout.deleteLater()
                except:
                    print("Could not clear layout with dummy approach either")
            
            # Delete the main layout
            current_layout.deleteLater()
            
            # Force process events to ensure cleanup
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            print("✅ Form layout cleanup completed")
                
        except Exception as e:
            print(f"❌ Error cleaning up form layout: {e}")
            # Force clear layout even if cleanup fails
            try:
                if self.form_frame:
                    self.form_frame.setVisible(False)
                    # Try to clear layout without errors
                    try:
                        if self.form_frame.layout():
                            # Just remove children without setting layout to None
                            layout = self.form_frame.layout()
                            while layout.count():
                                item = layout.takeAt(0)
                                if item and item.widget():
                                    item.widget().deleteLater()
                    except:
                        pass
            except:
                pass
    
    def _validate_form(self):
        """Validate all form fields and show errors."""
        errors = []
        
        # Required fields validation
        required_fields = {
            'student_id': 'Student ID',
            'student_name': 'Student Name', 
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'b_form_number': 'B-Form Number',
            'father_name': "Father's Name",
            'father_cnic': "Father's CNIC",
            'father_phone': "Father's Phone"
        }
        
        for field_name, display_name in required_fields.items():
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                
                if isinstance(widget, QLineEdit):
                    if not widget.text().strip():
                        errors.append(f"{display_name} is required")
                elif isinstance(widget, CustomComboBox):
                    if widget.currentText() in ["Select...", ""]:
                        errors.append(f"{display_name} must be selected")
                elif isinstance(widget, CustomDateEdit):
                    # Basic date validation - should not be future for birth dates
                    if 'birth' in field_name and widget.date() > QDate.currentDate():
                        errors.append(f"{display_name} cannot be in the future")
        
        # CNIC format validation
        if 'father_cnic' in self.student_fields:
            cnic_text = self.student_fields['father_cnic'].text().replace('-', '')
            if cnic_text and len(cnic_text) != 13:
                errors.append("Father's CNIC must be exactly 13 digits")
        
        if 'mother_cnic' in self.student_fields:
            mother_cnic_text = self.student_fields['mother_cnic'].text().replace('-', '')
            if mother_cnic_text and len(mother_cnic_text) != 13:
                errors.append("Mother's CNIC must be exactly 13 digits")
        
        # Phone format validation
        if 'father_phone' in self.student_fields:
            phone_text = self.student_fields['father_phone'].text().replace('-', '')
            if phone_text and (len(phone_text) != 11 or not phone_text.startswith('03')):
                errors.append("Father's Phone must be 11 digits starting with 03")
        
        # Student ID uniqueness check (skip for current student when editing)
        if 'student_id' in self.student_fields:
            student_id = self.student_fields['student_id'].text().strip()
            if student_id and self._check_student_id_exists(student_id):
                # Skip validation if this is the current student being edited
                if not (hasattr(self, 'current_student_id') and self.current_student_id == student_id):
                    errors.append(f"Student ID '{student_id}' already exists")
        
        return errors
    
    def _check_student_id_exists(self, student_id):
        """Check if student ID already exists in database."""
        try:
            existing_student = self.db.get_student_by_id(student_id)
            return existing_student is not None
        except Exception as e:
            print(f"Error checking student ID: {e}")
            return False
    
    def _show_validation_errors(self, errors):
        """Display validation errors to user."""
        if errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            show_warning_message("Form Validation", error_message)
            return False
        return True
    
    def _clear_form_fields(self):
        """Clear all form input fields."""
        try:
            if not hasattr(self, 'student_fields') or not self.student_fields:
                return
                
            for field_name, field_widget in self.student_fields.items():
                try:
                    if field_widget is None:
                        continue
                        
                    if hasattr(field_widget, 'clear'):
                        field_widget.clear()
                    elif hasattr(field_widget, 'setCurrentIndex'):
                        field_widget.setCurrentIndex(0)
                    elif hasattr(field_widget, 'setDate'):
                        # Reset to current date but mark as not user selected
                        field_widget.setDate(QDate.currentDate())
                        if hasattr(field_widget, '_user_selected'):
                            field_widget._user_selected = False
                        if hasattr(field_widget, '_original_date'):
                            field_widget._original_date = QDate.currentDate()
                    elif hasattr(field_widget, 'setValue'):
                        field_widget.setValue(0)
                    elif hasattr(field_widget, 'setChecked'):
                        field_widget.setChecked(False)
                        
                except Exception as field_error:
                    # Skip individual field errors to prevent crash
                    print(f"Warning: Could not clear field {field_name}: {field_error}")
                    continue
                    
        except Exception as e:
            print(f"Error clearing form fields: {e}")
    
    def _create_complete_form(self):
        """Create a complete form using the custom form components on a single page."""
        try:
            # Prevent multiple form creation
            if self.form_created:
                return

            # Create main form layout with better structure
            form_layout = QVBoxLayout()
            form_layout.setContentsMargins(20, 20, 20, 20)
            form_layout.setSpacing(15)
            
            # Create form header
            header_label = FormLabel("Student Information")
            header_label.setProperty("class", "FormHeading")
            
            # Create a form container with scroll capability
            form_container = QScrollArea()
            form_container.setWidgetResizable(True)
            form_container.setFrameShape(QFrame.NoFrame)
            
            form_widget = QWidget()
            form_content_layout = QFormLayout()
            form_content_layout.setSpacing(15)
            form_content_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
            form_content_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            
            # Initialize our form model to store fields and values
            self.form_model = FormModel()
            
            # Combine all fields from the tabs into one form
            # Personal Info Fields
            self._add_personal_info_fields(form_content_layout)
            
            # Academic Info Fields
            self._add_academic_info_fields(form_content_layout)
            
            # Contact Info Fields
            self._add_contact_info_fields(form_content_layout)
            
            # Set the layout to the form widget and add it to scroll area
            form_widget.setLayout(form_content_layout)
            form_container.setWidget(form_widget)
            
            # Form buttons with proper spacing
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(8)  # Better button spacing
            buttons_layout.setContentsMargins(10, 10, 10, 5)  # Proper margins for alignment
            
            # Close button
            close_btn = QPushButton("❌ Close")
            close_btn.setProperty("class", "danger")
            close_btn.clicked.connect(lambda: self.form_frame.setVisible(False))
            
            # Reset button
            reset_btn = QPushButton("🔄 Reset")
            reset_btn.setProperty("class", "warning")
            reset_btn.clicked.connect(self._reset_form)
            
            # Cancel button
            self.close_btn = QPushButton("✖️ Close")
            self.close_btn.clicked.connect(self._close_form)
            
            # Save button
            self.save_btn = QPushButton("💾 Save Student")
            self.save_btn.setProperty("class", "success")
            self.save_btn.clicked.connect(self._save_student)
            
            # Add buttons to layout (Close, Reset, Close, Save)
            buttons_layout.addWidget(close_btn)
            buttons_layout.addStretch()
            buttons_layout.addWidget(reset_btn)
            buttons_layout.addWidget(self.close_btn)
            buttons_layout.addWidget(self.save_btn)
            
            # Add to form layout
            form_layout.addWidget(header_label)
            form_layout.addWidget(form_container, 1)  # Give form container most of the space
            form_layout.addLayout(buttons_layout)
            
            # Set the layout to the form frame
            self.form_frame.setLayout(form_layout)
            
            # Mark form as created
            self.form_created = True
            
        except Exception as e:
            print(f"Error creating complete form: {e}")
            import traceback
            traceback.print_exc()
            self.form_created = False
    
    def _create_simple_form(self):
        """This method is no longer used - keeping for compatibility."""
        pass
    
    def _create_form_content(self):
        """This method is no longer used - keeping for compatibility."""  
        pass
    
    def _close_form_safely(self):
        """This method is no longer used - keeping for compatibility."""
        pass
    
    def _edit_student(self):
        """Edit the selected student."""
        selected_row = self.students_table.table.currentRow()
        if selected_row >= 0:
            try:
                # Get table items for the 5 columns that actually exist
                id_item = self.students_table.table.item(selected_row, 0)
                name_item = self.students_table.table.item(selected_row, 1)
                father_name_item = self.students_table.table.item(selected_row, 2)
                class_item = self.students_table.table.item(selected_row, 3)
                section_item = self.students_table.table.item(selected_row, 4)
                
                # Validate that we can read the essential data
                if not id_item or not name_item:
                    show_warning_message("Error", "Unable to read student data. Please refresh and try again.")
                    return
                
                student_id = id_item.text().strip()
                student_name = name_item.text().strip()
                
                if not student_id:
                    show_warning_message("Error", "Student ID is empty. Cannot edit student.")
                    return
                
                print(f"🔧 Editing student: ID={student_id}, Name={student_name}")
                
                # Get complete student data from database using the student_id
                full_student_data = self.db.get_student_by_id(student_id)
                
                if not full_student_data:
                    show_warning_message("Error", f"Could not find complete data for student ID: {student_id}")
                    return
                
                print(f"Retrieved full student data: {type(full_student_data)}")
                
                # Set editing state
                self.is_editing = True
                self.current_student_id = student_id
                
                # Close any existing form dialog to prevent crashes
                if hasattr(self, 'form_dialog') and self.form_dialog:
                    try:
                        self.form_dialog.close()
                        self.form_dialog.deleteLater()
                    except:
                        pass
                    self.form_dialog = None
                
                # Check if form_frame exists
                if not hasattr(self, 'form_frame') or not self.form_frame:
                    show_critical_message("Error", "Form frame not available.")
                    return
                
                # Hide form if already visible and reset
                if self.form_frame.isVisible():
                    self.form_frame.setVisible(False)
                    self._clear_form_safely()
                
                # Create fresh form using the new system
                self._create_complete_form()
                
                # Show the form
                self.form_frame.setVisible(True)
                
                # Load the complete student data into form
                self._load_student_data(student_id, full_student_data)
                
            except Exception as e:
                show_critical_message("Error", f"Failed to edit student: {str(e)}")
                print(f"❌ Edit error details: {e}")  # Debug output
                import traceback
                traceback.print_exc()
        else:
            show_info_message("No Selection", "Please select a student to edit.")
    
    def _delete_student(self):
        """Delete the selected student."""
        selected_row = self.students_table.table.currentRow()
        if selected_row >= 0:
            try:
                name_item = self.students_table.table.item(selected_row, 1)
                if not name_item:
                    show_warning_message("Error", "Unable to read student data. Please refresh and try again.")
                    return
                    
                student_name = name_item.text()
                
                # Use custom confirmation dialog
                if show_delete_confirmation(self, "Confirm Delete", f"Are you sure you want to delete student '{student_name}'?\n\nThis action cannot be undone."):
                    id_item = self.students_table.table.item(selected_row, 0)
                    if not id_item:
                        show_warning_message("Error", "Unable to read student ID. Please refresh and try again.")
                        return
                        
                    student_id = id_item.text()
                    
                    # Delete from database
                    try:
                        # Get current user information
                        user_id = self.current_user.id if self.current_user else None
                        username = self.current_user.username if self.current_user else None
                        user_phone = getattr(self.current_user, 'phone', None) if self.current_user else None
                        
                        if self.db.delete_student(student_id, user_id, username, user_phone):
                            self.students_table.table.removeRow(selected_row)
                            self.student_deleted.emit(student_id)
                            show_success_message(self, "Success", f"Student '{student_name}' has been deleted.")
                        else:
                            show_warning_message("Error", "Failed to delete student from database.")
                    except Exception as db_error:
                        show_critical_message("Database Error", f"Failed to delete student: {str(db_error)}")
            except Exception as e:
                show_critical_message("Error", f"Failed to delete student: {str(e)}")
        else:
            show_info_message("No Selection", "Please select a student to delete.")
    
    def _view_details(self):
        """View detailed information about the selected student."""
        selected_row = self.students_table.table.currentRow()
        if selected_row >= 0:
            try:
                id_item = self.students_table.table.item(selected_row, 0)
                name_item = self.students_table.table.item(selected_row, 1)
                
                if not all([id_item, name_item]):
                    show_warning_message("Error", "Unable to read student data. Please refresh and try again.")
                    return
                    
                student_id = id_item.text()
                student_name = name_item.text()
                
                # Show detailed student information dialog with history
                self._show_student_details_dialog(student_id, student_name)
            except Exception as e:
                show_critical_message("Error", f"Failed to view student details: {str(e)}")
        else:
            show_info_message("No Selection", "Please select a student to view details.")
    
    def _on_selection_changed(self):
        """Handle table selection changes with improved feedback."""
        has_selection = len(self.students_table.table.selectedItems()) > 0
        current_row = self.students_table.table.currentRow()
        
        # Enable/disable buttons based on selection
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.view_details_btn.setEnabled(has_selection)
        
        # Update button text to show selected student info
        if has_selection and current_row >= 0:
            try:
                student_name = self.students_table.table.item(current_row, 1).text()
                student_id = self.students_table.table.item(current_row, 0).text()

                self.edit_btn.setText(f"Edit {student_name}")
                self.delete_btn.setText(f"Delete {student_name}")
                self.view_details_btn.setText(f"View {student_name}")

                # Highlight the entire row
                for col in range(self.students_table.table.columnCount()):
                    item = self.students_table.table.item(current_row, col)
                    if item:
                        item.setSelected(True)
                        
            except (AttributeError, IndexError):
                # Fallback to default text
                self.edit_btn.setText("Edit Selected")
                self.delete_btn.setText("Delete Selected")
                self.view_details_btn.setText("View Details")
        else:
            # Reset to default text when no selection
            self.edit_btn.setText("Edit Selected")
            self.delete_btn.setText("Delete Selected")
            self.view_details_btn.setText("View Details")

    def _on_double_click(self, item):
        """Handle double-click on table item to show view details."""
        try:
            if item:  # Any column can trigger view details now
                self._view_details()
        except Exception as e:
            show_critical_message("Error", f"Double-click handler error: {str(e)}")
    
    def _show_actions_menu(self, item):
        """Show actions menu for the student row."""
        # For now, just trigger edit action
        self._edit_student()
    
    def _apply_filters(self):
        """Apply search and filter criteria by reloading data."""
        # For search-only filtering, do table-based filtering
        search_text = self.search_input.text().lower().strip()
        
        # If only search is applied, filter the current table
        if search_text and (
            self.school_combo.currentText() == "Please Select School" and
            self.class_combo.currentText() == "Please Select Class" and 
            self.section_combo.currentText() == "Please Select Section"
        ):
            # Apply search filter to current table
            for row in range(self.students_table.table.rowCount()):
                show_row = True
                
                if search_text:
                    row_text = ""
                    for col in range(self.students_table.table.columnCount() - 1):  # Exclude actions column
                        item = self.students_table.table.item(row, col)
                        if item:
                            row_text += item.text().lower() + " "
                    
                    if search_text not in row_text:
                        show_row = False
                
                self.students_table.table.setRowHidden(row, not show_row)
        else:
            # For dropdown filters, reload data from database
            self._load_data()
    
    def _refresh_data(self):
        """Refresh the student data."""
        self._load_data()
        self.search_input.clear()
        self.school_combo.setCurrentIndex(0)
        self.class_combo.setCurrentIndex(0)
        self.section_combo.setCurrentIndex(0)
        #QMessageBox.information(self, "Success", "🔄 Student data refreshed successfully!")
    
    def _load_schools_data(self):
        """Load schools from database and populate school combo."""
        try:
            # Clear existing items except placeholder
            while self.school_combo.count() > 1:
                self.school_combo.removeItem(self.school_combo.count() - 1)
                
            schools = self.db.get_schools()
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_combo.addItem(school_name, school_id)
            print(f"📚 Loaded {len(schools)} schools in student page")
        except Exception as e:
            print(f"❌ Error loading schools: {e}")
            # Add some default options if database fails
            self.school_combo.addItems(["Primary School", "Secondary School"])

    def _load_classes_data(self, school_id=None):
        """Load classes from database and populate class combo."""
        try:
            # Clear existing items except placeholder
            while self.class_combo.count() > 1:
                self.class_combo.removeItem(self.class_combo.count() - 1)
                
            classes = self.db.get_classes(school_id)
            for class_name in classes:
                self.class_combo.addItem(class_name)
            print(f"📚 Loaded {len(classes)} classes in student page")
        except Exception as e:
            print(f"❌ Error loading classes: {e}")
            # Add some default options if database fails
            self.class_combo.addItems(["9", "10", "11", "12"])

    def _load_sections_data(self, school_id=None, class_name=None):
        """Load sections from database and populate section combo."""
        try:
            # Clear existing items except placeholder
            while self.section_combo.count() > 1:
                self.section_combo.removeItem(self.section_combo.count() - 1)
                
            sections = self.db.get_sections(school_id, class_name)
            for section_name in sections:
                self.section_combo.addItem(section_name)
            print(f"📚 Loaded {len(sections)} sections in student page")
        except Exception as e:
            print(f"❌ Error loading sections: {e}")
            # Add some default options if database fails
            self.section_combo.addItems(["A", "B", "C"])

    def _on_school_changed(self, school_name):
        """Handle school selection change."""
        if school_name == "Please Select School":
            school_id = None
        else:
            # Get school ID from combo data
            current_index = self.school_combo.currentIndex()
            school_id = self.school_combo.itemData(current_index)
        
        print(f"🏫 School changed to: {school_name} (ID: {school_id})")
        
        # Reload classes and sections for selected school
        self._load_classes_data(school_id)
        self._load_sections_data(school_id)
        
        # Apply filters
        self._apply_filters()

    def _on_class_changed(self, class_name):
        """Handle class selection change."""
        if class_name == "Please Select Class":
            class_name = None
            
        # Get current school
        school_id = None
        if self.school_combo.currentText() != "Please Select School":
            current_index = self.school_combo.currentIndex()
            school_id = self.school_combo.itemData(current_index)
        
        print(f"📚 Class changed to: {class_name}")
        
        # Reload sections for selected school and class
        self._load_sections_data(school_id, class_name)
        
        # Apply filters
        self._apply_filters()

    def _on_school_selection_changed(self):
        """Auto-populate organizational fields when school is selected in form."""
        try:
            # Get the school combo widget from the sender
            school_combo = self.sender()
            if not school_combo or not hasattr(school_combo, 'currentData'):
                return
                
            # Get selected school ID
            school_id = school_combo.currentData()
            if not school_id:
                return
                
            print(f"🏫 School selected: ID {school_id}")
            
            # Get organizational data for this school
            org_data = self.db.get_school_organizational_data(school_id)
            if not org_data:
                print("❌ No organizational data found for school")
                return
                
            print(f"📊 Auto-populating organizational fields: {org_data}")
            
            # Auto-populate organizational fields
            self._populate_organizational_fields(org_data)
            
        except Exception as e:
            print(f"❌ Error in school selection change: {e}")
            
    def _populate_organizational_fields(self, org_data):
        """Populate organizational fields based on school data."""
        try:
            # Map the organizational IDs to combo box selections
            field_mappings = {
                'org_id': ('org_id', self._get_organizations_from_database()),
                'province_id': ('province_id', self._get_provinces_from_database()),
                'district_id': ('district_id', self._get_districts_from_database()),
                'union_council_id': ('union_council_id', self._get_union_councils_from_database()),
                'nationality_id': ('nationality_id', self._get_nationalities_from_database())
            }
            
            for data_key, (field_name, options_list) in field_mappings.items():
                if field_name in self.student_fields and data_key in org_data:
                    widget = self.student_fields[field_name]
                    if isinstance(widget, CustomComboBox):
                        # Get the ID value
                        id_value = org_data[data_key]
                        
                        # For now, set to first available option (can be enhanced later)
                        if widget.count() > 1:  # Skip "Select..." placeholder
                            widget.setCurrentIndex(1)  # Set to first real option
                            print(f"✅ Set {field_name} to index 1 (ID: {id_value})")
                        
        except Exception as e:
            print(f"❌ Error populating organizational fields: {e}")
    
    def _show_form(self, title):
        """Show the student form with the given title."""
        try:
            print(f"🔄 Opening {title} form...")
            
            # Check if form_frame exists
            if not self.form_frame:
                show_critical_message("Error", "Form frame is not initialized.")
                return
                
            # Clear student fields dictionary to prevent stale references
            self.student_fields.clear()
            
            # Properly cleanup existing layout and widgets
            self._cleanup_form_layout()
            
            # Disconnect any existing button signals to prevent crashes
            try:
                if hasattr(self, 'save_btn') and self.save_btn:
                    self.save_btn.clicked.disconnect()
                if hasattr(self, 'close_btn') and self.close_btn:
                    self.close_btn.clicked.disconnect()
                if hasattr(self, 'clear_btn') and self.clear_btn:
                    self.clear_btn.clicked.disconnect()
            except:
                pass  # Ignore if signals weren't connected
            
            # Ensure form frame is ready for new layout
            if self.form_frame.layout():
                print("⚠️ Warning: Form frame still has a layout after cleanup")
                # Force complete layout cleanup
                current_layout = self.form_frame.layout()
                while current_layout.count():
                    item = current_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                    elif item.layout():
                        item.layout().deleteLater()
                self.form_frame.setLayout(None)
                current_layout.deleteLater()
            
            # Create comprehensive form with consistent spacing
            form_layout = QVBoxLayout()
            form_layout.setContentsMargins(5, 0, 5, 0)
            form_layout.setSpacing(5)
        
            # Single page form content instead of tabs
            form_content_widget = self._create_single_page_form()
            
            # Validate form content widget
            if not form_content_widget:
                print("❌ Error: Form content widget is None")
                show_critical_message("Error", "Failed to create form content.")
                return
            
            # Form buttons - create new instances to avoid stale references
            buttons_layout = QHBoxLayout()
            
            # Create fresh button instances
            self.save_btn = QPushButton("💾 Save Student")
            self.save_btn.setProperty("class", "success")
            
            self.close_btn = QPushButton("✖️ Close")
            
            self.clear_btn = QPushButton("🔄 Reset Form")  # Use consistent naming
            self.clear_btn.setProperty("class", "warning")
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.clear_btn)
            buttons_layout.addWidget(self.close_btn)
            buttons_layout.addWidget(self.save_btn)
            
            # Connect button signals safely
            try:
                self.save_btn.clicked.connect(self._save_student)
                self.close_btn.clicked.connect(self._close_form)
                self.clear_btn.clicked.connect(self._reset_form)
            except Exception as signal_error:
                print(f"Warning: Could not connect button signals: {signal_error}")
        
            # Add to form layout (no header, just content and buttons)
            form_layout.addWidget(form_content_widget, 1)
            form_layout.addLayout(buttons_layout)
            
            # Validate layout integrity before setting
            if not self._validate_layout_integrity(form_layout):
                print("❌ Layout integrity check failed")
                show_critical_message("Error", "Form layout validation failed.")
                return
            
            # Set the layout to the form frame safely
            try:
                if form_layout and self.form_frame:
                    # Check if we need to recreate due to previous cleanup
                    if hasattr(self, '_needs_layout_recreation') and self._needs_layout_recreation:
                        print("🔄 Recreating form frame due to previous cleanup...")
                        self._alternative_form_cleanup()
                        self._needs_layout_recreation = False
                    elif self.form_frame.layout():
                        print("🔄 Form frame already has layout - clearing completely...")
                        # Use the alternative cleanup to recreate the frame
                        self._alternative_form_cleanup()
                    
                    # Ensure form frame has proper spacing settings
                    if hasattr(self.form_frame, 'setContentsMargins'):
                        self.form_frame.setContentsMargins(0, 0, 0, 0)
                    
                    # Now set the layout on the clean frame
                    self.form_frame.setLayout(form_layout)
                    print("✅ Form layout set successfully")
                else:
                    print("❌ Error: Form layout or form frame is None")
                    return
            except Exception as layout_error:
                print(f"❌ Error setting layout: {layout_error}")
                return
            
            # Make form visible after everything is set up
            self.form_frame.setVisible(True)
            print("✅ Student form displayed successfully")
            
        except Exception as e:
            show_critical_message("Error", f"Failed to create form:\n{str(e)}")
            print(f"Form creation error: {e}")  # Debug output
    
    def _close_form(self):
        """Properly close and cleanup the form."""
        try:
            print("🔄 Closing student form...")
            
            # Hide form first
            if self.form_frame:
                self.form_frame.setVisible(False)
            
            # Alternative cleanup approach - avoid setLayout(None)
            try:
                self._safe_form_cleanup()
            except Exception as cleanup_error:
                print(f"Safe cleanup failed: {cleanup_error}, trying alternative...")
                self._alternative_form_cleanup()
            
            # Clear student fields to prevent stale references
            self.student_fields.clear()
            
            # Reset editing state
            self.is_editing = False
            self.current_student_id = None
            
            # Reset form created flag
            self.form_created = False
            
            print("✅ Student form closed and cleaned up successfully")
                
        except Exception as e:
            print(f"❌ Error closing form: {e}")
            # Force hide the form even if cleanup fails
            try:
                if self.form_frame:
                    self.form_frame.setVisible(False)
                # Clear fields
                self.student_fields.clear()
                self.is_editing = False
                print("🔧 Form force-closed with minimal cleanup")
            except Exception as force_error:
                print(f"❌ Force close also failed: {force_error}")
                # Last resort - just clear the dictionary
                self.student_fields.clear()
    
    def _safe_form_cleanup(self):
        """Safe form cleanup without setLayout(None)."""
        if not self.form_frame:
            print("🔄 No form frame to cleanup")
            return
            
        if not self.form_frame.layout():
            print("🔄 No layout to cleanup")
            return
            
        layout = self.form_frame.layout()
        print("🧹 Safe form cleanup starting...")
        
        # Just clear all widgets, don't touch the layout itself
        while layout.count():
            item = layout.takeAt(0)
            if item:
                if item.widget():
                    widget = item.widget()
                    widget.blockSignals(True)
                    widget.setParent(None)
                    widget.deleteLater()
                elif item.layout():
                    child_layout = item.layout()
                    # Recursively clear child layout
                    while child_layout.count():
                        child_item = child_layout.takeAt(0)
                        if child_item and child_item.widget():
                            child_item.widget().deleteLater()
                    child_layout.deleteLater()
        
        # Mark that we need a fresh start next time
        self._needs_layout_recreation = True
        
        # Don't call setLayout(None) at all - just leave the empty layout
        print("✅ Safe cleanup completed")
    
    def _alternative_form_cleanup(self):
        """Alternative cleanup that recreates the form frame."""
        try:
            print("🔄 Alternative cleanup: recreating form frame...")
            
            if not self.form_frame:
                print("⚠️ No form frame to recreate")
                return
            
            # Store parent and geometry
            parent = self.form_frame.parent()
            geometry = self.form_frame.geometry()
            is_visible = self.form_frame.isVisible()
            
            # Delete old frame completely
            self.form_frame.deleteLater()
            
            # Create new form frame
            from PyQt5.QtWidgets import QFrame
            self.form_frame = QFrame()
            
            # Set size policy to expand in both directions
            self.form_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Set parent and geometry
            if parent:
                self.form_frame.setParent(parent)
            self.form_frame.setGeometry(geometry)
            
            # Restore visibility
            if is_visible:
                self.form_frame.show()
            else:
                self.form_frame.hide()
            
            print("✅ Alternative cleanup completed - new form frame created")
            
        except Exception as e:
            print(f"❌ Alternative cleanup failed: {e}")
            # Create minimal form frame as fallback
            try:
                from PyQt5.QtWidgets import QFrame
                self.form_frame = QFrame()
                print("✅ Minimal form frame created as fallback")
            except Exception as fallback_error:
                print(f"❌ Even fallback failed: {fallback_error}")
    
    def _validate_layout_integrity(self, layout):
        """Validate that the layout is properly formed."""
        try:
            if not layout:
                print("❌ Layout is None")
                return False
            
            # Check if layout has valid items
            if layout.count() == 0:
                print("⚠️ Warning: Layout has no items")
                return True  # Empty layout is still valid
            
            # Check each item in the layout
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if not item:
                    print(f"❌ Layout item {i} is None")
                    return False
                
                # If it's a widget, check if it's valid
                if item.widget():
                    widget = item.widget()
                    if not widget:
                        print(f"❌ Layout widget {i} is None")
                        return False
                    # Skip the isValid() check as it might be too strict
                    
                # If it's a layout, check if it's valid
                elif item.layout():
                    child_layout = item.layout()
                    if not child_layout:
                        print(f"❌ Child layout {i} is None")
                        return False
                    # Recursively validate child layouts if needed
                    # For now, just check it exists
            
            print("✅ Layout integrity check passed")
            return True
            
        except Exception as e:
            print(f"❌ Layout integrity check failed: {e}")
            return False
    
    def _create_personal_info_tab(self):
        """Create personal information tab."""
        tab = QWidget()
        
        # Create scroll area for the tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area
        
        # Create content widget for the scroll area
        content_widget = QWidget()
        layout = QGridLayout(content_widget)
        layout.setVerticalSpacing(18)  # Increased row spacing
        layout.setHorizontalSpacing(15)  # Better column spacing
        layout.setContentsMargins(20, 15, 20, 15)  # Better margins for proper alignment
        
        # Personal fields - matching database schema exactly (non-audit fields only)
        personal_fields = [
            # Primary and System Fields
            ("Status*", "status", "combo", True, [["active", "inactive", "transferred", "graduated"]]),
            ("Student ID*", "student_id", "text", True),
            ("Final Unique Codes*", "final_unique_codes", "text", True),
            
            # Student Basic Information
            ("Student Name*", "student_name", "text", True),
            ("Gender*", "gender", "combo", True, [["Male", "Female", "Other"]]),
            ("Date of Birth*", "date_of_birth", "date", True),
            ("B-Form Number*", "students_bform_number", "text", True),
            ("Year of Admission*", "year_of_admission", "date", True),
            ("Year of Admission Alt*", "year_of_admission_alt", "date", True),
            ("Address*", "address", "text", True),
            
            # Father Information
            ("Father Name*", "father_name", "text", True),
            ("Father CNIC*", "father_cnic", "cnic", True),
            ("Father Phone*", "father_phone", "phone", True),
            
            # Household Information
            ("Household Size*", "household_size", "number", True),
        ]
        
        row = 0
        for field_data in personal_fields:
            if len(field_data) >= 4:
                label_text, field_name, field_type, is_required = field_data[:4]
                options = field_data[4] if len(field_data) > 4 else []  # Get the 5th element directly
            else:
                label_text, field_name, field_type = field_data[:3]
                is_required = False
                options = field_data[3] if len(field_data) > 3 else []  # Get the 4th element directly
            
            # Create label with required field indicator
            label = QLabel(label_text + ":")
            # All labels use normal styling (no red color initially)
            label
            label.setAlignment(Qt.AlignVCenter)
            
            # Add tooltips for specific fields
            if "DOI" in label_text:
                label.setToolTip("Date of CNIC Issue")
            elif "Exp" in label_text:
                label.setToolTip("CNIC Expiry Date")
            elif "MWA" in label_text:
                label.setToolTip("Monthly Welfare Allowance")
            elif "*" in label_text:
                label.setToolTip("Required field")
            
            # Create widget based on type with enhanced validation
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {label_text.replace('*', '').lower()}")
                if is_required:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    
            elif field_type == "cnic":
                widget = QLineEdit()
                # Strict CNIC validator: exactly 13 digits with optional hyphens
                cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{5}-?[0-9]{7}-?[0-9]{1}$'))
                widget.setValidator(cnic_validator)
                widget.setPlaceholderText("12345-1234567-1 (13 digits)")
                widget.setMaxLength(15)  # Allow for hyphens
                if is_required:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    
            elif field_type == "phone":
                widget = QLineEdit()
                # Pakistani phone validator: 11 digits starting with 03
                phone_validator = QRegExpValidator(QRegExp(r'^03[0-9]{2}-?[0-9]{7}$'))
                widget.setValidator(phone_validator)
                widget.setPlaceholderText("0300-1234567 (11 digits)")
                widget.setMaxLength(12)  # Allow for hyphen
                if is_required:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    
            elif field_type == "number":
                widget = QSpinBox()
                if "mwa" in field_name.lower():
                    widget.setRange(0, 99999)
                    widget.setValue(0)
                    widget.setSuffix(" PKR")
                elif "_id" in field_name:
                    widget.setRange(1, 99999)
                    widget.setValue(1)
                else:
                    widget.setRange(1, 50)  # Default for household size
                    widget.setValue(1)
                    
            elif field_type == "date":
                widget = CustomDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd-MMM-yyyy")
                widget.setMinimumDate(QDate(1900, 1, 1))
                
                # Show current date by default but mark as "not manually selected"
                widget.setDate(QDate.currentDate())
                widget._user_selected = False  # Track if user manually selected date
                widget._original_date = QDate.currentDate()  # Store original date for comparison
                
                # Connect date changed signal to track user selection
                def on_date_changed(date_widget=widget):
                    # Only mark as user selected if date is different from original
                    if hasattr(date_widget, 'date') and hasattr(date_widget, '_original_date'):
                        if date_widget.date() != date_widget._original_date:
                            date_widget._user_selected = True
                        else:
                            date_widget._user_selected = False
                
                widget.dateChanged.connect(on_date_changed)
                
                # Enhanced calendar setup for large popup with current date
                def setup_enhanced_calendar():
                    calendar = widget.calendarWidget()
                    if calendar:
                        # Set current date as default selection in calendar
                        calendar.setSelectedDate(QDate.currentDate())
                        
                        # Make calendar larger to show full month
                        calendar.setMinimumSize(420, 350)
                        calendar.setMaximumSize(450, 380)
                        
                        # Enhanced calendar styling - fixed headers and full month view with smaller row height
                        calendar
                        
                        # Force calendar to show complete month view
                        if hasattr(calendar, 'setGridVisible'):
                            calendar.setGridVisible(True)
                        if hasattr(calendar, 'setVerticalHeaderFormat'):
                            calendar.setVerticalHeaderFormat(calendar.NoVerticalHeader)
                
                # Setup calendar immediately since it's available
                setup_enhanced_calendar()
                
                # Remove automatic required field styling - will be applied on validation
                if is_required:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    
            elif field_type == "combo":
                widget = CustomComboBox()
                if options and len(options) > 0:
                    # Handle both direct list and nested list structures
                    if isinstance(options[0], list):
                        combo_options = options[0]  # Nested: [["Father", "Mother", ...]]
                    else:
                        combo_options = options  # Direct: ["Male", "Female"]
                    
                    if is_required:
                        widget.addItems(["Select..."] + combo_options)
                        widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    else:
                        widget.addItems(["Not Specified"] + combo_options)
                    
                    # Store original items for later restoration
                    widget._original_items = []
                    for i in range(widget.count()):
                        widget._original_items.append(widget.itemText(i))
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "combo")
                        
            # Database-driven combo boxes
            elif field_type == "school_combo":
                widget = CustomComboBox()
                schools = self._get_schools_from_database()
                if is_required:
                    widget.addItems(["Select School..."] + schools)
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                else:
                    widget.addItems(["Not Specified"] + schools)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "school_combo")
                    
            elif field_type == "org_combo":
                widget = CustomComboBox()
                organizations = self._get_organizations_from_database()
                if is_required:
                    widget.addItems(["Select Organization..."] + organizations)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + organizations)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "org_combo")
                    
            elif field_type == "province_combo":
                widget = CustomComboBox()
                provinces = self._get_provinces_from_database()
                if is_required:
                    widget.addItems(["Select Province..."] + provinces)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + provinces)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "province_combo")
                    
            elif field_type == "district_combo":
                widget = CustomComboBox()
                districts = self._get_districts_from_database()
                if is_required:
                    widget.addItems(["Select District..."] + districts)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + districts)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "district_combo")
                    
            elif field_type == "union_council_combo":
                widget = CustomComboBox()
                union_councils = self._get_union_councils_from_database()
                if is_required:
                    widget.addItems(["Select Union Council..."] + union_councils)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + union_councils)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "union_council_combo")
                    
            elif field_type == "nationality_combo":
                widget = CustomComboBox()
                nationalities = self._get_nationalities_from_database()
                if is_required:
                    widget.addItems(["Select Nationality..."] + nationalities)
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                else:
                    widget.addItems(["Not Specified"] + nationalities)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "nationality_combo")
            
            # Apply normal styling to all fields (no red styling initially)
                
            self.student_fields[field_name] = widget
            
            layout.addWidget(label, row, 0)
            layout.addWidget(widget, row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
        
        # Set the content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main tab layout
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        return tab
    
    def _create_academic_info_tab(self):
        """Create academic information tab."""
        tab = QWidget()
        
        # Create scroll area for the tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area
        
        # Create content widget for the scroll area
        content_widget = QWidget()
        layout = QGridLayout(content_widget)
        layout.setVerticalSpacing(18)  # Increased row spacing
        layout.setHorizontalSpacing(15)  # Better column spacing
        layout.setContentsMargins(20, 15, 20, 15)  # Better margins for proper alignment
        
        # Academic fields - simplified: only school selection, organizational data auto-populated
        academic_fields = [
            # School Selection (required) - organizational data will be auto-populated
            ("School*", "school_id", "school_combo", True),
            
            # School Information (all required)
            ("Registration Number*", "registration_number", "text", True),
            ("Class Teacher Name*", "class_teacher_name", "text", True),
            
            # Academic Information (all required)
            ("Class*", "class", "class_combo", True),
            ("Section*", "section", "section_combo", True),
        ]
        
        row = 0
        for field_data in academic_fields:
            if len(field_data) >= 4:
                label_text, field_name, field_type, is_required = field_data[:4]
                options = field_data[4] if len(field_data) > 4 else []  # Get the 5th element directly
            else:
                label_text, field_name, field_type = field_data[:3]
                is_required = False
                options = field_data[3] if len(field_data) > 3 else []  # Get the 4th element directly
            
            # Create label with required field indicator
            label = QLabel(label_text + ":")
            # All labels use normal styling (no red color initially)
            label
            label.setAlignment(Qt.AlignVCenter)
            
            # Create widget based on type
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {label_text.replace('*', '').lower()}")
                
            elif field_type == "school_combo":
                widget = CustomComboBox()  # Using CustomComboBox for better styling
                # Load schools from database
                try:
                    print(f"🏫 Loading schools for academic info tab...")
                    schools = self.db.get_schools()
                    print(f"🏫 Found {len(schools)} schools for academic form")
                    
                    if is_required:
                        widget.addItem("Select School...")
                    else:
                        widget.addItem("Not Specified")
                    
                    for school in schools:
                        school_name = school.get('school_name', f"School {school.get('id', '')}")
                        widget.addItem(school_name, school.get('id'))
                        
                    if not schools:
                        widget.addItem("No schools found")
                    
                    print(f"🏫 Academic school combo populated with {widget.count()} items")
                    
                    # Connect school selection change to auto-populate organizational fields
                    widget.currentIndexChanged.connect(self._on_school_selection_changed)
                    
                except Exception as e:
                    print(f"❌ Error loading schools for academic form: {e}")
                    widget.addItems(["Error loading schools"])
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "school_combo")
                    
            elif field_type == "org_combo":
                widget = CustomComboBox()
                organizations = self._get_organizations_from_database()
                if is_required:
                    widget.addItems(["Select Organization..."] + organizations)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + organizations)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "org_combo")
                    
            elif field_type == "province_combo":
                widget = CustomComboBox()
                provinces = self._get_provinces_from_database()
                if is_required:
                    widget.addItems(["Select Province..."] + provinces)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + provinces)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "province_combo")
                    
            elif field_type == "district_combo":
                widget = CustomComboBox()
                districts = self._get_districts_from_database()
                if is_required:
                    widget.addItems(["Select District..."] + districts)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + districts)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "district_combo")
                    
            elif field_type == "union_council_combo":
                widget = CustomComboBox()
                union_councils = self._get_union_councils_from_database()
                if is_required:
                    widget.addItems(["Select Union Council..."] + union_councils)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + union_councils)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "union_council_combo")
                    
            elif field_type == "nationality_combo":
                widget = CustomComboBox()
                nationalities = self._get_nationalities_from_database()
                if is_required:
                    widget.addItems(["Select Nationality..."] + nationalities)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + nationalities)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "nationality_combo")
                    
            elif field_type == "combo":
                widget = CustomComboBox()
                if options and len(options) > 0:
                    # Handle both direct list and nested list structures
                    if isinstance(options[0], list):
                        combo_options = options[0]  # Nested: [["Father", "Mother", ...]]
                    else:
                        combo_options = options  # Direct: ["Male", "Female"]
                    
                    if is_required:
                        widget.addItems(["Select..."] + combo_options)
                    else:
                        widget.addItems(["Not Specified"] + combo_options)
                    
                    # Store original items for later restoration
                    widget._original_items = []
                    for i in range(widget.count()):
                        widget._original_items.append(widget.itemText(i))
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "combo")
                        
            elif field_type == "class_combo":
                widget = CustomComboBox()
                try:
                    classes = self.db.get_classes()
                    # Database method returns list of strings directly
                    class_names = classes if classes else []
                    
                    if is_required:
                        widget.addItem("Select Class...")
                        widget.addItems(class_names)
                        widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                    else:
                        widget.addItem("Not Specified")
                        widget.addItems(class_names)
                    
                    print(f"📚 Loaded {len(class_names)} classes for form: {class_names}")
                except Exception as e:
                    print(f"❌ Error loading classes for form: {e}")
                    widget.addItems(["Class 1", "Class 2", "Class 3"])
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "class_combo")
                    
            elif field_type == "section_combo":
                widget = CustomComboBox()
                try:
                    sections = self.db.get_sections()
                    # Database method returns list of strings directly
                    section_names = sections if sections else []
                    
                    if is_required:
                        widget.addItem("Select Section...")
                        widget.addItems(section_names)
                        widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                    else:
                        widget.addItem("Not Specified")
                        widget.addItems(section_names)
                    
                    print(f"📚 Loaded {len(section_names)} sections for form: {section_names}")
                except Exception as e:
                    print(f"❌ Error loading sections for form: {e}")
                    widget.addItems(["Section A", "Section B", "Section C"])
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "section_combo")
                        
            elif field_type == "number":
                widget = QSpinBox()
                widget.setRange(1, 99999)
                widget.setValue(1)
                
            elif field_type == "year":
                widget = QSpinBox()
                current_year = QDate.currentDate().year()
                widget.setRange(1990, current_year + 5)
                widget.setValue(current_year)
                widget.setSuffix(" year")
            
            # Apply normal styling to all fields (no red styling initially)
            if is_required:
                widget.setProperty("is_required", True)  # Mark as required but don't style yet
                
            self.student_fields[field_name] = widget
            
            layout.addWidget(label, row, 0)
            layout.addWidget(widget, row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
        
        # Set the content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main tab layout
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        return tab
    
    def _create_contact_info_tab(self):
        """Create contact information tab."""
        tab = QWidget()
        
        # Create scroll area for the tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area
        
        # Create content widget
        content_widget = QWidget()
        layout = QGridLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Contact fields - Recipient Type at top, then conditional fields
        contact_fields = [
            # Recipient Type - MUST BE FIRST for conditional logic
            ("Recipient Type*", "recipient_type", "combo", True, [["Principal", "Alternate"]]),
            
            # Mother Information (conditional based on recipient type)
            ("Mother Name", "mother_name", "text", False),
            ("Mother Date of Birth", "mother_date_of_birth", "date", False),
            ("Mother Marital Status", "mother_marital_status", "combo", False, [["Single", "Married", "Divorced", "Widowed", "Free union", "Separated", "Engaged"]]),
            ("Mother ID Type", "mother_id_type", "text", False),
            ("Mother CNIC", "mother_cnic", "cnic", False),
            ("Mother CNIC DOI", "mother_cnic_doi", "date", False),
            ("Mother CNIC Exp", "mother_cnic_exp", "date", False),
            ("Mother MWA", "mother_mwa", "phone", False),
            
            # Household Head Information (conditional based on recipient type)
            ("Household Role", "household_role", "combo", False, [["Head", "Son", "Daughter", "Wife", "Husband", "Brother", "Sister", "Mother", "Father", "Aunt", "Uncle", "Grand Mother", "Grand Father", "Mother-in-Law", "Father-in-Law", "Daughter-in-Law", "Son-in-Law", "Sister-in-Law", "Brother-in-Law", "Grand Daughter", "Grand Son", "Nephew", "Niece", "Cousin", "Other", "Not Member"]]),
            ("Household Name", "household_name", "text", False),
            ("HH Gender", "hh_gender", "combo", False, [["Male", "Female", "Other"]]),
            ("HH Date of Birth", "hh_date_of_birth", "date", False),
            
            # Alternate/Guardian Information (conditional based on recipient type)
            ("Alternate Name", "alternate_name", "text", False),
            ("Alternate Date of Birth", "alternate_date_of_birth", "date", False),
            ("Alternate Marital Status", "alternate_marital_status", "combo", False, [["Single", "Married", "Divorced", "Widowed", "Free union", "Separated", "Engaged"]]),
            ("Alternate ID Type", "alternate_id_type", "text", False),
            ("Alternate CNIC", "alternate_cnic", "cnic", False),
            ("Alternate CNIC DOI", "alternate_cnic_doi", "date", False),
            ("Alternate CNIC Exp", "alternate_cnic_exp", "date", False),
            ("Alternate MWA", "alternate_mwa", "phone", False),
            ("Alternate Relationship with Mother", "alternate_relationship_with_mother", "combo", False, [["Head", "Son", "Daughter", "Wife", "Husband", "Brother", "Sister", "Mother", "Father", "Aunt", "Uncle", "Grand Mother", "Grand Father", "Mother-in-Law", "Father-in-Law", "Daughter-in-Law", "Son-in-Law", "Sister-in-Law", "Brother-in-Law", "Grand Daughter", "Grand Son", "Nephew", "Niece", "Cousin", "Other", "Not Member"]]),
        ]
        
        # Store field categories for conditional logic
        self.mother_fields = ['mother_name', 'mother_date_of_birth', 'mother_marital_status', 
                             'mother_id_type', 'mother_cnic', 'mother_cnic_doi', 'mother_cnic_exp', 'mother_mwa']
        self.household_fields = ['household_role', 'household_name', 'hh_gender', 'hh_date_of_birth']
        self.alternate_fields = ['alternate_name', 'alternate_date_of_birth', 'alternate_marital_status',
                                'alternate_id_type', 'alternate_cnic', 'alternate_cnic_doi', 
                                'alternate_cnic_exp', 'alternate_mwa', 'alternate_relationship_with_mother']
        
        row = 0
        for field_data in contact_fields:
            if len(field_data) >= 4:
                label_text, field_name, field_type, is_required = field_data[:4]
                options = field_data[4] if len(field_data) > 4 else []  # Get the 5th element directly
            else:
                label_text, field_name, field_type = field_data[:3]
                is_required = False
                options = field_data[3] if len(field_data) > 3 else []  # Get the 4th element directly
            
            # Create label with required field indicator
            label = QLabel(label_text + ":")
            # All labels use normal styling (no red color initially)
            label
            label.setAlignment(Qt.AlignVCenter)
            
            # Create widget based on type
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {label_text.replace('*', '').lower()}")
                
            elif field_type == "email":
                widget = QLineEdit()
                widget.setPlaceholderText("Enter email address")
                
            elif field_type == "phone":
                widget = QLineEdit()
                # Pakistani phone validator: 11 digits starting with 03
                phone_validator = QRegExpValidator(QRegExp(r'^03[0-9]{2}-?[0-9]{7}$'))
                widget.setValidator(phone_validator)
                widget.setPlaceholderText("0300-1234567 (MWA number)")
                widget.setMaxLength(12)  # Allow for hyphen
                if is_required:
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                
            elif field_type == "cnic":
                widget = QLineEdit()
                # CNIC validator: 13 digits with optional hyphens
                cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{5}-?[0-9]{7}-?[0-9]$'))
                widget.setValidator(cnic_validator)
                widget.setPlaceholderText("12345-1234567-1 (13 digits)")
                widget.setMaxLength(15)  # Allow for hyphens
                if is_required:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    
            elif field_type == "date":
                widget = CustomDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd-MMM-yyyy")
                widget.setMinimumDate(QDate(1900, 1, 1))
                
                # Show current date by default but mark as "not manually selected"
                widget.setDate(QDate.currentDate())
                widget._user_selected = False  # Track if user manually selected date
                widget._original_date = QDate.currentDate()  # Store original date for comparison
                
                # Connect date changed signal to track user selection
                def on_date_changed(date_widget=widget):
                    # Only mark as user selected if date is different from original
                    if hasattr(date_widget, 'date') and hasattr(date_widget, '_original_date'):
                        if date_widget.date() != date_widget._original_date:
                            date_widget._user_selected = True
                        else:
                            date_widget._user_selected = False
                
                widget.dateChanged.connect(on_date_changed)
                
                # Enhanced calendar setup for large popup with current date
                def setup_enhanced_calendar():
                    calendar = widget.calendarWidget()
                    if calendar:
                        # Set current date as default selection in calendar
                        calendar.setSelectedDate(QDate.currentDate())
                        
                        # Make calendar larger to show full month
                        calendar.setMinimumSize(420, 350)
                        calendar.setMaximumSize(450, 380)
                        
                        # Enhanced calendar styling - fixed headers and full month view with smaller row height
                        calendar
                        
                        # Force calendar to show complete month view
                        if hasattr(calendar, 'setGridVisible'):
                            calendar.setGridVisible(True)
                        if hasattr(calendar, 'setVerticalHeaderFormat'):
                            calendar.setVerticalHeaderFormat(calendar.NoVerticalHeader)
                
                # Setup calendar immediately since it's available
                setup_enhanced_calendar()
                
                # Remove automatic required field styling - will be applied on validation
                if is_required:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                
            elif field_type == "combo":
                widget = CustomComboBox()
                if options and len(options) > 0:
                    # Handle both direct list and nested list structures
                    if isinstance(options[0], list):
                        combo_options = options[0]  # Nested: [["Father", "Mother", ...]]
                    else:
                        combo_options = options  # Direct: ["Male", "Female"]
                    
                    if is_required:
                        widget.addItems(["Select..."] + combo_options)
                    else:
                        widget.addItems(["Not Specified"] + combo_options)
                    
                    # Store original items for later restoration
                    widget._original_items = []
                    for i in range(widget.count()):
                        widget._original_items.append(widget.itemText(i))
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "combo")
            
            # Apply normal styling to all fields (no red styling initially)
            if is_required:
                widget.setProperty("is_required", True)  # Mark as required but don't style yet
                
            self.student_fields[field_name] = widget
            
            layout.addWidget(label, row, 0)
            layout.addWidget(widget, row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
        
        # Set the content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main tab layout
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        # Setup conditional logic for recipient type after all widgets are created
        self._setup_recipient_type_conditional_logic()
        
        return tab
    
    def _setup_recipient_type_conditional_logic(self):
        """Setup conditional logic for recipient type selection."""
        if 'recipient_type' not in self.student_fields:
            return
            
        recipient_combo = self.student_fields['recipient_type']
        
        # Set default to "Principal"
        principal_index = recipient_combo.findText("Principal")
        if principal_index >= 0:
            recipient_combo.setCurrentIndex(principal_index)
        
        # Connect signal for recipient type change
        recipient_combo.currentTextChanged.connect(self._on_recipient_type_changed)
        
        # Initialize with Principal as default
        self._on_recipient_type_changed("Principal")
    
    def _on_recipient_type_changed(self, selected_type):
        """Handle recipient type selection changes."""
        print(f"🎯 Recipient type changed to: {selected_type}")
        
        # Disable all conditional fields first
        self._disable_conditional_fields()
        
        if selected_type == "Principal":
            # Enable and make mother + household fields mandatory
            self._enable_mother_fields(mandatory=True)
            self._enable_household_fields(mandatory=True)
            self._disable_alternate_fields()
            print("✅ Principal selected - Mother and Household fields enabled and mandatory")
            
        elif selected_type == "Alternate":
            # Enable and make alternate fields mandatory
            self._enable_alternate_fields(mandatory=True)
            self._disable_mother_fields()
            self._disable_household_fields()
            print("✅ Alternate selected - Alternate fields enabled and mandatory")
            
        else:
            # "Select..." or other - disable all
            self._disable_all_conditional_fields()
            print("⚠️ No recipient type selected - all conditional fields disabled")
    
    def _enable_mother_fields(self, mandatory=False):
        """Enable mother-related fields and optionally make them mandatory."""
        for field_name in self.mother_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(True)
                
                if mandatory:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    # Update label to show required indicator
                    self._update_field_label(field_name, required=True)
                else:
                    widget.setProperty("is_required", False)
                    self._update_field_label(field_name, required=False)
    
    def _enable_household_fields(self, mandatory=False):
        """Enable household-related fields and optionally make them mandatory."""
        for field_name in self.household_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(True)
                
                if mandatory:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    self._update_field_label(field_name, required=True)
                else:
                    widget.setProperty("is_required", False)
                    self._update_field_label(field_name, required=False)
    
    def _enable_alternate_fields(self, mandatory=False):
        """Enable alternate-related fields and optionally make them mandatory."""
        for field_name in self.alternate_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(True)
                
                if mandatory:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    self._update_field_label(field_name, required=True)
                else:
                    widget.setProperty("is_required", False)
                    self._update_field_label(field_name, required=False)
    
    def _disable_mother_fields(self):
        """Disable mother-related fields."""
        for field_name in self.mother_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(False)
                self._update_field_label(field_name, required=False)
    
    def _disable_household_fields(self):
        """Disable household-related fields."""
        for field_name in self.household_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(False)
                self._update_field_label(field_name, required=False)
    
    def _disable_alternate_fields(self):
        """Disable alternate-related fields."""
        for field_name in self.alternate_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(False)
                self._update_field_label(field_name, required=False)
    
    def _disable_conditional_fields(self):
        """Disable all conditional fields."""
        self._disable_mother_fields()
        self._disable_household_fields()
        self._disable_alternate_fields()
    
    def _disable_all_conditional_fields(self):
        """Disable all conditional fields (alias for consistency)."""
        self._disable_conditional_fields()
    
    def _update_field_label(self, field_name, required=False):
        """Update field label to show/hide required indicator."""
        # Find the label widget associated with this field
        # This would need access to the layout or we could store label references
        # For now, we'll update the styling which is more reliable
        pass
    
    def _get_disabled_input_style(self):
        """Return styling for disabled input fields."""
        return """
            QLineEdit, CustomDateEdit, QSpinBox {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 6px 8px;
                font-family: 'Poppins Medium';
                font-size: 12px;
                color: #94A3B8;
                min-height: 24px;
                max-height: 32px;
            }
        """

    def _apply_combo_box_dropdown_fix(self, widget, combo_type="combo"):
        """Apply dropdown functionality fix with simple keyboard highlight.
        Note: This is now a compatibility method for CustomComboBox which has its own handling."""
        # CustomComboBox handles this functionality internally
        pass
        # Make combo box NOT editable for simple keyboard navigation
        widget.setEditable(False)
        
        # Set maximum visible items for dropdown
        widget.setMaxVisibleItems(6)
        
        # Store original items when combo is created
        if not hasattr(widget, '_original_items'):
            widget._original_items = []
            for i in range(widget.count()):
                widget._original_items.append(widget.itemText(i))
        
        # Simple keyboard navigation - highlight matching items
        original_key_press = widget.keyPressEvent
        def simple_key_press(event):
            try:
                from PyQt5.QtCore import Qt
                
                # Get the pressed key as text
                key_text = event.text().lower()
                
                # Only handle letter/number keys for navigation
                if key_text and key_text.isalnum():
                    # Find first item that starts with this key
                    for i in range(widget.count()):
                        item_text = widget.itemText(i).lower()
                        if item_text.startswith(key_text):
                            widget.setCurrentIndex(i)
                            # If dropdown is open, ensure item is visible
                            if widget.view().isVisible():
                                widget.view().scrollTo(widget.view().model().index(i, 0))
                            break
                    event.accept()
                    return
                
                # Handle other keys normally
                if original_key_press:
                    original_key_press(event)
                    
            except Exception as e:
                print(f"Warning: Combo key navigation error: {e}")
                # Fallback to original behavior
                if original_key_press:
                    try:
                        original_key_press(event)
                    except:
                        pass
        
        widget.keyPressEvent = simple_key_press
    
    def _create_single_page_form(self):
        """Create a single page form with 2-column layout using EXACT same pattern as mother_reg.py"""
        # Create main container
        container = QFrame()
        container
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area
        
        # Create content widget for scroll area
        content_widget = QWidget()
        content_widget
        scroll_area.setWidget(content_widget)
        
        # Main layout for content
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.setSpacing(5)
        
        # Create form grid EXACT same as mother_reg.py
        form_grid = QGridLayout()
        form_grid.setVerticalSpacing(5)
        form_grid.setHorizontalSpacing(25)
        form_grid.setContentsMargins(0, 0, 0, 0)
        
        # All form fields
        all_fields = [
            ("status", "Status", "combo", ["active", "inactive", "transferred", "graduated"]),
            ("student_id", "Student ID", "text"),
            ("student_name", "Student Name", "text"),
            ("final_unique_codes", "Final Unique Codes", "text"),
            ("gender", "Gender", "combo", ["Male", "Female", "Other"]),
            ("date_of_birth", "Date of Birth", "date"),
            ("students_bform_number", "B-Form Number", "text"),
            ("year_of_admission", "Year of Admission", "date"),
            ("year_of_admission_alt", "Year of Admission Alt", "date"),
            ("address", "Address", "text"),
            ("father_name", "Father Name", "text"),
            ("father_cnic", "Father CNIC", "cnic"),
            ("father_phone", "Father Phone", "phone"),
            ("household_size", "Household Size", "spinbox"),
            ("school_id", "School", "school_combo"),
            ("registration_number", "Registration Number", "text"),
            ("class_teacher_name", "Class Teacher Name", "text"),
            ("class", "Class", "class_combo"),
            ("section", "Section", "section_combo"),
            ("recipient_type", "Recipient Type", "combo", ["Principal", "Alternate"]),
            ("mother_name", "Mother Name", "text"),
            ("mother_date_of_birth", "Mother Date of Birth", "date"),
            ("mother_marital_status", "Mother Marital Status", "combo", ["Single", "Married", "Divorced", "Widowed", "Free union", "Separated", "Engaged"]),
            ("mother_id_type", "Mother ID Type", "text"),
            ("mother_cnic", "Mother CNIC", "cnic"),
            ("mother_cnic_doi", "Mother CNIC DOI", "date"),
            ("mother_cnic_exp", "Mother CNIC Exp", "date"),
            ("mother_mwa", "Mother MWA", "phone"),
            ("household_role", "Household Role", "combo", ["Head", "Son", "Daughter", "Wife", "Husband", "Brother", "Sister", "Mother", "Father", "Aunt", "Uncle", "Grand Mother", "Grand Father", "Mother-in-Law", "Father-in-Law", "Daughter-in-Law", "Son-in-Law", "Sister-in-Law", "Brother-in-Law", "Grand Daughter", "Grand Son", "Nephew", "Niece", "Cousin", "Other", "Not Member"]),
            ("household_name", "Household Name", "text"),
            ("hh_gender", "HH Gender", "combo", ["Male", "Female", "Other"]),
            ("hh_date_of_birth", "HH Date of Birth", "date"),
            ("alternate_name", "Alternate Name", "text"),
            ("alternate_date_of_birth", "Alternate Date of Birth", "date"),
            ("guardian_cnic", "Guardian CNIC", "cnic"),
        ]
        
        # Create form fields using EXACT same pattern as mother_reg.py
        row, col = 0, 0
        
        for field_data in all_fields:
            if len(field_data) >= 4:
                field_name, label_text, field_type, options = field_data
            else:
                field_name, label_text, field_type = field_data
                options = None
            
            # Create field widget using EXACT same pattern as mother_reg.py
            field_widget = self._create_field_widget_like_mother_reg(field_name, label_text, field_type, options)
            
            # Extract actual input widget from container for student_fields reference
            if hasattr(field_widget, 'layout') and field_widget.layout().count() > 1:
                # Get the input widget (second item in the container layout)
                input_widget = field_widget.layout().itemAt(1).widget()
                self.student_fields[field_name] = input_widget
            else:
                self.student_fields[field_name] = field_widget
            
            # Add container to grid EXACT same way as mother_reg.py
            form_grid.addWidget(field_widget, row, col)
            
            col += 1
            if col >= 2:  # 2 columns
                col = 0
                row += 1
        
        # Add form grid to main layout
        main_layout.addLayout(form_grid)
        # No addStretch() to avoid extra space
        
        # Add scroll area to container
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(scroll_area)
        
        # Setup conditional logic for recipient type
        self._setup_recipient_type_conditional_logic()
        
        return container
    
    def _create_field_widget_like_mother_reg(self, field_name, label_text, field_type, options=None):
        """Create a form field widget with label and input EXACT same as mother_reg.py"""
        container = QWidget()
        container.setObjectName(f"FormFieldContainer_{field_name}")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        container.setMinimumHeight(90)
        container.setMinimumWidth(250)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create label EXACT same as mother_reg.py
        label = FormLabel(label_text)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label)
        
        # Create input widget
        if field_type == "school_combo":
            widget = CustomComboBox()
            widget.setObjectName(f"FormField_{field_name}")
            self._load_schools_into_combo(widget)
            widget.currentTextChanged.connect(self._on_school_selection_changed)
        elif field_type == "class_combo":
            widget = CustomComboBox()
            widget.setObjectName(f"FormField_{field_name}")
            self._load_classes_into_combo(widget)
        elif field_type == "section_combo":
            widget = CustomComboBox()
            widget.setObjectName(f"FormField_{field_name}")
            self._load_sections_into_combo(widget)
        elif field_type in ["text", "cnic", "phone"]:
            widget = InputField.create_field(
                "cnic" if field_type == "cnic" else "phone" if field_type == "phone" else "text", 
                label_text
            )
            widget.setObjectName(f"FormField_{field_name}")
        elif field_type == "date":
            widget = CustomDateEdit(icon_only=True)
            widget.setDate(QDate.currentDate())
            widget.setObjectName(f"CustomDateEdit_{field_name}")
        elif field_type == "combo":
            widget = CustomComboBox()
            widget.setObjectName(f"CustomComboBox_{field_name}")
            if options:
                widget.addItems(options)
        elif field_type == "spinbox":
            widget = InputField.create_field("spinbox", label_text)
            widget.setObjectName(f"FormField_{field_name}")
        else:
            # Fallback to create_form_field_with_label
            _, widget, _ = create_form_field_with_label(field_name, label_text, field_type, options)
        
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(widget)
        
        layout.addStretch(1)
        
        return container  # Return the container, not just the widget
    
    def _load_schools_into_combo(self, combo):
        """Load schools data into combo box."""
        try:
            schools = self._get_schools_from_database()
            combo.clear()
            combo.addItem("Select School...")
            for school in schools:
                combo.addItem(school.get('name', ''), school.get('id'))
        except Exception as e:
            print(f"Error loading schools: {e}")
    
    def _load_classes_into_combo(self, combo):
        """Load classes data into combo box."""
        try:
            classes = self._get_classes_from_database()
            combo.clear()
            combo.addItem("Select Class...")
            for class_item in classes:
                combo.addItem(class_item.get('name', ''), class_item.get('id'))
        except Exception as e:
            print(f"Error loading classes: {e}")
    
    def _load_sections_into_combo(self, combo):
        """Load sections data into combo box."""
        try:
            sections = self._get_sections_from_database()
            combo.clear()
            combo.addItem("Select Section...")
            for section in sections:
                combo.addItem(section.get('name', ''), section.get('id'))
        except Exception as e:
            print(f"Error loading sections: {e}")
    
    def _get_classes_from_database(self):
        """Get classes from database."""
        try:
            if hasattr(self, 'db') and self.db:
                classes = self.db.get_classes()
                # Convert string list to dict format
                return [{'name': cls, 'id': idx} for idx, cls in enumerate(classes)]
            return []
        except Exception as e:
            print(f"Error getting classes: {e}")
            return []
    
    def _get_sections_from_database(self):
        """Get sections from database."""
        try:
            if hasattr(self, 'db') and self.db:
                sections = self.db.get_sections()
                # Convert string list to dict format
                return [{'name': sec, 'id': idx} for idx, sec in enumerate(sections)]
            return []
        except Exception as e:
            print(f"Error getting sections: {e}")
            return []

    def _clear_validation_errors(self):
        """Clear all validation error styling from form fields."""
        # No need for manual styling - centralized theme handles this
        pass
    
    def _highlight_validation_errors(self, error_fields):
        """Highlight fields that have validation errors in red."""
        # No need for manual styling - centralized theme handles this
        pass

    def _is_date_empty(self, date_widget):
        """Check if date widget has current date (not manually changed)."""
        # Check if date is current date - if yes, consider it as not selected
        if date_widget.date() == QDate.currentDate():
            return True  # Current date means user didn't select anything
        
        # If it's any other date, consider it as selected
        return False
    
    def _validate_form_with_fields(self):
        """Validate all form fields and return both errors and error field names."""
        errors = []
        error_fields = []
        
        # Required fields validation
        required_fields = {
            'student_id': 'Student ID',
            'student_name': 'Student Name', 
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'b_form_number': 'B-Form Number',
            'father_name': "Father's Name",
            'father_cnic': "Father's CNIC",
            'father_phone': "Father's Phone"
        }
        
        for field_name, display_name in required_fields.items():
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                
                if isinstance(widget, QLineEdit):
                    if not widget.text().strip():
                        errors.append(f"{display_name} is required")
                        error_fields.append(field_name)
                elif isinstance(widget, CustomComboBox):
                    if widget.currentIndex() <= 0:  # No selection or "Select..." option
                        errors.append(f"{display_name} must be selected")
                        error_fields.append(field_name)
                elif isinstance(widget, CustomDateEdit):
                    if self._is_date_empty(widget):
                        # Custom error message based on field type
                        if 'birth' in field_name.lower():
                            errors.append("Please select Birth Date")
                        elif 'admission' in field_name.lower():
                            errors.append("Please select Admission Date")
                        elif 'issue' in field_name.lower() or 'doi' in field_name.lower():
                            errors.append("Please select Issue Date")
                        elif 'exp' in field_name.lower():
                            errors.append("Please select Expiry Date")
                        else:
                            errors.append(f"Please select {display_name}")
                        error_fields.append(field_name)
                    elif 'birth' in field_name and widget.date() > QDate.currentDate():
                        errors.append(f"{display_name} cannot be in the future")
                        error_fields.append(field_name)
        
        # Phone format validation
        if 'father_phone' in self.student_fields:
            phone_widget = self.student_fields['father_phone']
            phone_text = phone_widget.text().replace('-', '')
            if phone_text and (len(phone_text) != 11 or not phone_text.startswith('03')):
                errors.append("Father's Phone must be 11 digits starting with 03")
                error_fields.append('father_phone')
        
        # Student ID uniqueness check (skip for current student when editing)
        if 'student_id' in self.student_fields:
            student_id_widget = self.student_fields['student_id']
            student_id = student_id_widget.text().strip()
            if student_id and self._check_student_id_exists(student_id):
                # Skip validation if this is the current student being edited
                if not (hasattr(self, 'current_student_id') and self.current_student_id == student_id):
                    errors.append(f"Student ID '{student_id}' already exists")
                    error_fields.append('student_id')
        
        return errors, error_fields
    
    def _validate_form(self):
        """Validate all form fields and return errors."""
        errors = []
        
        # Check required fields
        required_fields = [
            ('student_id', 'Student ID'),
            ('first_name', 'First Name'), 
            ('last_name', 'Last Name'),
            ('date_of_birth', 'Date of Birth'),
            ('gender', 'Gender'),
            ('cnic', 'CNIC'),
            ('school_id', 'School'),
            ('class_id', 'Class'),
            ('section', 'Section'),
            ('student_email', 'Student Email'),
            ('home_address', 'Home Address'),
            ('city', 'City'),
            ('father_name', 'Father Name'),
            ('father_cnic', 'Father CNIC'),
            ('father_phone', 'Father Phone'),
            ('mother_name', 'Mother Name'),
            ('emergency_contact_name', 'Emergency Contact Name'),
            ('emergency_contact_phone', 'Emergency Contact Phone'),
            ('emergency_contact_relation', 'Emergency Contact Relation')
        ]
        
        for field_name, field_label in required_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                value = ""
                
                if isinstance(widget, QLineEdit):
                    value = widget.text().strip()
                elif isinstance(widget, CustomComboBox):
                    value = widget.currentText()
                    if value in ["Select...", "Select School...", "Select Class...", "Select Section..."]:
                        value = ""
                elif isinstance(widget, QSpinBox):
                    value = str(widget.value())
                elif isinstance(widget, CustomDateEdit):
                    # Check if date is default or empty
                    if widget.date() == QDate.currentDate():
                        # If it's today's date for DOB, it might be unset
                        if field_name == 'date_of_birth':
                            value = ""
                    else:
                        value = widget.date().toString()
                
                if not value:
                    errors.append(f"{field_label} is required")
        
        # Validate CNIC format (13 digits)
        cnic_fields = ['cnic', 'father_cnic', 'mother_cnic']
        for field_name in cnic_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                if isinstance(widget, QLineEdit):
                    cnic = widget.text().replace('-', '').strip()
                    if cnic and (len(cnic) != 13 or not cnic.isdigit()):
                        field_label = field_name.replace('_', ' ').title()
                        errors.append(f"{field_label} must be 13 digits")
        
        # Validate phone numbers (11 digits starting with 0)
        phone_fields = ['student_phone', 'father_phone', 'mother_phone', 'guardian_phone', 'emergency_contact_phone']
        for field_name in phone_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                if isinstance(widget, QLineEdit):
                    phone = widget.text().replace('-', '').strip()
                    if phone and (len(phone) != 11 or not phone.startswith('0') or not phone.isdigit()):
                        field_label = field_name.replace('_', ' ').title()
                        errors.append(f"{field_label} must be 11 digits starting with 0")
        
        # Validate email format
        if 'student_email' in self.student_fields:
            email_widget = self.student_fields['student_email']
            if isinstance(email_widget, QLineEdit):
                email = email_widget.text().strip()
                if email and '@' not in email:
                    errors.append("Student Email must be a valid email address")
        
        # Check if Student ID already exists (if adding new student)
        if hasattr(self, 'current_student_id') and self.current_student_id is None:
            if 'student_id' in self.student_fields:
                student_id_widget = self.student_fields['student_id']
                if isinstance(student_id_widget, QSpinBox):
                    student_id = student_id_widget.value()
                    # Check if ID exists in database
                    try:
                        existing_student = self.db.get_student_by_id(student_id)
                        if existing_student:
                            errors.append(f"Student ID {student_id} already exists")
                    except Exception as e:
                        print(f"Error checking student ID: {e}")
        
        return errors
    
    def _collect_form_data(self):
        """Collect all form data into a dictionary."""
        data = {}
        
        # Get recipient type to determine which fields to exclude
        recipient_type = None
        if 'recipient_type' in self.student_fields:
            recipient_type = self.student_fields['recipient_type'].currentText()
        
        for field_name, widget in self.student_fields.items():
            # Skip disabled widgets (for conditional fields)
            if not widget.isEnabled():
                continue
            
            # Additional logic to exclude fields based on recipient type
            if recipient_type == "Principal":
                # Skip alternate fields when Principal is selected
                if hasattr(self, 'alternate_fields') and field_name in self.alternate_fields:
                    continue
            elif recipient_type == "Alternate":
                # Skip mother and household fields when Alternate is selected
                if hasattr(self, 'mother_fields') and field_name in self.mother_fields:
                    continue
                if hasattr(self, 'household_fields') and field_name in self.household_fields:
                    continue
                
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text().strip()
            elif isinstance(widget, CustomComboBox):
                current_text = widget.currentText()
                if current_text not in ["Select...", "Select School...", "Select Class...", "Select Section...", "Not Specified"]:
                    data[field_name] = current_text
                else:
                    data[field_name] = ""
                    
                # Get ID for database fields
                if field_name == "school_id" and widget.currentData():
                    data[field_name] = widget.currentData()
            elif isinstance(widget, QSpinBox):
                data[field_name] = widget.value()
            elif isinstance(widget, CustomDateEdit):
                # Define required date fields that must always be saved
                required_date_fields = ['date_of_birth', 'year_of_admission', 'year_of_admission_alt']
                
                # Save date for required fields or if user manually selected it
                if field_name in required_date_fields or (hasattr(widget, '_user_selected') and widget._user_selected):
                    data[field_name] = widget.date().toString("yyyy-MM-dd")
                else:
                    # For optional date fields, only save if not default current date
                    current_date = widget.date().toString("yyyy-MM-dd")
                    today = QDate.currentDate().toString("yyyy-MM-dd")
                    if current_date != today:
                        data[field_name] = current_date
                    else:
                        data[field_name] = ""
            elif isinstance(widget, QTextEdit):
                data[field_name] = widget.toPlainText().strip()
        
        # Auto-populate missing required fields for database compatibility
        self._auto_populate_required_fields(data)
        
        return data
        
    def _auto_populate_required_fields(self, data):
        """Auto-populate missing required database fields."""
        try:
            # If org_id is missing but we have a school selection, try to get org info
            if 'org_id' not in data or not data['org_id']:
                data['org_id'] = 1  # Default organization ID
                
            # If school_id is available, get related info from database
            if 'school_id' in data and data['school_id']:
                try:
                    school_info = self.db.get_school_info(data['school_id'])
                    if school_info:
                        # Set related IDs from school info
                        data['province_id'] = school_info.get('province_id', 1)
                        data['district_id'] = school_info.get('district_id', 1) 
                        data['union_council_id'] = school_info.get('union_council_id', 1)
                except:
                    # Fallback to defaults if school info fetch fails
                    pass
            
            # Set default values for missing required fields
            required_defaults = {
                'org_id': 1,
                'school_id': data.get('school_id', 1),
                'province_id': 1,
                'district_id': 1,
                'union_council_id': 1,
                'nationality_id': 1,
                'final_unique_codes': data.get('student_id', 'STU2025001'),
                'registration_number': data.get('student_id', 'REG2025001'),
                'class_teacher_name': 'Default Teacher',
                'students_bform_number': data.get('b_form_number', '12345-1234567-1'),
                'year_of_admission': data.get('date_of_birth', '2023-01-01'),
                'year_of_admission_alt': data.get('date_of_birth', '2023-01-01'),
                'household_size': 4,
                'mother_marital_status': 'Married',
                'mother_id_type': 'CNIC',
                'mother_cnic_doi': '2010-01-01',
                'mother_cnic_exp': '2030-01-01',
                'mother_mwa': 1,
                'household_role': 'Head',
                'hh_gender': data.get('gender', 'Male'),
                'hh_date_of_birth': data.get('date_of_birth', '1980-01-01'),
                'recipient_type': 'Principal'
            }
            
            # Only set defaults for missing fields
            for field, default_value in required_defaults.items():
                if field not in data or not data[field]:
                    data[field] = default_value
                    
            print(f"🔧 Auto-populated {len(required_defaults)} required fields")
            
        except Exception as e:
            print(f"❌ Error auto-populating required fields: {e}")
            # Set minimal defaults to prevent database errors
            minimal_defaults = {
                'org_id': 1, 'school_id': 1, 'province_id': 1, 'district_id': 1,
                'union_council_id': 1, 'nationality_id': 1,
                'final_unique_codes': 'STU2025001', 'registration_number': 'REG2025001',
                'class_teacher_name': 'Default Teacher'
            }
            for field, default_value in minimal_defaults.items():
                if field not in data or not data[field]:
                    data[field] = default_value
    
    def _populate_form_data(self, student_data):
        """Populate form fields with student data."""
        if not student_data:
            return
            
        for field_name, value in student_data.items():
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value) if value else "")
                elif isinstance(widget, CustomComboBox):
                    # Special handling for school_id field
                    if field_name == 'school_id' and value:
                        # Try to find by data value first (for school_id)
                        for i in range(widget.count()):
                            if widget.itemData(i) == value:
                                widget.setCurrentIndex(i)
                                print(f"🏫 Set school combo to index {i} for school_id: {value}")
                                break
                        else:
                            # Fallback to text search
                            index = widget.findText(str(value))
                            if index >= 0:
                                widget.setCurrentIndex(index)
                            else:
                                widget.setCurrentIndex(0)  # Default selection
                    else:
                        # Regular text-based combo box population
                        index = widget.findText(str(value) if value else "")
                        if index >= 0:
                            widget.setCurrentIndex(index)
                        else:
                            widget.setCurrentIndex(0)  # Default selection
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value) if value else 0)
                elif isinstance(widget, CustomDateEdit):
                    if value:
                        date = QDate.fromString(str(value), "yyyy-MM-dd")
                        if date.isValid():
                            widget.setDate(date)
                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(str(value) if value else "")
    
    def _save_student_data(self):
        """Save or update student data."""
        # Clear previous validation errors
        self._clear_validation_errors()
        
        # Debug info for troubleshooting
        print(f"🔍 DEBUG - Save operation starting:")
        print(f"  - is_editing: {getattr(self, 'is_editing', 'NOT SET')}")
        print(f"  - current_student_id: {getattr(self, 'current_student_id', 'NOT SET')}")
        if 'student_id' in self.student_fields:
            form_student_id = self.student_fields['student_id'].text().strip()
            print(f"  - form student_id: {form_student_id}")
            print(f"  - IDs match: {getattr(self, 'current_student_id', None) == form_student_id}")
        
        # Validate form first
        errors, error_fields = self._validate_form_with_fields()
        if errors:
            # Highlight error fields in red
            self._highlight_validation_errors(error_fields)
            
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            show_warning_message("Validation Error", error_message)
            return False
        
        # Collect form data
        data = self._collect_form_data()
        
        try:
            if hasattr(self, 'current_student_id') and self.current_student_id:
                # Update existing student - add student_id to data and include user info
                data['student_id'] = self.current_student_id
                
                # Get current user information
                user_id = self.current_user.id if self.current_user else None
                username = self.current_user.username if self.current_user else None
                user_phone = getattr(self.current_user, 'phone', None) if self.current_user else None
                
                success = self.db.update_student(data, user_id, username, user_phone)
                if success:
                    show_success_message(self, "Success", "Student updated successfully!")
                    # Close form and refresh data
                    self._close_form()
                    self._load_data()  # Refresh the student list
                    return True
                else:
                    show_critical_message("Error", "❌ Failed to update student.")
                    return False
            else:
                # Add new student
                success = self.db.add_student(data)
                if success:
                    show_success_message(self, "Success", "Student added successfully!")
                    self.student_form_dialog.accept()
                    self.load_students()  # Refresh the student list
                    return True
                else:
                    show_critical_message("Error", "Failed to add student.")
                    return False
        except Exception as e:
            show_critical_message("Database Error", f"An error occurred: {str(e)}")
            return False
    
    def _clear_layout(self, layout):
        """Recursively clear a layout."""
        if layout is not None:
            try:
                while layout.count():
                    child = layout.takeAt(0)
                    if child is not None:
                        if child.widget() is not None:
                            child.widget().deleteLater()
                        elif child.layout() is not None:
                            self._clear_layout(child.layout())
            except Exception as e:
                print(f"Error clearing layout: {e}")  # Debug output
    
    def _save_student(self):
        """Save the student data to database using new add_student method."""
        try:
            # Clear previous validation errors
            self._clear_validation_errors()
            
            # Validate form data first
            errors, error_fields = self._validate_form_with_fields()
            if errors:
                # Highlight error fields in red
                self._highlight_validation_errors(error_fields)
                
                if not self._show_validation_errors(errors):
                    return
            
            # Collect form data using enhanced method with conditional logic
            student_data = self._collect_form_data()
            
            # Handle school organizational data separately
            school_widget = self.student_fields.get('school_id')
            if school_widget and isinstance(school_widget, CustomComboBox):
                school_id = school_widget.currentData()
                if school_id:
                    student_data['school_id'] = school_id
                    
                    # Auto-populate organizational fields from school data
                    org_data = self.db.get_school_organizational_data(school_id)
                    if org_data:
                        print(f"Auto-adding organizational data: {org_data}")
                        # Add organizational IDs to student data
                        student_data.update(org_data)
            
            print(f"Final student data with org fields: {student_data}")
            
            # Determine if we're editing or adding
            if self.is_editing and self.current_student_id:
                print(f"🔄 Updating existing student ID: {self.current_student_id}")
                # Ensure student_id is in the data for update
                student_data['student_id'] = self.current_student_id
                # Update existing student with user information
                success = self.db.update_student(
                    student_data, 
                    user_id=1,  # TODO: Get from current session
                    username="admin",  # TODO: Get from current session
                    user_phone="N/A"  # TODO: Get from current session
                )
                action_text = "updated"
            else:
                print(f"➕ Adding new student")
                # Add new student with user information
                success = self.db.add_student(
                    student_data,
                    user_id=1,  # TODO: Get from current session
                    username="admin",  # TODO: Get from current session
                    user_phone="N/A"  # TODO: Get from current session
                )
                action_text = "added"
            
            if success:
                # Show success message
                show_success_message(
                    self, 
                    "Success", 
                    f"Student '{student_data.get('student_name', 'N/A')}' {action_text} successfully!\n\n"
                    f"Student ID: {student_data.get('student_id', 'N/A')}\n"
                    f"Class: {student_data.get('class', 'N/A')}\n"
                    f"Section: {student_data.get('section', 'N/A')}"
                )
                
                # Reset form and close
                self._reset_form()
                self._close_form()
                
                # Refresh the table data
                self._load_data()
                
            else:
                show_critical_message(
                    self, 
                    "Error", 
                    "❌ Failed to add student to database.\n\n"
                    "Please check the database connection and try again."
                )
                
        except Exception as e:
            show_critical_message(
                self, 
                "Error", 
                f"❌ An error occurred while saving student:\n\n{str(e)}\n\n"
                f"Please check your input and try again."
            )
            import traceback
            traceback.print_exc()
    
    def _reset_form(self):
        """Reset all form fields."""
        try:
            for field_name, widget in self.student_fields.items():
                if widget is None:
                    continue
                    
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, CustomComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, CustomDateEdit):
                    # Reset to current date but mark as not user selected
                    widget.setDate(QDate.currentDate())
                    if hasattr(widget, '_user_selected'):
                        widget._user_selected = False
                    if hasattr(widget, '_original_date'):
                        widget._original_date = QDate.currentDate()
                elif isinstance(widget, QTextEdit):
                    widget.clear()
        except Exception as e:
            print(f"Error resetting form: {e}")
            # Clear the fields dictionary to prevent further issues
            self.student_fields.clear()
    
    # Duplicate _close_form method removed - using the main one at line 1250
    
    def _load_student_data(self, student_id, student_data=None):
        """Load student data for editing."""
        print(f"Loading student data for ID: {student_id}")
        
        try:
            # Load complete student data from database
            complete_student_data = self.db.get_student_by_id(student_id)
            if not complete_student_data:
                show_warning_message("Error", "Student data not found in database.")
                return
            
            print(f"📊 Found complete student data: {list(complete_student_data.keys())}")
            
            # Populate form fields with database data
            self._populate_form_data(complete_student_data)
            
            print(f"✅ Student data loaded successfully for {complete_student_data.get('student_name', student_id)}")
            
        except Exception as e:
            print(f"❌ Error loading student data: {e}")
            show_critical_message("Error", f"Failed to load student data: {str(e)}")
            
            # Fallback to basic table data if database fails
            if student_data:
                print("📝 Using fallback table data...")
                # Load basic data from table as fallback
                if 'name' in student_data and 'student_name' in self.student_fields:
                    self.student_fields['student_name'].setText(student_data['name'])
                
                if 'id' in student_data and 'student_id' in self.student_fields:
                    self.student_fields['student_id'].setText(student_data['id'])
                
                if 'father_name' in student_data and 'father_name' in self.student_fields:
                    self.student_fields['father_name'].setText(student_data['father_name'])
                
                # Set class dropdown
                if 'class' in student_data and 'class' in self.student_fields:
                    class_combo = self.student_fields['class']
                    class_text = student_data['class']
                    index = class_combo.findText(class_text)
                    if index >= 0:
                        class_combo.setCurrentIndex(index)
                
                # Set section dropdown
                if 'section' in student_data and 'section' in self.student_fields:
                    section_combo = self.student_fields['section']
                    section_text = student_data['section']
                    index = section_combo.findText(section_text)
                    if index >= 0:
                        section_combo.setCurrentIndex(index)
    
    def _update_table_row(self, student_data):
        """Update the selected row in the table with new student data."""
        selected_row = self.students_table.currentRow()
        if selected_row >= 0:
            # Update ID
            if 'student_id' in student_data:
                id_item = QTableWidgetItem(str(student_data['student_id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(selected_row, 0, id_item)
            
            # Update Name
            if 'name' in student_data:
                name_item = QTableWidgetItem(student_data['name'])
                self.students_table.setItem(selected_row, 1, name_item)
            
            # Update Father Name
            if 'father_name' in student_data:
                father_name_item = QTableWidgetItem(student_data['father_name'])
                self.students_table.setItem(selected_row, 2, father_name_item)
            
            # Update Class
            if 'class' in student_data:
                class_item = QTableWidgetItem(student_data['class'])
                class_item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(selected_row, 3, class_item)
            
            # Update Section
            if 'section' in student_data:
                section_item = QTableWidgetItem(student_data['section'])
                section_item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(selected_row, 4, section_item)
            
            # Update Phone
            phone = student_data.get('student_phone', student_data.get('Alternate_phone', ''))
            if phone:
                phone_item = QTableWidgetItem(phone)
                self.students_table.setItem(selected_row, 5, phone_item)
            
            print(f"✅ Table row updated for student: {student_data.get('name', 'Unknown')}")
    
    def _add_table_row(self, student_data):
        """Add a new row to the table with student data."""
        row_count = self.students_table.rowCount()
        self.students_table.insertRow(row_count)
        
        # ID
        student_id = student_data.get('student_id', f"{row_count + 6:03d}")
        id_item = QTableWidgetItem(str(student_id))
        id_item.setTextAlignment(Qt.AlignCenter)
        self.students_table.setItem(row_count, 0, id_item)
        
        # Name
        name_item = QTableWidgetItem(student_data.get('name', ''))
        self.students_table.setItem(row_count, 1, name_item)
        
        # Father Name
        father_name_item = QTableWidgetItem(student_data.get('father_name', ''))
        self.students_table.setItem(row_count, 2, father_name_item)
        
        # Class
        class_item = QTableWidgetItem(student_data.get('class', ''))
        class_item.setTextAlignment(Qt.AlignCenter)
        self.students_table.setItem(row_count, 3, class_item)
        
        # Section
        section_item = QTableWidgetItem(student_data.get('section', ''))
        section_item.setTextAlignment(Qt.AlignCenter)
        self.students_table.setItem(row_count, 4, section_item)
        
        # Phone
        phone = student_data.get('student_phone', student_data.get('Alternate_phone', ''))
        phone_item = QTableWidgetItem(phone)
        self.students_table.setItem(row_count, 5, phone_item)
        
        # Actions
        actions_item = QTableWidgetItem("📋 Actions")
        actions_item.setTextAlignment(Qt.AlignCenter)
        self.students_table.setItem(row_count, 6, actions_item)
        
        print(f"✅ New student added to table: {student_data.get('name', 'Unknown')}")
    
    def _show_student_details_dialog(self, student_id, student_name):
        """Show comprehensive student details dialog with history."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📊 Complete Details - {student_name}")
        dialog.setModal(True)
        
        # Set dynamic sizing - no fixed size, let content determine size
        dialog.setSizeGripEnabled(True)  # Allow user to resize
        dialog.setMinimumSize(800, 400)  # Minimum size
        dialog.setMaximumSize(1200, 800) # Maximum size to fit most screens
        
        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel(f"👤 Complete Information: {student_name}")
        header_label
        layout.addWidget(header_label)
        
        # Create dynamic scroll area for single page content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Only when needed
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Only when needed
        scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)  # Adjust to content size
        scroll_area
        
        # Get complete student details from database
        try:
            # Fetch complete student data from database instead of table
            student_data = self.db.get_student_by_id(student_id)
            if not student_data:
                show_warning_message("Warning", "Student data not found in database.")
                return
            
            # Create single page content widget instead of tabs
            content_widget = self._create_single_page_details_view(student_data, student_id)
            
            # Add content widget to scroll area
            scroll_area.setWidget(content_widget)
            layout.addWidget(scroll_area)
            
            # Auto-adjust dialog size based on content
            dialog.adjustSize()  # Adjust to content size
            
            # Set dynamic size based on screen
            screen_geometry = self.geometry()
            max_width = min(1200, int(screen_geometry.width() * 0.9))
            max_height = min(800, int(screen_geometry.height() * 0.8))
            dialog.resize(max_width, max_height)
            
            # Button box
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec_()
            
        except Exception as e:
            show_critical_message("Error", f"Failed to load student details:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _create_details_personal_tab(self, student_data):
        """Create personal information display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create form layout
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        personal_info = [
            ("Student ID:", student_data.get('student_id', 'N/A')),
            ("Full Name:", student_data.get('student_name', 'N/A')),
            ("Date of Birth:", student_data.get('date_of_birth', 'N/A')),
            ("Gender:", student_data.get('gender', 'N/A')),
            ("CNIC/B-Form:", student_data.get('students_bform_number', 'N/A')),
            ("Address:", student_data.get('address', 'N/A')),
            ("Father's Name:", student_data.get('father_name', 'N/A')),
            ("Father's CNIC:", student_data.get('father_cnic', 'N/A')),
            ("Father's Phone:", student_data.get('father_phone', 'N/A')),
            ("Household Size:", student_data.get('household_size', 'N/A')),
            # Mother's Information
            ("Mother's Name:", student_data.get('mother_name', 'N/A')),
            ("Mother's Date of Birth:", student_data.get('mother_date_of_birth', 'N/A')),
            ("Mother's Marital Status:", student_data.get('mother_marital_status', 'N/A')),
            ("Mother's ID Type:", student_data.get('mother_id_type', 'N/A')),
            ("Mother's CNIC:", student_data.get('mother_cnic', 'N/A')),
            ("Mother's CNIC DOI:", student_data.get('mother_cnic_doi', 'N/A')),
            ("Mother's CNIC Exp:", student_data.get('mother_cnic_exp', 'N/A')),
            ("Mother's MWA:", student_data.get('mother_mwa', 'N/A')),
        ]
        
        row = 0
        for label_text, value in personal_info:
            label = QLabel(label_text)
            label
            
            value_label = QLabel(str(value))
            value_label
            
            form_layout.addWidget(label, row, 0)
            form_layout.addWidget(value_label, row, 1)
            row += 1
        
        layout.addLayout(form_layout)
        layout.addStretch()
        return tab
    
    def _create_details_academic_tab(self, student_data):
        """Create academic information display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create form layout
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        academic_info = [
            ("School Name:", student_data.get('school_name', 'N/A')),
            ("Organization:", student_data.get('organization_name', 'N/A')),
            ("Province:", student_data.get('province_name', 'N/A')),
            ("District:", student_data.get('district_name', 'N/A')),
            ("Union Council:", student_data.get('union_council_name', 'N/A')),
            ("Nationality:", student_data.get('nationality_name', 'N/A')),
            ("Class:", student_data.get('class', 'N/A')),
            ("Section:", student_data.get('section', 'N/A')),
            ("Registration Number:", student_data.get('registration_number', 'N/A')),
            ("Class Teacher Name:", student_data.get('class_teacher_name', 'N/A')),
            ("Year of Admission:", student_data.get('year_of_admission', 'N/A')),
            ("Year of Admission Alt:", student_data.get('year_of_admission_alt', 'N/A')),
        ]
        
        row = 0
        for label_text, value in academic_info:
            label = QLabel(label_text)
            label
            
            value_label = QLabel(str(value))
            value_label
            
            form_layout.addWidget(label, row, 0)
            form_layout.addWidget(value_label, row, 1)
            row += 1
        
        layout.addLayout(form_layout)
        layout.addStretch()
        return tab
    
    def _create_details_contact_tab(self, student_data):
        """Create contact information display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create form layout
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        contact_info = [
            ("Home Address:", student_data.get('address', 'N/A')),
            ("Father's Phone:", student_data.get('father_phone', 'N/A')),
            ("Nationality:", student_data.get('nationality_name', 'N/A')),
            # Household Head Information
            ("Household Role:", student_data.get('household_role', 'N/A')),
            ("Household Name:", student_data.get('household_name', 'N/A')),
            ("HH Gender:", student_data.get('hh_gender', 'N/A')),
            ("HH Date of Birth:", student_data.get('hh_date_of_birth', 'N/A')),
            ("Recipient Type:", student_data.get('recipient_type', 'N/A')),
            # Alternate/Guardian Information
            ("Alternate Name:", student_data.get('alternate_name', 'N/A')),
            ("Alternate Date of Birth:", student_data.get('alternate_date_of_birth', 'N/A')),
            ("Alternate Marital Status:", student_data.get('alternate_marital_status', 'N/A')),
            ("Alternate ID Type:", student_data.get('alternate_id_type', 'N/A')),
            ("Alternate CNIC:", student_data.get('alternate_cnic', 'N/A')),
            ("Alternate CNIC DOI:", student_data.get('alternate_cnic_doi', 'N/A')),
            ("Alternate CNIC Exp:", student_data.get('alternate_cnic_exp', 'N/A')),
            ("Alternate MWA:", student_data.get('alternate_mwa', 'N/A')),
            ("Alternate Relationship:", student_data.get('alternate_relationship_with_mother', 'N/A')),
        ]
        
        row = 0
        for label_text, value in contact_info:
            label = QLabel(label_text)
            label
            
            value_label = QLabel(str(value))
            value_label
            
            form_layout.addWidget(label, row, 0)
            form_layout.addWidget(value_label, row, 1)
            row += 1
        
        layout.addLayout(form_layout)
        layout.addStretch()
        return tab
    
    def _create_details_history_tab(self, student_id):
        """Create change history display tab with dynamic sizing."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)  # Reduced spacing between elements
        layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins
        
        # Make tab size adjustable to content
        tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Header - Compact design
        header_label = QLabel("Complete Change History")
        header_label.setProperty("class", "HistoryHeader")
        layout.addWidget(header_label)
        
        # History table - using custom table styling
        history_table = SMISTable(self)
        history_table.table.setColumnCount(6)
        history_table.table.setHorizontalHeaderLabels([
            "Date & Time", "Field Changed", "Old Value", "New Value", "Type", "Changed By"
        ])
        
        # Use SMISTable's built-in styling - no inline styles needed
        history_table.table.setAlternatingRowColors(True)
        
        # Load real history data from database
        try:
            history_records = self.db.get_student_history(student_id)
            print(f"Loaded {len(history_records)} history records for student {student_id}")
            
            if not history_records:
                # Show message if no history found
                history_records = [
                    {
                        'date_time': 'No data',
                        'field_changed': 'NO_HISTORY',
                        'old_value': '',
                        'new_value': 'No change history available for this student',
                        'change_type': 'INFO',
                        'changed_by': 'System'
                    }
                ]
        except Exception as e:
            print(f"❌ Error loading history: {e}")
            # Fallback to error message
            history_records = [
                {
                    'date_time': 'Error',
                    'field_changed': 'ERROR',
                    'old_value': '',
                    'new_value': f'Failed to load history: {str(e)}',
                    'change_type': 'ERROR',
                    'changed_by': 'System'
                }
            ]
        
        history_table.table.setRowCount(len(history_records))
        
        for row, record in enumerate(history_records):
            # Date & Time
            date_item = QTableWidgetItem(record.get('date_time', 'Unknown'))
            date_item.setTextAlignment(Qt.AlignCenter)
            history_table.table.setItem(row, 0, date_item)
            
            # Field Changed
            field_item = QTableWidgetItem(record.get('field_changed', 'N/A'))
            field_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            history_table.table.setItem(row, 1, field_item)
            
            # Old Value
            old_value = record.get('old_value', '')
            if len(old_value) > 100:  # Truncate very long values
                old_value = old_value[:100] + "..."
            old_item = QTableWidgetItem(old_value)
            old_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            old_item.setToolTip(record.get('old_value', ''))  # Show full value in tooltip
            history_table.table.setItem(row, 2, old_item)
            
            # New Value
            new_value = record.get('new_value', '')
            if len(new_value) > 100:  # Truncate very long values
                new_value = new_value[:100] + "..."
            new_item = QTableWidgetItem(new_value)
            new_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            new_item.setToolTip(record.get('new_value', ''))  # Show full value in tooltip
            history_table.table.setItem(row, 3, new_item)
            
            # Change Type
            change_type = record.get('change_type', 'UNKNOWN')
            type_item = QTableWidgetItem(change_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            if change_type == "INSERT":
                type_item.setBackground(QColor("#D1FAE5"))
                type_item.setForeground(QColor("#047857"))
            elif change_type == "UPDATE":
                type_item.setBackground(QColor("#FEF3C7"))
                type_item.setForeground(QColor("#D97706"))
            elif change_type == "DELETE":
                type_item.setBackground(QColor("#FEE2E2"))
                type_item.setForeground(QColor("#DC2626"))
            elif change_type == "ERROR":
                type_item.setBackground(QColor("#FEE2E2"))
                type_item.setForeground(QColor("#DC2626"))
            else:
                type_item.setBackground(QColor("#F3F4F6"))
                type_item.setForeground(QColor("#6B7280"))
            history_table.table.setItem(row, 4, type_item)
            
            # Changed By - Now showing proper usernames
            changed_by = record.get('changed_by', 'Unknown')
            changed_by_item = QTableWidgetItem(changed_by)
            changed_by_item.setTextAlignment(Qt.AlignCenter)
            # Highlight admin users with different color
            if changed_by.lower() == 'admin':
                changed_by_item.setBackground(QColor("#EBF8FF"))
                changed_by_item.setForeground(QColor("#1E40AF"))
            elif changed_by.lower() != 'unknown' and changed_by.lower() != 'system':
                changed_by_item.setBackground(QColor("#F0FDF4"))
                changed_by_item.setForeground(QColor("#166534"))
            history_table.table.setItem(row, 5, changed_by_item)
        
        # Auto resize columns based on content for better visibility
        header = history_table.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date & Time - fit content
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Field Changed - fit content
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Old Value - fit content
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # New Value - fit content  
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Change Type - fit content
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Changed By - fit content
        
        # Set minimum widths to ensure readability but allow expansion (reduced for better fit)
        history_table.table.setColumnWidth(0, 150)  # Date & Time minimum width
        history_table.table.setColumnWidth(1, 180)  # Field Changed minimum width
        history_table.table.setColumnWidth(2, 200)  # Old Value minimum width
        history_table.table.setColumnWidth(3, 200)  # New Value minimum width
        history_table.table.setColumnWidth(4, 100)  # Change Type minimum width
        history_table.table.setColumnWidth(5, 120)  # Changed By minimum width
        
        # Enable word wrap for better text display
        history_table.table.setWordWrap(True)
        
        # Allow horizontal stretching beyond table width for full content visibility
        header.setStretchLastSection(False)
        header.setCascadingSectionResizes(False)
        
        # Set row height for better content visibility (reduced from 50 to 40)
        history_table.table.verticalHeader().setDefaultSectionSize(40)
        
        # Auto-adjust table height dynamically based on content
        num_records = len(history_records)
        header_height = 30  # Header row height
        row_height = 40     # Data row height
        border_spacing = 8  # Spacing for borders and margins
        
        # Calculate optimal table height: header + (rows * row_height) + spacing
        optimal_height = header_height + (num_records * row_height) + border_spacing
        
        # Set minimum height (for at least 3 rows) but no maximum - let it grow
        min_height = header_height + (3 * row_height) + border_spacing
        
        # Use optimal height but ensure minimum
        table_height = max(min_height, optimal_height)
        
        # Instead of fixed height, set minimum height and let table expand naturally
        history_table.setMinimumHeight(table_height)
        
        # Make table responsive to content
        history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Enable table's own scrollbars for very large content
        history_table.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        history_table.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        print(f"📏 History table dynamic height: {num_records} records, min height: {table_height}px")
        
        layout.addWidget(history_table)
        
        # Summary info with real data - compact design
        latest_change = history_records[0].get('date_time', 'Unknown') if history_records else 'No changes'
        summary_label = QLabel(f"Total Changes: {len(history_records)} | Last Updated: {latest_change}")
        summary_label.setProperty("class", "HistorySummary")
        layout.addWidget(summary_label)
        
        return tab
    
    def refresh_data(self):
        """Public method to refresh data (called from main window)."""
        self._refresh_data()
        
    def _add_personal_info_fields(self, form_layout):
        """Add personal information fields to the form layout using form components."""
        # Personal Info Section Header
        section_label = FormLabel("Personal Information")
        section_label.setProperty("class", "FormSubheading")
        form_layout.addRow("", section_label)
        
        # Student ID (auto-generated or current when editing)
        if self.is_editing and self.current_student_id:
            id_field = InputField.create_field("text", "Student ID")
            id_field.setText(self.current_student_id)
            id_field.setReadOnly(True)
            self.student_fields["student_id"] = id_field
            form_layout.addRow(FormLabel("Student ID:"), id_field)
        
        # First Name (Required)
        first_name_field = InputField.create_field("text", "First Name")
        first_name_field.setProperty("is_required", True)
        self.student_fields["student_name"] = first_name_field
        form_layout.addRow(FormLabel("Student Name:"), first_name_field)
        
        # Father's Name (Required)
        father_name_field = InputField.create_field("text", "Father's Name")
        father_name_field.setProperty("is_required", True)
        self.student_fields["father_name"] = father_name_field
        form_layout.addRow(FormLabel("Father's Name:"), father_name_field)
        
        # Mother's Name
        mother_name_field = InputField.create_field("text", "Mother's Name")
        self.student_fields["mother_name"] = mother_name_field
        form_layout.addRow(FormLabel("Mother's Name:"), mother_name_field)
        
        # Date of Birth (Required)
        dob_field = InputField.create_field("date")
        dob_field.setProperty("is_required", True)
        self.student_fields["date_of_birth"] = dob_field
        form_layout.addRow(FormLabel("Date of Birth:"), dob_field)
        
        # Gender (Required)
        gender_field = InputField.create_field("combo", "Gender", ["Select Gender...", "Male", "Female", "Other"])
        gender_field.setProperty("is_required", True)
        self.student_fields["gender"] = gender_field
        form_layout.addRow(FormLabel("Gender:"), gender_field)
        
        # Blood Group
        blood_group_field = InputField.create_field("combo", "Blood Group", ["Select Blood Group...", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        self.student_fields["blood_group"] = blood_group_field
        form_layout.addRow(FormLabel("Blood Group:"), blood_group_field)
        
        # Religion
        religion_field = InputField.create_field("combo", "Religion", ["Select Religion...", "Islam", "Christianity", "Hinduism", "Buddhism", "Sikhism", "Other"])
        self.student_fields["religion"] = religion_field
        form_layout.addRow(FormLabel("Religion:"), religion_field)
        
        # Nationality
        nationality_field = InputField.create_field("text", "Nationality")
        self.student_fields["nationality"] = nationality_field
        form_layout.addRow(FormLabel("Nationality:"), nationality_field)
        
    def _add_academic_info_fields(self, form_layout):
        """Add academic information fields to the form layout using form components."""
        # Academic Info Section Header
        section_label = FormLabel("Academic Information")
        section_label.setProperty("class", "FormSubheading")
        form_layout.addRow("", section_label)
        
        # School (Required)
        schools = self._get_schools_from_database()
        school_field = InputField.create_field("combo", "School", ["Select School..."] + schools)
        school_field.setProperty("is_required", True)
        self.student_fields["school"] = school_field
        form_layout.addRow(FormLabel("School:"), school_field)
        
        # Class (Required)
        class_field = InputField.create_field("combo", "Class", ["Select Class..."])
        class_field.setProperty("is_required", True)
        class_field.setEnabled(False)
        self.student_fields["class"] = class_field
        form_layout.addRow(FormLabel("Class:"), class_field)
        
        # Section (Required)
        section_field = InputField.create_field("combo", "Section", ["Select Section..."])
        section_field.setProperty("is_required", True)
        section_field.setEnabled(False)
        self.student_fields["section"] = section_field
        form_layout.addRow(FormLabel("Section:"), section_field)
        
        # Roll Number (Required)
        roll_field = InputField.create_field("text", "Roll Number")
        roll_field.setProperty("is_required", True)
        self.student_fields["roll_number"] = roll_field
        form_layout.addRow(FormLabel("Roll Number:"), roll_field)
        
        # Admission Date
        admission_date_field = InputField.create_field("date")
        self.student_fields["admission_date"] = admission_date_field
        form_layout.addRow(FormLabel("Admission Date:"), admission_date_field)
        
        # Registration Number
        reg_field = InputField.create_field("text", "Registration Number")
        self.student_fields["registration_number"] = reg_field
        form_layout.addRow(FormLabel("Registration Number:"), reg_field)
        
    def _add_contact_info_fields(self, form_layout):
        """Add contact information fields to the form layout using form components."""
        # Contact Info Section Header
        section_label = FormLabel("Contact Information")
        section_label.setProperty("class", "FormSubheading")
        form_layout.addRow("", section_label)
        
        # Address (Required)
        address_field = InputField.create_field("text", "Home Address")
        address_field.setProperty("is_required", True)
        self.student_fields["address"] = address_field
        form_layout.addRow(FormLabel("Address:"), address_field)
        
        # City (Required)
        city_field = InputField.create_field("text", "City Name")
        city_field.setProperty("is_required", True)
        self.student_fields["city"] = city_field
        form_layout.addRow(FormLabel("City:"), city_field)
        
        # Father's Phone (Required)
        father_phone_field = InputField.create_field("phone")
        father_phone_field.setProperty("is_required", True)
        self.student_fields["father_phone"] = father_phone_field
        form_layout.addRow(FormLabel("Father's Phone:"), father_phone_field)
        
        # Father's CNIC
        father_cnic_field = InputField.create_field("cnic")
        self.student_fields["father_cnic"] = father_cnic_field
        form_layout.addRow(FormLabel("Father's CNIC:"), father_cnic_field)
        
        # Father's Occupation
        father_occupation_field = InputField.create_field("text", "Father's Occupation")
        self.student_fields["father_occupation"] = father_occupation_field
        form_layout.addRow(FormLabel("Father's Occupation:"), father_occupation_field)
        
        # Emergency Contact
        emergency_field = InputField.create_field("phone")
        self.student_fields["emergency_contact"] = emergency_field
        form_layout.addRow(FormLabel("Emergency Contact:"), emergency_field)
        
        # B-Form Number (Required)
        bform_field = InputField.create_field("text", "B-Form Number")
        bform_field.setProperty("is_required", True)
        self.student_fields["b_form_number"] = bform_field
        form_layout.addRow(FormLabel("B-Form Number:"), bform_field)

    def _create_single_page_details_view(self, student_data, student_id):
        """Create a single page view combining all student details and history."""
        # Main content widget
        content_widget = QWidget()
        content_widget
        
        # Main layout
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        # Create sections in a single page layout
        
        # 1. Personal Information Section
        personal_section = self._create_details_section("👤 Personal Information", [
            ("Student ID:", student_data.get('student_id', 'N/A')),
            ("Full Name:", student_data.get('student_name', 'N/A')),
            ("Date of Birth:", student_data.get('date_of_birth', 'N/A')),
            ("Gender:", student_data.get('gender', 'N/A')),
            ("CNIC/B-Form:", student_data.get('students_bform_number', 'N/A')),
            ("Address:", student_data.get('address', 'N/A')),
            ("Father's Name:", student_data.get('father_name', 'N/A')),
            ("Father's CNIC:", student_data.get('father_cnic', 'N/A')),
            ("Father's Phone:", student_data.get('father_phone', 'N/A')),
            ("Household Size:", student_data.get('household_size', 'N/A')),
            ("Mother's Name:", student_data.get('mother_name', 'N/A')),
            ("Mother's Date of Birth:", student_data.get('mother_date_of_birth', 'N/A')),
            ("Mother's Marital Status:", student_data.get('mother_marital_status', 'N/A')),
            ("Mother's CNIC:", student_data.get('mother_cnic', 'N/A')),
        ])
        main_layout.addWidget(personal_section)
        
        # 2. Academic Information Section
        academic_section = self._create_details_section("🎓 Academic Information", [
            ("School Name:", student_data.get('school_name', 'N/A')),
            ("Organization:", student_data.get('organization_name', 'N/A')),
            ("Province:", student_data.get('province_name', 'N/A')),
            ("District:", student_data.get('district_name', 'N/A')),
            ("Union Council:", student_data.get('union_council_name', 'N/A')),
            ("Nationality:", student_data.get('nationality_name', 'N/A')),
            ("Class:", student_data.get('class', 'N/A')),
            ("Section:", student_data.get('section', 'N/A')),
            ("Registration Number:", student_data.get('registration_number', 'N/A')),
            ("Class Teacher Name:", student_data.get('class_teacher_name', 'N/A')),
            ("Year of Admission:", student_data.get('year_of_admission', 'N/A')),
        ])
        main_layout.addWidget(academic_section)
        
        # 3. Contact Information Section
        contact_section = self._create_details_section("📞 Contact Information", [
            ("Recipient Type:", student_data.get('recipient_type', 'N/A')),
            ("Household Role:", student_data.get('household_role', 'N/A')),
            ("Household Name:", student_data.get('household_name', 'N/A')),
            ("HH Gender:", student_data.get('hh_gender', 'N/A')),
            ("HH Date of Birth:", student_data.get('hh_date_of_birth', 'N/A')),
            ("Alternate Name:", student_data.get('alternate_name', 'N/A')),
            ("Alternate Date of Birth:", student_data.get('alternate_date_of_birth', 'N/A')),
            ("Guardian CNIC:", student_data.get('guardian_cnic', 'N/A')),
        ])
        main_layout.addWidget(contact_section)
        
        # 4. Change History Section
        history_section = self._create_compact_history_section(student_id)
        main_layout.addWidget(history_section)
        
        return content_widget
    
    def _create_details_section(self, title, info_list):
        """Create a details section with title and 2-column grid layout."""
        section = QFrame()
        section
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel(title)
        title_label
        layout.addWidget(title_label)
        
        # Create 2-column grid for information
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(12)
        grid_layout.setHorizontalSpacing(30)
        
        row = 0
        col = 0
        
        for label_text, value in info_list:
            # Skip empty values
            if value == 'N/A' or not value:
                continue
                
            # Create label
            label = QLabel(label_text)
            label
            
            # Create value label
            value_label = QLabel(str(value))
            value_label
            value_label.setWordWrap(True)
            
            # Create a container for label and value
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(10)
            
            container_layout.addWidget(label)
            container_layout.addWidget(value_label, 1)
            
            # Add to grid
            grid_layout.addWidget(container, row, col)
            
            # Move to next position (2 columns)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        layout.addLayout(grid_layout)
        return section
    
    def _create_compact_history_section(self, student_id):
        """Create a compact history section for the single page view."""
        section = QFrame()
        section
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("📊 Change History")
        title_label
        layout.addWidget(title_label)
        
        # History table with compact design
        history_table = SMISTable()
        history_table.table.setColumnCount(4)
        history_table.table.setHorizontalHeaderLabels([
            "Date & Time", "Field Changed", "Old → New Value", "Changed By"
        ])
        
        # Load real history data from database
        try:
            history_records = self.db.get_student_history(student_id)
            print(f"📊 Found {len(history_records)} history records for student {student_id}")
        except Exception as e:
            print(f"❌ Error loading history: {e}")
            history_records = []
        
        history_table.table.setRowCount(len(history_records))
        
        for row, record in enumerate(history_records):
            # Date & Time (formatted)
            date_time = record.get('change_date', 'N/A')
            if date_time != 'N/A':
                try:
                    from datetime import datetime
                    if isinstance(date_time, str):
                        dt = datetime.fromisoformat(date_time.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                    else:
                        formatted_date = str(date_time)
                except:
                    formatted_date = str(date_time)
            else:
                formatted_date = date_time
            
            date_item = QTableWidgetItem(formatted_date)
            history_table.table.setItem(row, 0, date_item)
            
            # Field Changed
            field_item = QTableWidgetItem(record.get('field_name', 'N/A'))
            history_table.table.setItem(row, 1, field_item)
            
            # Old → New Value (combined)
            old_value = record.get('old_value', 'N/A')
            new_value = record.get('new_value', 'N/A')
            change_text = f"{old_value} → {new_value}"
            if len(change_text) > 50:
                change_text = change_text[:47] + "..."
            change_item = QTableWidgetItem(change_text)
            history_table.table.setItem(row, 2, change_item)
            
            # Changed By
            changed_by = record.get('changed_by', 'System')
            changed_by_item = QTableWidgetItem(changed_by)
            history_table.table.setItem(row, 3, changed_by_item)
        
        # Set compact table size
        history_table.table.setMaximumHeight(300)
        history_table.table.setAlternatingRowColors(True)
        
        # Auto-resize columns
        header = history_table.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date & Time
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Field Changed
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Old → New Value
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Changed By
        
        layout.addWidget(history_table)
        
        # History info label
        if len(history_records) == 0:
            info_label = QLabel("No change history available for this student.")
            info_label
            layout.addWidget(info_label)
        else:
            info_label = QLabel(f"Showing {len(history_records)} change record(s)")
            info_label
            layout.addWidget(info_label)
        
        return section
