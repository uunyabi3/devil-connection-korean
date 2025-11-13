# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

datas = [
    ('data/scenario/*.ks', 'data/scenario'),
    ('data/scenario/system/*.ks', 'data/scenario/system'),
    ('data/others/*.js', 'data/others'),
    ('data/others/*.ttf', 'data/others'),
    ('data/others/plugin/backlog/backlog/*.js', 'data/others/plugin/backlog/backlog'),
    ('data/others/plugin/backlog/backlog/*.css', 'data/others/plugin/backlog/backlog'),
    ('data/others/plugin/popopo_chara/*.js', 'data/others/plugin/popopo_chara'),
    ('data/system/*.tjs', 'data/system'),
    ('tyrano/lang.js', 'tyrano'),
    ('tyrano/*.css', 'tyrano'),
    ('tyrano/css/*.css', 'tyrano/css'),
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DevilConnection-Patcher-Windows',
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
