"""
Settings Window for Anime Buddy
Provides GUI for customizing all aspects of the buddy
"""
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import json


class SettingsWindow:
    """Settings window for customizing the anime buddy."""
    
    def __init__(self, parent, config_manager, on_apply=None):
        self.parent = parent
        self.config = config_manager
        self.on_apply = on_apply
        
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Anime Buddy Settings")
        self.window.geometry("600x700")
        self.window.configure(bg="#1A0A40")
        self.window.resizable(False, False)
        
        # Make modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self._build_ui()
        self._load_current_settings()
    
    def _build_ui(self):
        """Build the settings UI."""
        # Title
        tk.Label(self.window, text="⚙️ Customize Your Buddy", 
                bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Style for tabs
        style = ttk.Style()
        style.configure("TNotebook", background="#1A0A40")
        style.configure("TNotebook.Tab", font=("Segoe UI", 9))
        
        # Create tabs
        self._create_identity_tab()
        self._create_appearance_tab()
        self._create_behavior_tab()
        self._create_llm_tab()
        self._create_profiles_tab()
        
        # Buttons frame
        btn_frame = tk.Frame(self.window, bg="#1A0A40")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="💾 Save", bg="#6C3FCF", fg="white",
                 font=("Segoe UI", 10, "bold"), command=self._save_settings).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="🔄 Reset to Defaults", bg="#8B5FEF", fg="white",
                 font=("Segoe UI", 10), command=self._reset_defaults).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", bg="#404040", fg="white",
                 font=("Segoe UI", 10), command=self.window.destroy).pack(side="right", padx=5)
        
        tk.Button(btn_frame, text="✨ Apply", bg="#00C851", fg="white",
                 font=("Segoe UI", 10, "bold"), command=self._apply_settings).pack(side="right", padx=5)
    
    def _create_identity_tab(self):
        """Create identity/personality tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="👤 Identity")
        
        # Name
        tk.Label(tab, text="Buddy Name:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        self.name_var = tk.StringVar()
        tk.Entry(tab, textvariable=self.name_var, font=("Segoe UI", 11),
                bg="#2A1050", fg="white", insertbackground="white").pack(fill="x", padx=10, pady=5)
        
        # Title
        tk.Label(tab, text="Title/Role:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        self.title_var = tk.StringVar()
        tk.Entry(tab, textvariable=self.title_var, font=("Segoe UI", 11),
                bg="#2A1050", fg="white", insertbackground="white").pack(fill="x", padx=10, pady=5)
        
        # Personality
        tk.Label(tab, text="Personality:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(15, 0))
        
        self.personality_var = tk.StringVar()
        personalities = self.config.PERSONALITIES
        for value, label, desc in personalities:
            frame = tk.Frame(tab, bg="#1A0A40")
            frame.pack(fill="x", padx=10, pady=2)
            tk.Radiobutton(frame, text=f"{label} - {desc}", variable=self.personality_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 9)).pack(anchor="w")
        
        # Speech Style
        tk.Label(tab, text="Speech Style:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(15, 0))
        
        self.speech_var = tk.StringVar()
        speech_frame = tk.Frame(tab, bg="#1A0A40")
        speech_frame.pack(fill="x", padx=10, pady=5)
        for value, label, desc in self.config.SPEECH_STYLES:
            tk.Radiobutton(speech_frame, text=label, variable=self.speech_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 9)).pack(anchor="w")
    
    def _create_appearance_tab(self):
        """Create appearance/colors tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🎨 Appearance")
        
        # Canvas for preview (placeholder)
        tk.Label(tab, text="Color Customization", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        self.color_vars = {}
        color_labels = [
            ("skin", "Skin Tone"),
            ("hair_primary", "Hair Color (Main)"),
            ("hair_highlight", "Hair Highlight"),
            ("eye_color", "Eye Color"),
            ("shirt", "Outfit Top"),
            ("skirt", "Outfit Bottom"),
            ("ribbon", "Accessory/Ribbon"),
            ("blush", "Blush Color"),
        ]
        
        for key, label in color_labels:
            frame = tk.Frame(tab, bg="#1A0A40")
            frame.pack(fill="x", padx=10, pady=3)
            
            tk.Label(frame, text=f"{label}:", bg="#1A0A40", fg="white",
                    font=("Segoe UI", 9), width=15, anchor="w").pack(side="left")
            
            var = tk.StringVar()
            self.color_vars[key] = var
            
            entry = tk.Entry(frame, textvariable=var, width=10,
                           font=("Segoe UI", 9), bg="#2A1050", fg="white")
            entry.pack(side="left", padx=5)
            
            btn = tk.Button(frame, text="🎨", bg="#6C3FCF", fg="white",
                          command=lambda k=key, v=var: self._pick_color(k, v))
            btn.pack(side="left")
    
    def _pick_color(self, key, var):
        """Open color picker."""
        color = colorchooser.askcolor(color=var.get(), title=f"Choose {key}")[1]
        if color:
            var.set(color)
    
    def _create_behavior_tab(self):
        """Create behavior settings tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🚶 Behavior")
        
        # Walk Speed
        tk.Label(tab, text="Walk Speed:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        self.speed_var = tk.DoubleVar(value=2.5)
        tk.Scale(tab, from_=1.0, to=5.0, resolution=0.5, orient="horizontal",
                variable=self.speed_var, bg="#1A0A40", fg="white",
                highlightthickness=0).pack(fill="x", padx=10, pady=5)
        
        # Energy Level
        tk.Label(tab, text="Energy Level:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        self.energy_var = tk.StringVar(value="normal")
        energy_frame = tk.Frame(tab, bg="#1A0A40")
        energy_frame.pack(fill="x", padx=10, pady=5)
        for value, label, desc in self.config.ENERGY_LEVELS:
            tk.Radiobutton(energy_frame, text=f"{label} - {desc}", variable=self.energy_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 9)).pack(anchor="w")
        
        # Talk Frequency
        tk.Label(tab, text="Talk Frequency:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        self.talk_freq_var = tk.StringVar(value="normal")
        talk_frame = tk.Frame(tab, bg="#1A0A40")
        talk_frame.pack(fill="x", padx=10, pady=5)
        for value, label, desc in self.config.TALK_FREQUENCIES:
            tk.Radiobutton(talk_frame, text=f"{label} - {desc}", variable=self.talk_freq_var,
                          value=value, bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                          font=("Segoe UI", 9)).pack(anchor="w")
        
        # Checkboxes
        self.emojis_var = tk.BooleanVar(value=True)
        tk.Checkbutton(tab, text="Use Emojis", variable=self.emojis_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=10)
        
        self.human_var = tk.BooleanVar(value=True)
        tk.Checkbutton(tab, text="Human-like Behaviors", variable=self.human_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=5)
    
    def _create_llm_tab(self):
        """Create LLM/API settings tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="🤖 AI/LLM")
        
        # Warning
        tk.Label(tab, text="⚠️ API Key is stored locally on your computer",
                bg="#1A0A40", fg="#FF6B6B", font=("Segoe UI", 9)).pack(pady=10)
        
        # Enable LLM
        self.llm_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tab, text="Enable AI Features", variable=self.llm_enabled_var,
                      bg="#1A0A40", fg="white", selectcolor="#6C3FCF",
                      font=("Segoe UI", 11, "bold"), command=self._toggle_llm).pack(anchor="w", padx=10, pady=10)
        
        # API Key
        self.llm_frame = tk.Frame(tab, bg="#1A0A40")
        self.llm_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(self.llm_frame, text="API Key:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w")
        self.api_key_var = tk.StringVar()
        self.api_key_entry = tk.Entry(self.llm_frame, textvariable=self.api_key_var,
                                     font=("Segoe UI", 10), show="*",
                                     bg="#2A1050", fg="white", insertbackground="white")
        self.api_key_entry.pack(fill="x", pady=5)
        
        # API URL
        tk.Label(self.llm_frame, text="API URL:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w")
        self.api_url_var = tk.StringVar(value="https://api.openai.com/v1/chat/completions")
        tk.Entry(self.llm_frame, textvariable=self.api_url_var,
                font=("Segoe UI", 10), bg="#2A1050", fg="white", insertbackground="white").pack(fill="x", pady=5)
        
        # Model
        tk.Label(self.llm_frame, text="Model:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w")
        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        tk.Entry(self.llm_frame, textvariable=self.model_var,
                font=("Segoe UI", 10), bg="#2A1050", fg="white", insertbackground="white").pack(fill="x", pady=5)
        
        # Tips
        tips = """💡 Tips:
• Use OpenAI API key for GPT models
• Use Groq API (https://api.groq.com/openai/v1/chat/completions) for faster/cheaper models
• Other compatible APIs: LocalAI, Ollama, etc.
• Model examples: gpt-3.5-turbo, gpt-4, llama2-70b, mixtral-8x7b"""
        tk.Label(self.llm_frame, text=tips, bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 9), justify="left").pack(anchor="w", pady=10)
        
        self._toggle_llm()
    
    def _toggle_llm(self):
        """Enable/disable LLM fields."""
        state = "normal" if self.llm_enabled_var.get() else "disabled"
        for child in self.llm_frame.winfo_children():
            if isinstance(child, tk.Entry):
                child.configure(state=state)
    
    def _create_profiles_tab(self):
        """Create profiles management tab."""
        tab = tk.Frame(self.notebook, bg="#1A0A40")
        self.notebook.add(tab, text="💾 Profiles")
        
        tk.Label(tab, text="Profile Management", bg="#1A0A40", fg="#B090FF",
                font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        # Current Profile
        tk.Label(tab, text="Current Profile:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        
        profile_frame = tk.Frame(tab, bg="#1A0A40")
        profile_frame.pack(fill="x", padx=10, pady=5)
        
        self.profile_name_var = tk.StringVar(value="default")
        tk.Entry(profile_frame, textvariable=self.profile_name_var,
                font=("Segoe UI", 11), bg="#2A1050", fg="white", insertbackground="white").pack(side="left", fill="x", expand=True)
        
        tk.Button(profile_frame, text="💾 Save", bg="#6C3FCF", fg="white",
                 command=self._save_profile).pack(side="left", padx=5)
        
        # Load Profile
        tk.Label(tab, text="Load Profile:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(15, 0))
        
        load_frame = tk.Frame(tab, bg="#1A0A40")
        load_frame.pack(fill="x", padx=10, pady=5)
        
        self.load_profile_var = tk.StringVar()
        profiles = self.config.list_profiles()
        if profiles:
            self.load_profile_var.set(profiles[0])
        
        self.profile_menu = ttk.Combobox(load_frame, textvariable=self.load_profile_var,
                                        values=profiles, state="readonly")
        self.profile_menu.pack(side="left", fill="x", expand=True)
        
        tk.Button(load_frame, text="📂 Load", bg="#8B5FEF", fg="white",
                 command=self._load_profile).pack(side="left", padx=5)
        
        # Export/Import
        tk.Label(tab, text="Share Configuration:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(15, 0))
        
        share_frame = tk.Frame(tab, bg="#1A0A40")
        share_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(share_frame, text="📤 Export Config", bg="#00C851", fg="white",
                 command=self._export_config).pack(side="left", padx=5)
        
        tk.Button(share_frame, text="📥 Import Config", bg="#00C851", fg="white",
                 command=self._import_config).pack(side="left", padx=5)
    
    def _load_current_settings(self):
        """Load current settings into UI."""
        # Identity
        self.name_var.set(self.config.get("buddy", "name", "Miku"))
        self.title_var.set(self.config.get("buddy", "title", "Desktop Companion"))
        self.personality_var.set(self.config.get("buddy", "personality", "cheerful"))
        self.speech_var.set(self.config.get("buddy", "speech_style", "casual"))
        
        # Appearance
        colors = self.config.get("appearance", default={})
        for key, var in self.color_vars.items():
            var.set(colors.get(key, self.config.DEFAULTS["appearance"].get(key)))
        
        # Behavior
        self.speed_var.set(self.config.get("behavior", "walk_speed", 2.5))
        self.energy_var.set(self.config.get("buddy", "energy_level", "normal"))
        self.talk_freq_var.set(self.config.get("buddy", "talk_frequency", "normal"))
        self.emojis_var.set(self.config.get("behavior", "use_emojis", True))
        self.human_var.set(self.config.get("behavior", "human_behaviors", True))
        
        # LLM
        llm = self.config.get("llm", default={})
        self.llm_enabled_var.set(llm.get("enabled", False))
        self.api_key_var.set(llm.get("api_key", ""))
        self.api_url_var.set(llm.get("api_url", "https://api.openai.com/v1/chat/completions"))
        self.model_var.set(llm.get("model", "gpt-3.5-turbo"))
    
    def _save_settings(self):
        """Save settings to config."""
        # Identity
        self.config.set("buddy", "name", self.name_var.get())
        self.config.set("buddy", "title", self.title_var.get())
        self.config.set("buddy", "personality", self.personality_var.get())
        self.config.set("buddy", "speech_style", self.speech_var.get())
        self.config.set("buddy", "energy_level", self.energy_var.get())
        self.config.set("buddy", "talk_frequency", self.talk_freq_var.get())
        
        # Appearance
        colors = {key: var.get() for key, var in self.color_vars.items()}
        self.config.set_multi("appearance", colors)
        
        # Behavior
        self.config.set("behavior", "walk_speed", self.speed_var.get())
        self.config.set("behavior", "use_emojis", self.emojis_var.get())
        self.config.set("behavior", "human_behaviors", self.human_var.get())
        
        # LLM
        llm_config = {
            "enabled": self.llm_enabled_var.get(),
            "api_key": self.api_key_var.get(),
            "api_url": self.api_url_var.get(),
            "model": self.model_var.get(),
        }
        self.config.set_multi("llm", llm_config)
        
        # Mark first run as False
        self.config.set("first_run", False, None)
        
        self.config.save()
        messagebox.showinfo("💾 Saved", "Settings saved successfully!")
    
    def _apply_settings(self):
        """Save and apply settings immediately."""
        self._save_settings()
        if self.on_apply:
            self.on_apply()
        self.window.destroy()
    
    def _reset_defaults(self):
        """Reset to default settings."""
        if messagebox.askyesno("🔄 Reset", "Reset all settings to defaults?"):
            self.config.reset_to_defaults()
            self._load_current_settings()
            messagebox.showinfo("✅ Reset", "Settings reset to defaults!")
    
    def _save_profile(self):
        """Save current config as profile."""
        name = self.profile_name_var.get().strip()
        if not name:
            messagebox.showwarning("⚠️ Error", "Please enter a profile name")
            return
        self.config.save_profile(name)
        self._update_profile_list()
        messagebox.showinfo("💾 Profile Saved", f"Profile '{name}' saved!")
    
    def _load_profile(self):
        """Load selected profile."""
        name = self.load_profile_var.get()
        if name and self.config.load_profile(name):
            self._load_current_settings()
            messagebox.showinfo("📂 Profile Loaded", f"Profile '{name}' loaded!")
    
    def _update_profile_list(self):
        """Update profile dropdown."""
        profiles = self.config.list_profiles()
        self.profile_menu.configure(values=profiles)
        if profiles:
            self.load_profile_var.set(profiles[0])
    
    def _export_config(self):
        """Export config to file."""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Configuration"
        )
        if path:
            self.config.export_config(path)
            messagebox.showinfo("📤 Exported", f"Configuration exported to:\n{path}")
    
    def _import_config(self):
        """Import config from file."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Configuration"
        )
        if path:
            try:
                self.config.import_config(path)
                self._load_current_settings()
                messagebox.showinfo("📥 Imported", "Configuration imported successfully!")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to import: {e}")
