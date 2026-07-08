import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import os
from config import Config
import math
import time
import threading
from modules.translator import tr


# ─── Utility ──────────────────────────────────────────────────────────
def _create_rounded_rect(w, h, r, color):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=color)
    return ctk.CTkImage(img, size=(w, h))


# ─── Premium Glass Frame ─────────────────────────────────────────────
class GlassFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=Config.COLOR_CARD,
            border_color=Config.GLASS_BORDER,
            border_width=1,
            corner_radius=Config.CORNER_RADIUS
        )
    
    def on_hover(self, event=None):
        self.configure(fg_color=Config.COLOR_CARD_HOVER)
    
    def on_leave(self, event=None):
        self.configure(fg_color=Config.COLOR_CARD)


# ─── Premium Card with hover lift ─────────────────────────────────────
class PremiumCard(ctk.CTkFrame):
    def __init__(self, master, title="", value="---", subtitle="", icon="",
                 accent_color=None, width=320, height=180, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.configure(
            fg_color=Config.COLOR_CARD,
            border_color=Config.GLASS_BORDER,
            border_width=1,
            corner_radius=Config.CORNER_RADIUS
        )
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        self._accent = accent_color or Config.COLOR_PRIMARY
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=18)
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_rowconfigure(1, weight=1)
        
        # Top row: icon + title
        top = ctk.CTkFrame(inner, fg_color="transparent", height=24)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        top.grid_columnconfigure(1, weight=1)
        
        icon_label = ctk.CTkLabel(
            top, text=icon, font=("Segoe UI", 22),
            text_color=self._accent
        )
        icon_label.grid(row=0, column=0, padx=(0, 10))
        
        ctk.CTkLabel(
            top, text=title,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=1, sticky="w", padx=(0, 8))
        
        # Accent line
        line = ctk.CTkFrame(self, height=3, width=40,
                            fg_color=self._accent, corner_radius=2)
        line.place(x=20, y=0)
        
        # Value
        self._value_var = ctk.StringVar(value=value)
        ctk.CTkLabel(
            inner, textvariable=self._value_var,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_XXLARGE, "bold"),
            text_color=Config.COLOR_TEXT,
            anchor="w"
        ).grid(row=1, column=0, sticky="w", pady=(0, 4))
        
        # Subtitle
        self._subtitle_var = ctk.StringVar(value=subtitle)
        ctk.CTkLabel(
            inner, textvariable=self._subtitle_var,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_TERTIARY,
            anchor="w"
        ).grid(row=2, column=0, sticky="w")
        
        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.configure(fg_color=Config.COLOR_CARD_HOVER)
    
    def _on_leave(self, e):
        self.configure(fg_color=Config.COLOR_CARD)
    
    def update_value(self, value: str, subtitle: str = None):
        self._value_var.set(value)
        if subtitle is not None:
            self._subtitle_var.set(subtitle)


# ─── Health Score Ring ────────────────────────────────────────────────
class HealthRing(ctk.CTkFrame):
    def __init__(self, master, size=220, **kwargs):
        self._size = size
        self._score = 0
        self._target_score = 0
        self._animating = False
        h = size + 80
        super().__init__(master, fg_color="transparent", width=size, height=h, **kwargs)

        self.pack_propagate(False)

        self._canvas = ctk.CTkCanvas(
            self, width=size, height=size,
            bg=Config.COLOR_BG, highlightthickness=0
        )
        self._canvas.pack(pady=(0, 4))

        self._label = ctk.CTkLabel(
            self, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_HERO, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._label.place(relx=0.5, rely=0.34, anchor="center")

        self._status_label = ctk.CTkLabel(
            self, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        )
        self._status_label.place(relx=0.5, rely=0.52, anchor="center")

        self._draw_bg()

    def _draw_bg(self):
        cx = cy = self._size // 2
        r = self._size // 2 - 14
        self._canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=0, extent=360,
            outline="#2a2a3a", width=10,
            style="arc", tags="bg"
        )

    def set_score(self, score: float, animate=True):
        self._target_score = max(0, min(100, score))
        if animate:
            self._animate_to(self._target_score)
        else:
            self._score = self._target_score
            self._draw()

    def _animate_to(self, target):
        if self._animating:
            return
        self._animating = True

        def animate():
            start_score = self._score
            diff = target - start_score
            steps = 30
            for i in range(steps + 1):
                progress = 1 - (1 - i / steps) ** 3
                self._score = start_score + diff * progress
                self.after(i * 12, self._draw)
            self._animating = False

        threading.Thread(target=animate, daemon=True).start()

    def _purple_gradient(self, pct: float) -> str:
        if pct <= 0:
            return "#3D1A6E"
        elif pct < 0.5:
            t = pct / 0.5
            r = int(61 + (123 - 61) * t)
            g = int(26 + (45 - 26) * t)
            b = int(110 + (185 - 110) * t)
        elif pct < 0.85:
            t = (pct - 0.5) / 0.35
            r = int(123 + (156 - 123) * t)
            g = int(45 + (39 - 45) * t)
            b = int(185 + (230 - 185) * t)
        else:
            t = (pct - 0.85) / 0.15
            r = int(156 + (200 - 156) * t)
            g = int(39 + (50 - 39) * t)
            b = int(230 + (255 - 230) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, **kwargs):
        if not hasattr(self, '_canvas') or not hasattr(self, '_label'):
            return
        self._canvas.delete("arc")
        cx = cy = self._size // 2
        r = self._size // 2 - 14

        pct = max(0, min(1, self._score / 100))
        angle = 360 * pct
        color = self._purple_gradient(pct)

        if angle > 1:
            self._canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=90, extent=angle,
                outline=color, width=10,
                style="arc", tags="arc"
            )

        score_int = max(0, min(100, int(self._score)))
        self._label.configure(text=f"{score_int}", text_color=color)

        if score_int >= 80:
            status_text = tr.T("health.status.excellent")
        elif score_int >= 60:
            status_text = tr.T("health.status.good")
        elif score_int >= 40:
            status_text = tr.T("health.status.caution")
        else:
            status_text = tr.T("health.status.critical")
        self._status_label.configure(text=status_text, text_color=color)
    
    @staticmethod
    def _lerp_hex(c1, c2, t):
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"


# ─── Sensor Mini Card (compact, used in sensor grids) ────────────────
class SensorMiniCard(ctk.CTkFrame):
    def __init__(self, master, title="", value="--", icon="", unit="",
                 accent_color=None, width=160, height=100, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.configure(
            fg_color=Config.COLOR_CARD,
            border_color=Config.GLASS_BORDER,
            border_width=1,
            corner_radius=Config.CORNER_RADIUS_SMALL
        )
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        self._accent = accent_color or Config.COLOR_TEXT_SECONDARY
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)
        
        # Icon + title row
        row1 = ctk.CTkFrame(inner, fg_color="transparent", height=18)
        row1.pack(fill="x", pady=(0, 8))
        row1.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            row1, text=icon, font=("Segoe UI", 16),
            text_color=self._accent
        ).pack(side="left", padx=(0, 6))
        
        ctk.CTkLabel(
            row1, text=title,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(side="left")
        
        # Value
        self._value_var = ctk.StringVar(value=value)
        ctk.CTkLabel(
            inner, textvariable=self._value_var,
            font=(Config.FONT_FAMILY, 18, "bold"),
            text_color=Config.COLOR_TEXT,
            anchor="w"
        ).pack(fill="x")
        
        # Unit
        self._unit_var = ctk.StringVar(value=unit)
        ctk.CTkLabel(
            inner, textvariable=self._unit_var,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
            text_color=Config.COLOR_TEXT_TERTIARY,
            anchor="w"
        ).pack(fill="x")
        
        self.bind("<Enter>", lambda e: self.configure(fg_color=Config.COLOR_CARD_HOVER))
        self.bind("<Leave>", lambda e: self.configure(fg_color=Config.COLOR_CARD))
    
    def update_value(self, value: str, unit: str = None):
        self._value_var.set(value)
        if unit is not None:
            self._unit_var.set(unit)


# ─── Status Badge ─────────────────────────────────────────────────────
class StatusBadge(ctk.CTkFrame):
    def __init__(self, master, text="", status="info", **kwargs):
        colors = {
            "success": (Config.COLOR_ACCENT_GREEN, "#111428"),
            "warning": (Config.COLOR_ACCENT_ORANGE, "#2B2316"),
            "danger": (Config.COLOR_ACCENT_RED, "#2A171D"),
            "info": (Config.COLOR_ACCENT_BLUE, "#141F33"),
            "purple": (Config.COLOR_PRIMARY, "#1C1A34"),
        }
        fg, bg = colors.get(status, colors["info"])
        
        super().__init__(master, fg_color=bg,
                         corner_radius=20, **kwargs)
        
        dot = ctk.CTkFrame(self, width=6, height=6,
                           fg_color=fg, corner_radius=3)
        dot.pack(side="left", padx=(8, 4), pady=4)
        
        ctk.CTkLabel(
            self, text=text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY, "bold"),
            text_color=fg
        ).pack(side="left", padx=(0, 10), pady=4)


# ─── Mini Trend Indicator ─────────────────────────────────────────────
class MiniTrend(ctk.CTkLabel):
    def __init__(self, master, value="", trend="up", **kwargs):
        arrow = "\u25B2" if trend == "up" else "\u25BC"
        color = Config.COLOR_ACCENT_GREEN if trend == "up" else Config.COLOR_ACCENT_RED
        text = f"{arrow} {value}"
        super().__init__(
            master, text=text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY, "bold"),
            text_color=color, **kwargs
        )


# ─── Notification Card ────────────────────────────────────────────────
class NotificationCard(ctk.CTkFrame):
    def __init__(self, master, title="", message="", severity="info",
                 time_str="", **kwargs):
        colors = {
            "success": (Config.COLOR_ACCENT_GREEN, "#10201D"),
            "warning": (Config.COLOR_ACCENT_ORANGE, "#211D16"),
            "danger": (Config.COLOR_ACCENT_RED, "#21151B"),
            "info": (Config.COLOR_ACCENT_BLUE, "#121A29"),
        }
        accent, bg = colors.get(severity, colors["info"])
        
        super().__init__(master, fg_color=bg,
                         corner_radius=Config.CORNER_RADIUS_SMALL, **kwargs)
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)
        
        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x")
        row1.grid_columnconfigure(1, weight=1)
        
        # Accent dot
        dot = ctk.CTkFrame(row1, width=8, height=8,
                           fg_color=accent, corner_radius=4)
        dot.grid(row=0, column=0, padx=(0, 8))
        
        ctk.CTkLabel(
            row1, text=title,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT
        ).grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(
            row1, text=time_str,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).grid(row=0, column=2, sticky="e")
        
        if message:
            ctk.CTkLabel(
                inner, text=message,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_TEXT_SECONDARY,
                wraplength=280, justify="left"
            ).pack(fill="x", pady=(4, 0))


# ─── Compact Metric Row (for GPU detailed view) ──────────────────────
class MetricRow(ctk.CTkFrame):
    def __init__(self, master, label="", value="--", icon="",
                 accent_color=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(1, weight=1)
        
        self._accent = accent_color or Config.COLOR_TEXT_SECONDARY
        
        ctk.CTkLabel(
            self, text=icon,
            font=("Segoe UI", 14),
            text_color=self._accent
        ).grid(row=0, column=0, padx=(0, 8))
        
        ctk.CTkLabel(
            self, text=label,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=1, sticky="w")
        
        self._value_var = ctk.StringVar(value=value)
        ctk.CTkLabel(
            self, textvariable=self._value_var,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT
        ).grid(row=0, column=2, sticky="e")
    
    def update_value(self, value: str):
        self._value_var.set(value)


# ─── AI Typing Label ──────────────────────────────────────────────────
class AITypingLabel(ctk.CTkLabel):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, text="", **kwargs)
        self._full_text = text
        self._typing = False
    
    def type_text(self, text: str, speed_ms: int = 20):
        self._full_text = text
        self._typing = True
        
        def type_loop():
            for i in range(len(text) + 1):
                if not self._typing:
                    break
                self.after(i * speed_ms, lambda t=text[:i]: self.configure(text=t))
            self._typing = False
        
        threading.Thread(target=type_loop, daemon=True).start()
    
    def stop_typing(self):
        self._typing = False
        self.configure(text=self._full_text)


# ─── Section Divider ──────────────────────────────────────────────────
class SectionDivider(ctk.CTkFrame):
    def __init__(self, master, title="", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        if title:
            ctk.CTkLabel(
                self, text=title,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
                text_color=Config.COLOR_TEXT
            ).grid(row=0, column=0, padx=(0, 16), sticky="w")
        
        line = ctk.CTkFrame(self, height=1,
                            fg_color=Config.GLASS_BORDER)
        line.grid(row=0, column=1, sticky="ew", pady=(12, 0))


# ─── Sidebar Nav Button ──────────────────────────────────────────────
class NavButton(ctk.CTkFrame):

    def _active_bg(self):
        return "#EDEFF2" if Config._theme == "light" else "#1A1533"

    def _hover_bg(self):
        return "#E2E4E8" if Config._theme == "light" else "#1E2230"

    def __init__(self, master, text="", icon="", is_active=False,
                 command=None, **kwargs):
        super().__init__(master, fg_color=self._active_bg() if is_active else "transparent",
                         corner_radius=10, height=40, **kwargs)
        self.pack_propagate(False)
        
        self._command = command
        self._is_active = is_active
        
        inner = ctk.CTkFrame(self, fg_color="transparent", height=40)
        inner.pack(fill="x", padx=10, pady=0)
        inner.pack_propagate(False)
        
        # Active indicator bar (only when active)
        self._indicator = ctk.CTkFrame(self, width=3, height=20,
                                       fg_color="#7C5CFF",
                                       corner_radius=2)
        if is_active:
            self._indicator.place(x=0, rely=0.5, anchor="w")
        
        self._icon_label = ctk.CTkLabel(
            inner, text=icon,
            font=("Segoe UI", 16),
            text_color=Config.COLOR_TEXT if is_active else Config.COLOR_TEXT_TERTIARY
        )
        self._icon_label.pack(side="left", padx=(6, 6))
        
        self._text_label = ctk.CTkLabel(
            inner, text=text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold" if is_active else "normal"),
            text_color="#7C5CFF" if is_active else Config.COLOR_TEXT_SECONDARY
        )
        self._text_label.pack(side="left")
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        inner.bind("<Button-1>", self._on_click)
        self._icon_label.bind("<Button-1>", self._on_click)
        self._text_label.bind("<Button-1>", self._on_click)
    
    def _on_enter(self, e):
        if not self._is_active:
            self.configure(fg_color=self._hover_bg())

    def _on_leave(self, e):
        if not self._is_active:
            self.configure(fg_color="transparent")

    def _on_click(self, e):
        if self._command:
            self._command()

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.configure(fg_color=self._active_bg())
            self._indicator.place(x=0, rely=0.5, anchor="w")
            self._icon_label.configure(text_color=Config.COLOR_TEXT)
            self._text_label.configure(
                text_color="#7C5CFF",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold")
            )
        else:
            self.configure(fg_color="transparent")
            self._indicator.place_forget()
            self._icon_label.configure(text_color=Config.COLOR_TEXT_TERTIARY)
            self._text_label.configure(
                text_color=Config.COLOR_TEXT_SECONDARY,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "normal")
            )

    def refresh_theme(self):
        if self._is_active:
            self.configure(fg_color=self._active_bg())
        self._indicator.configure(fg_color=Config.COLOR_PRIMARY)


# ─── Top Bar Button ───────────────────────────────────────────────────
class TopBarButton(ctk.CTkFrame):
    def __init__(self, master, text="", icon="", command=None,
                 badge_count=0, width=36, **kwargs):
        super().__init__(master, fg_color="transparent",
                         width=width, height=36,
                         corner_radius=Config.CORNER_RADIUS_SMALL, **kwargs)
        self.pack_propagate(False)
        
        self._command = command
        
        ctk.CTkLabel(
            self, text=icon,
            font=("Segoe UI", 18),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        self._badge = None
        self._badge_label = None
        if badge_count > 0:
            self._show_badge(badge_count)
        
        self.bind("<Enter>", lambda e: self.configure(fg_color=Config.COLOR_CARD))
        self.bind("<Leave>", lambda e: self.configure(fg_color="transparent"))
        self.bind("<Button-1>", self._on_click)
    
    def _show_badge(self, count):
        if self._badge:
            self._badge.destroy()
        self._badge = ctk.CTkFrame(self, fg_color=Config.COLOR_ACCENT_RED,
                                   corner_radius=8, width=16, height=16)
        self._badge.place(x=self.winfo_width() - 10, y=2)
        self._badge_label = ctk.CTkLabel(
            self._badge, text=str(min(count, 9)),
            font=(Config.FONT_FAMILY, 8, "bold"),
            text_color="#FFFFFF"
        )
        self._badge_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def update_badge(self, count):
        if self._badge:
            self._badge.destroy()
            self._badge = None
            self._badge_label = None
        if count > 0:
            self._show_badge(count)
    
    def _on_click(self, e):
        if self._command:
            self._command()


# ─── Search Bar ───────────────────────────────────────────────────────
class SearchBar(ctk.CTkFrame):
    def __init__(self, master, width=240, **kwargs):
        super().__init__(master, width=width, height=36,
                         fg_color=Config.COLOR_CARD,
                         corner_radius=Config.CORNER_RADIUS_SMALL, **kwargs)
        self.pack_propagate(False)
        
        ctk.CTkLabel(
            self, text="\u2315",
            font=("Segoe UI", 14),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(side="left", padx=(10, 4), pady=6)
        
        self._entry = ctk.CTkEntry(
            self, placeholder_text="Ara...",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            fg_color="transparent",
            text_color=Config.COLOR_TEXT,
            placeholder_text_color=Config.COLOR_TEXT_TERTIARY,
            border_width=0,
            height=28
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=4)


# ─── Gauge Canvas (for CPU / GPU ring gauges) ────────────────────────
class RingGauge(ctk.CTkFrame):
    def __init__(self, master, size=120, title="", unit="%",
                 min_val=0, max_val=100, **kwargs):
        super().__init__(master, fg_color="transparent",
                         width=size, height=size + 40, **kwargs)
        self._size = size
        self._title = title
        self._unit = unit
        self._min = min_val
        self._max = max_val
        self._value = 0
        self.pack_propagate(False)
        
        self._canvas = ctk.CTkCanvas(
            self, width=size, height=size,
            bg=Config.COLOR_BG, highlightthickness=0
        )
        self._canvas.pack()
        
        self._value_label = ctk.CTkLabel(
            self, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_XLARGE, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._value_label.place(relx=0.5, rely=0.38, anchor="center")
        
        ctk.CTkLabel(
            self, text=title,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).place(relx=0.5, rely=0.62, anchor="center")
        
        self._draw_bg()
    
    def _draw_bg(self):
        cx = cy = self._size // 2
        r = self._size // 2 - 14
        self._canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=0, extent=360,
            outline="#1E2230", width=10,
            style="arc", tags="bg"
        )
    
    def set_value(self, value: float):
        self._value = max(self._min, min(self._max, value))
        self._draw()
    
    def _draw(self, **kwargs):
        if not hasattr(self, '_size'):
            return
        self._canvas.delete("arc")
        cx = cy = self._size // 2
        r = self._size // 2 - 14
        
        pct = (self._value - self._min) / (self._max - self._min)
        angle = 360 * pct
        
        if pct >= 0.85:
            color = Config.COLOR_ACCENT_RED
        elif pct >= 0.70:
            color = Config.COLOR_ACCENT_ORANGE
        elif pct >= 0.40:
            color = Config.COLOR_ACCENT_BLUE
        else:
            color = Config.COLOR_ACCENT_GREEN
        
        self._canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90, extent=angle,
            outline=color, width=10,
            style="arc", tags="arc",
            capstyle="round"
        )
        
        self._value_label.configure(
            text=f"{self._value:.0f}{self._unit}",
            text_color=color
        )


# ─── Mini Sparkline (Canvas-drawn mini chart) ────────────────────────
class Sparkline(ctk.CTkFrame):
    def __init__(self, master, width=120, height=32, color=None, **kwargs):
        super().__init__(master, fg_color="transparent",
                         width=width, height=height, **kwargs)
        self._width = width
        self._height = height
        self._color = color or Config.COLOR_PRIMARY
        self._data = []
        self.pack_propagate(False)
        
        self._canvas = ctk.CTkCanvas(
            self, width=width, height=height,
            bg=Config.COLOR_BG, highlightthickness=0
        )
        self._canvas.pack()
    
    def add_point(self, value: float):
        self._data.append(value)
        if len(self._data) > 50:
            self._data = self._data[-50:]
        self._draw()
    
    def set_data(self, data: list):
        self._data = data[-50:]
        self._draw()
    
    def _draw(self, **kwargs):
        if not hasattr(self, '_data'):
            return
        self._canvas.delete("all")
        if len(self._data) < 2:
            return
        
        w, h = self._width, self._height
        min_v = min(self._data) if self._data else 0
        max_v = max(self._data) if self._data else 1
        rng = max_v - min_v if max_v != min_v else 1
        
        points = []
        for i, v in enumerate(self._data):
            x = i / (len(self._data) - 1) * w
            y = h - ((v - min_v) / rng) * (h - 4) - 2
            points.extend([x, y])
        
        # Gradient line
        for i in range(len(points) // 2 - 1):
            x1, y1 = points[i * 2], points[i * 2 + 1]
            x2, y2 = points[(i + 1) * 2], points[(i + 1) * 2 + 1]
            alpha = int(180 + 75 * (i / (len(points) // 2)))
            r = int(self._color[1:3], 16)
            g = int(self._color[3:5], 16)
            b = int(self._color[5:7], 16)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self._canvas.create_line(x1, y1, x2, y2, fill=color,
                                     width=2, smooth=True, capstyle="round")


# ─── Status Dot ───────────────────────────────────────────────────────
class StatusDot(ctk.CTkFrame):
    def __init__(self, master, size=8, color=None, **kwargs):
        super().__init__(master, width=size, height=size,
                         fg_color=color or Config.COLOR_ACCENT_GREEN,
                         corner_radius=size // 2, **kwargs)
        self.pack_propagate(False)
    
    def set_color(self, color: str):
        self.configure(fg_color=color)


# ─── Circular Gauge (safe: doesn't override _draw) ────────────────────
class CircularGauge(ctk.CTkFrame):
    ARC_ANGLE = 270
    ARC_START = 315
    
    def __init__(self, master, size=120, title="", unit="%",
                 min_val=0, max_val=100, **kwargs):
        super().__init__(master, fg_color="transparent",
                         width=size, height=size + 36, **kwargs)
        self._size = size
        self._title = title
        self._unit = unit
        self._min = min_val
        self._max = max_val
        self._value = 0
        self._display_value = 0
        self._target_value = 0
        self._anim_running = False
        self.pack_propagate(False)
        
        self._canvas = ctk.CTkCanvas(
            self, width=size, height=size,
            bg=Config.COLOR_BG, highlightthickness=0
        )
        self._canvas.pack()
        
        fs = max(16, size // 4)
        self._value_label = ctk.CTkLabel(
            self, text="--",
            font=(Config.FONT_FAMILY, fs, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._value_label.place(relx=0.5, rely=0.42, anchor="center")
        
        self._unit_label = ctk.CTkLabel(
            self, text=unit,
            font=(Config.FONT_FAMILY, max(9, size//12)),
            text_color=Config.COLOR_TEXT_TERTIARY
        )
        self._unit_label.place(relx=0.5, rely=0.58, anchor="center")
        
        self._title_label = ctk.CTkLabel(
            self, text=title,
            font=(Config.FONT_FAMILY, max(8, size//13)),
            text_color=Config.COLOR_TEXT_TERTIARY,
        )
        self._title_label.place(relx=0.5, rely=0.72, anchor="center")
    
    def set_value(self, value: float, animate: bool = True):
        self._target_value = max(self._min, min(self._max, value))
        if animate and abs(self._display_value - self._target_value) > 1:
            if not self._anim_running:
                self._anim_running = True
                self._animate_step()
        else:
            self._display_value = self._target_value
            self._redraw()
    
    def _animate_step(self):
        diff = self._target_value - self._display_value
        step = max(1, abs(diff) * 0.2)
        if abs(diff) <= step:
            self._display_value = self._target_value
            self._anim_running = False
        else:
            self._display_value += step if diff > 0 else -step
            self.after(30, self._animate_step)
        self._redraw()
    
    def _pct(self):
        return (self._display_value - self._min) / (self._max - self._min)
    
    def _get_color(self, pct):
        """Smooth purple gradient: dark purple → bright purple → pinkish."""
        if pct <= 0:
            return "#3D1A6E"
        elif pct < 0.5:
            t = pct / 0.5
            r = int(61 + (123 - 61) * t)
            g = int(26 + (45 - 26) * t)
            b = int(110 + (185 - 110) * t)
        elif pct < 0.85:
            t = (pct - 0.5) / 0.35
            r = int(123 + (156 - 123) * t)
            g = int(45 + (39 - 45) * t)
            b = int(185 + (230 - 185) * t)
        else:
            t = (pct - 0.85) / 0.15
            r = int(156 + (200 - 156) * t)
            g = int(39 + (50 - 39) * t)
            b = int(230 + (255 - 230) * t)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _redraw(self):
        self._canvas.delete("all")
        cx = cy = self._size // 2
        r = self._size // 2 - 8
        
        # Background arc
        self._canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=self.ARC_START, extent=self.ARC_ANGLE,
            outline="#1E2230", width=16,
            style="arc"
        )
        
        pct = self._pct()
        angle = self.ARC_ANGLE * pct
        final_color = self._get_color(pct)
        
        # Smooth purple arc — single continuous arc, no segment lines
        if angle > 1:
            self._canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=self.ARC_START, extent=angle,
                outline=self._get_color(pct), width=16,
                style="arc"
            )
        
        # Label
        self._value_label.configure(
            text=f"{self._display_value:.0f}",
            text_color=final_color
        )
