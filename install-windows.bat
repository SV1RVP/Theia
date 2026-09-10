@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion
title Project Theia - Windows Installer
chcp 65001 >nul

echo.
echo ============================================================
echo       Project Theia - Windows Universal Installer
echo       Creator: Alexandros - Ermis Tsourapas (SV1RVP)
echo ============================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo [OK] Detected %PYTHON_VER%

:: 2. Create Virtual Environment
echo.
echo Setting up Python Virtual Environment (.venv)...
if not exist ".venv" (
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully at .venv\
) else (
    echo [INFO] Virtual environment .venv already exists.
)

:: 3. Install Requirements
echo.
echo Installing and upgrading dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\pip.exe install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)

:: 4. Configuration setup
echo.
echo Verifying configuration directory (config/)...
if not exist "config" (
    mkdir config
)
echo [OK] Configuration files located in config\
echo [NOTE] Edit config\app.json and platform files (gmcmap.json, radmon.json, etc.) as needed.

echo.
echo ============================================================
echo  Installation Complete! / Η εγκατάσταση ολοκληρώθηκε!
echo.
echo  To start Project Theia on Windows:
echo    Double click "start-windows.bat"
echo    or run: .venv\Scripts\python.exe main.py
echo.
echo  Access the dashboard at: http://localhost:80
echo ============================================================
echo.
pause
