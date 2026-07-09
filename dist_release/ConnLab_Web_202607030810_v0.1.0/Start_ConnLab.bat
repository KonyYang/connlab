@echo off
setlocal
cd /d "%~dp0"

if not exist "%~dp0ConnLab_Server.exe" (
  echo ConnLab_Server.exe was not found in this folder.
  pause
  exit /b 1
)

start "ConnLab Local Web Server" "%~dp0ConnLab_Server.exe"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"

endlocal
