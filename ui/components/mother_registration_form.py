"""
Mother registration form implementation using the reusable registration form component.
"""
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from ui.components.registration_form import RegistrationFormBase
from models.database import Database

class MotherRegistrationForm(RegistrationFormBase):
    """Mother registration form with mother-specific fields."""
    
    def __init__(self, parent=None):
        """Initialize the mother registration form."""
        super().__init__("Mother Registration", parent)
        self.db = Database()
        self._init_form_fields()
        
    def _init_form_fields(self):
        """Initialize form fields specific to mother registration."""
        # Personal Information
        name_field = self.add_text_field("name", "Mother's Full Name", required=True, 
                                         placeholder="Enter mother's full name")
        
        # Create a validator for phone numbers
        phone_regex = QRegExp("^[0-9]{10,11}$")
        phone_validator = QRegExpValidator(phone_regex)
        
        self.add_text_field("phone", "Phone Number", validator=phone_validator,
                           placeholder="10 or 11 digit phone number")
        
        # Additional fields
        self.add_date_field("dob", "Date of Birth")
        
        # Load education levels
        education_options = ["", "None", "Primary", "Secondary", "Higher Secondary", 
                            "Graduate", "Post Graduate", "Doctorate"]
        self.add_dropdown("education", "Education Level", options=education_options)
        
        # Load occupations
        occupation_options = ["", "Housewife", "Teacher", "Doctor", "Nurse", 
                             "Engineer", "Entrepreneur", "Other"]
        self.add_dropdown("occupation", "Occupation", options=occupation_options)
        
        self.add_text_field("id_number", "ID Number", 
                           placeholder="National ID or passport number")
        
        # Load relationship with student options
        relation_options = ["", "Mother", "Stepmother", "Guardian", "Other"]
        self.add_dropdown("relation", "Relation to Student", options=relation_options, required=True)
        
        # Link to student
        student_options = self._get_students_list()
        self.add_dropdown("student", "Student Name", options=student_options, required=True)
        
        self.add_text_area("address", "Address", 
                          placeholder="Enter complete address")
                          
        # Additional mother-specific fields
        self.add_text_field("emergency_contact", "Emergency Contact",
                           placeholder="Alternative contact number")
        
        self.add_checkbox("is_primary_contact", "Primary Contact for Student")
        
    def _get_students_list(self):
        """Get list of students from database."""
        try:
            self.db.cursor.execute("SELECT name FROM students ORDER BY name")
            students = [""] + [row[0] for row in self.db.cursor.fetchall()]
            return students
        except Exception as e:
            print(f"Error fetching students: {e}")
            return [""]
            
    def save_mother(self):
        """Save mother data to database."""
        data = self.get_form_data()
        
        try:
            # Get student_id from student name
            if data["student"]:
                self.db.cursor.execute(
                    "SELECT id FROM students WHERE name = ?", 
                    (data["student"],)
                )
                student_result = self.db.cursor.fetchone()
                
                if not student_result:
                    return False, "Invalid student selected"
                    
                student_id = student_result[0]
            else:
                student_id = None
            
            # Insert mother record
            self.db.cursor.execute("""
                INSERT INTO mothers (
                    name, phone, date_of_birth, education, occupation,
                    id_number, relation, student_id, address,
                    emergency_contact, is_primary_contact,
                    created_at, updated_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                          CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'active')
            """, (
                data["name"], data["phone"], data["dob"], data["education"],
                data["occupation"], data["id_number"], data["relation"],
                student_id, data["address"], data["emergency_contact"],
                data["is_primary_contact"]
            ))
            
            self.db.conn.commit()
            return True, "Mother added successfully"
            
        except Exception as e:
            self.db.conn.rollback()
            return False, f"Error saving mother: {e}"
