"""
Dynamic Futuristic Audio Visualizer Widget (Arc Reactor / Waveform) for Project Jarvis.
Rendered with PyQt6 QPainter with neon glows, breathing pulses, and state animations.
"""

import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QRadialGradient,
    QLinearGradient, QPainterPath
)

class AudioVisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 120)
        
        # States: "IDLE", "LISTENING", "THINKING", "SPEAKING"
        self.state = "IDLE"
        self._phase = 0.0
        self._rotation_angle = 0.0
        self._pulse_scale = 1.0
        self._wave_bars = [0.2] * 24
        
        # 60 FPS animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_frame)
        self._timer.start(16)

    def set_state(self, state: str):
        self.state = state.upper()
        self.update()

    def set_audio_level(self, level: float):
        """Update live audio input amplitude level (0.0 to 1.0)."""
        level = max(0.0, min(1.0, level))
        # Randomize wave bars slightly around level
        for i in range(len(self._wave_bars)):
            noise = random.uniform(0.7, 1.3)
            self._wave_bars[i] = min(1.0, level * noise + 0.1)

    def _animate_frame(self):
        self._phase += 0.06
        self._rotation_angle = (self._rotation_angle + (3.0 if self.state == "THINKING" else 0.8)) % 360.0
        
        # Pulse calculation
        if self.state == "LISTENING":
            self._pulse_scale = 1.0 + 0.15 * math.sin(self._phase * 2.5)
            # Jitter wave bars for listening effect
            for i in range(len(self._wave_bars)):
                self._wave_bars[i] = 0.2 + 0.5 * math.sin(self._phase * 3 + i * 0.4) ** 2
        elif self.state == "SPEAKING":
            self._pulse_scale = 1.0 + 0.20 * math.sin(self._phase * 3.5)
            for i in range(len(self._wave_bars)):
                self._wave_bars[i] = 0.3 + 0.7 * abs(math.sin(self._phase * 4 + i * 0.5))
        elif self.state == "THINKING":
            self._pulse_scale = 1.0 + 0.08 * math.sin(self._phase * 1.5)
        else: # IDLE
            self._pulse_scale = 1.0 + 0.04 * math.sin(self._phase * 1.0)
            for i in range(len(self._wave_bars)):
                self._wave_bars[i] = 0.15 + 0.05 * math.sin(self._phase + i)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipRect(self.rect())
        
        width = self.width()
        height = self.height()
        cx = width / 2.0
        cy = height / 2.0
        
        # Strictly clamp radius so it never exceeds widget bounds
        max_r = min(width, height) * 0.46
        base_radius = min(max_r / 1.35, min(width, height) * 0.28 * self._pulse_scale)

        # Color schemes based on state
        if self.state == "LISTENING":
            primary_color = QColor(0, 240, 255)      # Bright Neon Cyan
            glow_color = QColor(0, 200, 255, 60)
            core_color = QColor(200, 255, 255)
        elif self.state == "SPEAKING":
            primary_color = QColor(0, 255, 170)      # Neon Spring Green
            glow_color = QColor(0, 255, 170, 60)
            core_color = QColor(220, 255, 240)
        elif self.state == "THINKING":
            primary_color = QColor(255, 180, 0)      # Holographic Amber
            glow_color = QColor(255, 160, 0, 60)
            core_color = QColor(255, 240, 200)
        else: # IDLE
            primary_color = QColor(0, 150, 255)      # Deep Electric Blue
            glow_color = QColor(0, 120, 255, 35)
            core_color = QColor(180, 220, 255)

        # 1. Outer Ambient Radial Glow
        outer_r = min(max_r, base_radius * 1.30)
        radial_grad = QRadialGradient(cx, cy, outer_r)
        radial_grad.setColorAt(0.0, glow_color)
        radial_grad.setColorAt(0.6, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 15))
        radial_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(radial_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), outer_r, outer_r)

        # 2. Outer Rotating Segmented Tech Rings
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._rotation_angle)
        
        pen_ring = QPen(primary_color, 2.0)
        painter.setPen(pen_ring)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        num_segments = 8
        span_angle = 32
        for i in range(num_segments):
            start_ang = int(i * (360 / num_segments) * 16)
            painter.drawArc(
                QRectF(-base_radius, -base_radius, base_radius * 2, base_radius * 2),
                start_ang,
                int(span_angle * 16)
            )
        painter.restore()

        # 3. Inner Counter-Rotating Concentric Ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self._rotation_angle * 1.6)
        
        inner_r = base_radius * 0.70
        pen_inner = QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 180), 1.5, Qt.PenStyle.DashLine)
        painter.setPen(pen_inner)
        painter.drawEllipse(QRectF(-inner_r, -inner_r, inner_r * 2, inner_r * 2))
        painter.restore()

        # 4. Circular Arc Reactor Waveform Spikes
        num_bars = len(self._wave_bars)
        bar_radius = base_radius * 0.82
        for i in range(num_bars):
            angle_rad = (2 * math.pi / num_bars) * i + math.radians(self._rotation_angle * 0.3)
            bar_len = base_radius * 0.28 * self._wave_bars[i]
            
            x1 = cx + bar_radius * math.cos(angle_rad)
            y1 = cy + bar_radius * math.sin(angle_rad)
            x2 = cx + (bar_radius + bar_len) * math.cos(angle_rad)
            y2 = cy + (bar_radius + bar_len) * math.sin(angle_rad)
            
            bar_color = QColor(primary_color)
            bar_color.setAlpha(int(150 + 105 * self._wave_bars[i]))
            painter.setPen(QPen(bar_color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 5. Glowing Central Core Reactor
        core_r = base_radius * 0.40
        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, core_color)
        core_grad.setColorAt(0.5, primary_color)
        core_grad.setColorAt(1.0, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 100))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(core_grad))
        painter.drawEllipse(QPointF(cx, cy), core_r, core_r)
