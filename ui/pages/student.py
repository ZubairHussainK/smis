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
        
        # Filters section
        filters_group = QGroupBox("🔍 Search & Filter Students")
        filters_group.setStyleSheet("""
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
        
        filters_layout = QVBoxLayout(filters_group)
        
        # Search input
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, roll number, or phone...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 10px 12px;
                font-family: 'Poppins';
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                outline: none;
            }
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        filters_layout.addLayout(search_layout)
        
        # Filter dropdowns
        dropdowns_layout = QHBoxLayout()
        
        # School filter
        school_layout = QVBoxLayout()
        school_label = QLabel("School:")
        school_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        self.school_combo = QComboBox()
        self.school_combo.addItems(["All Schools", "Pine Valley School", "Green Park Academy", "Sunshine High"])
        self.school_combo.setStyleSheet(self._get_combo_style())
        school_layout.addWidget(school_label)
        school_layout.addWidget(self.school_combo)
        
        # Class filter
        class_layout = QVBoxLayout()
        class_label = QLabel("Class:")
        class_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        self.class_combo = QComboBox()
        self.class_combo.addItems(["All Classes"] + [f"Class {i}" for i in range(1, 13)])
        self.class_combo.setStyleSheet(self._get_combo_style())
        class_layout.addWidget(class_label)
        class_layout.addWidget(self.class_combo)
        
        # Section filter
        section_layout = QVBoxLayout()
        section_label = QLabel("Section:")
        section_label.setStyleSheet("color: #6B7280; font-family: 'Poppins'; font-size: 14px;")
        self.section_combo = QComboBox()
        self.section_combo.addItems(["All Sections", "A", "B", "C", "D", "E"])
        self.section_combo.setStyleSheet(self._get_combo_style())
        section_layout.addWidget(section_label)
        section_layout.addWidget(self.section_combo)
        
        dropdowns_layout.addLayout(school_layout)
        dropdowns_layout.addLayout(class_layout)
        dropdowns_layout.addLayout(section_layout)
        filters_layout.addLayout(dropdowns_layout)
        
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
        panel_layout.addWidget(filters_group)
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
        """Load student data from database."""
        try:
            # Fetch students from database
            import sqlite3
            conn = sqlite3.connect('school.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT student_id, student_name, father_name, class_name, section, father_phone
                FROM students 
                ORDER BY student_id
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to format expected by table
            students = []
            for row in rows:
                student = {
                    "id": row[0],  # student_id
                    "name": row[1],  # student_name  
                    "father_name": row[2],  # father_name
                    "class": row[3] if row[3] else "N/A",  # class_name
                    "section": row[4] if row[4] else "N/A",  # section
                    "phone": row[5] if row[5] else "N/A"  # father_phone
                }
                students.append(student)
            
            self._populate_table(students)
            print(f"📚 Loaded {len(students)} students from database")
            
        except Exception as e:
            print(f"Error loading student data: {e}")
            QMessageBox.warning(self, "Data Load Error", f"Failed to load student data: {str(e)}")
    
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
        
        # Filter changes
        self.search_input.textChanged.connect(self._apply_filters)
        self.school_combo.currentTextChanged.connect(self._apply_filters)
        self.class_combo.currentTextChanged.connect(self._apply_filters)
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
        """Apply search and filter criteria."""
        search_text = self.search_input.text().lower()
        school_filter = self.school_combo.currentText()
        class_filter = self.class_combo.currentText()
        section_filter = self.section_combo.currentText()
        
        for row in range(self.students_table.rowCount()):
            show_row = True
            
            # Apply search filter
            if search_text:
                row_text = ""
                for col in range(self.students_table.columnCount() - 1):  # Exclude actions column
                    item = self.students_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                
                if search_text not in row_text:
                    show_row = False
            
            # Apply school filter
            if school_filter != "All Schools" and show_row:
                # TODO: Add school filtering logic when school column is available
                pass
            
            # Apply class filter
            if class_filter != "All Classes" and show_row:
                class_item = self.students_table.item(row, 3)  # Class is now column 3
                if class_item and class_filter not in class_item.text():
                    show_row = False
            
            # Apply section filter
            if section_filter != "All Sections" and show_row:
                section_item = self.students_table.item(row, 4)  # Section is now column 4
                if section_item and section_filter != section_item.text():
                    show_row = False
            
            self.students_table.setRowHidden(row, not show_row)
    
    def _refresh_data(self):
        """Refresh the student data."""
        self._load_data()
        self.search_input.clear()
        self.school_combo.setCurrentIndex(0)
        self.class_combo.setCurrentIndex(0)
        self.section_combo.setCurrentIndex(0)
        QMessageBox.information(self, "Success", "🔄 Student data refreshed successfully!")
    
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
        
        # Personal fields - matching database exactly
        personal_fields = [
            ("Student ID", "student_id", "text"),
            ("Student Name", "student_name", "text"),
            ("Date of Birth", "date_of_birth", "date"),
            ("Gender", "gender", "combo", ["Male", "Female"]),
            ("Students B-Form Number", "students_bform_number", "text"),
            ("Father's Name", "father_name", "text"),
            ("Father CNIC", "father_cnic", "text"),
            ("Father Phone", "father_phone", "text"),
            ("Household Size", "household_size", "number"),
            # Mother's Information
            ("Mother's Name", "mother_name", "text"),
            ("Mother Date of Birth", "mother_date_of_birth", "date"),
            ("Mother's Marital Status", "mother_marital_status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("Mother's CNIC", "mother_cnic", "text"),
            ("Mother's CNIC DOI", "mother_cnic_doi", "date"),
            ("Mother's CNIC Exp", "mother_cnic_exp", "date"),
            ("Mother MWA", "mother_mwa", "number"),
            # Household Information
            ("Household Role", "household_role", "text"),
            ("Household Name", "household_name", "text"),
            ("HH Gender", "hh_gender", "combo", ["Male", "Female"]),
            ("HH Date of Birth", "hh_date_of_birth", "date"),
            ("Recipient Type", "recipient_type", "text"),
        ]
        
        row = 0
        for label_text, field_name, field_type, *options in personal_fields:
            label = QLabel(label_text + ":")
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
            label.setAlignment(Qt.AlignVCenter)  # Vertical center alignment
            
            # Add tooltips for specific fields
            if "DOI" in label_text:
                label.setToolTip("Date of CNIC Issues")
            elif "Exp" in label_text:
                label.setToolTip("CNIC Expiry Date")
            
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {label_text.lower()}")
                
                # Add input validators for specific fields
                if "cnic" in field_name.lower() or "b-form" in label_text.lower():
                    # CNIC validator: exactly 13 digits, can include hyphens for display
                    cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{1,5}-?[0-9]{1,7}-?[0-9]{1,1}$'))
                    widget.setValidator(cnic_validator)
                    widget.setPlaceholderText("12345-1234567-1 (13 digits)")
                    widget.setMaxLength(15)  # Allow for hyphens
                elif "phone" in field_name.lower() or "mobile" in field_name.lower():
                    # Mobile validator: exactly 11 digits, can include hyphens for display
                    mobile_validator = QRegExpValidator(QRegExp(r'^[0-9]{1,4}-?[0-9]{1,7}$'))
                    widget.setValidator(mobile_validator)
                    widget.setPlaceholderText("0300-1234567 (11 digits)")
                    widget.setMaxLength(12)  # Allow for hyphen
            elif field_type == "number":
                widget = QSpinBox()
                if "mwa" in field_name.lower():
                    widget.setRange(0, 99999)  # MWA can be large numbers
                    widget.setValue(0)
                elif "_id" in field_name:
                    widget.setRange(1, 99999)  # ID fields start from 1
                    widget.setValue(1)
                else:
                    widget.setRange(1, 50)  # Default for household size
                    widget.setValue(1)
            elif field_type == "date":
                widget = QDateEdit()
                widget.setDate(QDate.currentDate().addYears(-10))
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd-MMM-yy")  # Format: 03-Aug-25
            elif field_type == "combo":
                widget = QComboBox()
                if options:
                    widget.addItems(["Select..."] + options[0])
            
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
        
        # Academic fields - user-friendly fields only (foreign keys handled in backend)
        academic_fields = [
            ("Registration Number", "registration_number", "text"),
            ("Class Teacher Name", "class_teacher_name", "text"),
            ("Class", "class", "combo", ["Kachi", "Paki", "1", "2", "3", "4", "5"]),
            ("Class Name", "class_name", "text"),
            ("Section", "section", "combo", ["A", "B", "C", "D", "E"]),
            ("Year of Admission", "year_of_admission", "date"),
            ("Year of Admission Alt", "year_of_admission_alt", "date"),
            ("Address", "address", "textarea"),
            ("Final Unique Codes", "final_unique_codes", "text"),
        ]
        
        row = 0
        for label_text, field_name, field_type, *options in academic_fields:
            label = QLabel(label_text + ":")
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
            label.setAlignment(Qt.AlignVCenter)  # Vertical center alignment
            
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {label_text.lower()}")
            elif field_type == "number":
                widget = QSpinBox()
                if "mwa" in field_name.lower():
                    widget.setRange(0, 99999)  # MWA can be large numbers
                    widget.setValue(0)
                elif "_id" in field_name:
                    widget.setRange(1, 99999)  # ID fields start from 1
                    widget.setValue(1)
                else:
                    widget.setRange(1, 50)  # Default for household size
                    widget.setValue(1)
            elif field_type == "date":
                widget = QDateEdit()
                widget.setDate(QDate.currentDate())
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd-MMM-yy")  # Format: 03-Aug-25
            elif field_type == "combo":
                widget = QComboBox()
                if options:
                    widget.addItems(["Select..."] + options[0])
            
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
        
        # Contact fields - matching database exactly (alternates are optional)
        contact_fields = [
            # Alternate's Information (optional fields)
            ("Alternate Name", "alternate_name", "text"),
            ("Alternate Date of Birth", "alternate_date_of_birth", "date"),
            ("Alternate Marital Status", "alternate_marital_status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("Alternate ID Type", "alternate_id_type", "text"),
            ("Alternate CNIC", "alternate_cnic", "text"),
            ("Alternate CNIC DOI", "alternate_cnic_doi", "date"),
            ("Alternate CNIC Exp", "alternate_cnic_exp", "date"),
            ("Alternate MWA", "alternate_mwa", "number"),
            ("Alternate Relationship with Mother", "alternate_relationship_with_mother", "text"),
            ("Mother ID Type", "mother_id_type", "text"),
        ]
        
        row = 0
        for label_text, field_name, field_type, *options in contact_fields:
            label = QLabel(label_text + ":")
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
            label.setAlignment(Qt.AlignVCenter)  # Vertical center alignment
            
            # Add tooltips for specific fields
            if "DOI" in label_text:
                label.setToolTip("Date of CNIC Issues")
            elif "Exp" in label_text:
                label.setToolTip("CNIC Expiry Date")
            
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {label_text.lower()}")
                
                # Add input validators for specific fields
                if "cnic" in field_name.lower():
                    # CNIC validator: exactly 13 digits, can include hyphens for display
                    cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{1,5}-?[0-9]{1,7}-?[0-9]{1,1}$'))
                    widget.setValidator(cnic_validator)
                    widget.setPlaceholderText("12345-1234567-1 (13 digits)")
                    widget.setMaxLength(15)  # Allow for hyphens
                elif "phone" in field_name.lower() or "mobile" in field_name.lower():
                    # Mobile validator: exactly 11 digits, can include hyphens for display
                    mobile_validator = QRegExpValidator(QRegExp(r'^[0-9]{1,4}-?[0-9]{1,7}$'))
                    widget.setValidator(mobile_validator)
                    widget.setPlaceholderText("0300-1234567 (11 digits)")
                    widget.setMaxLength(12)  # Allow for hyphen
            elif field_type == "number":
                widget = QSpinBox()
                if "mwa" in field_name.lower():
                    widget.setRange(0, 99999)  # MWA can be large numbers
                    widget.setValue(0)
                elif "_id" in field_name:
                    widget.setRange(1, 99999)  # ID fields start from 1
                    widget.setValue(1)
                else:
                    widget.setRange(1, 50)  # Default for household size
                    widget.setValue(1)
            elif field_type == "date":
                widget = QDateEdit()
                widget.setDate(QDate.currentDate().addYears(-10))
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd-MMM-yy")  # Format: 03-Aug-25
            elif field_type == "textarea":
                widget = QTextEdit()
                widget.setMaximumHeight(80)
                widget.setPlaceholderText(f"Enter {label_text.lower()}")
            elif field_type == "combo":
                widget = QComboBox()
                if options:
                    widget.addItems(["Select..."] + options[0])
            
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
    
    def _get_input_style(self):
        """Get standard input field styling."""
        return """
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Poppins';
                font-size: 13px;
                background: white;
                min-height: 22px;
                max-height: 38px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border-color: #3B82F6;
                outline: none;
                background: #F8FAFC;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
                padding-right: 5px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #6B7280;
                margin-right: 8px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #374151;
            }
            QTextEdit {
                min-height: 80px;
                max-height: 100px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #F3F4F6;
                border: none;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #E5E7EB;
            }
        """
    
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
        """Save the student data."""
        # Define mandatory fields (all except Alternate fields)
        mandatory_fields = [
            "student_id", "name", "dob", "gender", "cnic", "religion", "nationality",
            "father_name", "household_size", "mother_name", "mother_marital_status", 
            "mother_cnic", "mother_cnic_doi", "mother_cnic_exp", "mother_mwa",
            "class", "section", "student_phone"
        ]
        
        # Optional Alternate fields
        optional_Alternate_fields = [
            "Alternate_name", "Alternate_cnic", "Alternate_cnic_doi", "Alternate_cnic_exp",
            "Alternate_marital_status", "Alternate_mwa", "Alternate_phone", "Alternate_relation"
        ]
        
        # Validation errors list
        validation_errors = []
        
        # Check mandatory fields
        for field_name in mandatory_fields:
            widget = self.student_fields.get(field_name)
            if widget:
                if isinstance(widget, QLineEdit):
                    if not widget.text().strip():
                        field_display = field_name.replace('_', ' ').title()
                        validation_errors.append(f"• {field_display} is required")
                elif isinstance(widget, QComboBox):
                    if widget.currentText() in ["Select...", "", "Male", "Female", "Other"][:1]:  # Only check if it's the default "Select..."
                        if widget.currentText() == "Select...":
                            field_display = field_name.replace('_', ' ').title()
                            validation_errors.append(f"• {field_display} must be selected")
                elif isinstance(widget, QDateEdit):
                    # Date fields are generally valid by default
                    pass
        
        # CNIC validation (13 digits)
        cnic_fields = ["cnic", "mother_cnic", "Alternate_cnic"]
        for field_name in cnic_fields:
            widget = self.student_fields.get(field_name)
            if widget and isinstance(widget, QLineEdit):
                cnic_value = widget.text().strip()
                # Skip validation for optional Alternate CNIC if empty
                if field_name == "Alternate_cnic" and not cnic_value:
                    continue
                # For mandatory CNIC fields or filled Alternate CNIC
                if cnic_value:
                    # Remove any non-digit characters for validation
                    digits_only = ''.join(filter(str.isdigit, cnic_value))
                    if len(digits_only) != 13:
                        field_display = field_name.replace('_', ' ').title()
                        validation_errors.append(f"• {field_display} must be exactly 13 digits")
        
        # Mobile number validation (11 digits)
        mobile_fields = ["student_phone", "Alternate_phone"]
        for field_name in mobile_fields:
            widget = self.student_fields.get(field_name)
            if widget and isinstance(widget, QLineEdit):
                mobile_value = widget.text().strip()
                # Skip validation for optional Alternate phone if empty
                if field_name == "Alternate_phone" and not mobile_value:
                    continue
                # For mandatory mobile fields or filled Alternate mobile
                if mobile_value:
                    # Remove any non-digit characters for validation
                    digits_only = ''.join(filter(str.isdigit, mobile_value))
                    if len(digits_only) != 11:
                        field_display = field_name.replace('_', ' ').title()
                        validation_errors.append(f"• {field_display} must be exactly 11 digits")
        
        # Show validation errors if any
        if validation_errors:
            QMessageBox.warning(
                self,
                "❌ Validation Error",
                f"Please fix the following issues:\n\n{chr(10).join(validation_errors)}\n\n"
                f"Note: Alternate fields are optional, but if filled, must follow the format rules."
            )
            return
        
        # Collect form data
        student_data = {}
        for field_name, widget in self.student_fields.items():
            if isinstance(widget, QLineEdit):
                student_data[field_name] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                student_data[field_name] = widget.currentText()
            elif isinstance(widget, QDateEdit):
                student_data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QTextEdit):
                student_data[field_name] = widget.toPlainText().strip()
        
        try:
            # TODO: Save to database with history tracking
            if self.is_editing:
                # Update existing student with history
                updates = {}
                for field_name, widget in self.student_fields.items():
                    if isinstance(widget, QLineEdit):
                        updates[field_name] = widget.text().strip()
                    elif isinstance(widget, QComboBox):
                        updates[field_name] = widget.currentText()
                    elif isinstance(widget, QDateEdit):
                        updates[field_name] = widget.date().toString("yyyy-MM-dd")
                    elif isinstance(widget, QTextEdit):
                        updates[field_name] = widget.toPlainText().strip()
                
                # For now, update table row (later integrate with database)
                self._update_table_row(student_data)
                self.student_updated.emit(student_data)
                
                # Show success message with history info
                QMessageBox.information(self, "Success", 
                    f"✅ Student information updated successfully!\n\n"
                    f"🔄 Changes have been recorded in history.\n"
                    f"📋 You can view complete change history using 'View Details' button.")
            else:
                # Add new student with initial history
                self._add_table_row(student_data)
                self.student_added.emit(student_data)
                
                # Show success message
                QMessageBox.information(self, "Success", 
                    f"✅ New student added successfully!\n\n"
                    f"📋 Initial record created in history.\n"
                    f"🔍 Use 'View Details' to see complete information and future changes.")
            
            self._reset_form()
            self._close_form()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to save student information:\n{str(e)}")
    
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
        dialog.resize(900, 700)
        
        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel(f"👤 Complete Information: {student_name}")
        header_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Bold';
                font-size: 24px;
                color: #374151;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
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
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Poppins Medium';
                font-weight: 600;
                font-size: 13px;
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
        
        # Get student details from database
        try:
            # Get current row data safely
            current_row = self.students_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Warning", "Please select a student first.")
                return
            
            # Extract data safely with proper error handling
            try:
                student_data = {
                    'id': student_id,
                    'name': student_name,
                    'father_name': self.students_table.item(current_row, 2).text() if self.students_table.item(current_row, 2) else 'N/A',
                    'class': self.students_table.item(current_row, 3).text() if self.students_table.item(current_row, 3) else 'N/A',
                    'section': self.students_table.item(current_row, 4).text() if self.students_table.item(current_row, 4) else 'N/A',
                    'phone': self.students_table.item(current_row, 5).text() if self.students_table.item(current_row, 5) else 'N/A',
                }
            except Exception as data_error:
                # Fallback data if table extraction fails
                student_data = {
                    'id': student_id,
                    'name': student_name,
                    'father_name': 'N/A',
                    'class': 'N/A',
                    'section': 'N/A',
                    'phone': 'N/A',
                }
                print(f"Data extraction error: {data_error}")
            
            # Create tabs with error handling for each
            personal_tab = self._create_details_personal_tab(student_data)
            tab_widget.addTab(personal_tab, "👤 Personal Info")
            
            academic_tab = self._create_details_academic_tab(student_data)
            tab_widget.addTab(academic_tab, "🎓 Academic Info")
            
            contact_tab = self._create_details_contact_tab(student_data)
            tab_widget.addTab(contact_tab, "📞 Contact Info")
            
            history_tab = self._create_details_history_tab(student_id)
            tab_widget.addTab(history_tab, "📋 Change History")
            
            layout.addWidget(tab_widget)
            
            # Button box
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.setStyleSheet("""
                QDialogButtonBox QPushButton {
                    background: #6B7280;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: 'Poppins Medium';
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 100px;
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
            ("Student ID:", student_data.get('id', 'N/A')),
            ("Full Name:", student_data.get('name', 'N/A')),
            ("Date of Birth:", "To be updated"),
            ("Gender:", "To be updated"),
            ("CNIC/B-Form:", "To be updated"),
            ("Religion:", "To be updated"),
            ("Nationality:", "Pakistani"),
            ("Father's Name:", student_data.get('father_name', 'N/A')),
            ("Household Size:", "To be updated"),
            # Mother's Information
            ("Mother's Name:", "To be updated"),
            ("Mother's Marital Status:", "To be updated"),
            ("Mother's CNIC:", "To be updated"),
            ("Mother's CNIC DOI:", "To be updated"),
            ("Mother's CNIC Exp:", "To be updated"),
            ("Mother's MWA:", "To be updated"),
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
            ("School:", "Pine Valley School"),  # Will come from database
            ("Class:", student_data.get('class', 'N/A')),
            ("Section:", student_data.get('section', 'N/A')),
            ("Roll Number:", f"R{student_data.get('id', '000')}"),
            ("Registration Number:", f"REG{student_data.get('id', '000')}"),
            ("Admission Date:", "2024-01-15"),  # Will come from database
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
            ("Student Phone:", student_data.get('phone', 'N/A')),
            ("Home Address:", "House # 123, Street 5, Block A, City"),
            ("City:", "Lahore"),
            ("Emergency Contact:", student_data.get('phone', 'N/A')),
            # Alternate's Information
            ("Alternate Name:", student_data.get('father_name', 'N/A')),
            ("Alternate CNIC:", "To be updated"),
            ("Alternate CNIC DOI:", "To be updated"),
            ("Alternate CNIC Exp:", "To be updated"),
            ("Alternate Marital Status:", "To be updated"),
            ("Alternate MWA:", "To be updated"),
            ("Alternate Phone:", student_data.get('phone', 'N/A')),
            ("Alternate Relation:", "Father"),
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