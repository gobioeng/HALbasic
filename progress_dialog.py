"""
Simplified Progress Dialog for HALog
Optimized for minimal overhead and fast updates
"""

from PyQt5.QtWidgets import QProgressDialog, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import time


class ProgressDialog(QProgressDialog):
    """Simplified progress dialog with essential features"""

    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.start_time = time.time()

    def setupUI(self):
        """Setup minimal UI"""
        self.setWindowTitle("Processing File")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumWidth(400)
        self.setRange(0, 100)
        self.setValue(0)

        # Simple styling
        self.setStyleSheet("""
            QProgressDialog {
                background-color: #f5f5f5;
                border-radius: 4px;
                padding: 16px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
                background-color: #e6e6e6;
                color: #333;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)

    def set_file_info(self, filename: str, file_size: int):
        """Set file information"""
        self.setWindowTitle(f"Processing: {filename}")
        size_mb = file_size / (1024 * 1024)
        self.setLabelText(f"Processing {filename} ({size_mb:.1f} MB)...")

    def update_progress(self, percentage: int, message: str = ""):
        """Update progress"""
        self.setValue(percentage)
        if message:
            self.setLabelText(message)

        # Process events to keep UI responsive
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

    def closeEvent(self, event):
        """Handle close event"""
        self.cancelled.emit()
        super().closeEvent(event)

    def reject(self):
        """Handle cancel"""
        self.cancelled.emit()
        super().reject()