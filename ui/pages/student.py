"""Student management page UI implementation."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QFrame, QGridLayout, 
                           QLineEdit, QMessageBox, QTableWidget, QHeaderView,
                           QScrollArea, QTableWidgetItem, QSplitter, QTextEdit,
                           QGroupBox, QFormLayout, QCheckBox, QDateEdit,
                           QSpinBox, QTabWidget, QDialog, QDialogButtonBox,
                           QAbstractItemView, QAbstractScrollArea, QSizePolicy)
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
        self.current_user = None  # Add current user tracking
        
        # Form management variables
        self.form_dialog = None
        self.form_created = False
        
        # Initialize database
        self.db = Database()
        
        # Setup UI
        self._init_ui()
        self._load_data()
        self._connect_signals()

    def set_current_user(self, user):
        """Set the current user for this page."""
        self.current_user = user

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
            
            # For new forms, don't clear fields immediately - let defaults show
            # Field clearing will happen when user clicks Reset button if needed
            
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
            QMessageBox.warning(self, "Form Validation", error_message)
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
                # Get table items for the 5 columns that actually exist
                id_item = self.students_table.item(selected_row, 0)
                name_item = self.students_table.item(selected_row, 1)
                father_name_item = self.students_table.item(selected_row, 2)
                class_item = self.students_table.item(selected_row, 3)
                section_item = self.students_table.item(selected_row, 4)
                
                # Validate that we can read the essential data
                if not id_item or not name_item:
                    QMessageBox.warning(self, "Error", "Unable to read student data. Please refresh and try again.")
                    return
                
                student_id = id_item.text().strip()
                student_name = name_item.text().strip()
                
                if not student_id:
                    QMessageBox.warning(self, "Error", "Student ID is empty. Cannot edit student.")
                    return
                
                print(f"🔧 Editing student: ID={student_id}, Name={student_name}")
                
                # Get complete student data from database using the student_id
                full_student_data = self.db.get_student_by_id(student_id)
                
                if not full_student_data:
                    QMessageBox.warning(self, "Error", f"Could not find complete data for student ID: {student_id}")
                    return
                
                print(f"📋 Retrieved full student data: {type(full_student_data)}")
                
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
                    QMessageBox.critical(self, "Error", "Form frame not available.")
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
                QMessageBox.critical(self, "Error", f"Failed to edit student: {str(e)}")
                print(f"❌ Edit error details: {e}")  # Debug output
                import traceback
                traceback.print_exc()
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
                    
                    # Delete from database
                    try:
                        # Get current user information
                        user_id = self.current_user.id if self.current_user else None
                        username = self.current_user.username if self.current_user else None
                        user_phone = getattr(self.current_user, 'phone', None) if self.current_user else None
                        
                        if self.db.delete_student(student_id, user_id, username, user_phone):
                            self.students_table.removeRow(selected_row)
                            self.student_deleted.emit(student_id)
                            QMessageBox.information(self, "Success", f"Student '{student_name}' has been deleted.")
                        else:
                            QMessageBox.warning(self, "Error", "Failed to delete student from database.")
                    except Exception as db_error:
                        QMessageBox.critical(self, "Database Error", f"Failed to delete student: {str(db_error)}")
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
            personal_tab = self._create_personal_info_tab()
            tab_widget.addTab(personal_tab, "👤 Personal Info")

            # Academic Information Tab
            academic_tab = self._create_academic_info_tab()  
            tab_widget.addTab(academic_tab, "🎓 Academic Info")

            # Contact Information Tab
            contact_tab = self._create_contact_info_tab()
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
                widget = QDateEdit()
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
                        calendar.setStyleSheet("""
                            QCalendarWidget {
                                background-color: white;
                                border: 2px solid #3B82F6;
                                border-radius: 8px;
                                font-family: 'Poppins Medium';
                                font-size: 12px;
                            }
                            QCalendarWidget QAbstractItemView {
                                background-color: white;
                                selection-background-color: #3B82F6;
                                selection-color: white;
                                gridline-color: #E5E7EB;
                                show-decoration-selected: 1;
                            }
                            QCalendarWidget QAbstractItemView:enabled {
                                color: #1F2937;
                                font-size: 12px;
                            }
                            QCalendarWidget QTableView {
                                alternate-background-color: #F9FAFB;
                            }
                            QCalendarWidget QTableView::item {
                                height: 22px;
                                min-height: 22px;
                                max-height: 22px;
                                padding: 2px;
                                text-align: center;
                            }
                            QCalendarWidget QToolButton {
                                background-color: transparent;
                                color: #1F2937;
                                border: none;
                                border-radius: 4px;
                                padding: 4px;
                                font-weight: bold;
                                min-width: 50px;
                                height: 24px;
                            }
                            QCalendarWidget QToolButton:hover {
                                background-color: #F3F4F6;
                                color: #1F2937;
                            }
                            QCalendarWidget QMenu {
                                background-color: white;
                                border: 1px solid #D1D5DB;
                                border-radius: 4px;
                            }
                            QCalendarWidget QSpinBox {
                                background-color: white;
                                border: 1px solid #D1D5DB;
                                border-radius: 4px;
                                padding: 4px;
                                font-size: 12px;
                                color: #1F2937;
                            }
                            QCalendarWidget QHeaderView::section {
                                background-color: transparent;
                                color: #1F2937;
                                border: none;
                                font-weight: bold;
                                padding: 4px;
                                height: 20px;
                            }
                            QCalendarWidget QWidget#qt_calendar_navigationbar {
                                background-color: white;
                            }
                            QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {
                                background-color: transparent;
                                color: #1F2937;
                            }
                        """)
                        
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
                widget = QComboBox()
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
                widget = QComboBox()
                schools = self._get_schools_from_database()
                if is_required:
                    widget.addItems(["Select School..."] + schools)
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                else:
                    widget.addItems(["Not Specified"] + schools)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "school_combo")
                    
            elif field_type == "org_combo":
                widget = QComboBox()
                organizations = self._get_organizations_from_database()
                if is_required:
                    widget.addItems(["Select Organization..."] + organizations)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + organizations)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "org_combo")
                    
            elif field_type == "province_combo":
                widget = QComboBox()
                provinces = self._get_provinces_from_database()
                if is_required:
                    widget.addItems(["Select Province..."] + provinces)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + provinces)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "province_combo")
                    
            elif field_type == "district_combo":
                widget = QComboBox()
                districts = self._get_districts_from_database()
                if is_required:
                    widget.addItems(["Select District..."] + districts)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + districts)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "district_combo")
                    
            elif field_type == "union_council_combo":
                widget = QComboBox()
                union_councils = self._get_union_councils_from_database()
                if is_required:
                    widget.addItems(["Select Union Council..."] + union_councils)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + union_councils)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "union_council_combo")
                    
            elif field_type == "nationality_combo":
                widget = QComboBox()
                nationalities = self._get_nationalities_from_database()
                if is_required:
                    widget.addItems(["Select Nationality..."] + nationalities)
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                else:
                    widget.addItems(["Not Specified"] + nationalities)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "nationality_combo")
            
            # Apply normal styling to all fields (no red styling initially)
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
            # All labels use normal styling (no red color initially)
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
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + organizations)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "org_combo")
                    
            elif field_type == "province_combo":
                widget = QComboBox()
                provinces = self._get_provinces_from_database()
                if is_required:
                    widget.addItems(["Select Province..."] + provinces)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + provinces)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "province_combo")
                    
            elif field_type == "district_combo":
                widget = QComboBox()
                districts = self._get_districts_from_database()
                if is_required:
                    widget.addItems(["Select District..."] + districts)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + districts)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "district_combo")
                    
            elif field_type == "union_council_combo":
                widget = QComboBox()
                union_councils = self._get_union_councils_from_database()
                if is_required:
                    widget.addItems(["Select Union Council..."] + union_councils)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
                else:
                    widget.addItems(["Not Specified"] + union_councils)
                
                # Apply universal dropdown fix
                self._apply_combo_box_dropdown_fix(widget, "union_council_combo")
                    
            elif field_type == "nationality_combo":
                widget = QComboBox()
                nationalities = self._get_nationalities_from_database()
                if is_required:
                    widget.addItems(["Select Nationality..."] + nationalities)
                    widget.setProperty("is_required", True)  # Mark as required but don`t style yet
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
                widget = QComboBox()
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
            widget.setStyleSheet(self._get_input_style())
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
                widget = QDateEdit()
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
                        calendar.setStyleSheet("""
                            QCalendarWidget {
                                background-color: white;
                                border: 2px solid #3B82F6;
                                border-radius: 8px;
                                font-family: 'Poppins Medium';
                                font-size: 12px;
                            }
                            QCalendarWidget QAbstractItemView {
                                background-color: white;
                                selection-background-color: #3B82F6;
                                selection-color: white;
                                gridline-color: #E5E7EB;
                                show-decoration-selected: 1;
                            }
                            QCalendarWidget QAbstractItemView:enabled {
                                color: #1F2937;
                                font-size: 12px;
                            }
                            QCalendarWidget QTableView {
                                alternate-background-color: #F9FAFB;
                            }
                            QCalendarWidget QTableView::item {
                                height: 22px;
                                min-height: 22px;
                                max-height: 22px;
                                padding: 2px;
                                text-align: center;
                            }
                            QCalendarWidget QToolButton {
                                background-color: transparent;
                                color: #1F2937;
                                border: none;
                                border-radius: 4px;
                                padding: 4px;
                                font-weight: bold;
                                min-width: 50px;
                                height: 24px;
                            }
                            QCalendarWidget QToolButton:hover {
                                background-color: #F3F4F6;
                                color: #1F2937;
                            }
                            QCalendarWidget QMenu {
                                background-color: white;
                                border: 1px solid #D1D5DB;
                                border-radius: 4px;
                            }
                            QCalendarWidget QSpinBox {
                                background-color: white;
                                border: 1px solid #D1D5DB;
                                border-radius: 4px;
                                padding: 4px;
                                font-size: 12px;
                                color: #1F2937;
                            }
                            QCalendarWidget QHeaderView::section {
                                background-color: transparent;
                                color: #1F2937;
                                border: none;
                                font-weight: bold;
                                padding: 4px;
                                height: 20px;
                            }
                            QCalendarWidget QWidget#qt_calendar_navigationbar {
                                background-color: white;
                            }
                            QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {
                                background-color: transparent;
                                color: #1F2937;
                            }
                        """)
                        
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
            
            # Apply normal styling to all fields (no red styling initially)
            widget.setStyleSheet(self._get_input_style())
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
                    widget.setStyleSheet(self._get_input_style())  # Use normal styling
                    # Update label to show required indicator
                    self._update_field_label(field_name, required=True)
                else:
                    widget.setProperty("is_required", False)
                    widget.setStyleSheet(self._get_input_style())
                    self._update_field_label(field_name, required=False)
    
    def _enable_household_fields(self, mandatory=False):
        """Enable household-related fields and optionally make them mandatory."""
        for field_name in self.household_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(True)
                
                if mandatory:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    widget.setStyleSheet(self._get_input_style())  # Use normal styling
                    self._update_field_label(field_name, required=True)
                else:
                    widget.setProperty("is_required", False)
                    widget.setStyleSheet(self._get_input_style())
                    self._update_field_label(field_name, required=False)
    
    def _enable_alternate_fields(self, mandatory=False):
        """Enable alternate-related fields and optionally make them mandatory."""
        for field_name in self.alternate_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(True)
                
                if mandatory:
                    widget.setProperty("is_required", True)  # Mark as required but don't style yet
                    widget.setStyleSheet(self._get_input_style())  # Use normal styling
                    self._update_field_label(field_name, required=True)
                else:
                    widget.setProperty("is_required", False)
                    widget.setStyleSheet(self._get_input_style())
                    self._update_field_label(field_name, required=False)
    
    def _disable_mother_fields(self):
        """Disable mother-related fields."""
        for field_name in self.mother_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(False)
                widget.setStyleSheet(self._get_disabled_input_style())
                self._update_field_label(field_name, required=False)
    
    def _disable_household_fields(self):
        """Disable household-related fields."""
        for field_name in self.household_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(False)
                widget.setStyleSheet(self._get_disabled_input_style())
                self._update_field_label(field_name, required=False)
    
    def _disable_alternate_fields(self):
        """Disable alternate-related fields."""
        for field_name in self.alternate_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                widget.setEnabled(False)
                widget.setStyleSheet(self._get_disabled_input_style())
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
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
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
        """Apply dropdown functionality fix with simple keyboard highlight (no filtering)."""
        
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
        
        # Apply improved combo box styling  
        self._apply_improved_combo_styling(widget, combo_type)
    
    def _apply_improved_combo_styling(self, widget, combo_type):
        """Apply single-frame combo box styling with editable support."""
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
            QComboBox:editable {
                background-color: #FFFFFF;
            }
            QComboBox QLineEdit {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-family: 'Poppins Medium';
                font-size: 12px;
                color: #1E293B;
            }
            QComboBox QLineEdit:focus {
                background-color: transparent;
                border: none;
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
    
    def _clear_validation_errors(self):
        """Clear all validation error styling from form fields."""
        # Clear styling from all student fields
        for field_name, widget in self.student_fields.items():
            if hasattr(widget, 'property') and widget.property("is_required"):
                # Apply normal styling to required fields
                if isinstance(widget, (QLineEdit, QSpinBox, QDateEdit)):
                    widget.setStyleSheet(self._get_input_style())
                elif isinstance(widget, QComboBox):
                    widget.setStyleSheet("")  # Use default combo styling
            else:
                # Apply normal styling to optional fields
                if isinstance(widget, (QLineEdit, QSpinBox, QDateEdit)):
                    widget.setStyleSheet(self._get_input_style())
                elif isinstance(widget, QComboBox):
                    widget.setStyleSheet("")
    
    def _highlight_validation_errors(self, error_fields):
        """Highlight fields that have validation errors in red."""
        for field_name in error_fields:
            if field_name in self.student_fields:
                widget = self.student_fields[field_name]
                if isinstance(widget, (QLineEdit, QSpinBox, QDateEdit)):
                    widget.setStyleSheet(self._get_required_input_style())
                elif isinstance(widget, QComboBox):
                    # Apply red styling to combo box
                    widget.setStyleSheet("""
                        QComboBox {
                            background-color: #FEF2F2;
                            border: 2px solid #FCA5A5;
                            border-radius: 4px;
                            padding: 6px 8px;
                            font-family: 'Poppins Medium';
                            font-size: 12px;
                            color: #1E293B;
                        }
                        QComboBox:focus {
                            border: 2px solid #DC2626;
                        }
                    """)
    
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
                elif isinstance(widget, QComboBox):
                    if widget.currentIndex() <= 0:  # No selection or "Select..." option
                        errors.append(f"{display_name} must be selected")
                        error_fields.append(field_name)
                elif isinstance(widget, QDateEdit):
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
                elif isinstance(widget, QComboBox):
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
                elif isinstance(widget, QDateEdit):
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
            QMessageBox.warning(self, "Validation Error", error_message)
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
                    QMessageBox.information(self, "Success", "✅ Student updated successfully!")
                    # Close form and refresh data
                    self._close_form()
                    self._load_data()  # Refresh the student list
                    return True
                else:
                    QMessageBox.critical(self, "Error", "❌ Failed to update student.")
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
            if school_widget and isinstance(school_widget, QComboBox):
                school_id = school_widget.currentData()
                if school_id:
                    student_data['school_id'] = school_id
                    
                    # Auto-populate organizational fields from school data
                    org_data = self.db.get_school_organizational_data(school_id)
                    if org_data:
                        print(f"🏫 Auto-adding organizational data: {org_data}")
                        # Add organizational IDs to student data
                        student_data.update(org_data)
            
            print(f"📊 Final student data with org fields: {student_data}")
            
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
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"✅ Student '{student_data.get('student_name', 'N/A')}' {action_text} successfully!\n\n"
                    f"📋 Student ID: {student_data.get('student_id', 'N/A')}\n"
                    f"🎓 Class: {student_data.get('class', 'N/A')}\n"
                    f"📚 Section: {student_data.get('section', 'N/A')}"
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
        
        try:
            # Load complete student data from database
            complete_student_data = self.db.get_student_by_id(student_id)
            if not complete_student_data:
                QMessageBox.warning(self, "Error", "Student data not found in database.")
                return
            
            print(f"📊 Found complete student data: {list(complete_student_data.keys())}")
            
            # Populate form fields with database data
            self._populate_form_data(complete_student_data)
            
            print(f"✅ Student data loaded successfully for {complete_student_data.get('student_name', student_id)}")
            
        except Exception as e:
            print(f"❌ Error loading student data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load student data: {str(e)}")
            
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
        
        # Create dynamic scroll area for tab widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Only when needed
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Only when needed
        scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)  # Adjust to content size
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
            
            # Auto-adjust dialog size based on content
            dialog.adjustSize()  # Adjust to content size
            
            # Set dynamic size based on screen
            screen_geometry = self.geometry()
            max_width = min(1200, int(screen_geometry.width() * 0.9))
            max_height = min(800, int(screen_geometry.height() * 0.8))
            dialog.resize(max_width, max_height)
            
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
        """Create change history display tab with dynamic sizing."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)  # Reduced spacing between elements
        layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins
        
        # Make tab size adjustable to content
        tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Header - Compact design
        header_label = QLabel("📋 Complete Change History")
        header_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Bold';
                font-size: 16px;
                color: #374151;
                padding: 6px 10px;
                background: #F8FAFC;
                border-radius: 6px;
                border: 1px solid #E5E7EB;
                max-height: 36px;
            }
        """)
        layout.addWidget(header_label)
        
        # History table
        history_table = QTableWidget()
        history_table.setColumnCount(6)
        history_table.setHorizontalHeaderLabels([
            "📅 Date & Time", "🔄 Field Changed", "📋 Old Value", "✨ New Value", "🏷️ Type", "👤 Changed By"
        ])
        
        # Apply standard table styling with enhanced readability
        apply_standard_table_style(history_table)
        
        # Additional styling for better content visibility and optimized text size
        history_table.setAlternatingRowColors(True)
        history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        history_table.setStyleSheet(history_table.styleSheet() + """
            QTableWidget {
                gridline-color: #E5E7EB;
                alternate-background-color: #F9FAFB;
                font-size: 12px;
                font-weight: 500;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #E5E7EB;
                font-size: 12px;
                line-height: 1.3;
                word-wrap: break-word;
            }
            QHeaderView::section {
                background-color: #F3F4F6;
                color: #374151;
                font-weight: 600;
                font-size: 11px;
                padding: 8px 6px;
                border: 1px solid #E5E7EB;
                text-align: center;
            }
        """)
        
        # Load real history data from database
        try:
            history_records = self.db.get_student_history(student_id)
            print(f"📋 Loaded {len(history_records)} history records for student {student_id}")
            
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
        
        history_table.setRowCount(len(history_records))
        
        for row, record in enumerate(history_records):
            # Date & Time
            date_item = QTableWidgetItem(record.get('date_time', 'Unknown'))
            date_item.setTextAlignment(Qt.AlignCenter)
            history_table.setItem(row, 0, date_item)
            
            # Field Changed
            field_item = QTableWidgetItem(record.get('field_changed', 'N/A'))
            field_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            history_table.setItem(row, 1, field_item)
            
            # Old Value
            old_value = record.get('old_value', '')
            if len(old_value) > 100:  # Truncate very long values
                old_value = old_value[:100] + "..."
            old_item = QTableWidgetItem(old_value)
            old_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            old_item.setToolTip(record.get('old_value', ''))  # Show full value in tooltip
            history_table.setItem(row, 2, old_item)
            
            # New Value
            new_value = record.get('new_value', '')
            if len(new_value) > 100:  # Truncate very long values
                new_value = new_value[:100] + "..."
            new_item = QTableWidgetItem(new_value)
            new_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            new_item.setToolTip(record.get('new_value', ''))  # Show full value in tooltip
            history_table.setItem(row, 3, new_item)
            
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
            history_table.setItem(row, 4, type_item)
            
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
            history_table.setItem(row, 5, changed_by_item)
        
        # Auto resize columns based on content for better visibility
        header = history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date & Time - fit content
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Field Changed - fit content
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Old Value - fit content
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # New Value - fit content  
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Change Type - fit content
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Changed By - fit content
        
        # Set minimum widths to ensure readability but allow expansion (reduced for better fit)
        history_table.setColumnWidth(0, 150)  # Date & Time minimum width
        history_table.setColumnWidth(1, 180)  # Field Changed minimum width
        history_table.setColumnWidth(2, 200)  # Old Value minimum width
        history_table.setColumnWidth(3, 200)  # New Value minimum width
        history_table.setColumnWidth(4, 100)  # Change Type minimum width
        history_table.setColumnWidth(5, 120)  # Changed By minimum width
        
        # Enable word wrap for better text display
        history_table.setWordWrap(True)
        
        # Allow horizontal stretching beyond table width for full content visibility
        header.setStretchLastSection(False)
        header.setCascadingSectionResizes(False)
        
        # Set row height for better content visibility (reduced from 50 to 40)
        history_table.verticalHeader().setDefaultSectionSize(40)
        
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
        history_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        history_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        print(f"📏 History table dynamic height: {num_records} records, min height: {table_height}px")
        
        layout.addWidget(history_table)
        
        # Summary info with real data - compact design
        latest_change = history_records[0].get('date_time', 'Unknown') if history_records else 'No changes'
        summary_label = QLabel(f"📊 Total Changes: {len(history_records)} | Last Updated: {latest_change}")
        summary_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Medium';
                color: #6B7280;
                font-size: 12px;
                padding: 4px 8px;
                background: #F9FAFB;
                border-radius: 4px;
                border: 1px solid #E5E7EB;
                max-height: 28px;
            }
        """)
        layout.addWidget(summary_label)
        
        return tab
    
    def refresh_data(self):
        """Public method to refresh data (called from main window)."""
        self._refresh_data()
