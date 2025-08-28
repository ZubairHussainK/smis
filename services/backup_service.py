"""Automated backup and recovery service."""
import os
import shutil
import sqlite3
import logging
import zipfile
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import List, Optional
from config.settings import Config
from config.security import DataEncryption
from core.exceptions import BackupError

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages database backups and recovery operations."""
    
    def __init__(self):
        self.backup_dir = Config.DATABASE_BACKUP_PATH
        self.encryption = DataEncryption() if Config.ENCRYPTION_ENABLED else None
        self.backup_thread = None
        self.running = False
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self):
        """Ensure backup directory exists."""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            logger.info(f"Backup directory ensured: {self.backup_dir}")
        except Exception as e:
            raise BackupError(f"Failed to create backup directory: {e}")
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create a database backup."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_name or f"backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, f"{backup_name}.db")
            
            # Create backup using sqlite3 backup API
            source_conn = sqlite3.connect(Config.DATABASE_PATH)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            # Create compressed backup with metadata
            compressed_backup_path = self._create_compressed_backup(backup_path, backup_name)
            
            # Remove uncompressed backup
            os.remove(backup_path)
            
            # Encrypt backup if encryption is enabled
            if self.encryption:
                encrypted_path = self._encrypt_backup(compressed_backup_path)
                os.remove(compressed_backup_path)
                compressed_backup_path = encrypted_path
            
            # Create backup metadata
            self._create_backup_metadata(compressed_backup_path, backup_name)
            
            logger.info(f"Backup created successfully: {compressed_backup_path}")
            return compressed_backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise BackupError(f"Failed to create backup: {e}")
    
    def _create_compressed_backup(self, backup_path: str, backup_name: str) -> str:
        """Create compressed backup with additional files."""
        compressed_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        
        try:
            with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database backup
                zipf.write(backup_path, os.path.basename(backup_path))
                
                # Add configuration files if they exist
                config_files = ['config/settings.py', 'config/security.py']
                for config_file in config_files:
                    if os.path.exists(config_file):
                        zipf.write(config_file, config_file)
                
                # Add recent logs
                self._add_recent_logs_to_backup(zipf)
            
            return compressed_path
        except Exception as e:
            raise BackupError(f"Failed to compress backup: {e}")
    
    def _add_recent_logs_to_backup(self, zipf: zipfile.ZipFile):
        """Add recent log files to backup."""
        try:
            log_dir = 'logs'
            if os.path.exists(log_dir):
                recent_logs = self._get_recent_log_files()
                for log_file in recent_logs:
                    if os.path.exists(log_file):
                        zipf.write(log_file, log_file)
        except Exception as e:
            logger.warning(f"Failed to add logs to backup: {e}")
    
    def _get_recent_log_files(self) -> List[str]:
        """Get list of recent log files."""
        log_files = []
        log_dir = 'logs'
        
        if not os.path.exists(log_dir):
            return log_files
        
        # Get log files from last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            if os.path.isfile(file_path):
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_modified > cutoff_date:
                    log_files.append(file_path)
        
        return log_files
    
    def _encrypt_backup(self, backup_path: str) -> str:
        """Encrypt backup file."""
        try:
            with open(backup_path, 'rb') as f:
                backup_data = f.read()
            
            encrypted_data = self.encryption.cipher.encrypt(backup_data)
            
            encrypted_path = backup_path + '.enc'
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            return encrypted_path
        except Exception as e:
            raise BackupError(f"Failed to encrypt backup: {e}")
    
    def _create_backup_metadata(self, backup_path: str, backup_name: str):
        """Create metadata file for backup."""
        try:
            metadata = {
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'database_path': Config.DATABASE_PATH,
                'backup_path': backup_path,
                'encrypted': self.encryption is not None,
                'compressed': True,
                'version': '1.0'
            }
            
            metadata_path = backup_path + '.meta'
            with open(metadata_path, 'w') as f:
                import json
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            logger.warning(f"Failed to create backup metadata: {e}")
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            if not os.path.exists(backup_path):
                raise BackupError(f"Backup file not found: {backup_path}")
            
            # Create backup of current database before restore
            current_backup = self.create_backup("pre_restore_backup")
            logger.info(f"Current database backed up to: {current_backup}")
            
            # Decrypt if necessary
            if backup_path.endswith('.enc'):
                backup_path = self._decrypt_backup(backup_path)
            
            # Extract if compressed
            if backup_path.endswith('.zip'):
                backup_path = self._extract_backup(backup_path)
            
            # Restore database
            if os.path.exists(Config.DATABASE_PATH):
                os.remove(Config.DATABASE_PATH)
            
            shutil.copy2(backup_path, Config.DATABASE_PATH)
            
            # Verify restored database
            if self._verify_database_integrity():
                logger.info(f"Database restored successfully from: {backup_path}")
                return True
            else:
                raise BackupError("Restored database failed integrity check")
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise BackupError(f"Failed to restore backup: {e}")
    
    def _decrypt_backup(self, encrypted_path: str) -> str:
        """Decrypt backup file."""
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.encryption.cipher.decrypt(encrypted_data)
            
            decrypted_path = encrypted_path.replace('.enc', '')
            with open(decrypted_path, 'wb') as f:
                f.write(decrypted_data)
            
            return decrypted_path
        except Exception as e:
            raise BackupError(f"Failed to decrypt backup: {e}")
    
    def _extract_backup(self, zip_path: str) -> str:
        """Extract database from compressed backup."""
        try:
            extract_dir = os.path.join(self.backup_dir, 'temp_extract')
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Find the database file
            for filename in os.listdir(extract_dir):
                if filename.endswith('.db'):
                    return os.path.join(extract_dir, filename)
            
            raise BackupError("No database file found in backup")
            
        except Exception as e:
            raise BackupError(f"Failed to extract backup: {e}")
    
    def _verify_database_integrity(self) -> bool:
        """Verify database integrity after restore."""
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] == 'ok'
            
        except Exception as e:
            logger.error(f"Database integrity check failed: {e}")
            return False
    
    def list_backups(self) -> List[dict]:
        """List available backups with metadata."""
        backups = []
        
        try:
            if not os.path.exists(self.backup_dir):
                return backups
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith(('.zip', '.zip.enc')):
                    backup_path = os.path.join(self.backup_dir, filename)
                    metadata_path = backup_path + '.meta'
                    
                    backup_info = {
                        'filename': filename,
                        'path': backup_path,
                        'size': os.path.getsize(backup_path),
                        'created': datetime.fromtimestamp(os.path.getctime(backup_path))
                    }
                    
                    # Load metadata if available
                    if os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, 'r') as f:
                                import json
                                metadata = json.load(f)
                                backup_info.update(metadata)
                        except Exception:
                            pass
                    
                    backups.append(backup_info)
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
        
        return backups
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove backups older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            removed_count = 0
            
            for backup in self.list_backups():
                if backup['created'] < cutoff_date:
                    try:
                        os.remove(backup['path'])
                        # Remove metadata file if exists
                        metadata_path = backup['path'] + '.meta'
                        if os.path.exists(metadata_path):
                            os.remove(metadata_path)
                        removed_count += 1
                        logger.info(f"Removed old backup: {backup['filename']}")
                    except Exception as e:
                        logger.warning(f"Failed to remove backup {backup['filename']}: {e}")
            
            logger.info(f"Cleanup completed. Removed {removed_count} old backups.")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def start_scheduled_backups(self):
        """Start automated backup schedule."""
        if Config.AUTO_BACKUP:
            schedule.every(Config.BACKUP_INTERVAL_HOURS).hours.do(self._scheduled_backup)
            
            self.running = True
            self.backup_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.backup_thread.start()
            
            logger.info(f"Scheduled backups started (every {Config.BACKUP_INTERVAL_HOURS} hours)")
    
    def stop_scheduled_backups(self):
        """Stop automated backup schedule."""
        self.running = False
        schedule.clear()
        logger.info("Scheduled backups stopped")
    
    def _scheduled_backup(self):
        """Create scheduled backup."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"scheduled_backup_{timestamp}"
            self.create_backup(backup_name)
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Scheduled backup failed: {e}")
    
    def _run_scheduler(self):
        """Run the backup scheduler in background thread."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Global backup manager instance
_backup_manager = None

def get_backup_manager() -> BackupManager:
    """Get global backup manager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
