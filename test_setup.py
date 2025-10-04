"""Test script to verify Money Manager setup."""
import sys
import os

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_module(module_name):
    """Check if a module is installed."""
    try:
        __import__(module_name)
        print(f"[OK] {module_name}")
        return True
    except ImportError:
        print(f"[FAIL] {module_name} - Not installed")
        return False

def check_files():
    """Check if all required files exist."""
    required_files = [
        'main.py',
        'requirements.txt',
        'buildozer.spec',
        'models/__init__.py',
        'utils/__init__.py',
        'kv/dashboard.kv',
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[FAIL] {file} - Missing")
            all_present = False
    
    return all_present

def main():
    """Run all checks."""
    print("=" * 50)
    print("MONEY MANAGER - SETUP VERIFICATION")
    print("=" * 50)
    print()
    
    print("[INFO] Checking Python Version...")
    python_ok = check_python_version()
    print()
    
    print("[INFO] Checking Required Modules...")
    modules = ['kivy', 'kivymd', 'matplotlib', 'PIL']
    modules_ok = all(check_module(m) for m in modules)
    print()
    
    print("[INFO] Checking Project Files...")
    files_ok = check_files()
    print()
    
    print("=" * 50)
    if python_ok and modules_ok and files_ok:
        print("[SUCCESS] ALL CHECKS PASSED!")
        print("=" * 50)
        print()
        print("You can now run the app:")
        print("  python run_desktop.py")
        print()
        print("Or generate sample data first:")
        print("  python sample_data.py")
        print()
        return 0
    else:
        print("[FAIL] SOME CHECKS FAILED")
        print("=" * 50)
        print()
        if not python_ok:
            print("Please install Python 3.8 or higher")
        if not modules_ok:
            print("Please install missing modules:")
            print("  pip install -r requirements.txt")
        if not files_ok:
            print("Some project files are missing")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
