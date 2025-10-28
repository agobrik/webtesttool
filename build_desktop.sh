#!/bin/bash
# WebTestool Desktop App Builder for Linux/macOS
# Builds standalone executable using PyInstaller

set -e

echo "========================================"
echo "WebTestool Desktop App Builder"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "[1/5] Checking/Installing PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
else
    echo "PyInstaller already installed"
fi

echo ""
echo "[2/5] Cleaning previous builds..."
rm -rf build dist

echo ""
echo "[3/5] Building executable with PyInstaller..."
python3 -m PyInstaller webtestool.spec --clean --noconfirm

echo ""
echo "[4/5] Creating data directories..."
mkdir -p dist/WebTestool/data
mkdir -p dist/WebTestool/logs
mkdir -p dist/WebTestool/reports

echo ""
echo "[5/5] Setting executable permissions..."
chmod +x dist/WebTestool/WebTestool

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""
echo "Executable location: dist/WebTestool/WebTestool"
echo ""
echo "You can now:"
echo "1. Run: ./dist/WebTestool/WebTestool"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "2. macOS App bundle: dist/WebTestool.app"
fi
echo "3. Create installer or compress dist/WebTestool for distribution"
echo ""
