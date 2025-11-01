"""
Video Trimmer - Main Entry Point
Professional Video Editor Application
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import VideoTrimmerApp


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Video Trimmer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("VideoTrimmer")
    
    window = VideoTrimmerApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
