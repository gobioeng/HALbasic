from PyQt5.QtCore import QThread, pyqtSignal
from unified_parser import UnifiedParser
from database import DatabaseManager
import os
import json


class FileProcessingWorker(QThread):
    """Background worker thread for processing large LINAC log files"""

    # Signals for communication with main thread
    progress_update = pyqtSignal(
        float, str, int, int, int, int
    )  # percentage, message, lines_processed, total_lines, bytes_processed, total_bytes
    status_update = pyqtSignal(str)  # status message
    finished = pyqtSignal(int, dict)  # records_count, parsing_stats
    error = pyqtSignal(str)  # error message

    def __init__(self, file_path: str, file_size: int, database: DatabaseManager):
        super().__init__()
        self.file_path = file_path
        self.file_size = file_size
        self.database = database
        self.parser = UnifiedParser()
        self._cancel_requested = False
        
        # Optimize chunk size based on file size
        if file_size > 100 * 1024 * 1024:  # > 100MB
            self.chunk_size = 5000  # Larger chunks for big files
        elif file_size > 10 * 1024 * 1024:  # > 10MB  
            self.chunk_size = 2000  # Medium chunks
        else:
            self.chunk_size = 1000  # Default chunk size

    def run(self):
        """Main worker thread execution"""
        try:
            self.status_update.emit("Initializing parser...")
            self.progress_update.emit(
                0, "Starting file processing...", 0, 0, 0, self.file_size
            )

            # Parse file with chunked processing
            df = self.parser.parse_linac_file(
                file_path=self.file_path,
                chunk_size=self.chunk_size,
                progress_callback=self._progress_callback,
                cancel_callback=self._cancel_callback,
            )

            if self._cancel_requested:
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

        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            self.error.emit(error_msg)

    def _progress_callback(self, percentage: float, message: str):
        """Handle progress updates from parser"""
        if self._cancel_requested:
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
        return self._cancel_requested

    def cancel_processing(self):
        """Request cancellation of processing"""
        self._cancel_requested = True
        self.status_update.emit("Cancelling processing...")

        # Terminate thread if it's still running
        if self.isRunning():
            self.terminate()
            self.wait(5000)  # Wait up to 5 seconds for clean termination


class AnalysisWorker(QThread):
    """Background worker for data analysis operations"""

    analysis_progress = pyqtSignal(int, str)  # percentage, message
    analysis_finished = pyqtSignal(dict)  # results dictionary
    analysis_error = pyqtSignal(str)  # error message

    def __init__(self, data_analyzer, dataframe):
        super().__init__()
        self.analyzer = data_analyzer
        self.df = dataframe
        self._cancel_requested = False

    def run(self):
        """Run comprehensive data analysis in background"""
        try:
            results = {}

            # Step 1: Calculate comprehensive statistics
            self.analysis_progress.emit(25, "Calculating comprehensive statistics...")
            if not self._cancel_requested:
                results["statistics"] = (
                    self.analyzer.calculate_comprehensive_statistics(self.df)
                )

            # Step 2: Detect anomalies
            self.analysis_progress.emit(50, "Detecting anomalies...")
            if not self._cancel_requested:
                results["anomalies"] = self.analyzer.detect_advanced_anomalies(self.df)

            # Step 3: Calculate trends
            self.analysis_progress.emit(75, "Analyzing trends...")
            if not self._cancel_requested:
                results["trends"] = self.analyzer.calculate_advanced_trends(self.df)

            # Step 4: Complete
            self.analysis_progress.emit(100, "Analysis completed!")
            if not self._cancel_requested:
                self.analysis_finished.emit(results)

        except Exception as e:
            self.analysis_error.emit(f"Analysis error: {str(e)}")

    def cancel_analysis(self):
        """Cancel the analysis operation"""
        self._cancel_requested = True


class DatabaseWorker(QThread):
    """Background worker for database operations"""

    db_progress = pyqtSignal(int, str)  # percentage, message
    db_finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, database: DatabaseManager, operation: str, **kwargs):
        super().__init__()
        self.database = database
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Execute database operation in background"""
        try:
            if self.operation == "clear_all":
                self.db_progress.emit(50, "Clearing database...")
                self.database.clear_all()
                self.db_progress.emit(100, "Database cleared successfully")
                self.db_finished.emit(True, "Database cleared successfully")

            elif self.operation == "vacuum":
                self.db_progress.emit(50, "Optimizing database...")
                self.database.vacuum_database()
                self.db_progress.emit(100, "Database optimized")
                self.db_finished.emit(True, "Database optimized successfully")

            else:
                self.db_finished.emit(False, f"Unknown operation: {self.operation}")

        except Exception as e:
            self.db_finished.emit(False, f"Database operation failed: {str(e)}")