"""Custom exceptions for the SMIS application."""
import logging
import sqlite3
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SMISException(Exception):
    """Base exception for SMIS application."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the exception
        logger.error(f"{self.__class__.__name__}: {message}", extra=self.details)

class DatabaseError(SMISException):
    """Database-related errors."""
    pass

class ValidationError(SMISException):
    """Data validation errors."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.value = value
        details = {'field': field}
        if value is not None:
            details['value'] = str(value)
        super().__init__(f"{message}", details)

class AuthenticationError(SMISException):
    """Authentication-related errors."""
    pass

class AuthorizationError(SMISException):
    """Authorization/permission-related errors."""
    pass

class BusinessLogicError(SMISException):
    """Business logic violation errors."""
    pass

class DataIntegrityError(SMISException):
    """Data integrity constraint violations."""
    pass

class BackupError(SMISException):
    """Backup and restore operation errors."""
    pass

class ConfigurationError(SMISException):
    """Configuration-related errors."""
    pass

class ExternalServiceError(SMISException):
    """External service integration errors."""
    pass

class FileOperationError(SMISException):
    """File operation errors."""
    pass

def handle_exception(exception: Exception, context: str = "Unknown") -> SMISException:
    """Convert generic exceptions to SMIS exceptions with context."""
    if isinstance(exception, SMISException):
        return exception
    
    error_message = f"Error in {context}: {str(exception)}"
    details = {
        'context': context,
        'original_exception': type(exception).__name__,
        'original_message': str(exception)
    }
    
    # Map common exceptions to SMIS exceptions
    if isinstance(exception, (sqlite3.Error, sqlite3.DatabaseError)):
        return DatabaseError(error_message, details)
    elif isinstance(exception, ValueError):
        return ValidationError("unknown", error_message)
    elif isinstance(exception, PermissionError):
        return AuthorizationError(error_message, details)
    elif isinstance(exception, FileNotFoundError):
        return FileOperationError(error_message, details)
    else:
        return SMISException(error_message, details)
