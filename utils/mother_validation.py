"""Form validation utilities for mother registration."""
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime, date
from PyQt5.QtCore import QDate


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.is_valid = False
        self.errors.append(error)


class MotherFormValidator:
    """Comprehensive form validation for mother registration."""
    
    # Validation patterns
    CNIC_PATTERN = r'^\d{5}-\d{7}-\d{1}$'
    PHONE_PATTERN = r'^0\d{10}$'
    MWA_PATTERN = r'^\d{11}$'
    
    @classmethod
    def validate_cnic(cls, cnic: str) -> ValidationResult:
        """Validate CNIC format."""
        result = ValidationResult()
        
        if not cnic or not cnic.strip():
            result.add_error("CNIC is required")
            return result
        
        # Remove spaces and dashes for validation
        clean_cnic = cnic.replace('-', '').replace(' ', '')
        
        if len(clean_cnic) != 13:
            result.add_error("CNIC must be 13 digits")
        elif not clean_cnic.isdigit():
            result.add_error("CNIC must contain only digits")
        
        return result
    
    @classmethod
    def validate_phone(cls, phone: str) -> ValidationResult:
        """Validate phone number format."""
        result = ValidationResult()
        
        if not phone or not phone.strip():
            result.add_error("Phone number is required")
            return result
        
        clean_phone = phone.replace('-', '').replace(' ', '').replace('+92', '0')
        
        if len(clean_phone) != 11:
            result.add_error("Phone number must be 11 digits")
        elif not clean_phone.isdigit():
            result.add_error("Phone number must contain only digits")
        elif not clean_phone.startswith('0'):
            result.add_error("Phone number must start with 0")
        
        return result
    
    @classmethod
    def validate_mwa(cls, mwa: str) -> ValidationResult:
        """Validate MWA number format."""
        result = ValidationResult()
        
        if not mwa or not mwa.strip():
            result.add_error("MWA number is required")
            return result
        
        clean_mwa = mwa.replace('-', '').replace(' ', '')
        
        if len(clean_mwa) != 11:
            result.add_error("MWA number must be 11 digits")
        elif not clean_mwa.isdigit():
            result.add_error("MWA number must contain only digits")
        
        return result
    
    @classmethod
    def validate_date(cls, date_value: Any) -> ValidationResult:
        """Validate date values."""
        result = ValidationResult()
        
        if date_value is None:
            result.add_error("Date is required")
            return result
        
        try:
            if isinstance(date_value, QDate):
                if not date_value.isValid():
                    result.add_error("Invalid date")
            elif isinstance(date_value, str):
                datetime.strptime(date_value, "%Y-%m-%d")
            elif isinstance(date_value, (date, datetime)):
                pass  # Already valid
            else:
                result.add_error("Invalid date format")
        except Exception:
            result.add_error("Invalid date format")
        
        return result
    
    @classmethod
    def validate_required_text(cls, text: str, field_name: str) -> ValidationResult:
        """Validate required text fields."""
        result = ValidationResult()
        
        if not text or not text.strip():
            result.add_error(f"{field_name} is required")
        elif len(text.strip()) < 2:
            result.add_error(f"{field_name} must be at least 2 characters")
        
        return result
    
    @classmethod
    def validate_household_size(cls, size: Any) -> ValidationResult:
        """Validate household size."""
        result = ValidationResult()
        
        try:
            size_int = int(size)
            if size_int < 1:
                result.add_error("Household size must be at least 1")
            elif size_int > 50:
                result.add_error("Household size cannot exceed 50")
        except (ValueError, TypeError):
            result.add_error("Household size must be a valid number")
        
        return result
    
    @classmethod
    def validate_mother_form(cls, form_data: Dict[str, Any], recipient_type: str) -> ValidationResult:
        """Validate complete mother form data."""
        result = ValidationResult()
        
        # Common validations
        household_result = cls.validate_household_size(form_data.get('household_size', 1))
        if not household_result.is_valid:
            result.errors.extend(household_result.errors)
        
        household_head_result = cls.validate_required_text(
            form_data.get('household_head_name', ''), 'Household Head Name'
        )
        if not household_head_result.is_valid:
            result.errors.extend(household_head_result.errors)
        
        if recipient_type == "Principal":
            # Mother-specific validations
            mother_name_result = cls.validate_required_text(
                form_data.get('mother_name', ''), 'Mother Name'
            )
            if not mother_name_result.is_valid:
                result.errors.extend(mother_name_result.errors)
            
            mother_cnic_result = cls.validate_cnic(form_data.get('mother_cnic', ''))
            if not mother_cnic_result.is_valid:
                result.errors.extend(mother_cnic_result.errors)
            
            if form_data.get('mother_mwa'):
                mwa_result = cls.validate_mwa(form_data.get('mother_mwa', ''))
                if not mwa_result.is_valid:
                    result.errors.extend(mwa_result.errors)
            
            # Date validations
            for date_field in ['mother_cnic_doi', 'mother_cnic_exp']:
                if form_data.get(date_field):
                    date_result = cls.validate_date(form_data.get(date_field))
                    if not date_result.is_valid:
                        result.errors.extend([f"{date_field}: {error}" for error in date_result.errors])
        
        else:  # Guardian
            # Guardian-specific validations
            guardian_name_result = cls.validate_required_text(
                form_data.get('guardian_name', ''), 'Guardian Name'
            )
            if not guardian_name_result.is_valid:
                result.errors.extend(guardian_name_result.errors)
            
            guardian_cnic_result = cls.validate_cnic(form_data.get('guardian_cnic', ''))
            if not guardian_cnic_result.is_valid:
                result.errors.extend(guardian_cnic_result.errors)
            
            guardian_phone_result = cls.validate_phone(form_data.get('guardian_phone', ''))
            if not guardian_phone_result.is_valid:
                result.errors.extend(guardian_phone_result.errors)
            
            if form_data.get('guardian_mwa'):
                mwa_result = cls.validate_mwa(form_data.get('guardian_mwa', ''))
                if not mwa_result.is_valid:
                    result.errors.extend(mwa_result.errors)
            
            # Date validations
            for date_field in ['guardian_cnic_doi', 'guardian_cnic_exp']:
                if form_data.get(date_field):
                    date_result = cls.validate_date(form_data.get(date_field))
                    if not date_result.is_valid:
                        result.errors.extend([f"{date_field}: {error}" for error in date_result.errors])
        
        result.is_valid = len(result.errors) == 0
        return result