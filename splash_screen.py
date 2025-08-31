"""
Enhanced Splash Screen and Bootstrap - Gobioeng HALog
Professional splash screen with animated loading and resource handling
Consolidated bootstrap functionality
Developer: Tanmay Pandey
Company: gobioeng.com
"""

from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QProgressBar, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect  # Explicitly import QRect
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QLinearGradient, QBrush
from resource_helper import resource_path, generate_icon
import time
import os


class BootstrapSplashWidget(QWidget):
    """
    Bootstrap splash screen component for lightweight initialization
    Developed by Tanmay Pandey - gobioeng.com
    """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(500, 350)
        self.setStyleSheet("background: #2c3e50;")
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # --- App logo from assets (robust path) ---
        self.logo_label = QLabel()
        logo_pix = QPixmap(resource_path("linac_logo.ico"))
        if not logo_pix.isNull():
            self.logo_label.setPixmap(
                logo_pix.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.logo_label.setText("🏥")
            self.logo_label.setStyleSheet("font-size: 64px; color: gold;")
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # App name
        app_name = QLabel("Gobioeng HALog")
        app_name.setFont(QFont("Arial", 22, QFont.Bold))
        app_name.setStyleSheet("color: #ecf0f1; margin-top:8px;")
        app_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name)

        # Version
        version = QLabel("Version 0.0.1 beta")
        version.setFont(QFont("Arial", 12))
        version.setStyleSheet("color: #bdc3c7; margin-bottom:8px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # Tagline
        tagline = QLabel("Professional LINAC water system monitor")
        tagline.setFont(QFont("Arial", 11))
        tagline.setStyleSheet("color: #95a5a6; margin-bottom:12px;")
        tagline.setAlignment(Qt.AlignCenter)
        layout.addWidget(tagline)

        # Designer/company footer with proper attribution
        designer = QLabel(
            "Designed & Developed by <b>Tanmay Pandey</b> • "
            "<a href='https://gobioeng.com'>gobioeng.com</a>"
        )
        designer.setOpenExternalLinks(True)
        designer.setFont(QFont("Arial", 11))
        designer.setStyleSheet("color: #ecf0f1; margin-top:24px;")
        designer.setAlignment(Qt.AlignCenter)
        layout.addWidget(designer)


class SplashScreen(QSplashScreen):
    finished = pyqtSignal()

    def __init__(self, app_version="0.0.1"):
        # Create pixmap for the splash screen
        pixmap = QPixmap(500, 350)
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.start_time = time.time()
        self.app_version = app_version
        self.minimum_display_time = 2.5  # seconds

        # Create a timer for animations
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(100)
        self.animation_step = 0

        self.setupUI()
        self.animation_timer.start()

    def setupUI(self):
        # Get the pixmap for customization
        pixmap = self.pixmap()
        pixmap.fill(Qt.transparent)

        # Create a painter for drawing on the pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Microsoft Word 2024 style gradient background - very subtle
        gradient = QLinearGradient(0, 0, 0, pixmap.height())
        gradient.setColorAt(0, QColor("#ffffff"))  # Pure white
        gradient.setColorAt(0.5, QColor("#fafbfc"))  # Very light gray
        gradient.setColorAt(1, QColor("#f8f9fa"))  # Slightly more gray
        painter.fillRect(pixmap.rect(), QBrush(gradient))

        # Subtle border like Word 2024
        painter.setPen(QPen(QColor("#e3e4e6"), 1))
        painter.drawRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)

        # Modern logo placement - centered and larger
        logo_size = 80
        logo_x = (pixmap.width() - logo_size) // 2
        logo_y = 60

        logo_path = resource_path("linac_logo.ico")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            painter.drawPixmap(
                logo_x,
                logo_y,
                logo_pixmap.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            )
        else:
            # Generate modern icon as fallback
            fallback_icon = generate_icon(logo_size)
            painter.drawPixmap(logo_x, logo_y, fallback_icon)

        # Main application title - Word 2024 style typography
        painter.setPen(QColor("#323130"))  # Word 2024 text color
        font = QFont("Segoe UI", 28, QFont.Light)  # Segoe UI like Word
        painter.setFont(font)
        title_y = logo_y + logo_size + 30
        title_rect = QRect(0, title_y, pixmap.width(), 40)
        painter.drawText(title_rect, Qt.AlignCenter, "HALog")

        # Subtitle with clean typography
        painter.setPen(QColor("#605e5c"))  # Subtle gray
        font = QFont("Segoe UI", 14, QFont.Normal)
        painter.setFont(font)
        subtitle_y = title_y + 45
        subtitle_rect = QRect(0, subtitle_y, pixmap.width(), 25)
        painter.drawText(subtitle_rect, Qt.AlignCenter, "LINAC Log Analyzer")

        # Version info in a clean, minimal way
        painter.setPen(QColor("#8a8886"))  # Light gray
        font = QFont("Segoe UI", 11, QFont.Normal)
        painter.setFont(font)
        version_y = subtitle_y + 35
        version_rect = QRect(0, version_y, pixmap.width(), 20)
        painter.drawText(version_rect, Qt.AlignCenter, f"Version {self.app_version}")

        # Progress bar area (modern flat design)
        progress_y = pixmap.height() - 80
        progress_width = 200
        progress_x = (pixmap.width() - progress_width) // 2
        
        # Progress bar background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#f3f2f1"))  # Light background
        painter.drawRoundedRect(progress_x, progress_y, progress_width, 6, 3, 3)

        # Branding footer - very subtle like Word 2024
        painter.setPen(QColor("#a19f9d"))  # Very light gray
        font = QFont("Segoe UI", 9, QFont.Normal)
        painter.setFont(font)
        branding_y = pixmap.height() - 25
        branding_rect = QRect(0, branding_y, pixmap.width(), 20)
        painter.drawText(branding_rect, Qt.AlignCenter, "Powered by gobioeng.com")

        # Finish painting
        painter.end()

        # Set the modified pixmap back
        self.setPixmap(pixmap)

        # Modern progress bar widget
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(progress_x, progress_y, progress_width, 6)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f3f2f1;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;  /* Microsoft blue */
                border-radius: 3px;
            }
        """)
        self.progress_bar.setTextVisible(False)

        # Modern status label
        self.status_label = QLabel(self)
        self.status_label.setGeometry(0, pixmap.height() - 55, pixmap.width(), 20)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #605e5c;
                font-family: 'Segoe UI';
                font-size: 11px;
                background: transparent;
            }
        """)
        self.status_label.setText("Initializing...")

    def update_animation(self):
        self.animation_step += 1

        # Update dots in status label for animation effect
        dots = "." * (self.animation_step % 4)
        message = self.status_label.text().rstrip(".")
        if message.endswith("ing"):
            self.status_label.setText(f"{message}{dots}")

        # Update progress with a smooth animation
        current_value = self.progress_bar.value()
        if current_value < 95:  # Cap at 95% until explicitly completed
            self.progress_bar.setValue(min(current_value + 1, 95))

    def update_status(self, message, progress_value=None):
        self.status_label.setText(message)
        if progress_value is not None:
            self.progress_bar.setValue(progress_value)

    def finish(self, main_window):
        # Ensure minimum display time
        elapsed = time.time() - self.start_time
        if elapsed < self.minimum_display_time:
            QTimer.singleShot(
                int((self.minimum_display_time - elapsed) * 1000),
                lambda: self._do_finish(main_window),
            )
        else:
            self._do_finish(main_window)

    def _do_finish(self, main_window):
        self.animation_timer.stop()
        self.update_status("Ready!", 100)

        # Short delay before hiding splash
        QTimer.singleShot(300, lambda: super().finish(main_window))
        self.finished.emit()
