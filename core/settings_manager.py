"""
Settings Manager - Persistent application settings
"""
from PyQt6.QtCore import QSettings
import json


class SettingsManager:
    def __init__(self):
        self.settings = QSettings('VideoTrimmer', 'Settings')
        self._init_defaults()
    
    def _init_defaults(self):
        """Initialize default settings if not present"""
        defaults = {
            'recent_files': [],
            'max_recent_files': 10,
            'last_export_path': '',
            'default_export_format': 'MP4',
            'default_export_quality': 'High',
            'default_export_mode': 'Separate Clips',
            'cache_size': 150,
            'cache_enabled': True,
            'zoom_level': 100,
            'window_geometry': None,
            'window_state': None,
            'playback_fps': 30,
            'auto_save_segments': True,
            'show_frame_numbers': True,
            'show_timecode': True,
            'theme': 'dark',
            'gpu_acceleration': True
        }
        
        for key, value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)
    
    # Recent Files
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        recent = self.get_recent_files()
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        
        max_recent = self.get('max_recent_files', 10)
        recent = recent[:max_recent]
        
        self.settings.setValue('recent_files', recent)
    
    def get_recent_files(self):
        """Get list of recent files"""
        return self.settings.value('recent_files', [])
    
    def clear_recent_files(self):
        """Clear recent files list"""
        self.settings.setValue('recent_files', [])
    
    # Export Settings
    def save_export_settings(self, format_type, quality, mode, output_path):
        """Save last used export settings"""
        self.settings.setValue('default_export_format', format_type)
        self.settings.setValue('default_export_quality', quality)
        self.settings.setValue('default_export_mode', mode)
        self.settings.setValue('last_export_path', output_path)
    
    def get_export_settings(self):
        """Get last used export settings"""
        return {
            'format': self.settings.value('default_export_format', 'MP4'),
            'quality': self.settings.value('default_export_quality', 'High'),
            'mode': self.settings.value('default_export_mode', 'Separate Clips'),
            'last_path': self.settings.value('last_export_path', '')
        }
    
    # Window State
    def save_window_state(self, geometry, state):
        """Save window geometry and state"""
        self.settings.setValue('window_geometry', geometry)
        self.settings.setValue('window_state', state)
    
    def restore_window_state(self):
        """Restore window geometry and state"""
        return {
            'geometry': self.settings.value('window_geometry', None),
            'state': self.settings.value('window_state', None)
        }
    
    # Cache Settings
    def save_cache_settings(self, size, enabled):
        """Save cache configuration"""
        self.settings.setValue('cache_size', size)
        self.settings.setValue('cache_enabled', enabled)
    
    def get_cache_settings(self):
        """Get cache configuration"""
        return {
            'size': int(self.settings.value('cache_size', 150)),
            'enabled': self.settings.value('cache_enabled', True, type=bool)
        }
    
    # Timeline Settings
    def save_zoom_level(self, zoom):
        """Save timeline zoom level"""
        self.settings.setValue('zoom_level', zoom)
    
    def get_zoom_level(self):
        """Get saved zoom level"""
        return int(self.settings.value('zoom_level', 100))
    
    # Generic getter/setter
    def get(self, key, default=None):
        """Get any setting value"""
        return self.settings.value(key, default)
    
    def set(self, key, value):
        """Set any setting value"""
        self.settings.setValue(key, value)
    
    # Project Management
    def save_project(self, project_data, file_path):
        """Save project to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    def load_project(self, file_path):
        """Load project from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
    
    # Reset
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings.clear()
        self._init_defaults()
