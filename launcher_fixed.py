"""
Anime Buddy Launcher - Control Panel
Manages settings and launches the buddy
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import json
import subprocess
import sys
import os


class BuddyLauncher:
    """Control panel for managing the anime buddy."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Anime Buddy Control Panel")
        self.root.geometry("850x650+50+50")
        self.root.configure(bg="#1A0A40")
        self.root.minsize(800, 600)
        
        self.buddy_process = None
        
        self._build_ui()
        self._load_settings()
        
    def _build_ui(self):
        """Build the UI."""
        # Header
        header = tk.Frame(self.root, bg="#2A1050", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🤖 Anime Buddy Control Panel", 
                bg="#2A1050", fg="#B090FF",
                font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="● Buddy: Stopped")
        self.status_label = tk.Label(header, textvariable=self.status_var,
                                     bg="#2A1050", fg="#FF6B6B",
                                     font=("Segoe UI", 12))
        self.status_label.pack(side="right", padx=20)
        
        # Main content
        main = tk.Frame(self.root, bg="#1A0A40")
        main.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Left: Launch Controls
        left = tk.Frame(main, bg="#2A1050", width=250)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        
        tk.Label(left, text="🚀 Launch", bg="#2A1050", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        tk.Button(left, text="▶ Start Buddy", bg="#00C851", fg="white",
                 font=("Segoe UI", 12, "bold"), command=self._start_buddy,
                 width=20).pack(pady=5)
        
        tk.Button(left, text="⏹ Stop Buddy", bg="#FF6B6B", fg="white",
                 font=("Segoe UI", 12), command=self._stop_buddy,
                 width=20).pack(pady=5)
        
        tk.Button(left, text="🔄 Restart Buddy", bg="#FFD700", fg="black",
                 font=("Segoe UI", 12), command=self._restart_buddy,
                 width=20).pack(pady=5)
        
        tk.Frame(left, bg="#1A0A40", height=2).pack(fill="x", pady=15)
        
        tk.Label(left, text="⚡ Quick Edit", bg="#2A1050", fg="#B090FF",
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Quick name edit
        tk.Label(left, text="Name:", bg="#2A1050", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", padx=10)
        self.name_var = tk.StringVar(value="Miku")
        tk.Entry(left, textvariable=self.name_var,
                font=("Segoe UI", 11), bg="#1A0A40", fg="white",
                insertbackground="white").pack(fill="x", padx=10, pady=5)
        
        # Quick personality edit
        tk.Label(left, text="Personality:", bg="#2A1050", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=(10,0))
        self.personality_var = tk.StringVar(value="cheerful")
        ttk.Combobox(left, textvariable=self.personality_var,
                    values=["cheerful", "tsundere", "shy", "genki", "mysterious", "royal", "yandere"],
                    state="readonly").pack(fill="x", padx=10, pady=5)
        
        tk.Button(left, text="💾 Save & Apply", bg="#6C3FCF", fg="white",
                 font=("Segoe UI", 11), command=self._quick_save).pack(pady=10)
        
        # Right: Full Settings Tabs
        right = tk.Frame(main, bg="#1A0A40")
        right.pack(side="right", fill="both", expand=True)
        
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self._create_appearance_tab()
        self._create_behavior_tab()
        self._create_ai_tab()
        self._create_profiles_tab()
        
        # Bottom
        bottom = tk.Frame(self.root, bg="#2A1050", height=50)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)
        
        tk.Button(bottom, text="💾 Save All Settings", bg="#00C851", fg="white",
                 font=("Segoe UI", 11, "bold"), command=self._save_settings).pack(side="left", padx=15, pady=8)
        
        tk.Button(bottom, text="📤 Export Config", bg="#8B5FEF", fg="white",
                 font=("Segoe UI", 10), command=self._export_config).pack(side="left", padx=5, pady=8)
        
        tk.Button(bottom, text="📥 Import Config", bg="#8B5FEF", fg="white",
                 font=("Segoe UI", 10), command=self._import_config).pack(side="left", padx=5, pady=8)
        
        tk.Button(bottom, text="❌ Exit", bg="#FF6B6B", fg="white",
                 font=("Segoe UI", 11), command=self._exit).pack(side="right", padx=15, pady=8)
        
    def _create_appearance_tab(self):
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🎨 Appearance")
        
        tk.Label(tab, text="Color Customization", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        self.color_vars = {}
        colors = [
            ("skin", "Skin", "#FFD5B8"),
            ("hair_primary", "Hair", "#3A1F6E"),
            ("hair_highlight", "Hair Shine", "#5B2FC0"),
            ("eye_color", "Eyes", "#6040E0"),
            ("shirt", "Top", "#6C8EEF"),
            ("skirt", "Bottom", "#3A54C0"),
            ("ribbon", "Ribbon", "#EF6CAA"),
            ("blush", "Blush", "#FFB3B3"),
        ]
        
        for key, label, default in colors:
            frame = tk.Frame(tab, bg="#1A0A40")
            frame.pack(fill="x", pady=3)
            
            tk.Label(frame, text=f"{label}:", bg="#1A0A40", fg="white",
                    font=("Segoe UI", 10), width=10, anchor="w").pack(side="left")
            
            var = tk.StringVar(value=default)
            self.color_vars[key] = var
            
            tk.Entry(frame, textvariable=var, width=10,
                    font=("Segoe UI", 10), bg="#2A1050", fg="white").pack(side="left", padx=5)
            
            preview = tk.Frame(frame, bg=default, width=25, height=20)
            preview.pack(side="left")
            
            tk.Button(frame, text="🎨", bg="#6C3FCF", fg="white",
                     command=lambda v=var, p=preview: self._pick_color(v, p)).pack(side="left", padx=5)
        
        # Themes
        tk.Label(tab, text="Quick Themes:", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20, 5))
        
        themes_frame = tk.Frame(tab, bg="#1A0A40")
        themes_frame.pack(fill="x")
        
        themes = [
            ("Classic", {"hair_primary": "#3A1F6E", "eye_color": "#6040E0"}),
            ("Pink", {"hair_primary": "#FF6B9D", "eye_color": "#FF1493"}),
            ("Red", {"hair_primary": "#DC143C", "eye_color": "#B22222"}),
            ("Blonde", {"hair_primary": "#FFD700", "eye_color": "#32CD32"}),
            ("Silver", {"hair_primary": "#C0C0C0", "eye_color": "#4682B4"}),
            ("Teal", {"hair_primary": "#20B2AA", "eye_color": "#00CED1"}),
        ]
        
        for name, colors in themes:
            tk.Button(themes_frame, text=name, bg="#6C3FCF", fg="white",
                     command=lambda c=colors: self._apply_theme(c)).pack(side="left", padx=3)
    
    def _create_behavior_tab(self):
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🚶 Behavior")
        
        tk.Label(tab, text="Behavior Settings", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        tk.Label(tab, text="Walk Speed:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        self.speed_var = tk.DoubleVar(value=2.5)
        tk.Scale(tab, from_=1.0, to=5.0, resolution=0.5, orient="horizontal",
                variable=self.speed_var, bg="#1A0A40", fg="white",
                highlightthickness=0, length=300).pack(anchor="w", pady=5)
        
        tk.Label(tab, text="Energy Level:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 0))
        self.energy_var = tk.StringVar(value="normal")
        for value, label in [("low", "Low"), ("normal", "Normal"), ("hyper", "Hyper")]:
            tk.Radiobutton(tab, text=label, variable=self.energy_var,
                          value=value, bg="#1A0A40", fg="white",
                          selectcolor="#6C3FCF", font=("Segoe UI", 10)).pack(anchor="w")
        
        tk.Label(tab, text="Talk Frequency:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 0))
        self.talk_freq_var = tk.StringVar(value="normal")
        for value, label in [("quiet", "Quiet"), ("normal", "Normal"), ("chatty", "Chatty")]:
            tk.Radiobutton(tab, text=label, variable=self.talk_freq_var,
                          value=value, bg="#1A0A40", fg="white",
                          selectcolor="#6C3FCF", font=("Segoe UI", 10)).pack(anchor="w")
        
        self.emojis_var = tk.BooleanVar(value=True)
        tk.Checkbutton(tab, text="Use Emojis", variable=self.emojis_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 11)).pack(anchor="w", pady=10)
    
    def _create_ai_tab(self):
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🤖 AI")
        
        tk.Label(tab, text="AI Settings (Optional)", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        self.llm_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tab, text="Enable AI Features", variable=self.llm_enabled_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=10)
        
        tk.Label(tab, text="API Key:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w")
        self.api_key_var = tk.StringVar()
        tk.Entry(tab, textvariable=self.api_key_var, show="*",
                font=("Segoe UI", 11), bg="#2A1050", fg="white",
                insertbackground="white").pack(fill="x", pady=5)
        
        tk.Label(tab, text="API URL:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w")
        self.api_url_var = tk.StringVar(value="https://api.openai.com/v1/chat/completions")
        tk.Entry(tab, textvariable=self.api_url_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white",
                insertbackground="white").pack(fill="x", pady=5)
        
        tk.Label(tab, text="Model:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w")
        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        tk.Entry(tab, textvariable=self.model_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white",
                insertbackground="white").pack(fill="x", pady=5)
    
    def _create_profiles_tab(self):
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="💾 Profiles")
        
        tk.Label(tab, text="Profile Management", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        save_frame = tk.Frame(tab, bg="#1A0A40")
        save_frame.pack(fill="x", pady=5)
        tk.Label(save_frame, text="Save as:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(side="left")
        self.profile_var = tk.StringVar()
        tk.Entry(save_frame, textvariable=self.profile_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white").pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(save_frame, text="💾 Save", bg="#6C3FCF", fg="white",
                 command=self._save_profile).pack(side="left")
        
        tk.Label(tab, text="Saved Profiles:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(20, 5))
        
        self.profiles_list = tk.Listbox(tab, bg="#2A1050", fg="white", font=("Segoe UI", 11))
        self.profiles_list.pack(fill="both", expand=True, pady=5)
        
        btn_frame = tk.Frame(tab, bg="#1A0A40")
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="📂 Load", bg="#8B5FEF", fg="white",
                 command=self._load_profile).pack(side="left", padx=3)
        tk.Button(btn_frame, text="🗑️ Delete", bg="#FF6B6B", fg="white",
                 command=self._delete_profile).pack(side="left", padx=3)
        
        self._refresh_profiles()
    
    def _start_buddy(self):
        """Start the anime buddy in a subprocess."""
        if self.buddy_process and self.buddy_process.poll() is None:
            messagebox.showinfo("Running", "Buddy is already running!")
            return
        
        try:
            # Save current settings first
            self._save_settings()
            
            # Start anime_buddy.py as subprocess
            self.buddy_process = subprocess.Popen(
                [sys.executable, "anime_buddy.py"],
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            self.status_var.set("● Buddy: Running")
            self.status_label.configure(fg="#00C851")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start buddy:\n{e}")
    
    def _stop_buddy(self):
        """Stop the buddy subprocess."""
        if self.buddy_process and self.buddy_process.poll() is None:
            self.buddy_process.terminate()
            self.buddy_process.wait(timeout=2)
            self.status_var.set("● Buddy: Stopped")
            self.status_label.configure(fg="#FF6B6B")
        else:
            messagebox.showinfo("Stopped", "Buddy is not running.")
    
    def _restart_buddy(self):
        """Restart the buddy."""
        self._stop_buddy()
        self.root.after(500, self._start_buddy)
    
    def _quick_save(self):
        """Quick save name and personality."""
        self._save_settings()
        messagebox.showinfo("Saved", "Settings saved! Restart buddy to apply changes.")
    
    def _pick_color(self, var, preview):
        """Open color picker."""
        color = colorchooser.askcolor(color=var.get())[1]
        if color:
            var.set(color)
            preview.configure(bg=color)
    
    def _apply_theme(self, colors):
        """Apply a preset theme."""
        for key, value in colors.items():
            if key in self.color_vars:
                self.color_vars[key].set(value)
    
    def _save_settings(self):
        """Save all settings to config file."""
        config = {
            "buddy": {
                "name": self.name_var.get(),
                "title": "Desktop Companion",
                "personality": self.personality_var.get(),
                "speech_style": "casual",
                "talk_frequency": self.talk_freq_var.get(),
                "energy_level": self.energy_var.get(),
            },
            "appearance": {k: v.get() for k, v in self.color_vars.items()},
            "behavior": {
                "walk_speed": self.speed_var.get(),
                "use_emojis": self.emojis_var.get(),
                "human_behaviors": True,
            },
            "llm": {
                "enabled": self.llm_enabled_var.get(),
                "api_key": self.api_key_var.get(),
                "api_url": self.api_url_var.get(),
                "model": self.model_var.get(),
            },
        }
        
        with open("anime_buddy_config.json", "w") as f:
            json.dump(config, f, indent=2)
    
    def _load_settings(self):
        """Load settings from config file."""
        try:
            with open("anime_buddy_config.json", "r") as f:
                config = json.load(f)
            
            buddy = config.get("buddy", {})
            self.name_var.set(buddy.get("name", "Miku"))
            self.personality_var.set(buddy.get("personality", "cheerful"))
            self.talk_freq_var.set(buddy.get("talk_frequency", "normal"))
            self.energy_var.set(buddy.get("energy_level", "normal"))
            
            colors = config.get("appearance", {})
            for key, val in colors.items():
                if key in self.color_vars:
                    self.color_vars[key].set(val)
            
            behavior = config.get("behavior", {})
            self.speed_var.set(behavior.get("walk_speed", 2.5))
            self.emojis_var.set(behavior.get("use_emojis", True))
            
            llm = config.get("llm", {})
            self.llm_enabled_var.set(llm.get("enabled", False))
            self.api_key_var.set(llm.get("api_key", ""))
            self.api_url_var.set(llm.get("api_url", "https://api.openai.com/v1/chat/completions"))
            self.model_var.set(llm.get("model", "gpt-3.5-turbo"))
        except FileNotFoundError:
            pass  # Use defaults
    
    def _save_profile(self):
        """Save current config as a profile."""
        name = self.profile_var.get().strip()
        if not name:
            return
        
        self._save_settings()
        
        # Copy to profile file
        import shutil
        shutil.copy("anime_buddy_config.json", f"profile_{name}.json")
        
        self._refresh_profiles()
        messagebox.showinfo("Saved", f"Profile '{name}' saved!")
    
    def _load_profile(self):
        """Load a saved profile."""
        sel = self.profiles_list.curselection()
        if not sel:
            return
        
        name = self.profiles_list.get(sel[0])
        try:
            import shutil
            shutil.copy(f"profile_{name}.json", "anime_buddy_config.json")
            self._load_settings()
            messagebox.showinfo("Loaded", f"Profile '{name}' loaded! Restart buddy to apply.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_profile(self):
        """Delete a profile."""
        sel = self.profiles_list.curselection()
        if not sel:
            return
        
        name = self.profiles_list.get(sel[0])
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            try:
                os.remove(f"profile_{name}.json")
                self._refresh_profiles()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _refresh_profiles(self):
        """Refresh profiles list."""
        self.profiles_list.delete(0, tk.END)
        import glob
        for f in glob.glob("profile_*.json"):
            name = f[8:-5]
            self.profiles_list.insert(tk.END, name)
    
    def _export_config(self):
        """Export config to file."""
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            import shutil
            shutil.copy("anime_buddy_config.json", path)
            messagebox.showinfo("Exported", f"Config exported to:\n{path}")
    
    def _import_config(self):
        """Import config from file."""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                import shutil
                shutil.copy(path, "anime_buddy_config.json")
                self._load_settings()
                messagebox.showinfo("Imported", "Config imported! Restart buddy to apply.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _exit(self):
        """Exit application."""
        if self.buddy_process and self.buddy_process.poll() is None:
            if messagebox.askyesno("Buddy Running", "Buddy is still running. Stop and exit?"):
                self._stop_buddy()
            else:
                return
        self.root.destroy()
    
    def run(self):
        """Run the launcher."""
        self.root.mainloop()


def main():
    app = BuddyLauncher()
    app.run()


if __name__ == "__main__":
    main()
