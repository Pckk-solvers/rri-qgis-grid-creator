# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\full_pipline_gui.py'],
    pathex=[r'C:\Users\yuuta.ochiai\Documents\GitHub\rri-qgis-grid-creator\src'],
    binaries=[],
    datas=[
        (r'.\venv\Lib\site-packages\rasterio', 'rasterio'),
        (r'config\standard_mesh.shx', 'config'),
        (r'config\standard_mesh.shp', 'config'),
        (r'config\standard_mesh.prj', 'config'),
        (r'config\standard_mesh.dbf', 'config'),
        (r'config\standard_mesh.cpg', 'config'),
    ],
    hiddenimports=['rasterio._shim', 'rasterio.sample', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
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
    name='RQGC-v0.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='RQGC-v0.1',
)
