#!/bin/bash

echo "================================================"
echo "WebTestool - System Test Runner"
echo "================================================"
echo ""

echo "[1/2] Running verification tests..."
python3 verify_installation.py
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Verification failed!"
    echo "Please fix installation issues before running tests."
    exit 1
fi

echo ""
echo "[2/2] Running system tests..."
python3 test_system.py
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Some system tests failed!"
    exit 1
fi

echo ""
echo "================================================"
echo "All tests passed successfully!"
echo "================================================"
echo ""
echo "System is ready for use."
echo ""
echo "Try running:"
echo "   python3 main.py --url https://example.com --profile quick"
echo ""
