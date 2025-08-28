"""Run the School Management System application."""
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import and run the application
from main import main

if __name__ == "__main__":
    main()
