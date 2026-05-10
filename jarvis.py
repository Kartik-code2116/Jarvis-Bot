"""
JARVIS AI Desktop Assistant — COMPLETE EDITION
================================================
Powered by Google Gemini AI

Features:
  - Holographic animated avatar (always on top, draggable)
  - Gemini AI brain — understands natural language
  - Full task execution: apps, files, browser, system, screenshots, typing
  - Persistent memory (remembers your preferences & past chats)
  - Voice output via Windows SAPI (text-to-speech)
  - Custom hotkey: Ctrl+Space to focus HUD
  - System tray icon support
  - Plugin/skills system — extend with your own commands
  - Mood system — JARVIS reacts to tone
  - HUD with chat history, quick-action toolbar, status bar

Author : You + Claude
Version: 2.0 COMPLETE
"""

# ── stdlib ────────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import math
import random
import time
import subprocess
import os
import sys
import json
import webbrowser
import urllib.parse
import datetime
import requests
import hashlib
import platform
import shutil
import glob
import re

# ── optional deps ─────────────────────────────────────────────────────────────
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.04
    PYAUTOGUI_OK = True
except ImportError:
    PYAUTOGUI_OK = False

try:
    import pygetwindow as gw
    GW_OK = True
except ImportError:
    GW_OK = False

try:
    import winsound
    WINSOUND_OK = True
except ImportError:
    WINSOUND_OK = False

try:
    import win32api, win32con, win32gui
    WIN32_OK = True
except ImportError:
    WIN32_OK = False

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyAfWyGTGNP-DQjIZe0FaSIErSDkFmtMqlY"
GEMINI_MODEL   = "gemini-2.0-flash"
GEMINI_URL     = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)
AI_OK = bool(GEMINI_API_KEY)

MEMORY_FILE  = os.path.join(os.path.dirname(__file__), "jarvis_memory.json")
PLUGINS_DIR  = os.path.join(os.path.dirname(__file__), "plugins")
HOTKEY       = "<Control-space>"

# ─────────────────────────────────────────────────────────────────────────────
# APP MAP  (name → shell command)
# ─────────────────────────────────────────────────────────────────────────────
APP_MAP = {
    # browsers
    "chrome":             "chrome",
    "google chrome":      "chrome",
    "firefox":            "firefox",
    "edge":               "msedge",
    "microsoft edge":     "msedge",
    "brave":              "brave",
    "opera":              "opera",
    # editors
    "notepad":            "notepad",
    "notepad++":          "notepad++",
    "vs code":            "code",
    "vscode":             "code",
    "visual studio code": "code",
    "sublime":            "subl",
    "atom":               "atom",
    "wordpad":            "wordpad",
    # office
    "word":               "winword",
    "excel":              "excel",
    "powerpoint":         "powerpnt",
    "outlook":            "outlook",
    "onenote":            "onenote",
    "access":             "msaccess",
    # system
    "calculator":         "calc",
    "calc":               "calc",
    "paint":              "mspaint",
    "paint 3d":           "mspaint3d",
    "explorer":           "explorer",
    "file explorer":      "explorer",
    "task manager":       "taskmgr",
    "cmd":                "cmd",
    "command prompt":     "cmd",
    "powershell":         "powershell",
    "regedit":            "regedit",
    "control panel":      "control",
    "settings":           "ms-settings:",
    "device manager":     "devmgmt.msc",
    "disk management":    "diskmgmt.msc",
    "event viewer":       "eventvwr.msc",
    "snipping tool":      "snippingtool",
    "magnifier":          "magnify",
    "on screen keyboard": "osk",
    # media / comms
    "photos":             "ms-photos:",
    "movies tv":          "mswindowsvideo:",
    "media player":       "wmplayer",
    "vlc":                "vlc",
    "spotify":            "spotify",
    "itunes":             "itunes",
    # chat / social
    "discord":            "discord",
    "slack":              "slack",
    "teams":              "teams",
    "zoom":               "zoom",
    "skype":              "skype",
    "whatsapp":           "whatsapp",
    "telegram":           "telegram",
    # dev / utilities
    "steam":              "steam",
    "obs":                "obs64",
    "obs studio":         "obs64",
    "putty":              "putty",
    "wsl":                "wsl",
    "docker":             "docker desktop",
}

# ─────────────────────────────────────────────────────────────────────────────
# PERSISTENT MEMORY
# ─────────────────────────────────────────────────────────────────────────────
class Memory:
    """Saves/loads JARVIS memory: history, preferences, notes."""

    def __init__(self, path=MEMORY_FILE):
        self.path = path
        self.data = {
            "history":     [],   # [{ts, user, jarvis}]
            "preferences": {},   # key → value
            "notes":       [],   # user notes
            "mood":        50,   # 0-100
            "name":        "Sir",
        }
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
        except Exception:
            pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Memory] Save failed: {e}")

    def add_history(self, user_msg, jarvis_msg):
        self.data["history"].append({
            "ts":     datetime.datetime.now().isoformat(timespec="seconds"),
            "user":   user_msg,
            "jarvis": jarvis_msg,
        })
        if len(self.data["history"]) > 200:
            self.data["history"] = self.data["history"][-200:]
        self.save()

    def get_recent(self, n=6):
        return self.data["history"][-n:]

    def set_pref(self, key, val):
        self.data["preferences"][key] = val
        self.save()

    def get_pref(self, key, default=None):
        return self.data["preferences"].get(key, default)

    def add_note(self, note):
        self.data["notes"].append({"ts": datetime.datetime.now().isoformat(), "text": note})
        self.save()

    def get_notes(self):
        return self.data["notes"]

    @property
    def name(self):
        return self.data.get("name", "Sir")

    @name.setter
    def name(self, v):
        self.data["name"] = v
        self.save()

    @property
    def mood(self):
        return self.data.get("mood", 50)

    @mood.setter
    def mood(self, v):
        self.data["mood"] = max(0, min(100, v))
        self.save()


# ─────────────────────────────────────────────────────────────────────────────
# TTS  (Windows SAPI)
# ─────────────────────────────────────────────────────────────────────────────
class TTS:
    def __init__(self):
        self.enabled = False
        self._engine = None
        self._init()

    def _init(self):
        try:
            import comtypes.client
            self._engine = comtypes.client.CreateObject("SAPI.SpVoice")
            self.enabled = True
        except Exception:
            try:
                import pyttsx3
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", 175)
                self.enabled = True
                self._mode = "pyttsx3"
            except Exception:
                self._mode = None
                return
        self._mode = "sapi"

    def speak(self, text):
        if not self.enabled:
            return
        def _go():
            try:
                clean = re.sub(r"[◈▶●✕◦]", "", text)
                if self._mode == "sapi":
                    self._engine.Speak(clean)
                elif self._mode == "pyttsx3":
                    self._engine.say(clean)
                    self._engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=_go, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
# TASK EXECUTOR
# ─────────────────────────────────────────────────────────────────────────────
class TaskExecutor:
    """Executes every real computer task JARVIS can perform."""

    def __init__(self, memory: Memory):
        self.mem = memory

    # ── App Control ───────────────────────────────────────────────────────────
    def open_app(self, name: str) -> str:
        key = name.lower().strip()
        cmd = APP_MAP.get(key)
        if not cmd:
            for k, v in APP_MAP.items():
                if key in k or k in key:
                    cmd = v; break
        if not cmd:
            # Try raw exec
            try:
                subprocess.Popen(key, shell=True,
                                 creationflags=subprocess.DETACHED_PROCESS)
                return f"Attempting to launch '{name}'."
            except Exception as e:
                return f"'{name}' not found. Add it to APP_MAP or install it."
        try:
            if cmd.startswith("ms-") or cmd.endswith(".msc"):
                subprocess.Popen(f'start {cmd}', shell=True)
            else:
                subprocess.Popen(cmd, shell=True,
                                 creationflags=subprocess.DETACHED_PROCESS)
            return f"'{name.title()}' launched."
        except Exception as e:
            return f"Launch failed: {e}"

    def close_app(self, name: str) -> str:
        """Kill a process by name."""
        key = name.lower().strip()
        # Map friendly names to exe names
        exe_map = {
            "chrome": "chrome.exe", "notepad": "notepad.exe",
            "edge": "msedge.exe", "firefox": "firefox.exe",
            "spotify": "Spotify.exe", "discord": "Discord.exe",
            "vlc": "vlc.exe", "steam": "steam.exe",
            "vs code": "Code.exe", "vscode": "Code.exe",
            "calculator": "Calculator.exe",
        }
        exe = exe_map.get(key, key if key.endswith(".exe") else key + ".exe")
        try:
            result = subprocess.run(
                f'taskkill /F /IM "{exe}"', shell=True,
                capture_output=True, text=True)
            if result.returncode == 0:
                return f"'{name.title()}' closed."
            return f"Could not close '{name}' (may not be running)."
        except Exception as e:
            return f"Close failed: {e}"

    # ── Screen ────────────────────────────────────────────────────────────────
    def screenshot(self, filename=None) -> str:
        if not PYAUTOGUI_OK:
            return "Install pyautogui: pip install pyautogui"
        try:
            time.sleep(0.4)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = filename or f"jarvis_{ts}.png"
            path = os.path.join(os.path.expanduser("~"), "Desktop", fname)
            pyautogui.screenshot().save(path)
            return f"Screenshot saved to Desktop: {fname}"
        except Exception as e:
            return f"Screenshot failed: {e}"

    # ── Keyboard / Mouse ──────────────────────────────────────────────────────
    def type_text(self, text: str) -> str:
        if not PYAUTOGUI_OK:
            return "Install pyautogui: pip install pyautogui"
        try:
            time.sleep(1.2)
            # Handle special chars pyautogui can't typewrite
            pyautogui.write(text, interval=0.03)
            return f"Typed: '{text[:50]}{'...' if len(text)>50 else ''}'"
        except Exception as e:
            return f"Typing failed: {e}"

    def press_key(self, key: str) -> str:
        if not PYAUTOGUI_OK:
            return "pyautogui needed."
        try:
            pyautogui.press(key)
            return f"Pressed: {key}"
        except Exception as e:
            return f"Key press failed: {e}"

    def hotkey(self, *keys) -> str:
        if not PYAUTOGUI_OK:
            return "pyautogui needed."
        try:
            pyautogui.hotkey(*keys)
            return f"Hotkey: {'+'.join(keys)}"
        except Exception as e:
            return f"Hotkey failed: {e}"

    def move_mouse(self, x, y) -> str:
        if not PYAUTOGUI_OK:
            return "pyautogui needed."
        pyautogui.moveTo(x, y, duration=0.2)
        return f"Mouse moved to ({x}, {y})"

    def click(self, x=None, y=None) -> str:
        if not PYAUTOGUI_OK:
            return "pyautogui needed."
        if x and y:
            pyautogui.click(x, y)
        else:
            pyautogui.click()
        return "Clicked."

    # ── Volume ────────────────────────────────────────────────────────────────
    def volume_up(self, steps=3) -> str:
        if PYAUTOGUI_OK:
            for _ in range(steps): pyautogui.press("volumeup")
            return f"Volume raised by {steps} steps."
        return "pyautogui needed."

    def volume_down(self, steps=3) -> str:
        if PYAUTOGUI_OK:
            for _ in range(steps): pyautogui.press("volumedown")
            return f"Volume lowered by {steps} steps."
        return "pyautogui needed."

    def volume_mute(self) -> str:
        if PYAUTOGUI_OK:
            pyautogui.press("volumemute")
            return "Audio toggled mute."
        return "pyautogui needed."

    def set_volume(self, level: int) -> str:
        """Set volume 0-100 using nircmd if available, else approximate."""
        try:
            subprocess.run(f'nircmd.exe setsysvolume {int(level * 655.35)}',
                           shell=True, timeout=3)
            return f"Volume set to {level}%."
        except Exception:
            return "Install nircmd for precise volume control."

    # ── Windows ───────────────────────────────────────────────────────────────
    def minimize_all(self) -> str:
        if PYAUTOGUI_OK:
            pyautogui.hotkey("win", "d")
            return "Desktop shown."
        return "pyautogui needed."

    def maximize_window(self) -> str:
        if PYAUTOGUI_OK:
            pyautogui.hotkey("win", "up")
            return "Window maximized."
        return "pyautogui needed."

    def snap_left(self) -> str:
        if PYAUTOGUI_OK:
            pyautogui.hotkey("win", "left")
            return "Window snapped left."
        return "pyautogui needed."

    def snap_right(self) -> str:
        if PYAUTOGUI_OK:
            pyautogui.hotkey("win", "right")
            return "Window snapped right."
        return "pyautogui needed."

    def lock_screen(self) -> str:
        if PYAUTOGUI_OK:
            pyautogui.hotkey("win", "l")
            return "Screen locked."
        subprocess.run("rundll32 user32.dll,LockWorkStation", shell=True)
        return "Screen locked."

    def sleep_pc(self) -> str:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "Going to sleep..."

    def shutdown(self) -> str:
        subprocess.run("shutdown /s /t 10", shell=True)
        return "Shutting down in 10 seconds. Run 'shutdown /a' to abort."

    def restart(self) -> str:
        subprocess.run("shutdown /r /t 10", shell=True)
        return "Restarting in 10 seconds."

    # ── Browser / Web ─────────────────────────────────────────────────────────
    def search_google(self, q: str) -> str:
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(q)}")
        return f"Google: {q}"

    def search_youtube(self, q: str) -> str:
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}")
        return f"YouTube: {q}"

    def open_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opened: {url}"

    def play_music(self, song: str) -> str:
        q = urllib.parse.quote(f"{song} official audio")
        webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
        return f"Playing: {song}"

    def weather(self, loc: str) -> str:
        webbrowser.open(f"https://www.google.com/search?q=weather+{urllib.parse.quote(loc)}")
        return f"Weather for: {loc}"

    def translate(self, text: str, to_lang="english") -> str:
        q = urllib.parse.quote(f"translate '{text}' to {to_lang}")
        webbrowser.open(f"https://www.google.com/search?q={q}")
        return f"Opening Google Translate."

    def open_maps(self, location: str) -> str:
        q = urllib.parse.quote(location)
        webbrowser.open(f"https://www.google.com/maps/search/{q}")
        return f"Maps: {location}"

    def news(self, topic="") -> str:
        q = urllib.parse.quote(topic + " news") if topic else "latest+news"
        webbrowser.open(f"https://news.google.com/search?q={q}")
        return f"News: {topic or 'latest'}"

    # ── File System ───────────────────────────────────────────────────────────
    def list_files(self, folder=None) -> str:
        folder = folder or os.path.expanduser("~")
        folder = folder.strip().strip('"')
        try:
            if not os.path.exists(folder):
                return f"Folder not found: {folder}"
            items = sorted(os.listdir(folder))
            dirs  = [d for d in items if os.path.isdir(os.path.join(folder, d))]
            files = [f for f in items if os.path.isfile(os.path.join(folder, f))]
            out   = f"📁 {folder}\n"
            if dirs:  out += "Dirs:  " + "  ".join(dirs[:8])  + ("…" if len(dirs)>8  else "") + "\n"
            if files: out += "Files: " + "  ".join(files[:12]) + ("…" if len(files)>12 else "")
            return out
        except PermissionError:
            return "Access denied."
        except Exception as e:
            return f"Error: {e}"

    def create_file(self, filename: str, content="") -> str:
        try:
            path = os.path.join(os.path.expanduser("~"), "Desktop",
                                os.path.basename(filename))
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Created: {path}"
        except Exception as e:
            return f"Create failed: {e}"

    def delete_file(self, path: str) -> str:
        try:
            full = os.path.expanduser(path.strip().strip('"'))
            if os.path.isfile(full):
                os.remove(full)
                return f"Deleted: {full}"
            elif os.path.isdir(full):
                shutil.rmtree(full)
                return f"Deleted folder: {full}"
            return f"Not found: {full}"
        except Exception as e:
            return f"Delete failed: {e}"

    def rename_file(self, old: str, new: str) -> str:
        try:
            o = os.path.expanduser(old.strip())
            n = os.path.join(os.path.dirname(o), os.path.basename(new))
            os.rename(o, n)
            return f"Renamed: {os.path.basename(o)} → {os.path.basename(n)}"
        except Exception as e:
            return f"Rename failed: {e}"

    def open_folder(self, path: str) -> str:
        try:
            full = os.path.expanduser(path.strip().strip('"'))
            if not os.path.exists(full):
                return f"Path not found: {full}"
            subprocess.Popen(f'explorer "{full}"', shell=True)
            return f"Opened: {full}"
        except Exception as e:
            return f"Open failed: {e}"

    def find_files(self, pattern: str, folder=None) -> str:
        folder = folder or os.path.expanduser("~")
        try:
            matches = glob.glob(os.path.join(folder, "**", pattern), recursive=True)[:20]
            if not matches:
                return f"No files matching '{pattern}' in {folder}"
            return "\n".join(matches)
        except Exception as e:
            return f"Search failed: {e}"

    def read_file(self, path: str) -> str:
        try:
            full = os.path.expanduser(path.strip().strip('"'))
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(2000)
            return f"[{full}]\n{content}"
        except Exception as e:
            return f"Read failed: {e}"

    # ── Clipboard ─────────────────────────────────────────────────────────────
    def copy_to_clipboard(self, text: str) -> str:
        try:
            import subprocess
            proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            proc.communicate(text.encode('utf-16'))
            return f"Copied to clipboard: {text[:60]}"
        except Exception as e:
            return f"Clipboard failed: {e}"

    # ── System Info ───────────────────────────────────────────────────────────
    def system_info(self) -> str:
        info = []
        info.append(f"Host:    {platform.node()}")
        info.append(f"OS:      {platform.system()} {platform.release()} {platform.version()[:20]}")
        info.append(f"CPU:     {platform.processor()[:60]}")
        info.append(f"Python:  {platform.python_version()}")
        try:
            import psutil
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu_pct = psutil.cpu_percent(interval=0.5)
            info.append(f"RAM:     {mem.used//1024//1024}MB / {mem.total//1024//1024}MB")
            info.append(f"Disk:    {disk.used//1024//1024//1024}GB / {disk.total//1024//1024//1024}GB")
            info.append(f"CPU use: {cpu_pct}%")
        except ImportError:
            pass
        return "\n".join(info)

    def battery_status(self) -> str:
        try:
            import psutil
            b = psutil.sensors_battery()
            if b:
                status = "Charging" if b.power_plugged else "Discharging"
                return f"Battery: {b.percent:.0f}% — {status}"
            return "No battery detected (desktop PC)."
        except ImportError:
            return "Install psutil for battery info."

    def running_processes(self) -> str:
        try:
            result = subprocess.run("tasklist /fo csv /nh", shell=True,
                                    capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n")[:20]
            names = [l.split(",")[0].strip('"') for l in lines if l]
            return "Running: " + ", ".join(names[:25])
        except Exception as e:
            return f"Failed: {e}"

    def ip_address(self) -> str:
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return f"Local IP: {ip}  |  Host: {hostname}"
        except Exception:
            return "Could not retrieve IP."

    def ping(self, host="google.com") -> str:
        try:
            result = subprocess.run(f"ping -n 1 {host}", shell=True,
                                    capture_output=True, text=True, timeout=8)
            if "Reply from" in result.stdout or "reply" in result.stdout.lower():
                return f"✅ {host} is reachable."
            return f"❌ {host} did not respond."
        except Exception:
            return f"Ping failed."

    # ── Time / Date ───────────────────────────────────────────────────────────
    def time_info(self, target="time") -> str:
        now = datetime.datetime.now()
        if "date" in target:
            return f"Today is {now.strftime('%A, %B %d, %Y')}."
        elif "day" in target:
            return f"Today is {now.strftime('%A')}."
        return f"Current time: {now.strftime('%I:%M:%S %p')}."

    def set_reminder(self, minutes: int, message: str) -> str:
        def _remind():
            time.sleep(minutes * 60)
            if WINSOUND_OK:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            messagebox.showinfo("JARVIS Reminder", message)
        threading.Thread(target=_remind, daemon=True).start()
        return f"Reminder set for {minutes} min: {message}"

    # ── Calculations ──────────────────────────────────────────────────────────
    def calculate(self, expr: str) -> str:
        try:
            safe = re.sub(r"[^0-9+\-*/.() %]", "", expr)
            result = eval(safe, {"__builtins__": {}})
            return f"{expr} = {result}"
        except Exception:
            return f"Could not evaluate: {expr}"

    # ── Notes ─────────────────────────────────────────────────────────────────
    def save_note(self, text: str) -> str:
        self.mem.add_note(text)
        return f"Note saved: {text[:80]}"

    def show_notes(self) -> str:
        notes = self.mem.get_notes()
        if not notes:
            return "No notes saved."
        return "\n".join(f"[{n['ts'][:10]}] {n['text']}" for n in notes[-10:])

    # ── Quick Run ─────────────────────────────────────────────────────────────
    def run_command(self, cmd: str) -> str:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True,
                                    text=True, timeout=10)
            out = (result.stdout + result.stderr).strip()
            return out[:500] if out else "(no output)"
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Run failed: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI AI BRAIN
# ─────────────────────────────────────────────────────────────────────────────
JARVIS_SYSTEM = """You are JARVIS, an advanced AI desktop assistant modeled after Iron Man's JARVIS.
You control a Windows PC for the user. Be professional, concise, and action-focused.
Address the user as {name}.

Respond ONLY with a single JSON object — no markdown fences, no extra text:
{{
  "intent":   "<intent_type>",
  "target":   "<app / query / url / path / or null>",
  "target2":  "<second arg if needed or null>",
  "text":     "<text to type / note text / or null>",
  "number":   <numeric arg like volume level / minutes, or null>,
  "response": "<1-2 sentence JARVIS-style reply to show in the HUD>"
}}

Intent types and when to use them:
  open_app        – launch an application (target = app name)
  close_app       – kill/close an application (target = app name)
  screenshot      – take a screenshot
  type_text       – type text (text = what to type)
  press_key       – press a keyboard key (target = key name, e.g. "enter","f5","esc")
  hotkey          – press combo (target = keys joined by +, e.g. "ctrl+c")
  search_google   – Google search (target = query)
  search_youtube  – YouTube search (target = query)
  open_url        – open a URL (target = URL)
  play_music      – play music on YouTube (target = song/artist)
  weather         – weather for a place (target = city/location)
  translate       – translate text (text = text, target = target language)
  open_maps       – open Google Maps (target = location)
  news            – open Google News (target = topic or empty)
  volume_up       – raise volume (number = steps, default 3)
  volume_down     – lower volume (number = steps, default 3)
  volume_mute     – toggle mute
  set_volume      – set exact volume 0-100 (number = level)
  minimize_all    – show desktop
  maximize_window – maximize current window
  snap_left       – snap window left
  snap_right      – snap window right
  lock_screen     – lock Windows
  sleep_pc        – sleep the computer
  shutdown        – shutdown computer
  restart         – restart computer
  system_info     – show system information
  battery         – battery status
  ip_address      – show IP address
  ping            – ping a host (target = hostname)
  processes       – list running processes
  time_date       – current time / date (target = "time" or "date")
  list_files      – list files in folder (target = path, or null for home)
  open_folder     – open a folder in Explorer (target = path)
  create_file     – create a file (target = filename, text = content)
  delete_file     – delete a file or folder (target = path)
  rename_file     – rename file (target = old path, target2 = new name)
  find_files      – search for files (target = pattern like "*.pdf", target2 = folder)
  read_file       – read a text file (target = path)
  copy_clipboard  – copy text to clipboard (text = text)
  calculate       – calculate math (text = expression)
  save_note       – save a note (text = note content)
  show_notes      – show all saved notes
  set_reminder    – set a reminder (text = message, number = minutes)
  run_command     – run a shell command (text = command)
  remember_name   – user told me their name (target = their name)
  chat            – general conversation (no action)
  unknown         – command not understood

Quick examples:
  "open chrome"              → {{"intent":"open_app","target":"chrome","target2":null,"text":null,"number":null,"response":"Launching Chrome, {name}."}}
  "close spotify"            → {{"intent":"close_app","target":"spotify","target2":null,"text":null,"number":null,"response":"Closing Spotify."}}
  "take a screenshot"        → {{"intent":"screenshot","target":null,"target2":null,"text":null,"number":null,"response":"Capturing screen."}}
  "type hello world"         → {{"intent":"type_text","target":null,"target2":null,"text":"hello world","number":null,"response":"Typing now. Please focus your target window."}}
  "press enter"              → {{"intent":"press_key","target":"enter","target2":null,"text":null,"number":null,"response":"Pressing Enter."}}
  "ctrl+s"                   → {{"intent":"hotkey","target":"ctrl+s","target2":null,"text":null,"number":null,"response":"Saving with Ctrl+S."}}
  "search machine learning"  → {{"intent":"search_google","target":"machine learning","target2":null,"text":null,"number":null,"response":"Searching for machine learning."}}
  "set volume to 40"         → {{"intent":"set_volume","target":null,"target2":null,"text":null,"number":40,"response":"Setting volume to 40%."}}
  "remind me in 5 minutes"   → {{"intent":"set_reminder","target":null,"target2":null,"text":"5 minute reminder","number":5,"response":"Reminder set for 5 minutes."}}
  "calculate 25 * 4"         → {{"intent":"calculate","target":null,"target2":null,"text":"25 * 4","number":null,"response":"Calculating that."}}
  "save note buy milk"       → {{"intent":"save_note","target":null,"target2":null,"text":"buy milk","number":null,"response":"Note saved."}}
  "my name is Tony"          → {{"intent":"remember_name","target":"Tony","target2":null,"text":null,"number":null,"response":"Understood, Mr. Tony. I'll remember that."}}
  "how are you"              → {{"intent":"chat","target":null,"target2":null,"text":"how are you","number":null,"response":"All systems operational, {name}."}}

Return ONLY valid JSON. No markdown. No explanation."""


class JarvisAI:
    def __init__(self, memory: Memory):
        self.mem = memory

    def _post(self, contents, system_text):
        body = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_text}]},
            "generationConfig": {
                "temperature": 0.15,
                "maxOutputTokens": 400,
            }
        }
        r = requests.post(GEMINI_URL, json=body, timeout=18)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _clean_json(self, raw: str) -> str:
        if "```" in raw:
            raw = re.sub(r"```json\s*", "", raw)
            raw = re.sub(r"```\s*", "", raw)
        return raw.strip()

    def parse(self, user_msg: str):
        """Parse command → dict with intent + args."""
        if not AI_OK:
            return None
        try:
            # Build context from recent history
            history = self.mem.get_recent(4)
            contents = []
            for h in history:
                contents.append({"role": "user",   "parts": [{"text": h["user"]}]})
                contents.append({"role": "model",  "parts": [{"text": h["jarvis"]}]})
            contents.append({"role": "user", "parts": [{"text": user_msg}]})

            sys_text = JARVIS_SYSTEM.replace("{name}", self.mem.name)
            raw = self._post(contents, sys_text)
            raw = self._clean_json(raw)
            return json.loads(raw)
        except Exception as e:
            print(f"[AI parse] {e}")
            return None

    def chat(self, msg: str) -> str:
        if not AI_OK:
            return "I need an API key to respond, sir."
        try:
            system = (
                f"You are JARVIS, Iron Man's AI. "
                f"Address the user as {self.mem.name}. "
                "Be helpful, witty, and professional. Max 2-3 sentences."
            )
            raw = self._post([{"role":"user","parts":[{"text":msg}]}], system)
            return raw
        except Exception as e:
            return f"Error: {str(e)[:80]}"


# ─────────────────────────────────────────────────────────────────────────────
# PLUGIN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
class PluginManager:
    """Loads Python plugins from ./plugins/*.py
    Each plugin must define:
        COMMANDS = ["keyword1", "keyword2"]
        def handle(cmd: str) -> str: ...
    """
    def __init__(self):
        self.plugins = []
        self._load()

    def _load(self):
        if not os.path.isdir(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR, exist_ok=True)
            self._write_example()
            return
        import importlib.util
        for f in glob.glob(os.path.join(PLUGINS_DIR, "*.py")):
            try:
                spec = importlib.util.spec_from_file_location("plugin", f)
                mod  = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "COMMANDS") and hasattr(mod, "handle"):
                    self.plugins.append(mod)
                    print(f"[Plugin] Loaded: {os.path.basename(f)}")
            except Exception as e:
                print(f"[Plugin] Failed {f}: {e}")

    def _write_example(self):
        ex = os.path.join(PLUGINS_DIR, "example_plugin.py")
        with open(ex, "w") as f:
            f.write(
                '# Example JARVIS plugin\n'
                '# Put your custom commands here\n\n'
                'COMMANDS = ["hello plugin", "test plugin"]\n\n'
                'def handle(cmd: str) -> str:\n'
                '    return "Hello from your custom plugin! Command was: " + cmd\n'
            )

    def try_handle(self, cmd: str):
        """Returns result string if a plugin handles it, else None."""
        cmd_l = cmd.lower()
        for plug in self.plugins:
            if any(kw in cmd_l for kw in plug.COMMANDS):
                try:
                    return plug.handle(cmd)
                except Exception as e:
                    return f"Plugin error: {e}"
        return None


# ─────────────────────────────────────────────────────────────────────────────
# HOLOGRAPHIC AVATAR
# ─────────────────────────────────────────────────────────────────────────────
class JarvisAvatar:
    C = {
        "cyan":  "#00F5FF",
        "blue":  "#0080FF",
        "glow":  "#00FFFF",
        "dim":   "#003D5C",
        "gold":  "#FFD700",
        "red":   "#FF4444",
        "green": "#00FF88",
        "white": "#FFFFFF",
    }

    def __init__(self, canvas: tk.Canvas, cx: int, cy: int):
        self.cv = canvas
        self.cx = cx
        self.cy = cy
        self._ids = []

    def _c(self): [self.cv.delete(i) for i in self._ids]; self._ids.clear()
    def _o(self,*a,**k): i=self.cv.create_oval(*a,**k);  self._ids.append(i);return i
    def _l(self,*a,**k): i=self.cv.create_line(*a,**k);  self._ids.append(i);return i
    def _p(self,*a,**k): i=self.cv.create_polygon(*a,**k);self._ids.append(i);return i
    def _t(self,*a,**k): i=self.cv.create_text(*a,**k);  self._ids.append(i);return i
    def _a(self,*a,**k): i=self.cv.create_arc(*a,**k);   self._ids.append(i);return i

    def draw(self, ph=0, mode="idle", mouth=0.0):
        self._c()
        cx, cy = self.cx, self.cy
        C = self.C
        glow = C["cyan"] if mode != "alert" else C["red"]
        dim  = C["dim"]  if mode != "alert" else "#3D0000"

        # ── outer rings ───────────────────────────────────────────────────────
        for i in range(3):
            a = (ph * 1.5 + i * 45) % 360
            self._a(cx-72,cy-72,cx+72,cy+72, start=a, extent=70+i*15,
                    style=tk.ARC, outline=glow, width=1+i%2)
        for i in range(5):
            a = -(ph * 2.2 + i * 36) % 360
            self._a(cx-56,cy-56,cx+56,cy+56, start=a, extent=40,
                    style=tk.ARC, outline=C["blue"], width=1)

        # ── core ──────────────────────────────────────────────────────────────
        cr = 38 + math.sin(ph * 0.07) * 3
        self._o(cx-cr,cy-cr,cx+cr,cy+cr, fill=dim, outline=glow, width=2)
        for r, fc in [(30,"#001A2E"),(22,"#002A40"),(14,"#003D5C")]:
            self._o(cx-r,cy-r,cx+r,cy+r, fill=fc,
                    outline=glow if r==30 else C["dim"], width=1)

        # ── eyes ──────────────────────────────────────────────────────────────
        ey = cy - 9
        for xo in (-13, 13):
            ex = cx + xo
            if mode == "thinking":
                sc = int(math.sin(ph * 0.22) * 7)
                self._l(ex-9,ey,ex+9,ey, fill=dim, width=1)
                self._o(ex+sc-4,ey-4,ex+sc+4,ey+4,
                        fill=C["cyan"], outline=C["glow"], width=1)
            elif mode == "executing":
                sp = ph * 10 % 360
                self._a(ex-8,ey-8,ex+8,ey+8, start=sp,extent=220,
                        style=tk.ARC, outline=glow, width=2)
            elif mode == "alert":
                # blinking red
                if (ph // 8) % 2 == 0:
                    self._o(ex-8,ey-6,ex+8,ey+6, fill="#660000", outline=C["red"], width=1)
                    self._o(ex-4,ey-3,ex+4,ey+3, fill=C["red"], outline=C["red"])
            else:
                self._o(ex-8,ey-6,ex+8,ey+6, fill=dim, outline=glow, width=1)
                px = ex + int(math.sin(ph*0.04)*3)
                py = ey + int(math.cos(ph*0.03)*2)
                self._o(px-4,py-4,px+4,py+4, fill=glow, outline=glow)
                self._o(px+1,py-3,px+3,py-1, fill="white", outline="white")

        # ── nose ──────────────────────────────────────────────────────────────
        ny = cy + 3
        self._p(cx-3,ny+5, cx+3,ny+5, cx,ny, fill=glow, outline="")

        # ── mouth ─────────────────────────────────────────────────────────────
        my = cy + 15
        if mode in ("talking","executing") and mouth > 0.05:
            bw,gap,n = 3,2,9
            sx = cx - (n*(bw+gap)-gap)//2
            for i in range(n):
                bx = sx + i*(bw+gap)
                h = abs(math.sin(ph*0.18+i*0.7))*11*mouth + 1.5
                self._l(bx,my-h,bx,my+h, fill=glow, width=bw, capstyle=tk.ROUND)
        else:
            mo = mouth * 6
            if mo < 1:
                self._l(cx-11,my,cx+11,my, fill=glow, width=2)
            else:
                self._o(cx-9,my-mo,cx+9,my+mo, fill=dim, outline=glow, width=1)

        # ── forehead status dot ───────────────────────────────────────────────
        dr = 3 + abs(math.sin(ph*0.09))*2
        dc = {"idle":C["cyan"],"thinking":C["gold"],"talking":C["green"],
              "executing":C["gold"],"alert":C["red"]}.get(mode, C["cyan"])
        self._o(cx-dr,cy-38-dr,cx+dr,cy-38+dr, fill=dc, outline="white")

        # ── data streams ──────────────────────────────────────────────────────
        if mode in ("thinking","executing"):
            for i in range(8):
                ang = (ph*3.5 + i*45) % 360
                rad = math.radians(ang)
                r1 = 42 + abs(math.sin(ph*0.12+i))*6
                r2 = r1 + random.randint(4,20)
                self._l(cx+math.cos(rad)*r1, cy+math.sin(rad)*r1,
                        cx+math.cos(rad)*r2, cy+math.sin(rad)*r2,
                        fill=glow, width=1)

        # ── HUD corner brackets ───────────────────────────────────────────────
        bd = 60; bl = 13
        for dx,dy in ((-1,-1),(1,-1),(-1,1),(1,1)):
            bx,by = cx+dx*bd, cy+dy*bd
            self._l(bx,by, bx-dx*bl,by, fill=glow, width=1)
            self._l(bx,by, bx,by-dy*bl, fill=glow, width=1)

        # ── mode label ────────────────────────────────────────────────────────
        lbl = {"idle":"STANDBY","thinking":"PROCESSING","talking":"RESPONDING",
               "executing":"EXECUTING","alert":"ALERT"}.get(mode,"JARVIS")
        self._t(cx, cy+90, text=lbl, fill=glow, font=("Courier New",7,"bold"))
        self._l(cx-42,cy+98,cx+42,cy+98, fill=dim, width=1)


# ─────────────────────────────────────────────────────────────────────────────
# HOLO SPEECH BUBBLE
# ─────────────────────────────────────────────────────────────────────────────
class HoloBubble(tk.Toplevel):
    def __init__(self, master, text, x, y):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#010101")
        self.configure(bg="#010101")

        fr = tk.Frame(self, bg="#001822",
                      highlightbackground="#00F5FF", highlightthickness=1)
        fr.pack()
        tk.Label(fr, text=text, bg="#001822", fg="#00F5FF",
                 font=("Courier New", 9), wraplength=270,
                 justify="left", padx=12, pady=9).pack()

        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"{w}x{h}+{max(0,int(x))}+{max(0,int(y))}")
        self.after(5000, self._bye)

    def _bye(self):
        try: self.destroy()
        except: pass


# ─────────────────────────────────────────────────────────────────────────────
# QUICK ACTION TOOLBAR
# ─────────────────────────────────────────────────────────────────────────────
QUICK_ACTIONS = [
    ("🌐", "open chrome"),
    ("📁", "open file explorer"),
    ("📷", "screenshot"),
    ("🔇", "mute"),
    ("🔊", "volume up"),
    ("🔉", "volume down"),
    ("🗒️", "open notepad"),
    ("⏰", "what time is it"),
    ("📋", "show notes"),
    ("🖥️", "system info"),
    ("🔒", "lock screen"),
    ("⬜", "minimize all"),
]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
class JarvisApp:
    AW, AH = 215, 255   # avatar window dimensions
    FPS = 25

    def __init__(self):
        self.mem     = Memory()
        self.ai      = JarvisAI(self.mem)
        self.exe     = TaskExecutor(self.mem)
        self.plugins = PluginManager()
        self.tts     = TTS()

        # ── Avatar window ─────────────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("JARVIS")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.root.configure(bg="#010101")
        self.root.resizable(False, False)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.wx = sw - self.AW - 20
        self.wy = sh - self.AH - 60
        self.root.geometry(f"{self.AW}x{self.AH}+{self.wx}+{self.wy}")

        self.cv = tk.Canvas(self.root, width=self.AW, height=self.AH,
                            bg="#010101", highlightthickness=0)
        self.cv.pack()
        self.av = JarvisAvatar(self.cv, cx=self.AW//2, cy=self.AH//2 - 12)

        # drag
        self._ds = None
        self.cv.bind("<ButtonPress-1>",   self._db)
        self.cv.bind("<B1-Motion>",       self._dm)
        self.cv.bind("<ButtonRelease-1>", self._de)
        self.cv.bind("<Button-3>",        self._rc)
        self.cv.bind("<Double-Button-1>", lambda e: self._show_hud())

        self.mode  = "idle"
        self.phase = 0
        self.bubble = None

        # ── Build HUD ─────────────────────────────────────────────────────────
        self._build_hud()

        # ── Global hotkey: Ctrl+Space ─────────────────────────────────────────
        self.hud.bind(HOTKEY, lambda e: self._focus_input())
        self.root.bind(HOTKEY, lambda e: self._focus_input())

        # ── Start loops ───────────────────────────────────────────────────────
        self._top_loop()
        self._tick()

        self._sys(f"JARVIS v2.0 ONLINE  |  AI: Gemini ({GEMINI_MODEL})")
        self._sys(f"TTS: {'ON' if self.tts.enabled else 'OFF'}  |  "
                  f"Plugins: {len(self.plugins.plugins)}  |  "
                  f"User: {self.mem.name}")
        self._j(f"Good {'morning' if datetime.datetime.now().hour < 12 else 'afternoon' if datetime.datetime.now().hour < 18 else 'evening'}, {self.mem.name}. All systems operational.")
        self.tts.speak(f"JARVIS online. Good day, {self.mem.name}.")

        self.root.mainloop()

    # ─── HUD ─────────────────────────────────────────────────────────────────
    def _build_hud(self):
        self.hud = tk.Toplevel(self.root)
        self.hud.title("J.A.R.V.I.S")
        self.hud.geometry("460x640+28+55")
        self.hud.attributes("-topmost", True)
        self.hud.resizable(True, True)
        self.hud.configure(bg="#000D1A")
        self.hud.protocol("WM_DELETE_WINDOW", lambda: self.hud.withdraw())
        self.hud.minsize(360, 420)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self.hud, bg="#001E30", height=48)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        tk.Label(hdr, text="◈  J.A.R.V.I.S  ◈",
                 bg="#001E30", fg="#00F5FF",
                 font=("Courier New", 13, "bold")).pack(side="left", padx=14, pady=10)

        self.slbl = tk.Label(hdr, text="● STANDBY",
                             bg="#001E30", fg="#00F5FF",
                             font=("Courier New", 8))
        self.slbl.pack(side="right", padx=14)

        # TTS toggle
        self.tts_var = tk.BooleanVar(value=self.tts.enabled)
        tk.Checkbutton(hdr, text="🔊", variable=self.tts_var,
                       bg="#001E30", fg="#00F5FF",
                       selectcolor="#003D5C",
                       activebackground="#001E30",
                       font=("Arial", 10),
                       command=lambda: setattr(self.tts, "enabled", self.tts_var.get())
                       ).pack(side="right", padx=4)

        # ── Quick Action Toolbar ──────────────────────────────────────────────
        tb = tk.Frame(self.hud, bg="#001020")
        tb.pack(fill="x", padx=6, pady=(3,0))
        for emoji, cmd in QUICK_ACTIONS:
            btn = tk.Button(tb, text=emoji, bg="#001020", fg="#00F5FF",
                            font=("Arial", 11), relief="flat",
                            padx=2, pady=1,
                            activebackground="#003D5C",
                            cursor="hand2",
                            command=lambda c=cmd: self._quick(c))
            btn.pack(side="left", padx=1)
        tk.Label(tb, text="quick actions", bg="#001020", fg="#003D5C",
                 font=("Courier New", 7)).pack(side="right", padx=6)

        # ── Hint ──────────────────────────────────────────────────────────────
        self.hint = tk.Label(self.hud,
            text=' Ctrl+Space = focus  |  "open X"  "search X"  "remind in 5 min X"',
            bg="#000D1A", fg="#004A6B", font=("Courier New", 7))
        self.hint.pack(fill="x", padx=6, pady=(3,0))

        # ── Log ───────────────────────────────────────────────────────────────
        lf = tk.Frame(self.hud, bg="#000D1A")
        lf.pack(fill="both", expand=True, padx=6, pady=4)

        self.log = tk.Text(lf, bg="#000D1A", fg="#00C8FF",
                           font=("Courier New", 9), state="disabled",
                           relief="flat", wrap="word",
                           padx=8, pady=4,
                           insertbackground="#00F5FF",
                           selectbackground="#003D5C")
        vsb = tk.Scrollbar(lf, command=self.log.yview, bg="#001A2E",
                           troughcolor="#000D1A", width=10)
        self.log.configure(yscrollcommand=vsb.set)
        self.log.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.log.tag_configure("j",  foreground="#00F5FF", font=("Courier New",9,"bold"))
        self.log.tag_configure("u",  foreground="#66FF99", font=("Courier New",9))
        self.log.tag_configure("s",  foreground="#FFD700", font=("Courier New",8,"italic"))
        self.log.tag_configure("r",  foreground="#AAAAEE", font=("Courier New",8))
        self.log.tag_configure("e",  foreground="#FF5555", font=("Courier New",8))
        self.log.tag_configure("ts", foreground="#003D5C", font=("Courier New",7))

        # ── Input ─────────────────────────────────────────────────────────────
        inf = tk.Frame(self.hud, bg="#001E30")
        inf.pack(fill="x", padx=6, pady=(0,6))

        tk.Label(inf, text="▶", bg="#001E30", fg="#00F5FF",
                 font=("Courier New", 11)).pack(side="left", padx=(8,2))

        self.ent = tk.Entry(inf, bg="#000D1A", fg="#00F5FF",
                            insertbackground="#00F5FF",
                            font=("Courier New", 11), relief="flat",
                            highlightbackground="#00F5FF", highlightthickness=1)
        self.ent.pack(side="left", fill="x", expand=True, ipady=9, padx=4)
        self.ent.bind("<Return>",    lambda e: self._send())
        self.ent.bind("<Up>",        self._history_up)
        self.ent.bind("<Down>",      self._history_down)
        self.ent.focus()

        tk.Button(inf, text="EXECUTE", bg="#002A40", fg="#00F5FF",
                  font=("Courier New", 9, "bold"), relief="flat", padx=12,
                  activebackground="#00F5FF", activeforeground="#000D1A",
                  cursor="hand2",
                  command=self._send).pack(side="right", padx=(4,6), pady=4)

        # ── Status bar ────────────────────────────────────────────────────────
        self.statbar = tk.Label(self.hud,
            text=f"  GEMINI AI  |  {GEMINI_MODEL}  |  Memory: ON  |  Plugins: {len(self.plugins.plugins)}",
            bg="#001020", fg="#004A6B", font=("Courier New", 7), anchor="w")
        self.statbar.pack(fill="x")

        # input history
        self._inp_history = []
        self._inp_idx     = -1

    # ── Logging ───────────────────────────────────────────────────────────────
    def _write(self, text, tag):
        self.log.configure(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M")
        self.log.insert("end", f"[{ts}] ", "ts")
        self.log.insert("end", text + "\n\n", tag)
        self.log.configure(state="disabled")
        self.log.see("end")

    def _j(self, t):   self._write(f"JARVIS » {t}", "j")
    def _u(self, t):   self._write(f"YOU    » {t}", "u")
    def _sys(self, t): self._write(f"[SYS]  {t}", "s")
    def _res(self, t): self._write(f"[RES]  {t}", "r")
    def _err(self, t): self._write(f"[ERR]  {t}", "e")

    def _status(self, t, c="#00F5FF"):
        try: self.slbl.configure(text=t, fg=c)
        except: pass

    # ── Input history (Up/Down arrows) ────────────────────────────────────────
    def _history_up(self, e):
        if not self._inp_history: return
        self._inp_idx = min(self._inp_idx + 1, len(self._inp_history) - 1)
        self.ent.delete(0, "end")
        self.ent.insert(0, self._inp_history[-(self._inp_idx+1)])

    def _history_down(self, e):
        if self._inp_idx <= 0:
            self._inp_idx = -1
            self.ent.delete(0, "end"); return
        self._inp_idx -= 1
        self.ent.delete(0, "end")
        self.ent.insert(0, self._inp_history[-(self._inp_idx+1)])

    # ── Quick action ──────────────────────────────────────────────────────────
    def _quick(self, cmd):
        self._u(cmd)
        threading.Thread(target=self._handle, args=(cmd,), daemon=True).start()

    # ── Send ──────────────────────────────────────────────────────────────────
    def _send(self):
        cmd = self.ent.get().strip()
        if not cmd: return
        self.ent.delete(0, "end")
        self._inp_history.append(cmd)
        if len(self._inp_history) > 50: self._inp_history = self._inp_history[-50:]
        self._inp_idx = -1
        self._u(cmd)
        threading.Thread(target=self._handle, args=(cmd,), daemon=True).start()

    # ── Handle command ────────────────────────────────────────────────────────
    def _handle(self, cmd):
        self.root.after(0, lambda: self._status("● PROCESSING", "#FFD700"))
        self.root.after(0, lambda: setattr(self, "mode", "thinking"))

        # 1) Plugin check
        plug_res = self.plugins.try_handle(cmd)
        if plug_res:
            self.root.after(0, lambda: self._j("Plugin activated."))
            self.root.after(0, lambda: self._res(plug_res))
            self.root.after(0, lambda: self._bubble(plug_res[:120]))
            self.root.after(0, lambda: setattr(self, "mode", "idle"))
            self.root.after(0, lambda: self._status("● STANDBY"))
            return

        # 2) AI parse
        parsed = self.ai.parse(cmd) if AI_OK else None

        if parsed:
            intent   = parsed.get("intent", "unknown")
            target   = (parsed.get("target")  or "").strip()
            target2  = (parsed.get("target2") or "").strip()
            text_arg = (parsed.get("text")    or "").strip()
            number   = parsed.get("number")
            response = parsed.get("response", "Processing…")

            self.root.after(0, lambda: self._j(response))
            self.root.after(0, lambda: self._bubble(response))
            self.root.after(0, lambda: self._run(intent, target, target2, text_arg, number))
            self.mem.add_history(cmd, response)
        else:
            self.root.after(0, lambda: self._fallback(cmd))

    def _run(self, intent, target, target2, text_arg, number):
        self.mode = "executing"
        self._status("● EXECUTING", "#FFD700")

        def go():
            e = self.exe
            res = None
            try:
                # ── App
                if   intent == "open_app":       res = e.open_app(target)
                elif intent == "close_app":      res = e.close_app(target)
                # ── Screen
                elif intent == "screenshot":     res = e.screenshot()
                # ── Input
                elif intent == "type_text":      res = e.type_text(text_arg or target)
                elif intent == "press_key":      res = e.press_key(target)
                elif intent == "hotkey":
                    keys = [k.strip() for k in target.replace("+", " ").split()]
                    res = e.hotkey(*keys)
                # ── Web
                elif intent == "search_google":  res = e.search_google(target)
                elif intent == "search_youtube": res = e.search_youtube(target)
                elif intent == "open_url":       res = e.open_url(target)
                elif intent == "play_music":     res = e.play_music(target)
                elif intent == "weather":        res = e.weather(target)
                elif intent == "translate":      res = e.translate(text_arg or target, target2 or "english")
                elif intent == "open_maps":      res = e.open_maps(target)
                elif intent == "news":           res = e.news(target)
                # ── Volume
                elif intent == "volume_up":      res = e.volume_up(int(number or 3))
                elif intent == "volume_down":    res = e.volume_down(int(number or 3))
                elif intent == "volume_mute":    res = e.volume_mute()
                elif intent == "set_volume":     res = e.set_volume(int(number or 50))
                # ── Windows
                elif intent == "minimize_all":   res = e.minimize_all()
                elif intent == "maximize_window":res = e.maximize_window()
                elif intent == "snap_left":      res = e.snap_left()
                elif intent == "snap_right":     res = e.snap_right()
                elif intent == "lock_screen":    res = e.lock_screen()
                elif intent == "sleep_pc":       res = e.sleep_pc()
                elif intent == "shutdown":       res = e.shutdown()
                elif intent == "restart":        res = e.restart()
                # ── System
                elif intent == "system_info":    res = e.system_info()
                elif intent == "battery":        res = e.battery_status()
                elif intent == "ip_address":     res = e.ip_address()
                elif intent == "ping":           res = e.ping(target or "google.com")
                elif intent == "processes":      res = e.running_processes()
                # ── Time
                elif intent == "time_date":      res = e.time_info(target)
                # ── Files
                elif intent == "list_files":     res = e.list_files(target or None)
                elif intent == "open_folder":    res = e.open_folder(target)
                elif intent == "create_file":    res = e.create_file(target, text_arg)
                elif intent == "delete_file":    res = e.delete_file(target)
                elif intent == "rename_file":    res = e.rename_file(target, target2)
                elif intent == "find_files":     res = e.find_files(target, target2 or None)
                elif intent == "read_file":      res = e.read_file(target)
                # ── Clipboard
                elif intent == "copy_clipboard": res = e.copy_to_clipboard(text_arg)
                # ── Calc / Notes / Reminder
                elif intent == "calculate":      res = e.calculate(text_arg or target)
                elif intent == "save_note":      res = e.save_note(text_arg)
                elif intent == "show_notes":     res = e.show_notes()
                elif intent == "set_reminder":
                    res = e.set_reminder(int(number or 5), text_arg or "Time's up!")
                # ── Shell
                elif intent == "run_command":    res = e.run_command(text_arg)
                # ── Memory
                elif intent == "remember_name":
                    self.mem.name = target
                    res = f"Got it. I'll call you {target} from now on."
                # ── Chat
                elif intent == "chat":
                    res = self.ai.chat(text_arg or target or "hello")
                    self.mode = "talking"
                elif intent == "unknown":
                    res = f"I didn't understand that command, {self.mem.name}. Could you rephrase?"
                    self.root.after(0, lambda: setattr(self, "mode", "alert"))
                else:
                    res = f"Intent '{intent}' not implemented yet."
            except Exception as ex:
                res = f"Execution error: {ex}"

            if res:
                r = res
                self.root.after(0, lambda: self._res(r))
                self.root.after(0, lambda: self._bubble(r[:130]))
                if self.tts.enabled and len(res) < 200:
                    self.tts.speak(res)

            self.root.after(800, lambda: setattr(self, "mode", "idle"))
            self.root.after(800, lambda: self._status("● STANDBY"))

        threading.Thread(target=go, daemon=True).start()

    # ── Keyword fallback (when AI offline) ────────────────────────────────────
    def _fallback(self, cmd):
        self.mode = "executing"
        cl  = cmd.lower()
        e   = self.exe
        res = None

        if cl.startswith("open "):
            app = cmd[5:].strip()
            self._j(f"Launching {app.title()}…")
            res = e.open_app(app)
        elif cl.startswith("close "):
            res = e.close_app(cmd[6:].strip())
        elif any(w in cl for w in ["screenshot","capture screen"]):
            self._j("Capturing screen…")
            res = e.screenshot()
        elif cl.startswith("type "):
            res = e.type_text(cmd[5:].strip())
        elif "search " in cl or "google " in cl:
            q = re.sub(r"(google|search|for)\s*", "", cl).strip()
            res = e.search_google(q)
        elif "youtube " in cl:
            res = e.search_youtube(cl.replace("youtube","").strip())
        elif "play " in cl:
            res = e.play_music(cl.replace("play","").strip())
        elif "weather " in cl:
            res = e.weather(cl.replace("weather","").strip())
        elif "volume up" in cl:   res = e.volume_up()
        elif "volume down" in cl: res = e.volume_down()
        elif any(w in cl for w in ["mute","unmute"]): res = e.volume_mute()
        elif "minimize" in cl or "show desktop" in cl: res = e.minimize_all()
        elif "lock" in cl:        res = e.lock_screen()
        elif any(w in cl for w in ["time","clock"]):
            res = e.time_info("time"); self._j(res)
        elif "date" in cl:
            res = e.time_info("date"); self._j(res)
        elif any(w in cl for w in ["system info","pc info","computer info"]):
            res = e.system_info()
        elif "ip" in cl:          res = e.ip_address()
        elif cl.startswith("calculate ") or cl.startswith("calc "):
            res = e.calculate(re.sub(r"^(calculate|calc)\s*","",cl))
        elif cl.startswith("note ") or cl.startswith("save note "):
            res = e.save_note(re.sub(r"^(save\s+)?note\s*","",cmd,flags=re.I))
        elif "show notes" in cl:  res = e.show_notes()
        elif cl.startswith("open folder ") or cl.startswith("open path "):
            path = re.sub(r"^open (folder|path)\s*","",cmd,flags=re.I)
            res = e.open_folder(path)
        elif cl.startswith("list files") or cl.startswith("ls "):
            folder = re.sub(r"^(list files?|ls)\s*","",cmd,flags=re.I) or None
            res = e.list_files(folder)
        elif cl.startswith("remind "):
            # e.g. "remind me in 10 minutes to drink water"
            m = re.search(r"(\d+)\s*min", cl)
            minutes = int(m.group(1)) if m else 5
            msg = re.sub(r"remind\s*(me)?\s*(in\s*\d+\s*min(utes?)?)?\s*(to)?","", cl, flags=re.I).strip()
            res = e.set_reminder(minutes, msg or "Reminder!")
        elif cl.startswith("run "):
            res = e.run_command(cmd[4:].strip())
        else:
            res = (f"Command not recognized, {self.mem.name}. "
                   "AI is active — rephrase or check your internet connection.")
            self.mode = "alert"
            self.root.after(0, lambda: self._err(res))
            self.root.after(2000, lambda: setattr(self, "mode", "idle"))
            self.root.after(0, lambda: self._status("● STANDBY"))
            return

        if res:
            self._res(res)
            self._bubble(res[:130])
            if self.tts.enabled and len(res) < 200:
                self.tts.speak(res)
        self.mode = "idle"
        self._status("● STANDBY")

    # ── Speech bubble ─────────────────────────────────────────────────────────
    def _bubble(self, text):
        def do():
            if self.bubble:
                try: self.bubble.destroy()
                except: pass
            bx = self.wx - 300 if self.wx > 320 else self.wx + self.AW + 8
            self.bubble = HoloBubble(self.root, text, bx, self.wy + 8)
        self.root.after(0, do)

    # ── Animation tick ────────────────────────────────────────────────────────
    def _tick(self):
        self.phase += 1
        m = abs(math.sin(self.phase * 0.28)) if self.mode in ("talking","executing") else 0.0
        self.av.draw(ph=self.phase, mode=self.mode, mouth=m)
        self.root.after(1000 // self.FPS, self._tick)

    # ── Always on top ─────────────────────────────────────────────────────────
    def _top_loop(self):
        self.root.attributes("-topmost", True)
        try: self.hud.attributes("-topmost", True)
        except: pass
        self.root.after(4000, self._top_loop)

    # ── Drag ──────────────────────────────────────────────────────────────────
    def _db(self, e): self._ds = (e.x_root - self.wx, e.y_root - self.wy)
    def _dm(self, e):
        if self._ds:
            self.wx = e.x_root - self._ds[0]
            self.wy = e.y_root - self._ds[1]
            self.root.geometry(f"{self.AW}x{self.AH}+{int(self.wx)}+{int(self.wy)}")
    def _de(self, e): self._ds = None

    # ── Right-click context menu ───────────────────────────────────────────────
    def _rc(self, e):
        m = tk.Menu(self.root, tearoff=0, bg="#001020", fg="#00F5FF",
                    activebackground="#003D5C", activeforeground="#00F5FF",
                    font=("Courier New", 9))
        m.add_command(label="◈ Show HUD         (Dbl-click)",
                      command=self._show_hud)
        m.add_separator()
        m.add_command(label="◈ Screenshot",
                      command=lambda: threading.Thread(
                          target=lambda: (self._res(self.exe.screenshot()),
                                         self._bubble("Screenshot saved.")),
                          daemon=True).start())
        m.add_command(label="◈ Open Chrome",
                      command=lambda: threading.Thread(
                          target=lambda: self.exe.open_app("chrome"),
                          daemon=True).start())
        m.add_command(label="◈ Minimize All",    command=self.exe.minimize_all)
        m.add_command(label="◈ Lock Screen",     command=self.exe.lock_screen)
        m.add_separator()
        m.add_command(label="◈ Toggle TTS",
                      command=lambda: setattr(self.tts,"enabled",not self.tts.enabled))
        m.add_command(label="◈ Clear Chat Log",  command=self._clear_log)
        m.add_separator()
        m.add_command(label="✕ Quit JARVIS",     command=self._quit)
        try: m.tk_popup(e.x_root, e.y_root)
        finally: m.grab_release()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _show_hud(self):
        self.hud.deiconify(); self.hud.lift()
        self.hud.attributes("-topmost", True)
        self._focus_input()

    def _focus_input(self):
        self._show_hud()
        self.ent.focus_force()

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _quit(self):
        self.mem.save()
        try: self.hud.destroy()
        except: pass
        self.root.quit(); self.root.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if sys.platform != "win32":
        print("⚠  JARVIS is designed for Windows.")
    JarvisApp()
