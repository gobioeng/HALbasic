"""
Simplified Worker Thread for HALog
Optimized for essential background processing
"""

from PyQt5.QtCore import QThread, pyqtSignal
from unified_parser import UnifiedParser
from database import DatabaseManager
import os


class FileProcessingWorker(QThread):
    """Simplified background worker for file processing"""

    progress_update = pyqtSignal(int, str)  # percentage, message
    finished = pyqtSignal(int, dict)  # records_count, stats
    error = pyqtSignal(str)  # error message

    def __init__(self, file_path: str, file_size: int, database: DatabaseManager):
        super().__init__()
        self.file_path = file_path
        self.file_size = file_size
        self.database = database
        self.parser = UnifiedParser()
        self._cancelled = False

    def run(self):
        """Main processing logic"""
        try:
            self.progress_update.emit(10, "Reading file...")

            # Parse file
            df = self.parser.parse_linac_file(
                self.file_path,
                progress_callback=self._update_progress,
                cancel_callback=lambda: self._cancelled
            )

            if self._cancelled:
                return

            self.progress_update.emit(80, "Saving to database...")

            # Insert to database
            records_inserted = self.database.insert_data_batch(df)

            # Save metadata
            filename = os.path.basename(self.file_path)
            self.database.insert_file_metadata(filename, self.file_size, records_inserted)

            self.progress_update.emit(100, "Complete!")
            self.finished.emit(records_inserted, self.parser.get_parsing_stats())

        except Exception as e:
            self.error.emit(str(e))

    def _update_progress(self, percentage: float):
        """Update progress from parser"""
        if not self._cancelled:
            # Scale to 10-80% range (10% for reading, 80% for parsing, 20% for saving)
            scaled_progress = 10 + (percentage * 0.7)
            self.progress_update.emit(int(scaled_progress), f"Processing... {percentage:.0f}%")

    def cancel_processing(self):
        """Cancel processing"""
        self._cancelled = True
        self.terminate()