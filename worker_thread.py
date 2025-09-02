from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from unified_parser import UnifiedParser
from database import DatabaseManager
import os
import json
import time
import logging


class FileProcessingWorker(QThread):
    """
    Professional background worker thread for processing large LINAC log files
    Includes fail-safe mechanisms and proper cleanup procedures
    """

    # Signals for communication with main thread
    progress_update = pyqtSignal(
        float, str, int, int, int, int
    )  # percentage, message, lines_processed, total_lines, bytes_processed, total_bytes
    status_update = pyqtSignal(str)  # status message
    finished = pyqtSignal(int, dict)  # records_count, parsing_stats
    error = pyqtSignal(str)  # error message
    cleanup_completed = pyqtSignal()  # cleanup finished signal

    def __init__(self, file_path: str, file_size: int, database: DatabaseManager):
        super().__init__()
        self.file_path = file_path
        self.file_size = file_size
        self.database = database
        self.parser = UnifiedParser()
        self._cancel_requested = False
        self._cleanup_completed = False
        self.mutex = QMutex()
        self.logger = logging.getLogger(f"{__name__}.FileProcessingWorker")
        
        # Optimize chunk size based on file size
        if file_size > 100 * 1024 * 1024:  # > 100MB
            self.chunk_size = 5000  # Larger chunks for big files
        elif file_size > 10 * 1024 * 1024:  # > 10MB  
            self.chunk_size = 2000  # Medium chunks
        else:
            self.chunk_size = 1000  # Default chunk size

    def run(self):
        """Main worker thread execution with enhanced error handling and cleanup"""
        try:
            self.logger.info(f"Starting file processing: {self.file_path}")
            self.status_update.emit("Initializing parser...")
            self.progress_update.emit(
                0, "Starting file processing...", 0, 0, 0, self.file_size
            )

            # Check for cancellation before starting
            if self._is_cancelled():
                return

            # Parse file with chunked processing
            df = self.parser.parse_linac_file(
                file_path=self.file_path,
                chunk_size=self.chunk_size,
                progress_callback=self._progress_callback,
                cancel_callback=self._cancel_callback,
            )

            if self._is_cancelled():
                self.status_update.emit("Processing cancelled by user")
                return

            if df.empty:
                self.finished.emit(0, self.parser.get_parsing_stats())
                return

            # Update progress for database insertion
            self.status_update.emit("Saving data to database...")
            self.progress_update.emit(
                90,
                "Inserting records into database...",
                self.parser.parsing_stats["lines_processed"],
                self.parser.parsing_stats["lines_processed"],
                self.file_size,
                self.file_size,
            )

            # Check for cancellation before database operations
            if self._is_cancelled():
                return

            # Insert data into database in optimized batches
            batch_size = min(1000, max(100, len(df) // 10))  # Dynamic batch size
            records_inserted = self.database.insert_data_batch(df, batch_size=batch_size)

            # Insert file metadata
            filename = os.path.basename(self.file_path)
            parsing_stats_json = json.dumps(self.parser.get_parsing_stats())
            self.database.insert_file_metadata(
                filename=filename,
                file_size=self.file_size,
                records_imported=records_inserted,
                parsing_stats=parsing_stats_json,
            )

            # Final progress update
            if not self._is_cancelled():
                self.progress_update.emit(
                    100,
                    "Processing completed successfully!",
                    self.parser.parsing_stats["lines_processed"],
                    self.parser.parsing_stats["lines_processed"],
                    self.file_size,
                    self.file_size,
                )

                # Emit completion signal
                self.finished.emit(records_inserted, self.parser.get_parsing_stats())
                self.logger.info(f"File processing completed successfully: {records_inserted} records")

        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            self.logger.error(error_msg)
            self.error.emit(error_msg)
        finally:
            self._perform_cleanup()

    def _is_cancelled(self) -> bool:
        """Thread-safe check for cancellation"""
        with QMutexLocker(self.mutex):
            return self._cancel_requested

    def _perform_cleanup(self):
        """Perform thread cleanup operations"""
        try:
            with QMutexLocker(self.mutex):
                if self._cleanup_completed:
                    return
                self._cleanup_completed = True
            
            self.logger.info("Performing thread cleanup")
            
            # Close any open file handles in parser
            if hasattr(self.parser, 'cleanup'):
                self.parser.cleanup()
            
            # Clear large data structures
            if hasattr(self, 'parser'):
                self.parser = None
            
            self.cleanup_completed.emit()
            self.logger.info("Thread cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def cancel_processing(self):
        """Request cancellation of processing with improved safety"""
        with QMutexLocker(self.mutex):
            self._cancel_requested = True
        
        self.status_update.emit("Cancelling processing...")
        self.logger.info("Processing cancellation requested")
        
        # Don't use terminate() - let the thread finish gracefully
        # The run() method will check _cancel_requested and exit cleanly

    def _progress_callback(self, percentage: float, message: str):
        """Handle progress updates from parser"""
        if self._is_cancelled():
            return

        # Calculate estimated lines and bytes processed
        lines_processed = self.parser.parsing_stats.get("lines_processed", 0)
        estimated_total_lines = max(lines_processed, int(self.file_size / 100))
        bytes_processed = int((percentage / 100.0) * self.file_size)

        # Ensure percentage is properly bounded integer
        progress_value = max(0.0, min(100.0, float(percentage)))

        self.progress_update.emit(
            progress_value,
            message,
            lines_processed,
            estimated_total_lines,
            bytes_processed,
            self.file_size,
        )

        self.status_update.emit(message)

    def _cancel_callback(self) -> bool:
        """Check if cancellation was requested"""
        return self._is_cancelled()

    def cancel_processing(self):
        """Request cancellation of processing with improved safety"""
        with QMutexLocker(self.mutex):
            self._cancel_requested = True
        
        self.status_update.emit("Cancelling processing...")
        self.logger.info("Processing cancellation requested")
        
        # Don't use terminate() - let the thread finish gracefully
        # The run() method will check _cancel_requested and exit cleanly


class AnalysisWorker(QThread):
    """
    Professional background worker for data analysis operations
    Includes fail-safe mechanisms and proper cleanup procedures
    """

    analysis_progress = pyqtSignal(int, str)  # percentage, message
    analysis_finished = pyqtSignal(dict)  # results dictionary
    analysis_error = pyqtSignal(str)  # error message
    cleanup_completed = pyqtSignal()  # cleanup finished signal

    def __init__(self, data_analyzer, dataframe):
        super().__init__()
        self.analyzer = data_analyzer
        self.df = dataframe
        self._cancel_requested = False
        self._cleanup_completed = False
        self.mutex = QMutex()
        self.logger = logging.getLogger(f"{__name__}.AnalysisWorker")

    def run(self):
        """Run comprehensive data analysis in background with enhanced error handling"""
        try:
            self.logger.info("Starting data analysis")
            results = {}

            # Step 1: Calculate comprehensive statistics
            if not self._is_cancelled():
                self.analysis_progress.emit(25, "Calculating comprehensive statistics...")
                results["statistics"] = (
                    self.analyzer.calculate_comprehensive_statistics(self.df)
                )

            # Step 2: Detect anomalies
            if not self._is_cancelled():
                self.analysis_progress.emit(50, "Detecting anomalies...")
                results["anomalies"] = self.analyzer.detect_advanced_anomalies(self.df)

            # Step 3: Calculate trends
            if not self._is_cancelled():
                self.analysis_progress.emit(75, "Analyzing trends...")
                results["trends"] = self.analyzer.calculate_advanced_trends(self.df)

            # Step 4: Complete
            if not self._is_cancelled():
                self.analysis_progress.emit(100, "Analysis completed!")
                self.analysis_finished.emit(results)
                self.logger.info("Data analysis completed successfully")

        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.logger.error(error_msg)
            self.analysis_error.emit(error_msg)
        finally:
            self._perform_cleanup()

    def _is_cancelled(self) -> bool:
        """Thread-safe check for cancellation"""
        with QMutexLocker(self.mutex):
            return self._cancel_requested

    def _perform_cleanup(self):
        """Perform thread cleanup operations"""
        try:
            with QMutexLocker(self.mutex):
                if self._cleanup_completed:
                    return
                self._cleanup_completed = True
            
            self.logger.info("Performing analysis thread cleanup")
            
            # Clear references to large data structures
            if hasattr(self, 'df'):
                self.df = None
            if hasattr(self, 'analyzer'):
                self.analyzer = None
            
            self.cleanup_completed.emit()
            self.logger.info("Analysis thread cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during analysis cleanup: {e}")

    def cancel_analysis(self):
        """Cancel the analysis operation safely"""
        with QMutexLocker(self.mutex):
            self._cancel_requested = True
        
        self.logger.info("Analysis cancellation requested")


class DatabaseWorker(QThread):
    """
    Professional background worker for database operations
    Includes fail-safe mechanisms and proper cleanup procedures
    """

    db_progress = pyqtSignal(int, str)  # percentage, message
    db_finished = pyqtSignal(bool, str)  # success, message
    cleanup_completed = pyqtSignal()  # cleanup finished signal

    def __init__(self, database: DatabaseManager, operation: str, **kwargs):
        super().__init__()
        self.database = database
        self.operation = operation
        self.kwargs = kwargs
        self._cancel_requested = False
        self._cleanup_completed = False
        self.mutex = QMutex()
        self.logger = logging.getLogger(f"{__name__}.DatabaseWorker")

    def run(self):
        """Execute database operation in background with enhanced error handling"""
        try:
            self.logger.info(f"Starting database operation: {self.operation}")
            
            if self._is_cancelled():
                return

            if self.operation == "clear_all":
                self.db_progress.emit(50, "Clearing database...")
                self.database.clear_all()
                self.db_progress.emit(100, "Database cleared successfully")
                if not self._is_cancelled():
                    self.db_finished.emit(True, "Database cleared successfully")

            elif self.operation == "vacuum":
                self.db_progress.emit(50, "Optimizing database...")
                self.database.vacuum_database()
                self.db_progress.emit(100, "Database optimized")
                if not self._is_cancelled():
                    self.db_finished.emit(True, "Database optimized successfully")

            else:
                if not self._is_cancelled():
                    self.db_finished.emit(False, f"Unknown operation: {self.operation}")

            self.logger.info(f"Database operation completed: {self.operation}")

        except Exception as e:
            error_msg = f"Database operation failed: {str(e)}"
            self.logger.error(error_msg)
            self.db_finished.emit(False, error_msg)
        finally:
            self._perform_cleanup()

    def _is_cancelled(self) -> bool:
        """Thread-safe check for cancellation"""
        with QMutexLocker(self.mutex):
            return self._cancel_requested

    def _perform_cleanup(self):
        """Perform thread cleanup operations"""
        try:
            with QMutexLocker(self.mutex):
                if self._cleanup_completed:
                    return
                self._cleanup_completed = True
            
            self.logger.info("Performing database thread cleanup")
            
            # Clear references
            if hasattr(self, 'database'):
                self.database = None
            
            self.cleanup_completed.emit()
            self.logger.info("Database thread cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during database cleanup: {e}")

    def cancel_operation(self):
        """Cancel the database operation safely"""
        with QMutexLocker(self.mutex):
            self._cancel_requested = True
        
        self.logger.info("Database operation cancellation requested")