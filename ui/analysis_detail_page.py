import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame, SectionDivider
import time


class AnalysisDetailPage(ctk.CTkScrollableFrame):
    def __init__(self, master, ai_engine=None, sensor_manager=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.ai = ai_engine
        self.sm = sensor_manager
        self.grid_columnconfigure(0, weight=1)
        self._build()
        self._update_counter = 0

    def _build(self):
        row = 0

        SectionDivider(self, title=tr.T("detail.game")).grid(
            row=row, column=0, padx=24, pady=(16, 4), sticky="ew")
        row += 1

        game_frame = GlassFrame(self)
        game_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        game_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        row += 1

        ctk.CTkLabel(game_frame, text=tr.T("analysis.game"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")
        self._game_name = ctk.CTkLabel(game_frame, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT)
        self._game_name.grid(row=0, column=1, padx=4, pady=(12, 4), sticky="w")

        ctk.CTkLabel(game_frame, text=tr.T("analysis.gpu"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=2, padx=(32, 4), pady=(12, 4), sticky="w")
        self._game_gpu = ctk.CTkLabel(game_frame, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT)
        self._game_gpu.grid(row=0, column=3, padx=4, pady=(12, 4), sticky="w")

        ctk.CTkLabel(game_frame, text=tr.T("detail.expected"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=1, column=0, padx=16, pady=4, sticky="w")
        self._game_expected = ctk.CTkLabel(game_frame, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT)
        self._game_expected.grid(row=1, column=1, padx=4, pady=4, sticky="w")

        ctk.CTkLabel(game_frame, text=tr.T("detail.verdict"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=1, column=2, padx=(32, 4), pady=4, sticky="w")
        self._game_verdict = ctk.CTkLabel(game_frame, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT)
        self._game_verdict.grid(row=1, column=3, padx=4, pady=4, sticky="w")

        ctk.CTkLabel(game_frame, text="").grid(row=2, column=0, pady=(0, 8))

        SectionDivider(self, title=tr.T("detail.power")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        power_frame = GlassFrame(self)
        power_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        power_frame.grid_columnconfigure((1, 3), weight=1)
        row += 1

        ctk.CTkLabel(power_frame, text=tr.T("analysis.gpu_power"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")
        self._power_gpu = ctk.CTkLabel(power_frame, text="--W",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            text_color=Config.COLOR_TEXT)
        self._power_gpu.grid(row=0, column=1, padx=4, pady=(12, 4), sticky="w")

        ctk.CTkLabel(power_frame, text=tr.T("detail.expected"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=2, padx=(32, 4), pady=(12, 4), sticky="w")
        self._power_expected = ctk.CTkLabel(power_frame, text="--W",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            text_color=Config.COLOR_TEXT)
        self._power_expected.grid(row=0, column=3, padx=4, pady=(12, 4), sticky="w")

        self._power_verdict = ctk.CTkLabel(power_frame, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_ACCENT_CYAN)
        self._power_verdict.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 12), sticky="w")

        SectionDivider(self, title=tr.T("detail.airflow")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        airflow_frame = GlassFrame(self)
        airflow_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        row += 1

        self._airflow_text = ctk.CTkLabel(
            airflow_frame, text=tr.T("detail.waiting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=700)
        self._airflow_text.pack(padx=16, pady=16, fill="x")

        SectionDivider(self, title=tr.T("detail.comparison")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        comp_frame = GlassFrame(self)
        comp_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        comp_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        row += 1

        labels = [
            (0, tr.T("detail.gpu_compare"), "_comp_gpu_label", (0, 1)),
            (1, tr.T("detail.cpu_compare"), "_comp_cpu_label", (2, 3)),
        ]
        for r_idx, title, attr, cols in labels:
            ctk.CTkLabel(comp_frame, text=title,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
                text_color=Config.COLOR_TEXT
            ).grid(row=r_idx*2, column=cols[0], columnspan=2, padx=16, pady=(12, 4), sticky="w")

            lbl = ctk.CTkLabel(comp_frame, text=tr.T("detail.waiting"),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_TEXT_SECONDARY,
                wraplength=300, justify="left")
            lbl.grid(row=r_idx*2+1, column=cols[0], columnspan=2, padx=16, pady=(0, 12), sticky="w")
            setattr(self, attr, lbl)

        SectionDivider(self, title=tr.T("detail.fault")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        fault_frame = GlassFrame(self)
        fault_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        fault_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        row += 1

        fault_items = [
            (0, lambda: tr.T("chat.quick.paste").split("  ")[-1], "_fault_paste_bar", "_fault_paste_lbl"),
            (1, lambda: tr.T("analysis.dust"), "_fault_dust_bar", "_fault_dust_lbl"),
            (2, lambda: tr.T("analysis.fan"), "_fault_fan_bar", "_fault_fan_lbl"),
            (3, lambda: tr.T("analysis.sensor"), "_fault_sensor_bar", "_fault_sensor_lbl"),
        ]
        for fi_idx, label_fn, bar_attr, lbl_attr in fault_items:
            c = fi_idx
            fi = ctk.CTkFrame(fault_frame, fg_color="transparent")
            fi.grid(row=0, column=c, sticky="nsew", padx=8, pady=12)
            fi.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(fi, text=label_fn(),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                text_color=Config.COLOR_TEXT_SECONDARY
            ).pack(anchor="center")

            bar = ctk.CTkProgressBar(fi, width=80, height=8,
                corner_radius=4, fg_color="#1E2230",
                progress_color=Config.COLOR_ACCENT_ORANGE)
            bar.pack(pady=6)
            bar.set(0.5)

            lbl = ctk.CTkLabel(fi, text="%0",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
                text_color=Config.COLOR_ACCENT_ORANGE)
            lbl.pack()

            setattr(self, bar_attr, bar)
            setattr(self, lbl_attr, lbl)

        ctk.CTkLabel(fault_frame, text="").grid(row=1, column=0, pady=(0, 4))

        SectionDivider(self, title=tr.T("detail.news")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        news_frame = GlassFrame(self)
        news_frame.grid(row=row, column=0, padx=24, pady=(0, 24), sticky="ew")
        row += 1

        self._news_container = ctk.CTkFrame(news_frame, fg_color="transparent")
        self._news_container.pack(padx=16, pady=16, fill="x")

        self._news_empty = ctk.CTkLabel(
            self._news_container, text=tr.T("detail.waiting"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY)
        self._news_empty.pack(pady=8)

    def update_sensor_data(self, data):
        self._update_counter += 1
        try:
            sensor_dict = data.to_dict() if hasattr(data, 'to_dict') else data.__dict__
            if not self.ai:
                return

            game_name = getattr(self.sm, '_current_game_process', "") if self.sm else ""
            if game_name:
                self._game_name.configure(text=game_name[:40])
                ga = self.ai.get_game_analysis(game_name, sensor_dict)
                if ga:
                    self._game_gpu.configure(text=f"{ga.gpu_temp:.0f}C")
                    self._game_expected.configure(text=f"{ga.expected_min:.0f}-{ga.expected_max:.0f}C")
                    v_color = Config.COLOR_ACCENT_GREEN if "Normal" in ga.verdict else (
                        Config.COLOR_ACCENT_ORANGE if "Yuksek" in ga.verdict else Config.COLOR_ACCENT_RED)
                    self._game_verdict.configure(text=ga.verdict, text_color=v_color)

            power = self.ai.get_power_analysis(sensor_dict)
            if power:
                self._power_gpu.configure(text=f"{power.gpu_power:.0f}W" if power.gpu_power > 0 else tr.T("detail.estimated"))
                self._power_expected.configure(text=f"{power.expected_gpu_power:.0f}W")
                self._power_verdict.configure(text=f"Toplam: ~{power.total_power:.0f}W | {power.verdict}")

            airflow = self.ai.get_airflow_analysis(sensor_dict)
            if airflow:
                text = f"CPU: {airflow.cpu_temp:.0f}C — {airflow.cpu_status}\nGPU: {airflow.gpu_temp:.0f}C — {airflow.gpu_status}\n\n{airflow.verdict}"
                if airflow.suggestion:
                    text += f"\n\n{airflow.suggestion}"
                self._airflow_text.configure(text=text) if hasattr(self, '_airflow_text') else None

            comp = self.ai.get_comparison(sensor_dict)
            if comp:
                prefix = tr.T("analysis.you")
                peers = tr.T("analysis.others")
                gpu_comp = comp.get("gpu")
                if gpu_comp:
                    self._comp_gpu_label.configure(
                        text=f"{prefix} {gpu_comp.user_temp:.0f}C | {peers} ~{gpu_comp.peer_avg_temp:.0f}C\n{gpu_comp.verdict}")
                cpu_comp = comp.get("cpu")
                if cpu_comp:
                    self._comp_cpu_label.configure(
                        text=f"{prefix} {cpu_comp.user_temp:.0f}C | {peers} ~{cpu_comp.peer_avg_temp:.0f}C\n{cpu_comp.verdict}")

            fault = self.ai.get_fault_prediction(sensor_dict)
            if fault:
                for attr_name, val in [
                    ("_fault_paste_bar", fault.thermal_paste),
                    ("_fault_dust_bar", fault.dust),
                    ("_fault_fan_bar", fault.fan_performance),
                    ("_fault_sensor_bar", fault.sensor_error),
                ]:
                    bar = getattr(self, attr_name, None)
                    if bar:
                        bar.set(val / 100.0)
                for attr_name, lbl_name, val in [
                    ("_fault_paste_lbl", "_fault_paste_bar", fault.thermal_paste),
                    ("_fault_dust_lbl", "_fault_dust_bar", fault.dust),
                    ("_fault_fan_lbl", "_fault_fan_bar", fault.fan_performance),
                    ("_fault_sensor_lbl", "_fault_sensor_bar", fault.sensor_error),
                ]:
                    lbl = getattr(self, attr_name, None)
                    if lbl:
                        lbl.configure(text=f"%{val:.0f}")

            if self._update_counter % 6 == 0:
                news = self.ai.get_news(force_refresh=False)
                for w in self._news_container.winfo_children():
                    w.destroy()
                if news:
                    for item in news[:5]:
                        src = getattr(item, 'source', '')
                        title = getattr(item, 'title', '')
                        summary = getattr(item, 'summary', '')
                        n_text = f"[{src}] {title}"
                        if summary:
                            n_text += f"\n{summary[:120]}"
                        ctk.CTkLabel(self._news_container, text=n_text,
                            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                            text_color=Config.COLOR_TEXT,
                            anchor="w", justify="left", wraplength=600
                        ).pack(fill="x", pady=2)
                else:
                    ctk.CTkLabel(self._news_container, text=tr.T("detail.news.none"),
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
                        text_color=Config.COLOR_TEXT_TERTIARY).pack(pady=8)

        except Exception as e:
            print(f"[AnalysisDetailPage] Hata: {e}")

    def refresh(self):
        pass

    def refresh_lang(self):
        pass
