"""Script to run the Money Manager app on desktop for testing."""
import os
import sys

# Set environment variables for better desktop experience
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

# Import and run the app
from main import MoneyManagerApp

if __name__ == '__main__':
    print("Starting Money Manager...")
    print("=" * 50)
    print("Desktop Test Mode")
    print("Window size: 360x640 (Mobile simulation)")
    print("=" * 50)
    
    try:
        MoneyManagerApp().run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

