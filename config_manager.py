"""
Configuration Manager for Anime Buddy
Handles user profiles, settings persistence, and customization
"""
import json
import os
from pathlib import Path

class ConfigManager:
    """Manages user configuration and profiles."""
    
    APP_NAME = "AnimeBuddy"
    CONFIG_DIR = Path.home() / ".animebuddy"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    PROFILES_DIR = CONFIG_DIR / "profiles"
    
    # Default configuration template
    DEFAULTS = {
        "buddy": {
            "name": "Miku",
            "title": "Desktop Companion",
            "personality": "cheerful",
            "speech_style": "casual",
            "talk_frequency": "normal",
            "energy_level": "normal",
        },
        "appearance": {
            "skin": "#FFD5B8",
            "hair_primary": "#3A1F6E",
            "hair_highlight": "#5B2FC0",
            "eye_color": "#6040E0",
            "shirt": "#6C8EEF",
            "skirt": "#3A54C0",
            "ribbon": "#EF6CAA",
            "blush": "#FFB3B3",
            "hair_style": "long",  # long, short, twintails
            "outfit": "school_uniform",  # school_uniform, casual, maid, fantasy
        },
        "behavior": {
            "walk_speed": 2.5,
            "idle_chance": 0.3,
            "use_emojis": True,
            "human_behaviors": True,
            "remember_history": True,
        },
        "llm": {
            "enabled": False,
            "api_key": "",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-3.5-turbo",
        },
        "window": {
            "start_position": "bottom_right",
            "always_on_top": True,
            "opacity": 1.0,
        },
        "first_run": True,
    }
    
    PERSONALITIES = [
        ("cheerful", "Cheerful & Bubbly", "Always happy and optimistic"),
        ("tsundere", "Tsundere", "Acts tough but secretly cares"),
        ("shy", "Shy & Gentle", "Quiet and easily flustered"),
        ("genki", "Genki (Hyper)", "Extremely energetic and loud"),
        ("mysterious", "Mysterious", "Wise and cryptic"),
        ("royal", "Royal/Princess", "Elegant and demanding"),
        ("yandere", "Yandere", "Intensely attached"),
    ]
    
    SPEECH_STYLES = [
        ("casual", "Casual", "Normal everyday speech"),
        ("formal", "Formal", "Polite and proper"),
        ("cute", "Cute (Uwu)", "Wike dis~ owo"),
        ("childish", "Childish", "Simple and innocent"),
    ]
    
    ENERGY_LEVELS = [
        ("low", "Low", "Slow and relaxed"),
        ("normal", "Normal", "Balanced pace"),
        ("hyper", "Hyper", "Fast and energetic"),
    ]
    
    TALK_FREQUENCIES = [
        ("quiet", "Quiet", "Rarely speaks"),
        ("normal", "Normal", "Occasional comments"),
        ("chatty", "Chatty", "Talks often"),
    ]
    
    def __init__(self):
        self.config = {}
        self._ensure_dirs()
        self.load()
    
    def _ensure_dirs(self):
        """Create config directories if they don't exist."""
        self.CONFIG_DIR.mkdir(exist_ok=True)
        self.PROFILES_DIR.mkdir(exist_ok=True)
    
    def load(self):
        """Load configuration from file or create defaults."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.config = self._merge_with_defaults(loaded)
            except Exception:
                self.config = self.DEFAULTS.copy()
        else:
            self.config = self.DEFAULTS.copy()
            self.save()
    
    def _merge_with_defaults(self, loaded):
        """Recursively merge loaded config with defaults."""
        result = self.DEFAULTS.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        return result
    
    def save(self):
        """Save current configuration to file."""
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, section, key=None, default=None):
        """Get configuration value."""
        if key is None:
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def set_multi(self, section, values_dict):
        """Set multiple values in a section."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section].update(values_dict)
    
    def save_profile(self, profile_name):
        """Save current config as a named profile."""
        profile_path = self.PROFILES_DIR / f"{profile_name}.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def load_profile(self, profile_name):
        """Load a named profile."""
        profile_path = self.PROFILES_DIR / f"{profile_name}.json"
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.save()
            return True
        return False
    
    def list_profiles(self):
        """List available profiles."""
        profiles = []
        if self.PROFILES_DIR.exists():
            for f in self.PROFILES_DIR.glob("*.json"):
                profiles.append(f.stem)
        return profiles
    
    def delete_profile(self, profile_name):
        """Delete a profile."""
        profile_path = self.PROFILES_DIR / f"{profile_name}.json"
        if profile_path.exists():
            profile_path.unlink()
            return True
        return False
    
    def export_config(self, filepath):
        """Export config to a file for sharing."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def import_config(self, filepath):
        """Import config from a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.save()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.config = self.DEFAULTS.copy()
        self.save()
    
    def apply_to_buddy(self, buddy_instance):
        """Apply current config to a buddy instance."""
        # Apply name and title
        buddy_instance.config.NAME = self.get("buddy", "name", "Miku")
        buddy_instance.config.TITLE = self.get("buddy", "title", "Desktop Companion")
        
        # Apply personality
        buddy_instance.config.PERSONALITY = self.get("buddy", "personality", "cheerful")
        buddy_instance.personality = BuddyPersonality(buddy_instance.config.PERSONALITY)
        
        # Apply speech style
        buddy_instance.config.SPEECH_STYLE = self.get("buddy", "speech_style", "casual")
        
        # Apply behavior settings
        buddy_instance.config.TALK_FREQUENCY = self.get("buddy", "talk_frequency", "normal")
        buddy_instance.config.ENERGY_LEVEL = self.get("buddy", "energy_level", "normal")
        buddy_instance.config.WALK_SPEED = self.get("behavior", "walk_speed", 2.5)
        buddy_instance.config.USE_EMOJIS = self.get("behavior", "use_emojis", True)
        
        # Apply colors
        colors = self.get("appearance", default={})
        buddy_instance.config.COLORS.update(colors)
        buddy_instance._apply_custom_colors()
        
        # Apply LLM settings
        global OPENAI_API_KEY, OPENAI_API_URL, OPENAI_MODEL
        llm_config = self.get("llm", default={})
        OPENAI_API_KEY = llm_config.get("api_key", "")
        OPENAI_API_URL = llm_config.get("api_url", "https://api.openai.com/v1/chat/completions")
        OPENAI_MODEL = llm_config.get("model", "gpt-3.5-turbo")


# Make BuddyPersonality available for import
from anime_buddy import BuddyPersonality, BuddyConfig
