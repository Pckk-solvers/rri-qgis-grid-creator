@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "PS5=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if /I "%PROCESSOR_ARCHITECTURE%"=="x86" if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" set "PS5=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"

echo [cmd] PS5=%PS5%

rem --- 1) Unblock (MOTW) ---
"%PS5%" -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -LiteralPath '%ROOT%' -Recurse -File -Force | Unblock-File -ErrorAction SilentlyContinue" 

rem --- 2) Run the PS1 (pass args as-is) ---
"%PS5%" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%build_scripts\run.ps1" %*

echo [cmd] ExitCode=%ERRORLEVEL%
rem if not defined CI pause
endlocal & exit /b %ERRORLEVEL%
