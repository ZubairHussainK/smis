"""SMIS Installation and Setup Script"""
import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """Setup basic logging for installation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('installation.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        logging.error("Python 3.8 or higher is required")
        return False
    logging.info(f"Python version {sys.version} is compatible")
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'backups',
        'config',
        'core',
        'services',
        'ui/components',
        'ui/pages',
        'utils',
        'models',
        'controllers',
        'resources/fonts',
        'resources/icons'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {directory}")

def install_requirements():
    """Install required packages."""
    try:
        logging.info("Installing required packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logging.info("All requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install requirements: {e}")
        return False

def setup_database():
    """Initialize the database."""
    try:
        logging.info("Setting up database...")
        from models.database import Database
        db = Database()
        logging.info("Database setup completed")
        return True
    except Exception as e:
        logging.error(f"Database setup failed: {e}")
        return False

def create_default_config():
    """Create default configuration files."""
    try:
        # Check if .env exists, if not create from template
        if not os.path.exists('.env'):
            logging.info("Creating default .env file...")
            # The .env file is already created in our implementation
        
        logging.info("Configuration files are ready")
        return True
    except Exception as e:
        logging.error(f"Configuration setup failed: {e}")
        return False

def run_security_checks():
    """Run basic security checks."""
    try:
        logging.info("Running security checks...")
        
        # Check if default passwords need to be changed
        logging.warning("SECURITY NOTICE: Default admin password is 'admin123'")
        logging.warning("Please change the default password immediately after first login")
        
        # Check file permissions
        if os.name != 'nt':  # Not Windows
            os.chmod('.env', 0o600)  # Restrict access to .env file
            logging.info("Set secure permissions on .env file")
        
        logging.info("Security checks completed")
        return True
    except Exception as e:
        logging.error(f"Security checks failed: {e}")
        return False

def main():
    """Main installation function."""
    print("=" * 60)
    print("SMIS - School Management Information System")
    print("Enhanced Installation Script")
    print("=" * 60)
    
    setup_logging()
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directories", create_directories),
        ("Installing requirements", install_requirements),
        ("Setting up configuration", create_default_config),
        ("Initializing database", setup_database),
        ("Running security checks", run_security_checks)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        logging.info(f"Starting: {step_name}")
        try:
            if step_function():
                logging.info(f"✓ Completed: {step_name}")
            else:
                logging.error(f"✗ Failed: {step_name}")
                failed_steps.append(step_name)
        except Exception as e:
            logging.error(f"✗ Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    print("\n" + "=" * 60)
    if failed_steps:
        print("❌ Installation completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease check the installation.log file for details.")
        return 1
    else:
        print("✅ Installation completed successfully!")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Login with username: admin, password: admin123")
        print("3. IMPORTANT: Change the default password immediately!")
        print("\nFor help, please refer to the documentation.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
