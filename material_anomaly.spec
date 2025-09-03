# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add the current directory to the Python path
import os
import sys

# Get the absolute path to the directory containing the spec file
spec_dir = os.path.dirname(os.path.abspath(__file__))

# Add the directory to sys.path if it's not already there
if spec_dir not in sys.path:
    sys.path.append(spec_dir)

a = Analysis(
    ['main.py'],
    pathex=[spec_dir],  # Add the spec directory to the path
    binaries=[],
    datas=[],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'sqlalchemy',
        'mysql.connector',
        'watchdog',
        'tkinter',
        'threading',
        'hashlib',
        'pathlib',
        'subprocess',
        'datetime',
        're',
        'os',
        'sys',
        'time',
        'logging',
        'logging.handlers',
        'mysql.connector.plugins',
        'mysql.connector.plugins.caching_sha2_password',
        'mysql.connector.plugins.mysql_native_password',
        'frame',
        'csb_data_output',
        'rod_blk_output',
        'em_material',
        'df_blk_output',
        'check_table_schemas'
    ],
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
    name='MaterialAnomalyDetector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
