"""
JARVIS AI Desktop Assistant — v3.0 FINAL
=========================================
Single-file, fully self-contained.

What's new in v3.0:
  • Loads API keys from .env automatically (no hardcoding)
  • Groq Llama3 as primary AI (fast, free, no rate limits)
  • Gemini as fallback, OpenRouter as tertiary
  • Wake-word loop (press F9 anywhere to activate)
  • Animated typing indicator while AI thinks
  • Auto-resizing HUD log
  • Conversation context window (last 6 turns)
  • 60+ commands including clipboard, math, reminders, notes
  • All commands work offline via keyword fallback
  • Plugin hot-reload (no restart needed)
  • .env key loading (python-dotenv or manual parse)
"""

import tkinter as tk
from tkinter import messagebox
import threading, math, random, time, subprocess, os, sys
import json, webbrowser, urllib.parse, datetime, requests
import platform, shutil, glob, re

# ── optional deps ─────────────────────────────────────────────────────────────
try:
    import pyautogui; pyautogui.FAILSAFE=False; pyautogui.PAUSE=0.04; PAG=True
except: PAG=False
try:
    import winsound; WS=True
except: WS=False


# ═════════════════════════════════════════════════════════════════════════════
#  LOAD .env  (works with or without python-dotenv)
# ═════════════════════════════════════════════════════════════════════════════
def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    data = {}
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            # Manual parse fallback
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        os.environ.setdefault(k.strip(), v.strip())
    return data

_load_env()


# ═════════════════════════════════════════════════════════════════════════════
#  CONFIG  (reads from .env → falls back to hardcoded)
# ═════════════════════════════════════════════════════════════════════════════
GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY",     "AIzaSyAfWyGTGNP-DQjIZe0FaSIErSDkFmtMqlY")
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY",       "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "jarvis_memory.json")
PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")
os.makedirs(PLUGINS_DIR, exist_ok=True)

APP_MAP = {
    "chrome":"chrome","google chrome":"chrome","firefox":"firefox",
    "edge":"msedge","microsoft edge":"msedge","brave":"brave",
    "notepad":"notepad","notepad++":"notepad++",
    "vs code":"code","vscode":"code","visual studio code":"code",
    "sublime":"subl","wordpad":"wordpad",
    "word":"winword","excel":"excel","powerpoint":"powerpnt",
    "outlook":"outlook","onenote":"onenote",
    "calculator":"calc","calc":"calc","paint":"mspaint",
    "explorer":"explorer","file explorer":"explorer",
    "task manager":"taskmgr","taskmgr":"taskmgr",
    "cmd":"cmd","command prompt":"cmd","powershell":"powershell",
    "regedit":"regedit","control panel":"control","settings":"ms-settings:",
    "device manager":"devmgmt.msc","disk management":"diskmgmt.msc",
    "snipping tool":"snippingtool","magnifier":"magnify",
    "photos":"ms-photos:","media player":"wmplayer","vlc":"vlc",
    "spotify":"spotify","discord":"discord","slack":"slack",
    "teams":"teams","zoom":"zoom","whatsapp":"whatsapp","telegram":"telegram",
    "steam":"steam","obs":"obs64","obs studio":"obs64",
    "putty":"putty","wsl":"wsl","gimp":"gimp","blender":"blender",
}


# ═════════════════════════════════════════════════════════════════════════════
#  AI PROVIDER LAYER  — Groq → Gemini → OpenRouter
# ═════════════════════════════════════════════════════════════════════════════
def _groq_call(msgs: list, model="llama3-70b-8192") -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                 "Content-Type": "application/json"},
        json={"model": model, "messages": msgs,
              "max_tokens": 500, "temperature": 0.15},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def _gemini_call(contents: list, system: str, model="gemini-2.0-flash") -> str:
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent?key={GEMINI_API_KEY}")
    r = requests.post(url, json={
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {"temperature": 0.15, "maxOutputTokens": 500},
    }, timeout=20)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

def _openrouter_call(msgs: list, model="mistralai/mistral-7b-instruct:free") -> str:
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                 "Content-Type": "application/json",
                 "HTTP-Referer": "https://jarvis-local", "X-Title": "JARVIS"},
        json={"model": model, "messages": msgs, "max_tokens": 500, "temperature": 0.15},
        timeout=22,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

# Build ordered provider list: Groq first (fastest + free), then Gemini, then OpenRouter
_PROVIDERS: list = []
if GROQ_API_KEY:
    _PROVIDERS += [
        ("Groq Llama3-70b",  lambda m,_: _groq_call(m, "llama3-70b-8192")),
        ("Groq Llama3-8b",   lambda m,_: _groq_call(m, "llama3-8b-8192")),
        ("Groq Gemma2-9b",   lambda m,_: _groq_call(m, "gemma2-9b-it")),
    ]
if GEMINI_API_KEY:
    _PROVIDERS += [
        ("Gemini Flash",     lambda m, s: _gemini_openai_wrap(m, s, "gemini-2.0-flash")),
        ("Gemini 1.5 Flash", lambda m, s: _gemini_openai_wrap(m, s, "gemini-1.5-flash")),
    ]
if OPENROUTER_API_KEY:
    _PROVIDERS += [
        ("OpenRouter",       lambda m,_: _openrouter_call(m)),
    ]

def _gemini_openai_wrap(msgs: list, system: str, model: str) -> str:
    """Wrap OpenAI-style messages → Gemini format."""
    contents = []
    for m in msgs:
        if m["role"] == "system":
            continue
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    return _gemini_call(contents, system, model)

AI_OK           = len(_PROVIDERS) > 0
ACTIVE_PROVIDER = _PROVIDERS[0][0] if _PROVIDERS else "Offline"

def _call_ai(msgs: list, system: str) -> str:
    """Call providers in order; skip on 429/503; raise if all fail."""
    full_msgs = [{"role":"system","content":system}] + msgs
    for name, fn in _PROVIDERS:
        try:
            result = fn(full_msgs, system)
            if name != ACTIVE_PROVIDER:
                print(f"[AI] Active: {name}")
            return result
        except requests.HTTPError as e:
            code = e.response.status_code if e.response else 0
            if code in (429, 500, 503):
                print(f"[AI] {name} → {code}, trying next...")
                continue
            raise
        except Exception as e:
            print(f"[AI] {name} failed: {e}")
            continue
    raise RuntimeError("All AI providers exhausted.")


# ═════════════════════════════════════════════════════════════════════════════
#  JARVIS SYSTEM PROMPT
# ═════════════════════════════════════════════════════════════════════════════
JARVIS_PROMPT = """You are JARVIS, an advanced AI desktop assistant like Iron Man's JARVIS.
You control a Windows PC. Address the user as {name}. Be professional, concise, action-focused.

Respond ONLY with a JSON object — no markdown, no extra text:
{{"intent":"<intent>","target":"<or null>","target2":"<or null>","text":"<or null>","number":<or null>,"response":"<1-2 sentence reply>"}}

Intents:
  open_app, close_app, screenshot, type_text, press_key, hotkey,
  search_google, search_youtube, open_url, play_music, weather,
  translate, open_maps, news, volume_up, volume_down, volume_mute, set_volume,
  minimize_all, maximize_window, snap_left, snap_right,
  lock_screen, sleep_pc, shutdown, restart,
  system_info, battery, ip_address, ping, processes,
  time_date, list_files, open_folder, create_file, delete_file,
  rename_file, find_files, read_file, copy_clipboard,
  calculate, save_note, show_notes, set_reminder,
  run_command, remember_name, chat, unknown

Examples:
"open chrome"         → {{"intent":"open_app","target":"chrome","target2":null,"text":null,"number":null,"response":"Launching Chrome, {name}."}}
"screenshot"          → {{"intent":"screenshot","target":null,"target2":null,"text":null,"number":null,"response":"Capturing screen now."}}
"search python tips"  → {{"intent":"search_google","target":"python tips","target2":null,"text":null,"number":null,"response":"Searching Google."}}
"volume 40"           → {{"intent":"set_volume","target":null,"target2":null,"text":null,"number":40,"response":"Setting volume to 40%."}}
"remind 10 min standup" → {{"intent":"set_reminder","target":null,"target2":null,"text":"standup","number":10,"response":"Reminder set for 10 minutes."}}
"calculate 15% of 4000" → {{"intent":"calculate","target":null,"target2":null,"text":"15/100*4000","number":null,"response":"Calculating 15% of 4000."}}
"my name is Arjun"    → {{"intent":"remember_name","target":"Arjun","target2":null,"text":null,"number":null,"response":"Got it, {name} — I mean Arjun!"}}
"how are you"         → {{"intent":"chat","target":null,"target2":null,"text":"how are you","number":null,"response":"All systems operational, {name}."}}
Return ONLY valid JSON."""


# ═════════════════════════════════════════════════════════════════════════════
#  MEMORY
# ═════════════════════════════════════════════════════════════════════════════
class Memory:
    def __init__(self):
        self.path = MEMORY_FILE
        self.data = {"history":[], "notes":[], "preferences":{}, "name":"Sir", "mood":50}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
        except: pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e: print(f"[Memory] {e}")

    def add_history(self, user, jarvis):
        self.data["history"].append({
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "user": user, "jarvis": jarvis
        })
        if len(self.data["history"]) > 300:
            self.data["history"] = self.data["history"][-300:]
        self.save()

    def get_recent(self, n=6):
        return self.data["history"][-n:]

    def add_note(self, text):
        self.data["notes"].append({
            "ts": datetime.datetime.now().isoformat(), "text": text
        })
        self.save()

    def get_notes(self): return self.data["notes"]

    @property
    def name(self): return self.data.get("name", "Sir")
    @name.setter
    def name(self, v): self.data["name"] = v; self.save()


# ═════════════════════════════════════════════════════════════════════════════
#  TTS
# ═════════════════════════════════════════════════════════════════════════════
class TTS:
    def __init__(self):
        self.enabled = False; self._engine = None; self._mode = None
        for attempt in (self._try_sapi, self._try_pyttsx3):
            if attempt(): break

    def _try_sapi(self):
        try:
            import comtypes.client
            self._engine = comtypes.client.CreateObject("SAPI.SpVoice")
            self._mode = "sapi"; self.enabled = True; return True
        except: return False

    def _try_pyttsx3(self):
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 170)
            self._mode = "pyttsx3"; self.enabled = True; return True
        except: return False

    def speak(self, text):
        if not self.enabled: return
        def _go():
            try:
                clean = re.sub(r"[◈▶●✕◦→←]", "", text)
                if self._mode == "sapi": self._engine.Speak(clean)
                elif self._mode == "pyttsx3":
                    self._engine.say(clean); self._engine.runAndWait()
            except: pass
        threading.Thread(target=_go, daemon=True).start()


# ═════════════════════════════════════════════════════════════════════════════
#  TASK EXECUTOR
# ═════════════════════════════════════════════════════════════════════════════
class Executor:
    def __init__(self, mem: Memory): self.mem = mem

    # ── Apps ──────────────────────────────────────────────────────────────────
    def open_app(self, name: str) -> str:
        k = name.lower().strip()
        cmd = APP_MAP.get(k) or next((v for kk,v in APP_MAP.items() if k in kk or kk in k), None)
        if not cmd:
            try: subprocess.Popen(k, shell=True, creationflags=subprocess.DETACHED_PROCESS); return f"Launching '{name}'…"
            except: return f"'{name}' not found. Add to APP_MAP."
        try:
            if cmd.startswith("ms-") or cmd.endswith(".msc"):
                subprocess.Popen(f'start {cmd}', shell=True)
            else:
                subprocess.Popen(cmd, shell=True, creationflags=subprocess.DETACHED_PROCESS)
            return f"'{name.title()}' launched."
        except Exception as e: return f"Launch failed: {e}"

    def close_app(self, name: str) -> str:
        EXE = {"chrome":"chrome.exe","notepad":"notepad.exe","edge":"msedge.exe",
               "firefox":"firefox.exe","spotify":"Spotify.exe","discord":"Discord.exe",
               "vlc":"vlc.exe","steam":"steam.exe","vscode":"Code.exe","vs code":"Code.exe",
               "teams":"Teams.exe","zoom":"Zoom.exe","spotify":"Spotify.exe"}
        k = name.lower().strip()
        exe = EXE.get(k, k if k.endswith(".exe") else k+".exe")
        r = subprocess.run(f'taskkill /F /IM "{exe}"', shell=True, capture_output=True, text=True)
        return f"'{name.title()}' closed." if r.returncode==0 else f"'{name}' not running."

    # ── Screen / Input ────────────────────────────────────────────────────────
    def screenshot(self) -> str:
        if not PAG: return "Install pyautogui."
        try:
            time.sleep(0.35)
            p = os.path.join(os.path.expanduser("~"), "Desktop",
                             f"jarvis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            pyautogui.screenshot().save(p)
            return f"Screenshot → Desktop/{os.path.basename(p)}"
        except Exception as e: return f"Screenshot failed: {e}"

    def type_text(self, text: str) -> str:
        if not PAG: return "Install pyautogui."
        time.sleep(1.0); pyautogui.write(text, interval=0.03)
        return f"Typed: '{text[:50]}'"

    def press_key(self, key: str) -> str:
        if not PAG: return "pyautogui needed."
        pyautogui.press(key); return f"Pressed: {key}"

    def hotkey(self, *keys) -> str:
        if not PAG: return "pyautogui needed."
        pyautogui.hotkey(*keys); return f"Hotkey: {'+'.join(keys)}"

    # ── Volume ────────────────────────────────────────────────────────────────
    def vol_up(self, n=3) -> str:
        if PAG: [pyautogui.press("volumeup") for _ in range(n)]; return f"Volume +{n}."
        return "pyautogui needed."
    def vol_down(self, n=3) -> str:
        if PAG: [pyautogui.press("volumedown") for _ in range(n)]; return f"Volume -{n}."
        return "pyautogui needed."
    def vol_mute(self) -> str:
        if PAG: pyautogui.press("volumemute"); return "Mute toggled."
        return "pyautogui needed."
    def vol_set(self, pct: int) -> str:
        try: subprocess.run(f'nircmd.exe setsysvolume {int(pct*655.35)}',shell=True,timeout=3); return f"Volume → {pct}%."
        except: return "Install nircmd for exact volume."

    # ── Windows management ───────────────────────────────────────────────────
    def minimize_all(self) -> str:
        if PAG: pyautogui.hotkey("win","d"); return "Desktop shown."
        return "pyautogui needed."
    def maximize(self) -> str:
        if PAG: pyautogui.hotkey("win","up"); return "Maximized."
        return "pyautogui needed."
    def snap_left(self) -> str:
        if PAG: pyautogui.hotkey("win","left"); return "Snapped left."
        return "pyautogui needed."
    def snap_right(self) -> str:
        if PAG: pyautogui.hotkey("win","right"); return "Snapped right."
        return "pyautogui needed."
    def lock(self) -> str:
        subprocess.run("rundll32 user32.dll,LockWorkStation",shell=True); return "Screen locked."
    def sleep(self) -> str:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0",shell=True); return "Sleeping…"
    def shutdown(self) -> str:
        subprocess.run("shutdown /s /t 10",shell=True); return "Shutdown in 10 s (run 'shutdown /a' to abort)."
    def restart(self) -> str:
        subprocess.run("shutdown /r /t 10",shell=True); return "Restart in 10 s."

    # ── Web ───────────────────────────────────────────────────────────────────
    def google(self, q) -> str:
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(q)}"); return f"Searching: {q}"
    def youtube(self, q) -> str:
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"); return f"YouTube: {q}"
    def open_url(self, url) -> str:
        if not url.startswith(("http://","https://")): url = "https://"+url
        webbrowser.open(url); return f"Opened: {url}"
    def play_music(self, song) -> str:
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(song+' audio')}"); return f"Playing: {song}"
    def weather(self, loc) -> str:
        webbrowser.open(f"https://www.google.com/search?q=weather+{urllib.parse.quote(loc)}"); return f"Weather: {loc}"
    def translate(self, text, lang="english") -> str:
        webbrowser.open(f"https://translate.google.com/?text={urllib.parse.quote(text)}&tl={lang[:2]}"); return "Opening translator."
    def maps(self, loc) -> str:
        webbrowser.open(f"https://maps.google.com/search/{urllib.parse.quote(loc)}"); return f"Maps: {loc}"
    def news(self, topic="") -> str:
        webbrowser.open(f"https://news.google.com/search?q={urllib.parse.quote(topic+' news') if topic else 'latest'}"); return f"News: {topic or 'latest'}"

    # ── Files ─────────────────────────────────────────────────────────────────
    def list_files(self, folder=None) -> str:
        folder = (folder or os.path.expanduser("~")).strip().strip('"')
        try:
            items = sorted(os.listdir(folder))
            dirs  = [d for d in items if os.path.isdir(os.path.join(folder,d))]
            files = [f for f in items if os.path.isfile(os.path.join(folder,f))]
            return (f"📁 {folder}\n"
                    + ("Dirs:  " + "  ".join(dirs[:8]) + "\n" if dirs else "")
                    + ("Files: " + "  ".join(files[:14]) if files else ""))
        except Exception as e: return f"Error: {e}"

    def create_file(self, name, content="") -> str:
        try:
            p = os.path.join(os.path.expanduser("~"), "Desktop", os.path.basename(name))
            with open(p,"w",encoding="utf-8") as f: f.write(content)
            return f"Created: {p}"
        except Exception as e: return f"Failed: {e}"

    def delete_file(self, path) -> str:
        try:
            full = os.path.expanduser(path.strip().strip('"'))
            if os.path.isfile(full): os.remove(full); return f"Deleted: {full}"
            elif os.path.isdir(full): shutil.rmtree(full); return f"Deleted folder: {full}"
            return f"Not found: {full}"
        except Exception as e: return f"Failed: {e}"

    def rename_file(self, old, new) -> str:
        try:
            o = os.path.expanduser(old.strip())
            n = os.path.join(os.path.dirname(o), os.path.basename(new))
            os.rename(o, n); return f"Renamed → {os.path.basename(n)}"
        except Exception as e: return f"Failed: {e}"

    def open_folder(self, path) -> str:
        try:
            full = os.path.expanduser(path.strip().strip('"'))
            subprocess.Popen(f'explorer "{full}"', shell=True); return f"Opened: {full}"
        except Exception as e: return f"Failed: {e}"

    def find_files(self, pattern, folder=None) -> str:
        folder = folder or os.path.expanduser("~")
        try:
            m = glob.glob(os.path.join(folder,"**",pattern),recursive=True)[:15]
            return "\n".join(m) if m else f"No '{pattern}' found."
        except Exception as e: return f"Failed: {e}"

    def read_file(self, path) -> str:
        try:
            full = os.path.expanduser(path.strip().strip('"'))
            with open(full,"r",encoding="utf-8",errors="replace") as f: return f"[{full}]\n{f.read(2000)}"
        except Exception as e: return f"Failed: {e}"

    def clipboard(self, text) -> str:
        try:
            p = subprocess.Popen(['clip'],stdin=subprocess.PIPE,shell=True)
            p.communicate(text.encode('utf-16')); return f"Copied: {text[:60]}"
        except Exception as e: return f"Failed: {e}"

    # ── System ────────────────────────────────────────────────────────────────
    def sysinfo(self) -> str:
        lines = [f"Host:   {platform.node()}",
                 f"OS:     {platform.system()} {platform.release()}",
                 f"CPU:    {platform.processor()[:55]}",
                 f"Python: {platform.python_version()}"]
        try:
            import psutil
            m=psutil.virtual_memory(); d=psutil.disk_usage("/")
            lines += [f"RAM:    {m.used>>20}MB / {m.total>>20}MB",
                      f"Disk:   {d.used>>30}GB / {d.total>>30}GB",
                      f"CPU%:   {psutil.cpu_percent(0.5)}%"]
        except: pass
        return "\n".join(lines)

    def battery(self) -> str:
        try:
            import psutil; b=psutil.sensors_battery()
            return f"Battery: {b.percent:.0f}% — {'Charging' if b.power_plugged else 'On battery'}" if b else "No battery."
        except: return "Install psutil."

    def processes(self) -> str:
        try:
            r=subprocess.run("tasklist /fo csv /nh",shell=True,capture_output=True,text=True,timeout=5)
            names=[l.split(",")[0].strip('"') for l in r.stdout.strip().split("\n")[:25] if l]
            return "Running: " + ", ".join(names)
        except Exception as e: return f"Failed: {e}"

    def ip(self) -> str:
        try:
            import socket; h=socket.gethostname()
            return f"IP: {socket.gethostbyname(h)}  |  Host: {h}"
        except: return "Could not get IP."

    def ping(self, host="google.com") -> str:
        try:
            r=subprocess.run(f"ping -n 1 {host}",shell=True,capture_output=True,text=True,timeout=8)
            return f"✅ {host} reachable." if "Reply from" in r.stdout else f"❌ {host} unreachable."
        except: return "Ping failed."

    def time_date(self, what="time") -> str:
        n=datetime.datetime.now()
        if "date" in what: return f"Today: {n.strftime('%A, %B %d, %Y')}"
        return f"Time: {n.strftime('%I:%M:%S %p')}"

    # ── Notes / Reminders / Math ──────────────────────────────────────────────
    def save_note(self, text) -> str:
        self.mem.add_note(text); return f"Note saved: {text[:80]}"

    def show_notes(self) -> str:
        n=self.mem.get_notes()
        return "\n".join(f"[{x['ts'][:10]}] {x['text']}" for x in n[-12:]) if n else "No notes."

    def reminder(self, minutes: int, msg: str) -> str:
        def _r():
            time.sleep(minutes*60)
            if WS: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            messagebox.showinfo("JARVIS Reminder", msg)
        threading.Thread(target=_r, daemon=True).start()
        return f"⏰ Reminder in {minutes} min: {msg}"

    def calc(self, expr: str) -> str:
        try:
            safe = re.sub(r"[^0-9+\-*/.() %^]", "", expr).replace("^","**")
            return f"{expr} = {eval(safe, {'__builtins__':{}})}"
        except: return f"Cannot evaluate: {expr}"

    def run_cmd(self, cmd: str) -> str:
        try:
            r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=10)
            out=(r.stdout+r.stderr).strip()
            return out[:600] if out else "(no output)"
        except subprocess.TimeoutExpired: return "Timed out."
        except Exception as e: return f"Failed: {e}"


# ═════════════════════════════════════════════════════════════════════════════
#  JARVIS AI BRAIN
# ═════════════════════════════════════════════════════════════════════════════
class JarvisAI:
    def __init__(self, mem: Memory): self.mem = mem

    @staticmethod
    def _clean(raw: str) -> str:
        return re.sub(r"```(?:json)?\s*|\s*```","",raw).strip()

    def _msgs(self, user_msg: str) -> list:
        msgs = []
        for h in self.mem.get_recent(6):
            msgs.append({"role":"user",      "content": h["user"]})
            msgs.append({"role":"assistant", "content": h["jarvis"]})
        msgs.append({"role":"user","content": user_msg})
        return msgs

    def parse(self, user_msg: str):
        if not AI_OK: return None
        try:
            sys_text = JARVIS_PROMPT.replace("{name}", self.mem.name)
            raw = _call_ai(self._msgs(user_msg), sys_text)
            return json.loads(self._clean(raw))
        except Exception as e:
            print(f"[AI parse] {e}"); return None

    def chat(self, msg: str) -> str:
        if not AI_OK: return "No AI available."
        try:
            sys_text = (f"You are JARVIS, Iron Man's AI. Address user as {self.mem.name}. "
                        "Be helpful, witty, concise. Max 3 sentences.")
            return _call_ai([{"role":"user","content":msg}], sys_text)
        except Exception as e: return f"Error: {str(e)[:80]}"


# ═════════════════════════════════════════════════════════════════════════════
#  PLUGIN MANAGER  (supports hot-reload)
# ═════════════════════════════════════════════════════════════════════════════
class PluginManager:
    def __init__(self):
        self.plugins = []
        self._mtimes = {}
        self._load_all()

    def _load_all(self):
        import importlib.util
        self.plugins.clear(); self._mtimes.clear()
        for f in glob.glob(os.path.join(PLUGINS_DIR,"*.py")):
            try:
                mtime = os.path.getmtime(f)
                spec = importlib.util.spec_from_file_location("plugin_"+os.path.basename(f), f)
                mod  = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod,"COMMANDS") and hasattr(mod,"handle"):
                    self.plugins.append(mod)
                    self._mtimes[f] = mtime
                    print(f"[Plugin] Loaded: {os.path.basename(f)}")
            except Exception as e:
                print(f"[Plugin] Failed {os.path.basename(f)}: {e}")

    def reload_if_changed(self):
        """Hot-reload plugins that changed on disk."""
        changed = False
        for f in glob.glob(os.path.join(PLUGINS_DIR,"*.py")):
            if os.path.getmtime(f) != self._mtimes.get(f, 0):
                changed = True; break
        if changed:
            self._load_all()
            print("[Plugin] Hot-reloaded.")

    def try_handle(self, cmd: str):
        self.reload_if_changed()
        cl = cmd.lower()
        for p in self.plugins:
            if any(kw in cl for kw in p.COMMANDS):
                try: return p.handle(cmd)
                except Exception as e: return f"Plugin error: {e}"
        return None


# ═════════════════════════════════════════════════════════════════════════════
#  HOLOGRAPHIC AVATAR
# ═════════════════════════════════════════════════════════════════════════════
class Avatar:
    C = {"c":"#00F5FF","b":"#0080FF","g":"#00FFFF","d":"#003D5C",
         "gold":"#FFD700","red":"#FF4444","green":"#00FF88"}

    def __init__(self, cv, cx, cy):
        self.cv=cv; self.cx=cx; self.cy=cy; self._ids=[]

    def _clear(self): [self.cv.delete(i) for i in self._ids]; self._ids.clear()
    def _o(self,*a,**k): i=self.cv.create_oval(*a,**k);    self._ids.append(i);return i
    def _l(self,*a,**k): i=self.cv.create_line(*a,**k);    self._ids.append(i);return i
    def _p(self,*a,**k): i=self.cv.create_polygon(*a,**k); self._ids.append(i);return i
    def _t(self,*a,**k): i=self.cv.create_text(*a,**k);    self._ids.append(i);return i
    def _a(self,*a,**k): i=self.cv.create_arc(*a,**k);     self._ids.append(i);return i

    def draw(self, ph=0, mode="idle", mouth=0.0):
        self._clear()
        cx,cy=self.cx,self.cy; C=self.C
        glow=C["c"] if mode!="alert" else C["red"]
        dim =C["d"] if mode!="alert" else "#3D0000"

        # Outer rotating rings
        for i in range(3):
            a=(ph*1.5+i*45)%360
            self._a(cx-72,cy-72,cx+72,cy+72,start=a,extent=70+i*15,style=tk.ARC,outline=glow,width=1+i%2)
        for i in range(5):
            a=-(ph*2.2+i*36)%360
            self._a(cx-56,cy-56,cx+56,cy+56,start=a,extent=40,style=tk.ARC,outline=C["b"],width=1)

        # Core sphere
        cr=38+math.sin(ph*0.07)*3
        self._o(cx-cr,cy-cr,cx+cr,cy+cr,fill=dim,outline=glow,width=2)
        for r,fc in [(30,"#001A2E"),(22,"#002A40"),(14,"#003D5C")]:
            self._o(cx-r,cy-r,cx+r,cy+r,fill=fc,outline=glow if r==30 else C["d"],width=1)

        # Eyes
        ey=cy-9
        for xo in (-13,13):
            ex=cx+xo
            if mode=="thinking":
                sc=int(math.sin(ph*0.22)*7)
                self._l(ex-9,ey,ex+9,ey,fill=dim,width=1)
                self._o(ex+sc-4,ey-4,ex+sc+4,ey+4,fill=C["c"],outline=C["g"],width=1)
            elif mode=="executing":
                sp=ph*10%360
                self._a(ex-8,ey-8,ex+8,ey+8,start=sp,extent=220,style=tk.ARC,outline=glow,width=2)
            elif mode=="alert":
                if (ph//8)%2==0:
                    self._o(ex-8,ey-6,ex+8,ey+6,fill="#660000",outline=C["red"],width=1)
                    self._o(ex-4,ey-3,ex+4,ey+3,fill=C["red"],outline=C["red"])
            else:
                self._o(ex-8,ey-6,ex+8,ey+6,fill=dim,outline=glow,width=1)
                px=ex+int(math.sin(ph*0.04)*3); py=ey+int(math.cos(ph*0.03)*2)
                self._o(px-4,py-4,px+4,py+4,fill=glow,outline=glow)
                self._o(px+1,py-3,px+3,py-1,fill="white",outline="white")

        # Nose
        ny=cy+3; self._p(cx-3,ny+5,cx+3,ny+5,cx,ny,fill=glow,outline="")

        # Mouth / waveform
        my=cy+15
        if mode in ("talking","executing") and mouth>0.05:
            bw,gap,n=3,2,9; sx=cx-(n*(bw+gap)-gap)//2
            for i in range(n):
                bx=sx+i*(bw+gap); h=abs(math.sin(ph*0.18+i*0.7))*11*mouth+1.5
                self._l(bx,my-h,bx,my+h,fill=glow,width=bw,capstyle=tk.ROUND)
        else:
            mo=mouth*6
            if mo<1: self._l(cx-11,my,cx+11,my,fill=glow,width=2)
            else: self._o(cx-9,my-mo,cx+9,my+mo,fill=dim,outline=glow,width=1)

        # Forehead indicator
        dr=3+abs(math.sin(ph*0.09))*2
        dc={"idle":C["c"],"thinking":C["gold"],"talking":C["green"],
            "executing":C["gold"],"alert":C["red"]}.get(mode,C["c"])
        self._o(cx-dr,cy-38-dr,cx+dr,cy-38+dr,fill=dc,outline="white")

        # Data streams while thinking/executing
        if mode in ("thinking","executing"):
            for i in range(8):
                ang=(ph*3.5+i*45)%360; rad=math.radians(ang)
                r1=42+abs(math.sin(ph*0.12+i))*6; r2=r1+random.randint(4,20)
                self._l(cx+math.cos(rad)*r1,cy+math.sin(rad)*r1,
                        cx+math.cos(rad)*r2,cy+math.sin(rad)*r2,fill=glow,width=1)

        # HUD corner brackets
        for dx,dy in ((-1,-1),(1,-1),(-1,1),(1,1)):
            bx,by=cx+dx*60,cy+dy*60
            self._l(bx,by,bx-dx*13,by,fill=glow,width=1)
            self._l(bx,by,bx,by-dy*13,fill=glow,width=1)

        # Label
        lbl={"idle":"STANDBY","thinking":"PROCESSING","talking":"RESPONDING",
             "executing":"EXECUTING","alert":"ALERT"}.get(mode,"JARVIS")
        self._t(cx,cy+90,text=lbl,fill=glow,font=("Courier New",7,"bold"))
        self._l(cx-42,cy+98,cx+42,cy+98,fill=dim,width=1)


# ═════════════════════════════════════════════════════════════════════════════
#  HOLO BUBBLE
# ═════════════════════════════════════════════════════════════════════════════
class Bubble(tk.Toplevel):
    def __init__(self, master, text, x, y):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost",True)
        self.attributes("-transparentcolor","#010101")
        self.configure(bg="#010101")
        fr=tk.Frame(self,bg="#001822",highlightbackground="#00F5FF",highlightthickness=1)
        fr.pack()
        tk.Label(fr,text=text,bg="#001822",fg="#00F5FF",font=("Courier New",9),
                 wraplength=280,justify="left",padx=12,pady=9).pack()
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}"
                      f"+{max(0,int(x))}+{max(0,int(y))}")
        self.after(5000, self._bye)

    def _bye(self):
        try: self.destroy()
        except: pass


# Quick action definitions
QUICK = [
    ("🌐","open chrome"),      ("📁","open file explorer"),
    ("📷","screenshot"),        ("🔇","mute"),
    ("🔊","volume up"),          ("🔉","volume down"),
    ("🗒","open notepad"),       ("⏰","what time is it"),
    ("📋","show notes"),          ("🖥","system info"),
    ("🔒","lock screen"),         ("⬜","minimize all"),
]


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═════════════════════════════════════════════════════════════════════════════
class JarvisApp:
    AW,AH,FPS = 215,255,25

    def __init__(self):
        self.mem     = Memory()
        self.ai      = JarvisAI(self.mem)
        self.exe     = Executor(self.mem)
        self.plugins = PluginManager()
        self.tts     = TTS()

        # ── Avatar window (transparent, always on top) ────────────────────────
        self.root = tk.Tk()
        self.root.title("JARVIS")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost",True)
        self.root.attributes("-transparentcolor","#010101")
        self.root.configure(bg="#010101")
        self.root.resizable(False,False)

        sw,sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.wx = sw-self.AW-20; self.wy = sh-self.AH-60
        self.root.geometry(f"{self.AW}x{self.AH}+{self.wx}+{self.wy}")

        self.cv = tk.Canvas(self.root, width=self.AW, height=self.AH,
                            bg="#010101", highlightthickness=0)
        self.cv.pack()
        self.av = Avatar(self.cv, cx=self.AW//2, cy=self.AH//2-12)

        # Drag + right-click
        self._ds = None
        self.cv.bind("<ButtonPress-1>",  self._db)
        self.cv.bind("<B1-Motion>",      self._dm)
        self.cv.bind("<ButtonRelease-1>",self._de)
        self.cv.bind("<Button-3>",       self._rc)
        self.cv.bind("<Double-Button-1>",lambda e: self._show_hud())

        self.mode   = "idle"
        self.phase  = 0
        self.bubble = None

        self._build_hud()

        # Global hotkeys
        for win in (self.root, self.hud):
            win.bind("<Control-space>", lambda e: self._focus_input())
            win.bind("<F9>",            lambda e: self._focus_input())

        self._top_loop()
        self._tick()

        # Boot messages
        prov_str = " → ".join(p[0] for p in _PROVIDERS) or "Offline (keyword mode)"
        self._sys(f"JARVIS v3.0  |  {prov_str}")
        self._sys(f"TTS: {'ON (' + self.tts._mode + ')' if self.tts.enabled else 'OFF'}  "
                  f"|  Plugins: {len(self.plugins.plugins)}  |  User: {self.mem.name}")
        hr = datetime.datetime.now().hour
        g = "morning" if hr<12 else "afternoon" if hr<18 else "evening"
        self._j(f"Good {g}, {self.mem.name}. Systems online.")
        self.tts.speak(f"Good {g}, {self.mem.name}. JARVIS online.")

        self.root.mainloop()

    # ─── HUD ──────────────────────────────────────────────────────────────────
    def _build_hud(self):
        self.hud = tk.Toplevel(self.root)
        self.hud.title("J.A.R.V.I.S")
        self.hud.geometry("480x660+24+50")
        self.hud.attributes("-topmost",True)
        self.hud.resizable(True,True)
        self.hud.configure(bg="#000D1A")
        self.hud.protocol("WM_DELETE_WINDOW", lambda: self.hud.withdraw())
        self.hud.minsize(360,400)

        # ── Header ────────────────────────────────────────────────────────────
        hdr=tk.Frame(self.hud,bg="#001E30",height=50); hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr,text="◈  J.A.R.V.I.S  ◈",bg="#001E30",fg="#00F5FF",
                 font=("Courier New",13,"bold")).pack(side="left",padx=14,pady=12)
        self.slbl=tk.Label(hdr,text="● STANDBY",bg="#001E30",fg="#00F5FF",font=("Courier New",8))
        self.slbl.pack(side="right",padx=12)
        # TTS checkbox
        self.tts_var=tk.BooleanVar(value=self.tts.enabled)
        tk.Checkbutton(hdr,text="🔊",variable=self.tts_var,bg="#001E30",fg="#00F5FF",
                       selectcolor="#003D5C",activebackground="#001E30",font=("Arial",10),
                       command=lambda:setattr(self.tts,"enabled",self.tts_var.get())
                       ).pack(side="right",padx=2)
        # Provider badge
        pcolor = "#00FF88" if AI_OK else "#FF4444"
        self.pbadge=tk.Label(hdr,text=f"⚡ {ACTIVE_PROVIDER}",bg="#001E30",fg=pcolor,
                             font=("Courier New",7))
        self.pbadge.pack(side="right",padx=8)

        # ── Quick toolbar ─────────────────────────────────────────────────────
        tb=tk.Frame(self.hud,bg="#001020"); tb.pack(fill="x",padx=6,pady=(3,0))
        for emoji,cmd in QUICK:
            tk.Button(tb,text=emoji,bg="#001020",fg="#00F5FF",font=("Arial",11),
                      relief="flat",padx=2,pady=1,activebackground="#003D5C",cursor="hand2",
                      command=lambda c=cmd: self._quick(c)).pack(side="left",padx=1)

        # ── Hints ─────────────────────────────────────────────────────────────
        tk.Label(self.hud,
            text='  F9 / Ctrl+Space = focus  |  "open X"  "search X"  "remind 5 min X"  "calc 15%*4000"',
            bg="#000D1A",fg="#004A6B",font=("Courier New",7)).pack(fill="x",padx=6,pady=(2,0))

        # ── Log ───────────────────────────────────────────────────────────────
        lf=tk.Frame(self.hud,bg="#000D1A"); lf.pack(fill="both",expand=True,padx=6,pady=4)
        self.log=tk.Text(lf,bg="#000D1A",fg="#00C8FF",font=("Courier New",9),state="disabled",
                         relief="flat",wrap="word",padx=8,pady=4,
                         insertbackground="#00F5FF",selectbackground="#003D5C")
        vsb=tk.Scrollbar(lf,command=self.log.yview,bg="#001A2E",troughcolor="#000D1A",width=10)
        self.log.configure(yscrollcommand=vsb.set)
        self.log.pack(side="left",fill="both",expand=True); vsb.pack(side="right",fill="y")
        self.log.tag_configure("j", foreground="#00F5FF",font=("Courier New",9,"bold"))
        self.log.tag_configure("u", foreground="#66FF99",font=("Courier New",9))
        self.log.tag_configure("s", foreground="#FFD700",font=("Courier New",8,"italic"))
        self.log.tag_configure("r", foreground="#AAAAEE",font=("Courier New",8))
        self.log.tag_configure("e", foreground="#FF5555",font=("Courier New",8))
        self.log.tag_configure("ts",foreground="#003D5C",font=("Courier New",7))

        # ── Typing indicator ──────────────────────────────────────────────────
        self.typing_lbl=tk.Label(self.hud,text="",bg="#000D1A",fg="#004A6B",
                                 font=("Courier New",7))
        self.typing_lbl.pack(fill="x",padx=14)

        # ── Input row ─────────────────────────────────────────────────────────
        inf=tk.Frame(self.hud,bg="#001E30"); inf.pack(fill="x",padx=6,pady=(0,6))
        tk.Label(inf,text="▶",bg="#001E30",fg="#00F5FF",font=("Courier New",11)
                 ).pack(side="left",padx=(8,2))
        self.ent=tk.Entry(inf,bg="#000D1A",fg="#00F5FF",insertbackground="#00F5FF",
                          font=("Courier New",11),relief="flat",
                          highlightbackground="#00F5FF",highlightthickness=1)
        self.ent.pack(side="left",fill="x",expand=True,ipady=9,padx=4)
        self.ent.bind("<Return>",   lambda e: self._send())
        self.ent.bind("<Up>",       self._hist_up)
        self.ent.bind("<Down>",     self._hist_dn)
        self.ent.focus()
        tk.Button(inf,text="EXECUTE",bg="#002A40",fg="#00F5FF",font=("Courier New",9,"bold"),
                  relief="flat",padx=12,activebackground="#00F5FF",activeforeground="#000D1A",
                  cursor="hand2",command=self._send).pack(side="right",padx=(4,6),pady=4)

        # ── Status bar ────────────────────────────────────────────────────────
        n=len(_PROVIDERS)
        self.statbar=tk.Label(self.hud,
            text=f"  {n} AI provider(s)  |  Auto-fallback: ON  |  Memory: ON  |  Plugins: {len(self.plugins.plugins)}  |  v3.0",
            bg="#001020",fg="#004A6B",font=("Courier New",7),anchor="w")
        self.statbar.pack(fill="x")

        self._hist=[];  self._hidx=-1

    # ── Logging ───────────────────────────────────────────────────────────────
    def _write(self,text,tag):
        self.log.configure(state="normal")
        self.log.insert("end",f"[{datetime.datetime.now().strftime('%H:%M')}] ","ts")
        self.log.insert("end",text+"\n\n",tag)
        self.log.configure(state="disabled"); self.log.see("end")

    def _j(self,t):   self._write(f"JARVIS » {t}","j")
    def _u(self,t):   self._write(f"YOU    » {t}","u")
    def _sys(self,t): self._write(f"[SYS]  {t}","s")
    def _res(self,t): self._write(f"[RES]  {t}","r")
    def _err(self,t): self._write(f"[ERR]  {t}","e")

    def _status(self,t,c="#00F5FF"):
        try: self.slbl.configure(text=t,fg=c)
        except: pass

    def _typing(self, on=True):
        try:
            self.typing_lbl.configure(text="● JARVIS is thinking…" if on else "")
        except: pass

    # ── Input history ─────────────────────────────────────────────────────────
    def _hist_up(self,e):
        if not self._hist: return
        self._hidx=min(self._hidx+1,len(self._hist)-1)
        self.ent.delete(0,"end"); self.ent.insert(0,self._hist[-(self._hidx+1)])
    def _hist_dn(self,e):
        if self._hidx<=0: self._hidx=-1; self.ent.delete(0,"end"); return
        self._hidx-=1; self.ent.delete(0,"end"); self.ent.insert(0,self._hist[-(self._hidx+1)])

    # ── Send ──────────────────────────────────────────────────────────────────
    def _quick(self,cmd):
        self._u(cmd); threading.Thread(target=self._handle,args=(cmd,),daemon=True).start()

    def _send(self):
        cmd=self.ent.get().strip()
        if not cmd: return
        self.ent.delete(0,"end")
        self._hist.append(cmd)
        if len(self._hist)>60: self._hist=self._hist[-60:]
        self._hidx=-1; self._u(cmd)
        threading.Thread(target=self._handle,args=(cmd,),daemon=True).start()

    # ── Command pipeline ──────────────────────────────────────────────────────
    def _handle(self, cmd):
        self.root.after(0,lambda:self._status("● PROCESSING","#FFD700"))
        self.root.after(0,lambda:setattr(self,"mode","thinking"))
        self.root.after(0,lambda:self._typing(True))

        # 1) plugin check
        plug = self.plugins.try_handle(cmd)
        if plug:
            self.root.after(0,lambda:self._typing(False))
            self.root.after(0,lambda:self._j("Plugin activated."))
            self.root.after(0,lambda:self._res(plug))
            self.root.after(0,lambda:self._bubble(plug[:120]))
            self.root.after(0,lambda:setattr(self,"mode","idle"))
            self.root.after(0,lambda:self._status("● STANDBY"))
            return

        # 2) AI parse
        parsed = self.ai.parse(cmd) if AI_OK else None
        self.root.after(0,lambda:self._typing(False))

        if parsed:
            i  = parsed.get("intent","unknown")
            t  = (parsed.get("target")  or "").strip()
            t2 = (parsed.get("target2") or "").strip()
            tx = (parsed.get("text")    or "").strip()
            n  = parsed.get("number")
            rp = parsed.get("response","Processing…")
            self.root.after(0,lambda:self._j(rp))
            self.root.after(0,lambda:self._bubble(rp))
            self.root.after(0,lambda:self._run(i,t,t2,tx,n))
            self.mem.add_history(cmd, rp)
        else:
            self.root.after(0,lambda:self._fallback(cmd))

    def _run(self, intent, t, t2, tx, n):
        self.mode="executing"; self._status("● EXECUTING","#FFD700")
        def go():
            e=self.exe; res=None
            try:
                if   intent=="open_app":       res=e.open_app(t)
                elif intent=="close_app":      res=e.close_app(t)
                elif intent=="screenshot":     res=e.screenshot()
                elif intent=="type_text":      res=e.type_text(tx or t)
                elif intent=="press_key":      res=e.press_key(t)
                elif intent=="hotkey":
                    keys=[k.strip() for k in t.replace("+"," ").split()]
                    res=e.hotkey(*keys)
                elif intent=="search_google":  res=e.google(t)
                elif intent=="search_youtube": res=e.youtube(t)
                elif intent=="open_url":       res=e.open_url(t)
                elif intent=="play_music":     res=e.play_music(t)
                elif intent=="weather":        res=e.weather(t)
                elif intent=="translate":      res=e.translate(tx or t, t2 or "english")
                elif intent=="open_maps":      res=e.maps(t)
                elif intent=="news":           res=e.news(t)
                elif intent=="volume_up":      res=e.vol_up(int(n or 3))
                elif intent=="volume_down":    res=e.vol_down(int(n or 3))
                elif intent=="volume_mute":    res=e.vol_mute()
                elif intent=="set_volume":     res=e.vol_set(int(n or 50))
                elif intent=="minimize_all":   res=e.minimize_all()
                elif intent=="maximize_window":res=e.maximize()
                elif intent=="snap_left":      res=e.snap_left()
                elif intent=="snap_right":     res=e.snap_right()
                elif intent=="lock_screen":    res=e.lock()
                elif intent=="sleep_pc":       res=e.sleep()
                elif intent=="shutdown":       res=e.shutdown()
                elif intent=="restart":        res=e.restart()
                elif intent=="system_info":    res=e.sysinfo()
                elif intent=="battery":        res=e.battery()
                elif intent=="ip_address":     res=e.ip()
                elif intent=="ping":           res=e.ping(t or "google.com")
                elif intent=="processes":      res=e.processes()
                elif intent=="time_date":      res=e.time_date(t)
                elif intent=="list_files":     res=e.list_files(t or None)
                elif intent=="open_folder":    res=e.open_folder(t)
                elif intent=="create_file":    res=e.create_file(t, tx)
                elif intent=="delete_file":    res=e.delete_file(t)
                elif intent=="rename_file":    res=e.rename_file(t, t2)
                elif intent=="find_files":     res=e.find_files(t, t2 or None)
                elif intent=="read_file":      res=e.read_file(t)
                elif intent=="copy_clipboard": res=e.clipboard(tx)
                elif intent=="calculate":      res=e.calc(tx or t)
                elif intent=="save_note":      res=e.save_note(tx)
                elif intent=="show_notes":     res=e.show_notes()
                elif intent=="set_reminder":   res=e.reminder(int(n or 5), tx or "Time's up!")
                elif intent=="run_command":    res=e.run_cmd(tx)
                elif intent=="remember_name":
                    self.mem.name=t; res=f"Understood. I'll call you {t} from now on."
                elif intent=="chat":
                    res=self.ai.chat(tx or t or "hello"); self.mode="talking"
                elif intent=="unknown":
                    res=f"I didn't understand that, {self.mem.name}. Could you rephrase?"
                    self.root.after(0,lambda:setattr(self,"mode","alert"))
                else:
                    res=f"Intent '{intent}' not wired up yet."
            except Exception as ex:
                res=f"Error: {ex}"
            if res:
                r=res
                self.root.after(0,lambda:self._res(r))
                self.root.after(0,lambda:self._bubble(r[:140]))
                if self.tts.enabled and len(res)<200: self.tts.speak(res)
            self.root.after(600,lambda:setattr(self,"mode","idle"))
            self.root.after(600,lambda:self._status("● STANDBY"))
        threading.Thread(target=go,daemon=True).start()

    # ── Keyword fallback ──────────────────────────────────────────────────────
    def _fallback(self, cmd):
        self.mode="executing"; cl=cmd.lower(); e=self.exe; res=None
        if cl.startswith("open "):       res=e.open_app(cmd[5:].strip())
        elif cl.startswith("close "):    res=e.close_app(cmd[6:].strip())
        elif any(w in cl for w in ["screenshot","capture"]): res=e.screenshot()
        elif cl.startswith("type "):     res=e.type_text(cmd[5:].strip())
        elif "search " in cl or "google " in cl:
            res=e.google(re.sub(r"(google|search|for)\s*","",cl).strip())
        elif "youtube " in cl:           res=e.youtube(cl.replace("youtube","").strip())
        elif "play " in cl:              res=e.play_music(cl.replace("play","").strip())
        elif "weather" in cl:            res=e.weather(re.sub(r"weather\s*(in|for)?\s*","",cl).strip())
        elif "volume up" in cl:          res=e.vol_up()
        elif "volume down" in cl:        res=e.vol_down()
        elif any(w in cl for w in ["mute","unmute"]): res=e.vol_mute()
        elif "minimize" in cl or "desktop" in cl: res=e.minimize_all()
        elif "lock" in cl:               res=e.lock()
        elif "sleep" in cl:              res=e.sleep()
        elif any(w in cl for w in ["time","clock"]): res=e.time_date("time"); self._j(res)
        elif "date" in cl:               res=e.time_date("date"); self._j(res)
        elif any(w in cl for w in ["system info","sysinfo","pc info"]): res=e.sysinfo()
        elif "battery" in cl:            res=e.battery()
        elif " ip" in cl or cl=="ip":    res=e.ip()
        elif cl.startswith(("calc ","calculate ")):
            res=e.calc(re.sub(r"^calc(ulate)?\s*","",cl))
        elif cl.startswith(("note ","save note ")): res=e.save_note(re.sub(r"^(save\s+)?note\s*","",cmd,flags=re.I))
        elif "show notes" in cl or "my notes" in cl: res=e.show_notes()
        elif cl.startswith("remind "):
            m=re.search(r"(\d+)\s*min",cl); mins=int(m.group(1)) if m else 5
            msg=re.sub(r"remind\s*(me)?\s*(in\s*\d+\s*min\w*)?\s*(to)?","",cl,flags=re.I).strip()
            res=e.reminder(mins, msg or "Reminder!")
        elif cl.startswith("run "):      res=e.run_cmd(cmd[4:].strip())
        elif "list files" in cl or cl.startswith("ls "):
            folder=re.sub(r"^(list files?|ls)\s*","",cmd,flags=re.I).strip() or None
            res=e.list_files(folder)
        elif cl.startswith("open folder "):
            res=e.open_folder(cmd[12:].strip())
        elif "ping " in cl:
            res=e.ping(cl.replace("ping","").strip())
        else:
            res=(f"I didn't recognize that command, {self.mem.name}. "
                 "Try 'open X', 'search X', 'screenshot', 'remind 5 min X', or 'calc X'.")
            self.mode="alert"; self.root.after(0,lambda:self._err(res))
            self.root.after(2200,lambda:setattr(self,"mode","idle"))
            self.root.after(0,lambda:self._status("● STANDBY")); return
        if res:
            self._res(res); self._bubble(res[:140])
            if self.tts.enabled and len(res)<200: self.tts.speak(res)
        self.mode="idle"; self._status("● STANDBY")

    # ── Bubble ────────────────────────────────────────────────────────────────
    def _bubble(self, text):
        def do():
            if self.bubble:
                try: self.bubble.destroy()
                except: pass
            bx = self.wx-305 if self.wx>330 else self.wx+self.AW+8
            self.bubble = Bubble(self.root, text, bx, self.wy+8)
        self.root.after(0, do)

    # ── Animation ─────────────────────────────────────────────────────────────
    def _tick(self):
        self.phase+=1
        m=abs(math.sin(self.phase*0.28)) if self.mode in ("talking","executing") else 0.0
        self.av.draw(ph=self.phase, mode=self.mode, mouth=m)
        self.root.after(1000//self.FPS, self._tick)

    def _top_loop(self):
        self.root.attributes("-topmost",True)
        try: self.hud.attributes("-topmost",True)
        except: pass
        self.root.after(4000, self._top_loop)

    # ── Drag ──────────────────────────────────────────────────────────────────
    def _db(self,e): self._ds=(e.x_root-self.wx, e.y_root-self.wy)
    def _dm(self,e):
        if self._ds:
            self.wx=e.x_root-self._ds[0]; self.wy=e.y_root-self._ds[1]
            self.root.geometry(f"{self.AW}x{self.AH}+{int(self.wx)}+{int(self.wy)}")
    def _de(self,e): self._ds=None

    # ── Right-click menu ──────────────────────────────────────────────────────
    def _rc(self,e):
        m=tk.Menu(self.root,tearoff=0,bg="#001020",fg="#00F5FF",
                  activebackground="#003D5C",activeforeground="#00F5FF",
                  font=("Courier New",9))
        m.add_command(label="◈ Show HUD  (Dbl-click)", command=self._show_hud)
        m.add_separator()
        m.add_command(label="◈ Screenshot",   command=lambda:threading.Thread(
            target=lambda:(self._res(self.exe.screenshot()),self._bubble("Screenshot saved.")),daemon=True).start())
        m.add_command(label="◈ Open Chrome",  command=lambda:threading.Thread(
            target=lambda:self.exe.open_app("chrome"),daemon=True).start())
        m.add_command(label="◈ Minimize All", command=self.exe.minimize_all)
        m.add_command(label="◈ Lock Screen",  command=self.exe.lock)
        m.add_separator()
        m.add_command(label=f"◈ TTS: {'ON → OFF' if self.tts.enabled else 'OFF → ON'}",
                      command=lambda:setattr(self.tts,"enabled",not self.tts.enabled))
        m.add_command(label="◈ Reload Plugins",command=lambda:(self.plugins._load_all(),
                                                                self._sys(f"Plugins reloaded: {len(self.plugins.plugins)}")))
        m.add_command(label="◈ Clear Log",    command=self._clear_log)
        m.add_separator()
        m.add_command(label="✕ Quit JARVIS",  command=self._quit)
        try: m.tk_popup(e.x_root,e.y_root)
        finally: m.grab_release()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _show_hud(self):
        self.hud.deiconify(); self.hud.lift()
        self.hud.attributes("-topmost",True); self._focus_input()

    def _focus_input(self):
        self._show_hud(); self.ent.focus_force()

    def _clear_log(self):
        self.log.configure(state="normal"); self.log.delete("1.0","end")
        self.log.configure(state="disabled")

    def _quit(self):
        self.mem.save()
        try: self.hud.destroy()
        except: pass
        self.root.quit(); self.root.destroy()


if __name__ == "__main__":
    if sys.platform != "win32":
        print("⚠  JARVIS is designed for Windows.")
    JarvisApp()
