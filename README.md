# RRI QGIS Grid Creator

QGIS と Python を用いて、RRI モデル用の計算格子とDEM前処理（窪地充填・流向計算）を自動化するツールです。GUI と CLI の両方に対応します。

- GUI ランチャ: `src/full_pipline_gui.py`（エントリ `src/__main__.py`）
- サブモジュール（DEM処理など）: `src/pyqg/`

## 機能

- 計算領域・流域ポリゴン（SHP）と点群CSVから、格子（メッシュ）を生成
- 標高列の自動検出（点群CSVから）と属性付与
- ベクタ→ラスタ（ASC）変換
- 窪地充填・流向処理（QGIS Processing/SAGA）とASC出力
- GUI によるフルパイプラインの一括実行

詳細は `docs/` 参照:
- `docs/00_overview.md`（概要・入出力と処理フロー）
- `docs/01_input_format.md`（入力形式）
- `docs/02_qgis_process.md`（QGIS処理の流れ）
- `docs/cmd_command.md`（qgis_process のメモ）

## 必要要件

- Windows（動作想定）
- Python 3.11+ 推奨
- QGIS LTR（例: 3.34.x または 3.40.x LTR）
- 依存Pythonパッケージは `requirements.txt` に記載（`geopandas`, `rasterio`, `fiona`, `shapely`, `numpy`, `pandas`, `pyinstaller` など）

注意:
- QGISのProcessing/SAGAを使用します。QGISのインストールと`qgis_process`のパス設定が必要になります（`docs/cmd_command.md` 参照）。

## セットアップ

1) 依存関係のセットアップ（仮想環境を自動作成）
```cmd
setup.cmd
```
内部で `build_scripts/setup.ps1` が動作し、`.venv` を作成して `requirements.txt` をインストールします。

2) 動作確認（GUI起動）
```cmd
run.cmd
```
- 既定では `.venv\Scripts\python.exe -m src` を実行し、`src/__main__.py` から GUI が起動します。
- PowerShell を直接使う場合は `build_scripts/run.ps1` を参照。

## 使い方

### GUI

- `run.cmd` を実行するか、仮想環境で以下を実行:
```cmd
.venv\Scripts\python.exe -m src
```
- GUI では以下を指定します（`src/full_pipline_gui.py`）:
  - 計算領域（SHP）
  - 流域界（SHP）
  - 点群CSV（複数可、標高列を自動検出）
  - 標準メッシュ（SHP）（`config/` の同梱SHPが既定）
  - メッシュ分割数、NoData、MINSLOPE、THRESHOLD
  - 出力フォルダ（既定は `<repo>/outputs/` またはPyInstaller実行時はEXE隣）
  - QGIS-LTR バージョン（例: 3.34.9）

処理完了/エラーはダイアログとステータスに表示されます。

### CLI（補助）

`src/pyqg/__main__.py` は GUI/CLIのエントリです（内部で `pyqg.core` を呼び出し）。将来的な直接CLI利用を想定しています。
```cmd
# GUI
python -m pyqg

# CLI（実装状況により変更される可能性あり）
python -m pyqg.core <入力> <出力> [オプション]
```

## 入出力

- 入力
  - 計算領域ポリゴン（SHP）
  - 流域ポリゴン（SHP）
  - 点群CSV（X, Y, 標高列）
- 出力（例）
  - 中間: 標高付与メッシュSHP、ASC変換結果
  - 最終: 窪地処理済みDEM（.asc）、流向（.asc）

入力詳細は `docs/01_input_format.md` を参照。

## QGISの設定メモ

- `qgis_process-qgis-ltr.bat` の場所を確認:
```cmd
where /R "C:\Program Files" qgis_process-qgis-ltr.bat
"C:\Program Files\QGIS 3.40.4\apps\qgis-ltr\bin\qgis_process-qgis-ltr.bat" --version
```
- 代表的な実行例は `docs/cmd_command.md` に記載。

## よくある質問（FAQ）

- GUIの標高列が空です
  - CSVのヘッダ行に標高列が存在するか確認してください。複数CSV選択時は共通の列名が必要です（`src/make_shp/zcol_list.py` で検出）。
- QGISが見つからない/処理が失敗する
  - QGIS LTR のインストールと `qgis_process` のパスを確認。`--help`/`--version` が応答するかチェックしてください。

## 開発

- リポジトリ構成例
  - `src/full_pipline_gui.py` GUI本体
  - `src/__main__.py` GUIエントリ
  - `src/pyqg/` DEM処理サブモジュール
  - `tools/` QGIS関連の補助スクリプト
  - `build_scripts/` セットアップと起動スクリプト
  - `docs/` ドキュメント
  - `config/` 標準メッシュSHP等
- 仮想環境で実行:
```cmd
.venv\Scripts\python.exe -m src
```

## 配布（PyInstaller）

- 単体配布を想定する場合は `pyinstaller` を利用。必要なデータ（`config/` のSHP群等）は `--add-data` で同梱が必要です（`docs/01_input_format.md` のメモ参照）。
- Rasterio等は隠しインポートやデータ同梱が必要な場合があります。

## ライセンス

- プロジェクトに合わせて記載してください（未定の場合は「TBD」）。
