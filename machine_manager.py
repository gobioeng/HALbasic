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


# Professional color palette for multi-machine visualization (10+ distinct colors)
MACHINE_COLORS = {
    'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'],
    'palette': {
        'blue': '#1f77b4', 'orange': '#ff7f0e', 'green': '#2ca02c', 
        'red': '#d62728', 'purple': '#9467bd', 'brown': '#8c564b',
        'pink': '#e377c2', 'gray': '#7f7f7f', 'olive': '#bcbd22', 'cyan': '#17becf'
    }
}


class MachineManager:
    """Manages machine-specific datasets and analysis contexts for single-machine support"""
    
    def __init__(self, database_manager: DatabaseManager):
        """Initialize machine manager with database connection"""
        self.db = database_manager
        self._available_machines = []
        self._selected_machine = None
        self._selected_machines = []  # For multi-selection support
        self._machine_data_cache = {}
        
        # Initialize single machine database manager for new architecture
        try:
            from single_machine_database import SingleMachineDatabaseManager
            self.single_machine_db = SingleMachineDatabaseManager()
            self._use_single_machine_architecture = True
            print("✓ Single-machine database architecture enabled")
        except ImportError:
            self.single_machine_db = None
            self._use_single_machine_architecture = False
            print("Warning: Single-machine database architecture not available, using legacy mode")
        
    def get_available_machines(self) -> List[str]:
        """Get list of unique serial numbers available in the database"""
        try:
            # Use single-machine architecture if available
            if self._use_single_machine_architecture and self.single_machine_db:
                machines = self.single_machine_db.discover_available_machines()
                self._available_machines = machines
                return machines
            
            # Fallback to legacy combined database approach
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
    
    def set_selected_machine(self, machine_id: str, validate=True):
        """Set the currently selected machine for analysis (single selection)
        
        Args:
            machine_id: Machine ID to select
            validate: Whether to validate machine exists (set False for testing)
        """
        if validate:
            available_machines = self.get_available_machines()
            if machine_id not in available_machines and machine_id != "All Machines":
                raise ValueError(f"Machine {machine_id} not found in available machines")
        
        # Handle single-machine database switching
        if self._use_single_machine_architecture and self.single_machine_db and machine_id != "All Machines":
            success = self.single_machine_db.switch_to_machine(machine_id)
            if not success:
                raise RuntimeError(f"Failed to switch to machine {machine_id} database")
        
        self._selected_machine = machine_id
        # For backward compatibility, reset multi-selection when single machine is selected
        if machine_id == "All Machines":
            self._selected_machines = []
        else:
            self._selected_machines = [machine_id]
        # Clear cached data when selection changes
        self._machine_data_cache.clear()
    
    def set_selected_machines(self, machine_ids: List[str], validate=True):
        """Set multiple selected machines for analysis (multi-selection)
        
        Args:
            machine_ids: List of machine IDs to select
            validate: Whether to validate machines exist (set False for testing)
        """
        if validate:
            available_machines = self.get_available_machines()
            valid_machines = []
            for machine_id in machine_ids:
                if machine_id in available_machines:
                    valid_machines.append(machine_id)
                else:
                    print(f"Warning: Machine {machine_id} not found in available machines")
        else:
            valid_machines = machine_ids
        
        self._selected_machines = valid_machines
        # Update single selection for backward compatibility
        if len(valid_machines) == 1:
            self._selected_machine = valid_machines[0]
        elif len(valid_machines) == 0:
            self._selected_machine = "All Machines"
        else:
            self._selected_machine = "Multiple Machines"
        
        # Clear cached data when selection changes
        self._machine_data_cache.clear()
    
    def get_selected_machines(self) -> List[str]:
        """Get list of currently selected machines"""
        return self._selected_machines.copy()
    
    def is_multi_machine_selected(self) -> bool:
        """Check if multiple machines are selected"""
        return len(self._selected_machines) > 1
    
    def get_selected_machine(self) -> Optional[str]:
        """Get currently selected machine ID"""
        return self._selected_machine
    
    def get_filtered_data(self, data: pd.DataFrame = None) -> pd.DataFrame:
        """Filter data by currently selected machine
        
        Args:
            data: DataFrame to filter. If None, loads raw data from database
            
        Returns:
            Filtered DataFrame for selected machine
        """
        if data is None:
            # Load raw data from database using a simple query
            try:
                with self.db.get_connection() as conn:
                    data = pd.read_sql_query("""
                        SELECT datetime, serial_number, parameter_type, 
                               statistic_type, value, count, unit, description
                        FROM water_logs
                        ORDER BY datetime
                    """, conn)
                    # Convert datetime with flexible parsing
                    if not data.empty and 'datetime' in data.columns:
                        try:
                            data['datetime'] = pd.to_datetime(data['datetime'], format='mixed')
                        except:
                            # Fallback to basic conversion
                            data['datetime'] = pd.to_datetime(data['datetime'], errors='coerce')
            except Exception as e:
                print(f"Error loading raw data: {e}")
                return pd.DataFrame()
        
        if data.empty:
            return data
            
        # If no machine selected or "All Machines" selected, return all data
        if not self._selected_machine or self._selected_machine == "All Machines":
            return data
        
        # If multiple machines selected, return data for all selected machines
        if self.is_multi_machine_selected():
            # Use 'serial' column name for DataFrames from get_all_logs()
            serial_col = 'serial' if 'serial' in data.columns else 'serial_number'
            filtered_data = data[data[serial_col].isin(self._selected_machines)].copy()
            return filtered_data
        
        # Filter by single selected machine
        # Use 'serial' column name for DataFrames from get_all_logs()
        serial_col = 'serial' if 'serial' in data.columns else 'serial_number'
        filtered_data = data[data[serial_col] == self._selected_machine].copy()
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
    
    def get_multi_machine_data(self, data: pd.DataFrame = None) -> Dict[str, pd.DataFrame]:
        """Get data for multiple selected machines, organized by machine ID
        
        Args:
            data: DataFrame to filter. If None, loads from database
            
        Returns:
            Dictionary mapping machine IDs to their filtered data
        """
        if data is None:
            # Load raw data from database
            try:
                with self.db.get_connection() as conn:
                    data = pd.read_sql_query("""
                        SELECT datetime, serial_number, parameter_type, 
                               statistic_type, value, count, unit, description
                        FROM water_logs
                        ORDER BY datetime
                    """, conn)
                    if not data.empty and 'datetime' in data.columns:
                        try:
                            data['datetime'] = pd.to_datetime(data['datetime'], format='mixed')
                        except:
                            data['datetime'] = pd.to_datetime(data['datetime'], errors='coerce')
            except Exception as e:
                print(f"Error loading raw data: {e}")
                return {}
        
        if data.empty:
            return {}
        
        # If no specific machines selected, return all available machines
        if not self._selected_machines or len(self._selected_machines) == 0:
            available_machines = self.get_available_machines()
            result = {}
            # Use 'serial' column name for DataFrames from get_all_logs()
            serial_col = 'serial' if 'serial' in data.columns else 'serial_number'
            for machine in available_machines:
                machine_data = data[data[serial_col] == machine].copy()
                if not machine_data.empty:
                    result[machine] = machine_data
            return result
        
        # Return data for selected machines only
        result = {}
        # Use 'serial' column name for DataFrames from get_all_logs()
        serial_col = 'serial' if 'serial' in data.columns else 'serial_number'
        for machine_id in self._selected_machines:
            machine_data = data[data[serial_col] == machine_id].copy()
            if not machine_data.empty:
                result[machine_id] = machine_data
        return result
    
    def get_machine_color(self, machine_id: str) -> str:
        """Get consistently assigned color for a machine ID
        
        Args:
            machine_id: Machine ID to get color for
            
        Returns:
            Hex color code for the machine
        """
        available_machines = self.get_available_machines()
        
        # Create consistent mapping by sorting machine IDs alphabetically  
        if machine_id in available_machines:
            index = sorted(available_machines).index(machine_id)
            color_index = index % len(MACHINE_COLORS['default'])
            return MACHINE_COLORS['default'][color_index]
        
        # Fallback to default blue for unknown machines
        return MACHINE_COLORS['palette']['blue']
    
    def get_machine_metadata(self, machine_id: str) -> dict:
        """Get machine metadata including color, display name, and status
        
        Args:
            machine_id: Machine ID to get metadata for
            
        Returns:
            Dictionary with color, display_name, status information
        """
        try:
            available_machines = self.get_available_machines()
            
            if machine_id not in available_machines and machine_id != "All Machines":
                return {
                    'machine_id': machine_id,
                    'color': MACHINE_COLORS['palette']['gray'],
                    'display_name': machine_id,
                    'status': 'unknown',
                    'available': False
                }
            
            # Get basic summary for status determination
            summary = self.get_machine_summary(machine_id)
            
            # Determine status based on data availability
            status = 'active'
            if summary.get('record_count', 0) == 0:
                status = 'inactive'
            elif summary.get('parameter_count', 0) < 3:
                status = 'limited'
                
            return {
                'machine_id': machine_id,
                'color': self.get_machine_color(machine_id),
                'display_name': machine_id.replace('_', ' ').title(),
                'status': status,
                'available': True,
                'record_count': summary.get('record_count', 0),
                'parameter_count': summary.get('parameter_count', 0),
                'date_range': (summary.get('start_date'), summary.get('end_date'))
            }
            
        except Exception as e:
            print(f"Error getting machine metadata for {machine_id}: {e}")
            return {
                'machine_id': machine_id,
                'color': MACHINE_COLORS['palette']['gray'],
                'display_name': machine_id,
                'status': 'error',
                'available': False
            }
    
    def get_machine_comparison_data(self, machine1_id: str, machine2_id: str, parameter: str) -> dict:
        """Get comparison data between two machines for a specific parameter
        
        Args:
            machine1_id: First machine ID
            machine2_id: Second machine ID  
            parameter: Parameter type to compare
            
        Returns:
            Dictionary with comparison data for both machines
        """
        # Use single-machine architecture if available for better performance
        if self._use_single_machine_architecture and self.single_machine_db:
            return self.single_machine_db.get_comparison_data(machine1_id, machine2_id, parameter)
        
        # Fallback to legacy approach
        try:
            comparison_data = {
                'machine1': {'id': machine1_id, 'data': pd.DataFrame()},
                'machine2': {'id': machine2_id, 'data': pd.DataFrame()},
                'parameter': parameter,
                'comparison_stats': {},
                'correlation': None
            }
            
            # Get data for each machine
            for machine_key, machine_id in [('machine1', machine1_id), ('machine2', machine2_id)]:
                # Temporarily set selected machine to get filtered data
                original_selection = self._selected_machine
                self.set_selected_machine(machine_id)
                
                # Get parameter-specific data
                with self.db.get_connection() as conn:
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
                    # Calculate statistics for this machine
                    avg_data = data[data['statistic_type'] == 'avg']['value']
                    if not avg_data.empty:
                        comparison_data[machine_key]['data'] = data
                        comparison_data[machine_key]['stats'] = {
                            'mean': avg_data.mean(),
                            'std': avg_data.std(),
                            'min': avg_data.min(), 
                            'max': avg_data.max(),
                            'count': len(avg_data)
                        }
                
                # Restore original selection
                self.set_selected_machine(original_selection)
            
            # Calculate cross-machine comparison statistics
            if (not comparison_data['machine1']['data'].empty and 
                not comparison_data['machine2']['data'].empty):
                
                m1_avg = comparison_data['machine1']['data'][comparison_data['machine1']['data']['statistic_type'] == 'avg']['value']
                m2_avg = comparison_data['machine2']['data'][comparison_data['machine2']['data']['statistic_type'] == 'avg']['value']
                
                if len(m1_avg) > 1 and len(m2_avg) > 1:
                    # Calculate correlation if we have enough data points
                    min_len = min(len(m1_avg), len(m2_avg))
                    try:
                        correlation = m1_avg.iloc[:min_len].corr(m2_avg.iloc[:min_len])
                        comparison_data['correlation'] = correlation
                    except:
                        comparison_data['correlation'] = None
                
                comparison_data['comparison_stats'] = {
                    'mean_difference': comparison_data['machine1']['stats']['mean'] - comparison_data['machine2']['stats']['mean'],
                    'std_difference': comparison_data['machine1']['stats']['std'] - comparison_data['machine2']['stats']['std'],
                    'range_overlap': self._calculate_range_overlap(
                        comparison_data['machine1']['stats'],
                        comparison_data['machine2']['stats']
                    )
                }
            
            return comparison_data
            
        except Exception as e:
            print(f"Error getting machine comparison data: {e}")
            return {
                'machine1': {'id': machine1_id, 'data': pd.DataFrame()},
                'machine2': {'id': machine2_id, 'data': pd.DataFrame()},
                'parameter': parameter,
                'error': str(e)
            }
    
    def get_multi_machine_stats(self) -> dict:
        """Get comprehensive statistics for all machines
        
        Returns:
            Dictionary with per-machine statistics and fleet summaries
        """
        try:
            available_machines = self.get_available_machines()
            
            if not available_machines:
                return {'machines': {}, 'fleet_stats': {}, 'error': 'No machines available'}
            
            machine_stats = {}
            fleet_totals = {
                'total_records': 0,
                'total_parameters': set(),
                'date_range': {'earliest': None, 'latest': None}
            }
            
            # Get statistics for each machine
            for machine_id in available_machines:
                try:
                    summary = self.get_machine_summary(machine_id)
                    metadata = self.get_machine_metadata(machine_id)
                    
                    machine_stats[machine_id] = {
                        **summary,
                        **metadata,
                        'performance_rank': 0  # Will be calculated later
                    }
                    
                    # Accumulate fleet statistics
                    fleet_totals['total_records'] += summary.get('record_count', 0)
                    
                    # Track date range
                    start_date = summary.get('start_date')
                    end_date = summary.get('end_date')
                    
                    if start_date and (not fleet_totals['date_range']['earliest'] or start_date < fleet_totals['date_range']['earliest']):
                        fleet_totals['date_range']['earliest'] = start_date
                        
                    if end_date and (not fleet_totals['date_range']['latest'] or end_date > fleet_totals['date_range']['latest']):
                        fleet_totals['date_range']['latest'] = end_date
                        
                except Exception as e:
                    print(f"Error getting stats for machine {machine_id}: {e}")
                    continue
            
            # Calculate performance rankings
            machine_records = [(mid, stats.get('record_count', 0)) for mid, stats in machine_stats.items()]
            machine_records.sort(key=lambda x: x[1], reverse=True)
            
            for rank, (machine_id, _) in enumerate(machine_records, 1):
                if machine_id in machine_stats:
                    machine_stats[machine_id]['performance_rank'] = rank
            
            fleet_stats = {
                'total_machines': len(available_machines),
                'active_machines': sum(1 for stats in machine_stats.values() if stats.get('status') == 'active'),
                'total_records': fleet_totals['total_records'],
                'average_records_per_machine': fleet_totals['total_records'] / len(available_machines) if available_machines else 0,
                'fleet_date_range': fleet_totals['date_range']
            }
            
            return {
                'machines': machine_stats,
                'fleet_stats': fleet_stats,
                'color_mapping': {mid: self.get_machine_color(mid) for mid in available_machines}
            }
            
        except Exception as e:
            print(f"Error getting multi-machine stats: {e}")
            return {'machines': {}, 'fleet_stats': {}, 'error': str(e)}
    
    def export_machine_comparison(self, machines: List[str], parameters: List[str]) -> pd.DataFrame:
        """Export machine comparison data for specified machines and parameters
        
        Args:
            machines: List of machine IDs to include
            parameters: List of parameters to compare
            
        Returns:
            DataFrame with comparison data suitable for export
        """
        try:
            export_data = []
            
            for machine_id in machines:
                machine_metadata = self.get_machine_metadata(machine_id)
                
                for parameter in parameters:
                    # Get parameter data for this machine
                    with self.db.get_connection() as conn:
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
                        # Calculate summary statistics for export
                        for stat_type in ['avg', 'min', 'max']:
                            stat_data = data[data['statistic_type'] == stat_type]
                            if not stat_data.empty:
                                export_row = {
                                    'Machine_ID': machine_id,
                                    'Machine_Color': machine_metadata['color'],
                                    'Parameter': parameter,
                                    'Statistic_Type': stat_type,
                                    'Value_Mean': stat_data['value'].mean(),
                                    'Value_Std': stat_data['value'].std(),
                                    'Value_Min': stat_data['value'].min(),
                                    'Value_Max': stat_data['value'].max(),
                                    'Data_Points': len(stat_data),
                                    'Unit': stat_data['unit'].iloc[0] if not stat_data['unit'].isna().all() else '',
                                    'Date_Range_Start': stat_data['datetime'].min(),
                                    'Date_Range_End': stat_data['datetime'].max(),
                                    'Machine_Status': machine_metadata['status']
                                }
                                export_data.append(export_row)
            
            if export_data:
                return pd.DataFrame(export_data)
            else:
                # Return empty DataFrame with proper column structure
                return pd.DataFrame(columns=[
                    'Machine_ID', 'Machine_Color', 'Parameter', 'Statistic_Type',
                    'Value_Mean', 'Value_Std', 'Value_Min', 'Value_Max', 'Data_Points',
                    'Unit', 'Date_Range_Start', 'Date_Range_End', 'Machine_Status'
                ])
                
        except Exception as e:
            print(f"Error exporting machine comparison: {e}")
            return pd.DataFrame()
    
    def _calculate_range_overlap(self, stats1: dict, stats2: dict) -> float:
        """Calculate the overlap percentage between two machines' parameter ranges
        
        Args:
            stats1: Statistics for first machine
            stats2: Statistics for second machine
            
        Returns:
            Overlap percentage (0.0 to 1.0)
        """
        try:
            min1, max1 = stats1['min'], stats1['max']
            min2, max2 = stats2['min'], stats2['max']
            
            # Calculate overlap
            overlap_start = max(min1, min2)
            overlap_end = min(max1, max2)
            
            if overlap_start >= overlap_end:
                return 0.0  # No overlap
            
            overlap_range = overlap_end - overlap_start
            total_range = max(max1, max2) - min(min1, min2)
            
            if total_range == 0:
                return 1.0  # Both ranges are single points and they overlap
                
            return overlap_range / total_range
            
        except Exception:
            return 0.0

    def get_machine_color_scheme(self) -> Dict[str, str]:
        """Get color scheme for multi-machine visualization
        
        Returns:
            Dictionary mapping machine IDs to colors
        """
        machines = self.get_available_machines() if not self._selected_machines else self._selected_machines
        
        machine_colors = {}
        for machine in machines:
            machine_colors[machine] = self.get_machine_color(machine)
        
        return machine_colors