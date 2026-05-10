# ✨ Anime Desktop Buddy for Windows

A cute anime girl who lives on your screen and does tasks for you!

---

## 🚀 Quick Start

1. Make sure **Python 3.8+** is installed (from https://python.org)
2. Double-click **`START_BUDDY.bat`**  — it installs everything and launches!

Or manually:
```
pip install pyautogui pillow
python anime_buddy.py
```

---

## 💬 Commands (type in the chat panel)

| Command | What she does |
|---------|---------------|
| `open chrome` | Opens Google Chrome |
| `open notepad` | Opens Notepad |
| `open calculator` | Opens Calculator |
| `open paint` | Opens MS Paint |
| `open explorer` | Opens File Explorer |
| `open vs code` | Opens VS Code |
| `take screenshot` | Saves a screenshot to your Desktop |
| `type Hello World` | Types "Hello World" wherever your cursor is |
| `write Dear friend...` | Types that text |
| `dance` | She dances! 💃 |
| `wave` | She waves at you 👋 |
| `sleep` / `rest` | She goes idle |
| `walk` | She walks across your screen |
| `volume up` | Presses the volume-up key |
| `volume down` | Presses the volume-down key |
| `mute` | Mutes the audio |
| `hide` | Hides the chat panel |

---

## 🖱️ Mouse Controls

| Action | What happens |
|--------|-------------|
| **Left click** her | She reacts with surprise! |
| **Drag** her | Move her anywhere on screen |
| **Right click** her | Quick actions menu |

---

## 🎨 Customise

Open `anime_buddy.py` in any text editor and change:

- **Colors** — edit the color constants at the top of `AnimeCharacter` class:
  ```python
  HAIR  = "#3A1F6E"   # change hair color
  SHIRT = "#6C8EEF"   # change uniform color
  RIBBON= "#EF6CAA"   # change ribbon color
  ```

- **Speed** — change `speed = 2.0` in the `_tick` method

- **Add more apps** — add entries to the `APP_MAP` dictionary:
  ```python
  "firefox": "firefox",
  "my app": "myapp.exe",
  ```

- **Add more commands** — add `elif` blocks in `_handle_command()`

---

## ⚠️ Notes

- For `type` command: click the window you want to type in **before** pressing Send (she waits 1 second)
- Screenshots are saved to your **Desktop**
- The buddy window has **no taskbar icon** — right-click her to quit

---

## 📦 Requirements

- Python 3.8+
- `tkinter` (included with Python)
- `pyautogui` (auto-installed by START_BUDDY.bat)
- `pillow` (auto-installed by START_BUDDY.bat)

---

Made with 💜 — your own anime desktop companion!
