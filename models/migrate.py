"""
Database migration script for SMIS application.
This script handles database migrations and schema upgrades between versions.

Usage:
    python migrate.py [--version VERSION] [--backup]

Options:
    --version VERSION    Target schema version (defaults to latest)
    --backup            Create a backup before migration
"""

import os
import sys
import logging
import argparse
import sqlite3
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from models.schema_manager import SchemaManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration.log')
    ]
)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Database migration manager for SMIS application."""
    
    MIGRATIONS = {
        '1.0': 'migrate_1_0_to_2_0',
        '2.0': 'migrate_2_0_to_3_0',
        # Add more migrations as needed
    }
    
    LATEST_VERSION = '2.0'  # Current latest schema version
    
    def __init__(self, db_path: str = None):
        """
        Initialize the migration manager.
        
        Args:
            db_path (str): Path to the database file
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            sys.exit(1)
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def get_current_version(self) -> str:
        """
        Get the current schema version from the database.
        
        Returns:
            str: Current schema version
        """
        try:
            # Check if version table exists
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='schema_version'
            """)
            if not self.cursor.fetchone():
                # No version table, assume version 1.0
                logger.info("No schema_version table found, assuming version 1.0")
                return '1.0'
                
            # Get current version
            self.cursor.execute("SELECT version FROM schema_version")
            result = self.cursor.fetchone()
            if result:
                version = result[0]
                logger.info(f"Current schema version: {version}")
                return version
            else:
                # Empty version table, assume version 1.0
                logger.info("Empty schema_version table, assuming version 1.0")
                return '1.0'
                
        except sqlite3.Error as e:
            logger.error(f"Error getting current version: {e}")
            return '1.0'  # Default to oldest version
    
    def set_version(self, version: str):
        """
        Set the schema version in the database.
        
        Args:
            version (str): Schema version to set
        """
        try:
            # Create version table if it doesn't exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if there's an existing version
            self.cursor.execute("SELECT COUNT(*) FROM schema_version")
            if self.cursor.fetchone()[0] > 0:
                # Update existing version
                self.cursor.execute(
                    "UPDATE schema_version SET version = ?, updated_at = CURRENT_TIMESTAMP",
                    (version,)
                )
            else:
                # Insert new version
                self.cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (version,)
                )
            
            self.conn.commit()
            logger.info(f"Schema version set to {version}")
            
        except sqlite3.Error as e:
            logger.error(f"Error setting schema version: {e}")
            self.conn.rollback()
    
    def backup_database(self) -> bool:
        """
        Create a backup of the database before migration.
        
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.db_path}.{timestamp}.bak"
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def migrate(self, target_version: str = None, create_backup: bool = True):
        """
        Migrate the database to the target version.
        
        Args:
            target_version (str): Target schema version
            create_backup (bool): Whether to create a backup before migration
        """
        try:
            # Connect to database
            self.connect()
            
            # Create backup if requested
            if create_backup:
                if not self.backup_database():
                    logger.warning("Migration proceeding without backup")
            
            # Determine current and target versions
            current_version = self.get_current_version()
            target_version = target_version or self.LATEST_VERSION
            
            # Check if migration is needed
            if current_version == target_version:
                logger.info(f"Database already at version {target_version}, no migration needed")
                return
            
            # Check if migration path exists
            if not self._can_migrate(current_version, target_version):
                logger.error(f"No migration path from {current_version} to {target_version}")
                return
            
            # Perform the migration
            logger.info(f"Migrating from version {current_version} to {target_version}")
            
            # Get migration steps
            migration_steps = self._get_migration_steps(current_version, target_version)
            
            # Execute each migration step
            for from_version, to_version in migration_steps:
                method_name = self.MIGRATIONS.get(from_version)
                if method_name and hasattr(self, method_name):
                    logger.info(f"Executing migration step: {from_version} to {to_version}")
                    migration_method = getattr(self, method_name)
                    migration_method()
                else:
                    logger.error(f"Migration method not found for {from_version} to {to_version}")
                    return
            
            # Update schema version
            self.set_version(target_version)
            logger.info(f"Migration to version {target_version} completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.close()
    
    def _can_migrate(self, from_version: str, to_version: str) -> bool:
        """
        Check if migration is possible between versions.
        
        Args:
            from_version (str): Source schema version
            to_version (str): Target schema version
            
        Returns:
            bool: True if migration is possible, False otherwise
        """
        # Get available versions in order
        versions = sorted(list(self.MIGRATIONS.keys()) + [self.LATEST_VERSION])
        
        # Check if both versions exist in the list
        if from_version not in versions or to_version not in versions:
            return False
        
        # Check if target version is newer than current version
        return versions.index(to_version) > versions.index(from_version)
    
    def _get_migration_steps(self, from_version: str, to_version: str) -> List[tuple]:
        """
        Get the migration steps needed to go from source to target version.
        
        Args:
            from_version (str): Source schema version
            to_version (str): Target schema version
            
        Returns:
            List[tuple]: List of migration step tuples (from_version, to_version)
        """
        # Get all versions in order
        versions = sorted(list(self.MIGRATIONS.keys()) + [self.LATEST_VERSION])
        
        # Find indices of source and target versions
        try:
            from_idx = versions.index(from_version)
            to_idx = versions.index(to_version)
        except ValueError:
            logger.error(f"Invalid version: {from_version} or {to_version}")
            return []
        
        # Create migration steps
        steps = []
        for i in range(from_idx, to_idx):
            steps.append((versions[i], versions[i + 1]))
        
        return steps
    
    # Migration methods
    def migrate_1_0_to_2_0(self):
        """Migrate database from version 1.0 to 2.0."""
        try:
            # Begin transaction
            self.conn.execute("BEGIN")
            
            # Example migration steps:
            
            # 1. Add new columns to existing tables
            self.cursor.execute("""
                ALTER TABLE students 
                ADD COLUMN enrollment_date DATE
            """)
            
            self.cursor.execute("""
                ALTER TABLE students 
                ADD COLUMN graduation_date DATE
            """)
            
            # 2. Create new tables
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    attendance_date DATE NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'late', 'excused')),
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                    UNIQUE(student_id, attendance_date)
                )
            """)
            
            # 3. Create indexes for new tables
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_attendance_student 
                ON student_attendance(student_id)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_attendance_date 
                ON student_attendance(attendance_date)
            """)
            
            # Commit changes
            self.conn.commit()
            logger.info("Migration from 1.0 to 2.0 completed")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Migration 1.0 to 2.0 failed: {e}")
            raise
    
    def migrate_2_0_to_3_0(self):
        """Migrate database from version 2.0 to 3.0."""
        # Implement migration logic when needed
        logger.info("Migration from 2.0 to 3.0 not yet implemented")


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(description="SMIS Database Migration Tool")
    parser.add_argument("--version", help="Target schema version")
    parser.add_argument("--backup", action="store_true", help="Create backup before migration")
    args = parser.parse_args()
    
    try:
        # Run migration
        migration = DatabaseMigration()
        migration.migrate(args.version, args.backup)
        
    except KeyboardInterrupt:
        logger.warning("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Migration failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
