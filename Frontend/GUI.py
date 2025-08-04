#!/usr/bin/env python3
"""
JARVIS GUI - Advanced Iron Man Style Interface
Futuristic design with holographic elements, voice visualization, and advanced animations
"""

import sys
import time
import math
import random
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QPoint, QPointF, QRectF, QDateTime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QLineEdit,
    QVBoxLayout, QWidget, QHBoxLayout, QGraphicsDropShadowEffect,
    QMessageBox, QSplitter, QFrame, QGraphicsOpacityEffect, QSlider,
    QScrollArea, QSizePolicy, QGraphicsBlurEffect
)
from PyQt5.QtGui import (
    QColor, QPainter, QBrush, QPen, QPainterPath, QLinearGradient, QRadialGradient, QPixmap, QFontMetrics, QPalette, QFont, QTextCursor, QIcon,
    QConicalGradient, QPolygon
)
from dotenv import dotenv_values
import time
import numpy as np
import os
try:
    from PyQt5.QtConcurrent import QtConcurrent
    HAVE_QTCONCURRENT = True
except ImportError:
    HAVE_QTCONCURRENT = False
    from PyQt5.QtCore import QRunnable, QThreadPool
    class Runnable(QRunnable):
        def __init__(self, fn, *args, **kwargs):
            super().__init__()
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
        def run(self):
            self.fn(*self.args, **self.kwargs)
    def run_in_thread(fn, *args, **kwargs):
        QThreadPool.globalInstance().start(Runnable(fn, *args, **kwargs))

# Configuration
config = dotenv_values(".env")
Assistantname = config.get("Assistantname", "JARVIS")
Username = config.get("Username", "Sir")
FONT_FAMILY = "Segoe UI"

# JARVIS Color Scheme
JARVIS_BLUE = QColor(0, 150, 255)
JARVIS_DARK_BLUE = QColor(0, 100, 200)
JARVIS_LIGHT_BLUE = QColor(0, 200, 255)
JARVIS_WHITE = QColor(255, 255, 255)
JARVIS_GRAY = QColor(50, 50, 50)
JARVIS_DARK_GRAY = QColor(20, 20, 20)
JARVIS_GREEN = QColor(0, 255, 150)
JARVIS_RED = QColor(255, 50, 50)
JARVIS_BLACK = QColor(0, 0, 0)

class HolographicFrame(QFrame):
    """Holographic-style frame with glowing borders"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw glowing border
            pen = QPen(JARVIS_BLUE, 2)
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            
            # Create glow effect
            for i in range(5):
                alpha = 255 - (i * 50)
                pen.setColor(QColor(JARVIS_BLUE.red(), JARVIS_BLUE.green(), JARVIS_BLUE.blue(), alpha))
                pen.setWidth(2 + i)
                painter.setPen(pen)
                painter.drawRect(i, i, self.width() - 2*i, self.height() - 2*i)
        except Exception as e:
            print(f"[HolographicFrame] Paint error: {e}")

class AnimatedLabel(QLabel):
    """Animated label with typing effect"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.current_text = ""
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.type_next_char)
        self.typing_speed = 50  # ms per character
        
    def set_text_with_animation(self, text):
        self.full_text = text
        self.current_text = ""
        self.typing_timer.start(self.typing_speed)
        
    def type_next_char(self):
        if len(self.current_text) < len(self.full_text):
            self.current_text += self.full_text[len(self.current_text)]
            self.setText(self.current_text)
        else:
            self.typing_timer.stop()

class CircularButton(QPushButton):
    """Circular button with holographic effect"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(80, 80)
        self.setStyleSheet("""
            QPushButton {
                border-radius: 40px;
                background: qradialgradient(cx:0.5, cy:0.5, radius:1, 
                    stop:0 #4a90e2, stop:1 #357abd);
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #2c5aa0;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:1, 
                    stop:0 #5ba0f2, stop:1 #4a90e2);
                border: 2px solid #3c6ab0;
            }
            QPushButton:pressed {
                background: qradialgradient(cx:0.5, cy:0.5, radius:1, 
                    stop:0 #357abd, stop:1 #2c5aa0);
            }
        """)
        
        # Removed shadow effect to prevent QPainter conflicts

class AdvancedChatWidget(QWidget):
    """FUTURISTIC AI Chat Interface with Neural Network Visualization and Glassmorphism"""
    def __init__(self, backend_manager=None):
        super().__init__()
        self.backend_manager = backend_manager
        self.message_count = 0
        self.typing_animation_timer = QTimer()
        self.typing_animation_timer.timeout.connect(self.update_typing_animation)
        self.typing_dots = 0
        self.is_typing = False
        # Neural network visualization
        self.neural_timer = QTimer()
        self.neural_timer.timeout.connect(self.update_neural_network)
        self.neural_timer.start(30)
        self.neural_nodes = []
        self.neural_connections = []
        self.init_neural_network()
        # 3D/Parallax particle system
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(40)
        self.particles = []
        self.init_particles()
        # Scanline effect
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scanline)
        self.scan_timer.start(60)
        self.scan_y = 0
        self.setup_ui()
        self.setup_connections()
        self.setup_animations()
        # Animated energy waves
        self.energy_waves = [
            {'y': 80, 'amplitude': 18, 'frequency': 0.025, 'phase': 0.0, 'color': QColor(0,255,255,80)},
            {'y': 160, 'amplitude': 12, 'frequency': 0.018, 'phase': 1.5, 'color': QColor(0,255,150,60)},
            {'y': 240, 'amplitude': 22, 'frequency': 0.021, 'phase': 3.0, 'color': QColor(255,255,0,40)}
        ]
        self.energy_wave_timer = QTimer(self)
        self.energy_wave_timer.timeout.connect(self.animate_energy_waves)
        self.energy_wave_timer.start(30)

    def init_neural_network(self):
        for i in range(12):
            self.neural_nodes.append({
                'x': random.uniform(80, 920),
                'y': random.uniform(80, 620),
                'vx': random.uniform(-0.2, 0.2),
                'vy': random.uniform(-0.2, 0.2),
                'size': random.uniform(4, 10),
                'pulse': random.uniform(0, 2*math.pi),
                'color': random.choice([QColor(0,255,150), QColor(0,255,255), QColor(255,100,255)])
            })
        for i in range(18):
            node1 = random.choice(self.neural_nodes)
            node2 = random.choice(self.neural_nodes)
            if node1 != node2:
                self.neural_connections.append({
                    'node1': node1,
                    'node2': node2,
                    'strength': random.uniform(0.2, 1.0),
                    'pulse': random.uniform(0, 2*math.pi)
                })

    def update_neural_network(self):
        for node in self.neural_nodes:
            node['x'] += node['vx']
            node['y'] += node['vy']
            node['pulse'] += 0.07
            if node['x'] < 60 or node['x'] > 940:
                node['vx'] *= -1
            if node['y'] < 60 or node['y'] > 640:
                node['vy'] *= -1
            node['x'] = max(60, min(940, node['x']))
            node['y'] = max(60, min(640, node['y']))
        for connection in self.neural_connections:
            connection['pulse'] += 0.04
        self.update()

    def init_particles(self):
        for _ in range(20):
            self.particles.append({
                'x': random.uniform(0, 1000),
                'y': random.uniform(0, 700),
                'z': random.uniform(0, 100),
                'vx': random.uniform(-0.7, 0.7),
                'vy': random.uniform(-0.4, 0.4),
                'vz': random.uniform(-0.2, 0.2),
                'size': random.uniform(2, 7),
                'alpha': random.uniform(60, 180),
                'color': random.choice([
                    QColor(0,255,150), QColor(0,255,255), QColor(255,100,255), QColor(255,255,0)
                ])
            })

    def update_particles(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['z'] += p['vz']
            if p['z'] < 0: p['z'] = 100
            elif p['z'] > 100: p['z'] = 0
            if p['x'] < 0: p['x'] = self.width()
            elif p['x'] > self.width(): p['x'] = 0
            if p['y'] < 0: p['y'] = self.height()
            elif p['y'] > self.height(): p['y'] = 0
            p['alpha'] = max(40, min(180, 180 - p['z'] * 1.2))
        self.update()

    def update_scanline(self):
        self.scan_y += 3
        if self.scan_y > self.height():
            self.scan_y = 0
        self.update()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #000000, stop:0.2 #0a0a0a, stop:0.4 #1a1a2e, stop:0.6 #16213e, stop:0.8 #0f3460, stop:1 #000428);
                border-radius: 30px;
                border: 4px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:0.2 #00ff96, stop:0.4 #ff00ff, stop:0.6 #00ffff, stop:0.8 #ffff00, stop:1 #00d4ff);
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 25, 30, 25)
        title_label = QLabel(f"{Assistantname} NEURAL AI")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                font-size: 36px;
                font-weight: 900;
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        subtitle_label = QLabel("QUANTUM NEURAL NETWORK INTERFACE v2.0")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: 700;
                background: transparent;
                border: none;
                padding: 0;
                margin: 5px 0 0 0;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_frame)
        chat_frame = QFrame()
        chat_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000428, stop:0.2 #001428, stop:0.4 #001e3c, stop:0.6 #002346, stop:0.8 #001932, stop:1 #000428);
                border: 4px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff96, stop:0.25 #00d4ff, stop:0.5 #ff00ff, stop:0.75 #00ffff, stop:1 #00ff96);
                border-radius: 30px;
            }
        """)
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(25, 25, 25, 25)
        self.chat_area = QTextEdit()
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 15px;
                line-height: 1.6;
                padding: 30px;
            }
        """)
        chat_layout.addWidget(self.chat_area)
        layout.addWidget(chat_frame)

        # Professional input area with glass morphism
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:0.5 #00ff96, stop:1 #00d4ff);
                border-radius: 25px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(15)

        # Premium text input with modern styling
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #001428, stop:1 #001e3c);
                border: 2px solid #00ff96;
                border-radius: 20px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                padding: 15px 20px;
            }
            QLineEdit:focus {
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff96, stop:1 #00d4ff);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #001932, stop:1 #002346);
            }
            QLineEdit::placeholder {
                color: #888888;
                font-style: italic;
            }
        """)
        self.text_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.text_input)

        # Professional send button with gradient
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(100, 50)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #00ff96);
                color: #001428;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                box-shadow: 0 2px 8px #00d4ff44;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffaa, stop:1 #00e6ff);
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addWidget(input_frame)
        # ... keep rest of setup_ui unchanged ...
        # Add status area (quantum/futuristic look)
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0a0a0a, stop:0.3 #1a1a2e, stop:0.6 #16213e, stop:1 #0f3460);
                border: 3px solid #00ff96;
                border-radius: 25px;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(25, 20, 25, 20)
        self.status_label = QLabel("QUANTUM NEURAL NETWORK READY")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: 900;
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        layout.addWidget(status_frame)
        # Add voice visualizer below status
        self.voice_visualizer = ModernVoiceVisualizer()
        layout.addWidget(self.voice_visualizer)
        self.setLayout(layout)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Draw neural network connections
        for connection in self.neural_connections:
            node1 = connection['node1']
            node2 = connection['node2']
            strength = connection['strength']
            pulse = connection['pulse']
            alpha = int(60 + math.sin(pulse) * 40)
            color = QColor(0,255,150, alpha)
            painter.setPen(QPen(color, strength * 2))
            painter.drawLine(int(node1['x']), int(node1['y']), int(node2['x']), int(node2['y']))
        # Draw neural network nodes
        for node in self.neural_nodes:
            pulse = node['pulse']
            size = node['size'] + math.sin(pulse) * 2
            color = node['color']
            color.setAlpha(int(180 + math.sin(pulse) * 50))
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(node['x'] - size/2), int(node['y'] - size/2), int(size), int(size))
        # Draw particles with 3D effect
        for p in self.particles:
            color = p['color']
            color.setAlpha(int(p['alpha']))
            painter.setPen(QPen(color, p['size']))
            scale = 1 - (p['z'] / 100) * 0.5 if 'z' in p else 1.0
            x = int(p['x'] * scale)
            y = int(p['y'] * scale)
            size = int(p['size'] * scale)
            painter.drawEllipse(x - size, y - size, size * 2, size * 2)
        # Draw scanline overlay
        scan_color = QColor(0,255,255, 60)
        painter.setPen(QPen(scan_color, 3))
        painter.drawLine(0, self.scan_y, self.width(), self.scan_y)
        glow_color = QColor(0,255,255, 20)
        painter.setPen(QPen(glow_color, 10))
        painter.drawLine(0, self.scan_y, self.width(), self.scan_y)

    def setup_connections(self):
        """Setup connections to backend manager"""
        if self.backend_manager:
            self.backend_manager.chat_response.connect(self.handle_assistant_response)
            self.backend_manager.status_update.connect(self.handle_status_update)
            self.backend_manager.voice_input.connect(self.handle_voice_input)
            self.backend_manager.error_occurred.connect(self.handle_error)
    
    def setup_animations(self):
        """Setup QUANTUM UI animations"""
        # Only typing animation timer, no geometry animation
        self.typing_animation_timer.start(600)
        
    def update_typing_animation(self):
        """Update QUANTUM typing animation"""
        if self.is_typing:
            self.typing_dots = (self.typing_dots + 1) % 4
            dots = "." * self.typing_dots
            self.status_label.setText(f"QUANTUM PROCESSING{dots}")
        
    def send_message(self):
        """Send QUANTUM message with advanced animation"""
        text = self.text_input.text().strip()
        if text and self.backend_manager:
            self.text_input.clear()
            self.append_message("user", text)
            # QUANTUM button animation
            self.animate_quantum_button(self.send_button)
            # Show QUANTUM processing
            self.is_typing = True
            # Add placeholder assistant message
            self.placeholder_cursor = self.chat_area.textCursor()
            placeholder_html = '''
            <div style="margin: 25px 0; text-align: left;">
                <div style="
                    display: inline-block;
                    max-width: 80%;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #001428, stop:0.25 #001e3c, stop:0.5 #002346, 
                        stop:0.75 #001932, stop:1 #000428);
                    color: #888888;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    font-weight: 600;
                    line-height: 1.7;
                    padding: 20px 25px;
                    border-radius: 25px 25px 25px 5px;
                    border: 3px solid #00ffff;
                ">
                    QUANTUM is thinking...
                </div>
                <div style="
                    color: #00ffff;
                    font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    margin-top: 8px;
                    margin-left: 15px;
                    font-weight: 600;
                ">
                    NEURAL RESPONSE: ...
                </div>
            </div>
            '''
            cursor = self.chat_area.textCursor()
            cursor.movePosition(cursor.End)
            self.chat_area.setTextCursor(cursor)
            self.chat_area.insertHtml(placeholder_html)
            self.chat_area.ensureCursorVisible()
            if HAVE_QTCONCURRENT:
                QtConcurrent.run(self.backend_manager.process_input, text, "text")
            else:
                run_in_thread(self.backend_manager.process_input, text, "text")
    
    def handle_assistant_response(self, response):
        """Handle QUANTUM response"""
        self.is_typing = False
        # Replace placeholder with real response if present
        if hasattr(self, 'placeholder_cursor') and self.placeholder_cursor is not None:
            cursor = self.chat_area.textCursor()
            self.chat_area.setTextCursor(self.placeholder_cursor)
            self.chat_area.moveCursor(cursor.End, cursor.KeepAnchor)
            # Use QTextCursor.removeSelectedText()
            self.chat_area.textCursor().removeSelectedText()
            self.chat_area.setTextCursor(cursor)
            self.placeholder_cursor = None
        self.append_message("assistant", response)
    
    def handle_voice_input(self, voice_text):
        """Handle QUANTUM voice input"""
        self.append_message("user", voice_text)
        self.voice_visualizer.set_listening(False)
    
    def handle_error(self, error_msg):
        """Handle QUANTUM error"""
        self.is_typing = False
        self.append_message("assistant", f"QUANTUM ERROR: {error_msg}")
    
    def handle_status_update(self, status):
        """Handle QUANTUM status updates"""
        self.is_typing = False
        self.status_label.setText(f"QUANTUM: {status}")
        
        # Update voice visualizer
        status_lower = status.lower()
        if "listening" in status_lower:
            self.voice_visualizer.set_listening(True)
            self.voice_visualizer.set_speaking(False)
        elif "speaking" in status_lower or "started speaking" in status_lower:
            self.voice_visualizer.set_listening(False)
            self.voice_visualizer.set_speaking(True)
        elif "speech completed" in status_lower or "stopping speech" in status_lower:
            self.voice_visualizer.set_listening(False)
            self.voice_visualizer.set_speaking(False)
        else:
            self.voice_visualizer.set_listening(False)
            self.voice_visualizer.set_speaking(False)
    
    def append_message(self, role, message):
        """Append QUANTUM message with futuristic styling"""
        self.message_count += 1
        
        # QUANTUM timestamp
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        
        if role == "user":
            # QUANTUM user message
            message_html = f"""
            <div style="margin: 25px 0; text-align: right;">
                <div style="
                    display: inline-block;
                    max-width: 80%;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00ff96, stop:0.25 #00d4ff, stop:0.5 #ff00ff, 
                        stop:0.75 #00ffff, stop:1 #00ff96);
                    color: #000000;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    font-weight: 700;
                    line-height: 1.7;
                    padding: 20px 25px;
                    border-radius: 25px 25px 5px 25px;
                    border: 2px solid #00ffff;
                ">
                    {message}
                </div>
                <div style="
                    color: #00ffff;
                    font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    margin-top: 8px;
                    margin-right: 15px;
                    font-weight: 600;
                ">
                    QUANTUM TIMESTAMP: {timestamp}
                </div>
            </div>
            """
        else:
            # QUANTUM assistant message
            message_html = f"""
            <div style="margin: 25px 0; text-align: left;">
                <div style="
                    display: inline-block;
                    max-width: 80%;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #001428, stop:0.25 #001e3c, stop:0.5 #002346, 
                        stop:0.75 #001932, stop:1 #000428);
                    color: #ffffff;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    font-weight: 600;
                    line-height: 1.7;
                    padding: 20px 25px;
                    border-radius: 25px 25px 25px 5px;
                    border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00ff96, stop:0.3 #00d4ff, stop:0.6 #ff00ff, stop:1 #00ffff);
                ">
                    {message}
                </div>
                <div style="
                    color: #00ffff;
                    font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    margin-top: 8px;
                    margin-left: 15px;
                    font-weight: 600;
                ">
                    NEURAL RESPONSE: {timestamp}
                </div>
            </div>
            """
        
        # Add message with QUANTUM scrolling
        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.End)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.insertHtml(message_html)
        
        # QUANTUM scroll to bottom
        scrollbar = self.chat_area.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
        else:
            self.chat_area.ensureCursorVisible()
        
        # QUANTUM message animation
        QTimer.singleShot(150, self.animate_quantum_message)

    def toggle_mic(self):
        """Toggle QUANTUM microphone"""
        if self.backend_manager:
            if self.backend_manager.is_running:
                # Stop QUANTUM listening
                self.backend_manager.is_running = False
                self.mic_button.setText("🔇 OFFLINE")
                self.mic_button.setStyleSheet("""
                    QPushButton {
                        background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                            stop:0 #ff3232, stop:0.3 #cc2626, stop:0.6 #992020, stop:1 #ff3232);
                        color: #ffffff;
                        font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                        font-weight: 900;
                        font-size: 14px;
                        border: 3px solid #992020;
                        border-radius: 20px;
                        padding: 15px 20px;
                    }
                    QPushButton:hover {
                        background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                            stop:0 #ff4242, stop:0.3 #ff3232, stop:0.6 #cc2626, stop:1 #ff4242);
                        border: 3px solid #cc2626;
                    }
                """)
                self.status_label.setText("QUANTUM NEURAL OFFLINE")
                self.voice_visualizer.set_listening(False)
            else:
                # Start QUANTUM listening
                self.backend_manager.is_running = True
                self.backend_manager.start_voice_listening()
                self.mic_button.setText("🧠 NEURAL")
                self.mic_button.setStyleSheet("""
                    QPushButton {
                        background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                            stop:0 #00ff96, stop:0.3 #00d4ff, stop:0.6 #ff00ff, stop:1 #00ffff);
                        color: #000000;
                        font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
                        font-weight: 900;
                        font-size: 14px;
                        border: 3px solid #00ff96;
                        border-radius: 20px;
                        padding: 15px 20px;
                    }
                    QPushButton:hover {
                        background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                            stop:0 #00ffff, stop:0.3 #ff00ff, stop:0.6 #00d4ff, stop:1 #00ff96);
                        border: 3px solid #00ffff;
                    }
                """)
                self.status_label.setText("QUANTUM NEURAL ACTIVE")
                self.voice_visualizer.set_listening(True)
        
        # QUANTUM button animation
        QTimer.singleShot(150, lambda: self.animate_quantum_button(self.mic_button))
    
    def animate_quantum_button(self, button):
        """QUANTUM button press animation"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        animation.setStartValue(button.geometry())
        animation.setEndValue(button.geometry().adjusted(3, 3, -3, -3))
        animation.setEasingCurve(QEasingCurve.OutBack)
        animation.start()
    
    def animate_quantum_status(self):
        """QUANTUM status indicator pulse"""
        current_rect = self.status_label.geometry()
        self.pulse_animation.setStartValue(current_rect)
        self.pulse_animation.setEndValue(current_rect.adjusted(0, 0, 5, 5))
        self.pulse_animation.start()
    
    def animate_quantum_message(self):
        """QUANTUM message appearance"""
        original_style = self.chat_area.styleSheet()
        self.chat_area.setStyleSheet(original_style + "border: 4px solid #00ffff;")
        QTimer.singleShot(400, lambda: self.chat_area.setStyleSheet(original_style))
    
    def animate_quantum_error(self):
        """QUANTUM error state animation"""
        self.status_label.setStyleSheet("color: #ff3232; font-weight: 900;")
        QTimer.singleShot(1200, lambda: self.status_label.setStyleSheet("color: #00ffff; font-weight: 900;"))
    
    def paintEvent(self, event):
        """QUANTUM paint event with neural network and holographic effects"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw neural network connections
        for connection in self.neural_connections:
            node1 = connection['node1']
            node2 = connection['node2']
            strength = connection['strength']
            pulse = connection['pulse']
            
            # Dynamic connection color based on pulse
            alpha = int(50 + math.sin(pulse) * 30)
            color = QColor(0, 255, 150, alpha)
            painter.setPen(QPen(color, strength * 2))
            painter.drawLine(int(node1['x']), int(node1['y']), int(node2['x']), int(node2['y']))
        
        # Draw neural network nodes
        for node in self.neural_nodes:
            pulse = node['pulse']
            size = node['size'] + math.sin(pulse) * 2
            color = node['color']
            color.setAlpha(int(150 + math.sin(pulse) * 50))
            
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(node['x'] - size/2), int(node['y'] - size/2), int(size), int(size))
        
        # Draw holographic particles with 3D effect
        for p in self.particles:
            color = p['color']
            color.setAlpha(int(p['alpha']))
            painter.setPen(QPen(color, p['size']))
            scale = 1 - (p['z'] / 100) * 0.5 if 'z' in p else 1.0
            x = int(p['x'] * scale)
            y = int(p['y'] * scale)
            size = int(p['size'] * scale)
            painter.drawEllipse(x - size, y - size, size * 2, size * 2)
        
        # Draw energy field waves
        for wave in self.energy_waves:
            color = wave['color']
            painter.setPen(QPen(color, 2))
            
            path = QPainterPath()
            path.moveTo(0, wave['y'])
            
            for x in range(0, self.width(), 5):
                y = wave['y'] + math.sin(x * wave['frequency'] + wave['phase']) * wave['amplitude']
                path.lineTo(x, y)
            
            painter.drawPath(path)
        
        # Draw scanning line effect
        scan_color = QColor(0, 255, 255, 100)
        painter.setPen(QPen(scan_color, 3))
        painter.drawLine(0, self.scan_y, self.width(), self.scan_y)
        
        # Draw scan line glow
        glow_color = QColor(0, 255, 255, 30)
        painter.setPen(QPen(glow_color, 10))
        painter.drawLine(0, self.scan_y, self.width(), self.scan_y)

    def animate_energy_waves(self):
        for wave in self.energy_waves:
            wave['phase'] += 0.08
        self.update()

class UltraJarvisBlobWidget(QWidget):
    """Advanced market-ready JARVIS blob with organic morphing, particles, and professional effects."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 600)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # 60 FPS for smooth professional animation
        self.phase = 0
        self.state = 'idle'  # 'idle', 'listening', 'speaking', 'sleeping', 'processing'
        self.radius = 200
        self.center = QPoint(self.width() // 2, self.height() // 2)
        
        # Advanced color system
        self.base_color = QColor(0, 150, 255)  # JARVIS blue
        self.inner_color = QColor(0, 200, 255)  # Bright center
        self.outer_color = QColor(0, 100, 200)  # Darker edge
        self.glow_color = QColor(0, 255, 255)   # Cyan glow
        self.energy_color = QColor(0, 255, 150) # Green energy
        self.shadow_color = QColor(0, 30, 60, 120)  # Dark shadow
        
        # Interactive states
        self.is_hovered = False
        self.is_clicked = False
        self.hover_amplitude = 0.0
        self.click_amplitude = 0.0
        
        # Advanced animation system
        self.breathing_phase = 0
        self.pulse_phase = 0
        self.glow_phase = 0
        self.morph_phase = 0
        self.particle_phase = 0
        
        # Random movement system for natural behavior
        self.random_generator = random.Random()
        self.movement_noise = [self.random_generator.uniform(0, 2*math.pi) for _ in range(20)]
        self.natural_breathing_rate = self.random_generator.uniform(0.8, 1.2)
        self.natural_pulse_rate = self.random_generator.uniform(0.7, 1.3)
        self.movement_timer = 0
        self.random_shift_phases = [self.random_generator.uniform(0, 2*math.pi) for _ in range(8)]
        
        # Random movement system
        self.random_seed = random.randint(1, 10000)
        self.random_generator = random.Random(self.random_seed)
        self.movement_noise = [self.random_generator.uniform(0, 2*math.pi) for _ in range(20)]
        self.noise_phases = [self.random_generator.uniform(0, 2*math.pi) for _ in range(15)]
        self.organic_offsets = [self.random_generator.uniform(-0.5, 0.5) for _ in range(30)]
        
        # Natural movement patterns
        self.morph_complexity = self.random_generator.uniform(0.6, 1.4)
        
        # Organic shape parameters
        self.n_points = 60
        self.morph_intensity = 0.0
        self.organic_noise = 0.0
        
        # Particle system with randomness
        self.particles = []
        self.max_particles = 20
        self.particle_life = 0.0
        
        # Advanced lighting with random positioning
        self.light_sources = []
        self.reflection_phase = 0
        self.caustics_phase = 0
        
        # Performance optimization
        self.last_update = time.time()
        self.frame_count = 0
        
        # Random movement timers
        self.random_shift_timer = 0
        self.natural_shift_phases = [self.random_generator.uniform(0, 2*math.pi) for _ in range(8)]
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to open chat interface")
        
        # Initialize particle system
        self.init_particles()
        self.init_lighting()

    def init_particles(self):
        """Initialize particle system for ambient effects with randomness"""
        for i in range(self.max_particles):
            particle = {
                'x': self.random_generator.uniform(-self.radius, self.radius),
                'y': self.random_generator.uniform(-self.radius, self.radius),
                'vx': self.random_generator.uniform(-0.8, 0.8),
                'vy': self.random_generator.uniform(-0.8, 0.8),
                'life': self.random_generator.uniform(0, 1.0),
                'size': self.random_generator.uniform(1.5, 7),
                'color': QColor(0, 255, 255, self.random_generator.randint(20, 100)),
                'individual_phase': self.random_generator.uniform(0, 2*math.pi),
                'movement_pattern': self.random_generator.choice(['circular', 'linear', 'chaotic'])
            }
            self.particles.append(particle)

    def init_lighting(self):
        """Initialize advanced lighting system with random positioning"""
        self.light_sources = [
            {
                'x': self.random_generator.uniform(-0.4, 0.4), 
                'y': self.random_generator.uniform(-0.4, 0.4), 
                'intensity': self.random_generator.uniform(0.6, 1.0), 
                'color': QColor(255, 255, 255, self.random_generator.randint(40, 80)),
                'phase': self.random_generator.uniform(0, 2*math.pi),
                'speed': self.random_generator.uniform(0.5, 1.5)
            },
            {
                'x': self.random_generator.uniform(-0.3, 0.3), 
                'y': self.random_generator.uniform(-0.3, 0.3), 
                'intensity': self.random_generator.uniform(0.4, 0.8), 
                'color': QColor(0, 255, 255, self.random_generator.randint(30, 60)),
                'phase': self.random_generator.uniform(0, 2*math.pi),
                'speed': self.random_generator.uniform(0.3, 1.2)
            },
            {
                'x': self.random_generator.uniform(-0.2, 0.2), 
                'y': self.random_generator.uniform(-0.2, 0.2), 
                'intensity': self.random_generator.uniform(0.3, 0.7), 
                'color': QColor(0, 200, 255, self.random_generator.randint(20, 50)),
                'phase': self.random_generator.uniform(0, 2*math.pi),
                'speed': self.random_generator.uniform(0.4, 1.0)
            }
        ]

    def set_state(self, state):
        self.state = state
        if state == 'speaking':
            self.morph_intensity = 1.0
            self.organic_noise = 0.8
            # Add random speaking patterns
            self.add_random_speaking_effects()
        elif state == 'listening':
            self.morph_intensity = 0.6
            self.organic_noise = 0.4
            # Add random listening patterns
            self.add_random_listening_effects()
        elif state == 'processing':
            self.morph_intensity = 0.3
            self.organic_noise = 0.2
        else:
            self.morph_intensity = 0.0
            self.organic_noise = 0.0
        self.update()

    def add_random_speaking_effects(self):
        """Add random effects when speaking starts"""
        # Randomly adjust particle behavior
        for particle in self.particles:
            if self.random_generator.random() < 0.3:  # 30% chance
                particle['vx'] += self.random_generator.uniform(-1.0, 1.0)
                particle['vy'] += self.random_generator.uniform(-1.0, 1.0)
        
        # Random light intensity boost
        for light in self.light_sources:
            if self.random_generator.random() < 0.5:  # 50% chance
                light['intensity'] *= self.random_generator.uniform(1.2, 1.8)

    def add_random_listening_effects(self):
        """Add random effects when listening starts"""
        # Random particle attraction
        for particle in self.particles:
            if self.random_generator.random() < 0.4:  # 40% chance
                particle['movement_pattern'] = 'circular'
        
        # Random light movement
        for light in self.light_sources:
            if self.random_generator.random() < 0.6:  # 60% chance
                light['x'] += self.random_generator.uniform(-0.1, 0.1)
                light['y'] += self.random_generator.uniform(-0.1, 0.1)

    def set_amplitude(self, amplitude):
        # Use amplitude for dynamic effects
        self.particle_life = amplitude
        # Add random amplitude-based effects
        if amplitude > 0.5 and self.random_generator.random() < 0.1:  # 10% chance
            self.add_random_amplitude_effects()
        self.update()

    def add_random_amplitude_effects(self):
        """Add random effects based on amplitude"""
        # Random particle bursts
        if self.random_generator.random() < 0.3:
            for _ in range(self.random_generator.randint(1, 3)):
                new_particle = {
                    'x': self.random_generator.uniform(-50, 50),
                    'y': self.random_generator.uniform(-50, 50),
                    'vx': self.random_generator.uniform(-2, 2),
                    'vy': self.random_generator.uniform(-2, 2),
                    'life': 0.0,
                    'size': self.random_generator.uniform(3, 8),
                    'color': QColor(0, 255, 255, self.random_generator.randint(50, 120)),
                    'individual_phase': self.random_generator.uniform(0, 2*math.pi),
                    'movement_pattern': 'chaotic'
                }
                self.particles.append(new_particle)

    def animate(self):
        # Professional animation timing with randomness
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        
        # Add random timing variations
        timing_variation = 1.0 + self.random_generator.uniform(-0.2, 0.2)
        
        # Smooth animation phases with natural variations
        self.breathing_phase += 0.02 * delta_time * 60 * self.natural_breathing_rate * timing_variation
        self.pulse_phase += 0.03 * delta_time * 60 * self.natural_pulse_rate * timing_variation
        self.glow_phase += 0.015 * delta_time * 60 * timing_variation
        self.morph_phase += 0.04 * delta_time * 60 * self.morph_complexity * timing_variation
        self.particle_phase += 0.05 * delta_time * 60 * timing_variation
        self.reflection_phase += 0.01 * delta_time * 60 * timing_variation
        self.caustics_phase += 0.025 * delta_time * 60 * timing_variation
        
        # Update random movement timers
        self.movement_timer += delta_time
        
        # Add random movement shifts every few seconds
        if self.movement_timer > self.random_generator.uniform(2, 5):
            self.add_random_movement_shift()
            self.movement_timer = 0
        
        # Update hover animation with randomness
        if self.is_hovered:
            hover_speed = 0.2 + self.random_generator.uniform(-0.05, 0.05)
            self.hover_amplitude = min(1.0, self.hover_amplitude + hover_speed)
        else:
            hover_speed = 0.15 + self.random_generator.uniform(-0.03, 0.03)
            self.hover_amplitude = max(0.0, self.hover_amplitude - hover_speed)
        
        # Update click animation
        if self.is_clicked:
            self.click_amplitude = min(1.0, self.click_amplitude + 0.4)
            if self.click_amplitude >= 1.0:
                self.is_clicked = False
        else:
            self.click_amplitude = max(0.0, self.click_amplitude - 0.25)
        
        # Update particle system with enhanced randomness
        self.update_particles(delta_time)
        
        # Update organic morphing with random variations
        self.update_organic_shape()
        
        # Update light sources with random movement
        self.update_light_sources(delta_time)
        
        self.frame_count += 1
        self.update()

    def add_random_movement_shift(self):
        """Add random shifts to movement patterns"""
        # Randomly adjust movement parameters
        for i in range(len(self.movement_noise)):
            if self.random_generator.random() < 0.3:  # 30% chance
                self.movement_noise[i] += self.random_generator.uniform(-0.5, 0.5)
        
        # Randomly adjust natural rates
        if self.random_generator.random() < 0.2:  # 20% chance
            self.natural_breathing_rate = self.random_generator.uniform(0.8, 1.2)
        if self.random_generator.random() < 0.2:  # 20% chance
            self.natural_pulse_rate = self.random_generator.uniform(0.7, 1.3)

    def update_particles(self, delta_time):
        """Update particle system with enhanced physics and randomness"""
        for particle in self.particles:
            # Individual particle timing
            individual_speed = 1.0 + self.random_generator.uniform(-0.3, 0.3)
            
            # Update position based on movement pattern
            if particle['movement_pattern'] == 'circular':
                angle = particle['individual_phase'] + self.particle_phase * individual_speed
                radius = 30 + 20 * math.sin(particle['individual_phase'] * 0.5)
                particle['x'] = radius * math.cos(angle)
                particle['y'] = radius * math.sin(angle)
            elif particle['movement_pattern'] == 'chaotic':
                particle['x'] += particle['vx'] * delta_time * 30 * individual_speed
                particle['y'] += particle['vy'] * delta_time * 30 * individual_speed
                if self.random_generator.random() < 0.1:
                    particle['vx'] += self.random_generator.uniform(-0.5, 0.5)
                    particle['vy'] += self.random_generator.uniform(-0.5, 0.5)
            else:
                particle['x'] += particle['vx'] * delta_time * 30 * individual_speed
                particle['y'] += particle['vy'] * delta_time * 30 * individual_speed
                dx = -particle['x']
                dy = -particle['y']
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    attraction = 0.1 / (1 + distance * 0.01)
                    particle['vx'] += dx * attraction * delta_time
                    particle['vy'] += dy * attraction * delta_time
            
            # Damping with random variation
            damping = 0.98 + self.random_generator.uniform(-0.02, 0.02)
            particle['vx'] *= damping
            particle['vy'] *= damping
            
            # Update life with random variation
            life_speed = 0.5 + self.random_generator.uniform(-0.2, 0.2)
            particle['life'] += delta_time * life_speed
            if particle['life'] > 1.0:
                particle['life'] = 0.0
                particle['x'] = self.random_generator.uniform(-self.radius, self.radius)
                particle['y'] = self.random_generator.uniform(-self.radius, self.radius)
                particle['vx'] = self.random_generator.uniform(-0.8, 0.8)
                particle['vy'] = self.random_generator.uniform(-0.8, 0.8)
                particle['size'] = self.random_generator.uniform(1.5, 7)
                particle['color'] = QColor(0, 255, 255, self.random_generator.randint(20, 100))
                particle['movement_pattern'] = self.random_generator.choice(['circular', 'linear', 'chaotic'])

    def update_light_sources(self, delta_time):
        """Update light sources with random movement"""
        for light in self.light_sources:
            # Random light movement
            if self.random_generator.random() < 0.05:  # 5% chance per frame
                light['x'] += self.random_generator.uniform(-0.02, 0.02)
                light['y'] += self.random_generator.uniform(-0.02, 0.02)
                light['x'] = max(-0.5, min(0.5, light['x']))
                light['y'] = max(-0.5, min(0.5, light['y']))
            
            # Update individual light phase
            light['phase'] += delta_time * light['speed'] * self.random_generator.uniform(0.8, 1.2)

    def update_organic_shape(self):
        """Update organic shape parameters with enhanced randomness"""
        if self.state == 'speaking':
            # Dynamic speaking patterns with randomness
            base_noise = 0.8 + 0.2 * math.sin(self.morph_phase * 2)
            random_variation = self.random_generator.uniform(-0.1, 0.1)
            self.organic_noise = base_noise + random_variation
        elif self.state == 'listening':
            # Dynamic listening patterns with randomness
            base_noise = 0.4 + 0.2 * math.sin(self.morph_phase * 1.5)
            random_variation = self.random_generator.uniform(-0.05, 0.05)
            self.organic_noise = base_noise + random_variation
        else:
            # Subtle idle movement with randomness
            base_noise = 0.1 + 0.1 * math.sin(self.morph_phase * 0.5)
            random_variation = self.random_generator.uniform(-0.02, 0.02)
            self.organic_noise = base_noise + random_variation

    def resizeEvent(self, event):
        self.center = QPoint(self.width() // 2, self.height() // 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        cx, cy = self.center.x(), self.center.y()
        
        # Calculate dynamic radius with natural breathing
        breathing_factor = 1.0 + 0.02 * math.sin(self.breathing_phase)
        current_radius = self.radius * breathing_factor
        
        # Add hover and click effects
        if self.hover_amplitude > 0:
            current_radius *= (1.0 + 0.08 * self.hover_amplitude)
        if self.click_amplitude > 0:
            current_radius *= (1.0 + 0.15 * self.click_amplitude)
        
        # Draw advanced shadow with multiple layers
        self.draw_advanced_shadow(painter, cx, cy, current_radius)
        
        # Draw main organic blob
        self.draw_organic_blob(painter, cx, cy, current_radius)
        
        # Draw particle system
        self.draw_particles(painter, cx, cy)
        
        # Draw advanced lighting effects
        self.draw_advanced_lighting(painter, cx, cy, current_radius)
        
        # Draw state-specific effects
        self.draw_state_effects(painter, cx, cy, current_radius)

    def draw_advanced_shadow(self, painter, cx, cy, radius):
        """Draw multi-layered professional shadow"""
        # Primary shadow
        shadow_radius = radius * 1.15
        shadow_gradient = QRadialGradient(cx, cy + 20, shadow_radius, cx, cy)
        shadow_gradient.setColorAt(0, QColor(0, 20, 40, 80))
        shadow_gradient.setColorAt(0.7, QColor(0, 10, 20, 40))
        shadow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow_gradient))
        painter.drawEllipse(int(cx - shadow_radius), int(cy - shadow_radius + 20), 
                           int(shadow_radius * 2), int(shadow_radius * 2))
        
        # Secondary ambient shadow
        ambient_radius = radius * 1.25
        ambient_gradient = QRadialGradient(cx, cy + 10, ambient_radius, cx, cy)
        ambient_gradient.setColorAt(0, QColor(0, 30, 60, 30))
        ambient_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(ambient_gradient))
        painter.drawEllipse(int(cx - ambient_radius), int(cy - ambient_radius + 10), 
                           int(ambient_radius * 2), int(ambient_radius * 2))

    def draw_organic_blob(self, painter, cx, cy, radius):
        """Draw organic morphing blob with advanced gradients and randomness"""
        # Generate organic shape points with enhanced randomness
        points = self.generate_organic_points(cx, cy, radius)
        
        # Create advanced gradient
        blob_gradient = QRadialGradient(cx, cy, radius * 0.7, cx, cy)
        
        # Calculate dynamic colors
        base_color = self.base_color
        inner_color = self.inner_color
        outer_color = self.outer_color
        
        # Add hover glow
        if self.hover_amplitude > 0:
            glow_factor = self.hover_amplitude * 0.6
            base_color = self.blend_colors(base_color, self.glow_color, glow_factor)
            inner_color = self.blend_colors(inner_color, self.glow_color, glow_factor)
        
        # Add click flash
        if self.click_amplitude > 0:
            flash_factor = self.click_amplitude * 0.8
            white_color = QColor(255, 255, 255)
            base_color = self.blend_colors(base_color, white_color, flash_factor)
            inner_color = self.blend_colors(inner_color, white_color, flash_factor)
        
        # Dim colors when sleeping
        if self.state == 'sleeping':
            base_color = QColor(base_color.red() // 4, base_color.green() // 4, base_color.blue() // 4)
            inner_color = QColor(inner_color.red() // 4, inner_color.green() // 4, inner_color.blue() // 4)
            outer_color = QColor(outer_color.red() // 4, outer_color.green() // 4, outer_color.blue() // 4)
        
        blob_gradient.setColorAt(0.0, inner_color)
        blob_gradient.setColorAt(0.5, base_color)
        blob_gradient.setColorAt(0.8, outer_color)
        blob_gradient.setColorAt(1.0, QColor(0, 80, 160, 0))
        
        # Draw organic path
        path = QPainterPath()
        if len(points) > 2:
            path.moveTo(points[0])
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                p3 = points[(i + 2) % len(points)]
                
                # Calculate smooth control points with random variation
                control_variation = 0.3 + self.random_generator.uniform(-0.1, 0.1)
                cp1x = p1.x() + (p2.x() - points[(i - 1) % len(points)].x()) * control_variation
                cp1y = p1.y() + (p2.y() - points[(i - 1) % len(points)].y()) * control_variation
                cp2x = p2.x() - (p3.x() - p1.x()) * control_variation
                cp2y = p2.y() - (p3.y() - p1.y()) * control_variation
                
                path.cubicTo(cp1x, cp1y, cp2x, cp2y, p2.x(), p2.y())
        
        painter.setBrush(QBrush(blob_gradient))
        painter.drawPath(path)

    def generate_organic_points(self, cx, cy, radius):
        """Generate organic shape points with enhanced randomness and natural movement"""
        points = []
        for i in range(self.n_points):
            angle = (2 * math.pi * i) / self.n_points
            
            # Base radius with breathing
            base_r = radius
            
            # Add organic morphing with enhanced randomness
            morph_factor = 1.0 + self.organic_noise * (
                math.sin(self.morph_phase + angle * 3 + self.movement_noise[i % len(self.movement_noise)]) * 0.1 +
                math.cos(self.morph_phase * 0.7 + angle * 5) * 0.08 +
                math.sin(self.morph_phase * 1.3 + angle * 7) * 0.06
            )
            
            # Add state-specific distortion with randomness
            if self.state == 'speaking':
                speech_distortion = 0.2 * math.sin(angle * 6 + self.pulse_phase * 2 + self.random_generator.uniform(-0.5, 0.5))
                morph_factor += speech_distortion
            elif self.state == 'listening':
                listening_distortion = 0.15 * math.sin(angle * 4 + self.pulse_phase * 1.5 + self.random_generator.uniform(-0.3, 0.3))
                morph_factor += listening_distortion
            
            # Add natural shift variations
            natural_shift = 0.02 * math.sin(self.random_shift_phases[i % len(self.random_shift_phases)] + angle * 2)
            morph_factor += natural_shift
            
            # Add subtle noise with random variation
            noise = 0.02 * math.sin(self.morph_phase * 0.5 + i * 0.1 + self.random_generator.uniform(-0.2, 0.2))
            morph_factor += noise
            
            final_radius = base_r * morph_factor
            x = cx + math.cos(angle) * final_radius
            y = cy + math.sin(angle) * final_radius
            points.append(QPointF(x, y))
        
        return points

    def draw_particles(self, painter, cx, cy):
        """Draw advanced particle system with enhanced effects"""
        for particle in self.particles:
            alpha = int(particle['color'].alpha() * (1 - particle['life']))
            if alpha > 0:
                particle_color = QColor(
                    particle['color'].red(),
                    particle['color'].green(),
                    particle['color'].blue(),
                    alpha
                )
                size = particle['size'] * (1 + 0.5 * math.sin(particle['life'] * math.pi + particle['individual_phase']))
                x = cx + particle['x']
                y = cy + particle['y']
                glow_size = size * (2 + self.random_generator.uniform(-0.5, 0.5))
                glow_gradient = QRadialGradient(x, y, glow_size)
                glow_gradient.setColorAt(0, particle_color)
                glow_gradient.setColorAt(1, QColor(particle_color.red(), particle_color.green(), particle_color.blue(), 0))
                painter.setBrush(QBrush(glow_gradient))
                painter.drawEllipse(int(x - glow_size), int(y - glow_size), int(glow_size * 2), int(glow_size * 2))
                core_size = size * (0.8 + self.random_generator.uniform(-0.2, 0.2))
                painter.setBrush(QBrush(particle_color))
                painter.drawEllipse(int(x - core_size), int(y - core_size), int(core_size * 2), int(core_size * 2))

    def draw_advanced_lighting(self, painter, cx, cy, radius):
        """Draw advanced lighting effects with random movement"""
        # Draw multiple light sources with enhanced randomness
        for light in self.light_sources:
            light_x = cx + light['x'] * radius
            light_y = cy + light['y'] * radius
            light_radius = radius * (0.4 + self.random_generator.uniform(-0.1, 0.1))
            
            # Animate light intensity with individual phase
            intensity = light['intensity'] * (0.8 + 0.2 * math.sin(light['phase']))
            
            # Create light gradient with random variation
            light_gradient = QRadialGradient(light_x, light_y, light_radius)
            light_color = light['color']
            light_gradient.setColorAt(0, QColor(light_color.red(), 
                                               light_color.green(), 
                                               light_color.blue(), 
                                               int(light_color.alpha() * intensity)))
            light_gradient.setColorAt(1, QColor(light_color.red(), 
                                               light_color.green(), 
                                               light_color.blue(), 0))
            
            painter.setBrush(QBrush(light_gradient))
            painter.drawEllipse(int(light_x - light_radius), int(light_y - light_radius), 
                               int(light_radius * 2), int(light_radius * 2))

    def draw_state_effects(self, painter, cx, cy, radius):
        """Draw state-specific advanced effects with randomness"""
        if self.state == 'listening':
            # Advanced listening rings with random variations
            for i in range(3):
                ring_radius = radius * (1.1 + 0.1 * i + 0.05 * math.sin(self.pulse_phase + i + self.random_generator.uniform(-0.2, 0.2)))
                ring_alpha = 60 - i * 15 + self.random_generator.randint(-5, 5)
                ring_gradient = QRadialGradient(cx, cy, ring_radius, cx, cy)
                ring_gradient.setColorAt(0.9, QColor(0, 255, 150, 0))
                ring_gradient.setColorAt(1.0, QColor(0, 255, 150, max(0, ring_alpha)))
                painter.setBrush(QBrush(ring_gradient))
                painter.drawEllipse(int(cx - ring_radius), int(cy - ring_radius), 
                                   int(ring_radius * 2), int(ring_radius * 2))
        
        elif self.state == 'speaking':
            # Advanced speaking effects with random variations
            for i in range(4):
                energy_radius = radius * (1.05 + 0.08 * i + 0.04 * math.sin(self.pulse_phase + i * 0.5 + self.random_generator.uniform(-0.3, 0.3)))
                energy_alpha = 100 - i * 20 + self.random_generator.randint(-10, 10)
                energy_gradient = QRadialGradient(cx, cy, energy_radius, cx, cy)
                energy_gradient.setColorAt(0.8, QColor(255, 255, 255, 0))
                energy_gradient.setColorAt(1.0, QColor(255, 255, 255, max(0, energy_alpha)))
                painter.setBrush(QBrush(energy_gradient))
                painter.drawEllipse(int(cx - energy_radius), int(cy - energy_radius), 
                                   int(energy_radius * 2), int(energy_radius * 2))
        
        elif self.state == 'processing':
            # Processing animation with random variations
            processing_radius = radius * (1.1 + 0.05 * math.sin(self.pulse_phase * 2 + self.random_generator.uniform(-0.2, 0.2)))
            processing_alpha = 80 + self.random_generator.randint(-10, 10)
            processing_gradient = QRadialGradient(cx, cy, processing_radius, cx, cy)
            processing_gradient.setColorAt(0.9, QColor(255, 165, 0, 0))  # Orange
            processing_gradient.setColorAt(1.0, QColor(255, 165, 0, max(0, processing_alpha)))
            painter.setBrush(QBrush(processing_gradient))
            painter.drawEllipse(int(cx - processing_radius), int(cy - processing_radius), 
                               int(processing_radius * 2), int(processing_radius * 2))

    def blend_colors(self, color1, color2, factor):
        """Advanced color blending with gamma correction"""
        r = int(color1.red() * (1 - factor) + color2.red() * factor)
        g = int(color1.green() * (1 - factor) + color2.green() * factor)
        b = int(color1.blue() * (1 - factor) + color2.blue() * factor)
        return QColor(r, g, b)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_clicked = True
            self.click_amplitude = 0.0
            if hasattr(self.parent(), 'on_blob_clicked'):
                self.parent().on_blob_clicked()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        cx, cy = self.center.x(), self.center.y()
        distance = math.sqrt((event.x() - cx)**2 + (event.y() - cy)**2)
        
        was_hovered = self.is_hovered
        self.is_hovered = distance < self.radius * 1.3
        
        if was_hovered != self.is_hovered:
            self.update()
        
        super().mouseMoveEvent(event)

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

class BlobHomeWindow(QMainWindow):
    """Home window with the animated JARVIS blob"""
    
    def __init__(self, backend_manager):
        super().__init__()
        self.backend_manager = backend_manager
        self.setWindowTitle("JARVIS AI Assistant - Home")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create the blob widget
        self.blob_widget = UltraJarvisBlobWidget()
        layout.addWidget(self.blob_widget, 1)
        
        # Connect backend signals
        self.backend_manager.status_update.connect(self._update_status)
        self.backend_manager.error_occurred.connect(self._show_error)
        self.backend_manager.go_home_requested.connect(self._go_home)
        self.backend_manager.volume_update.connect(self.blob_widget.set_amplitude)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 16px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        
        self.chat_button = QPushButton("Open Chat")
        self.chat_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00aaff, stop:1 #0088cc);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ccff, stop:1 #00aaff);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0088cc, stop:1 #006699);
            }
        """)
        self.chat_button.clicked.connect(self._open_chat)
        button_layout.addWidget(self.chat_button)
        
        layout.addLayout(button_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #1a1a1a, stop:1 #0a0a0a);
            }
        """)
        
        self.chat_window = None

    def set_chat_window(self, chat_window):
        """Set reference to chat window for navigation"""
        self.chat_window = chat_window

    def _update_status(self, status):
        if "sleeping" in status.lower():
            self.blob_widget.set_state('sleeping')
            self.status_label.setText("💤 Sleeping...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 16px;
                    font-weight: bold;
                    background: rgba(0, 0, 0, 0.7);
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px;
                }
            """)
        elif "listening" in status.lower():
            self.blob_widget.set_state('listening')
            self.status_label.setText(status)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #00ff96;
                    font-size: 16px;
                    font-weight: bold;
                    background: rgba(0, 0, 0, 0.7);
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px;
                }
            """)
        elif "speaking" in status.lower():
            self.blob_widget.set_state('speaking')
            self.status_label.setText(status)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ff6b35;
                    font-size: 16px;
                    font-weight: bold;
                    background: rgba(0, 0, 0, 0.7);
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px;
                }
            """)
        else:
            self.blob_widget.set_state('idle')
            self.status_label.setText(status)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: bold;
                    background: rgba(0, 0, 0, 0.7);
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px;
                }
            """)

    def _show_error(self, error_msg):
        self.status_label.setText(f"Error: {error_msg}")

    def _go_home(self):
        # Already on home, do nothing
        pass

    def _open_chat(self):
        self.hide()
        if hasattr(self, 'chat_window'):
            self.chat_window.show()

    def on_blob_clicked(self):
        """Handle blob click events with interactive responses"""
        # Add visual feedback
        self.blob_widget.set_state('interactive')
        
        # Show a temporary message
        original_text = self.status_label.text()
        self.status_label.setText("✨ Interactive Mode Activated!")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffd700;
                font-size: 16px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.8);
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }
        """)
        
        # Reset after 2 seconds
        QTimer.singleShot(2000, lambda: self._restore_status(original_text))
        
        # Emit a signal to trigger some action (like opening chat)
        if hasattr(self, 'chat_window') and self.chat_window:
            QTimer.singleShot(500, self._open_chat)

    def _restore_status(self, text):
        """Restore the original status text"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }
        """)
        self.blob_widget.set_state('idle')

class ModernVoiceVisualizer(QWidget):
    """Advanced voice visualizer with cutting-edge styling and dynamic effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)  # Increased height for better visual impact
        self.bars = [0] * 20  # More bars for richer visualization
        self.is_listening = False
        self.is_speaking = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_bars)
        self.animation_timer.start(40)  # 25 FPS for smooth animation
        
        # Advanced state tracking
        self.speech_intensity = 0.0
        self.listening_intensity = 0.0
        self.energy_level = 0.0
        self.pulse_phase = 0.0
        
    def set_listening(self, listening):
        self.is_listening = listening
        if not listening:
            self.bars = [0] * 20
            self.listening_intensity = 0.0
        else:
            self.listening_intensity = 1.0
        self.update()
    
    def set_speaking(self, speaking):
        """Set speaking state for visual feedback"""
        self.is_speaking = speaking
        if speaking:
            self.speech_intensity = 1.0
        else:
            self.speech_intensity = 0.0
        self.update()
    
    def set_amplitude(self, amplitude):
        """Set audio amplitude for dynamic visualization"""
        if self.is_listening:
            self.listening_intensity = min(1.0, amplitude)
        elif self.is_speaking:
            self.speech_intensity = min(1.0, amplitude)
        self.energy_level = amplitude
        self.update()
    
    def update_bars(self):
        """Advanced bar update with dynamic effects"""
        self.pulse_phase += 0.1
        
        if self.is_listening:
            # Dynamic listening visualization
            for i in range(len(self.bars)):
                if random.random() < 0.4:  # Higher chance for more activity
                    base_height = 0.3 + (self.listening_intensity * 0.7)
                    # Add wave effect
                    wave = math.sin(self.pulse_phase + i * 0.3) * 0.1
                    self.bars[i] = random.uniform(0.1, base_height + wave)
                else:
                    # Smooth decay with energy influence
                    decay_rate = 0.06 + (self.energy_level * 0.02)
                    self.bars[i] = max(0, self.bars[i] - decay_rate)
        elif self.is_speaking:
            # Dynamic speaking visualization
            for i in range(len(self.bars)):
                if random.random() < 0.5:  # Higher activity for speaking
                    base_height = 0.4 + (self.speech_intensity * 0.6)
                    # Add rhythmic pattern
                    rhythm = math.sin(self.pulse_phase * 2 + i * 0.2) * 0.15
                    self.bars[i] = random.uniform(0.2, base_height + rhythm)
                else:
                    # Slower decay for speaking
                    decay_rate = 0.04 + (self.energy_level * 0.01)
                    self.bars[i] = max(0, self.bars[i] - decay_rate)
        else:
            # Enhanced idle state with subtle movement
            for i in range(len(self.bars)):
                if random.random() < 0.15:  # Moderate chance
                    # Subtle breathing effect
                    breath = math.sin(self.pulse_phase * 0.5 + i * 0.1) * 0.05
                    self.bars[i] = random.uniform(0, 0.15 + breath)
                else:
                    self.bars[i] = max(0, self.bars[i] - 0.03)
        self.update()
    
    def paintEvent(self, event):
        """Advanced paint event with cutting-edge rendering"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Advanced background with gradient
        bg_gradient = QLinearGradient(0, 0, 0, self.height())
        bg_gradient.setColorAt(0, QColor(10, 10, 10, 180))
        bg_gradient.setColorAt(0.5, QColor(26, 26, 46, 180))
        bg_gradient.setColorAt(1, QColor(15, 15, 30, 180))
        painter.fillRect(self.rect(), QBrush(bg_gradient))
        
        # Draw advanced audio bars
        bar_width = self.width() / len(self.bars)
        bar_spacing = 2
        
        for i, height in enumerate(self.bars):
            x = i * bar_width + bar_spacing
            bar_w = bar_width - bar_spacing * 2
            
            # Advanced bar gradient based on state
            if self.is_listening:
                bar_gradient = QLinearGradient(x, self.height(), x, self.height() - height * self.height())
                bar_gradient.setColorAt(0, QColor(0, 255, 150))  # Green for listening
                bar_gradient.setColorAt(0.3, QColor(0, 212, 255))
                bar_gradient.setColorAt(0.7, QColor(0, 255, 200))
                bar_gradient.setColorAt(1, QColor(0, 255, 150))
            elif self.is_speaking:
                bar_gradient = QLinearGradient(x, self.height(), x, self.height() - height * self.height())
                bar_gradient.setColorAt(0, QColor(0, 255, 255))  # Cyan for speaking
                bar_gradient.setColorAt(0.3, QColor(0, 200, 255))
                bar_gradient.setColorAt(0.7, QColor(0, 255, 255))
                bar_gradient.setColorAt(1, QColor(0, 255, 255))
            else:
                bar_gradient = QLinearGradient(x, self.height(), x, self.height() - height * self.height())
                bar_gradient.setColorAt(0, QColor(0, 255, 150, 120))
                bar_gradient.setColorAt(0.5, QColor(0, 255, 150, 80))
                bar_gradient.setColorAt(1, QColor(0, 255, 150, 60))
            
            bar_height = height * self.height() * 0.85
            bar_rect = QRectF(x, self.height() - bar_height, bar_w, bar_height)
            
            # Draw bar with advanced styling
            painter.fillRect(bar_rect, QBrush(bar_gradient))
            
            # Enhanced glow effect for active bars
            if height > 0.3 and (self.is_listening or self.is_speaking):
                glow_color = QColor(0, 255, 150, 80) if self.is_listening else QColor(0, 255, 255, 80)
                glow_rect = QRectF(x - 2, self.height() - bar_height - 2, bar_w + 4, bar_height + 4)
                painter.setPen(QPen(glow_color, 3))
                painter.drawRect(glow_rect)
                
                # Additional inner glow
                inner_glow_color = QColor(0, 255, 150, 40) if self.is_listening else QColor(0, 255, 255, 40)
                inner_glow_rect = QRectF(x - 1, self.height() - bar_height - 1, bar_w + 2, bar_height + 2)
                painter.setPen(QPen(inner_glow_color, 1))
                painter.drawRect(inner_glow_rect)

class ChatWindow(QMainWindow):
    """Modern chat window with advanced voice visualizer"""
    def __init__(self, backend_manager=None):
        super().__init__()
        self.backend_manager = backend_manager
        self.setWindowTitle(f"{Assistantname} AI Assistant - Chat")
        self.setWindowIcon(QIcon())
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        self.center_window()
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0a0a0a, stop:1 #1a1a1a);")
        # Chat widget
        self.chat_widget = AdvancedChatWidget(self.backend_manager)
        self.setCentralWidget(self.chat_widget)
        # Modern voice visualizer
        self.voice_visualizer = ModernVoiceVisualizer(self)
        self.chat_widget.layout().insertWidget(2, self.voice_visualizer)
        # Navigation button
        self.home_btn = QPushButton("🏠 Home", self)
        self.home_btn.setFixedSize(100, 44)
        self.home_btn.setStyleSheet("font-size:18px; border-radius:22px; background:#222; color:#00ffcc; position:absolute; right:20px; top:20px;")
        self.home_btn.move(self.width() - 120, 20)
        self.home_btn.clicked.connect(self.goto_home)
        self.home_btn.raise_()
        self.home_btn.show()
        # Connect backend signals
        if self.backend_manager:
            self.backend_manager.status_update.connect(self.on_status_update)
        # State
        self.is_listening = False

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def goto_home(self):
        self.hide()
        if hasattr(self, 'blob_window'):
            self.blob_window.show()

    def set_blob_window(self, blob_window):
        self.blob_window = blob_window

    def on_status_update(self, status):
        if "listening" in status.lower():
            self.voice_visualizer.set_listening(True)
        else:
            self.voice_visualizer.set_listening(False)

class AdvancedMainWindow(QMainWindow):
    """Advanced main window with Iron Man JARVIS styling and animated blob home screen"""
    def __init__(self, backend_manager=None):
        super().__init__()
        self.backend_manager = backend_manager
        self.setup_ui()
        self.setup_window()
        self.setup_animations()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # Blob home screen
        self.blob_widget = BlobHomeWindow(self.backend_manager)
        self.layout.addWidget(self.blob_widget)
        # Chat widget (hidden initially)
        self.chat_widget = ChatWindow(self.backend_manager)
        self.layout.addWidget(self.chat_widget)
        self.chat_widget.hide()
        # Home button (optional, for demo)
        self.home_btn = QPushButton("🏠 Home", self)
        self.home_btn.setFixedSize(80, 40)
        self.home_btn.setStyleSheet("font-size:18px; border-radius:20px; background:#222; color:#00ffcc;")
        self.home_btn.clicked.connect(self.show_blob_home)
        self.layout.addWidget(self.home_btn, alignment=2)
        self.home_btn.hide()

    def show_blob_home(self):
        self.blob_widget.show()
        self.chat_widget.hide()
        self.home_btn.hide()

    def show_chat(self):
        self.blob_widget.hide()
        self.chat_widget.show()
        self.home_btn.show()

    def setup_window(self):
        self.setWindowTitle(f"{Assistantname} AI Assistant - Advanced Interface")
        self.setWindowIcon(QIcon())
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        self.center_window()
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
            }
        """)
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint))

    def setup_animations(self):
        pass

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        if self.backend_manager:
            self.backend_manager.stop()
        event.accept()

def main():
    """Test the advanced GUI independently"""
    app = QApplication(sys.argv)
    window = AdvancedMainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 
