# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import os

project_dir = os.path.abspath(os.path.dirname(__file__))

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        ('app_icon.ico', '.'),
        ('icon.png', '.'),
    ],
    hiddenimports=[
        'openpyxl',
        'openpyxl.styles',
        'tkcalendar',
        'babel',
        'babel.numbers',
        'sqlite3',
    ],
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
    name='IT_Error_Logger_v2',
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
    icon='app_icon.ico',
)
