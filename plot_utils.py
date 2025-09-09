"""
Enhanced Unified Plotting Utilities for HALbasic
Combines plotting widgets with LINAC-specific data processing
Developer: gobioeng.com
Date: 2025-01-21
"""

# CRITICAL: Import matplotlib and configure before other imports
import matplotlib
# FIXED: Try Qt5Agg first, fall back gracefully for headless environments
try:
    matplotlib.use('Qt5Agg')
except ImportError:
    # Fallback to Agg for headless environments
    matplotlib.use('Agg')
    print("ℹ️ Using Agg backend for headless environment")

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='matplotlib')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                            QCheckBox, QGroupBox, QSplitter, QTableWidget, QTableWidgetItem,
                            QHeaderView, QPushButton, QDialog, QDialogButtonBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional, Dict, List

# Set matplotlib style for professional appearance
plt.style.use('default')


class InteractivePlotManager:
    """Manages interactive functionality for matplotlib plots"""

    def __init__(self, fig, ax, canvas):
        self.fig = fig
        self.ax = ax if isinstance(ax, list) else [ax]  # Support multiple axes
        self.canvas = canvas
        self.press = None
        self.initial_xlim = None
        self.initial_ylim = None
        self.tooltip_annotation = None

        # Store initial view for reset functionality
        self._store_initial_view()

        # Connect event handlers
        self._connect_events()

    def _store_initial_view(self):
        """Store initial view limits for reset functionality"""
        self.initial_views = []
        for ax in self.ax:
            self.initial_views.append({
                'xlim': ax.get_xlim(),
                'ylim': ax.get_ylim()
            })

    def _connect_events(self):
        """Connect interactive event handlers"""
        self.canvas.mpl_connect('scroll_event', self._handle_zoom)
        self.canvas.mpl_connect('button_press_event', self._handle_button_press)
        self.canvas.mpl_connect('button_release_event', self._handle_button_release)
        self.canvas.mpl_connect('motion_notify_event', self._handle_motion)
        self.canvas.mpl_connect('key_press_event', self._handle_key_press)

    def _handle_key_press(self, event):
        """Handle keyboard shortcuts for time scale control"""
        if event.inaxes is None:
            return
            
        ax = event.inaxes
        
        # Time scale shortcuts
        if event.key == 'h':  # Zoom to last hour
            self._zoom_to_time_range(ax, hours=1)
        elif event.key == 'd':  # Zoom to last day
            self._zoom_to_time_range(ax, hours=24)
        elif event.key == 'w':  # Zoom to last week
            self._zoom_to_time_range(ax, hours=24*7)
        elif event.key == 'm':  # Zoom to last month
            self._zoom_to_time_range(ax, hours=24*30)
        elif event.key == 'r':  # Reset view
            self.reset_view()
        elif event.key == 'f':  # Fit all data
            self._fit_all_data(ax)
            
    def _zoom_to_time_range(self, ax, hours=24):
        """Zoom to show last N hours of data"""
        try:
            # Get the latest time from all lines in the axis
            latest_time = None
            for line in ax.get_lines():
                xdata = line.get_xdata()
                if len(xdata) > 0:
                    # Assume x-axis is time data
                    line_latest = max(xdata)
                    if latest_time is None or line_latest > latest_time:
                        latest_time = line_latest
                        
            if latest_time is not None:
                # Calculate time range (hours in matplotlib date units)
                hours_in_days = hours / 24.0
                start_time = latest_time - hours_in_days
                
                ax.set_xlim([start_time, latest_time])
                self.canvas.draw()
                
        except Exception as e:
            print(f"Error zooming to time range: {e}")

    def _handle_zoom(self, event):
        """Handle mouse wheel zoom"""
        if event.inaxes is None:
            return

        ax = event.inaxes
        scale_factor = 1.1 if event.button == 'up' else 0.9

        # Get current limits and mouse position
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata

        if xdata is None or ydata is None:
            return

        # Calculate new limits
        x_range = (xlim[1] - xlim[0]) * scale_factor
        y_range = (ylim[1] - ylim[0]) * scale_factor

        # Center zoom on mouse position
        new_xlim = [xdata - x_range / 2, xdata + x_range / 2]
        new_ylim = [ydata - y_range / 2, ydata + y_range / 2]

        # Set new limits
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)

        # Redraw
        self.canvas.draw()

    def _handle_button_press(self, event):
        """Handle button press events"""
        if event.inaxes is None:
            return

        # Double-click to reset view
        if event.dblclick:
            self.reset_view()
            return

        # Start pan operation on left mouse button
        if event.button == 1:  # Left mouse button
            self.press = (event.xdata, event.ydata)
            self.current_ax = event.inaxes

    def _handle_button_release(self, event):
        """Handle button release events"""
        self.press = None
        self.current_ax = None
        self.canvas.draw()

    def _handle_motion(self, event):
        """Handle mouse motion for panning and tooltips"""
        if event.inaxes is None:
            return

        # Handle panning
        if self.press is not None and event.button == 1:
            ax = self.current_ax
            if ax is None:
                return

            # Calculate movement
            dx = event.xdata - self.press[0]
            dy = event.ydata - self.press[1]

            # Get current limits
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            # Apply pan
            ax.set_xlim([xlim[0] - dx, xlim[1] - dx])
            ax.set_ylim([ylim[0] - dy, ylim[1] - dy])

            self.canvas.draw_idle()

        # Handle tooltips
        else:
            self._update_tooltip(event)

    def _update_tooltip(self, event):
        """Update tooltip showing data values"""
        # Implementation for tooltips could be added here
        pass

    def reset_view(self):
        """Reset all axes to initial view"""
        for i, ax in enumerate(self.ax):
            if i < len(self.initial_views):
                ax.set_xlim(self.initial_views[i]['xlim'])
                ax.set_ylim(self.initial_views[i]['ylim'])
        self.canvas.draw()


class PlotUtils:
    """Enhanced plotting utilities for LINAC water system data"""

    @staticmethod
    def setup_professional_style():
        """Setup professional plotting style with Calibri font"""
        try:
            # Set professional font
            plt.rcParams['font.family'] = ['Calibri', 'DejaVu Sans', 'sans-serif']
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.labelsize'] = 11
            plt.rcParams['axes.titlesize'] = 12
            plt.rcParams['xtick.labelsize'] = 9
            plt.rcParams['ytick.labelsize'] = 9
            plt.rcParams['legend.fontsize'] = 9
            
            # Set colors and styling
            plt.rcParams['axes.grid'] = True
            plt.rcParams['grid.alpha'] = 0.3
            plt.rcParams['axes.spines.top'] = False
            plt.rcParams['axes.spines.right'] = False
            plt.rcParams['figure.facecolor'] = 'white'
            
        except Exception as e:
            print(f"Style setup warning: {e}")

    @staticmethod
    def group_parameters(parameters):
        """Group parameters by type for better visualization"""
        parameter_groups = {
            'Temperature': [],
            'Pressure': [],
            'Flow': [],
            'Level': [],
            'Voltage': [],
            'Current': [],
            'Humidity': [],
            'Position': [],
            'Other': []
        }
        
        for param in parameters:
            param_lower = param.lower()
            if any(temp_keyword in param_lower for temp_keyword in ['temp', 'temperature', '°c', 'celsius', '°f']):
                parameter_groups['Temperature'].append(param)
            elif any(pres_keyword in param_lower for pres_keyword in ['press', 'pressure', 'psi', 'bar', 'mbar', 'pa']):
                parameter_groups['Pressure'].append(param)
            elif any(flow_keyword in param_lower for flow_keyword in ['flow', 'rate', 'gpm', 'lpm', 'l/min']):
                parameter_groups['Flow'].append(param)
            elif any(level_keyword in param_lower for level_keyword in ['level', 'height', 'depth', 'tank']):
                parameter_groups['Level'].append(param)
            elif any(volt_keyword in param_lower for volt_keyword in ['volt', 'voltage', 'v', 'kv']):
                parameter_groups['Voltage'].append(param)
            elif any(curr_keyword in param_lower for curr_keyword in ['current', 'amp', 'ampere', 'ma']):
                parameter_groups['Current'].append(param)
            elif any(humid_keyword in param_lower for humid_keyword in ['humid', 'humidity', '%rh', 'moisture']):
                parameter_groups['Humidity'].append(param)
            elif any(pos_keyword in param_lower for pos_keyword in ['pos', 'position', 'x', 'y', 'z', 'angle']):
                parameter_groups['Position'].append(param)
            else:
                parameter_groups['Other'].append(param)

        # Remove empty groups
        return {k: v for k, v in parameter_groups.items() if v}

    @staticmethod
    def get_group_colors():
        """Get consistent colors for parameter groups"""
        return {
            'Temperature': '#FF6B6B',  # Red
            'Pressure': '#4ECDC4',     # Teal
            'Flow': '#45B7D1',         # Blue
            'Level': '#96CEB4',        # Green
            'Voltage': '#FECA57',      # Yellow
            'Current': '#FF9FF3',      # Pink
            'Humidity': '#54A0FF',     # Light Blue
            'Position': '#5F27CD',     # Purple
            'Other': '#636E72'         # Gray
        }

    @staticmethod
    def find_time_clusters(df_times, gap_threshold=timedelta(days=1)):
        """Find clusters of data based on time gaps"""
        if len(df_times) == 0:
            return []
        
        df_times_sorted = sorted(df_times)
        clusters = []
        current_cluster = [df_times_sorted[0]]
        
        for i in range(1, len(df_times_sorted)):
            if df_times_sorted[i] - df_times_sorted[i-1] <= gap_threshold:
                current_cluster.append(df_times_sorted[i])
            else:
                clusters.append(current_cluster)
                current_cluster = [df_times_sorted[i]]
        
        clusters.append(current_cluster)
        return clusters

    @staticmethod
    def _plot_parameter_data_single(widget, data, parameter_name):
        """Plot single parameter data with compressed timeline for distant dates"""
        if hasattr(widget, 'figure') and widget.figure:
            widget.figure.clear()
            ax = widget.figure.add_subplot(111)
            
            # Apply professional styling
            PlotUtils.setup_professional_style()
            
            if data.empty:
                ax.text(0.5, 0.5, f'No data available for {parameter_name}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                widget.canvas.draw()
                return

            # Process time data
            if 'datetime' in data.columns:
                data_copy = data.copy()
                data_copy['datetime'] = pd.to_datetime(data_copy['datetime'])
                data_copy = data_copy.sort_values('datetime')
                
                # Find time clusters for compressed timeline
                time_clusters = PlotUtils.find_time_clusters(data_copy['datetime'].tolist())
                
                if len(time_clusters) > 1:
                    PlotUtils._plot_single_parameter_compressed(ax, data_copy, parameter_name, time_clusters)
                else:
                    PlotUtils._plot_single_parameter_continuous(ax, data_copy, parameter_name)
            
            # Enhanced title with data range and point count information
            title = f"{parameter_name} Trends"
            if not data_copy.empty:
                data_range_start = data_copy['datetime'].min().strftime('%b %d')
                data_range_end = data_copy['datetime'].max().strftime('%b %d')
                point_count = len(data_copy)
                
                # Add data context to title without making it too long
                if data_range_start == data_range_end:
                    title += f" ({data_range_start})"
                else:
                    title += f" ({data_range_start} - {data_range_end})"
                
                # Add point count as subtitle if there's enough space
                subtitle = f"Based on {point_count:,} measurements"
                ax.text(0.5, 0.95, subtitle, ha='center', va='top', 
                       transform=ax.transAxes, fontsize=10, style='italic', alpha=0.7)
            
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            widget.figure.tight_layout()
            
            # Add interactive capabilities if canvas exists
            if hasattr(widget, 'canvas'):
                widget.canvas.draw()

    @staticmethod
    def _plot_parameter_data_multi_machine(widget, machine_data_dict, parameter_name, machine_colors):
        """Plot multi-machine parameter data with different colors per machine"""
        if hasattr(widget, 'figure') and widget.figure:
            widget.figure.clear()
            ax = widget.figure.add_subplot(111)
            
            # Apply professional styling
            PlotUtils.setup_professional_style()
            
            if not machine_data_dict:
                ax.text(0.5, 0.5, f'No data available for {parameter_name}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                widget.canvas.draw()
                return

            plotted_count = 0
            machine_periods = {}  # Track data periods for each machine
            
            for machine_id, data in machine_data_dict.items():
                if data.empty:
                    continue
                    
                # Process time data
                if 'datetime' in data.columns:
                    data_copy = data.copy()
                    data_copy['datetime'] = pd.to_datetime(data_copy['datetime'])
                    data_copy = data_copy.sort_values('datetime')
                    
                    # Track data period for this machine
                    start_date = data_copy['datetime'].min()
                    end_date = data_copy['datetime'].max()
                    machine_periods[machine_id] = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"
                    
                    color = machine_colors.get(machine_id, '#1976D2')
                    
                    # Plot average values for multi-machine view
                    if 'value' in data_copy.columns:
                        avg_data = data_copy.groupby(['datetime'])['value'].mean().reset_index()
                        # Enhanced label with period info for non-overlapping data
                        label = f'{machine_id} ({machine_periods[machine_id]})'
                        ax.plot(avg_data['datetime'], avg_data['value'], 
                               label=label, color=color, linewidth=2, marker='o', markersize=4)
                        plotted_count += 1
            
            if plotted_count > 0:
                # Smart title based on data overlap
                title = f"{parameter_name} Trends - Machine Comparison"
                if len(machine_periods) > 1:
                    # Check if periods overlap or are separate
                    periods_list = list(machine_periods.values())
                    if len(set(periods_list)) == len(periods_list):
                        title += " (Different Periods)"
                    else:
                        title += " (Overlapping Data)"
                
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xlabel('Time')
                ax.set_ylabel('Value')
                ax.grid(True, alpha=0.3)
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                
                # Format datetime axis
                if plotted_count > 0:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
                    widget.figure.autofmt_xdate()
            else:
                ax.text(0.5, 0.5, f'No data available for {parameter_name}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
            
            widget.figure.tight_layout()
            
            # Add interactive capabilities if canvas exists
            if hasattr(widget, 'canvas'):
                widget.canvas.draw()

    @staticmethod
    def _plot_single_parameter_compressed(ax, data, parameter_name, time_clusters):
        """Plot single parameter with compressed timeline"""
        colors = {'avg': '#1976D2', 'min': '#388E3C', 'max': '#D32F2F'}
        
        x_positions = []
        labels = []
        
        for i, cluster in enumerate(time_clusters):
            cluster_data = data[data['datetime'].isin(cluster)]
            
            # Create compressed x-positions
            cluster_start = i * 10  # Space clusters apart
            cluster_positions = np.linspace(cluster_start, cluster_start + 8, len(cluster_data))
            x_positions.extend(cluster_positions)
            
            # Plot data for this cluster
            for stat in ['avg', 'min', 'max']:
                if stat in cluster_data.columns:
                    values = cluster_data[stat].dropna()
                    if not values.empty:
                        positions = cluster_positions[:len(values)]
                        ax.plot(positions, values, marker='o', markersize=3, 
                               label=stat.upper() if i == 0 else "", 
                               color=colors.get(stat, '#666666'), 
                               linewidth=2, alpha=0.8)
            
            # Add cluster label
            cluster_start_date = min(cluster).strftime('%m/%d')
            cluster_end_date = max(cluster).strftime('%m/%d')
            if cluster_start_date != cluster_end_date:
                labels.append(f"{cluster_start_date}-{cluster_end_date}")
            else:
                labels.append(cluster_start_date)
        
        # Customize x-axis
        if labels:
            tick_positions = [i * 10 + 4 for i in range(len(labels))]  # Center of each cluster
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(labels, rotation=45)
        
        ax.legend()

    @staticmethod
    def _plot_single_parameter_continuous(ax, data, parameter_name):
        """Plot single parameter with continuous timeline"""
        colors = {'avg': '#1976D2', 'min': '#388E3C', 'max': '#D32F2F'}
        
        for stat in ['avg', 'min', 'max']:
            if stat in data.columns:
                values = data[stat].dropna()
                if not values.empty:
                    times = data.loc[values.index, 'datetime']
                    ax.plot(times, values, marker='o', markersize=3, 
                           label=stat.upper(), 
                           color=colors.get(stat, '#666666'), 
                           linewidth=2, alpha=0.8)
        
        # Format x-axis for continuous timeline
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.figure.autofmt_xdate()
        ax.legend()

    @staticmethod
    def interpolate_data(data: pd.DataFrame, method: str = 'linear') -> pd.DataFrame:
        """
        Interpolate missing data points in time series data
        
        Args:
            data: DataFrame with datetime column and parameter values
            method: Interpolation method ('linear', 'cubic', 'quadratic')
        
        Returns:
            DataFrame with interpolated data
        """
        try:
            if data.empty or 'datetime' not in data.columns:
                return data
            
            data_copy = data.copy()
            data_copy = data_copy.sort_values('datetime').reset_index(drop=True)
            
            # Interpolate numeric columns
            numeric_columns = data_copy.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if col in ['avg', 'min', 'max']:
                    # Use pandas interpolate method
                    data_copy[col] = data_copy[col].interpolate(method=method)
            
            return data_copy
            
        except Exception as e:
            print(f"Error in data interpolation: {e}")
            return data

    @staticmethod
    def smooth_data(data: pd.DataFrame, window_size: int = 5, method: str = 'rolling') -> pd.DataFrame:
        """
        Apply data smoothing to reduce noise and improve visual appearance
        
        Args:
            data: DataFrame with parameter values
            window_size: Size of the smoothing window
            method: Smoothing method ('rolling', 'ewm', 'savgol')
        
        Returns:
            DataFrame with smoothed data
        """
        try:
            if data.empty:
                return data
            
            data_copy = data.copy()
            numeric_columns = data_copy.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col in ['avg', 'min', 'max']:
                    if method == 'rolling':
                        # Rolling average
                        data_copy[col] = data_copy[col].rolling(window=window_size, center=True).mean()
                    elif method == 'ewm':
                        # Exponentially weighted moving average
                        data_copy[col] = data_copy[col].ewm(span=window_size).mean()
                    elif method == 'savgol' and window_size >= 3:
                        # Savitzky-Golay filter (requires scipy)
                        try:
                            from scipy.signal import savgol_filter
                            # Ensure window size is odd and >= 3
                            if window_size % 2 == 0:
                                window_size += 1
                            data_copy[col] = savgol_filter(data_copy[col].dropna(), window_size, 2)
                        except ImportError:
                            # Fallback to rolling average if scipy not available
                            data_copy[col] = data_copy[col].rolling(window=window_size, center=True).mean()
            
            return data_copy
            
        except Exception as e:
            print(f"Error in data smoothing: {e}")
            return data

    @staticmethod
    def aggregate_data_by_time(data: pd.DataFrame, freq: str = 'H') -> pd.DataFrame:
        """
        Aggregate data by time periods (hourly, daily, etc.)
        
        Args:
            data: DataFrame with datetime column and parameter values
            freq: Aggregation frequency ('H' for hourly, 'D' for daily, 'T' for minute)
        
        Returns:
            DataFrame with aggregated data including min, max, avg for each period
        """
        try:
            if data.empty or 'datetime' not in data.columns:
                return data
            
            data_copy = data.copy()
            data_copy['datetime'] = pd.to_datetime(data_copy['datetime'])
            data_copy.set_index('datetime', inplace=True)
            
            # Aggregate numeric columns
            numeric_columns = data_copy.select_dtypes(include=[np.number]).columns
            agg_dict = {}
            
            for col in numeric_columns:
                if col in ['avg', 'min', 'max']:
                    agg_dict[col] = ['min', 'max', 'mean']
            
            if agg_dict:
                aggregated = data_copy.resample(freq).agg(agg_dict)
                
                # Flatten column names
                aggregated.columns = ['_'.join(col).strip() for col in aggregated.columns]
                aggregated.reset_index(inplace=True)
                
                return aggregated
            
            return data_copy.reset_index()
            
        except Exception as e:
            print(f"Error in data aggregation: {e}")
            return data

    @staticmethod
    def calculate_statistics(data: pd.DataFrame, time_range: str = None) -> dict:
        """
        Calculate statistical summary for the visible data
        
        Args:
            data: DataFrame with parameter values
            time_range: Optional time range filter ('1H', '1D', '1W')
        
        Returns:
            Dictionary with statistical summary
        """
        try:
            if data.empty:
                return {}
            
            data_copy = data.copy()
            
            # Filter by time range if specified
            if time_range and 'datetime' in data_copy.columns:
                data_copy['datetime'] = pd.to_datetime(data_copy['datetime'])
                cutoff_time = data_copy['datetime'].max() - pd.Timedelta(time_range)
                data_copy = data_copy[data_copy['datetime'] >= cutoff_time]
            
            stats = {}
            numeric_columns = data_copy.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col in ['avg', 'min', 'max']:
                    values = data_copy[col].dropna()
                    if not values.empty:
                        stats[col] = {
                            'min': float(values.min()),
                            'max': float(values.max()),
                            'mean': float(values.mean()),
                            'std': float(values.std()) if len(values) > 1 else 0.0,
                            'count': len(values)
                        }
            
            return stats
            
        except Exception as e:
            print(f"Error in statistics calculation: {e}")
            return {}

    @staticmethod
    def synchronize_time_axes(ax_list: list, data_list: list) -> None:
        """
        Synchronize time axes across multiple subplots for multi-machine comparison
        
        Args:
            ax_list: List of matplotlib axes
            data_list: List of DataFrames corresponding to each axis
        """
        try:
            if not ax_list or not data_list:
                return
            
            # Find common time range across all datasets
            min_time = None
            max_time = None
            
            for data in data_list:
                if not data.empty and 'datetime' in data.columns:
                    data_times = pd.to_datetime(data['datetime'])
                    data_min = data_times.min()
                    data_max = data_times.max()
                    
                    if min_time is None or data_min < min_time:
                        min_time = data_min
                    if max_time is None or data_max > max_time:
                        max_time = data_max
            
            # Apply common time range to all axes
            if min_time is not None and max_time is not None:
                for ax in ax_list:
                    ax.set_xlim(min_time, max_time)
                    
        except Exception as e:
            print(f"Error in time axis synchronization: {e}")


class EnhancedPlotWidget(QWidget):
    """Enhanced plotting widget with professional styling and LINAC data processing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = None
        self.canvas = None
        self.interactive_manager = None
        self.data = pd.DataFrame()
        self.raw_data = pd.DataFrame()
        self.current_view_mode = 'raw'  # 'raw', 'interpolated', 'smoothed', 'aggregated'
        self.current_aggregation = 'H'  # 'T' for minute, 'H' for hourly, 'D' for daily
        self.statistics_panel = None
        self.show_statistics = True
        self.init_ui()
    
    def init_ui(self):
        """Initialize plotting UI with enhanced error handling and backend verification"""
        self.layout = QVBoxLayout(self)
        self.setMinimumHeight(300)
        
        # Add control panel for view options
        self._setup_control_panel()
        
        try:
            # Ensure matplotlib backend is properly configured
            backend = matplotlib.get_backend()
            if backend.lower() != 'qt5agg':
                print(f"Warning: matplotlib backend is {backend}, expected Qt5Agg")
                matplotlib.use('Qt5Agg', force=True)
                
            # FIXED: Smaller figure size for embedded use with proper DPI
            self.figure = Figure(figsize=(8, 4), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            
            # CRITICAL: Ensure proper parent-child relationship to prevent popup windows
            self.canvas.setParent(self)
            self.canvas.setFocusPolicy(1)  # Allow focus for interactions
            self.layout.addWidget(self.canvas)
            
            # Apply professional styling
            PlotUtils.setup_professional_style()
            
            # Add statistics panel
            self._setup_statistics_panel()
            
            # Add a test plot to verify functionality
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Graph Ready', ha='center', va='center', 
                   fontsize=12, color='#666', alpha=0.7)
            self.canvas.draw()
            
        except Exception as e:
            print(f"Plot widget initialization error: {e}")
            error_label = QLabel(f"Plotting initialization failed: {str(e)}\nCheck matplotlib backend configuration.")
            error_label.setStyleSheet("color: red; padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7;")
            self.layout.addWidget(error_label)
    
    def _setup_control_panel(self):
        """Setup control panel for view options"""
        try:
            control_frame = QFrame()
            control_frame.setMaximumHeight(50)
            control_layout = QHBoxLayout(control_frame)
            control_layout.setContentsMargins(5, 5, 5, 5)
            
            # View mode controls
            view_label = QLabel("View:")
            control_layout.addWidget(view_label)
            
            self.view_combo = QComboBox()
            self.view_combo.addItems(['Raw Data', 'Interpolated', 'Smoothed', 'Aggregated'])
            self.view_combo.currentTextChanged.connect(self._on_view_mode_changed)
            control_layout.addWidget(self.view_combo)
            
            control_layout.addWidget(QLabel("|"))
            
            # Aggregation controls
            agg_label = QLabel("Period:")
            control_layout.addWidget(agg_label)
            
            self.agg_combo = QComboBox()
            self.agg_combo.addItems(['Minute', 'Hourly', 'Daily'])
            self.agg_combo.setCurrentText('Hourly')
            self.agg_combo.currentTextChanged.connect(self._on_aggregation_changed)
            self.agg_combo.setEnabled(False)  # Initially disabled
            control_layout.addWidget(self.agg_combo)
            
            control_layout.addWidget(QLabel("|"))
            
            # Statistics toggle
            self.stats_checkbox = QCheckBox("Show Statistics")
            self.stats_checkbox.setChecked(True)
            self.stats_checkbox.toggled.connect(self._on_statistics_toggled)
            control_layout.addWidget(self.stats_checkbox)
            
            control_layout.addStretch()
            
            self.layout.addWidget(control_frame)
            
        except Exception as e:
            print(f"Error setting up control panel: {e}")
    
    def _setup_statistics_panel(self):
        """Setup statistics panel"""
        try:
            self.statistics_panel = QLabel()
            self.statistics_panel.setMaximumHeight(30)
            self.statistics_panel.setStyleSheet(
                "background-color: #f8f9fa; border: 1px solid #dee2e6; "
                "padding: 5px; font-size: 10px; color: #495057;"
            )
            self.statistics_panel.setText("Statistics will appear here when data is plotted")
            self.layout.addWidget(self.statistics_panel)
            
        except Exception as e:
            print(f"Error setting up statistics panel: {e}")
    
    def _on_view_mode_changed(self, view_text):
        """Handle view mode change"""
        mode_map = {
            'Raw Data': 'raw',
            'Interpolated': 'interpolated', 
            'Smoothed': 'smoothed',
            'Aggregated': 'aggregated'
        }
        
        self.current_view_mode = mode_map.get(view_text, 'raw')
        
        # Enable/disable aggregation combo based on view mode
        if hasattr(self, 'agg_combo'):
            self.agg_combo.setEnabled(self.current_view_mode == 'aggregated')
        
        # Re-plot with new view mode if data exists
        if not self.raw_data.empty:
            self._replot_with_current_settings()
    
    def _on_aggregation_changed(self, agg_text):
        """Handle aggregation period change"""
        agg_map = {
            'Minute': 'T',
            'Hourly': 'H',
            'Daily': 'D'
        }
        
        self.current_aggregation = agg_map.get(agg_text, 'H')
        
        # Re-plot with new aggregation if in aggregated mode
        if self.current_view_mode == 'aggregated' and not self.raw_data.empty:
            self._replot_with_current_settings()
    
    def _on_statistics_toggled(self, checked):
        """Handle statistics panel toggle"""
        self.show_statistics = checked
        if hasattr(self, 'statistics_panel'):
            self.statistics_panel.setVisible(checked)
    
    def _replot_with_current_settings(self):
        """Re-plot data with current view settings"""
        # This will be implemented to re-plot using the current view mode and settings
        # For now, just update statistics
        self._update_statistics_panel()
    
    def _update_statistics_panel(self):
        """Update the statistics panel with current data statistics"""
        try:
            if not self.show_statistics or not hasattr(self, 'statistics_panel'):
                return
            
            if self.data.empty:
                self.statistics_panel.setText("No data available")
                return
            
            stats = PlotUtils.calculate_statistics(self.data)
            if stats:
                stats_text = []
                for param, stat_info in stats.items():
                    stats_text.append(
                        f"{param.upper()}: Min={stat_info['min']:.2f}, "
                        f"Max={stat_info['max']:.2f}, Avg={stat_info['mean']:.2f} "
                        f"(n={stat_info['count']})"
                    )
                self.statistics_panel.setText(" | ".join(stats_text))
            else:
                self.statistics_panel.setText("No statistics available")
                
        except Exception as e:
            print(f"Error updating statistics panel: {e}")
    
    def set_data(self, data: pd.DataFrame):
        """Set data for the plot widget"""
        self.raw_data = data.copy() if not data.empty else pd.DataFrame()
        self._process_data_for_current_view()
        self._update_statistics_panel()
    
    def _process_data_for_current_view(self):
        """Process raw data according to current view mode"""
        try:
            if self.raw_data.empty:
                self.data = pd.DataFrame()
                return
            
            if self.current_view_mode == 'raw':
                self.data = self.raw_data.copy()
            elif self.current_view_mode == 'interpolated':
                self.data = PlotUtils.interpolate_data(self.raw_data)
            elif self.current_view_mode == 'smoothed':
                self.data = PlotUtils.smooth_data(self.raw_data, window_size=5)
            elif self.current_view_mode == 'aggregated':
                self.data = PlotUtils.aggregate_data_by_time(self.raw_data, self.current_aggregation)
            
        except Exception as e:
            print(f"Error processing data for view mode {self.current_view_mode}: {e}")
            self.data = self.raw_data.copy()
    
    def plot_multi_machine_parameter(self, data_dict: Dict[str, pd.DataFrame], parameter: str, colors: Dict[str, str]):
        """Plot multi-machine parameter data with different colors per machine
        
        Args:
            data_dict: Dictionary mapping machine IDs to their data
            parameter: Parameter name for the plot title
            colors: Dictionary mapping machine IDs to colors
        """
        try:
            if self.figure is None:
                return
                
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Apply professional styling
            PlotUtils.setup_professional_style()
            
            if not data_dict:
                ax.text(0.5, 0.5, f'No data available for {parameter}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                self.canvas.draw()
                return

            plotted_count = 0
            legend_handles = []
            legend_labels = []
            processed_data_list = []
            
            # Process each machine's data according to current view settings
            for machine_id, data in data_dict.items():
                if data.empty:
                    continue
                
                # Store raw data for processing
                self.raw_data = data.copy()
                self._process_data_for_current_view()
                processed_data = self.data.copy()
                
                if processed_data.empty:
                    continue
                    
                # Process time data
                if 'datetime' in processed_data.columns:
                    processed_data['datetime'] = pd.to_datetime(processed_data['datetime'])
                    processed_data = processed_data.sort_values('datetime')
                    processed_data_list.append(processed_data)
                    
                    color = colors.get(machine_id, '#1976D2')
                    
                    # Plot average values with enhanced styling
                    if 'avg' in processed_data.columns:
                        avg_data = processed_data.groupby(['datetime'])['avg'].mean().reset_index()
                        if not avg_data.empty:
                            # Use different line styles for different machines
                            line_style = '-' if plotted_count == 0 else '--' if plotted_count == 1 else ':'
                            line = ax.plot(avg_data['datetime'], avg_data['avg'], 
                                         color=color, linewidth=2.5, linestyle=line_style,
                                         marker='o', markersize=3, alpha=0.8, 
                                         label=f"{machine_id} (avg)")[0]
                            legend_handles.append(line)
                            legend_labels.append(f"{machine_id} (avg)")
                            plotted_count += 1
                    
                    # Optionally plot min/max ranges for aggregated view
                    if self.current_view_mode == 'aggregated':
                        if 'avg_min' in processed_data.columns and 'avg_max' in processed_data.columns:
                            min_data = processed_data.groupby(['datetime'])['avg_min'].min().reset_index()
                            max_data = processed_data.groupby(['datetime'])['avg_max'].max().reset_index()
                            if not min_data.empty and not max_data.empty:
                                ax.fill_between(min_data['datetime'], min_data['avg_min'], 
                                               max_data['avg_max'], alpha=0.2, color=color)
            
            # Synchronize time axes for multi-machine comparison
            if len(processed_data_list) > 1:
                PlotUtils.synchronize_time_axes([ax], processed_data_list)
            
            if plotted_count > 0:
                # Enhanced title with view mode information
                view_mode_text = f" ({self.current_view_mode.title()}"
                if self.current_view_mode == 'aggregated':
                    agg_text = {'T': 'Minute', 'H': 'Hourly', 'D': 'Daily'}.get(self.current_aggregation, 'Hourly')
                    view_mode_text += f", {agg_text}"
                view_mode_text += ")"
                
                ax.set_title(f"{parameter} - Multi-Machine Comparison{view_mode_text}", 
                           fontsize=12, fontweight='bold')
                ax.set_xlabel('Time', fontsize=10)
                ax.set_ylabel('Value', fontsize=10)
                ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                
                # Enhanced legend with better positioning
                if legend_handles:
                    legend = ax.legend(legend_handles, legend_labels, 
                                     bbox_to_anchor=(1.02, 1), loc='upper left',
                                     fontsize=9, frameon=True, fancybox=True, 
                                     shadow=True, framealpha=0.9)
                    legend.set_draggable(True)
                
                # Enhanced datetime formatting
                if plotted_count > 0:
                    try:
                        if self.current_aggregation == 'D':
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                        elif self.current_aggregation == 'H':
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
                        else:  # Minute
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
                        self.figure.autofmt_xdate()
                    except:
                        pass  # Fallback if date formatting fails
                
                # Update statistics panel
                if processed_data_list:
                    # Combine all processed data for statistics
                    combined_data = pd.concat(processed_data_list, ignore_index=True)
                    self.data = combined_data
                    self._update_statistics_panel()
            else:
                ax.text(0.5, 0.5, f'No valid data for {parameter}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
            
            self.figure.tight_layout()
            
            # Add interactive capabilities if canvas exists
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.draw()
                
                # Store machine visibility state for toggle functionality
                if not hasattr(self, '_machine_visibility'):
                    self._machine_visibility = {machine_id: True for machine_id in data_dict.keys()}
                    
        except Exception as e:
            print(f"Error plotting multi-machine parameter: {e}")
            if self.figure:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=12, color='red')
                self.canvas.draw()

    def plot_parameter_trends(self, data: pd.DataFrame, parameter: str, 
                            title: str = "", show_statistics: bool = True):
        """Plot parameter trends with enhanced visualization using PlotUtils"""
        try:
            if data.empty or self.figure is None:
                return
            
            # Use PlotUtils for enhanced plotting
            PlotUtils._plot_parameter_data_single(self, data, parameter)
            
            # Add interactive capabilities
            if self.canvas and self.figure:
                axes = self.figure.get_axes()
                if axes:
                    self.interactive_manager = InteractivePlotManager(
                        self.figure, axes, self.canvas
                    )
                    
        except Exception as e:
            print(f"Parameter trends plotting error: {e}")
            if self.figure:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=12, color='red')
                self.canvas.draw()

    def plot_comparison(self, data: pd.DataFrame, param1: str, param2: str):
        """Plot comparison between two parameters"""
        try:
            if data.empty or self.figure is None:
                return
            
            self.figure.clear()
            
            # Create subplots for comparison
            ax1 = self.figure.add_subplot(211)
            ax2 = self.figure.add_subplot(212)
            
            # Plot first parameter
            self._plot_single_parameter(ax1, data, param1, f"Top: {param1}")
            
            # Plot second parameter
            self._plot_single_parameter(ax2, data, param2, f"Bottom: {param2}")
            
            self.figure.tight_layout()
            self.canvas.draw()
            
            # Add interactive capabilities
            self.interactive_manager = InteractivePlotManager(
                self.figure, [ax1, ax2], self.canvas
            )
            
        except Exception as e:
            print(f"Comparison plot error: {e}")
    
    def _plot_single_parameter(self, ax, data: pd.DataFrame, parameter: str, title: str):
        """Plot single parameter on given axis"""
        try:
            # Filter for parameter
            if 'param' in data.columns:
                param_data = data[data['param'] == parameter].copy()
            else:
                param_data = data.copy()
            
            if param_data.empty:
                ax.text(0.5, 0.5, f'No data for {parameter}', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(title)
                return
            
            # Ensure datetime
            if 'datetime' in param_data.columns:
                param_data['datetime'] = pd.to_datetime(param_data['datetime'], errors='coerce')
                param_data = param_data.dropna(subset=['datetime'])
                param_data = param_data.sort_values('datetime')
            
            # Plot with professional styling
            colors = {'avg': '#1976D2', 'min': '#388E3C', 'max': '#D32F2F'}
            line_styles = {'avg': '-', 'min': '--', 'max': '--'}
            
            plotted_any = False
            
            for stat in ['avg', 'min', 'max']:
                if stat in param_data.columns and not param_data[stat].isna().all():
                    values = param_data[stat].dropna()
                    if not values.empty:
                        ax.plot(param_data.loc[values.index, 'datetime'], values,
                               marker='o', markersize=3, label=f'{stat.upper()}',
                               color=colors.get(stat, '#666666'),
                               linestyle=line_styles.get(stat, '-'),
                               linewidth=2, alpha=0.8)
                        plotted_any = True
            
            if plotted_any:
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=9)
                
                # Format dates
                if 'datetime' in param_data.columns and len(param_data) > 0:
                    date_range = param_data['datetime'].max() - param_data['datetime'].min()
                    if pd.notna(date_range):
                        if date_range.total_seconds() < 24*3600:
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                        else:
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                
                self.figure.autofmt_xdate()
            
        except Exception as e:
            print(f"Single parameter plot error: {e}")


class EnhancedDualPlotWidget(QWidget):
    """Enhanced dual plot widget with LINAC data processing capabilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = None
        self.canvas = None
        self.interactive_manager = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize dual plot UI"""
        self.layout = QVBoxLayout(self)
        self.setMinimumHeight(500)  # Taller for dual plots
        
        try:
            # Create figure with subplots
            self.figure = Figure(figsize=(10, 8), dpi=80)
            self.canvas = FigureCanvas(self.figure)
            
            # CRITICAL: Ensure proper parent-child relationship
            self.canvas.setParent(self)
            self.layout.addWidget(self.canvas)
            
            # Apply professional styling
            PlotUtils.setup_professional_style()
            
        except Exception as e:
            error_label = QLabel(f"Dual plot initialization failed: {str(e)}")
            self.layout.addWidget(error_label)
    
    def update_comparison(self, data: pd.DataFrame, top_param: str, bottom_param: str):
        """Update comparison plots with enhanced LINAC data processing"""
        try:
            if data.empty or self.figure is None:
                return
            
            self.figure.clear()
            
            # Create subplots
            ax1 = self.figure.add_subplot(211)
            ax2 = self.figure.add_subplot(212)
            
            # Use enhanced plotting for both parameters
            self._plot_enhanced_parameter(ax1, data, top_param, f"📈 {top_param}")
            self._plot_enhanced_parameter(ax2, data, bottom_param, f"📉 {bottom_param}")
            
            self.figure.tight_layout()
            self.canvas.draw()
            
            # Add interactive capabilities
            self.interactive_manager = InteractivePlotManager(
                self.figure, [ax1, ax2], self.canvas
            )
            
        except Exception as e:
            print(f"Dual plot comparison error: {e}")
    
    def _plot_enhanced_parameter(self, ax, data: pd.DataFrame, parameter: str, title: str):
        """Plot parameter with enhanced LINAC-specific processing"""
        try:
            # Filter for parameter using PlotUtils logic
            if 'param' in data.columns:
                param_data = data[data['param'] == parameter].copy()
            else:
                # Look for parameter in column names
                if parameter in data.columns:
                    param_data = data.copy()
                    param_data['value'] = data[parameter]
                else:
                    param_data = pd.DataFrame()
            
            if param_data.empty:
                ax.text(0.5, 0.5, f'No data available for {parameter}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(title, fontsize=12, fontweight='bold')
                return
            
            # Process datetime with PlotUtils methodology
            if 'datetime' in param_data.columns:
                param_data['datetime'] = pd.to_datetime(param_data['datetime'], errors='coerce')
                param_data = param_data.dropna(subset=['datetime'])
                param_data = param_data.sort_values('datetime')
                
                # Check for time gaps and use appropriate plotting method
                time_clusters = PlotUtils.find_time_clusters(param_data['datetime'].tolist())
                
                if len(time_clusters) > 1:
                    # Use compressed timeline for multiple clusters
                    self._plot_compressed_timeline(ax, param_data, parameter, time_clusters)
                else:
                    # Use continuous timeline
                    self._plot_continuous_timeline(ax, param_data, parameter)
            
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
                
        except Exception as e:
            print(f"Enhanced parameter plot error: {e}")
            ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=10, color='red')
    
    def _plot_compressed_timeline(self, ax, data, parameter, time_clusters):
        """Plot with compressed timeline for multiple date ranges"""
        colors = PlotUtils.get_group_colors()
        default_color = colors.get('Other', '#1976D2')
        
        x_positions = []
        labels = []
        
        for i, cluster in enumerate(time_clusters):
            cluster_data = data[data['datetime'].isin(cluster)]
            
            # Create compressed x-positions
            cluster_start = i * 10
            cluster_positions = np.linspace(cluster_start, cluster_start + 8, len(cluster_data))
            
            # Plot statistics
            for stat in ['avg', 'min', 'max', 'value']:
                if stat in cluster_data.columns:
                    values = cluster_data[stat].dropna()
                    if not values.empty:
                        positions = cluster_positions[:len(values)]
                        ax.plot(positions, values, marker='o', markersize=3, 
                               label=stat.upper() if i == 0 else "", 
                               color=default_color, linewidth=2, alpha=0.8)
                        break  # Use first available statistic
            
            # Add cluster label
            cluster_start_date = min(cluster).strftime('%m/%d')
            cluster_end_date = max(cluster).strftime('%m/%d')
            if cluster_start_date != cluster_end_date:
                labels.append(f"{cluster_start_date}-{cluster_end_date}")
            else:
                labels.append(cluster_start_date)
        
        # Customize x-axis
        if labels:
            tick_positions = [i * 10 + 4 for i in range(len(labels))]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(labels, rotation=45)
        
        if ax.get_legend_handles_labels()[0]:  # Only show legend if there are labels
            ax.legend(fontsize=9)
    
    def _plot_continuous_timeline(self, ax, data, parameter):
        """Plot with continuous timeline for single date range"""
        colors = {'avg': '#1976D2', 'min': '#388E3C', 'max': '#D32F2F', 'value': '#1976D2'}
        
        plotted = False
        for stat in ['avg', 'min', 'max', 'value']:
            if stat in data.columns:
                values = data[stat].dropna()
                if not values.empty:
                    times = data.loc[values.index, 'datetime']
                    ax.plot(times, values, marker='o', markersize=3, 
                           label=stat.upper(),
                           color=colors.get(stat, '#1976D2'), 
                           linewidth=2, alpha=0.8)
                    plotted = True
        
        if plotted:
            ax.legend(fontsize=9)
            
            # Format x-axis for continuous timeline
            date_range = data['datetime'].max() - data['datetime'].min()
            if pd.notna(date_range):
                if date_range.total_seconds() < 24*3600:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                else:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            
            # Y-axis label
            unit = data['unit'].iloc[0] if 'unit' in data.columns and not data.empty else ''
            ax.set_ylabel(f"Value ({unit})" if unit else "Value", fontsize=10)


class MachineComparisonWidget(QWidget):
    """Machine comparison widget with dual-pane comparison and synchronized plotting"""
    
    def __init__(self, machine_manager, parent=None):
        super().__init__(parent)
        self.machine_manager = machine_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the machine comparison UI"""
        layout = QVBoxLayout(self)
        
        # Machine selection panel
        selection_panel = self.create_machine_selection_panel()
        layout.addWidget(selection_panel)
        
        # Comparison content (splitter with two panes)
        self.comparison_splitter = QSplitter(Qt.Horizontal)
        
        # Left pane - Machine A
        self.machine_a_widget = self.create_machine_pane("Machine A")
        self.comparison_splitter.addWidget(self.machine_a_widget)
        
        # Right pane - Machine B  
        self.machine_b_widget = self.create_machine_pane("Machine B")
        self.comparison_splitter.addWidget(self.machine_b_widget)
        
        layout.addWidget(self.comparison_splitter)
        
        # Statistics comparison table
        self.stats_table = self.create_comparison_table()
        layout.addWidget(self.stats_table)
        
    def create_machine_selection_panel(self):
        """Create the machine selection panel"""
        panel = QGroupBox("Machine Selection")
        layout = QHBoxLayout(panel)
        
        # Machine A selector
        layout.addWidget(QLabel("Machine A:"))
        self.machine_a_combo = QComboBox()
        self.machine_a_combo.currentTextChanged.connect(self.on_machine_selection_changed)
        layout.addWidget(self.machine_a_combo)
        
        # Machine B selector
        layout.addWidget(QLabel("Machine B:"))
        self.machine_b_combo = QComboBox()
        self.machine_b_combo.currentTextChanged.connect(self.on_machine_selection_changed)
        layout.addWidget(self.machine_b_combo)
        
        # Parameter selector
        layout.addWidget(QLabel("Parameter:"))
        self.parameter_combo = QComboBox()
        self.parameter_combo.currentTextChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.parameter_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Comparison")
        refresh_btn.clicked.connect(self.refresh_comparison)
        layout.addWidget(refresh_btn)
        
        # Populate combos
        self.populate_machine_combos()
        self.populate_parameter_combo()
        
        return panel
    
    def create_machine_pane(self, title: str):
        """Create a machine comparison pane"""
        pane = QGroupBox(title)
        layout = QVBoxLayout(pane)
        
        # Plot widget for this machine
        plot_widget = EnhancedPlotWidget()
        layout.addWidget(plot_widget)
        
        return pane
    
    def create_comparison_table(self):
        """Create the statistical comparison table"""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Statistic", "Machine A", "Machine B"])
        
        # Set table properties
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setMaximumHeight(200)
        
        return table
    
    def populate_machine_combos(self):
        """Populate machine selection combo boxes"""
        if not self.machine_manager:
            return
            
        machines = self.machine_manager.get_available_machines()
        
        self.machine_a_combo.clear()
        self.machine_b_combo.clear()
        
        self.machine_a_combo.addItem("Select Machine A...")
        self.machine_b_combo.addItem("Select Machine B...")
        
        for machine in machines:
            self.machine_a_combo.addItem(machine)
            self.machine_b_combo.addItem(machine)
    
    def populate_parameter_combo(self):
        """Populate parameter selection combo box"""
        # This would be populated based on available parameters in the data
        self.parameter_combo.clear()
        self.parameter_combo.addItem("Select Parameter...")
        
        # Add common parameters (this could be made dynamic)
        parameters = [
            "magnetronFlow", "magnetronTemp", "targetAndCirculatorFlow",
            "FanremoteTempStatistics", "FanhumidityStatistics",
            "MLC_ADC_CHAN_TEMP_BANKA_STAT_24V", "MLC_ADC_CHAN_TEMP_BANKB_STAT_24V"
        ]
        
        for param in parameters:
            self.parameter_combo.addItem(param)
    
    def on_machine_selection_changed(self):
        """Handle machine selection changes"""
        self.refresh_comparison()
    
    def on_parameter_changed(self):
        """Handle parameter selection changes"""
        self.refresh_comparison()
    
    def refresh_comparison(self):
        """Refresh the machine comparison display"""
        try:
            machine_a = self.machine_a_combo.currentText()
            machine_b = self.machine_b_combo.currentText()
            parameter = self.parameter_combo.currentText()
            
            if (machine_a == "Select Machine A..." or 
                machine_b == "Select Machine B..." or
                parameter == "Select Parameter..." or
                not self.machine_manager):
                return
            
            # Get comparison data
            comparison_data = self.machine_manager.get_machine_comparison_data(
                machine_a, machine_b, parameter
            )
            
            # Update plots
            self.update_machine_plots(comparison_data)
            
            # Update statistics table
            self.update_statistics_table(comparison_data)
            
        except Exception as e:
            print(f"Error refreshing comparison: {e}")
    
    def update_machine_plots(self, comparison_data: dict):
        """Update the plots for both machines"""
        try:
            # Get plot widgets from the panes
            machine_a_plot = self.machine_a_widget.findChild(EnhancedPlotWidget)
            machine_b_plot = self.machine_b_widget.findChild(EnhancedPlotWidget)
            
            if machine_a_plot and not comparison_data['machine1']['data'].empty:
                machine_a_plot.plot_parameter_trends(
                    comparison_data['machine1']['data'],
                    comparison_data['parameter'],
                    f"Machine A: {comparison_data['machine1']['id']}"
                )
            
            if machine_b_plot and not comparison_data['machine2']['data'].empty:
                machine_b_plot.plot_parameter_trends(
                    comparison_data['machine2']['data'],
                    comparison_data['parameter'],
                    f"Machine B: {comparison_data['machine2']['id']}"
                )
                
        except Exception as e:
            print(f"Error updating machine plots: {e}")
    
    def update_statistics_table(self, comparison_data: dict):
        """Update the statistical comparison table"""
        try:
            # Clear existing data
            self.stats_table.setRowCount(0)
            
            machine1_stats = comparison_data['machine1'].get('stats', {})
            machine2_stats = comparison_data['machine2'].get('stats', {})
            
            if not machine1_stats or not machine2_stats:
                return
            
            # Statistics to display
            stats_to_show = [
                ('Mean', 'mean'),
                ('Std Dev', 'std'),
                ('Minimum', 'min'),
                ('Maximum', 'max'),
                ('Count', 'count')
            ]
            
            self.stats_table.setRowCount(len(stats_to_show))
            
            for row, (stat_name, stat_key) in enumerate(stats_to_show):
                # Statistic name
                self.stats_table.setItem(row, 0, QTableWidgetItem(stat_name))
                
                # Machine A value
                value_a = machine1_stats.get(stat_key, 'N/A')
                if isinstance(value_a, (int, float)):
                    value_a = f"{value_a:.2f}"
                self.stats_table.setItem(row, 1, QTableWidgetItem(str(value_a)))
                
                # Machine B value
                value_b = machine2_stats.get(stat_key, 'N/A')
                if isinstance(value_b, (int, float)):
                    value_b = f"{value_b:.2f}"
                self.stats_table.setItem(row, 2, QTableWidgetItem(str(value_b)))
            
            # Add correlation if available
            if 'correlation' in comparison_data and comparison_data['correlation'] is not None:
                row_count = self.stats_table.rowCount()
                self.stats_table.setRowCount(row_count + 1)
                self.stats_table.setItem(row_count, 0, QTableWidgetItem("Correlation"))
                corr_text = f"{comparison_data['correlation']:.3f}"
                self.stats_table.setItem(row_count, 1, QTableWidgetItem(corr_text))
                self.stats_table.setItem(row_count, 2, QTableWidgetItem(corr_text))
                
        except Exception as e:
            print(f"Error updating statistics table: {e}")


class MultiMachineDashboardWidget(QWidget):
    """Multi-machine dashboard with status indicators and real-time monitoring"""
    
    def __init__(self, machine_manager, parent=None):
        super().__init__(parent)
        self.machine_manager = machine_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the multi-machine dashboard UI"""
        layout = QVBoxLayout(self)
        
        # Machine status grid
        status_group = QGroupBox("Machine Status")
        self.status_layout = QVBoxLayout(status_group)
        self.machine_status_widgets = {}
        layout.addWidget(status_group)
        
        # Real-time parameter comparison charts
        charts_group = QGroupBox("Parameter Comparison")
        charts_layout = QHBoxLayout(charts_group)
        
        self.comparison_plot = EnhancedPlotWidget()
        charts_layout.addWidget(self.comparison_plot)
        layout.addWidget(charts_group)
        
        # Alert panel
        alerts_group = QGroupBox("Machine Alerts")
        self.alerts_layout = QVBoxLayout(alerts_group)
        layout.addWidget(alerts_group)
        
        # Performance ranking table
        ranking_group = QGroupBox("Performance Ranking")
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(5)
        self.ranking_table.setHorizontalHeaderLabels([
            "Rank", "Machine", "Status", "Records", "Score"
        ])
        self.ranking_table.horizontalHeader().setStretchLastSection(True)
        ranking_layout = QVBoxLayout(ranking_group)
        ranking_layout.addWidget(self.ranking_table)
        layout.addWidget(ranking_group)
        
        # Initialize dashboard
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh all dashboard components"""
        try:
            if not self.machine_manager:
                return
                
            # Get multi-machine stats
            stats = self.machine_manager.get_multi_machine_stats()
            
            # Update machine status indicators
            self.update_machine_status(stats.get('machines', {}))
            
            # Update performance ranking
            self.update_performance_ranking(stats.get('machines', {}))
            
            # Update alerts (placeholder for now)
            self.update_alerts(stats.get('machines', {}))
            
            # Update comparison chart with available data
            self.update_comparison_chart(stats.get('machines', {}))
            
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
    
    def update_machine_status(self, machines: Dict):
        """Update machine status indicators"""
        try:
            # Clear existing status widgets
            for widget in self.machine_status_widgets.values():
                widget.setParent(None)
            self.machine_status_widgets.clear()
            
            # Create status indicators for each machine
            for machine_id, machine_data in machines.items():
                status_widget = self.create_machine_status_indicator(machine_id, machine_data)
                self.status_layout.addWidget(status_widget)
                self.machine_status_widgets[machine_id] = status_widget
                
        except Exception as e:
            print(f"Error updating machine status: {e}")
    
    def create_machine_status_indicator(self, machine_id: str, machine_data: Dict):
        """Create a status indicator widget for a machine"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Status indicator (colored circle)
        status = machine_data.get('status', 'unknown')
        color = machine_data.get('color', '#808080')
        
        status_colors = {
            'active': '#4CAF50',    # Green
            'limited': '#FF9800',   # Orange  
            'inactive': '#F44336',  # Red
            'unknown': '#808080'    # Gray
        }
        
        indicator_color = status_colors.get(status, '#808080')
        
        status_label = QLabel("●")
        status_label.setStyleSheet(f"color: {indicator_color}; font-size: 16px; font-weight: bold;")
        layout.addWidget(status_label)
        
        # Machine name
        name_label = QLabel(machine_id)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)
        
        # Record count
        record_count = machine_data.get('record_count', 0)
        count_label = QLabel(f"{record_count:,} records")
        layout.addWidget(count_label)
        
        # Status text
        status_text = QLabel(status.title())
        layout.addWidget(status_text)
        
        layout.addStretch()
        
        return widget
    
    def update_performance_ranking(self, machines: Dict):
        """Update the performance ranking table"""
        try:
            # Sort machines by performance rank
            ranked_machines = sorted(machines.items(), 
                                   key=lambda x: x[1].get('performance_rank', 999))
            
            self.ranking_table.setRowCount(len(ranked_machines))
            
            for row, (machine_id, machine_data) in enumerate(ranked_machines):
                # Rank
                rank = machine_data.get('performance_rank', 'N/A')
                self.ranking_table.setItem(row, 0, QTableWidgetItem(str(rank)))
                
                # Machine name
                self.ranking_table.setItem(row, 1, QTableWidgetItem(machine_id))
                
                # Status
                status = machine_data.get('status', 'Unknown').title()
                self.ranking_table.setItem(row, 2, QTableWidgetItem(status))
                
                # Records
                records = machine_data.get('record_count', 0)
                self.ranking_table.setItem(row, 3, QTableWidgetItem(f"{records:,}"))
                
                # Score (based on record count for now)
                score = records / 1000 if records > 0 else 0
                self.ranking_table.setItem(row, 4, QTableWidgetItem(f"{score:.1f}"))
                
        except Exception as e:
            print(f"Error updating performance ranking: {e}")
    
    def update_alerts(self, machines: Dict):
        """Update the alerts panel"""
        try:
            # Clear existing alerts
            for i in reversed(range(self.alerts_layout.count())):
                self.alerts_layout.itemAt(i).widget().setParent(None)
            
            # Check for alert conditions
            alerts_found = False
            
            for machine_id, machine_data in machines.items():
                status = machine_data.get('status', 'unknown')
                
                if status == 'inactive':
                    alert = QLabel(f"⚠️ {machine_id}: No recent data")
                    alert.setStyleSheet("color: #F44336; font-weight: bold;")
                    self.alerts_layout.addWidget(alert)
                    alerts_found = True
                elif status == 'limited':
                    alert = QLabel(f"⚠️ {machine_id}: Limited parameter data")
                    alert.setStyleSheet("color: #FF9800; font-weight: bold;")
                    self.alerts_layout.addWidget(alert)
                    alerts_found = True
            
            if not alerts_found:
                no_alerts = QLabel("✅ No alerts - All systems normal")
                no_alerts.setStyleSheet("color: #4CAF50; font-weight: bold;")
                self.alerts_layout.addWidget(no_alerts)
                
        except Exception as e:
            print(f"Error updating alerts: {e}")
    
    def update_comparison_chart(self, machines: Dict):
        """Update the real-time comparison chart"""
        try:
            # This would plot a comparison of key parameters across machines
            # For now, just show a placeholder
            if self.comparison_plot and self.comparison_plot.figure:
                self.comparison_plot.figure.clear()
                ax = self.comparison_plot.figure.add_subplot(111)
                
                machine_names = list(machines.keys())
                record_counts = [machines[m].get('record_count', 0) for m in machine_names]
                colors = [machines[m].get('color', '#1976D2') for m in machine_names]
                
                if machine_names and record_counts:
                    bars = ax.bar(machine_names, record_counts, color=colors, alpha=0.7)
                    ax.set_title('Machine Data Volume Comparison', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Records Count')
                    
                    # Add value labels on bars
                    for bar, count in zip(bars, record_counts):
                        if count > 0:
                            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(record_counts)*0.01,
                                   f'{count:,}', ha='center', va='bottom', fontsize=9)
                    
                    plt.xticks(rotation=45)
                else:
                    ax.text(0.5, 0.5, 'No machine data available', 
                           ha='center', va='center', transform=ax.transAxes, fontsize=14)
                
                self.comparison_plot.figure.tight_layout()
                self.comparison_plot.canvas.draw()
                
        except Exception as e:
            print(f"Error updating comparison chart: {e}")


# Maintain backwards compatibility - alias the enhanced classes
PlotWidget = EnhancedPlotWidget
DualPlotWidget = EnhancedDualPlotWidget


# Standalone utility functions for backwards compatibility
def create_summary_chart(data: pd.DataFrame, title: str = "Parameter Summary") -> Figure:
    """Create summary chart with professional styling"""
    fig = Figure(figsize=(12, 8), dpi=100)
    
    # Apply professional styling
    PlotUtils.setup_professional_style()
    
    if data.empty:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No data available for summary', 
               ha='center', va='center', transform=ax.transAxes, fontsize=14)
        return fig
    
    # Group parameters and create multi-subplot visualization
    if 'param' in data.columns:
        unique_params = data['param'].unique()[:6]  # Limit to 6 for readability
        
        rows = min(3, len(unique_params))
        cols = min(2, (len(unique_params) + 1) // 2)
        
        for i, param in enumerate(unique_params):
            ax = fig.add_subplot(rows, cols, i + 1)
            param_data = data[data['param'] == param]
            
            # Plot using PlotUtils methodology
            if 'datetime' in param_data.columns and 'avg' in param_data.columns:
                param_data = param_data.sort_values('datetime')
                ax.plot(param_data['datetime'], param_data['avg'], 
                       marker='o', markersize=2, linewidth=1.5, alpha=0.8)
                ax.set_title(param, fontsize=10, fontweight='bold')
                ax.grid(True, alpha=0.3)
                
                # Format x-axis
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                fig.autofmt_xdate()
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    fig.tight_layout()
    
    return fig


def apply_professional_style():
    """Apply professional styling globally"""
    PlotUtils.setup_professional_style()


# Legacy function aliases for backwards compatibility with main.py
def plot_trend(widget, df: pd.DataFrame, title_suffix: str = ""):
    """Plot trend data - legacy function for backwards compatibility"""
    try:
        if hasattr(widget, 'plot_parameter_trends'):
            # Use enhanced widget functionality
            if not df.empty and 'param' in df.columns:
                # Get the first parameter for plotting
                first_param = df['param'].iloc[0]
                widget.plot_parameter_trends(df, first_param, title_suffix)
            else:
                widget.plot_parameter_trends(df, "Data", title_suffix)
        else:
            # Fallback for legacy widgets
            PlotUtils._plot_parameter_data_single(widget, df, title_suffix or "Trend")
    except Exception as e:
        print(f"Legacy plot_trend error: {e}")


def reset_plot_view(widget):
    """Reset plot view - legacy function"""
    try:
        if hasattr(widget, 'interactive_manager') and widget.interactive_manager:
            widget.interactive_manager.reset_view()
        elif hasattr(widget, 'canvas'):
            widget.canvas.draw()
    except Exception as e:
        print(f"Reset plot view error: {e}")