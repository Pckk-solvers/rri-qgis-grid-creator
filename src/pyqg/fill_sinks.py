# pyqg/fill_sinks.py
import sys
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
)
import processing
from processing.core.Processing import Processing



def fill_sinks(input_path: str, output_path: str, minslope: float = 0.1) -> None:
    """
    窪地処理を実行する（fill sinks xxl）。
    
    Parameters:
        input_path (str): 元となるDEMファイル（.ascなど）
        output_path (str): 出力されるfilledファイル（.sdat）
        minslope (float): 最小勾配（default=0.1）
    """
    processing.run("sagang:fillsinksxxlwangliu", {
        'ELEV': input_path,
        'FILLED': output_path,
        'MINSLOPE': minslope
    })
