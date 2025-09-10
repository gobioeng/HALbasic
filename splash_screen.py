"""
Minimalistic Splash Screen - HALog
Clean, modern splash screen with progress bar, logo with shadow, app name and version
Developer: Tanmay Pandey
Company: gobioeng.com
"""

from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QBrush, QPen
from resource_helper import resource_path, load_splash_icon
import time


class MinimalisticSplashScreen(QSplashScreen):
    """
    Minimalistic splash screen with clean design
    Features: Logo with shadow, app name, version, progress bar
    """
    finished = pyqtSignal()

    def __init__(self, app_version="1.0.0"):
        # Create clean splash screen INSTANTLY
        pixmap = QPixmap(400, 250)  # Smaller, more compact size
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)  # Added Qt.Tool to prevent blocking
        self.app_version = app_version
        self.start_time = time.time()
        # FIXED: Reduced minimum display time to prevent blocking menu access
        self.minimum_display_time = 1.5  # Reduced from 3.0 to 1.5 seconds to prevent menu blocking
        
        # OPTIMIZED: Less frequent animation updates to reduce CPU usage
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(200)  # Reduced from 100ms to 200ms
        self.animation_step = 0
        
        # INSTANT SETUP: Create UI immediately without delays
        self.setupUI()
        self.animation_timer.start()

    def setupUI(self):
        """Setup minimalistic UI with logo, shadow, name, version, and progress bar"""
        pixmap = self.pixmap()
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Clean white background with subtle rounded corners
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRoundedRect(0, 0, pixmap.width(), pixmap.height(), 8, 8)
        
        # Subtle border
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(0, 0, pixmap.width()-1, pixmap.height()-1, 8, 8)
        
        # Logo with shadow
        logo_size = 85
        logo_x = (pixmap.width() - logo_size) // 2
        logo_y = 30
        
        # Load logo
        try:
            logo_pixmap = load_splash_icon(logo_size)
            
            # Draw shadow first (offset by 2px)
            shadow_x = logo_x + 2
            shadow_y = logo_y + 2
            
            
            
            # Draw main logo
            painter.drawPixmap(logo_x, logo_y, logo_pixmap)
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback: simple circle with "HA"
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(33, 150, 243)))  # Blue
            painter.drawEllipse(logo_x, logo_y, logo_size, logo_size)
            
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Arial", 18, QFont.Bold)
            painter.setFont(font)
            painter.drawText(logo_x, logo_y, logo_size, logo_size, Qt.AlignCenter, "HA")
        
        # App name - Improved typography
        painter.setPen(QColor(28, 28, 31))  # Darker text for better readability
        font = QFont("Segoe UI", 20, QFont.Bold)  # Larger, bold font with better letter spacing
        painter.setFont(font)
        name_y = logo_y + logo_size + 15  # Better spacing
        name_rect = QRect(0, name_y, pixmap.width(), 35)
        painter.drawText(name_rect, Qt.AlignCenter, "HALog")
        
        # Subtitle - Improved spacing and typography
        painter.setPen(QColor(102, 102, 102))  # Better contrast
        font = QFont("Segoe UI", 11, QFont.Normal)  # Slightly larger for readability
        painter.setFont(font)
        subtitle_y = name_y + 30  # Better spacing
        subtitle_rect = QRect(0, subtitle_y, pixmap.width(), 22)
        painter.drawText(subtitle_rect, Qt.AlignCenter, "LINAC Log Analysis Tool")
        
        # Version - Better typography and spacing
        painter.setPen(QColor(136, 136, 136))  # Improved color
        font = QFont("Segoe UI", 10, QFont.Normal)  # Consistent font family
        painter.setFont(font)
        version_y = subtitle_y + 20  # Better spacing
        version_rect = QRect(0, version_y, pixmap.width(), 18)
        painter.drawText(version_rect, Qt.AlignCenter, f"Version {self.app_version}")
        
        painter.end()
        self.setPixmap(pixmap)
        
        # Progress bar
        progress_y = pixmap.height() - 40
        progress_width = 200
        progress_x = (pixmap.width() - progress_width) // 2
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(progress_x, progress_y, progress_width, 6)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #2196f3;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setTextVisible(False)
        
        # Status label
        self.status_label = QLabel(self)
        self.status_label.setGeometry(0, progress_y + 15, pixmap.width(), 20)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #555;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 10px;
                font-weight: 400;
                background: transparent;
            }
        """)
        self.status_label.setText("Initializing...")

    def update_animation(self):
        """Simple animation for status text"""
        self.animation_step += 1
        
        # Animate dots
        dots = "." * (self.animation_step % 4)
        message = self.status_label.text().rstrip(".")
        if not message.endswith("!"):
            self.status_label.setText(f"{message}{dots}")
        
        # Auto-increment progress
        current_value = self.progress_bar.value()
        if current_value < 95:
            self.progress_bar.setValue(min(current_value + 1, 95))

    def update_status(self, message, progress_value=None):
        """Update status message and progress"""
        self.status_label.setText(message)
        if progress_value is not None:
            self.progress_bar.setValue(progress_value)

    def finish(self, main_window):
        """Finish splash screen with minimum display time and aggressive cleanup"""
        try:
            elapsed = time.time() - self.start_time
            if elapsed < self.minimum_display_time:
                remaining_time = int((self.minimum_display_time - elapsed) * 1000)
                QTimer.singleShot(remaining_time, lambda: self._do_finish(main_window))
            else:
                self._do_finish(main_window)
                
            # Additional safety: Force cleanup after 5 seconds regardless
            QTimer.singleShot(5000, lambda: self._force_cleanup())
        except Exception as e:
            print(f"Error in splash finish: {e}")
            # Fallback: try to finish immediately
            try:
                self._do_finish(main_window)
            except Exception as fallback_error:
                print(f"Fallback finish failed: {fallback_error}")
                # Last resort: hide splash screen
                self._force_cleanup()

    def _force_cleanup(self):
        """Force cleanup of splash screen to prevent menu blocking"""
        try:
            if hasattr(self, 'animation_timer'):
                self.animation_timer.stop()
            self.hide()
            self.close()
            self.finished.emit()
        except:
            pass  # Ignore cleanup errors

    def _do_finish(self, main_window):
        """Complete the splash screen"""
        try:
            self.animation_timer.stop()
            self.update_status("Ready!", 100)
            # Fix: Avoid lambda/super combination - use a proper method reference
            QTimer.singleShot(300, lambda: self._complete_finish(main_window))
            self.finished.emit()
        except Exception as e:
            print(f"Error in _do_finish: {e}")
            # Fallback: finish immediately
            try:
                super().finish(main_window)
                self.finished.emit()
            except Exception as fallback_error:
                print(f"Fallback finish also failed: {fallback_error}")
    
    def _complete_finish(self, main_window):
        """Complete the finish process - separated from lambda to avoid super() issues"""
        try:
            super().finish(main_window)
        except Exception as e:
            print(f"Error in _complete_finish: {e}")
            # If super().finish fails, try to hide the splash screen directly
            try:
                self.hide()
                self.close()
            except:
                pass


# For backward compatibility with existing imports
SplashScreen = MinimalisticSplashScreen
BootstrapSplashWidget = MinimalisticSplashScreen
