"""
Mother Registration Service - Handles data operations for mother registration.
Extracted from mother_reg.py for better separation of concerns.
"""
from models.database import Database
from config.settings import STUDENT_FIELDS

class MotherRegistrationService:
    """Service class for mother registration data operations."""
    
    def __init__(self):
        """Initialize the service with database connection."""
        self.db = Database()
        
    def get_students_needing_mother_info(self, filters=None):
        """
        Get students who need mother/guardian information.
        
        Args:
            filters (dict): Filter criteria containing school, class, section, status
            
        Returns:
            list: List of student records needing mother information
        """
        try:
            # Build SQL query with filters
            where_clauses = []
            params = []
            
            # Core condition: students missing BOTH mother AND alternate guardian info
            where_clauses.append("""
                (
                    (COALESCE(mother_name,'') = '' OR COALESCE(mother_cnic,'') = '') 
                    AND 
                    (COALESCE(alternate_name,'') = '' OR COALESCE(alternate_cnic,'') = '' OR COALESCE(alternate_relationship_with_mother,'') = '')
                )
            """)
            
            # Always exclude deleted records and only show active students
            where_clauses.append("is_deleted = 0")
            where_clauses.append("status = 'Active'")
            
            # Apply filters if provided
            if filters:
                # School filter (skip for now - needs JOIN with schools table)
                # Class filter
                if filters.get("class") and filters["class"] not in ["Please Select Class", "All Classes"]:
                    where_clauses.append("class = ?")
                    params.append(filters["class"])
                
                # Section filter
                if filters.get("section") and filters["section"] not in ["Please Select Section", "All Sections"]:
                    where_clauses.append("section = ?")
                    params.append(filters["section"])
                
                # Status filter
                if filters.get("status") and filters["status"] != "All Status":
                    where_clauses.append("status = ?")
                    params.append(filters["status"])
            
            # Build complete query
            where_clause = " AND ".join(where_clauses)
            query = f"SELECT * FROM students WHERE {where_clause} ORDER BY name ASC"
            
            # Execute query
            result = self.db.execute_query(query, params)
            return result if result else []
            
        except Exception as e:
            print(f"Error loading students needing mother info: {e}")
            return []
    
    def save_mother_info(self, student_id, mother_data):
        """
        Save mother/guardian information for a student.
        
        Args:
            student_id (str): Student ID
            mother_data (dict): Mother/guardian information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            recipient_type = mother_data.get("recipient_type", "Principal")
            
            # Prepare update data based on recipient type
            update_fields = {}
            
            if recipient_type == "Principal":
                # Map principal fields
                field_mapping = {
                    "household_size": "household_size",
                    "mother_name": "mother_name", 
                    "mother_marital_status": "mother_marital_status",
                    "mother_cnic": "mother_cnic",
                    "mother_cnic_doi": "mother_cnic_doi",
                    "mother_cnic_exp": "mother_cnic_exp",
                    "mother_mwa": "mother_mwa"
                }
            else:  # Alternate Guardian
                # Map guardian fields
                field_mapping = {
                    "household_name": "alternate_name",
                    "guardian_cnic": "alternate_cnic",
                    "guardian_cnic_doi": "alternate_cnic_doi", 
                    "guardian_cnic_exp": "alternate_cnic_exp",
                    "guardian_marital_status": "alternate_marital_status",
                    "guardian_mwa": "alternate_mwa",
                    "guardian_phone": "alternate_phone",
                    "guardian_relation": "alternate_relationship_with_mother"
                }
            
            # Build update fields
            for form_field, db_field in field_mapping.items():
                if form_field in mother_data and mother_data[form_field]:
                    update_fields[db_field] = mother_data[form_field]
            
            # Update database
            if update_fields:
                success = self.db.update_student(student_id, update_fields)
                return success
            else:
                print("No valid data to update")
                return False
                
        except Exception as e:
            print(f"Error saving mother information: {e}")
            return False
    
    def get_filter_options(self):
        """
        Get options for filter dropdowns.
        
        Returns:
            dict: Dictionary containing filter options
        """
        try:
            options = {
                'schools': [],
                'classes': [],
                'sections': [],
                'status_options': ['All Status', 'Active', 'Inactive']
            }
            
            # Get schools
            schools = self.db.get_schools()
            options['schools'] = [{'name': 'All Schools', 'id': None}]
            for school in schools:
                options['schools'].append({
                    'name': school.get('name', 'Unknown School'),
                    'id': school.get('id', '')
                })
            
            # Get classes
            classes = self.db.get_classes()
            options['classes'] = ['All Classes'] + list(classes)
            
            # Get sections  
            sections = self.db.get_sections()
            options['sections'] = ['All Sections'] + list(sections)
            
            return options
            
        except Exception as e:
            print(f"Error loading filter options: {e}")
            return {
                'schools': [{'name': 'All Schools', 'id': None}],
                'classes': ['All Classes'],
                'sections': ['All Sections'],
                'status_options': ['All Status', 'Active', 'Inactive']
            }
    
    def get_student_details(self, student_id):
        """
        Get detailed information for a specific student.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            dict: Student details or None if not found
        """
        try:
            query = "SELECT * FROM students WHERE id = ? AND is_deleted = 0"
            result = self.db.execute_query(query, [student_id])
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting student details: {e}")
            return None
    
    def bulk_update_mother_info(self, student_ids, mother_data):
        """
        Apply mother information to multiple students.
        
        Args:
            student_ids (list): List of student IDs
            mother_data (dict): Mother/guardian information to apply
            
        Returns:
            dict: Results containing success count and errors
        """
        results = {
            'success_count': 0,
            'error_count': 0,
            'errors': []
        }
        
        for student_id in student_ids:
            try:
                if self.save_mother_info(student_id, mother_data):
                    results['success_count'] += 1
                else:
                    results['error_count'] += 1
                    results['errors'].append(f"Failed to update student {student_id}")
            except Exception as e:
                results['error_count'] += 1
                results['errors'].append(f"Error updating student {student_id}: {str(e)}")
        
        return results
    
    def validate_cnic(self, cnic):
        """
        Validate CNIC format.
        
        Args:
            cnic (str): CNIC to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not cnic:
            return False
        
        # Remove any dashes or spaces
        clean_cnic = cnic.replace('-', '').replace(' ', '')
        
        # Check if it's exactly 13 digits
        return clean_cnic.isdigit() and len(clean_cnic) == 13
    
    def validate_phone(self, phone):
        """
        Validate phone number format.
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not phone:
            return False
        
        # Remove any spaces, dashes, or plus signs
        clean_phone = phone.replace(' ', '').replace('-', '').replace('+', '')
        
        # Check if it's 10 or 11 digits
        return clean_phone.isdigit() and len(clean_phone) in [10, 11]
    
    def get_table_column_mapping(self):
        """
        Get mapping between database fields and table display columns.
        
        Returns:
            list: List of column configurations
        """
        return [
            {'key': 'checkbox', 'label': '✓', 'width': 30},
            {'key': 'id', 'label': 'S#', 'width': 80},
            {'key': 'name', 'label': 'Name', 'width': 150},
            {'key': 'father_name', 'label': 'Father Name', 'width': 150},
            {'key': 'class', 'label': 'Class', 'width': 80},
            {'key': 'section', 'label': 'Section', 'width': 80},
            {'key': 'school_name', 'label': 'School', 'width': 200},
            {'key': 'status', 'label': 'Status', 'width': 80}
        ]
    
    def format_student_for_table(self, student):
        """
        Format student data for table display.
        
        Args:
            student (dict): Raw student data from database
            
        Returns:
            dict: Formatted student data for table
        """
        def get_value(data, *keys):
            """Helper to get value from multiple possible keys."""
            for key in keys:
                if isinstance(key, tuple):
                    for k in key:
                        if k in data and data[k]:
                            return data[k]
                else:
                    if key in data and data[key]:
                        return data[key]
            return ""
        
        return {
            'id': str(get_value(student, 'id', 'S#')),
            'name': str(get_value(student, 'name', 'Name')),
            'father_name': str(get_value(student, 'father_name', 'Father', ("Father's Name",))),
            'class': str(get_value(student, 'class', 'Class', ('class_2025',))),
            'section': str(get_value(student, 'section', 'Section')),
            'school_name': str(get_value(student, 'school_name', 'School', ('School Name', 'school_name'))),
            'status': str(get_value(student, 'status', 'Status'))
        }