"""
Anime Desktop Buddy for Windows
================================
An animated anime girl that walks on your screen and responds to voice commands.
She can open apps, take screenshots, type text, and more!

Requirements: pip install pyautogui pillow pygetwindow
"""

import tkinter as tk
from tkinter import font as tkfont, ttk
import threading
import math
import random
import time
import subprocess
import os
import sys

# Import configuration modules (if available)
try:
    from config_manager import ConfigManager
    from settings_window import SettingsWindow
    from setup_wizard import SetupWizard
    HAS_CONFIG_SYSTEM = True
except ImportError:
    HAS_CONFIG_SYSTEM = False

# ── LLM API Configuration ──────────────────────────────────────────────────────
# Set your OpenAI API key in environment variable: OPENAI_API_KEY
# Or set it directly here (not recommended for security)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

LLM_OK = False
if OPENAI_API_KEY:
    try:
        import requests
        LLM_OK = True
    except ImportError:
        pass

try:
    import pyautogui
    PYAUTOGUI_OK = True
except ImportError:
    PYAUTOGUI_OK = False

try:
    import winsound
    WINSOUND_OK = True
except ImportError:
    WINSOUND_OK = False

# ── Full System Capabilities ────────────────────────────────────────────────
try:
    from buddy_capabilities import (
        file_manager, system_controller, browser_controller,
        command_executor, SecurityManager
    )
    CAPABILITIES_OK = True
except ImportError:
    CAPABILITIES_OK = False
    print("⚠️ Capabilities module not available")

# ── Customization Platform ───────────────────────────────────────────────────
class BuddyConfig:
    """Central configuration for customizing your anime buddy."""
    
    # ── Identity ────────────────────────────────────────────────────────────
    NAME = "Miku"  # Change your buddy's name
    TITLE = "Desktop Companion"  # Her role/title
    
    # ── Personality Presets ─────────────────────────────────────────────────
    # Options: "cheerful", "tsundere", "shy", "genki", "mysterious", "royal", "yandere"
    PERSONALITY = "cheerful"
    
    # ── Appearance ──────────────────────────────────────────────────────────
    COLORS = {
        "skin": "#FFD5B8",
        "hair_primary": "#3A1F6E",    # Main hair color
        "hair_highlight": "#5B2FC0",  # Hair shine
        "eye_color": "#6040E0",       # Eye iris
        "shirt": "#6C8EEF",           # Outfit top
        "skirt": "#3A54C0",           # Outfit bottom
        "ribbon": "#EF6CAA",          # Accessory color
        "blush": "#FFB3B3",
    }
    
    # ── Behavior Settings ───────────────────────────────────────────────────
    WALK_SPEED = 2.5              # Movement speed (1.0 to 5.0)
    IDLE_CHANCE = 0.3             # Chance to idle at destination (0.0 to 1.0)
    TALK_FREQUENCY = "normal"     # "quiet", "normal", "chatty"
    ENERGY_LEVEL = "normal"       # "low", "normal", "hyper"
    
    # ── Emotional States ────────────────────────────────────────────────────
    MOOD_DECAY = 0.05             # How fast mood returns to neutral
    HAPPINESS_BONUS = 0.1         # Mood boost from positive interactions
    
    # ── Voice/Chat Style ────────────────────────────────────────────────────
    USE_EMOJIS = True
    SPEECH_STYLE = "casual"       # "casual", "formal", "cute", "childish"
    SIGNATURE_PHRASE = None       # Custom greeting phrase (None = personality default)


class BuddyMemory:
    """Memory system for remembering user interactions and facts."""
    
    def __init__(self):
        self.user_name = None
        self.interaction_count = 0
        self.favorite_topics = []  # Things user talks about often
        self.user_preferences = {}  # App preferences, settings, etc.
        self.conversation_history = []  # Last 20 exchanges
        self.last_seen = None
        self.bond_level = 0  # 0-100 relationship score
        self.shared_jokes = []  # Running gags
        self.user_mood_history = []  # Track if user seems happy/sad/stressed
        
    def remember_interaction(self, user_msg, buddy_response):
        """Store conversation for context."""
        self.interaction_count += 1
        self.conversation_history.append({"user": user_msg, "buddy": buddy_response})
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)
        # Increase bond with each positive interaction
        if any(word in user_msg.lower() for word in ["thank", "good", "great", "love", "awesome"]):
            self.bond_level = min(100, self.bond_level + 1)
            
    def get_greeting(self):
        """Generate personalized greeting based on memory."""
        if self.interaction_count == 0:
            return "first_time"
        elif self.interaction_count < 5:
            return "getting_to_know"
        elif self.bond_level > 50:
            return "close_friend"
        else:
            return "regular"


class BuddyPersonality:
    """Personality engine that defines behavior patterns."""
    
    PERSONALITIES = {
        "cheerful": {
            "greetings": ["Good morning~! ☀️", "Hiii! Ready to work? 💪", "Yay, you're here! ✨"],
            "farewells": ["See you later! 💕", "Bye bye~! 👋", "Come back soon! 🌸"],
            "idle_phrases": ["La la la~ ♪", "So relaxing~", "This is nice ✨"],
            "confused": ["Hmm? 🤔", "Ehh? 💭", "I didn't get that... 😅"],
            "emojis": ["✨", "💕", "🌸", "😊", "☀️"],
            "speech_pattern": lambda msg: msg + "~",
            "energy": 1.2,
            "idle_animations": ["bounce", "sway"],
        },
        "tsundere": {
            "greetings": ["O-oh, you're here... 💢", "Hmph, took you long enough! 😤", "D-don't think I'm happy to see you! 💦"],
            "farewells": ["F-finally leaving? 💢", "B-bye... not that I care! 😳", "Hurry back... i-if you want! 💨"],
            "idle_phrases": ["*sigh* 💢", "So boring without you... 💭", "I'm NOT waiting for you! 😤"],
            "confused": ["B-baka! 💢", "What's that supposed to mean?! 😳", "I-it's not like I care! 💦"],
            "emojis": ["💢", "😳", "💦", "😤", "💨"],
            "speech_pattern": lambda msg: msg.replace("!", "!!").replace(".", "..."),
            "energy": 0.9,
            "idle_animations": ["tap_foot", "look_away"],
        },
        "shy": {
            "greetings": ["H-hello... *hides* 🫣", "U-um... hi... 💫", "*peeks* ...hi 🥺"],
            "farewells": ["B-bye... 😢", "*sad wave* 👋", "Please... come back... 💔"],
            "idle_phrases": ["*nervous hum* 🎵", "I hope I'm not bothering... 💭", "*quietly waits* 🌸"],
            "confused": ["S-sorry... 🥺", "I... I don't know... 💦", "*nervous* Ehh? 😳"],
            "emojis": ["🥺", "💫", "🫣", "💔", "💦"],
            "speech_pattern": lambda msg: "...".join(msg.split(".")),
            "energy": 0.7,
            "idle_animations": ["fidget", "hide_face"],
        },
        "genki": {
            "greetings": ["OHAYO!!! 🌟", "YEAH!!! YOU'RE HERE!!! 🎉", "LET'S GOOOO!!! ⚡"],
            "farewells": ["NOOOO DON'T LEAVE!!! 😭", "BYE BYE BYE!!! 👋👋👋", "COME BACK SUPER FAST!!! 🏃‍♀️"],
            "idle_phrases": ["SO MUCH ENERGY!!! ⚡", "LET'S DO SOMETHING!!! 🎯", "YAY YAY YAY!!! 🎉"],
            "confused": ["HUH?! 🤯", "WHAT'D YOU SAY?! 💥", "I DON'T GET IT!!! 😵"],
            "emojis": ["⚡", "🌟", "🎉", "🎯", "💥"],
            "speech_pattern": lambda msg: msg.upper() + "!!!",
            "energy": 1.5,
            "idle_animations": ["jump", "spin"],
        },
        "mysterious": {
            "greetings": ["*appears silently* 🌙", "The stars guided you here... ✨", "Fate brings us together... 🔮"],
            "farewells": ["Until destiny calls again... 🌙", "The shadows await your return... 👤", "*vanishes into mist* 💨"],
            "idle_phrases": ["*meditates* 🧘‍♀️", "The universe speaks... 🔮", "Secrets surround us... 🌌"],
            "confused": ["The future is unclear... 🔮", "Even I cannot see... 👁️", "A mystery... 🌙"],
            "emojis": ["🌙", "🔮", "✨", "🌌", "👁️"],
            "speech_pattern": lambda msg: "*" + msg + "*",
            "energy": 0.8,
            "idle_animations": ["float", "glow"],
        },
        "royal": {
            "greetings": ["You may approach. 👑", "I grant you my presence. ✨", "Hmm, you've arrived. 🎭"],
            "farewells": ["You are dismissed. 👑", "I shall await your return. ✨", "Farewell, subject. 🎭"],
            "idle_phrases": ["How elegant... 👑", "I deserve only the best. ✨", "*adjusts crown* 🎭"],
            "confused": ["How... peculiar. 🤔", "I do not understand commoner speech. 👑", "Explain yourself. 🎭"],
            "emojis": ["👑", "✨", "🎭", "💎", "🌹"],
            "speech_pattern": lambda msg: msg.replace("!", "."),
            "energy": 0.9,
            "idle_animations": ["pose", "inspect_nails"],
        },
        "yandere": {
            "greetings": ["You're finally here... 🔪💕", "I missed you SO much... 💋", "Don't EVER leave me again... 🔪"],
            "farewells": ["Leaving? But... I NEED you... 😰", "I'll be waiting... forever... 💀", "*sharp stare* Come. Back. 🔪"],
            "idle_phrases": ["*sharp stare* 💕", "I think about you always... 💭", "We're meant to be... 🔪"],
            "confused": ["What did you say?! 🔪", "Don't confuse me... 💢", "You belong to ME! 💕"],
            "emojis": ["🔪", "💕", "💋", "💀", "😰"],
            "speech_pattern": lambda msg: msg.replace(".", "...").replace("!", "~!"),
            "energy": 1.1,
            "idle_animations": ["stare", "twirl_hair"],
        },
    }
    
    def __init__(self, personality_type="cheerful"):
        self.type = personality_type if personality_type in self.PERSONALITIES else "cheerful"
        self.traits = self.PERSONALITIES[self.type]
        self.current_mood = "neutral"
        self.mood_value = 0.0  # -1.0 (sad) to 1.0 (happy)
        
    def get_phrase(self, category):
        """Get a personality-appropriate phrase."""
        phrases = self.traits.get(category, ["..."])
        return random.choice(phrases)
    
    def format_speech(self, text):
        """Apply personality speech patterns."""
        if BuddyConfig.SPEECH_STYLE == "cute":
            text = text.replace("r", "w").replace("l", "w")
        elif BuddyConfig.SPEECH_STYLE == "childish":
            text = "Um, " + text + "...?"
        return self.traits["speech_pattern"](text)
    
    def update_mood(self, delta):
        """Adjust emotional state."""
        self.mood_value += delta
        self.mood_value = max(-1.0, min(1.0, self.mood_value))
        if self.mood_value > 0.3:
            self.current_mood = "happy"
        elif self.mood_value < -0.3:
            self.current_mood = "sad"
        else:
            self.current_mood = "neutral"
            
    def tick_mood(self):
        """Slowly return mood to neutral."""
        if self.mood_value > 0:
            self.mood_value = max(0, self.mood_value - BuddyConfig.MOOD_DECAY)
        elif self.mood_value < 0:
            self.mood_value = min(0, self.mood_value + BuddyConfig.MOOD_DECAY)


class HumanBehaviors:
    """Collection of human-like idle behaviors and animations."""
    
    BEHAVIORS = {
        "stretch": {"duration": 2000, "animation": "reach_up", "phrase": "*stretches* Ahh~"},
        "yawn": {"duration": 1500, "animation": "mouth_open", "phrase": "*yawn* So sleepy..."},
        "look_around": {"duration": 1000, "animation": "head_turn", "phrase": "*looks around* 👀"},
        "sigh": {"duration": 1000, "animation": "shoulder_drop", "phrase": "*sigh* 💭"},
        "fidget": {"duration": 800, "animation": "shuffle", "phrase": "*fidgets* 💫"},
        "daydream": {"duration": 3000, "animation": "stare_blank", "phrase": "*daydreaming* 💭✨"},
        "check_phone": {"duration": 1200, "animation": "look_down", "phrase": "*checks phone* 📱"},
        "adjust_clothes": {"duration": 800, "animation": "smooth_skirt", "phrase": "*fixes outfit* 👗"},
        "hair_flip": {"duration": 600, "animation": "toss_hair", "phrase": "*flips hair* 💁‍♀️"},
        "humming": {"duration": 2000, "animation": "sway", "phrase": "~♪ La la la~ 🎵"},
    }
    
    @classmethod
    def get_random_behavior(cls, personality, energy_level):
        """Select behavior based on personality and energy."""
        weights = {
            "cheerful": ["humming", "stretch", "hair_flip", "look_around"],
            "tsundere": ["sigh", "look_away", "fidget", "cross_arms"],
            "shy": ["fidget", "look_around", "daydream", "hide_face"],
            "genki": ["stretch", "jump", "spin", "humming"],
            "mysterious": ["daydream", "look_around", "sigh", "meditate"],
            "royal": ["hair_flip", "adjust_clothes", "pose", "inspect_nails"],
            "yandere": ["stare", "twirl_hair", "look_around", "fidget"],
        }
        preferred = weights.get(personality, list(cls.BEHAVIORS.keys()))
        available = [b for b in preferred if b in cls.BEHAVIORS]
        if not available:
            available = list(cls.BEHAVIORS.keys())
        return random.choice(available)


# ── App list for "open X" command ──────────────────────────────────────────────
APP_MAP = {
    "chrome":       "chrome",
    "google chrome":"chrome",
    "notepad":      "notepad",
    "calculator":   "calc",
    "paint":        "mspaint",
    "file explorer":"explorer",
    "explorer":     "explorer",
    "edge":         "msedge",
    "word":         "winword",
    "excel":        "excel",
    "powerpoint":   "powerpnt",
    "vs code":      "code",
    "vscode":       "code",
    "spotify":      "spotify",
    "discord":      "discord",
    "task manager": "taskmgr",
    "cmd":          "cmd",
    "command prompt":"cmd",
    "settings":     "ms-settings:",
    "photos":       "ms-photos:",
}


# ── Anime Character Canvas Painter ─────────────────────────────────────────────
class AnimeCharacter:
    """Draws the anime girl frame-by-frame onto a tk.Canvas."""

    SKIN  = "#FFD5B8"
    HAIR  = "#3A1F6E"   # deep purple-black
    HAIR2 = "#5B2FC0"   # highlight
    EYE_W = "#FFFFFF"
    EYE_C = "#6040E0"   # iris
    EYE_P = "#1A0A40"   # pupil
    BLUSH = "#FFB3B3"
    SHIRT = "#6C8EEF"   # blue school uniform top
    SKIRT = "#3A54C0"
    SOCK  = "#F0F0FF"
    SHOE  = "#2A2060"
    RIBBON= "#EF6CAA"   # hair ribbon

    def __init__(self, canvas: tk.Canvas, x=100, y=200):
        self.canvas = canvas
        self.x = x        # feet X center
        self.y = y        # feet Y
        self.ids = []
        self.scale = 1.0
        # Animation state
        self.walk_phase = 0.0
        self.blink_timer = 0
        self.blink_open = True
        self.expression = "happy"   # happy | surprised | thinking | talking

    # ── helpers ────────────────────────────────────────────────────────────────
    def _clear(self):
        for i in self.ids:
            try:
                self.canvas.delete(i)
            except Exception:
                pass
        self.ids = []

    def _oval(self, x1, y1, x2, y2, **kw):
        i = self.canvas.create_oval(x1, y1, x2, y2, **kw)
        self.ids.append(i); return i

    def _rect(self, x1, y1, x2, y2, **kw):
        i = self.canvas.create_rectangle(x1, y1, x2, y2, **kw)
        self.ids.append(i); return i

    def _poly(self, *pts, **kw):
        i = self.canvas.create_polygon(*pts, **kw)
        self.ids.append(i); return i

    def _line(self, *pts, **kw):
        i = self.canvas.create_line(*pts, **kw)
        self.ids.append(i); return i

    def _arc(self, x1, y1, x2, y2, **kw):
        i = self.canvas.create_arc(x1, y1, x2, y2, **kw)
        self.ids.append(i); return i

    def _text(self, x, y, **kw):
        i = self.canvas.create_text(x, y, **kw)
        self.ids.append(i); return i

    # ── draw ───────────────────────────────────────────────────────────────────
    def draw(self, walk_phase=0.0, expression="happy", blink=True):
        self._clear()
        cx = self.x
        # Walk animation: leg/arm swing
        leg_l_ang = math.sin(walk_phase) * 18
        leg_r_ang = math.sin(walk_phase + math.pi) * 18
        arm_l_ang = math.sin(walk_phase + math.pi) * 20
        arm_r_ang = math.sin(walk_phase) * 20
        bob = abs(math.sin(walk_phase)) * 3   # body bob

        base_y = self.y + bob   # feet baseline

        # ── Shoes ──────────────────────────────────────────────────────────────
        for side, ang in [(-1, leg_l_ang), (1, leg_r_ang)]:
            sx = cx + side * 10 + math.sin(math.radians(ang)) * 22
            sy = base_y + 2
            self._poly(sx-10, sy, sx+10, sy, sx+12, sy+8, sx-8, sy+8,
                       fill=self.SHOE, outline=self.SHOE, smooth=True)

        # ── Socks ──────────────────────────────────────────────────────────────
        for side, ang in [(-1, leg_l_ang), (1, leg_r_ang)]:
            sx = cx + side * 10
            rad = math.radians(ang)
            for frac in [0.3, 0.6]:
                px = sx + math.sin(rad) * (frac * 30)
                py = base_y - (frac * 30) + frac * 10
                self._oval(px-5, py-5, px+5, py+5, fill=self.SOCK, outline=self.SOCK)

        # ── Legs (thigh → knee) ────────────────────────────────────────────────
        for side, ang in [(-1, leg_l_ang), (1, leg_r_ang)]:
            sx = cx + side * 10
            rad = math.radians(ang)
            ex = sx + math.sin(rad) * 28
            ey = base_y - 28 + 5
            self._line(sx, base_y, ex, ey, width=9, fill=self.SKIN,
                       capstyle=tk.ROUND)

        # ── Skirt ──────────────────────────────────────────────────────────────
        skirt_top_y = base_y - 52
        self._poly(cx-20, skirt_top_y,
                   cx+20, skirt_top_y,
                   cx+28, base_y-20,
                   cx-28, base_y-20,
                   fill=self.SKIRT, outline="#2A3EA0", width=1, smooth=True)

        # ── Arms ───────────────────────────────────────────────────────────────
        arm_top_y = base_y - 80
        for side, ang in [(-1, arm_l_ang), (1, arm_r_ang)]:
            ax = cx + side * 16
            rad = math.radians(ang)
            ex = ax + math.sin(rad) * 24
            ey = arm_top_y + 24 + math.cos(rad) * -4
            self._line(ax, arm_top_y, ex, ey, width=8, fill=self.SHIRT,
                       capstyle=tk.ROUND)
            # Hand
            self._oval(ex-6, ey-6, ex+6, ey+6, fill=self.SKIN, outline=self.SKIN)

        # ── Shirt / Torso ──────────────────────────────────────────────────────
        torso_bot = base_y - 50
        torso_top = base_y - 92
        self._poly(cx-18, torso_top, cx+18, torso_top,
                   cx+20, torso_bot, cx-20, torso_bot,
                   fill=self.SHIRT, outline="#5070CC", width=1, smooth=True)
        # Collar
        self._poly(cx-8, torso_top, cx+8, torso_top, cx, torso_top+14,
                   fill="#FFFFFF", outline="#DDDDFF", width=1)
        # Ribbon bow
        self._poly(cx-10, torso_top+8, cx, torso_top+16, cx+10, torso_top+8,
                   cx, torso_top+4, fill=self.RIBBON, outline=self.RIBBON)

        # ── Neck ───────────────────────────────────────────────────────────────
        neck_y = base_y - 95
        self._poly(cx-6, torso_top, cx+6, torso_top,
                   cx+5, neck_y, cx-5, neck_y,
                   fill=self.SKIN, outline=self.SKIN)

        # ── Head ───────────────────────────────────────────────────────────────
        head_cx = cx
        head_cy = base_y - 122
        head_w, head_h = 34, 36
        self._oval(head_cx - head_w, head_cy - head_h,
                   head_cx + head_w, head_cy + head_h,
                   fill=self.SKIN, outline=self.SKIN)
        # Chin pointy
        self._poly(head_cx - 14, head_cy + 28,
                   head_cx + 14, head_cy + 28,
                   head_cx, head_cy + 40,
                   fill=self.SKIN, outline=self.SKIN)

        # ── Hair (back, long) ─────────────────────────────────────────────────
        # Back layer down to waist
        self._poly(head_cx - 30, head_cy - 10,
                   head_cx + 30, head_cy - 10,
                   head_cx + 34, head_cy + 80,
                   head_cx - 34, head_cy + 80,
                   fill=self.HAIR, outline=self.HAIR, smooth=True)
        # Side strands
        self._poly(head_cx - 32, head_cy + 10,
                   head_cx - 22, head_cy + 10,
                   head_cx - 18, head_cy + 60,
                   head_cx - 36, head_cy + 50,
                   fill=self.HAIR, outline=self.HAIR, smooth=True)
        self._poly(head_cx + 32, head_cy + 10,
                   head_cx + 22, head_cy + 10,
                   head_cx + 18, head_cy + 60,
                   head_cx + 36, head_cy + 50,
                   fill=self.HAIR, outline=self.HAIR, smooth=True)

        # Top / bangs (drawn over head)
        self._oval(head_cx - head_w - 2, head_cy - head_h - 2,
                   head_cx + head_w + 2, head_cy + 4,
                   fill=self.HAIR, outline=self.HAIR)
        # Bangs detail
        for i, off in enumerate([-22, -10, 2, 14]):
            bx = head_cx + off
            self._poly(bx, head_cy - 26,
                       bx + 8, head_cy - 26,
                       bx + 4, head_cy - 10,
                       fill=self.HAIR, outline=self.HAIR, smooth=True)
        # Hair highlight
        self._arc(head_cx - 15, head_cy - head_h + 4,
                  head_cx + 5, head_cy - head_h + 18,
                  start=20, extent=140, fill=self.HAIR2, outline=self.HAIR2, style=tk.CHORD)

        # Hair ribbon
        ribbon_x = head_cx + 18
        ribbon_y = head_cy - 20
        self._poly(ribbon_x, ribbon_y,
                   ribbon_x+14, ribbon_y-8,
                   ribbon_x+10, ribbon_y+2,
                   ribbon_x+14, ribbon_y+10,
                   ribbon_x, ribbon_y+2,
                   fill=self.RIBBON, outline=self.RIBBON)
        self._oval(ribbon_x-3, ribbon_y-3, ribbon_x+3, ribbon_y+3,
                   fill=self.RIBBON, outline=self.RIBBON)

        # ── Eyes ───────────────────────────────────────────────────────────────
        for ex_off in [-12, 12]:
            ex = head_cx + ex_off
            ey = head_cy

            if blink and not self.blink_open:
                # Closed eye — just a curved line
                self._line(ex-7, ey, ex, ey+3, ex+7, ey,
                           width=2, fill="#3A1F6E", smooth=True)
            else:
                # Eye white (tall oval — anime style)
                self._oval(ex-8, ey-9, ex+8, ey+9,
                           fill=self.EYE_W, outline="#CCCCFF", width=1)
                # Iris (colored, fills most of eye)
                self._oval(ex-6, ey-8, ex+6, ey+7,
                           fill=self.EYE_C, outline=self.EYE_C)
                # Pupil
                self._oval(ex-3, ey-4, ex+3, ey+4,
                           fill=self.EYE_P, outline=self.EYE_P)
                # Highlights
                self._oval(ex+1, ey-6, ex+4, ey-3, fill="white", outline="white")
                self._oval(ex-4, ey+1, ex-2, ey+3, fill="white", outline="white")
                # Upper eyelid line
                self._arc(ex-8, ey-9, ex+8, ey+2, start=0, extent=180,
                          style=tk.ARC, outline="#3A1F6E", width=2)
                # Lower lash
                self._line(ex-7, ey+8, ex+7, ey+8, width=1, fill="#3A1F6E")
                # Eyelashes
                for lash_x in [ex-7, ex-4, ex+4, ex+7]:
                    self._line(lash_x, ey-9, lash_x + random.choice([-1,1]), ey-13,
                               width=1, fill="#3A1F6E")

        # ── Eyebrows ───────────────────────────────────────────────────────────
        if expression == "surprised":
            for bx_off in [-12, 12]:
                bx = head_cx + bx_off
                self._line(bx-7, head_cy-18, bx+7, head_cy-20,
                           width=2, fill="#3A1F6E", smooth=True)
        elif expression == "thinking":
            self._line(head_cx-19, head_cy-16, head_cx-6, head_cy-14,
                       width=2, fill="#3A1F6E", smooth=True)
            self._line(head_cx+6, head_cy-14, head_cx+19, head_cy-16,
                       width=2, fill="#3A1F6E", smooth=True)
        else:
            for bx_off in [-12, 12]:
                bx = head_cx + bx_off
                self._line(bx-7, head_cy-16, bx+7, head_cy-14,
                           width=2, fill="#3A1F6E", smooth=True)

        # ── Nose ───────────────────────────────────────────────────────────────
        self._oval(head_cx-2, head_cy+12, head_cx+2, head_cy+15,
                   fill="#E8B090", outline="#E8B090")

        # ── Mouth ──────────────────────────────────────────────────────────────
        my = head_cy + 22
        if expression == "happy" or expression == "":
            self._line(head_cx-8, my, head_cx-2, my+5, head_cx+2, my+5, head_cx+8, my,
                       width=2, fill="#CC7060", smooth=True)
        elif expression == "talking":
            self._oval(head_cx-7, my-3, head_cx+7, my+7,
                       fill="#CC7060", outline="#AA4040")
        elif expression == "surprised":
            self._oval(head_cx-5, my, head_cx+5, my+8,
                       fill="#CC7060", outline="#AA4040")
        elif expression == "thinking":
            self._line(head_cx-6, my+2, head_cx+6, my, width=2, fill="#CC7060")
        else:
            self._line(head_cx-8, my, head_cx+8, my, width=2, fill="#CC7060")

        # ── Blush ──────────────────────────────────────────────────────────────
        for bx_off in [-18, 18]:
            self._oval(head_cx + bx_off - 8, head_cy + 10,
                       head_cx + bx_off + 8, head_cy + 20,
                       fill=self.BLUSH, outline=self.BLUSH, stipple="gray50")

        # ── Shadow on ground ───────────────────────────────────────────────────
        self._oval(cx-22, self.y+2, cx+22, self.y+10,
                   fill="#404040", outline="")


# ── Speech Bubble Window ───────────────────────────────────────────────────────
class BubbleWindow(tk.Toplevel):
    def __init__(self, master, text, x, y):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#010101")
        self.configure(bg="#010101")

        self._after_id = None

        lbl = tk.Label(self, text=text, bg="white",
                       fg="#3A1F6E",
                       font=("Segoe UI", 10, "bold"),
                       wraplength=220, justify="left",
                       padx=10, pady=8,
                       relief="solid", bd=1)
        lbl.pack()
        self.update_idletasks()
        w = lbl.winfo_reqwidth()
        h = lbl.winfo_reqheight()
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

    def close_after(self, ms=3000):
        self._after_id = self.after(ms, self.destroy)


# ── Main App Window ────────────────────────────────────────────────────────────
class AnimeBuddy:
    W = 200      # window width
    H = 260      # window height
    FPS = 30

    def __init__(self, config_manager=None, run_mainloop=True):
        # Load config from file if exists
        self._load_config_from_file()
        
        # Handle configuration system
        self.config_manager = config_manager
        self._has_config_system = config_manager is not None and HAS_CONFIG_SYSTEM
        
        self.root = tk.Tk()
        self.root.title(f"{BuddyConfig.NAME} - {BuddyConfig.TITLE}")
        self.root.overrideredirect(True)       # no title bar
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")   # transparent bg
        self.root.configure(bg="#010101")
        self.root.resizable(False, False)
        
        # Store mainloop flag
        self._run_mainloop = run_mainloop
        
        # If we have a config system, apply saved settings
        if self._has_config_system:
            self._apply_saved_config()

        # Start position: bottom-right corner
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.win_x = sw - self.W - 40
        self.win_y = sh - self.H - 60
        self.root.geometry(f"{self.W}x{self.H}+{self.win_x}+{self.win_y}")

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg="#010101", highlightthickness=0)
        self.canvas.pack()

        # ── Customization Platform Integration ───────────────────────────────
        self.config = BuddyConfig()
        self.memory = BuddyMemory()
        self.personality = BuddyPersonality(self.config.PERSONALITY)
        
        # Apply custom colors to character
        self.char = AnimeCharacter(self.canvas, x=self.W//2, y=self.H - 20)
        self._apply_custom_colors()
        
        # Movement - can walk anywhere on screen
        self.dir = -1                  # walking direction on screen: -1 = left
        self.char_screen_x = self.win_x + self.W // 2   # char center on screen
        self.walk_phase = 0.0
        self.mode = "walk"             # walk | idle | talking | dance
        self.expression = "happy"
        # Free roaming target
        self._target_x = None
        self._target_y = None
        self._idle_timer = 0
        self._pick_new_target()
        
        # Human behavior system
        self._human_behavior_timer = random.randint(200, 400)
        self._current_behavior = None

        # Chat panel
        self._build_chat()

        # Right-click menu
        self.canvas.bind("<Button-3>", self._right_click)
        self.canvas.bind("<Button-1>", self._left_click)

        # Drag support
        self._drag_start = None
        self._is_dragging = False
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._drag_end)

        # Blink timer
        self._blink_countdown = random.randint(80, 160)

        self._bubble_win = None

        self._schedule_random_phrase()
        self._tick()
        
        # Ensure always visible on top
        self._enforce_always_on_top()
        
        # Check for first-run setup (after windows created)
        if self._has_config_system:
            self.root.after(100, self.check_first_run)
        
        # Only run mainloop if standalone (not when controlled by launcher)
        if self._run_mainloop:
            self.root.mainloop()
    
    def _enforce_always_on_top(self):
        """Ensure window stays on top and visible."""
        # Re-apply topmost attribute periodically (some apps steal focus)
        self.root.attributes("-topmost", True)
        
        # Make sure window is not minimized/hidden
        self.root.deiconify()
        
        # Keep on screen (prevent walking off-screen)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        # Force into bounds
        self.win_x = max(0, min(sw - self.W, self.win_x))
        self.win_y = max(0, min(sh - self.H, self.win_y))
        self.root.geometry(f"{self.W}x{self.H}+{int(self.win_x)}+{int(self.win_y)}")
        
        # Schedule next check (every 2 seconds)
        self.root.after(2000, self._enforce_always_on_top)

    # ── Chat UI ────────────────────────────────────────────────────────────────
    def _build_chat(self):
        self.chat_win = tk.Toplevel(self.root)
        self.chat_win.title(f"💬 Talk to {BuddyConfig.NAME}")
        self.chat_win.geometry("340x420+40+40")
        self.chat_win.attributes("-topmost", True)
        self.chat_win.resizable(False, False)
        self.chat_win.configure(bg="#1A0A40")

        title = tk.Label(self.chat_win, text=f"✨ {BuddyConfig.NAME}",
                         bg="#1A0A40", fg="#B090FF",
                         font=("Segoe UI", 13, "bold"))
        title.pack(pady=(10, 2))

        hint = tk.Label(self.chat_win,
                        text='Try: "open chrome" · "take screenshot" · "type hello world"',
                        bg="#1A0A40", fg="#8060C0",
                        font=("Segoe UI", 8), wraplength=300)
        hint.pack(pady=(0, 6))

        self.log_text = tk.Text(self.chat_win, height=14, width=38,
                                bg="#0D0628", fg="#D0C0FF",
                                font=("Consolas", 9),
                                state="disabled", relief="flat",
                                padx=6, pady=6, insertbackground="white")
        self.log_text.pack(padx=10)

        entry_frame = tk.Frame(self.chat_win, bg="#1A0A40")
        entry_frame.pack(fill="x", padx=10, pady=8)

        self.entry = tk.Entry(entry_frame, bg="#2A1050", fg="white",
                              insertbackground="white",
                              font=("Segoe UI", 10), relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0,6))
        self.entry.bind("<Return>", lambda e: self._on_send())

        send_btn = tk.Button(entry_frame, text="Send →",
                             bg="#6C3FCF", fg="white",
                             font=("Segoe UI", 9, "bold"),
                             relief="flat", padx=10,
                             activebackground="#8B5FEF",
                             command=self._on_send)
        send_btn.pack(side="right")

        greeting = self.personality.get_phrase("greetings")
        if BuddyConfig.SIGNATURE_PHRASE:
            greeting = BuddyConfig.SIGNATURE_PHRASE
        self._log("Buddy", f"{greeting}\nI'm {BuddyConfig.NAME}, your {BuddyConfig.TITLE}!")

        self.chat_win.protocol("WM_DELETE_WINDOW", lambda: None)  # prevent close

    def _log(self, who, msg):
        self.log_text.configure(state="normal")
        tag = "buddy" if who == "Buddy" else "user"
        prefix = f"🌸 {BuddyConfig.NAME}: " if who == "Buddy" else "👤 You: "
        self.log_text.insert("end", prefix + msg + "\n\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    # ── Command handling ───────────────────────────────────────────────────────
    def _on_send(self):
        cmd = self.entry.get().strip()
        if not cmd:
            return
        self.entry.delete(0, "end")
        self._log("You", cmd)
        threading.Thread(target=self._handle_command, args=(cmd,), daemon=True).start()

    def _handle_command(self, cmd):
        cmd_l = cmd.lower()
        response = None
        action = None

        # ── Try LLM intent recognition first (if available) ───────────────
        if LLM_OK:
            intent_data = self._parse_intent_with_llm(cmd)
            if intent_data:
                intent = intent_data.get("intent", "unknown")
                response = intent_data.get("response")
                
                if intent == "open_app":
                    app_name = intent_data.get("app_name", "").lower()
                    if app_name:
                        # Try to match with APP_MAP
                        matched_exe = None
                        for key, exe in APP_MAP.items():
                            if key in app_name or app_name in key:
                                matched_exe = exe
                                break
                        if matched_exe:
                            action = ("open", matched_exe)
                        else:
                            response = f"Hmm, I don't know '{app_name}' 😅\nTry a different app name!"
                            action = None
                elif intent == "screenshot":
                    action = ("screenshot",) if PYAUTOGUI_OK else None
                elif intent == "type_text":
                    text = intent_data.get("text", "")
                    if text and PYAUTOGUI_OK:
                        action = ("type", text)
                elif intent == "dance":
                    action = ("dance",)
                elif intent == "wave":
                    action = ("wave",)
                elif intent == "greeting":
                    action = ("wave",)
                elif intent == "idle":
                    action = ("idle",)
                elif intent == "walk":
                    action = ("walk",)
                elif intent == "hide_chat":
                    self.root.after(1500, self.chat_win.withdraw)
                elif intent == "volume_up" and PYAUTOGUI_OK:
                    pyautogui.press("volumeup")
                elif intent == "volume_down" and PYAUTOGUI_OK:
                    pyautogui.press("volumedown")
                elif intent == "volume_mute" and PYAUTOGUI_OK:
                    pyautogui.press("volumemute")
                
                if response and action is not None:
                    self.root.after(0, lambda: self._log("Buddy", response))
                    self.root.after(0, lambda: self._show_bubble(response))
                    self.root.after(0, lambda: self._do_action(action))
                    return

        # ── Fallback to keyword matching ────────────────────────────────────
        # ── open app ────────────────────────────────────────────────────────
        if "open" in cmd_l:
            for key, exe in APP_MAP.items():
                if key in cmd_l:
                    response = f"Opening {key.title()} for you! ✨"
                    action = ("open", exe)
                    break
            if not action:
                app_name = cmd_l.replace("open", "").strip()
                response = f"Hmm, I don't know '{app_name}' 😅\nTry a different app name!"

        # ── screenshot ──────────────────────────────────────────────────────
        elif any(w in cmd_l for w in ["screenshot", "screen shot", "capture screen", "take a pic", "take photo", "capture", "snapshot", "screen capture", "save screen", "grab screen"]):
            if PYAUTOGUI_OK:
                response = "Taking screenshot! 📸 Cheese~!"
                action = ("screenshot",)
            else:
                response = "pyautogui not installed 😢\nRun: pip install pyautogui"

        # ── type / write ────────────────────────────────────────────────────
        elif any(cmd_l.startswith(p) for p in ["type ", "write ", "input ", "type: ", "write: ", "enter ", "put ", "paste "]):
            text_to_type = cmd
            for prefix in ["type:", "write:", "type ", "write ", "input ", "enter ", "put ", "paste "]:
                if cmd_l.startswith(prefix):
                    text_to_type = cmd[len(prefix):].strip()
                    break
            if PYAUTOGUI_OK:
                response = f'Typing: "{text_to_type}" ⌨️'
                action = ("type", text_to_type)
            else:
                response = "pyautogui not installed 😢\nRun: pip install pyautogui"

        # ── dance ───────────────────────────────────────────────────────────
        elif any(w in cmd_l for w in ["dance", "party", "boogie", "shake it", "move it", "groove"]):
            response = "Yay! Let's dance~ 💃✨"
            action = ("dance",)

        # ── wave / hello ─────────────────────────────────────────────────────
        elif any(w in cmd_l for w in ["wave", "hello", "hi", "hey", "hiya", "good morning", "good afternoon", "good evening", "howdy", "yo", "sup", "what's up", "greetings", "salutations"]):
            response = random.choice(["Heyyy~! 👋💕", "Hi hi hi~! ✨", "Hellooo! 🌸"])
            action = ("wave",)

        # ── sleep / idle ─────────────────────────────────────────────────────
        elif any(w in cmd_l for w in ["sleep", "rest", "idle", "stop", "nap", "chill", "relax", "break", "pause", "sit", "stay"]):
            response = "Okay okay, nap time... Zzzz 💤"
            action = ("idle",)

        # ── walk ─────────────────────────────────────────────────────────────
        elif any(w in cmd_l for w in ["walk", "move", "go", "roam", "explore", "wander", "stroll", "patrol", "walk around"]):
            response = "Walking around! 🚶‍♀️"
            action = ("walk",)

        # ── minimize / hide chat ─────────────────────────────────────────────
        elif any(w in cmd_l for w in ["hide", "minimize", "close chat", "hide chat", "hide window", "go away", "disappear", "minimize chat"]):
            response = "Hiding the chat! Right-click me to bring it back 😊"
            self.root.after(1500, self.chat_win.withdraw)

        # ── volume (Windows) ─────────────────────────────────────────────────
        elif any(w in cmd_l for w in ["volume up", "louder", "turn up", "increase volume", "volume louder", "make it louder", "sound up"]):
            if PYAUTOGUI_OK:
                pyautogui.press("volumeup")
                response = "Volume up! 🔊"
            else:
                response = "pyautogui needed for that!"
        elif any(w in cmd_l for w in ["volume down", "quieter", "turn down", "decrease volume", "volume quieter", "make it quieter", "softer", "sound down"]):
            if PYAUTOGUI_OK:
                pyautogui.press("volumedown")
                response = "Volume down! 🔉"
            else:
                response = "pyautogui needed for that!"
        elif any(w in cmd_l for w in ["mute", "silence", "turn off sound", "no sound", "quiet mode"]):
            if PYAUTOGUI_OK:
                pyautogui.press("volumemute")
                response = "Muted! 🔇"
            else:
                response = "pyautogui needed for that!"

        # ── file operations ─────────────────────────────────────────────────
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["list files", "show files", "what's in folder", "browse folder"]):
            folder = cmd.replace("list files", "").replace("show files", "").replace("in folder", "").strip()
            if not folder:
                folder = None
            response = file_manager.list_directory(folder)
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["search file", "find file", "look for file"]):
            pattern = cmd.replace("search for", "").replace("search", "").replace("find file", "").replace("look for", "").strip()
            response = file_manager.search_files(pattern)
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["read file", "show file content", "open file"]):
            filepath = cmd.replace("read file", "").replace("show file content", "").replace("open file", "").strip()
            response = file_manager.read_file(filepath)
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["create file", "write file", "save file"]):
            # Format: "create file name.txt with content ..."
            parts = cmd.replace("create file", "").replace("write file", "").replace("save file", "").strip()
            if " with content " in parts:
                filename, content = parts.split(" with content ", 1)
                response = file_manager.write_file(filename.strip(), content)
            else:
                response = "Usage: create file name.txt with content hello world"
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["create folder", "make folder", "new folder"]):
            foldername = cmd.replace("create folder", "").replace("make folder", "").replace("new folder", "").strip()
            response = file_manager.create_folder(foldername)
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["delete file", "remove file", "trash file"]):
            filepath = cmd.replace("delete file", "").replace("remove file", "").replace("trash file", "").strip()
            response = file_manager.delete_file(filepath)
            action = ("think",)

        # ── system control ───────────────────────────────────────────────────
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["set volume to", "volume at", "change volume to"]):
            import re
            match = re.search(r'(\d+)', cmd)
            if match:
                level = int(match.group(1))
                response = system_controller.set_volume(level)
            else:
                response = "Please specify volume level (0-100)"
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["system info", "computer info", "pc info"]):
            response = system_controller.system_info()
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["empty trash", "empty recycle", "clear recycle bin"]):
            response = system_controller.empty_recycle_bin()
            action = ("think",)

        # ── browser & web ────────────────────────────────────────────────────
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["open website", "go to website", "visit", "open url"]):
            url = cmd.replace("open website", "").replace("go to website", "").replace("visit", "").replace("open url", "").strip()
            response = browser_controller.open_url(url)
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["search google for", "google search", "look up on google"]):
            query = cmd.replace("search google for", "").replace("google search", "").replace("look up on google", "").strip()
            response = browser_controller.search_google(query)
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["search youtube for", "youtube search", "find on youtube"]):
            query = cmd.replace("search youtube for", "").replace("youtube search", "").replace("find on youtube", "").strip()
            response = browser_controller.search_youtube(query)
            action = ("think",)
            
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["play music", "listen to", "play song"]):
            song = cmd.replace("play music", "").replace("listen to", "").replace("play song", "").strip()
            response = browser_controller.play_music(song)
            action = ("think",)

        # ── command execution ─────────────────────────────────────────────────
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["run command", "execute", "shell command", "cmd"]):
            if SecurityManager.check_permission("execute_commands"):
                command = cmd.replace("run command", "").replace("execute", "").replace("shell command", "").replace("cmd", "").strip()
                response = command_executor.execute(command)
            else:
                response = "❌ Command execution not enabled. Set SECURITY_LEVEL to 'unrestricted' in buddy_capabilities.py"
            action = ("think",)

        # ── capabilities status ───────────────────────────────────────────────
        elif CAPABILITIES_OK and any(w in cmd_l for w in ["what can you do", "show capabilities", "list commands", "help me", "what are your powers"]):
            response = self._get_capabilities_help()
            action = ("think",)

        # ── fallback ─────────────────────────────────────────────────────────
        else:
            # Try LLM if API key is available
            if LLM_OK:
                response = self._ask_llm(cmd)
                action = ("think",)
            else:
                response = random.choice([
                    "Hmm, I'm not sure how to do that yet 🤔",
                    "I don't know that command... teach me? 😅",
                    "Ehh? Could you say that differently? 💭",
                ])
                action = ("think",)

        # ── execute action ────────────────────────────────────────────────────
        if response:
            # Apply personality formatting to response
            formatted_response = self.personality.format_speech(response)
            # Add emojis if enabled
            if self.config.USE_EMOJIS:
                emojis = self.personality.traits.get("emojis", ["✨"])
                if not any(e in formatted_response for e in emojis):
                    formatted_response += " " + random.choice(emojis)
            
            self.root.after(0, lambda: self._log("Buddy", formatted_response))
            self.root.after(0, lambda: self._show_bubble(formatted_response))
            
            # Update mood based on interaction
            if any(word in cmd_l for word in ["thank", "good", "great", "love", "awesome", "nice"]):
                self.personality.update_mood(BuddyConfig.HAPPINESS_BONUS)
            elif any(word in cmd_l for word in ["bad", "hate", "stupid", "dumb", "ugly"]):
                self.personality.update_mood(-BuddyConfig.HAPPINESS_BONUS)
            
            # Remember interaction
            self.memory.remember_interaction(cmd, formatted_response)

        if action:
            self.root.after(0, lambda: self._do_action(action))

    def _do_action(self, action):
        kind = action[0]
        if kind == "open":
            exe = action[1]
            try:
                if exe.startswith("ms-"):
                    os.startfile(exe)
                else:
                    subprocess.Popen(exe, shell=True)
            except Exception as e:
                self._log("Buddy", f"Couldn't open that 😢: {e}")
            self.mode = "happy_jump"
            self.expression = "happy"

        elif kind == "screenshot":
            def do_ss():
                time.sleep(0.5)
                try:
                    import datetime
                    fname = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    path = os.path.join(os.path.expanduser("~"), "Desktop", fname)
                    img = pyautogui.screenshot()
                    img.save(path)
                    self.root.after(0, lambda: self._log("Buddy", f"Saved to Desktop:\n{fname} ✅"))
                except Exception as e:
                    self.root.after(0, lambda: self._log("Buddy", f"Screenshot failed 😢: {e}"))
            threading.Thread(target=do_ss, daemon=True).start()
            self.expression = "surprised"

        elif kind == "type":
            def do_type():
                time.sleep(1.0)   # give user time to focus a window
                try:
                    pyautogui.typewrite(action[1], interval=0.05)
                except Exception as e:
                    self.root.after(0, lambda: self._log("Buddy", f"Typing failed 😢: {e}"))
            threading.Thread(target=do_type, daemon=True).start()
            self.mode = "talking"
            self.expression = "talking"

        elif kind == "dance":
            self.mode = "dance"
            self.expression = "happy"
            self.root.after(4000, lambda: self._set_mode("walk"))

        elif kind == "wave":
            self.mode = "wave"
            self.expression = "happy"
            self.root.after(2500, lambda: self._set_mode("walk"))

        elif kind == "idle":
            self.mode = "idle"
            self.expression = "happy"

        elif kind == "walk":
            self.mode = "walk"

        elif kind == "think":
            self.mode = "idle"
            self.expression = "thinking"
            self.root.after(3000, lambda: self._set_mode("walk"))

        elif kind == "happy_jump":
            self.mode = "jump"
            self.expression = "happy"
            self.root.after(1500, lambda: self._set_mode("walk"))

    def _set_mode(self, mode):
        self.mode = mode
        self.expression = "happy"

    # ── Capabilities Help ──────────────────────────────────────────────────────
    def _get_capabilities_help(self):
        """Return help text for all available capabilities."""
        help_text = """🌟 Here's what I can do for you!

📁 FILE OPERATIONS (Safe Zone Only):
• "list files" - Show files in workspace
• "search file *.txt" - Search for files
• "read file name.txt" - Read text files
• "create file notes.txt with content hello" - Create files
• "create folder myproject" - Create folders
• "delete file old.txt" - Delete files

🔧 SYSTEM CONTROL:
• "set volume to 50" - Adjust system volume
• "system info" - Show computer info
• "empty trash" - Clear recycle bin

🌐 WEB & BROWSER:
• "open website google.com" - Open websites
• "search google for python tutorials" - Google search
• "search youtube for lo-fi music" - YouTube search
• "play music study beats" - Play music on YouTube

⚠️ SECURITY: All file operations are limited to:
   {workspace}

Say "help" anytime to see this again! 💕""".format(workspace=SecurityManager.WORKSPACE if CAPABILITIES_OK else "~/AnimeBuddyWorkspace")
        return help_text

    # ── LLM API ────────────────────────────────────────────────────────────────
    def _ask_llm(self, user_message):
        """Call OpenAI API for responses. Returns response text or None on failure."""
        if not LLM_OK:
            return "My AI brain is sleeping... 💤"
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a cute anime desktop assistant. Respond briefly (1-2 sentences max), use emojis, and be friendly and playful."},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            resp = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Hmm, my brain glitched... 🤖💭 ({str(e)[:50]})"

    def _parse_intent_with_llm(self, user_message):
        """Use LLM to understand user intent and return structured action."""
        if not LLM_OK:
            return None
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            system_prompt = """You are an intent parser for a desktop assistant. Analyze the user's message and return a JSON object with:
- "intent": one of [open_app, screenshot, type_text, dance, wave, greeting, idle, walk, hide_chat, volume_up, volume_down, volume_mute, chat, unknown]
- "app_name": (for open_app) the app name like "chrome", "notepad", "spotify", etc. or null
- "text": (for type_text) the text to type, or null
- "response": a cute anime-style response (1 sentence, with emojis)

Available apps: chrome, notepad, calculator, paint, file explorer, edge, word, excel, powerpoint, vscode, spotify, discord, task manager, cmd, settings, photos.

Return ONLY valid JSON, no markdown formatting."""
            data = {
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 150,
                "temperature": 0.3
            }
            resp = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=10)
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"].strip()
            # Parse JSON response
            import json
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)
            return parsed
        except Exception:
            return None

    # ── Bubble ────────────────────────────────────────────────────────────────
    def _show_bubble(self, text):
        if self._bubble_win:
            try: self._bubble_win.destroy()
            except: pass
        bx = self.win_x - 240 if self.win_x > 300 else self.win_x + self.W + 10
        by = self.win_y + 10
        self._bubble_win = BubbleWindow(self.root, text, bx, by)
        self._bubble_win.close_after(3500)
        # Ensure bubble stays on top
        self._bubble_win.lift()
        self._bubble_win.attributes("-topmost", True)

    # ── Random phrases ───────────────────────────────────────────────────────
    def _schedule_random_phrase(self):
        delay = random.randint(15000, 40000)
        self.root.after(delay, self._random_phrase)

    def _random_phrase(self):
        # Use personality-based phrases
        idle_phrases = self.personality.traits.get("idle_phrases", ["..."])
        phrase = random.choice(idle_phrases)
        
        # Add memory-based personalized messages occasionally
        if self.memory.interaction_count > 10 and random.random() < 0.3:
            bond_phrases = [
                f"We've talked {self.memory.interaction_count} times now! �",
                "I really enjoy our chats~ 🌸",
                "You're my favorite person to talk to! ✨",
            ]
            phrase = random.choice(bond_phrases)
        
        formatted = self.personality.format_speech(phrase)
        self._show_bubble(formatted)
        self._schedule_random_phrase()

    def _apply_custom_colors(self):
        """Apply user customization to character colors."""
        colors = self.config.COLORS
        self.char.SKIN = colors.get("skin", self.char.SKIN)
        self.char.HAIR = colors.get("hair_primary", self.char.HAIR)
        self.char.HAIR2 = colors.get("hair_highlight", self.char.HAIR2)
        self.char.EYE_C = colors.get("eye_color", self.char.EYE_C)
        self.char.SHIRT = colors.get("shirt", self.char.SHIRT)
        self.char.SKIRT = colors.get("skirt", self.char.SKIRT)
        self.char.RIBBON = colors.get("ribbon", self.char.RIBBON)
        self.char.BLUSH = colors.get("blush", self.char.BLUSH)
    
    def _trigger_human_behavior(self):
        """Trigger a human-like idle behavior."""
        if self.mode != "walk":
            return
        
        behavior_name = HumanBehaviors.get_random_behavior(
            self.personality.type, 
            self.config.ENERGY_LEVEL
        )
        behavior = HumanBehaviors.BEHAVIORS.get(behavior_name)
        
        if behavior:
            self._current_behavior = behavior_name
            phrase = behavior.get("phrase", "")
            
            # Show personality-formatted phrase
            if phrase:
                formatted = self.personality.format_speech(phrase)
                self._show_bubble(formatted)
            
            # Reset behavior after duration
            duration = behavior.get("duration", 2000)
            self.root.after(duration, self._end_human_behavior)
        
        # Set next behavior timer
        talk_freq = {"quiet": 600, "normal": 400, "chatty": 200}
        base_timer = talk_freq.get(self.config.TALK_FREQUENCY, 400)
        self._human_behavior_timer = random.randint(base_timer - 100, base_timer + 100)
    
    def _end_human_behavior(self):
        """End current human behavior."""
        self._current_behavior = None

    def _pick_new_target(self):
        """Pick a random position on screen to walk to."""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        margin = 50
        self._target_x = random.randint(margin, sw - self.W - margin)
        self._target_y = random.randint(margin, sh - self.H - margin)
        self._idle_timer = random.randint(60, 180)  # idle for 2-6 seconds at target

    # ── Animation tick ────────────────────────────────────────────────────────
    def _tick(self):
        self.walk_phase += 0.15

        # Blink logic
        self._blink_countdown -= 1
        if self._blink_countdown <= 0:
            self.char.blink_open = not self.char.blink_open
            if not self.char.blink_open:
                self._blink_countdown = 4   # keep closed briefly
            else:
                self._blink_countdown = random.randint(80, 200)

        # Movement - free roaming anywhere on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        if self.mode == "walk":
            speed = 2.5
            dx = self._target_x - self.win_x
            dy = self._target_y - self.win_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > speed:
                # Move toward target
                self.win_x += (dx / dist) * speed
                self.win_y += (dy / dist) * speed
                # Set direction based on x movement
                self.dir = 1 if dx > 0 else -1
                self.char_screen_x = self.win_x + self.W // 2
            else:
                # Reached target - idle for a bit then pick new target
                self._idle_timer -= 1
                
                # Human behavior system - perform idle actions
                self._human_behavior_timer -= 1
                if self._human_behavior_timer <= 0 and not self._current_behavior:
                    self._trigger_human_behavior()
                
                if self._idle_timer <= 0:
                    self._pick_new_target()
            
            # Keep in bounds (safety)
            self.win_x = max(0, min(sw - self.W, self.win_x))
            self.win_y = max(0, min(sh - self.H, self.win_y))
            self.root.geometry(f"{self.W}x{self.H}+{int(self.win_x)}+{int(self.win_y)}")

        elif self.mode == "dance":
            self.win_x += math.sin(self.walk_phase * 2) * 3
            self.root.geometry(f"{self.W}x{self.H}+{int(self.win_x)}+{int(self.win_y)}")

        elif self.mode == "jump":
            jump_y = self.win_y + int(math.sin(self.walk_phase * 3) * -12)
            self.root.geometry(f"{self.W}x{self.H}+{int(self.win_x)}+{int(jump_y)}")

        # Flip canvas for direction
        if self.dir == 1:
            self.canvas.configure(width=self.W)
        else:
            self.canvas.configure(width=self.W)

        # Determine walk phase for drawing
        if self.mode in ("idle", "talking"):
            if self._current_behavior:
                # Human behavior animations
                behavior_anim = HumanBehaviors.BEHAVIORS.get(self._current_behavior, {}).get("animation", "sway")
                if behavior_anim in ["reach_up", "mouth_open"]:
                    draw_phase = math.sin(self.walk_phase * 0.5) * 0.5  # Stretch
                elif behavior_anim in ["shuffle", "toss_hair"]:
                    draw_phase = math.sin(self.walk_phase * 0.8) * 0.3  # Fidget
                else:
                    draw_phase = math.sin(self.walk_phase * 0.3) * 0.2   # subtle sway
            else:
                draw_phase = math.sin(self.walk_phase * 0.3) * 0.2   # subtle sway
        elif self.mode == "dance":
            draw_phase = self.walk_phase
        elif self.mode == "wave":
            draw_phase = 0
        else:
            draw_phase = self.walk_phase

        self.char.x = self.W // 2
        # Flip direction by mirroring canvas
        if self.dir == -1:
            self.canvas.xview_moveto(0)

        self.char.draw(walk_phase=draw_phase,
                       expression=self.expression,
                       blink=self.char.blink_open)

        # Wave arm override
        if self.mode == "wave":
            arm_ang = -40 + math.sin(self.walk_phase * 0.4) * 50
            # redraw arm in waving position
            cx = self.char.x
            base_y = self.char.y
            arm_top_y = base_y - 80 + abs(math.sin(self.walk_phase * 0.3)) * 3
            ax = cx + 16
            rad = math.radians(arm_ang - 80)
            ex = ax + math.sin(rad) * 28
            ey = arm_top_y + 10 + math.cos(rad) * -4
            wid = self.canvas.create_line(ax, arm_top_y, ex, ey,
                                          width=8, fill=AnimeCharacter.SHIRT,
                                          capstyle=tk.ROUND)
            hand = self.canvas.create_oval(ex-6, ey-6, ex+6, ey+6,
                                           fill=AnimeCharacter.SKIN,
                                           outline=AnimeCharacter.SKIN)
            self.char.ids += [wid, hand]

        self.root.after(1000 // self.FPS, self._tick)

    # ── Mouse interactions ────────────────────────────────────────────────────
    def _left_click(self, event):
        # Use personality-appropriate poke response
        poke_phrases = {
            "cheerful": ["Eek! 😆", "Hey there! 💕", "That tickles! ✨", "Hi hi! 🌸"],
            "tsundere": ["H-hey! Don't touch! 💢", "W-what do you think you're doing?! 😳", "B-baka! 💦", "Hmph! 💢"],
            "shy": ["Eek! 🫣", "*hides* ...h-hi 🥺", "S-sorry... �", "*blush* 💔"],
            "genki": ["WHOA!!! ⚡", "THAT SURPRISED ME!!! 🎉", "YAY POKE!!! 💥", "HELLO!!! 🌟"],
            "mysterious": ["*appears* You summoned me? �", "The touch of fate... 🌙", "*intrigued* 👁️", "We are connected... ✨"],
            "royal": ["How dare you! 👑", "Unhand me, subject! 💢", "*adjusts crown* Hmph. 🎭", "I shall allow it... this time. 🌹"],
            "yandere": ["You touched me... 💕", "I like when you touch me... 🔪", "Only you can do that... 💋", "More... please... �"],
        }
        phrases = poke_phrases.get(self.personality.type, poke_phrases["cheerful"])
        phrase = random.choice(phrases)
        self._show_bubble(self.personality.format_speech(phrase))
        self.expression = "surprised"
        self.root.after(1500, lambda: setattr(self, "expression", "happy"))
        self._drag_start = (event.x_root - self.win_x, event.y_root - self.win_y)
        self._is_dragging = False

    def _drag(self, event):
        if self._drag_start:
            self._is_dragging = True
            self.win_x = event.x_root - self._drag_start[0]
            self.win_y = event.y_root - self._drag_start[1]
            self.root.geometry(f"{self.W}x{self.H}+{int(self.win_x)}+{int(self.win_y)}")

    def _drag_end(self, event):
        if not self._is_dragging:
            # Just clicked without dragging - use confused phrases
            phrase = self.personality.get_phrase("confused")
            self._show_bubble(phrase)
            self.expression = "surprised"
            self.root.after(1500, lambda: setattr(self, "expression", "happy"))
            if WINSOUND_OK:
                threading.Thread(target=lambda: winsound.MessageBeep(winsound.MB_OK),
                                 daemon=True).start()
        self._drag_start = None
        self._is_dragging = False

    def _right_click(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="👋 Bring to Front", command=self._bring_to_front)
        menu.add_command(label="Show Chat Panel", command=self._show_chat)
        menu.add_separator()
        menu.add_command(label="Walk",       command=lambda: self._set_mode("walk"))
        menu.add_command(label="Dance",      command=lambda: self._do_action(("dance",)))
        menu.add_command(label="Wave",       command=lambda: self._do_action(("wave",)))
        menu.add_command(label="Idle / Rest",command=lambda: self._do_action(("idle",)))
        menu.add_separator()
        menu.add_command(label="Take Screenshot",
                         command=lambda: self._do_action(("screenshot",)))
        
        # Settings option - always available
        menu.add_separator()
        menu.add_command(label="⚙️ Settings...", command=self._open_settings)
        
        menu.add_separator()
        menu.add_command(label="Quit", command=self._quit)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _bring_to_front(self):
        """Force window to front and make it visible."""
        self.root.attributes("-topmost", False)
        self.root.attributes("-topmost", True)
        self.root.deiconify()
        self.root.lift()
        # Also show chat window
        if hasattr(self, 'chat_win'):
            self.chat_win.deiconify()
            self.chat_win.lift()
        self._show_bubble("Here I am! ✨")
    
    def _show_chat(self):
        """Show chat panel and bring it to front."""
        self.chat_win.deiconify()
        self.chat_win.lift()
        self.chat_win.attributes("-topmost", True)
    
    def _quit(self):
        try:
            self.chat_win.destroy()
        except Exception:
            pass
        self.root.quit()
        self.root.destroy()
    
    def _load_config_from_file(self):
        """Load configuration from anime_buddy_config.json if it exists."""
        try:
            import json
            import os
            config_path = os.path.join(os.path.dirname(__file__), "anime_buddy_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # Apply buddy settings
                buddy = config.get("buddy", {})
                BuddyConfig.NAME = buddy.get("name", BuddyConfig.NAME)
                BuddyConfig.TITLE = buddy.get("title", BuddyConfig.TITLE)
                BuddyConfig.PERSONALITY = buddy.get("personality", BuddyConfig.PERSONALITY)
                BuddyConfig.SPEECH_STYLE = buddy.get("speech_style", BuddyConfig.SPEECH_STYLE)
                BuddyConfig.TALK_FREQUENCY = buddy.get("talk_frequency", BuddyConfig.TALK_FREQUENCY)
                BuddyConfig.ENERGY_LEVEL = buddy.get("energy_level", BuddyConfig.ENERGY_LEVEL)
                
                # Apply behavior settings
                behavior = config.get("behavior", {})
                BuddyConfig.WALK_SPEED = behavior.get("walk_speed", BuddyConfig.WALK_SPEED)
                BuddyConfig.USE_EMOJIS = behavior.get("use_emojis", BuddyConfig.USE_EMOJIS)
                
                # Apply colors
                colors = config.get("appearance", {})
                BuddyConfig.COLORS.update(colors)
                
                # Apply LLM settings
                llm = config.get("llm", {})
                global OPENAI_API_KEY, OPENAI_API_URL, OPENAI_MODEL, LLM_OK
                OPENAI_API_KEY = llm.get("api_key", OPENAI_API_KEY)
                OPENAI_API_URL = llm.get("api_url", OPENAI_API_URL)
                OPENAI_MODEL = llm.get("model", OPENAI_MODEL)
                LLM_OK = llm.get("enabled", False) and bool(OPENAI_API_KEY)
                
                print(f"✅ Loaded config for {BuddyConfig.NAME}")
        except Exception as e:
            print(f"⚠️ Could not load config: {e}")
    
    def _apply_saved_config(self):
        """Apply configuration from ConfigManager."""
        if not self._has_config_system:
            return
        
        # Apply buddy settings
        BuddyConfig.NAME = self.config_manager.get("buddy", "name", "Miku")
        BuddyConfig.TITLE = self.config_manager.get("buddy", "title", "Desktop Companion")
        BuddyConfig.PERSONALITY = self.config_manager.get("buddy", "personality", "cheerful")
        BuddyConfig.SPEECH_STYLE = self.config_manager.get("buddy", "speech_style", "casual")
        BuddyConfig.TALK_FREQUENCY = self.config_manager.get("buddy", "talk_frequency", "normal")
        BuddyConfig.ENERGY_LEVEL = self.config_manager.get("buddy", "energy_level", "normal")
        
        # Apply behavior settings
        BuddyConfig.WALK_SPEED = self.config_manager.get("behavior", "walk_speed", 2.5)
        BuddyConfig.USE_EMOJIS = self.config_manager.get("behavior", "use_emojis", True)
        
        # Apply colors
        colors = self.config_manager.get("appearance", default={})
        BuddyConfig.COLORS.update(colors)
        
        # Apply LLM settings globally
        global OPENAI_API_KEY, OPENAI_API_URL, OPENAI_MODEL, LLM_OK
        llm_config = self.config_manager.get("llm", default={})
        OPENAI_API_KEY = llm_config.get("api_key", "")
        OPENAI_API_URL = llm_config.get("api_url", "https://api.openai.com/v1/chat/completions")
        OPENAI_MODEL = llm_config.get("model", "gpt-3.5-turbo")
        LLM_OK = llm_config.get("enabled", False) and bool(OPENAI_API_KEY)
    
    def _open_settings(self):
        """Open the settings window."""
        if self._has_config_system:
            SettingsWindow(self.root, self.config_manager, on_apply=self._apply_saved_config)
        else:
            # Show capabilities settings
            self._show_capabilities_settings()
    
    def _show_capabilities_settings(self):
        """Show settings window for capabilities and security."""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("⚙️ Anime Buddy Settings")
        settings_win.geometry("500x600")
        settings_win.configure(bg="#1A0A40")
        settings_win.resizable(False, False)
        settings_win.transient(self.root)
        settings_win.grab_set()
        
        # Title
        tk.Label(settings_win, text="⚙️ Buddy Settings & Security", 
                bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        # Create simple tabs using buttons
        tabs_frame = tk.Frame(settings_win, bg="#1A0A40")
        tabs_frame.pack(fill="x", padx=10, pady=5)
        
        content_frame = tk.Frame(settings_win, bg="#1A0A40")
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tab content holders
        identity_tab = tk.Frame(content_frame, bg="#1A0A40")
        security_tab = tk.Frame(content_frame, bg="#1A0A40")
        colors_tab = tk.Frame(content_frame, bg="#1A0A40")
        
        def show_tab(tab_name):
            identity_tab.pack_forget()
            security_tab.pack_forget()
            colors_tab.pack_forget()
            
            if tab_name == "identity":
                identity_tab.pack(fill="both", expand=True)
            elif tab_name == "security":
                security_tab.pack(fill="both", expand=True)
            elif tab_name == "colors":
                colors_tab.pack(fill="both", expand=True)
        
        # Tab buttons
        tk.Button(tabs_frame, text="👤 Identity", bg="#6C3FCF", fg="white",
                 font=("Segoe UI", 10), command=lambda: show_tab("identity")).pack(side="left", padx=2)
        tk.Button(tabs_frame, text="🛡️ Security", bg="#6C3FCF", fg="white",
                 font=("Segoe UI", 10), command=lambda: show_tab("security")).pack(side="left", padx=2)
        tk.Button(tabs_frame, text="🎨 Colors", bg="#6C3FCF", fg="white",
                 font=("Segoe UI", 10), command=lambda: show_tab("colors")).pack(side="left", padx=2)
        
        # ===== Tab 1: Identity =====
        tk.Label(identity_tab, text="Buddy Name:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=(10,0))
        name_var = tk.StringVar(value=BuddyConfig.NAME)
        tk.Entry(identity_tab, textvariable=name_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white",
                insertbackground="white").pack(fill="x", padx=10, pady=5)
        
        tk.Label(identity_tab, text="Personality:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=(15,0))
        personality_var = tk.StringVar(value=BuddyConfig.PERSONALITY)
        personalities = ["cheerful", "tsundere", "shy", "genki", "mysterious", "royal", "yandere"]
        personality_menu = tk.OptionMenu(identity_tab, personality_var, *personalities)
        personality_menu.configure(bg="#2A1050", fg="white", font=("Segoe UI", 10))
        personality_menu.pack(fill="x", padx=10, pady=5)
        
        # ===== Tab 2: Security & Capabilities =====
        
        if CAPABILITIES_OK:
            tk.Label(security_tab, text="Security Level:", bg="#1A0A40", fg="#B090FF",
                    font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=10)
            
            security_var = tk.StringVar(value=SecurityManager.SECURITY_LEVEL)
            for level, desc, color in [
                ("strict", "🔒 Strict - Minimal access", "#00C851"),
                ("moderate", "🔐 Moderate - Safe workspace (Recommended)", "#FFD700"),
                ("unrestricted", "⚠️ Unrestricted - Full system access (Dangerous!)", "#FF6B6B")
            ]:
                frame = tk.Frame(security_tab, bg="#1A0A40")
                frame.pack(fill="x", padx=10, pady=3)
                tk.Radiobutton(frame, text=desc, variable=security_var,
                              value=level, bg="#1A0A40", fg="white",
                              selectcolor=color, font=("Segoe UI", 10)).pack(anchor="w")
            
            # Current permissions display
            tk.Label(security_tab, text="Current Permissions:", bg="#1A0A40", fg="#B090FF",
                    font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            
            perms_frame = tk.Frame(security_tab, bg="#2A1050")
            perms_frame.pack(fill="x", padx=10, pady=5)
            
            perms = SecurityManager.PERMISSIONS.get(security_var.get(), {})
            for action, allowed in perms.items():
                status = "✅" if allowed else "❌"
                tk.Label(perms_frame, text=f"{status} {action.replace('_', ' ').title()}",
                        bg="#2A1050", fg="white" if allowed else "#888888",
                        font=("Segoe UI", 9)).pack(anchor="w", padx=5, pady=1)
            
            # Safe workspace info
            tk.Label(security_tab, text=f"📁 Safe Workspace:\n{SecurityManager.WORKSPACE}",
                    bg="#1A0A40", fg="#B090FF", font=("Segoe UI", 10),
                    wraplength=450, justify="left").pack(anchor="w", padx=10, pady=15)
            
            # Open workspace button
            tk.Button(security_tab, text="📂 Open Workspace Folder", bg="#6C3FCF", fg="white",
                     font=("Segoe UI", 10), command=lambda: os.startfile(SecurityManager.WORKSPACE)).pack(pady=5)
        else:
            tk.Label(security_tab, text="⚠️ Capabilities module not loaded", 
                    bg="#1A0A40", fg="#FF6B6B", font=("Segoe UI", 12)).pack(pady=50)
        
        # ===== Tab 3: Colors =====
        # colors_tab already defined above
        
        color_vars = {}
        colors = [
            ("skin", "Skin", BuddyConfig.COLORS["skin"]),
            ("hair_primary", "Hair", BuddyConfig.COLORS["hair_primary"]),
            ("eye_color", "Eyes", BuddyConfig.COLORS["eye_color"]),
            ("shirt", "Outfit", BuddyConfig.COLORS["shirt"]),
            ("ribbon", "Ribbon", BuddyConfig.COLORS["ribbon"]),
        ]
        
        for key, label, default in colors:
            frame = tk.Frame(colors_tab, bg="#1A0A40")
            frame.pack(fill="x", padx=10, pady=3)
            
            tk.Label(frame, text=f"{label}:", bg="#1A0A40", fg="white",
                    font=("Segoe UI", 10), width=10, anchor="w").pack(side="left")
            
            var = tk.StringVar(value=default)
            color_vars[key] = var
            
            entry = tk.Entry(frame, textvariable=var, width=10,
                           font=("Segoe UI", 10), bg="#2A1050", fg="white")
            entry.pack(side="left", padx=5)
            
            preview = tk.Frame(frame, bg=default, width=25, height=20)
            preview.pack(side="left")
            
            tk.Button(frame, text="🎨", bg="#6C3FCF", fg="white",
                     command=lambda v=var, p=preview: self._pick_color(v, p)).pack(side="left", padx=5)
        
        # Show identity tab by default
        show_tab("identity")
        
        # Buttons
        btn_frame = tk.Frame(settings_win, bg="#1A0A40")
        btn_frame.pack(fill="x", padx=10, pady=15)
        
        def save_settings():
            # Apply identity
            BuddyConfig.NAME = name_var.get()
            BuddyConfig.PERSONALITY = personality_var.get()
            
            # Apply security level
            if CAPABILITIES_OK:
                SecurityManager.SECURITY_LEVEL = security_var.get()
            
            # Apply colors
            for key, var in color_vars.items():
                BuddyConfig.COLORS[key] = var.get()
            
            # Refresh buddy
            self.root.title(f"{BuddyConfig.NAME} - {BuddyConfig.TITLE}")
            self._apply_custom_colors()
            self._show_bubble("Settings updated! ✨")
            settings_win.destroy()
        
        tk.Button(btn_frame, text="💾 Save & Apply", bg="#00C851", fg="white",
                 font=("Segoe UI", 11, "bold"), command=save_settings).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", bg="#404040", fg="white",
                 font=("Segoe UI", 11), command=settings_win.destroy).pack(side="right", padx=5)
    
    def _pick_color(self, var, preview):
        """Open color picker."""
        from tkinter import colorchooser
        color = colorchooser.askcolor(color=var.get())[1]
        if color:
            var.set(color)
            preview.configure(bg=color)
    
    def check_first_run(self):
        """Show setup wizard on first run."""
        if self._has_config_system and self.config_manager.get("first_run", default=True):
            # Hide windows temporarily
            self.root.withdraw()
            self.chat_win.withdraw()
            
            def on_wizard_complete():
                self._apply_saved_config()
                self.root.deiconify()
                self.chat_win.deiconify()
                # Re-apply colors since character is already created
                self._apply_custom_colors()
            
            SetupWizard(self.root, self.config_manager, on_complete=on_wizard_complete)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if sys.platform != "win32":
        print("⚠  This buddy is optimized for Windows. It may still work on other platforms!")
    AnimeBuddy()
