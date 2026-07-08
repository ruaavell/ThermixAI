import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame
import time
import threading


class AIDoctorPage(ctk.CTkFrame):
    def __init__(self, master, ai_engine=None, sensor_manager=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.ai = ai_engine
        self.sm = sensor_manager
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(16, 8), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        self._doctor_title = ctk.CTkLabel(header, text=tr.T("doctor.title"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_XLARGE, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._doctor_title.pack(side="left")
        
        self._scan_btn = ctk.CTkButton(header, text=tr.T("doctor.scan"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            fg_color=Config.COLOR_PRIMARY_DARK,
            hover_color=Config.COLOR_PRIMARY,
            command=self._full_scan)
        self._scan_btn.pack(side="right")

        chat_container = ctk.CTkFrame(self, fg_color="transparent")
        chat_container.grid(row=1, column=0, padx=24, pady=(0, 8), sticky="nsew")
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_rowconfigure(0, weight=1)

        self._chat_area = ctk.CTkScrollableFrame(
            chat_container, fg_color="transparent",
            scrollbar_button_color=Config.COLOR_CARD,
            scrollbar_button_hover_color=Config.COLOR_CARD_HOVER)
        self._chat_area.grid(row=0, column=0, sticky="nsew")

        welcome_text = f"{tr.T('doctor.title')}'a Hos Geldiniz\n\n{tr.T('chat.subtitle')}\n\n{tr.T('doctor.subtitle')}"
        welcome = ctk.CTkLabel(self._chat_area, text=welcome_text if tr.lang == "tr" else
            f"Welcome to {tr.T('doctor.title')}\n\nWrite your computer problems here.\n\n{tr.T('doctor.subtitle')}",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=600)
        welcome.pack(pady=20)

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self._entry = ctk.CTkEntry(input_frame,
            placeholder_text=tr.T("doctor.placeholder"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            fg_color=Config.COLOR_CARD,
            text_color=Config.COLOR_TEXT,
            placeholder_text_color=Config.COLOR_TEXT_TERTIARY,
            border_width=1, border_color=Config.GLASS_BORDER,
            height=40)
        self._entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._entry.bind("<Return>", lambda e: self._send_query())

        self._send_btn = ctk.CTkButton(input_frame, text=tr.T("doctor.ask") if tr.lang == "en" else "Gonder",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            fg_color=Config.COLOR_PRIMARY_DARK,
            hover_color=Config.COLOR_PRIMARY,
            width=100, command=self._send_query)
        self._send_btn.grid(row=0, column=1)

    def _add_message(self, role, text):
        color = Config.COLOR_ACCENT_BLUE if role == "user" else Config.COLOR_ACCENT_GREEN
        prefix = "🧑 You" if tr.lang == "en" else "🧑 Siz" if role == "user" else f"🩺 {tr.T('doctor.title')}"
        frame = GlassFrame(self._chat_area)
        frame.pack(fill="x", pady=4, padx=4)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(padx=12, pady=10, fill="x")

        ctk.CTkLabel(inner, text=prefix,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
            text_color=color).pack(anchor="w")

        ctk.CTkLabel(inner, text=text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT,
            anchor="w", justify="left", wraplength=600).pack(fill="x", pady=(4, 0))

        self._chat_area.update()
        self._chat_area._parent_canvas.yview_moveto(1.0)

    def _send_query(self):
        query = self._entry.get().strip()
        if not query:
            return
        self._entry.delete(0, "end")
        self._add_message("user", query)
        self._add_message("assistant", tr.T("doctor.diagnosing"))
        threading.Thread(target=self._do_diagnose, args=(query,), daemon=True).start()

    def _do_diagnose(self, query):
        try:
            sensor_data = {}
            if self.sm:
                data = self.sm.read_once()
                sensor_data = data.to_dict() if hasattr(data, 'to_dict') else data.__dict__

            if self.ai:
                diagnosis = self.ai.get_doctor_diagnosis(query, sensor_data)
                text = f"**{diagnosis.main_issue}**\n\n"
                if diagnosis.evidence:
                    text += "\n".join(f"• {e}" for e in diagnosis.evidence[:5])
                    text += "\n\n"
                if diagnosis.recommendations:
                    text += "**Oneriler:**\n" + "\n".join(f"• {r}" for r in diagnosis.recommendations[:5])
            else:
                text = tr.T("chat.not_started")
        except Exception as e:
            text = tr.T("doctor.error", msg=str(e)[:80])

        self.after(0, lambda: self._update_last_message(text))

    def _full_scan(self):
        self._add_message("user", tr.T("doctor.scan") + (" (full system scan)" if tr.lang == "en" else ""))
        self._add_message("assistant", tr.T("doctor.fullscan"))
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        try:
            sensor_data = {}
            if self.sm:
                data = self.sm.read_once()
                sensor_data = data.to_dict() if hasattr(data, 'to_dict') else data.__dict__

            if self.ai:
                diagnosis = self.ai.ai_doctor.full_scan(sensor_data, self.ai.temp_history)
                text = f"**{diagnosis.main_issue}**\n\n"
                if diagnosis.evidence:
                    text += "\n".join(f"• {e}" for e in diagnosis.evidence[:8])
                    text += "\n\n"
                if diagnosis.recommendations:
                    text += "**Oneriler:**\n" + "\n".join(f"• {r}" for r in diagnosis.recommendations[:5])
            else:
                text = tr.T("chat.not_started")
        except Exception as e:
            text = tr.T("doctor.scan_error", msg=str(e)[:80])

        self.after(0, lambda: self._update_last_message(text))

    def _update_last_message(self, text):
        children = self._chat_area.winfo_children()
        if children:
            last = children[-1]
            lbl = last.winfo_children()[0].winfo_children()[-1] if last.winfo_children() else None
            if lbl and hasattr(lbl, 'configure'):
                lbl.configure(text=text)

    def refresh_lang(self):
        try:
            self._doctor_title.configure(text=tr.T("doctor.title"))
            self._scan_btn.configure(text=tr.T("doctor.scan"))
        except Exception:
            pass

    def refresh(self):
        pass
