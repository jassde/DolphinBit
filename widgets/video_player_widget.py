"""
Video Player Widget - Enhanced display area for video playback with overlays
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QFont


class VideoPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Overlay information
        self.show_info_overlay = True
        self.current_frame = 0
        self.total_frames = 0
        self.current_time = "00:00:00"
        self.fps = 0
        self.resolution = ""
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video display area
        self.video_frame = QLabel("No Video Loaded\n\nDrag and drop video files here")
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setStyleSheet("""
            QLabel {
                background: #1a1a1a;
                border: 2px dashed #666;
                border-radius: 8px;
                color: #888;
                font-size: 16px;
                font-weight: 500;
                min-height: 300px;
            }
        """)
        layout.addWidget(self.video_frame)
    
    def set_video_info(self, frame, total_frames, time, fps, resolution):
        """Update video information for overlay"""
        self.current_frame = frame
        self.total_frames = total_frames
        self.current_time = time
        self.fps = fps
        self.resolution = resolution
        self.update()
    
    def toggle_info_overlay(self):
        """Toggle info overlay visibility"""
        self.show_info_overlay = not self.show_info_overlay
        self.update()
    
    def paintEvent(self, event):
        """Draw info overlay on video player"""
        super().paintEvent(event)
        
        if not self.show_info_overlay or self.total_frames == 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent background for overlay
        overlay_height = 80
        overlay_rect = QRect(0, self.height() - overlay_height, self.width(), overlay_height)
        
        # Gradient background
        gradient_color = QColor(0, 0, 0, 180)
        painter.fillRect(overlay_rect, gradient_color)
        
        # Set font for text
        font = QFont("Segoe UI", 11)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        # Draw info text
        padding = 16
        y_pos = self.height() - overlay_height + 20
        
        # Timecode
        timecode_text = f"⏱ {self.current_time}"
        painter.drawText(padding, y_pos, timecode_text)
        
        # Frame counter
        frame_text = f"🎞 Frame {self.current_frame + 1} / {self.total_frames}"
        painter.drawText(padding, y_pos + 25, frame_text)
        
        # FPS and Resolution (right aligned)
        fps_text = f"{self.fps:.2f} FPS"
        res_text = f"{self.resolution}"
        
        metrics = painter.fontMetrics()
        fps_width = metrics.horizontalAdvance(fps_text)
        res_width = metrics.horizontalAdvance(res_text)
        
        painter.drawText(self.width() - fps_width - padding, y_pos, fps_text)
        painter.drawText(self.width() - res_width - padding, y_pos + 25, res_text)
        
        painter.end()
    
    def set_aspect_ratio_mode(self, mode):
        """Set how video fits in player (Fit/Fill/Stretch)"""
        if mode == "Fit":
            self.video_frame.setScaledContents(False)
            self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif mode == "Fill":
            self.video_frame.setScaledContents(True)
        # Add more modes as needed
