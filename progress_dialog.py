"""
Enhanced Progress Dialog for HALog
Native Windows styling with responsive design and validation reporting
"""

from PyQt5.QtWidgets import (QProgressDialog, QProgressBar, QLabel, QVBoxLayout, 
                           QHBoxLayout, QWidget, QApplication, QFrame, QTextEdit, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class ProgressDialog(QProgressDialog):
    """Enhanced progress dialog with validation reporting and native Windows styling"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Processing...")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumWidth(500)  # Wider to accommodate validation info
        self.setMinimumHeight(200)  # Taller for validation details

        # Use native Windows styling with validation info styling
        self.setStyleSheet("""
            QProgressDialog {
                background-color: white;
                border: 1px solid #c0c0c0;
                font-family: 'Segoe UI';
                font-size: 9pt;
            }
            QProgressBar {
                border: 1px solid #c0c0c0;
                border-radius: 2px;
                text-align: center;
                background-color: #f0f0f0;
                color: #000000;
                font-size: 8pt;
                min-height: 16px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 1px;
            }
            QLabel {
                color: #000000;
                font-size: 9pt;
                padding: 4px;
            }
            QLabel#validationStatus {
                color: #0078d4;
                font-weight: bold;
                font-size: 8pt;
                padding: 2px;
            }
            QLabel#qualityScore {
                font-weight: bold;
                font-size: 8pt;
                padding: 2px;
            }
            QLabel#anomalyCount {
                color: #d13212;
                font-weight: bold;
                font-size: 8pt;
                padding: 2px;
            }
            QPushButton {
                background-color: #e1e1e1;
                border: 1px solid #adadad;
                padding: 6px 12px;
                border-radius: 2px;
                font-size: 9pt;
                min-width: 75px;
            }
            QPushButton:hover {
                background-color: #e5f1fb;
                border: 1px solid #0078d4;
            }
            QPushButton:pressed {
                background-color: #cce4f7;
            }
            QFrame#validationFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                padding: 6px;
                margin: 4px;
            }
        """)

        self.current_phase = "processing"
        self.current_phase_progress = 0
        
        # Validation display components
        self.validation_enabled = False
        self.validation_frame = None
        self.quality_label = None
        self.anomaly_label = None
        self.validation_status_label = None
        
        self._setup_validation_display()

        # Setup initial state
        self.setRange(0, 100)
        self.setValue(0)
        self.setLabelText("Initializing...")
        
        # Ensure dialog stays visible and responsive
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    
    def _setup_validation_display(self):
        """Setup validation information display within the dialog"""
        try:
            # Create validation frame
            self.validation_frame = QFrame()
            self.validation_frame.setObjectName("validationFrame")
            self.validation_frame.setVisible(False)  # Initially hidden
            
            # Create validation layout
            validation_layout = QVBoxLayout(self.validation_frame)
            validation_layout.setContentsMargins(6, 6, 6, 6)
            validation_layout.setSpacing(3)
            
            # Validation status label
            self.validation_status_label = QLabel("Data Validation: Enabled")
            self.validation_status_label.setObjectName("validationStatus")
            validation_layout.addWidget(self.validation_status_label)
            
            # Quality and anomaly info in horizontal layout
            info_layout = QHBoxLayout()
            
            self.quality_label = QLabel("Quality: --")
            self.quality_label.setObjectName("qualityScore")
            info_layout.addWidget(self.quality_label)
            
            self.anomaly_label = QLabel("Anomalies: --")
            self.anomaly_label.setObjectName("anomalyCount")
            info_layout.addWidget(self.anomaly_label)
            
            info_layout.addStretch()  # Push labels to left
            validation_layout.addLayout(info_layout)
            
            # Add validation frame to dialog (this is tricky with QProgressDialog)
            # We'll update the label text to include validation info instead
            
        except Exception as e:
            print(f"Warning: Could not setup validation display: {e}")
    
    def enable_validation_display(self):
        """Enable validation information display"""
        self.validation_enabled = True
        if self.validation_frame:
            self.validation_frame.setVisible(True)
    
    def disable_validation_display(self):
        """Disable validation information display"""
        self.validation_enabled = False
        if self.validation_frame:
            self.validation_frame.setVisible(False)
    
    def ensure_visible(self):
        """Ensure the dialog is visible and responsive"""
        if not self.isVisible():
            self.show()
        self.raise_()
        self.activateWindow()
        QApplication.processEvents()

    def set_phase(self, phase_name, initial_progress=0):
        """Set current processing phase"""
        phase_names = {
            "uploading": "Reading and uploading file...",
            "processing": "Processing data...",
            "finalizing": "Finalizing...",
            "saving": "Saving results...",
            "analyzing": "Analyzing data..."
        }

        self.current_phase = phase_name
        self.current_phase_progress = initial_progress

        label_text = phase_names.get(phase_name, f"{phase_name.title()}...")
        self.setLabelText(label_text)
        self.setValue(int(initial_progress))  # Ensure integer value
        
        # Ensure dialog is visible when setting phase
        self.ensure_visible()

    def update_progress(self, percentage, status_message="", lines_processed=0, 
                       total_lines=0, bytes_processed=0, total_bytes=0, validation_info=None):
        """Update progress with detailed information and validation results"""
        self.setValue(min(100, max(0, int(percentage))))

        # Create enhanced status message with validation info
        display_message = status_message
        
        if self.validation_enabled and validation_info:
            quality_score = validation_info.get('quality_score', 0)
            anomalies = validation_info.get('anomalies', 0)
            
            # Update validation labels if available
            if self.quality_label:
                self.quality_label.setText(f"Quality: {quality_score:.1f}%")
                
                # Color code quality score
                if quality_score >= 90:
                    self.quality_label.setStyleSheet("color: #2d7d2d; font-weight: bold;")  # Green
                elif quality_score >= 75:
                    self.quality_label.setStyleSheet("color: #cc8800; font-weight: bold;")  # Orange  
                else:
                    self.quality_label.setStyleSheet("color: #d13212; font-weight: bold;")  # Red
            
            if self.anomaly_label:
                self.anomaly_label.setText(f"Anomalies: {anomalies}")
            
            # Include validation info in main status message
            if status_message:
                display_message = f"{status_message}\n• Quality: {quality_score:.1f}% • Anomalies: {anomalies}"
        
        if display_message:
            self.setLabelText(display_message)
        
        # Ensure dialog is visible and on top
        if not self.isVisible():
            self.show()
        self.raise_()
        self.activateWindow()

        # Process events to keep UI responsive
        QApplication.processEvents()
    
    def update_validation_results(self, quality_score, anomaly_count, warnings=None):
        """Update just the validation results display"""
        if not self.validation_enabled:
            return
        
        try:
            if self.quality_label:
                self.quality_label.setText(f"Quality: {quality_score:.1f}%")
                
                # Color code quality score
                if quality_score >= 90:
                    color = "#2d7d2d"  # Green
                elif quality_score >= 75:
                    color = "#cc8800"  # Orange
                else:
                    color = "#d13212"  # Red
                
                self.quality_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 8pt; padding: 2px;")
            
            if self.anomaly_label:
                self.anomaly_label.setText(f"Anomalies: {anomaly_count}")
            
            # Update main status if needed
            if warnings and len(warnings) > 0:
                recent_warning = warnings[-1] if warnings else ""
                if len(recent_warning) > 80:
                    recent_warning = recent_warning[:77] + "..."
                
                if self.validation_status_label:
                    self.validation_status_label.setText(f"Latest: {recent_warning}")
        
        except Exception as e:
            print(f"Warning: Could not update validation results: {e}")

    def mark_complete(self):
        """Mark processing as complete with validation summary"""
        self.setValue(100)
        
        if self.validation_enabled:
            self.setLabelText("Complete! Validation summary available.")
        else:
            self.setLabelText("Complete!")
            
        self.ensure_visible()