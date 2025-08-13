@echo off
setlocal
pushd "%~dp0"

REM prefer pwsh if available; fallback to Windows PowerShell
where pwsh >nul 2>nul
if %ERRORLEVEL%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File ".\build_scripts\setup.ps1" %*
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File ".\build_scripts\setup.ps1" %*
)

set ERR=%ERRORLEVEL%
popd
exit /b %ERR%
