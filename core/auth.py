"""Authentication and authorization system."""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal
from config.security import PasswordHasher, JWTManager, SecurityConfig
from models.database import Database

logger = logging.getLogger(__name__)

class User:
    """User model."""
    
    def __init__(self, user_id: int, username: str, email: str, role: str, 
                 full_name: str = "", is_active: bool = True, last_login: datetime = None):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.full_name = full_name
        self.is_active = is_active
        self.last_login = last_login
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        from config.settings import USER_ROLES
        role_permissions = USER_ROLES.get(self.role, {}).get('permissions', [])
        return permission in role_permissions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class AuthenticationManager(QObject):
    """Handles user authentication and session management."""
    
    # Signals
    user_logged_in = pyqtSignal(object)  # User object
    user_logged_out = pyqtSignal()
    login_failed = pyqtSignal(str)  # Error message
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user: Optional[User] = None
        self.session_token: Optional[str] = None
        self.login_attempts: Dict[str, Dict] = {}
        self._create_users_table()
    
    def _create_users_table(self):
        """Create users table if it doesn't exist."""
        try:
            self.db.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                full_name TEXT,
                phone TEXT,
                organization TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )''')
            
            # Add new columns if they don't exist (for existing databases)
            try:
                self.db.cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
            except:
                pass  # Column already exists
                
            try:
                self.db.cursor.execute('ALTER TABLE users ADD COLUMN organization TEXT')
            except:
                pass  # Column already exists
            
            # Session tracking table
            self.db.cursor.execute('''CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')
            
            self.db.conn.commit()
            logger.info("User authentication tables created successfully")
        except Exception as e:
            logger.error(f"Error creating user tables: {e}")
            raise

    def login(self, username: str, password: str) -> bool:
        """Authenticate user and create session."""
        try:
            # Check if account is locked
            if self._is_account_locked(username):
                remaining_time = self._get_lockout_remaining_time(username)
                self.login_failed.emit(f"Account locked. Try again in {remaining_time} minutes.")
                return False
            
            # Get user from database
            self.db.cursor.execute("""
                SELECT id, username, email, password_hash, role, full_name, is_active, last_login
                FROM users WHERE username = ? AND is_active = 1
            """, (username,))
            
            user_data = self.db.cursor.fetchone()
            
            if not user_data:
                self._record_failed_attempt(username)
                self.login_failed.emit("Invalid username or password.")
                return False
            
            # Verify password
            if not PasswordHasher.verify_password(password, user_data[3]):
                self._record_failed_attempt(username)
                self.login_failed.emit("Invalid username or password.")
                return False
            
            # Create user object
            self.current_user = User(
                user_id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                role=user_data[4],
                full_name=user_data[5] or "",
                last_login=datetime.fromisoformat(user_data[7]) if user_data[7] else None
            )
            
            # Create session token
            self.session_token = JWTManager.create_token(self.current_user.id, self.current_user.role)
            
            # Update last login and reset failed attempts
            self._update_last_login(self.current_user.id)
            self._reset_failed_attempts(username)
            
            # Store session in database
            self._store_session(self.current_user.id, self.session_token)
            
            logger.info(f"User {username} logged in successfully")
            self.user_logged_in.emit(self.current_user)
            return True
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.login_failed.emit("Login system error. Please try again.")
            return False
    
    def logout(self):
        """Log out current user and invalidate session."""
        try:
            if self.session_token:
                # Invalidate session in database
                self.db.cursor.execute("""
                    UPDATE user_sessions SET is_active = 0 
                    WHERE token = ?
                """, (self.session_token,))
                self.db.conn.commit()
            
            if self.current_user:
                logger.info(f"User {self.current_user.username} logged out")
            
            self.current_user = None
            self.session_token = None
            self.user_logged_out.emit()
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.current_user is not None and self.session_token is not None
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission."""
        if not self.current_user:
            return False
        return self.current_user.has_permission(permission)
    
    def create_user(self, username: str, password: str, role: str, 
                   full_name: str = "", email: str = "", phone: str = "", 
                   organization: str = "") -> bool:
        """Create a new user account."""
        try:
            # Check if username already exists
            if self.user_exists(username):
                return False
                
            # Hash password
            password_hash = PasswordHasher.hash_password(password)
            
            # Insert new user
            self.db.cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, full_name, phone, organization)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, role, full_name, phone, organization))
            
            self.db.conn.commit()
            logger.info(f"User {username} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False
    
    def user_exists(self, username: str) -> bool:
        """Check if a username already exists."""
        try:
            self.db.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            return self.db.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if user exists: {e}")
            return False
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is currently locked."""
        try:
            self.db.cursor.execute("""
                SELECT locked_until FROM users WHERE username = ?
            """, (username,))
            
            result = self.db.cursor.fetchone()
            if not result or not result[0]:
                return False
            
            locked_until = datetime.fromisoformat(result[0])
            return datetime.now() < locked_until
            
        except Exception as e:
            logger.error(f"Error checking account lock status: {e}")
            return False
    
    def _get_lockout_remaining_time(self, username: str) -> int:
        """Get remaining lockout time in minutes."""
        try:
            self.db.cursor.execute("""
                SELECT locked_until FROM users WHERE username = ?
            """, (username,))
            
            result = self.db.cursor.fetchone()
            if result and result[0]:
                locked_until = datetime.fromisoformat(result[0])
                remaining = locked_until - datetime.now()
                return max(0, int(remaining.total_seconds() / 60))
            
            return 0
        except Exception:
            return 0
    
    def _record_failed_attempt(self, username: str):
        """Record failed login attempt."""
        try:
            self.db.cursor.execute("""
                UPDATE users SET failed_login_attempts = failed_login_attempts + 1
                WHERE username = ?
            """, (username,))
            
            # Check if we need to lock the account
            self.db.cursor.execute("""
                SELECT failed_login_attempts FROM users WHERE username = ?
            """, (username,))
            
            result = self.db.cursor.fetchone()
            if result and result[0] >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
                # Lock account
                lockout_until = datetime.now() + timedelta(minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES)
                self.db.cursor.execute("""
                    UPDATE users SET locked_until = ? WHERE username = ?
                """, (lockout_until.isoformat(), username))
            
            self.db.conn.commit()
            
        except Exception as e:
            logger.error(f"Error recording failed attempt: {e}")
    
    def _reset_failed_attempts(self, username: str):
        """Reset failed login attempts."""
        try:
            self.db.cursor.execute("""
                UPDATE users SET failed_login_attempts = 0, locked_until = NULL
                WHERE username = ?
            """, (username,))
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Error resetting failed attempts: {e}")
    
    def _update_last_login(self, user_id: int):
        """Update user's last login timestamp."""
        try:
            self.db.cursor.execute("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (datetime.now().isoformat(), user_id))
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
    
    def _store_session(self, user_id: int, token: str):
        """Store session token in database."""
        try:
            expires_at = datetime.now() + timedelta(hours=SecurityConfig.JWT_EXPIRATION_HOURS)
            self.db.cursor.execute("""
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, token, expires_at.isoformat()))
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Error storing session: {e}")

class PermissionDecorator:
    """Decorator for checking user permissions."""
    
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            from core.auth import get_current_user
            user = get_current_user()
            if not user or not user.has_permission(self.required_permission):
                raise PermissionError(f"Permission '{self.required_permission}' required")
            return func(*args, **kwargs)
        return wrapper

# Global authentication manager instance
_auth_manager = None

def get_auth_manager() -> AuthenticationManager:
    """Get global authentication manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager

def get_current_user() -> Optional[User]:
    """Get currently authenticated user."""
    return get_auth_manager().current_user

def require_permission(permission: str):
    """Decorator for requiring specific permission."""
    return PermissionDecorator(permission)
