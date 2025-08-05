# tools/list_algorithms.py

import os
import sys
from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm
)

# --- QGIS 初期化 ---
QGIS_PREFIX = r"C:\Program Files\QGIS 3.40.4\apps\qgis-ltr"
QgsApplication.setPrefixPath(QGIS_PREFIX, True)
qgs = QgsApplication([], False)
qgs.initQgis()

# processing パス追加と初期化
sys.path.append(os.path.join(QGIS_PREFIX, "python", "plugins"))
import processing
from processing.core.Processing import Processing
Processing.initialize()

# --- アルゴリズム一覧を表示 ---
registry = QgsApplication.processingRegistry()
providers = registry.providers()

for provider in providers:
    print(f"[{provider.id()}] {provider.name()}")
    for alg in provider.algorithms():
        print(f"  {alg.id()}")

qgs.exitQgis()
