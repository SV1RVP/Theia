#!/bin/bash
# Project Theia - Linux / Raspberry Pi System Updater
# Repository: https://github.com/SV1RVP/Theia
# Author: Alexandros - Ermis Tsourapas (SV1RVP)

echo ""
echo "============================================================"
echo "      Project Theia - System Updater (Linux / RPi)"
echo "      Repository: https://github.com/SV1RVP/Theia"
echo "============================================================"
echo ""

REPO_URL="https://github.com/SV1RVP/Theia.git"
ZIP_URL="https://github.com/SV1RVP/Theia/archive/refs/heads/main.tar.gz"

if command -v git &> /dev/null; then
    echo "[OK] Git detected."
    if [ -d ".git" ]; then
        echo "[INFO] Pulling latest updates from GitHub..."
        git fetch origin main 2>/dev/null
        git pull origin main
    else
        echo "[INFO] Configuring Git repository tracking..."
        git init
        git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
        git fetch origin main
        git reset --hard origin/main
    fi
else
    echo "[INFO] Git not found. Downloading release archive from GitHub..."
    if command -v curl &> /dev/null; then
        curl -L "$ZIP_URL" -o /tmp/theia-update.tar.gz
    elif command -v wget &> /dev/null; then
        wget -qO /tmp/theia-update.tar.gz "$ZIP_URL"
    else
        echo "[ERROR] Neither git, curl, nor wget found. Please install git or curl."
        exit 1
    fi
    tar -xzf /tmp/theia-update.tar.gz --strip-components=1
    rm -f /tmp/theia-update.tar.gz
    echo "[OK] Files updated from GitHub release archive."
fi

# Make scripts executable
chmod +x install-linux.sh update-linux.sh 2>/dev/null

# Update Python dependencies
if [ -f ".venv/bin/activate" ]; then
    echo ""
    echo "[INFO] Upgrading Python dependencies..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt --upgrade
    echo "[OK] Dependencies updated."
fi

echo ""
echo "============================================================"
echo " Update Complete! / Η ενημέρωση ολοκληρώθηκε επιτυχώς!"
echo " Restart the service or run:"
echo " sudo .venv/bin/gunicorn --bind 0.0.0.0:80 main:app"
echo "============================================================"
echo ""
