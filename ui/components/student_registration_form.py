"""
Student registration form implementation using the reusable registration form component.
"""
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from ui.components.registration_form import RegistrationFormBase
from models.database import Database

class StudentRegistrationForm(RegistrationFormBase):
    """Student registration form with school-specific fields."""
    
    def __init__(self, parent=None):
        """Initialize the student registration form."""
        super().__init__("Student Registration", parent)
        self.db = Database()
        self._init_form_fields()
        
    def _init_form_fields(self):
        """Initialize form fields specific to student registration."""
        # Personal Information
        name_field = self.add_text_field("name", "Full Name", required=True, 
                                         placeholder="Enter student's full name")
        
        # Create a validator for phone numbers
        phone_regex = QRegExp("^[0-9]{10,11}$")
        phone_validator = QRegExpValidator(phone_regex)
        
        self.add_text_field("phone", "Phone Number", validator=phone_validator,
                           placeholder="10 or 11 digit phone number")
        
        # Load schools from database
        schools = self._get_schools_list()
        school_combo = self.add_dropdown("school", "School", options=schools, required=True)
        
        # Load classes from database
        classes = self._get_classes_list()
        class_combo = self.add_dropdown("class", "Class", options=classes, required=True)
        
        # Load sections from database
        sections = self._get_sections_list()
        section_combo = self.add_dropdown("section", "Section", options=sections, required=True)
        
        # Additional fields
        self.add_date_field("dob", "Date of Birth", required=True)
        
        gender_options = ["", "Male", "Female", "Other"]
        self.add_dropdown("gender", "Gender", options=gender_options, required=True)
        
        self.add_text_field("father_name", "Father's Name", 
                           placeholder="Enter father's name")
        
        self.add_text_field("mother_name", "Mother's Name", 
                           placeholder="Enter mother's name")
        
        self.add_text_area("address", "Address", 
                          placeholder="Enter complete address")
        
        # Setup interdependent dropdowns
        school_combo.currentTextChanged.connect(self._on_school_changed)
        class_combo.currentTextChanged.connect(self._on_class_changed)
        
    def _get_schools_list(self):
        """Get list of schools from database."""
        try:
            self.db.cursor.execute("SELECT name FROM schools ORDER BY name")
            schools = [""] + [row[0] for row in self.db.cursor.fetchall()]
            return schools
        except Exception as e:
            print(f"Error fetching schools: {e}")
            return [""]
    
    def _get_classes_list(self, school_id=None):
        """Get list of classes from database, optionally filtered by school."""
        try:
            if school_id:
                self.db.cursor.execute(
                    "SELECT name FROM classes WHERE school_id = ? ORDER BY name", 
                    (school_id,)
                )
            else:
                self.db.cursor.execute("SELECT name FROM classes ORDER BY name")
                
            classes = [""] + [row[0] for row in self.db.cursor.fetchall()]
            return classes
        except Exception as e:
            print(f"Error fetching classes: {e}")
            return [""]
    
    def _get_sections_list(self, class_id=None):
        """Get list of sections from database, optionally filtered by class."""
        try:
            if class_id:
                self.db.cursor.execute(
                    "SELECT name FROM sections WHERE class_id = ? ORDER BY name", 
                    (class_id,)
                )
            else:
                self.db.cursor.execute("SELECT name FROM sections ORDER BY name")
                
            sections = [""] + [row[0] for row in self.db.cursor.fetchall()]
            return sections
        except Exception as e:
            print(f"Error fetching sections: {e}")
            return [""]
    
    def _on_school_changed(self, school_name):
        """Update class dropdown when school selection changes."""
        try:
            # Get school ID
            if not school_name:
                # Clear class dropdown
                self.field_values["class"].clear()
                self.field_values["class"].addItem("")
                return
                
            self.db.cursor.execute(
                "SELECT id FROM schools WHERE name = ?", 
                (school_name,)
            )
            result = self.db.cursor.fetchone()
            
            if not result:
                return
                
            school_id = result[0]
            
            # Update classes dropdown
            classes = self._get_classes_list(school_id)
            
            class_combo = self.field_values["class"]
            class_combo.clear()
            class_combo.addItems(classes)
            
        except Exception as e:
            print(f"Error updating class dropdown: {e}")
    
    def _on_class_changed(self, class_name):
        """Update section dropdown when class selection changes."""
        try:
            # Get class ID
            if not class_name:
                # Clear section dropdown
                self.field_values["section"].clear()
                self.field_values["section"].addItem("")
                return
                
            self.db.cursor.execute(
                "SELECT id FROM classes WHERE name = ?", 
                (class_name,)
            )
            result = self.db.cursor.fetchone()
            
            if not result:
                return
                
            class_id = result[0]
            
            # Update sections dropdown
            sections = self._get_sections_list(class_id)
            
            section_combo = self.field_values["section"]
            section_combo.clear()
            section_combo.addItems(sections)
            
        except Exception as e:
            print(f"Error updating section dropdown: {e}")
            
    def save_student(self):
        """Save student data to database."""
        data = self.get_form_data()
        
        try:
            # Get school_id from school name
            self.db.cursor.execute(
                "SELECT id FROM schools WHERE name = ?", 
                (data["school"],)
            )
            school_result = self.db.cursor.fetchone()
            
            if not school_result:
                return False, "Invalid school selected"
                
            school_id = school_result[0]
            
            # Get class_id from class name
            self.db.cursor.execute(
                "SELECT id FROM classes WHERE name = ?", 
                (data["class"],)
            )
            class_result = self.db.cursor.fetchone()
            
            if not class_result:
                return False, "Invalid class selected"
                
            class_id = class_result[0]
            
            # Get section_id from section name
            self.db.cursor.execute(
                "SELECT id FROM sections WHERE name = ?", 
                (data["section"],)
            )
            section_result = self.db.cursor.fetchone()
            
            if not section_result:
                return False, "Invalid section selected"
                
            section_id = section_result[0]
            
            # Insert student record
            self.db.cursor.execute("""
                INSERT INTO students (
                    name, phone, school_id, class_id, section_id, 
                    date_of_birth, gender, father_name, mother_name, address,
                    created_at, updated_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 
                          CURRENT_TIMESTAMP, 'active')
            """, (
                data["name"], data["phone"], school_id, class_id, section_id,
                data["dob"], data["gender"], data["father_name"], 
                data["mother_name"], data["address"]
            ))
            
            self.db.conn.commit()
            return True, "Student added successfully"
            
        except Exception as e:
            self.db.conn.rollback()
            return False, f"Error saving student: {e}"
