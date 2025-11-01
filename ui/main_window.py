"""
Main Window - Primary application window with advanced features
"""
import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QListWidget, 
                            QListWidgetItem, QLineEdit, QComboBox,
                            QMessageBox, QSplitter, QProgressBar,
                            QFileDialog, QSizePolicy, QSlider, QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent, QKeySequence, QShortcut

from widgets.timeline_widget import TimelineWidget
from widgets.video_player_widget import VideoPlayerWidget
from core.video_handler import VideoHandler
from core.video_exporter import VideoExporter
from core.settings_manager import SettingsManager
from ui.styles import get_dark_palette, get_stylesheet, Colors, Typography, Spacing


class VideoTrimmerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Trimmer - Professional Video Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Hide status bar
        self.statusBar().hide()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Initialize video data
        self.video_handler = VideoHandler()
        self.video_exporter = VideoExporter(self)
        self.settings_manager = SettingsManager()
        self.video_files = []
        self.is_playing = False
        self.trim_segments = []  # Store all trim segments
        
        # Load settings
        self._load_settings()
        
        # Playback timer
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.playback_tick)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Setup UI
        self.setup_ui()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are video files
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if Path(file_path).suffix.lower() in video_extensions:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
        files_added = 0
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).suffix.lower() in video_extensions:
                # Add to video list
                self.video_files.append(file_path)
                files_added += 1
        
        if files_added > 0:
            self.update_status(f"Loaded {files_added} video(s)")
            # Automatically load the first dropped video
            first_dropped_file = self.video_files[-files_added]
            self.load_video(first_dropped_file)
        else:
            QMessageBox.warning(self, "Invalid Files", "No valid video files were dropped")
        
        event.acceptProposedAction()

    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setPalette(get_dark_palette())
        self.setStyleSheet(get_stylesheet())

    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Top toolbar
        main_layout.addLayout(self.create_toolbar())
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Video list and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Video player and timeline
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 1000])
        main_layout.addWidget(splitter)

    def create_toolbar(self):
        """Create the enhanced toolbar with grouped buttons"""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(Spacing.MD)
        
        # File group
        file_group = QWidget()
        file_layout = QHBoxLayout(file_group)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(Spacing.SM)
        
        file_label = QLabel("File:")
        file_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.SEMIBOLD};")
        
        self.import_btn = QPushButton("📁 Import")
        self.import_btn.clicked.connect(self.import_videos)
        self.import_btn.setToolTip("Import videos (Ctrl+O)")
        self.import_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.SECONDARY});
                border: none;
                color: {Colors.TEXT_PRIMARY};
                padding: {Spacing.SM}px {Spacing.MD}px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                font-weight: {Typography.SEMIBOLD};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY_LIGHT}, stop:1 {Colors.SECONDARY_LIGHT});
            }}
        """)
        
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.clicked.connect(self.export_project)
        self.export_btn.setToolTip("Export project (Ctrl+E)")
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.SUCCESS};
                border: none;
                color: {Colors.TEXT_PRIMARY};
                padding: {Spacing.SM}px {Spacing.MD}px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                font-weight: {Typography.SEMIBOLD};
            }}
            QPushButton:hover {{
                background: {Colors.PRIMARY_LIGHT};
            }}
        """)
        
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.import_btn)
        file_layout.addWidget(self.export_btn)
        
        # View group
        view_group = QWidget()
        view_layout = QHBoxLayout(view_group)
        view_layout.setContentsMargins(0, 0, 0, 0)
        view_layout.setSpacing(Spacing.SM)
        
        view_label = QLabel("View:")
        view_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.SEMIBOLD};")
        
        self.toggle_info_btn = QPushButton("ℹ️ Info")
        self.toggle_info_btn.setCheckable(True)
        self.toggle_info_btn.setChecked(True)
        self.toggle_info_btn.clicked.connect(self.toggle_player_info)
        self.toggle_info_btn.setToolTip("Toggle video info overlay")
        
        self.toggle_ruler_btn = QPushButton("📏 Ruler")
        self.toggle_ruler_btn.setCheckable(True)
        self.toggle_ruler_btn.setChecked(True)
        self.toggle_ruler_btn.clicked.connect(self.toggle_timeline_ruler)
        self.toggle_ruler_btn.setToolTip("Toggle timeline ruler")
        
        view_layout.addWidget(view_label)
        view_layout.addWidget(self.toggle_info_btn)
        view_layout.addWidget(self.toggle_ruler_btn)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        toolbar_layout.addWidget(file_group)
        toolbar_layout.addWidget(self._create_separator())
        toolbar_layout.addWidget(view_group)
        toolbar_layout.addWidget(spacer)
        
        return toolbar_layout
    
    def _create_separator(self):
        """Create a vertical separator"""
        separator = QLabel()
        separator.setFixedWidth(1)
        separator.setStyleSheet(f"background-color: {Colors.DIVIDER};")
        separator.setFixedHeight(30)
        return separator

    def create_left_panel(self):
        """Create the left panel with enhanced trim segments list"""
        left_widget = QWidget()
        left_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.SURFACE};
                border-radius: {Spacing.BORDER_RADIUS_LARGE}px;
                padding: {Spacing.MD}px;
            }}
        """)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(Spacing.MD)
        
        # Trim segments header
        segments_label = QLabel("📋 Trim Segments")
        segments_label.setFont(Typography.get_font(Typography.H3_SIZE, Typography.BOLD))
        segments_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        
        # Segment count badge
        self.segment_count_label = QLabel("0 segments")
        self.segment_count_label.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.SMALL_SIZE}px;
            padding: {Spacing.XS}px {Spacing.SM}px;
            background-color: {Colors.SURFACE_HOVER};
            border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
        """)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(segments_label)
        header_layout.addWidget(self.segment_count_label)
        header_layout.addStretch()
        
        # Enhanced segments list with better styling
        self.segments_list = QListWidget()
        self.segments_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.segments_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.segments_list.model().rowsMoved.connect(self._on_segments_reordered)
        self.segments_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Colors.BACKGROUND};
                border: 1px solid {Colors.BORDER};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                padding: {Spacing.XS}px;
            }}
            QListWidget::item {{
                padding: {Spacing.MD}px;
                margin: {Spacing.XS}px;
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                font-size: {Typography.BODY_SIZE}px;
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.SECONDARY});
            }}
            QListWidget::item:hover {{
                background-color: {Colors.SURFACE_HOVER};
            }}
        """)
        
        # Segment controls with improved styling
        segment_controls = QHBoxLayout()
        segment_controls.setSpacing(Spacing.SM)
        
        self.add_segment_btn = QPushButton("➕ Add")
        self.remove_segment_btn = QPushButton("🗑️ Remove")
        self.clear_segments_btn = QPushButton("Clear All")
        
        self.add_segment_btn.clicked.connect(self.add_segment)
        self.remove_segment_btn.clicked.connect(self.remove_segment)
        self.clear_segments_btn.clicked.connect(self.clear_segments)
        
        self.add_segment_btn.setToolTip("Add segment (A)")
        self.remove_segment_btn.setToolTip("Remove segment (Delete)")
        self.clear_segments_btn.setToolTip("Clear all segments")
        
        self.add_segment_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                border: none;
                color: white;
                font-weight: {Typography.SEMIBOLD};
                padding: {Spacing.SM}px {Spacing.MD}px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_LIGHT};
            }}
        """)
        
        self.remove_segment_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.DANGER};
                border: none;
                color: white;
                font-weight: {Typography.SEMIBOLD};
                padding: {Spacing.SM}px {Spacing.MD}px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QPushButton:hover {{
                background-color: #ff6b9d;
            }}
        """)
        
        segment_controls.addWidget(self.add_segment_btn)
        segment_controls.addWidget(self.remove_segment_btn)
        segment_controls.addWidget(self.clear_segments_btn)
        
        # Export settings
        export_group = self.create_export_settings()
        
        # Assemble left panel
        left_layout.addLayout(header_layout)
        left_layout.addWidget(self.segments_list)
        left_layout.addLayout(segment_controls)
        left_layout.addWidget(export_group)
        left_layout.addStretch()
        
        return left_widget

    def create_export_settings(self):
        """Create the export settings widget"""
        export_group = QWidget()
        export_layout = QVBoxLayout(export_group)
        
        export_label = QLabel("Export Settings")
        export_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        self.export_name = QLineEdit()
        self.export_name.setPlaceholderText("Export file name...")
        
        # Export mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Export Mode:"))
        self.export_mode_combo = QComboBox()
        self.export_mode_combo.addItems(["Separate Clips", "Combined File"])
        mode_layout.addWidget(self.export_mode_combo)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MOV", "WMV"])
        format_layout.addWidget(self.format_combo)
        
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High", "Medium", "Low"])
        quality_layout.addWidget(self.quality_combo)
        
        export_layout.addWidget(export_label)
        export_layout.addWidget(self.export_name)
        export_layout.addLayout(mode_layout)
        export_layout.addLayout(format_layout)
        export_layout.addLayout(quality_layout)
        
        return export_group

    def create_right_panel(self):
        """Create the right panel with video player and timeline"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Video player
        self.video_player = VideoPlayerWidget()
        self.video_player.setMinimumSize(800, 600)
        right_layout.addWidget(self.video_player, stretch=1)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        
        self.play_btn = QPushButton("⏵ Play")
        self.pause_btn = QPushButton("⏸ Pause")
        self.stop_btn = QPushButton("⏹ Stop")
        
        self.play_btn.clicked.connect(self.play_video)
        self.pause_btn.clicked.connect(self.pause_video)
        self.stop_btn.clicked.connect(self.stop_video)
        
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.stop_btn)
        
        # In/Out point controls
        self.set_in_btn = QPushButton("Set In Point")
        self.set_out_btn = QPushButton("Set Out Point")
        self.clear_in_out_btn = QPushButton("Clear")
        
        self.set_in_btn.clicked.connect(self.set_in_point)
        self.set_out_btn.clicked.connect(self.set_out_point)
        self.clear_in_out_btn.clicked.connect(self.clear_in_out_points)
        
        controls_layout.addWidget(self.set_in_btn)
        controls_layout.addWidget(self.set_out_btn)
        controls_layout.addWidget(self.clear_in_out_btn)
        controls_layout.addStretch()
        
        # Time label above timeline
        time_layout = QHBoxLayout()
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("font-size: 14px; color: #ccc;")
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        
        # Timeline
        self.timeline = TimelineWidget()
        self.timeline.positionChanged.connect(self.seek_video)
        self.timeline.inOutChanged.connect(self.on_in_out_changed)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Timeline Zoom:")
        zoom_label.setStyleSheet("color: #ccc; font-size: 12px;")
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)  # 10% = 0.1x
        self.zoom_slider.setMaximum(1000)  # 1000% = 10x
        self.zoom_slider.setValue(100)  # 100% = 1x
        self.zoom_slider.setMaximumWidth(150)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        
        zoom_fit_btn = QPushButton("Fit")
        zoom_fit_btn.setMaximumWidth(50)
        zoom_fit_btn.clicked.connect(self._zoom_to_fit)
        
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(zoom_fit_btn)
        zoom_layout.addStretch()
        
        # Assemble right panel
        right_layout.addLayout(controls_layout)
        right_layout.addLayout(time_layout)
        right_layout.addWidget(self.timeline)
        right_layout.addWidget(self.progress_bar)
        right_layout.addLayout(zoom_layout)
        
        return right_widget

    def import_videos(self):
        """Import video files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        
        if files:
            for file_path in files:
                self.video_files.append(file_path)
            
            self.update_status(f"Loaded {len(files)} video(s)")
            # Load the first imported video
            self.load_video(files[0])

    def add_segment(self):
        """Add current in/out points as a trim segment"""
        if not self.video_handler.cap:
            QMessageBox.warning(self, "No Video", "Please load a video first")
            return
        
        in_point = self.timeline.in_point
        out_point = self.timeline.out_point
        
        if in_point >= out_point:
            QMessageBox.warning(self, "Invalid Segment", "Out point must be after in point")
            return
        
        # Calculate duration
        duration = (out_point - in_point) / self.video_handler.fps
        mins, secs = divmod(int(duration), 60)
        
        # Create segment data
        segment = {
            'in_frame': in_point,
            'out_frame': out_point,
            'duration': duration
        }
        self.trim_segments.append(segment)
        
        # Add to list widget
        segment_text = f"Segment {len(self.trim_segments)}: {in_point} → {out_point} ({mins:02d}:{secs:02d})"
        self.segments_list.addItem(segment_text)
        
        self.update_status(f"Added segment {len(self.trim_segments)}")
        
    def remove_segment(self):
        """Remove selected segment"""
        current_row = self.segments_list.currentRow()
        if current_row >= 0:
            self.segments_list.takeItem(current_row)
            self.trim_segments.pop(current_row)
            # Update segment numbers
            self._refresh_segment_list()
            self.update_status(f"Removed segment {current_row + 1}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a segment to remove")
    
    def clear_segments(self):
        """Clear all segments"""
        if self.trim_segments:
            reply = QMessageBox.question(
                self,
                "Clear Segments",
                f"Remove all {len(self.trim_segments)} segments?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.segments_list.clear()
                self.trim_segments.clear()
                self.update_status("All segments cleared")
    
    def _refresh_segment_list(self):
        """Refresh the segment list display with enhanced formatting"""
        self.segments_list.clear()
        for idx, segment in enumerate(self.trim_segments, 1):
            duration = segment['duration']
            mins, secs = divmod(int(duration), 60)
            
            # Enhanced segment text with icons and formatting
            segment_text = f"🎬 Segment {idx}  |  {segment['in_frame']:,} → {segment['out_frame']:,}  |  ⏱ {mins:02d}:{secs:02d}"
            item = QListWidgetItem(segment_text)
            
            # Add tooltip with details
            tooltip = f"Segment {idx}\nStart: Frame {segment['in_frame']}\nEnd: Frame {segment['out_frame']}\nDuration: {mins:02d}:{secs:02d}"
            item.setToolTip(tooltip)
            
            self.segments_list.addItem(item)
        
        # Update segment count badge
        total_duration = sum(seg['duration'] for seg in self.trim_segments)
        total_mins, total_secs = divmod(int(total_duration), 60)
        self.segment_count_label.setText(f"{len(self.trim_segments)} segments • {total_mins:02d}:{total_secs:02d} total")
    
    def _load_settings(self):
        """Load settings from settings manager"""
        # Restore window state
        window_state = self.settings_manager.restore_window_state()
        if window_state['geometry']:
            self.restoreGeometry(window_state['geometry'])
        if window_state['state']:
            self.restoreState(window_state['state'])
        
        # Load export settings
        export_settings = self.settings_manager.get_export_settings()
        # Will be applied when export dialog opens
        
        # Load cache settings
        cache_settings = self.settings_manager.get_cache_settings()
        if hasattr(self, 'video_handler'):
            self.video_handler.cache_size = cache_settings['size']
            self.video_handler.cache_enabled = cache_settings['enabled']
    
    def _save_settings(self):
        """Save settings to settings manager"""
        self.settings_manager.save_window_state(
            self.saveGeometry(),
            self.saveState()
        )
        self.settings_manager.save_zoom_level(int(self.timeline.zoom_level * 100))
    
    def toggle_player_info(self):
        """Toggle video player info overlay"""
        self.video_player.toggle_info_overlay()
        self.update_status("Info overlay toggled")
    
    def toggle_timeline_ruler(self):
        """Toggle timeline ruler display"""
        self.timeline.show_frame_numbers = not self.timeline.show_frame_numbers
        self.timeline.update()
        self.update_status("Timeline ruler toggled")

    def load_video(self, video_path):
        """Load a video file"""
        try:
            video_props = self.video_handler.load_video(video_path)
            
            if not video_props:
                QMessageBox.warning(self, "Error", "Could not open video file")
                return
            
            # Update timeline
            self.timeline.set_duration(video_props['frame_count'])
            self.timeline.set_in_out_points(0, video_props['frame_count'])
            self.timeline.set_fps(video_props['fps'])
            
            # Update UI
            mins, secs = divmod(int(video_props['duration']), 60)
            self.time_label.setText(f"00:00 / {mins:02d}:{secs:02d}")
            self.progress_bar.setMaximum(video_props['frame_count'])
            
            # Update video player info
            resolution = f"{video_props['width']}x{video_props['height']}"
            self.video_player.set_video_info(
                0, 
                video_props['frame_count'], 
                "00:00:00:00",
                video_props['fps'],
                resolution
            )
            
            # Add to recent files
            self.settings_manager.add_recent_file(video_path)
            
            self.update_status(f"Loaded: {os.path.basename(video_path)}")
            
            # Show first frame
            self.show_current_frame()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load video: {str(e)}")

    def show_current_frame(self):
        """Display the current video frame"""
        frame = self.video_handler.get_current_frame()
        if frame is not None:
            pixmap = self.video_handler.frame_to_pixmap(
                frame,
                self.video_player.video_frame.size()
            )
            if pixmap:
                self.video_player.video_frame.setPixmap(pixmap)

    def play_video(self):
        """Start video playback"""
        if self.video_handler.cap and not self.is_playing:
            self.is_playing = True
            self.playback_timer.start(1000 // 30)  # 30 fps
            self.update_status("Playing...")

    def pause_video(self):
        """Pause video playback"""
        self.is_playing = False
        self.playback_timer.stop()
        self.update_status("Paused")

    def stop_video(self):
        """Stop video playback"""
        self.is_playing = False
        self.playback_timer.stop()
        if self.video_handler.cap:
            self.video_handler.seek(0)
            self.timeline.set_position(0)
            self.show_current_frame()
        self.update_status("Stopped")

    def playback_tick(self):
        """Handle playback timer tick"""
        if not self.video_handler.cap or not self.is_playing:
            return
            
        current_frame = self.video_handler.get_current_position()
        
        # Check if we've reached the out point
        if current_frame >= self.timeline.out_point:
            self.video_handler.seek(self.timeline.in_point)
            current_frame = self.timeline.in_point
        
        self.timeline.set_position(current_frame)
        self.show_current_frame()
        
        # Update time label
        current_time = current_frame / self.video_handler.fps if self.video_handler.fps > 0 else 0
        total_time = self.video_handler.duration
        current_mins, current_secs = divmod(int(current_time), 60)
        total_mins, total_secs = divmod(int(total_time), 60)
        self.time_label.setText(f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
        
        # Update video player overlay
        hours = current_mins // 60
        mins = current_mins % 60
        secs = current_secs
        frames = int(current_frame % self.video_handler.fps)
        timecode = f"{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"
        
        resolution = f"{int(self.video_handler.cap.get(3))}x{int(self.video_handler.cap.get(4))}"
        self.video_player.set_video_info(
            current_frame,
            self.video_handler.frame_count,
            timecode,
            self.video_handler.fps,
            resolution
        )
        
        self.progress_bar.setValue(current_frame)

    def seek_video(self, position):
        """Seek to a specific frame position"""
        self.video_handler.seek(position)
        self.show_current_frame()

    def set_in_point(self):
        """Set the in point at current position"""
        if self.video_handler.cap:
            current_frame = self.video_handler.get_current_position()
            self.timeline.set_in_out_points(current_frame, self.timeline.out_point)
            self.update_status(f"In point set at frame {current_frame}")

    def set_out_point(self):
        """Set the out point at current position"""
        if self.video_handler.cap:
            current_frame = self.video_handler.get_current_position()
            self.timeline.set_in_out_points(self.timeline.in_point, current_frame)
            self.update_status(f"Out point set at frame {current_frame}")

    def clear_in_out_points(self):
        """Clear in/out points"""
        self.timeline.set_in_out_points(0, self.video_handler.frame_count)
        self.update_status("In/Out points cleared")

    def on_in_out_changed(self, in_point, out_point):
        """Handle in/out point changes"""
        self.update_status(f"Trim region: {in_point} - {out_point} frames")

    def export_project(self):
        """Export the trimmed video segments"""
        if not self.video_handler.current_video:
            QMessageBox.warning(self, "Warning", "No video loaded to export")
            return
        
        # Check if there are segments to export
        if not self.trim_segments:
            QMessageBox.warning(
                self, 
                "No Segments", 
                "Please add at least one trim segment before exporting.\n\n"
                "Set In/Out points and click '➕ Add Segment'"
            )
            return
        
        # Check if FFmpeg is available
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  timeout=2)
            if result.returncode != 0:
                raise FileNotFoundError
        except (FileNotFoundError, subprocess.TimeoutExpired):
            QMessageBox.critical(
                self, 
                "FFmpeg Not Found", 
                "FFmpeg is required for video export but was not found.\n\n"
                "Please install FFmpeg and add it to your system PATH.\n"
                "Download from: https://ffmpeg.org/download.html"
            )
            return
        
        # Get export settings
        format_type = self.format_combo.currentText()
        extension = format_type.lower()
        export_mode = self.export_mode_combo.currentText()
        combine = (export_mode == "Combined File")
        
        # Get output filename
        default_name = self.export_name.text().strip()
        if not default_name:
            base_name = os.path.splitext(os.path.basename(self.video_handler.current_video))[0]
            if combine:
                default_name = f"{base_name}_combined"
            else:
                default_name = f"{base_name}_trimmed"
        
        # Open save dialog
        if combine:
            dialog_title = "Export Combined Video"
        else:
            dialog_title = "Export Video Segments (Base Name)"
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            dialog_title,
            default_name,
            f"{format_type} Files (*.{extension});;All Files (*)"
        )
        
        if not output_path:
            return  # User cancelled
        
        # Ensure correct extension
        if not output_path.lower().endswith(f'.{extension}'):
            output_path += f'.{extension}'
        
        # Calculate total duration
        total_duration = sum(seg['duration'] for seg in self.trim_segments)
        total_mins, total_secs = divmod(int(total_duration), 60)
        
        # Show confirmation
        if combine:
            message = (
                f"Export {len(self.trim_segments)} segments combined into one file?\n\n"
                f"Format: {format_type}\n"
                f"Total Duration: {total_mins:02d}:{total_secs:02d}\n"
                f"Segments: {len(self.trim_segments)}\n"
                f"Output: {os.path.basename(output_path)}"
            )
        else:
            message = (
                f"Export {len(self.trim_segments)} separate video files?\n\n"
                f"Format: {format_type}\n"
                f"Total Duration: {total_mins:02d}:{total_secs:02d}\n"
                f"Files will be named: {os.path.basename(output_path).replace(f'.{extension}', '')}_segment001.{extension}, etc."
            )
        
        reply = QMessageBox.question(
            self,
            "Confirm Export",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.update_status("Starting export...")
                
                # Run export in a thread to avoid blocking UI
                import threading
                
                def do_export():
                    try:
                        self.video_exporter.export_segments(
                            input_path=self.video_handler.current_video,
                            output_path=output_path,
                            segments=self.trim_segments,
                            fps=self.video_handler.fps,
                            format_type=format_type,
                            combine=combine
                        )
                        
                        # Show success message
                        if not self.video_exporter.cancel_requested:
                            from PyQt6.QtCore import QTimer
                            def show_success():
                                if combine:
                                    msg_text = "Combined video exported successfully!"
                                else:
                                    msg_text = f"{len(self.trim_segments)} video segments exported successfully!"
                                
                                QMessageBox.information(
                                    self,
                                    "Export Complete",
                                    f"{msg_text}\n\nSaved to:\n{output_path}"
                                )
                            QTimer.singleShot(0, show_success)
                            
                    except Exception as e:
                        # Show error on main thread
                        from PyQt6.QtCore import QTimer
                        def show_error():
                            QMessageBox.critical(
                                self,
                                "Export Error",
                                f"Failed to export video:\n{str(e)}"
                            )
                            self.update_status("Export failed")
                        QTimer.singleShot(0, show_error)
                
                thread = threading.Thread(target=do_export, daemon=True)
                thread.start()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to start export:\n{str(e)}"
                )
                self.update_status("Export failed")

    def update_status(self, message):
        """Update status message (shown in time label temporarily)"""
        # Store original text
        if not hasattr(self, '_original_time_text'):
            self._original_time_text = self.time_label.text()
        
        # Show status message
        self.time_label.setText(f"Status: {message}")
        self.time_label.setStyleSheet("font-size: 14px; color: #4a9eff;")
        
        # Restore after 3 seconds
        QTimer.singleShot(3000, self._restore_time_label)
    
    def _restore_time_label(self):
        """Restore time label to normal state"""
        if hasattr(self, '_original_time_text'):
            self.time_label.setText(self._original_time_text)
        self.time_label.setStyleSheet("font-size: 14px; color: #ccc;")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Playback controls
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_play_pause)
        QShortcut(QKeySequence("Ctrl+P"), self, self.play_video)
        QShortcut(QKeySequence("Ctrl+S"), self, self.stop_video)
        
        # Frame navigation
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.previous_frame)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.next_frame)
        QShortcut(QKeySequence("Shift+Left"), self, self.skip_backward)
        QShortcut(QKeySequence("Shift+Right"), self, self.skip_forward)
        
        # Trim points
        QShortcut(QKeySequence("I"), self, self.set_in_point)
        QShortcut(QKeySequence("O"), self, self.set_out_point)
        QShortcut(QKeySequence("X"), self, self.clear_in_out_points)
        
        # Segments
        QShortcut(QKeySequence("A"), self, self.add_segment)
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self, self.remove_segment)
        QShortcut(QKeySequence("Ctrl+Shift+A"), self, self.clear_segments)
        
        # File operations
        QShortcut(QKeySequence("Ctrl+O"), self, self.import_videos)
        QShortcut(QKeySequence("Ctrl+E"), self, self.export_project)
        
        # Timeline zoom
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in_timeline)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out_timeline)
        QShortcut(QKeySequence("Ctrl+0"), self, self._zoom_to_fit)
        
        self.update_status("Keyboard shortcuts enabled")
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()
    
    def next_frame(self):
        """Move to next frame"""
        if self.video_handler.cap:
            current = self.video_handler.get_current_position()
            new_pos = min(current + 1, self.video_handler.frame_count - 1)
            self.seek_video(new_pos)
            self.timeline.set_position(new_pos)
    
    def previous_frame(self):
        """Move to previous frame"""
        if self.video_handler.cap:
            current = self.video_handler.get_current_position()
            new_pos = max(current - 1, 0)
            self.seek_video(new_pos)
            self.timeline.set_position(new_pos)
    
    def skip_forward(self):
        """Skip forward 1 second"""
        if self.video_handler.cap:
            current = self.video_handler.get_current_position()
            skip_frames = int(self.video_handler.fps)
            new_pos = min(current + skip_frames, self.video_handler.frame_count - 1)
            self.seek_video(new_pos)
            self.timeline.set_position(new_pos)
    
    def skip_backward(self):
        """Skip backward 1 second"""
        if self.video_handler.cap:
            current = self.video_handler.get_current_position()
            skip_frames = int(self.video_handler.fps)
            new_pos = max(current - skip_frames, 0)
            self.seek_video(new_pos)
            self.timeline.set_position(new_pos)
    
    def zoom_in_timeline(self):
        """Zoom in timeline"""
        self.timeline.zoom_in()
        self._update_zoom_slider()
    
    def zoom_out_timeline(self):
        """Zoom out timeline"""
        self.timeline.zoom_out()
        self._update_zoom_slider()
    
    def _zoom_to_fit(self):
        """Reset timeline zoom to fit"""
        self.timeline.zoom_to_fit()
        self.zoom_slider.setValue(100)
    
    def _on_zoom_changed(self, value):
        """Handle zoom slider change"""
        zoom_level = value / 100.0
        self.timeline.set_zoom(zoom_level)
    
    def _update_zoom_slider(self):
        """Update zoom slider to match timeline zoom"""
        zoom_value = int(self.timeline.zoom_level * 100)
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(zoom_value)
        self.zoom_slider.blockSignals(False)
    
    def _on_segments_reordered(self, parent, start, end, destination, row):
        """Handle segment reordering via drag and drop"""
        # Rebuild the segments list from the widget order
        new_segments = []
        for i in range(self.segments_list.count()):
            item_text = self.segments_list.item(i).text()
            # Extract segment number from text (format: "Segment N: ...")
            try:
                seg_num = int(item_text.split(':')[0].split()[-1]) - 1
                if 0 <= seg_num < len(self.trim_segments):
                    new_segments.append(self.trim_segments[seg_num])
            except:
                pass
        
        if len(new_segments) == len(self.trim_segments):
            self.trim_segments = new_segments
            self._refresh_segment_list()
            self.update_status("Segments reordered")

    def closeEvent(self, event):
        """Handle window close event"""
        self._save_settings()
        self.video_handler.release()
        event.accept()
