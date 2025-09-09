"""
Common UI components for the SMIS application.
These components are designed to be reusable across different parts of the application.
"""

from ui.components.registration_form import RegistrationFormBase
from ui.components.student_registration_form import StudentRegistrationForm
from ui.components.mother_registration_form import MotherRegistrationForm

__all__ = [
    'RegistrationFormBase',
    'StudentRegistrationForm',
    'MotherRegistrationForm'
]
