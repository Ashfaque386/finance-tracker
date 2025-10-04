#!/bin/bash

# Build script for Money Manager APK
echo "=========================================="
echo "Money Manager APK Build Script"
echo "=========================================="
echo ""

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null
then
    echo "❌ Buildozer not found!"
    echo "Installing buildozer..."
    pip install buildozer
fi

# Check if Cython is installed
if ! command -v cython &> /dev/null
then
    echo "Installing Cython..."
    pip install cython
fi

echo "✅ Prerequisites checked"
echo ""

# Clean previous builds (optional)
read -p "Clean previous builds? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🧹 Cleaning previous builds..."
    buildozer android clean
fi

echo ""
echo "🔨 Building APK..."
echo "This may take 15-30 minutes on first build..."
echo ""

# Build APK
buildozer -v android debug

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ BUILD SUCCESSFUL!"
    echo "=========================================="
    echo ""
    echo "APK location: bin/MoneyManager-*.apk"
    echo ""
    echo "To install on device:"
    echo "  adb install bin/MoneyManager-*.apk"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ BUILD FAILED!"
    echo "=========================================="
    echo ""
    echo "Check the errors above for details."
    echo ""
    exit 1
fi

