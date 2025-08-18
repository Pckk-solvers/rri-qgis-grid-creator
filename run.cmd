
@echo off
setlocal
set "ROOT=%~dp0"

REM --- 64bitの Windows PowerShell 5.1 を明示指定 ---
set "PS5=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

REM もし32bitプロセスから実行されていたら、Sysnative経由で64bitを呼ぶ
if "%PROCESSOR_ARCHITECTURE%"=="x86" if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" (
  set "PS5=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
)

if not exist "%PS5%" (
  echo Windows PowerShell 5.1 が見つかりません。処理を終了します。
  exit /b 1
)

REM 1) ZIP由来のブロック解除（失敗しても無視）
"%PS5%" -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { Get-ChildItem -LiteralPath '%ROOT%' -Recurse | Unblock-File -ErrorAction Stop } catch {}" >nul 2>&1

REM 2) Bypassで run.ps1 を実行（必要に応じて -Gui を付ける）
"%PS5%" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%build_scripts\run.ps1" %*

set ERR=%ERRORLEVEL%
if %ERR% neq 0 pause
endlocal & exit /b %ERR%
