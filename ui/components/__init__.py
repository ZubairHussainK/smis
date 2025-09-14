"""
Common UI components for the SMIS application.
These components are designed to be reusable across different parts of the application.
"""

from ui.components.registration_form import RegistrationFormBase
from ui.components.student_registration_form import StudentRegistrationForm
from ui.components.custom_date_picker import CustomDateEdit, CustomCalendarWidget, MonthSelectionDialog, YearSelectionDialog
from ui.components.custom_combo_box import CustomComboBox
from ui.components.form_components import (
    FormModel, InputField, FormLabel, 
    create_form_field_with_label, apply_form_styles,
    highlight_field_error, collect_form_data, 
    validate_and_highlight, reset_form
)

__all__ = [
    # Registration forms
    'RegistrationFormBase',
    'StudentRegistrationForm',
    'MotherRegistrationForm',
    
    # Date picker components
    'CustomDateEdit',
    'CustomCalendarWidget',
    'MonthSelectionDialog',
    'YearSelectionDialog',
    
    # ComboBox components
    'CustomComboBox',
    
    # Form components
    'FormModel',
    'InputField',
    'FormLabel',
    'create_form_field_with_label',
    'apply_form_styles',
    'highlight_field_error',
    'collect_form_data',
    'validate_and_highlight',
    'reset_form'
]
