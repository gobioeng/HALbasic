"""
Machine Manager for HALbasic Multi-Machine Log Analysis
Handles machine-specific dataset filtering and management.

This module provides functionality to:
- Extract unique machine serial numbers from uploaded logs
- Filter data by selected machine
- Manage machine-specific analysis contexts
- Handle fallback behavior for single-machine scenarios

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from database import DatabaseManager


class MachineManager:
    """Manages machine-specific datasets and analysis contexts for multi-machine support"""
    
    def __init__(self, database_manager: DatabaseManager):
        """Initialize machine manager with database connection"""
        self.db = database_manager
        self._available_machines = []
        self._selected_machine = None
        self._machine_data_cache = {}
        
    def get_available_machines(self) -> List[str]:
        """Get list of unique serial numbers available in the database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT serial_number 
                    FROM water_logs 
                    WHERE serial_number IS NOT NULL 
                    AND serial_number != ''
                    AND serial_number != 'Unknown'
                    ORDER BY serial_number
                """)
                machines = [row[0] for row in cursor.fetchall()]
                self._available_machines = machines
                return machines
        except Exception as e:
            print(f"Error getting available machines: {e}")
            return []
    
    def get_machine_count(self) -> int:
        """Get total number of unique machines in database"""
        return len(self.get_available_machines())
    
    def set_selected_machine(self, machine_id: str):
        """Set the currently selected machine for analysis"""
        if machine_id in self.get_available_machines() or machine_id == "All Machines":
            self._selected_machine = machine_id
            # Clear cached data when selection changes
            self._machine_data_cache.clear()
        else:
            raise ValueError(f"Machine {machine_id} not found in available machines")
    
    def get_selected_machine(self) -> Optional[str]:
        """Get currently selected machine ID"""
        return self._selected_machine
    
    def get_filtered_data(self, data: pd.DataFrame = None) -> pd.DataFrame:
        """Filter data by currently selected machine
        
        Args:
            data: DataFrame to filter. If None, loads all data from database
            
        Returns:
            Filtered DataFrame for selected machine
        """
        if data is None:
            # Load data from database
            try:
                data = self.db.get_all_logs(chunk_size=10000)
            except TypeError:
                data = self.db.get_all_logs()
        
        if data.empty:
            return data
            
        # If no machine selected or "All Machines" selected, return all data
        if not self._selected_machine or self._selected_machine == "All Machines":
            return data
        
        # Filter by selected machine
        # Handle different possible column names for serial number
        serial_column = None
        for col in ['serial_number', 'serial', 'Serial']:
            if col in data.columns:
                serial_column = col
                break
        
        if serial_column is None:
            print("Warning: No serial number column found in data")
            return data
        
        filtered_data = data[data[serial_column] == self._selected_machine].copy()
        return filtered_data
    
    def get_machine_summary(self, machine_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for a specific machine
        
        Args:
            machine_id: Machine to get summary for. If None, uses selected machine
            
        Returns:
            Dictionary with machine summary statistics
        """
        target_machine = machine_id or self._selected_machine
        if not target_machine or target_machine == "All Machines":
            return self._get_all_machines_summary()
        
        try:
            with self.db.get_connection() as conn:
                # Get record count for machine
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM water_logs 
                    WHERE serial_number = ?
                """, (target_machine,))
                record_count = cursor.fetchone()[0]
                
                # Get parameter count for machine
                cursor = conn.execute("""
                    SELECT COUNT(DISTINCT parameter_type) FROM water_logs 
                    WHERE serial_number = ?
                """, (target_machine,))
                parameter_count = cursor.fetchone()[0]
                
                # Get date range for machine
                cursor = conn.execute("""
                    SELECT MIN(datetime), MAX(datetime) FROM water_logs 
                    WHERE serial_number = ?
                """, (target_machine,))
                date_range = cursor.fetchone()
                
                return {
                    'machine_id': target_machine,
                    'record_count': record_count,
                    'parameter_count': parameter_count,
                    'start_date': date_range[0] if date_range[0] else 'N/A',
                    'end_date': date_range[1] if date_range[1] else 'N/A'
                }
        except Exception as e:
            print(f"Error getting machine summary: {e}")
            return {}
    
    def _get_all_machines_summary(self) -> Dict[str, Any]:
        """Get summary for all machines combined"""
        try:
            summary_stats = self.db.get_summary_statistics()
            machines = self.get_available_machines()
            
            return {
                'machine_id': 'All Machines',
                'record_count': summary_stats.get('total_records', 0),
                'parameter_count': summary_stats.get('unique_parameters', 0),
                'machine_count': len(machines),
                'machines': machines
            }
        except Exception as e:
            print(f"Error getting all machines summary: {e}")
            return {}
    
    def auto_select_machine(self) -> str:
        """Auto-select machine based on available data
        
        Returns:
            Selected machine ID or "All Machines"
        """
        machines = self.get_available_machines()
        
        if len(machines) == 0:
            return "No Machines"
        elif len(machines) == 1:
            # Single machine - auto select it
            self.set_selected_machine(machines[0])
            return machines[0]
        else:
            # Multiple machines - default to "All Machines"
            self.set_selected_machine("All Machines")
            return "All Machines"
    
    def get_machine_dropdown_options(self) -> List[str]:
        """Get list of options for machine selection dropdown
        
        Returns:
            List including "All Machines" option plus individual machines
        """
        machines = self.get_available_machines()
        
        if len(machines) == 0:
            return ["No Machines Available"]
        elif len(machines) == 1:
            # Single machine - just show the machine name
            return machines
        else:
            # Multiple machines - show "All Machines" option first
            return ["All Machines"] + machines
    
    def clear_cache(self):
        """Clear internal data cache"""
        self._machine_data_cache.clear()