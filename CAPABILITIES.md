# 🤖 Anime Buddy - Full System Capabilities

## Overview

Your anime buddy now has **full system access** with security controls! She can manage files, control system settings, browse the web, and more - all safely contained.

---

## 🛡️ Security Architecture

### Permission Levels

| Level | File Access | System Control | Network | Commands |
|-------|-------------|----------------|---------|----------|
| **Strict** | ❌ None | ❌ None | ✅ Browser only | ❌ None |
| **Moderate** (Default) | ✅ Read/Write (Safe folders) | ✅ With limits | ✅ Full | ❌ None |
| **Unrestricted** | ✅ Full access | ✅ Full | ✅ Full | ✅ Shell commands |

**To change security level**, edit `buddy_capabilities.py`:
```python
SECURITY_LEVEL = "moderate"  # Options: "strict", "moderate", "unrestricted"
```

### Safe Zone

All file operations are restricted to:
- `~/Documents`
- `~/Desktop`
- `~/Downloads`
- `~/AnimeBuddyWorkspace` (created automatically)

This prevents accidental deletion of system files!

---

## 📁 File Operations

### List Files
```
"list files"
"show files in folder Documents"
```
Shows files and folders with icons.

### Search Files
```
"search file *.txt"
"find file report.pdf"
"look for *.py files"
```
Searches recursively for matching files.

### Read Files
```
"read file notes.txt"
"show file content todo.txt"
"open file readme.md"
```
Reads text files (limited to 100KB for safety).

### Create Files
```
"create file notes.txt with content hello world"
"write file data.json with content {"key": "value"}"
```
Creates new text files in the workspace.

### Create Folders
```
"create folder myproject"
"make folder work"
"new folder 2024"
```
Creates folders in the workspace.

### Delete Files
```
"delete file old.txt"
"remove file temp.pdf"
"trash file junk.md"
```
⚠️ **Warning**: Permanently deletes files (no recycle bin)!

---

## 🔧 System Control

### Volume Control
```
"set volume to 50"
"volume at 30"
"change volume to 75"
```
Set system volume (0-100).

**Requires**: `pip install pycaw comtypes`

### System Info
```
"system info"
"computer info"
"pc info"
```
Shows OS version, processor, hostname, etc.

### Empty Recycle Bin
```
"empty trash"
"empty recycle bin"
"clear recycle bin"
```
Empties the Windows recycle bin.

---

## 🌐 Web & Browser

### Open Websites
```
"open website google.com"
"go to website youtube.com"
"visit github.com"
```
Opens URLs in your default browser.

### Google Search
```
"search google for python tutorials"
"google search weather today"
```
Performs Google searches.

### YouTube Search
```
"search youtube for lo-fi music"
"youtube search study beats"
```
Searches YouTube.

### Play Music
```
"play music study beats"
"listen to jazz"
"play song lofi girl"
```
Opens YouTube search for music.

---

## ⚡ Command Execution (Unrestricted Mode Only)

```
"run command calc"
"execute notepad"
"cmd echo hello world"
```

**⚠️ DANGER**: Only enable in `unrestricted` mode. Can execute ANY shell command!

---

## 🆘 Getting Help

```
"what can you do"
"show capabilities"
"list commands"
"help me"
"what are your powers"
```

Shows all available commands and capabilities.

---

## 🔐 Audit Logging

All actions are logged to:
```
~/AnimeBuddyWorkspace/action_log.txt
```

Example log:
```
[2024-05-09 21:30:15] list_directory: C:\Users\You\AnimeBuddyWorkspace
[2024-05-09 21:32:08] read_file: notes.txt
[2024-05-09 21:35:22] search_google: python tutorials
```

---

## 📦 Installation

### Basic Setup
```bash
pip install pyautogui pillow requests
```

### Full System Access
```bash
# For volume control
pip install pycaw comtypes

# For system notifications
pip install win10toast

# For browser automation
pip install selenium webdriver-manager
```

---

## 🎯 Quick Start Commands

Try these to test capabilities:

1. `"list files"` - See workspace contents
2. `"create file hello.txt with content hi from buddy`" - Create a file
3. `"search google for cute cat pictures`" - Web search
4. `"system info`" - Show computer info
5. `"what can you do`" - Show all commands

---

## ⚠️ Safety Tips

1. **Keep Security at "moderate"** for daily use
2. **Use "strict" mode** if children use the bot
3. **Review action logs** periodically
4. **Never enable "unrestricted"** on work/production machines
5. **Files in workspace are safe** - system files are protected

---

## 🔧 Troubleshooting

### "❌ File reading not permitted"
→ Security level is too strict. Change to `moderate`.

### "❌ Access denied: Outside safe zone"
→ File is outside allowed folders. Move file to workspace first.

### "⚠️ Install pycaw" for volume control
→ Run: `pip install pycaw comtypes`

### "🚫 Command blocked for security"
→ Command matched blocked patterns. Modify `BLOCKED_PATTERNS` if needed.

---

## 🚀 Future Enhancements

Planned capabilities:
- 📧 Email sending (with confirmation)
- 📅 Calendar integration
- 🔔 Custom notifications
- 📊 Process monitoring
- 🌡️ System resource monitoring
- 📷 Camera capture (with permission)
- 🎤 Voice commands

---

**Enjoy your super-powered anime buddy!** 💕
Use responsibly and have fun!
