@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion
title Project Theia - System Updater
chcp 65001 >nul

echo.
echo ============================================================
echo       Project Theia - System Updater
echo       Repository: https://github.com/SV1RVP/Theia
echo       Creator: Alexandros - Ermis Tsourapas (SV1RVP)
echo ============================================================
echo.

set "REPO_URL=https://github.com/SV1RVP/Theia.git"

:: 1. Check Git installation
where git >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Git is available on this system.
    
    if exist ".git" (
        echo [INFO] Fetching latest updates from GitHub...
        git fetch origin main 2>nul
        if %ERRORLEVEL% equ 0 (
            git pull origin main
            echo [OK] Code updated to latest commit from %REPO_URL%
        ) else (
            echo [WARNING] Attempting default git pull...
            git pull
        )
    ) else (
        echo [INFO] Initializing Git tracking for https://github.com/SV1RVP/Theia...
        git init
        git remote add origin %REPO_URL% 2>nul
        git fetch origin main 2>nul
        if !ERRORLEVEL! equ 0 (
            git reset --hard origin/main
            echo [OK] Synchronized cleanly with remote repository!
        ) else (
            echo [INFO] Remote repository ready. Local files preserved.
        )
    )
) else (
    echo [INFO] Git was not found in PATH.
    echo Downloading latest archive from GitHub...
    powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'https://github.com/SV1RVP/Theia/archive/refs/heads/main.zip' -OutFile 'update_temp.zip'; Expand-Archive -Path 'update_temp.zip' -DestinationPath 'update_extracted' -Force; Copy-Item -Path 'update_extracted\Theia-main\*' -Destination '.' -Recurse -Force; Remove-Item -Path 'update_temp.zip', 'update_extracted' -Recurse -Force; Write-Host '[OK] Updated files from GitHub archive!' } catch { Write-Error $_; exit 1 }"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to download update from GitHub.
        pause
        exit /b 1
    )
)

:: 2. Upgrade Python dependencies in .venv if present
if exist ".venv\Scripts\python.exe" (
    echo.
    echo [INFO] Upgrading dependencies in virtual environment...
    .venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>nul
    .venv\Scripts\pip.exe install -r requirements.txt --upgrade
    echo [OK] Dependencies are up to date.
)

echo.
echo ============================================================
echo  Update Complete! / Η ενημέρωση ολοκληρώθηκε επιτυχώς!
echo  Restart Project Theia using "start-windows.bat"
echo ============================================================
echo.
pause
