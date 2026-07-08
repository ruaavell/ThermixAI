#!/usr/bin/env python3
"""
ThermixAI - AI Powered Hardware Monitoring Assistant
Main entry point for the application.
"""

import sys
import os
import ctypes

from config import Config

# Single-instance mutex — check BEFORE importing anything heavy
MUTEX_NAME = "Global\\ThermixAI_Mutex"
_mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
if _mutex_handle and ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    ctypes.windll.kernel32.CloseHandle(_mutex_handle)
    print("Program zaten çalışıyor.")
    sys.exit(0)
Config._mutex_handle = _mutex_handle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from ui.app import App


def main():
    try:
        app = App()
        app.run()
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Kritik hata: {e}")
        import traceback
        traceback.print_exc()
        input("\nDevam etmek için Enter'a basın...")


if __name__ == "__main__":
    main()
