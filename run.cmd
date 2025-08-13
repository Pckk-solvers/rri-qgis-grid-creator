@echo off
setlocal
pushd "%~dp0"
where pwsh >nul 2>nul
if %ERRORLEVEL%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File ".\build_scripts\run.ps1" %*
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File ".\build_scripts\run.ps1" %*
)
set ERR=%ERRORLEVEL%
popd
exit /b %ERR%

