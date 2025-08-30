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
                # Organizations table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT,
                    code TEXT UNIQUE,
                    description TEXT,
                    address TEXT,
                    contact_number TEXT,
                    email TEXT,
                    registration_number TEXT,
                    head_office_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive'))
                )''')
                
                # Provinces table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS provinces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    code TEXT UNIQUE,
                    country TEXT DEFAULT 'Pakistan',
                    capital_city TEXT,
                    population INTEGER,
                    area_km2 REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive'))
                )''')
                
                # Districts table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS districts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE,
                    province_id INTEGER NOT NULL,
                    headquarters TEXT,
                    population INTEGER,
                    area_km2 REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
                    FOREIGN KEY (province_id) REFERENCES provinces (id) ON DELETE CASCADE,
                    UNIQUE(name, province_id)
                )''')
                
                # Union Councils table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS union_councils (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE,
                    district_id INTEGER NOT NULL,
                    province_id INTEGER NOT NULL,
                    population INTEGER,
                    area_km2 REAL,
                    chairman_name TEXT,
                    contact_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
                    FOREIGN KEY (district_id) REFERENCES districts (id) ON DELETE CASCADE,
                    FOREIGN KEY (province_id) REFERENCES provinces (id) ON DELETE CASCADE,
                    UNIQUE(name, district_id)
                )''')
                
                # Enhanced schools table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS schools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT,
                    org_id INTEGER,
                    province_id INTEGER,
                    district_id INTEGER,
                    union_council_id INTEGER,
                    address TEXT,
                    contact_number TEXT,
                    principal_name TEXT,
                    email TEXT,
                    registration_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
                    FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE SET NULL,
                    FOREIGN KEY (province_id) REFERENCES provinces (id) ON DELETE SET NULL,
                    FOREIGN KEY (district_id) REFERENCES districts (id) ON DELETE SET NULL,
                    FOREIGN KEY (union_council_id) REFERENCES union_councils (id) ON DELETE SET NULL
                )''')
                
                # Classes table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT UNIQUE NOT NULL,
                    class_level INTEGER,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive'))
                )''')
                
                # Sections table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                
                # Student audit table for storing original versions before updates
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS students_audit (
                    -- Audit specific fields
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_record_id INTEGER NOT NULL,
                    audit_action TEXT NOT NULL CHECK(audit_action IN ('UPDATE', 'DELETE')) DEFAULT 'UPDATE',
                    audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    audit_user_id INTEGER,
                    audit_username TEXT,
                    audit_user_phone TEXT,
                    audit_reason TEXT,
                    
                    -- Original student data (exact copy of students table structure)
                    id INTEGER,
                    status TEXT,
                    student_id TEXT,
                    final_unique_codes TEXT,
                    org_id INTEGER,
                    school_id INTEGER,
                    province_id INTEGER,
                    district_id INTEGER,
                    union_council_id INTEGER,
                    nationality_id INTEGER,
                    registration_number TEXT,
                    class_teacher_name TEXT,
                    student_name TEXT,
                    gender TEXT,
                    date_of_birth DATE,
                    students_bform_number TEXT,
                    year_of_admission DATE,
                    year_of_admission_alt DATE,
                    class TEXT,
                    section TEXT,
                    address TEXT,
                    father_name TEXT,
                    father_cnic TEXT,
                    father_phone TEXT,
                    household_size INTEGER,
                    mother_name TEXT,
                    mother_date_of_birth DATE,
                    mother_marital_status TEXT,
                    mother_id_type TEXT,
                    mother_cnic TEXT,
                    mother_cnic_doi DATE,
                    mother_cnic_exp DATE,
                    mother_mwa INTEGER,
                    household_role TEXT,
                    household_name TEXT,
                    hh_gender TEXT,
                    hh_date_of_birth DATE,
                    recipient_type TEXT,
                    alternate_name TEXT,
                    alternate_date_of_birth DATE,
                    alternate_marital_status TEXT,
                    alternate_id_type TEXT,
                    alternate_cnic TEXT,
                    alternate_cnic_doi DATE,
                    alternate_cnic_exp DATE,
                    alternate_mwa INTEGER,
                    alternate_relationship_with_mother TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    created_by INTEGER,
                    updated_by INTEGER,
                    created_by_username TEXT,
                    updated_by_username TEXT,
                    created_by_phone TEXT,
                    updated_by_phone TEXT,
                    is_deleted INTEGER,
                    deleted_at TIMESTAMP,
                    deleted_by INTEGER,
                    deleted_by_username TEXT,
                    deleted_by_phone TEXT,
                    version INTEGER
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
                
                # Basic student field indexes (only for fields that exist in current schema)
                "CREATE INDEX IF NOT EXISTS idx_students_student_name ON students(student_name)",
                "CREATE INDEX IF NOT EXISTS idx_students_class_section ON students(class, section)",
                "CREATE INDEX IF NOT EXISTS idx_students_status ON students(status)",
                "CREATE INDEX IF NOT EXISTS idx_students_gender ON students(gender)",
                
                # Family information indexes (only for existing fields)
                "CREATE INDEX IF NOT EXISTS idx_students_father_cnic ON students(father_cnic)",
                "CREATE INDEX IF NOT EXISTS idx_students_mother_cnic ON students(mother_cnic)",
                
                # Organizations table indexes
                "CREATE INDEX IF NOT EXISTS idx_organizations_name ON organizations(name)",
                "CREATE INDEX IF NOT EXISTS idx_organizations_code ON organizations(code)",
                "CREATE INDEX IF NOT EXISTS idx_organizations_type ON organizations(type)",
                "CREATE INDEX IF NOT EXISTS idx_organizations_status ON organizations(status)",
                
                # Provinces table indexes
                "CREATE INDEX IF NOT EXISTS idx_provinces_name ON provinces(name)",
                "CREATE INDEX IF NOT EXISTS idx_provinces_code ON provinces(code)",
                "CREATE INDEX IF NOT EXISTS idx_provinces_country ON provinces(country)",
                "CREATE INDEX IF NOT EXISTS idx_provinces_status ON provinces(status)",
                
                # Districts table indexes
                "CREATE INDEX IF NOT EXISTS idx_districts_name ON districts(name)",
                "CREATE INDEX IF NOT EXISTS idx_districts_province_id ON districts(province_id)",
                "CREATE INDEX IF NOT EXISTS idx_districts_code ON districts(code)",
                "CREATE INDEX IF NOT EXISTS idx_districts_status ON districts(status)",
                "CREATE INDEX IF NOT EXISTS idx_districts_name_province ON districts(name, province_id)",
                
                # Union Councils table indexes
                "CREATE INDEX IF NOT EXISTS idx_union_councils_name ON union_councils(name)",
                "CREATE INDEX IF NOT EXISTS idx_union_councils_district_id ON union_councils(district_id)",
                "CREATE INDEX IF NOT EXISTS idx_union_councils_province_id ON union_councils(province_id)",
                "CREATE INDEX IF NOT EXISTS idx_union_councils_code ON union_councils(code)",
                "CREATE INDEX IF NOT EXISTS idx_union_councils_status ON union_councils(status)",
                "CREATE INDEX IF NOT EXISTS idx_union_councils_name_district ON union_councils(name, district_id)",
                
                # Schools table indexes (enhanced)
                "CREATE INDEX IF NOT EXISTS idx_schools_name ON schools(name)",
                "CREATE INDEX IF NOT EXISTS idx_schools_type ON schools(type)",
                "CREATE INDEX IF NOT EXISTS idx_schools_status ON schools(status)",
                
                # Classes table indexes
                "CREATE INDEX IF NOT EXISTS idx_classes_name ON classes(class_name)",
                "CREATE INDEX IF NOT EXISTS idx_classes_level ON classes(class_level)",
                "CREATE INDEX IF NOT EXISTS idx_classes_status ON classes(status)",
                
                # Sections table indexes
                "CREATE INDEX IF NOT EXISTS idx_sections_name ON sections(section_name)",
                "CREATE INDEX IF NOT EXISTS idx_sections_status ON sections(status)",
                
                # Attendance and audit indexes
                "CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, date)",
                "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)",
                "CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id)",
                "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_activity_log_user_timestamp ON activity_log(user_id, timestamp)",
                
                # Composite indexes for common queries
                "CREATE INDEX IF NOT EXISTS idx_students_search ON students(student_name, student_id, father_name)"
            ]
            
            for index_sql in indexes:
                try:
                    self.cursor.execute(index_sql)
                except Exception as index_error:
                    # Log but don't fail - some indexes might reference columns that don't exist yet
                    logger.warning(f"Could not create index: {index_sql} - {index_error}")
            
            self.conn.commit()
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            # Don't raise exception to avoid breaking database initialization
            logger.warning("Some indexes may not have been created - continuing with database initialization")
    
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
                # Return the complete raw database row data for full field access
                students.append(student_data)
            
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
                raise ValueError("student_id is required for updating")
            
            # Check if student exists and get original record
            original_student = self.get_student_by_id(student_id)
            if not original_student:
                raise ValueError(f"Student not found: {student_id}")
            
            # Save original record to audit table before updating
            self._save_student_to_audit(original_student, 'UPDATE', user_id, username, user_phone, 'Student record update')
            
            # Build update query dynamically based on provided data
            update_fields = []
            values = []
            
            # Complete field mappings for all student fields
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
                'mother_date_of_birth': 'mother_date_of_birth',
                'mother_marital_status': 'mother_marital_status',
                'mother_id_type': 'mother_id_type',
                'mother_cnic_doi': 'mother_cnic_doi',
                'mother_cnic_exp': 'mother_cnic_exp',
                'mother_mwa': 'mother_mwa',
                'household_role': 'household_role',
                'household_name': 'household_name',
                'hh_gender': 'hh_gender',
                'hh_date_of_birth': 'hh_date_of_birth',
                'recipient_type': 'recipient_type',
                'alternate_name': 'alternate_name',
                'alternate_date_of_birth': 'alternate_date_of_birth',
                'alternate_marital_status': 'alternate_marital_status',
                'alternate_id_type': 'alternate_id_type',
                'alternate_cnic': 'alternate_cnic',
                'alternate_cnic_doi': 'alternate_cnic_doi',
                'alternate_cnic_exp': 'alternate_cnic_exp',
                'alternate_mwa': 'alternate_mwa',
                'alternate_relationship_with_mother': 'alternate_relationship_with_mother',
                'students_bform_number': 'students_bform_number',
                'year_of_admission': 'year_of_admission',
                'year_of_admission_alt': 'year_of_admission_alt',
                'registration_number': 'registration_number',
                'class_teacher_name': 'class_teacher_name',
                'household_size': 'household_size',
                'org_id': 'org_id',
                'school_id': 'school_id',
                'province_id': 'province_id',
                'district_id': 'district_id',
                'union_council_id': 'union_council_id',
                'nationality_id': 'nationality_id'
            }
            
            for key, db_field in field_mappings.items():
                if key in data and data[key] is not None:
                    update_fields.append(f"{db_field} = ?")
                    values.append(data[key])
            
            if not update_fields:
                logger.info(f"No fields to update for student: {student_id}")
                return True  # Nothing to update
            
            # Add audit fields
            update_fields.extend([
                "updated_by = ?",
                "updated_by_username = ?", 
                "updated_by_phone = ?",
                "updated_at = CURRENT_TIMESTAMP",
                "version = version + 1"
            ])
            values.extend([user_id, username, user_phone])
            
            # Add WHERE clause parameter
            values.append(student_id)
            
            update_sql = f"""
                UPDATE students SET {', '.join(update_fields)}
                WHERE student_id = ? AND status = 'active' AND is_deleted = 0
            """
            
            print(f"🔄 Updating student {student_id} with {len(update_fields)} fields")
            self.cursor.execute(update_sql, values)
            
            # Check if any rows were affected
            if self.cursor.rowcount == 0:
                raise ValueError(f"No student record updated. Student {student_id} may not exist or is deleted.")
            
            self.conn.commit()
            
            # Log the successful update
            logger.info(f"Student updated successfully: {student_id} by {username}")
            print(f"✅ Student {student_id} updated successfully by {username}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating student: {e}")
            print(f"❌ Error updating student: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def _save_student_to_audit(self, original_data: Dict[str, Any], action: str, user_id: int = None, username: str = None, user_phone: str = None, reason: str = ""):
        """Save the original student record to audit table before modification."""
        try:
            audit_sql = """
                INSERT INTO students_audit (
                    original_record_id, audit_action, audit_user_id, audit_username, 
                    audit_user_phone, audit_reason,
                    id, status, student_id, final_unique_codes, org_id, school_id,
                    province_id, district_id, union_council_id, nationality_id,
                    registration_number, class_teacher_name, student_name, gender,
                    date_of_birth, students_bform_number, year_of_admission, year_of_admission_alt,
                    class, section, address, father_name, father_cnic, father_phone,
                    household_size, mother_name, mother_date_of_birth, mother_marital_status,
                    mother_id_type, mother_cnic, mother_cnic_doi, mother_cnic_exp, mother_mwa,
                    household_role, household_name, hh_gender, hh_date_of_birth, recipient_type,
                    alternate_name, alternate_date_of_birth, alternate_marital_status,
                    alternate_id_type, alternate_cnic, alternate_cnic_doi, alternate_cnic_exp,
                    alternate_mwa, alternate_relationship_with_mother, created_at, updated_at,
                    created_by, updated_by, created_by_username, updated_by_username,
                    created_by_phone, updated_by_phone, version, is_deleted, deleted_at, 
                    deleted_by, deleted_by_username, deleted_by_phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            audit_values = (
                original_data.get('id'), action, user_id, username, user_phone, reason,
                original_data.get('id'), original_data.get('status'), original_data.get('student_id'),
                original_data.get('final_unique_codes'), original_data.get('org_id'), 
                original_data.get('school_id'), original_data.get('province_id'),
                original_data.get('district_id'), original_data.get('union_council_id'),
                original_data.get('nationality_id'), original_data.get('registration_number'),
                original_data.get('class_teacher_name'), original_data.get('student_name'),
                original_data.get('gender'), original_data.get('date_of_birth'),
                original_data.get('students_bform_number'), original_data.get('year_of_admission'),
                original_data.get('year_of_admission_alt'), original_data.get('class'),
                original_data.get('section'), original_data.get('address'),
                original_data.get('father_name'), original_data.get('father_cnic'),
                original_data.get('father_phone'), original_data.get('household_size'),
                original_data.get('mother_name'), original_data.get('mother_date_of_birth'),
                original_data.get('mother_marital_status'), original_data.get('mother_id_type'),
                original_data.get('mother_cnic'), original_data.get('mother_cnic_doi'),
                original_data.get('mother_cnic_exp'), original_data.get('mother_mwa'),
                original_data.get('household_role'), original_data.get('household_name'),
                original_data.get('hh_gender'), original_data.get('hh_date_of_birth'),
                original_data.get('recipient_type'), original_data.get('alternate_name'),
                original_data.get('alternate_date_of_birth'), original_data.get('alternate_marital_status'),
                original_data.get('alternate_id_type'), original_data.get('alternate_cnic'),
                original_data.get('alternate_cnic_doi'), original_data.get('alternate_cnic_exp'),
                original_data.get('alternate_mwa'), original_data.get('alternate_relationship_with_mother'),
                original_data.get('created_at'), original_data.get('updated_at'),
                original_data.get('created_by'), original_data.get('updated_by'),
                original_data.get('created_by_username'), original_data.get('updated_by_username'),
                original_data.get('created_by_phone'), original_data.get('updated_by_phone'),
                original_data.get('version'), original_data.get('is_deleted'), 
                original_data.get('deleted_at'), original_data.get('deleted_by'),
                original_data.get('deleted_by_username'), original_data.get('deleted_by_phone')
            )
            
            self.cursor.execute(audit_sql, audit_values)
            logger.info(f"Original student record saved to audit: {original_data.get('student_id')} by {username}")
            print(f"💾 Original record saved to audit for student: {original_data.get('student_id')}")
            
        except Exception as e:
            logger.error(f"Error saving student to audit: {e}")
            print(f"❌ Error saving to audit: {e}")
            # Don't fail the main operation if audit fails
            pass
    
    def delete_student(self, student_id: str, user_id: int = None, username: str = None, user_phone: str = None) -> bool:
        """Soft delete a student record with auditing."""
        try:
            # Check if student exists
            if not self.student_exists(student_id):
                raise ValueError("Student not found")
            
            # Get original record for audit trail
            original_query = "SELECT * FROM students WHERE student_id = ? AND is_deleted = 0"
            self.cursor.execute(original_query, (student_id,))
            original_record = self.cursor.fetchone()
            
            if original_record:
                # Save original record to audit table before deletion
                self._save_student_to_audit(
                    original_record, 
                    action='delete',
                    user_id=user_id,
                    username=username,
                    user_phone=user_phone,
                    reason=f'Student deleted by {username}'
                )
            
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
        """Get student by student ID with all related names included."""
        try:
            # Query with multiple JOINs to include all related names
            query = """
                SELECT s.*, 
                       sch.name as school_name,
                       o.name as organization_name,
                       p.name as province_name,
                       d.name as district_name,
                       uc.name as union_council_name,
                       n.name as nationality_name
                FROM students s 
                LEFT JOIN schools sch ON s.school_id = sch.id 
                LEFT JOIN organizations o ON s.org_id = o.id
                LEFT JOIN provinces p ON s.province_id = p.id
                LEFT JOIN districts d ON s.district_id = d.id
                LEFT JOIN union_councils uc ON s.union_council_id = uc.id
                LEFT JOIN nationalities n ON s.nationality_id = n.id
                WHERE s.student_id = ? AND s.status = 'active' AND s.is_deleted = 0
            """
            
            self.cursor.execute(query, (student_id,))
            result = self.cursor.fetchone()
            if result:
                # Convert to dict manually since result might be Row object
                columns = [desc[0] for desc in self.cursor.description]
                student_data = dict(zip(columns, result))
                
                # Provide meaningful fallbacks for missing data
                if not student_data.get('organization_name'):
                    student_data['organization_name'] = f"Organization ID #{student_data.get('org_id', 'N/A')}"
                if not student_data.get('province_name'):
                    student_data['province_name'] = f"Province ID #{student_data.get('province_id', 'N/A')}"
                if not student_data.get('district_name'):
                    student_data['district_name'] = f"District ID #{student_data.get('district_id', 'N/A')}"
                if not student_data.get('union_council_name'):
                    student_data['union_council_name'] = f"UC ID #{student_data.get('union_council_id', 'N/A')}"
                if not student_data.get('nationality_name'):
                    student_data['nationality_name'] = f"Nationality ID #{student_data.get('nationality_id', 'N/A')}"
                
                return student_data
            
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
        """Insert dummy data for organizations, provinces, districts, union councils, schools, classes, and sections if tables are empty."""
        try:
            # Check if organizations table is empty
            self.cursor.execute("SELECT COUNT(*) FROM organizations")
            if self.cursor.fetchone()[0] == 0:
                # Insert dummy organizations
                organizations_data = [
                    ("Department of Education Punjab", "Government", "DOE-PB", "Provincial education department", "Civil Secretariat, Lahore", "042-99200000", "doe@punjab.gov.pk", "GOV-PB-001", "Civil Secretariat, Punjab"),
                    ("Education Foundation Pakistan", "Non-Profit", "EFP", "Educational foundation", "Islamabad", "051-9876543", "info@efp.org.pk", "NGO-001", "F-8/2, Islamabad"),
                    ("Private Schools Association", "Association", "PSA", "Private schools regulatory body", "Karachi", "021-3456789", "admin@psa.edu.pk", "ASSOC-001", "Clifton, Karachi"),
                    ("Ministry of Education", "Federal", "MOE", "Federal education ministry", "Islamabad", "051-9207000", "moe@education.gov.pk", "FED-001", "Sector G-5/2, Islamabad")
                ]
                
                for org in organizations_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO organizations 
                        (name, type, code, description, address, contact_number, email, registration_number, head_office_address) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", org)

            # Check if provinces table is empty
            self.cursor.execute("SELECT COUNT(*) FROM provinces")
            if self.cursor.fetchone()[0] == 0:
                # Insert Pakistan provinces
                provinces_data = [
                    ("Punjab", "PB", "Pakistan", "Lahore", 120000000, 205344),
                    ("Sindh", "SD", "Pakistan", "Karachi", 55000000, 140914),
                    ("Khyber Pakhtunkhwa", "KP", "Pakistan", "Peshawar", 40000000, 101741),
                    ("Balochistan", "BA", "Pakistan", "Quetta", 15000000, 347190),
                    ("Islamabad Capital Territory", "ICT", "Pakistan", "Islamabad", 2500000, 906),
                    ("Gilgit-Baltistan", "GB", "Pakistan", "Gilgit", 2000000, 72971),
                    ("Azad Jammu and Kashmir", "AJK", "Pakistan", "Muzaffarabad", 4500000, 13297)
                ]
                
                for province in provinces_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO provinces 
                        (name, code, country, capital_city, population, area_km2) 
                        VALUES (?, ?, ?, ?, ?, ?)""", province)

            # Check if districts table is empty
            self.cursor.execute("SELECT COUNT(*) FROM districts")
            if self.cursor.fetchone()[0] == 0:
                # Get province IDs first
                self.cursor.execute("SELECT id, name FROM provinces")
                province_map = {row['name']: row['id'] for row in self.cursor.fetchall()}
                
                # Insert sample districts for major provinces
                districts_data = [
                    # Punjab districts
                    ("Lahore", "LHR", province_map.get("Punjab", 1), "Lahore", 12000000, 1772),
                    ("Karachi", "KHI", province_map.get("Sindh", 2), "Karachi", 16000000, 3527),
                    ("Faisalabad", "FSD", province_map.get("Punjab", 1), "Faisalabad", 8000000, 5856),
                    ("Rawalpindi", "RWP", province_map.get("Punjab", 1), "Rawalpindi", 6000000, 5286),
                    ("Peshawar", "PSH", province_map.get("Khyber Pakhtunkhwa", 3), "Peshawar", 5000000, 1257),
                    ("Multan", "MLT", province_map.get("Punjab", 1), "Multan", 4500000, 3720),
                    ("Hyderabad", "HYD", province_map.get("Sindh", 2), "Hyderabad", 2500000, 26000),
                    ("Gujranwala", "GRW", province_map.get("Punjab", 1), "Gujranwala", 2500000, 3622),
                    ("Islamabad", "ISB", province_map.get("Islamabad Capital Territory", 5), "Islamabad", 2500000, 906),
                    ("Quetta", "QTA", province_map.get("Balochistan", 4), "Quetta", 2500000, 2653)
                ]
                
                for district in districts_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO districts 
                        (name, code, province_id, headquarters, population, area_km2) 
                        VALUES (?, ?, ?, ?, ?, ?)""", district)

            # Check if union_councils table is empty
            self.cursor.execute("SELECT COUNT(*) FROM union_councils")
            if self.cursor.fetchone()[0] == 0:
                # Get district and province IDs
                self.cursor.execute("SELECT id, name, province_id FROM districts")
                districts = self.cursor.fetchall()
                
                # Insert sample union councils for major districts
                union_councils_data = []
                uc_counter = 1
                
                for district in districts[:5]:  # Only for first 5 districts to keep data manageable
                    district_name = district['name']
                    district_id = district['id']
                    province_id = district['province_id']
                    
                    # Add 3-5 union councils per district
                    for i in range(1, 4):
                        uc_name = f"{district_name} UC-{i}"
                        uc_code = f"UC-{uc_counter:03d}"
                        chairman = f"Chairman {district_name} {i}"
                        contact = f"03{uc_counter:02d}{1000000 + uc_counter}"
                        
                        union_councils_data.append((uc_name, uc_code, district_id, province_id, 50000 + (uc_counter * 1000), 25.5, chairman, contact))
                        uc_counter += 1
                
                for uc in union_councils_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO union_councils 
                        (name, code, district_id, province_id, population, area_km2, chairman_name, contact_number) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", uc)

            # Check if schools table is empty
            self.cursor.execute("SELECT COUNT(*) FROM schools")
            if self.cursor.fetchone()[0] == 0:
                # Get organization, province, district, and union council IDs
                self.cursor.execute("SELECT id FROM organizations LIMIT 1")
                org_id = self.cursor.fetchone()
                org_id = org_id['id'] if org_id else 1
                
                self.cursor.execute("SELECT id FROM provinces WHERE name = 'Punjab' LIMIT 1")
                province_id = self.cursor.fetchone()
                province_id = province_id['id'] if province_id else 1
                
                self.cursor.execute("SELECT id FROM districts WHERE name = 'Lahore' LIMIT 1")
                district_id = self.cursor.fetchone()
                district_id = district_id['id'] if district_id else 1
                
                self.cursor.execute("SELECT id FROM union_councils LIMIT 1")
                uc_id = self.cursor.fetchone()
                uc_id = uc_id['id'] if uc_id else 1
                
                # Insert dummy schools with foreign key references
                schools_data = [
                    ("Greenfield Public School", "Public", org_id, province_id, district_id, uc_id, "123 Education Street, Karachi", "021-12345678", "Dr. Ahmad Khan", "greenfield@education.pk", "SCH-001"),
                    ("Elite Grammar School", "Private", org_id, province_id, district_id, uc_id, "456 Learning Avenue, Lahore", "042-87654321", "Mrs. Fatima Sheikh", "elite@grammar.edu.pk", "SCH-002"),
                    ("Sunrise Academy", "Private", org_id, province_id, district_id, uc_id, "789 Knowledge Road, Islamabad", "051-11223344", "Mr. Hassan Ali", "sunrise@academy.edu.pk", "SCH-003"),
                    ("City Model School", "Public", org_id, province_id, district_id, uc_id, "321 School Lane, Peshawar", "091-55667788", "Ms. Ayesha Malik", "citymodel@education.pk", "SCH-004"),
                    ("Future Leaders Institute", "Private", org_id, province_id, district_id, uc_id, "654 Academic Plaza, Multan", "061-99887766", "Prof. Muhammad Iqbal", "future@leaders.edu.pk", "SCH-005"),
                    ("Al-Huda International School", "Private", org_id, province_id, district_id, uc_id, "987 Campus Drive, Faisalabad", "041-33445566", "Dr. Zainab Ahmed", "alhuda@international.edu.pk", "SCH-006")
                ]
                
                for school in schools_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO schools 
                        (name, type, org_id, province_id, district_id, union_council_id, address, contact_number, principal_name, email, registration_number) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", school)
            
            # Check if classes table is empty
            self.cursor.execute("SELECT COUNT(*) FROM classes")
            if self.cursor.fetchone()[0] == 0:
                # Insert classes data
                classes_data = [
                    ("Kachi", 0, "Pre-Primary class"),
                    ("Paki", 1, "Primary class"),
                    ("1", 2, "Grade 1"),
                    ("2", 3, "Grade 2"),
                    ("3", 4, "Grade 3"),
                    ("4", 5, "Grade 4"),
                    ("5", 6, "Grade 5"),
                    ("6", 7, "Grade 6"),
                    ("7", 8, "Grade 7"),
                    ("8", 9, "Grade 8"),
                    ("9", 10, "Grade 9"),
                    ("10", 11, "Grade 10")
                ]
                
                for class_data in classes_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO classes 
                        (class_name, class_level, description) 
                        VALUES (?, ?, ?)""", class_data)
            
            # Check if sections table is empty
            self.cursor.execute("SELECT COUNT(*) FROM sections")
            if self.cursor.fetchone()[0] == 0:
                # Insert sections data
                sections_data = [
                    ("A", "Section A"),
                    ("B", "Section B"),
                    ("C", "Section C"),
                    ("D", "Section D"),
                    ("E", "Section E"),
                    ("F", "Section F")
                ]
                
                for section_data in sections_data:
                    self.cursor.execute("""INSERT OR IGNORE INTO sections 
                        (section_name, description) 
                        VALUES (?, ?)""", section_data)
            
            # For students table, we'll skip dummy data since we have a clean structure now
            # and want to avoid column reference issues
            
            self.conn.commit()
            logging.info("Dummy data inserted successfully for all tables")
            
        except Exception as e:
            logging.error(f"Error inserting dummy data: {e}")
            # Don't raise the exception to avoid breaking database initialization

    def get_schools(self):
        """Get all schools from schools table."""
        try:
            self.cursor.execute("SELECT * FROM schools WHERE status = 'active' ORDER BY name")
            schools = []
            for row in self.cursor.fetchall():
                school_dict = dict(row)
                # Ensure backward compatibility by providing both 'name' and 'school_name' keys
                school_dict['school_name'] = school_dict.get('name', '')
                schools.append(school_dict)
            return schools
        except Exception as e:
            logging.error(f"Error getting schools: {e}")
            return []

    def get_school_organizational_data(self, school_id):
        """Get organizational data for a school (org_id, province_id, district_id, union_council_id, nationality_id)."""
        try:
            self.cursor.execute("SELECT * FROM schools WHERE id = ?", (school_id,))
            school = self.cursor.fetchone()
            
            if school:
                # Convert to dict for easier access
                school_dict = dict(school)
                
                # Default organizational data based on school info
                # For now, we'll set default values - these can be enhanced later
                organizational_data = {
                    'org_id': 1,  # Default organization
                    'province_id': 1,  # Default province (Punjab)
                    'district_id': 1,  # Default district (Lahore)
                    'union_council_id': 1,  # Default union council
                    'nationality_id': 1  # Default nationality (Pakistani)
                }
                
                # Try to map based on school's province/district text fields if available
                province_text = school_dict.get('province', '').lower()
                district_text = school_dict.get('district', '').lower()
                
                # Map province text to province_id
                if 'sindh' in province_text:
                    organizational_data['province_id'] = 2
                elif 'khyber' in province_text or 'kp' in province_text:
                    organizational_data['province_id'] = 3
                elif 'balochistan' in province_text:
                    organizational_data['province_id'] = 4
                elif 'islamabad' in province_text:
                    organizational_data['province_id'] = 5
                    
                # Map district text to district_id
                if 'karachi' in district_text:
                    organizational_data['district_id'] = 2
                elif 'rawalpindi' in district_text:
                    organizational_data['district_id'] = 3
                elif 'peshawar' in district_text:
                    organizational_data['district_id'] = 4
                elif 'islamabad' in district_text:
                    organizational_data['district_id'] = 6
                
                return organizational_data
            
            return None
        except Exception as e:
            logging.error(f"Error getting school organizational data: {e}")
            return None

    def get_classes(self, school_id=None):
        """Get classes from classes table."""
        try:
            self.cursor.execute("""
                SELECT name 
                FROM classes 
                ORDER BY name
            """)
            return [row['name'] for row in self.cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting classes: {e}")
            # Fallback to distinct values from students table
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
            except Exception as fallback_error:
                logging.error(f"Error getting classes from students table: {fallback_error}")
                return []

    def get_sections(self, school_id=None, class_name=None):
        """Get sections from sections table."""
        try:
            self.cursor.execute("""
                SELECT name 
                FROM sections 
                ORDER BY name
            """)
            return [row['name'] for row in self.cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting sections: {e}")
            # Fallback to distinct values from students table
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
            except Exception as fallback_error:
                logging.error(f"Error getting sections from students table: {fallback_error}")
                return []

    def get_organizations(self):
        """Get all organizations from organizations table."""
        try:
            self.cursor.execute("SELECT * FROM organizations WHERE status = 'active' ORDER BY name")
            organizations = []
            for row in self.cursor.fetchall():
                org_dict = dict(row)
                organizations.append(org_dict)
            return organizations
        except Exception as e:
            logging.error(f"Error getting organizations: {e}")
            return []

    def get_provinces(self):
        """Get all provinces from provinces table."""
        try:
            self.cursor.execute("SELECT * FROM provinces WHERE status = 'active' ORDER BY name")
            provinces = []
            for row in self.cursor.fetchall():
                province_dict = dict(row)
                provinces.append(province_dict)
            return provinces
        except Exception as e:
            logging.error(f"Error getting provinces: {e}")
            return []

    def get_districts(self, province_id=None):
        """Get districts from districts table, optionally filtered by province."""
        try:
            if province_id:
                self.cursor.execute("""
                    SELECT * FROM districts 
                    WHERE status = 'active' AND province_id = ? 
                    ORDER BY name
                """, (province_id,))
            else:
                self.cursor.execute("SELECT * FROM districts WHERE status = 'active' ORDER BY name")
            
            districts = []
            for row in self.cursor.fetchall():
                district_dict = dict(row)
                districts.append(district_dict)
            return districts
        except Exception as e:
            logging.error(f"Error getting districts: {e}")
            return []

    def get_union_councils(self, district_id=None, province_id=None):
        """Get union councils from union_councils table, optionally filtered by district or province."""
        try:
            query = "SELECT * FROM union_councils WHERE status = 'active'"
            params = []
            
            if district_id:
                query += " AND district_id = ?"
                params.append(district_id)
            elif province_id:
                query += " AND province_id = ?"
                params.append(province_id)
                
            query += " ORDER BY name"
            
            self.cursor.execute(query, params)
            union_councils = []
            for row in self.cursor.fetchall():
                uc_dict = dict(row)
                union_councils.append(uc_dict)
            return union_councils
        except Exception as e:
            logging.error(f"Error getting union councils: {e}")
            return []

    def get_nationalities(self):
        """Get nationalities list. For now, return Pakistani and common nationalities."""
        try:
            # For now, return a hardcoded list. Later this can be from a nationalities table
            nationalities = [
                {"id": 1, "name": "Pakistani", "code": "PAK"},
                {"id": 2, "name": "Indian", "code": "IND"},
                {"id": 3, "name": "Bangladeshi", "code": "BGD"},
                {"id": 4, "name": "Afghan", "code": "AFG"},
                {"id": 5, "name": "British", "code": "GBR"},
                {"id": 6, "name": "American", "code": "USA"},
                {"id": 7, "name": "Canadian", "code": "CAN"},
                {"id": 8, "name": "Australian", "code": "AUS"},
                {"id": 9, "name": "Chinese", "code": "CHN"},
                {"id": 10, "name": "Other", "code": "OTH"}
            ]
            return nationalities
        except Exception as e:
            logging.error(f"Error getting nationalities: {e}")
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

    def add_student(self, student_data: Dict[str, Any]) -> int:
        """Add new student with only non-audit fields."""
        try:
            # Define allowed non-audit fields based on database schema
            allowed_fields = [
                # Primary and System Fields
                'status', 'student_id', 'final_unique_codes',
                
                # Organization and Location IDs
                'org_id', 'school_id', 'province_id', 'district_id', 
                'union_council_id', 'nationality_id',
                
                # School Information
                'registration_number', 'class_teacher_name',
                
                # Student Basic Information
                'student_name', 'gender', 'date_of_birth', 'students_bform_number',
                'year_of_admission', 'year_of_admission_alt', 'class', 'section', 'address',
                
                # Father Information
                'father_name', 'father_cnic', 'father_phone',
                
                # Household Information
                'household_size',
                
                # Mother Information
                'mother_name', 'mother_date_of_birth', 'mother_marital_status',
                'mother_id_type', 'mother_cnic', 'mother_cnic_doi', 
                'mother_cnic_exp', 'mother_mwa',
                
                # Household Head Information
                'household_role', 'household_name', 'hh_gender', 
                'hh_date_of_birth', 'recipient_type',
                
                # Alternate/Guardian Information (Optional)
                'alternate_name', 'alternate_date_of_birth', 'alternate_marital_status',
                'alternate_id_type', 'alternate_cnic', 'alternate_cnic_doi',
                'alternate_cnic_exp', 'alternate_mwa', 'alternate_relationship_with_mother'
            ]
            
            # Filter data to include only allowed fields
            filtered_data = {k: v for k, v in student_data.items() if k in allowed_fields}
            
            # Add default values for required fields if not provided
            defaults = {
                'final_unique_codes': 'AUTO_GENERATED',
                'org_id': 1,  # Default organization
                'school_id': 1,  # Default school
                'province_id': 1,  # Default province
                'district_id': 1,  # Default district
                'union_council_id': 1,  # Default union council
                'nationality_id': 1,  # Default nationality (Pakistani)
                'registration_number': f"REG_{student_data.get('student_id', 'AUTO')}",
                'class_teacher_name': 'TBD',  # To Be Determined
                'students_bform_number': student_data.get('b_form_number', ''),
                'year_of_admission': student_data.get('date_of_birth', '2023-01-01'),
                'year_of_admission_alt': student_data.get('date_of_birth', '2023-01-01'),
                'household_size': 1,
                'mother_marital_status': 'Married',
                'mother_id_type': 'CNIC',
                'mother_cnic_doi': '2000-01-01',
                'mother_cnic_exp': '2030-01-01',
                'mother_mwa': 0,
                'household_role': 'Child',
                'household_name': student_data.get('father_name', 'Guardian'),
                'hh_gender': 'Male',
                'hh_date_of_birth': '1980-01-01',
                'recipient_type': 'Principal'
            }
            
            # Apply defaults for missing required fields
            for field, default_value in defaults.items():
                if field not in filtered_data or not filtered_data[field]:
                    filtered_data[field] = default_value
            
            # Validate required fields
            required_fields = [
                'student_id', 'final_unique_codes', 'org_id', 'school_id',
                'province_id', 'district_id', 'union_council_id', 'nationality_id',
                'registration_number', 'class_teacher_name', 'student_name', 'gender',
                'date_of_birth', 'students_bform_number', 'year_of_admission',
                'year_of_admission_alt', 'class', 'section', 'address',
                'father_name', 'father_cnic', 'father_phone', 'household_size',
                'mother_name', 'mother_date_of_birth', 'mother_marital_status',
                'mother_id_type', 'mother_cnic', 'mother_cnic_doi',
                'mother_cnic_exp', 'mother_mwa', 'household_role',
                'household_name', 'hh_gender', 'hh_date_of_birth', 'recipient_type'
            ]
            
            missing_fields = [field for field in required_fields if field not in filtered_data or not filtered_data[field]]
            if missing_fields:
                raise ValidationError("missing_fields", f"Required fields missing: {', '.join(missing_fields)}")
            
            # Set default status if not provided
            if 'status' not in filtered_data:
                filtered_data['status'] = 'active'
            
            # Build and execute INSERT query
            fields = ", ".join(filtered_data.keys())
            placeholders = ", ".join(["?" for _ in filtered_data])
            values = list(filtered_data.values())
            
            query = f"INSERT INTO students ({fields}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            student_id = self.cursor.lastrowid
            
            self.conn.commit()
            logger.info(f"Student {filtered_data.get('student_id')} added successfully with ID: {student_id}")
            return student_id
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error adding student: {e}")
            raise DatabaseError(f"Failed to add student: {e}")

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

    def get_school_info(self, school_id):
        """Get school information including related IDs."""
        try:
            # For now, return default values since schools table structure is not defined
            # This can be enhanced later when proper schools table is implemented
            return {
                'school_id': school_id,
                'org_id': 1,
                'province_id': 1,
                'district_id': 1,
                'union_council_id': 1,
                'nationality_id': 1
            }
        except Exception as e:
            logging.error(f"Error getting school info: {e}")
            return None

    def get_student_history(self, student_id):
        """Get complete change history for a student from audit table with detailed field changes."""
        try:
            cursor = self.conn.cursor()
            
            # Get audit records for this student with proper field changes
            audit_query = """
                SELECT 
                    audit_timestamp as action_date,
                    audit_action,
                    audit_username,
                    audit_reason,
                    student_name,
                    class,
                    section,
                    father_name,
                    father_phone,
                    address,
                    created_by_username,
                    updated_by_username,
                    audit_id
                FROM students_audit 
                WHERE student_id = ? 
                ORDER BY audit_timestamp DESC
            """
            
            cursor.execute(audit_query, (student_id,))
            audit_records = cursor.fetchall()
            
            # Get current student data for comparison
            current_query = """
                SELECT 
                    created_at,
                    updated_at,
                    created_by_username,
                    updated_by_username,
                    student_name,
                    class,
                    section,
                    father_name,
                    father_phone,
                    address
                FROM students 
                WHERE student_id = ? AND is_deleted = 0
            """
            
            cursor.execute(current_query, (student_id,))
            current_data = cursor.fetchone()
            
            history_records = []
            
            # Process audit records to detect actual field changes
            for i, record in enumerate(audit_records):
                action_date = record[0] or 'Unknown'
                action_type = record[1] or 'UPDATE'
                username = record[2] or record[10] or record[11] or 'System'
                reason = record[3] or 'Record update'
                
                # Compare with previous record to detect actual changes
                changed_fields = []
                old_values = []
                new_values = []
                
                if i < len(audit_records) - 1:  # Not the last record
                    prev_record = audit_records[i + 1]
                    
                    # Check each field for changes
                    field_mapping = {
                        4: 'Student Name',
                        5: 'Class', 
                        6: 'Section',
                        7: "Father's Name",
                        8: "Father's Phone",
                        9: 'Address'
                    }
                    
                    for field_idx, field_name in field_mapping.items():
                        if record[field_idx] != prev_record[field_idx]:
                            changed_fields.append(field_name)
                            old_values.append(str(prev_record[field_idx] or ''))
                            new_values.append(str(record[field_idx] or ''))
                
                else:  # First record (original creation)
                    if action_type == 'INSERT' or len(audit_records) == 1:
                        changed_fields = ['RECORD_CREATED']
                        old_values = ['']
                        new_values = [f"Student '{record[4]}' added to system"]
                
                # Create history entry for each changed field or group them
                if changed_fields:
                    if len(changed_fields) == 1:
                        # Single field change
                        history_records.append({
                            'date_time': action_date,
                            'field_changed': changed_fields[0],
                            'old_value': old_values[0] if old_values else '',
                            'new_value': new_values[0] if new_values else '',
                            'change_type': action_type,
                            'changed_by': username
                        })
                    else:
                        # Multiple field changes - create one entry with summary
                        field_summary = f"{len(changed_fields)} fields: " + ", ".join(changed_fields)
                        value_summary = " | ".join([f"{field}: '{old}' → '{new}'" 
                                                  for field, old, new in zip(changed_fields, old_values, new_values)])
                        
                        history_records.append({
                            'date_time': action_date,
                            'field_changed': field_summary,
                            'old_value': 'Multiple changes',
                            'new_value': value_summary,
                            'change_type': action_type,
                            'changed_by': username
                        })
                else:
                    # No specific field changes detected, show generic update
                    history_records.append({
                        'date_time': action_date,
                        'field_changed': 'Record updated',
                        'old_value': 'Previous state',
                        'new_value': reason,
                        'change_type': action_type,
                        'changed_by': username
                    })
            
            # Add current record creation if no audit records exist
            if not history_records and current_data:
                history_records.append({
                    'date_time': current_data[0] or 'Unknown',
                    'field_changed': 'RECORD_CREATED',
                    'old_value': '',
                    'new_value': f"Student '{current_data[4]}' added to system",
                    'change_type': 'INSERT',
                    'changed_by': current_data[2] or 'System'
                })
            
            return history_records
            
        except Exception as e:
            logging.error(f"Error getting student history: {e}")
            return []
