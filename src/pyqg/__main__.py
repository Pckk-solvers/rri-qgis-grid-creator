#!/usr/bin/env python3
"""
DEM処理ツールのエントリーポイント

使い方:
    # GUIモードで起動
    python -m pyqg
    
    # CLIモードで起動
    python -m pyqg.core 入力ファイル 出力ディレクトリ [オプション]
    
    # GUIモードで直接起動
    python -m pyqg.gui
"""
import argparse
import sys
import os
from pathlib import Path

def main():
    # モジュールのパスを追加
    if __package__ is None:
        # 直接実行時
        sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(description='DEM処理ツール')
    parser.add_argument('--gui', action='store_true', help='GUIモードで起動')
    
    # 引数が指定されていない場合はGUIモードで起動
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == '--gui'):
        from pyqg.gui import main as gui_main
        gui_main()
    else:
        # CLIモードで起動
        from pyqg.core import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()
