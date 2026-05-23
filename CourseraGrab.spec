# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller build recipe for CourseraGrab.
#
# Build a single-file Windows app with:
#     pyinstaller CourseraGrab.spec
#
# The result is dist/CourseraGrab.exe
#
# Notes:
#   * The icon folder is bundled so the window icon works inside the .exe.
#   * rookiepy ships a compiled (Rust) extension, so we collect everything it
#     needs explicitly.
#   * browser_cookie3 is excluded on purpose - the app authenticates with
#     rookiepy instead, and pulling it in just produces noisy warnings.

from PyInstaller.utils.hooks import collect_all

datas = [('icon', 'icon')]
binaries = []
# download_worker is imported only inside the __main__ guard (worker mode),
# so list it explicitly to guarantee PyInstaller bundles it.
hiddenimports = ['download_worker']

for _pkg in ('rookiepy',):
    _d, _b, _h = collect_all(_pkg)
    datas += _d
    binaries += _b
    hiddenimports += _h


a = Analysis(
    ['maingui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['browser_cookie3'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CourseraGrab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,            # no console window; progress shows inside the app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/icon.ico',
)
