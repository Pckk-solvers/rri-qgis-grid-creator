#!/usr/bin/env python3
import os
import argparse
import glob
from pathlib import Path
from src.make_shp.add_elevation import main as elevation_main
from src.make_shp.extract_standard_mesh import extract_cells
from shp_to_asc.mesh_to_asc import convert_mesh_to_asc

def pipeline(domain_shp, basin_shp, num_cells_x, num_cells_y, points_path, out_dir, 
             standard_mesh, zcol=None, nodata=None, mesh_id=None):
    """メッシュ生成パイプラインを実行する"""
    # 出力ファイルを格納する辞書を初期化
    output_files = {}
    
    try:
        # 1) 標準メッシュの抽出
        extracted = os.path.join(out_dir, "domain_standard_mesh.shp")
        print(f"Extracting standard mesh cells intersecting domain → {extracted}")
        print(f"Standard mesh path: {standard_mesh}")  # デバッグ用に追加
        if not os.path.exists(standard_mesh):
            raise FileNotFoundError(f"標準メッシュファイルが見つかりません: {standard_mesh}")

        extract_cells(standard_mesh, domain_shp, extracted, mesh_id)
        print(f"Extracted standard mesh to {extracted}")
        output_files['standard_mesh'] = extracted
        
        # 2) 標準メッシュに対してメッシュ生成を実行
        print("\n=== 標準メッシュに対してメッシュ生成を実行 ===")
        print(f"入力ファイル: {extracted}")
        
        # メッシュ生成を実行
        try:
            from src.make_shp.generate_mesh import main as generate_mesh_main
            print(f"\n=== メッシュ生成を開始します ===")
            domain_mesh = os.path.join(out_dir, "domain_mesh.shp")
            basin_mesh = os.path.join(out_dir, "basin_mesh.shp")
            
            # 標準メッシュの抽出結果を入力としてメッシュ生成を実行
            generate_mesh_main(extracted, basin_shp, num_cells_x, num_cells_y, out_dir)
            
            # 出力ファイルの存在を確認
            if not os.path.exists(domain_mesh):
                raise FileNotFoundError(f"ドメインメッシュが生成されていません: {domain_mesh}")
            if not os.path.exists(basin_mesh):
                print(f"警告: 流域メッシュが生成されていません: {basin_mesh}")
            
            # 出力ファイルパスを保存
            output_files['domain_mesh'] = domain_mesh
            output_files['basin_mesh'] = basin_mesh
            
            print(f"ドメインメッシュ: {domain_mesh}")
            print(f"流域メッシュ: {basin_mesh}")
            
        except Exception as e:
            print(f"[ERROR] メッシュ生成中にエラーが発生しました: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

        # 3) 標高付与
        print("\n=== 標高付与 ===")
        elevation_main(domain_mesh, basin_mesh, points_path, out_dir, zcol, nodata)

        # 4) ASC形式に変換
        # 標高付与後のファイル名を設定（_elevが付く）
        domain_mesh_elev = os.path.splitext(domain_mesh)[0] + "_elev.shp"
        domain_mesh_asc = os.path.join(out_dir, "domain_mesh_elev.asc")
        
        print(f"\n=== ドメインメッシュをASC形式に変換 ===")
        print(f"入力ファイル: {domain_mesh_elev}")
        print(f"出力ファイル: {domain_mesh_asc}")
        
        # デバッグ用：シェープファイルのカラム名を表示
        import geopandas as gpd
        print("\n=== シェープファイルのカラム名 ===")
        domain_df = gpd.read_file(domain_mesh_elev)
        print("domain_mesh columns:", domain_df.columns.tolist())
        print("Available numeric columns:", 
              [col for col in domain_df.columns 
               if domain_df[col].dtype in ['float64', 'int64', 'float32', 'int32']])
        
        # 標高データが含まれているフィールドを確認
        elevation_field = "elevation"
        if elevation_field not in domain_df.columns:
            raise ValueError(f"標高データのカラム '{elevation_field}' が見つかりません。利用可能なカラム: {domain_df.columns.tolist()}")
        
        convert_mesh_to_asc(
            input_mesh=domain_mesh_elev,  # _elevが付いたファイルを指定
            output_asc=domain_mesh_asc,
            field=elevation_field,
            nodata=nodata if nodata is not None else -9999.0
        )
        output_files['domain_mesh_asc'] = domain_mesh_asc

    except Exception as e:
        print(f"[WARNING] 処理中にエラーが発生しました: {e}")
        # エラーが発生しても、これまでに作成されたoutput_filesは保持する

    # # 5) 中間ファイルをまとめて削除
    # try:
    #     for basename in ("domain_mesh", "basin_mesh"):
    #         pattern = os.path.join(out_dir, f"{basename}.*")
    #         for fp in glob.glob(pattern):
    #             # ASCファイルは削除しない
    #             if not fp.lower().endswith('.asc'):
    #                 try:
    #                     os.remove(fp)
    #                 except Exception as e:
    #                     print(f"[WARNING] ファイルの削除に失敗しました: {fp} - {e}")
    # except Exception as e:
    #     print(f"[WARNING] 中間ファイルの削除中にエラーが発生しました: {e}")
    
    # 6) 出力ファイルのパスを表示
    print("\n=== 出力ファイル一覧 ===")
    if output_files:  # output_filesが空でない場合のみ表示
        for name, path in output_files.items():
            if os.path.exists(path):
                print(f"- {name}: {path}")
            else:
                print(f"- [WARNING] ファイルが見つかりません: {name} ({path})")
    else:
        print("出力ファイルは作成されませんでした。")
    
    return output_files  # 呼び出し元で利用できるように返す

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="計算領域→（標準地域メッシュ抽出）→メッシュ生成→標高付与 を一括実行"
    )
    ap.add_argument("--domain",        required=True, help="計算領域ポリゴン (.shp)")
    ap.add_argument("--basin",         required=True, help="流域界ポリゴン (.shp)")
    ap.add_argument("--cells_x",       type=int, required=True, help="X方向セル数")
    ap.add_argument("--cells_y",       type=int, required=True, help="Y方向セル数")
    ap.add_argument("--points",        required=True, help="点群データ (CSV/SHP)")
    ap.add_argument("--zcol",          default=None, help="Z 列名")
    ap.add_argument("--outdir",        default="./outputs", help="出力フォルダ")
    ap.add_argument("--nodata",        type=float, default=None, help="NODATA値 (デフォルト: -9999)")
    ap.add_argument("--standard-mesh", required=True, help="標準地域メッシュ (.shp) を指定")
    ap.add_argument("--mesh-id",       default=None, help="標準メッシュのID列名 (省略可)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    pipeline(
        args.domain,
        args.basin,
        args.cells_x,
        args.cells_y,
        args.points,
        args.outdir,
        args.zcol,
        args.nodata,
        args.standard_mesh,
        args.mesh_id
    )
