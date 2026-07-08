import os
import json
from pathlib import Path

class Config:
    APP_NAME = "ThermixAI"
    APP_VERSION = "1.0.0"
    AUTHOR = "AI Hardware Assistant Team"
    
    # Single-instance mutex handle (set by main.py)
    _mutex_handle = None
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    ASSETS_DIR = BASE_DIR / "assets"
    ICONS_DIR = ASSETS_DIR / "icons"
    
    DB_PATH = DATA_DIR / "history.db"
    HW_DB_PATH = DATA_DIR / "hardware_db.json"
    SETTINGS_PATH = DATA_DIR / "settings.json"
    LOG_PATH = LOGS_DIR / "app.log"
    
    UPDATE_INTERVAL_MS = 1000
    SENSOR_UPDATE_INTERVAL = 1.0
    DB_SAVE_INTERVAL = 60
    CHART_UPDATE_INTERVAL = 5
    
    THEME = "dark"
    _theme = "dark"
    
    # -- Dark Theme colors (default) --
    DARK_COLORS = {
        "COLOR_PRIMARY": "#7C5CFF",
        "COLOR_PRIMARY_LIGHT": "#A78BFA",
        "COLOR_PRIMARY_DARK": "#5B3DC7",
        "COLOR_SECONDARY": "#3B82F6",
        "COLOR_BG": "#0E1117",
        "COLOR_BG_LIGHT": "#F5F7FB",
        "COLOR_CARD": "#181C24",
        "COLOR_CARD_HOVER": "#1F2430",
        "COLOR_CARD_LIGHT": "#FFFFFF",
        "COLOR_TEXT": "#FFFFFF",
        "COLOR_TEXT_PRIMARY": "#F1F5F9",
        "COLOR_TEXT_SECONDARY": "#94A3B8",
        "COLOR_TEXT_TERTIARY": "#64748B",
        "COLOR_ACCENT_GREEN": "#22C55E",
        "COLOR_ACCENT_RED": "#EF4444",
        "COLOR_ACCENT_ORANGE": "#F59E0B",
        "COLOR_ACCENT_YELLOW": "#EAB308",
        "COLOR_ACCENT_BLUE": "#3B82F6",
        "COLOR_ACCENT_PURPLE": "#7C5CFF",
        "COLOR_ACCENT_CYAN": "#06B6D4",
        "COLOR_ACCENT_PINK": "#EC4899",
        "COLOR_MICA": "#161A21",
        "COLOR_BORDER": "#2A2E3A",
        "COLOR_BORDER_LIGHT": "#E2E8F0",
        "COLOR_GRADIENT_START": "#7C5CFF",
        "COLOR_GRADIENT_END": "#3B82F6",
        "GLASS_ALPHA": "#161A21",
        "GLASS_BORDER": "#1A1D23",
    }
    
    # -- Light Theme colors --
    LIGHT_COLORS = {
        "COLOR_PRIMARY": "#7C5CFF",
        "COLOR_PRIMARY_LIGHT": "#A78BFA",
        "COLOR_PRIMARY_DARK": "#5B3DC7",
        "COLOR_SECONDARY": "#3B82F6",
        "COLOR_BG": "#F5F7FB",
        "COLOR_BG_LIGHT": "#F5F7FB",
        "COLOR_CARD": "#FFFFFF",
        "COLOR_CARD_HOVER": "#F1F5F9",
        "COLOR_CARD_LIGHT": "#FFFFFF",
        "COLOR_TEXT": "#0F172A",
        "COLOR_TEXT_PRIMARY": "#1E293B",
        "COLOR_TEXT_SECONDARY": "#64748B",
        "COLOR_TEXT_TERTIARY": "#94A3B8",
        "COLOR_ACCENT_GREEN": "#16A34A",
        "COLOR_ACCENT_RED": "#DC2626",
        "COLOR_ACCENT_ORANGE": "#D97706",
        "COLOR_ACCENT_YELLOW": "#CA8A04",
        "COLOR_ACCENT_BLUE": "#2563EB",
        "COLOR_ACCENT_PURPLE": "#7C5CFF",
        "COLOR_ACCENT_CYAN": "#0891B2",
        "COLOR_ACCENT_PINK": "#DB2777",
        "COLOR_MICA": "#FFFFFF",
        "COLOR_BORDER": "#E2E8F0",
        "COLOR_BORDER_LIGHT": "#CBD5E1",
        "COLOR_GRADIENT_START": "#7C5CFF",
        "COLOR_GRADIENT_END": "#3B82F6",
        "GLASS_ALPHA": "#FFFFFF",
        "GLASS_BORDER": "#E2E8F0",
    }
    
    COLOR_PRIMARY = DARK_COLORS["COLOR_PRIMARY"]
    COLOR_PRIMARY_LIGHT = DARK_COLORS["COLOR_PRIMARY_LIGHT"]
    COLOR_PRIMARY_DARK = DARK_COLORS["COLOR_PRIMARY_DARK"]
    COLOR_SECONDARY = DARK_COLORS["COLOR_SECONDARY"]
    COLOR_BG = DARK_COLORS["COLOR_BG"]
    COLOR_BG_LIGHT = DARK_COLORS["COLOR_BG_LIGHT"]
    COLOR_CARD = DARK_COLORS["COLOR_CARD"]
    COLOR_CARD_HOVER = DARK_COLORS["COLOR_CARD_HOVER"]
    COLOR_CARD_LIGHT = DARK_COLORS["COLOR_CARD_LIGHT"]
    COLOR_TEXT = DARK_COLORS["COLOR_TEXT"]
    COLOR_TEXT_PRIMARY = DARK_COLORS["COLOR_TEXT_PRIMARY"]
    COLOR_TEXT_SECONDARY = DARK_COLORS["COLOR_TEXT_SECONDARY"]
    COLOR_TEXT_TERTIARY = DARK_COLORS["COLOR_TEXT_TERTIARY"]
    COLOR_ACCENT_GREEN = DARK_COLORS["COLOR_ACCENT_GREEN"]
    COLOR_ACCENT_RED = DARK_COLORS["COLOR_ACCENT_RED"]
    COLOR_ACCENT_ORANGE = DARK_COLORS["COLOR_ACCENT_ORANGE"]
    COLOR_ACCENT_YELLOW = DARK_COLORS["COLOR_ACCENT_YELLOW"]
    COLOR_ACCENT_BLUE = DARK_COLORS["COLOR_ACCENT_BLUE"]
    COLOR_ACCENT_PURPLE = DARK_COLORS["COLOR_ACCENT_PURPLE"]
    COLOR_ACCENT_CYAN = DARK_COLORS["COLOR_ACCENT_CYAN"]
    COLOR_ACCENT_PINK = DARK_COLORS["COLOR_ACCENT_PINK"]
    COLOR_MICA = DARK_COLORS["COLOR_MICA"]
    COLOR_BORDER = DARK_COLORS["COLOR_BORDER"]
    COLOR_BORDER_LIGHT = DARK_COLORS["COLOR_BORDER_LIGHT"]
    COLOR_GRADIENT_START = DARK_COLORS["COLOR_GRADIENT_START"]
    COLOR_GRADIENT_END = DARK_COLORS["COLOR_GRADIENT_END"]
    GLASS_ALPHA = DARK_COLORS["GLASS_ALPHA"]
    GLASS_BORDER = DARK_COLORS["GLASS_BORDER"]
    
    GLASS_BLUR = 20
    
    FONT_FAMILY = "Segoe UI Variable"
    FONT_SIZE_TINY = 10
    FONT_SIZE_SMALL = 12
    FONT_SIZE_NORMAL = 13
    FONT_SIZE_MEDIUM = 15
    FONT_SIZE_LARGE = 18
    FONT_SIZE_XLARGE = 24
    FONT_SIZE_XXLARGE = 32
    FONT_SIZE_HERO = 48
    
    ANIMATION_DURATION = 250
    ANIMATION_DURATION_SLOW = 400
    CORNER_RADIUS = 16
    CORNER_RADIUS_SMALL = 10
    CORNER_RADIUS_LARGE = 24
    
    TRANSPARENCY_ALPHA = 0.85
    SHADOW_OFFSET = 4
    
    SETTINGS_DEFAULTS = {
        "language": "tr",
        "theme": "dark",
        "start_with_windows": False,
        "minimize_to_tray": True,
        "notification_enabled": True,
        "notification_cpu_threshold": 85,
        "notification_gpu_threshold": 85,
        "notification_hotspot_threshold": 100,
        "notification_vram_threshold": 90,
        "notification_ssd_threshold": 60,
        "sensor_update_interval": 1.0,
        "ai_auto_analyze": True,
        "web_research_enabled": True,
        "save_history": True,
        "history_retention_days": 365,
        "room_temp_enabled": False,
        "room_temp_value": 25.0,
        "gpu_install_date": "",
        "cpu_install_date": "",
        "last_clean_date": "",
        "last_paste_date": "",
    }
    
    _settings = None
    
    @classmethod
    def load_settings(cls):
        if cls._settings is not None:
            return cls._settings
        cls._settings = cls.SETTINGS_DEFAULTS.copy()
        if cls.SETTINGS_PATH.exists():
            try:
                with open(cls.SETTINGS_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    cls._settings.update(saved)
            except Exception:
                pass
        return cls._settings
    
    @classmethod
    def save_settings(cls, settings=None):
        if settings:
            cls._settings = settings
        if cls._settings:
            cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(cls.SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(cls._settings, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def get(cls, key, default=None):
        s = cls.load_settings()
        return s.get(key, default)
    
    @classmethod
    def apply_theme(cls, theme="dark"):
        cls._theme = theme
        import customtkinter as ctk
        scheme = cls.LIGHT_COLORS if theme == "light" else cls.DARK_COLORS
        for key, value in scheme.items():
            setattr(cls, key, value)
        ctk.set_appearance_mode("Light" if theme == "light" else "Dark")
