import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.main_page import MainPage
from ui.chat_page import ChatPage
from ui.history_page import HistoryPage
from ui.settings_page import SettingsPage
from ui.analysis_page import AnalysisPage
from ui.notifications_page import NotificationsPage
from ui.dashboard_page import DashboardPage
from ui.analysis_detail_page import AnalysisDetailPage
from ui.ai_doctor_page import AIDoctorPage
from ui.expert_page import ExpertPage
from ui.splash import SplashScreen
from ui.components import GlassFrame, NavButton, TopBarButton, SearchBar, StatusDot
from modules.sensor_manager import SensorManager
from modules.ai_engine import AIEngine
from modules.database import Database
from modules.web_researcher import WebResearcher
from modules.notification_manager import NotificationManager
from modules.hardware_database import HardwareDatabase
from modules.win_notify import show_toast
import time
import threading
import os
import sys
import winreg
import tkinter as tk

# Patch CTkLabel to silently ignore canvas-deleted TclErrors during page switches
_orig_ctklabel_draw = ctk.CTkLabel._draw
def _safe_ctklabel_draw(self, *a, **kw):
    try:
        _orig_ctklabel_draw(self, *a, **kw)
    except tk.TclError:
        pass
ctk.CTkLabel._draw = _safe_ctklabel_draw


# ─── Navigation labels (translated) ──────────────────────────
NAV_ITEMS = [
    ("main",     "\u2302",      lambda: tr.T("nav.dashboard")),
    ("dashboard", "\U0001F3AF", lambda: tr.T("nav.health")),
    ("analysis", "\U0001D4CA", lambda: tr.T("nav.analysis")),
    ("analysis_detail", "\U0001F50D", lambda: tr.T("nav.detail")),
    ("ai_doctor", "\U0001FA7A", lambda: tr.T("nav.doctor")),
    ("notifications", "\U0001F514", lambda: tr.T("nav.notifications")),
    ("chat",     "\U0001F4AC", lambda: tr.T("nav.chat")),
    ("history",  "\U0001D4C8", lambda: tr.T("nav.history")),
    ("expert",   "\U0001F4CB", lambda: tr.T("nav.expert")),
    ("settings", "\u2699",      lambda: tr.T("nav.settings")),
]


class App(ctk.CTk):
    def __init__(self, start_minimized=False):
        super().__init__()
        
        self._tray_icon = None
        self._tray_thread = None
        self._tray_flashing = False
        self._tray_flash_timer = None
        self._tray_normal_icon = None
        self._tray_alert_icon = None
        self._start_minimized = start_minimized
        
        # Window config
        self.title(Config.APP_NAME)
        self.geometry("1400x860")
        self.minsize(1200, 700)
        
        try:
            if os.name == "nt":
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        
        settings = Config.load_settings()
        tr.load(settings.get("language", "tr"))
        Config.apply_theme(settings.get("theme", "dark"))
        
        self._apply_startup_setting()
        
        # Show splash screen (packs itself)
        self._splash = SplashScreen(self)
        
        # Force window to render the splash immediately
        self.update()
        
        # Run initialization with splash updates
        self._init_with_splash()
    
    def _init_with_splash(self):
        self._splash.set_status(tr.T("splash.status.db"))
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        self.hardware_db = HardwareDatabase(str(Config.HW_DB_PATH))
        if Config.HW_DB_PATH.exists():
            self.hardware_db.load_from_file(str(Config.HW_DB_PATH))
        
        self._splash.set_status(tr.T("splash.status.sensor"))
        self.database = Database(str(Config.DB_PATH))
        
        self.web_researcher = WebResearcher(
            enabled=Config.get("web_research_enabled", True)
        )
        
        self.ai_engine = AIEngine(
            hardware_db=self.hardware_db,
            database=self.database,
            web_researcher=self.web_researcher
        )
        
        self._splash.set_status(tr.T("splash.status.lhm"))
        self.sensor_manager = SensorManager(
            update_interval=Config.get("sensor_update_interval", 2.0)
        )
        
        self.notification_manager = NotificationManager()
        self.notification_manager.add_callback(self._on_notification)
        
        self._splash.set_status(tr.T("splash.status.hwinfo"))
        cpu_name = self.sensor_manager.get_cpu_name()
        gpu_name = self.sensor_manager.get_gpu_name()
        ram_info = self.sensor_manager.get_ram_info()
        
        self.ai_engine.set_hardware_info(cpu_name, gpu_name, ram_info)
        self.ai_engine.update_settings(Config.load_settings())
        
        self.database.save_system_info("cpu_name", cpu_name)
        self.database.save_system_info("gpu_name", gpu_name)
        self.database.save_system_info("ram", ram_info)
        self.database.save_system_info("windows", self.sensor_manager.get_windows_version())
        self.database.save_system_info("bios", self.sensor_manager.get_bios_version())
        self.database.save_system_info("gpu_driver", self.sensor_manager.get_gpu_driver())
        
        self._splash.set_status(tr.T("splash.status.ui"))
        
        # Read initial sensor data synchronously so the UI has data on first render
        self._splash.set_status(tr.T("splash.status.data"))
        initial_data = self.sensor_manager.read_once()
        
        # Remove splash before building UI (pack vs pack conflict otherwise)
        self._splash.destroy()
        self._splash = None
        self._init_ui()
        
        # Populate UI with the initial sensor data immediately
        self._pages["main"].update_sensor_data(initial_data)
        
        self._start_sensors()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._post_init)
    
    def _fade_out_splash(self):
        pass
    
    
    def _init_ui(self):
        self.configure(fg_color=Config.COLOR_BG)
        
        # ─── Main horizontal layout ────────────────────────────
        main_row = ctk.CTkFrame(self, fg_color="transparent")
        main_row.pack(fill="both", expand=True, padx=0, pady=0)
        main_row.grid_columnconfigure(1, weight=1)
        main_row.grid_rowconfigure(1, weight=1)
        
        # ─── Sidebar ───────────────────────────────────────────
        self._sidebar = ctk.CTkFrame(main_row, width=220,
                                     fg_color=Config.COLOR_CARD,
                                     corner_radius=0)
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        self._sidebar.grid_propagate(False)
        sidebar = self._sidebar
        
        # Sidebar inner (with border)
        sidebar_inner = ctk.CTkFrame(sidebar, fg_color="transparent")
        sidebar_inner.pack(fill="both", expand=True, padx=8, pady=12)
        
        # Logo area
        logo_frame = ctk.CTkFrame(sidebar_inner, fg_color="transparent")
        logo_frame.pack(fill="x", padx=8, pady=(4, 28))
        
        # Logo image
        logo_path = str(Config.ASSETS_DIR / "icons" / "logo.png")
        if os.path.exists(logo_path):
            from PIL import Image
            pil_logo = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(160, 45))
            ctk.CTkLabel(logo_frame, image=logo_ctk, text="").pack(anchor="w")
        else:
            ctk.CTkLabel(
                logo_frame, text="ThermixAI",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_XLARGE, "bold"),
                text_color=Config.COLOR_TEXT
            ).pack(anchor="w")
        
        # Version
        ctk.CTkLabel(
            logo_frame, text="v" + Config.APP_VERSION,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(anchor="w")
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar_inner, fg_color="transparent")
        nav_frame.pack(fill="x", padx=4)
        
        self._nav_buttons = {}
        for key, icon, label_fn in NAV_ITEMS:
            is_active = key == "main"
            btn = NavButton(
                nav_frame, text=label_fn(), icon=icon,
                is_active=is_active,
                command=lambda k=key: self._switch_page(k)
            )
            btn.pack(fill="x", pady=2)
            self._nav_buttons[key] = btn
        
        # Spacer
        ctk.CTkFrame(sidebar_inner, fg_color="transparent").pack(fill="both", expand=True)
        
        # Profile area
        profile_frame = ctk.CTkFrame(sidebar_inner, fg_color=Config.COLOR_CARD,
                                     corner_radius=Config.CORNER_RADIUS_SMALL,
                                     border_color=Config.GLASS_BORDER,
                                     border_width=1)
        profile_frame.pack(fill="x", padx=4, pady=(0, 4))
        
        profile_inner = ctk.CTkFrame(profile_frame, fg_color="transparent")
        profile_inner.pack(padx=12, pady=10)
        
        # Avatar
        avatar = ctk.CTkFrame(profile_inner, width=36, height=36,
                              fg_color=Config.COLOR_PRIMARY,
                              corner_radius=10)
        avatar.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(avatar, text="AI",
                     font=(Config.FONT_FAMILY, 12, "bold"),
                     text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")
        
        self._profile_label = ctk.CTkLabel(profile_inner, text=tr.T("profile.label"),
                     font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
                     text_color=Config.COLOR_TEXT)
        self._profile_label.pack(anchor="w")
        self._profile_online = ctk.CTkLabel(profile_inner, text=tr.T("profile.online"),
                     font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
                     text_color=Config.COLOR_ACCENT_GREEN)
        self._profile_online.pack(anchor="w")
        
        # ─── Top Bar ───────────────────────────────────────────
        topbar = ctk.CTkFrame(main_row, height=56,
                              fg_color="transparent")
        topbar.grid(row=0, column=1, sticky="ew", padx=24, pady=(16, 0))
        topbar.grid_columnconfigure(0, weight=0)
        topbar.grid_columnconfigure(2, weight=1)
        
        # Left: Search
        self._search_bar = SearchBar(topbar, width=280)
        self._search_bar.grid(row=0, column=0, sticky="w")
        
        # Right: actions
        actions = ctk.CTkFrame(topbar, fg_color="transparent")
        actions.grid(row=0, column=2, sticky="e")
        
        # Status indicator
        status_frame = ctk.CTkFrame(actions, fg_color="transparent")
        status_frame.pack(side="left", padx=(0, 8))
        self._top_status_dot = StatusDot(status_frame, size=8, color=Config.COLOR_ACCENT_GREEN)
        self._top_status_dot.pack(side="left", padx=(0, 6))
        self._top_status_lbl = ctk.CTkLabel(status_frame, text=tr.T("status.live"),
                     font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                     text_color=Config.COLOR_ACCENT_GREEN)
        self._top_status_lbl.pack(side="left")
        
        # Theme toggle
        TopBarButton(actions, icon="\u263C", command=self._toggle_theme).pack(side="left", padx=2)
        
        # Notifications bell
        notif_btn = TopBarButton(actions, icon="\uD83D\uDD14", command=self._show_notifications,
                                 badge_count=0)
        notif_btn.pack(side="left", padx=2)
        self._notif_btn = notif_btn
        
        # Settings
        TopBarButton(actions, icon="\u2699", command=lambda: self._switch_page("settings")
                     ).pack(side="left", padx=2)
        
        # ─── Pages Container ───────────────────────────────────
        self._pages_container = ctk.CTkFrame(main_row, fg_color="transparent")
        self._pages_container.grid(row=1, column=1, sticky="nsew", padx=24, pady=(8, 16))
        self._pages_container.grid_columnconfigure(0, weight=1)
        self._pages_container.grid_rowconfigure(0, weight=1)
        
        self._pages = {}
        
        self._pages["main"] = MainPage(
            self._pages_container,
            sensor_manager=self.sensor_manager,
            ai_engine=self.ai_engine
        )
        
        self._pages["dashboard"] = DashboardPage(
            self._pages_container,
            ai_engine=self.ai_engine,
            sensor_manager=self.sensor_manager
        )
        
        self._pages["analysis_detail"] = AnalysisDetailPage(
            self._pages_container,
            ai_engine=self.ai_engine,
            sensor_manager=self.sensor_manager
        )
        
        self._pages["ai_doctor"] = AIDoctorPage(
            self._pages_container,
            ai_engine=self.ai_engine,
            sensor_manager=self.sensor_manager
        )
        
        self._pages["expert"] = ExpertPage(
            self._pages_container,
            ai_engine=self.ai_engine,
            sensor_manager=self.sensor_manager
        )
        
        self._pages["chat"] = ChatPage(
            self._pages_container,
            ai_engine=self.ai_engine,
            sensor_manager=self.sensor_manager,
            database=self.database
        )
        
        self._pages["history"] = HistoryPage(
            self._pages_container,
            database=self.database
        )
        
        self._pages["settings"] = SettingsPage(
            self._pages_container,
            config_callback=self._on_settings_changed
        )
        
        self._pages["analysis"] = AnalysisPage(
            self._pages_container,
            sensor_manager=self.sensor_manager,
            ai_engine=self.ai_engine,
            database=self.database
        )
        
        self._pages["notifications"] = NotificationsPage(
            self._pages_container,
            notification_manager=self.notification_manager
        )
        
        self._current_page = "main"
        self._show_page("main")
    
    def _switch_page(self, page_name: str):
        if page_name == self._current_page:
            return
        
        for key, btn in self._nav_buttons.items():
            btn.set_active(key == page_name)
        
        self._show_page(page_name)
        self._current_page = page_name
    
    def _show_page(self, page_name: str):
        for key, page in self._pages.items():
            if key == page_name:
                page.pack(fill="both", expand=True)
            else:
                page.pack_forget()
    
    def _toggle_theme(self):
        current = Config._theme
        new = "light" if current == "dark" else "dark"
        Config.apply_theme(new)
        settings = Config.load_settings()
        settings["theme"] = new
        Config.save_settings(settings)
        self._refresh_ui_theme()
        self._refresh_ui_lang()
        self.after(200, self._restart_app)

    def _restart_app(self):
        try:
            # Release the single-instance mutex so the new process can start
            if Config._mutex_handle:
                import ctypes
                ctypes.windll.kernel32.CloseHandle(Config._mutex_handle)
                Config._mutex_handle = None
            import sys
            import subprocess
            subprocess.Popen([sys.executable, *sys.argv])
            self.after(100, self._do_exit)
        except Exception as e:
            print(f"[App] Restart failed: {e}")

    def _do_exit(self):
        if Config._mutex_handle:
            import ctypes
            ctypes.windll.kernel32.CloseHandle(Config._mutex_handle)
            Config._mutex_handle = None
        self.destroy()
        import sys
        sys.exit(0)
    
    def _refresh_ui_lang(self):
        try:
            for key, btn in self._nav_buttons.items():
                for k, icon, label_fn in NAV_ITEMS:
                    if k == key:
                        btn.configure(text=label_fn())
                        break
            if self._current_page in self._pages:
                page = self._pages[self._current_page]
                if hasattr(page, 'refresh_lang'):
                    page.refresh_lang()
            self._profile_label.configure(text=tr.T("profile.label"))
            self._profile_online.configure(text=tr.T("profile.online"))
            self._top_status_lbl.configure(text=tr.T("status.live"))
        except Exception:
            pass

    def _refresh_ui_theme(self):
        try:
            self.configure(fg_color=Config.COLOR_BG)
            if hasattr(self, '_sidebar'):
                self._sidebar.configure(fg_color=Config.COLOR_CARD)
            for btn in self._nav_buttons.values():
                if hasattr(btn, 'refresh_theme'):
                    btn.refresh_theme()
            if self._current_page in self._pages:
                page = self._pages[self._current_page]
                page.configure(fg_color=Config.COLOR_BG)
                if hasattr(page, 'refresh_theme'):
                    page.refresh_theme()
        except Exception:
            pass
    
    def _show_notifications(self):
        self._switch_page("notifications")
    
    def _on_notification(self, notification):
        """Called when any new notification is created — update badge and refresh page."""
        try:
            self._notif_btn.update_badge(self.notification_manager.get_unread_count())
            if self._current_page == "notifications":
                self._pages["notifications"].refresh()
        except Exception:
            pass
        
        # Windows toast + tray flash when window is hidden
        try:
            if not self.winfo_viewable():
                show_toast(notification.title, notification.message)
                self._start_tray_flash()
        except Exception:
            pass
    
    def _start_sensors(self):
        self.sensor_manager.add_callback(self._on_sensor_data)
        self.sensor_manager.add_gaming_callback(self._on_gaming_event)
        self.sensor_manager.start()
        
        self._sensor_save_count = 0
        self._save_interval = Config.get("save_history", True)
    
    def _on_gaming_event(self, active: bool, report: dict = None):
        try:
            self._pages["analysis"].update_gaming_status(active, report)
            self.ai_engine.gaming_mode = active
            if active:
                game = self.sensor_manager._current_game_process if self.sensor_manager else ""
                if game and hasattr(self.ai_engine, 'timeline'):
                    self.ai_engine.timeline.add_sensor_event(
                        "game_start", tr.T("timeline.game_start", game=game), 
                        tr.T("game.monitoring", game=game), "\uD83C\uDFAE")
                
                title = tr.T("game.started")
                msg = tr.T("game.monitoring", game=game) if game else tr.T("game.unknown")
                self.notification_manager.notify(title, msg, "info", "Gaming")
            elif report:
                self.database.save_system_info("last_gaming_report", str(report))
                game_name = report.get("game_name", "")
                dur = report.get("duration", 0)
                dur_str = f"{int(dur//60)}dk {int(dur%60)}sn" if dur < 3600 else f"{dur/3600:.1f}s"
                
                if game_name and hasattr(self.ai_engine, 'timeline'):
                    gpu_max = report.get('gpu_temp_max', 0)
                    self.ai_engine.timeline.add_sensor_event(
                        "game_end", tr.T("timeline.game_end", game=game_name),
                        tr.T("game.duration", duration=dur_str, temp=gpu_max), "\u23F9")
                
                self._pages["analysis_detail"].refresh()
                title = tr.T("game.ended")
                cpu_mx = report.get('cpu_temp_max', 0)
                gpu_mx = report.get('gpu_temp_max', 0)
                msg = tr.T("game.report_line", game=game_name, duration=dur_str, cpu=cpu_mx, gpu=gpu_mx) if game_name else tr.T("game.session_ended", duration=dur_str)
                self.notification_manager.notify(title, msg, "info", "Gaming")
                report_text = self.ai_engine._format_gaming_report(report)
                if report_text:
                    self.database.save_chat_message("assistant", report_text)
                if game_name:
                    threading.Thread(target=self._enrich_gaming_report, args=(report,), daemon=True).start()
            unread = self.notification_manager.get_unread_count()
            self._notif_btn.update_badge(unread)
        except Exception:
            pass
    
    def _enrich_gaming_report(self, report: dict):
        try:
            enhanced = self.ai_engine._generate_enhanced_gaming_report(report)
            if enhanced:
                self.after(0, lambda: self.database.save_chat_message("assistant", enhanced))
        except Exception:
            pass
    
    def _on_sensor_data(self, data):
        try:
            self._pages["main"].update_sensor_data(data)
        except Exception as e:
            print(f"[SENSOR UPDATE ERROR] {e}")
        
        try:
            self._pages["dashboard"].update_sensor_data(data)
        except Exception:
            pass
        
        try:
            self._pages["analysis_detail"].update_sensor_data(data)
        except Exception:
            pass
        
        try:
            self._pages["expert"].update_sensor_data(data)
        except Exception:
            pass
        
        try:
            if self._sensor_save_count % 10 == 0:
                self._pages["analysis"].refresh()
        except Exception:
            pass
        
        self._sensor_save_count += 1
        if self._save_interval and self._sensor_save_count % 60 == 0:
            try:
                simple = data.to_simple_dict()
                simple["_workload"] = self.sensor_manager._heavy_workload_type if hasattr(self.sensor_manager, '_heavy_workload_type') else ""
                self.database.save_sensor_data(simple)
                self.ai_engine.add_sensor_data(simple)
                
                full = data.to_dict()
                full["_workload"] = simple["_workload"]
                results = self.ai_engine.analyze(full)
                for result in results:
                    if result.severity in ("danger", "warning"):
                        self.notification_manager.notify(
                            result.summary, result.details,
                            result.severity, result.component
                        )
                        self.database.save_analysis({
                            "component": result.component,
                            "status": result.status,
                            "severity": result.severity,
                            "summary": result.summary,
                            "details": result.details,
                            "suggestions": result.suggestions,
                            "timestamp": result.timestamp
                        })
                
                self._check_notification_thresholds(data)
            except Exception as e:
                print(f"[ANALYSIS ERROR] {e}")
        
        try:
            if self._sensor_save_count % 30 == 0:
                notifs = self.notification_manager.get_recent(5)
                self._pages["main"].update_notifications(notifs)
                # Update badge
                unread = self.notification_manager.get_unread_count()
                self._notif_btn.update_badge(unread)
                # Stop tray flash if no more unread
                if unread == 0 and self._tray_flashing:
                    self._stop_tray_flash()
                # Refresh notifications page if it's visible
                if self._current_page == "notifications":
                    self._pages["notifications"].refresh()
        except Exception:
            pass
    
    def _check_notification_thresholds(self, data):
        thresholds = {
            "cpu_threshold": Config.get("notification_cpu_threshold", 85),
            "gpu_threshold": Config.get("notification_gpu_threshold", 85),
            "hotspot_threshold": Config.get("notification_hotspot_threshold", 100),
            "vram_threshold": Config.get("notification_vram_threshold", 90),
            "ssd_threshold": Config.get("notification_ssd_threshold", 60),
        }
        
        if Config.get("notification_enabled", True):
            self.notification_manager.check_and_notify(
                data.to_dict(), thresholds
            )
    
    def _on_settings_changed(self, settings: dict):
        self.ai_engine.update_settings(settings)
        self.web_researcher.set_enabled(settings.get("web_research_enabled", True))
        self.sensor_manager.update_interval = settings.get("sensor_update_interval", 2.0)
        self._apply_startup_setting()
        self._refresh_ui_theme()
        self._refresh_ui_lang()
        if not settings.get("minimize_to_tray", True) and self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None
        elif settings.get("minimize_to_tray", True) and not self._tray_icon:
            self.after(500, self._init_tray)
    
    def _apply_startup_setting(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            )
            enable = Config.get("start_with_windows", False)
            app_name = "ThermixAI"
            if enable:
                script = os.path.abspath(sys.argv[0]) if sys.argv else __file__
                if script.endswith(".py"):
                    value = f'"{sys.executable}" "{script}"'
                else:
                    value = f'"{script}"'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, value)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass
    
    def iconify(self):
        if Config.get("minimize_to_tray", True):
            self._hide_window()
        else:
            super().iconify()
    
    def _init_tray(self):
        if not Config.get("minimize_to_tray", True):
            return
        try:
            self._create_tray_icon()
        except Exception:
            pass
    
    def _create_tray_icon(self):
        from PIL import Image
        
        icon_size = 64
        logo_path = str(Config.ASSETS_DIR / "icons" / "logo.png")
        if os.path.exists(logo_path):
            self._tray_normal_icon = Image.open(logo_path).resize((icon_size, icon_size), Image.LANCZOS)
            # Create alert version with yellow tint overlay
            alert = self._tray_normal_icon.copy().convert("RGBA")
            overlay = Image.new("RGBA", alert.size, (255, 200, 50, 100))
            alert.alpha_composite(overlay)
            self._tray_alert_icon = alert
        else:
            # Fallback to text icon
            from PIL import ImageDraw
            self._tray_normal_icon = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(self._tray_normal_icon)
            draw.rounded_rectangle(
                [4, 4, icon_size - 4, icon_size - 4],
                radius=12, fill=(124, 92, 255, 230)
            )
            draw.text((8, 14), "TX", fill=(255, 255, 255, 255))
            self._tray_alert_icon = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(self._tray_alert_icon)
            draw.rounded_rectangle(
                [4, 4, icon_size - 4, icon_size - 4],
                radius=12, fill=(255, 200, 50, 240)
            )
            draw.text((8, 14), "TX", fill=(255, 255, 255, 255))
        
        import pystray
        
        def on_show(icon, item):
            self._show_window()
        
        def on_quit(icon, item):
            self._tray_icon = None
            self._real_close()
        
        menu = (
            pystray.MenuItem(tr.T("tray.show"), on_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(tr.T("tray.quit"), on_quit),
        )
        
        self._tray_icon = pystray.Icon(
            "ThermixAI", self._tray_normal_icon,
            f"{Config.APP_NAME} v{Config.APP_VERSION}",
            menu
        )
        self._tray_thread = threading.Thread(
            target=self._tray_icon.run, daemon=True
        )
        self._tray_thread.start()
    
    def _start_tray_flash(self):
        if self._tray_flashing or not self._tray_icon:
            return
        self._tray_flashing = True
        self._tray_flash_timer = threading.Timer(0.0, self._tray_flash_loop)
        self._tray_flash_timer.daemon = True
        self._tray_flash_timer.start()
    
    def _stop_tray_flash(self):
        self._tray_flashing = False
        if self._tray_flash_timer:
            self._tray_flash_timer.cancel()
            self._tray_flash_timer = None
        if self._tray_icon and self._tray_normal_icon:
            try:
                self._tray_icon.icon = self._tray_normal_icon
            except Exception:
                pass
    
    def _tray_flash_loop(self):
        use_alert = False
        while self._tray_flashing and self._tray_icon:
            try:
                self._tray_icon.icon = self._tray_alert_icon if use_alert else self._tray_normal_icon
                use_alert = not use_alert
                time.sleep(0.8)
            except Exception:
                break
    
    def _show_window(self):
        self._stop_tray_flash()
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def _hide_window(self):
        self.withdraw()
        if self._tray_icon:
            try:
                show_toast(Config.APP_NAME, tr.T("tray.toast"))
            except Exception:
                pass
    
    def _post_init(self):
        self._show_page("main")
        self.after(500, self._init_tray)
        if self._start_minimized and Config.get("minimize_to_tray", True):
            self.after(100, self._hide_window)
    
    def _on_close(self):
        minimize = Config.get("minimize_to_tray", True)
        if minimize and self._tray_icon is not None:
            self._hide_window()
        else:
            self._real_close()
    
    def _real_close(self):
        self._stop_tray_flash()
        try:
            self.sensor_manager.stop()
            self.database.save_system_info("last_shutdown", str(time.time()))
            self.database.close()
            self.hardware_db.save_to_file(str(Config.HW_DB_PATH))
            if self._tray_icon:
                self._tray_icon.stop()
        except Exception:
            pass
        self.destroy()
    
    def run(self):
        self.mainloop()
