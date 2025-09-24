"""
Reusable registration form component for the SMIS application.
This component can be used for both student and mother registration forms,
reducing code duplication and ensuring consistent UI.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QFrame, QGridLayout, 
                           QLineEdit, QMessageBox, QTableWidget, QHeaderView,
                           QScrollArea, QTableWidgetItem, QSplitter, QTextEdit,
                           QGroupBox, QFormLayout, QCheckBox, QDateEdit,
                           QSpinBox, QTabWidget, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QIcon, QColor, QRegExpValidator
from resources.styles import COLORS, SPACING_MD, SPACING_LG
from resources.styles.messages import (
    show_info_message, show_warning_message, show_error_message, 
    show_critical_message, show_success_message, show_confirmation_message, 
    show_delete_confirmation
)

class RegistrationFormBase(QFrame):
    """
    Base class for registration forms used in student and mother registration.
    
    This component provides a standardized layout and styling for registration forms
    and can be customized for different registration types.
    """
    
    # Signals
    form_submitted = pyqtSignal(dict)
    form_cancelled = pyqtSignal()
    
    def __init__(self, form_title="Registration Form", parent=None):
        """
        Initialize the registration form.
        
        Args:
            form_title (str): Title of the form
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        self.form_title = form_title
        self.field_values = {}
        self.required_fields = []
        self.field_validators = {}
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the form UI structure."""
        # Style the frame
        self.setStyleSheet(f"""
            RegistrationFormBase {{
                background: white;
                border-radius: 16px;
                border: 1.5px solid {COLORS['gray_200']};
                min-width: 600px;
                max-width: 900px;
            }}
            QLabel#formTitle {{
                font-size: 18px;
                font-weight: bold;
                color: {COLORS['primary']};
                padding: {SPACING_MD};
            }}
            QLabel.fieldLabel {{
                font-weight: bold;
                color: {COLORS['gray_700']};
            }}
            QPushButton#submitButton {{
                background-color: {COLORS['primary']};
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton#submitButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
            QPushButton#cancelButton {{
                background-color: {COLORS['gray_200']};
                color: {COLORS['gray_700']};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton#cancelButton:hover {{
                background-color: {COLORS['gray_300']};
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Form title
        title_label = QLabel(self.form_title)
        title_label.setObjectName("formTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Form content container (to be filled by subclasses)
        self.form_content = QWidget()
        self.form_layout = QFormLayout(self.form_content)
        self.form_layout.setSpacing(12)
        self.form_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.form_content)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.setObjectName("submitButton")
        self.submit_button.clicked.connect(self._on_submit_clicked)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        main_layout.addLayout(button_layout)
    
    def add_text_field(self, field_id, label, required=False, validator=None, placeholder=""):
        """
        Add a text input field to the form.
        
        Args:
            field_id (str): Unique identifier for the field
            label (str): Display label for the field
            required (bool): Whether the field is required
            validator (QValidator): Validator for the field
            placeholder (str): Placeholder text
            
        Returns:
            QLineEdit: The created line edit widget
        """
        field_label = QLabel(label)
        field_label.setObjectName(f"{field_id}Label")
        field_label.setProperty("class", "fieldLabel")
        
        field = QLineEdit()
        field.setObjectName(field_id)
        field.setPlaceholderText(placeholder)
        
        if validator:
            field.setValidator(validator)
            self.field_validators[field_id] = validator
        
        if required:
            self.required_fields.append(field_id)
            field_label.setText(f"{label} *")
        
        self.form_layout.addRow(field_label, field)
        self.field_values[field_id] = field
        return field
    
    def add_dropdown(self, field_id, label, options=None, required=False):
        """
        Add a dropdown field to the form.
        
        Args:
            field_id (str): Unique identifier for the field
            label (str): Display label for the field
            options (list): List of options for the dropdown
            required (bool): Whether the field is required
            
        Returns:
            QComboBox: The created combo box widget
        """
        field_label = QLabel(label)
        field_label.setObjectName(f"{field_id}Label")
        field_label.setProperty("class", "fieldLabel")
        
        field = QComboBox()
        field.setObjectName(field_id)
        
        if options:
            field.addItems(options)
        
        if required:
            self.required_fields.append(field_id)
            field_label.setText(f"{label} *")
        
        self.form_layout.addRow(field_label, field)
        self.field_values[field_id] = field
        return field
    
    def add_date_field(self, field_id, label, required=False):
        """
        Add a date picker field to the form.
        
        Args:
            field_id (str): Unique identifier for the field
            label (str): Display label for the field
            required (bool): Whether the field is required
            
        Returns:
            QDateEdit: The created date edit widget
        """
        field_label = QLabel(label)
        field_label.setObjectName(f"{field_id}Label")
        field_label.setProperty("class", "fieldLabel")
        
        field = QDateEdit()
        field.setObjectName(field_id)
        field.setCalendarPopup(True)
        field.setDate(QDate.currentDate())
        
        if required:
            self.required_fields.append(field_id)
            field_label.setText(f"{label} *")
        
        self.form_layout.addRow(field_label, field)
        self.field_values[field_id] = field
        return field
    
    def add_checkbox(self, field_id, label):
        """
        Add a checkbox field to the form.
        
        Args:
            field_id (str): Unique identifier for the field
            label (str): Display label for the field
            
        Returns:
            QCheckBox: The created checkbox widget
        """
        field = QCheckBox(label)
        field.setObjectName(field_id)
        
        self.form_layout.addRow("", field)
        self.field_values[field_id] = field
        return field
    
    def add_numeric_field(self, field_id, label, min_val=0, max_val=100, required=False):
        """
        Add a numeric spinner field to the form.
        
        Args:
            field_id (str): Unique identifier for the field
            label (str): Display label for the field
            min_val (int): Minimum value
            max_val (int): Maximum value
            required (bool): Whether the field is required
            
        Returns:
            QSpinBox: The created spin box widget
        """
        field_label = QLabel(label)
        field_label.setObjectName(f"{field_id}Label")
        field_label.setProperty("class", "fieldLabel")
        
        field = QSpinBox()
        field.setObjectName(field_id)
        field.setMinimum(min_val)
        field.setMaximum(max_val)
        
        if required:
            self.required_fields.append(field_id)
            field_label.setText(f"{label} *")
        
        self.form_layout.addRow(field_label, field)
        self.field_values[field_id] = field
        return field
    
    def add_text_area(self, field_id, label, required=False, placeholder=""):
        """
        Add a text area field to the form.
        
        Args:
            field_id (str): Unique identifier for the field
            label (str): Display label for the field
            required (bool): Whether the field is required
            placeholder (str): Placeholder text
            
        Returns:
            QTextEdit: The created text edit widget
        """
        field_label = QLabel(label)
        field_label.setObjectName(f"{field_id}Label")
        field_label.setProperty("class", "fieldLabel")
        
        field = QTextEdit()
        field.setObjectName(field_id)
        field.setPlaceholderText(placeholder)
        
        if required:
            self.required_fields.append(field_id)
            field_label.setText(f"{label} *")
        
        self.form_layout.addRow(field_label, field)
        self.field_values[field_id] = field
        return field
    
    def get_form_data(self):
        """
        Get the form data as a dictionary.
        
        Returns:
            dict: Form data with field_id as keys
        """
        data = {}
        
        for field_id, widget in self.field_values.items():
            if isinstance(widget, QLineEdit):
                data[field_id] = widget.text()
            elif isinstance(widget, QComboBox):
                data[field_id] = widget.currentText()
            elif isinstance(widget, QDateEdit):
                data[field_id] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QCheckBox):
                data[field_id] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                data[field_id] = widget.value()
            elif isinstance(widget, QTextEdit):
                data[field_id] = widget.toPlainText()
        
        return data
    
    def _validate_form(self):
        """
        Validate the form data.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check required fields
        for field_id in self.required_fields:
            widget = self.field_values.get(field_id)
            
            if not widget:
                continue
                
            if isinstance(widget, QLineEdit) and not widget.text():
                field_label = self.form_layout.labelForField(widget).text().replace(' *', '')
                return False, f"Please fill in the required field: {field_label}"
            
            elif isinstance(widget, QComboBox) and widget.currentText() == "":
                field_label = self.form_layout.labelForField(widget).text().replace(' *', '')
                return False, f"Please select an option for: {field_label}"
            
            elif isinstance(widget, QTextEdit) and not widget.toPlainText():
                field_label = self.form_layout.labelForField(widget).text().replace(' *', '')
                return False, f"Please fill in the required field: {field_label}"
        
        # Additional custom validation can be implemented by subclasses
        return True, ""
    
    def set_form_data(self, data):
        """
        Set form data from a dictionary.
        
        Args:
            data (dict): Form data with field_id as keys
        """
        for field_id, value in data.items():
            widget = self.field_values.get(field_id)
            
            if not widget:
                continue
                
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.fromString(str(value), "yyyy-MM-dd"))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value))
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(value))
    
    def reset_form(self):
        """Clear all form fields."""
        for widget in self.field_values.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QSpinBox):
                widget.setValue(0)
            elif isinstance(widget, QTextEdit):
                widget.clear()
    
    def _on_submit_clicked(self):
        """Handle submit button click."""
        is_valid, error_message = self._validate_form()
        
        if not is_valid:
            show_warning_message(self, "Validation Error", error_message)
            return
        
        form_data = self.get_form_data()
        self.form_submitted.emit(form_data)
    
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.form_cancelled.emit()
