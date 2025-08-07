@echo off
setlocal

echo アプリケーションを起動しています...

:: 仮想環境が存在するか確認
if not exist "venv" (
    echo 仮想環境が見つかりません。最初に setup.bat を実行してください
    pause
    exit /b 1
)

:: 仮想環境を有効化
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo 仮想環境の有効化に失敗しました
    pause
    exit /b 1
)

:: メインスクリプトを実行
python src\full_pipline_gui.py

:: エラーが発生した場合にウィンドウを閉じない
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo エラーが発生しました。エラーメッセージを確認してください
    pause
)