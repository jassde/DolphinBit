"""
Timeline Widget - Custom timeline control with in/out points and zoom
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QPointF
from PyQt6.QtGui import QPalette, QColor, QPainter, QPen, QLinearGradient


class TimelineWidget(QWidget):
    positionChanged = pyqtSignal(int)
    inOutChanged = pyqtSignal(int, int)
    
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        
        # Timeline data
        self.duration = 100
        self.current_position = 0
        self.in_point = 0
        self.out_point = 100
        self.dragging_in = False
        self.dragging_out = False
        self.dragging_position = False
        
        # Zoom support
        self.zoom_level = 1.0  # 1.0 = 100%, 2.0 = 200%, etc.
        self.view_start = 0  # Start of visible range
        self.view_end = 100  # End of visible range
        self.dragging_timeline = False
        self.last_drag_pos = None
        
        # Display options
        self.show_frame_numbers = True
        self.show_timecode = True
        self.fps = 30  # Default FPS for timecode calculation
        
        # Style
        self.setStyleSheet("""
            TimelineWidget {
                background: #2d2d2d;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
            }
        """)

    def set_fps(self, fps):
        """Set FPS for timecode display"""
        self.fps = fps
    
    def toggle_frame_numbers(self):
        """Toggle frame number display"""
        self.show_frame_numbers = not self.show_frame_numbers
        self.update()
    
    def toggle_timecode(self):
        """Toggle timecode display"""
        self.show_timecode = not self.show_timecode
        self.update()
    
    def _format_timecode(self, frame):
        """Convert frame number to timecode (HH:MM:SS:FF)"""
        if self.fps <= 0:
            return "00:00:00:00"
        
        total_seconds = frame / self.fps
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        frames = int(frame % self.fps)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
    
    def set_duration(self, duration):
        self.duration = max(1, duration)
        self.view_end = duration
        self.update()
    
    def set_zoom(self, zoom_level):
        """Set zoom level (1.0 = 100%, 2.0 = 200%, etc.)"""
        old_zoom = self.zoom_level
        self.zoom_level = max(0.1, min(10.0, zoom_level))
        
        # Adjust view range to keep current position centered
        visible_frames = self.duration / self.zoom_level
        center = (self.view_start + self.view_end) / 2
        
        self.view_start = max(0, center - visible_frames / 2)
        self.view_end = min(self.duration, self.view_start + visible_frames)
        
        # Adjust if we hit boundaries
        if self.view_end >= self.duration:
            self.view_end = self.duration
            self.view_start = max(0, self.duration - visible_frames)
        
        self.update()
    
    def zoom_in(self):
        """Zoom in (show less frames)"""
        self.set_zoom(self.zoom_level * 1.2)
    
    def zoom_out(self):
        """Zoom out (show more frames)"""
        self.set_zoom(self.zoom_level / 1.2)
    
    def zoom_to_fit(self):
        """Reset zoom to show entire timeline"""
        self.zoom_level = 1.0
        self.view_start = 0
        self.view_end = self.duration
        self.update()

    def set_position(self, position):
        self.current_position = max(0, min(position, self.duration))
        self.update()

    def set_in_out_points(self, in_point, out_point):
        self.in_point = max(0, min(in_point, self.duration))
        self.out_point = max(self.in_point, min(out_point, self.duration))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw timeline background
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.fillRect(rect, QColor(45, 45, 45))
        
        # Draw timeline track
        track_rect = QRect(rect.x() + 10, rect.center().y() - 8, rect.width() - 20, 16)
        painter.fillRect(track_rect, QColor(60, 60, 60))
        
        # Calculate visible range mapping
        visible_duration = self.view_end - self.view_start
        
        # Draw in/out region (only if visible)
        if self.duration > 0 and visible_duration > 0:
            if self.out_point >= self.view_start and self.in_point <= self.view_end:
                # Map in/out points to screen coordinates
                in_screen = self._frame_to_screen(self.in_point, track_rect)
                out_screen = self._frame_to_screen(self.out_point, track_rect)
                
                # Clamp to visible area
                in_screen = max(track_rect.x(), min(in_screen, track_rect.x() + track_rect.width()))
                out_screen = max(track_rect.x(), min(out_screen, track_rect.x() + track_rect.width()))
                
                # Highlight region between in and out points
                highlight_rect = QRect(int(in_screen), track_rect.y(), 
                                     int(out_screen - in_screen), track_rect.height())
                
                # Use QPointF for gradient coordinates
                gradient = QLinearGradient(
                    QPointF(highlight_rect.topLeft()), 
                    QPointF(highlight_rect.topRight())
                )
                gradient.setColorAt(0, QColor(100, 149, 237))  # Cornflower blue
                gradient.setColorAt(1, QColor(65, 105, 225))   # Royal blue
                painter.fillRect(highlight_rect, gradient)
        
        # Draw position indicator (only if visible)
        if self.duration > 0 and visible_duration > 0:
            if self.view_start <= self.current_position <= self.view_end:
                pos_x = self._frame_to_screen(self.current_position, track_rect)
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.drawLine(int(pos_x), track_rect.y() - 5, int(pos_x), track_rect.y() + track_rect.height() + 5)
                
                # Draw position triangle
                points = [
                    QPoint(int(pos_x) - 6, track_rect.y() - 10),
                    QPoint(int(pos_x) + 6, track_rect.y() - 10),
                    QPoint(int(pos_x), track_rect.y() - 20)
                ]
                painter.setBrush(QColor(255, 255, 255))
                painter.drawPolygon(points)
        
        # Draw in/out markers (only if visible)
        if self.duration > 0 and visible_duration > 0:
            # In point marker
            if self.view_start <= self.in_point <= self.view_end:
                in_x = self._frame_to_screen(self.in_point, track_rect)
                painter.setPen(QPen(QColor(50, 205, 50), 2))  # Lime green
                painter.drawLine(int(in_x), track_rect.y() - 8, int(in_x), track_rect.y() + track_rect.height() + 8)
            
            # Out point marker
            if self.view_start <= self.out_point <= self.view_end:
                out_x = self._frame_to_screen(self.out_point, track_rect)
                painter.setPen(QPen(QColor(220, 20, 60), 2))  # Crimson red
                painter.drawLine(int(out_x), track_rect.y() - 8, int(out_x), track_rect.y() + track_rect.height() + 8)
        
        # Draw zoom indicator
        if self.zoom_level > 1.0:
            zoom_text = f"Zoom: {int(self.zoom_level * 100)}%"
            painter.setPen(QColor(180, 180, 180))
            painter.drawText(rect.x() + 10, rect.y() + 15, zoom_text)
        
        # Draw frame numbers/timecode ruler
        if self.show_frame_numbers or self.show_timecode:
            self._draw_ruler(painter, track_rect)
    
    def _draw_ruler(self, painter, track_rect):
        """Draw frame numbers or timecode on timeline"""
        painter.setPen(QColor(150, 150, 150))
        font = painter.font()
        font.setPixelSize(9)
        painter.setFont(font)
        
        visible_duration = self.view_end - self.view_start
        if visible_duration <= 0:
            return
        
        # Calculate tick spacing based on zoom level
        if self.zoom_level < 0.5:
            tick_interval = max(100, int(self.duration / 10))
        elif self.zoom_level < 2:
            tick_interval = max(50, int(self.duration / 20))
        else:
            tick_interval = max(10, int(visible_duration / 10))
        
        # Draw ticks
        start_frame = int(self.view_start / tick_interval) * tick_interval
        for frame in range(start_frame, int(self.view_end) + 1, tick_interval):
            if frame < 0 or frame > self.duration:
                continue
            
            x = self._frame_to_screen(frame, track_rect)
            if track_rect.x() <= x <= track_rect.x() + track_rect.width():
                # Draw tick mark
                painter.drawLine(int(x), track_rect.y() - 10, int(x), track_rect.y() - 5)
                
                # Draw label
                if self.show_timecode and self.fps > 0:
                    label = self._format_timecode(frame)
                else:
                    label = str(frame)
                
                metrics = painter.fontMetrics()
                label_width = metrics.horizontalAdvance(label)
                painter.drawText(int(x - label_width / 2), track_rect.y() - 12, label)
    
    def _frame_to_screen(self, frame, track_rect):
        """Convert frame number to screen x coordinate"""
        visible_duration = self.view_end - self.view_start
        if visible_duration <= 0:
            return track_rect.x()
        
        relative_pos = (frame - self.view_start) / visible_duration
        return track_rect.x() + relative_pos * track_rect.width()
    
    def _screen_to_frame(self, screen_x, track_rect):
        """Convert screen x coordinate to frame number"""
        relative_pos = (screen_x - track_rect.x()) / track_rect.width()
        frame = self.view_start + relative_pos * (self.view_end - self.view_start)
        return max(0, min(int(frame), self.duration))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            track_rect = self.rect().adjusted(12, self.rect().center().y() - 8, -12, 0)
            track_rect.setHeight(16)
            
            pos = event.position().x()
            
            # Check if clicking near in point
            if self.view_start <= self.in_point <= self.view_end:
                in_x = self._frame_to_screen(self.in_point, track_rect)
                if abs(pos - in_x) < 10:
                    self.dragging_in = True
                    return
                
            # Check if clicking near out point
            if self.view_start <= self.out_point <= self.view_end:
                out_x = self._frame_to_screen(self.out_point, track_rect)
                if abs(pos - out_x) < 10:
                    self.dragging_out = True
                    return
            
            # Otherwise set position or start panning
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift + drag to pan timeline
                self.dragging_timeline = True
                self.last_drag_pos = pos
            else:
                # Regular click to set position
                self.dragging_position = True
                self.update_position_from_mouse(event)
        
        elif event.button() == Qt.MouseButton.MiddleButton:
            # Middle mouse to pan
            self.dragging_timeline = True
            self.last_drag_pos = event.position().x()

    def mouseMoveEvent(self, event):
        if self.dragging_in:
            self.update_in_point_from_mouse(event)
        elif self.dragging_out:
            self.update_out_point_from_mouse(event)
        elif self.dragging_position:
            self.update_position_from_mouse(event)
        elif self.dragging_timeline:
            # Pan the timeline view
            current_pos = event.position().x()
            if self.last_drag_pos is not None:
                delta_x = current_pos - self.last_drag_pos
                track_rect = self.rect().adjusted(12, self.rect().center().y() - 8, -12, 0)
                
                # Convert pixel delta to frame delta
                visible_duration = self.view_end - self.view_start
                frame_delta = -(delta_x / track_rect.width()) * visible_duration
                
                # Apply pan
                new_start = self.view_start + frame_delta
                new_end = self.view_end + frame_delta
                
                # Clamp to valid range
                if new_start < 0:
                    new_end -= new_start
                    new_start = 0
                if new_end > self.duration:
                    new_start -= (new_end - self.duration)
                    new_end = self.duration
                
                self.view_start = max(0, new_start)
                self.view_end = min(self.duration, new_end)
                
                self.update()
            self.last_drag_pos = current_pos

    def mouseReleaseEvent(self, event):
        self.dragging_in = False
        self.dragging_out = False
        self.dragging_position = False
        self.dragging_timeline = False
        self.last_drag_pos = None
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def update_position_from_mouse(self, event):
        track_rect = self.rect().adjusted(12, self.rect().center().y() - 8, -12, 0)
        pos = event.position().x()
        new_pos = self._screen_to_frame(pos, track_rect)
        
        if new_pos != self.current_position:
            self.current_position = new_pos
            self.positionChanged.emit(new_pos)
            self.update()

    def update_in_point_from_mouse(self, event):
        track_rect = self.rect().adjusted(12, self.rect().center().y() - 8, -12, 0)
        pos = event.position().x()
        new_in = self._screen_to_frame(pos, track_rect)
        new_in = max(0, min(new_in, self.out_point))
        
        if new_in != self.in_point:
            self.in_point = new_in
            self.inOutChanged.emit(self.in_point, self.out_point)
            self.update()

    def update_out_point_from_mouse(self, event):
        track_rect = self.rect().adjusted(12, self.rect().center().y() - 8, -12, 0)
        pos = event.position().x()
        new_out = self._screen_to_frame(pos, track_rect)
        new_out = max(self.in_point, min(new_out, self.duration))
        
        if new_out != self.out_point:
            self.out_point = new_out
            self.inOutChanged.emit(self.in_point, self.out_point)
            self.update()
