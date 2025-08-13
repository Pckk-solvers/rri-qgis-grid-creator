# zcol_list.py
"""
複数の点群ファイルの共通の標高値列を返す。
見つからない場合はエラーを返す。
"""
import pandas as pd
from src.make_shp.add_elevation import get_xy_columns, get_z_candidates

def get_zcol_list(files) -> list:
    """
    複数の点群ファイルの共通の標高値列を返す。
    見つからない場合はエラーを返す。
    
    Args:
        files: 点群ファイルのパスのリスト
        
    Returns:
        list: すべてのファイルに共通する標高値列のリスト
        
    Raises:
        ValueError: 共通の標高値列が見つからない場合
    """
    if not files:
        raise ValueError("ファイルが指定されていません")
    
    common_zcols = None
    
    # 各ファイルの標高値列候補を取得
    for file in files:
        # ファイルを読み込む
        try:
            points = pd.read_csv(file)
        except Exception as e:
            raise ValueError(f"ファイルの読み込みに失敗しました: {file}\n{str(e)}")
            
        # X, Y 列を取得
        try:
            x_col, y_col = get_xy_columns(points)
        except Exception as e:
            raise ValueError(f"X, Y座標列の取得に失敗しました: {file}\n{str(e)}")
        
        # 標高値列候補を取得
        try:
            current_zcols = set(get_z_candidates(points, x_col, y_col))
        except Exception as e:
            raise ValueError(f"標高値列候補の取得に失敗しました: {file}\n{str(e)}")
        
        # 共通の標高値列を更新
        if common_zcols is None:
            common_zcols = current_zcols
        else:
            common_zcols = common_zcols.intersection(current_zcols)
            if not common_zcols:
                break  # 共通の列がなくなったら早期終了
    
    # 結果をリストに変換して返す
    if common_zcols:
        return sorted(list(common_zcols))
    else:
        raise ValueError("すべてのファイルに共通する標高値列が見つかりませんでした")
