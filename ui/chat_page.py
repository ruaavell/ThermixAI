import customtkinter as ctk
from config import Config
from modules.translator import tr
from ui.components import GlassFrame
import time
import threading


class ChatPage(ctk.CTkFrame):
    def __init__(self, master, ai_engine=None, sensor_manager=None, database=None, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        self.ai_engine = ai_engine
        self.sensor_manager = sensor_manager
        self.database = database
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        self._build_chat_area()
        self._build_quick_actions()
        self._build_input_area()
        
        self._add_welcome_message()
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=32, pady=(24, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, text="\uD83E\uDD16",
            font=("Segoe UI", 28)
        ).pack(side="left", padx=(0, 12))
        
        self._chat_title = ctk.CTkLabel(
            header, text=tr.T("chat.title"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_XLARGE, "bold"),
            text_color=Config.COLOR_TEXT
        )
        self._chat_title.pack(side="left")
        
        self._chat_subtitle = ctk.CTkLabel(
            header, text=tr.T("chat.subtitle"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_TERTIARY
        )
        self._chat_subtitle.pack(side="left", padx=12)
    
    def _build_chat_area(self):
        chat_container = GlassFrame(self)
        chat_container.grid(row=1, column=0, padx=24, pady=8, sticky="nsew")
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_rowconfigure(0, weight=1)
        
        self._chat_frame = ctk.CTkScrollableFrame(
            chat_container,
            fg_color="transparent",
            scrollbar_button_color=Config.COLOR_BORDER,
            scrollbar_button_hover_color=Config.COLOR_TEXT_SECONDARY
        )
        self._chat_frame.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self._chat_frame.grid_columnconfigure(1, weight=1)
    
    def _build_quick_actions(self):
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=2, column=0, padx=32, pady=(8, 4), sticky="ew")
        actions_frame.grid_columnconfigure(0, weight=1)

        scroll_container = ctk.CTkFrame(actions_frame, fg_color="transparent")
        scroll_container.pack(fill="x")

        actions = [
            (tr.T("chat.quick.status"), tr.T("chat.quick.status_q")),
            (tr.T("chat.quick.temp"), tr.T("chat.quick.temp_q")),
            (tr.T("chat.quick.paste"), tr.T("chat.quick.paste_q")),
            (tr.T("chat.quick.fan"), tr.T("chat.quick.fan_q")),
            (tr.T("chat.quick.perf"), tr.T("chat.quick.perf_q")),
        ]

        for label, query in actions:
            btn = ctk.CTkButton(
                scroll_container,
                text=label,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
                fg_color="transparent",
                hover_color="#1C1A34",
                text_color=Config.COLOR_TEXT_SECONDARY,
                border_color=Config.GLASS_BORDER,
                border_width=1,
                corner_radius=20,
                height=30,
                command=lambda q=query: self._quick_action_click(q)
            )
            btn.pack(side="left", padx=3)

    def _quick_action_click(self, query: str):
        self._input_entry.delete(0, "end")
        self._input_entry.insert(0, query)
        self._send_message()

    def _build_input_area(self):
        input_container = GlassFrame(self)
        input_container.grid(row=3, column=0, padx=32, pady=(4, 24), sticky="ew")
        input_container.grid_columnconfigure(0, weight=1)
        
        inner = ctk.CTkFrame(input_container, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        inner.grid_columnconfigure(0, weight=1)
        
        self._input_entry = ctk.CTkEntry(
            inner,
            placeholder_text=tr.T("chat.placeholder"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            fg_color=Config.COLOR_CARD,
            text_color=Config.COLOR_TEXT,
            border_color=Config.GLASS_BORDER,
            border_width=1,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            height=44
        )
        self._input_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self._input_entry.bind("<Return>", self._send_message)
        
        ctk.CTkButton(
            inner,
            text=tr.T("chat.send"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            fg_color=Config.COLOR_PRIMARY,
            hover_color=Config.COLOR_PRIMARY_DARK,
            corner_radius=Config.CORNER_RADIUS_SMALL,
            width=100,
            height=44,
            command=self._send_message
        ).grid(row=0, column=1)
    
    def _add_welcome_message(self):
        welcome = (
            "🎯 **" + tr.T("chat.title") + "**\n\n"
            + tr.T("chat.quick.status_q") + "\n\n"
            "💡 **" + tr.T("chat.quick.status") + "**\n"
            "• " + tr.T("chat.quick.temp_q") + "\n"
            "• " + tr.T("chat.quick.paste_q") + "\n"
            "• " + tr.T("chat.quick.fan_q") + "\n"
            "• " + tr.T("chat.quick.perf_q") + "\n"
        )
        self._add_message("assistant", welcome)
    
    def _add_message(self, role: str, text: str):
        frame = ctk.CTkFrame(self._chat_frame, fg_color="transparent")
        frame.grid(sticky="ew", pady=4)
        frame.grid_columnconfigure(1, weight=1)
        
        if role == "assistant":
            bubble = ctk.CTkFrame(
                frame, fg_color=Config.COLOR_CARD,
                corner_radius=Config.CORNER_RADIUS,
                border_color=Config.GLASS_BORDER,
                border_width=1
            )
            bubble.grid(row=0, column=0, padx=(0, 80), pady=2, sticky="w")
        else:
            bubble = ctk.CTkFrame(
                frame, fg_color="#1C1A34",
                corner_radius=Config.CORNER_RADIUS,
                border_color="#231F43",
                border_width=1
            )
            bubble.grid(row=0, column=1, padx=(80, 0), pady=2, sticky="e")
        
        label = ctk.CTkLabel(
            bubble,
            text=text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT,
            wraplength=500,
            justify="left"
        )
        label.pack(padx=16, pady=(12, 4))
        
        copy_btn = ctk.CTkLabel(
            bubble, text="\uD83D\uDCCB",
            font=(Config.FONT_FAMILY, 11),
            text_color=Config.COLOR_TEXT_TERTIARY,
            cursor="hand2"
        )
        copy_btn.pack(anchor="e", padx=(0, 8), pady=(0, 6))
        copy_btn.bind("<Button-1>", lambda e, t=text: self._copy_message(t))
        
        if self.database:
            self.database.save_chat_message(role, text)
        
        self._chat_frame._parent_canvas.yview_moveto(1.0)
    
    def _copy_message(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception:
            pass
    
    def _send_message(self, event=None):
        message = self._input_entry.get().strip()
        if not message:
            return
        
        self._input_entry.delete(0, "end")
        self._add_message("user", message)
        
        self._add_typing_indicator()
        
        thread = threading.Thread(target=self._process_query, args=(message,), daemon=True)
        thread.start()
    
    def _add_typing_indicator(self):
        self._typing_frame = ctk.CTkFrame(
            self._chat_frame, fg_color=Config.COLOR_CARD,
            corner_radius=Config.CORNER_RADIUS,
            border_color=Config.GLASS_BORDER,
            border_width=1
        )
        self._typing_frame.grid(sticky="w", pady=4, padx=(0, 80))
        
        ctk.CTkLabel(
            self._typing_frame,
            text=tr.T("chat.typing"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(padx=16, pady=12)
        
        self._chat_frame._parent_canvas.yview_moveto(1.0)
    
    def _remove_typing_indicator(self):
        if hasattr(self, '_typing_frame') and self._typing_frame:
            try:
                self._typing_frame.destroy()
            except Exception:
                pass
            self._typing_frame = None
    
    def _process_query(self, message: str):
        
        try:
            sensor_data = {}
            if self.sensor_manager:
                last_data = self.sensor_manager.get_last_data()
                if last_data:
                    sensor_data = last_data.to_dict()
            
            response = ""
            if self.ai_engine:
                response = self.ai_engine.analyze_chat_query(message, sensor_data)
            else:
                response = tr.T("chat.not_started")
            
            time.sleep(0.5)
            
            self.after(0, self._remove_typing_indicator)
            self.after(50, lambda: self._add_message("assistant", response))
            
        except Exception as e:
            self.after(0, self._remove_typing_indicator)
            self.after(50, lambda e=e: self._add_message("assistant",
                tr.T("chat.error", msg=str(e))))

    def refresh_lang(self):
        pass
