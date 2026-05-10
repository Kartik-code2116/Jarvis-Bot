"""
First-Run Setup Wizard for Anime Buddy
Guides new users through initial configuration
"""
import tkinter as tk
from tkinter import ttk, messagebox


class SetupWizard:
    """First-time setup wizard for new users."""
    
    def __init__(self, parent, config_manager, on_complete=None):
        self.parent = parent
        self.config = config_manager
        self.on_complete = on_complete
        self.current_step = 0
        
        self.window = tk.Toplevel(parent)
        self.window.title("✨ Welcome to Anime Buddy!")
        self.window.geometry("500x600")
        self.window.configure(bg="#1A0A40")
        self.window.resizable(False, False)
        
        # Make modal
        self.window.transient(parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._build_ui()
        self._show_step(0)
    
    def _build_ui(self):
        """Build the wizard UI."""
        # Header
        self.header = tk.Label(self.window, text="✨ Welcome! ✨", 
                              bg="#1A0A40", fg="#B090FF",
                              font=("Segoe UI", 18, "bold"))
        self.header.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.window, length=400, mode='determinate')
        self.progress.pack(pady=10)
        
        # Content frame
        self.content_frame = tk.Frame(self.window, bg="#1A0A40", width=450, height=400)
        self.content_frame.pack(pady=10)
        self.content_frame.pack_propagate(False)
        
        # Buttons frame
        btn_frame = tk.Frame(self.window, bg="#1A0A40")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.back_btn = tk.Button(btn_frame, text="◀ Back", bg="#404040", fg="white",
                                 font=("Segoe UI", 10), command=self._prev_step)
        self.back_btn.pack(side="left")
        
        self.next_btn = tk.Button(btn_frame, text="Next ▶", bg="#6C3FCF", fg="white",
                                 font=("Segoe UI", 10, "bold"), command=self._next_step)
        self.next_btn.pack(side="right")
        
        # Skip link
        tk.Button(self.window, text="Skip Setup (Use Defaults)", bg="#1A0A40", fg="#8060C0",
                 font=("Segoe UI", 9), bd=0, command=self._skip).pack(pady=5)
    
    def _show_step(self, step):
        """Show a specific step."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_step = step
        self.progress['value'] = (step / 4) * 100
        
        # Update buttons
        self.back_btn.configure(state="normal" if step > 0 else "disabled")
        self.next_btn.configure(text="Finish! ✨" if step == 4 else "Next ▶")
        
        # Show step content
        steps = [
            self._step_welcome,
            self._step_name,
            self._step_personality,
            self._step_appearance,
            self._step_llm,
        ]
        
        if step < len(steps):
            steps[step]()
    
    def _step_welcome(self):
        """Welcome step."""
        self.header.configure(text="✨ Welcome to Anime Buddy! ✨")
        
        tk.Label(self.content_frame, 
                text="Your new desktop companion is almost ready!\n\nLet's set up your buddy in just a few steps.",
                bg="#1A0A40", fg="white", font=("Segoe UI", 12), wraplength=400).pack(pady=50)
        
        features = [
            "🚶 Walks around your screen freely",
            "💬 Responds to your commands",
            "🎨 Fully customizable appearance",
            "🧠 Optional AI brain for smart conversations",
            "💕 Remembers your interactions",
        ]
        
        for feat in features:
            tk.Label(self.content_frame, text=feat, bg="#1A0A40", fg="#B090FF",
                    font=("Segoe UI", 11), anchor="w").pack(fill="x", padx=50, pady=3)
    
    def _step_name(self):
        """Name step."""
        self.header.configure(text="👤 What's Their Name?")
        
        tk.Label(self.content_frame,
                text="Give your buddy a name!\nThis is what they'll call themselves.",
                bg="#1A0A40", fg="white", font=("Segoe UI", 12), wraplength=400).pack(pady=30)
        
        self.name_var = tk.StringVar(value="Miku")
        tk.Entry(self.content_frame, textvariable=self.name_var,
                font=("Segoe UI", 16), bg="#2A1050", fg="white",
                insertbackground="white", justify="center").pack(pady=20)
        
        # Quick suggestions
        tk.Label(self.content_frame, text="Popular names:", bg="#1A0A40", fg="#8060C0",
                font=("Segoe UI", 10)).pack(pady=(20, 5))
        
        names_frame = tk.Frame(self.content_frame, bg="#1A0A40")
        names_frame.pack()
        
        popular_names = ["Miku", "Sakura", "Yui", "Hina", "Mio", "Rin", "Luna"]
        for name in popular_names:
            tk.Button(names_frame, text=name, bg="#6C3FCF", fg="white",
                     font=("Segoe UI", 9), 
                     command=lambda n=name: self.name_var.set(n)).pack(side="left", padx=3)
    
    def _step_personality(self):
        """Personality step."""
        self.header.configure(text="🎭 Choose a Personality")
        
        tk.Label(self.content_frame,
                text="What kind of personality should your buddy have?",
                bg="#1A0A40", fg="white", font=("Segoe UI", 12), wraplength=400).pack(pady=20)
        
        self.personality_var = tk.StringVar(value="cheerful")
        
        personalities = [
            ("cheerful", "😊 Cheerful", "Happy, optimistic, always smiling"),
            ("tsundere", "💢 Tsundere", "Acts tough but secretly cares about you"),
            ("shy", "🫣 Shy", "Quiet, gentle, easily flustered"),
            ("genki", "⚡ Genki", "Extremely energetic and enthusiastic"),
            ("mysterious", "🔮 Mysterious", "Wise, cryptic, speaks in riddles"),
            ("royal", "👑 Royal", "Elegant, demanding, princess-like"),
            ("yandere", "🔪 Yandere", "Intensely attached (for fun!)"),
        ]
        
        for value, label, desc in personalities:
            frame = tk.Frame(self.content_frame, bg="#1A0A40")
            frame.pack(fill="x", padx=30, pady=3)
            
            tk.Radiobutton(frame, text=label, variable=self.personality_var,
                          value=value, bg="#1A0A40", fg="white",
                          selectcolor="#6C3FCF", font=("Segoe UI", 11, "bold"),
                          anchor="w").pack(anchor="w")
            tk.Label(frame, text=desc, bg="#1A0A40", fg="#B090FF",
                    font=("Segoe UI", 9), anchor="w").pack(anchor="w", padx=30)
    
    def _step_appearance(self):
        """Appearance step."""
        self.header.configure(text="🎨 Customize Appearance")
        
        tk.Label(self.content_frame,
                text="Choose a color theme for your buddy:",
                bg="#1A0A40", fg="white", font=("Segoe UI", 12)).pack(pady=20)
        
        self.theme_var = tk.StringVar(value="default")
        
        themes = [
            ("default", "Classic", "#3A1F6E", "#6040E0", "Purple hair, blue eyes"),
            ("pink", "Sakura", "#FF6B9D", "#FF1493", "Pink hair, pink eyes"),
            ("red", "Scarlet", "#DC143C", "#B22222", "Red hair, red eyes"),
            ("blonde", "Golden", "#FFD700", "#32CD32", "Blonde hair, green eyes"),
            ("silver", "Silver", "#C0C0C0", "#4682B4", "Silver hair, blue eyes"),
            ("teal", "Ocean", "#20B2AA", "#00CED1", "Teal hair, cyan eyes"),
        ]
        
        for value, name, hair, eye, desc in themes:
            frame = tk.Frame(self.content_frame, bg="#1A0A40")
            frame.pack(fill="x", padx=30, pady=5)
            
            tk.Radiobutton(frame, text=f"{name}", variable=self.theme_var,
                          value=value, bg="#1A0A40", fg="white",
                          selectcolor="#6C3FCF", font=("Segoe UI", 11, "bold"),
                          anchor="w").pack(anchor="w")
            
            color_preview = tk.Frame(frame, bg=hair, width=20, height=20)
            color_preview.pack(side="left", padx=5)
            color_preview2 = tk.Frame(frame, bg=eye, width=20, height=20)
            color_preview2.pack(side="left", padx=5)
            
            tk.Label(frame, text=desc, bg="#1A0A40", fg="#B090FF",
                    font=("Segoe UI", 9)).pack(side="left", padx=10)
    
    def _step_llm(self):
        """LLM/AI step."""
        self.header.configure(text="🤖 Enable AI? (Optional)")
        
        tk.Label(self.content_frame,
                text="Would you like to add an AI brain to your buddy?\n\nThis lets them understand natural language and have conversations!",
                bg="#1A0A40", fg="white", font=("Segoe UI", 12), wraplength=400).pack(pady=20)
        
        self.llm_enabled_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(self.content_frame, text="✅ Enable AI Features",
                      variable=self.llm_enabled_var, bg="#1A0A40", fg="white",
                      selectcolor="#6C3FCF", font=("Segoe UI", 12, "bold"),
                      command=self._toggle_llm_fields).pack(pady=10)
        
        self.llm_frame = tk.Frame(self.content_frame, bg="#1A0A40")
        self.llm_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Label(self.llm_frame, text="API Key:", bg="#1A0A40", fg="white",
                font=("Segoe UI", 10)).pack(anchor="w")
        
        self.api_key_var = tk.StringVar()
        self.api_entry = tk.Entry(self.llm_frame, textvariable=self.api_key_var,
                                 font=("Segoe UI", 10), show="*",
                                 bg="#2A1050", fg="white", insertbackground="white")
        self.api_entry.pack(fill="x", pady=5)
        
        tk.Label(self.llm_frame, 
                text="💡 Don't have one? Get a free key from:\n   • openai.com (GPT models)\n   • groq.com (Faster, free tier)\n   • Or skip this - you can always add it later!",
                bg="#1A0A40", fg="#B090FF", font=("Segoe UI", 9), justify="left").pack(pady=10)
        
        self._toggle_llm_fields()
    
    def _toggle_llm_fields(self):
        """Show/hide LLM fields."""
        state = "normal" if self.llm_enabled_var.get() else "disabled"
        for widget in self.llm_frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.configure(state=state)
    
    def _next_step(self):
        """Go to next step or finish."""
        if self.current_step == 4:
            self._finish()
        else:
            self._show_step(self.current_step + 1)
    
    def _prev_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)
    
    def _skip(self):
        """Skip wizard with defaults."""
        if messagebox.askyesno("Skip Setup?", "Skip setup and use default settings?\nYou can always change them later in Settings."):
            self.config.set("first_run", False, None)
            self.config.save()
            self._close()
    
    def _finish(self):
        """Finish wizard and save settings."""
        # Save all settings
        if hasattr(self, 'name_var'):
            self.config.set("buddy", "name", self.name_var.get())
        
        if hasattr(self, 'personality_var'):
            self.config.set("buddy", "personality", self.personality_var.get())
        
        # Apply theme colors
        if hasattr(self, 'theme_var'):
            themes = {
                "default": {"hair_primary": "#3A1F6E", "eye_color": "#6040E0", "hair_highlight": "#5B2FC0"},
                "pink": {"hair_primary": "#FF6B9D", "eye_color": "#FF1493", "hair_highlight": "#FFB6C1"},
                "red": {"hair_primary": "#DC143C", "eye_color": "#B22222", "hair_highlight": "#FF6B6B"},
                "blonde": {"hair_primary": "#FFD700", "eye_color": "#32CD32", "hair_highlight": "#FFFACD"},
                "silver": {"hair_primary": "#C0C0C0", "eye_color": "#4682B4", "hair_highlight": "#E8E8E8"},
                "teal": {"hair_primary": "#20B2AA", "eye_color": "#00CED1", "hair_highlight": "#40E0D0"},
            }
            theme = themes.get(self.theme_var.get(), themes["default"])
            self.config.set_multi("appearance", theme)
        
        # LLM settings
        if hasattr(self, 'llm_enabled_var'):
            llm_config = {
                "enabled": self.llm_enabled_var.get(),
                "api_key": self.api_key_var.get() if self.llm_enabled_var.get() else "",
                "api_url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-3.5-turbo",
            }
            self.config.set_multi("llm", llm_config)
        
        # Mark setup as complete
        self.config.set("first_run", False, None)
        self.config.save()
        
        messagebox.showinfo("✨ All Set!", 
                           f"Your buddy {self.config.get('buddy', 'name', 'Miku')} is ready!\n\nRight-click them anytime for Settings!")
        
        self._close()
    
    def _on_close(self):
        """Handle window close."""
        if messagebox.askyesno("Close Setup?", "Are you sure you want to close setup?\nDefault settings will be used."):
            self._close()
    
    def _close(self):
        """Close wizard."""
        if self.on_complete:
            self.on_complete()
        self.window.destroy()
