# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['crosshair.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='CrosshairOverlay',
    debug=False, bootloader_ignore_signals=False, strip=False,
    upx=True, upx_exclude=[], runtime_tmpdir=None,
    console=False, disable_windowed_traceback=False, icon=None,
)
