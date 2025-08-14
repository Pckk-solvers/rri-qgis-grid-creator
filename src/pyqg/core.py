#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# 自作モジュールのインポート
from src.pyqg.processor import process_dem
from src.pyqg.processor import MIN_SLOPE, THRESHOLD  # デフォルト値をインポート

def main():
    """
    DEM処理のコマンドラインインターフェース
    """
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='Process DEM data using QGIS')
    parser.add_argument('input_file', 
                       help='Path to input DEM file (.asc)')
    parser.add_argument('output_dir', 
                       help='Directory to save output files')
    parser.add_argument('--min-slope', 
                       type=float, 
                       default=MIN_SLOPE,
                       help=f'Minimum slope (default: {MIN_SLOPE})')
    parser.add_argument('--threshold', 
                       type=int, 
                       default=THRESHOLD,
                       help=f'Threshold for channel network (default: {THRESHOLD})')
    
    # 引数のパース
    args = parser.parse_args()
    
    # 出力ディレクトリの作成
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # DEM処理の実行
    result = process_dem(
        input_path=args.input_file,
        output_dir=output_dir,
        min_slope=args.min_slope,
        threshold=args.threshold
    )
    
    # エラーチェック
    if not result['success']:
        print("\n❌ 処理中にエラーが発生しました")
        print(f"エラータイプ: {result.get('error_type', 'Unknown')}")
        print(f"エラーメッセージ: {result.get('error', 'No error message')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
