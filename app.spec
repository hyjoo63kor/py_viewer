# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Image & Document Viewer."""

a = Analysis(
    ["src/my_app/main.py"],
    pathex=[],
    binaries=[],
    datas=[("resources/icon.svg", "resources")],
    hiddenimports=["PySide6", "fitz"],
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
    name="SvgViewer",
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
)
