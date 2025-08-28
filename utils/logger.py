"""Enhanced logging configuration for the application."""
import logging
import logging.handlers
import os
import sys
import json
import structlog
from datetime import datetime
from typing import Any, Dict
from config.settings import Config

class SMISLoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter with context information."""
    
    def process(self, msg, kwargs):
        return f"[{self.extra.get('user', 'System')}] {msg}", kwargs

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'action'):
            log_entry['action'] = record.action
        if hasattr(record, 'details'):
            log_entry['details'] = record.details
        
        return json.dumps(log_entry)

def setup_logging():
    """Configure enhanced application logging."""
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set up logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create formatters
    formatter = logging.Formatter(log_format, date_format)
    json_formatter = JSONFormatter()
    
    # Set up file handlers with rotation
    log_file = os.path.join(log_dir, f'sms_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=Config.LOG_FILE_MAX_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    
    # Set up JSON log file for structured logging
    json_log_file = os.path.join(log_dir, f'sms_structured_{datetime.now().strftime("%Y%m%d")}.json')
    json_file_handler = logging.handlers.RotatingFileHandler(
        json_log_file,
        maxBytes=Config.LOG_FILE_MAX_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    json_file_handler.setFormatter(json_formatter)
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Set up error file handler
    error_log_file = os.path.join(log_dir, f'sms_errors_{datetime.now().strftime("%Y%m%d")}.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=Config.LOG_FILE_MAX_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(json_file_handler)
    root_logger.addHandler(error_handler)
    
    # Add console handler only in debug mode
    if Config.DEBUG:
        root_logger.addHandler(console_handler)
    
    # Set up specific loggers
    setup_security_logger()
    setup_audit_logger()
    
    logging.info("Enhanced logging system initialized")

def setup_security_logger():
    """Set up dedicated security event logger."""
    security_logger = logging.getLogger('security')
    
    # Security log file
    security_log_file = os.path.join('logs', f'security_{datetime.now().strftime("%Y%m%d")}.log')
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=Config.LOG_FILE_MAX_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    
    security_formatter = logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    security_handler.setFormatter(security_formatter)
    
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False  # Don't propagate to root logger

def setup_audit_logger():
    """Set up dedicated audit trail logger."""
    if not Config.ENABLE_AUDIT_LOG:
        return
    
    audit_logger = logging.getLogger('audit')
    
    # Audit log file
    audit_log_file = os.path.join('logs', f'audit_{datetime.now().strftime("%Y%m%d")}.log')
    audit_handler = logging.handlers.RotatingFileHandler(
        audit_log_file,
        maxBytes=Config.LOG_FILE_MAX_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    
    audit_formatter = JSONFormatter()
    audit_handler.setFormatter(audit_formatter)
    
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False  # Don't propagate to root logger

def get_logger(name: str, user_context: Dict[str, Any] = None) -> SMISLoggerAdapter:
    """Get logger with user context."""
    logger = logging.getLogger(name)
    context = user_context or {}
    return SMISLoggerAdapter(logger, context)

def log_security_event(event_type: str, user_id: int = None, details: Dict[str, Any] = None):
    """Log security-related events."""
    security_logger = logging.getLogger('security')
    
    message = f"Security Event: {event_type}"
    if user_id:
        message += f" (User ID: {user_id})"
    
    extra_data = {'event_type': event_type}
    if user_id:
        extra_data['user_id'] = user_id
    if details:
        extra_data['details'] = details
    
    security_logger.info(message, extra=extra_data)

def log_audit_event(action: str, user_id: int, resource_type: str, 
                   resource_id: str = None, details: Dict[str, Any] = None):
    """Log audit trail events."""
    if not Config.ENABLE_AUDIT_LOG:
        return
    
    audit_logger = logging.getLogger('audit')
    
    audit_data = {
        'action': action,
        'user_id': user_id,
        'resource_type': resource_type,
        'timestamp': datetime.now().isoformat()
    }
    
    if resource_id:
        audit_data['resource_id'] = resource_id
    if details:
        audit_data['details'] = details
    
    audit_logger.info(f"Audit: {action} on {resource_type}", extra=audit_data)

class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger('performance')
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.logger.info(
            f"Performance: {self.operation_name} completed in {duration:.3f}s",
            extra={
                'operation': self.operation_name,
                'duration_seconds': duration,
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
        )
