"""
Video Exporter - Export trimmed videos using FFmpeg
"""
import os
import subprocess
import threading
from pathlib import Path


class VideoExporter:
    def __init__(self, main_window):
        self.main_window = main_window
        self.cancel_requested = False
        self.process = None
        self.has_nvidia_gpu = self._check_nvidia_gpu()
        
    def _check_nvidia_gpu(self):
        """Check if NVIDIA GPU is available for hardware acceleration"""
        try:
            result = subprocess.run(
                ['nvidia-smi'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            return result.returncode == 0 and 'NVIDIA' in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return False
    
    def cancel_export(self):
        """Cancel the current export operation"""
        self.cancel_requested = True
        if self.process:
            self.process.terminate()
        print("Export cancelled by user")
    
    def get_unique_filename(self, file_path):
        """Generate a unique filename if file already exists"""
        base, ext = os.path.splitext(file_path)
        counter = 1
        unique_file = file_path
        while os.path.exists(unique_file):
            unique_file = f"{base}_{counter}{ext}"
            counter += 1
        return unique_file
    
    def export_segments(self, input_path, output_path, segments, fps, format_type="MP4", combine=False):
        """
        Export multiple trimmed video segments
        
        Args:
            input_path: Path to source video
            output_path: Base path for exported videos
            segments: List of segment dictionaries with 'in_frame' and 'out_frame'
            fps: Frames per second of the source video
            format_type: Output format (MP4, AVI, MOV, WMV)
            combine: If True, combine all segments into one file
        """
        if not segments:
            raise ValueError("No segments to export")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Source video not found: {input_path}")
        
        # Reset cancel flag
        self.cancel_requested = False
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        if combine:
            # Export all segments combined into one file
            self._export_combined(input_path, output_path, segments, fps, format_type)
        else:
            # Export each segment as a separate file
            self._export_separate(input_path, output_path, segments, fps, format_type)
    
    def _export_separate(self, input_path, output_path, segments, fps, format_type):
        """Export segments as separate files"""
        base, ext = os.path.splitext(output_path)
        exported_files = []
        
        for idx, segment in enumerate(segments, 1):
            if self.cancel_requested:
                break
            
            # Create output path for this segment
            segment_path = f"{base}_segment{idx:03d}{ext}"
            segment_path = self.get_unique_filename(segment_path)
            
            # Export this segment
            self._export_single_segment(
                input_path, 
                segment_path, 
                segment['in_frame'],
                segment['out_frame'],
                fps,
                format_type,
                idx,
                len(segments)
            )
            exported_files.append(segment_path)
        
        return exported_files
    
    def _export_combined(self, input_path, output_path, segments, fps, format_type):
        """Export all segments combined into one file"""
        output_path = self.get_unique_filename(output_path)
        
        # Create a temporary file list for FFmpeg concat
        concat_file = output_path + "_concat.txt"
        temp_files = []
        
        try:
            # First, export each segment to a temporary file
            for idx, segment in enumerate(segments, 1):
                if self.cancel_requested:
                    return
                
                temp_path = f"{output_path}_temp{idx:03d}.ts"
                self._export_single_segment(
                    input_path,
                    temp_path,
                    segment['in_frame'],
                    segment['out_frame'],
                    fps,
                    "TS",  # Use transport stream for better concatenation
                    idx,
                    len(segments)
                )
                temp_files.append(temp_path)
            
            if self.cancel_requested:
                return
            
            # Create concat file
            with open(concat_file, 'w') as f:
                for temp_file in temp_files:
                    f.write(f"file '{os.path.abspath(temp_file)}'\n")
            
            # Combine all segments using FFmpeg concat
            self._combine_segments(concat_file, output_path, format_type)
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            try:
                if os.path.exists(concat_file):
                    os.remove(concat_file)
            except:
                pass
    
    def _export_single_segment(self, input_path, output_path, in_frame, out_frame, fps, format_type, current=1, total=1):
        """Export a single segment"""
        start_time = in_frame / fps
        duration = (out_frame - in_frame) / fps
        
        cmd = self._build_ffmpeg_command(
            input_path,
            output_path,
            start_time,
            duration,
            format_type
        )
        
        print(f"Exporting segment {current}/{total}: {output_path}")
        self.main_window.update_status(f"Exporting segment {current}/{total}...")
        
        # Run synchronously for batch exports
        self._run_export_sync(cmd, output_path)
    
    def _combine_segments(self, concat_file, output_path, format_type):
        """Combine segments using FFmpeg concat demuxer"""
        self.main_window.update_status("Combining segments...")
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
        ]
        
        # Add format-specific options
        if format_type.upper() == "MP4":
            cmd.extend(["-c", "copy"])
        else:
            cmd.extend(["-c:v", "copy", "-c:a", "copy"])
        
        cmd.extend(["-y", output_path])
        
        print(f"Combining segments into: {output_path}")
        self._run_export_sync(cmd, output_path)
    
    def export_video(self, input_path, output_path, in_frame, out_frame, fps, format_type="MP4"):
        """
        Export a trimmed video segment (legacy method for single segment export)
        
        Args:
            input_path: Path to source video
            output_path: Path for exported video
            in_frame: Starting frame number
            out_frame: Ending frame number
            fps: Frames per second of the source video
            format_type: Output format (MP4, AVI, MOV, WMV)
        """
        segments = [{'in_frame': in_frame, 'out_frame': out_frame}]
        self._export_separate(input_path, output_path, segments, fps, format_type)
    
    def _build_ffmpeg_command(self, input_path, output_path, start_time, duration, format_type):
        """Build the FFmpeg command based on available hardware and format"""
        
        # Base command with fast seeking
        cmd = [
            "ffmpeg",
            "-ss", str(start_time),  # Seek to start time (fast seek before input)
            "-i", input_path,
            "-t", str(duration),  # Duration to encode
            "-map_metadata", "-1",  # Remove metadata
            "-y"  # Overwrite output file
        ]
        
        # Format-specific encoding settings
        if format_type.upper() == "MP4":
            if self.has_nvidia_gpu:
                # GPU-accelerated H.264 encoding
                cmd.extend([
                    "-c:v", "h264_nvenc",
                    "-preset", "slow",
                    "-cq", "23",
                ])
            else:
                # Software H.264 encoding
                cmd.extend([
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                ])
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
            ])
        
        elif format_type.upper() == "AVI":
            cmd.extend([
                "-c:v", "mpeg4",
                "-q:v", "5",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
            ])
        
        elif format_type.upper() == "MOV":
            if self.has_nvidia_gpu:
                cmd.extend([
                    "-c:v", "h264_nvenc",
                    "-preset", "slow",
                    "-cq", "23",
                ])
            else:
                cmd.extend([
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                ])
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "192k",
            ])
        
        elif format_type.upper() == "WMV":
            cmd.extend([
                "-c:v", "wmv2",
                "-b:v", "5000k",
                "-c:a", "wmav2",
                "-b:a", "192k",
            ])
        
        # Add output path
        cmd.append(output_path)
        
        return cmd
    
    def _run_export_sync(self, cmd, output_path):
        """Run export synchronously (for batch processing)"""
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stdout, stderr = self.process.communicate()
            
            if self.process.returncode != 0 and not self.cancel_requested:
                print(f"FFmpeg error: {stderr}")
                raise Exception(f"Export failed: {stderr[:200]}")
                
        except Exception as e:
            if not self.cancel_requested:
                raise e
        finally:
            self.process = None
    
    def _run_export(self, cmd, output_path):
        """Run the FFmpeg export process"""
        try:
            # Update status
            self.main_window.update_status("Exporting video...")
            
            # Start FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Wait for completion
            stdout, stderr = self.process.communicate()
            
            # Check result
            if self.process.returncode == 0 and not self.cancel_requested:
                print(f"Export completed successfully: {output_path}")
                self.main_window.update_status("Export completed successfully!")
                self._show_success_message(output_path)
            elif self.cancel_requested:
                print("Export was cancelled")
                self.main_window.update_status("Export cancelled")
            else:
                print(f"Export failed with code {self.process.returncode}")
                print(f"Error: {stderr}")
                self.main_window.update_status(f"Export failed: {stderr[:100]}")
                
        except Exception as e:
            print(f"Export error: {str(e)}")
            self.main_window.update_status(f"Export error: {str(e)}")
        finally:
            self.process = None
    
    def _show_success_message(self, output_path):
        """Show success message on the main thread"""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import QTimer
        
        def show_msg():
            msg = QMessageBox(self.main_window)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Export Complete")
            msg.setText("Video exported successfully!")
            msg.setInformativeText(f"Saved to:\n{output_path}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        
        # Use QTimer to show message on main thread
        QTimer.singleShot(0, show_msg)
