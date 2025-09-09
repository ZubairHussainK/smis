"""Enhanced database management with ORM-like schema management."""
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
from models.schema_manager import SchemaManager

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
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one database connection."""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database with enhanced security."""
        if self._initialized:
            return
            
        self.db_conn = DatabaseConnection()
        self.conn = self.db_conn.conn
        self.cursor = self.db_conn.cursor
        
        # Initialize schema manager
        self.schema_manager = SchemaManager(self.conn)
        self.schema_manager.define_schema()
        
        # Create or upgrade schema
        self._create_or_upgrade_schema()
        
        self._initialized = True
    
    def _create_or_upgrade_schema(self):
        """Create or upgrade database schema."""
        try:
            # Check if schema needs to be created or upgraded
            if not self.schema_manager.check_schema_matches():
                logger.info("Creating or upgrading database schema")
                self.schema_manager.create_all_tables()
                self.schema_manager.create_triggers()
                self._create_indexes()
                self._initialize_lookup_data()
                logger.info("Schema creation/upgrade completed")
            
        except Exception as e:
            logger.error(f"Schema creation/upgrade failed: {e}")
            raise DatabaseError(f"Failed to create/upgrade database schema: {e}")
    
    def _create_indexes(self):
        """Create database indexes for performance optimization."""
        try:
            with self.db_conn.transaction():
                # Students indexes for common queries
                self.cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
                ''')
                
                self.cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_students_school_class 
                    ON students(school_id, class_id);
                ''')
                
                # Schools indexes
                self.cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_schools_district 
                    ON schools(district_id);
                ''')
                
                # Users indexes for authentication
                self.cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_users_username 
                    ON users(username);
                ''')
                
                self.cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_users_email 
                    ON users(email);
                ''')
                
                logger.info("Database indexes created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    def _initialize_lookup_data(self):
        """Initialize lookup data for dropdown lists."""
        try:
            with self.db_conn.transaction():
                # Check if any provinces exist
                self.cursor.execute("SELECT COUNT(*) FROM provinces")
                if self.cursor.fetchone()[0] == 0:
                    # Add provinces
                    provinces = [
                        ("Punjab", "PB"),
                        ("Sindh", "SD"),
                        ("Khyber Pakhtunkhwa", "KP"),
                        ("Balochistan", "BL"),
                        ("Islamabad", "IS")
                    ]
                    self.cursor.executemany(
                        "INSERT INTO provinces (name, code) VALUES (?, ?)",
                        provinces
                    )
                    logger.info("Initialized provinces lookup data")
                
                # Check if any classes exist
                self.cursor.execute("SELECT COUNT(*) FROM classes")
                if self.cursor.fetchone()[0] == 0:
                    # Add classes
                    classes = [
                        ("Class 1", 1),
                        ("Class 2", 2),
                        ("Class 3", 3),
                        ("Class 4", 4),
                        ("Class 5", 5),
                        ("Class 6", 6),
                        ("Class 7", 7),
                        ("Class 8", 8),
                        ("Class 9", 9),
                        ("Class 10", 10),
                    ]
                    self.cursor.executemany(
                        "INSERT INTO classes (class_name, class_level) VALUES (?, ?)",
                        classes
                    )
                    logger.info("Initialized classes lookup data")
                
                # Check if any sections exist
                self.cursor.execute("SELECT COUNT(*) FROM sections")
                if self.cursor.fetchone()[0] == 0:
                    # Add sections
                    sections = [
                        ("Section A",),
                        ("Section B",),
                        ("Section C",),
                        ("Section D",),
                    ]
                    self.cursor.executemany(
                        "INSERT INTO sections (section_name) VALUES (?)",
                        sections
                    )
                    logger.info("Initialized sections lookup data")
                
        except Exception as e:
            logger.error(f"Failed to initialize lookup data: {e}")
    
    def _create_triggers(self):
        """Create database triggers for automatic timestamps and auditing."""
        try:
            with self.db_conn.transaction():
                # Updated at trigger for students
                self.cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS update_student_timestamp
                    AFTER UPDATE ON students
                    BEGIN
                        UPDATE students SET updated_at = CURRENT_TIMESTAMP
                        WHERE id = NEW.id;
                    END;
                ''')
                
                # Audit trigger for students
                self.cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS audit_student_changes
                    AFTER UPDATE ON students
                    BEGIN
                        INSERT INTO audit_log (
                            table_name, record_id, action, user_id, 
                            timestamp, old_values, new_values
                        )
                        VALUES (
                            'students', NEW.id, 'UPDATE', NULL,
                            CURRENT_TIMESTAMP, 
                            json_object(
                                'name', OLD.name,
                                'class_id', OLD.class_id,
                                'section_id', OLD.section_id,
                                'status', OLD.status
                            ),
                            json_object(
                                'name', NEW.name,
                                'class_id', NEW.class_id,
                                'section_id', NEW.section_id,
                                'status', NEW.status
                            )
                        );
                    END;
                ''')
                
                logger.info("Database triggers created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create triggers: {e}")
            
    # Add more methods for database operations...
    
    def execute_safe_query(self, query, params=None):
        """Execute a safe query with parameter sanitization."""
        with PerformanceLogger("database_query"):
            # Sanitize parameters
            safe_params = []
            if params:
                if isinstance(params, dict):
                    safe_params = {k: SQLSanitizer.sanitize(v) for k, v in params.items()}
                else:
                    safe_params = [SQLSanitizer.sanitize(p) for p in params]
                    
            try:
                if params:
                    self.cursor.execute(query, safe_params)
                else:
                    self.cursor.execute(query)
                    
                return self.cursor
            except Exception as e:
                logger.error(f"Query execution error: {e}, Query: {query}")
                raise DatabaseError(f"Query execution failed: {e}")
                
    def fetch_all(self, query, params=None):
        """Fetch all rows from a query with sanitization."""
        cursor = self.execute_safe_query(query, params)
        return cursor.fetchall()
        
    def fetch_one(self, query, params=None):
        """Fetch one row from a query with sanitization."""
        cursor = self.execute_safe_query(query, params)
        return cursor.fetchone()
        
    def insert(self, table, data, return_id=False):
        """Insert data into a table with sanitization."""
        # Sanitize input data
        safe_data = {k: SQLSanitizer.sanitize(v) for k, v in data.items()}
        
        columns = ", ".join(safe_data.keys())
        placeholders = ", ".join(["?" for _ in safe_data])
        values = list(safe_data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.db_conn.transaction():
                self.cursor.execute(query, values)
                
                if return_id:
                    return self.cursor.lastrowid
                return True
                
        except Exception as e:
            logger.error(f"Insert error: {e}, Table: {table}, Data: {data}")
            raise DatabaseError(f"Insert operation failed: {e}")
            
    def update(self, table, data, condition, params=None):
        """Update data in a table with sanitization."""
        # Sanitize input data
        safe_data = {k: SQLSanitizer.sanitize(v) for k, v in data.items()}
        
        # Build SET clause
        set_clause = ", ".join([f"{k} = ?" for k in safe_data.keys()])
        values = list(safe_data.values())
        
        # Add condition parameters
        if params:
            if isinstance(params, dict):
                condition_params = [SQLSanitizer.sanitize(v) for v in params.values()]
            else:
                condition_params = [SQLSanitizer.sanitize(p) for p in params]
            values.extend(condition_params)
        
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        try:
            with self.db_conn.transaction():
                self.cursor.execute(query, values)
                return self.cursor.rowcount
                
        except Exception as e:
            logger.error(f"Update error: {e}, Table: {table}, Data: {data}")
            raise DatabaseError(f"Update operation failed: {e}")
            
    def delete(self, table, condition, params=None):
        """Delete data from a table with sanitization."""
        query = f"DELETE FROM {table} WHERE {condition}"
        
        try:
            with self.db_conn.transaction():
                if params:
                    # Sanitize parameters
                    if isinstance(params, dict):
                        safe_params = {k: SQLSanitizer.sanitize(v) for k, v in params.items()}
                    else:
                        safe_params = [SQLSanitizer.sanitize(p) for p in params]
                    
                    self.cursor.execute(query, safe_params)
                else:
                    self.cursor.execute(query)
                    
                return self.cursor.rowcount
                
        except Exception as e:
            logger.error(f"Delete error: {e}, Table: {table}")
            raise DatabaseError(f"Delete operation failed: {e}")
            
    def backup_database(self, backup_path):
        """Create a backup of the database."""
        try:
            # Create a new connection to the backup file
            backup_conn = sqlite3.connect(backup_path)
            
            # Backup using the SQLite backup API
            with backup_conn:
                self.conn.backup(backup_conn)
                
            backup_conn.close()
            logger.info(f"Database backup created at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup error: {e}")
            return False
            
    def close(self):
        """Close the database connection."""
        self.db_conn.close()
