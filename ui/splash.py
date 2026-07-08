import customtkinter as ctk
from config import Config
from modules.translator import tr
import os
import time


class SplashScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Config.COLOR_BG, **kwargs)
        
        self.pack(fill="both", expand=True)
        
        # Center content
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        # App logo
        logo_path = str(Config.ASSETS_DIR / "icons" / "logo.png")
        if os.path.exists(logo_path):
            from PIL import Image
            pil_logo = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(200, 56))
            ctk.CTkLabel(center, image=logo_ctk, text="").pack(pady=(0, 8))
        else:
            ctk.CTkLabel(
                center, text=Config.APP_NAME,
                font=(Config.FONT_FAMILY, 28, "bold"),
                text_color=Config.COLOR_TEXT
            ).pack(pady=(0, 8))
        
        # Tagline
        ctk.CTkLabel(
            center, text=tr.T("splash.title"),
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(pady=(4, 24))
        
        # Status text (updates during loading)
        self._status_var = ctk.StringVar(value=tr.T("splash.loading"))
        self._status_label = ctk.CTkLabel(
            center, textvariable=self._status_var,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            text_color=Config.COLOR_TEXT_SECONDARY
        )
        self._status_label.pack(pady=(0, 16))
        
        # Progress bar
        self._progress = ctk.CTkProgressBar(
            center, width=280, height=4,
            fg_color=Config.COLOR_CARD,
            progress_color=Config.COLOR_PRIMARY,
            mode="indeterminate"
        )
        self._progress.pack()
        self._progress.start()
        
        # Version
        ctk.CTkLabel(
            center, text="v1.0.0",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_TINY),
            text_color=Config.COLOR_TEXT_TERTIARY
        ).pack(pady=(32, 0))
    
    def set_status(self, text: str):
        self._status_var.set(text)
        self.master.update()
    
    def destroy(self):
        self._progress.stop()
        super().destroy()