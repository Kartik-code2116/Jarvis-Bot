# ◈ J.A.R.V.I.S — AI Desktop Assistant

A Jarvis-style AI desktop assistant with holographic avatar, Claude AI brain, and real task execution.

## 🚀 Quick Start

Double-click **`START_JARVIS.bat`** — it installs everything and launches.

Or manually:
```
pip install pyautogui pillow requests pygetwindow
python jarvis.py
```

## 💬 Commands

| Command | Action |
|---------|--------|
| `open chrome` | Launch Chrome instantly |
| `open notepad` | Launch Notepad |
| `open vs code` | Launch VS Code |
| `open spotify` | Launch Spotify |
| `take screenshot` | Save to Desktop |
| `type Hello World` | Type text (focus target window first) |
| `search python tutorials` | Google search |
| `youtube lofi music` | YouTube search |
| `what time is it` | Current time |
| `what's today's date` | Current date |
| `volume up` / `volume down` | Audio control |
| `mute` | Mute audio |
| `system info` | PC information |
| `minimize all` | Show desktop |
| `list files` | List home folder |
| `weather Mumbai` | Open weather |
| `play song name` | Play on YouTube |
| Anything else | Natural conversation (needs API key) |

## 🔑 API Key Setup (for full AI)

**Permanent:**
1. Win+R → `sysdm.cpl` → Advanced → Environment Variables
2. New: Name=`ANTHROPIC_API_KEY`, Value=`sk-ant-api03-...`

**Per-session:** Enter key when launcher asks.

Get key at: https://console.anthropic.com

## 🖱️ Controls

- **Drag** avatar to move it anywhere
- **Right-click** avatar for quick menu

## ⚙️ Requirements

- Python 3.8+, Windows 10/11
- pyautogui, pillow, requests (auto-installed)
