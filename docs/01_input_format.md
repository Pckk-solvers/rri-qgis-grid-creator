# 入力について
このファイルでは入力条件やファイルをまとめる

## [入力ファイルについての説明 (00_overview.md参照) ](00_overview.md#入出力仕様)
### 計算領域ポリゴン（.shp）
計算領域としてユーザが用意したベクタのシェープファイル形式のポリゴン<br>
ジオメトリデータのみを持っている。

### 流域ポリゴン（.shp）
計算領域よりも狭い領域のベクタのシェープファイル形式のポリゴン<br>
ジオメトリデータのみを持っている。

### 点群地形データ（.csv）
例：「X, Y, Value」
最低3列を持つCSV形式のファイルで、必ず「X(x) ,Y(y)」を持っているいことが条件<br>
Valueはどんな列名でも問題ないが標高値が存在することが条件で値は空白を想定していない。


## pyinstallerオプション（メモ）

```cmd
うごかない
pyinstaller `
  --name RQGC-v0.1 `
  --onedir `
  --console `
  --hidden-import=rasterio._shim `
  --hidden-import=rasterio.sample `
  --add-data "./venv/Lib/site-packages/rasterio;rasterio" `
  --add-data "config/standard_mesh.shx;config" `
  --add-data "config/standard_mesh.shp;config" `
  --add-data "config/standard_mesh.prj;config" `
  --add-data "config/standard_mesh.dbf;config" `
  --add-data "config/standard_mesh.cpg;config" `
  --noconfirm src/full_pipline_gui.py

```