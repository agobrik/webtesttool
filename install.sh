#!/bin/bash

echo "================================================"
echo "WebTestool Installation Script (Linux/Mac)"
echo "================================================"
echo ""

echo "[1/4] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found! Please install Python 3.11 or higher."
    exit 1
fi

python3 --version
echo ""

echo "[2/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo ""

echo "[3/4] Activating virtual environment and installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ""

echo "[4/4] Installing Playwright browsers..."
python -m playwright install chromium firefox
echo ""

echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "To activate the environment, run:"
echo "   source venv/bin/activate"
echo ""
echo "To run a scan:"
echo "   python main.py --url https://example.com"
echo ""
echo "See USAGE_GUIDE.md for more information."
echo ""
