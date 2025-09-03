
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from typing import Optional, Dict, List


class PlotWidget(QWidget):
    """Enhanced plotting widget with professional styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = None
        self.canvas = None
        self.data = pd.DataFrame()
        self.init_ui()
    
    def init_ui(self):
        """Initialize plotting UI"""
        self.layout = QVBoxLayout(self)
        self.setMinimumHeight(300)
        
        try:
            # FIXED: Smaller figure size for embedded use
            self.figure = Figure(figsize=(8, 4), dpi=80)
            self.canvas = FigureCanvas(self.figure)
            
            # CRITICAL: Ensure proper parent-child relationship to prevent popup windows
            self.canvas.setParent(self)
            self.layout.addWidget(self.canvas)
            
            # Set professional style
            try:
                plt.style.use('seaborn-v0_8-whitegrid')
            except:
                # Fallback if seaborn style not available
                plt.style.use('default')
            
        except Exception as e:
            error_label = QLabel(f"Plotting initialization failed: {str(e)}")
            self.layout.addWidget(error_label)
    
    def plot_parameter_trends(self, data: pd.DataFrame, parameter: str, 
                            title: str = "", show_statistics: bool = True):
        """Plot parameter trends with enhanced visualization"""
        try:
            if data.empty or self.figure is None:
                return
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Filter data for parameter
            if parameter != "All" and 'param' in data.columns:
                param_data = data[data['param'] == parameter].copy()
            else:
                param_data = data.copy()
            
            if param_data.empty:
                ax.text(0.5, 0.5, f'No data available for {parameter}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                self.canvas.draw()
                return
            
            # Ensure datetime is properly formatted
            if 'datetime' in param_data.columns:
                param_data['datetime'] = pd.to_datetime(param_data['datetime'], errors='coerce')
                param_data = param_data.dropna(subset=['datetime'])
                param_data = param_data.sort_values('datetime')
            
            # Plot different statistics if available
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
            
            # Fill between min and max if both available
            if show_statistics and 'min' in param_data.columns and 'max' in param_data.columns:
                min_values = param_data['min'].dropna()
                max_values = param_data['max'].dropna()
                
                if not min_values.empty and not max_values.empty:
                    # Align indices
                    common_idx = min_values.index.intersection(max_values.index)
                    if len(common_idx) > 0:
                        ax.fill_between(
                            param_data.loc[common_idx, 'datetime'],
                            min_values.loc[common_idx],
                            max_values.loc[common_idx],
                            alpha=0.2, color='#1976D2', label='Range'
                        )
            
            if not plotted_any:
                ax.text(0.5, 0.5, 'No plottable data found', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                self.canvas.draw()
                return
            
            # Styling
            chart_title = title or f"LINAC Trends: {parameter}"
            ax.set_title(chart_title, fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel("Date/Time", fontsize=12, fontweight='bold')
            
            # Y-axis label with unit
            unit = param_data['unit'].iloc[0] if 'unit' in param_data.columns and not param_data.empty else ''
            ax.set_ylabel(f"Value ({unit})" if unit else "Value", fontsize=12, fontweight='bold')
            
            # Grid and legend
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            
            # Format x-axis
            if 'datetime' in param_data.columns and len(param_data) > 0:
                date_range = param_data['datetime'].max() - param_data['datetime'].min()
                
                if pd.notna(date_range):
                    if date_range.total_seconds() < 24*3600:  # Less than a day
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    elif date_range.total_seconds() < 7*24*3600:  # Less than a week
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                    else:
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                
                self.figure.autofmt_xdate()
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Plotting error: {e}")
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
            
            # Plot statistics
            colors = {'avg': '#1976D2', 'min': '#388E3C', 'max': '#D32F2F'}
            
            for stat in ['avg', 'min', 'max']:
                if stat in param_data.columns:
                    values = param_data[stat].dropna()
                    if not values.empty:
                        ax.plot(param_data.loc[values.index, 'datetime'], values,
                               marker='o', markersize=2, label=stat.upper(),
                               color=colors.get(stat, '#666666'), linewidth=1.5)
            
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=9)
            
            # Y-axis label
            unit = param_data['unit'].iloc[0] if 'unit' in param_data.columns and not param_data.empty else ''
            ax.set_ylabel(f"Value ({unit})" if unit else "Value", fontsize=10)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, color='red')
            ax.set_title(title)


class DualPlotWidget(QWidget):
    """Widget for dual parameter comparison plots"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = None
        self.canvas = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize dual plot UI"""
        self.layout = QVBoxLayout(self)
        self.setMinimumHeight(500)
        
        try:
            # FIXED: Better size for embedded use
            self.figure = Figure(figsize=(10, 6), dpi=80)
            self.canvas = FigureCanvas(self.figure)
            
            # CRITICAL: Ensure proper parent-child relationship
            self.canvas.setParent(self)
            self.layout.addWidget(self.canvas)
        except Exception as e:
            error_label = QLabel(f"Dual plot initialization failed: {str(e)}")
            self.layout.addWidget(error_label)
    
    def update_comparison(self, data: pd.DataFrame, top_param: str, bottom_param: str):
        """Update comparison plots"""
        try:
            if data.empty or self.figure is None:
                return
            
            self.figure.clear()
            
            # Create subplots
            ax1 = self.figure.add_subplot(211)
            ax2 = self.figure.add_subplot(212)
            
            # Plot top parameter
            self._plot_parameter_on_axis(ax1, data, top_param, f"📈 {top_param}")
            
            # Plot bottom parameter
            self._plot_parameter_on_axis(ax2, data, bottom_param, f"📉 {bottom_param}")
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Comparison update error: {e}")
    
    def _plot_parameter_on_axis(self, ax, data: pd.DataFrame, parameter: str, title: str):
        """Plot parameter data on specific axis"""
        try:
            # Filter for parameter
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
            
            # Ensure datetime
            if 'datetime' in param_data.columns:
                param_data['datetime'] = pd.to_datetime(param_data['datetime'], errors='coerce')
                param_data = param_data.dropna(subset=['datetime'])
                param_data = param_data.sort_values('datetime')
            
            # Plot with professional styling
            colors = {'avg': '#1976D2', 'min': '#388E3C', 'max': '#D32F2F'}
            
            plotted = False
            for stat in ['avg', 'min', 'max']:
                if stat in param_data.columns:
                    values = param_data[stat].dropna()
                    if not values.empty:
                        ax.plot(param_data.loc[values.index, 'datetime'], values,
                               marker='o', markersize=3, label=stat.upper(),
                               color=colors.get(stat, '#666666'), linewidth=2, alpha=0.8)
                        plotted = True
            
            # If no statistics columns, try to plot direct value
            if not plotted and 'value' in param_data.columns:
                values = param_data['value'].dropna()
                if not values.empty:
                    ax.plot(param_data.loc[values.index, 'datetime'], values,
                           marker='o', markersize=3, label='Value',
                           color='#1976D2', linewidth=2, alpha=0.8)
                    plotted = True
            
            if plotted:
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=9)
                
                # Y-axis label
                unit = param_data['unit'].iloc[0] if 'unit' in param_data.columns and not param_data.empty else ''
                ax.set_ylabel(f"Value ({unit})" if unit else "Value", fontsize=10)
                
                # Format x-axis
                if 'datetime' in param_data.columns and len(param_data) > 0:
                    date_range = param_data['datetime'].max() - param_data['datetime'].min()
                    if pd.notna(date_range):
                        if date_range.total_seconds() < 24*3600:
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                        else:
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            else:
                ax.text(0.5, 0.5, f'No plottable data for {parameter}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(title, fontsize=12, fontweight='bold')
                
        except Exception as e:
            print(f"Parameter plot error: {e}")
            ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=10, color='red')
            ax.set_title(title, fontsize=12, fontweight='bold')


def create_summary_chart(data: pd.DataFrame, title: str = "Parameter Summary") -> Figure:
    """Create summary chart for multiple parameters"""
    try:
        fig = Figure(figsize=(12, 8), dpi=100)
        
        if data.empty:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available for summary chart', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title, fontsize=16, fontweight='bold')
            return fig
        
        # Get numeric columns for summary
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove statistical columns if present
        stat_columns = ['avg', 'min', 'max', 'count', 'diff']
        plot_columns = [col for col in numeric_columns if col not in stat_columns]
        
        if not plot_columns:
            # If no direct parameter columns, use avg values grouped by parameter
            if 'param' in data.columns and 'avg' in data.columns:
                summary_data = data.groupby('param')['avg'].mean().sort_values(ascending=False)
                
                ax = fig.add_subplot(111)
                bars = ax.bar(range(len(summary_data)), summary_data.values, 
                             color='#4CAF50', alpha=0.8)
                
                ax.set_xlabel("Parameters", fontsize=12, fontweight='bold')
                ax.set_ylabel("Average Value", fontsize=12, fontweight='bold')
                ax.set_title(title, fontsize=16, fontweight='bold')
                ax.set_xticks(range(len(summary_data)))
                ax.set_xticklabels(summary_data.index, rotation=45, ha='right')
                
                # Add value labels on bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=9)
                
                ax.grid(True, alpha=0.3)
            else:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No suitable data for summary chart', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_title(title, fontsize=16, fontweight='bold')
        
        fig.tight_layout()
        return fig
        
    except Exception as e:
        print(f"Summary chart error: {e}")
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, f'Chart error: {str(e)}', 
               ha='center', va='center', transform=ax.transAxes, 
               fontsize=12, color='red')
        ax.set_title(title, fontsize=16, fontweight='bold')
        return fig


def apply_professional_style():
    """Apply professional matplotlib styling"""
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Set default colors
        plt.rcParams['axes.prop_cycle'] = plt.cycler(
            color=['#1976D2', '#388E3C', '#D32F2F', '#FF9800', '#9C27B0', '#607D8B']
        )
        
        # Typography - IMPROVED: Using Calibri font for better readability
        plt.rcParams['font.family'] = ['Calibri', 'DejaVu Sans', 'Arial']  # Calibri as primary choice
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 10
        
        # Grid and spines
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        
    except Exception as e:
        print(f"Style application error: {e}")
