import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame, SectionDivider, HealthRing
import time
from datetime import datetime


class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, master, ai_engine=None, sensor_manager=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.ai = ai_engine
        self.sm = sensor_manager
        self.grid_columnconfigure(0, weight=1)
        self._build()
        self._update_counter = 0

    def _build(self):
        row = 0

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.grid(row=row, column=0, padx=24, pady=(16, 8), sticky="ew")
        top_row.grid_columnconfigure(1, weight=1)
        row += 1

        health_frame = ctk.CTkFrame(top_row, fg_color="transparent", width=280)
        health_frame.grid(row=0, column=0, sticky="nsw")
        health_frame.grid_propagate(False)

        self._health_ring = HealthRing(health_frame, size=180)
        self._health_ring.pack(pady=(0, 4))

        self._health_summary = ctk.CTkLabel(
            health_frame, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            wraplength=240, justify="center"
        )
        self._health_summary.pack(pady=(0, 8))

        scores_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        scores_frame.grid(row=0, column=1, sticky="nsew", padx=(16, 0))

        score_items = [
            ("CPU", "_cpu_score_bar", "_cpu_score_lbl"),
            ("GPU", "_gpu_score_bar", "_gpu_score_lbl"),
            ("SSD", "_ssd_score_bar", "_ssd_score_lbl"),
            ("Sogutma", "_cool_score_bar", "_cool_score_lbl"),
        ]

        for i, (label, bar_attr, lbl_attr) in enumerate(score_items):
            r = i // 2
            c = i % 2
            item = ctk.CTkFrame(scores_frame, fg_color="transparent")
            item.grid(row=r, column=c, sticky="ew", padx=4, pady=4)
            item.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(item, text=label,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_TEXT_SECONDARY
            ).grid(row=0, column=0, padx=(0, 8), sticky="w")

            bar = ctk.CTkProgressBar(item, width=140, height=8,
                corner_radius=4, fg_color="#1E2230",
                progress_color=Config.COLOR_ACCENT_GREEN)
            bar.grid(row=0, column=1, sticky="ew", padx=(0, 8))
            bar.set(1.0)

            lbl = ctk.CTkLabel(item, text="100",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
                text_color=Config.COLOR_TEXT)
            lbl.grid(row=0, column=2, sticky="e")

            setattr(self, bar_attr, bar)
            setattr(self, lbl_attr, lbl)

        SectionDivider(self, title=tr.T("dashboard.trend")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        trend_frame = GlassFrame(self)
        trend_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        trend_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        row += 1

        trend_items = [
            (lambda: tr.T("gpu.temp").rstrip(':'), "_gpu_trend_today", "_gpu_trend_7d", "_gpu_trend_30d", "_gpu_trend_pred"),
            (lambda: tr.T("cpu.temp").rstrip(':'), "_cpu_trend_today", "_cpu_trend_7d", "_cpu_trend_30d", "_cpu_trend_pred"),
        ]

        for ti_idx, (title_fn, today_attr, week_attr, month_attr, pred_attr) in enumerate(trend_items):
            ctk.CTkLabel(trend_frame, text=title_fn(),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
                text_color=Config.COLOR_TEXT
            ).grid(row=ti_idx*2, column=0, columnspan=4, padx=16, pady=(12, 4), sticky="w")

            today_lbl = ctk.CTkLabel(trend_frame, text=tr.T("dashboard.today", val="--°C"),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_TEXT_SECONDARY)
            today_lbl.grid(row=ti_idx*2+1, column=0, padx=16, pady=(0, 12))

            week_lbl = ctk.CTkLabel(trend_frame, text=tr.T("dashboard.7days", val="--°C"),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_TEXT_SECONDARY)
            week_lbl.grid(row=ti_idx*2+1, column=1, padx=4, pady=(0, 12))

            month_lbl = ctk.CTkLabel(trend_frame, text=tr.T("dashboard.30days", val="--°C"),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_TEXT_SECONDARY)
            month_lbl.grid(row=ti_idx*2+1, column=2, padx=4, pady=(0, 12))

            pred_lbl = ctk.CTkLabel(trend_frame, text="--",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_ACCENT_CYAN)
            pred_lbl.grid(row=ti_idx*2+1, column=3, padx=4, pady=(0, 12))

            setattr(self, today_attr, today_lbl)
            setattr(self, week_attr, week_lbl)
            setattr(self, month_attr, month_lbl)
            setattr(self, pred_attr, pred_lbl)

        SectionDivider(self, title=tr.T("dashboard.digest")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        digest_frame = GlassFrame(self)
        digest_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        row += 1

        self._digest_text = ctk.CTkLabel(
            digest_frame, text=tr.T("dashboard.waiting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=700
        )
        self._digest_text.pack(padx=16, pady=16, fill="x")

        SectionDivider(self, title=tr.T("dashboard.timeline")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        timeline_frame = GlassFrame(self)
        timeline_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        row += 1

        self._timeline_container = ctk.CTkFrame(timeline_frame, fg_color="transparent")
        self._timeline_container.pack(padx=16, pady=16, fill="x")

        self._timeline_empty = ctk.CTkLabel(
            self._timeline_container, text=tr.T("detail.waiting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY
        )
        self._timeline_empty.pack(pady=8)

        self._timeline_summary = ctk.CTkLabel(
            timeline_frame, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_ACCENT_CYAN,
            anchor="w", justify="left", wraplength=700
        )
        self._timeline_summary.pack(padx=16, pady=(0, 16), fill="x")

        SectionDivider(self, title=tr.T("dashboard.room_temp")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        room_frame = GlassFrame(self)
        room_frame.grid(row=row, column=0, padx=24, pady=(0, 24), sticky="ew")
        row += 1

        room_inner = ctk.CTkFrame(room_frame, fg_color="transparent")
        room_inner.pack(padx=16, pady=16, fill="x")

        self._room_label = ctk.CTkLabel(room_inner, text=tr.T("dashboard.waiting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_SECONDARY)
        self._room_label.pack(anchor="w")

        room_btn_frame = ctk.CTkFrame(room_inner, fg_color="transparent")
        room_btn_frame.pack(fill="x", pady=(8, 0))

        self._room_entry = ctk.CTkEntry(room_btn_frame, width=80,
            placeholder_text="25", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        self._room_entry.pack(side="left", padx=(0, 8))

        self._room_btn = ctk.CTkButton(room_btn_frame, text=tr.T("dashboard.room_set"), width=70,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            fg_color=Config.COLOR_PRIMARY_DARK,
            hover_color=Config.COLOR_PRIMARY,
            command=self._set_room_temp)
        self._room_btn.pack(side="left")

        self._room_analysis = ctk.CTkLabel(room_inner, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_ACCENT_CYAN,
            anchor="w", justify="left", wraplength=700)
        self._room_analysis.pack(fill="x", pady=(8, 0))

    def _set_room_temp(self):
        try:
            temp = float(self._room_entry.get().strip())
            if 0 < temp < 60 and self.ai:
                self.ai.room_temp.set_room_temp(temp)
                self.ai.room_temp.set_enabled(True)
                self._room_label.configure(text=tr.T("dashboard.today", val=f"{temp}°C"))
                self._update_room_analysis()
                settings = Config.load_settings()
                settings["room_temp_enabled"] = True
                settings["room_temp_value"] = temp
                Config.save_settings(settings)
        except (ValueError, AttributeError):
            pass

    def _update_room_analysis(self):
        try:
            if not self.ai or not self.ai.room_temp.is_enabled():
                return
            room_temp = self.ai.room_temp.get_room_temp()
            sensor_data = self.sm.read_once() if self.sm else None
            if sensor_data:
                gpu_temp = getattr(sensor_data, 'gpu_temp', 0)
                cpu_temp = getattr(sensor_data, 'cpu_temp', 0)
                cpu_analysis = self.ai.room_temp.analyze_temp_with_ambient(cpu_temp, "CPU", 45)
                gpu_analysis = self.ai.room_temp.analyze_temp_with_ambient(gpu_temp, "GPU", 45)
                self._room_analysis.configure(text=f"{cpu_analysis}\n{gpu_analysis}")
        except Exception:
            pass

    def update_sensor_data(self, data):
        self._update_counter += 1
        if self._update_counter % 3 != 0:
            return

        try:
            sensor_dict = data.to_dict() if hasattr(data, 'to_dict') else data.__dict__

            if self.ai:
                health = self.ai.get_health_report(sensor_dict)
                ring = getattr(health, 'overall', 0)
                self._health_ring.set_score(ring, animate=True)

                for name, bar_attr, lbl_attr in [
                    ("cpu_score", "_cpu_score_bar", "_cpu_score_lbl"),
                    ("gpu_score", "_gpu_score_bar", "_gpu_score_lbl"),
                    ("ssd_score", "_ssd_score_bar", "_ssd_score_lbl"),
                    ("cooling_score", "_cool_score_bar", "_cool_score_lbl"),
                ]:
                    bar = getattr(self, bar_attr, None)
                    lbl = getattr(self, lbl_attr, None)
                    val = getattr(health, name, 100)
                    if bar:
                        bar.set(val / 100.0)
                        pct = val / 100.0
                        if pct <= 0:
                            p_color = "#3D1A6E"
                        elif pct < 0.5:
                            t = pct / 0.5
                            r = int(61 + (123 - 61) * t)
                            g = int(26 + (45 - 26) * t)
                            b = int(110 + (185 - 110) * t)
                            p_color = f"#{r:02x}{g:02x}{b:02x}"
                        elif pct < 0.85:
                            t = (pct - 0.5) / 0.35
                            r = int(123 + (156 - 123) * t)
                            g = int(45 + (39 - 45) * t)
                            b = int(185 + (230 - 185) * t)
                            p_color = f"#{r:02x}{g:02x}{b:02x}"
                        else:
                            t = (pct - 0.85) / 0.15
                            r = int(156 + (200 - 156) * t)
                            g = int(39 + (50 - 39) * t)
                            b = int(230 + (255 - 230) * t)
                            p_color = f"#{r:02x}{g:02x}{b:02x}"
                        bar.configure(progress_color=p_color)
                    if lbl:
                        lbl.configure(text=f"{val:.0f}")

                summary = getattr(health, 'summary', '')
                self._health_summary.configure(text=summary[:100])

                trend = self.ai.get_trend_report()
                if hasattr(trend, 'components'):
                    for comp_key, comp_name in [("gpu_core", "_gpu"), ("cpu", "_cpu")]:
                        td = trend.components.get(comp_key)
                        if td:
                            for attr_suffix, val in [
                                ("trend_today", tr.T("dashboard.today", val=f"{td.current:.0f}°C")),
                                ("trend_7d", tr.T("dashboard.7days", val=f"{td.week_ago:.0f}°C")),
                                ("trend_30d", tr.T("dashboard.30days", val=f"{td.month_ago:.0f}°C")),
                            ]:
                                lbl = getattr(self, f"{comp_name}_{attr_suffix}", None)
                                if lbl:
                                    lbl.configure(text=val)
                            pred_lbl = getattr(self, f"{comp_name}_trend_pred", None)
                            if pred_lbl and td.prediction_text:
                                pred_lbl.configure(text=td.prediction_text[:50])

                digest = self.ai.get_daily_digest(sensor_dict)
                if hasattr(digest, 'summary_lines') and digest.summary_lines:
                    text = "\n".join(digest.summary_lines[:8])
                    overall = digest.overall_emoji if hasattr(digest, 'overall_emoji') else ""
                    verdict = digest.verdict if hasattr(digest, 'verdict') else ""
                    self._digest_text.configure(text=f"{text}\n\n{overall} {verdict}")
                elif hasattr(digest, 'verdict'):
                    self._digest_text.configure(text=digest.verdict)

                events = self.ai.get_timeline_events(10)
                for w in self._timeline_container.winfo_children():
                    w.destroy()
                if events:
                    for ev in events[:8]:
                        ts = datetime.fromtimestamp(ev.timestamp).strftime("%H:%M")
                        ev_text = f"{ts}  {getattr(ev, 'icon', '') or ''} {ev.title}"
                        ctk.CTkLabel(self._timeline_container, text=ev_text,
                            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                            text_color=Config.COLOR_TEXT,
                            anchor="w").pack(fill="x", pady=1)
                    summary = self.ai.get_timeline_summary()
                    if summary:
                        self._timeline_summary.configure(text=summary[:120])
                else:
                    self._timeline_empty = ctk.CTkLabel(
                        self._timeline_container, text=tr.T("dashboard.timeline_empty"),
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                        text_color=Config.COLOR_TEXT_TERTIARY)
                    self._timeline_empty.pack(pady=8)

                self._update_room_analysis()

        except Exception as e:
            print(f"[DashboardPage] Guncelleme hatasi: {e}")

    def refresh_lang(self):
        pass
