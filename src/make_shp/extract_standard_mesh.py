#!/usr/bin/env python3
"""
extract_standard_mesh.py

標準地域メッシュシェープと計算領域ポリゴンを重ね合わせ、
重なるメッシュセルを抽出するスクリプト。
属性はほぼ不要なので、geometry のみを保持する仕様です。

Usage:
    python extract_standard_mesh.py \
        --standard-mesh standard_mesh.shp \
        --domain domain.shp \
        --output extracted_mesh.shp

--id オプションを指定すると、そのID列のみ保持します。
"""
import argparse
import os
import sys
import geopandas as gpd

def extract_cells(standard_shp, domain_shp, output_shp, id_col=None):
    # シェープ読み込み
    mesh_gdf = gpd.read_file(standard_shp)
    domain_gdf = gpd.read_file(domain_shp)

    # CRS を合わせる
    if mesh_gdf.crs != domain_gdf.crs:
        mesh_gdf = mesh_gdf.to_crs(domain_gdf.crs)

    # ドメインを一つの形状に統合
    domain_union = domain_gdf.unary_union

    # 重なり判定: intersects でセル全体を抽出
    mask = mesh_gdf.geometry.intersects(domain_union)
    extracted = mesh_gdf.loc[mask].copy()

    # すべてのポリゴンを1つのマルチポリゴンに結合
    from shapely.ops import unary_union
    combined_geom = unary_union(extracted.geometry)
    
    # 新しいGeoDataFrameを作成（単一のフィーチャに）
    combined_gdf = gpd.GeoDataFrame(geometry=[combined_geom], crs=extracted.crs)
    
    # 元のID列を保持する場合
    if id_col and id_col in extracted.columns:
        # 最初の有効なIDを取得（または適切な方法でIDを選択）
        first_valid_id = extracted[id_col].iloc[0] if not extracted.empty else None
        combined_gdf[id_col] = first_valid_id
    
    # 出力先ディレクトリ作成
    out_dir = os.path.dirname(output_shp)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # ファイル出力
    combined_file=combined_gdf.to_file(output_shp)
    print(f"Extracted {len(extracted)} cells to {output_shp}")
    return combined_file

def main():
    parser = argparse.ArgumentParser(description='標準地域メッシュから重なるセルを抽出')
    parser.add_argument('--standard-mesh', required=True, help='標準地域メッシュ (.shp)')
    parser.add_argument('--domain',        required=True, help='計算領域ポリゴン (.shp)')
    parser.add_argument('--output',        required=True, help='抽出後のシェープ (.shp)')
    parser.add_argument('--id',            help='保持するID列名 (省略可)')
    args = parser.parse_args()

    file=extract_cells(
        args.standard_mesh,
        args.domain,
        args.output,
        args.id
    )
    return file

if __name__ == '__main__':
    main()
