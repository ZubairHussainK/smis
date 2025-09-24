"""Mother registration service layer for database operations."""
from typing import List, Dict, Optional, Any
from models.database import Database


class StudentData:
    """Data transfer object for student information."""
    
    def __init__(self, student_id: str = "", name: str = "", father_name: str = "", 
                 class_name: str = "", section: str = "", school: str = ""):
        self.student_id = student_id
        self.name = name
        self.father_name = father_name
        self.class_name = class_name
        self.section = section
        self.school = school
    
    @classmethod
    def from_db_row(cls, row: Any) -> 'StudentData':
        """Create StudentData from database row."""
        if hasattr(row, 'keys'):
            row_dict = {key: row[key] for key in row.keys()}
        else:
            row_dict = dict(row)
            
        return cls(
            student_id=str(row_dict.get('student_id', '')),
            name=str(row_dict.get('student_name', '')),
            father_name=str(row_dict.get('father_name', '')),
            class_name=str(row_dict.get('class', '')),
            section=str(row_dict.get('section', '')),
            school=str(row_dict.get('school', ''))  # Remove school_name reference
        )
    
    def to_table_row(self) -> List[str]:
        """Convert to table row format."""
        return ["", self.student_id, self.name, self.father_name, 
                self.class_name, self.section, self.school]


class MotherFilters:
    """Data transfer object for filter criteria."""
    
    def __init__(self, school: str = "", class_name: str = "", 
                 section: str = "", status: str = ""):
        self.school = school
        self.class_name = class_name
        self.section = section
        self.status = status
    
    def is_active_filter(self, filter_value: str, default_values: List[str]) -> bool:
        """Check if a filter value is active (not default)."""
        return filter_value and filter_value not in default_values
    
    def get_active_filters(self) -> Dict[str, str]:
        """Get dictionary of only active filters."""
        active = {}
        
        if self.is_active_filter(self.school, ["Please Select School", "All Schools"]):
            active["school"] = self.school
            
        if self.is_active_filter(self.class_name, ["Please Select Class", "All Classes"]):
            active["class"] = self.class_name
            
        if self.is_active_filter(self.section, ["Please Select Section", "All Sections"]):
            active["section"] = self.section
            
        if self.is_active_filter(self.status, ["All Status"]):
            active["status"] = self.status
            
        return active


class MotherService:
    """Service layer for mother registration operations."""
    
    def __init__(self):
        self.db = Database()
    
    def get_students_needing_mother_info(self, filters: MotherFilters) -> List[StudentData]:
        """Get students who need mother/guardian information."""
        try:
            where_clauses = [
                "is_deleted = 0",
                "status = 'Active'",
                """(
                    (COALESCE(mother_name,'') = '' OR COALESCE(mother_cnic,'') = '') 
                    AND 
                    (COALESCE(alternate_name,'') = '' OR COALESCE(alternate_cnic,'') = '' 
                     OR COALESCE(alternate_relationship_with_mother,'') = '')
                )"""
            ]
            params = []
            
            active_filters = filters.get_active_filters()
            
            if "class" in active_filters:
                where_clauses.append("class = ?")
                params.append(active_filters["class"])
                
            if "section" in active_filters:
                where_clauses.append("section = ?")
                params.append(active_filters["section"])
                
            if "status" in active_filters:
                where_clauses.append("status = ?")
                params.append(active_filters["status"])
            
            where_sql = f"WHERE {' AND '.join(where_clauses)}"
            sql = f"""
                SELECT student_id, student_name, father_name, class, section
                FROM students 
                {where_sql} 
                ORDER BY student_name
            """
            
            rows = self.db.execute_secure_query(sql, tuple(params))
            return [StudentData.from_db_row(row) for row in rows]
            
        except Exception as e:
            print(f"Error getting students needing mother info: {e}")
            return []
    
    def update_mother_info(self, student_id: str, mother_info: Dict[str, Any]) -> bool:
        """Update mother information for a single student."""
        try:
            # Validate student ID
            if not student_id or not student_id.strip():
                return False
            
            # Build update query based on provided fields
            set_clauses = []
            params = []
            
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
            
            for field_key, db_column in field_mapping.items():
                if field_key in mother_info and mother_info[field_key]:
                    set_clauses.append(f"{db_column} = ?")
                    params.append(mother_info[field_key])
            
            if not set_clauses:
                return False
            
            params.append(student_id)
            sql = f"UPDATE students SET {', '.join(set_clauses)} WHERE student_id = ?"
            
            result = self.db.execute_secure_query(sql, tuple(params))
            return result is not None
            
        except Exception as e:
            print(f"Error updating mother info for student {student_id}: {e}")
            return False
    
    def update_mother_info_bulk(self, student_ids: List[str], mother_info: Dict[str, Any]) -> int:
        """Update mother information for multiple students."""
        updated_count = 0
        for student_id in student_ids:
            if self.update_mother_info(student_id, mother_info):
                updated_count += 1
        return updated_count
    
    def get_schools(self) -> List[Dict[str, Any]]:
        """Get list of schools."""
        try:
            return self.db.get_schools()
        except Exception as e:
            print(f"Error getting schools: {e}")
            return [{'name': 'Default School', 'id': '1'}]
    
    def get_classes(self, school_id: Optional[str] = None) -> List[str]:
        """Get list of classes."""
        try:
            return self.db.get_classes(school_id)
        except Exception as e:
            print(f"Error getting classes: {e}")
            return [f"Class {i}" for i in range(1, 13)]
    
    def get_sections(self, school_id: Optional[str] = None, class_name: Optional[str] = None) -> List[str]:
        """Get list of sections."""
        try:
            return self.db.get_sections(school_id, class_name)
        except Exception as e:
            print(f"Error getting sections: {e}")
            return ["A", "B", "C", "D", "E"]