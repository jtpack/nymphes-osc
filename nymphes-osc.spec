# -*- mode: python ; coding: utf-8 -*-

hidden_imports=['zeroconf._utils.ipaddress', 'zeroconf._handlers.answers']

if sys.platform == "win32":
    hidden_imports.append('win32timezone')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('config.txt', '.')],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='nymphes-osc',
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
