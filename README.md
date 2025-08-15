# RRI QGIS Grid Creator — ZIP配布ブランチ用 README（cmd 推奨）

本ブランチは、ZIP をダウンロードしてそのまま使える **配布用最小構成** です。QGIS の Processing（SAGA NextGen / GDAL）と Python を組み合わせ、RRI 用の計算格子（メッシュ）生成〜標高付与〜ASC 出力〜流向等の前処理までを自動化します。

---

## 収録物（最小構成）

* `setup.cmd` / `run.cmd` … Windows 用セットアップ・起動スクリプト
* `requirements.txt` … Python 依存関係
* `src/` … メインコード（`python -m src` で起動）
* `config/` … 設定・標準地域メッシュ（`standard_mesh.*` 同梱）
* `build_scripts/` … 配布用ビルド関連（任意）
* `.gitignore` … 一時ファイル除外

> 想定利用: **Windows** で ZIP を展開し、`setup.cmd` → `run.cmd` の順に実行。

---

## 動作要件

* OS: Windows 10/11（64bit）
* Python: 3.12–3.13
* QGIS: 3.34 LTR または 3.40 系（Processing + SAGA NextGen, GDAL 有効）

> `qgis_process`（LTR）を使用します。標準外の場所に QGIS を入れている場合は、環境変数 `QGIS_PROCESS_PATH` を設定してください。

---

## クイックスタート（**cmd 起動を推奨**）

**理由**: 1) エラーやログを確認できる 2) セッションの環境変数/venv を確実に引き継げる 3) 作業ディレクトリ（CWD）を明示できる

1. スタートメニュー > **コマンド プロンプト**（または Windows Terminal）を開く
2. ZIP を展開したフォルダへ移動（例）
   
   ```bat
   cd C:\tools\rri-qgis-grid-creator-shared
   ```
4. 初回セットアップ（仮想環境作成 + 依存関係インストール）

   ```bat
   setup.cmd
   ```
5. 起動（GUI ランチャー）

   ```bat
   run.cmd
   ```

> ダブルクリックでも起動は可能ですが、上記理由から **cmd 経由を推奨** します。

---

## QGIS パスが標準でない場合

```bat
set QGIS_PROCESS_PATH=C:\Program Files\QGIS 3.34.9\bin\qgis_process-qgis-ltr.bat
run.cmd
```

`run.cmd` 内に既定値を用意していますが、上書きしたい場合は実行前に上記を設定してください。

---

## 手動セットアップ（スクリプトが使えない場合）

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m src
```

---

## 入力データ

* **計算領域**: Shapefile（ポリゴン）
* **流域界**: Shapefile（ポリゴン）
* **点群**: CSV または Shapefile

  * CSV の場合、列名 `x`, `y` 必須（小文字）。標高列は自動検出または GUI で指定
* **標準地域メッシュ**: `config/standard_mesh.*`（同梱）

> パスは ASCII のみ・短めを推奨（長い日本語パスは避ける）。

---

## 使い方（GUI）

1. `run.cmd` で GUI を起動
2. 入力（計算領域 / 流域界 / 点群 / 標準メッシュ）を指定
3. 分割セル数（X=Y）、NODATA 値、最小勾配・閾値などのパラメータを設定
4. 出力先フォルダを指定し **実行**

### 出力先

* `outputs/mesh/` … メッシュ生成・標高付与・ASC 変換

  * 例: `domain_mesh_elev.asc`（RRI 等で利用）
* `outputs/pyqg/` … 窪地埋め、流向、チャネル抽出などの前処理成果

---

## 使い方（CLI 例）

### フルパイプライン

```bat
python run_full_pipeline.py ^
  --domain path\to\計算領域.shp ^
  --basin path\to\流域界.shp ^
  --cells_x 100 --cells_y 100 ^
  --points path\to\標高点群.csv ^
  --standard-mesh config\standard_mesh.shp ^
  --outdir outputs --min-slope 0.1 --threshold 5
```

### メッシュ→ASC 変換のみ

```bat
python -m shp_to_asc.mesh_to_asc input_mesh_elev.shp outputs\domain_mesh_elev.asc --field elevation --nodata -9999
```

---

## トラブルシュート

* **`qgis_process` が見つからない**: `QGIS_PROCESS_PATH` を設定。QGIS LTR を推奨。
* **SAGA 関連の失敗（例: NoneType）**: QGIS の「Processing SAGA NextGen Provider」を有効化し、`qgis_process` から利用可能か確認。
* **`python src/__main__.py` で ImportError**: 直接実行ではなく **`python -m src`** を使用（パッケージ相対 import が安定）。
* **パス問題**: ASCII のみ/短いパスに展開。ネットワークドライブは避ける。

  
