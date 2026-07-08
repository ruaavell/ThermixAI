import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame, SectionDivider, StatusBadge, NotificationCard, CircularGauge, HealthRing
import time
from datetime import datetime


class MainPage(ctk.CTkFrame):
    def __init__(self, master, sensor_manager=None, ai_engine=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.sensor_manager = sensor_manager
        self.ai_engine = ai_engine
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Config.COLOR_CARD,
            scrollbar_button_hover_color=Config.COLOR_CARD_HOVER
        )
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        self._build(container)
        self._update_counter = 0
        self._health_ring_shown = False
    
    def _safe_label(self, lbl, text, color=None):
        try:
            if color:
                lbl.configure(text=text, text_color=color)
            else:
                lbl.configure(text=text)
        except Exception:
            pass
    
    def _log(self, msg):
        try:
            print(f"[MainPage] {msg}")
        except Exception:
            pass
    
    def _build(self, container):
        row = 0
        
        # ─── Header ──────────────────────
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=row, column=0, padx=24, pady=(20, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        self._status_dot = ctk.CTkFrame(header, width=10, height=10,
                                        fg_color=Config.COLOR_ACCENT_GREEN,
                                        corner_radius=5)
        self._status_dot.pack(side="left", padx=(0, 8))
        
        self._status_label = ctk.CTkLabel(
            header, text=tr.T("status.starting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            text_color=Config.COLOR_TEXT_SECONDARY
        )
        self._status_label.pack(side="left")
        
        self._time_label = ctk.CTkLabel(
            header, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY
        )
        self._time_label.pack(side="right")
        row += 1
        
        # ─── Health Score Ring ──────────────
        health_row = ctk.CTkFrame(container, fg_color="transparent")
        health_row.grid(row=row, column=0, padx=24, pady=(4, 8), sticky="ew")
        health_row.grid_columnconfigure(1, weight=1)
        row += 1

        self._mini_health = HealthRing(health_row, size=130)
        self._mini_health.grid(row=0, column=0, padx=(0, 16))

        health_info = ctk.CTkFrame(health_row, fg_color="transparent")
        health_info.grid(row=0, column=1, sticky="nsew")

        self._health_ai_text = ctk.CTkLabel(
            health_info, text=tr.T("main.health.loading"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=500
        )
        self._health_ai_text.pack(fill="x", pady=(4, 2))

        self._health_tip = ctk.CTkLabel(
            health_info, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
            text_color=Config.COLOR_ACCENT_CYAN,
            anchor="w"
        )
        self._health_tip.pack(fill="x")

        # ─── Sensor Status Bar ──────────────
        self._sensor_status = ctk.CTkLabel(
            container, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_ACCENT_ORANGE,
            anchor="w", justify="left"
        )
        self._sensor_status.grid(row=row, column=0, padx=28, pady=(0, 4), sticky="w")
        row += 1
        
        # ─── Gauge Grid (CPU, GPU, Disk) ──
        gauge_grid = ctk.CTkFrame(container, fg_color="transparent")
        gauge_grid.grid(row=row, column=0, padx=24, pady=(4, 12), sticky="ew")
        for c in range(3):
            gauge_grid.grid_columnconfigure(c, weight=1)
        row += 1
        
        self._cpu_gauge = CircularGauge(gauge_grid, size=110, title=tr.T("gauge.cpu"))
        self._cpu_gauge.grid(row=0, column=0, padx=4)
        self._gpu_gauge = CircularGauge(gauge_grid, size=110, title=tr.T("gauge.gpu"))
        self._gpu_gauge.grid(row=0, column=1, padx=4)
        self._disk_gauge = CircularGauge(gauge_grid, size=110, title=tr.T("gauge.disk"))
        self._disk_gauge.grid(row=0, column=2, padx=4)
        
        # ─── CPU ─────────────────────────
        SectionDivider(container, title=tr.T("cpu.title")).grid(
            row=row, column=0, padx=24, pady=(8, 4), sticky="ew")
        row += 1
        
        cpu_frame = GlassFrame(container)
        cpu_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        cpu_frame.grid_columnconfigure((1, 3, 5), weight=1)
        row += 1
        
        self._cpu_name = ctk.CTkLabel(cpu_frame, text=tr.T("cpu.detecting"),
                                       font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                                       text_color=Config.COLOR_TEXT_TERTIARY)
        self._cpu_name.grid(row=0, column=0, columnspan=6, padx=16, pady=(8, 4), sticky="w")
        
        labels = [
            (tr.T("cpu.temp"), "_cpu_temp_val", "\u00B0C"),
            (tr.T("cpu.freq"), "_cpu_freq_val", " GHz"),
            (tr.T("cpu.fan"), "_cpu_fan_val", " RPM"),
        ]
        for i, (lbl, attr, u) in enumerate(labels):
            ctk.CTkLabel(cpu_frame, text=lbl, font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                         text_color=Config.COLOR_TEXT_SECONDARY).grid(row=1, column=i*2, padx=(16, 4), pady=4, sticky="w")
            setattr(self, attr, ctk.CTkLabel(cpu_frame, text="--",
                                            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
                                            text_color=Config.COLOR_TEXT))
            getattr(self, attr).grid(row=1, column=i*2+1, padx=(0, 8), pady=4, sticky="w")
        
        # bottom spacer
        ctk.CTkLabel(cpu_frame, text="").grid(row=2, column=0, pady=(0, 4))
        
        # ─── GPU ─────────────────────────
        SectionDivider(container, title=tr.T("gpu.title")).grid(
            row=row, column=0, padx=24, pady=(8, 4), sticky="ew")
        row += 1
        
        gpu_frame = GlassFrame(container)
        gpu_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        gpu_frame.grid_columnconfigure((1, 3, 5, 7, 9), weight=1)
        row += 1
        
        self._gpu_name = ctk.CTkLabel(gpu_frame, text=tr.T("gpu.detecting"),
                                       font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                                       text_color=Config.COLOR_TEXT_TERTIARY)
        self._gpu_name.grid(row=0, column=0, columnspan=10, padx=16, pady=(8, 4), sticky="w")
        
        gpu_labels = [
            (tr.T("gpu.temp"), "_gpu_temp_val", "\u00B0C"),
            (tr.T("gpu.hotspot"), "_gpu_hotspot_val", "\u00B0C"),
            (tr.T("gpu.vram"), "_gpu_vram_val", "%"),
            (tr.T("gpu.fan"), "_gpu_fan_val", "%"),
            (tr.T("gpu.power"), "_gpu_power_val", "W"),
        ]
        for i, (lbl, attr, u) in enumerate(gpu_labels):
            ctk.CTkLabel(gpu_frame, text=lbl, font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                         text_color=Config.COLOR_TEXT_SECONDARY).grid(row=1, column=i*2, padx=(16, 4), pady=4, sticky="w")
            setattr(self, attr, ctk.CTkLabel(gpu_frame, text="--",
                                            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
                                            text_color=Config.COLOR_TEXT))
            getattr(self, attr).grid(row=1, column=i*2+1, padx=(0, 8), pady=4, sticky="w")
        
        ctk.CTkLabel(gpu_frame, text="").grid(row=2, column=0, pady=(0, 4))
        
        # ─── SSD ─────────────────────────
        SectionDivider(container, title=tr.T("ssd.title")).grid(
            row=row, column=0, padx=24, pady=(8, 4), sticky="ew")
        row += 1
        
        ssd_frame = GlassFrame(container)
        ssd_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        ssd_frame.grid_columnconfigure((1, 3), weight=1)
        row += 1
        
        ctk.CTkLabel(ssd_frame, text=tr.T("ssd.temp"), font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                     text_color=Config.COLOR_TEXT_SECONDARY).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")
        self._ssd_temp_val = ctk.CTkLabel(ssd_frame, text="--",
                                          font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                                          text_color=Config.COLOR_TEXT)
        self._ssd_temp_val.grid(row=0, column=1, padx=8, pady=(12, 4), sticky="w")
        
        ctk.CTkLabel(ssd_frame, text=tr.T("ssd.health"), font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                     text_color=Config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=(32, 4), pady=(12, 4), sticky="w")
        self._ssd_health_val = ctk.CTkLabel(ssd_frame, text="--",
                                            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                                            text_color=Config.COLOR_TEXT)
        self._ssd_health_val.grid(row=0, column=3, padx=8, pady=(12, 4), sticky="w")
        
        ctk.CTkLabel(ssd_frame, text="").grid(row=1, column=0, pady=(0, 8))
        
        # ─── Network ─────────────────────
        SectionDivider(container, title=tr.T("net.title")).grid(
            row=row, column=0, padx=24, pady=(8, 4), sticky="ew")
        row += 1
        
        net_frame = GlassFrame(container)
        net_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        net_frame.grid_columnconfigure((1, 3), weight=1)
        row += 1
        
        ctk.CTkLabel(net_frame, text=tr.T("net.download"), font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                     text_color=Config.COLOR_TEXT_SECONDARY).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")
        self._net_down_val = ctk.CTkLabel(net_frame, text="--",
                                          font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                                          text_color=Config.COLOR_TEXT)
        self._net_down_val.grid(row=0, column=1, padx=8, pady=(12, 4), sticky="w")
        
        ctk.CTkLabel(net_frame, text=tr.T("net.upload"), font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                     text_color=Config.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=(32, 4), pady=(12, 4), sticky="w")
        self._net_up_val = ctk.CTkLabel(net_frame, text="--",
                                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                                        text_color=Config.COLOR_TEXT)
        self._net_up_val.grid(row=0, column=3, padx=8, pady=(12, 4), sticky="w")
        
        ctk.CTkLabel(net_frame, text="").grid(row=1, column=0, pady=(0, 8))
        
        # ─── AI Analysis ─────────────────
        SectionDivider(container, title=tr.T("ai.title")).grid(
            row=row, column=0, padx=24, pady=(8, 4), sticky="ew")
        row += 1
        
        ai_frame = GlassFrame(container)
        ai_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        row += 1
        
        self._ai_text = ctk.CTkLabel(
            ai_frame, text=tr.T("main.ai.waiting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=600
        )
        self._ai_text.pack(padx=16, pady=16, fill="x")
        
        # ─── Notifications ───────────────
        self._notif_container = ctk.CTkFrame(container, fg_color="transparent")
        self._notif_container.grid(row=row, column=0, padx=24, pady=(0, 24), sticky="ew")
        row += 1
        
        self._no_notif = ctk.CTkLabel(
            self._notif_container, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY
        )
        self._no_notif.pack()
    
    def update_sensor_data(self, data):
        self._update_counter += 1
        
        def _safe(cb):
            try:
                cb()
            except Exception:
                pass
        
        self._time_label.configure(text=time.strftime("%H:%M:%S"))
        
        # Gauge values
        _safe(lambda: self._cpu_gauge.set_value(data.cpu_usage))
        _safe(lambda: self._gpu_gauge.set_value(data.gpu_usage))
        _safe(lambda: self._disk_gauge.set_value(data.disk_usage_percent))
        
        # Sensor status bar — only show truly missing (even admin LHM can't read)
        missing = []
        if data.cpu_temp < 0 and data.gpu_temp < 0:
            missing.append("Sensors unavailable")
        if missing:
            _safe(lambda: self._sensor_status.configure(
                text=tr.T("main.sensor.warning", items=", ".join(missing)),
                text_color=Config.COLOR_ACCENT_ORANGE))
        else:
            _safe(lambda: self._sensor_status.configure(text=""))
        
        # Names
        if self.sensor_manager:
            _safe(lambda: self._cpu_name.configure(text=self.sensor_manager.get_cpu_name()[:40]))
            _safe(lambda: self._gpu_name.configure(text=self.sensor_manager.get_gpu_name()[:40]))
        
        # CPU
        _safe(lambda: self._cpu_temp_val.configure(text=f"{data.cpu_temp:.0f}\u00B0C"))
        _safe(lambda: self._cpu_freq_val.configure(
            text=f"{data.cpu_freq/1000:.1f} GHz" if data.cpu_freq > 0 else "N/A"))
        _safe(lambda: self._cpu_fan_val.configure(
            text=f"{data.cpu_fan_rpm:.0f} RPM" if data.cpu_fan_rpm > 0 else "N/A"))
        
        # GPU
        _safe(lambda: self._gpu_temp_val.configure(text=f"{data.gpu_temp:.0f}\u00B0C"))
        _safe(lambda: self._gpu_hotspot_val.configure(
            text=f"{data.gpu_hotspot_temp:.0f}\u00B0C" if data.gpu_hotspot_temp > 0 else "--"))
        vram_pct = (data.gpu_vram_used / max(data.gpu_vram_total, 1)) * 100 if data.gpu_vram_total > 0 else 0
        _safe(lambda: self._gpu_vram_val.configure(text=f"{vram_pct:.0f}%"))
        _safe(lambda: self._gpu_fan_val.configure(
            text=f"%{data.gpu_fan_percent:.0f}" if data.gpu_fan_percent > 0 or data.gpu_temp > 0 else "N/A"))
        _safe(lambda: self._gpu_power_val.configure(
            text=f"{data.gpu_power:.0f}W" if data.gpu_power > 0 else "--"))
        
        # SSD
        _safe(lambda: self._ssd_temp_val.configure(
            text=f"{data.ssd_temp:.0f}\u00B0C" if data.ssd_temp > 0 else "N/A"))
        if data.ssd_health > 0:
            hc = Config.COLOR_ACCENT_GREEN if data.ssd_health > 70 else \
                 Config.COLOR_ACCENT_ORANGE if data.ssd_health > 40 else Config.COLOR_ACCENT_RED
            _safe(lambda: self._ssd_health_val.configure(
                text=f"{data.ssd_health:.0f}%", text_color=hc))
        else:
            _safe(lambda: self._ssd_health_val.configure(text="N/A"))
        
        # Network
        def fmt(bps):
            if bps >= 1_000_000: return f"{bps/1_000_000:.1f} MB/s"
            if bps >= 1_000: return f"{bps/1_000:.0f} KB/s"
            return f"{bps:.0f} B/s"
        _safe(lambda: self._net_down_val.configure(text=fmt(data.net_download_speed)))
        _safe(lambda: self._net_up_val.configure(text=fmt(data.net_upload_speed)))
        
        # Status
        if data.gpu_hotspot_temp > 100 or data.cpu_temp > 85 or data.gpu_temp > 85:
            _safe(lambda: self._status_label.configure(
                text=tr.T("status.critical"), text_color=Config.COLOR_ACCENT_RED))
            _safe(lambda: self._status_dot.configure(fg_color=Config.COLOR_ACCENT_RED))
        elif data.cpu_temp > 70 or data.gpu_temp > 70:
            _safe(lambda: self._status_label.configure(
                text=tr.T("status.caution"), text_color=Config.COLOR_ACCENT_ORANGE))
            _safe(lambda: self._status_dot.configure(fg_color=Config.COLOR_ACCENT_ORANGE))
        else:
            _safe(lambda: self._status_label.configure(
                text=tr.T("status.healthy"), text_color=Config.COLOR_ACCENT_GREEN))
            _safe(lambda: self._status_dot.configure(fg_color=Config.COLOR_ACCENT_GREEN))
        
        # Health ring + AI analysis
        if self.ai_engine:
            try:
                sensor_dict = data.to_dict()
                
                # Health score ring
                health = self.ai_engine.get_health_report(sensor_dict)
                if hasattr(health, 'overall'):
                    self._mini_health.set_score(health.overall, animate=True)
                    self._health_ring_shown = True
                
                # Health AI text
                analysis = self.ai_engine.get_system_health_summary(sensor_dict)
                self._ai_text.configure(text=analysis)
                
                # Health tip
                tip = getattr(health, 'maintenance_tip', '')
                if tip:
                    self._health_tip.configure(text=tip)
                
                scores = tr.T("health.scores",
                    cpu=getattr(health, 'cpu_score', 0),
                    gpu=getattr(health, 'gpu_score', 0),
                    ssd=getattr(health, 'ssd_score', 0),
                    cool=getattr(health, 'cooling_score', 0))
                self._health_ai_text.configure(text=scores)
            except Exception as ex:
                print(f"[AI] Analiz hatasi: {ex}")
    
    def update_notifications(self, notifications: list):
        for w in self._notif_container.winfo_children():
            w.destroy()
        
        if not notifications:
            self._no_notif = ctk.CTkLabel(
                self._notif_container,
                text=tr.T("main.no_notifications"),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                text_color=Config.COLOR_TEXT_TERTIARY
            )
            self._no_notif.pack(pady=8)
            return
        
        for n in notifications[:5]:
            sev = n.severity if hasattr(n, 'severity') else "info"
            title = n.title if hasattr(n, 'title') else ""
            msg = n.message if hasattr(n, 'message') else ""
            t = n.time_ago() if hasattr(n, 'time_ago') else ""
            card = NotificationCard(
                self._notif_container,
                title=title, message=msg,
                severity=sev, time_str=t
            )
            card.pack(fill="x", pady=2)

    def refresh_lang(self):
        pass
