"""
Desktop Application Coordinator for Project Jarvis.
Unites PyQt6 Application, Glass HUD, System Tray, Global Hotkeys, Single-Instance IPC, and the Async Core Engine.
"""

import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.engine import JarvisEngine
from ui.hud_window import JarvisHUDWindow
from ui.tray import JarvisTrayIcon
from ui.hotkey_listener import HotkeyListener

SINGLE_INSTANCE_PORT = 54123

class JarvisApp:
    def __init__(self):
        # 1. Create Qt Application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Allow background tray operation
        
        # 2. Create Floating HUD
        self.hud = JarvisHUDWindow(on_user_query=self._handle_user_query)
        
        # 3. Create Tray Icon
        self.tray = JarvisTrayIcon(
            on_toggle_hud=self.hud.toggle_summon,
            on_toggle_mic=self._handle_toggle_mic,
            on_exit=self.exit_app
        )
        self.tray.show()

        # 4. Create Core Engine
        self.engine = JarvisEngine(
            on_status_change=self._on_engine_status,
            on_transcript=self._on_engine_transcript
        )

        # 5. Create Global Hotkey Hook
        self.hotkey_listener = HotkeyListener(
            on_summon=lambda: self.hud.signals.summon_requested.emit(),
            on_push_to_talk=self._handle_ptt
        )

        # 6. Setup Single Instance Server
        self._server_socket = None
        self._start_ipc_server()

    def _start_ipc_server(self):
        """Listen on local port for signals from subsequent double-clicks/launches."""
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(('127.0.0.1', SINGLE_INSTANCE_PORT))
            self._server_socket.listen(3)
            
            def _ipc_listener():
                while self._server_socket:
                    try:
                        client, _ = self._server_socket.accept()
                        data = client.recv(1024)
                        if b"SUMMON" in data:
                            self.hud.signals.summon_requested.emit()
                        client.close()
                    except Exception:
                        break

            threading.Thread(target=_ipc_listener, name="JarvisIPCListener", daemon=True).start()
        except Exception as e:
            print(f"[JarvisApp] IPC Server warning: {e}")

    def _handle_user_query(self, query: str):
        self.engine.process_query(query)

    def _handle_toggle_mic(self):
        if self.engine._is_running:
            self.engine.recorder.stop()
            self.engine._is_running = False
            self.tray.showMessage("Jarvis", "Microphone listening paused.", JarvisTrayIcon.MessageIcon.Information, 1500)
        else:
            self.engine.recorder.start()
            self.engine._is_running = True
            self.tray.showMessage("Jarvis", "Microphone listening active.", JarvisTrayIcon.MessageIcon.Information, 1500)

    def _handle_ptt(self):
        self.hud.signals.summon_requested.emit()

    def _on_engine_status(self, status: str):
        self.hud.signals.status_updated.emit(status)

    def _on_engine_transcript(self, speaker: str, text: str):
        self.hud.signals.transcript_received.emit(speaker, text)

    def start(self):
        """Launch the entire Jarvis assistant system."""
        print("[JarvisApp] 🚀 Launching Jarvis GUI & Background Daemons...")
        
        # Start hotkeys
        self.hotkey_listener.start()
        
        # Start audio listening engine
        self.engine.start()
        
        # Display initial HUD
        self.hud.show()
        
        # Run Qt Event Loop
        sys.exit(self.app.exec())

    def exit_app(self):
        print("[JarvisApp] Shutting down...")
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
        self.hotkey_listener.stop()
        self.engine.stop()
        self.app.quit()


def ensure_single_instance() -> bool:
    """
    If Jarvis is already running, notify the running instance to summon HUD and return False.
    Otherwise return True to proceed with startup.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect(('127.0.0.1', SINGLE_INSTANCE_PORT))
        sock.sendall(b"SUMMON\n")
        sock.close()
        print("[Jarvis] ℹ️ Jarvis is already running. Brought existing window to front.")
        return False
    except Exception:
        # Not running -> safe to proceed
        return True


def run_app():
    if not ensure_single_instance():
        sys.exit(0)
    app = JarvisApp()
    app.start()


if __name__ == "__main__":
    run_app()
