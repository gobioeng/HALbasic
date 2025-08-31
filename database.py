"""
Enhanced Database Manager - Gobioeng HALog
Provides optimized database operations for LINAC water system data
"""

import sqlite3
import pandas as pd
from typing import Optional, Dict
import os
from functools import reduce
import time
import traceback
from contextlib import contextmanager


class DatabaseManager:
    """Enhanced database manager with batch operations and optimized queries"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_pool = {}
        self.prepared_statements = {}
        self.init_db()

    def init_db(self):
        """Initialize database with enhanced schema"""
        with self.get_connection() as conn:
            # Enable performance optimizations
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=30000000")

            # Create tables if they don't exist
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS water_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime TEXT NOT NULL,
                    serial_number TEXT NOT NULL,
                    parameter_type TEXT NOT NULL,
                    statistic_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    count INTEGER,
                    unit TEXT,
                    description TEXT,
                    data_quality TEXT,
                    raw_parameter TEXT,
                    line_number INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create optimized indices
            self._create_indices(conn)

            # Create metadata table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_size INTEGER,
                    records_imported INTEGER,
                    import_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parsing_stats TEXT
                )
            """
            )

            conn.commit()

    def _create_indices(self, conn):
        """Create optimized database indices"""
        # Check if indices already exist to avoid redundant operations
        indices = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        ).fetchall()
        existing_indices = [idx[0] for idx in indices]

        index_definitions = [
            (
                "idx_datetime",
                "CREATE INDEX IF NOT EXISTS idx_datetime ON water_logs(datetime)",
            ),
            (
                "idx_parameter_type",
                "CREATE INDEX IF NOT EXISTS idx_parameter_type ON water_logs(parameter_type)",
            ),
            (
                "idx_serial_parameter",
                "CREATE INDEX IF NOT EXISTS idx_serial_parameter ON water_logs(serial_number, parameter_type)",
            ),
            (
                "idx_datetime_parameter",
                "CREATE INDEX IF NOT EXISTS idx_datetime_parameter ON water_logs(datetime, parameter_type)",
            ),
            (
                "idx_statistic_type",
                "CREATE INDEX IF NOT EXISTS idx_statistic_type ON water_logs(statistic_type)",
            ),
            (
                "idx_combined",
                "CREATE INDEX IF NOT EXISTS idx_combined ON water_logs(datetime, serial_number, parameter_type, statistic_type)",
            ),
        ]

        for idx_name, idx_query in index_definitions:
            if idx_name not in existing_indices:
                conn.execute(idx_query)

    @contextmanager
    def get_connection(self):
        """Get a database connection with thread safety"""
        # Thread-safe connection pool
        import threading

        thread_id = threading.get_ident()

        if thread_id not in self.connection_pool:
            self.connection_pool[thread_id] = sqlite3.connect(
                self.db_path, timeout=30.0, isolation_level=None
            )
            # Enable foreign keys
            self.connection_pool[thread_id].execute("PRAGMA foreign_keys=ON")

        conn = self.connection_pool[thread_id]
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            # Don't close the connection, keep it in the pool
            pass

    def insert_data_batch(self, df: pd.DataFrame, batch_size: int = 1000) -> int:
        """Insert data in optimized batches for better performance"""
        if df.empty:
            return 0

        total_inserted = 0
        start_time = time.time()

        try:
            with self.get_connection() as conn:
                # Begin transaction for all inserts
                conn.execute("BEGIN TRANSACTION")

                # Prepare DataFrame for insertion
                df_clean = df.copy()
                if (
                    "datetime" in df_clean.columns
                    and pd.api.types.is_datetime64_any_dtype(df_clean["datetime"])
                ):
                    df_clean["datetime"] = df_clean["datetime"].dt.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                # Ensure all required columns exist
                columns_to_insert = [
                    "datetime",
                    "serial_number",
                    "parameter_type",
                    "statistic_type",
                    "value",
                    "count",
                    "unit",
                    "description",
                    "data_quality",
                    "raw_parameter",
                    "line_number",
                ]

                for col in columns_to_insert:
                    if col not in df_clean.columns:
                        df_clean[col] = None

                # Prepare the insert statement once
                insert_sql = """
                    INSERT INTO water_logs
                    (datetime, serial_number, parameter_type, statistic_type,
                     value, count, unit, description, data_quality,
                     raw_parameter, line_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                # Process in batches for memory efficiency
                for start_idx in range(0, len(df_clean), batch_size):
                    end_idx = min(start_idx + batch_size, len(df_clean))
                    batch_df = df_clean.iloc[start_idx:end_idx]
                    data_to_insert = batch_df[columns_to_insert].values.tolist()

                    # Execute batch insert
                    conn.executemany(insert_sql, data_to_insert)
                    total_inserted += len(batch_df)

                    # Intermediate commit for very large datasets to avoid transaction overhead
                    if total_inserted % 10000 == 0:
                        conn.execute("COMMIT")
                        conn.execute("BEGIN TRANSACTION")

                # Final commit
                conn.execute("COMMIT")

                # Log performance metrics
                elapsed = time.time() - start_time
                print(
                    f"Batch insert completed: {total_inserted:,} records in {elapsed:.2f}s ({total_inserted/elapsed:.1f} records/sec)"
                )

        except Exception as e:
            print(f"Error inserting data: {e}")
            traceback.print_exc()
            return 0

        return total_inserted

    def insert_file_metadata(
        self, filename: str, file_size: int, records_imported: int, parsing_stats: str
    ):
        """Insert file metadata with error handling"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO file_metadata
                    (filename, file_size, records_imported, parsing_stats)
                    VALUES (?, ?, ?, ?)
                """,
                    (filename, file_size, records_imported, parsing_stats),
                )
        except Exception as e:
            print(f"Error inserting file metadata: {e}")
            traceback.print_exc()

    def get_all_logs(
        self, limit: Optional[int] = None, chunk_size: int = None
    ) -> pd.DataFrame:
        """
        Get all logs with memory-optimized processing for large datasets
        """
        try:
            with self.get_connection() as conn:
                stats = ["avg", "min", "max"]
                frames = []

                # Process each statistic type separately for memory efficiency
                for stat in stats:
                    stat_query = f"""
                        SELECT
                            datetime,
                            serial_number AS serial,
                            parameter_type AS param,
                            value AS {stat},
                            unit
                        FROM water_logs
                        WHERE statistic_type = ?
                    """

                    # Add limit if specified
                    if limit:
                        stat_query += f" LIMIT {limit}"

                    # Use chunked reading for large datasets
                    if chunk_size:
                        chunks = []
                        for chunk in pd.read_sql_query(
                            stat_query,
                            conn,
                            params=[stat],
                            parse_dates=["datetime"],
                            chunksize=chunk_size,
                        ):
                            chunks.append(chunk)

                        if chunks:
                            df_stat = pd.concat(chunks)
                        else:
                            df_stat = pd.DataFrame()
                    else:
                        df_stat = pd.read_sql_query(
                            stat_query, conn, params=[stat], parse_dates=["datetime"]
                        )

                    frames.append(df_stat)

                # If any frames are empty, return empty dataframe
                if any(df.empty for df in frames):
                    return pd.DataFrame()

                # Optimize merge for memory efficiency
                def merge_func(left, right):
                    return pd.merge(
                        left,
                        right,
                        on=["datetime", "serial", "param", "unit"],
                        how="outer",
                        # Use copy=False for memory efficiency (modifies in place)
                        copy=False,
                    )

                df_merged = reduce(merge_func, frames)

                # Calculate diff column
                df_merged["diff"] = df_merged["max"] - df_merged["min"]

                return df_merged

        except Exception as e:
            print(f"Error retrieving logs: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_logs_by_parameter(
        self,
        parameter_type: str,
        serial_number: Optional[str] = None,
        chunk_size: Optional[int] = None,
    ) -> pd.DataFrame:
        """Get logs filtered by parameter type with chunked processing"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT
                        datetime,
                        serial_number as serial,
                        parameter_type as param,
                        value as avg,
                        unit,
                        statistic_type,
                        data_quality
                    FROM water_logs
                    WHERE parameter_type = ?
                """
                params = [parameter_type]

                if serial_number:
                    query += " AND serial_number = ?"
                    params.append(serial_number)

                query += " ORDER BY datetime ASC"

                # Use chunked reading for large datasets
                if chunk_size:
                    chunks = []
                    for chunk in pd.read_sql_query(
                        query,
                        conn,
                        params=params,
                        parse_dates=["datetime"],
                        chunksize=chunk_size,
                    ):
                        chunks.append(chunk)

                    if chunks:
                        return pd.concat(chunks)
                    return pd.DataFrame()
                else:
                    return pd.read_sql_query(
                        query, conn, params=params, parse_dates=["datetime"]
                    )

        except Exception as e:
            print(f"Error retrieving parameter logs: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_summary_statistics(self) -> Dict:
        """Get summary statistics with optimized queries"""
        try:
            with self.get_connection() as conn:
                # Use a single transaction for better performance
                conn.execute("BEGIN")

                # Get basic counts with optimized queries
                total_records = conn.execute(
                    "SELECT COUNT(*) FROM water_logs"
                ).fetchone()[0]

                unique_params = conn.execute(
                    "SELECT COUNT(DISTINCT parameter_type) FROM water_logs"
                ).fetchone()[0]

                unique_serials = conn.execute(
                    "SELECT COUNT(DISTINCT serial_number) FROM water_logs"
                ).fetchone()[0]

                date_range = conn.execute(
                    "SELECT MIN(datetime), MAX(datetime) FROM water_logs"
                ).fetchone()

                # Get quality distribution efficiently
                quality_dist = pd.read_sql_query(
                    """
                    SELECT data_quality, COUNT(*) as count
                    FROM water_logs
                    GROUP BY data_quality
                    """,
                    conn,
                )

                conn.execute("COMMIT")

                return {
                    "total_records": total_records,
                    "unique_parameters": unique_params,
                    "unique_serials": unique_serials,
                    "date_range": date_range,
                    "quality_distribution": (
                        quality_dist.to_dict("records")
                        if not quality_dist.empty
                        else []
                    ),
                }

        except Exception as e:
            print(f"Error getting summary statistics: {e}")
            traceback.print_exc()
            return {}

    def get_file_history(self, chunk_size: Optional[int] = None) -> pd.DataFrame:
        """Get file import history with chunked reading"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT
                        filename,
                        file_size,
                        records_imported,
                        import_timestamp,
                        parsing_stats
                    FROM file_metadata
                    ORDER BY import_timestamp DESC
                """

                if chunk_size:
                    chunks = []
                    for chunk in pd.read_sql_query(
                        query,
                        conn,
                        parse_dates=["import_timestamp"],
                        chunksize=chunk_size,
                    ):
                        chunks.append(chunk)

                    if chunks:
                        return pd.concat(chunks)
                    return pd.DataFrame()
                else:
                    return pd.read_sql_query(
                        query, conn, parse_dates=["import_timestamp"]
                    )

        except Exception as e:
            print(f"Error retrieving file history: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def clear_all(self):
        """Clear all data with optimized transaction handling"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN TRANSACTION")
                conn.execute("DELETE FROM water_logs")
                conn.execute("DELETE FROM file_metadata")
                conn.execute("COMMIT")

                # Reset auto-increment counters
                conn.execute("BEGIN TRANSACTION")
                conn.execute("DELETE FROM sqlite_sequence WHERE name='water_logs'")
                conn.execute("DELETE FROM sqlite_sequence WHERE name='file_metadata'")
                conn.execute("COMMIT")

        except Exception as e:
            print(f"Error clearing database: {e}")
            traceback.print_exc()

    def vacuum_database(self):
        """Optimize database by running VACUUM"""
        try:
            # VACUUM requires its own connection
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("VACUUM")
                print("Database vacuumed successfully")
        except Exception as e:
            print(f"Error vacuuming database: {e}")
            traceback.print_exc()

    def get_database_size(self) -> int:
        """Get database file size in bytes with error handling"""
        try:
            return os.path.getsize(self.db_path)
        except Exception as e:
            print(f"Error getting database size: {e}")
            return 0

    def optimize_for_reading(self):
        """Apply optimizations for read performance"""
        try:
            with self.get_connection() as conn:
                # Memory and performance optimizations
                conn.execute("PRAGMA cache_size=20000")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA temp_store=MEMORY")
                conn.execute("PRAGMA mmap_size=30000000")

                # Analyze tables for query planner
                conn.execute("ANALYZE water_logs")
                conn.execute("ANALYZE file_metadata")

                print("Database optimized for reading")
        except Exception as e:
            print(f"Error optimizing DB: {e}")
            traceback.print_exc()

    def __del__(self):
        """Cleanup database connections on object destruction"""
        try:
            # Close all pooled connections
            for thread_id, conn in self.connection_pool.items():
                try:
                    conn.close()
                except:
                    pass
        except:
            pass
