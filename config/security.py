"""Security configuration and utilities."""
import os
import hashlib
import secrets
import bcrypt
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import jwt
from typing import Tuple, List
from config.settings import Config


def _get_or_set_env(key: str, generator) -> str:
    """Get env var or set it (persisting in .env) in development; require in non-dev."""
    val = os.getenv(key)
    if val:
        return val
    # In development, generate and persist for stability across runs
    if Config.ENVIRONMENT == 'development':
        try:
            new_val = generator()
            # Append to .env for persistence
            try:
                with open('.env', 'a') as f:
                    f.write(f"{key}={new_val}\n")
            except Exception:
                pass
            return new_val
        except Exception:
            pass
    # In non-development, require explicit configuration
    raise RuntimeError(f"Missing required secret: {key}. Please set it in your .env or environment.")


class SecurityConfig:
    """Security configuration class."""
    
    # Generate or load encryption key
    SECRET_KEY = _get_or_set_env('SECRET_KEY', lambda: secrets.token_hex(32))
    JWT_SECRET = _get_or_set_env('JWT_SECRET', lambda: secrets.token_hex(32))
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # Password policy
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '60'))
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION_MINUTES = int(os.getenv('LOCKOUT_DURATION_MINUTES', '30'))

class PasswordHasher:
    """Secure password hashing utility."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

class DataEncryption:
    """Data encryption utilities."""
    
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create new one."""
        key_file = os.path.join('config', '.encryption_key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs('config', exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

class JWTManager:
    """JWT token management."""
    
    @staticmethod
    def create_token(user_id: int, role: str) -> str:
        """Create JWT token for user."""
        payload = {
            'user_id': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=SecurityConfig.JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, SecurityConfig.JWT_SECRET, algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SecurityConfig.JWT_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password against security policy."""
    errors: List[str] = []
    
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters long")
    
    if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if SecurityConfig.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    if SecurityConfig.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return (len(errors) == 0, errors)
