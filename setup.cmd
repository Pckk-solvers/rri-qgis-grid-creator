@echo off & setlocal & pushd "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\build_scripts\run.ps1" %*
set ERR=%ERRORLEVEL%
popd & exit /b %ERR%
