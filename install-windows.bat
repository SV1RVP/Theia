@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion
title Project Theia - Windows Installer
chcp 65001 >nul

echo.
echo ============================================================
echo       Project Theia - Windows Universal Installer
echo       Author: Alexandros - Ermis Tsourapas
echo ============================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found in your PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python detected successfully.

:: 2. Create Virtual Environment
echo.
echo Setting up Python Virtual Environment (.venv)...
if exist ".venv" (
    call .venv\Scripts\python.exe -c "import sys" >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Existing virtual environment is invalid or points to an outdated Python installation.
        echo Recreating .venv...
        rmdir /s /q .venv
    )
)
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully at .venv\
) else (
    echo [INFO] Virtual environment .venv is valid and ready.
)

:: 3. Install Requirements
echo.
echo Installing and upgrading dependencies...
call .venv\Scripts\python.exe -m pip install --upgrade pip
call .venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
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
echo [NOTE] Edit config\app.json and platform files as needed.

echo.
echo ============================================================
echo  Installation Complete!
echo.
echo  To start Project Theia on Windows:
echo    Double click "start-windows.bat"
echo    or run: .venv\Scripts\python.exe main.py
echo.
echo  Access the dashboard at: http://localhost:80
echo ============================================================
echo.
pause
