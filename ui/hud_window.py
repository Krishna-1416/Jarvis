"""
Futuristic Glassmorphic Floating HUD Window for Project Jarvis.
Frameless, translucent, movable desktop overlay with real-time visualizer, chat feed,
expand/contract mode toggles, corner resize grips, and multi-edge drag resizing.
"""

import re
import sys
from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QLineEdit, QPushButton, QScrollArea, QFrame, QGraphicsDropShadowEffect, QSizeGrip
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont, QIcon, QKeyEvent, QCursor

from ui.audio_visualizer import AudioVisualizerWidget

class SignalBus(QObject):
    status_updated = pyqtSignal(str)
    transcript_received = pyqtSignal(str, str)
    summon_requested = pyqtSignal()

class JarvisHUDWindow(QWidget):
    # Resizing margins and directions
    EDGE_MARGIN = 8
    
    def __init__(self, on_user_query: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.on_user_query = on_user_query
        self.signals = SignalBus()
        
        # State tracking
        self._drag_pos = QPoint()
        self._resize_drag = False
        self._resize_edge = None
        self._resize_start_pos = QPoint()
        self._resize_start_geo = QRect()
        self._is_expanded = False
        self._normal_geo = QRect()
        
        self._init_window_properties()
        self._init_ui()
        self._connect_signals()

    def _init_window_properties(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        # Constraints
        self.setMinimumSize(340, 280)
        self.resize(480, 640)
        
        # Position in top-right of screen
        screen_geo = self.screen().availableGeometry()
        self.move(screen_geo.width() - 520, 50)
        self._normal_geo = self.geometry()

    def _init_ui(self):
        # Outer Container Frame with Glassmorphic styling
        self.container = QFrame(self)
        self.container.setObjectName("container")
        self.container.setMouseTracking(True)
        self.container.setStyleSheet("""
            QFrame#container {
                background-color: rgba(11, 16, 26, 0.94);
                border: 1.5px solid rgba(0, 240, 255, 0.38);
                border-radius: 18px;
            }
        """)
        
        # Glow drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 240, 255, 55))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(18, 14, 18, 14)
        container_layout.setSpacing(10)

        # 1. Header Bar with Controls
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        self.title_label = QLabel("JARVIS // OS")
        self.title_label.setStyleSheet("color: #00f0ff; font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: bold; letter-spacing: 2px;")
        
        self.status_badge = QLabel("● IDLE")
        self.status_badge.setStyleSheet("""
            background-color: rgba(0, 240, 255, 0.12);
            color: #00f0ff;
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 600;
        """)

        # Expand / Contract (Maximize/Restore) Button
        self.btn_expand = QPushButton("⤢")
        self.btn_expand.setToolTip("Expand / Contract Window Size")
        self.btn_expand.setFixedSize(24, 24)
        self.btn_expand.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 240, 255, 0.1);
                color: #00f0ff;
                border: 1px solid rgba(0, 240, 255, 0.25);
                border-radius: 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 240, 255, 0.3);
                color: #ffffff;
            }
        """)
        self.btn_expand.clicked.connect(self.toggle_expand_contract)

        # Close Button
        self.btn_close = QPushButton("✕")
        self.btn_close.setToolTip("Dismiss HUD (Ctrl+Shift+J)")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #88a0b0;
                border: none;
                border-radius: 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(255, 70, 70, 0.3);
                color: #ff5555;
            }
        """)
        self.btn_close.clicked.connect(self.hide)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_badge)
        header_layout.addWidget(self.btn_expand)
        header_layout.addWidget(self.btn_close)
        container_layout.addLayout(header_layout)

        # 2. Central Visualizer
        self.visualizer = AudioVisualizerWidget(self)
        self.visualizer.setFixedHeight(110)
        container_layout.addWidget(self.visualizer)

        # 3. Chat / Output Feed
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: rgba(6, 10, 18, 0.65);
                border: 1px solid rgba(0, 240, 255, 0.15);
                border-radius: 12px;
                color: #d0e8ff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                padding: 10px;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,0.1);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 240, 255, 0.3);
                border-radius: 3px;
            }
        """)
        self._append_message("JARVIS", "Online and standing by, sir. You can resize or drag this window freely.")
        container_layout.addWidget(self.chat_display, stretch=1)

        # 4. Prompt Input Bar with Bottom Corner Grip
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Jarvis or type command... (Enter)")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(14, 22, 36, 0.85);
                border: 1px solid rgba(0, 240, 255, 0.30);
                border-radius: 10px;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #00f0ff;
                background-color: rgba(18, 28, 48, 0.95);
            }
        """)
        self.input_field.returnPressed.connect(self._handle_send)

        self.btn_send = QPushButton("➤")
        self.btn_send.setFixedSize(36, 36)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00b4d8, stop:1 #0077b6);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00f0ff;
                color: #001824;
            }
        """)
        self.btn_send.clicked.connect(self._handle_send)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_send)
        container_layout.addLayout(input_layout)

        # Bottom Grip Row for clear visual resizing
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.addStretch()
        
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)
        self.size_grip.setStyleSheet("""
            QSizeGrip {
                image: none;
                background: transparent;
                width: 16px;
                height: 16px;
            }
        """)
        bottom_row.addWidget(self.size_grip)
        container_layout.addLayout(bottom_row)

    def _connect_signals(self):
        self.signals.status_updated.connect(self._update_status_ui)
        self.signals.transcript_received.connect(self._append_message)
        self.signals.summon_requested.connect(self.toggle_summon)

    def toggle_expand_contract(self):
        """Toggle between Expanded View and Compact View."""
        screen_geo = self.screen().availableGeometry()
        if not self._is_expanded:
            # Save normal geometry before expanding
            self._normal_geo = self.geometry()
            # Expand to spacious widescreen view
            target_w = min(780, screen_geo.width() - 80)
            target_h = min(840, screen_geo.height() - 80)
            self.setGeometry(
                screen_geo.width() - target_w - 40,
                40,
                target_w,
                target_h
            )
            self.btn_expand.setText("⤡")
            self._is_expanded = True
        else:
            # Contract back to standard HUD size
            if self._normal_geo.isValid():
                self.setGeometry(self._normal_geo)
            else:
                self.resize(480, 640)
            self.btn_expand.setText("⤢")
            self._is_expanded = False

    def _handle_send(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.input_field.clear()
        self._append_message("USER", text)
        if self.on_user_query:
            self.on_user_query(text)

    def _format_markdown_for_hud(self, text: str) -> str:
        """Convert markdown, bullet points, bold tags, and links into crisp HTML for the HUD."""
        formatted = re.sub(r'\*\*(.+?)\*\*', r'<b style="color: #00f0ff;">\1</b>', text)
        formatted = re.sub(
            r'\[([^\]]+)\]\((https?://[^\)]+)\)',
            r'<a href="\2" style="color: #00b4d8; text-decoration: none; font-weight: 500;">\1</a>',
            formatted
        )
        
        lines = formatted.split('\n')
        html_blocks = []
        
        for line in lines:
            l = line.strip()
            if not l:
                continue
            if re.match(r'^(?:<b[^>]*>)?Sources:?(?:</b>)?$', l, re.IGNORECASE) or "Sources:" in l:
                html_blocks.append("<div style='margin-top: 8px; margin-bottom: 4px; padding-top: 4px; border-top: 1px dashed rgba(0, 240, 255, 0.2); font-size: 11px; color: #8ecae6;'><b>Sources:</b></div>")
            elif l.startswith('•') or l.startswith('-') or l.startswith('*'):
                content = re.sub(r'^[•\-\*]\s*', '', l)
                html_blocks.append(
                    f"<div style='margin: 4px 0 4px 4px; line-height: 1.45;'>"
                    f"<span style='color: #00f0ff; font-weight: bold;'>▸</span> "
                    f"<span style='color: #e2f1ff;'>{content}</span>"
                    f"</div>"
                )
            else:
                html_blocks.append(f"<div style='margin-bottom: 4px; line-height: 1.45; color: #ffffff;'>{l}</div>")
                
        return "".join(html_blocks)

    def _append_message(self, speaker: str, text: str):
        body_html = self._format_markdown_for_hud(text)
        if speaker.upper() == "USER":
            formatted = (
                f"<div style='margin-bottom: 10px; padding: 6px 8px; background-color: rgba(0, 168, 255, 0.08); border-left: 2px solid #00a8ff; border-radius: 4px;'>"
                f"<span style='color: #00a8ff; font-weight: bold;'>You:</span> "
                f"<span style='color: #e2f1ff;'>{text}</span>"
                f"</div>"
            )
        else:
            formatted = (
                f"<div style='margin-bottom: 12px; padding: 8px 10px; background-color: rgba(0, 240, 255, 0.08); border-left: 3px solid #00f0ff; border-radius: 6px;'>"
                f"<div style='margin-bottom: 4px;'><span style='color: #00f0ff; font-weight: bold;'>Jarvis</span></div>"
                f"{body_html}"
                f"</div>"
            )
        
        self.chat_display.append(formatted)
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _update_status_ui(self, status: str):
        status_upper = status.upper()
        self.visualizer.set_state(status_upper)
        
        if status_upper == "LISTENING":
            self.status_badge.setText("🎙️ LISTENING")
            self.status_badge.setStyleSheet("background-color: rgba(0, 240, 255, 0.2); color: #00f0ff; border: 1px solid #00f0ff; border-radius: 10px; padding: 2px 8px; font-weight: 600;")
        elif status_upper == "THINKING":
            self.status_badge.setText("⚡ THINKING")
            self.status_badge.setStyleSheet("background-color: rgba(255, 180, 0, 0.2); color: #ffaa00; border: 1px solid #ffaa00; border-radius: 10px; padding: 2px 8px; font-weight: 600;")
        elif status_upper == "SPEAKING":
            self.status_badge.setText("🔊 SPEAKING")
            self.status_badge.setStyleSheet("background-color: rgba(0, 255, 170, 0.2); color: #00ffaa; border: 1px solid #00ffaa; border-radius: 10px; padding: 2px 8px; font-weight: 600;")
        else:
            self.status_badge.setText("● IDLE")
            self.status_badge.setStyleSheet("background-color: rgba(0, 240, 255, 0.1); color: #00f0ff; border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 10px; padding: 2px 8px; font-weight: 600;")

    def show_and_activate(self):
        """Always show and focus HUD without toggling."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.input_field.setFocus()

    def toggle_summon(self):
        """Summon or dismiss the HUD."""
        if self.isVisible():
            self.hide()
        else:
            self.show_and_activate()

    def mouseDoubleClickEvent(self, event):
        """Double clicking top header toggles expand/contract."""
        if event.pos().y() <= 45:
            self.toggle_expand_contract()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)


    # --- Edge & Corner Resizing / Dragging Logic ---

    def _get_edge_at_pos(self, pos: QPoint) -> Optional[str]:
        """Determine if mouse position is within the resize border margins."""
        w = self.width()
        h = self.height()
        m = self.EDGE_MARGIN
        x = pos.x()
        y = pos.y()

        on_left = x <= m
        on_right = x >= w - m
        on_top = y <= m
        on_bottom = y >= h - m

        if on_top and on_left:
            return "top_left"
        if on_top and on_right:
            return "top_right"
        if on_bottom and on_left:
            return "bottom_left"
        if on_bottom and on_right:
            return "bottom_right"
        if on_left:
            return "left"
        if on_right:
            return "right"
        if on_top:
            return "top"
        if on_bottom:
            return "bottom"
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_edge_at_pos(event.pos())
            if edge:
                self._resize_drag = True
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geo = self.geometry()
                event.accept()
                return

            # Window title bar dragging
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 1. Update cursor icon based on border position
        if not self._resize_drag:
            edge = self._get_edge_at_pos(event.pos())
            if edge in ("top_left", "bottom_right"):
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif edge in ("top_right", "bottom_left"):
                self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            elif edge in ("left", "right"):
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            elif edge in ("top", "bottom"):
                self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        # 2. Handle active border resizing drag
        if self._resize_drag and self._resize_edge:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            orig = self._resize_start_geo
            min_w = self.minimumWidth()
            min_h = self.minimumHeight()

            left = orig.left()
            top = orig.top()
            right = orig.right()
            bottom = orig.bottom()

            if "right" in self._resize_edge:
                right = max(left + min_w, orig.right() + delta.x())
            if "bottom" in self._resize_edge:
                bottom = max(top + min_h, orig.bottom() + delta.y())
            if "left" in self._resize_edge:
                left = min(right - min_w, orig.left() + delta.x())
            if "top" in self._resize_edge:
                top = min(bottom - min_h, orig.top() + delta.y())

            new_geo = QRect(QPoint(left, top), QPoint(right, bottom))
            self.setGeometry(new_geo)
            self._normal_geo = new_geo
            event.accept()
            return

        # 3. Handle window move drag
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self._normal_geo = self.geometry()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._resize_drag = False
        self._resize_edge = None
        self._drag_pos = QPoint()
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
