"""
Build script for Anime Buddy Desktop Application
Creates a distributable .exe with all resources
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """Clean previous build artifacts."""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for d in dirs_to_remove:
        if os.path.exists(d):
            print(f"🗑️  Removing {d}/...")
            shutil.rmtree(d)
    
    files_to_remove = ['AnimeBuddy.spec']
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
    print("✅ Cleaned build directory")


def build_exe():
    """Build the executable using PyInstaller."""
    print("🔨 Building AnimeBuddy.exe...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=AnimeBuddy',
        '--onefile',           # Single executable
        '--windowed',          # No console window
        '--noconfirm',         # Overwrite existing
        '--clean',             # Clean cache
        
        # Icon (if available)
        # '--icon=icon.ico',
        
        # Add data files
        '--add-data', 'anime_buddy.py;.',
        '--add-data', 'config_manager.py;.',
        '--add-data', 'settings_window.py;.',
        '--add-data', 'setup_wizard.py;.',
        
        # Hidden imports
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.font',
        '--hidden-import=pyautogui',
        '--hidden-import=PIL',
        '--hidden-import=requests',
        
        # Main entry point
        'main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def create_distribution():
    """Create distribution folder with all necessary files."""
    print("📦 Creating distribution package...")
    
    dist_dir = Path('dist/AnimeBuddy-Portable')
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_source = Path('dist/AnimeBuddy.exe')
    if exe_source.exists():
        shutil.copy2(exe_source, dist_dir / 'AnimeBuddy.exe')
        print("✅ Copied executable")
    else:
        print("❌ Executable not found!")
        return False
    
    # Create sample config file
    sample_config = '''{
  "buddy": {
    "name": "Miku",
    "title": "Desktop Companion",
    "personality": "cheerful",
    "speech_style": "casual",
    "talk_frequency": "normal",
    "energy_level": "normal"
  },
  "appearance": {
    "skin": "#FFD5B8",
    "hair_primary": "#3A1F6E",
    "hair_highlight": "#5B2FC0",
    "eye_color": "#6040E0",
    "shirt": "#6C8EEF",
    "skirt": "#3A54C0",
    "ribbon": "#EF6CAA",
    "blush": "#FFB3B3"
  },
  "behavior": {
    "walk_speed": 2.5,
    "use_emojis": true,
    "human_behaviors": true,
    "remember_history": true
  },
  "llm": {
    "enabled": false,
    "api_key": "",
    "api_url": "https://api.openai.com/v1/chat/completions",
    "model": "gpt-3.5-turbo"
  },
  "window": {
    "start_position": "bottom_right",
    "always_on_top": true,
    "opacity": 1.0
  },
  "first_run": true
}'''
    
    with open(dist_dir / 'sample-config.json', 'w') as f:
        f.write(sample_config)
    
    # Create README
    readme = '''# Anime Buddy - Desktop Companion

## 🚀 Quick Start

1. Run `AnimeBuddy.exe`
2. Follow the setup wizard to customize your buddy
3. Right-click your buddy anytime for Settings

## 🎮 Features

- **AI-Powered Chat**: Optional LLM integration for smart conversations
- **Personality System**: 7 unique personalities (cheerful, tsundere, shy, genki, mysterious, royal, yandere)
- **Customizable Appearance**: Change colors, name, and style
- **Desktop Actions**: Open apps, take screenshots, type text
- **Human Behaviors**: Stretches, daydreams, hums, and more
- **Memory System**: Remembers your interactions

## ⚙️ Settings

Right-click your buddy → "⚙️ Settings..."

Or manually edit config at:
`%USERPROFILE%/.animebuddy/config.json`

## 🔑 AI Setup (Optional)

To enable AI features:
1. Get an API key from:
   - OpenAI: https://platform.openai.com
   - Groq: https://console.groq.com (faster, free tier available)
2. Open Settings → 🤖 AI/LLM tab
3. Enter your API key and enable AI

## 📁 Files

- `AnimeBuddy.exe` - Main application
- `sample-config.json` - Example configuration

Config is stored in: `%USERPROFILE%/.animebuddy/`

## ❓ Need Help?

- Check the chat panel hints
- Right-click buddy for options
- Open Settings to customize everything

---
Made with 💕 by Anime Buddy Team
'''
    
    with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"✅ Distribution created at: {dist_dir}")
    return True


def main():
    """Main build process."""
    print("=" * 60)
    print("🌸 Anime Buddy - Build Script")
    print("=" * 60)
    
    # Check requirements
    try:
        import pyautogui
        import PIL
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Clean previous build
    clean_build()
    
    # Build executable
    if not build_exe():
        sys.exit(1)
    
    # Create distribution
    if not create_distribution():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Build Complete!")
    print("=" * 60)
    print(f"📦 Distribution folder: dist/AnimeBuddy-Portable/")
    print(f"📦 Zip this folder to share your app!")
    print("\n🚀 Ready to distribute!")


if __name__ == "__main__":
    main()
