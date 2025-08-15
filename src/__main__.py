# src/__main__.py
from __future__ import annotations
import sys
from pathlib import Path

# --- 直接実行対策: リポジトリルートを sys.path に追加 ---
if __package__ is None or __package__ == "":
    # このファイル .../repo/src/__main__.py から2つ上 = リポジトリルート
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

# ここからは絶対インポートでOK
from src.full_pipline_gui import main  # 例：既存のエントリ関数
from src.common.imports_check import check_all

if __name__ == "__main__":
    print("src.__main__.pyを実行します")
    check_all()
    main()
