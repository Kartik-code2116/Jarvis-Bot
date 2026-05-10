"""
Launcher - Starts Bot Manager + Anime Buddy together
Manager window stays behind, Buddy stays on top
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import json
import threading
import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class CombinedApp:
    """Combined Manager + Buddy Application."""
    
    def __init__(self):
        # Start Manager Window first (will be behind)
        self.manager_root = tk.Tk()
        self.manager_root.title("🤖 Anime Buddy Control Panel")
        self.manager_root.geometry("900x700+50+50")
        self.manager_root.configure(bg="#1A0A40")
        self.manager_root.minsize(800, 600)
        
        # Manager stays in background
        self.manager_root.attributes("-topmost", False)
        self.manager_root.lift()
        
        self.buddy = None
        self.buddy_window = None
        
        self._build_manager_ui()
        
        # Start buddy after manager is ready
        self.manager_root.after(500, self._start_buddy)
        
    def _build_manager_ui(self):
        """Build the manager control panel."""
        # Header
        header = tk.Frame(self.manager_root, bg="#2A1050", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🤖 Anime Buddy Control Panel", 
                bg="#2A1050", fg="#B090FF",
                font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="● Starting...")
        self.status_label = tk.Label(header, textvariable=self.status_var,
                                     bg="#2A1050", fg="#FFD700",
                                     font=("Segoe UI", 12))
        self.status_label.pack(side="right", padx=20)
        
        # Main area
        main_frame = tk.Frame(self.manager_root, bg="#1A0A40")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Left: Controls
        left_panel = tk.Frame(main_frame, bg="#2A1050", width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="🎛️ Quick Controls", bg="#2A1050", fg="#B090FF",
                font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        # Quick action buttons
        controls = [
            ("👋 Bring Buddy to Front", self._bring_buddy_front),
            ("💬 Toggle Chat Panel", self._toggle_chat),
            ("🚶 Make Walk", self._make_walk),
            ("💃 Make Dance", self._make_dance),
            ("😴 Make Idle", self._make_idle),
        ]
        
        for text, cmd in controls:
            tk.Button(left_panel, text=text, bg="#6C3FCF", fg="white",
                     font=("Segoe UI", 11), command=cmd,
                     width=25).pack(pady=5)
        
        tk.Frame(left_panel, bg="#1A0A40", height=2).pack(fill="x", pady=15)
        
        # Customization shortcuts
        tk.Label(left_panel, text="⚡ Quick Customize", bg="#2A1050", fg="#B090FF",
                font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Name change
        name_frame = tk.Frame(left_panel, bg="#2A1050")
        name_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(name_frame, text="Name:", bg="#2A1050", fg="white",
                font=("Segoe UI", 10)).pack(side="left")
        self.name_var = tk.StringVar(value="Miku")
        tk.Entry(name_frame, textvariable=self.name_var,
                font=("Segoe UI", 10), bg="#1A0A40", fg="white",
                insertbackground="white", width=15).pack(side="left", padx=5)
        tk.Button(name_frame, text="✓", bg="#00C851", fg="white",
                 command=self._update_name, width=3).pack(side="left")
        
        # Personality
        tk.Label(left_panel, text="Personality:", bg="#2A1050", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        self.personality_var = tk.StringVar(value="cheerful")
        personalities = ["cheerful", "tsundere", "shy", "genki", "mysterious", "royal", "yandere"]
        ttk.Combobox(left_panel, textvariable=self.personality_var,
                    values=personalities, state="readonly").pack(fill="x", padx=10, pady=5)
        tk.Button(left_panel, text="Apply Personality", bg="#6C3FCF", fg="white",
                 command=self._update_personality).pack(pady=5)
        
        # Right: Full Settings Tabs
        right_panel = tk.Frame(main_frame, bg="#1A0A40")
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill="both", expand=True)
        
        # Style
        style = ttk.Style()
        style.configure("TNotebook", background="#1A0A40")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10))
        
        # Create tabs
        self._create_appearance_tab()
        self._create_behavior_tab()
        self._create_ai_tab()
        self._create_profiles_tab()
        
        # Bottom bar
        bottom = tk.Frame(self.manager_root, bg="#2A1050", height=50)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)
        
        tk.Button(bottom, text="💾 Save All Settings", bg="#00C851", fg="white",
                 font=("Segoe UI", 11, "bold"), command=self._save_settings).pack(side="left", padx=15, pady=8)
        
        tk.Button(bottom, text="🔄 Apply to Buddy", bg="#6C3FCF", fg="white",
                 font=("Segoe UI", 11, "bold"), command=self._apply_to_buddy).pack(side="left", padx=5, pady=8)
        
        tk.Button(bottom, text="📤 Export", bg="#8B5FEF", fg="white",
                 font=("Segoe UI", 10), command=self._export_config).pack(side="left", padx=5, pady=8)
        
        tk.Button(bottom, text="📥 Import", bg="#8B5FEF", fg="white",
                 font=("Segoe UI", 10), command=self._import_config).pack(side="left", padx=5, pady=8)
        
        tk.Button(bottom, text="❌ Exit", bg="#FF6B6B", fg="white",
                 font=("Segoe UI", 11), command=self._exit).pack(side="right", padx=15, pady=8)
        
    def _create_appearance_tab(self):
        """Create appearance customization tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🎨 Appearance")
        
        tk.Label(tab, text="Color Customization", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Color pickers
        self.color_vars = {}
        colors = [
            ("skin", "Skin Tone", "#FFD5B8"),
            ("hair_primary", "Hair Color", "#3A1F6E"),
            ("hair_highlight", "Hair Shine", "#5B2FC0"),
            ("eye_color", "Eye Color", "#6040E0"),
            ("shirt", "Outfit Top", "#6C8EEF"),
            ("skirt", "Outfit Bottom", "#3A54C0"),
            ("ribbon", "Ribbon", "#EF6CAA"),
            ("blush", "Blush", "#FFB3B3"),
        ]
        
        for key, label, default in colors:
            frame = tk.Frame(tab, bg="#1A0A40")
            frame.pack(fill="x", pady=3)
            
            tk.Label(frame, text=f"{label}:", bg="#1A0A40", fg="white",
                    font=("Segoe UI", 10), width=12, anchor="w").pack(side="left")
            
            var = tk.StringVar(value=default)
            self.color_vars[key] = var
            
            entry = tk.Entry(frame, textvariable=var, width=10,
                           font=("Segoe UI", 10), bg="#2A1050", fg="white")
            entry.pack(side="left", padx=5)
            
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
        """Create behavior settings tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🚶 Behavior")
        
        tk.Label(tab, text="Behavior Settings", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Walk Speed
        tk.Label(tab, text="Walk Speed:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        self.speed_var = tk.DoubleVar(value=2.5)
        tk.Scale(tab, from_=1.0, to=5.0, resolution=0.5, orient="horizontal",
                variable=self.speed_var, bg="#1A0A40", fg="white",
                highlightthickness=0, length=300).pack(anchor="w", pady=5)
        
        # Energy
        tk.Label(tab, text="Energy Level:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 0))
        self.energy_var = tk.StringVar(value="normal")
        for value, label in [("low", "Low"), ("normal", "Normal"), ("hyper", "Hyper")]:
            tk.Radiobutton(tab, text=label, variable=self.energy_var,
                          value=value, bg="#1A0A40", fg="white",
                          selectcolor="#6C3FCF", font=("Segoe UI", 10)).pack(anchor="w")
        
        # Talk Frequency
        tk.Label(tab, text="Talk Frequency:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 0))
        self.talk_freq_var = tk.StringVar(value="normal")
        for value, label in [("quiet", "Quiet"), ("normal", "Normal"), ("chatty", "Chatty")]:
            tk.Radiobutton(tab, text=label, variable=self.talk_freq_var,
                          value=value, bg="#1A0A40", fg="white",
                          selectcolor="#6C3FCF", font=("Segoe UI", 10)).pack(anchor="w")
        
        # Checkboxes
        self.emojis_var = tk.BooleanVar(value=True)
        tk.Checkbutton(tab, text="Use Emojis", variable=self.emojis_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 11)).pack(anchor="w", pady=10)
    
    def _create_ai_tab(self):
        """Create AI settings tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🤖 AI")
        
        tk.Label(tab, text="AI / LLM Settings", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        self.llm_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tab, text="Enable AI", variable=self.llm_enabled_var,
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
    
    def _create_profiles_tab(self):
        """Create profiles tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="💾 Profiles")
        
        tk.Label(tab, text="Save/Load Profiles", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Save
        save_frame = tk.Frame(tab, bg="#1A0A40")
        save_frame.pack(fill="x", pady=5)
        tk.Label(save_frame, text="Profile Name:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(side="left")
        self.profile_var = tk.StringVar()
        tk.Entry(save_frame, textvariable=self.profile_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white").pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(save_frame, text="💾 Save", bg="#6C3FCF", fg="white",
                 command=self._save_profile).pack(side="left")
        
        # Load
        tk.Label(tab, text="Saved Profiles:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(20, 5))
        
        self.profiles_list = tk.Listbox(tab, bg="#2A1050", fg="white",
                                       font=("Segoe UI", 11))
        self.profiles_list.pack(fill="both", expand=True, pady=5)
        
        btn_frame = tk.Frame(tab, bg="#1A0A40")
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="📂 Load", bg="#8B5FEF", fg="white",
                 command=self._load_profile).pack(side="left", padx=3)
        tk.Button(btn_frame, text="🗑️ Delete", bg="#FF6B6B", fg="white",
                 command=self._delete_profile).pack(side="left", padx=3)
        
        self._refresh_profiles()
    
    def _start_buddy(self):
        """Start the anime buddy - creates buddy using same mainloop."""
        if self.buddy:
            messagebox.showinfo("Already Running", "Buddy is already running!")
            return
        
        try:
            # Import anime_buddy module
            import anime_buddy
            from anime_buddy import BuddyConfig, BuddyPersonality, BuddyMemory
            
            # Create buddy window as Toplevel (shares mainloop with manager)
            self.buddy_root = tk.Toplevel(self.manager_root)
            self.buddy_root.title(f"{BuddyConfig.NAME} - {BuddyConfig.TITLE}")
            self.buddy_root.overrideredirect(True)
            self.buddy_root.attributes("-topmost", True)
            self.buddy_root.attributes("-transparentcolor", "#010101")
            self.buddy_root.configure(bg="#010101")
            self.buddy_root.resizable(False, False)
            
            # Position buddy on screen
            sw = self.manager_root.winfo_screenwidth()
            sh = self.manager_root.winfo_screenheight()
            buddy_x = sw - 200 - 40
            buddy_y = sh - 260 - 60
            self.buddy_root.geometry(f"200x260+{buddy_x}+{buddy_y}")
            
            # Create the buddy instance manually (we'll create a minimal version)
            self._create_minimal_buddy(self.buddy_root)
            
            self.status_var.set("● Buddy: Running")
            self.status_label.configure(fg="#00C851")
            
        except Exception as e:
            self.status_var.set("● Error")
            self.status_label.configure(fg="#FF6B6B")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to start buddy:\n{e}")
    
    def _bring_buddy_front(self):
        """Bring buddy window to front."""
        if self.buddy:
            self.buddy._bring_to_front()
    
    def _toggle_chat(self):
        """Toggle chat panel."""
        if self.buddy:
            self.buddy._show_chat()
    
    def _make_walk(self):
        """Set buddy to walk mode."""
        if self.buddy:
            self.buddy._set_mode("walk")
    
    def _make_dance(self):
        """Make buddy dance."""
        if self.buddy:
            self.buddy._do_action(("dance",))
    
    def _make_idle(self):
        """Set buddy to idle."""
        if self.buddy:
            self.buddy._do_action(("idle",))
    
    def _update_name(self):
        """Update buddy name."""
        if self.buddy:
            from anime_buddy import BuddyConfig
            BuddyConfig.NAME = self.name_var.get()
            self.buddy.root.title(f"{BuddyConfig.NAME} - {BuddyConfig.TITLE}")
            self.buddy._show_bubble(f"I'm {BuddyConfig.NAME} now! ✨")
    
    def _update_personality(self):
        """Update buddy personality."""
        if self.buddy:
            from anime_buddy import BuddyConfig, BuddyPersonality
            BuddyConfig.PERSONALITY = self.personality_var.get()
            self.buddy.personality = BuddyPersonality(BuddyConfig.PERSONALITY)
            self.buddy._show_bubble("Personality updated! 💕")
    
    def _pick_color(self, var, preview):
        """Open color picker."""
        color = colorchooser.askcolor(color=var.get())[1]
        if color:
            var.set(color)
            preview.configure(bg=color)
    
    def _apply_theme(self, colors):
        """Apply color theme."""
        for key, value in colors.items():
            if key in self.color_vars:
                self.color_vars[key].set(value)
    
    def _apply_to_buddy(self):
        """Apply all settings to buddy."""
        if not self.buddy:
            messagebox.showinfo("Not Running", "Buddy is not running yet!")
            return
        
        try:
            from anime_buddy import BuddyConfig
            
            # Update config
            BuddyConfig.NAME = self.name_var.get()
            BuddyConfig.PERSONALITY = self.personality_var.get()
            BuddyConfig.WALK_SPEED = self.speed_var.get()
            BuddyConfig.ENERGY_LEVEL = self.energy_var.get()
            BuddyConfig.TALK_FREQUENCY = self.talk_freq_var.get()
            BuddyConfig.USE_EMOJIS = self.emojis_var.get()
            
            # Update colors
            for key, var in self.color_vars.items():
                BuddyConfig.COLORS[key] = var.get()
            
            # Apply to buddy
            self.buddy._apply_custom_colors()
            self.buddy._show_bubble("Settings updated! ✨")
            
            messagebox.showinfo("Applied", "Settings applied to buddy!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply:\n{e}")
    
    def _save_settings(self):
        """Save settings to file."""
        config = {
            "buddy": {
                "name": self.name_var.get(),
                "personality": self.personality_var.get(),
            },
            "appearance": {k: v.get() for k, v in self.color_vars.items()},
            "behavior": {
                "walk_speed": self.speed_var.get(),
                "energy_level": self.energy_var.get(),
                "talk_frequency": self.talk_freq_var.get(),
                "use_emojis": self.emojis_var.get(),
            },
            "llm": {
                "enabled": self.llm_enabled_var.get(),
                "api_key": self.api_key_var.get(),
                "api_url": self.api_url_var.get(),
            },
        }
        
        with open("anime_buddy_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        messagebox.showinfo("Saved", "Settings saved!")
    
    def _save_profile(self):
        """Save as profile."""
        name = self.profile_var.get().strip()
        if not name:
            return
        
        config = {
            "buddy": {
                "name": self.name_var.get(),
                "personality": self.personality_var.get(),
            },
            "appearance": {k: v.get() for k, v in self.color_vars.items()},
        }
        
        with open(f"profile_{name}.json", "w") as f:
            json.dump(config, f, indent=2)
        
        self._refresh_profiles()
        messagebox.showinfo("Saved", f"Profile '{name}' saved!")
    
    def _load_profile(self):
        """Load a profile."""
        sel = self.profiles_list.curselection()
        if not sel:
            return
        
        name = self.profiles_list.get(sel[0])
        try:
            with open(f"profile_{name}.json", "r") as f:
                config = json.load(f)
            
            # Apply to UI
            buddy = config.get("buddy", {})
            self.name_var.set(buddy.get("name", "Miku"))
            self.personality_var.set(buddy.get("personality", "cheerful"))
            
            colors = config.get("appearance", {})
            for key, val in colors.items():
                if key in self.color_vars:
                    self.color_vars[key].set(val)
            
            self._apply_to_buddy()
            messagebox.showinfo("Loaded", f"Profile '{name}' loaded!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_profile(self):
        """Delete a profile."""
        sel = self.profiles_list.curselection()
        if not sel:
            return
        
        name = self.profiles_list.get(sel[0])
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            import os
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
        """Export config."""
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            config = {
                "buddy": {"name": self.name_var.get(), "personality": self.personality_var.get()},
                "appearance": {k: v.get() for k, v in self.color_vars.items()},
            }
            with open(path, "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Exported", f"Config exported to:\n{path}")
    
    def _import_config(self):
        """Import config."""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, "r") as f:
                    config = json.load(f)
                
                buddy = config.get("buddy", {})
                self.name_var.set(buddy.get("name", "Miku"))
                self.personality_var.set(buddy.get("personality", "cheerful"))
                
                colors = config.get("appearance", {})
                for key, val in colors.items():
                    if key in self.color_vars:
                        self.color_vars[key].set(val)
                
                self._apply_to_buddy()
                messagebox.showinfo("Imported", "Config imported!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _exit(self):
        """Exit application."""
        if hasattr(self, 'buddy_root') and self.buddy_root:
            try:
                self.buddy_root.destroy()
            except:
                pass
        self.manager_root.destroy()
        import sys
        sys.exit(0)
    
    def run(self):
        """Run the application."""
        self.manager_root.mainloop()


def main():
    """Main entry point."""
    app = CombinedApp()
    app.run()


if __name__ == "__main__":
    main()
