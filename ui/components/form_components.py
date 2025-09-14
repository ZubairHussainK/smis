import os
from PyQt5.QtWidgets import (QLineEdit, QDateEdit, QSpinBox, QComboBox,
                           QSizePolicy, QWidget, QLabel)
from PyQt5.QtCore import Qt, QDate, QRegExp, QTimer
from PyQt5.QtGui import QRegExpValidator

from .custom_combo_box import CustomComboBox
from .custom_date_picker import CustomDateEdit

# Constants
TEXT_COLOR = "#333333"        # Normal text
BORDER_COLOR = "#cccccc"      # Input borders
BORDER_RADIUS = "12px"        # Standard border radius
INPUT_PADDING = "15px 20px"   # Standard input padding
PRIMARY_COLOR = "#0175b6"     # Selection, hover, focus blue
LIGHTER_COLOR = "#ffffff"     # Input field background
PLACEHOLDER_COLOR = "#999999" # Placeholder text

# Base Style for Form Fields with more specific selectors and !important flags
BASE_FIELD_STYLE = f"""
    QLineEdit[class="FormField"], 
    QLineEdit#FormField_*,
    QSpinBox[class="FormField"],
    QSpinBox#FormField_* {{
        background-color: {LIGHTER_COLOR} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: {BORDER_RADIUS} !important;
        padding: {INPUT_PADDING} !important;
        font-size: 14px !important;
        color: {TEXT_COLOR} !important;
        margin-bottom: 10px !important;
        min-height: 32px !important;
        /* Removed fixed height to allow flexibility */
        margin-top: 3px !important;
        margin: 0 !important;
        min-width: 150px !important;  /* Minimum width */
        width: 100% !important;       /* Fill available space */
    }}
    
    QLineEdit[class="FormField"]:focus,
    QLineEdit#FormField_*:focus,
    QSpinBox[class="FormField"]:focus,
    QSpinBox#FormField_*:focus {{
        border: 2px solid {PRIMARY_COLOR} !important;
    }}
    
    /* Hide spinbox buttons completely */
    QSpinBox::up-button, 
    QSpinBox::down-button,
    QSpinBox[class="FormField"]::up-button,
    QSpinBox[class="FormField"]::down-button,
    QSpinBox#FormField_*::up-button,
    QSpinBox#FormField_*::down-button {{
        width: 0px !important;
        height: 0px !important;
        border: none !important;
        background: none !important;
        display: none !important;
        background-color: {LIGHTER_COLOR} !important;
        outline: none !important;
    }}
    
    QLineEdit[class="FormField"]::placeholder,
    QLineEdit#FormField_*::placeholder {{
        color: {PLACEHOLDER_COLOR} !important;
        font-style: normal !important;
    }}
"""


class FormModel:
    """Model to handle form data and validation."""
    
    def __init__(self):
        self.fields = {}
        self.errors = {}
        self.validators = {}
        
    def set_field(self, name, value):
        """Set field value."""
        self.fields[name] = value
        
    def get_field(self, name):
        """Get field value."""
        return self.fields.get(name, None)
    
    def add_validator(self, field_name, validator_func, error_message):
        """
        Add a validator function for a field.
        
        Args:
            field_name (str): Name of the field to validate
            validator_func (callable): Function that takes the field value and returns True if valid
            error_message (str): Error message to display if validation fails
        """
        self.validators[field_name] = {
            'func': validator_func,
            'error': error_message
        }
    
    def validate_field(self, field_name):
        """
        Validate a single field and return result.
        
        Args:
            field_name (str): Name of the field to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if field_name not in self.fields:
            return True, None
            
        value = self.fields.get(field_name)
        
        # Check custom validators
        if field_name in self.validators:
            validator = self.validators[field_name]
            if not validator['func'](value):
                return False, validator['error']
                
        return True, None
        
    def validate(self):
        """
        Validate all fields.
        
        Returns:
            tuple: (is_valid, errors_dict)
        """
        self.errors = {}
        valid = True
        
        # Validate all fields that have validators
        for field_name in self.fields:
            field_valid, error_msg = self.validate_field(field_name)
            if not field_valid:
                valid = False
                self.errors[field_name] = error_msg
                
        # Add common built-in validators
        for field_name, value in self.fields.items():
            if field_name.endswith('_cnic') and value:
                # CNIC must be 13 digits
                if not (isinstance(value, str) and len(value.replace('-', '').strip()) == 13):
                    valid = False
                    self.errors[field_name] = "CNIC must be 13 digits"
            
            elif field_name.endswith('_phone') and value:
                # Phone must be 11 digits
                if not (isinstance(value, str) and len(value.replace('-', '').strip()) == 11):
                    valid = False
                    self.errors[field_name] = "Phone must be 11 digits"
        
        return valid, self.errors


class InputField:
    """Factory for creating input fields with consistent styling."""
    
    @staticmethod
    def create_field(field_type, placeholder="", options=None, validator=None):
        """
        Create an input field with specified type and styling.
        
        Args:
            field_type: The type of field ("text", "cnic", "phone", "date", "combo", "spinbox")
            placeholder: Text placeholder or label
            options: List of options for combo boxes
            validator: Custom validator for text fields
            
        Returns:
            QWidget: The created input widget
        """
        widget = None
        
        if field_type == "text":
            widget = QLineEdit()
            widget.setPlaceholderText(f"Enter your {placeholder.lower()}")
            if validator:
                widget.setValidator(validator)
        
        elif field_type == "cnic":
            widget = QLineEdit()
            widget.setPlaceholderText("0000 0000 0000 0")
            cnic_validator = QRegExpValidator(QRegExp(r'^[0-9]{13}$'))
            widget.setValidator(cnic_validator)
            widget.setMaxLength(13)
        
        elif field_type == "phone":
            widget = QLineEdit()
            widget.setPlaceholderText("0000 0000 000")
            phone_validator = QRegExpValidator(QRegExp(r'^[0-9]{11}$'))
            widget.setValidator(phone_validator)
            widget.setMaxLength(11)
        
        elif field_type == "date":
            widget = CustomDateEdit()
            # All settings are handled in the CustomDateEdit class constructor
        
        elif field_type == "combo":
            widget = CustomComboBox()
            if options:
                widget.addItems(options)
        
        elif field_type == "spinbox":
            widget = QSpinBox()
            widget.setRange(1, 50)
            
            
            # Hide spinbox navigation buttons (up/down arrows)
            widget.setButtonSymbols(QSpinBox.NoButtons)
            
        # Apply common properties
        if widget:
            if isinstance(widget, QLineEdit) or isinstance(widget, QSpinBox):
                # Add FormField class
                widget.setProperty("class", "FormField")
                
                # Set size constraints
                widget.setMinimumHeight(32)
                widget.setFixedHeight(32)
                
                # Apply base styles
                widget.setStyleSheet(BASE_FIELD_STYLE)
                
                # Override any global styles with inline styles for maximum specificity
                widget.setStyleSheet(widget.styleSheet() + """
                    QLineEdit, QSpinBox {
                        border: 1px solid #cccccc !important;
                        border-radius: 12px !important;
                        padding: 15px 20px !important;
                        background-color: #ffffff !important;
                        color: #333333 !important;
                        font-size: 14px !important;
                        min-height: 32px !important;
                        height: 32px !important;
                    }
                """)
            
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
        return widget


class FormLabel(QLabel):
    """Custom form label with consistent styling."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("FormLabel")
        # Using !important flags for all properties to override any conflicting styles
        self.setStyleSheet(f"""
            QLabel#FormLabel {{
                color: #666666 !important;
                font-size: 13px !important;
                font-weight: 500 !important;
                margin-bottom: 1px !important;
                border: none !important;
                background-color: transparent !important;
                background: transparent !important;
                padding: 0px !important;
                min-height: 32px !important;
                height: 32px !important;
            }}
        """)
        
        # Set explicit transparent background - belt and suspenders approach
        self.setAutoFillBackground(False)
        
    def enforceStyle(self):
        """Enforce transparent background styling."""
        # Re-apply style sheet with !important flags
        self.setStyleSheet(f"""
            QLabel#FormLabel {{
                color: #666666 !important;
                font-size: 13px !important;
                font-weight: 500 !important;
                margin-bottom: 1px !important;
                border: none !important;
                background-color: transparent !important;
                background: transparent !important;
                padding: 0px !important;
                min-height: 32px !important;
                height: 32px !important;
            }}
        """)
        
        # Double ensure transparency
        self.setAutoFillBackground(False)
        
        # Override the palette to ensure transparency
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.transparent)
        self.setPalette(palette)
        
        # Use a QTimer to reapply style later in case it gets overridden
        QTimer.singleShot(100, self._enforce_style)
        QTimer.singleShot(300, self._enforce_style)
        QTimer.singleShot(500, self._enforce_style)
    
    def _enforce_style(self):
        """Enforce transparent background style."""
        # Re-apply all transparent styling to overcome any parent influences
        self.setAutoFillBackground(False)
        
        # Ensure palette is transparent
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.transparent)
        self.setPalette(palette)
        
        # Apply super-specific stylesheet
        self.setStyleSheet("""
            QLabel#FormLabel {
                color: #666666 !important;
                font-size: 13px !important;
                font-weight: 500 !important;
                margin-bottom: 1px !important;
                border: none !important;
                background-color: transparent !important;
                background: transparent !important;
                padding: 0px !important;
                min-height: 32px !important;
                height: 32px !important;
            }
        """)
        
        # Set fixed height to ensure consistent sizing
        self.setFixedHeight(32)



def create_form_field_with_label(field_name, label_text, field_type, options=None, validator=None):
    """
    Create a form field with its associated label.
    
    Args:
        field_name (str): Field name/identifier
        label_text (str): Label text to display
        field_type (str): Type of field ("text", "cnic", "phone", "date", "combo", "spinbox")
        options (list, optional): Options for combo boxes
        validator (QValidator, optional): Custom validator
        
    Returns:
        tuple: (label, widget, field_name)
    """
    label = FormLabel(label_text)
    widget = InputField.create_field(field_type, label_text, options, validator)
    
    # Make label responsive
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    # Apply responsive sizing for all widgets
    if widget:
        widget.setMinimumHeight(32)
        # Only set minimum width, let it expand horizontally
        widget.setMinimumWidth(150)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Apply FormField class for standard widgets
        if isinstance(widget, QLineEdit) or isinstance(widget, QSpinBox):
            widget.setProperty("class", "FormField")
            widget.setStyleSheet(BASE_FIELD_STYLE)
    
    return label, widget, field_name


def apply_form_styles(widget):
    """Apply the base form styles to the provided widget with maximum specificity."""
    if isinstance(widget, QLineEdit) or isinstance(widget, QSpinBox):
        # Add CSS class
        widget.setProperty("class", "FormField")
        
        # Force the stylesheet with max specificity
        specific_style = BASE_FIELD_STYLE
        
        # Add direct ID-based styling if the widget has an objectName
        if widget.objectName():
            object_name = widget.objectName()
            specific_style += f"""
                #{object_name} {{
                    background-color: {LIGHTER_COLOR} !important;
                    border: 1px solid {BORDER_COLOR} !important;
                    border-radius: {BORDER_RADIUS} !important;
                    padding: {INPUT_PADDING} !important;
                    font-size: 14px !important;
                    color: {TEXT_COLOR} !important;
                    min-height: 32px !important;
                    margin-top: 3px !important;
                    margin: 0 !important;
                    /* Removed fixed height to allow flexibility */
                }}
                
                #{object_name}:focus {{
                    border: 2px solid {PRIMARY_COLOR} !important;
                }}
            """
        
        # Apply the stylesheet
        widget.setStyleSheet(specific_style)
        
        # Make widget responsive
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        widget.setMinimumWidth(150)  # Set minimum width but allow expansion
        widget.setMinimumHeight(32)
        widget.setFixedHeight(32)


def highlight_field_error(widget, has_error=True):
    """
    Highlight or remove error styling from a field.
    
    Args:
        widget (QWidget): Form field widget
        has_error (bool): True to show error, False to clear error
    """
    if has_error:
        widget.setStyleSheet(widget.styleSheet() + """
            border: 2px solid #dc3545 !important;
        """)
    else:
        # Reset to default styling
        widget.setStyleSheet("")
        apply_form_styles(widget)


def collect_form_data(widgets_dict, model):
    """
    Collect data from form widgets into a model.
    
    Args:
        widgets_dict (dict): Dictionary of field_name: widget pairs
        model (FormModel): Model to store the collected data
    """
    for field_name, widget in widgets_dict.items():
        if widget.isVisible():
            if isinstance(widget, QLineEdit):
                model.set_field(field_name, widget.text())
            elif isinstance(widget, QDateEdit):
                model.set_field(field_name, widget.date().toString('dd/MM/yyyy'))
            elif isinstance(widget, QSpinBox):
                model.set_field(field_name, widget.value())
            elif isinstance(widget, QComboBox):
                model.set_field(field_name, widget.currentText())


def validate_and_highlight(widgets_dict, model):
    """
    Validate form data and highlight errors.
    
    Args:
        widgets_dict (dict): Dictionary of field_name: widget pairs
        model (FormModel): Model containing the data and validation logic
        
    Returns:
        bool: True if form is valid, False otherwise
    """
    # First collect the current data
    collect_form_data(widgets_dict, model)
    
    # Validate the data
    valid, errors = model.validate()
    
    # Clear previous error styling
    for field_name, widget in widgets_dict.items():
        highlight_field_error(widget, False)
    
    # Apply error styling to invalid fields
    if not valid:
        for field_name, error_msg in errors.items():
            if field_name in widgets_dict:
                highlight_field_error(widgets_dict[field_name], True)
    
    return valid


def reset_form(widgets_dict):
    """
    Reset all form fields to their default values.
    
    Args:
        widgets_dict (dict): Dictionary of field_name: widget pairs
    """
    for field_name, widget in widgets_dict.items():
        if isinstance(widget, QLineEdit):
            widget.clear()
        elif isinstance(widget, QDateEdit):
            widget.setDate(QDate.currentDate())
        elif isinstance(widget, QSpinBox):
            widget.setValue(widget.minimum())
        elif isinstance(widget, QComboBox):
            widget.setCurrentIndex(0)
        
        # Clear any error styling
        highlight_field_error(widget, False)
