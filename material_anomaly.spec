# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frame.py', '.'),
        ('csb_data_output.py', '.'),
        ('rod_blk_output.py', '.'),
        ('em_material.py', '.'),
        ('df_blk_output.py', '.'),
        ('check_table_schemas.py', '.'),
        ('*.pyd', '.'),
        ('*.dll', '.'),
    ],
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
        'mysql.connector.plugins.mysql_native_password'
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
