#!/usr/bin/env python3
"""
メッシュ生成からpyqg処理までのフルパイプラインを実行するスクリプト

使用方法:
    python scripts/run_full_pipeline.py \
        --domain 入力領域.shp \
        --basin 流域界.shp \
        --cells_x 100 \
        --cells_y 100 \
        --points 標高点群.csv \
        --standard-mesh 標準メッシュ.shp \
        [--outdir 出力ディレクトリ] \
        [--zcol 標高列名] \
        [--nodata NODATA値] \
        [--mesh-id メッシュID列名] \
        [--min-slope 最小勾配] \
        [--threshold 閾値]
"""
import argparse
from pathlib import Path

from src.make_shp.pipeline import pipeline
from src.pyqg.processor import process_dem

def run_full_pipeline(
    domain_shp,
    basin_shp,
    num_cells_x,
    num_cells_y,
    points_path,
    standard_mesh,
    output_dir="outputs",
    zcol=None,
    nodata=None,
    mesh_id=None,
    min_slope=0.1,
    threshold=5,
    qgis_version: str | None = None,
    qgis_process_path: str | None = None
):
    # パスをPathオブジェクトに変換
    output_dir = Path(output_dir)
    mesh_dir = output_dir / "mesh"
    pyqg_dir = output_dir / "pyqg"

    mesh_dir.mkdir(parents=True, exist_ok=True)
    pyqg_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("メッシュ生成パイプラインを開始します")
    print("=" * 50)

    # 1) メッシュ生成＋ASC変換
    print("\n=== メッシュ生成パイプラインを実行中 ===")
    print(f"出力先: {mesh_dir}")
    pipeline(
        domain_shp=domain_shp,
        basin_shp=basin_shp,
        num_cells_x=num_cells_x,
        num_cells_y=num_cells_y,
        points_path=points_path,
        out_dir=str(mesh_dir),
        zcol=zcol,
        nodata=nodata,
        standard_mesh=standard_mesh,
        mesh_id=mesh_id
    )

    # 2) pyqg 処理
    print("\n" + "=" * 50)
    print("pyqgによるDEM処理を開始します")
    print("=" * 50)

    input_asc = mesh_dir / "domain_mesh_elev.asc"
    if not input_asc.exists():
        err = f"メッシュファイルが見つかりません: {input_asc}"
        print(err)
        return {'success': False, 'error': err, 'error_type': 'FileNotFoundError'}

    print(f"\n入力ファイル: {input_asc}")
    print(f"出力先: {pyqg_dir}")
    print(f"最小勾配: {min_slope}")
    print(f"閾値: {threshold}")

    pyqg_result = process_dem(
        input_path=str(input_asc),
        output_dir=str(pyqg_dir),
        min_slope=min_slope,
        threshold=threshold,
        qgis_version=qgis_version,
        qgis_process_path=qgis_process_path
    )

    # process_dem の結果を正規化して返す
    if not isinstance(pyqg_result, dict):
        # 念のための保険（GUI 側の想定に合わせる）
        pyqg_result = {'success': bool(pyqg_result), 'output_files': {}}

    if pyqg_result.get('success') is not True:
        # エラー情報を上位に返す
        return {
            'success': False,
            'stage': 'pyqg',
            'mesh_dir': str(mesh_dir),
            'pyqg_dir': str(pyqg_dir),
            'error': pyqg_result.get('error', 'pyqg 処理で不明なエラー'),
            'error_type': pyqg_result.get('error_type')
        }

    print("\n" + "=" * 50)
    print("処理が完了しました！")
    print("=" * 50)
    print(f"メッシュデータ: {mesh_dir}")
    print(f"pyqg 出力: {pyqg_dir}")
    print("=" * 50)

    # ✅ ここで dict を返す（GUI が期待するフォーマット）
    return {
        'success': True,
        'mesh_dir': str(mesh_dir),
        'pyqg_dir': str(pyqg_dir),
        'mesh_outputs': {
            'domain_mesh_elev_asc': str(input_asc)
        },
        'pyqg_outputs': pyqg_result.get('output_files', {})
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="メッシュ生成からpyqg処理までのフルパイプラインを実行")
    
    # 必須引数
    parser.add_argument("--domain", required=True, help="計算領域ポリゴン (.shp)")
    parser.add_argument("--basin", required=True, help="流域界ポリゴン (.shp)")
    parser.add_argument("--cells_x", type=int, required=True, help="X方向セル数")
    parser.add_argument("--cells_y", type=int, required=True, help="Y方向セル数")
    parser.add_argument("--points", required=True, help="点群データ (CSV/SHP)")
    parser.add_argument("--standard-mesh", required=True, help="標準地域メッシュ (.shp)")
    
    # オプション引数
    parser.add_argument("--outdir", default="outputs", help="出力ディレクトリ (デフォルト: outputs)")
    parser.add_argument("--zcol", help="標高値が格納されている列名 (デフォルト: 自動検出)")
    parser.add_argument("--nodata", type=float, help=f"NODATA値 (デフォルト: -9999)")
    parser.add_argument("--mesh-id", help="標準メッシュのID列名 (デフォルト: 自動検出)")
    parser.add_argument("--min-slope", type=float, default=0.1, help="最小勾配 (デフォルト: 0.1)")
    parser.add_argument("--threshold", type=int, default=5, help="閾値 (デフォルト: 5)")
    parser.add_argument("--qgis-version", default="3.34.9", help="QGIS-LTRのバージョン (デフォルト: 3.34.9)")
    parser.add_argument("--qgis-process-path", help="qgis_processの実行ファイルパス")
    
    args = parser.parse_args()
    
    run_full_pipeline(
        domain_shp=args.domain,
        basin_shp=args.basin,
        num_cells_x=args.cells_x,
        num_cells_y=args.cells_y,
        points_path=args.points,
        standard_mesh=args.standard_mesh,
        output_dir=args.outdir,
        zcol=args.zcol,
        nodata=args.nodata,
        mesh_id=args.mesh_id,
        qgis_version=args.qgis_version,
        qgis_process_path=args.qgis_process_path,
        min_slope=args.min_slope,
        threshold=args.threshold
    )

# 例：実行の仕方
# python src/run_full_pipeline.py --domain data\input\計算領域_POL.shp --basin data\input\流域界_POL.shp --cells_x 20 --cells_y 20 --points data\input\標高点群.csv --standard-mesh config\standard_mesh.shp