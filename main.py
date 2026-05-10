"""
Anime Buddy - Desktop Companion Application
Main launcher with configuration management
"""
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point."""
    print("🌸 Starting Anime Buddy...")
    
    try:
        # Import after path setup
        from config_manager import ConfigManager
        
        # Initialize config
        config = ConfigManager()
        
        # Import main app
        from anime_buddy import AnimeBuddy
        
        # Create and run app
        app = AnimeBuddy(config_manager=config)
        
    except Exception as e:
        print(f"❌ Error starting Anime Buddy: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Anime Buddy - Error",
                f"Failed to start Anime Buddy:\n\n{e}\n\n"
                "Make sure you have installed all requirements:\n"
                "pip install pyautogui pillow requests"
            )
            root.destroy()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
