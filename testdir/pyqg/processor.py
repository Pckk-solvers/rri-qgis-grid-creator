#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import os

# デフォルト値
MIN_SLOPE = 0.1
THRESHOLD = 5

# qgis_process のパスを環境変数またはデフォルトで取得
QGIS_PROCESS = os.getenv(
    "QGIS_PROCESS_PATH",
    r"C:\Program Files\QGIS 3.34.9\bin\qgis_process-qgis-ltr.bat"
)
if not os.path.isfile(QGIS_PROCESS):
    print(f"ERROR: qgis_process が見つかりません: {QGIS_PROCESS}", file=sys.stderr)
    sys.exit(1)

def run_qgis(alg_id: str, params: dict) -> str:
    """
    qgis_process を実行するヘルパー関数
    
    Args:
        alg_id: 実行するアルゴリズムのID
        params: アルゴリズムのパラメータ（辞書形式）
        
    Returns:
        str: 実行結果の標準出力
    """
    cmd = [QGIS_PROCESS, "run", alg_id, "--json"]
    for k, v in params.items():
        cmd.append(f"{k}={v}")
    print(">>>", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR running qgis_process:", result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout

def process_dem(
    input_path: str | Path,
    output_dir: str | Path,
    min_slope: float = 0.1,
    threshold: int = 5
) -> dict:
    """
    DEMデータを処理するメイン関数
    
    Args:
        input_path: 入力DEMファイルのパス
        output_dir: 出力ディレクトリのパス
        min_slope: 最小勾配（デフォルト: 0.1）
        threshold: チャネルネットワークの閾値（デフォルト: 5）
        
    Returns:
        dict: 出力ファイルのパスを含む辞書
    """
    # パスをPathオブジェクトに変換
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    
    # 出力ファイルのパスを構築
    output_files = {
        'filled_sdat': output_dir / 'filled.sdat',
        'filled_asc': output_dir / 'filled_asc.asc',
        'direction_sdat': output_dir / 'direction.sdat',
        'direction_asc': output_dir / 'direction_asc.asc'
    }
    
    try:
        # 1) 窪地処理
        print("\n[1/4] 窪地処理を開始しています...")
        print(f"  入力ファイル: {input_path}")
        print(f"  出力先: {output_files['filled_sdat']}")
        print(f"  最小勾配: {min_slope}")
        
        run_qgis(
            "sagang:fillsinksxxlwangliu",
            {
                "ELEV": str(input_path),
                "FILLED": str(output_files['filled_sdat']),
                "MINSLOPE": min_slope
            }
        )
        print("  ✅ 窪地処理が完了しました")

        # 2) 流向処理
        print("\n[2/4] 流向・流域解析を開始しています...")
        print(f"  閾値: {threshold}")
        print(f"  流向データ出力先: {output_files['direction_sdat']}")
        
        run_qgis(
            "sagang:channelnetworkanddrainagebasins",
            {
                "DEM": str(input_path),
                "DIRECTION": str(output_files['direction_sdat']),
                "SEGMENTS": "TEMPORARY_OUTPUT",
                "BASINS": "TEMPORARY_OUTPUT",
                "THRESHOLD": threshold,
                "SUBBASINS": True
            }
        )
        print("  ✅ 流向・流域解析が完了しました")

        # 3-1) 変換処理 (filled)
        print("\n[3/4] 埋め立て済みDEMをASC形式に変換しています...")
        run_qgis(
            "gdal:translate",
            {
                "INPUT": str(output_files['filled_sdat']),
                "OUTPUT": str(output_files['filled_asc']),
                "DATA_TYPE": 0
            }
        )
        print(f"  ✅ 変換完了: {output_files['filled_asc']}")
        
        # 3-2) 変換処理 (direction)
        print("\n[4/4] 流向データをASC形式に変換しています...")
        run_qgis(
            "gdal:translate",
            {
                "INPUT": str(output_files['direction_sdat']),
                "OUTPUT": str(output_files['direction_asc']),
                "DATA_TYPE": 0
            }
        )
        print(f"  ✅ 変換完了: {output_files['direction_asc']}")
        
        # 処理完了メッセージ
        print("\n=======================================")
        print("✅ すべての処理が正常に完了しました！")
        print("=======================================")
        print("\n【出力ファイル一覧】")
        for name, path in output_files.items():
            print(f"- {name}: {path}")
        print(f"\n出力先ディレクトリ: {output_dir.absolute()}")
        
        # 出力ファイルのパスを返す
        return {
            'success': True,
            'output_files': {k: str(v) for k, v in output_files.items()}
        }
        
    except Exception as e:
        print("\n❌ エラーが発生しました")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラーメッセージ: {str(e)}")
        print("\n処理を中断します。")
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
