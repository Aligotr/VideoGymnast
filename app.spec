# -*- mode: python ; coding: utf-8 -*-
import importlib.util

block_cipher = None


# Получить настройки приложения
spec = importlib.util.spec_from_file_location("config", "src/core/config.py")
config = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(config)  # type: ignore

a = Analysis(  # type: ignore
    ["src\\main.py"],
    pathex=[],
    binaries=[],
    datas=[("resources\\ffmpeg", "resources\\ffmpeg")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)  # type: ignore

exe = EXE(  # type: ignore
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=config.APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(  # type: ignore
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=config.APP_NAME,
)
