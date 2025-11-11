# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

datas = [
    ('data/scenario/*.ks', 'data/scenario'),
    ('data/scenario/system/*.ks', 'data/scenario/system'),
    ('data/others/*.js', 'data/others'),
    ('tyrano/lang.js', 'tyrano'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'asar',
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
    [],
    exclude_binaries=True, 
    name='DevilConnection-Patcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DevilConnection-Patcher',
)

app = BUNDLE(
    coll,
    name='DevilConnection-Patcher.app',
    icon=None, 
    bundle_identifier='com.nyabi.devilconnection.patcher',
)