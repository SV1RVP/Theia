@echo off
cd /d "%~dp0"
title Project Theia - Radiation Monitor ^& GMCMap Proxy
chcp 65001 >nul

echo ============================================================
echo       Project Theia - Radiation Monitoring Server
echo       Creator: Alexandros - Ermis Tsourapas (SV1RVP)
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [WARNING] Virtual environment not found. Running installer first...
    call install-windows.bat
    if %ERRORLEVEL% neq 0 exit /b 1
)

echo Starting server...
echo Access Web Dashboard at: http://localhost:80
echo (If running on port 80 requires administrator privileges, run as Administrator)
echo.

.venv\Scripts\python.exe main.py
set SERVER_EXIT_CODE=%ERRORLEVEL%

if %SERVER_EXIT_CODE% neq 0 (
    echo.
    echo [ERROR] Server exited with error code %SERVER_EXIT_CODE%.
    pause
)

