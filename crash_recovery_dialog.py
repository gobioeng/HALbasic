"""
Professional Crash Recovery Dialog for HALbasic
Provides user-friendly crash recovery and error reporting interface

Author: gobioeng.com
Date: 2025-01-20
"""

import sys
import os
import time
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QProgressBar, QFrame, QScrollArea, QWidget,
    QCheckBox, QGroupBox, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette


class CrashRecoveryDialog(QDialog):
    """
    Professional crash recovery dialog
    Provides options for crash reporting, data recovery, and safe restart
    """
    
    recovery_requested = pyqtSignal(bool)  # restart_requested
    report_submitted = pyqtSignal(str)  # report_content
    
    def __init__(self, crash_reason: str = "", crash_info: dict = None, parent=None):
        super().__init__(parent)
        self.crash_reason = crash_reason
        self.crash_info = crash_info or {}
        self.recovery_options = {}
        
        self.setWindowTitle("HALbasic - Application Recovery")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.setMaximumSize(800, 700)
        
        self._setup_ui()
        self._setup_styles()
        self._populate_crash_info()
        
        # Center the dialog
        self._center_dialog()
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        self._create_header(layout)
        
        # Crash information section
        self._create_crash_info_section(layout)
        
        # Recovery options section
        self._create_recovery_options_section(layout)
        
        # Action buttons
        self._create_action_buttons(layout)
    
    def _create_header(self, parent_layout):
        """Create header with icon and title"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Application icon (if available)
        try:
            from resource_helper import get_app_icon
            icon_label = QLabel()
            icon_pixmap = get_app_icon()
            if icon_pixmap and not icon_pixmap.isNull():
                scaled_pixmap = icon_pixmap.pixmap(48, 48)
                icon_label.setPixmap(scaled_pixmap)
            else:
                icon_label.setText("⚠️")
                icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(48, 48)
            header_layout.addWidget(icon_label)
        except:
            # Fallback to warning emoji
            icon_label = QLabel("⚠️")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(48, 48)
            header_layout.addWidget(icon_label)
        
        # Title and description
        text_layout = QVBoxLayout()
        
        title_label = QLabel("Application Recovery Required")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(
            "HALbasic has detected an unexpected issue and needs to recover. "
            "Your data and settings will be preserved."
        )
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Segoe UI", 9))
        text_layout.addWidget(desc_label)
        
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        parent_layout.addWidget(header_frame)
    
    def _create_crash_info_section(self, parent_layout):
        """Create crash information section"""
        info_group = QGroupBox("Crash Information")
        info_layout = QVBoxLayout(info_group)
        
        # Crash reason
        reason_label = QLabel(f"Reason: {self.crash_reason}")
        reason_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        info_layout.addWidget(reason_label)
        
        # Detailed crash info (collapsible)
        self.crash_details = QTextEdit()
        self.crash_details.setMaximumHeight(100)
        self.crash_details.setFont(QFont("Consolas", 8))
        self.crash_details.setReadOnly(True)
        info_layout.addWidget(self.crash_details)
        
        # Show/hide details button
        self.details_button = QPushButton("Show Details")
        self.details_button.clicked.connect(self._toggle_details)
        info_layout.addWidget(self.details_button)
        
        parent_layout.addWidget(info_group)
    
    def _create_recovery_options_section(self, parent_layout):
        """Create recovery options section"""
        options_group = QGroupBox("Recovery Options")
        options_layout = QVBoxLayout(options_group)
        
        # Data recovery options
        self.preserve_data_cb = QCheckBox("Preserve all data and settings")
        self.preserve_data_cb.setChecked(True)
        options_layout.addWidget(self.preserve_data_cb)
        
        self.restore_session_cb = QCheckBox("Restore previous session")
        self.restore_session_cb.setChecked(True)
        options_layout.addWidget(self.restore_session_cb)
        
        self.safe_mode_cb = QCheckBox("Start in safe mode (disabled extensions)")
        options_layout.addWidget(self.safe_mode_cb)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        options_layout.addWidget(separator)
        
        # Error reporting
        self.send_report_cb = QCheckBox("Send crash report to improve HALbasic")
        self.send_report_cb.setChecked(True)
        options_layout.addWidget(self.send_report_cb)
        
        report_note = QLabel(
            "Crash reports help us identify and fix issues. No personal data is included."
        )
        report_note.setFont(QFont("Segoe UI", 8))
        report_note.setStyleSheet("color: gray;")
        report_note.setWordWrap(True)
        options_layout.addWidget(report_note)
        
        parent_layout.addWidget(options_group)
    
    def _create_action_buttons(self, parent_layout):
        """Create action buttons"""
        button_layout = QHBoxLayout()
        
        # Recovery progress (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)
        
        button_layout.addStretch()
        
        # Exit button
        self.exit_button = QPushButton("Exit Application")
        self.exit_button.clicked.connect(self._exit_application)
        button_layout.addWidget(self.exit_button)
        
        # Restart button
        self.restart_button = QPushButton("Restart HALbasic")
        self.restart_button.setDefault(True)
        self.restart_button.clicked.connect(self._restart_application)
        button_layout.addWidget(self.restart_button)
        
        parent_layout.addLayout(button_layout)
    
    def _setup_styles(self):
        """Setup professional styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QPushButton:default {
                background-color: #28a745;
            }
            
            QPushButton:default:hover {
                background-color: #1e7e34;
            }
            
            QCheckBox {
                spacing: 8px;
                font-size: 10px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            
            QCheckBox::indicator:unchecked {
                border: 2px solid #6c757d;
                border-radius: 3px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                border: 2px solid #007bff;
                border-radius: 3px;
                background-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC41IDEuNUw0LjUgNy41TDEuNSA0LjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            
            QFrame[frameShape="4"] {
                color: #dee2e6;
            }
        """)
    
    def _populate_crash_info(self):
        """Populate crash information details"""
        details = []
        
        if self.crash_info:
            details.append(f"Crash Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if 'crash_count' in self.crash_info:
                details.append(f"Previous Crashes: {self.crash_info['crash_count']}")
            
            if 'last_crash_time' in self.crash_info and self.crash_info['last_crash_time']:
                last_crash = time.strftime(
                    '%Y-%m-%d %H:%M:%S', 
                    time.localtime(self.crash_info['last_crash_time'])
                )
                details.append(f"Last Crash: {last_crash}")
            
            if 'uptime_seconds' in self.crash_info:
                uptime = self.crash_info['uptime_seconds']
                details.append(f"Runtime: {uptime:.1f} seconds")
        
        details.append(f"Reason: {self.crash_reason}")
        details.append("\nSystem Information:")
        details.append(f"Python: {sys.version}")
        details.append(f"Platform: {sys.platform}")
        
        self.crash_details.setPlainText("\n".join(details))
    
    def _toggle_details(self):
        """Toggle crash details visibility"""
        if self.crash_details.isVisible():
            self.crash_details.hide()
            self.details_button.setText("Show Details")
        else:
            self.crash_details.show()
            self.details_button.setText("Hide Details")
    
    def _center_dialog(self):
        """Center the dialog on screen"""
        try:
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.desktop().screenGeometry()
            dialog_size = self.geometry()
            x = (screen.width() - dialog_size.width()) // 2
            y = (screen.height() - dialog_size.height()) // 2
            self.move(x, y)
        except:
            pass
    
    def _restart_application(self):
        """Handle restart request"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Collect recovery options
        self.recovery_options = {
            'preserve_data': self.preserve_data_cb.isChecked(),
            'restore_session': self.restore_session_cb.isChecked(),
            'safe_mode': self.safe_mode_cb.isChecked(),
            'send_report': self.send_report_cb.isChecked()
        }
        
        # Simulate recovery progress
        self._simulate_recovery_progress()
    
    def _simulate_recovery_progress(self):
        """Simulate recovery progress for user feedback"""
        self.restart_button.setEnabled(False)
        self.exit_button.setEnabled(False)
        
        progress_steps = [
            (20, "Saving application state..."),
            (40, "Cleaning up resources..."),
            (60, "Preparing recovery..."),
            (80, "Initializing restart..."),
            (100, "Restart ready!")
        ]
        
        self.current_step = 0
        self.progress_steps = progress_steps
        
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_timer.start(500)  # Update every 500ms
    
    def _update_progress(self):
        """Update progress bar"""
        if self.current_step < len(self.progress_steps):
            progress, message = self.progress_steps[self.current_step]
            self.progress_bar.setValue(progress)
            self.progress_bar.setFormat(f"{progress}% - {message}")
            self.current_step += 1
        else:
            self.progress_timer.stop()
            QTimer.singleShot(500, self._complete_restart)
    
    def _complete_restart(self):
        """Complete the restart process"""
        if self.recovery_options.get('send_report', False):
            self._send_crash_report()
        
        self.recovery_requested.emit(True)
        self.accept()
    
    def _send_crash_report(self):
        """Send crash report (placeholder implementation)"""
        try:
            report_content = self._generate_crash_report()
            self.report_submitted.emit(report_content)
            print("📧 Crash report generated (would be sent to developers)")
        except Exception as e:
            print(f"Warning: Could not generate crash report: {e}")
    
    def _generate_crash_report(self) -> str:
        """Generate crash report content"""
        report = []
        report.append("=== HALbasic Crash Report ===")
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
        report.append(f"Crash Reason: {self.crash_reason}")
        report.append("")
        
        if self.crash_info:
            report.append("Crash Information:")
            for key, value in self.crash_info.items():
                report.append(f"  {key}: {value}")
            report.append("")
        
        report.append("System Information:")
        report.append(f"  Python Version: {sys.version}")
        report.append(f"  Platform: {sys.platform}")
        report.append(f"  Working Directory: {os.getcwd()}")
        report.append("")
        
        report.append("Recovery Options Selected:")
        for key, value in self.recovery_options.items():
            report.append(f"  {key}: {value}")
        
        return "\n".join(report)
    
    def _exit_application(self):
        """Handle exit request"""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit HALbasic?\n\nAny unsaved work may be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.recovery_options.get('send_report', False):
                self._send_crash_report()
            
            self.recovery_requested.emit(False)
            self.reject()
    
    def get_recovery_options(self) -> dict:
        """Get selected recovery options"""
        return self.recovery_options


def show_crash_recovery_dialog(crash_reason: str = "", crash_info: dict = None, parent=None) -> dict:
    """
    Show crash recovery dialog and return recovery options
    
    Args:
        crash_reason: Reason for the crash
        crash_info: Additional crash information
        parent: Parent widget
        
    Returns:
        Dictionary with recovery options and restart flag
    """
    dialog = CrashRecoveryDialog(crash_reason, crash_info, parent)
    
    restart_requested = False
    recovery_options = {}
    
    def on_recovery(restart):
        nonlocal restart_requested
        restart_requested = restart
    
    dialog.recovery_requested.connect(on_recovery)
    
    result = dialog.exec_()
    recovery_options = dialog.get_recovery_options()
    
    return {
        'restart_requested': restart_requested,
        'recovery_options': recovery_options,
        'dialog_accepted': result == QDialog.Accepted
    }


if __name__ == "__main__":
    """Test the crash recovery dialog"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test crash info
    crash_info = {
        'crash_count': 2,
        'last_crash_time': time.time() - 3600,  # 1 hour ago
        'uptime_seconds': 157.3
    }
    
    result = show_crash_recovery_dialog(
        "Thread timeout detected", 
        crash_info
    )
    
    print("Recovery Dialog Result:")
    print(f"Restart Requested: {result['restart_requested']}")
    print(f"Recovery Options: {result['recovery_options']}")
    print(f"Dialog Accepted: {result['dialog_accepted']}")
    
    sys.exit(0)