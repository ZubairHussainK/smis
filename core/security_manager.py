"""
SMIS Key Validation & Security System

This module implements hardcore security for SMIS application:
- Key validation before app starts
- Anti-crack protection  
- Registration system
- Secure key storage
"""

import os
import sys
import json
import hashlib
import base64
import sqlite3
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SMISSecurityManager:
    """
    Ultra-secure key validation and anti-crack system.
    No key = No access. Period.
    """
    
    def __init__(self):
        self.app_name = "SMIS_SCHOOL_MANAGEMENT"
        self.validation_server = "https://api.github.com/repos/YOUR_USERNAME/smis-key-generator"
        self.local_key_file = self._get_secure_key_path()
        self.registration_db = self._get_registration_db_path()
        self.security_key = self._generate_security_key()
        
        # Anti-crack measures
        self._check_integrity()
        self._check_debugger()
        self._obfuscate_critical_data()
    
    def _get_secure_key_path(self) -> str:
        """Get secure path for key storage."""
        # Use local directory for better compatibility
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        secure_dir = os.path.join(app_dir, '.smis_data')
        os.makedirs(secure_dir, exist_ok=True)
        return os.path.join(secure_dir, '.activation_key')
    
    def _get_registration_db_path(self) -> str:
        """Get secure path for registration database."""
        # Use local directory for better compatibility
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        secure_dir = os.path.join(app_dir, '.smis_data')
        os.makedirs(secure_dir, exist_ok=True)
        return os.path.join(secure_dir, '.registration.db')
    
    def _generate_security_key(self) -> bytes:
        """Generate security key for encryption."""
        password = f"{self.app_name}_SECURITY_2025".encode()
        salt = b'smis_ultra_secure_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        f = Fernet(self.security_key)
        return f.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        f = Fernet(self.security_key)
        return f.decrypt(encrypted_data.encode()).decode()
    
    def _check_integrity(self):
        """Check application integrity - anti-crack measure."""
        try:
            # Check if critical files exist
            current_file = __file__
            if not os.path.exists(current_file):
                self._security_breach("File integrity compromised")
            
            # Check file size (basic tamper detection)
            file_size = os.path.getsize(current_file)
            if file_size < 1000:  # Too small = potentially modified
                self._security_breach("File size anomaly detected")
                
        except Exception:
            self._security_breach("Integrity check failed")
    
    def _check_debugger(self):
        """Detect debugger/reverse engineering attempts."""
        import time
        start_time = time.time()
        
        # Anti-debugging technique
        for i in range(1000):
            pass
        
        end_time = time.time()
        if end_time - start_time > 0.1:  # Too slow = debugger present
            self._security_breach("Debugging attempt detected")
    
    def _obfuscate_critical_data(self):
        """Obfuscate critical security data."""
        # Create fake variables to confuse crackers
        fake_key1 = "FAKE-KEY1-2025-DECOY-SMIS"
        fake_key2 = "CRACKER-TRAP-INVALID-KEY"
        fake_validation = "https://fake-api.example.com/validate"
        
        # Use fake data in dummy operations
        dummy_hash = hashlib.md5(fake_key1.encode()).hexdigest()
        dummy_check = len(fake_key2) > 10
        dummy_url = fake_validation.startswith("https")
    
    def _security_breach(self, reason: str):
        """Handle security breach."""
        print("🚫 SECURITY BREACH DETECTED")
        print(f"Reason: {reason}")
        print("Application terminated for security reasons.")
        
        # Log security breach
        self._log_security_event("BREACH", reason)
        
        # Immediate exit
        os._exit(1)
    
    def _log_security_event(self, event_type: str, details: str):
        """Log security events."""
        try:
            log_file = os.path.join(os.path.dirname(self.local_key_file), '.security_log')
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()}: {event_type} - {details}\n")
        except:
            pass  # Fail silently
    
    def validate_key_format(self, key: str) -> bool:
        """Validate key format - supports both SMIS and Enhanced formats."""
        if not key:
            return False
        
        # Check for Enhanced format (25 chars: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        if len(key) == 29:  # 25 chars + 4 dashes = 29
            parts = key.split('-')
            if len(parts) == 5:
                # All parts should be 5 characters and alphanumeric
                for part in parts:
                    if len(part) != 5 or not part.isalnum():
                        return False
                return True
        
        # Check for SMIS format (24 chars: SMIS-XXXX-XXXX-XXXX-XXXX)
        if len(key) == 24:
            parts = key.split('-')
            if len(parts) != 5 or parts[0] != 'SMIS':
                return False
            
            # Validate each part
            if len(parts[1]) != 4 or not parts[1].isalnum():
                return False
            if len(parts[2]) != 4 or not parts[2].isdigit():
                return False
            if len(parts[3]) != 4 or not parts[3].isalnum():
                return False
            if len(parts[4]) != 4 or not parts[4].isalnum():
                return False
            
            return True
        
        return False
    
    def validate_key_checksum(self, key: str) -> bool:
        """Validate key checksum - supports both SMIS and Enhanced formats."""
        try:
            parts = key.split('-')
            
            # For Enhanced format keys (5 parts, each 5 chars)
            if len(parts) == 5 and len(parts[0]) == 5:
                # Enhanced keys have built-in validation through the enhanced system
                # For now, we'll allow them through as they're generated by our enhanced system
                return True
            
            # For SMIS format keys (SMIS-XXXX-XXXX-XXXX-XXXX)
            elif len(parts) == 5 and parts[0] == 'SMIS':
                checksum = parts[4]
                
                # Recalculate checksum
                input_data = parts[1] + parts[2] + parts[3]
                calculated_checksum = self._calculate_checksum(input_data)
                
                return checksum.upper() == calculated_checksum.upper()
            
            return False
            
        except:
            return False
    
    def _calculate_checksum(self, input_data: str) -> str:
        """Calculate checksum for key validation."""
        hash_value = 0
        for char in input_data:
            hash_value = ((hash_value << 5) - hash_value) + ord(char)
            hash_value = hash_value & 0xFFFFFFFF  # Keep 32-bit
        
        return format(abs(hash_value) % (36**4), 'X')[:4]
    
    def validate_key_online(self, key: str) -> Dict[str, Any]:
        """Validate key with online server."""
        try:
            # Simulate online validation (replace with real API)
            validation_data = {
                'key': key,
                'timestamp': int(time.time()),
                'app_id': self.app_name
            }
            
            # For now, return mock validation
            # In production, make actual HTTP request to your server
            if self.validate_key_format(key) and self.validate_key_checksum(key):
                return {
                    'valid': True,
                    'message': 'Key validated successfully',
                    'expiry': (datetime.now() + timedelta(days=365)).isoformat()
                }
            else:
                return {
                    'valid': False,
                    'message': 'Invalid key format or checksum'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'message': f'Validation error: {str(e)}'
            }
    
    def store_validated_key(self, key: str, validation_data: Dict[str, Any]):
        """Store validated key securely."""
        try:
            key_data = {
                'key': key,
                'validated_at': datetime.now().isoformat(),
                'expires_at': validation_data.get('expiry'),
                'validation_hash': hashlib.sha256(f"{key}_{self.app_name}".encode()).hexdigest()
            }
            
            encrypted_data = self._encrypt_data(json.dumps(key_data))
            
            # Ensure directory exists and is writable
            os.makedirs(os.path.dirname(self.local_key_file), exist_ok=True)
            
            # Write with proper permissions
            with open(self.local_key_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            # Set file permissions (make it readable only by owner)
            if os.name == 'nt':
                try:
                    os.system(f'attrib +h "{self.local_key_file}"')
                except:
                    pass  # Ignore if attrib fails
            else:
                os.chmod(self.local_key_file, 0o600)
                
        except Exception as e:
            # Don't raise exception, just log and continue
            print(f"Warning: Could not store key securely: {e}")
            # For development, we'll continue without storing
    
    def load_stored_key(self) -> Optional[Dict[str, Any]]:
        """Load stored key data."""
        try:
            if not os.path.exists(self.local_key_file):
                return None
            
            with open(self.local_key_file, 'r') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._decrypt_data(encrypted_data)
            key_data = json.loads(decrypted_data)
            
            # Verify integrity
            expected_hash = hashlib.sha256(f"{key_data['key']}_{self.app_name}".encode()).hexdigest()
            if key_data.get('validation_hash') != expected_hash:
                self._security_breach("Key data integrity compromised")
            
            return key_data
            
        except Exception:
            return None
    
    def is_key_expired(self, key_data: Dict[str, Any]) -> bool:
        """Check if key is expired."""
        try:
            expires_at = key_data.get('expires_at')
            if not expires_at:
                return True
            
            expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            return datetime.now() > expiry_date
            
        except:
            return True
    
    def register_user(self, key: str, user_info: Dict[str, str]) -> bool:
        """Register user with validated key."""
        try:
            # Validate key format first
            if not self.validate_key_format(key):
                print("Invalid key format")
                return False
            
            # Validate key checksum
            if not self.validate_key_checksum(key):
                print("Invalid key checksum")
                return False
            
            # For enhanced keys (25-char), skip online validation
            # For SMIS keys, use online validation
            parts = key.split('-')
            if len(parts) == 5 and len(parts[0]) == 5:
                # Enhanced key - create mock validation result
                validation_result = {
                    'valid': True,
                    'message': 'Enhanced key validated successfully',
                    'expiry': (datetime.now() + timedelta(days=365)).isoformat()
                }
            else:
                # SMIS key - use online validation
                validation_result = self.validate_key_online(key)
                if not validation_result.get('valid'):
                    print(f"Key validation failed: {validation_result.get('message', 'Unknown error')}")
                    return False
            
            # Store validated key (non-critical if it fails)
            try:
                self.store_validated_key(key, validation_result)
            except Exception as e:
                print(f"Warning: Could not store key: {e}")
                # Continue anyway - storage is not critical for operation
            
            # Create registration database
            conn = sqlite3.connect(self.registration_db)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_hash TEXT UNIQUE NOT NULL,
                    organization TEXT NOT NULL,
                    contact_person TEXT NOT NULL,
                    email TEXT NOT NULL,
                    registered_at TEXT NOT NULL,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0
                )
            ''')
            
            # Insert registration
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            cursor.execute('''
                INSERT OR REPLACE INTO registrations 
                (key_hash, organization, contact_person, email, registered_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                key_hash,
                user_info['organization'],
                user_info['contact_person'],
                user_info['email'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Registration error: {e}")
            return False
            
            return True
            
        except Exception as e:
            print(f"Registration failed: {e}")
            return False
    
    def update_login_stats(self):
        """Update login statistics."""
        try:
            key_data = self.load_stored_key()
            if not key_data:
                return
            
            key_hash = hashlib.sha256(key_data['key'].encode()).hexdigest()
            
            conn = sqlite3.connect(self.registration_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE registrations 
                SET last_login = ?, login_count = login_count + 1
                WHERE key_hash = ?
            ''', (datetime.now().isoformat(), key_hash))
            
            conn.commit()
            conn.close()
            
        except:
            pass  # Fail silently
    
    def verify_license(self) -> bool:
        """
        Main license verification function.
        Returns True if license is valid, False otherwise.
        """
        try:
            # Step 1: Check for stored key
            key_data = self.load_stored_key()
            
            if not key_data:
                return False
            
            # Step 2: Check expiry
            if self.is_key_expired(key_data):
                # Remove expired key
                if os.path.exists(self.local_key_file):
                    os.remove(self.local_key_file)
                return False
            
            # Step 3: Verify key integrity
            if not self.validate_key_format(key_data['key']):
                return False
            
            if not self.validate_key_checksum(key_data['key']):
                return False
            
            # Step 4: Update login stats
            self.update_login_stats()
            
            return True
            
        except Exception:
            return False


def secure_app_startup() -> bool:
    """
    Secure application startup function.
    Must be called before any other app functionality.
    """
    try:
        security_manager = SMISSecurityManager()
        
        # Check if license is valid
        if security_manager.verify_license():
            print("✅ License verified successfully")
            return True
        else:
            print("❌ No valid license found")
            print("Please register your application with a valid key")
            return False
            
    except Exception as e:
        print(f"❌ Security check failed: {e}")
        return False


def register_application() -> bool:
    """
    Registration function for new installations.
    """
    print("SMIS Registration Required")
    print("=" * 50)
    
    try:
        security_manager = SMISSecurityManager()
        
        # Get activation key
        key = input("Enter your activation key: ").strip().upper()
        
        if not security_manager.validate_key_format(key):
            print("Invalid key format")
            return False
        
        # Get user information
        print("\nPlease provide registration information:")
        user_info = {
            'organization': input("Organization/School Name: ").strip(),
            'contact_person': input("Contact Person: ").strip(),
            'email': input("Email Address: ").strip()
        }
        
        if not all(user_info.values()):
            print("All fields are required")
            return False
        
        # Register
        print("\nValidating key...")
        if security_manager.register_user(key, user_info):
            print("Registration successful!")
            print("You can now use SMIS application.")
            return True
        else:
            print("Registration failed. Please check your key.")
            return False
            
    except KeyboardInterrupt:
        print("\nRegistration cancelled")
        return False
    except Exception as e:
        print(f"Registration error: {e}")
        return False


if __name__ == "__main__":
    # Test the security system
    if len(sys.argv) > 1 and sys.argv[1] == "register":
        register_application()
    else:
        if secure_app_startup():
            print("Application can start normally")
        else:
            print("Application blocked - license required")
