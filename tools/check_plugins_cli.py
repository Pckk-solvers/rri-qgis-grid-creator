# check_plugins_cli.py

import os, subprocess

# QGIS 環境変数をバッチで設定済みなら PATH に qgis_process.exe が通っています
# もし通っていなければ絶対パスを指定してください
qgis_process = r"qgis_process"  # または r"C:\Program Files\QGIS 3.40.4\bin\qgis_process.exe"

proc = subprocess.run(
    [qgis_process, "plugins"], 
    capture_output=True, text=True, shell=True,
    env=os.environ  # 必要ならここで環境変数を調整
)

print(proc.stdout)
if proc.stderr:
    print("ERROR:", proc.stderr)


# call "C:\Program Files\QGIS 3.40.4\bin\qgis-ltr-bin.env"
# call "C:\Program Files\QGIS 3.40.4\bin\python-qgis-ltr.bat" ^
# C:\Users\yuuta.ochiai\Documents\GitHub\rri-qgis-grid-creator\tools\check_plugins_cli.py