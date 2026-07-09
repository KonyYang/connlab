# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


repo_root = Path(SPECPATH).resolve().parent
release_name = os.environ.get("CONNLAB_RELEASE_NAME", "ConnLab_Server")
frontend_dist = repo_root / "frontend" / "dist"
app_icon = repo_root / "packaging" / "assets" / "connlab.ico"

if not (frontend_dist / "index.html").is_file():
    raise SystemExit(f"frontend/dist/index.html not found: {frontend_dist}")
if not app_icon.is_file():
    raise SystemExit(f"release icon not found: {app_icon}")

datas = [
    (str(frontend_dist), "frontend_dist"),
    *collect_data_files(
        "backend.modules.fee_evaluation.seeds",
        includes=["*.json"],
    ),
]

hiddenimports = collect_submodules("backend") + ["backend.desktop.packaged_server"]

a = Analysis(
    [str(repo_root / "backend" / "desktop" / "packaged_server.py")],
    pathex=[str(repo_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name=release_name,
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
    icon=str(app_icon),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=release_name,
)
