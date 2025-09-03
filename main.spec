# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('frame.py', '.'), ('csb_data_output.py', '.'), ('rod_blk_output.py', '.'), ('em_material.py', '.'), ('df_blk_output.py', '.'), ('check_table_schemas.py', '.')],
    hiddenimports=['frame', 'csb_data_output', 'rod_blk_output', 'em_material', 'df_blk_output', 'check_table_schemas', 'mysql.connector.plugins.caching_sha2_password', 'mysql.connector.plugins.mysql_native_password'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
