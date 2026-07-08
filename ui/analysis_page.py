import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame, SectionDivider, StatusBadge, PremiumCard, NotificationCard
from datetime import datetime
import time


class AnalysisPage(ctk.CTkFrame):
    def __init__(self, master, sensor_manager=None, ai_engine=None, database=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.sensor_manager = sensor_manager
        self.ai_engine = ai_engine
        self.database = database
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        self._build_content()
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=32, pady=(24, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, text="\uD83D\uDCCA",
            font=("Segoe UI", 28)
        ).pack(side="left", padx=(0, 12))
        
        self._analysis_title = ctk.CTkLabel(
            header, text=tr.T("analysis.title"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_XLARGE, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._analysis_title.pack(side="left")
        
        self._analysis_badge = StatusBadge(header, text=tr.T("status.live"), status="purple")
        self._analysis_badge.pack(side="right")
    
    def _build_content(self):
        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Config.COLOR_CARD,
            scrollbar_button_hover_color=Config.COLOR_CARD_HOVER
        )
        container.grid(row=1, column=0, padx=32, pady=8, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # Gaming Status Card
        self._gaming_frame = GlassFrame(container)
        self._gaming_frame.grid(row=row, column=0, padx=4, pady=(0, 16), sticky="nsew")
        row += 1
        
        gaming_inner = ctk.CTkFrame(self._gaming_frame, fg_color="transparent")
        gaming_inner.pack(fill="x", padx=24, pady=20)
        
        ctk.CTkLabel(
            gaming_inner, text="\uD83C\uDFAE",
            font=("Segoe UI", 32)
        ).pack(anchor="w")
        
        SectionDivider(gaming_inner, title=tr.T("analysis.game.title")).pack(fill="x", pady=(8, 12))
        
        self._gaming_status = ctk.CTkLabel(
            gaming_inner,
            text=tr.T("analysis.waiting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            text_color=Config.COLOR_TEXT_SECONDARY
        )
        self._gaming_status.pack(anchor="w")
        
        self._gaming_duration_label = ctk.CTkLabel(
            gaming_inner,
            text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY
        )
        self._gaming_duration_label.pack(anchor="w", pady=(4, 0))
        
        # Last Gaming Report
        self._report_frame = GlassFrame(container)
        self._report_frame.grid(row=row, column=0, padx=4, pady=(0, 16), sticky="nsew")
        row += 1
        
        report_inner = ctk.CTkFrame(self._report_frame, fg_color="transparent")
        report_inner.pack(fill="x", padx=24, pady=20)
        
        SectionDivider(report_inner, title=tr.T("analysis.game.title")).pack(fill="x", pady=(0, 12))
        
        self._report_content = ctk.CTkFrame(report_inner, fg_color="transparent")
        self._report_content.pack(fill="x")
        
        self._game_name_label = ctk.CTkLabel(
            self._report_content,
            text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            text_color=Config.COLOR_PRIMARY,
            anchor="w"
        )
        self._game_name_label.pack(anchor="w", pady=(0, 8))
        
        self._no_report_label = ctk.CTkLabel(
            self._report_content,
            text=tr.T("analysis.game.none"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY,
            justify="left"
        )
        self._no_report_label.pack(anchor="w", pady=8)
        
        # Analysis History
        SectionDivider(container, title=tr.T("analysis.history")).grid(
            row=row, column=0, padx=4, pady=(8, 16), sticky="ew")
        row += 1
        
        self._history_frame = GlassFrame(container)
        self._history_frame.grid(row=row, column=0, padx=4, pady=(0, 24), sticky="nsew")
        row += 1
        
        self._history_content = ctk.CTkFrame(self._history_frame, fg_color="transparent")
        self._history_content.pack(fill="x", padx=24, pady=16)
        
        self._no_history_label = ctk.CTkLabel(
            self._history_content,
            text=tr.T("analysis.history.none"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY
        )
        self._no_history_label.pack(anchor="w", pady=8)
    
    def update_gaming_status(self, active: bool, report: dict = None):
        if active:
            game = self.sensor_manager._current_game_process if self.sensor_manager else ""
            status_text = f"\uD83C\uDFAE {game} \u00E7al\u0131\u015F\u0131yor — sistem izleniyor..." if game else "\uD83C\uDFAE Oyun \u00E7al\u0131\u015F\u0131yor — sistem izleniyor..."
            self._gaming_status.configure(
                text=status_text,
                text_color=Config.COLOR_ACCENT_GREEN
            )
        else:
            self._gaming_status.configure(
                text=tr.T("analysis.idle"),
                text_color=Config.COLOR_TEXT_SECONDARY
            )
            self._gaming_duration_label.configure(text="")
        
        if report:
            self._show_gaming_report(report)
    
    def _show_gaming_report(self, report: dict):
        for w in self._report_content.winfo_children():
            w.destroy()
        
        start = report.get("start_time", 0)
        duration = report.get("duration", 0)
        
        lines = []
        dur_str = f"{int(duration // 60)} dk {int(duration % 60)} sn" if duration < 3600 else f"{duration/3600:.1f} saat"
        lines.append(f"\U0001F4C5 Tarih: {datetime.fromtimestamp(start).strftime('%d.%m.%Y %H:%M')}" if start else "")
        lines.append(f"\u23F1 S\u00FCre: {dur_str}")
        game_name = report.get("game_name", "")
        if game_name:
            lines.append(f"\uD83C\uDFAE Oyun: {game_name}")
        if report.get("steam_running"):
            lines.append("\U0001F535 Steam a\u00E7\u0131k")
        lines.append("")
        
        lines.append("S\u0131cakl\u0131klar:")
        lines.append(f"  \u2022 CPU: {report.get('cpu_temp_avg', 0):.1f}\u00B0C (min {report.get('cpu_temp_min', 0):.1f}\u00B0C / max {report.get('cpu_temp_max', 0):.1f}\u00B0C)")
        lines.append(f"  \u2022 GPU: {report.get('gpu_temp_avg', 0):.1f}\u00B0C (min {report.get('gpu_temp_min', 0):.1f}\u00B0C / max {report.get('gpu_temp_max', 0):.1f}\u00B0C)")
        hs = report.get('hotspot_temp_avg', 0)
        if hs > 0:
            lines.append(f"  \u2022 Hotspot: {hs:.1f}\u00B0C (max {report.get('hotspot_temp_max', 0):.1f}\u00B0C, delta {report.get('hotspot_delta_avg', 0):.1f}\u00B0C)")
        lines.append("")
        lines.append("Kullan\u0131m:")
        lines.append(f"  \u2022 GPU Kullan\u0131m\u0131: ortalama %{report.get('gpu_usage_avg', 0):.1f}")
        lines.append(f"  \u2022 CPU Kullan\u0131m\u0131: ortalama %{report.get('cpu_usage_avg', 0):.1f}")
        lines.append(f"  \u2022 GPU Fan\u0131: ortalama %{report.get('gpu_fan_avg', 0):.1f}")
        lines.append(f"  \u2022 GPU G\u00FCc\u00FC: ortalama {report.get('gpu_power_avg', 0):.1f}W")
        
        text = "\n".join(lines)
        
        if game_name:
            self._game_name_label.configure(text=f"\uD83C\uDFAE {game_name}")
            self._game_name_label.pack(anchor="w", pady=(0, 8))
        else:
            self._game_name_label.pack_forget()
        
        ctk.CTkLabel(
            self._report_content,
            text=text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            justify="left",
            anchor="w"
        ).pack(fill="x", pady=4)
    
    def refresh_lang(self):
        try:
            self._analysis_title.configure(text=tr.T("analysis.title"))
            self._analysis_badge.configure(text=tr.T("status.live"))
        except Exception:
            pass

    def refresh(self):
        if self.sensor_manager:
            report = self.sensor_manager.get_gaming_report()
            active = self.sensor_manager.gaming_active
            self.update_gaming_status(active, report)
        
        if self.database:
            self._load_analysis_history()
    
    def _load_analysis_history(self):
        for w in self._history_content.winfo_children():
            w.destroy()
        
        try:
            history = self.database.get_recent_analysis(limit=10)
        except Exception:
            history = []
        
        if not history:
            self._no_history_label = ctk.CTkLabel(
                self._history_content,
                text=tr.T("analysis.history.none"),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                text_color=Config.COLOR_TEXT_TERTIARY
            )
            self._no_history_label.pack(anchor="w", pady=8)
            return
        
        for item in history:
            ts = item.get("timestamp", 0)
            summary = item.get("summary", "")
            severity = item.get("severity", "info")
            component = item.get("component", "")
            
            colors = {
                "danger": Config.COLOR_ACCENT_RED,
                "warning": Config.COLOR_ACCENT_ORANGE,
                "info": Config.COLOR_ACCENT_BLUE,
                "success": Config.COLOR_ACCENT_GREEN
            }
            
            item_frame = ctk.CTkFrame(self._history_content, fg_color="transparent")
            item_frame.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                item_frame,
                text=f"[{datetime.fromtimestamp(ts).strftime('%H:%M')}] {component}: {summary[:120]}",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=colors.get(severity, Config.COLOR_TEXT_SECONDARY),
                anchor="w"
            ).pack(fill="x")
