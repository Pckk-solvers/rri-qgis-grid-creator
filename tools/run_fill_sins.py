# tools/run_fill_sinks.py

import os
import sys
from qgis.core import QgsApplication
from qgis.analysis import QgsNativeAlgorithms

def main():
    # --- QGIS 初期化 ---
    QGIS_PREFIX = r"C:\Program Files\QGIS 3.40.4\apps\qgis-ltr"
    QgsApplication.setPrefixPath(QGIS_PREFIX, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # processing プラグインの読み込みパス追加
    sys.path.append(os.path.join(QGIS_PREFIX, "python", "plugins"))
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    # --- プロジェクトsrcをパスに追加 ---
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
    sys.path.append(PROJECT_ROOT)

    # --- 実行 ---
    from pyqg.fill_sinks import fill_sinks

    input_asc = r'C:\Users\yuuta.ochiai\Documents\GitHub\rri-qgis-grid-creator\data\input\domain_mesh_elev.asc'
    output_sdat = r'C:\Users\yuuta.ochiai\Documents\GitHub\rri-qgis-grid-creator\data\output\filled.sdat'

    print("窪地処理 開始")
    try:
        fill_sinks(input_asc, output_sdat)
        print("窪地処理 完了 =>", output_sdat)
    except Exception as e:
        print("エラー発生:", e)

    qgs.exitQgis()

if __name__ == "__main__":
    main()
