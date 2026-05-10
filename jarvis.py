"""
JARVIS AI Desktop Assistant — Powered by Google Gemini
=======================================================
- Holographic animated avatar on screen (always on top)
- Google Gemini AI brain for natural language understanding
- Real task execution: open apps, screenshots, type text, web search
- Sci-fi HUD chat interface
"""

import tkinter as tk
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

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.05
    PYAUTOGUI_OK = True
except ImportError:
    PYAUTOGUI_OK = False

try:
    import pygetwindow as gw
    GW_OK = True
except ImportError:
    GW_OK = False

# ─── AI Configuration — Google Gemini ─────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyAJu8g4yjdvGBA3K59Dm_KnrnJ02aX0ptg"
GEMINI_MODEL   = "gemini-flash-latest:generateContent"          # fast + free tier
GEMINI_URL     = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)
AI_OK = bool(GEMINI_API_KEY)

# ─── App Map ──────────────────────────────────────────────────────────────────
APP_MAP = {
    "chrome":              "chrome",
    "google chrome":       "chrome",
    "firefox":             "firefox",
    "edge":                "msedge",
    "microsoft edge":      "msedge",
    "notepad":             "notepad",
    "notepad++":           "notepad++",
    "calculator":          "calc",
    "calc":                "calc",
    "paint":               "mspaint",
    "explorer":            "explorer",
    "file explorer":       "explorer",
    "task manager":        "taskmgr",
    "taskmgr":             "taskmgr",
    "cmd":                 "cmd",
    "command prompt":      "cmd",
    "powershell":          "powershell",
    "vs code":             "code",
    "vscode":              "code",
    "visual studio code":  "code",
    "spotify":             "spotify",
    "discord":             "discord",
    "word":                "winword",
    "excel":               "excel",
    "powerpoint":          "powerpnt",
    "outlook":             "outlook",
    "teams":               "teams",
    "zoom":                "zoom",
    "vlc":                 "vlc",
    "steam":               "steam",
    "settings":            "ms-settings:",
    "photos":              "ms-photos:",
    "snipping tool":       "snippingtool",
    "wordpad":             "wordpad",
    "control panel":       "control",
    "whatsapp":            "whatsapp",
    "telegram":            "telegram",
    "obs":                 "obs64",
}


# ─── JARVIS Holographic Avatar ────────────────────────────────────────────────
class JarvisAvatar:
    C_CYAN  = "#00F5FF"
    C_BLUE  = "#0080FF"
    C_GLOW  = "#00FFFF"
    C_DIM   = "#003D5C"
    C_GOLD  = "#FFD700"
    C_RED   = "#FF4444"
    C_GREEN = "#00FF88"

    def __init__(self, canvas, cx=105, cy=110):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.ids = []

    def _clear(self):
        for i in self.ids:
            try: self.canvas.delete(i)
            except: pass
        self.ids = []

    def _o(self, x1,y1,x2,y2,**kw):
        i=self.canvas.create_oval(x1,y1,x2,y2,**kw); self.ids.append(i); return i
    def _l(self,*pts,**kw):
        i=self.canvas.create_line(*pts,**kw); self.ids.append(i); return i
    def _p(self,*pts,**kw):
        i=self.canvas.create_polygon(*pts,**kw); self.ids.append(i); return i
    def _t(self,x,y,**kw):
        i=self.canvas.create_text(x,y,**kw); self.ids.append(i); return i
    def _a(self,x1,y1,x2,y2,**kw):
        i=self.canvas.create_arc(x1,y1,x2,y2,**kw); self.ids.append(i); return i

    def draw(self, phase=0, mode="idle", mouth=0.0):
        self._clear()
        cx, cy = self.cx, self.cy
        p = phase
        glow = self.C_CYAN if mode != "alert" else self.C_RED
        dim  = self.C_DIM  if mode != "alert" else "#3D0000"

        # Outer rotating arcs
        for i in range(3):
            a = (p*1.5 + i*40) % 360
            self._a(cx-70,cy-70,cx+70,cy+70, start=a, extent=80+i*20,
                    style=tk.ARC, outline=glow, width=1+i%2)
        for i in range(4):
            a = -(p*2.0 + i*30) % 360
            self._a(cx-55,cy-55,cx+55,cy+55, start=a, extent=50,
                    style=tk.ARC, outline=self.C_BLUE, width=1)

        # Core
        cr = 38 + math.sin(p*0.08)*3
        self._o(cx-cr,cy-cr,cx+cr,cy+cr, fill=dim, outline=glow, width=2)
        for r,c in [(30,"#001A2E"),(22,"#002A40"),(14,"#003D5C")]:
            self._o(cx-r,cy-r,cx+r,cy+r, fill=c, outline=glow if r==30 else self.C_DIM, width=1)

        # Eyes
        ey = cy - 8
        for xo in [-13, 13]:
            ex = cx + xo
            if mode == "thinking":
                sc = int(math.sin(p*0.25)*8)
                self._l(ex-9,ey,ex+9,ey, fill=dim, width=1)
                self._o(ex+sc-4,ey-4,ex+sc+4,ey+4, fill=self.C_CYAN, outline=self.C_GLOW, width=1)
            elif mode == "executing":
                sp = p*8 % 360
                self._a(ex-8,ey-8,ex+8,ey+8, start=sp, extent=240,
                        style=tk.ARC, outline=glow, width=2)
            else:
                self._o(ex-8,ey-6,ex+8,ey+6, fill=dim, outline=glow, width=1)
                px = ex + int(math.sin(p*0.04)*3)
                py = ey + int(math.cos(p*0.03)*2)
                self._o(px-4,py-4,px+4,py+4, fill=glow, outline=glow)
                self._o(px+1,py-3,px+3,py-1, fill="white", outline="white")

        # Nose
        ny = cy+2
        self._p(cx-3,ny+4, cx+3,ny+4, cx,ny, fill=glow, outline="")

        # Mouth / waveform
        my = cy+14
        if mode in ("talking","executing") and mouth > 0:
            bw,gap,n = 3,2,7
            sx = cx - (n*(bw+gap)-gap)//2
            for i in range(n):
                bx = sx + i*(bw+gap)
                h = abs(math.sin(p*0.2+i*0.8))*10*mouth + 2
                self._l(bx,my-h,bx,my+h, fill=glow, width=bw, capstyle=tk.ROUND)
        else:
            if mouth*5 < 1:
                self._l(cx-10,my,cx+10,my, fill=glow, width=2)
            else:
                self._o(cx-8,my-mouth*5,cx+8,my+mouth*5, fill=dim, outline=glow, width=1)

        # Status dot
        dr = 3 + abs(math.sin(p*0.1))*2
        dc = {"idle":self.C_CYAN,"thinking":self.C_GOLD,"talking":self.C_GREEN,
              "executing":self.C_GOLD,"alert":self.C_RED}.get(mode, self.C_CYAN)
        self._o(cx-dr,cy-36-dr,cx+dr,cy-36+dr, fill=dc, outline="white")

        # Data streams
        if mode in ("thinking","executing"):
            for i in range(6):
                ang = (p*3+i*60) % 360
                r = math.radians(ang)
                r1 = 42 + abs(math.sin(p*0.1+i))*5
                r2 = r1 + random.randint(5,18)
                self._l(cx+math.cos(r)*r1, cy+math.sin(r)*r1,
                        cx+math.cos(r)*r2, cy+math.sin(r)*r2, fill=glow, width=1)

        # HUD brackets
        for dx,dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
            bx,by,bl = cx+dx*58, cy+dy*58, 12
            self._l(bx,by, bx+dx*(-bl),by, fill=glow,width=1)
            self._l(bx,by, bx,by+dy*(-bl), fill=glow,width=1)

        lbl = {"idle":"STANDBY","thinking":"PROCESSING","talking":"RESPONDING",
               "executing":"EXECUTING","alert":"ALERT"}.get(mode,"JARVIS")
        self._t(cx,cy+88, text=lbl, fill=glow, font=("Courier New",7,"bold"))
        self._l(cx-40,cy+96,cx+40,cy+96, fill=dim, width=1)


# ─── Holo Bubble ──────────────────────────────────────────────────────────────
class HoloBubble(tk.Toplevel):
    def __init__(self, master, text, x, y):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#010101")
        self.configure(bg="#010101")
        fr = tk.Frame(self, bg="#001520", highlightbackground="#00F5FF", highlightthickness=1)
        fr.pack()
        lbl = tk.Label(fr, text=text, bg="#001520", fg="#00F5FF",
                       font=("Courier New", 9), wraplength=260, justify="left",
                       padx=10, pady=8)
        lbl.pack()
        self.update_idletasks()
        w, h = lbl.winfo_reqwidth()+2, lbl.winfo_reqheight()+2
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
        self.after(4500, self._die)

    def _die(self):
        try: self.destroy()
        except: pass


# ─── Google Gemini AI Brain ───────────────────────────────────────────────────
class JarvisAI:
    SYSTEM = """You are JARVIS, an advanced AI desktop assistant like Iron Man's JARVIS.
You control a Windows computer for the user. Be concise and professional.

Respond ONLY with a JSON object — no markdown, no explanation:
{
  "intent": "<intent>",
  "target": "<app/query/url or null>",
  "text": "<text to type or null>",
  "response": "<1-2 sentence JARVIS reply>"
}

Intents: open_app, screenshot, type_text, search_google, search_youtube,
open_url, volume_up, volume_down, volume_mute, system_info, time_date,
list_files, play_music, weather, minimize_all, chat, unknown

Examples:
"open chrome"   → {"intent":"open_app","target":"chrome","text":null,"response":"Launching Chrome now, sir."}
"what time"     → {"intent":"time_date","target":"time","text":null,"response":"Checking the time for you."}
"search dogs"   → {"intent":"search_google","target":"dogs","text":null,"response":"Searching Google for dogs."}
"type hello"    → {"intent":"type_text","target":null,"text":"hello","response":"Typing now. Focus your target window."}
"play lofi"     → {"intent":"play_music","target":"lofi","text":null,"response":"Opening lofi music on YouTube."}

Return ONLY the JSON. No backticks."""

    def __init__(self):
        self.history = []   # [{role, parts:[{text}]}]

    def _gemini_post(self, contents, system=None):
        body = {"contents": contents}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        body["generationConfig"] = {"temperature": 0.2, "maxOutputTokens": 300}
        r = requests.post(GEMINI_URL, json=body, timeout=15)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    def parse_command(self, msg):
        if not AI_OK:
            return None
        try:
            self.history.append({"role": "user", "parts": [{"text": msg}]})
            if len(self.history) > 20:
                self.history = self.history[-20:]

            raw = self._gemini_post(self.history, system=self.SYSTEM)

            # Strip accidental markdown fences
            if "```" in raw:
                raw = raw.split("```json")[-1] if "```json" in raw else raw.split("```")[1]
                raw = raw.split("```")[0].strip()

            parsed = json.loads(raw)
            self.history.append({"role": "model", "parts": [{"text": raw}]})
            return parsed
        except Exception as e:
            print(f"[Gemini parse error] {e}")
            return None

    def chat(self, msg):
        if not AI_OK:
            return "I need an API key to think, sir."
        try:
            contents = [{"role": "user", "parts": [{"text": msg}]}]
            system = ("You are JARVIS, Iron Man's AI assistant. "
                      "Be brief, helpful, professional. Max 2 sentences.")
            return self._gemini_post(contents, system=system)
        except Exception as e:
            return f"Processing error: {str(e)[:60]}"


# ─── Task Executor ────────────────────────────────────────────────────────────
class TaskExecutor:

    def open_app(self, name):
        key = name.lower().strip()
        cmd = APP_MAP.get(key)
        if not cmd:
            for k, v in APP_MAP.items():
                if key in k or k in key:
                    cmd = v; break
        if not cmd:
            try:
                subprocess.Popen(key, shell=True)
                return f"Attempting to launch '{name}'..."
            except:
                return f"App '{name}' not found in my database."
        try:
            if cmd.startswith("ms-"):
                os.startfile(cmd)
            else:
                subprocess.Popen(cmd, shell=True)
            return f"'{name.title()}' launched."
        except Exception as e:
            return f"Launch failed: {e}"

    def screenshot(self):
        if not PYAUTOGUI_OK:
            return "Install pyautogui: pip install pyautogui"
        try:
            time.sleep(0.3)
            fname = f"jarvis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(os.path.expanduser("~"), "Desktop", fname)
            pyautogui.screenshot().save(path)
            return f"Screenshot saved: {fname}"
        except Exception as e:
            return f"Screenshot failed: {e}"

    def type_text(self, text):
        if not PYAUTOGUI_OK:
            return "Install pyautogui: pip install pyautogui"
        try:
            time.sleep(1.0)
            pyautogui.typewrite(text, interval=0.03)
            return f"Typed: '{text[:50]}'"
        except Exception as e:
            return f"Typing failed: {e}"

    def vol_up(self):
        if PYAUTOGUI_OK:
            [pyautogui.press("volumeup") for _ in range(3)]
            return "Volume increased."
        return "pyautogui needed."

    def vol_down(self):
        if PYAUTOGUI_OK:
            [pyautogui.press("volumedown") for _ in range(3)]
            return "Volume decreased."
        return "pyautogui needed."

    def vol_mute(self):
        if PYAUTOGUI_OK:
            pyautogui.press("volumemute")
            return "Audio muted."
        return "pyautogui needed."

    def minimize_all(self):
        if PYAUTOGUI_OK:
            pyautogui.hotkey("win", "d")
            return "All windows minimized."
        return "pyautogui needed."

    def system_info(self):
        import platform
        return (f"Host: {platform.node()} | OS: {platform.system()} "
                f"{platform.release()} | CPU: {platform.processor()[:40]}")

    def time_date(self, target="time"):
        now = datetime.datetime.now()
        return (f"Date: {now.strftime('%A, %B %d, %Y')}"
                if "date" in target
                else f"Time: {now.strftime('%I:%M %p')}")

    def google(self, q):
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(q)}")
        return f"Google: {q}"

    def youtube(self, q):
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}")
        return f"YouTube: {q}"

    def url(self, u):
        if not u.startswith(("http://","https://")):
            u = "https://" + u
        webbrowser.open(u)
        return f"Opened: {u}"

    def music(self, song):
        webbrowser.open(
            f"https://www.youtube.com/results?search_query={urllib.parse.quote(song+' official audio')}")
        return f"Playing: {song}"

    def weather(self, loc):
        webbrowser.open(f"https://www.google.com/search?q=weather+{urllib.parse.quote(loc)}")
        return f"Weather for: {loc}"

    def list_files(self, folder=None):
        folder = folder or os.path.expanduser("~")
        try:
            items = os.listdir(folder)
            dirs  = [d for d in items if os.path.isdir(os.path.join(folder, d))]
            files = [f for f in items if os.path.isfile(os.path.join(folder, f))]
            return (f"[{folder}]\nDirs: {', '.join(dirs[:6])}\n"
                    f"Files: {', '.join(files[:10])}")
        except Exception as e:
            return f"Error: {e}"


# ─── Main App ─────────────────────────────────────────────────────────────────
class JarvisApp:
    W, H, FPS = 210, 250, 25

    def __init__(self):
        self.ai  = JarvisAI()
        self.exe = TaskExecutor()

        # Transparent avatar window
        self.root = tk.Tk()
        self.root.title("JARVIS")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.root.configure(bg="#010101")
        self.root.resizable(False, False)

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.wx = sw - self.W - 20
        self.wy = sh - self.H - 60
        self.root.geometry(f"{self.W}x{self.H}+{self.wx}+{self.wy}")

        self.cv = tk.Canvas(self.root, width=self.W, height=self.H,
                            bg="#010101", highlightthickness=0)
        self.cv.pack()
        self.av = JarvisAvatar(self.cv, cx=self.W//2, cy=self.H//2 - 15)

        self.cv.bind("<ButtonPress-1>",   self._db)
        self.cv.bind("<B1-Motion>",       self._dm)
        self.cv.bind("<ButtonRelease-1>", self._de)
        self.cv.bind("<Button-3>",        self._rc)

        self.mode   = "idle"
        self.phase  = 0
        self.bubble = None
        self._ds    = None

        self._build_hud()
        self._top_loop()
        self._tick()
        self.root.mainloop()

    # ── HUD ───────────────────────────────────────────────────────────────────
    def _build_hud(self):
        self.hud = tk.Toplevel(self.root)
        self.hud.title("JARVIS")
        self.hud.geometry("430x590+30+60")
        self.hud.attributes("-topmost", True)
        self.hud.resizable(True, True)
        self.hud.configure(bg="#000D1A")
        self.hud.protocol("WM_DELETE_WINDOW", lambda: None)

        # Title
        hdr = tk.Frame(self.hud, bg="#00293D", height=46)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="◈  J.A.R.V.I.S  ◈  GEMINI AI",
                 bg="#00293D", fg="#00F5FF",
                 font=("Courier New", 11, "bold")).pack(side="left", padx=12, pady=12)
        self.slbl = tk.Label(hdr, text="● STANDBY", bg="#00293D", fg="#00F5FF",
                             font=("Courier New", 8))
        self.slbl.pack(side="right", padx=12)

        # Hint
        tk.Label(self.hud,
                 text=' "open chrome"  "search X"  "screenshot"  "what time"  "play song"',
                 bg="#000D1A", fg="#004A6B", font=("Courier New", 7)).pack(fill="x", padx=6, pady=(4,0))

        # Log
        lf = tk.Frame(self.hud, bg="#000D1A")
        lf.pack(fill="both", expand=True, padx=8, pady=6)

        self.log = tk.Text(lf, bg="#000D1A", fg="#00C8FF",
                           font=("Courier New", 9), state="disabled",
                           relief="flat", wrap="word", padx=8, pady=6,
                           insertbackground="#00F5FF", selectbackground="#003D5C")
        sb = tk.Scrollbar(lf, command=self.log.yview,
                          bg="#001A2E", troughcolor="#000D1A")
        self.log.configure(yscrollcommand=sb.set)
        self.log.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.log.tag_configure("j", foreground="#00F5FF", font=("Courier New",9,"bold"))
        self.log.tag_configure("u", foreground="#88FF88", font=("Courier New",9))
        self.log.tag_configure("s", foreground="#FFD700", font=("Courier New",8,"italic"))
        self.log.tag_configure("r", foreground="#AAAAFF", font=("Courier New",8))
        self.log.tag_configure("e", foreground="#FF4444", font=("Courier New",8))

        # Input
        inf = tk.Frame(self.hud, bg="#00293D")
        inf.pack(fill="x", padx=8, pady=(0,8))
        tk.Label(inf, text="▶", bg="#00293D", fg="#00F5FF",
                 font=("Courier New", 11)).pack(side="left", padx=(8,2))
        self.ent = tk.Entry(inf, bg="#001520", fg="#00F5FF",
                            insertbackground="#00F5FF", font=("Courier New", 11),
                            relief="flat", highlightbackground="#00F5FF", highlightthickness=1)
        self.ent.pack(side="left", fill="x", expand=True, ipady=8, padx=4)
        self.ent.bind("<Return>", lambda e: self._send())
        self.ent.focus()
        tk.Button(inf, text="EXECUTE", bg="#003D5C", fg="#00F5FF",
                  font=("Courier New",9,"bold"), relief="flat", padx=12,
                  activebackground="#00F5FF", activeforeground="#000D1A",
                  command=self._send).pack(side="right", padx=(4,8), pady=4)

        self._sys(f"JARVIS ONLINE  |  AI: Google Gemini ({GEMINI_MODEL})")
        self._j("Good day. I am JARVIS, powered by Google Gemini. How may I assist?")

    def _w(self, txt, tag):
        self.log.configure(state="normal")
        self.log.insert("end", txt+"\n\n", tag)
        self.log.configure(state="disabled")
        self.log.see("end")

    def _j(self, t):   self._w("JARVIS » "+t, "j")
    def _u(self, t):   self._w("YOU    » "+t, "u")
    def _sys(self, t): self._w("[SYS]  "+t, "s")
    def _res(self, t): self._w("[RES]  "+t, "r")
    def _err(self, t): self._w("[ERR]  "+t, "e")

    def _status(self, t, c="#00F5FF"):
        self.slbl.configure(text=t, fg=c)

    # ── Send command ──────────────────────────────────────────────────────────
    def _send(self):
        cmd = self.ent.get().strip()
        if not cmd: return
        self.ent.delete(0, "end")
        self._u(cmd)
        threading.Thread(target=self._handle, args=(cmd,), daemon=True).start()

    def _handle(self, cmd):
        self.root.after(0, lambda: self._status("● PROCESSING", "#FFD700"))
        self.root.after(0, lambda: setattr(self, "mode", "thinking"))

        parsed = self.ai.parse_command(cmd) if AI_OK else None

        if parsed:
            intent   = parsed.get("intent", "unknown")
            target   = parsed.get("target") or ""
            text     = parsed.get("text") or ""
            response = parsed.get("response", "Processing...")
            self.root.after(0, lambda: self._j(response))
            self.root.after(0, lambda: self._bubble(response))
            self.root.after(0, lambda: self._run(intent, target, text))
        else:
            self.root.after(0, lambda: self._fallback(cmd))

    def _run(self, intent, target, text):
        self.mode = "executing"
        self._status("● EXECUTING", "#FFD700")

        def go():
            res = None
            e = self.exe
            if   intent == "open_app":     res = e.open_app(target)
            elif intent == "screenshot":   res = e.screenshot()
            elif intent == "type_text":    res = e.type_text(text or target)
            elif intent == "search_google":res = e.google(target)
            elif intent == "search_youtube":res = e.youtube(target)
            elif intent == "open_url":     res = e.url(target)
            elif intent == "volume_up":    res = e.vol_up()
            elif intent == "volume_down":  res = e.vol_down()
            elif intent == "volume_mute":  res = e.vol_mute()
            elif intent == "minimize_all": res = e.minimize_all()
            elif intent == "system_info":  res = e.system_info()
            elif intent == "time_date":    res = e.time_date(target)
            elif intent == "list_files":   res = e.list_files(target or None)
            elif intent == "play_music":   res = e.music(target)
            elif intent == "weather":      res = e.weather(target)
            elif intent == "chat":
                res = self.ai.chat(target or text) if AI_OK else "Need API key."
            elif intent == "unknown":
                res = "Command unclear. Please rephrase, sir."
                self.root.after(0, lambda: setattr(self, "mode", "alert"))

            if res:
                self.root.after(0, lambda: self._res(res))
                self.root.after(0, lambda: self._bubble(res[:120]))
            self.root.after(0, lambda: setattr(self, "mode", "idle"))
            self.root.after(0, lambda: self._status("● STANDBY"))

        threading.Thread(target=go, daemon=True).start()

    def _fallback(self, cmd):
        self.mode = "executing"
        cl = cmd.lower()
        res = None
        e = self.exe

        if "open " in cl:
            app = cl.replace("open","").strip()
            self._j(f"Launching {app.title()}...")
            self._bubble(f"Launching {app.title()}...")
            res = e.open_app(app)
        elif any(w in cl for w in ["screenshot","capture"]):
            self._j("Capturing screen.")
            res = e.screenshot()
        elif any(cl.startswith(p) for p in ["type ","write ","input "]):
            res = e.type_text(cmd.split(" ",1)[1] if " " in cmd else "")
        elif "search " in cl or "google " in cl:
            q = cl.replace("search","").replace("google","").replace("for","").strip()
            res = e.google(q)
        elif "youtube" in cl:
            res = e.youtube(cl.replace("youtube","").replace("search","").strip())
        elif "volume up" in cl:   res = e.vol_up()
        elif "volume down" in cl: res = e.vol_down()
        elif "mute" in cl:        res = e.vol_mute()
        elif any(w in cl for w in ["time","date","clock"]):
            res = e.time_date(cl); self._j(res)
        elif any(w in cl for w in ["system","computer","pc"]):
            res = e.system_info()
        elif "minimize" in cl or "desktop" in cl:
            res = e.minimize_all()
        elif "play " in cl:
            res = e.music(cl.replace("play","").strip())
        elif "weather" in cl:
            res = e.weather(cl.replace("weather","").strip())
        else:
            res = "Command not recognized. Set GEMINI_API_KEY for full AI."
            self.mode = "alert"
            self._err(res)
            self.root.after(2000, lambda: setattr(self,"mode","idle"))

        if res: self._res(res); self._bubble(res[:120])
        self.mode = "idle"
        self._status("● STANDBY")

    # ── Bubble ────────────────────────────────────────────────────────────────
    def _bubble(self, text):
        def do():
            if self.bubble:
                try: self.bubble.destroy()
                except: pass
            bx = self.wx - 295 if self.wx > 300 else self.wx + self.W + 10
            self.bubble = HoloBubble(self.root, text, bx, self.wy + 10)
        self.root.after(0, do)

    # ── Animation tick ────────────────────────────────────────────────────────
    def _tick(self):
        self.phase += 1
        m = abs(math.sin(self.phase*0.3)) if self.mode == "talking" else 0.0
        self.av.draw(phase=self.phase, mode=self.mode, mouth=m)
        self.root.after(1000//self.FPS, self._tick)

    def _top_loop(self):
        self.root.attributes("-topmost", True)
        self.root.after(3000, self._top_loop)

    # ── Drag ──────────────────────────────────────────────────────────────────
    def _db(self, e): self._ds = (e.x_root - self.wx, e.y_root - self.wy)
    def _dm(self, e):
        if self._ds:
            self.wx = e.x_root - self._ds[0]
            self.wy = e.y_root - self._ds[1]
            self.root.geometry(f"{self.W}x{self.H}+{int(self.wx)}+{int(self.wy)}")
    def _de(self, e): self._ds = None

    # ── Right-click menu ──────────────────────────────────────────────────────
    def _rc(self, e):
        m = tk.Menu(self.root, tearoff=0, bg="#001520", fg="#00F5FF",
                    activebackground="#003D5C", activeforeground="#00F5FF",
                    font=("Courier New",9))
        m.add_command(label="◈ Show HUD",      command=self._show_hud)
        m.add_command(label="◈ Screenshot",    command=lambda: threading.Thread(
            target=lambda: self._res(self.exe.screenshot()), daemon=True).start())
        m.add_command(label="◈ Minimize All",  command=self.exe.minimize_all)
        m.add_separator()
        m.add_command(label="✕ Quit JARVIS",   command=self._quit)
        try: m.tk_popup(e.x_root, e.y_root)
        finally: m.grab_release()

    def _show_hud(self):
        self.hud.deiconify(); self.hud.lift()
        self.hud.attributes("-topmost", True); self.ent.focus()

    def _quit(self):
        try: self.hud.destroy()
        except: pass
        self.root.quit(); self.root.destroy()


if __name__ == "__main__":
    JarvisApp()
