"""
ORM-like database schema manager for SMIS application.
This module provides a more maintainable approach to database schema management
than using raw SQL strings directly in the code.
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TableSchema:
    """Class representing a database table schema."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new table schema.
        
        Args:
            name (str): Name of the table
            description (str): Description of the table purpose
        """
        self.name = name
        self.description = description
        self.columns = []
        self.indexes = []
        self.foreign_keys = []
        
    def add_column(self, name: str, type_: str, **kwargs):
        """
        Add a column to the table schema.
        
        Args:
            name (str): Column name
            type_ (str): Column type (TEXT, INTEGER, etc.)
            **kwargs: Additional column attributes (PRIMARY KEY, NOT NULL, etc.)
        
        Returns:
            TableSchema: Self for method chaining
        """
        column = {
            "name": name,
            "type": type_,
            **kwargs
        }
        self.columns.append(column)
        return self
    
    def add_primary_key(self, name: str = "id"):
        """
        Add an auto-incrementing primary key to the table.
        
        Args:
            name (str): Name of the primary key column
        
        Returns:
            TableSchema: Self for method chaining
        """
        self.add_column(name, "INTEGER", primary_key=True, autoincrement=True)
        return self
    
    def add_foreign_key(self, column: str, ref_table: str, ref_column: str = "id", 
                       on_delete: str = "CASCADE", on_update: str = "CASCADE"):
        """
        Add a foreign key constraint to the table.
        
        Args:
            column (str): Column name in this table
            ref_table (str): Referenced table
            ref_column (str): Referenced column in referenced table
            on_delete (str): ON DELETE behavior
            on_update (str): ON UPDATE behavior
        
        Returns:
            TableSchema: Self for method chaining
        """
        self.foreign_keys.append({
            "column": column,
            "ref_table": ref_table,
            "ref_column": ref_column,
            "on_delete": on_delete,
            "on_update": on_update
        })
        return self
    
    def add_index(self, columns: List[str], name: str = None, unique: bool = False):
        """
        Add an index to the table.
        
        Args:
            columns (List[str]): List of columns to include in the index
            name (str): Optional index name
            unique (bool): Whether the index should be unique
        
        Returns:
            TableSchema: Self for method chaining
        """
        if name is None:
            name = f"idx_{self.name}_{'_'.join(columns)}"
        
        self.indexes.append({
            "name": name,
            "columns": columns,
            "unique": unique
        })
        return self
    
    def add_timestamps(self):
        """
        Add created_at and updated_at timestamp columns.
        
        Returns:
            TableSchema: Self for method chaining
        """
        self.add_column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP")
        self.add_column("updated_at", "TIMESTAMP", default="CURRENT_TIMESTAMP")
        return self
    
    def add_audit_columns(self):
        """
        Add audit columns (created_by, updated_by).
        
        Returns:
            TableSchema: Self for method chaining
        """
        self.add_column("created_by", "INTEGER")
        self.add_column("updated_by", "INTEGER")
        return self
    
    def add_status_column(self, default: str = "active"):
        """
        Add a status column with check constraint.
        
        Args:
            default (str): Default status value
        
        Returns:
            TableSchema: Self for method chaining
        """
        self.add_column(
            "status", "TEXT", 
            default=f"'{default}'", 
            check=f"status IN ('active', 'inactive', 'deleted', 'pending')"
        )
        return self
    
    def get_create_statement(self) -> str:
        """
        Generate the CREATE TABLE SQL statement.
        
        Returns:
            str: SQL statement for creating the table
        """
        # Start with column definitions
        column_defs = []
        for col in self.columns:
            col_def = f"{col['name']} {col['type']}"
            
            # Handle primary key
            if col.get("primary_key"):
                col_def += " PRIMARY KEY"
                if col.get("autoincrement"):
                    col_def += " AUTOINCREMENT"
            
            # Handle not null
            if col.get("not_null"):
                col_def += " NOT NULL"
            
            # Handle unique
            if col.get("unique"):
                col_def += " UNIQUE"
            
            # Handle default
            if "default" in col:
                col_def += f" DEFAULT {col['default']}"
            
            # Handle check constraints
            if "check" in col:
                col_def += f" CHECK({col['check']})"
            
            column_defs.append(col_def)
        
        # Add foreign key constraints
        for fk in self.foreign_keys:
            fk_def = f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['ref_table']}({fk['ref_column']})"
            if fk.get("on_delete"):
                fk_def += f" ON DELETE {fk['on_delete']}"
            if fk.get("on_update"):
                fk_def += f" ON UPDATE {fk['on_update']}"
            column_defs.append(fk_def)
        
        # Combine into CREATE TABLE statement
        create_statement = f"CREATE TABLE IF NOT EXISTS {self.name} (\n"
        create_statement += ",\n".join(f"    {col_def}" for col_def in column_defs)
        create_statement += "\n)"
        
        return create_statement
    
    def get_index_statements(self) -> List[str]:
        """
        Generate CREATE INDEX SQL statements.
        
        Returns:
            List[str]: List of SQL statements for creating indexes
        """
        statements = []
        for idx in self.indexes:
            unique_str = "UNIQUE " if idx["unique"] else ""
            columns_str = ", ".join(idx["columns"])
            stmt = f"CREATE {unique_str}INDEX IF NOT EXISTS {idx['name']} ON {self.name} ({columns_str})"
            statements.append(stmt)
        return statements


class SchemaManager:
    """
    Database schema manager for creating and upgrading database schema.
    """
    
    def __init__(self, db_connection):
        """
        Initialize the schema manager.
        
        Args:
            db_connection: SQLite database connection
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self.tables = {}
    
    def define_schema(self):
        """Define the complete database schema."""
        # Organizations table
        org_table = TableSchema("organizations", "Organizations or schools in the system")
        org_table.add_primary_key()
        org_table.add_column("name", "TEXT", not_null=True, unique=True)
        org_table.add_column("type", "TEXT")
        org_table.add_column("code", "TEXT", unique=True)
        org_table.add_column("description", "TEXT")
        org_table.add_column("address", "TEXT")
        org_table.add_column("contact_number", "TEXT")
        org_table.add_column("email", "TEXT")
        org_table.add_column("registration_number", "TEXT")
        org_table.add_column("head_office_address", "TEXT")
        org_table.add_timestamps()
        org_table.add_column("created_by", "INTEGER")
        org_table.add_status_column()
        org_table.add_index(["name"])
        org_table.add_index(["code"], unique=True)
        self.tables["organizations"] = org_table
        
        # Provinces table
        provinces = TableSchema("provinces", "Provinces or states")
        provinces.add_primary_key()
        provinces.add_column("name", "TEXT", not_null=True)
        provinces.add_column("code", "TEXT")
        provinces.add_timestamps()
        provinces.add_status_column()
        provinces.add_index(["name"])
        self.tables["provinces"] = provinces
        
        # Districts table
        districts = TableSchema("districts", "Districts or cities")
        districts.add_primary_key()
        districts.add_column("name", "TEXT", not_null=True)
        districts.add_column("code", "TEXT")
        districts.add_column("province_id", "INTEGER", not_null=True)
        districts.add_timestamps()
        districts.add_status_column()
        districts.add_foreign_key("province_id", "provinces")
        districts.add_index(["name", "province_id"])
        self.tables["districts"] = districts
        
        # Schools table
        schools = TableSchema("schools", "Schools in the system")
        schools.add_primary_key()
        schools.add_column("name", "TEXT", not_null=True)
        schools.add_column("code", "TEXT")
        schools.add_column("address", "TEXT")
        schools.add_column("phone", "TEXT")
        schools.add_column("email", "TEXT")
        schools.add_column("principal_name", "TEXT")
        schools.add_column("district_id", "INTEGER")
        schools.add_column("organization_id", "INTEGER")
        schools.add_timestamps()
        schools.add_audit_columns()
        schools.add_status_column()
        schools.add_foreign_key("district_id", "districts", on_delete="SET NULL")
        schools.add_foreign_key("organization_id", "organizations", on_delete="SET NULL")
        schools.add_index(["name"])
        schools.add_index(["organization_id"])
        self.tables["schools"] = schools
        
        # Classes table
        classes = TableSchema("classes", "Grade levels")
        classes.add_primary_key()
        classes.add_column("name", "TEXT", not_null=True)
        classes.add_column("display_name", "TEXT")
        classes.add_column("school_id", "INTEGER", not_null=True)
        classes.add_timestamps()
        classes.add_audit_columns()
        classes.add_status_column()
        classes.add_foreign_key("school_id", "schools")
        classes.add_index(["school_id", "name"], unique=True)
        self.tables["classes"] = classes
        
        # Sections table
        sections = TableSchema("sections", "Class sections")
        sections.add_primary_key()
        sections.add_column("name", "TEXT", not_null=True)
        sections.add_column("class_id", "INTEGER", not_null=True)
        sections.add_column("capacity", "INTEGER")
        sections.add_column("teacher_id", "INTEGER")
        sections.add_timestamps()
        sections.add_audit_columns()
        sections.add_status_column()
        sections.add_foreign_key("class_id", "classes")
        sections.add_index(["class_id", "name"], unique=True)
        self.tables["sections"] = sections
        
        # Students table
        students = TableSchema("students", "Student records")
        students.add_primary_key()
        students.add_column("name", "TEXT", not_null=True)
        students.add_column("registration_number", "TEXT")
        students.add_column("gender", "TEXT")
        students.add_column("date_of_birth", "DATE")
        students.add_column("phone", "TEXT")
        students.add_column("email", "TEXT")
        students.add_column("address", "TEXT")
        students.add_column("father_name", "TEXT")
        students.add_column("mother_name", "TEXT")
        students.add_column("admission_date", "DATE")
        students.add_column("blood_group", "TEXT")
        students.add_column("photo_path", "TEXT")
        students.add_column("school_id", "INTEGER", not_null=True)
        students.add_column("class_id", "INTEGER", not_null=True)
        students.add_column("section_id", "INTEGER")
        students.add_timestamps()
        students.add_audit_columns()
        students.add_status_column()
        students.add_foreign_key("school_id", "schools")
        students.add_foreign_key("class_id", "classes")
        students.add_foreign_key("section_id", "sections", on_delete="SET NULL")
        students.add_index(["school_id", "registration_number"], unique=True)
        students.add_index(["class_id"])
        students.add_index(["section_id"])
        students.add_index(["name"])
        self.tables["students"] = students
        
        # Define more tables as needed...
        
        # Users table
        users = TableSchema("users", "System users")
        users.add_primary_key()
        users.add_column("username", "TEXT", not_null=True, unique=True)
        users.add_column("password_hash", "TEXT", not_null=True)
        users.add_column("full_name", "TEXT")
        users.add_column("email", "TEXT")
        users.add_column("role", "TEXT", not_null=True)
        users.add_column("last_login", "TIMESTAMP")
        users.add_column("failed_login_attempts", "INTEGER", default="0")
        users.add_column("locked_until", "TIMESTAMP")
        users.add_timestamps()
        users.add_status_column()
        users.add_index(["username"], unique=True)
        users.add_index(["email"])
        self.tables["users"] = users
        
        return self
    
    def create_all_tables(self):
        """Create all defined tables in the database."""
        try:
            with self.conn:
                # Enable foreign keys
                self.cursor.execute("PRAGMA foreign_keys = ON")
                
                # Create each table
                for table_name, table_schema in self.tables.items():
                    logger.info(f"Creating table: {table_name}")
                    create_statement = table_schema.get_create_statement()
                    self.cursor.execute(create_statement)
                    
                    # Create indexes
                    for idx_stmt in table_schema.get_index_statements():
                        self.cursor.execute(idx_stmt)
                
                logger.info("All tables created successfully")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            return False
            
    def create_triggers(self):
        """Create database triggers for auditing and timestamps."""
        try:
            with self.conn:
                # Create updated_at trigger for each table with timestamps
                for table_name, table_schema in self.tables.items():
                    # Check if table has updated_at column
                    has_updated_at = any(col["name"] == "updated_at" for col in table_schema.columns)
                    
                    if has_updated_at:
                        # Create trigger to update the updated_at column
                        trigger_stmt = f"""
                        CREATE TRIGGER IF NOT EXISTS trg_{table_name}_updated_at
                        AFTER UPDATE ON {table_name}
                        BEGIN
                            UPDATE {table_name} SET updated_at = CURRENT_TIMESTAMP
                            WHERE id = NEW.id;
                        END;
                        """
                        self.cursor.execute(trigger_stmt)
                        
                logger.info("All triggers created successfully")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error creating triggers: {e}")
            return False
    
    def get_table_info(self, table_name):
        """Get information about a table's columns."""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting table info: {e}")
            return []
            
    def check_schema_matches(self) -> bool:
        """
        Check if the current database schema matches the defined schema.
        
        Returns:
            bool: True if schema matches, False otherwise
        """
        try:
            # Get list of tables in the database
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = set(row[0] for row in self.cursor.fetchall())
            
            # Check if all defined tables exist
            defined_tables = set(self.tables.keys())
            if not defined_tables.issubset(existing_tables):
                logger.warning("Missing tables in database")
                return False
            
            # Check each table's columns
            for table_name, table_schema in self.tables.items():
                if table_name not in existing_tables:
                    continue
                
                # Get existing columns
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = {row[1]: row for row in self.cursor.fetchall()}
                
                # Check if all defined columns exist
                defined_columns = {col["name"] for col in table_schema.columns}
                if not defined_columns.issubset(existing_columns.keys()):
                    logger.warning(f"Missing columns in table {table_name}")
                    return False
            
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error checking schema: {e}")
            return False
