import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import NotificationCard
from datetime import datetime
import time


class NotificationsPage(ctk.CTkFrame):
    def __init__(self, master, notification_manager=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.notification_manager = notification_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._build()
    
    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(24, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(2, weight=0)
        
        self._title_lbl = ctk.CTkLabel(
            header, text=tr.T("notifications.title"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_HERO, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._title_lbl.grid(row=0, column=0, sticky="w")
        
        # Action buttons
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=2, sticky="e")
        
        self._mark_read_btn = ctk.CTkButton(
            actions, text=tr.T("notifications.mark_read"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            fg_color=Config.COLOR_CARD, text_color=Config.COLOR_TEXT,
            hover_color=Config.COLOR_CARD_HOVER,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            height=32, command=self._mark_all_read
        )
        self._mark_read_btn.pack(side="left", padx=(0, 8))
        
        self._clear_btn = ctk.CTkButton(
            actions, text=tr.T("notifications.clear"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            fg_color=Config.COLOR_CARD, text_color=Config.COLOR_ACCENT_RED,
            hover_color=Config.COLOR_CARD_HOVER,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            height=32, command=self._clear_all
        )
        self._clear_btn.pack(side="left")
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color=Config.COLOR_CARD).grid(
            row=1, column=0, padx=24, pady=(0, 12), sticky="ew"
        )
        
        # Scrollable notification list
        self._list_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Config.COLOR_CARD,
            scrollbar_button_hover_color=Config.COLOR_CARD_HOVER
        )
        self._list_container.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="nsew")
        self._list_container.grid_columnconfigure(0, weight=1)
        
        self._notif_widgets = []
    
    def _format_time(self, ts: float) -> str:
        dt = datetime.fromtimestamp(ts)
        now = datetime.now()
        if dt.date() == now.date():
            return dt.strftime("%H:%M")
        if (now - dt).days < 2:
            return tr.T("notifications.yesterday", time=dt.strftime("%H:%M"))
        return dt.strftime("%d.%m.%Y %H:%M")
    
    def _mark_all_read(self):
        if self.notification_manager:
            self.notification_manager.mark_all_read()
            self.refresh()
    
    def _clear_all(self):
        if self.notification_manager:
            self.notification_manager.clear_all()
            self.refresh()
    
    def refresh(self):
        # Clear existing widgets
        for w in self._notif_widgets:
            w.destroy()
        self._notif_widgets.clear()
        
        if not self.notification_manager:
            return
        
        notifs = self.notification_manager.get_notifications(include_dismissed=False)
        notifs.sort(key=lambda x: x.timestamp, reverse=True)
        
        if not notifs:
            ctk.CTkLabel(
                self._list_container,
                text=tr.T("notifications.empty"),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                text_color=Config.COLOR_TEXT_TERTIARY
            ).pack(pady=60)
            return
        
        for n in notifs:
            severity = "info"
            if n.severity == "danger":
                severity = "danger"
            elif n.severity == "warning":
                severity = "warning"
            
            card = NotificationCard(
                self._list_container,
                title=n.title,
                message=n.message,
                severity=severity,
                time_str=self._format_time(n.timestamp)
            )
            card.pack(fill="x", pady=3)
            if not n.read:
                ctk.CTkFrame(card, height=2, fg_color=Config.COLOR_ACCENT_BLUE,
                            corner_radius=1).place(relx=0, rely=1, relwidth=1, anchor="sw")
            self._notif_widgets.append(card)

    def refresh_lang(self):
        try:
            self._title_lbl.configure(text=tr.T("notifications.title"))
            self._mark_read_btn.configure(text=tr.T("notifications.mark_read"))
            self._clear_btn.configure(text=tr.T("notifications.clear"))
        except Exception:
            pass
