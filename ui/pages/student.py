"""Student management page UI implementation."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QFrame, QGridLayout, 
                           QLineEdit, QMessageBox, QTableWidget, QHeaderView,
                           QScrollArea, QTableWidgetItem, QSplitter, QTextEdit,
                           QGroupBox, QFormLayout, QCheckBox, QDateEdit,
                           QSpinBox, QTabWidget, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QIcon, QColor, QRegExpValidator
from models.database import Database
from ui.styles.table_styles import apply_standard_table_style
from resources.style import COLORS, get_attendance_styles

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
        self.cancel_btn = None
        self.students_table = None
        self.search_input = None
        self.form_frame = None
        self.current_student_id = None
        self.is_editing = False
        
        # Form management variables
        self.form_dialog = None
        self.form_created = False
        
        # Initialize database
        self.db = Database()
        
        # Setup UI
        self._init_ui()
        self._load_data()
        self._connect_signals()

    def _init_ui(self):
        """Initialize the modern student management UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header section
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)
        
        # Main content with splitter for responsive design
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Student list and filters
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Student form
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (55% left, 45% right - more space for form)
        splitter.setSizes([550, 450])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        main_layout.addWidget(splitter)
        
        # Initially hide the form
        self.form_frame.setVisible(False)
        
    def _create_header(self):
        """Create the page header with title and actions."""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3B82F6, stop:1 #2563EB);
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 8px;
                max-height: 60px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(12)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        page_title = QLabel("👥 Student Management")
        page_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-family: 'Poppins Bold';
                font-weight: 700;
                margin: 0px;
                padding: (0px, 0px, 5px, 5px);
                border: none;
                background: transparent;
            }
        """)
        
        # page_subtitle = QLabel("Manage student records and information")
        # page_subtitle.setStyleSheet("""
        #     QLabel {
        #         color: rgba(255, 255, 255, 0.85);
        #         font-size: 12px;
        #         font-family: 'Poppins';
        #         margin: 0px;
        #         border: none;
        #     }
        # """)
        
        title_layout.addWidget(page_title)
        #title_layout.addWidget(page_subtitle)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.add_new_btn = QPushButton("➕ Add Student")
        self.add_new_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        actions_layout.addWidget(self.add_new_btn)
        actions_layout.addWidget(self.refresh_btn)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(actions_layout)
        
        return header_frame
    def _create_left_panel(self):
        """Create the left panel with filters and student list."""
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)
        
        panel_layout = QVBoxLayout(left_panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(15)
        
        # Filters section with attendance.py style design
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
        
        # Create 2x2 grid layout for basic filters and search
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)
        filter_grid.setColumnStretch(0, 1)  # Equal column widths
        filter_grid.setColumnStretch(1, 1)
        
        styles = get_attendance_styles()
        
        # Row 1, Column 1: School filter (with placeholder)
        self.school_combo = QComboBox()
        self.school_combo.addItem("Please Select School")  # Placeholder
        self._load_schools_data()  # Load from database
        self.school_combo.setStyleSheet(styles['combobox_standard'])
        self.school_combo.currentTextChanged.connect(self._on_school_changed)
        
        # Row 1, Column 2: Class filter (with placeholder)
        self.class_combo = QComboBox()
        self.class_combo.addItem("Please Select Class")  # Placeholder
        self._load_classes_data()  # Load from database
        self.class_combo.setStyleSheet(styles['combobox_standard'])
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        
        # Row 2, Column 1: Section filter (with placeholder)
        self.section_combo = QComboBox()
        self.section_combo.addItem("Please Select Section")  # Placeholder
        self._load_sections_data()  # Load from database
        self.section_combo.setStyleSheet(styles['combobox_standard'])
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        
        # Row 2, Column 2: Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, roll number, or phone...")
        self.search_input.setStyleSheet(styles['search_input'])
        self.search_input.textChanged.connect(self._apply_filters)
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)    # Row 1, Col 1
        filter_grid.addWidget(self.class_combo, 0, 1)     # Row 1, Col 2
        filter_grid.addWidget(self.section_combo, 1, 0)   # Row 2, Col 1
        filter_grid.addWidget(self.search_input, 1, 1)    # Row 2, Col 2
        filter_grid.addWidget(self.search_input, 1, 1)    # Row 2, Col 2
        
        filters_layout.addLayout(filter_grid)
        
        # Students table
        table_group = QGroupBox("📋 Student Records")
        table_group.setStyleSheet("""
            QGroupBox {
                font-family: 'Poppins Medium';
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)
        
        table_layout = QVBoxLayout(table_group)
        
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels([
            "🆔 Student ID", "👤 Student Name", "👨‍👦 Father Name", "📚 Class", "📝 Section"
        ])
        
        self.students_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                background: white;
                gridline-color: #E5E7EB;
                font-family: 'Poppins';
                font-size: 8px;
                selection-background-color: #3B82F6;
                selection-color: white;
                alternate-background-color: #F8FAFC;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #F1F5F9, stop:1 #E2E8F0);
                color: #1E293B;
                font-family: 'Poppins Bold';
                font-weight: 700;
                font-size: 13px;
                padding: 12px 10px;
                border: none;
                border-bottom: 3px solid #3B82F6;
                border-right: 1px solid #CBD5E1;
                text-align: center;
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
                border-right: none;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #E2E8F0;
                border-right: 1px solid #F1F5F9;
                background: white;
                color: #374151;
                font-weight: 500;
                outline: none;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                font-weight: 600;
                outline: none;
            }
            QTableWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #EBF4FF, stop:1 #DBEAFE);
                color: #1E40AF;
                border: none;
                outline: none;
            }
            QTableWidget::item:focus {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                outline: none;
            }
            QTableWidget::item:alternate {
                background: #F8FAFC;
            }
            QTableWidget::item:alternate:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                outline: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """)
        
        # Table properties for better readability and selection
        self.students_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.students_table.setSelectionMode(QTableWidget.SingleSelection)
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setSortingEnabled(True)
        self.students_table.verticalHeader().setVisible(False)
        self.students_table.setShowGrid(True)
        self.students_table.setFocusPolicy(Qt.StrongFocus)
        
        # Disable direct editing - users can only select and use edit button
        self.students_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set row height for comfortable reading
        self.students_table.verticalHeader().setDefaultSectionSize(35)
        
        # Auto resize columns for 5 columns only
        header = self.students_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Student Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Father Name
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Class
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Section
        
        table_layout.addWidget(self.students_table)
        
        # Table actions
        table_actions = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Edit Selected")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setStyleSheet(self._get_button_style('#F59E0B', '#D97706'))
        
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet(self._get_button_style('#EF4444', '#DC2626'))
        
        self.view_details_btn = QPushButton("👁️ View Details")
        self.view_details_btn.setEnabled(False)
        self.view_details_btn.setStyleSheet(self._get_button_style('#6B7280', '#4B5563'))
        
        table_actions.addWidget(self.edit_btn)
        table_actions.addWidget(self.delete_btn)
        table_actions.addWidget(self.view_details_btn)
        table_actions.addStretch()
        
        table_layout.addLayout(table_actions)
        
        # Add to panel
        panel_layout.addWidget(filters_frame)
        panel_layout.addWidget(table_group, 1)
        
        return left_panel
    
    def _create_right_panel(self):
        """Create the right panel with student form."""
        self.form_frame = QFrame()
        self.form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                min-height: 500px;
                max-height: 700px;
            }
        """)
        
        return self.form_frame
        return self.form_frame
    
    def _get_combo_style(self):
        """Get standard combobox styling."""
        return """
            QComboBox {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Poppins';
                font-size: 14px;
                background: white;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #3B82F6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6B7280;
                margin-right: 5px;
            }
        """
    
    def _get_button_style(self, color, hover_color):
        """Get standard button styling."""
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
            QPushButton:pressed {{
                background: {hover_color};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background: #D1D5DB;
                color: #9CA3AF;
            }}
        """
    
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
            
            print(f"📋 Loading students with filters: School ID={school_id}, Class={class_name}, Section={section}")
            
            # Get students using Database class method
            students_data = self.db.get_students(school_id=school_id, class_name=class_name, section=section)
            
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
            QMessageBox.warning(self, "Data Load Error", f"Failed to load student data: {str(e)}")
            # Fallback to empty table
            self._populate_table([])
    
    def _get_schools_from_database(self):
        """Fetch schools from database for combo box."""
        try:
            schools = self.db.get_schools()
            return [school.get('name', f"School {school.get('id', '')}") for school in schools]
        except Exception as e:
            print(f"Error fetching schools: {e}")
            return ["School 1", "School 2", "School 3"]  # Fallback
    
    def _get_organizations_from_database(self):
        """Fetch organizations from database for combo box."""
        try:
            # Assuming organizations table exists or using dummy data
            organizations = ["Organization 1", "Organization 2", "Organization 3", "Government", "Private", "NGO"]
            return organizations
        except Exception as e:
            print(f"Error fetching organizations: {e}")
            return ["Organization 1", "Organization 2", "Organization 3"]  # Fallback
    
    def _get_provinces_from_database(self):
        """Fetch provinces from database for combo box."""
        try:
            # Common Pakistani provinces
            provinces = ["Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan", "Gilgit-Baltistan", "Azad Kashmir", "Islamabad Capital Territory"]
            return provinces
        except Exception as e:
            print(f"Error fetching provinces: {e}")
            return ["Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan"]  # Fallback
    
    def _get_districts_from_database(self):
        """Fetch districts from database for combo box."""
        try:
            # Common Pakistani districts (sample)
            districts = ["Lahore", "Karachi", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala"]
            return districts
        except Exception as e:
            print(f"Error fetching districts: {e}")
            return ["Lahore", "Karachi", "Islamabad", "Rawalpindi"]  # Fallback
    
    def _get_union_councils_from_database(self):
        """Fetch union councils from database for combo box."""
        try:
            # Sample union councils
            union_councils = ["UC-1", "UC-2", "UC-3", "UC-4", "UC-5", "UC-6", "UC-7", "UC-8", "UC-9", "UC-10"]
            return union_councils
        except Exception as e:
            print(f"Error fetching union councils: {e}")
            return ["UC-1", "UC-2", "UC-3", "UC-4"]  # Fallback
    
    def _get_nationalities_from_database(self):
        """Fetch nationalities from database for combo box."""
        try:
            # Common nationalities
            nationalities = ["Pakistani", "Indian", "Afghan", "Bangladeshi", "Sri Lankan", "Chinese", "American", "British", "Other"]
            return nationalities
        except Exception as e:
            print(f"Error fetching nationalities: {e}")
            return ["Pakistani", "Indian", "Afghan", "Other"]  # Fallback
    
    def _populate_table(self, students):
        """Populate the students table with data and improved styling."""
        self.students_table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # Student ID with smaller font
            id_item = QTableWidgetItem(str(student["id"]))  # Keep original ID format
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFont(QFont('Poppins', 8))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.setItem(row, 0, id_item)
            
            # Student Name with smaller font
            name_item = QTableWidgetItem(student["name"].title())
            name_item.setFont(QFont('Poppins', 8))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.setItem(row, 1, name_item)
            
            # Father Name with smaller font
            father_name_item = QTableWidgetItem(student.get("father_name", "N/A").title())
            father_name_item.setFont(QFont('Poppins', 8))
            father_name_item.setFlags(father_name_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.setItem(row, 2, father_name_item)
            
            # Class with smaller font
            class_item = QTableWidgetItem(student["class"])
            class_item.setTextAlignment(Qt.AlignCenter)
            class_item.setFont(QFont('Poppins', 8))
            class_item.setFlags(class_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.setItem(row, 3, class_item)
            
            # Section with smaller font
            section_item = QTableWidgetItem(student["section"])
            section_item.setTextAlignment(Qt.AlignCenter)
            section_item.setFont(QFont('Poppins', 8))
            section_item.setFlags(section_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.students_table.setItem(row, 4, section_item)
    
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
        self.students_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.students_table.itemDoubleClicked.connect(self._on_double_click)
        
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
                QMessageBox.critical(self, "Error", "Form frame not available.")
                return
            
            # Hide form if already visible and reset
            if self.form_frame.isVisible():
                self.form_frame.setVisible(False)
                self._clear_form_safely()
            
            # Create fresh form
            self._create_complete_form()
            
            # Show the form
            self.form_frame.setVisible(True)
            
            # Clear all input fields for new student
            self._clear_form_fields()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Add Student form:\n{str(e)}")
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
    
    def _clear_form_fields(self):
        """Clear all form field values."""
        try:
            for field_name, widget in self.student_fields.items():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)  # Reset to first item (usually "Select...")
                elif isinstance(widget, QSpinBox):
                    widget.setValue(widget.minimum())
                elif isinstance(widget, QDateEdit):
                    widget.setDate(QDate.currentDate())
                elif isinstance(widget, QTextEdit):
                    widget.clear()
        except Exception as e:
            print(f"Error clearing form fields: {e}")
    
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
                elif isinstance(widget, QComboBox):
                    if widget.currentText() in ["Select...", ""]:
                        errors.append(f"{display_name} must be selected")
                elif isinstance(widget, QDateEdit):
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
        
        # Student ID uniqueness check
        if 'student_id' in self.student_fields:
            student_id = self.student_fields['student_id'].text().strip()
            if student_id and self._check_student_id_exists(student_id):
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
            QMessageBox.warning(self, "Form Validation", error_message)
            return False
    def _show_validation_errors(self, errors):
        """Display validation errors to user."""
        if errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Form Validation", error_message)
            return False
        return True
    
    def _clear_form_fields(self):
        """Clear all form input fields."""
        try:
            for field_name, field_widget in self.student_fields.items():
                if hasattr(field_widget, 'clear'):
                    field_widget.clear()
                elif hasattr(field_widget, 'setCurrentIndex'):
                    field_widget.setCurrentIndex(0)
                elif hasattr(field_widget, 'setDate'):
                    field_widget.setDate(QDate.currentDate())
                elif hasattr(field_widget, 'setValue'):
                    field_widget.setValue(0)
                elif hasattr(field_widget, 'setChecked'):
                    field_widget.setChecked(False)
        except Exception as e:
            print(f"Error clearing form fields: {e}")
    
    def _create_complete_form(self):
        """Create a complete form with tabs for student details."""
        try:
            # Prevent multiple form creation
            if self.form_created:
                return
            
            # Clear any existing layout first
            self._clear_form_safely()
            
            # Create main form layout with better structure
            form_layout = QVBoxLayout()
            form_layout.setContentsMargins(10, 0, 10, 5)  # Reduced side margins
            form_layout.setSpacing(8)  # Better spacing for readability
            
            # Form header with better positioning
            # title_label = QLabel("➕ Add New Student")
            # title_label.setStyleSheet("""
            #     QLabel {
            #         font-family: 'Poppins Medium';
            #         font-size: 16px;
            #         font-weight: 600;
            #         color: #374151;
            #         background: transparent;
            #         border: none;
            #         padding: 5px 0px 5px 0px;
            #         margin: 0px;
            #     }
            # """)
            
            # Create tab widget with reduced spacing
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                    background: white;
                    margin-top: 0px;
                    min-height: 300px;
                }
                QTabBar::tab {
                    background: #F3F4F6;
                    color: #374151;
                    padding: 8px 20px;
                    margin-right: 8px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-family: 'Poppins Medium';
                    font-weight: 600;
                    font-size: 12px;
                    min-height: 30px;
                    min-width: 140px;
                    text-align: center;
                }
                QTabBar::tab:selected {
                    background: #3B82F6;
                    color: white;
                }
                QTabBar::tab:hover {
                    background: #E5E7EB;
                }
            """)
            
            # Set tab bar to expand horizontally
            tab_widget.tabBar().setExpanding(True)
            
            # Add tabs
            personal_tab = self._create_personal_info_tab()
            academic_tab = self._create_academic_info_tab()
            contact_tab = self._create_contact_info_tab()
            
            tab_widget.addTab(personal_tab, "👤 Personal Info")
            tab_widget.addTab(academic_tab, "🎓 Academic Info")
            tab_widget.addTab(contact_tab, "📞 Contact Info")
            
            # Form buttons with proper spacing
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(8)  # Better button spacing
            buttons_layout.setContentsMargins(10, 10, 10, 5)  # Proper margins for alignment
            
            # Close button
            close_btn = QPushButton("❌ Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-family: 'Poppins Medium';
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background: #DC2626;
                }
                QPushButton:pressed {
                    background: #B91C1C;
                    transform: translateY(1px);
                }
            """)
            close_btn.clicked.connect(lambda: self.form_frame.setVisible(False))
            
            # Reset button
            reset_btn = QPushButton("🔄 Reset")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background: #F59E0B;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-family: 'Poppins Medium';
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background: #D97706;
                }
                QPushButton:pressed {
                    background: #B45309;
                    transform: translateY(1px);
                }
            """)
            reset_btn.clicked.connect(self._reset_form)
            
            # Cancel button
            self.cancel_btn = QPushButton("⚠️ Cancel")
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #6B7280;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-family: 'Poppins Medium';
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background: #4B5563;
                }
                QPushButton:pressed {
                    background: #374151;
                    transform: translateY(1px);
                }
            """)
            self.cancel_btn.clicked.connect(self._close_form)
            
            # Save button
            self.save_btn = QPushButton("💾 Save Student")
            self.save_btn.setStyleSheet("""
                QPushButton {
                    background: #10B981;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-family: 'Poppins Medium';
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 110px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background: #059669;
                }
                QPushButton:pressed {
                    background: #047857;
                    transform: translateY(1px);
                }
            """)
            self.save_btn.clicked.connect(self._save_student)
            
            # Add buttons to layout (Close, Reset, Cancel, Save)
            buttons_layout.addWidget(close_btn)
            buttons_layout.addStretch()
            buttons_layout.addWidget(reset_btn)
            buttons_layout.addWidget(self.cancel_btn)
            buttons_layout.addWidget(self.save_btn)
            
            # Add to form layout
            # form_layout.addWidget(title_label)
            form_layout.addWidget(tab_widget)  # Give maximum space to tabs
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
        selected_row = self.students_table.currentRow()
        if selected_row >= 0:
            try:
                # Safely get table items with null checks
                id_item = self.students_table.item(selected_row, 0)
                name_item = self.students_table.item(selected_row, 1)
                father_name_item = self.students_table.item(selected_row, 2)
                class_item = self.students_table.item(selected_row, 3)
                section_item = self.students_table.item(selected_row, 4)
                phone_item = self.students_table.item(selected_row, 5)
                
                if not all([id_item, name_item, father_name_item, class_item, section_item, phone_item]):
                    QMessageBox.warning(self, "Error", "Unable to read student data. Please refresh and try again.")
                    return
                
                student_id = id_item.text()
                student_name = name_item.text()
                student_father_name = father_name_item.text()
                student_class = class_item.text()
                student_section = section_item.text()
                student_phone = phone_item.text()
                
                self.is_editing = True
                self.current_student_id = student_id
                self._show_form(f"Edit Student - {student_name}")
                
                # Load student data into form
                self._load_student_data(student_id, {
                    'id': student_id,
                    'name': student_name,
                    'father_name': student_father_name,
                    'class': student_class,
                    'section': student_section,
                    'phone': student_phone
                })
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to edit student: {str(e)}")
        else:
            QMessageBox.information(self, "No Selection", "Please select a student to edit.")
    
    def _delete_student(self):
        """Delete the selected student."""
        selected_row = self.students_table.currentRow()
        if selected_row >= 0:
            try:
                name_item = self.students_table.item(selected_row, 1)
                if not name_item:
                    QMessageBox.warning(self, "Error", "Unable to read student data. Please refresh and try again.")
                    return
                    
                student_name = name_item.text()
                
                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete student '{student_name}'?\n\nThis action cannot be undone.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    id_item = self.students_table.item(selected_row, 0)
                    if not id_item:
                        QMessageBox.warning(self, "Error", "Unable to read student ID. Please refresh and try again.")
                        return
                        
                    student_id = id_item.text()
                    # TODO: Delete from database
                    self.students_table.removeRow(selected_row)
                    self.student_deleted.emit(student_id)
                    QMessageBox.information(self, "Success", f"Student '{student_name}' has been deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete student: {str(e)}")
        else:
            QMessageBox.information(self, "No Selection", "Please select a student to delete.")
    
    def _view_details(self):
        """View detailed information about the selected student."""
        selected_row = self.students_table.currentRow()
        if selected_row >= 0:
            try:
                id_item = self.students_table.item(selected_row, 0)
                name_item = self.students_table.item(selected_row, 1)
                
                if not all([id_item, name_item]):
                    QMessageBox.warning(self, "Error", "Unable to read student data. Please refresh and try again.")
                    return
                    
                student_id = id_item.text()
                student_name = name_item.text()
                
                # Show detailed student information dialog with history
                self._show_student_details_dialog(student_id, student_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to view student details: {str(e)}")
        else:
            QMessageBox.information(self, "No Selection", "Please select a student to view details.")
    
    def _on_selection_changed(self):
        """Handle table selection changes with improved feedback."""
        has_selection = len(self.students_table.selectedItems()) > 0
        current_row = self.students_table.currentRow()
        
        # Enable/disable buttons based on selection
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.view_details_btn.setEnabled(has_selection)
        
        # Update button text to show selected student info
        if has_selection and current_row >= 0:
            try:
                student_name = self.students_table.item(current_row, 1).text()
                student_id = self.students_table.item(current_row, 0).text()
                
                self.edit_btn.setText(f"✏️ Edit {student_name}")
                self.delete_btn.setText(f"🗑️ Delete {student_name}")
                self.view_details_btn.setText(f"👁️ View {student_name}")
                
                # Highlight the entire row
                for col in range(self.students_table.columnCount()):
                    item = self.students_table.item(current_row, col)
                    if item:
                        item.setSelected(True)
                        
            except (AttributeError, IndexError):
                # Fallback to default text
                self.edit_btn.setText("✏️ Edit Selected")
                self.delete_btn.setText("🗑️ Delete Selected") 
                self.view_details_btn.setText("👁️ View Details")
        else:
            # Reset to default text when no selection
            self.edit_btn.setText("✏️ Edit Selected")
            self.delete_btn.setText("🗑️ Delete Selected")
            self.view_details_btn.setText("👁️ View Details")
    
    def _on_double_click(self, item):
        """Handle double-click on table item to show view details."""
        try:
            if item:  # Any column can trigger view details now
                self._view_details()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Double-click handler error: {str(e)}")
    
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
            for row in range(self.students_table.rowCount()):
                show_row = True
                
                if search_text:
                    row_text = ""
                    for col in range(self.students_table.columnCount() - 1):  # Exclude actions column
                        item = self.students_table.item(row, col)
                        if item:
                            row_text += item.text().lower() + " "
                    
                    if search_text not in row_text:
                        show_row = False
                
                self.students_table.setRowHidden(row, not show_row)
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
        QMessageBox.information(self, "Success", "🔄 Student data refreshed successfully!")
    
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
                    if isinstance(widget, QComboBox):
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
            # Check if form_frame exists
            if not self.form_frame:
                QMessageBox.critical(self, "Error", "Form frame is not initialized.")
                return
                
            # Clear student fields dictionary to prevent stale references
            self.student_fields.clear()
            
            # Clear existing layout if any
            if self.form_frame.layout():
                # Simple cleanup - just remove the layout
                self.form_frame.setLayout(None)
            
            # Create comprehensive form
            form_layout = QVBoxLayout()
            form_layout.setContentsMargins(20, 20, 20, 20)
            form_layout.setSpacing(20)
        
            # Form header
            header_layout = QHBoxLayout()
        
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins Bold';
                    font-size: 24px;
                    color: #374151;
                    margin: 0px;
                    border: none;
                }
            """)
            
            close_btn = QPushButton("❌")
            close_btn.setFixedSize(40, 40)
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #DC2626;
                }
            """)
            close_btn.clicked.connect(self._close_form)
            
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            header_layout.addWidget(close_btn)
        
            # Form content with tabs
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                    background: white;
                }
                QTabBar::tab {
                    background: #F3F4F6;
                    color: #374151;
                    padding: 12px 30px;
                    margin-right: 8px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-family: 'Poppins Medium';
                    font-weight: 600;
                    font-size: 13px;
                    min-width: 150px;
                    text-align: center;
                }
                QTabBar::tab:selected {
                    background: #3B82F6;
                    color: white;
                }
                QTabBar::tab:hover {
                    background: #E5E7EB;
                }
            """)
            
            # Set tab bar to expand horizontally
            tab_widget.tabBar().setExpanding(True)
            
            # Personal Information Tab
            personal_tab = QWidget()  
            tab_widget.addTab(personal_tab, "👤 Personal Info")

            # Academic Information Tab
            academic_tab = QWidget()  
            tab_widget.addTab(academic_tab, "🎓 Academic Info")

            # Contact Information Tab
            contact_tab = QWidget()  
            tab_widget.addTab(contact_tab, "📞 Contact Info")
            
            # Form buttons
            buttons_layout = QHBoxLayout()
            
            self.save_btn = QPushButton("💾 Save Student")
            self.save_btn.setStyleSheet(self._get_button_style('#10B981', '#059669'))
            
            self.cancel_btn = QPushButton("❌ Cancel")
            self.cancel_btn.setStyleSheet(self._get_button_style('#6B7280', '#4B5563'))
            
            reset_btn = QPushButton("🔄 Reset Form")
            reset_btn.setStyleSheet(self._get_button_style('#F59E0B', '#D97706'))
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(reset_btn)
            buttons_layout.addWidget(self.cancel_btn)
            buttons_layout.addWidget(self.save_btn)
            
            # Connect button signals
            self.save_btn.clicked.connect(self._save_student)
            self.cancel_btn.clicked.connect(self._close_form)
            reset_btn.clicked.connect(self._reset_form)
        
            # Add to form layout
            form_layout.addLayout(header_layout)
            form_layout.addWidget(tab_widget, 1)
            form_layout.addLayout(buttons_layout)
            
            # Set the layout to the form frame
            self.form_frame.setLayout(form_layout)
            
            # Make form visible after everything is set up
            self.form_frame.setVisible(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create form:\n{str(e)}")
            print(f"Form creation error: {e}")  # Debug output
    
    def _close_form(self):
        """Properly close and cleanup the form."""
        try:
            # Hide form first
            if self.form_frame:
                self.form_frame.setVisible(False)
            
            # Clear form safely
            self._clear_form_safely()
            
            # Reset editing state
            self.is_editing = False
            self.current_student_id = None
            
            # Reset form created flag
            self.form_created = False
                
        except Exception as e:
            print(f"Error closing form: {e}")
            # Force hide the form even if cleanup fails
            try:
                if self.form_frame:
                    self.form_frame.setVisible(False)
            except:
                pass
    
    def _create_personal_info_tab(self):
        """Create personal information tab."""
        tab = QWidget()
        
        # Create scroll area for the tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
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
            ("Gender*", "gender", "combo", True, [["Boy", "Girl", "Other"]]),
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
            if is_required:
                label.setStyleSheet("""
                    QLabel {
                        color: #DC2626; 
                        font-family: 'Poppins Medium'; 
                        font-weight: 700;
                        font-size: 13px;
                        min-height: 38px;
                        max-height: 38px;
                        padding: 8px 0px;
                    }
                """)
            else:
                label.setStyleSheet("""
                    QLabel {
                        color: #374151; 
                        font-family: 'Poppins Medium'; 
                        font-weight: 600;
                        font-size: 13px;
                        min-height: 38px;
                        max-height: 38px;
                        padding: 8px 0px;
                    }
                """)
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
                    widget.setObjectName("required_field")
                    
            elif field_type == "cnic":
                widget = QLineEdit()
                # Strict CNIC validator: exactly 13 digits with optional hyphens
                cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{5}-?[0-9]{7}-?[0-9]{1}$'))
                widget.setValidator(cnic_validator)
                widget.setPlaceholderText("12345-1234567-1 (13 digits)")
                widget.setMaxLength(15)  # Allow for hyphens
                if is_required:
                    widget.setObjectName("required_field")
                    
            elif field_type == "phone":
                widget = QLineEdit()
                # Pakistani phone validator: 11 digits starting with 03
                phone_validator = QRegExpValidator(QRegExp(r'^03[0-9]{2}-?[0-9]{7}$'))
                widget.setValidator(phone_validator)
                widget.setPlaceholderText("0300-1234567 (11 digits)")
                widget.setMaxLength(12)  # Allow for hyphen
                if is_required:
                    widget.setObjectName("required_field")
                    
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
                widget = QDateEdit()
                if "birth" in field_name.lower() or "dob" in field_name.lower():
                    widget.setDate(QDate.currentDate().addYears(-20))  # Default age 20
                elif "doi" in field_name.lower():
                    widget.setDate(QDate.currentDate().addYears(-5))   # CNIC issued 5 years ago
                elif "exp" in field_name.lower():
                    widget.setDate(QDate.currentDate().addYears(5))    # Expires in 5 years
                else:
                    widget.setDate(QDate.currentDate())
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd-MMM-yyyy")
                if is_required:
                    widget.setObjectName("required_field")
                    
            elif field_type == "combo":
                widget = QComboBox()
                if options and len(options) > 0:
                    # Handle both direct list and nested list structures
                    if isinstance(options[0], list):
                        combo_options = options[0]  # Nested: [["Father", "Mother", ...]]
                    else:
                        combo_options = options  # Direct: ["Male", "Female"]
                    
                    if is_required:
                        widget.addItems(["Select..."] + combo_options)
                        widget.setObjectName("required_field")
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
                widget = QComboBox()
                schools = self._get_schools_from_database()
                if is_required:
                    widget.addItems(["Select School..."] + schools)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + schools)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "school_combo")
                    
            elif field_type == "org_combo":
                widget = QComboBox()
                organizations = self._get_organizations_from_database()
                if is_required:
                    widget.addItems(["Select Organization..."] + organizations)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + organizations)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "org_combo")
                    
            elif field_type == "province_combo":
                widget = QComboBox()
                provinces = self._get_provinces_from_database()
                if is_required:
                    widget.addItems(["Select Province..."] + provinces)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + provinces)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "province_combo")
                    
            elif field_type == "district_combo":
                widget = QComboBox()
                districts = self._get_districts_from_database()
                if is_required:
                    widget.addItems(["Select District..."] + districts)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + districts)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "district_combo")
                    
            elif field_type == "union_council_combo":
                widget = QComboBox()
                union_councils = self._get_union_councils_from_database()
                if is_required:
                    widget.addItems(["Select Union Council..."] + union_councils)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + union_councils)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "union_council_combo")
                    
            elif field_type == "nationality_combo":
                widget = QComboBox()
                nationalities = self._get_nationalities_from_database()
                if is_required:
                    widget.addItems(["Select Nationality..."] + nationalities)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + nationalities)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "nationality_combo")
            
            # Apply styling based on required status
            if is_required:
                widget.setStyleSheet(self._get_required_input_style())
            else:
                widget.setStyleSheet(self._get_input_style())
                
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
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
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
            if is_required:
                label.setStyleSheet("""
                    QLabel {
                        color: #DC2626; 
                        font-family: 'Poppins Medium'; 
                        font-weight: 700;
                        font-size: 13px;
                        min-height: 38px;
                        max-height: 38px;
                        padding: 8px 0px;
                    }
                """)
            else:
                label.setStyleSheet("""
                    QLabel {
                        color: #374151; 
                        font-family: 'Poppins Medium'; 
                        font-weight: 600;
                        font-size: 13px;
                        min-height: 38px;
                        max-height: 38px;
                        padding: 8px 0px;
                    }
                """)
            label.setAlignment(Qt.AlignVCenter)
            
            # Create widget based on type
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {label_text.replace('*', '').lower()}")
                
            elif field_type == "school_combo":
                widget = QComboBox()
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
                widget = QComboBox()
                organizations = self._get_organizations_from_database()
                if is_required:
                    widget.addItems(["Select Organization..."] + organizations)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + organizations)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "org_combo")
                    
            elif field_type == "province_combo":
                widget = QComboBox()
                provinces = self._get_provinces_from_database()
                if is_required:
                    widget.addItems(["Select Province..."] + provinces)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + provinces)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "province_combo")
                    
            elif field_type == "district_combo":
                widget = QComboBox()
                districts = self._get_districts_from_database()
                if is_required:
                    widget.addItems(["Select District..."] + districts)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + districts)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "district_combo")
                    
            elif field_type == "union_council_combo":
                widget = QComboBox()
                union_councils = self._get_union_councils_from_database()
                if is_required:
                    widget.addItems(["Select Union Council..."] + union_councils)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + union_councils)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "union_council_combo")
                    
            elif field_type == "nationality_combo":
                widget = QComboBox()
                nationalities = self._get_nationalities_from_database()
                if is_required:
                    widget.addItems(["Select Nationality..."] + nationalities)
                    widget.setObjectName("required_field")
                else:
                    widget.addItems(["Not Specified"] + nationalities)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "nationality_combo")
                    
            elif field_type == "combo":
                widget = QComboBox()
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
                widget = QComboBox()
                try:
                    classes = self.db.get_classes()
                    # Database method returns list of strings directly
                    class_names = classes if classes else []
                    
                    if is_required:
                        widget.addItem("Select Class...")
                        widget.addItems(class_names)
                        widget.setObjectName("required_field")
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
                widget = QComboBox()
                try:
                    sections = self.db.get_sections()
                    # Database method returns list of strings directly
                    section_names = sections if sections else []
                    
                    if is_required:
                        widget.addItem("Select Section...")
                        widget.addItems(section_names)
                        widget.setObjectName("required_field")
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
            
            # Apply styling based on required status
            if is_required:
                widget.setStyleSheet(self._get_required_input_style())
                widget.setObjectName("required_field")
            else:
                widget.setStyleSheet(self._get_input_style())
                
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
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """)
        
        # Create content widget
        content_widget = QWidget()
        layout = QGridLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Contact fields - matching database schema exactly (non-audit fields only)
        contact_fields = [
            # Mother Information (all required)
            ("Mother Name*", "mother_name", "text", True),
            ("Mother Date of Birth*", "mother_date_of_birth", "date", True),
            ("Mother Marital Status*", "mother_marital_status", "combo", True, [["Single", "Married", "Divorced", "Widowed", "Free union", "Separated", "Engaged"]]),
            ("Mother ID Type*", "mother_id_type", "text", True),
            ("Mother CNIC*", "mother_cnic", "cnic", True),
            ("Mother CNIC DOI*", "mother_cnic_doi", "date", True),
            ("Mother CNIC Exp*", "mother_cnic_exp", "date", True),
            ("Mother MWA*", "mother_mwa", "phone", True),
            
            # Household Head Information (all required)
            ("Household Role*", "household_role", "combo", True, [["Head", "Son", "Daughter", "Wife", "Husband", "Brother", "Sister", "Mother", "Father", "Aunt", "Uncle", "Grand Mother", "Grand Father", "Mother-in-Law", "Father-in-Law", "Daughter-in-Law", "Son-in-Law", "Sister-in-Law", "Brother-in-Law", "Grand Daughter", "Grand Son", "Nephew", "Niece", "Cousin", "Other", "Not Member"]]),
            ("Household Name*", "household_name", "text", True),
            ("HH Gender*", "hh_gender", "combo", True, [["Male", "Female", "Other"]]),
            ("HH Date of Birth*", "hh_date_of_birth", "date", True),
            ("Recipient Type*", "recipient_type", "combo", True, [["Principal", "Alternate"]]),
            
            # Alternate/Guardian Information (Optional fields)
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
            if is_required:
                label.setStyleSheet("""
                    QLabel {
                        color: #DC2626; 
                        font-family: 'Poppins Medium'; 
                        font-weight: 700;
                        font-size: 13px;
                        min-height: 38px;
                        max-height: 38px;
                        padding: 8px 0px;
                    }
                """)
            else:
                label.setStyleSheet("""
                    QLabel {
                        color: #374151; 
                        font-family: 'Poppins Medium'; 
                        font-weight: 600;
                        font-size: 13px;
                        min-height: 38px;
                        max-height: 38px;
                        padding: 8px 0px;
                    }
                """)
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
                    widget.setObjectName("required_field")
                
            elif field_type == "cnic":
                widget = QLineEdit()
                # CNIC validator: 13 digits with optional hyphens
                cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{5}-?[0-9]{7}-?[0-9]$'))
                widget.setValidator(cnic_validator)
                widget.setPlaceholderText("12345-1234567-1 (13 digits)")
                widget.setMaxLength(15)  # Allow for hyphens
                if is_required:
                    widget.setObjectName("required_field")
                    
            elif field_type == "date":
                widget = QDateEdit()
                if "birth" in field_name.lower() or "dob" in field_name.lower():
                    widget.setDate(QDate.currentDate().addYears(-20))  # Default age 20
                elif "doi" in field_name.lower():
                    widget.setDate(QDate.currentDate().addYears(-5))   # CNIC issued 5 years ago
                elif "exp" in field_name.lower():
                    widget.setDate(QDate.currentDate().addYears(5))    # Expires in 5 years
                else:
                    widget.setDate(QDate.currentDate())
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd-MMM-yyyy")
                if is_required:
                    widget.setObjectName("required_field")
                
            elif field_type == "combo":
                widget = QComboBox()
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
            
            # Apply styling based on required status
            if is_required:
                widget.setStyleSheet(self._get_required_input_style())
                widget.setObjectName("required_field")
            else:
                widget.setStyleSheet(self._get_input_style())
                
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
    
    def _apply_combo_box_dropdown_fix(self, widget, combo_type="combo"):
        """Apply dropdown functionality fix to any combo box widget."""
        
        # Set maximum visible items for dropdown to control height
        widget.setMaxVisibleItems(2)  # Limit dropdown to only 2 visible items for ultra-compact height
        
        # Force a fixed size policy for the dropdown
        widget.setSizePolicy(widget.sizePolicy().horizontalPolicy(), widget.sizePolicy().Fixed)
        
        # Store original items when combo is created to restore if needed
        if not hasattr(widget, '_original_items'):
            widget._original_items = []
            for i in range(widget.count()):
                widget._original_items.append(widget.itemText(i))
        
        # Override the showPopup method to control dropdown size
        original_show_popup = widget.showPopup
        
        def custom_show_popup():
            original_show_popup()
            # Get the popup view and force exact size matching
            popup = widget.view()
            if popup:
                # Match popup width exactly to combo box width
                popup.setFixedWidth(widget.width())
                
                # Ultra-compact height for 2 items only
                popup.setFixedHeight(44)  # Just enough for 2 items (20px each + 4px padding)
                
                # Position popup directly below combo box
                global_pos = widget.mapToGlobal(widget.rect().bottomLeft())
                popup.move(global_pos.x(), global_pos.y())
                
                # Remove any margins or borders that cause dual frame effect
                popup.setContentsMargins(0, 0, 0, 0)
                popup.setStyleSheet("""
                    QAbstractItemView {
                        border: 1px solid #D1D5DB;
                        border-radius: 4px;
                        background-color: #FFFFFF;
                        margin: 0px;
                        padding: 0px;
                    }
                """)
        
        widget.showPopup = custom_show_popup
        
        # Improve the mouse press event handling
        original_mouse_press = widget.mousePressEvent
        
        def enhanced_mouse_press(event):
            print(f"🎯 {combo_type} combo clicked - enhanced handling")
            
            # Check if items were cleared - repopulate if needed
            if widget.count() == 0:
                print(f"🎯 {combo_type} combo box is empty! Repopulating...")
                try:
                    # Repopulate based on combo type
                    if combo_type == "school_combo":
                        schools = self.db.get_schools()
                        widget.addItem("Select School...")
                        for school in schools:
                            school_name = school.get('school_name', f"School {school.get('id', '')}")
                            widget.addItem(school_name, school.get('id'))
                    elif combo_type == "class_combo":
                        classes = self.db.get_classes()
                        widget.addItem("Select Class...")
                        widget.addItems(classes)
                    elif combo_type == "section_combo":
                        sections = self.db.get_sections()
                        widget.addItem("Select Section...")
                        widget.addItems(sections)
                    else:
                        # For other combo types (gender, etc.), restore original items
                        if hasattr(widget, '_original_items') and widget._original_items:
                            widget.addItems(widget._original_items)
                        else:
                            widget.addItem("Select...")
                    print(f"🎯 Repopulated {combo_type} with {widget.count()} items")
                except Exception as e:
                    print(f"🎯 Error repopulating {combo_type}: {e}")
            
            # Call the original mouse press event to maintain proper behavior
            original_mouse_press(event)
        
        widget.mousePressEvent = enhanced_mouse_press
        
        # Apply improved combo box styling
        self._apply_improved_combo_styling(widget, combo_type)
        
        # Also add keyboard support
        def key_press_override(event):
            from PyQt5.QtCore import Qt
            if event.key() in [Qt.Key_Enter, Qt.Key_Return, Qt.Key_Space, Qt.Key_Down]:
                print(f"🎯 {combo_type} combo opened via keyboard")
                widget.showPopup()
                event.accept()
            else:
                super(QComboBox, widget).keyPressEvent(event)
        
        widget.keyPressEvent = key_press_override
    
    def _apply_improved_combo_styling(self, widget, combo_type):
        """Apply single-frame combo box styling to eliminate dual background."""
        improved_style = """
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 6px 8px;
                font-family: 'Poppins Medium';
                font-size: 12px;
                color: #1E293B;
                min-height: 24px;
                max-height: 32px;
            }
            QComboBox:focus {
                border: 2px solid #3B82F6;
                background-color: #FFFFFF;
            }
            QComboBox:hover {
                border: 1px solid #6B7280;
                background-color: #F9FAFB;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                border-left: 1px solid #D1D5DB;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background: #F3F4F6;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #6B7280;
                margin: auto;
            }
            QComboBox::down-arrow:hover {
                border-top: 5px solid #374151;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                background-color: #FFFFFF;
                selection-background-color: #3B82F6;
                selection-color: white;
                outline: none;
                show-decoration-selected: 1;
                margin: 0px;
                padding: 0px;
            }
            QComboBox QAbstractItemView::item {
                height: 20px;
                padding: 4px 8px;
                border: none;
                background-color: transparent;
                margin: 0px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3B82F6;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #EBF4FF;
                color: #1E293B;
            }
        """
        
        # Apply style based on field requirements
        if hasattr(widget, 'objectName') and widget.objectName() == "required_field":
            # Red styling for required fields
            required_style = improved_style.replace("#E2E8F0", "#FCA5A5").replace("#3B82F6", "#DC2626")
            widget.setStyleSheet(required_style)
        else:
            widget.setStyleSheet(improved_style)

    def _get_input_style(self):
        """Return standard input field styling."""
        return """
            QLineEdit, QSpinBox, QDateEdit {
                background-color: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                color: #1E293B;
                selection-background-color: #3B82F6;
                min-height: 30px;
                max-height: 44px;
            }
            QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #FFFFFF;
            }
            QLineEdit:hover, QSpinBox:hover, QDateEdit:hover {
                border: 2px solid #CBD5E1;
                background-color: #FFFFFF;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #F1F5F9;
                border: none;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 2px solid #E2E8F0;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background: #F1F5F9;
            }
        """
    
    def _get_required_input_style(self):
        """Return required field input styling with red accent."""
        return """
            QLineEdit, QSpinBox, QDateEdit {
                background-color: #FEF2F2;
                border: 2px solid #FCA5A5;
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                color: #1E293B;
                selection-background-color: #DC2626;
                min-height: 30px;
                max-height: 44px;
            }
            QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {
                border: 2px solid #DC2626;
                background-color: #FFFFFF;
            }
            QLineEdit:hover, QSpinBox:hover, QDateEdit:hover {
                border: 2px solid #F87171;
                background-color: #FFFFFF;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #FEE2E2;
                border: none;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 2px solid #FCA5A5;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background: #FEE2E2;
            }
        """
    
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
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                    if value in ["Select...", "Select School...", "Select Class...", "Select Section..."]:
                        value = ""
                elif isinstance(widget, QSpinBox):
                    value = str(widget.value())
                elif isinstance(widget, QDateEdit):
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
        
        for field_name, widget in self.student_fields.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text().strip()
            elif isinstance(widget, QComboBox):
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
            elif isinstance(widget, QDateEdit):
                data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QTextEdit):
                data[field_name] = widget.toPlainText().strip()
        
        return data
    
    def _populate_form_data(self, student_data):
        """Populate form fields with student data."""
        if not student_data:
            return
            
        for field_name, value in student_data.items():
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value) if value else "")
                elif isinstance(widget, QComboBox):
                    # Find and set the correct item
                    index = widget.findText(str(value) if value else "")
                    if index >= 0:
                        widget.setCurrentIndex(index)
                    else:
                        widget.setCurrentIndex(0)  # Default selection
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value) if value else 0)
                elif isinstance(widget, QDateEdit):
                    if value:
                        date = QDate.fromString(str(value), "yyyy-MM-dd")
                        if date.isValid():
                            widget.setDate(date)
                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(str(value) if value else "")
    
    def _save_student_data(self):
        """Save or update student data."""
        # Validate form first
        errors = self._validate_form()
        if errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Validation Error", error_message)
            return False
        
        # Collect form data
        data = self._collect_form_data()
        
        try:
            if hasattr(self, 'current_student_id') and self.current_student_id:
                # Update existing student
                success = self.db.update_student(self.current_student_id, data)
                if success:
                    QMessageBox.information(self, "Success", "Student updated successfully!")
                    self.student_form_dialog.accept()
                    self.load_students()  # Refresh the student list
                    return True
                else:
                    QMessageBox.critical(self, "Error", "Failed to update student.")
                    return False
            else:
                # Add new student
                success = self.db.add_student(data)
                if success:
                    QMessageBox.information(self, "Success", "Student added successfully!")
                    self.student_form_dialog.accept()
                    self.load_students()  # Refresh the student list
                    return True
                else:
                    QMessageBox.critical(self, "Error", "Failed to add student.")
                    return False
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
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
            # Validate form data first
            errors = self._validate_form()
            if not self._show_validation_errors(errors):
                return
            
            # Collect form data
            student_data = {}
            for field_name, widget in self.student_fields.items():
                if isinstance(widget, QLineEdit):
                    value = widget.text().strip()
                    if value:  # Only include non-empty values
                        student_data[field_name] = value
                elif isinstance(widget, QComboBox):
                    if field_name == "school_id":
                        # For school, get the ID from combo data
                        school_id = widget.currentData()
                        if school_id:
                            student_data[field_name] = school_id
                            
                            # Auto-populate organizational fields from school data
                            org_data = self.db.get_school_organizational_data(school_id)
                            if org_data:
                                print(f"🏫 Auto-adding organizational data: {org_data}")
                                # Add organizational IDs to student data
                                student_data.update(org_data)
                    else:
                        value = widget.currentText()
                        if value and value != "Select...":  # Only include valid selections
                            student_data[field_name] = value
                elif isinstance(widget, QDateEdit):
                    student_data[field_name] = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QTextEdit):
                    value = widget.toPlainText().strip()
                    if value:  # Only include non-empty values
                        student_data[field_name] = value
                elif isinstance(widget, QSpinBox):
                    student_data[field_name] = widget.value()
            
            print(f"📊 Final student data with org fields: {student_data}")
            
            # Add the student to database using our new method
            success = self.db.add_student(student_data)
            
            if success:
                # Show success message
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"✅ Student '{student_data.get('student_name', 'N/A')}' added successfully!\n\n"
                    f"📋 Student ID: {student_data.get('student_id', 'N/A')}\n"
                    f"🎓 Class: {student_data.get('class_id', 'N/A')}\n"
                    f"📚 Section: {student_data.get('section_id', 'N/A')}"
                )
                
                # Reset form and close
                self._reset_form()
                self._close_form()
                
                # Refresh the table data
                self._load_data()
                
            else:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    "❌ Failed to add student to database.\n\n"
                    "Please check the database connection and try again."
                )
                
        except Exception as e:
            QMessageBox.critical(
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
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, QDateEdit):
                    widget.setDate(QDate.currentDate())
                elif isinstance(widget, QTextEdit):
                    widget.clear()
        except Exception as e:
            print(f"Error resetting form: {e}")
            # Clear the fields dictionary to prevent further issues
            self.student_fields.clear()
    
    def _close_form(self):
        """Close the student form."""
        try:
            if hasattr(self, 'form_frame') and self.form_frame:
                self.form_frame.setVisible(False)
                self.is_editing = False
            print("✅ Student form closed successfully")
        except Exception as e:
            print(f"Error closing form: {e}")
    
    def _load_student_data(self, student_id, student_data=None):
        """Load student data for editing."""
        print(f"Loading student data for ID: {student_id}")
        
        if student_data:
            # Load basic data from table
            if 'name' in student_data and 'name' in self.student_fields:
                self.student_fields['name'].setText(student_data['name'])
            
            if 'id' in student_data and 'student_id' in self.student_fields:
                self.student_fields['student_id'].setText(student_data['id'])
            
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
            
            # Set phone number
            if 'phone' in student_data and 'student_phone' in self.student_fields:
                self.student_fields['student_phone'].setText(student_data['phone'])
            
            # Set some default values for demo
            if 'father_name' in student_data and 'father_name' in self.student_fields:
                self.student_fields['father_name'].setText(student_data['father_name'])
            elif 'father_name' in self.student_fields:
                self.student_fields['father_name'].setText(f"Father of {student_data.get('name', '')}")
            
            if 'school' in self.student_fields:
                school_combo = self.student_fields['school']
                school_combo.setCurrentIndex(1)  # Set to first school
            
            if 'roll_number' in self.student_fields:
                self.student_fields['roll_number'].setText(f"R{student_id}")
            
            if 'Alternate_phone' in self.student_fields:
                self.student_fields['Alternate_phone'].setText(student_data.get('phone', ''))
            
            print(f"✅ Student data loaded successfully for {student_data.get('name', student_id)}")
        else:
            # TODO: Load actual student data from database
            print(f"⚠️ No student data provided for ID: {student_id}")
    
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
        dialog.resize(900, 500)  # Reduced height from 700 to 500
        
        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel(f"👤 Complete Information: {student_name}")
        header_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Bold';
                font-size: 20px;
                color: #374151;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Create scroll area for tab widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """)
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #F3F4F6;
                color: #374151;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Poppins Medium';
                font-weight: 600;
                font-size: 12px;
                min-width: 120px;
                text-align: center;
            }
            QTabBar::tab:selected {
                background: #3B82F6;
                color: white;
            }
            QTabBar::tab:hover {
                background: #E5E7EB;
            }
        """)
        
        # Get complete student details from database
        try:
            # Fetch complete student data from database instead of table
            student_data = self.db.get_student_by_id(student_id)
            if not student_data:
                QMessageBox.warning(self, "Warning", "Student data not found in database.")
                return
            
            # Create tabs with complete database data
            personal_tab = self._create_details_personal_tab(student_data)
            tab_widget.addTab(personal_tab, "👤 Personal Info")
            
            academic_tab = self._create_details_academic_tab(student_data)
            tab_widget.addTab(academic_tab, "🎓 Academic Info")
            
            contact_tab = self._create_details_contact_tab(student_data)
            tab_widget.addTab(contact_tab, "📞 Contact Info")
            
            history_tab = self._create_details_history_tab(student_id)
            tab_widget.addTab(history_tab, "📋 Change History")
            
            # Add tab widget to scroll area
            scroll_area.setWidget(tab_widget)
            layout.addWidget(scroll_area)
            
            # Button box
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.setStyleSheet("""
                QDialogButtonBox QPushButton {
                    background: #6B7280;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-family: 'Poppins Medium';
                    font-size: 13px;
                    font-weight: 600;
                    min-width: 80px;
                }
                QDialogButtonBox QPushButton:hover {
                    background: #4B5563;
                }
            """)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load student details:\n{str(e)}")
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
            ("CNIC/B-Form:", student_data.get('b_form_number', 'N/A')),
            ("Address:", student_data.get('address', 'N/A')),
            ("Father's Name:", student_data.get('father_name', 'N/A')),
            ("Father's CNIC:", student_data.get('father_cnic', 'N/A')),
            ("Father's Phone:", student_data.get('father_phone', 'N/A')),
            ("Household Size:", student_data.get('household_size', 'N/A')),
            # Mother's Information
            ("Mother's Name:", student_data.get('mother_name', 'N/A')),
            ("Mother's Date of Birth:", student_data.get('mother_dob', 'N/A')),
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
            label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins Medium';
                    font-weight: 600;
                    color: #374151;
                    font-size: 14px;
                }
            """)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins';
                    color: #6B7280;
                    font-size: 14px;
                    background: #F9FAFB;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #E5E7EB;
                }
            """)
            
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
            ("Organization ID:", student_data.get('org_id', 'N/A')),
            ("School ID:", student_data.get('school_id', 'N/A')),
            ("Province ID:", student_data.get('province_id', 'N/A')),
            ("District ID:", student_data.get('district_id', 'N/A')),
            ("Union Council ID:", student_data.get('union_council_id', 'N/A')),
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
            label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins Medium';
                    font-weight: 600;
                    color: #374151;
                    font-size: 14px;
                }
            """)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins';
                    color: #6B7280;
                    font-size: 14px;
                    background: #F9FAFB;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #E5E7EB;
                }
            """)
            
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
            ("Nationality ID:", student_data.get('nationality_id', 'N/A')),
            # Household Head Information
            ("Household Role:", student_data.get('household_role', 'N/A')),
            ("Household Name:", student_data.get('household_name', 'N/A')),
            ("HH Gender:", student_data.get('hh_gender', 'N/A')),
            ("HH Date of Birth:", student_data.get('hh_dob', 'N/A')),
            ("Recipient Type:", student_data.get('recipient_type', 'N/A')),
            # Alternate/Guardian Information
            ("Alternate Name:", student_data.get('alternate_name', 'N/A')),
            ("Alternate Date of Birth:", student_data.get('alternate_dob', 'N/A')),
            ("Alternate Marital Status:", student_data.get('alternate_marital_status', 'N/A')),
            ("Alternate ID Type:", student_data.get('alternate_id_type', 'N/A')),
            ("Alternate CNIC:", student_data.get('alternate_cnic', 'N/A')),
            ("Alternate CNIC DOI:", student_data.get('alternate_cnic_doi', 'N/A')),
            ("Alternate CNIC Exp:", student_data.get('alternate_cnic_exp', 'N/A')),
            ("Alternate MWA:", student_data.get('alternate_mwa', 'N/A')),
            ("Alternate Relationship:", student_data.get('alternate_relationship', 'N/A')),
        ]
        
        row = 0
        for label_text, value in contact_info:
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins Medium';
                    font-weight: 600;
                    color: #374151;
                    font-size: 14px;
                }
            """)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins';
                    color: #6B7280;
                    font-size: 14px;
                    background: #F9FAFB;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #E5E7EB;
                }
            """)
            
            form_layout.addWidget(label, row, 0)
            form_layout.addWidget(value_label, row, 1)
            row += 1
        
        layout.addLayout(form_layout)
        layout.addStretch()
        return tab
    
    def _create_details_history_tab(self, student_id):
        """Create change history display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("📋 Complete Change History")
        header_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Bold';
                font-size: 18px;
                color: #374151;
                padding: 10px;
                background: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
            }
        """)
        layout.addWidget(header_label)
        
        # History table
        history_table = QTableWidget()
        history_table.setColumnCount(6)
        history_table.setHorizontalHeaderLabels([
            "📅 Date & Time", "🔄 Field Changed", "📋 Old Value", "✨ New Value", "🏷️ Change Type", "👤 Changed By"
        ])
        
        # Apply standard table styling
        apply_standard_table_style(history_table)
        
        # Sample history data (will be replaced with actual database data)
        sample_history = [
            ("2024-08-02 10:30:15", "RECORD_CREATED", "", "Student record created", "INSERT", "System"),
            ("2024-08-02 14:25:30", "phone", "03001234567", "03001234999", "UPDATE", "Admin"),
            ("2024-08-01 09:15:45", "class", "Class 9", "Class 10", "UPDATE", "Teacher"),
            ("2024-07-30 16:45:20", "section", "B", "A", "UPDATE", "Admin"),
            ("2024-07-28 11:20:10", "father_name", "Muhammad Ali", "Muhammad Ali Khan", "UPDATE", "Student"),
        ]
        
        history_table.setRowCount(len(sample_history))
        
        for row, (date_time, field, old_val, new_val, change_type, changed_by) in enumerate(sample_history):
            # Date & Time
            date_item = QTableWidgetItem(date_time)
            history_table.setItem(row, 0, date_item)
            
            # Field Changed
            field_item = QTableWidgetItem(field)
            history_table.setItem(row, 1, field_item)
            
            # Old Value
            old_item = QTableWidgetItem(old_val)
            history_table.setItem(row, 2, old_item)
            
            # New Value
            new_item = QTableWidgetItem(new_val)
            history_table.setItem(row, 3, new_item)
            
            # Change Type
            type_item = QTableWidgetItem(change_type)
            if change_type == "INSERT":
                type_item.setBackground(QColor("#D1FAE5"))
                type_item.setForeground(QColor("#047857"))
            elif change_type == "UPDATE":
                type_item.setBackground(QColor("#FEF3C7"))
                type_item.setForeground(QColor("#D97706"))
            elif change_type == "DELETE":
                type_item.setBackground(QColor("#FEE2E2"))
                type_item.setForeground(QColor("#DC2626"))
            history_table.setItem(row, 4, type_item)
            
            # Changed By
            by_item = QTableWidgetItem(changed_by)
            history_table.setItem(row, 5, by_item)
        
        # Auto resize columns
        header = history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date & Time
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Field Changed
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Old Value
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # New Value
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Change Type
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Changed By
        
        layout.addWidget(history_table)
        
        # Summary info
        summary_label = QLabel(f"📊 Total Changes: {len(sample_history)} | Last Updated: 2024-08-02 14:25:30")
        summary_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Medium';
                color: #6B7280;
                font-size: 14px;
                padding: 10px;
                background: #F9FAFB;
                border-radius: 6px;
                border: 1px solid #E5E7EB;
            }
        """)
        layout.addWidget(summary_label)
        
        return tab
    
    def refresh_data(self):
        """Public method to refresh data (called from main window)."""
        self._refresh_data()