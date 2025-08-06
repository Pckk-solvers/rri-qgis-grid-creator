# PyQGISの処理３つについての

この３つの処理は、QGISのプロセシングツールで行うことが可能です。
そのためまずはこの3つの処理の流れを連結する。
> **窪地処理 → 流向処理 → ラスタ形式変換処理**
このような流れで処理を行う。
モジュール化しておきたいため、モジュール名はpyqgとしておく。
必要に応じてスクリプト分けをするが個人的意には単一でも良いと考えている。

# Pythonコマンド
## 窪地処理
fill sinks xxl
```python
processing.run("sagang:fillsinksxxlwangliu", {
'ELEV':'//z101070380/fujimoto/RRI-dataset/mesh/elev.asc',
'FILLED':'C:/Users/manami.fujimoto/Desktop/ASC変換ツール確認作業/fill/fill_sample.sdat',
'MINSLOPE':0.1
})
```
 
## 流向処理
channel～flowdirection
```python
processing.run("sagang:channelnetworkanddrainagebasins", {
'DEM':'C:/Users/manami.fujimoto/Desktop/ASC変換ツール確認作業/fill/fill_sample_asc.asc',
'DIRECTION':'C:/Users/manami.fujimoto/Desktop/ASC変換ツール確認作業/flow_direction/fow_direction_sample.sdat',
'SEGMENTS':'TEMPORARY_OUTPUT',
'BASINS':'TEMPORARY_OUTPUT',
'THRESHOLD':5,
'SUBBASINS':True
})
```
 
## ラスタ形式変換処理
sdat→asc変換
```python
processing.run("gdal:translate", {
'INPUT':'C:/Users/manami.fujimoto/Desktop/ASC変換ツール確認作業/fill/fill_sample.sdat',
'TARGET_CRS':None,
'NODATA':None,
'COPY_SUBDATASETS':False,
'OPTIONS':'',
'EXTRA':'',
'DATA_TYPE':0,
'OUTPUT':'C:/Users/manami.fujimoto/Desktop/ASC変換ツール確認作業/fill/fill_sample_asc.asc'
})
```

# CLIコマンド
## 窪地処理
```cmd
"C:\Program Files\QGIS 3.40.4\bin\qgis_process-qgis-ltr.bat" run sagang:fillsinksxxlwangliu --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7030 --ELEV="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/input/domain_mesh_elev.asc" --FILLED="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/output/files.sdat" --MINSLOPE=0.1
```

JSONの場合
```cmd
{
  "area_units": "m2",
  "distance_units": "meters",
  "ellipsoid": "EPSG:7030",
  "inputs": {
    "ELEV": "C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/input/domain_mesh_elev.asc",
    "FILLED": "TEMPORARY_OUTPUT",
    "MINSLOPE": 0.1
  }
}
```

## 流向処理
```cmd
"C:\Program Files\QGIS 3.40.4\bin\qgis_process-qgis-ltr.bat" run sagang:channelnetworkanddrainagebasins --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7030 --DEM="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/input/domain_mesh_elev.asc" --DIRECTION="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/output/ta.sdat" --SEGMENTS=TEMPORARY_OUTPUT --BASINS=TEMPORARY_OUTPUT --THRESHOLD=5 --SUBBASINS=true

"C:\Program Files\QGIS 3.40.4\bin\qgis_process-qgis-ltr.bat" run sagang:channelnetworkanddrainagebasins --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7030 --DEM='C:/Users/manami.fujimoto/Desktop/mesh_test/269-645/output/filled_asc.asc' --DIRECTION='C:/Users/manami.fujimoto/Desktop/mesh_test/0805/flow_dir.sdat' --SEGMENTS=TEMPORARY_OUTPUT --BASINS=TEMPORARY_OUTPUT --THRESHOLD=5 --SUBBASINS=true
```

JSONの場合
```cmd
{
  "area_units": "m2",
  "distance_units": "meters",
  "ellipsoid": "EPSG:7030",
  "inputs": {
    "BASINS": "TEMPORARY_OUTPUT",
    "DEM": "C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/input/domain_mesh_elev.asc",
    "DIRECTION": "C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/output/ta.sdat",
    "SEGMENTS": "TEMPORARY_OUTPUT",
    "SUBBASINS": true,
   "THRESHOLD": 5
  }
}
```

## ラスタ形式変換処理
```cmd
"C:\Program Files\QGIS 3.40.4\bin\qgis_process-qgis-ltr.bat" run gdal:translate --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7030 --INPUT="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/output/files.sdat" --COPY_SUBDATASETS=false --OPTIONS= --EXTRA= --DATA_TYPE=0 --OUTPUT="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/output/files_asc.asc"

"C:\Program Files\QGIS 3.40.4\bin\qgis_process-qgis-ltr.bat" run gdal:translate --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7030 --INPUT="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/output/ta.sdat" --COPY_SUBDATASETS=false --OPTIONS= --EXTRA= --DATA_TYPE=0 --OUTPUT="C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/output/ta_asc.asc"
``` 

JSONの場合
```cmd
{
  "area_units": "m2",
  "distance_units": "meters",
  "ellipsoid": "EPSG:7030",
  "inputs": {
    "COPY_SUBDATASETS": false,
    "DATA_TYPE": 0,
    "EXTRA": "",
    "INPUT": "C:/Users/yuuta.ochiai/Documents/GitHub/rri-qgis-grid-creator/data/input/domain_mesh_elev.asc",
    "NODATA": null,
    "OPTIONS": null,
    "OUTPUT": "TEMPORARY_OUTPUT",
    "TARGET_CRS": null
  }
}
```
