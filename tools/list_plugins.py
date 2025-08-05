import os, sys

# QGIS のインストール先
QGIS_ROOT = r"C:\Program Files\QGIS 3.40.4"

# PyQGIS モジュール本体・プラグインフォルダのパス
qgis_python  = os.path.join(QGIS_ROOT, "apps", "qgis-ltr", "python")
qgis_plugins = os.path.join(qgis_python, "plugins")
site_pkgs    = os.path.join(QGIS_ROOT, "apps", "Python312", "Lib", "site-packages")

# sys.path に追加
for p in (site_pkgs, qgis_plugins, qgis_python):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

# PyQGIS 初期化
from qgis.core import QgsApplication
QgsApplication.setPrefixPath(
    os.path.join(QGIS_ROOT, "apps", "qgis-ltr"), True
)
qgs = QgsApplication([], False)
qgs.initQgis()

# ここで初めて processing を import
import processing
from qgis.analysis import QgsNativeAlgorithms
qgs.processingRegistry().addProvider(QgsNativeAlgorithms())

# 一覧出力
import qgis.utils
print("=== Processing Providers ===")
for prov in qgs.processingRegistry().providers():
    print(f"- {prov.id()} ({prov.name()})")

print("\n=== Loaded QGIS Plugins ===")
for name in qgis.utils.plugins.keys():
    print(f"- {name}")

qgs.exitQgis()
