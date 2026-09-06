"""
Global Hotkey Listener for Project Jarvis.
Monitors system-wide keyboard shortcuts via pynput to summon or dismiss the HUD.
"""

import threading
from typing import Callable, Optional
from pynput import keyboard
from core.config import config

class HotkeyListener:
    def __init__(
        self,
        on_summon: Optional[Callable[[], None]] = None,
        on_push_to_talk: Optional[Callable[[], None]] = None,
    ):
        self.on_summon = on_summon
        self.on_push_to_talk = on_push_to_talk
        
        self.summon_hotkey = config.summon_hotkey
        self.ptt_hotkey = config.push_to_talk_hotkey
        
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._thread: Optional[threading.Thread] = None
        self._is_running = False

    def _handle_summon(self):
        print(f"[Hotkey] 🎯 Summon hotkey triggered ({self.summon_hotkey})")
        if self.on_summon:
            try:
                self.on_summon()
            except Exception as e:
                print(f"[Hotkey] Error in summon callback: {e}")

    def _handle_ptt(self):
        print(f"[Hotkey] 🎙️ Push-to-talk triggered ({self.ptt_hotkey})")
        if self.on_push_to_talk:
            try:
                self.on_push_to_talk()
            except Exception as e:
                print(f"[Hotkey] Error in PTT callback: {e}")

    def start(self):
        """Start listening for global hotkeys in a background thread."""
        if self._is_running:
            return

        hotkey_map = {}
        if self.summon_hotkey:
            hotkey_map[self.summon_hotkey] = self._handle_summon
        if self.ptt_hotkey:
            hotkey_map[self.ptt_hotkey] = self._handle_ptt

        try:
            self._listener = keyboard.GlobalHotKeys(hotkey_map)
            self._listener.start()
            self._is_running = True
            print(f"[Hotkey] ✅ Global hotkey listener active: Summon='{self.summon_hotkey}'")
        except Exception as e:
            print(f"[Hotkey] ⚠️ Failed to bind global hotkeys: {e}")

    def stop(self):
        """Stop hotkey listener."""
        self._is_running = False
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
        print("[Hotkey] Hotkey listener stopped.")
