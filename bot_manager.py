"""
Bot Manager - Control Panel Application
A main window behind the anime buddy for full control and customization
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import json
import threading
import time


class BotManagerApp:
    """Main control panel application that runs behind the anime buddy."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Anime Buddy Manager")
        self.root.geometry("900x700")
        self.root.configure(bg="#1A0A40")
        self.root.minsize(800, 600)
        
        # Don't stay on top - let buddy be on top
        self.root.attributes("-topmost", False)
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Buddy reference (set later)
        self.buddy = None
        self.buddy_running = False
        
        self._build_ui()
        
    def _build_ui(self):
        """Build the control panel UI."""
        # Header
        header = tk.Frame(self.root, bg="#2A1050", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🤖 Anime Buddy Manager", 
                bg="#2A1050", fg="#B090FF",
                font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=10)
        
        # Status indicator
        self.status_var = tk.StringVar(value="● Buddy: Stopped")
        self.status_label = tk.Label(header, textvariable=self.status_var,
                                     bg="#2A1050", fg="#FF6B6B",
                                     font=("Segoe UI", 11))
        self.status_label.pack(side="right", padx=20)
        
        # Main content area (sidebar + content)
        main_frame = tk.Frame(self.root, bg="#1A0A40")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sidebar
        sidebar = tk.Frame(main_frame, bg="#2A1050", width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Sidebar buttons
        self._create_sidebar_button(sidebar, "▶ Start Buddy", self._start_buddy, "#00C851")
        self._create_sidebar_button(sidebar, "⏹ Stop Buddy", self._stop_buddy, "#FF6B6B")
        tk.Frame(sidebar, bg="#1A0A40", height=2).pack(fill="x", pady=10)
        
        self._create_sidebar_button(sidebar, "👤 Identity", lambda: self._show_tab("identity"))
        self._create_sidebar_button(sidebar, "🎨 Appearance", lambda: self._show_tab("appearance"))
        self._create_sidebar_button(sidebar, "🚶 Behavior", lambda: self._show_tab("behavior"))
        self._create_sidebar_button(sidebar, "🤖 AI Settings", lambda: self._show_tab("ai"))
        self._create_sidebar_button(sidebar, "💾 Profiles", lambda: self._show_tab("profiles"))
        tk.Frame(sidebar, bg="#1A0A40", height=2).pack(fill="x", pady=10)
        
        self._create_sidebar_button(sidebar, "📤 Export Config", self._export_config)
        self._create_sidebar_button(sidebar, "📥 Import Config", self._import_config)
        
        # Content area with tabs
        self.content = tk.Frame(main_frame, bg="#1A0A40")
        self.content.pack(side="right", fill="both", expand=True, padx=10)
        
        # Create all tabs
        self.tabs = {}
        self._create_identity_tab()
        self._create_appearance_tab()
        self._create_behavior_tab()
        self._create_ai_tab()
        self._create_profiles_tab()
        
        # Show default tab
        self._show_tab("identity")
        
        # Bottom bar
        bottom = tk.Frame(self.root, bg="#2A1050", height=40)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)
        
        tk.Button(bottom, text="💾 Save Settings", bg="#6C3FCF", fg="white",
                 font=("Segoe UI", 10, "bold"), command=self._save_settings).pack(side="left", padx=10, pady=5)
        
        tk.Button(bottom, text="🔄 Apply to Buddy", bg="#00C851", fg="white",
                 font=("Segoe UI", 10, "bold"), command=self._apply_to_buddy).pack(side="left", padx=5, pady=5)
        
        tk.Button(bottom, text="❌ Exit", bg="#FF6B6B", fg="white",
                 font=("Segoe UI", 10), command=self._on_close).pack(side="right", padx=10, pady=5)
        
    def _create_sidebar_button(self, parent, text, command, color="#6C3FCF"):
        """Create a styled sidebar button."""
        btn = tk.Button(parent, text=text, bg=color, fg="white",
                       font=("Segoe UI", 10), relief="flat",
                       command=command)
        btn.pack(fill="x", padx=10, pady=3)
        return btn
        
    def _show_tab(self, tab_name):
        """Show a specific tab."""
        for name, frame in self.tabs.items():
            frame.pack_forget()
        self.tabs[tab_name].pack(fill="both", expand=True)
        
    def _create_identity_tab(self):
        """Create identity/personality tab."""
        tab = tk.Frame(self.content, bg="#1A0A40")
        self.tabs["identity"] = tab
        
        tk.Label(tab, text="👤 Buddy Identity", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Name
        frame = tk.Frame(tab, bg="#1A0A40")
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text="Name:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11), width=12, anchor="w").pack(side="left")
        self.name_var = tk.StringVar(value="Miku")
        tk.Entry(frame, textvariable=self.name_var, font=("Segoe UI", 11),
                bg="#2A1050", fg="white", insertbackground="white").pack(side="left", fill="x", expand=True)
        
        # Title
        frame = tk.Frame(tab, bg="#1A0A40")
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text="Title:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11), width=12, anchor="w").pack(side="left")
        self.title_var = tk.StringVar(value="Desktop Companion")
        tk.Entry(frame, textvariable=self.title_var, font=("Segoe UI", 11),
                bg="#2A1050", fg="white", insertbackground="white").pack(side="left", fill="x", expand=True)
        
        # Personality
        tk.Label(tab, text="Personality:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 5))
        
        self.personality_var = tk.StringVar(value="cheerful")
        personalities = [
            ("cheerful", "😊 Cheerful", "Happy, optimistic, always smiling"),
            ("tsundere", "💢 Tsundere", "Acts tough but secretly cares"),
            ("shy", "🫣 Shy", "Quiet, gentle, easily flustered"),
            ("genki", "⚡ Genki", "Extremely energetic and enthusiastic"),
            ("mysterious", "🔮 Mysterious", "Wise, cryptic, speaks in riddles"),
            ("royal", "👑 Royal", "Elegant, demanding, princess-like"),
            ("yandere", "🔪 Yandere", "Intensely attached (for fun!)"),
        ]
        
        for value, label, desc in personalities:
            frame = tk.Frame(tab, bg="#1A0A40")
            frame.pack(fill="x", pady=2)
            tk.Radiobutton(frame, text=f"{label} - {desc}", variable=self.personality_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 10)).pack(anchor="w")
        
        # Speech Style
        tk.Label(tab, text="Speech Style:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 5))
        
        self.speech_var = tk.StringVar(value="casual")
        styles = [
            ("casual", "Casual", "Normal everyday speech"),
            ("formal", "Formal", "Polite and proper"),
            ("cute", "Cute (Uwu)", "Wike dis~ owo"),
            ("childish", "Childish", "Simple and innocent"),
        ]
        
        for value, label, desc in styles:
            frame = tk.Frame(tab, bg="#1A0A40")
            frame.pack(fill="x", pady=2)
            tk.Radiobutton(frame, text=f"{label} - {desc}", variable=self.speech_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 10)).pack(anchor="w")
        
    def _create_appearance_tab(self):
        """Create appearance/colors tab."""
        tab = tk.Frame(self.content, bg="#1A0A40")
        self.tabs["appearance"] = tab
        
        tk.Label(tab, text="🎨 Appearance Customization", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Color pickers
        self.color_vars = {}
        colors = [
            ("skin", "Skin Tone", "#FFD5B8"),
            ("hair_primary", "Hair Color (Main)", "#3A1F6E"),
            ("hair_highlight", "Hair Highlight", "#5B2FC0"),
            ("eye_color", "Eye Color", "#6040E0"),
            ("shirt", "Outfit Top", "#6C8EEF"),
            ("skirt", "Outfit Bottom", "#3A54C0"),
            ("ribbon", "Accessory", "#EF6CAA"),
            ("blush", "Blush", "#FFB3B3"),
        ]
        
        for key, label, default in colors:
            frame = tk.Frame(tab, bg="#1A0A40")
            frame.pack(fill="x", pady=3)
            
            tk.Label(frame, text=f"{label}:", bg="#1A0A40", fg="white",
                    font=("Segoe UI", 10), width=15, anchor="w").pack(side="left")
            
            var = tk.StringVar(value=default)
            self.color_vars[key] = var
            
            entry = tk.Entry(frame, textvariable=var, width=12,
                           font=("Segoe UI", 10), bg="#2A1050", fg="white")
            entry.pack(side="left", padx=5)
            
            # Color preview
            preview = tk.Frame(frame, bg=default, width=30, height=20)
            preview.pack(side="left", padx=5)
            
            def update_preview(p=preview, v=var: p.configure(bg=v.get())):
                p.configure(bg=v.get())
            
            tk.Button(frame, text="🎨 Pick", bg="#6C3FCF", fg="white",
                     command=lambda v=var, p=preview: self._pick_color(v, p)).pack(side="left", padx=5)
            
            # Theme presets
        tk.Label(tab, text="Quick Themes:", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20, 5))
        
        themes_frame = tk.Frame(tab, bg="#1A0A40")
        themes_frame.pack(fill="x")
        
        themes = [
            ("Classic", {"hair_primary": "#3A1F6E", "eye_color": "#6040E0", "hair_highlight": "#5B2FC0"}),
            ("Sakura", {"hair_primary": "#FF6B9D", "eye_color": "#FF1493", "hair_highlight": "#FFB6C1"}),
            ("Scarlet", {"hair_primary": "#DC143C", "eye_color": "#B22222", "hair_highlight": "#FF6B6B"}),
            ("Golden", {"hair_primary": "#FFD700", "eye_color": "#32CD32", "hair_highlight": "#FFFACD"}),
            ("Silver", {"hair_primary": "#C0C0C0", "eye_color": "#4682B4", "hair_highlight": "#E8E8E8"}),
            ("Teal", {"hair_primary": "#20B2AA", "eye_color": "#00CED1", "hair_highlight": "#40E0D0"}),
        ]
        
        for name, colors in themes:
            tk.Button(themes_frame, text=name, bg="#6C3FCF", fg="white",
                     command=lambda c=colors: self._apply_theme(c)).pack(side="left", padx=3, pady=3)
        
    def _pick_color(self, var, preview):
        """Open color picker."""
        color = colorchooser.askcolor(color=var.get(), title="Choose Color")[1]
        if color:
            var.set(color)
            preview.configure(bg=color)
    
    def _apply_theme(self, colors):
        """Apply a preset theme."""
        for key, value in colors.items():
            if key in self.color_vars:
                self.color_vars[key].set(value)
                
    def _create_behavior_tab(self):
        """Create behavior settings tab."""
        tab = tk.Frame(self.content, bg="#1A0A40")
        self.tabs["behavior"] = tab
        
        tk.Label(tab, text="🚶 Behavior Settings", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Walk Speed
        tk.Label(tab, text="Walk Speed:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        self.speed_var = tk.DoubleVar(value=2.5)
        tk.Scale(tab, from_=1.0, to=5.0, resolution=0.5, orient="horizontal",
                variable=self.speed_var, bg="#1A0A40", fg="white",
                highlightthickness=0, length=400).pack(anchor="w", pady=5)
        
        # Energy Level
        tk.Label(tab, text="Energy Level:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 0))
        self.energy_var = tk.StringVar(value="normal")
        for value, label, desc in [("low", "Low", "Slow and relaxed"), 
                                    ("normal", "Normal", "Balanced pace"),
                                    ("hyper", "Hyper", "Fast and energetic")]:
            tk.Radiobutton(tab, text=f"{label} - {desc}", variable=self.energy_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        
        # Talk Frequency
        tk.Label(tab, text="Talk Frequency:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(15, 0))
        self.talk_freq_var = tk.StringVar(value="normal")
        for value, label, desc in [("quiet", "Quiet", "Rarely speaks"),
                                    ("normal", "Normal", "Occasional comments"),
                                    ("chatty", "Chatty", "Talks often")]:
            tk.Radiobutton(tab, text=f"{label} - {desc}", variable=self.talk_freq_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        
        # Checkboxes
        self.emojis_var = tk.BooleanVar(value=True)
        tk.Checkbutton(tab, text="Use Emojis", variable=self.emojis_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 11)).pack(anchor="w", pady=10)
        
        self.human_var = tk.BooleanVar(value=True)
        tk.Checkbutton(tab, text="Human-like Behaviors", variable=self.human_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 11)).pack(anchor="w", pady=5)
        
    def _create_ai_tab(self):
        """Create AI/LLM settings tab."""
        tab = tk.Frame(self.content, bg="#1A0A40")
        self.tabs["ai"] = tab
        
        tk.Label(tab, text="🤖 AI / LLM Settings", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Warning
        tk.Label(tab, text="⚠️ API Key is stored locally on your computer only",
                bg="#1A0A40", fg="#FF6B6B", font=("Segoe UI", 10)).pack(pady=10)
        
        # Enable LLM
        self.llm_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tab, text="Enable AI Features", variable=self.llm_enabled_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 12, "bold"), command=self._toggle_llm).pack(anchor="w", pady=10)
        
        # LLM Frame
        self.llm_frame = tk.Frame(tab, bg="#1A0A40")
        self.llm_frame.pack(fill="x", pady=10)
        
        # API Key
        tk.Label(self.llm_frame, text="API Key:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w")
        self.api_key_var = tk.StringVar()
        self.api_key_entry = tk.Entry(self.llm_frame, textvariable=self.api_key_var,
                                     font=("Segoe UI", 11), show="*",
                                     bg="#2A1050", fg="white", insertbackground="white")
        self.api_key_entry.pack(fill="x", pady=5)
        
        # API URL
        tk.Label(self.llm_frame, text="API URL:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w")
        self.api_url_var = tk.StringVar(value="https://api.openai.com/v1/chat/completions")
        tk.Entry(self.llm_frame, textvariable=self.api_url_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white", insertbackground="white").pack(fill="x", pady=5)
        
        # Model
        tk.Label(self.llm_frame, text="Model:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w")
        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        tk.Entry(self.llm_frame, textvariable=self.model_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white", insertbackground="white").pack(fill="x", pady=5)
        
        # Tips
        tips = """💡 Tips:
• OpenAI: https://platform.openai.com (GPT models)
• Groq: https://console.groq.com (Faster, free tier available)
• Model examples: gpt-3.5-turbo, gpt-4, llama2-70b, mixtral-8x7b"""
        tk.Label(self.llm_frame, text=tips, bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 10), justify="left").pack(anchor="w", pady=10)
        
        self._toggle_llm()
        
    def _toggle_llm(self):
        """Enable/disable LLM fields."""
        state = "normal" if self.llm_enabled_var.get() else "disabled"
        for child in self.llm_frame.winfo_children():
            if isinstance(child, tk.Entry):
                child.configure(state=state)
                
    def _create_profiles_tab(self):
        """Create profiles management tab."""
        tab = tk.Frame(self.content, bg="#1A0A40")
        self.tabs["profiles"] = tab
        
        tk.Label(tab, text="💾 Profile Management", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)
        
        # Save Profile
        tk.Label(tab, text="Save Current as Profile:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        
        save_frame = tk.Frame(tab, bg="#1A0A40")
        save_frame.pack(fill="x", pady=5)
        
        self.profile_name_var = tk.StringVar()
        tk.Entry(save_frame, textvariable=self.profile_name_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white", insertbackground="white").pack(side="left", fill="x", expand=True)
        
        tk.Button(save_frame, text="💾 Save", bg="#6C3FCF", fg="white",
                 command=self._save_profile).pack(side="left", padx=5)
        
        # Saved profiles list
        tk.Label(tab, text="Saved Profiles:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 11)).pack(anchor="w", pady=(20, 5))
        
        self.profiles_listbox = tk.Listbox(tab, bg="#2A1050", fg="white",
                                          font=("Segoe UI", 11), selectmode="single")
        self.profiles_listbox.pack(fill="both", expand=True, pady=5)
        
        # Profile buttons
        btn_frame = tk.Frame(tab, bg="#1A0A40")
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="📂 Load", bg="#8B5FEF", fg="white",
                 command=self._load_profile).pack(side="left", padx=3)
        tk.Button(btn_frame, text="🗑️ Delete", bg="#FF6B6B", fg="white",
                 command=self._delete_profile).pack(side="left", padx=3)
        
    def _start_buddy(self):
        """Start the anime buddy."""
        if self.buddy_running:
            messagebox.showinfo("Already Running", "Buddy is already running!")
            return
        
        try:
            # Import and start buddy in a separate thread
            import anime_buddy
            
            def run_buddy():
                self.buddy = anime_buddy.AnimeBuddy()
                
            self.buddy_thread = threading.Thread(target=run_buddy, daemon=True)
            self.buddy_thread.start()
            
            self.buddy_running = True
            self.status_var.set("● Buddy: Running")
            self.status_label.configure(fg="#00C851")
            
            # Apply current settings
            self._apply_to_buddy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start buddy:\n{e}")
            
    def _stop_buddy(self):
        """Stop the anime buddy."""
        if not self.buddy_running:
            messagebox.showinfo("Not Running", "Buddy is not running.")
            return
        
        try:
            if self.buddy:
                self.buddy._quit()
            self.buddy_running = False
            self.status_var.set("● Buddy: Stopped")
            self.status_label.configure(fg="#FF6B6B")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop buddy:\n{e}")
            
    def _save_settings(self):
        """Save settings to config file."""
        try:
            config = self._gather_config()
            
            # Save to file
            with open("anime_buddy_config.json", "w") as f:
                json.dump(config, f, indent=2)
                
            messagebox.showinfo("💾 Saved", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")
            
    def _apply_to_buddy(self):
        """Apply current settings to running buddy."""
        if not self.buddy_running:
            messagebox.showinfo("Not Running", "Start the buddy first!")
            return
        
        try:
            # Apply settings to buddy
            if self.buddy:
                # Update buddy config
                self.buddy.config.NAME = self.name_var.get()
                self.buddy.config.TITLE = self.title_var.get()
                self.buddy.config.PERSONALITY = self.personality_var.get()
                self.buddy.config.SPEECH_STYLE = self.speech_var.get()
                self.buddy.config.TALK_FREQUENCY = self.talk_freq_var.get()
                self.buddy.config.ENERGY_LEVEL = self.energy_var.get()
                self.buddy.config.WALK_SPEED = self.speed_var.get()
                self.buddy.config.USE_EMOJIS = self.emojis_var.get()
                
                # Apply colors
                for key, var in self.color_vars.items():
                    self.buddy.config.COLORS[key] = var.get()
                
                # Apply to character
                self.buddy._apply_custom_colors()
                
            messagebox.showinfo("✅ Applied", "Settings applied to buddy!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply:\n{e}")
            
    def _gather_config(self):
        """Gather all settings into a dict."""
        return {
            "buddy": {
                "name": self.name_var.get(),
                "title": self.title_var.get(),
                "personality": self.personality_var.get(),
                "speech_style": self.speech_var.get(),
                "talk_frequency": self.talk_freq_var.get(),
                "energy_level": self.energy_var.get(),
            },
            "appearance": {key: var.get() for key, var in self.color_vars.items()},
            "behavior": {
                "walk_speed": self.speed_var.get(),
                "use_emojis": self.emojis_var.get(),
                "human_behaviors": self.human_var.get(),
            },
            "llm": {
                "enabled": self.llm_enabled_var.get(),
                "api_key": self.api_key_var.get(),
                "api_url": self.api_url_var.get(),
                "model": self.model_var.get(),
            },
        }
        
    def _save_profile(self):
        """Save current config as a profile."""
        name = self.profile_name_var.get().strip()
        if not name:
            messagebox.showwarning("Error", "Please enter a profile name")
            return
        
        config = self._gather_config()
        try:
            with open(f"profile_{name}.json", "w") as f:
                json.dump(config, f, indent=2)
            self._refresh_profiles_list()
            messagebox.showinfo("Saved", f"Profile '{name}' saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile:\n{e}")
            
    def _load_profile(self):
        """Load a selected profile."""
        selection = self.profiles_listbox.curselection()
        if not selection:
            messagebox.showwarning("Error", "Please select a profile")
            return
        
        name = self.profiles_listbox.get(selection[0])
        try:
            with open(f"profile_{name}.json", "r") as f:
                config = json.load(f)
            self._apply_config(config)
            messagebox.showinfo("Loaded", f"Profile '{name}' loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile:\n{e}")
            
    def _delete_profile(self):
        """Delete selected profile."""
        selection = self.profiles_listbox.curselection()
        if not selection:
            messagebox.showwarning("Error", "Please select a profile")
            return
        
        name = self.profiles_listbox.get(selection[0])
        if messagebox.askyesno("Confirm", f"Delete profile '{name}'?"):
            try:
                import os
                os.remove(f"profile_{name}.json")
                self._refresh_profiles_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete:\n{e}")
                
    def _refresh_profiles_list(self):
        """Refresh the profiles listbox."""
        self.profiles_listbox.delete(0, tk.END)
        import os
        import glob
        for file in glob.glob("profile_*.json"):
            name = file[8:-5]  # Remove "profile_" prefix and ".json" suffix
            self.profiles_listbox.insert(tk.END, name)
            
    def _apply_config(self, config):
        """Apply a config dict to UI."""
        # Apply buddy settings
        buddy = config.get("buddy", {})
        self.name_var.set(buddy.get("name", "Miku"))
        self.title_var.set(buddy.get("title", "Desktop Companion"))
        self.personality_var.set(buddy.get("personality", "cheerful"))
        self.speech_var.set(buddy.get("speech_style", "casual"))
        self.talk_freq_var.set(buddy.get("talk_frequency", "normal"))
        self.energy_var.set(buddy.get("energy_level", "normal"))
        
        # Apply colors
        colors = config.get("appearance", {})
        for key, value in colors.items():
            if key in self.color_vars:
                self.color_vars[key].set(value)
        
        # Apply behavior
        behavior = config.get("behavior", {})
        self.speed_var.set(behavior.get("walk_speed", 2.5))
        self.emojis_var.set(behavior.get("use_emojis", True))
        self.human_var.set(behavior.get("human_behaviors", True))
        
        # Apply LLM
        llm = config.get("llm", {})
        self.llm_enabled_var.set(llm.get("enabled", False))
        self.api_key_var.set(llm.get("api_key", ""))
        self.api_url_var.set(llm.get("api_url", "https://api.openai.com/v1/chat/completions"))
        self.model_var.set(llm.get("model", "gpt-3.5-turbo"))
        
    def _export_config(self):
        """Export config to file."""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export Configuration"
        )
        if path:
            config = self._gather_config()
            with open(path, "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Exported", f"Config exported to:\n{path}")
            
    def _import_config(self):
        """Import config from file."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import Configuration"
        )
        if path:
            try:
                with open(path, "r") as f:
                    config = json.load(f)
                self._apply_config(config)
                messagebox.showinfo("Imported", "Configuration imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import:\n{e}")
                
    def _on_close(self):
        """Handle window close."""
        if self.buddy_running:
            if messagebox.askyesno("Buddy Running", "Buddy is still running. Stop and exit?"):
                self._stop_buddy()
            else:
                return
        self.root.destroy()
        
    def run(self):
        """Run the manager application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = BotManagerApp()
    
    # Auto-start buddy if desired
    # app._start_buddy()
    
    app.run()


if __name__ == "__main__":
    main()
