# rthooks/rt_gdal_env.py
import os, sys, pathlib, importlib, importlib.util

# ---- PROJ: pyproj 公式データを最優先 ----
try:
    import pyproj.datadir as pdd
    proj_dir = pdd.get_data_dir()
    if proj_dir and os.path.isdir(proj_dir):
        os.environ["PROJ_LIB"] = proj_dir
except Exception:
    pass

# ---- GDAL: rasterio から検出、なければ候補探索 ----
def _find_gdal_data():
    try:
        from rasterio._env import get_gdal_data
        p = get_gdal_data()
        if p and os.path.isdir(p):
            return p
    except Exception:
        pass

    def _cands(modname):
        spec = importlib.util.find_spec(modname)
        if not spec or not getattr(spec, "origin", None):
            return []
        base = pathlib.Path(spec.origin).parent
        return [base / "_gdal_data", base / "gdal_data", base / "share" / "gdal"]

    for m in ("rasterio", "fiona"):
        for c in _cands(m):
            if c.is_dir():
                return str(c)
    return None

gd = _find_gdal_data()
if gd:
    os.environ["GDAL_DATA"] = gd

# ---- DLL解決: “インストール済みのものだけ” *.libs を PATH へ ----
def _pkg_exists(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False

def _add_libdir(modname: str):
    try:
        spec = importlib.util.find_spec(modname)
    except Exception:
        return
    if not spec or not getattr(spec, "origin", None):
        return
    libdir = pathlib.Path(spec.origin).parent
    if libdir.is_dir():
        os.environ["PATH"] = str(libdir) + os.pathsep + os.environ.get("PATH", "")

for base in ("rasterio", "pyproj", "fiona", "shapely"):
    if _pkg_exists(base) and _pkg_exists(f"{base}.libs"):
        _add_libdir(f"{base}.libs")

# onefile 展開先 / onedir フォルダも PATH へ
base_dir = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
os.environ["PATH"] = base_dir + os.pathsep + os.environ.get("PATH", "")
