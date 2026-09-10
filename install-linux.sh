#!/bin/bash
# Project Theia - Linux Universal Installation Script
# Author: SV1RVP

echo ""
echo "============================================================"
echo "      Project Theia - Universal Linux Installer"
echo "============================================================"
echo ""

# Detect Distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s)
fi

echo "Detected OS: $OS"
echo "Installing system dependencies..."

case $OS in
    ubuntu|debian|raspbian)
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
        ;;
    fedora)
        sudo dnf update -y
        sudo dnf install -y python3 python3-pip
        ;;
    centos|rhel|almalinux|rocky)
        sudo dnf install -y epel-release
        sudo dnf update -y
        sudo dnf install -y python3 python3-pip
        ;;
    arch)
        sudo pacman -Syu --noconfirm python python-pip
        ;;
    opensuse*|suse)
        sudo zypper refresh
        sudo zypper install -y python3 python3-pip python3-virtualenv
        ;;
    alpine)
        sudo apk update
        sudo apk add python3 py3-pip
        ;;
    *)
        echo "[WARNING] Unknown distribution: $OS"
        echo "Please install Python 3 and venv manually."
        ;;
esac

echo ""
echo "Setting up Python Virtual Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "[OK] Virtual environment created at .venv/"
else
    echo "[INFO] Virtual environment already exists."
fi

echo "Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Ensure config directory exists
if [ ! -d "config" ]; then
    mkdir -p config
fi
echo "[OK] Configuration files ready in config/ directory."

echo ""
echo "============================================================"
echo " Installation Complete!"
echo " Edit config/app.json and platform configs (gmcmap.json, etc.) as needed."
echo " To run the application in production with Gunicorn:"
echo " sudo .venv/bin/gunicorn --bind 0.0.0.0:80 main:app"
echo "============================================================"
echo ""
