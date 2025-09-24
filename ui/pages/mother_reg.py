"""Mother Registration management page UI implementation."""
import os
import sys
from typing import List, Dict, Optional, Any

# Add the project root to the path when running this file directly
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# PyQt5 imports
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QLineEdit, QHeaderView, QTableWidgetItem,
    QScrollArea, QSplitter, QTextEdit, QGroupBox, 
    QFormLayout, QCheckBox, QDateEdit, QSpinBox, QTabWidget, QDialog, 
    QDialogButtonBox, QSizePolicy, QApplication, QStackedWidget, QComboBox
)
from ui.components.custom_combo_box import CustomComboBox
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp, QTimer, QEvent, QObject
from PyQt5.QtGui import QFont, QIcon, QColor, QRegExpValidator

# Import SMISTable for enhanced table functionality
from ui.components.custom_table import SMISTable

# Internal imports
from models.database import Database
from config.settings import STUDENT_FIELDS
from ui.components.custom_date_picker import CustomDateEdit

# Import styling functions
from resources.styles import get_global_styles, get_modern_widget_styles, COLORS, FONT_REGULAR, FONT_SEMIBOLD
from ui.components.custom_combo_box import CustomComboBox
from ui.components.form_components import (
    FormModel, InputField, FormLabel
)
from resources.styles import (
     get_global_styles, COLORS, RADIUS, SPACING_LG, SPACING_MD, SPACING_SM,
    FONT_MEDIUM, FONT_SEMIBOLD, FONT_REGULAR, PRIMARY_COLOR, FOCUS_BORDER_COLOR,
    show_info_message, show_warning_message, show_error_message, show_critical_message,
    show_success_message, show_confirmation_message, show_delete_confirmation
)

# Import service layer and validation
try:
    from services.mother_service import MotherService, StudentData, MotherFilters
    from utils.mother_validation import MotherFormValidator, ValidationResult
except ImportError:
    # Fallback if service layer not available
    print("Warning: Service layer not available, using fallback")
    MotherService = None
    MotherFormValidator = None


# Improved Form styling utilities
class MotherRegPage(QWidget):
    """Modern Mother Registration management page with improved structure."""
    
    # Signals
    mother_added = pyqtSignal(dict)
    mother_updated = pyqtSignal(dict)
    mother_deleted = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Initialize core components first
        self._init_core_attributes()
        self._init_ui_components()
        self._setup_ui()
        self._load_initial_data()
    
    def _init_core_attributes(self):
        """Initialize core attributes and services."""
        # Services
        self.styles = get_global_styles()
        
        # Initialize services with fallback
        if MotherService:
            self.mother_service = MotherService()
        else:
            self.mother_service = None
            self.db = Database()  # Fallback to direct database access
            
        if MotherFormValidator:
            self.validator = MotherFormValidator()
        else:
            self.validator = None
        
        # Form state
        self.current_mother_id = None
        self.is_editing = False
        self._is_populating = False
        
        # Selection tracking
        self.selected_snos = set()
        
        # Field configurations
        self.principal_fields = [
            ("household_size", "Household Size", "spinbox"),
            ("household_head_name", "Household Head Name", "text"),
            ("mother_name", "Mother's Name", "text"),
            ("mother_marital_status", "Mother's Marital Status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("mother_cnic", "Mother's CNIC (13 digits)", "cnic"),
            ("mother_cnic_doi", "Mother's CNIC Date of Issue", "date"),
            ("mother_cnic_exp", "Mother's CNIC Expiry Date", "date"),
            ("mother_mwa", "Mother's MWA (11 digits)", "mwa"),
        ]
        
        self.guardian_fields = [
            ("household_size", "Household Size", "spinbox"),
            ("household_head_name", "Household Head Name", "text"),
            ("guardian_name", "Guardian Name", "text"),
            ("guardian_cnic", "Guardian CNIC (13 digits)", "cnic"),
            ("guardian_cnic_doi", "Guardian CNIC Date of Issue", "date"),
            ("guardian_cnic_exp", "Guardian CNIC Expiry Date", "date"),
            ("guardian_marital_status", "Guardian Marital Status", "combo", ["Single", "Married", "Divorced", "Widowed"]),
            ("guardian_mwa", "Guardian MWA (11 digits)", "mwa"),
            ("guardian_phone", "Guardian Phone (11 digits)", "phone"),
            ("guardian_relation", "Guardian Relation", "combo", ["Father", "Mother", "Uncle", "Aunt", "Grandfather", "Grandmother", "Other"]),
        ]
        
        # Apply proper styles instead of QSS
        self.apply_modern_styles()
    
    def _init_ui_components(self):
        """Initialize UI component references."""
        # Form fields
        self.mother_fields = {}
        
        # Filter components
        self.school_combo = None
        self.class_combo = None
        self.section_combo = None
        self.status_filter_combo = None
        self.filter_info_label = None
        
        # Action components
        self.save_btn = None
        self.cancel_btn = None
        self.view_selected_btn = None
        self.edit_btn = None
        self.delete_btn = None
        self.view_details_btn = None
        self.add_new_btn = None
        self.refresh_btn = None
        
        # Main UI components
        self.mothers_table = None
        self.form_frame = None
        self.selected_info_label = None
        self.recipient_combo = None
        self.content_splitter = None
        self.main_container = None
        self.form_grid = None
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        self._init_ui()
        self._connect_signals()
    
    def _load_initial_data(self):
        """Load initial data and filters."""
        self._load_initial_filter_data()
        self._load_data()

    def _init_ui(self):
        """Initialize the main UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 5, 20, 20)
        main_layout.setSpacing(0)
        
        # Create the main container
        self.main_container = QFrame()
        # Styling handled by global stylesheet
        
        # Main container layout
        main_container_layout = QVBoxLayout(self.main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)
        
        # Create filter section
        filter_frame = self._create_filter_section()
        main_container_layout.addWidget(filter_frame)
        
        # Create content area with splitter
        content_container = QFrame()
        # Styling handled by global stylesheet
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(15, 0, 15, 15)
        content_layout.setSpacing(0)
        
        # Create splitter for table and form
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # Create and add panels
        table_panel = self._create_table_panel()
        self.content_splitter.addWidget(table_panel)
        
        form_panel = self._create_form_panel()
        self.content_splitter.addWidget(form_panel)
        
        # Set initial sizes and hide form
        self.content_splitter.setSizes([1000, 0])
        self.content_splitter.setCollapsible(0, False)
        self.content_splitter.setCollapsible(1, False)
        self.form_frame.setVisible(False)
        
        # Add to layouts
        content_layout.addWidget(self.content_splitter)
        main_container_layout.addWidget(content_container, 1)
        main_layout.addWidget(self.main_container, 1)

    def _create_filter_section(self):
        """Create enhanced filter section with 2x2 grid layout."""
        filters_frame = QFrame()
        filters_frame.setFixedHeight(180)
        # Styling handled by global stylesheet
        
        filters_layout = QVBoxLayout(filters_frame)
        filters_layout.setSpacing(10)
        filters_layout.setContentsMargins(10, 4, 10, 4)
        
        # Create grid layout for filters
        filter_grid = QGridLayout()
        filter_grid.setSpacing(12)
        filter_grid.setVerticalSpacing(10)
        filter_grid.setColumnStretch(0, 1)
        filter_grid.setColumnStretch(1, 1)
        
        # Create filter combo boxes
        self.school_combo = CustomComboBox()
        self.school_combo.addItem("Please Select School")
        
        self.class_combo = CustomComboBox()
        self.class_combo.addItem("Please Select Class")
        
        self.section_combo = CustomComboBox()
        self.section_combo.addItem("Please Select Section")
        
        self.status_filter_combo = CustomComboBox()
        self.status_filter_combo.addItems([
            "All Status", "Active", "Inactive", "Duplicate"
        ])
        
        # Add widgets to grid: 2x2 layout
        filter_grid.addWidget(self.school_combo, 0, 0)
        filter_grid.addWidget(self.class_combo, 0, 1)
        filter_grid.addWidget(self.section_combo, 1, 0)
        filter_grid.addWidget(self.status_filter_combo, 1, 1)
        filters_layout.addLayout(filter_grid)
        
        # Create action bar
        action_bar = self._create_action_bar()
        filters_layout.addLayout(action_bar)
        
        return filters_frame

    def _create_action_bar(self):
        """Create the action bar with filter info and buttons."""
        action_bar = QHBoxLayout()
        action_bar.setContentsMargins(15, 5, 15, 5)
        action_bar.setSpacing(15)
        
        # Filter information label
        self.filter_info_label = QLabel("No filters applied")
        # Styling handled by global stylesheet
        action_bar.addWidget(self.filter_info_label)
        
        # Add spacer
        action_bar.addStretch(1)
        
        # Actions label
        actions_label = QLabel("Actions:")
        # Styling handled by global stylesheet
        action_bar.addWidget(actions_label)
        
        # Add header buttons (moved from header)
        self.add_new_btn = QPushButton("Add Mother")
        self.add_new_btn.setProperty("class", "success")
        action_bar.addWidget(self.add_new_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "secondary")
        action_bar.addWidget(self.refresh_btn)
        
        # Selected count info
        self.selected_info_label = QLabel("Selected: 0")
        # Styling handled by global stylesheet
        action_bar.addWidget(self.selected_info_label)
        
        # Create action buttons
        self.view_selected_btn = QPushButton("View Selected")
        self.view_selected_btn.setEnabled(False)
        self.view_selected_btn.setProperty("class", "secondary")
        action_bar.addWidget(self.view_selected_btn)
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setProperty("class", "secondary")
        action_bar.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setProperty("class", "warning")
        action_bar.addWidget(self.delete_btn)
        
        self.view_details_btn = QPushButton("View Details")
        self.view_details_btn.setEnabled(False)
        self.view_details_btn.setProperty("class", "primary")
        action_bar.addWidget(self.view_details_btn)
        
        return action_bar

    def _create_table_panel(self):
        """Create the table panel."""
        table_panel = QFrame()
        # Styling handled by global stylesheet
        
        panel_layout = QVBoxLayout(table_panel)
        panel_layout.setContentsMargins(0, 10, 0, 0)
        panel_layout.setSpacing(0)
        
        # Create and configure the SMISTable component
        self.mothers_table = SMISTable()
        self.mothers_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set up table headers and checkbox column
        headers = ["", "ID", "Student Name", "Father Name", "Class", "Section", "School"]
        self.mothers_table.setup_with_headers(headers, checkbox_column=0)
        
        # Connect to selection changed signal
        self.mothers_table.selectionChanged.connect(self._on_table_selection_changed)
        
        panel_layout.addWidget(self.mothers_table, 1)
        
        return table_panel

    def _create_form_panel(self):
        """Create the form panel for data entry."""
        self.form_frame = QFrame()
        # Styling handled by global stylesheet
        return self.form_frame

    def _connect_signals(self):
        """Connect all UI signals to their handlers."""
        # Header buttons
        self.add_new_btn.clicked.connect(self._show_add_form)
        self.refresh_btn.clicked.connect(self._load_data)
        
        # Filter combo boxes
        self.school_combo.currentTextChanged.connect(self._apply_filters)
        self.class_combo.currentTextChanged.connect(self._apply_filters)
        self.section_combo.currentTextChanged.connect(self._apply_filters)
        self.status_filter_combo.currentTextChanged.connect(self._apply_filters)
        
        # Action buttons
        self.edit_btn.clicked.connect(self._edit_mother)
        self.delete_btn.clicked.connect(self._delete_mother)
        self.view_details_btn.clicked.connect(self._view_details)
        self.view_selected_btn.clicked.connect(self._view_selected_list)
        
        # Table signals
        if self.mothers_table:
            self.mothers_table.table.itemDoubleClicked.connect(self._on_double_click)

    def _load_initial_filter_data(self):
        """Load initial data for filter dropdowns."""
        try:
            # Clear existing items
            self.school_combo.clear()
            self.class_combo.clear()
            self.section_combo.clear()
            
            # Add default options
            self.school_combo.addItem("All Schools")
            self.class_combo.addItem("All Classes")
            self.section_combo.addItem("All Sections")
            
            # Load data from service or database
            if self.mother_service:
                schools = self.mother_service.get_schools()
                classes = self.mother_service.get_classes()
                sections = self.mother_service.get_sections()
            else:
                schools = self.db.get_schools() if hasattr(self, 'db') else []
                classes = self.db.get_classes() if hasattr(self, 'db') else []
                sections = self.db.get_sections() if hasattr(self, 'db') else []
            
            # Populate dropdowns
            for school in schools:
                school_name = school.get('name', 'Unknown School')
                school_id = school.get('id', '')
                self.school_combo.addItem(school_name, school_id)
                
            for class_name in classes:
                self.class_combo.addItem(class_name)
                
            for section_name in sections:
                self.section_combo.addItem(section_name)
                
        except Exception as e:
            print(f"Error loading filter data: {e}")
            # Add fallback data
            self.school_combo.addItems(["Pine Valley School", "Green Park Academy"])
            self.class_combo.addItems([f"Class {i}" for i in range(1, 13)])
            self.section_combo.addItems(["A", "B", "C", "D", "E"])

    def _load_data(self):
        """Load student data that needs mother/guardian information."""
        try:
            filters = self._get_current_filters()
            
            if self.mother_service:
                students = self.mother_service.get_students_needing_mother_info(filters)
                table_data = [student.to_table_row() for student in students]
            else:
                # Fallback to direct database access
                students = self._get_students_needing_mother_info_fallback(filters)
                table_data = [self._format_student_to_row_data(student) for student in students]
            
            self._populate_table(table_data)
            
        except Exception as e:
            print(f"Error loading student data: {e}")
            show_warning_message("Data Load Error", f"Failed to load student data: {str(e)}")

    def _get_current_filters(self):
        """Get current filter values as MotherFilters object."""
        if MotherFilters:
            return MotherFilters(
                school=self.school_combo.currentText(),
                class_name=self.class_combo.currentText(),
                section=self.section_combo.currentText(),
                status=self.status_filter_combo.currentText()
            )
        else:
            # Fallback dictionary
            return {
                "school": self.school_combo.currentText(),
                "class": self.class_combo.currentText(),
                "section": self.section_combo.currentText(),
                "status": self.status_filter_combo.currentText()
            }

    def _get_students_needing_mother_info_fallback(self, filters):
        """Fallback method for getting students when service layer not available."""
        where_clauses = [
            "is_deleted = 0",
            "status = 'Active'",
            """(
                (COALESCE(mother_name,'') = '' OR COALESCE(mother_cnic,'') = '') 
                AND 
                (COALESCE(alternate_name,'') = '' OR COALESCE(alternate_cnic,'') = '')
            )"""
        ]
        params = []
        
        # Apply filters
        if isinstance(filters, dict):
            if filters.get("class") and filters["class"] not in ["Please Select Class", "All Classes"]:
                where_clauses.append("class = ?")
                params.append(filters["class"])
                
            if filters.get("section") and filters["section"] not in ["Please Select Section", "All Sections"]:
                where_clauses.append("section = ?")
                params.append(filters["section"])
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}"
        sql = f"""
            SELECT student_id, student_name, father_name, class, section 
            FROM students {where_sql} 
            ORDER BY student_name
        """
        
        return self.db.execute_secure_query(sql, tuple(params))

    def _format_student_to_row_data(self, student_data):
        """Format student data into table row format."""
        def get_value(data, key, default=""):
            if hasattr(data, 'keys'):
                return data.get(key, default)
            return getattr(data, key, default)
        
        return [
            "",  # Checkbox column
            str(get_value(student_data, 'student_id')),
            str(get_value(student_data, 'student_name')),
            str(get_value(student_data, 'father_name')),
            str(get_value(student_data, 'class')),
            str(get_value(student_data, 'section')),
            str(get_value(student_data, 'school', ''))
        ]

    def _populate_table(self, table_data):
        """Populate table with student data."""
        self._is_populating = True
        
        # Use SMISTable's populate_data method
        self.mothers_table.populate_data(table_data, id_column=1)
        
        # Set selected rows if any
        if self.selected_snos:
            self.mothers_table.set_selected_rows(list(self.selected_snos))
        
        self._is_populating = False
        self._update_selected_summary()

    def _apply_filters(self):
        """Apply current filter settings and reload data."""
        filters = self._get_current_filters()
        
        # Update filter info label
        filter_texts = []
        
        if hasattr(filters, 'get_active_filters'):
            active_filters = filters.get_active_filters()
            for key, value in active_filters.items():
                filter_texts.append(f"{key.title()}: {value}")
        else:
            # Fallback for dictionary filters
            for key, value in filters.items():
                if value and value not in ["Please Select", "All"]:
                    filter_texts.append(f"{key.title()}: {value}")
        
        if filter_texts:
            self.filter_info_label.setText("Filters: " + " | ".join(filter_texts))
        else:
            self.filter_info_label.setText("No filters applied")
        
        # Reload data
        self._load_data()

    def _on_table_selection_changed(self, selected_ids):
        """Handle table selection changes."""
        self.selected_snos = set(selected_ids)
        self._on_selection_changed()
        self._update_selected_summary()

    def _on_selection_changed(self):
        """Update button states based on selection."""
        has_selection = bool(self.selected_snos)
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.view_details_btn.setEnabled(has_selection)

    def _update_selected_summary(self):
        """Update the selected count display."""
        count = len(self.selected_snos)
        if self.selected_info_label:
            self.selected_info_label.setText(f"Selected: {count}")
        if self.view_selected_btn:
            self.view_selected_btn.setEnabled(count > 0)

    def _show_add_form(self):
        """Show the form for adding mother/guardian information."""
        try:
            if not self._validate_form_frame():
                return
            
            self._setup_form_layout()
            self.form_frame.setVisible(True)
            
            # Adjust splitter to show both table and form
            total_width = self.content_splitter.width()
            table_width = int(total_width * 0.4)
            form_width = int(total_width * 0.6)
            self.content_splitter.setSizes([table_width, form_width])
            
        except Exception as e:
            show_critical_message("Error", f"Failed to open form:\n{str(e)}")

    def _validate_form_frame(self):
        """Validate that form frame is available."""
        if not hasattr(self, 'form_frame') or not self.form_frame:
            show_critical_message("Error", "Form frame not available.")
            return False
        return True

    def _setup_form_layout(self):
        """Setup the main form layout."""
        # Clear existing layout
        current_layout = self.form_frame.layout()
        if current_layout:
            QWidget().setLayout(current_layout)
        
        # Apply styling
        # Styling handled by global stylesheet
        
        # Create main layout
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(10, 10, 5, 10)
        form_layout.setSpacing(20)
        
        # Add form sections
        form_layout.addWidget(self._create_recipient_container())
        form_layout.addWidget(self._create_fields_container(), 1)
        form_layout.addWidget(self._create_actions_container())
        
        self.form_frame.setLayout(form_layout)
        self._on_recipient_type_changed()

    def _create_recipient_container(self):
        """Create recipient type selection container."""
        container = QFrame()
        # Styling handled by global stylesheet
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 25, 5)
        layout.setSpacing(0)
        
        self.recipient_combo = CustomComboBox()
        self.recipient_combo.addItems(["Principal", "Alternate Guardian"])
        self.recipient_combo.setCurrentText("Principal")
        self.recipient_combo.currentTextChanged.connect(self._on_recipient_type_changed)
        
        layout.addWidget(self.recipient_combo)
        layout.addStretch()
        
        return container

    def _create_fields_container(self):
        """Create scrollable form fields container."""
        container = QFrame()
        # Styling handled by global stylesheet
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(10)
        
        # Create scrollable area
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("")
        # Styling handled by global stylesheet
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("")
        # Styling handled by global stylesheet
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(10)
        
        # Create form grid
        self.form_grid = QGridLayout()
        self.form_grid.setVerticalSpacing(5)
        self.form_grid.setHorizontalSpacing(25)
        self.form_grid.setContentsMargins(0, 0, 0, 0)
        
        # Initialize fields
        self.mother_fields = {}
        self._create_form_fields()
        
        scroll_layout.addLayout(self.form_grid)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        return container

    def _create_actions_container(self):
        """Create action buttons container."""
        container = QFrame()
        # Styling handled by global stylesheet
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Create buttons
        reset_btn = QPushButton("Reset")
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save Information")
        apply_all_checkbox = QCheckBox("Apply to all filtered rows")
        
        # Apply styling
        reset_btn.setProperty("class", "secondary")
        cancel_btn.setProperty("class", "warning")
        save_btn.setProperty("class", "success")
        
        # Connect signals
        reset_btn.clicked.connect(self._reset_form)
        cancel_btn.clicked.connect(self._show_table)
        save_btn.clicked.connect(lambda: self._save_form_data(apply_all_checkbox.isChecked()))
        
        # Layout buttons
        layout.addWidget(reset_btn)
        layout.addWidget(cancel_btn)
        layout.addWidget(apply_all_checkbox)
        layout.addStretch()
        layout.addWidget(save_btn)
        
        return container

    def _create_form_fields(self):
        """Create form fields based on configurations."""
        # Create unique fields set
        all_unique_fields = []
        field_names_added = set()
        
        for field_config in self.principal_fields + self.guardian_fields:
            field_name = field_config[0]
            if field_name not in field_names_added:
                all_unique_fields.append(field_config)
                field_names_added.add(field_name)
        
        self._add_fields_to_grid(all_unique_fields)

    def _add_fields_to_grid(self, fields):
        """Add field configurations to the grid layout."""
        row, col = 0, 0
        
        for field_name, label_text, field_type, *extras in fields:
            field_widget = self._create_field_widget(field_name, label_text, field_type, extras)
            self.mother_fields[field_name] = field_widget
            
            self.form_grid.addWidget(field_widget, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def _create_field_widget(self, field_name, label_text, field_type, extra_params=None):
        """Create a form field widget with label and input."""
        container = QWidget()
        container.setObjectName(f"FormFieldContainer_{field_name}")
        # Styling handled by global stylesheet
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        container.setMinimumHeight(90)
        container.setMinimumWidth(250)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create label
        label = FormLabel(label_text)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label)
        
        # Create input widget
        widget = self._create_input_widget(field_type, field_name, label_text, extra_params)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(widget)
        
        layout.addStretch(1)
        
        return container

    def _create_input_widget(self, field_type, field_name, label_text, extra_params):
        """Create the appropriate input widget based on field type."""
        if field_type in ["text", "cnic", "phone", "mwa"]:
            widget = InputField.create_field(
                "cnic" if field_type == "cnic" else "phone" if field_type in ["phone", "mwa"] else "text", 
                label_text
            )
            widget.setObjectName(f"FormField_{field_name}")
            
            # Styling handled by global stylesheet
            
        elif field_type == "date":
            widget = CustomDateEdit(icon_only=True)
            widget.setDate(QDate.currentDate())
            widget.setObjectName(f"CustomDateEdit_{field_name}")
            
        elif field_type == "combo":
            widget = CustomComboBox()
            widget.setObjectName(f"CustomComboBox_{field_name}")
            if extra_params and len(extra_params) > 0:
                widget.addItems(extra_params[0])
                
        elif field_type == "spinbox":
            widget = InputField.create_field("spinbox", label_text)
            widget.setObjectName(f"FormField_{field_name}")
            
            # Styling handled by global stylesheet
            
        else:
            widget = InputField.create_field("text", label_text)
            widget.setObjectName(f"FormField_{field_name}")
            
            # Styling handled by global stylesheet
        
        return widget

    def _on_recipient_type_changed(self):
        """Show/hide fields based on recipient type selection."""
        if not hasattr(self, 'recipient_combo') or not self.recipient_combo:
            return
            
        recipient_type = self.recipient_combo.currentText()
        
        # Hide all fields first
        for field_name in self.mother_fields:
            self.mother_fields[field_name].setVisible(False)
        
        if recipient_type == "Principal":
            # Show principal (mother) fields
            for field_name, _, _, *_ in self.principal_fields:
                if field_name in self.mother_fields:
                    self.mother_fields[field_name].setVisible(True)
        else:  # Alternate Guardian
            # Show guardian fields
            for field_name, _, _, *_ in self.guardian_fields:
                if field_name in self.mother_fields:
                    self.mother_fields[field_name].setVisible(True)

    def _reset_form(self):
        """Reset all form fields to default values."""
        for field_name, container in self.mother_fields.items():
            layout = container.layout()
            if layout and layout.count() >= 2:
                widget = layout.itemAt(1).widget()
                
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QSpinBox):
                    widget.setValue(1)
                elif isinstance(widget, CustomComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, (QDateEdit, CustomDateEdit)):
                    widget.setDate(QDate.currentDate())

    def _show_table(self):
        """Show the table panel and hide form."""
        self.form_frame.setVisible(False)
        self.content_splitter.setSizes([1000, 0])

    def _save_form_data(self, apply_all):
        """Save form data with validation."""
        try:
            # Get target students
            target_snos = []
            if apply_all:
                for r in range(self.mothers_table.table.rowCount()):
                    s_no_item = self.mothers_table.table.item(r, 1)
                    if s_no_item and s_no_item.text().strip():
                        target_snos.append(s_no_item.text().strip())
            else:
                target_snos = list(self.selected_snos)
            
            if not target_snos:
                show_warning_message("No Students Selected", 
                                  "Select students or tick 'Apply to all filtered rows'.")
                return
            
            # Collect and validate form data
            form_data = self._collect_form_data()
            recipient_type = self.recipient_combo.currentText()
            
            # Validate if validator available
            if self.validator:
                validation_result = self.validator.validate_mother_form(form_data, recipient_type)
                if not validation_result.is_valid:
                    error_msg = "Please fix the following errors:\n\n" + "\n".join(validation_result.errors)
                    show_warning_message("Validation Errors", error_msg)
                    return
            
            # Save data
            updated_count = 0
            if self.mother_service:
                if len(target_snos) == 1:
                    updated = self.mother_service.update_mother_info(target_snos[0], form_data)
                    updated_count = 1 if updated else 0
                else:
                    updated_count = self.mother_service.update_mother_info_bulk(target_snos, form_data)
            else:
                # Fallback implementation
                updated_count = self._save_form_data_fallback(target_snos, form_data)
            
            if updated_count > 0:
                show_success_message("Saved", 
                                      f"{recipient_type} info saved to {updated_count} student(s).")
                self._show_table()
                self.selected_snos.clear()
                self._load_data()
            else:
                show_info_message("No Changes", "Nothing to save.")
                
        except Exception as e:
            show_critical_message("Save Error", f"Failed to save:\n{str(e)}")

    def _collect_form_data(self):
        """Collect data from form fields."""
        form_data = {}
        recipient_type = self.recipient_combo.currentText()
        
        # Get visible fields based on recipient type
        visible_fields = self.principal_fields if recipient_type == "Principal" else self.guardian_fields
        
        for field_name, _, _, *_ in visible_fields:
            if field_name in self.mother_fields:
                container = self.mother_fields[field_name]
                layout = container.layout()
                if layout and layout.count() >= 2:
                    widget = layout.itemAt(1).widget()
                    
                    if isinstance(widget, QLineEdit):
                        form_data[field_name] = widget.text().strip()
                    elif isinstance(widget, QSpinBox):
                        form_data[field_name] = widget.value()
                    elif isinstance(widget, CustomComboBox):
                        form_data[field_name] = widget.currentText()
                    elif isinstance(widget, (QDateEdit, CustomDateEdit)):
                        form_data[field_name] = widget.date().toString("yyyy-MM-dd")
        
        return form_data

    def _save_form_data_fallback(self, student_ids, form_data):
        """Fallback save method when service layer not available."""
        updated_count = 0
        
        # Map form fields to database columns
        field_mapping = {
            'household_size': 'household_size',
            'household_head_name': 'household_head_name',
            'mother_name': 'mother_name',
            'mother_marital_status': 'mother_marital_status',
            'mother_cnic': 'mother_cnic',
            'mother_cnic_doi': 'mother_cnic_doi',
            'mother_cnic_exp': 'mother_cnic_exp',
            'mother_mwa': 'mother_mwa',
            'guardian_name': 'alternate_name',
            'guardian_cnic': 'alternate_cnic',
            'guardian_cnic_doi': 'alternate_cnic_doi',
            'guardian_cnic_exp': 'alternate_cnic_exp',
            'guardian_marital_status': 'alternate_marital_status',
            'guardian_mwa': 'alternate_mwa',
            'guardian_phone': 'alternate_phone',
            'guardian_relation': 'alternate_relationship_with_mother'
        }
        
        for student_id in student_ids:
            try:
                set_clauses = []
                params = []
                
                for field_key, db_column in field_mapping.items():
                    if field_key in form_data and form_data[field_key]:
                        set_clauses.append(f"{db_column} = ?")
                        params.append(form_data[field_key])
                
                if set_clauses:
                    params.append(student_id)
                    sql = f"UPDATE students SET {', '.join(set_clauses)} WHERE student_id = ?"
                    
                    result = self.db.execute_secure_query(sql, tuple(params))
                    if result is not None:
                        updated_count += 1
                        
            except Exception as e:
                print(f"Error updating student {student_id}: {e}")
        
        return updated_count

    def _view_details(self):
        """Show details of selected student."""
        selected_ids = self.mothers_table.get_selected_rows()
        if not selected_ids:
            show_warning_message("No Selection", "Please select a record to view details.")
            return
        
        student_id = selected_ids[0]
        student_details = self._get_student_details(student_id)
        
        if student_details:
            details_text = "\n".join([f"{key}: {value}" for key, value in student_details.items()])
            show_info_message("Student Details", details_text)
        else:
            show_warning_message("Error", "Could not find student details.")

    def _get_student_details(self, student_id):
        """Get detailed information for a student."""
        # Find student data from table
        for row in range(self.mothers_table.table.rowCount()):
            item = self.mothers_table.table.item(row, 1)
            if item and item.text() == student_id:
                return {
                    "ID": student_id,
                    "Name": self.mothers_table.table.item(row, 2).text() if self.mothers_table.table.item(row, 2) else "",
                    "Father": self.mothers_table.table.item(row, 3).text() if self.mothers_table.table.item(row, 3) else "",
                    "Class": self.mothers_table.table.item(row, 4).text() if self.mothers_table.table.item(row, 4) else "",
                    "Section": self.mothers_table.table.item(row, 5).text() if self.mothers_table.table.item(row, 5) else "",
                    "School": self.mothers_table.table.item(row, 6).text() if self.mothers_table.table.item(row, 6) else ""
                }
        return None

    def _edit_mother(self):
        """Edit selected mother record."""
        selected_ids = self.mothers_table.get_selected_rows()
        if not selected_ids:
            show_warning_message("No Selection", "Please select a mother to edit.")
            return
        
        # For now, show edit form (future enhancement)
        self._show_add_form()

    def _delete_mother(self):
        """Delete selected mother record."""
        selected_ids = self.mothers_table.get_selected_rows()
        if not selected_ids:
            show_warning_message("No Selection", "Please select a mother to delete.")
            return
        
        student_id = selected_ids[0]
        student_details = self._get_student_details(student_id)
        student_name = student_details.get("Name", "Unknown") if student_details else "Unknown"
        
        if show_delete_confirmation(f"mother info for: {student_name}"):
            # Implement deletion logic
            show_success_message("Deleted", f"Mother info for '{student_name}' deleted.")
            self._load_data()

    def _view_selected_list(self):
        """Show dialog with selected students list."""
        selected_list = []
        visible_map = {}
        
        # Create mapping of visible students
        for r in range(self.mothers_table.table.rowCount()):
            sno_item = self.mothers_table.table.item(r, 1)
            name_item = self.mothers_table.table.item(r, 2)
            if sno_item and name_item:
                visible_map[sno_item.text().strip()] = name_item.text().strip()
        
        # Build selected list
        for sno in sorted(self.selected_snos):
            name = visible_map.get(sno, "(hidden)")
            selected_list.append(f"{sno} - {name}")
        
        if not selected_list:
            show_info_message("Selected Students", "No students selected.")
            return
        
        # Show dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Selected Students")
        dlg.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dlg)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText("\n".join(selected_list))
        layout.addWidget(text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)
        
        dlg.exec_()

    def _on_double_click(self, item):
        """Handle double-click on table item."""
        self._view_details()

    def apply_modern_styles(self):
        """Apply modern styles using centralized theme.py styling."""
        # Get modern widget styles from theme.py
        widget_style = get_modern_widget_styles()
        self.setStyleSheet(widget_style)


# Standalone application class
class StandaloneMotherRegApp(QApplication):
    """Standalone application to run the Mother Registration form."""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setStyle("Fusion")
        self.setApplicationName("Mother Registration")
        
        # Initialize database connection
        try:
            from models.database import Database
            self.db = Database()
            print("Database connection established")
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
            self.db = None
        
        # Create main window
        self.main_window = QWidget()
        self.main_window.setWindowTitle("Mother Registration Form")
        self.main_window.setGeometry(100, 100, 1200, 800)
        
        # Create layout and add mother registration page
        main_layout = QVBoxLayout(self.main_window)
        self.mother_reg_page = MotherRegPage()
        main_layout.addWidget(self.mother_reg_page)
        
        # Show window
        self.main_window.show()


# Main execution
if __name__ == "__main__":
    import sys
    print("Running Mother Registration form standalone...")
    app = StandaloneMotherRegApp(sys.argv)
    sys.exit(app.exec_())