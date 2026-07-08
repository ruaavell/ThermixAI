import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame, SectionDivider
import time
import os


class ExpertPage(ctk.CTkScrollableFrame):
    def __init__(self, master, ai_engine=None, sensor_manager=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.ai = ai_engine
        self.sm = sensor_manager
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        row = 0

        SectionDivider(self, title=tr.T("expert.report")).grid(
            row=row, column=0, padx=24, pady=(16, 4), sticky="ew")
        row += 1

        report_frame = GlassFrame(self)
        report_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        row += 1

        report_inner = ctk.CTkFrame(report_frame, fg_color="transparent")
        report_inner.pack(padx=16, pady=16, fill="x")

        self._report_btn = ctk.CTkButton(report_inner, text=tr.T("expert.report"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            fg_color=Config.COLOR_PRIMARY_DARK,
            hover_color=Config.COLOR_PRIMARY,
            height=40, command=self._generate_report)
        self._report_btn.pack(side="left", padx=(0, 16))

        self._report_status = ctk.CTkLabel(report_inner, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_ACCENT_GREEN)
        self._report_status.pack(side="left")

        SectionDivider(self, title=tr.T("expert.age")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        age_frame = GlassFrame(self)
        age_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        age_frame.grid_columnconfigure((1, 3), weight=1)
        row += 1

        ctk.CTkLabel(age_frame, text=tr.T("detail.gpu_compare") + ":",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")
        self._age_gpu = ctk.CTkLabel(age_frame, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT)
        self._age_gpu.grid(row=0, column=1, padx=4, pady=(12, 4), sticky="w")

        ctk.CTkLabel(age_frame, text=tr.T("detail.cpu_compare") + ":",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        ).grid(row=0, column=2, padx=(32, 4), pady=(12, 4), sticky="w")
        self._age_cpu = ctk.CTkLabel(age_frame, text="--",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            text_color=Config.COLOR_TEXT)
        self._age_cpu.grid(row=0, column=3, padx=4, pady=(12, 4), sticky="w")

        self._maintenance_text = ctk.CTkLabel(age_frame, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_ACCENT_CYAN,
            anchor="w", justify="left", wraplength=700)
        self._maintenance_text.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 12), sticky="w")

        SectionDivider(self, title=tr.T("expert.daily_check")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        control_frame = GlassFrame(self)
        control_frame.grid(row=row, column=0, padx=24, pady=(0, 8), sticky="ew")
        row += 1

        self._control_btn = ctk.CTkButton(control_frame, text=tr.T("expert.daily_check"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            fg_color=Config.COLOR_PRIMARY_DARK,
            hover_color=Config.COLOR_PRIMARY,
            command=self._run_daily_check)
        self._control_btn.pack(padx=16, pady=(16, 4), anchor="w")

        self._control_result = ctk.CTkLabel(control_frame, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=700)
        self._control_result.pack(padx=16, pady=(4, 16), fill="x")

        SectionDivider(self, title=tr.T("expert.maintenance")).grid(
            row=row, column=0, padx=24, pady=(12, 4), sticky="ew")
        row += 1

        maint_frame = GlassFrame(self)
        maint_frame.grid(row=row, column=0, padx=24, pady=(0, 24), sticky="ew")
        row += 1

        maint_inner = ctk.CTkFrame(maint_frame, fg_color="transparent")
        maint_inner.pack(padx=16, pady=16, fill="x")

        self._last_clean_lbl = ctk.CTkLabel(maint_inner, text=tr.T("expert.last_clean", date="Unknown"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY)
        self._last_clean_lbl.pack(anchor="w", pady=2)

        self._last_paste_lbl = ctk.CTkLabel(maint_inner, text=tr.T("expert.last_paste", date="Unknown"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY)
        self._last_paste_lbl.pack(anchor="w", pady=2)

        self._maint_suggestion = ctk.CTkLabel(maint_inner, text="",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_ACCENT_CYAN,
            anchor="w", justify="left", wraplength=700)
        self._maint_suggestion.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(maint_inner, text=tr.T("dashboard.room_set") if tr.lang == "en" else "Temizlik Tarihini Ayarla",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            fg_color=Config.COLOR_CARD_HOVER,
            hover_color=Config.COLOR_PRIMARY_DARK,
            command=self._set_clean_date
        ).pack(anchor="w", pady=(8, 0))

    def _generate_report(self):
        if not self.ai or not self.sm:
            self._report_status.configure(text=tr.T("chat.not_started"))
            return
        try:
            data = self.sm.read_once()
            sensor_dict = data.to_dict() if hasattr(data, 'to_dict') else data.__dict__
            filepath = self.ai.generate_report(sensor_dict)
            if filepath and os.path.exists(filepath):
                fname = os.path.basename(filepath)
                self._report_status.configure(text=tr.T("expert.report.done", path=fname))
            else:
                self._report_status.configure(text=tr.T("expert.report.fail"))
        except Exception as e:
            self._report_status.configure(text=f"Error: {str(e)[:50]}")

    def _run_daily_check(self):
        if not self.ai or not self.sm:
            self._control_result.configure(text=tr.T("chat.not_started"))
            return
        try:
            data = self.sm.read_once()
            sensor_dict = data.to_dict() if hasattr(data, 'to_dict') else data.__dict__
            digest = self.ai.get_daily_digest(sensor_dict)
            lines = [f"{digest.overall_emoji} {digest.verdict}"] if hasattr(digest, 'overall_emoji') else []
            if hasattr(digest, 'summary_lines') and digest.summary_lines:
                lines.extend(digest.summary_lines[:8])
            self._control_result.configure(text="\n".join(lines) if lines else tr.T("detail.waiting"))
        except Exception as e:
            self._control_result.configure(text=f"Error: {str(e)[:80]}")

    def _set_clean_date(self):
        try:
            if self.ai:
                self.ai.hardware_age.set_last_clean(time.time())
                report = self.ai.get_hardware_age_report("gpu")
                self._last_clean_lbl.configure(text=tr.T("expert.last_clean", date="Today"))
                if report and report.maintenance_suggestion:
                    self._maint_suggestion.configure(text=report.maintenance_suggestion)
        except Exception:
            pass

    def update_sensor_data(self, data):
        try:
            if not self.ai:
                return
            sensor_dict = data.to_dict() if hasattr(data, 'to_dict') else data.__dict__

            for comp in ["gpu", "cpu"]:
                report = self.ai.get_hardware_age_report(comp)
                if report:
                    lbl = getattr(self, f"_age_{comp}", None)
                    if lbl and report.age_display:
                        lbl.configure(text=report.age_display)
                    if report.maintenance_suggestion:
                        self._maintenance_text.configure(text=report.maintenance_suggestion[:150])
                    if report.last_clean_display:
                        self._last_clean_lbl.configure(text=tr.T("expert.last_clean", date=report.last_clean_display))
                    if report.last_paste_display:
                        self._last_paste_lbl.configure(text=tr.T("expert.last_paste", date=report.last_paste_display))

        except Exception as e:
            print(f"[ExpertPage] Hata: {e}")

    def refresh(self):
        pass

    def refresh_lang(self):
        pass
