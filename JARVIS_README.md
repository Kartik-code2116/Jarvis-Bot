# ◈ J.A.R.V.I.S — Complete AI Desktop Assistant v2.0

Powered by **Google Gemini AI** · Python · Tkinter · Windows

---

## 🚀 Quick Start

```
Double-click  START_JARVIS.bat
```

The holographic avatar appears **bottom-right**.  
Double-click it (or press **Ctrl+Space**) to open the HUD chat.

---

## ✨ What's New in v2.0

| Feature | Details |
|---|---|
| 🧠 Gemini AI | Natural language — say anything naturally |
| 💾 Persistent Memory | Remembers your name, preferences, chat history |
| 🔊 Text-to-Speech | JARVIS speaks responses (Windows SAPI / pyttsx3) |
| 🔌 Plugin System | Drop `.py` files in `/plugins/` to add commands |
| ⚡ Quick Toolbar | 12 one-click action buttons in the HUD |
| ⬆️ Input History | Press ↑/↓ to recall previous commands |
| ⏰ Reminders | Pop-up reminders with sound |
| 📝 Notes | Save and view notes |
| 🧮 Calculator | Evaluate math expressions |
| 📡 System Stats | RAM, CPU, battery, IP, ping, processes |
| 🗂️ Full File Ops | Create, read, delete, rename, find, open files |
| 📋 Clipboard | Copy text to clipboard |
| 🌍 Maps / News / Translate | Web integrations |
| 🔒 System Control | Lock, sleep, shutdown, restart |
| 🪟 Window Snapping | Snap left/right, maximize |

---

## 💬 Command Examples

### Apps
```
open chrome
open vs code
open spotify
close discord
```

### Files
```
list files
list files C:\Users\YourName\Documents
open folder D:\Projects
create file notes.txt
find files *.pdf
read file C:\path\to\file.txt
delete file C:\path\to\file.txt
```

### Web
```
search artificial intelligence
youtube lofi hip hop
play Bohemian Rhapsody
weather Pune
open maps Eiffel Tower Paris
news technology
translate hello to Hindi
open github.com
```

### System
```
what time is it
what's today's date
system info
battery status
my ip address
ping google.com
running processes
volume up
volume down
mute
set volume to 50
minimize all
lock screen
sleep
shutdown
restart
```

### Smart Inputs
```
type Hello, World!
press enter
ctrl+s
ctrl+c
screenshot
copy to clipboard Hello World
calculate 25 * 8 + 12
remind me in 10 minutes to drink water
save note buy groceries tomorrow
show notes
run ipconfig
my name is Tony
```

### Conversation
```
how are you
tell me a joke
what can you do
```

---

## 🔌 Plugin System

Create a `.py` file in the `/plugins/` folder:

```python
COMMANDS = ["my command", "trigger phrase"]

def handle(cmd: str) -> str:
    return "Plugin response!"
```

JARVIS auto-loads all plugins on startup. See `plugins/my_shortcuts.py` for an example.

---

## 🖱️ Avatar Controls

| Action | Result |
|---|---|
| **Drag** | Move avatar anywhere on screen |
| **Double-click** | Open/focus HUD |
| **Right-click** | Quick menu |

---

## ⌨️ HUD Shortcuts

| Key | Action |
|---|---|
| **Enter** | Send command |
| **Ctrl+Space** | Focus input (from anywhere) |
| **↑ / ↓** | Browse command history |

---

## 📁 Project Structure

```
Jarvis Bot/
├── jarvis.py            ← Main application (everything in one file)
├── START_JARVIS.bat     ← Launch script
├── jarvis_memory.json   ← Auto-created: your preferences + history
├── plugins/
│   └── my_shortcuts.py  ← Your custom commands
└── JARVIS_README.md
```

---

## ⚙️ Dependencies

Auto-installed by `START_JARVIS.bat`:
- `pyautogui` — keyboard/mouse/screenshot
- `pillow` — image handling
- `requests` — Gemini API calls
- `pygetwindow` — window management
- `pyttsx3` — text-to-speech fallback
- `psutil` *(optional)* — RAM/CPU/battery stats

---

## 🔑 API Key

Your key is already set in `jarvis.py`:
```python
GEMINI_API_KEY = "AIzaSyAf..."
```
To change it, edit that line in `jarvis.py`.

---

*Built with ❤️ by You + Claude*
