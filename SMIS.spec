# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Get the directory of this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Import PyInstaller hooks
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

# Collect ALL PyQt5 related modules, data, and binaries
print("Collecting PyQt5 modules...")
PyQt5_datas, PyQt5_binaries, PyQt5_hiddenimports = collect_all('PyQt5')

# Also collect PyQt5-Qt5 and PyQt5-sip
try:
    qt5_datas, qt5_binaries, qt5_hiddenimports = collect_all('PyQt5-Qt5')
    PyQt5_datas.extend(qt5_datas)
    PyQt5_binaries.extend(qt5_binaries)
    PyQt5_hiddenimports.extend(qt5_hiddenimports)
except:
    pass

try:
    sip_datas, sip_binaries, sip_hiddenimports = collect_all('PyQt5-sip')
    PyQt5_datas.extend(sip_datas)
    PyQt5_binaries.extend(sip_binaries)
    PyQt5_hiddenimports.extend(sip_hiddenimports)
except:
    pass

# Add all PyQt5 submodules explicitly
PyQt5_submodules = collect_submodules('PyQt5')
PyQt5_hiddenimports.extend(PyQt5_submodules)

# Get PyQt5 path and add ALL files as binaries
import PyQt5
pyqt5_path = os.path.dirname(PyQt5.__file__)
print(f"PyQt5 path: {pyqt5_path}")

# Add all .pyd files explicitly as binaries to root PyQt5 folder
for file in os.listdir(pyqt5_path):
    if file.endswith('.pyd') or file.endswith('.dll'):
        source_path = os.path.join(pyqt5_path, file)
        PyQt5_binaries.append((source_path, 'PyQt5'))
        print(f"Adding binary: {file}")

# Also check for Qt5 folder and add those files
qt5_folder = os.path.join(os.path.dirname(pyqt5_path), 'PyQt5-Qt5', 'PyQt5', 'Qt5')
if os.path.exists(qt5_folder):
    for root, dirs, files in os.walk(qt5_folder):
        for file in files:
            if file.endswith('.dll'):
                source_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, qt5_folder)
                dest_path = os.path.join('PyQt5', 'Qt5', rel_path) if rel_path != '.' else 'PyQt5/Qt5'
                PyQt5_binaries.append((source_path, dest_path))
                print(f"Adding Qt5 DLL: {file}")

print(f"Total PyQt5 binaries: {len(PyQt5_binaries)}")
print(f"Total PyQt5 hidden imports: {len(PyQt5_hiddenimports)}")

# Define all required hidden imports - be very explicit
all_hiddenimports = [
    # Core PyQt5 modules
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.QtSql',
    'PyQt5.Qt',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtNetwork',
    'PyQt5.sip',
    
    # SIP modules  
    'sip',
    'PyQt5-sip',
    
    # System modules
    'sqlite3',
    'sys',
    'os',
    'json',
    'datetime',
    'logging',
    'traceback',
    'threading',
    'webbrowser',
    'urllib.request',
    'urllib.parse', 
    'urllib.error',
    'zipfile',
    'tempfile',
    'shutil',
    'subprocess',
    'hashlib',
    'base64',
    'typing',
    
    # Security modules
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.backends',
    
    # Optional modules
    'dotenv',
] + PyQt5_hiddenimports  # Add all collected PyQt5 hidden imports

# Remove duplicates
all_hiddenimports = list(set(all_hiddenimports))
print(f"Total hidden imports: {len(all_hiddenimports)}")

# Define data files - make sure we include everything
all_datas = [
    ('resources', 'resources'),
    ('config', 'config'),
    ('app_icon.ico', '.'),
] + PyQt5_datas  # Add all collected PyQt5 data files

print(f"Total data files: {len(all_datas)}")
print(f"Total binary files: {len(PyQt5_binaries)}")

a = Analysis(
    ['main.py'],
    pathex=[spec_dir],
    binaries=PyQt5_binaries,  # Use all collected PyQt5 binaries
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SMIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid corruption
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_dir, 'app_icon.ico')
)