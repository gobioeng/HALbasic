"""
Single Machine Database Manager - HALog Enhancement
Provides per-machine database architecture for improved performance and data isolation.

This module implements:
- Separate SQLite database per machine: halog_machine_{serial_number}.db
- Database switching mechanism when user selects different machine
- Machine database discovery and management
- Data migration from combined database to per-machine databases
- Connection management with single machine context

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import sqlite3
import pandas as pd
from typing import Optional, Dict, List, Any, Tuple
import os
from pathlib import Path
from contextlib import contextmanager
import shutil
import traceback
from datetime import datetime

from database import DatabaseManager


class SingleMachineDatabaseManager:
    """Enhanced database manager with single-machine architecture for better performance"""
    
    def __init__(self, app_data_dir: str = "data"):
        self.app_data_dir = Path(app_data_dir)
        self.db_dir = self.app_data_dir / "database"
        self.machines_dir = self.db_dir / "machines"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Current machine context
        self.current_machine_id = None
        self.current_db_path = None
        self.current_connection = None
        
        # Cache of available machines discovered from database files
        self._available_machines_cache = {}
        
        # Connection pool for comparison mode (machine_id -> connection)
        self.comparison_connections = {}
        
        print("✓ Single Machine Database Manager initialized")
    
    def add_sample_data_for_testing(self):
        """Add sample data to machine databases for testing purposes"""
        from datetime import datetime, timedelta
        
        machines = ["2123", "2207", "2350"]
        sample_parameters = [
            ("magnetronFlow", "L/min", "Mag Flow"),
            ("pumpPressure", "PSI", "Pump Pressure"), 
            ("FanremoteTempStatistics", "°C", "Temp Room"),
            ("targetAndCirculatorFlow", "L/min", "Flow Target")
        ]
        
        for machine_id in machines:
            if self.create_machine_database(machine_id):
                if self.switch_to_machine(machine_id):
                    print(f"Adding sample data for machine {machine_id}...")
                    
                    # Generate sample data for last 24 hours
                    base_time = datetime.now() - timedelta(hours=24)
                    sample_records = []
                    
                    for i in range(48):  # Every 30 minutes for 24 hours
                        timestamp = base_time + timedelta(minutes=30 * i)
                        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        
                        for param_name, unit, description in sample_parameters:
                            # Generate realistic values
                            if "Flow" in param_name:
                                base_value = 10.0 + float(machine_id) / 1000  # Slight variation per machine
                                value = base_value + (i % 10) * 0.5  # Vary over time
                            elif "Pressure" in param_name:
                                base_value = 20.0 + float(machine_id) / 1000 
                                value = base_value + (i % 8) * 0.8
                            else:  # Temperature
                                base_value = 22.0 + float(machine_id) / 1000
                                value = base_value + (i % 6) * 0.3
                            
                            sample_records.append({
                                'datetime': timestamp_str,
                                'serial_number': machine_id,
                                'parameter_type': param_name,
                                'statistic_type': 'avg',
                                'value': round(value, 2),
                                'count': 10,
                                'unit': unit,
                                'description': description,
                                'data_quality': 'good',
                                'raw_parameter': param_name,
                                'line_number': i + 1
                            })
                    
                    # Insert sample data
                    import pandas as pd
                    sample_df = pd.DataFrame(sample_records)
                    self.insert_data_batch(sample_df)
                    print(f"✓ Added {len(sample_records)} sample records for machine {machine_id}")
        
        # Clear cache to refresh machine discovery
        self._available_machines_cache.clear()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        self.app_data_dir.mkdir(exist_ok=True)
        self.db_dir.mkdir(exist_ok=True)
        self.machines_dir.mkdir(exist_ok=True)
    
    def get_machine_database_path(self, machine_id: str) -> str:
        """Get database path for specific machine"""
        filename = f"halog_machine_{machine_id}.db"
        return str(self.machines_dir / filename)
    
    def discover_available_machines(self) -> List[str]:
        """Discover available machines by scanning database files"""
        machine_ids = []
        
        try:
            if not self.machines_dir.exists():
                return machine_ids
                
            for db_file in self.machines_dir.glob("halog_machine_*.db"):
                # Extract machine ID from filename
                filename = db_file.name
                if filename.startswith("halog_machine_") and filename.endswith(".db"):
                    machine_id = filename[14:-3]  # Remove "halog_machine_" and ".db"
                    
                    # Verify the database is valid (allow empty databases for now)
                    try:
                        with sqlite3.connect(str(db_file)) as conn:
                            # Check if table exists
                            cursor = conn.execute("""
                                SELECT name FROM sqlite_master 
                                WHERE type='table' AND name='water_logs'
                            """)
                            if cursor.fetchone():
                                cursor = conn.execute("SELECT COUNT(*) FROM water_logs")
                                record_count = cursor.fetchone()[0]
                                machine_ids.append(machine_id)
                                # Cache basic info
                                self._available_machines_cache[machine_id] = {
                                    'db_path': str(db_file),
                                    'record_count': record_count,
                                    'last_checked': datetime.now()
                                }
                    except Exception as e:
                        print(f"Warning: Could not validate database for machine {machine_id}: {e}")
                        
        except Exception as e:
            print(f"Error discovering machines: {e}")
            
        machine_ids.sort()
        return machine_ids
    
    def switch_to_machine(self, machine_id: str) -> bool:
        """Switch database context to specified machine
        
        Args:
            machine_id: Serial number of machine to switch to
            
        Returns:
            True if switch successful, False otherwise
        """
        try:
            # Close current connection if any
            if self.current_connection:
                self.current_connection.close()
                self.current_connection = None
            
            # Get database path for the machine
            new_db_path = self.get_machine_database_path(machine_id)
            
            # Check if database exists
            if not os.path.exists(new_db_path):
                print(f"Database for machine {machine_id} does not exist: {new_db_path}")
                return False
            
            # Test connection to the new database
            test_conn = sqlite3.connect(new_db_path)
            cursor = test_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='water_logs'")
            table_exists = cursor.fetchone() is not None
            test_conn.close()
            
            if not table_exists:
                print(f"Invalid database for machine {machine_id}: missing water_logs table")
                return False
                
            # Update current context
            self.current_machine_id = machine_id
            self.current_db_path = new_db_path
            
            print(f"✓ Switched to machine {machine_id} database: {new_db_path}")
            return True
            
        except Exception as e:
            print(f"Error switching to machine {machine_id}: {e}")
            return False
    
    @contextmanager
    def get_connection(self):
        """Get a database connection for current machine with performance optimizations"""
        if not self.current_db_path:
            raise RuntimeError("No machine selected. Call switch_to_machine() first.")
        
        # Create new connection for this context
        conn = sqlite3.connect(self.current_db_path, timeout=30.0, isolation_level=None)
        
        try:
            # Apply performance optimizations
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")  # Smaller cache for single machine
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA busy_timeout=30000")
            
            yield conn
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_machine_database(self, machine_id: str) -> bool:
        """Create a new database for specified machine
        
        Args:
            machine_id: Serial number of machine
            
        Returns:
            True if creation successful, False otherwise
        """
        try:
            db_path = self.get_machine_database_path(machine_id)
            
            # Don't overwrite existing database
            if os.path.exists(db_path):
                print(f"Database for machine {machine_id} already exists")
                return True
            
            # Create the database with same schema as main database
            conn = sqlite3.connect(db_path)
            
            # Create water_logs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS water_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime TEXT NOT NULL,
                    serial_number TEXT NOT NULL,
                    parameter_type TEXT NOT NULL,
                    statistic_type TEXT NOT NULL,
                    value REAL,
                    count INTEGER,
                    unit TEXT,
                    description TEXT,
                    data_quality TEXT DEFAULT 'good',
                    raw_parameter TEXT,
                    line_number INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create file_metadata table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_size INTEGER,
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    records_imported INTEGER DEFAULT 0,
                    processing_status TEXT DEFAULT 'pending',
                    error_details TEXT,
                    file_checksum TEXT,
                    machine_serial TEXT
                )
            """)
            
            # Create import_validation_log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS import_validation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    total_records INTEGER,
                    valid_records INTEGER,
                    invalid_records INTEGER,
                    validation_score REAL,
                    validation_details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_water_logs_datetime ON water_logs(datetime)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_water_logs_serial ON water_logs(serial_number)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_water_logs_parameter ON water_logs(parameter_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_water_logs_composite ON water_logs(serial_number, parameter_type, datetime)")
            
            conn.commit()
            conn.close()
            
            print(f"✓ Created database for machine {machine_id}: {db_path}")
            return True
            
        except Exception as e:
            print(f"Error creating database for machine {machine_id}: {e}")
            traceback.print_exc()
            return False
    
    def migrate_machine_data(self, source_db_manager: DatabaseManager, machine_id: str) -> bool:
        """Migrate data for specific machine from combined database to machine-specific database
        
        Args:
            source_db_manager: Source database manager with combined data
            machine_id: Machine serial number to migrate
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            print(f"🔄 Migrating data for machine {machine_id}...")
            
            # Create machine database if it doesn't exist
            if not self.create_machine_database(machine_id):
                return False
            
            # Get machine database path
            machine_db_path = self.get_machine_database_path(machine_id)
            
            # Extract data for this machine from source database
            with source_db_manager.get_connection() as source_conn:
                # Get water_logs data for this machine
                water_logs_query = """
                    SELECT datetime, serial_number, parameter_type, statistic_type, 
                           value, count, unit, description, data_quality, 
                           raw_parameter, line_number, created_at
                    FROM water_logs 
                    WHERE serial_number = ?
                    ORDER BY datetime
                """
                
                water_logs_df = pd.read_sql_query(
                    water_logs_query, 
                    source_conn, 
                    params=[machine_id]
                )
                
                # Get file_metadata for this machine
                metadata_query = """
                    SELECT filename, file_size, upload_timestamp, records_imported,
                           processing_status, error_details, file_checksum, machine_serial
                    FROM file_metadata
                    WHERE machine_serial = ? OR machine_serial IS NULL
                """
                
                metadata_df = pd.read_sql_query(
                    metadata_query,
                    source_conn,
                    params=[machine_id]
                )
            
            # Insert data into machine database
            machine_conn = sqlite3.connect(machine_db_path)
            
            if not water_logs_df.empty:
                water_logs_df.to_sql('water_logs', machine_conn, if_exists='append', index=False)
                print(f"  ✓ Migrated {len(water_logs_df)} water log records")
            
            if not metadata_df.empty:
                metadata_df.to_sql('file_metadata', machine_conn, if_exists='append', index=False)
                print(f"  ✓ Migrated {len(metadata_df)} file metadata records")
            
            machine_conn.commit()
            machine_conn.close()
            
            print(f"✅ Successfully migrated data for machine {machine_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error migrating data for machine {machine_id}: {e}")
            traceback.print_exc()
            return False
    
    def migrate_all_machines(self, source_db_path: str = None) -> Dict[str, bool]:
        """Migrate all machine data from combined database to separate machine databases
        
        Args:
            source_db_path: Path to source combined database (uses default if None)
            
        Returns:
            Dictionary mapping machine IDs to migration success status
        """
        try:
            # Use default combined database path if not specified
            if source_db_path is None:
                source_db_path = str(self.db_dir / "halog_water.db")
            
            if not os.path.exists(source_db_path):
                print(f"Source database not found: {source_db_path}")
                return {}
            
            # Create source database manager
            source_db_manager = DatabaseManager(source_db_path)
            
            # Get all unique machines from source database
            with source_db_manager.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT serial_number 
                    FROM water_logs 
                    WHERE serial_number IS NOT NULL 
                    AND serial_number != ''
                    AND serial_number != 'Unknown'
                    ORDER BY serial_number
                """)
                machine_ids = [row[0] for row in cursor.fetchall()]
            
            print(f"🚀 Starting migration for {len(machine_ids)} machines...")
            
            # Migrate each machine
            migration_results = {}
            for machine_id in machine_ids:
                migration_results[machine_id] = self.migrate_machine_data(source_db_manager, machine_id)
            
            # Summary
            successful = sum(1 for success in migration_results.values() if success)
            print(f"📊 Migration completed: {successful}/{len(machine_ids)} machines migrated successfully")
            
            return migration_results
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            traceback.print_exc()
            return {}
    
    def get_machine_summary(self, machine_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for current machine or specified machine
        
        Args:
            machine_id: Machine ID to get summary for (uses current if None)
            
        Returns:
            Dictionary with machine summary statistics
        """
        target_machine = machine_id or self.current_machine_id
        
        if not target_machine:
            return {'error': 'No machine specified or selected'}
        
        try:
            # If requesting different machine than current, temporarily switch
            original_machine = self.current_machine_id
            if machine_id and machine_id != self.current_machine_id:
                if not self.switch_to_machine(machine_id):
                    return {'error': f'Could not switch to machine {machine_id}'}
            
            with self.get_connection() as conn:
                # Get record count
                cursor = conn.execute("SELECT COUNT(*) FROM water_logs WHERE serial_number = ?", (target_machine,))
                record_count = cursor.fetchone()[0]
                
                # Get parameter count
                cursor = conn.execute("""
                    SELECT COUNT(DISTINCT parameter_type) FROM water_logs WHERE serial_number = ?
                """, (target_machine,))
                parameter_count = cursor.fetchone()[0]
                
                # Get date range
                cursor = conn.execute("""
                    SELECT MIN(datetime), MAX(datetime) FROM water_logs WHERE serial_number = ?
                """, (target_machine,))
                date_range = cursor.fetchone()
                
                summary = {
                    'machine_id': target_machine,
                    'record_count': record_count,
                    'parameter_count': parameter_count,
                    'start_date': date_range[0] if date_range[0] else 'N/A',
                    'end_date': date_range[1] if date_range[1] else 'N/A',
                    'database_path': self.current_db_path
                }
                
            # Restore original machine if we switched
            if original_machine and original_machine != target_machine:
                self.switch_to_machine(original_machine)
                
            return summary
            
        except Exception as e:
            print(f"Error getting machine summary: {e}")
            return {'error': str(e)}
    
    def insert_data_batch(self, df: pd.DataFrame, batch_size: int = 1000) -> int:
        """Insert data in optimized batches for current machine database
        
        Args:
            df: DataFrame with water logs data
            batch_size: Number of records per batch
            
        Returns:
            Number of records inserted
        """
        if not self.current_db_path:
            raise RuntimeError("No machine selected. Call switch_to_machine() first.")
        
        try:
            with self.get_connection() as conn:
                # Insert data in batches
                total_inserted = 0
                for i in range(0, len(df), batch_size):
                    batch_df = df.iloc[i:i + batch_size]
                    batch_df.to_sql('water_logs', conn, if_exists='append', index=False)
                    total_inserted += len(batch_df)
                
                print(f"✓ Inserted {total_inserted} records into machine {self.current_machine_id} database")
                return total_inserted
                
        except Exception as e:
            print(f"Error inserting data batch: {e}")
            raise
    
    def get_comparison_data(self, machine1_id: str, machine2_id: str, parameter: str) -> Dict[str, Any]:
        """Load comparison data from multiple machine databases
        
        Args:
            machine1_id: First machine serial number
            machine2_id: Second machine serial number  
            parameter: Parameter type to compare
            
        Returns:
            Dictionary with comparison data for both machines
        """
        comparison_data = {
            'machine1': {'id': machine1_id, 'data': pd.DataFrame(), 'stats': {}},
            'machine2': {'id': machine2_id, 'data': pd.DataFrame(), 'stats': {}}
        }
        
        try:
            # Load data for each machine
            for machine_key, machine_id in [('machine1', machine1_id), ('machine2', machine2_id)]:
                machine_db_path = self.get_machine_database_path(machine_id)
                
                if not os.path.exists(machine_db_path):
                    print(f"Warning: Database not found for machine {machine_id}")
                    continue
                
                with sqlite3.connect(machine_db_path) as conn:
                    query = """
                        SELECT datetime, value, statistic_type, unit
                        FROM water_logs 
                        WHERE serial_number = ? AND parameter_type = ?
                        ORDER BY datetime
                    """
                    
                    data = pd.read_sql_query(
                        query, conn,
                        params=[machine_id, parameter],
                        parse_dates=['datetime']
                    )
                    
                    if not data.empty:
                        comparison_data[machine_key]['data'] = data
                        
                        # Calculate statistics
                        avg_data = data[data['statistic_type'] == 'avg']['value']
                        if not avg_data.empty:
                            comparison_data[machine_key]['stats'] = {
                                'mean': avg_data.mean(),
                                'std': avg_data.std(),
                                'min': avg_data.min(),
                                'max': avg_data.max(),
                                'count': len(avg_data)
                            }
            
            return comparison_data
            
        except Exception as e:
            print(f"Error loading comparison data: {e}")
            return comparison_data
    
    def cleanup_comparison_connections(self):
        """Clean up comparison mode database connections"""
        for conn in self.comparison_connections.values():
            try:
                conn.close()
            except:
                pass
        self.comparison_connections.clear()