"""
Buddy Capabilities - Full System Access with Security
Provides file management, system control, and browser automation
"""
import os
import shutil
import glob
import subprocess
import ctypes
import webbrowser
import json
from datetime import datetime
from pathlib import Path


class SecurityManager:
    """Manages permissions and security for bot actions."""
    
    # Security levels: strict, moderate, unrestricted
    SECURITY_LEVEL = "moderate"
    
    # Allowed actions per level
    PERMISSIONS = {
        "strict": {
            "open_apps": True,
            "screenshots": True,
            "type_text": True,
            "file_read": False,
            "file_write": False,
            "system_settings": False,
            "browser": True,
            "execute_commands": False,
        },
        "moderate": {
            "open_apps": True,
            "screenshots": True,
            "type_text": True,
            "file_read": True,       # Read-only in safe folders
            "file_write": True,      # Write only in quarantine
            "system_settings": True,  # With confirmation
            "browser": True,
            "execute_commands": False,
        },
        "unrestricted": {
            "open_apps": True,
            "screenshots": True,
            "type_text": True,
            "file_read": True,
            "file_write": True,
            "system_settings": True,
            "browser": True,
            "execute_commands": True,  # Dangerous!
        }
    }
    
    # Dangerous commands to block
    BLOCKED_PATTERNS = [
        "format", "del /f", "rd /s", "rmdir /s",
        "reg delete", "net user", "net localgroup",
        "takeown", "icacls", "attrib -r -s -h",
        "powershell -enc", "wget.*|.*sh", "curl.*|.*bash",
    ]
    
    # Safe folders for file operations
    SAFE_FOLDERS = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/AnimeBuddyWorkspace"),
    ]
    
    # Ensure workspace exists
    WORKSPACE = os.path.expanduser("~/AnimeBuddyWorkspace")
    os.makedirs(WORKSPACE, exist_ok=True)
    
    @classmethod
    def check_permission(cls, action):
        """Check if an action is allowed."""
        return cls.PERMISSIONS.get(cls.SECURITY_LEVEL, {}).get(action, False)
    
    @classmethod
    def is_safe_path(cls, filepath):
        """Check if file path is in safe zone."""
        real_path = os.path.realpath(filepath)
        for safe in cls.SAFE_FOLDERS + [cls.WORKSPACE]:
            if real_path.startswith(os.path.realpath(safe)):
                return True
        return False
    
    @classmethod
    def is_safe_command(cls, command):
        """Check if shell command is safe."""
        cmd_lower = command.lower()
        for pattern in cls.BLOCKED_PATTERNS:
            if pattern.lower() in cmd_lower:
                return False
        return True
    
    @classmethod
    def log_action(cls, action, details=""):
        """Log all actions for audit."""
        log_file = os.path.join(cls.WORKSPACE, "action_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {action}: {details}\n")


class FileManager:
    """File system operations with security."""
    
    def __init__(self):
        self.workspace = SecurityManager.WORKSPACE
    
    def list_directory(self, path=None):
        """List files in directory."""
        if path is None:
            path = self.workspace
        
        if not SecurityManager.check_permission("file_read"):
            return "❌ File reading not permitted"
        
        if not SecurityManager.is_safe_path(path):
            return "❌ Access denied: Outside safe zone"
        
        try:
            items = os.listdir(path)
            files = []
            folders = []
            for item in items:
                full = os.path.join(path, item)
                if os.path.isdir(full):
                    folders.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(full)
                    files.append(f"📄 {item} ({size} bytes)")
            
            SecurityManager.log_action("list_directory", path)
            return "\n".join(folders + files) if items else "Empty folder"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def search_files(self, pattern, location=None):
        """Search for files matching pattern."""
        if not SecurityManager.check_permission("file_read"):
            return "❌ File reading not permitted"
        
        if location is None:
            location = self.workspace
        
        if not SecurityManager.is_safe_path(location):
            return "❌ Access denied: Outside safe zone"
        
        try:
            results = glob.glob(os.path.join(location, "**", pattern), recursive=True)
            SecurityManager.log_action("search_files", f"{pattern} in {location}")
            return f"Found {len(results)} files:\n" + "\n".join(results[:20])  # Limit output
        except Exception as e:
            return f"❌ Error: {e}"
    
    def read_file(self, filepath):
        """Read text file contents."""
        if not SecurityManager.check_permission("file_read"):
            return "❌ File reading not permitted"
        
        if not SecurityManager.is_safe_path(filepath):
            return "❌ Access denied: Outside safe zone"
        
        try:
            # Only read text files, limited size
            if not filepath.endswith(('.txt', '.md', '.py', '.json', '.log', '.csv')):
                return "❌ Only text files allowed"
            
            size = os.path.getsize(filepath)
            if size > 100000:  # 100KB limit
                return "❌ File too large (>100KB)"
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            SecurityManager.log_action("read_file", filepath)
            return content[:2000] + ("..." if len(content) > 2000 else "")
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    def write_file(self, filepath, content):
        """Write content to file."""
        if not SecurityManager.check_permission("file_write"):
            return "❌ File writing not permitted"
        
        # Force into workspace
        safe_path = os.path.join(self.workspace, os.path.basename(filepath))
        
        try:
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            SecurityManager.log_action("write_file", safe_path)
            return f"✅ Saved to {safe_path}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def create_folder(self, foldername):
        """Create a new folder."""
        if not SecurityManager.check_permission("file_write"):
            return "❌ File writing not permitted"
        
        path = os.path.join(self.workspace, foldername)
        try:
            os.makedirs(path, exist_ok=True)
            SecurityManager.log_action("create_folder", path)
            return f"✅ Created folder: {foldername}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def delete_file(self, filepath):
        """Delete a file or folder."""
        if not SecurityManager.check_permission("file_write"):
            return "❌ File deletion not permitted"
        
        # Must be in workspace
        safe_path = os.path.join(self.workspace, os.path.basename(filepath))
        
        if not os.path.exists(safe_path):
            return "❌ File not found"
        
        try:
            if os.path.isdir(safe_path):
                shutil.rmtree(safe_path)
            else:
                os.remove(safe_path)
            
            SecurityManager.log_action("delete_file", safe_path)
            return f"🗑️ Deleted: {os.path.basename(filepath)}"
        except Exception as e:
            return f"❌ Error: {e}"


class SystemController:
    """System-level controls."""
    
    def set_volume(self, level):
        """Set system volume (0-100)."""
        if not SecurityManager.check_permission("system_settings"):
            return "❌ System control not permitted"
        
        try:
            # Windows volume via nircmd (if available) or alternative
            # Using Windows Core Audio API via comtypes
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            
            SecurityManager.log_action("set_volume", str(level))
            return f"🔊 Volume set to {level}%"
        except ImportError:
            return "⚠️ Install pycaw: pip install pycaw"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def set_wallpaper(self, image_path):
        """Change desktop wallpaper."""
        if not SecurityManager.check_permission("system_settings"):
            return "❌ System control not permitted"
        
        try:
            if not os.path.exists(image_path):
                return "❌ Image not found"
            
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            SecurityManager.log_action("set_wallpaper", image_path)
            return "🖼️ Wallpaper changed!"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def system_info(self):
        """Get system information."""
        import platform
        info = {
            "OS": platform.system(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Hostname": platform.node(),
        }
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    
    def shutdown(self, delay=60):
        """Shutdown computer (requires confirmation)."""
        if not SecurityManager.check_permission("system_settings"):
            return "❌ System control not permitted"
        
        # This is dangerous - require manual confirmation
        return f"⚠️ Shutdown requires manual confirmation in Settings"
    
    def empty_recycle_bin(self):
        """Empty recycle bin."""
        if not SecurityManager.check_permission("system_settings"):
            return "❌ System control not permitted"
        
        try:
            # SHEmptyRecycleBinW
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
            return "🗑️ Recycle bin emptied!"
        except Exception as e:
            return f"❌ Error: {e}"


class BrowserController:
    """Browser and web control."""
    
    def open_url(self, url):
        """Open URL in default browser."""
        if not SecurityManager.check_permission("browser"):
            return "❌ Browser control not permitted"
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            SecurityManager.log_action("open_url", url)
            return f"🌐 Opening {url}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def search_google(self, query):
        """Search Google."""
        if not SecurityManager.check_permission("browser"):
            return "❌ Browser control not permitted"
        
        import urllib.parse
        encoded = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        SecurityManager.log_action("search_google", query)
        return f"🔍 Searching Google for: {query}"
    
    def search_youtube(self, query):
        """Search YouTube."""
        if not SecurityManager.check_permission("browser"):
            return "❌ Browser control not permitted"
        
        import urllib.parse
        encoded = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        SecurityManager.log_action("search_youtube", query)
        return f"📺 Searching YouTube for: {query}"
    
    def play_music(self, query):
        """Search and play music on YouTube."""
        if not SecurityManager.check_permission("browser"):
            return "❌ Browser control not permitted"
        
        import urllib.parse
        encoded = urllib.parse.quote(query + " music")
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"🎵 Looking for: {query}"


class CommandExecutor:
    """Execute shell commands safely."""
    
    SAFE_COMMANDS = [
        "echo", "dir", "cd", "cls", "date", "time",
        "calc", "notepad", "mspaint", "explorer",
        "start", "chrome", "firefox", "edge",
    ]
    
    def execute(self, command):
        """Execute a command safely."""
        if not SecurityManager.check_permission("execute_commands"):
            return "❌ Command execution not permitted"
        
        if not SecurityManager.is_safe_command(command):
            SecurityManager.log_action("BLOCKED_COMMAND", command)
            return "🚫 Command blocked for security"
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            SecurityManager.log_action("execute_command", command)
            return result.stdout or result.stderr or "✅ Command executed"
        except subprocess.TimeoutExpired:
            return "⏱️ Command timed out"
        except Exception as e:
            return f"❌ Error: {e}"


# Create singleton instances
file_manager = FileManager()
system_controller = SystemController()
browser_controller = BrowserController()
command_executor = CommandExecutor()
