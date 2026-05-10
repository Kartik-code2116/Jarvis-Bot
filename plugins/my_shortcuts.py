# ─────────────────────────────────────────────────────────────────────────────
# JARVIS Plugin: Custom Shortcuts
# ─────────────────────────────────────────────────────────────────────────────
# Add your own commands here!
# Trigger words go in COMMANDS list (lowercase).
# The handle() function receives the full command string and returns a response.
#
# To activate: save any .py file in the /plugins/ folder — JARVIS auto-loads it.
# ─────────────────────────────────────────────────────────────────────────────

import os
import webbrowser
import subprocess

COMMANDS = [
    "my project",
    "open project",
    "open jarvis folder",
    "open downloads",
    "dev mode",
    "github",
]

def handle(cmd: str) -> str:
    c = cmd.lower()

    if "project" in c or "jarvis folder" in c:
        path = r"D:\9)projects\Jarvis Bot"
        if os.path.exists(path):
            subprocess.Popen(f'explorer "{path}"', shell=True)
            return f"Opening project folder: {path}"
        return "Project folder not found."

    elif "downloads" in c:
        path = os.path.join(os.path.expanduser("~"), "Downloads")
        subprocess.Popen(f'explorer "{path}"', shell=True)
        return f"Opening Downloads."

    elif "github" in c:
        webbrowser.open("https://github.com")
        return "Opening GitHub."

    elif "dev mode" in c:
        # Open VS Code in project folder
        path = r"D:\9)projects\Jarvis Bot"
        subprocess.Popen(f'code "{path}"', shell=True)
        return "Opening project in VS Code."

    return "Custom plugin triggered."
