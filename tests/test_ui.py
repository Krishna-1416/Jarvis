"""
Diagnostic test for Jarvis PyQt6 UI, HUD Window, and Visualizer.
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from ui.hud_window import JarvisHUDWindow
from ui.tray import JarvisTrayIcon

def main():
    print("=== [UI] Testing Jarvis PyQt6 Desktop HUD & Tray ===")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    hud = JarvisHUDWindow(on_user_query=lambda q: print(f"HUD Query Received: {q}"))
    tray = JarvisTrayIcon(on_toggle_hud=hud.toggle_summon)
    
    print("  -> HUD Window initialized.")
    print("  -> System Tray Icon initialized.")
    
    # Test state transitions
    print("  -> Testing visualizer state switches...")
    hud.signals.status_updated.emit("LISTENING")
    hud.signals.status_updated.emit("THINKING")
    hud.signals.status_updated.emit("SPEAKING")
    hud.signals.status_updated.emit("IDLE")
    
    print("  -> Testing transcript insertion...")
    hud.signals.transcript_received.emit("USER", "Hello Jarvis!")
    hud.signals.transcript_received.emit("JARVIS", "Good day, sir. All systems nominal.")
    
    # Close after 1.5 seconds in test mode
    QTimer.singleShot(1500, app.quit)
    app.exec()
    
    print("[SUCCESS] UI Components & Glass HUD Diagnostic Completed.")

if __name__ == "__main__":
    main()
