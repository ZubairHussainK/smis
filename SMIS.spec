# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Get the directory of this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Import PyInstaller hooks
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all PyQt5 data, binaries, and hidden imports
PyQt5_datas, PyQt5_binaries, PyQt5_hiddenimports = collect_all('PyQt5')

# Add explicit PyQt5 .pyd files to binaries
import PyQt5
pyqt5_path = os.path.dirname(PyQt5.__file__)
for file in os.listdir(pyqt5_path):
    if file.endswith('.pyd'):
        PyQt5_binaries.append((os.path.join(pyqt5_path, file), 'PyQt5'))

# Define all required hidden imports
all_hiddenimports = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.QtSql',
    'PyQt5.Qt',
    'PyQt5.sip',
    'sip',
    'sqlite3',
    'sys',
    'os',
    'json',
    'datetime',
    'logging',
    'traceback',
    'dotenv',
    'typing',
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
    'cryptography',
    'cryptography.fernet',
] + PyQt5_hiddenimports

# Define data files
all_datas = [
    ('resources', 'resources'),
    ('config', 'config'),
    ('app_icon.ico', '.'),
] + PyQt5_datas

a = Analysis(
    ['main.py'],
    pathex=[spec_dir],
    binaries=PyQt5_binaries,
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
    upx=False,
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