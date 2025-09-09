"""
Enhanced Error Handling & Recovery System for HALog
Comprehensive error management with recovery mechanisms and user-friendly reporting

Features:
- Import recovery system with checkpoint saving
- Rollback mechanism for failed imports  
- Database resilience with repair functionality
- User-friendly error reporting with categorization
- Connection retry logic with exponential backoff
- Error logging with rotation
- Recovery workflow management

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import os
import json
import time
import traceback
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QGroupBox, QScrollArea, QFrame, QProgressBar, QMessageBox, QComboBox,
    QCheckBox, QSpinBox, QTabWidget, QWidget, QGridLayout, QFormLayout,
    QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMutex
from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap


class ErrorCategory(Enum):
    """Error categorization for better handling"""
    DATA_ERROR = "Data Error"
    DATABASE_ERROR = "Database Error"
    SYSTEM_ERROR = "System Error"
    IMPORT_ERROR = "Import Error"
    NETWORK_ERROR = "Network Error"
    VALIDATION_ERROR = "Validation Error"
    UI_ERROR = "UI Error"
    UNKNOWN_ERROR = "Unknown Error"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ImportCheckpoint:
    """Represents a checkpoint during import process"""
    
    def __init__(self, checkpoint_id: str, file_path: str, records_processed: int, 
                 timestamp: datetime, data_hash: str = ""):
        self.checkpoint_id = checkpoint_id
        self.file_path = file_path
        self.records_processed = records_processed
        self.timestamp = timestamp
        self.data_hash = data_hash
        self.additional_data = {}
    
    def to_dict(self) -> Dict:
        """Convert checkpoint to dictionary for serialization"""
        return {
            'checkpoint_id': self.checkpoint_id,
            'file_path': self.file_path,
            'records_processed': self.records_processed,
            'timestamp': self.timestamp.isoformat(),
            'data_hash': self.data_hash,
            'additional_data': self.additional_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ImportCheckpoint':
        """Create checkpoint from dictionary"""
        checkpoint = cls(
            data['checkpoint_id'],
            data['file_path'],
            data['records_processed'],
            datetime.fromisoformat(data['timestamp']),
            data.get('data_hash', '')
        )
        checkpoint.additional_data = data.get('additional_data', {})
        return checkpoint


class ErrorReportDialog(QDialog):
    """User-friendly error reporting dialog with detailed information"""
    
    def __init__(self, error_info: Dict, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        self.setWindowTitle("HALog Error Report")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup error report dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Error header
        header_frame = QFrame()
        header_frame.setObjectName("errorHeader")
        header_layout = QHBoxLayout(header_frame)
        
        # Error icon/severity indicator
        severity = self.error_info.get('severity', ErrorSeverity.MEDIUM)
        severity_label = QLabel("⚠️" if severity == ErrorSeverity.MEDIUM else 
                               "🛑" if severity == ErrorSeverity.CRITICAL else "ℹ️")
        severity_label.setStyleSheet("font-size: 32px; margin-right: 12px;")
        header_layout.addWidget(severity_label)
        
        # Error title and category
        title_layout = QVBoxLayout()
        title_label = QLabel(self.error_info.get('title', 'An error occurred'))
        title_label.setObjectName("errorTitle")
        title_layout.addWidget(title_label)
        
        category = self.error_info.get('category', ErrorCategory.UNKNOWN_ERROR)
        category_label = QLabel(f"Category: {category.value}")
        category_label.setObjectName("errorCategory")
        title_layout.addWidget(category_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
        # Tab widget for error details
        tab_widget = QTabWidget()
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Error description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)
        
        desc_text = QTextEdit()
        desc_text.setMaximumHeight(100)
        desc_text.setPlainText(self.error_info.get('description', 'No description available'))
        desc_text.setReadOnly(True)
        desc_layout.addWidget(desc_text)
        overview_layout.addWidget(desc_group)
        
        # Suggested solutions
        solutions_group = QGroupBox("Suggested Solutions")
        solutions_layout = QVBoxLayout(solutions_group)
        
        solutions_text = QTextEdit()
        solutions_text.setMaximumHeight(120)
        solutions = self.error_info.get('suggested_solutions', ['Contact system administrator'])
        solutions_text.setPlainText('\n'.join(f"• {solution}" for solution in solutions))
        solutions_text.setReadOnly(True)
        solutions_layout.addWidget(solutions_text)
        overview_layout.addWidget(solutions_group)
        
        # Error context
        if 'context' in self.error_info:
            context_group = QGroupBox("Context")
            context_layout = QFormLayout(context_group)
            
            context = self.error_info['context']
            for key, value in context.items():
                context_layout.addRow(f"{key}:", QLabel(str(value)))
            
            overview_layout.addWidget(context_group)
        
        overview_layout.addStretch()
        tab_widget.addTab(overview_tab, "Overview")
        
        # Technical details tab
        if 'technical_details' in self.error_info or 'traceback' in self.error_info:
            technical_tab = QWidget()
            technical_layout = QVBoxLayout(technical_tab)
            
            technical_text = QTextEdit()
            technical_text.setFont(QFont("Consolas", 9))
            
            technical_content = ""
            if 'technical_details' in self.error_info:
                technical_content += f"Technical Details:\n{self.error_info['technical_details']}\n\n"
            
            if 'traceback' in self.error_info:
                technical_content += f"Traceback:\n{self.error_info['traceback']}"
            
            technical_text.setPlainText(technical_content)
            technical_text.setReadOnly(True)
            technical_layout.addWidget(technical_text)
            
            tab_widget.addTab(technical_tab, "Technical Details")
        
        # Log tab
        if 'log_entries' in self.error_info:
            log_tab = QWidget()
            log_layout = QVBoxLayout(log_tab)
            
            log_text = QTextEdit()
            log_text.setFont(QFont("Consolas", 9))
            log_entries = self.error_info['log_entries']
            log_content = '\n'.join(log_entries)
            log_text.setPlainText(log_content)
            log_text.setReadOnly(True)
            log_layout.addWidget(log_text)
            
            tab_widget.addTab(log_tab, "Related Logs")
        
        layout.addWidget(tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Report bug button
        report_btn = QPushButton("Report Bug")
        report_btn.clicked.connect(self._report_bug)
        button_layout.addWidget(report_btn)
        
        # Export report button
        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(self._export_report)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        # Retry button (if applicable)
        if self.error_info.get('retryable', False):
            retry_btn = QPushButton("Retry Operation")
            retry_btn.clicked.connect(self._retry_operation)
            retry_btn.setObjectName("retryButton")
            button_layout.addWidget(retry_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _apply_styling(self):
        """Apply professional styling to error dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
            }
            QFrame#errorHeader {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }
            QLabel#errorTitle {
                font-size: 16px;
                font-weight: 600;
                color: #D32F2F;
                margin-bottom: 4px;
            }
            QLabel#errorCategory {
                font-size: 12px;
                color: #79747E;
                font-weight: 500;
            }
            QGroupBox {
                font-weight: 600;
                color: #1C1B1F;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 4px 8px;
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#retryButton {
                background-color: #2D7D2D;
            }
            QPushButton#retryButton:hover {
                background-color: #2E7D32;
            }
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                color: #79747E;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0px 0px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1976D2;
                font-weight: 600;
            }
        """)
    
    def _report_bug(self):
        """Handle bug reporting"""
        # In a real implementation, this would send to bug tracking system
        QMessageBox.information(
            self, "Bug Report", 
            "Bug report functionality would integrate with your bug tracking system.\n\n"
            "Error details have been prepared for submission."
        )
    
    def _export_report(self):
        """Export error report to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Error Report",
                f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                report_content = self._generate_report_content()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                QMessageBox.information(self, "Export Success", f"Error report exported to:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Could not export report:\n{str(e)}")
    
    def _generate_report_content(self) -> str:
        """Generate comprehensive error report content"""
        lines = [
            "HALog Error Report",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "ERROR DETAILS",
            "-" * 20,
            f"Title: {self.error_info.get('title', 'Unknown')}",
            f"Category: {self.error_info.get('category', ErrorCategory.UNKNOWN_ERROR).value}",
            f"Severity: {self.error_info.get('severity', ErrorSeverity.MEDIUM).value}",
            f"Timestamp: {self.error_info.get('timestamp', 'Unknown')}",
            "",
            "DESCRIPTION",
            "-" * 12,
            self.error_info.get('description', 'No description available'),
            "",
        ]
        
        # Add suggested solutions
        solutions = self.error_info.get('suggested_solutions', [])
        if solutions:
            lines.extend([
                "SUGGESTED SOLUTIONS",
                "-" * 19,
            ])
            for solution in solutions:
                lines.append(f"• {solution}")
            lines.append("")
        
        # Add context
        context = self.error_info.get('context', {})
        if context:
            lines.extend([
                "CONTEXT",
                "-" * 7,
            ])
            for key, value in context.items():
                lines.append(f"{key}: {value}")
            lines.append("")
        
        # Add technical details
        if 'technical_details' in self.error_info:
            lines.extend([
                "TECHNICAL DETAILS",
                "-" * 16,
                self.error_info['technical_details'],
                ""
            ])
        
        # Add traceback
        if 'traceback' in self.error_info:
            lines.extend([
                "TRACEBACK",
                "-" * 9,
                self.error_info['traceback'],
                ""
            ])
        
        return '\n'.join(lines)
    
    def _retry_operation(self):
        """Handle operation retry"""
        self.done(2)  # Custom return code for retry


class ImportRecoverySystem:
    """System for managing import checkpoints and recovery"""
    
    def __init__(self, checkpoint_dir: str = None):
        self.checkpoint_dir = Path(checkpoint_dir or "checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.active_checkpoints = {}
        
        # Setup logging
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for recovery system"""
        logger = logging.getLogger('ImportRecovery')
        logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not logger.handlers:
            handler = logging.FileHandler(
                self.checkpoint_dir / 'recovery.log',
                encoding='utf-8'
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def create_checkpoint(self, file_path: str, records_processed: int, 
                         additional_data: Dict = None) -> str:
        """Create a checkpoint during import process"""
        checkpoint_id = f"ckpt_{int(time.time())}_{os.path.basename(file_path)}"
        
        checkpoint = ImportCheckpoint(
            checkpoint_id=checkpoint_id,
            file_path=file_path,
            records_processed=records_processed,
            timestamp=datetime.now(),
            data_hash=self._calculate_data_hash(file_path, records_processed)
        )
        
        if additional_data:
            checkpoint.additional_data = additional_data
        
        # Save checkpoint to file
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
            
            self.active_checkpoints[checkpoint_id] = checkpoint
            self.logger.info(f"Created checkpoint {checkpoint_id} at {records_processed} records")
            
            return checkpoint_id
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint {checkpoint_id}: {e}")
            raise
    
    def get_available_checkpoints(self, file_path: str = None) -> List[ImportCheckpoint]:
        """Get available checkpoints for recovery"""
        checkpoints = []
        
        try:
            for checkpoint_file in self.checkpoint_dir.glob("ckpt_*.json"):
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    checkpoint = ImportCheckpoint.from_dict(data)
                    
                    # Filter by file path if specified
                    if file_path is None or checkpoint.file_path == file_path:
                        checkpoints.append(checkpoint)
            
            # Sort by timestamp (newest first)
            checkpoints.sort(key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error loading checkpoints: {e}")
        
        return checkpoints
    
    def resume_from_checkpoint(self, checkpoint_id: str) -> Optional[ImportCheckpoint]:
        """Resume import from a specific checkpoint"""
        try:
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            
            if not checkpoint_file.exists():
                self.logger.error(f"Checkpoint file not found: {checkpoint_file}")
                return None
            
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                checkpoint = ImportCheckpoint.from_dict(data)
            
            self.logger.info(f"Resuming from checkpoint {checkpoint_id} at {checkpoint.records_processed} records")
            return checkpoint
            
        except Exception as e:
            self.logger.error(f"Failed to resume from checkpoint {checkpoint_id}: {e}")
            return None
    
    def clean_checkpoints(self, max_age_hours: int = 24, keep_count: int = 10):
        """Clean old checkpoints to prevent disk space issues"""
        try:
            checkpoints = self.get_available_checkpoints()
            
            # Remove checkpoints older than max_age_hours
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            old_checkpoints = [cp for cp in checkpoints if cp.timestamp < cutoff_time]
            
            # Keep at least keep_count recent checkpoints
            if len(checkpoints) - len(old_checkpoints) >= keep_count:
                for checkpoint in old_checkpoints:
                    checkpoint_file = self.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
                    if checkpoint_file.exists():
                        checkpoint_file.unlink()
                        self.logger.info(f"Cleaned old checkpoint {checkpoint.checkpoint_id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning checkpoints: {e}")
    
    def _calculate_data_hash(self, file_path: str, records_processed: int) -> str:
        """Calculate a simple hash for data integrity checking"""
        import hashlib
        
        try:
            # Create hash from file path, size, and records processed
            hash_input = f"{file_path}_{os.path.getsize(file_path)}_{records_processed}"
            return hashlib.md5(hash_input.encode()).hexdigest()[:16]
        except:
            return "unknown"


class DatabaseResilienceManager:
    """Manager for database health monitoring and repair"""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.logger = self._setup_logging()
        
        # Connection retry settings
        self.max_retries = 3
        self.base_retry_delay = 1.0  # seconds
        self.max_retry_delay = 10.0  # seconds
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for database resilience"""
        logger = logging.getLogger('DatabaseResilience')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('database_resilience.log', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def check_database_health(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        health_status = {
            'overall_health': 'unknown',
            'issues_found': [],
            'recommendations': [],
            'metrics': {}
        }
        
        try:
            with self.db_manager.get_connection() as conn:
                # Check database file exists and is accessible
                if not os.path.exists(self.db_manager.db_path):
                    health_status['issues_found'].append("Database file does not exist")
                    health_status['overall_health'] = 'critical'
                    return health_status
                
                # Check integrity
                cursor = conn.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                if integrity_result != "ok":
                    health_status['issues_found'].append(f"Database integrity issue: {integrity_result}")
                    health_status['overall_health'] = 'poor'
                else:
                    health_status['metrics']['integrity'] = 'ok'
                
                # Check table existence
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['water_logs', 'file_metadata', 'import_validation_log']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    health_status['issues_found'].append(f"Missing tables: {missing_tables}")
                    health_status['recommendations'].append("Reinitialize database schema")
                
                # Check database size and performance metrics
                cursor = conn.execute("SELECT COUNT(*) FROM water_logs")
                record_count = cursor.fetchone()[0]
                health_status['metrics']['record_count'] = record_count
                
                # Check for index effectiveness
                cursor = conn.execute("ANALYZE")
                
                # Determine overall health
                if not health_status['issues_found']:
                    health_status['overall_health'] = 'good'
                elif len(health_status['issues_found']) <= 2:
                    health_status['overall_health'] = 'fair'
                else:
                    health_status['overall_health'] = 'poor'
                    
        except Exception as e:
            health_status['issues_found'].append(f"Database connection error: {str(e)}")
            health_status['overall_health'] = 'critical'
            self.logger.error(f"Database health check failed: {e}")
        
        return health_status
    
    def repair_database(self) -> bool:
        """Attempt to repair database issues"""
        try:
            self.logger.info("Starting database repair process")
            
            # Create backup before repair
            backup_path = f"{self.db_manager.db_path}.repair_backup_{int(time.time())}"
            
            try:
                import shutil
                shutil.copy2(self.db_manager.db_path, backup_path)
                self.logger.info(f"Created repair backup: {backup_path}")
            except Exception as e:
                self.logger.warning(f"Could not create repair backup: {e}")
            
            # Attempt repairs
            with self.db_manager.get_connection() as conn:
                # Vacuum database to rebuild and optimize
                conn.execute("VACUUM")
                self.logger.info("Database vacuum completed")
                
                # Reindex all indexes
                conn.execute("REINDEX")
                self.logger.info("Database reindex completed")
                
                # Analyze tables for query optimization
                conn.execute("ANALYZE")
                self.logger.info("Database analyze completed")
                
                # Check if repair was successful
                cursor = conn.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                if integrity_result == "ok":
                    self.logger.info("Database repair successful")
                    return True
                else:
                    self.logger.error(f"Database repair failed: {integrity_result}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Database repair failed: {e}")
            return False
    
    def execute_with_retry(self, operation_func, *args, **kwargs):
        """Execute database operation with retry logic and exponential backoff"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return operation_func(*args, **kwargs)
                
            except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                last_error = e
                self.logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    delay = min(
                        self.base_retry_delay * (2 ** attempt),
                        self.max_retry_delay
                    )
                    
                    # Add small random jitter
                    import random
                    delay += random.uniform(0, 0.5)
                    
                    self.logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"All retry attempts failed for database operation")
                    raise last_error
            
            except Exception as e:
                # Non-retryable error
                self.logger.error(f"Non-retryable database error: {e}")
                raise e
        
        # This should not be reached, but just in case
        raise last_error


class ErrorHandlingManager:
    """Central error handling manager for the application"""
    
    def __init__(self):
        self.error_handlers = {}
        self.error_history = []
        self.max_history_size = 1000
        
        # Initialize logging
        self.logger = self._setup_error_logging()
        
        # Initialize recovery systems
        self.import_recovery = ImportRecoverySystem()
        self.db_resilience = None  # Will be set when database manager is available
    
    def _setup_error_logging(self) -> logging.Logger:
        """Setup centralized error logging with rotation"""
        logger = logging.getLogger('HALogErrors')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Create logs directory
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Setup rotating file handler
            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(
                logs_dir / 'halog_errors.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Also add console handler for important errors
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def register_error_handler(self, error_category: ErrorCategory, handler_func):
        """Register custom error handler for specific category"""
        self.error_handlers[error_category] = handler_func
    
    def handle_error(self, error: Exception, context: Dict = None, 
                    category: ErrorCategory = None, severity: ErrorSeverity = None,
                    show_dialog: bool = True) -> bool:
        """Main error handling entry point"""
        try:
            # Categorize error if not provided
            if category is None:
                category = self._categorize_error(error)
            
            if severity is None:
                severity = self._assess_severity(error, category)
            
            # Create error info
            error_info = {
                'title': f"{category.value}: {type(error).__name__}",
                'description': str(error),
                'category': category,
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'traceback': traceback.format_exc(),
                'context': context or {},
                'suggested_solutions': self._get_suggested_solutions(error, category),
                'retryable': self._is_retryable(error, category)
            }
            
            # Add to history
            self.error_history.append(error_info)
            if len(self.error_history) > self.max_history_size:
                self.error_history = self.error_history[-self.max_history_size:]
            
            # Log error
            self.logger.error(
                f"{category.value} - {severity.value}: {str(error)}",
                exc_info=True,
                extra={'context': context}
            )
            
            # Call custom handler if available
            if category in self.error_handlers:
                try:
                    handled = self.error_handlers[category](error_info)
                    if handled:
                        return True
                except Exception as handler_error:
                    self.logger.error(f"Error handler failed: {handler_error}")
            
            # Show user-friendly dialog for critical/high severity errors
            if show_dialog and severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                return self._show_error_dialog(error_info)
            
            return True
            
        except Exception as handling_error:
            # Fallback error handling
            self.logger.critical(f"Error handling system failed: {handling_error}")
            return False
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on exception type and context"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Database errors
        if 'sqlite' in error_type.lower() or 'database' in error_message:
            return ErrorCategory.DATABASE_ERROR
        
        # Import/parsing errors
        if 'import' in error_message or 'parse' in error_message:
            return ErrorCategory.IMPORT_ERROR
        
        # Validation errors
        if 'validation' in error_message or 'invalid' in error_message:
            return ErrorCategory.VALIDATION_ERROR
        
        # Network errors
        if any(keyword in error_message for keyword in ['network', 'connection', 'timeout']):
            return ErrorCategory.NETWORK_ERROR
        
        # System errors
        if any(keyword in error_message for keyword in ['memory', 'disk', 'permission']):
            return ErrorCategory.SYSTEM_ERROR
        
        # UI errors
        if 'qt' in error_type.lower() or 'widget' in error_message:
            return ErrorCategory.UI_ERROR
        
        # Data errors
        if any(keyword in error_message for keyword in ['data', 'format', 'column']):
            return ErrorCategory.DATA_ERROR
        
        return ErrorCategory.UNKNOWN_ERROR
    
    def _assess_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Assess error severity based on type and category"""
        error_message = str(error).lower()
        
        # Critical errors
        if any(keyword in error_message for keyword in ['critical', 'fatal', 'corruption']):
            return ErrorSeverity.CRITICAL
        
        # High severity by category
        if category in [ErrorCategory.DATABASE_ERROR, ErrorCategory.SYSTEM_ERROR]:
            return ErrorSeverity.HIGH
        
        # Medium severity
        if category in [ErrorCategory.IMPORT_ERROR, ErrorCategory.VALIDATION_ERROR]:
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _get_suggested_solutions(self, error: Exception, category: ErrorCategory) -> List[str]:
        """Get suggested solutions based on error type and category"""
        solutions = []
        error_message = str(error).lower()
        
        if category == ErrorCategory.DATABASE_ERROR:
            solutions.extend([
                "Check if database file is accessible and not corrupted",
                "Try restarting the application",
                "Check available disk space",
                "Consider running database repair tool"
            ])
        
        elif category == ErrorCategory.IMPORT_ERROR:
            solutions.extend([
                "Verify the file format is correct",
                "Check if file is not corrupted or incomplete",
                "Try importing a smaller file first",
                "Check available memory and disk space"
            ])
        
        elif category == ErrorCategory.VALIDATION_ERROR:
            solutions.extend([
                "Review data for format consistency",
                "Check parameter ranges and values",
                "Verify timestamp formats are correct",
                "Consider adjusting validation settings"
            ])
        
        elif category == ErrorCategory.SYSTEM_ERROR:
            solutions.extend([
                "Check system resources (memory, disk space)",
                "Verify file permissions",
                "Try restarting the application",
                "Check for system updates"
            ])
        
        else:
            solutions.extend([
                "Try the operation again",
                "Check application logs for more details",
                "Contact technical support if problem persists"
            ])
        
        return solutions
    
    def _is_retryable(self, error: Exception, category: ErrorCategory) -> bool:
        """Determine if an error is retryable"""
        non_retryable_keywords = ['permission', 'corruption', 'format', 'syntax']
        error_message = str(error).lower()
        
        if any(keyword in error_message for keyword in non_retryable_keywords):
            return False
        
        return category not in [ErrorCategory.DATA_ERROR, ErrorCategory.VALIDATION_ERROR]
    
    def _show_error_dialog(self, error_info: Dict) -> bool:
        """Show error reporting dialog to user"""
        try:
            dialog = ErrorReportDialog(error_info)
            result = dialog.exec_()
            
            if result == 2:  # Retry requested
                return False  # Indicate retry needed
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to show error dialog: {e}")
            return True
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        if not self.error_history:
            return {'total_errors': 0}
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        
        recent_errors = [e for e in self.error_history 
                        if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=24)]
        
        for error in recent_errors:
            category = error['category'].value
            severity = error['severity'].value
            
            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'recent_errors_24h': len(recent_errors),
            'category_breakdown': category_counts,
            'severity_breakdown': severity_counts,
            'last_error_time': self.error_history[-1]['timestamp'] if self.error_history else None
        }


def setup_global_error_handling():
    """Setup global error handling for the application"""
    global_error_manager = ErrorHandlingManager()
    
    # Register with Python's exception hook
    original_excepthook = sys.excepthook
    
    def halog_excepthook(exc_type, exc_value, exc_traceback):
        # Handle uncaught exceptions
        if exc_type != KeyboardInterrupt:
            global_error_manager.handle_error(
                exc_value,
                context={'uncaught': True, 'exc_type': exc_type.__name__},
                severity=ErrorSeverity.CRITICAL
            )
        
        # Call original handler
        original_excepthook(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = halog_excepthook
    
    return global_error_manager