"""
Windows System Tray Icon & Background Daemon for Project Jarvis.
Provides context menu, instant summon toggle, and background persistence.
"""

from typing import Optional, Callable
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QAction
from PyQt6.QtCore import Qt

class JarvisTrayIcon(QSystemTrayIcon):
    def __init__(
        self,
        on_toggle_hud: Optional[Callable[[], None]] = None,
        on_toggle_mic: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
        parent=None
    ):
        super().__init__(parent)
        self.on_toggle_hud = on_toggle_hud
        self.on_toggle_mic = on_toggle_mic
        self.on_exit = on_exit
        
        self._init_icon()
        self._init_menu()
        self.activated.connect(self._handle_tray_activated)

    def _init_icon(self):
        """Generate a crisp, glowing cyan reactor tray icon using QPixmap."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Outer ring
        painter.setBrush(QBrush(QColor(11, 16, 26)))
        painter.setPen(QColor(0, 240, 255))
        painter.drawEllipse(4, 4, 56, 56)
        
        # Glowing inner core
        painter.setBrush(QBrush(QColor(0, 240, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(20, 20, 24, 24)
        
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setToolTip("Jarvis AI Assistant (Running)")

    def _init_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #0b101a;
                color: #e0f0ff;
                border: 1px solid rgba(0, 240, 255, 0.4);
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 240, 255, 0.2);
                color: #00f0ff;
            }
        """)

        # Actions
        action_summon = QAction("👁️ Summon HUD (Ctrl+Shift+J)", self)
        if self.on_toggle_hud:
            action_summon.triggered.connect(self.on_toggle_hud)

        action_mic = QAction("🎙️ Toggle Listening", self)
        if self.on_toggle_mic:
            action_mic.triggered.connect(self.on_toggle_mic)

        menu.addAction(action_summon)
        menu.addAction(action_mic)
        menu.addSeparator()

        action_exit = QAction("🚪 Exit Jarvis", self)
        if self.on_exit:
            action_exit.triggered.connect(self.on_exit)
        menu.addAction(action_exit)

        self.setContextMenu(menu)

    def _handle_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click toggles HUD
            if self.on_toggle_hud:
                self.on_toggle_hud()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click guarantees HUD is shown and focused
            if self.on_toggle_hud:
                self.on_toggle_hud()

