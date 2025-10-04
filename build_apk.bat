@echo off
REM Build script for Money Manager APK on Windows

echo ==========================================
echo Money Manager APK Build Script
echo ==========================================
echo.

REM Check if buildozer is installed
buildozer --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing buildozer...
    pip install buildozer
)

echo Prerequisites checked
echo.

REM Note for Windows users
echo ==========================================
echo IMPORTANT NOTE FOR WINDOWS USERS
echo ==========================================
echo.
echo Buildozer is primarily designed for Linux/Mac.
echo For Windows, you have two options:
echo.
echo 1. Use WSL (Windows Subsystem for Linux)
echo    - Install WSL2 from Microsoft Store
echo    - Install Ubuntu from Microsoft Store
echo    - Run this script inside WSL
echo.
echo 2. Use a Virtual Machine
echo    - Install VirtualBox or VMware
echo    - Install Ubuntu 20.04 or later
echo    - Run this script inside the VM
echo.
echo 3. Use GitHub Actions / Cloud Build
echo    - Push code to GitHub
echo    - Use GitHub Actions to build APK
echo.
echo Alternatively, you can test the app on desktop:
echo    python run_desktop.py
echo.
pause

