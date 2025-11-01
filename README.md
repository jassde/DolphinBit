<img width="1402" height="979" alt="image" src="https://github.com/user-attachments/assets/ea12ddc8-5560-47c7-8163-01eb530fd70b" />

# 🎬 Video Trimmer - Professional Video Editor

A powerful, feature-rich video trimming application with a modern UI, built with PyQt6 and OpenCV.

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

### Core Functionality
- 📹 **Multi-Segment Trimming** - Cut multiple parts from a single video
- 🎯 **Frame-Perfect Editing** - Frame-by-frame navigation for precision
- 💾 **Flexible Export** - Export as separate clips or one combined file
- 🖱️ **Drag & Drop** - Drop videos directly into the application
- 🔄 **Segment Reordering** - Drag segments to change export order

### Performance
- ⚡ **Hardware Acceleration** - Automatic GPU detection and usage
- 🗂️ **Smart Caching** - LRU cache stores 150+ frames for instant playback
- 🚀 **Optimized Loading** - Pre-fetches frames for smooth scrubbing
- 💨 **Fast Export** - GPU-accelerated encoding when available

### User Experience
- ⌨️ **Keyboard Shortcuts** - Complete keyboard control
- 🔍 **Timeline Zoom** - Zoom from 10% to 1000% with mouse wheel
- 🎨 **Modern UI** - Professional design with purple-blue gradient theme
- 📊 **Video Overlay** - Real-time timecode, frame count, FPS, resolution
- 📏 **Timeline Ruler** - Frame numbers or timecode display
- ⚙️ **Settings Persistence** - Remembers your preferences

### Design System
- 🎨 **Consistent Colors** - Semantic color scheme throughout
- 📝 **Typography Hierarchy** - Clear font sizes and weights
- 📐 **8-Point Grid** - Consistent spacing and layout
- 💎 **Modern Style** - Gradients, shadows, smooth interactions

## 🚀 Quick Start

### Installation

1. **Clone or download** this repository

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg** (required for export):
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

4. **Run the application**:
```bash
python main.py
```

## 📖 Usage Guide

### Basic Workflow

1. **Import Video**
   - Click "📁 Import Videos" or drag & drop a video file
   - Supported formats: MP4, AVI, MOV, MKV, WMV

2. **Set Trim Points**
   - Use arrow keys to navigate frame-by-frame
   - Press `I` to set In point (green marker)
   - Press `O` to set Out point (red marker)

3. **Add Segment**
   - Press `A` or click "➕ Add Segment"
   - Segment appears in left panel with duration

4. **Repeat for More Segments**
   - Set new In/Out points
   - Add as many segments as needed
   - Reorder by dragging in the list

5. **Export**
   - Click "💾 Export Project"
   - Choose mode:
     - **Separate Clips**: Each segment as individual file
     - **Combined File**: All segments merged into one
   - Select format (MP4, AVI, MOV, WMV) and quality
   - Click Export

## ⌨️ Keyboard Shortcuts

### Playback
- `Space` - Play / Pause
- `Ctrl+P` - Play
- `Ctrl+S` - Stop

### Navigation
- `←` / `→` - Previous/Next frame
- `Shift+←` / `Shift+→` - Skip 1 second backward/forward

### Editing
- `I` - Set In point
- `O` - Set Out point
- `X` - Clear In/Out points
- `A` - Add segment
- `Delete` - Remove selected segment

### Timeline
- `Ctrl++` / `Ctrl+-` - Zoom in/out
- `Ctrl+0` - Fit timeline
- `Mouse Wheel` - Zoom at cursor
- `Shift+Drag` - Pan timeline

### File
- `Ctrl+O` - Import videos
- `Ctrl+E` - Export project

## 🎯 Pro Tips

### Frame-Perfect Editing
1. Zoom in on timeline (`Ctrl++` or mouse wheel)
2. Use arrow keys to move frame-by-frame
3. Watch video player for exact frame
4. Set In/Out points with `I` and `O`

### Fast Workflow
```
1. Press I (set in point)
2. Press O (set out point)
3. Press A (add segment)
4. Repeat!
```

### Timeline Navigation
- **Zoom with mouse**: Hover over timeline and scroll
- **Pan**: Hold Shift and drag, or use middle mouse button
- **Fit view**: Press `Ctrl+0` to see entire timeline
- **Precise positioning**: Zoom in, click exact frame

### Performance
- **First load is slower**: Building frame cache
- **Subsequent playback**: Lightning fast from cache
- **GPU acceleration**: Automatic if NVIDIA GPU detected
- **Export speed**: Uses hardware encoding when available

## 🎨 Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│ [📁 Import] [💾 Export]                                  │
├──────────────┬──────────────────────────────────────────┤
│ Trim Segments│  [Video Player - 800x600 minimum]       │
│              │                                           │
│ Segment 1    │  [⏵Play] [⏸Pause] [⏹Stop]              │
│ Segment 2    │  [Set In] [Set Out] [Clear]             │
│ Segment 3    │                                           │
│              │  00:05 / 02:30                           │
│ [➕] [🗑️] [Clear] │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│              │  [Progress Bar]                          │
│ Export Mode  │  Timeline Zoom: [slider] [Fit]          │
│ Format: MP4  │                                           │
│ Quality: High│                                           │
└──────────────┴──────────────────────────────────────────┘
```

## 🛠️ System Requirements

- **OS**: Windows 10+, macOS 10.14+, Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **GPU**: Optional (NVIDIA for hardware acceleration)
- **FFmpeg**: Required for export functionality

## 📦 Dependencies

- PyQt6 >= 6.4.0
- opencv-python >= 4.8.0
- numpy >= 1.24.0

## 🐛 Troubleshooting

### Video won't load
- Check if file format is supported
- Try converting to MP4 with another tool
- Ensure video file isn't corrupted

### Export fails
- Verify FFmpeg is installed: `ffmpeg -version`
- Check disk space for output folder
- Try different output format

### Slow playback
- First playback builds cache (normal)
- Close other applications
- Reduce video resolution for editing
- Check if hardware acceleration is active

### No keyboard shortcuts
- Click on video player or timeline first
- Shortcuts won't work in text fields

## 🤝 Contributing

Suggestions and improvements welcome! Please test thoroughly before submitting changes.

## 📄 License

Free to use for personal and commercial projects.

## 🙏 Acknowledgments

Built with:
- **PyQt6** - Modern Qt bindings
- **OpenCV** - Computer vision library
- **FFmpeg** - Video processing powerhouse

---

**Happy Editing! 🎬✨**
