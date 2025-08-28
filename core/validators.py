"""Input validation and data sanitization."""
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from config.settings import VALIDATION_PATTERNS, REQUIRED_STUDENT_FIELDS

logger = logging.getLogger(__name__)

from core.exceptions import ValidationError

class DataValidator:
    """Comprehensive data validation class."""
    
    @staticmethod
    def validate_string(value: Any, field_name: str, min_length: int = 1, 
                       max_length: int = 255, required: bool = True) -> str:
        """Validate string input."""
        if value is None or value == "":
            if required:
                raise ValidationError(field_name, "This field is required")
            return ""
        
        if not isinstance(value, str):
            value = str(value)
        
        # Remove dangerous characters and sanitize
        value = DataValidator._sanitize_string(value)
        
        if len(value) < min_length:
            raise ValidationError(field_name, f"Must be at least {min_length} characters long")
        
        if len(value) > max_length:
            raise ValidationError(field_name, f"Must be no more than {max_length} characters long")
        
        return value.strip()
    
    @staticmethod
    def validate_email(email: str, required: bool = True) -> str:
        """Validate email address."""
        if not email and not required:
            return ""
        
        email = DataValidator.validate_string(email, "Email", required=required)
        
        if email and not re.match(VALIDATION_PATTERNS["email"], email):
            raise ValidationError("Email", "Invalid email format")
        
        return email.lower()
    
    @staticmethod
    def validate_phone(phone: str, required: bool = True) -> str:
        """Validate phone number."""
        if not phone and not required:
            return ""
        
        phone = DataValidator.validate_string(phone, "Phone", required=required)
        
        if phone and not re.match(VALIDATION_PATTERNS["mobile"], phone):
            raise ValidationError("Phone", "Invalid phone number format (use format: +92XXXXXXXXXX or 03XXXXXXXXX)")
        
        return phone
    
    @staticmethod
    def validate_cnic(cnic: str, required: bool = True) -> str:
        """Validate CNIC number."""
        if not cnic and not required:
            return ""
        
        cnic = DataValidator.validate_string(cnic, "CNIC", required=required)
        
        if cnic and not re.match(VALIDATION_PATTERNS["cnic"], cnic):
            raise ValidationError("CNIC", "Invalid CNIC format (use format: XXXXX-XXXXXXX-X)")
        
        return cnic
    
    @staticmethod
    def validate_student_id(student_id: str) -> str:
        """Validate student ID."""
        student_id = DataValidator.validate_string(student_id, "Student ID", min_length=1, max_length=20)
        
        # Ensure alphanumeric only
        if not re.match(r'^[A-Za-z0-9_-]+$', student_id):
            raise ValidationError("Student ID", "Can only contain letters, numbers, hyphens, and underscores")
        
        return student_id.upper()
    
    @staticmethod
    def validate_date(date_str: str, field_name: str, required: bool = True) -> Optional[str]:
        """Validate date string."""
        if not date_str and not required:
            return None
        
        if not date_str and required:
            raise ValidationError(field_name, "Date is required")
        
        try:
            # Try multiple date formats
            date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
            parsed_date = None
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                raise ValidationError(field_name, "Invalid date format (use YYYY-MM-DD)")
            
            # Check if date is reasonable (not too far in past/future)
            current_year = datetime.now().year
            if parsed_date.year < 1900 or parsed_date.year > current_year + 10:
                raise ValidationError(field_name, f"Date year must be between 1900 and {current_year + 10}")
            
            return parsed_date.strftime('%Y-%m-%d')
            
        except ValueError as e:
            raise ValidationError(field_name, f"Invalid date: {str(e)}")
    
    @staticmethod
    def validate_gender(gender: str, required: bool = True) -> str:
        """Validate gender field."""
        if not gender and not required:
            return ""
        
        gender = DataValidator.validate_string(gender, "Gender", required=required)
        
        valid_genders = ['Male', 'Female', 'Other', 'M', 'F']
        if gender and gender not in valid_genders:
            raise ValidationError("Gender", f"Must be one of: {', '.join(valid_genders)}")
        
        # Normalize gender
        if gender in ['M', 'Male']:
            return 'Male'
        elif gender in ['F', 'Female']:
            return 'Female'
        else:
            return gender
    
    @staticmethod
    def validate_class_section(class_name: str, section: str) -> Tuple[str, str]:
        """Validate class and section."""
        class_name = DataValidator.validate_string(class_name, "Class", min_length=1, max_length=50)
        section = DataValidator.validate_string(section, "Section", min_length=1, max_length=10)
        
        # Validate class format (numbers and optional text)
        if not re.match(r'^(Class\s+)?[0-9]+[A-Za-z]*$|^[A-Za-z]+\s*[0-9]*$', class_name):
            raise ValidationError("Class", "Invalid class format")
        
        # Validate section (single letter/number)
        if not re.match(r'^[A-Za-z0-9]$', section):
            raise ValidationError("Section", "Section must be a single letter or number")
        
        return class_name, section.upper()
    
    @staticmethod
    def _sanitize_string(value: str) -> str:
        """Sanitize string input to prevent injection attacks."""
        if not value:
            return ""
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # Remove potential SQL injection patterns
        dangerous_patterns = [
            r'[;\'\"\\]',  # SQL injection characters
            r'<script[^>]*>.*?</script>',  # XSS scripts
            r'javascript:',  # JavaScript URLs
            r'vbscript:',  # VBScript URLs
        ]
        
        for pattern in dangerous_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value.strip()

class StudentDataValidator:
    """Specialized validator for student data."""
    
    @staticmethod
    def validate_student_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete student data."""
        errors = []
        validated_data = {}
        
        try:
            # Validate required fields
            for field in REQUIRED_STUDENT_FIELDS:
                if field not in data or not data[field]:
                    errors.append(ValidationError(field, "This field is required"))
            
            # Validate Student ID
            if 'S#' in data:
                try:
                    validated_data['S#'] = DataValidator.validate_student_id(data['S#'])
                except ValidationError as e:
                    errors.append(e)
            
            # Validate Name
            if 'Name' in data:
                try:
                    validated_data['Name'] = DataValidator.validate_string(
                        data['Name'], 'Name', min_length=2, max_length=100
                    )
                except ValidationError as e:
                    errors.append(e)
            
            # Validate Phone
            if 'Mobile Number' in data:
                try:
                    validated_data['Mobile Number'] = DataValidator.validate_phone(
                        data['Mobile Number'], required=False
                    )
                except ValidationError as e:
                    errors.append(e)
            
            # Validate Father's CNIC
            if "Father's CNIC" in data:
                try:
                    validated_data["Father's CNIC"] = DataValidator.validate_cnic(
                        data["Father's CNIC"], required=False
                    )
                except ValidationError as e:
                    errors.append(e)
            
            # Validate Date of Birth
            if 'Date of Birth' in data:
                try:
                    validated_data['Date of Birth'] = DataValidator.validate_date(
                        data['Date of Birth'], 'Date of Birth', required=False
                    )
                except ValidationError as e:
                    errors.append(e)
            
            # Validate Gender
            if 'Gender' in data:
                try:
                    validated_data['Gender'] = DataValidator.validate_gender(
                        data['Gender'], required=False
                    )
                except ValidationError as e:
                    errors.append(e)
            
            # Validate Class and Section
            if 'Class 2025' in data and 'Section' in data:
                try:
                    class_name, section = DataValidator.validate_class_section(
                        data['Class 2025'], data['Section']
                    )
                    validated_data['Class 2025'] = class_name
                    validated_data['Section'] = section
                except ValidationError as e:
                    errors.append(e)
            
            # Validate other string fields
            string_fields = [
                'School Name', 'Organization', 'BEMIS', 'Type of School', 'UC',
                'B-Form Number', 'Year of Admission', "Father's Contact",
                "Guardian's Address", 'Registration Number', 'Class Teacher',
                'S# as per Register', "Father's Name", 'Class Status',
                'Verification Status', 'Status', 'Remarks'
            ]
            
            for field in string_fields:
                if field in data:
                    try:
                        validated_data[field] = DataValidator.validate_string(
                            data[field], field, required=False, max_length=255
                        )
                    except ValidationError as e:
                        errors.append(e)
            
            if errors:
                raise ValueError(f"Validation failed: {[str(e) for e in errors]}")
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Student data validation error: {e}")
            raise

class SQLSanitizer:
    """SQL injection prevention utilities."""
    
    @staticmethod
    def sanitize_query_param(param: Any) -> str:
        """Sanitize query parameter to prevent SQL injection."""
        if param is None:
            return ""
        
        param_str = str(param)
        
        # Remove dangerous SQL characters and keywords
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            param_str = param_str.replace(char, '')
        
        # Remove SQL keywords that could be dangerous
        sql_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER',
            'EXEC', 'EXECUTE', 'UNION', 'SELECT', 'FROM', 'WHERE'
        ]
        
        for keyword in sql_keywords:
            pattern = rf'\b{keyword}\b'
            param_str = re.sub(pattern, '', param_str, flags=re.IGNORECASE)
        
        return param_str.strip()
    
    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """Validate table name to prevent SQL injection."""
        # Only allow alphanumeric characters and underscores
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name))
    
    @staticmethod
    def validate_column_name(column_name: str) -> bool:
        """Validate column name to prevent SQL injection."""
        # Only allow alphanumeric characters and underscores
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column_name))

def validate_and_sanitize_input(data: Dict[str, Any], validator_type: str = 'student') -> Dict[str, Any]:
    """Main validation and sanitization function."""
    try:
        if validator_type == 'student':
            return StudentDataValidator.validate_student_data(data)
        else:
            # Generic validation
            validated_data = {}
            for key, value in data.items():
                validated_data[key] = DataValidator.validate_string(
                    value, key, required=False, max_length=255
                )
            return validated_data
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise
