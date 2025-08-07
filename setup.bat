@echo off
setlocal enabledelayedexpansion

echo 仮想環境のセットアップを開始します...

:: Pythonのバージョン確認
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Pythonがインストールされていないか、PATHに追加されていません
    pause
    exit /b 1
)

:: 仮想環境の作成
if not exist "venv" (
    echo 仮想環境を作成しています...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo 仮想環境の作成に失敗しました
        pause
        exit /b 1
    )
)

:: 仮想環境を有効化
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo 仮想環境の有効化に失敗しました
    pause
    exit /b 1
)

:: 依存パッケージのインストール
echo 依存パッケージをインストールしています...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo セットアップが完了しました！
    echo アプリケーションを起動するには run.bat を実行してください
) else (
    echo 依存パッケージのインストール中にエラーが発生しました
)

pause