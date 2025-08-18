
@echo off
setlocal
set "ROOT=%~dp0"

REM --- 64bit�� Windows PowerShell 5.1 �𖾎��w�� ---
set "PS5=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

REM ����32bit�v���Z�X������s����Ă�����ASysnative�o�R��64bit���Ă�
if "%PROCESSOR_ARCHITECTURE%"=="x86" if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" (
  set "PS5=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
)

if not exist "%PS5%" (
  echo Windows PowerShell 5.1 ��������܂���B�������I�����܂��B
  exit /b 1
)

REM 1) ZIP�R���̃u���b�N�����i���s���Ă������j
"%PS5%" -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { Get-ChildItem -LiteralPath '%ROOT%' -Recurse | Unblock-File -ErrorAction Stop } catch {}" >nul 2>&1

REM 2) Bypass�� run.ps1 �����s�i�K�v�ɉ����� -Gui ��t����j
"%PS5%" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%build_scripts\run.ps1" %*

set ERR=%ERRORLEVEL%
if %ERR% neq 0 pause
endlocal & exit /b %ERR%
