#!/usr/bin/env python3
"""
Workspace Verification Script
Ensures VS Code workspace is properly configured and clean
"""

import os
import json

def verify_workspace_settings():
    """Verify workspace configuration files."""
    print("🔍 Verifying workspace configuration...")
    
    # Check workspace file
    workspace_file = "SMIS.code-workspace"
    if os.path.exists(workspace_file):
        with open(workspace_file, 'r') as f:
            try:
                workspace_config = json.load(f)
                print("✅ Workspace file exists and is valid JSON")
                
                # Check if exclude patterns are set
                if 'settings' in workspace_config and 'files.exclude' in workspace_config['settings']:
                    excludes = workspace_config['settings']['files.exclude']
                    important_excludes = ['**/test_*.py', '**/debug_*.py', '**/KeyGenerator']
                    all_present = all(pattern in excludes for pattern in important_excludes)
                    
                    if all_present:
                        print("✅ File exclusion patterns properly configured")
                    else:
                        print("⚠️ Some exclusion patterns missing")
                else:
                    print("❌ File exclusion not configured")
                    
            except json.JSONDecodeError:
                print("❌ Workspace file has invalid JSON")
    else:
        print("❌ Workspace file not found")
    
    # Check VS Code settings
    vscode_settings = ".vscode/settings.json"
    if os.path.exists(vscode_settings):
        with open(vscode_settings, 'r') as f:
            try:
                settings = json.load(f)
                print("✅ VS Code settings file exists and is valid JSON")
                
                # Check Python interpreter path
                if 'python.defaultInterpreterPath' in settings:
                    print("✅ Python interpreter path configured")
                else:
                    print("⚠️ Python interpreter path not set")
                    
            except json.JSONDecodeError:
                print("❌ VS Code settings file has invalid JSON")
    else:
        print("❌ VS Code settings file not found")

def check_unwanted_files():
    """Check for unwanted files that should be excluded."""
    print("\n🧹 Checking for unwanted files...")
    
    unwanted_patterns = [
        'test_*.py',
        'debug_*.py', 
        '*_fixed.py',
        'check_*.py',
        'verify_*.py'
    ]
    
    found_unwanted = []
    
    for root, dirs, files in os.walk('.'):
        # Skip .venv and other excluded directories
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.git', 'KeyGenerator']]
        
        for file in files:
            for pattern in unwanted_patterns:
                if pattern.replace('*', '') in file:
                    found_unwanted.append(os.path.join(root, file))
    
    if found_unwanted:
        print(f"⚠️ Found {len(found_unwanted)} unwanted files:")
        for file in found_unwanted[:5]:  # Show first 5
            print(f"   - {file}")
        if len(found_unwanted) > 5:
            print(f"   ... and {len(found_unwanted) - 5} more")
    else:
        print("✅ No unwanted files found")

def verify_core_files():
    """Verify essential application files exist."""
    print("\n📋 Verifying core application files...")
    
    essential_files = [
        'main.py',
        'run.py', 
        'setup.py',
        'ui/pages/attendance.py',
        'ui/pages/student.py',
        'ui/pages/dashboard.py',
        'models/database.py',
        'core/auth.py'
    ]
    
    missing_files = []
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ {len(missing_files)} essential files are missing!")
    else:
        print("\n✅ All essential files present")

if __name__ == "__main__":
    print("🚀 SMIS Workspace Verification")
    print("=" * 40)
    
    verify_workspace_settings()
    check_unwanted_files() 
    verify_core_files()
    
    print("\n" + "=" * 40)
    print("✅ Workspace verification complete!")
    print("\n💡 To ensure clean restarts:")
    print("   1. Close VS Code completely")
    print("   2. Reopen using: code SMIS.code-workspace")
    print("   3. Only essential files will be visible")
