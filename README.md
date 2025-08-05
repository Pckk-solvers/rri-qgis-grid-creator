# DEM Processor Tool

DEM (Digital Elevation Model) 処理ツールは、QGISの機能を使用してDEMデータを処理するためのツールです。

## 主な機能

- 窪地処理（Fill Sinks）
- 流向・流域解析（Flow Direction & Watershed）
- ラスタ形式の変換（SAGA format ↔ ASC format）

## インストール

1. 必要なパッケージをインストール:
   ```bash
   pip install -r requirements.txt
   ```

2. QGIS 3.x がインストールされていることを確認してください。

## 使い方

### GUI モード

```bash
# GUI で起動
python -m pyqg

# または直接 gui.py を実行
python -m pyqg.gui
```

### コマンドライン モード

```bash
# 基本的な使い方
python -m pyqg.core 入力ファイル.asc 出力ディレクトリ [オプション]

# 例
python -m pyqg.core input.asc output --min-slope 0.1 --threshold 5
```

#### オプション

- `--min-slope` : 最小勾配（デフォルト: 0.1）
- `--threshold` : チャネルネットワークの閾値（デフォルト: 5）

## 出力ファイル

処理が完了すると、以下のファイルが出力ディレクトリに作成されます：

- `filled.sdat` - 窪地処理済みDEM (SAGA形式)
- `filled_asc.asc` - 窪地処理済みDEM (ASC形式)
- `direction.sdat` - 流向データ (SAGA形式)
- `direction_asc.asc` - 流向データ (ASC形式)

## 開発者向け情報

### プロジェクト構成

```
src/
  pyqg/
    __init__.py
    __main__.py   # エントリーポイント
    core.py       # コマンドラインインターフェース
    gui.py        # GUI インターフェース
    processor.py  # 主要な処理ロジック
```

### 開発環境のセットアップ

1. リポジトリをクローン:
   ```bash
   git clone <repository-url>
   cd rri-qgis-grid-creator
   ```

2. 仮想環境を作成して有効化:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. 開発用パッケージをインストール:
   ```bash
   pip install -e .
   ```

## ライセンス

MIT License
