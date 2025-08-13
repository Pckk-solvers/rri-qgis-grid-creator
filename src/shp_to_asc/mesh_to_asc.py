#!/usr/bin/env python3
"""
メッシュデータをASC形式に変換するスクリプト

使用方法:
    python -m shp_to_asc.mesh_to_asc input_mesh.shp output.asc [--field FIELD] [--nodata NODATA]
"""
import os
import argparse
from pathlib import Path
from .core import shp_to_ascii

def convert_mesh_to_asc(
    input_mesh: str | Path,
    output_asc: str | Path,
    field: str = "elevation",
    nodata: float = -9999.0
) -> None:
    """
    メッシュデータをASC形式に変換する
    
    Args:
        input_mesh: 入力メッシュファイルパス (.shp)
        output_asc: 出力ASCファイルパス
        field: 標高値が格納されているフィールド名
        nodata: NoData値
    """
    input_mesh = Path(input_mesh)
    output_asc = Path(output_asc)
    
    # 出力ディレクトリが存在しない場合は作成
    output_asc.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"メッシュをASC形式に変換中: {input_mesh} -> {output_asc}")
    print(f"  標高フィールド: {field}")
    print(f"  NoData値: {nodata}")
    
    # 変換を実行
    shp_to_ascii(
        shp_path=str(input_mesh),
        field=field,
        output_path=str(output_asc),
        nodata=nodata
    )
    
    print(f"変換が完了しました: {output_asc}")
    return output_asc

def main():
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='メッシュデータをASC形式に変換')
    parser.add_argument('input_mesh', help='入力メッシュファイル (.shp)')
    parser.add_argument('output_asc', help='出力ASCファイル')
    parser.add_argument('--field', default='elevation', help='標高値が格納されているフィールド名 (デフォルト: elevation)')
    parser.add_argument('--nodata', type=float, default=-9999.0, help='NoData値 (デフォルト: -9999.0)')
    
    args = parser.parse_args()
    
    convert_mesh_to_asc(
        input_mesh=args.input_mesh,
        output_asc=args.output_asc,
        field=args.field,
        nodata=args.nodata
    )

if __name__ == "__main__":
    main()
