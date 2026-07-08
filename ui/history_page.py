import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame, SectionDivider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("Agg")
import time
from datetime import datetime


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, database=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.database = database
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._build_header()
        self._build_time_selector()
        self._build_charts()
    
    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=32, pady=(24, 8), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame, text="\uD83D\uDCC8",
            font=("Segoe UI", 28)
        ).pack(side="left", padx=(0, 12))
        
        self._history_title = ctk.CTkLabel(
            header_frame, text=tr.T("history.title"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_XLARGE, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._history_title.pack(side="left")
        
        self._time_hours = 24
        self._time_var = ctk.StringVar(value=tr.T("history.last_24h"))
    
    def _build_time_selector(self):
        selector_frame = GlassFrame(self)
        selector_frame.grid(row=1, column=0, padx=32, pady=8, sticky="ew")
        
        inner = ctk.CTkFrame(selector_frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        inner.grid_columnconfigure(0, weight=1)
        
        self._time_opt_map = {
            tr.T("history.last_1h"): 1,
            tr.T("history.last_6h"): 6,
            tr.T("history.last_24h"): 24,
            tr.T("history.last_7d"): 168,
            tr.T("history.last_30d"): 720,
        }
        time_options = list(self._time_opt_map.keys())
        
        ctk.CTkLabel(
            inner, text="\uD83D\uDD52",
            font=("Segoe UI", 16),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(side="left", padx=(0, 8))
        
        self._time_menu = ctk.CTkOptionMenu(
            inner,
            values=time_options,
            variable=self._time_var,
            command=self._on_time_select,
            fg_color=Config.COLOR_CARD,
            button_color=Config.COLOR_PRIMARY,
            button_hover_color=Config.COLOR_PRIMARY_DARK,
            text_color=Config.COLOR_TEXT,
            dropdown_fg_color=Config.COLOR_CARD,
            dropdown_text_color=Config.COLOR_TEXT,
            dropdown_hover_color=Config.COLOR_CARD_HOVER,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            width=160
        )
        self._time_menu.pack(side="left", padx=4)
        
        ctk.CTkButton(
            inner, text=tr.T("history.refresh"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            fg_color=Config.COLOR_PRIMARY,
            hover_color=Config.COLOR_PRIMARY_DARK,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            width=100,
            height=32,
            command=self.refresh_charts
        ).pack(side="right", padx=4)
    
    def _build_charts(self):
        charts_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Config.COLOR_CARD,
            scrollbar_button_hover_color=Config.COLOR_CARD_HOVER
        )
        charts_container.grid(row=2, column=0, padx=32, pady=8, sticky="nsew")
        charts_container.grid_columnconfigure(0, weight=1)
        
        self._charts_frame = ctk.CTkFrame(charts_container, fg_color="transparent")
        self._charts_frame.grid(row=0, column=0, sticky="nsew")
        self._charts_frame.grid_columnconfigure(0, weight=1)
        
        self._figure_cpu = Figure(figsize=(10, 3), dpi=100, facecolor=Config.COLOR_CARD)
        self._figure_gpu = Figure(figsize=(10, 3), dpi=100, facecolor=Config.COLOR_CARD)
        self._figure_usage = Figure(figsize=(10, 3), dpi=100, facecolor=Config.COLOR_CARD)
        
        self._setup_figure(self._figure_cpu, tr.T("history.cpu_temp_title"), Config.COLOR_ACCENT_BLUE)
        self._setup_figure(self._figure_gpu, tr.T("history.gpu_temp_title"), Config.COLOR_ACCENT_RED)
        self._setup_figure(self._figure_usage, tr.T("history.usage_title"), Config.COLOR_ACCENT_CYAN)
        
        self._canvas_cpu = self._embed_figure(self._figure_cpu, 0)
        self._canvas_gpu = self._embed_figure(self._figure_gpu, 1)
        self._canvas_usage = self._embed_figure(self._figure_usage, 2)
        
        self._stats_frame = GlassFrame(self._charts_frame)
        self._stats_frame.grid(row=3, column=0, padx=4, pady=12, sticky="ew")
        
        self._stats_labels = {}
        self._create_stat_cards()
        
        self.after(100, self.refresh_charts)
    
    def _setup_figure(self, fig, title, color):
        fig.set_facecolor(Config.COLOR_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(Config.COLOR_BG)
        ax.set_title(title, color=Config.COLOR_TEXT, fontsize=10, pad=10)
        ax.tick_params(colors=Config.COLOR_TEXT_SECONDARY, labelsize=8)
        ax.spines["bottom"].set_color(Config.COLOR_BORDER)
        ax.spines["top"].set_color(Config.COLOR_BORDER)
        ax.spines["left"].set_color(Config.COLOR_BORDER)
        ax.spines["right"].set_color(Config.COLOR_BORDER)
        ax.grid(True, alpha=0.15, color=Config.COLOR_TEXT_SECONDARY)
    
    def _embed_figure(self, fig, row):
        canvas = FigureCanvasTkAgg(fig, master=self._charts_frame)
        canvas.get_tk_widget().grid(row=row, column=0, padx=4, pady=8, sticky="ew")
        return canvas
    
    def _create_stat_cards(self):
        self._stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        stats = [
            ("avg_cpu", tr.T("history.avg_cpu"), "\u00B0C"),
            ("avg_gpu", tr.T("history.avg_gpu"), "\u00B0C"),
            ("max_cpu", tr.T("history.max_cpu"), "\u00B0C"),
            ("max_gpu", tr.T("history.max_gpu"), "\u00B0C"),
        ]
        
        for i, (key, title, unit) in enumerate(stats):
            frame = GlassFrame(self._stats_frame)
            frame.grid(row=0, column=i, padx=6, pady=16, sticky="ew")
            
            inner = ctk.CTkFrame(frame, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)
            
            ctk.CTkLabel(inner, text=title,
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                        text_color=Config.COLOR_TEXT_TERTIARY).pack()
            
            var = ctk.StringVar(value="--")
            self._stats_labels[key] = var
            ctk.CTkLabel(inner, textvariable=var,
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_XXLARGE, "bold"),
                        text_color=Config.COLOR_TEXT).pack(pady=(4, 0))
    
    def refresh_lang(self):
        try:
            self._history_title.configure(text=tr.T("history.title"))
            self._time_opt_map = {
                tr.T("history.last_1h"): 1,
                tr.T("history.last_6h"): 6,
                tr.T("history.last_24h"): 24,
                tr.T("history.last_7d"): 168,
                tr.T("history.last_30d"): 720,
            }
            if hasattr(self, '_time_menu'):
                self._time_menu.configure(values=list(self._time_opt_map.keys()))
                self._time_var.set(tr.T("history.last_24h"))
                self._time_hours = 24
        except Exception:
            pass

    def _on_time_select(self, choice):
        self._time_hours = self._time_opt_map.get(choice, 24)
        self.refresh_charts()
    
    def refresh_charts(self):
        if not self.database:
            print("[HISTORY] No database")
            return
        
        hours = self._time_hours
        
        try:
            if hours <= 24:
                data = self.database.get_hourly_averages(hours)
            else:
                data = self.database.get_daily_averages(hours // 24)
            
            if data and len(data) > 0:
                self._update_charts(data)
                self._update_stats(data)
            else:
                print(f"[HISTORY] No data for last {hours}h")
        except Exception as e:
            print(f"[HISTORY ERROR] {e}")
    
    def _update_charts(self, data):
        self._update_figure(self._figure_cpu, self._canvas_cpu, data, 
                           ["avg_cpu_temp"], [tr.T("history.cpu_temp")], ["#2979FF"])
        self._update_figure(self._figure_gpu, self._canvas_gpu, data,
                           ["avg_gpu_temp", "avg_hotspot"], [tr.T("history.gpu_temp"), tr.T("history.hotspot")], 
                           ["#FF1744", "#FF9100"])
        
        self._update_figure(self._figure_usage, self._canvas_usage, data,
                           ["avg_cpu_usage", "avg_gpu_usage"],
                           [tr.T("history.cpu_usage"), tr.T("history.gpu_usage")],
                           ["#00E5FF", "#D500F9"])
    
    def _update_figure(self, fig, canvas, data, keys, labels, colors):
        ax = fig.axes[0]
        ax.clear()
        
        self._setup_figure(fig, ax.get_title(), colors[0] if colors else "#FFFFFF")
        
        x = range(len(data))
        
        for i, key in enumerate(keys):
            values = [d.get(key, 0) or 0 for d in data]
            ax.plot(x, values, label=labels[i], color=colors[i], linewidth=2, alpha=0.9)
            ax.fill_between(x, values, alpha=0.1, color=colors[i])
        
        if data:
            n = max(1, len(data) // 5)
            ax.set_xticks(range(0, len(data), n))
        
        ax.legend(loc="upper left", facecolor=Config.COLOR_CARD, 
                 edgecolor=Config.COLOR_BORDER, labelcolor=Config.COLOR_TEXT,
                 fontsize=8)
        
        fig.tight_layout()
        canvas.draw()
    
    def _update_stats(self, data):
        cpu_temps = [d.get("avg_cpu_temp", 0) or 0 for d in data if d.get("avg_cpu_temp")]
        gpu_temps = [d.get("avg_gpu_temp", 0) or 0 for d in data if d.get("avg_gpu_temp")]
        
        if cpu_temps:
            self._stats_labels["avg_cpu"].set(f"{sum(cpu_temps)/len(cpu_temps):.1f}°C")
            self._stats_labels["max_cpu"].set(f"{max(cpu_temps):.1f}°C")
        
        if gpu_temps:
            self._stats_labels["avg_gpu"].set(f"{sum(gpu_temps)/len(gpu_temps):.1f}°C")
            self._stats_labels["max_gpu"].set(f"{max(gpu_temps):.1f}°C")
