import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame, SectionDivider


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, config_callback=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.config_callback = config_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        self._build_content()
        self._load_settings()
    
    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=32, pady=(24, 8), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame, text="\u2699\uFE0F",
            font=("Segoe UI", 28)
        ).pack(side="left", padx=(0, 12))
        
        self._title_label = ctk.CTkLabel(
            header_frame, text=tr.T("settings.title"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_XLARGE, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._title_label.pack(side="left")
    
    def _build_content(self):
        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Config.COLOR_CARD,
            scrollbar_button_hover_color=Config.COLOR_CARD_HOVER
        )
        container.grid(row=1, column=0, padx=32, pady=8, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        self._widgets = {}
        row = 0
        
        # Language & Theme Settings
        SectionDivider(container, title=tr.T("settings.language") + " / " + tr.T("settings.theme")).grid(
            row=row, column=0, padx=4, pady=(0, 12), sticky="ew")
        row += 1
        
        lang_frame = GlassFrame(container)
        lang_frame.grid(row=row, column=0, padx=4, pady=(0, 20), sticky="ew")
        lang_frame.grid_columnconfigure(1, weight=1)
        row += 1
        self._add_language_selector(lang_frame, 0)
        self._add_theme_selector(lang_frame, 1)
        
        # Notification Settings
        SectionDivider(container, title=tr.T("settings.notifications")).grid(
            row=row, column=0, padx=4, pady=(12, 12), sticky="ew")
        row += 1
        
        notif_frame = GlassFrame(container)
        notif_frame.grid(row=row, column=0, padx=4, pady=(0, 20), sticky="ew")
        notif_frame.grid_columnconfigure(1, weight=1)
        row += 1
        
        self._add_switch(notif_frame, tr.T("settings.notif_enable"), "notification_enabled", 0)
        self._add_slider(notif_frame, tr.T("settings.cpu_threshold"), "notification_cpu_threshold", 50, 100, 1)
        self._add_slider(notif_frame, tr.T("settings.gpu_threshold"), "notification_gpu_threshold", 50, 100, 2)
        self._add_slider(notif_frame, tr.T("settings.hotspot_threshold"), "notification_hotspot_threshold", 80, 110, 3)
        self._add_slider(notif_frame, tr.T("settings.ssd_threshold"), "notification_ssd_threshold", 40, 80, 4)
        
        # AI Settings
        SectionDivider(container, title=tr.T("settings.ai")).grid(
            row=row, column=0, padx=4, pady=(12, 12), sticky="ew")
        row += 1
        
        ai_frame = GlassFrame(container)
        ai_frame.grid(row=row, column=0, padx=4, pady=(0, 20), sticky="ew")
        ai_frame.grid_columnconfigure(1, weight=1)
        row += 1
        
        self._add_switch(ai_frame, tr.T("settings.auto_ai"), "ai_auto_analyze", 0)
        self._add_switch(ai_frame, tr.T("settings.web_research"), "web_research_enabled", 1)
        
        # Data Settings
        SectionDivider(container, title=tr.T("settings.data")).grid(
            row=row, column=0, padx=4, pady=(12, 12), sticky="ew")
        row += 1
        
        data_frame = GlassFrame(container)
        data_frame.grid(row=row, column=0, padx=4, pady=(0, 20), sticky="ew")
        data_frame.grid_columnconfigure(1, weight=1)
        row += 1
        
        self._add_switch(data_frame, tr.T("settings.save_history"), "save_history", 0)
        self._add_slider(data_frame, tr.T("settings.history_days"), "history_retention_days", 1, 365, 1)
        
        # System Settings
        SectionDivider(container, title=tr.T("settings.system")).grid(
            row=row, column=0, padx=4, pady=(12, 12), sticky="ew")
        row += 1
        
        sys_frame = GlassFrame(container)
        sys_frame.grid(row=row, column=0, padx=4, pady=(0, 20), sticky="ew")
        sys_frame.grid_columnconfigure(1, weight=1)
        row += 1
        
        self._add_switch(sys_frame, tr.T("settings.startup"), "start_with_windows", 0)
        self._add_switch(sys_frame, tr.T("settings.tray"), "minimize_to_tray", 1)
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=row, column=0, padx=4, pady=(16, 8), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            btn_frame,
            text=tr.T("settings.save"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            fg_color=Config.COLOR_PRIMARY,
            hover_color=Config.COLOR_PRIMARY_DARK,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            height=40,
            command=self._save_settings
        ).grid(row=0, column=0, padx=4, pady=8, sticky="ew")
        
        ctk.CTkButton(
            btn_frame,
            text=tr.T("settings.reset"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            fg_color="transparent",
            hover_color=Config.COLOR_CARD_HOVER,
            text_color=Config.COLOR_TEXT_SECONDARY,
            border_color=Config.GLASS_BORDER,
            border_width=1,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            height=40,
            command=self._reset_settings
        ).grid(row=0, column=1, padx=4, pady=8, sticky="ew")
        row += 1
        
        # About
        about_frame = GlassFrame(container)
        about_frame.grid(row=row, column=0, padx=4, pady=(8, 24), sticky="ew")
        
        inner = ctk.CTkFrame(about_frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)
        
        ctk.CTkLabel(
            inner,
            text=f"{Config.APP_NAME} v{Config.APP_VERSION}",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            text_color=Config.COLOR_TEXT
        ).pack()
        
        ctk.CTkLabel(
            inner,
            text=tr.T("settings.about", name=Config.APP_NAME, version=Config.APP_VERSION),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(pady=(4, 0))
    
    def _add_switch(self, parent, label, key, row):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, padx=16, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame, text=label,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT
        ).pack(side="left")
        
        var = ctk.BooleanVar()
        ctk.CTkSwitch(
            frame, text="", variable=var,
            onvalue=True, offvalue=False,
            progress_color=Config.COLOR_PRIMARY,
            button_color=Config.COLOR_TEXT,
            button_hover_color=Config.COLOR_TEXT_SECONDARY
        ).pack(side="right")
        
        self._widgets[key] = var
    
    def _add_slider(self, parent, label, key, min_val, max_val, row):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, padx=16, pady=6, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame, text=label,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT
        ).grid(row=0, column=0, sticky="w")
        
        var = ctk.DoubleVar()
        value_label = ctk.CTkLabel(
            frame, text=f"{int((min_val + max_val) / 2)}",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_TERTIARY, width=36
        )
        value_label.grid(row=0, column=2, padx=(8, 0))
        
        ctk.CTkSlider(
            frame, from_=min_val, to=max_val,
            variable=var,
            fg_color=Config.COLOR_CARD,
            progress_color=Config.COLOR_PRIMARY,
            button_color=Config.COLOR_PRIMARY,
            button_hover_color=Config.COLOR_PRIMARY_DARK,
            command=lambda v, vl=value_label: vl.configure(text=f"{int(v)}")
        ).grid(row=0, column=1, padx=(8, 4), sticky="ew")
        
        self._widgets[key] = var
    
    def _add_language_selector(self, parent, row):
        from modules.translator import tr
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, padx=16, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame, text=tr.T("settings.language"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT
        ).pack(side="left")
        
        self._lang_var = ctk.StringVar(value=Config.get("language", "tr"))
        lang_menu = ctk.CTkOptionMenu(
            frame, variable=self._lang_var,
            values=["tr", "en"],
            fg_color=Config.COLOR_CARD,
            button_color=Config.COLOR_PRIMARY,
            button_hover_color=Config.COLOR_PRIMARY_DARK,
            dropdown_fg_color=Config.COLOR_CARD,
            dropdown_hover_color=Config.COLOR_CARD_HOVER,
            dropdown_text_color=Config.COLOR_TEXT,
            text_color=Config.COLOR_TEXT
        )
        lang_menu.pack(side="right")
    
    def _add_theme_selector(self, parent, row):
        from modules.translator import tr
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, padx=16, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame, text=tr.T("settings.theme"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT
        ).pack(side="left")
        
        self._theme_var = ctk.StringVar(value=Config.get("theme", "dark"))
        theme_menu = ctk.CTkOptionMenu(
            frame, variable=self._theme_var,
            values=[tr.T("settings.theme.dark"), tr.T("settings.theme.light")],
            fg_color=Config.COLOR_CARD,
            button_color=Config.COLOR_PRIMARY,
            button_hover_color=Config.COLOR_PRIMARY_DARK,
            dropdown_fg_color=Config.COLOR_CARD,
            dropdown_hover_color=Config.COLOR_CARD_HOVER,
            dropdown_text_color=Config.COLOR_TEXT,
            text_color=Config.COLOR_TEXT,
            command=self._on_theme_change
        )
        theme_menu.pack(side="right")
        self._theme_menu = theme_menu
    
    def _on_theme_change(self, value):
        theme = "dark" if value == tr.T("settings.theme.dark") else "light"
        Config.apply_theme(theme)
        settings = Config.load_settings()
        settings["theme"] = theme
        Config.save_settings(settings)
        if self.config_callback:
            self.config_callback(settings)
        self._show_toast(tr.T("settings.restarting"))
        self.after(800, self._restart_app)
    
    def _load_settings(self):
        settings = Config.load_settings()
        for key, widget in self._widgets.items():
            if key in settings:
                try:
                    if isinstance(widget, ctk.BooleanVar):
                        widget.set(bool(settings[key]))
                    elif isinstance(widget, ctk.DoubleVar):
                        widget.set(float(settings[key]))
                except Exception:
                    pass
    
    def _get_settings(self):
        settings = Config.load_settings().copy()
        for key, widget in self._widgets.items():
            try:
                if isinstance(widget, ctk.BooleanVar):
                    settings[key] = widget.get()
                elif isinstance(widget, ctk.DoubleVar):
                    settings[key] = int(widget.get())
            except Exception:
                pass
        if hasattr(self, '_lang_var'):
            settings["language"] = self._lang_var.get()
        if hasattr(self, '_theme_var'):
            val = self._theme_var.get()
            settings["theme"] = "dark" if val == tr.T("settings.theme.dark") else "light"
        return settings
    
    def _save_settings(self):
        settings = self._get_settings()
        old_lang = Config.get("language", "tr")
        old_theme = Config.get("theme", "dark")
        Config.save_settings(settings)
        tr.load(settings.get("language", "tr"))
        Config.apply_theme(settings.get("theme", "dark"))
        if self.config_callback:
            self.config_callback(settings)
        if settings.get("language") != old_lang or settings.get("theme") != old_theme:
            self._show_toast(tr.T("settings.restarting"))
            self.after(800, self._restart_app)
        else:
            self._show_toast(tr.T("settings.saved"))
    
    def _reset_settings(self):
        defaults = Config.SETTINGS_DEFAULTS.copy()
        old_lang = Config.get("language", "tr")
        old_theme = Config.get("theme", "dark")
        Config.save_settings(defaults)
        self._load_settings()
        tr.load(defaults.get("language", "tr"))
        Config.apply_theme(defaults.get("theme", "dark"))
        if self.config_callback:
            self.config_callback(defaults)
        if defaults.get("language") != old_lang or defaults.get("theme") != old_theme:
            self._show_toast(tr.T("settings.restarting"))
            self.after(800, self._restart_app)
        else:
            self._show_toast(tr.T("settings.reset_done"))
    
    def refresh_lang(self):
        try:
            self._title_label.configure(text=tr.T("settings.title"))
            if hasattr(self, '_theme_menu'):
                self._theme_menu.configure(
                    values=[tr.T("settings.theme.dark"), tr.T("settings.theme.light")]
                )
            if hasattr(self, '_lang_var'):
                self._lang_var.set(Config.get("language", "tr"))
            if hasattr(self, '_theme_var'):
                theme_key = Config.get("theme", "dark")
                self._theme_var.set(
                    tr.T("settings.theme.dark") if theme_key == "dark" else tr.T("settings.theme.light")
                )
        except Exception:
            pass

    def _restart_app(self):
        try:
            if Config._mutex_handle:
                import ctypes
                ctypes.windll.kernel32.CloseHandle(Config._mutex_handle)
                Config._mutex_handle = None
            import sys
            import subprocess
            subprocess.Popen([sys.executable, *sys.argv])
            self.after(100, self._do_exit)
        except Exception as e:
            print(f"[Settings] Restart failed: {e}")

    def _do_exit(self):
        if Config._mutex_handle:
            import ctypes
            ctypes.windll.kernel32.CloseHandle(Config._mutex_handle)
            Config._mutex_handle = None
        toplevel = self.winfo_toplevel()
        try:
            if hasattr(toplevel, 'destroy') and toplevel != self:
                toplevel.destroy()
        except Exception:
            pass
        import sys
        sys.exit(0)
    
    def _show_toast(self, message: str):
        try:
            toast = ctk.CTkToplevel(self)
        except Exception:
            return
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        
        tw, th = 300, 50
        x = self.winfo_rootx() + (self.winfo_width() - tw) // 2
        y = self.winfo_rooty() + self.winfo_height() - th - 20
        
        toast.geometry(f"{tw}x{th}+{x}+{y}")
        toast.attributes("-alpha", 0.95)
        
        frame = ctk.CTkFrame(toast, fg_color=Config.COLOR_CARD,
                            corner_radius=Config.CORNER_RADIUS_SMALL,
                            border_color=Config.COLOR_PRIMARY,
                            border_width=1)
        frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            frame, text=message,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT
        ).pack(expand=True)
        
        toast.after(2000, toast.destroy)
