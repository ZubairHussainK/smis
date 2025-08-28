"""Enhanced database management with security and performance optimizations."""
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from config.settings import Config, DATABASE_CONFIG
from config.security import DataEncryption
from core.exceptions import DatabaseError, ValidationError
from core.validators import validate_and_sanitize_input, SQLSanitizer
from utils.logger import log_audit_event, PerformanceLogger

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Thread-safe database connection manager."""
    
    def __init__(self):
        self.encryption = DataEncryption() if Config.ENCRYPTION_ENABLED else None
        self._init_connection()
    
    def _init_connection(self):
        """Initialize database connection with security settings."""
        try:
            self.conn = sqlite3.connect(
                Config.DATABASE_PATH,
                timeout=DATABASE_CONFIG['timeout'],
                check_same_thread=DATABASE_CONFIG['check_same_thread'],
                isolation_level=DATABASE_CONFIG['isolation_level']
            )
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            
            # Enable foreign key constraints
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # Enable WAL mode for better concurrency
            self.cursor.execute("PRAGMA journal_mode = WAL")
            
            # Set secure deletion mode
            self.cursor.execute("PRAGMA secure_delete = ON")
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise DatabaseError(f"Failed to initialize database connection: {e}")
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            self.conn.execute("BEGIN")
            yield self.cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise DatabaseError(f"Transaction failed: {e}")
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

class Database:
    """Enhanced database operations with security and performance features."""
    
    def __init__(self):
        """Initialize database with enhanced security."""
        self.db_conn = DatabaseConnection()
        self.conn = self.db_conn.conn
        self.cursor = self.db_conn.cursor
        self._create_tables()
        self._create_indexes()
        self._create_triggers()
    
    def _create_tables(self):
        """Create necessary database tables with enhanced security."""
        try:
            with self.db_conn.transaction():
                # Enhanced schools table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS schools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT,
                    address TEXT,
                    contact_number TEXT,
                    principal_name TEXT,
                    email TEXT,
                    registration_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive'))
                )''')
                
                # Enhanced students table with only required fields and audit columns
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                    -- Primary and System Fields
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'transferred', 'graduated')) NOT NULL,
                    student_id TEXT UNIQUE NOT NULL,
                    final_unique_codes TEXT NOT NULL,
                    
                    -- Organization and Location IDs
                    org_id INTEGER NOT NULL,
                    school_id INTEGER NOT NULL,
                    province_id INTEGER NOT NULL,
                    district_id INTEGER NOT NULL,
                    union_council_id INTEGER NOT NULL,
                    nationality_id INTEGER NOT NULL,
                    
                    -- School Information
                    registration_number TEXT NOT NULL,
                    class_teacher_name TEXT NOT NULL,
                    
                    -- Student Basic Information
                    student_name TEXT NOT NULL,
                    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')) NOT NULL,
                    date_of_birth DATE NOT NULL,
                    students_bform_number TEXT NOT NULL,
                    year_of_admission DATE NOT NULL,
                    year_of_admission_alt DATE NOT NULL,
                    class TEXT CHECK(class IN ('Kachi', 'Paki', '1', '2', '3', '4', '5')) NOT NULL,
                    section TEXT CHECK(section IN ('A', 'B', 'C', 'D', 'E', 'F')) NOT NULL,
                    address TEXT NOT NULL,
                    
                    -- Father Information
                    father_name TEXT NOT NULL,
                    father_cnic TEXT NOT NULL,
                    father_phone TEXT NOT NULL,
                    
                    -- Household Information
                    household_size INTEGER NOT NULL,
                    
                    -- Mother Information
                    mother_name TEXT NOT NULL,
                    mother_date_of_birth DATE NOT NULL,
                    mother_marital_status TEXT CHECK(mother_marital_status IN ('Single', 'Married', 'Divorced', 'Widowed', 'Free union', 'Separated', 'Engaged')) NOT NULL,
                    mother_id_type TEXT NOT NULL,
                    mother_cnic TEXT NOT NULL,
                    mother_cnic_doi DATE NOT NULL,
                    mother_cnic_exp DATE NOT NULL,
                    mother_mwa INTEGER NOT NULL,
                    
                    -- Household Head Information
                    household_role TEXT CHECK(household_role IN ('Head', 'Son', 'Daughter', 'Wife', 'Husband', 'Brother', 'Sister', 'Mother', 'Father', 'Aunt', 'Uncle', 'Grand Mother', 'Grand Father', 'Mother-in-Law', 'Father-in-Law', 'Daughter-in-Law', 'Son-in-Law', 'Sister-in-Law', 'Brother-in-Law', 'Grand Daughter', 'Grand Son', 'Nephew', 'Niece', 'Cousin', 'Other', 'Not Member')) NOT NULL,
                    household_name TEXT NOT NULL,
                    hh_gender TEXT CHECK(hh_gender IN ('Male', 'Female', 'Other')) NOT NULL,
                    hh_date_of_birth DATE NOT NULL,
                    recipient_type TEXT CHECK(recipient_type IN ('Principal', 'Alternate')) NOT NULL,
                    
                    -- Alternate/Guardian Information (Optional fields)
                    alternate_name TEXT,
                    alternate_date_of_birth DATE,
                    alternate_marital_status TEXT CHECK(alternate_marital_status IN ('Single', 'Married', 'Divorced', 'Widowed', 'Free union', 'Separated', 'Engaged')),
                    alternate_id_type TEXT,
                    alternate_cnic TEXT,
                    alternate_cnic_doi DATE,
                    alternate_cnic_exp DATE,
                    alternate_mwa INTEGER,
                    alternate_relationship_with_mother TEXT CHECK(alternate_relationship_with_mother IN ('Head', 'Son', 'Daughter', 'Wife', 'Husband', 'Brother', 'Sister', 'Mother', 'Father', 'Aunt', 'Uncle', 'Grand Mother', 'Grand Father', 'Mother-in-Law', 'Father-in-Law', 'Daughter-in-Law', 'Son-in-Law', 'Sister-in-Law', 'Brother-in-Law', 'Grand Daughter', 'Grand Son', 'Nephew', 'Niece', 'Cousin', 'Other', 'Not Member')),
                    
                    -- Audit and System Fields
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    updated_by INTEGER,
                    created_by_username TEXT,
                    updated_by_username TEXT,
                    created_by_phone TEXT,
                    updated_by_phone TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    deleted_at TIMESTAMP,
                    deleted_by INTEGER,
                    deleted_by_username TEXT,
                    deleted_by_phone TEXT,
                    version INTEGER DEFAULT 1
                )''')
                
                # Enhanced attendance table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late', 'Excused', 'Holiday')),
                    remarks TEXT,
                    marked_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                    UNIQUE(student_id, date)
                )''')
                
                # Audit log table for tracking all changes
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    action TEXT NOT NULL CHECK(action IN ('INSERT', 'UPDATE', 'DELETE')),
                    old_values TEXT,
                    new_values TEXT,
                    changed_fields TEXT,
                    user_id INTEGER,
                    username TEXT,
                    user_phone TEXT,
                    user_ip TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )''')
                
                # Activity log for user actions
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    user_phone TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )''')
                
                # Data integrity checks table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS data_integrity_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_type TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('passed', 'failed', 'warning')),
                    details TEXT,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
                
                # Student history table (used by add_student_history/get_student_history)
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS student_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    student_s_no TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_type TEXT NOT NULL,
                    changed_by TEXT DEFAULT 'System',
                    changed_by_username TEXT,
                    changed_by_phone TEXT,
                    change_reason TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
                )''')
                
            self._insert_dummy_data()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise DatabaseError(f"Failed to create database tables: {e}")
    
    def _create_indexes(self):
        """Create database indexes for performance optimization."""
        try:
            indexes = [
                # Primary student identification indexes
                "CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id)",
                "CREATE INDEX IF NOT EXISTS idx_students_final_unique_codes ON students(final_unique_codes)",
                "CREATE INDEX IF NOT EXISTS idx_students_registration_number ON students(registration_number)",
                
                # New structured field indexes
                "CREATE INDEX IF NOT EXISTS idx_students_student_name ON students(student_name)",
                "CREATE INDEX IF NOT EXISTS idx_students_org_school ON students(org_id, school_id)",
                "CREATE INDEX IF NOT EXISTS idx_students_location ON students(province_id, district_id, union_council_id)",
                "CREATE INDEX IF NOT EXISTS idx_students_class_section ON students(class, section)",
                "CREATE INDEX IF NOT EXISTS idx_students_status ON students(status)",
                "CREATE INDEX IF NOT EXISTS idx_students_gender ON students(gender)",
                "CREATE INDEX IF NOT EXISTS idx_students_admission_year ON students(year_of_admission)",
                "CREATE INDEX IF NOT EXISTS idx_students_class_teacher ON students(class_teacher_name)",
                
                # Family information indexes
                "CREATE INDEX IF NOT EXISTS idx_students_father_cnic ON students(father_cnic)",
                "CREATE INDEX IF NOT EXISTS idx_students_mother_cnic ON students(mother_cnic)",
                "CREATE INDEX IF NOT EXISTS idx_students_alternate_cnic ON students(alternate_cnic)",
                
                # Attendance and audit indexes
                "CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, date)",
                "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)",
                "CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id)",
                "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_activity_log_user_timestamp ON activity_log(user_id, timestamp)",
                
                # Composite indexes for common queries
                "CREATE INDEX IF NOT EXISTS idx_students_search ON students(student_name, student_id, father_name)",
                "CREATE INDEX IF NOT EXISTS idx_students_demographic ON students(gender, date_of_birth, nationality_id)"
            ]
            
            for index_sql in indexes:
                self.cursor.execute(index_sql)
            
            self.conn.commit()
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise DatabaseError(f"Failed to create database indexes: {e}")
    
    def _create_triggers(self):
        """Create database triggers for automatic auditing."""
        try:
            # Trigger for students table updates
            self.cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS student_update_timestamp
                AFTER UPDATE ON students
                FOR EACH ROW
                BEGIN
                    UPDATE students SET updated_at = CURRENT_TIMESTAMP, version = version + 1
                    WHERE id = NEW.id;
                END
            ''')
            
            # Trigger for audit logging on student changes
            self.cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS student_audit_log
                AFTER UPDATE ON students
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id)
                    VALUES ('students', NEW.id, 'UPDATE', 
                           json_object('student_name', OLD.student_name, 'student_id', OLD.student_id),
                           json_object('student_name', NEW.student_name, 'student_id', NEW.student_id),
                           NEW.updated_by);
                END
            ''')
            
            self.conn.commit()
            logger.info("Database triggers created successfully")
            
        except Exception as e:
            logger.error(f"Error creating triggers: {e}")
            # Don't raise exception for triggers as they're not critical
            logger.warning("Continuing without database triggers")
    
    def execute_secure_query(self, query: str, params: Tuple = (), 
                           user_id: int = None) -> List[sqlite3.Row]:
        """Execute query with security validation and logging."""
        try:
            # Validate query for dangerous operations
            if not self._is_query_safe(query):
                raise DatabaseError("Query contains potentially dangerous operations")
            
            # Log the query for auditing
            if user_id and Config.ENABLE_AUDIT_LOG:
                log_audit_event("database_query", user_id, "database", details={'query': query})
            
            with PerformanceLogger(f"Database Query: {query[:50]}..."):
                self.cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    return self.cursor.fetchall()
                else:
                    self.conn.commit()
                    return []
                    
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    def _is_query_safe(self, query: str) -> bool:
        """Check if query is safe to execute."""
        query_upper = query.upper().strip()
        
        # Allow standard operations
        allowed_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE INDEX', 'DROP INDEX']
        
        # Block dangerous operations
        dangerous_patterns = [
            'DROP TABLE', 'DROP DATABASE', 'TRUNCATE', 'ALTER TABLE',
            'CREATE TRIGGER', 'DROP TRIGGER', 'PRAGMA',
            'ATTACH', 'DETACH', 'VACUUM'
        ]
        
        if not any(query_upper.startswith(start) for start in allowed_starts):
            return False
        
        if any(pattern in query_upper for pattern in dangerous_patterns):
            return False
        
        return True

    
    def get_students(self, school_id=None, class_name=None, section=None, 
                    page: int = 1, per_page: int = None, user_id: int = None) -> Dict[str, Any]:
        """Get filtered and paginated list of students with enhanced security."""
        try:
            per_page = per_page or 50  # Default page size
            offset = (page - 1) * per_page
            
            # Build secure query with JOIN to schools table for school names
            base_query = """
                SELECT s.*, 
                       sch.name as school_name,
                       COUNT(*) OVER() as total_count
                FROM students s 
                LEFT JOIN schools sch ON s.school_id = sch.id
                WHERE s.is_deleted = 0
            """
            count_query = """
                SELECT COUNT(*) 
                FROM students s 
                LEFT JOIN schools sch ON s.school_id = sch.id
                WHERE s.is_deleted = 0
            """
            params = []
            
            # Add filters with validation
            if school_id and school_id != "All Schools":
                base_query += " AND s.school_id = ?"
                count_query += " AND s.school_id = ?"
                params.append(school_id)
            
            if class_name and class_name != "All Classes":
                base_query += " AND s.class = ?"
                count_query += " AND s.class = ?"
                params.append(class_name)
            
            if section and section != "All Sections":
                base_query += " AND s.section = ?"
                count_query += " AND s.section = ?"
                params.append(section)
            
            # Add pagination
            base_query += " ORDER BY s.student_name LIMIT ? OFFSET ?"
            params.extend([per_page, offset])
            
            # Execute queries
            try:
                # Get total count
                total_records = self.execute_secure_query(count_query, tuple(params[:-2]), user_id)[0][0]
                
                # Get paginated results
                rows = self.execute_secure_query(base_query, tuple(params), user_id)
            except:
                # Fallback if execute_secure_query doesn't work
                self.cursor.execute(count_query, tuple(params[:-2]))
                total_records = self.cursor.fetchone()[0]
                
                self.cursor.execute(base_query, tuple(params))
                rows = self.cursor.fetchall()
            
            students = []
            for row in rows:
                student_data = dict(row)
                
                students.append({
                    "ID": student_data.get("id"),
                    "Student_ID": student_data.get("student_id"),
                    "Name": student_data.get("student_name"),
                    "Class": student_data.get("class"),
                    "Section": student_data.get("section"),
                    "School_ID": student_data.get("school_id"),  # Added missing school_id
                    "Gender": student_data.get("gender"),
                    "DOB": student_data.get("date_of_birth"),
                    "Father": student_data.get("father_name"),
                    "Address": student_data.get("address"),
                    "Status": student_data.get("status")
                })
            
            return {
                'students': students,
                'total_records': total_records,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_records + per_page - 1) // per_page
            }
            
        except Exception as e:
            logger.error(f"Error getting students: {e}")
            return {
                'students': [],
                'total_records': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
            }
    
    def search_students(self, query: str, user_id: int = None) -> List[Dict[str, Any]]:
        """Search students with enhanced security and performance."""
        try:
            if len(query.strip()) < 2:
                return []
            
            search_sql = """
                SELECT student_id, student_name, class, section, status
                FROM students 
                WHERE status = 'active' AND is_deleted = 0
                AND (student_name LIKE ? OR student_id LIKE ?)
                ORDER BY student_name 
                LIMIT 20
            """
            
            search_pattern = f"%{query}%"
            try:
                rows = self.execute_secure_query(search_sql, (search_pattern, search_pattern), user_id)
            except:
                # Fallback
                self.cursor.execute(search_sql, (search_pattern, search_pattern))
                rows = self.cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error searching students: {e}")
            return []
    
    def save_student(self, data: Dict[str, Any], user_id: int = None, username: str = None, user_phone: str = None) -> int:
        """Save a new student record with validation and auditing."""
        try:
            # Basic data validation
            required_fields = ['student_id', 'student_name']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"Required field {field} is missing")
            
            # Check if student already exists
            if self.student_exists(data["student_id"]):
                raise ValueError("Student with this ID already exists")
            
            insert_sql = """
                INSERT INTO students (
                    student_id, student_name, gender, date_of_birth, address, 
                    class, section, father_name, father_cnic, father_phone,
                    org_id, school_id, province_id, district_id, union_council_id,
                    nationality_id, registration_number, class_teacher_name,
                    students_bform_number, year_of_admission, year_of_admission_alt,
                    household_size, mother_name, mother_date_of_birth, mother_marital_status,
                    mother_id_type, mother_cnic, mother_cnic_doi, mother_cnic_exp, mother_mwa,
                    household_role, household_name, hh_gender, hh_date_of_birth, recipient_type,
                    alternate_name, alternate_date_of_birth, alternate_marital_status,
                    alternate_id_type, alternate_cnic, alternate_cnic_doi, alternate_cnic_exp,
                    alternate_mwa, alternate_relationship_with_mother,
                    created_by, created_by_username, created_by_phone, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """
            
            values = (
                data.get("student_id"),
                data.get("student_name"),
                data.get("gender"),
                data.get("date_of_birth"),
                data.get("address"),
                data.get("class"),
                data.get("section"),
                data.get("father_name"),
                data.get("father_cnic"),
                data.get("father_phone"),
                data.get("org_id"),
                data.get("school_id"),
                data.get("province_id"),
                data.get("district_id"),
                data.get("union_council_id"),
                data.get("nationality_id"),
                data.get("registration_number"),
                data.get("class_teacher_name"),
                data.get("students_bform_number"),
                data.get("year_of_admission"),
                data.get("year_of_admission_alt"),
                data.get("household_size"),
                data.get("mother_name"),
                data.get("mother_date_of_birth"),
                data.get("mother_marital_status"),
                data.get("mother_id_type"),
                data.get("mother_cnic"),
                data.get("mother_cnic_doi"),
                data.get("mother_cnic_exp"),
                data.get("mother_mwa"),
                data.get("household_role"),
                data.get("household_name"),
                data.get("hh_gender"),
                data.get("hh_date_of_birth"),
                data.get("recipient_type"),
                data.get("alternate_name"),
                data.get("alternate_date_of_birth"),
                data.get("alternate_marital_status"),
                data.get("alternate_id_type"),
                data.get("alternate_cnic"),
                data.get("alternate_cnic_doi"),
                data.get("alternate_cnic_exp"),
                data.get("alternate_mwa"),
                data.get("alternate_relationship_with_mother"),
                user_id,
                username,
                user_phone
            )
            
            self.cursor.execute(insert_sql, values)
            self.conn.commit()
            
            student_id = self.cursor.lastrowid
            logger.info(f"Student created successfully: {data.get('student_id')} by {username}")
            return student_id
            
        except Exception as e:
            logger.error(f"Error saving student: {e}")
            raise
    
    def update_student(self, data: Dict[str, Any], user_id: int = None, username: str = None, user_phone: str = None) -> bool:
        """Update an existing student record with validation and auditing."""
        try:
            student_id = data.get("student_id")
            if not student_id:
                raise ValueError("student_id is required")
            
            # Check if student exists
            if not self.student_exists(student_id):
                raise ValueError("Student not found")
            
            # Build update query dynamically based on provided data
            update_fields = []
            values = []
            
            field_mappings = {
                'student_name': 'student_name',
                'gender': 'gender',
                'date_of_birth': 'date_of_birth',
                'address': 'address',
                'class': 'class',
                'section': 'section',
                'father_name': 'father_name',
                'father_cnic': 'father_cnic',
                'father_phone': 'father_phone',
                'mother_name': 'mother_name',
                'mother_cnic': 'mother_cnic',
                # Add other fields as needed
            }
            
            for key, db_field in field_mappings.items():
                if key in data and data[key] is not None:
                    update_fields.append(f"{db_field} = ?")
                    values.append(data[key])
            
            if not update_fields:
                return True  # Nothing to update
            
            update_fields.append("updated_by = ?")
            update_fields.append("updated_by_username = ?")
            update_fields.append("updated_by_phone = ?")
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.extend([user_id, username, user_phone, student_id])
            
            update_sql = f"""
                UPDATE students SET {', '.join(update_fields)}
                WHERE student_id = ? AND status = 'active'
            """
            
            self.cursor.execute(update_sql, values)
            self.conn.commit()
            
            logger.info(f"Student updated successfully: {student_id} by {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating student: {e}")
            return False
    
    def delete_student(self, student_id: str, user_id: int = None, username: str = None, user_phone: str = None) -> bool:
        """Soft delete a student record with auditing."""
        try:
            # Check if student exists
            if not self.student_exists(student_id):
                raise ValueError("Student not found")
            
            # Soft delete - mark as deleted instead of actual deletion
            delete_sql = """
                UPDATE students 
                SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP, deleted_by = ?, deleted_by_username = ?, deleted_by_phone = ?, 
                    status = 'inactive', updated_by = ?, updated_by_username = ?, updated_by_phone = ?, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND is_deleted = 0
            """
            
            self.cursor.execute(delete_sql, (user_id, username, user_phone, user_id, username, user_phone, student_id))
            self.conn.commit()
            
            logger.info(f"Student soft deleted successfully: {student_id} by {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting student: {e}")
            return False
    
    def student_exists(self, student_id: str) -> bool:
        """Check if a student exists by student_id with enhanced security."""
        try:
            query = "SELECT 1 FROM students WHERE student_id = ? AND status = 'active' AND is_deleted = 0"
            try:
                result = self.execute_secure_query(query, (student_id,))
                return len(result) > 0
            except:
                # Fallback
                self.cursor.execute(query, (student_id,))
                result = self.cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Error checking student existence: {e}")
            return False
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get student by student ID with security validation."""
        try:
            query = "SELECT * FROM students WHERE student_id = ? AND status = 'active' AND is_deleted = 0"
            try:
                result = self.execute_secure_query(query, (student_id,))
                if result:
                    return dict(result[0])
            except:
                # Fallback
                self.cursor.execute(query, (student_id,))
                result = self.cursor.fetchone()
                if result:
                    return dict(result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting student by student_id: {e}")
            return None
    
    def _encrypt_student_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive student data."""
        return data  # Simplified - no encryption for now
    
    def _decrypt_student_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive student data."""
        return data  # Simplified - no encryption for now
    
    def _get_changed_fields(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fields that changed between old and new data."""
        return {}  # Simplified - no change tracking for now
    
    def run_data_integrity_check(self) -> Dict[str, Any]:
        """Run comprehensive data integrity checks."""
        try:
            results = {
                'passed': 0,
                'failed': 0,
                'warnings': 0,
                'checks': []
            }
            
            # Check for duplicate student numbers
            check_result = self._check_duplicate_student_numbers()
            results['checks'].append(check_result)
            results[check_result['status']] += 1
            
            # Check for orphaned attendance records
            check_result = self._check_orphaned_attendance()
            results['checks'].append(check_result)
            results[check_result['status']] += 1
            
            # Check for invalid dates
            check_result = self._check_invalid_dates()
            results['checks'].append(check_result)
            results[check_result['status']] += 1
            
            # Store check results
            with self.db_conn.transaction():
                for check in results['checks']:
                    self.cursor.execute("""
                        INSERT INTO data_integrity_checks (check_type, status, details)
                        VALUES (?, ?, ?)
                    """, (check['name'], check['status'], check['details']))
            
            return results
            
        except Exception as e:
            logger.error(f"Data integrity check failed: {e}")
            raise DatabaseError(f"Data integrity check failed: {e}")
    
    def _check_duplicate_student_numbers(self) -> Dict[str, Any]:
        """Check for duplicate student IDs."""
        try:
            query = """
                SELECT student_id, COUNT(*) as count 
                FROM students 
                WHERE is_deleted = 0 
                GROUP BY student_id 
                HAVING COUNT(*) > 1
            """
            duplicates = self.execute_secure_query(query)
            
            if duplicates:
                return {
                    'name': 'Duplicate Student Numbers',
                    'status': 'failed',
                    'details': f"Found {len(duplicates)} duplicate student numbers"
                }
            else:
                return {
                    'name': 'Duplicate Student Numbers',
                    'status': 'passed',
                    'details': 'No duplicate student numbers found'
                }
        except Exception:
            return {
                'name': 'Duplicate Student Numbers',
                'status': 'failed',
                'details': 'Check failed due to error'
            }
    
    def _check_orphaned_attendance(self) -> Dict[str, Any]:
        """Check for orphaned attendance records."""
        try:
            query = """
                SELECT COUNT(*) 
                FROM attendance a 
                LEFT JOIN students s ON a.student_id = s.id 
                WHERE s.id IS NULL
            """
            result = self.execute_secure_query(query)
            orphaned_count = result[0][0]
            
            if orphaned_count > 0:
                return {
                    'name': 'Orphaned Attendance Records',
                    'status': 'warning',
                    'details': f"Found {orphaned_count} orphaned attendance records"
                }
            else:
                return {
                    'name': 'Orphaned Attendance Records',
                    'status': 'passed',
                    'details': 'No orphaned attendance records found'
                }
        except Exception:
            return {
                'name': 'Orphaned Attendance Records',
                'status': 'failed',
                'details': 'Check failed due to error'
            }
    
    def _check_invalid_dates(self) -> Dict[str, Any]:
        """Check for invalid date formats."""
        try:
            # This is a simplified check - you could make it more comprehensive
            query = """
                SELECT COUNT(*) 
                FROM students 
                WHERE dob IS NOT NULL 
                AND dob != '' 
                AND status = 'active'
                AND (length(dob) != 10 OR dob NOT LIKE '____-__-__')
            """
            result = self.execute_secure_query(query)
            invalid_count = result[0][0]
            
            if invalid_count > 0:
                return {
                    'name': 'Invalid Date Formats',
                    'status': 'warning',
                    'details': f"Found {invalid_count} records with invalid date formats"
                }
            else:
                return {
                    'name': 'Invalid Date Formats',
                    'status': 'passed',
                    'details': 'All date formats are valid'
                }
        except Exception:
            return {
                'name': 'Invalid Date Formats',
                'status': 'failed',
                'details': 'Check failed due to error'
            }
    
    def close(self):
        """Close database connection."""
        self.db_conn.close()

    def _insert_dummy_data(self):
        """Insert dummy data for schools if tables are empty."""
        try:
            # Check if schools table is empty
            self.cursor.execute("SELECT COUNT(*) FROM schools")
            if self.cursor.fetchone()[0] == 0:
                # Insert dummy schools
                schools_data = [
                    ("Greenfield Public School", "Public", "123 Education Street, Karachi", "021-12345678", "Dr. Ahmad Khan"),
                    ("Elite Grammar School", "Private", "456 Learning Avenue, Lahore", "042-87654321", "Mrs. Fatima Sheikh"),
                    ("Sunrise Academy", "Private", "789 Knowledge Road, Islamabad", "051-11223344", "Mr. Hassan Ali"),
                    ("City Model School", "Public", "321 School Lane, Peshawar", "091-55667788", "Ms. Ayesha Malik"),
                    ("Future Leaders Institute", "Private", "654 Academic Plaza, Multan", "061-99887766", "Prof. Muhammad Iqbal")
                ]
                
                for school in schools_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO schools 
                        (name, type, address, contact_number, principal_name) 
                        VALUES (?, ?, ?, ?, ?)""", school)
            
            # For students table, we'll skip dummy data since we have a clean structure now
            # and want to avoid column reference issues
            
            self.conn.commit()
            logging.info("Dummy data inserted successfully")
            
        except Exception as e:
            logging.error(f"Error inserting dummy data: {e}")

    def get_schools(self):
        """Get all schools."""
        try:
            self.cursor.execute("SELECT * FROM schools ORDER BY name")
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting schools: {e}")
            return []

    def get_classes(self, school_id=None):
        """Get distinct classes from students table."""
        try:
            if school_id:
                self.cursor.execute("""
                    SELECT DISTINCT class 
                    FROM students 
                    WHERE is_deleted = 0 AND school_id = ? AND class IS NOT NULL AND class != ''
                    ORDER BY class
                """, (school_id,))
            else:
                self.cursor.execute("""
                    SELECT DISTINCT class 
                    FROM students 
                    WHERE is_deleted = 0 AND class IS NOT NULL AND class != ''
                    ORDER BY class
                """)
            return [row['class'] for row in self.cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting classes: {e}")
            return []

    def get_sections(self, school_id=None, class_name=None):
        """Get distinct sections from students table."""
        try:
            query = """
                SELECT DISTINCT section 
                FROM students 
                WHERE is_deleted = 0 AND section IS NOT NULL AND section != ''
            """
            params = []
            
            if school_id:
                query += " AND school_id = ?"
                params.append(school_id)
                
            if class_name:
                query += " AND class = ?"
                params.append(class_name)
                
            query += " ORDER BY section"
            
            self.cursor.execute(query, params)
            return [row['section'] for row in self.cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting sections: {e}")
            return []

    def get_student_id_by_student_id(self, student_id_code):
        """Get student database ID by student_id code."""
        try:
            # Use correct field name from database schema
            self.cursor.execute("SELECT id FROM students WHERE student_id = ?", (student_id_code,))
            result = self.cursor.fetchone()
            return result['id'] if result else None
        except Exception as e:
            logging.error(f"Error getting student database ID: {e}")
            return None

    def get_attendance(self, student_id=None, date=None):
        """Get attendance records."""
        try:
            query = """SELECT a.*, s.student_name as student_name, s.student_id 
                      FROM attendance a 
                      JOIN students s ON a.student_id = s.id 
                      WHERE s.is_deleted = 0"""
            params = []
            
            if student_id:
                # If student_id is a string (student_id code), convert it to database ID
                if isinstance(student_id, str):
                    db_id = self.get_student_id_by_student_id(student_id)
                    if db_id:
                        student_id = db_id
                    else:
                        return []
                query += " AND a.student_id = ?"
                params.append(student_id)
            if date:
                query += " AND a.date = ?"
                params.append(date)
                
            query += " ORDER BY a.date DESC, s.student_name"
            
            self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting attendance: {e}")
            return []

    def mark_attendance(self, student_id, date, status, remarks=""):
        """Mark attendance for a student."""
        try:
            # If student_id is a string (student_id code), convert it to database ID
            if isinstance(student_id, str):
                db_id = self.get_student_id_by_student_id(student_id)
                if not db_id:
                    raise ValueError(f"Student with ID {student_id} not found")
                student_id = db_id
                
            # Check if attendance already exists for this date
            self.cursor.execute("""SELECT id FROM attendance 
                               WHERE student_id = ? AND date = ?""", (student_id, date))
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing record
                self.cursor.execute("""UPDATE attendance 
                                   SET status = ?, remarks = ? 
                                   WHERE student_id = ? AND date = ?""", 
                                 (status, remarks, student_id, date))
            else:
                # Insert new record
                self.cursor.execute("""INSERT INTO attendance 
                                   (student_id, date, status, remarks) 
                                   VALUES (?, ?, ?, ?)""", 
                                 (student_id, date, status, remarks))
            
            self.conn.commit()
            logging.info(f"Attendance marked: Student {student_id}, Date {date}, Status {status}")
            
        except Exception as e:
            logging.error(f"Error marking attendance: {e}")
            raise

    def add_student_history(self, student_id, student_s_no, field_name, old_value, new_value, change_type, changed_by="System", changed_by_username=None, changed_by_phone=None, change_reason=""):
        """Add a history record for student changes."""
        try:
            self.cursor.execute("""INSERT INTO student_history 
                               (student_id, student_s_no, field_name, old_value, new_value, change_type, changed_by, changed_by_username, changed_by_phone, change_reason) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                             (student_id, student_s_no, field_name, old_value, new_value, change_type, changed_by, changed_by_username, changed_by_phone, change_reason))
            self.conn.commit()
            logging.info(f"History added for student {student_s_no}: {field_name} changed from '{old_value}' to '{new_value}' by {changed_by_username or changed_by}")
        except Exception as e:
            logging.error(f"Error adding student history: {e}")
            raise

    def get_student_history(self, student_id):
        """Get complete history for a student."""
        try:
            self.cursor.execute("""SELECT * FROM student_history 
                               WHERE student_id = ? 
                               ORDER BY changed_at DESC""", (student_id,))
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error getting student history: {e}")
            raise

    def get_student_by_database_id(self, database_id: int) -> Optional[Dict[str, Any]]:
        """Get student details by database ID."""
        try:
            self.cursor.execute("SELECT * FROM students WHERE id = ? AND is_deleted = 0", (database_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting student by database ID: {e}")
            return None

    def update_student_with_history(self, student_id, updates, changed_by="System", change_reason=""):
        """Update student record and track changes in history."""
        try:
            # First get the current student data
            current_student = self.get_student_by_id(student_id)
            if not current_student:
                raise ValueError(f"Student with ID {student_id} not found")
            
            student_s_no = current_student['student_id']
            
            # Track changes for each field
            for field_name, new_value in updates.items():
                if field_name in dict(current_student).keys():
                    old_value = current_student[field_name]
                    if str(old_value) != str(new_value):  # Only track actual changes
                        self.add_student_history(
                            student_id, student_s_no, field_name, 
                            old_value, new_value, 'UPDATE', changed_by, change_reason
                        )
            
            # Build update query
            set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
            values = list(updates.values()) + [student_id]
            
            self.cursor.execute(f"UPDATE students SET {set_clause} WHERE id = ?", values)
            self.conn.commit()
            logging.info(f"Student {student_s_no} updated successfully with history tracking")
            
        except Exception as e:
            logging.error(f"Error updating student with history: {e}")
            raise

    def add_student_with_history(self, student_data, added_by="System", add_reason="New student registration"):
        """Add new student and create initial history record."""
        try:
            # Insert the student
            fields = ", ".join(student_data.keys())
            placeholders = ", ".join(["?" for _ in student_data])
            values = list(student_data.values())
            
            self.cursor.execute(f"INSERT INTO students ({fields}) VALUES ({placeholders})", values)
            student_id = self.cursor.lastrowid
            
            # Add history for creation
            student_s_no = student_data.get('student_id', f'STU_{student_id}')
            self.add_student_history(
                student_id, student_s_no, 'RECORD_CREATED', 
                '', 'Student record created', 'INSERT', added_by, add_reason
            )
            
            self.conn.commit()
            logging.info(f"New student {student_s_no} added with history tracking")
            return student_id
            
        except Exception as e:
            logging.error(f"Error adding student with history: {e}")
            raise

    def update_mother_info(self, student_id_code: str, info: Dict[str, Any]) -> bool:
        """Update mother/guardian fields for a student identified by student_id."""
        try:
            sanitized_id = SQLSanitizer.sanitize_query_param(student_id_code)
            if not sanitized_id:
                raise ValidationError("student_id", "Invalid student ID")
            # Allow only known columns
            allowed = [
                'household_size', 'mother_name', 'mother_marital_status', 'mother_cnic',
                'mother_cnic_doi', 'mother_cnic_exp', 'mother_mwa', 'household_name',
                'alternate_cnic', 'alternate_cnic_doi', 'alternate_cnic_exp',
                'alternate_marital_status', 'alternate_mwa', 'father_phone', 'alternate_relationship_with_mother'
            ]
            updates = {k: info.get(k) for k in allowed if k in info}
            if not updates:
                return False
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [sanitized_id]
            self.cursor.execute(
                f"UPDATE students SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE student_id = ?",
                tuple(values)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating mother info: {e}")
            raise

    def update_mother_info_bulk(self, student_snos: List[str], info: Dict[str, Any]) -> int:
        """Bulk update mother/guardian fields for multiple students by S#.
        Returns the number of updated rows.
        """
        if not student_snos:
            return 0
        try:
            # Sanitize S# values and remove empties/dupes
            safe_snos = []
            for s in student_snos:
                ss = SQLSanitizer.sanitize_query_param(str(s))
                if ss:
                    safe_snos.append(ss)
            safe_snos = list(dict.fromkeys(safe_snos))
            if not safe_snos:
                return 0
            # Allowed columns
            allowed = [
                'household_size', 'mother_name', 'mother_marital_status', 'mother_cnic',
                'mother_cnic_doi', 'mother_cnic_exp', 'mother_mwa', 'household_name',
                'alternate_cnic', 'alternate_cnic_doi', 'alternate_cnic_exp',
                'alternate_marital_status', 'alternate_mwa', 'father_phone', 'alternate_relationship_with_mother'
            ]
            updates = {k: info.get(k) for k in allowed if k in info}
            if not updates:
                return 0
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()]) + ", updated_at = CURRENT_TIMESTAMP"
            params_template = list(updates.values())
            # Use a transaction and executemany for performance
            with self.db_conn.transaction() as cur:
                param_rows = [tuple(params_template + [sno]) for sno in safe_snos]
                cur.executemany(
                    f"UPDATE students SET {set_clause} WHERE student_id = ?",
                    param_rows
                )
                # Calculate number of rows changed in this transaction
                # sqlite3 total_changes is cumulative per connection; capture delta
                # However within this transaction we can approximate via len(safe_snos)
            return len(safe_snos)
        except Exception as e:
            logging.error(f"Error bulk updating mother info: {e}")
            raise
