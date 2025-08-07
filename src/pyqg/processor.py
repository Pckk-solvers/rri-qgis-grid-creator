#!/usr/bin/env python3
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import os
from typing import Dict, Any, Optional
from contextlib import contextmanager

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

@contextmanager
def temp_sdat_files(*filenames: str) -> Dict[str, str]:
    """一時的なSDATファイルを作成し、処理後に削除するコンテキストマネージャー
    
    Args:
        *filenames: 作成する一時ファイルのベース名のリスト
        
    Yields:
        Dict[str, str]: 一時ファイルのパスを保持する辞書
    """
    temp_dir = tempfile.mkdtemp()
    temp_files = {}
    
    try:
        for filename in filenames:
            base_name = Path(filename).stem  # 拡張子を除いたファイル名を取得
            temp_files[base_name] = str(Path(temp_dir) / f"{base_name}.sdat")
        yield temp_files
    finally:
        # 一時ディレクトリとその内容を削除
        shutil.rmtree(temp_dir, ignore_errors=True)

def process_dem(
    input_path: str | Path,
    output_dir: str | Path,
    min_slope: float = 0.1,
    threshold: int = 5,
    keep_temp_files: bool = False
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
    
    # 出力ディレクトリを作成
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 出力ファイルのパスを構築
    output_files = {
        'filled_asc': output_dir / 'filled.asc',
        'direction_asc': output_dir / 'direction.asc'
    }
    
    # 一時ファイルのパスを設定
    temp_sdat_files_map = {
        'filled': 'filled.sdat',
        'direction': 'direction.sdat',
        'segments': 'segments.sdat',
        'basins': 'basins.sdat'
    }
    
    try:
        # 一時ファイル用のコンテキストを作成
        with temp_sdat_files(*temp_sdat_files_map.values()) as temp_files:
            # 1) 窪地処理
            print("\n[1/4] 窪地処理を開始しています...")
            print(f"  入力ファイル: {input_path}")
            print(f"  一時ファイル: {temp_files['filled']}" if not keep_temp_files else f"  出力先: {temp_files['filled']}")
            print(f"  最小勾配: {min_slope}")
            
            run_qgis(
                "sagang:fillsinksxxlwangliu",
                {
                    "ELEV": str(input_path),
                    "FILLED": temp_files['filled'],
                    "MINSLOPE": min_slope
                }
            )
            print("  ✅ 窪地処理が完了しました")

            # 2) 流向処理
            print("\n[2/4] 流向・流域解析を開始しています...")
            print(f"  閾値: {threshold}")
            print(f"  流向データ一時ファイル: {temp_files['direction']}" if not keep_temp_files else f"  流向データ出力先: {temp_files['direction']}")
            
            run_qgis(
                "sagang:channelnetworkanddrainagebasins",
                {
                    "DEM": temp_files['filled'],
                    "DIRECTION": temp_files['direction'],
                    "SEGMENTS": temp_files['segments'],
                    "BASINS": temp_files['basins'],
                    "THRESHOLD": threshold,
                    "SUBBASINS": True
                }
            )
            print("  ✅ 流向・流域解析が完了しました")

            # 3) ラスタ変換 (filled.sdat → filled.asc)
            print("\n[3/4] ラスタ変換を実行しています (filled.sdat → filled.asc)...")
            run_qgis(
                "gdal:translate",
                {
                    "INPUT": temp_files['filled'],
                    "OUTPUT": str(output_files['filled_asc'])
                }
            )
            print("  ✅ ラスタ変換が完了しました (filled)")

            # 4) ラスタ変換 (direction.sdat → direction.asc)
            print("\n[4/4] ラスタ変換を実行しています (direction.sdat → direction.asc)...")
            run_qgis(
                "gdal:translate",
                {
                    "INPUT": temp_files['direction'],
                    "OUTPUT": str(output_files['direction_asc'])
                }
            )
            print("  ✅ ラスタ変換が完了しました (direction)")
            
            # 一時ファイルを保持する場合、出力ディレクトリにコピー
            if keep_temp_files:
                for key, temp_path in temp_files.items():
                    if Path(temp_path).exists():
                        dest_path = output_dir / f"{key}.sdat"
                        shutil.copy2(temp_path, dest_path)
                        output_files[f"{key}_sdat"] = dest_path
                        print(f"  ✅ 一時ファイルを保持: {dest_path}")
        
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
