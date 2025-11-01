"""
Video Handler - Core video processing and playback logic with caching and hardware acceleration
"""
import cv2
from collections import OrderedDict
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


class VideoHandler:
    def __init__(self, cache_size=150):
        self.cap = None
        self.current_video = None
        self.frame_count = 0
        self.fps = 0
        self.duration = 0
        
        # Frame cache for smooth playback
        self.frame_cache = OrderedDict()
        self.cache_size = cache_size
        self.cache_enabled = True
        
        # Hardware acceleration
        self.hw_accel_available = False
        self._check_hw_acceleration()
    
    def _check_hw_acceleration(self):
        """Check if hardware acceleration is available"""
        try:
            # Try to open a test capture with hardware acceleration
            backends = [
                (cv2.CAP_DSHOW, "DirectShow (Windows)"),
                (cv2.CAP_MSMF, "Media Foundation (Windows)"),
                (cv2.CAP_FFMPEG, "FFmpeg"),
                (cv2.CAP_ANY, "Default")
            ]
            
            for backend, name in backends:
                try:
                    test_cap = cv2.VideoCapture(0, backend)
                    if test_cap.isOpened():
                        test_cap.release()
                        print(f"Hardware acceleration available via {name}")
                        self.hw_accel_available = True
                        return
                except:
                    continue
                    
            print("Hardware acceleration not available, using software decoding")
        except Exception as e:
            print(f"Hardware acceleration check failed: {e}")
            self.hw_accel_available = False
    
    def load_video(self, video_path):
        """Load a video file with hardware acceleration and return its properties"""
        if self.cap:
            self.cap.release()
        
        # Clear cache when loading new video
        self.frame_cache.clear()
        
        # Try hardware accelerated backends first
        backends_to_try = [
            cv2.CAP_FFMPEG,
            cv2.CAP_MSMF,  # Media Foundation (Windows, HW accel)
            cv2.CAP_DSHOW,  # DirectShow (Windows)
            cv2.CAP_ANY
        ]
        
        self.cap = None
        for backend in backends_to_try:
            try:
                test_cap = cv2.VideoCapture(video_path, backend)
                if test_cap.isOpened():
                    self.cap = test_cap
                    print(f"Video opened with backend: {backend}")
                    break
                test_cap.release()
            except:
                continue
        
        # Fallback to default
        if not self.cap:
            self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            return None
        
        # Enable hardware acceleration if available
        try:
            self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
        except:
            pass
        
        # Get video properties
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        self.current_video = video_path
        
        # Pre-cache first frames for instant playback
        self._prefetch_frames(0, min(30, self.frame_count))
        
        return {
            'frame_count': self.frame_count,
            'fps': self.fps,
            'duration': self.duration,
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        }
    
    def _prefetch_frames(self, start_frame, end_frame):
        """Pre-fetch frames into cache for smooth playback"""
        if not self.cache_enabled or not self.cap:
            return
        
        current_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        for frame_num in range(start_frame, min(end_frame, self.frame_count)):
            if frame_num in self.frame_cache:
                continue
            
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()
            if ret:
                self._add_to_cache(frame_num, frame.copy())
        
        # Restore position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos)
    
    def _add_to_cache(self, frame_num, frame):
        """Add frame to cache with LRU eviction"""
        if not self.cache_enabled:
            return
        
        # Remove oldest if cache is full
        if len(self.frame_cache) >= self.cache_size:
            self.frame_cache.popitem(last=False)
        
        self.frame_cache[frame_num] = frame
    
    def _get_from_cache(self, frame_num):
        """Get frame from cache if available"""
        if not self.cache_enabled:
            return None
        
        if frame_num in self.frame_cache:
            # Move to end (most recently used)
            frame = self.frame_cache.pop(frame_num)
            self.frame_cache[frame_num] = frame
            return frame
        return None
    
    def get_current_frame(self):
        """Read and return the current frame (with caching)"""
        if not self.cap:
            return None
        
        current_frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        # Try cache first
        cached_frame = self._get_from_cache(current_frame_num)
        if cached_frame is not None:
            # Still need to advance position
            ret, _ = self.cap.read()
            return cached_frame.copy()
        
        ret, frame = self.cap.read()
        if ret:
            # Add to cache
            self._add_to_cache(current_frame_num, frame.copy())
            
            # Prefetch next frames in background
            next_start = current_frame_num + 1
            next_end = min(current_frame_num + 10, self.frame_count)
            if next_end > next_start:
                self._prefetch_frames(next_start, next_end)
            
            return frame
        return None
    
    def get_frame_at_position(self, frame_number):
        """Seek to a specific frame and return it (with caching)"""
        if not self.cap:
            return None
        
        # Check cache first
        cached_frame = self._get_from_cache(frame_number)
        if cached_frame is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number + 1)
            return cached_frame.copy()
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        frame = self.get_current_frame()
        
        # Prefetch surrounding frames
        prefetch_start = max(0, frame_number - 5)
        prefetch_end = min(frame_number + 15, self.frame_count)
        self._prefetch_frames(prefetch_start, prefetch_end)
        
        return frame
    
    def get_current_position(self):
        """Get the current frame position"""
        if self.cap:
            return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return 0
    
    def seek(self, frame_number):
        """Seek to a specific frame"""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Prefetch frames around seek position
            prefetch_start = max(0, frame_number - 5)
            prefetch_end = min(frame_number + 20, self.frame_count)
            self._prefetch_frames(prefetch_start, prefetch_end)
    
    def frame_to_pixmap(self, frame, target_size=None):
        """Convert a CV2 frame to QPixmap"""
        if frame is None:
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        # Convert to QImage
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # Scale if target size provided
        if target_size:
            pixmap = pixmap.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        
        return pixmap
    
    def clear_cache(self):
        """Clear the frame cache"""
        self.frame_cache.clear()
    
    def get_cache_info(self):
        """Get cache statistics"""
        return {
            'size': len(self.frame_cache),
            'max_size': self.cache_size,
            'enabled': self.cache_enabled,
            'hw_accel': self.hw_accel_available
        }
    
    def release(self):
        """Release video capture resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        self.frame_cache.clear()
