from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta

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

    def _handle_zoom(self, event):
        """Handle mouse wheel zoom"""
        if event.inaxes is None:
            return

        # Get the current axis
        ax = event.inaxes

        # Get current limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Calculate zoom factor
        zoom_factor = 1.1 if event.button == 'down' else 1 / 1.1

        # Get mouse position in data coordinates
        xdata = event.xdata
        ydata = event.ydata

        # Calculate new limits
        x_range = (xlim[1] - xlim[0]) * zoom_factor
        y_range = (ylim[1] - ylim[0]) * zoom_factor

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
        """Update tooltip with data values"""
        if event.inaxes is None:
            if self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
                self.canvas.draw_idle()
            return

        ax = event.inaxes

        # Find closest data point
        closest_point = self._find_closest_point(event.xdata, event.ydata, ax)

        if closest_point:
            x_val, y_val, param_name = closest_point

            # Remove old tooltip
            if self.tooltip_annotation:
                self.tooltip_annotation.remove()

            # Create new tooltip
            tooltip_text = f"{param_name}\nX: {x_val}\nY: {y_val:.3f}"
            self.tooltip_annotation = ax.annotate(
                tooltip_text,
                xy=(event.xdata, event.ydata),
                xytext=(20, 20),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.8),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                fontsize=8
            )

            self.canvas.draw_idle()

    def _find_closest_point(self, x, y, ax):
        """Find the closest data point to the mouse cursor"""
        min_distance = float('inf')
        closest_point = None

        for line in ax.get_lines():
            if line.get_label().startswith('_'):  # Skip internal matplotlib lines
                continue

            xdata = line.get_xdata()
            ydata = line.get_ydata()

            if len(xdata) == 0:
                continue

            # Convert to display coordinates for distance calculation
            try:
                # Handle datetime x-axis
                if hasattr(xdata[0], 'timestamp'):
                    x_numeric = [mdates.date2num(xi) for xi in xdata]
                else:
                    x_numeric = xdata

                # Find closest point
                distances = [(abs(xi - x) + abs(yi - y)) for xi, yi in zip(x_numeric, ydata)]
                min_idx = np.argmin(distances)

                if distances[min_idx] < min_distance:
                    min_distance = distances[min_idx]
                    x_val = xdata[min_idx]
                    y_val = ydata[min_idx]
                    param_name = line.get_label() or "Data"

                    # Format x value based on type
                    if hasattr(x_val, 'strftime'):
                        x_formatted = x_val.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        x_formatted = f"{x_val:.3f}"

                    closest_point = (x_formatted, y_val, param_name)
            except Exception as e:
                continue

        return closest_point

    def reset_view(self):
        """Reset view to initial limits"""
        for i, ax in enumerate(self.ax):
            if i < len(self.initial_views):
                view = self.initial_views[i]
                ax.set_xlim(view['xlim'])
                ax.set_ylim(view['ylim'])

        self.canvas.draw()


class PlotUtils:
    """Enhanced plotting utilities for LINAC water system data"""

    @staticmethod
    def setup_professional_style():
        """Setup professional plotting style"""
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': '#cccccc',
            'axes.linewidth': 1,
            'axes.grid': True,
            'grid.color': '#f0f0f0',
            'grid.linewidth': 0.5,
            'font.family': 'sans-serif',
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        })

    @staticmethod
    def group_parameters(parameters):
        """Group parameters by type for better visualization"""
        parameter_groups = {
            'Temperature': [],
            'Pressure': [],
            'Flow': [],
            'Voltage': [],
            'Current': [],
            'Humidity': [],
            'Position': [],
            'Other': []
        }

        for param in parameters:
            param_lower = param.lower()
            if any(temp_keyword in param_lower for temp_keyword in ['temp', 'temperature', '°c', 'celsius']):
                parameter_groups['Temperature'].append(param)
            elif any(press_keyword in param_lower for press_keyword in ['press', 'pressure', 'psi', 'bar', 'pa']):
                parameter_groups['Pressure'].append(param)
            elif any(flow_keyword in param_lower for flow_keyword in ['flow', 'rate', 'gpm', 'lpm', 'l/min']):
                parameter_groups['Flow'].append(param)
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
            'Temperature': '#ff6b6b',  # Red
            'Pressure': '#4ecdc4',     # Teal
            'Flow': '#45b7d1',         # Blue
            'Voltage': '#96ceb4',      # Green
            'Current': '#ffeaa7',      # Yellow
            'Humidity': '#dda0dd',     # Plum
            'Position': '#98d8c8',     # Mint
            'Other': '#95a5a6'         # Gray
        }

    @staticmethod
    def create_dual_graph_plot(widget, data_top=None, data_bottom=None, title_top="Top Graph", title_bottom="Bottom Graph"):
        """Create dual graph layout (top and bottom) for enhanced parameter visualization"""
        from PyQt5.QtWidgets import QVBoxLayout

        # Clear existing plot
        layout = widget.layout()
        if layout is None:
            layout = QVBoxLayout(widget)
            widget.setLayout(widget)
        else:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

        # Setup professional style
        PlotUtils.setup_professional_style()

        # Create figure with two subplots
        fig = Figure(figsize=(12, 8))

        # Top subplot
        ax1 = fig.add_subplot(2, 1, 1)
        PlotUtils._plot_parameter_data(ax1, data_top, title_top)

        # Bottom subplot  
        ax2 = fig.add_subplot(2, 1, 2)
        PlotUtils._plot_parameter_data(ax2, data_bottom, title_bottom)

        # Adjust layout
        fig.tight_layout(pad=3.0)

        # Add to widget
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        # Add interactive manager
        interactive_manager = InteractivePlotManager(fig, [ax1, ax2], canvas)

        return canvas, interactive_manager

    @staticmethod
    def _plot_parameter_data(ax, data, title):
        """Plot parameter data on a specific axis with compressed time gaps for distant dates"""
        if data is None or data.empty:
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            ax.set_title(title, fontsize=12, fontweight='bold')
            return

        # Ensure datetime column exists and is valid
        if 'datetime' in data.columns:
            data['datetime'] = pd.to_datetime(data['datetime'], errors='coerce')
            data = data[data['datetime'].notna()]

        if data.empty:
            ax.text(0.5, 0.5, 'No valid data', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            ax.set_title(title, fontsize=12, fontweight='bold')
            return

        # Determine value column to use
        value_col = None
        possible_value_cols = ['avg', 'avg_value', 'Average', 'value']
        for col in possible_value_cols:
            if col in data.columns:
                value_col = col
                break

        if not value_col:
            ax.text(0.5, 0.5, f'No value column found\nAvailable: {list(data.columns)}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=10, color='red')
            ax.set_title(title, fontsize=12, fontweight='bold')
            return

        print(f"🔍 Using value column: '{value_col}' for plotting")

        # Sort data by datetime for proper time gap analysis
        data_sorted = data.sort_values('datetime')
        
        # Check for significant time gaps (more than 1 day) that should be compressed
        time_clusters = find_time_clusters(data_sorted['datetime'], gap_threshold=timedelta(days=1))
        
        colors = PlotUtils.get_group_colors()
        color_cycle = list(colors.values())

        if len(time_clusters) > 1:
            # Multiple time clusters - use compressed timeline plotting
            PlotUtils._plot_with_compressed_timeline(ax, data_sorted, value_col, title, time_clusters, color_cycle)
        else:
            # Single continuous time period - use normal plotting
            PlotUtils._plot_continuous_timeline(ax, data_sorted, value_col, title, color_cycle)

        # Format axes
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Auto-scale with some padding
        ax.margins(x=0.02, y=0.05)

        # Add legend if multiple parameters
        if ('parameter' in data.columns and len(data['parameter'].unique()) > 1) or \
           ('parameter_name' in data.columns and len(data['parameter_name'].unique()) > 1):
            ax.legend(loc='best', framealpha=0.9)

    @staticmethod
    def _plot_with_compressed_timeline(ax, data, value_col, title, time_clusters, color_cycle):
        """Plot data with compressed timeline for multiple date ranges"""
        try:
            # Calculate the normalized positions for each cluster
            total_points = sum(len(cluster) for cluster in time_clusters)
            cluster_widths = []
            
            for cluster in time_clusters:
                # Give each cluster width proportional to its data points
                width = len(cluster) / total_points
                cluster_widths.append(max(0.15, width * 0.8))  # Minimum 15% width
            
            # Add gaps between clusters
            gap_width = 0.05
            total_width = sum(cluster_widths) + gap_width * (len(time_clusters) - 1)
            
            # Normalize to fit in [0, 1]
            if total_width > 1:
                scale_factor = 1.0 / total_width
                cluster_widths = [w * scale_factor for w in cluster_widths]
                gap_width *= scale_factor
            
            # Plot each cluster
            current_pos = 0
            tick_positions = []
            tick_labels = []
            
            for i, cluster in enumerate(time_clusters):
                cluster_data = data.iloc[cluster]
                cluster_width = cluster_widths[i]
                
                if cluster_data.empty:
                    current_pos += cluster_width + gap_width
                    continue
                
                # Get time range for this cluster
                start_time = cluster_data['datetime'].min()
                end_time = cluster_data['datetime'].max()
                
                # Transform datetime to normalized positions within this cluster
                if start_time == end_time:
                    # Single time point
                    norm_positions = [current_pos + cluster_width / 2] * len(cluster_data)
                else:
                    time_range = (end_time - start_time).total_seconds()
                    norm_positions = []
                    for dt in cluster_data['datetime']:
                        relative_pos = (dt - start_time).total_seconds() / time_range
                        norm_pos = current_pos + relative_pos * cluster_width
                        norm_positions.append(norm_pos)
                
                # Plot the data points for this cluster
                if 'parameter' in cluster_data.columns or 'parameter_name' in cluster_data.columns:
                    param_col = 'parameter' if 'parameter' in cluster_data.columns else 'parameter_name'
                    unique_params = cluster_data[param_col].unique()
                    
                    for j, param in enumerate(unique_params):
                        param_data = cluster_data[cluster_data[param_col] == param]
                        if not param_data.empty:
                            color = color_cycle[j % len(color_cycle)]
                            param_positions = [norm_positions[k] for k in param_data.index - cluster_data.index[0]]
                            ax.plot(param_positions, param_data[value_col], 
                                   label=param if i == 0 else "", color=color, 
                                   linewidth=2, marker='o', markersize=4)
                else:
                    # Single parameter
                    color = color_cycle[0]
                    ax.plot(norm_positions, cluster_data[value_col], 
                           color=color, linewidth=2, marker='o', markersize=4, 
                           label=title if i == 0 else "")
                
                # Add gap indicators
                if i < len(time_clusters) - 1:
                    gap_start = current_pos + cluster_width
                    gap_end = gap_start + gap_width
                    gap_mid = (gap_start + gap_end) / 2
                    
                    # Add visual gap indicator
                    ax.axvspan(gap_start, gap_end, color='lightgray', alpha=0.3, zorder=-1)
                    
                    # Calculate gap duration
                    next_cluster_data = data.iloc[time_clusters[i + 1]]
                    if not next_cluster_data.empty:
                        gap_duration = next_cluster_data['datetime'].min() - end_time
                        if gap_duration.days > 0:
                            gap_text = f"{gap_duration.days}d gap"
                        else:
                            gap_text = f"{gap_duration.seconds//3600}h gap"
                        
                        # Add gap annotation
                        ax.annotate(gap_text, xy=(gap_mid, 0.02), xycoords='axes fraction',
                                   ha='center', va='bottom', fontsize=8, color='red', alpha=0.7,
                                   bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))
                
                # Add tick marks for this cluster
                tick_positions.append(current_pos)
                tick_labels.append(start_time.strftime('%m/%d'))
                
                if start_time.date() != end_time.date():
                    tick_positions.append(current_pos + cluster_width)
                    tick_labels.append(end_time.strftime('%m/%d'))
                
                current_pos += cluster_width + gap_width
            
            # Set custom x-axis
            ax.set_xlim(0, 1)
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45)
            ax.set_xlabel("Date (compressed timeline)", fontsize=10)
            
            print(f"✓ Plotted {len(time_clusters)} time clusters with compressed gaps")
            
        except Exception as e:
            print(f"Error in compressed timeline plotting: {e}")
            # Fallback to continuous plotting
            PlotUtils._plot_continuous_timeline(ax, data, value_col, title, color_cycle)

    @staticmethod
    def _plot_continuous_timeline(ax, data, value_col, title, color_cycle):
        """Plot data with continuous timeline for single date range"""
        try:
            if 'parameter' in data.columns or 'parameter_name' in data.columns:
                # Multiple parameters
                param_col = 'parameter' if 'parameter' in data.columns else 'parameter_name'
                unique_params = data[param_col].unique()
                for i, param in enumerate(unique_params):
                    param_data = data[data[param_col] == param]
                    color = color_cycle[i % len(color_cycle)]

                    if 'datetime' in param_data.columns and value_col in param_data.columns:
                        ax.plot(param_data['datetime'], param_data[value_col], 
                               label=param, color=color, linewidth=2, marker='o', markersize=4)

                        # Add error bands if min/max available
                        if 'min_value' in param_data.columns and 'max_value' in param_data.columns:
                            ax.fill_between(param_data['datetime'], 
                                          param_data['min_value'], param_data['max_value'],
                                          alpha=0.2, color=color)
                        elif 'Min' in param_data.columns and 'Max' in param_data.columns:
                            ax.fill_between(param_data['datetime'], 
                                          param_data['Min'], param_data['Max'],
                                          alpha=0.2, color=color)
            else:
                # Single parameter
                if 'datetime' in data.columns and value_col in data.columns:
                    ax.plot(data['datetime'], data[value_col], 
                           color=color_cycle[0], linewidth=2, marker='o', markersize=4, 
                           label=title)

                    # Add error bands if min/max available
                    if 'min_value' in data.columns and 'max_value' in data.columns:
                        ax.fill_between(data['datetime'], 
                                      data['min_value'], data['max_value'],
                                      alpha=0.2, color=color_cycle[0])
                    elif 'Min' in data.columns and 'Max' in data.columns:
                        ax.fill_between(data['datetime'], 
                                      data['Min'], data['Max'],
                                      alpha=0.2, color=color_cycle[0])

            # Format x-axis for continuous timeline
            if 'datetime' in data.columns and not data.empty:
                date_range = data['datetime'].max() - data['datetime'].min()

                if date_range.total_seconds() < 86400:  # Less than 1 day
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, int(date_range.total_seconds() / 21600))))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                else:  # More than 1 day
                    interval = max(1, int(date_range.days / 5))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
                
        except Exception as e:
            print(f"Error in continuous timeline plotting: {e}")
            ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=10, color='red')

    @staticmethod
    def _plot_parameter_data_single(widget, data, parameter_name):
        """Plot single parameter data with compressed timeline for distant dates"""
        try:
            # Clear existing layout
            for i in reversed(range(widget.layout().count() if widget.layout() else 0)):
                widget.layout().itemAt(i).widget().setParent(None)

            if widget.layout() is None:
                from PyQt5.QtWidgets import QVBoxLayout
                widget.setLayout(QVBoxLayout())

            layout = widget.layout()

            # Create matplotlib figure with enhanced styling
            fig = Figure(figsize=(12, 4), dpi=100, facecolor='white')
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

            ax = fig.add_subplot(111)

            if data.empty:
                # Show helpful message for empty data
                ax.text(0.5, 0.5, f"No data available for:\n{parameter_name}", 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12, color='#666666', style='italic')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_title(f"{parameter_name} - No Data", fontsize=14, fontweight='bold')
                fig.tight_layout()
                canvas.draw()
                return

            # Ensure datetime column is properly formatted
            if 'datetime' in data.columns:
                data['datetime'] = pd.to_datetime(data['datetime'])
                data = data.sort_values('datetime')

                # Check for time gaps that should be compressed
                time_clusters = find_time_clusters(data['datetime'], gap_threshold=timedelta(days=1))
                
                if len(time_clusters) > 1:
                    # Multiple time clusters - use compressed timeline
                    PlotUtils._plot_single_parameter_compressed(ax, data, parameter_name, time_clusters)
                else:
                    # Single continuous time period - use normal plotting
                    PlotUtils._plot_single_parameter_continuous(ax, data, parameter_name)

            # Professional styling
            ax.set_title(parameter_name, fontsize=14, fontweight='bold', pad=20)
            ax.set_ylabel('Value', fontsize=11)

            # Set background colors
            ax.set_facecolor('#FAFAFA')
            fig.patch.set_facecolor('white')

            # Enhanced grid
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)

            # Auto-adjust layout to prevent label cutoff
            fig.tight_layout(pad=2.0)

            # Draw the canvas
            canvas.draw()

        except Exception as e:
            print(f"Error plotting {parameter_name}: {e}")
            # Show error in graph
            if 'ax' in locals():
                ax.text(0.5, 0.5, f"Error plotting {parameter_name}", 
                       transform=ax.transAxes, ha='center', va='center',
                       fontsize=12, color='red')
                fig.tight_layout()
                canvas.draw()

    @staticmethod
    def _plot_single_parameter_compressed(ax, data, parameter_name, time_clusters):
        """Plot single parameter with compressed timeline"""
        try:
            # Calculate cluster positions and widths
            total_points = sum(len(cluster) for cluster in time_clusters)
            cluster_widths = []
            
            for cluster in time_clusters:
                width = len(cluster) / total_points
                cluster_widths.append(max(0.15, width * 0.8))
            
            gap_width = 0.05
            total_width = sum(cluster_widths) + gap_width * (len(time_clusters) - 1)
            
            if total_width > 1:
                scale_factor = 1.0 / total_width
                cluster_widths = [w * scale_factor for w in cluster_widths]
                gap_width *= scale_factor
            
            # Plot each cluster
            current_pos = 0
            tick_positions = []
            tick_labels = []
            
            for i, cluster in enumerate(time_clusters):
                cluster_data = data.iloc[cluster]
                cluster_width = cluster_widths[i]
                
                if cluster_data.empty:
                    current_pos += cluster_width + gap_width
                    continue
                
                start_time = cluster_data['datetime'].min()
                end_time = cluster_data['datetime'].max()
                
                # Transform datetime to normalized positions
                if start_time == end_time:
                    norm_positions = [current_pos + cluster_width / 2] * len(cluster_data)
                else:
                    time_range = (end_time - start_time).total_seconds()
                    norm_positions = []
                    for dt in cluster_data['datetime']:
                        relative_pos = (dt - start_time).total_seconds() / time_range
                        norm_pos = current_pos + relative_pos * cluster_width
                        norm_positions.append(norm_pos)
                
                # Plot avg line (solid, prominent)
                if 'avg' in cluster_data.columns:
                    ax.plot(norm_positions, cluster_data['avg'], 
                           color='#1976D2', linewidth=2.5, 
                           label='Average' if i == 0 else '', 
                           marker='o', markersize=3, alpha=0.9)

                # Plot min/max lines (dashed, faded)
                if 'min_value' in cluster_data.columns:
                    ax.plot(norm_positions, cluster_data['min_value'], 
                           color='#1976D2', linewidth=1.5, linestyle='--', 
                           alpha=0.6, label='Minimum' if i == 0 else '')

                if 'max_value' in cluster_data.columns:
                    ax.plot(norm_positions, cluster_data['max_value'], 
                           color='#1976D2', linewidth=1.5, linestyle='--', 
                           alpha=0.6, label='Maximum' if i == 0 else '')
                
                # Add gap indicators
                if i < len(time_clusters) - 1:
                    gap_start = current_pos + cluster_width
                    gap_end = gap_start + gap_width
                    gap_mid = (gap_start + gap_end) / 2
                    
                    ax.axvspan(gap_start, gap_end, color='lightgray', alpha=0.3, zorder=-1)
                    
                    # Calculate gap duration
                    next_cluster_data = data.iloc[time_clusters[i + 1]]
                    if not next_cluster_data.empty:
                        gap_duration = next_cluster_data['datetime'].min() - end_time
                        if gap_duration.days > 0:
                            gap_text = f"{gap_duration.days}d gap"
                        else:
                            gap_text = f"{gap_duration.seconds//3600}h gap"
                        
                        ax.annotate(gap_text, xy=(gap_mid, 0.02), xycoords='axes fraction',
                                   ha='center', va='bottom', fontsize=8, color='red', alpha=0.7,
                                   bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))
                
                # Add tick marks
                tick_positions.append(current_pos)
                tick_labels.append(start_time.strftime('%m/%d'))
                
                if start_time.date() != end_time.date():
                    tick_positions.append(current_pos + cluster_width)
                    tick_labels.append(end_time.strftime('%m/%d'))
                
                current_pos += cluster_width + gap_width
            
            # Set custom x-axis
            ax.set_xlim(0, 1)
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45, ha='right')
            ax.set_xlabel("Date (compressed timeline)", fontsize=11)
            
            # Add legend if multiple lines
            if len([col for col in ['avg', 'min_value', 'max_value'] if col in data.columns]) > 1:
                ax.legend(loc='upper right', framealpha=0.9)
                
            print(f"✓ Plotted {parameter_name} with {len(time_clusters)} compressed time periods")
            
        except Exception as e:
            print(f"Error in compressed single parameter plotting: {e}")
            PlotUtils._plot_single_parameter_continuous(ax, data, parameter_name)

    @staticmethod
    def _plot_single_parameter_continuous(ax, data, parameter_name):
        """Plot single parameter with continuous timeline"""
        try:
            x_data = data['datetime']

            # Plot avg line (solid, prominent)
            if 'avg' in data.columns:
                ax.plot(x_data, data['avg'], 
                       color='#1976D2', linewidth=2.5, label='Average', 
                       marker='o', markersize=3, alpha=0.9)

            # Plot min/max lines (dashed, faded)
            if 'min_value' in data.columns:
                ax.plot(x_data, data['min_value'], 
                       color='#1976D2', linewidth=1.5, linestyle='--', 
                       alpha=0.6, label='Minimum')

            if 'max_value' in data.columns:
                ax.plot(x_data, data['max_value'], 
                       color='#1976D2', linewidth=1.5, linestyle='--', 
                       alpha=0.6, label='Maximum')

            # Enhanced timeline formatting
            if 'datetime' in data.columns and not data.empty:
                date_range = data['datetime'].max() - data['datetime'].min()

                if date_range.total_seconds() < 86400:  # Less than 1 day
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, int(date_range.total_seconds() / 21600))))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                else:  # More than 1 day
                    interval = max(1, int(date_range.days / 5))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

                # Rotate labels for better readability
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

            ax.set_xlabel('Time', fontsize=11)

            # Add legend if multiple lines
            if len([col for col in ['avg', 'min_value', 'max_value'] if col in data.columns]) > 1:
                ax.legend(loc='upper right', framealpha=0.9)
                
        except Exception as e:
            print(f"Error in continuous single parameter plotting: {e}")
            ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=10, color='red')


    @staticmethod
    def plot_shortdata_parameters(widget, shortdata_parser, group_name, serial_number=None, parameter_name=None):
        """Plot shortdata parameters using dual graph layout"""
        try:
            # Get parameters for the group
            if parameter_name:
                # Plot specific parameter in top graph
                data_top = shortdata_parser.get_data_for_visualization(group_name, parameter_name)
                title_top = f"{parameter_name} - {group_name.title()}"

                # Get another parameter for bottom graph
                all_params = shortdata_parser.get_unique_parameter_names(group_name)
                other_params = [p for p in all_params if p != parameter_name]
                if other_params:
                    data_bottom = shortdata_parser.get_data_for_visualization(group_name, other_params[0])
                    title_bottom = f"{other_params[0]} - {group_name.title()}"
                else:
                    data_bottom = pd.DataFrame()
                    title_bottom = f"No additional {group_name.title()} data"
            else:
                # Plot top 2 parameters in the group
                all_params = shortdata_parser.get_unique_parameter_names(group_name)
                if len(all_params) >= 1:
                    data_top = shortdata_parser.get_data_for_visualization(group_name, all_params[0])
                    title_top = f"{all_params[0]} - {group_name.title()}"
                else:
                    data_top = pd.DataFrame()
                    title_top = f"No {group_name.title()} data"

                if len(all_params) >= 2:
                    data_bottom = shortdata_parser.get_data_for_visualization(group_name, all_params[1])
                    title_bottom = f"{all_params[1]} - {group_name.title()}"
                else:
                    data_bottom = pd.DataFrame()
                    title_bottom = f"No additional {group_name.title()} data"

            # Filter by serial number if specified
            if serial_number and serial_number != "All":
                if not data_top.empty and 'serial_number' in data_top.columns:
                    data_top = data_top[data_top['serial_number'] == serial_number]
                if not data_bottom.empty and 'serial_number' in data_bottom.columns:
                    data_bottom = data_bottom[data_bottom['serial_number'] == serial_number]

            # Create dual graph plot
            return PlotUtils.create_dual_graph_plot(widget, data_top, data_bottom, title_top, title_bottom)

        except Exception as e:
            print(f"Error plotting shortdata parameters: {e}")
            import traceback
            traceback.print_exc()
            return None, None


def plot_trend(widget, df: pd.DataFrame, title_suffix: str = ""):
    """Enhanced trend plotting with parameter grouping and professional styling"""
    # Clear existing plot
    layout = widget.layout()
    if layout is None:
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(widget)
        widget.setLayout(layout)
    else:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    if df.empty or "datetime" not in df.columns:
        # Show empty state
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No data available for plotting', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        return

    # Prepare data
    df_clean = df.copy()
    df_clean["datetime"] = pd.to_datetime(df_clean["datetime"], errors="coerce")
    df_clean = df_clean[df_clean["datetime"].notna() & df_clean["avg"].notna()]

    if df_clean.empty:
        return

    # Setup professional style
    PlotUtils.setup_professional_style()

    # Group parameters by type
    unique_params = df_clean["param"].unique()
    parameter_groups = PlotUtils.group_parameters(unique_params)
    group_colors = PlotUtils.get_group_colors()

    # Determine subplot layout based on number of groups
    num_groups = len(parameter_groups)
    if num_groups <= 2:
        rows, cols = 1, num_groups
        fig_height = 6
    elif num_groups <= 4:
        rows, cols = 2, 2
        fig_height = 10
    else:
        rows = (num_groups + 2) // 3
        cols = 3
        fig_height = max(8, rows * 4)

    # Create figure with enhanced layout
    fig = Figure(figsize=(14, fig_height))
    fig.suptitle(f"LINAC System Parameters by Type{title_suffix}", fontsize=14, fontweight='bold')

    # Create canvas first
    canvas = FigureCanvas(fig)

    # Add navigation toolbar
    toolbar = NavigationToolbar2QT(canvas, widget)
    layout.addWidget(toolbar)

    axes = []  # Store axes for interactive manager

    # Plot each parameter group in separate subplots
    for idx, (group_name, params) in enumerate(parameter_groups.items()):
        if not params:
            continue

        ax = fig.add_subplot(rows, cols, idx + 1)
        axes.append(ax)

        group_color = group_colors.get(group_name, '#95a5a6')

        # Plot each parameter in the group with slight color variations
        for i, param in enumerate(params):
            param_data = df_clean[df_clean["param"] == param]
            if param_data.empty:
                continue

            # Create slight color variation for multiple parameters in same group
            if len(params) > 1:
                color_variation = min(i * 0.2, 0.8)
                import matplotlib.colors as mcolors
                base_color = mcolors.to_rgb(group_color)
                varied_color = tuple(max(0, min(1, c - color_variation)) for c in base_color)
                plot_color = mcolors.to_hex(varied_color)
            else:
                plot_color = group_color

            # Use enhanced multi-date plotting with gap handling
            plot_multi_date_timeline(ax, param_data, param)

        # Customize subplot
        ax.set_title(f"{group_name} Parameters", fontsize=12, fontweight='bold')
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.grid(True, alpha=0.3)

        # Format x-axis to show dates nicely
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(param_data) // 10)))

        # Add legend if multiple parameters in group
        if len(params) > 1:
            ax.legend(loc='best', fontsize=8)

        # Rotate x-axis labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # Adjust layout to prevent overlap
    fig.tight_layout()

    # Create interactive manager
    interactive_manager = InteractivePlotManager(fig, axes, canvas)

    # Add canvas to layout
    layout.addWidget(canvas)

    # Store reference to prevent garbage collection
    widget._interactive_manager = interactive_manager

    if len(unique_params) == 1:
        # Single parameter plot
        ax = fig.add_subplot(111)
        axes.append(ax)
        _plot_single_parameter(ax, df_clean, unique_params[0])
    else:
        # Multiple parameters - create subplots
        n_params = len(unique_params)
        n_cols = min(2, n_params)
        n_rows = (n_params + n_cols - 1) // n_cols

        for i, param in enumerate(unique_params):
            ax = fig.add_subplot(n_rows, n_cols, i + 1)
            axes.append(ax)
            param_data = df_clean[df_clean["param"] == param]
            _plot_single_parameter(ax, param_data, param, subplot=True)

    # Adjust layout and add to widget
    fig.tight_layout()
    layout.addWidget(canvas)

    # Add interactive functionality
    interactive_manager = InteractivePlotManager(fig, axes, canvas)

    # Store the interactive manager in the canvas for potential reset button access
    canvas.interactive_manager = interactive_manager


def reset_plot_view(widget):
    """Reset the plot view to initial state - to be connected to reset button"""
    layout = widget.layout()
    if layout is None:
        return

    # Find the canvas widget
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item and item.widget():
            canvas = item.widget()
            if hasattr(canvas, 'interactive_manager'):
                canvas.interactive_manager.reset_view()
                break

def find_time_clusters(df_times, gap_threshold=timedelta(days=1)):
    """
    Group data points into clusters based on time proximity - Enhanced for multi-date handling

    Parameters:
    -----------
    df_times : pandas Series
        Datetime values
    gap_threshold : timedelta
        Maximum gap between points in the same cluster

    Returns:
    --------
    clusters : list of lists
        Each inner list contains indices for each cluster
    """
    # Convert to Python datetime objects for safety
    try:
        times = np.array([t.to_pydatetime() for t in df_times])
    except Exception:
        times = [pd.to_datetime(t).to_pydatetime() for t in df_times]

    if len(times) <= 1:
        return [list(range(len(times)))]

    # Sort times and get indices
    indices = sorted(range(len(times)), key=lambda i: times[i])

    clusters = []
    current_cluster = [indices[0]]

    for i in range(1, len(indices)):
        curr_idx = indices[i]
        prev_idx = indices[i-1]

        # Calculate time gap
        time_gap = times[curr_idx] - times[prev_idx]

        if time_gap <= gap_threshold:
            current_cluster.append(curr_idx)
        else:
            # Start new cluster
            clusters.append(current_cluster)
            current_cluster = [curr_idx]

    clusters.append(current_cluster)
    return clusters


def plot_multi_date_timeline(ax, df, param_name, gap_threshold=timedelta(days=1)):
    """
    Plot data with visual gaps for missing data between dates

    Parameters:
    -----------
    ax : matplotlib axis
        The axis to plot on
    df : pandas DataFrame
        Data with datetime and value columns
    param_name : str
        Parameter name for labeling
    gap_threshold : timedelta
        Threshold for considering a gap significant
    """
    if df.empty or 'datetime' not in df.columns:
        return

    # Ensure datetime column is properly formatted
    df_clean = df.copy()
    df_clean['datetime'] = pd.to_datetime(df_clean['datetime'], errors='coerce')
    df_clean = df_clean.dropna(subset=['datetime'])

    if df_clean.empty:
        return

    # Sort by datetime
    df_clean = df_clean.sort_values('datetime')

    # Find time clusters (continuous data periods)
    clusters = find_time_clusters(df_clean['datetime'], gap_threshold)

    # Plot each cluster separately with gaps
    colors = plt.cm.Set1(np.linspace(0, 1, len(clusters)))

    for i, cluster in enumerate(clusters):
        cluster_data = df_clean.iloc[cluster]

        # Plot the cluster
        ax.plot(cluster_data['datetime'], cluster_data['avg'], 
               color=colors[i], linewidth=2, alpha=0.8, 
               marker='o', markersize=4, label=f'Period {i+1}' if len(clusters) > 1 else param_name)

        # Add a visual gap indicator if there are multiple clusters
        if i < len(clusters) - 1:
            # Add a gap marker between clusters
            next_cluster = clusters[i + 1]
            gap_start = cluster_data['datetime'].iloc[-1]
            gap_end = df_clean.iloc[next_cluster[0]]['datetime']

            # Add vertical dashed line to indicate gap
            gap_mid = gap_start + (gap_end - gap_start) / 2
            ax.axvline(x=gap_mid, color='red', linestyle='--', alpha=0.5, linewidth=1)

            # Add text annotation for gap
            gap_duration = gap_end - gap_start
            if gap_duration.days > 0:
                gap_text = f'{gap_duration.days}d gap'
            else:
                gap_text = f'{gap_duration.seconds//3600}h gap'

            ax.annotate(gap_text, xy=(gap_mid, ax.get_ylim()[1] * 0.9), 
                       ha='center', va='bottom', fontsize=8, color='red', alpha=0.7)

    # Enhance axis formatting
    if 'datetime' in df_clean.columns and not df_clean.empty:
        date_range = df_clean['datetime'].max() - df_clean['datetime'].min()

        if date_range.total_seconds() < 86400:  # Less than 1 day
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, int(date_range.total_seconds() / 21600))))  # Max 4 ticks
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        else:  # More than 1 day
            interval = max(1, int(date_range.days / 5))  # Max 5 ticks
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    # Add legend if multiple periods
    if len(clusters) > 1:
        ax.legend(loc='best', fontsize=8)

    # Rotate x-axis labels for better readability
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

def _plot_single_parameter(ax, df: pd.DataFrame, param_name: str, subplot: bool = False):
    """Plot data for a single parameter with compressed time gaps"""
    try:
        # Get parameter-specific styling
        param_colors = {
            'pumpPressure': '#e74c3c',
            'magnetronFlow': '#3498db',
            'targetAndCirculatorFlow': '#2ecc71',
            'cityWaterFlow': '#f39c12'
        }
        color = param_colors.get(param_name, '#34495e')

        # Sort by datetime
        df_sorted = df.sort_values("datetime")

        # If statistic_type exists, split out avg, min, max
        if "statistic_type" in df_sorted.columns:
            avg_df = df_sorted[df_sorted["statistic_type"] == "avg"]
            min_df = df_sorted[df_sorted["statistic_type"] == "min"]
            max_df = df_sorted[df_sorted["statistic_type"] == "max"]
        else:
            avg_df = df_sorted
            min_df = pd.DataFrame()
            max_df = pd.DataFrame()

        # If we have enough data points, create a broken axis plot
        if len(avg_df) > 1:
            # Find clusters of points that are close in time
            clusters = find_time_clusters(avg_df["datetime"], timedelta(days=1))

            # If we have multiple clusters, create a broken-axis style plot
            if len(clusters) > 1:
                # Clear the original axis for custom implementation
                ax.clear()

                # Extract time ranges for each cluster
                domains = []
                for cluster_indices in clusters:
                    cluster_times = [avg_df["datetime"].iloc[i] for i in cluster_indices]
                    min_time = min(cluster_times)
                    max_time = max(cluster_times)
                    domains.append((min_time, max_time))

                # Calculate total time span across all domains (within clusters only)
                total_span = sum((max_t - min_t).total_seconds() for min_t, max_t in domains)

                # Calculate the normalized domain bounds for each cluster
                # Each cluster gets space proportional to its time span plus padding
                norm_domains = []
                curr_pos = 0.05  # Start with some padding
                for i, (min_t, max_t) in enumerate(domains):
                    # Give each domain space proportional to its time span
                    span_ratio = (max_t - min_t).total_seconds() / total_span if total_span > 0 else 0

                    # Minimum width for any domain is 15% of the axis
                    domain_width = max(0.15, span_ratio * 0.7)  # 70% of space for data, adjust as needed

                    norm_domains.append((curr_pos, curr_pos + domain_width))
                    curr_pos += domain_width + 0.05  # Add some padding between domains

                # Create plot for each cluster
                for i, cluster_indices in enumerate(clusters):
                    # Get the normalized domain range
                    left, right = norm_domains[i]

                    # Extract data for this cluster
                    cluster_times = [avg_df["datetime"].iloc[j] for j in cluster_indices]
                    cluster_values = [avg_df["avg"].iloc[j] for j in cluster_indices]

                    # Skip empty clusters
                    if len(cluster_times) == 0:
                        continue

                    # Get time range for this cluster
                    min_time = min(cluster_times)
                    max_time = max(cluster_times)

                    # Linear transformation from datetime to normalized position
                    def transform_time(t):
                        if min_time == max_time:  # Handle single-point clusters
                            return (left + right) / 2
                        ratio = (t - min_time).total_seconds() / (max_time - min_time).total_seconds()
                        return left + ratio * (right - left)

                    # Transform all times to normalized positions
                    norm_times = [transform_time(t) for t in cluster_times]

                    # Plot data points in this cluster
                    ax.plot(norm_times, cluster_values, color=color, linewidth=2, alpha=0.8)
                    ax.scatter(norm_times, cluster_values, color=color, s=30, alpha=0.6, zorder=5)

                    # Find min/max values for this time range if available
                    if not min_df.empty:
                        min_cluster_data = min_df[
                            (min_df["datetime"] >= min_time) & 
                            (min_df["datetime"] <= max_time)
                        ]
                        if not min_cluster_data.empty:
                            norm_min_times = [transform_time(t) for t in min_cluster_data["datetime"]]
                            ax.plot(norm_min_times, min_cluster_data["avg"].tolist(), 
                                  color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='Min Range')

                    if not max_df.empty:
                        max_cluster_data = max_df[
                            (max_df["datetime"] >= min_time) & 
                            (max_df["datetime"] <= max_time)
                        ]
                        if not max_cluster_data.empty:
                            norm_max_times = [transform_time(t) for t in max_cluster_data["datetime"]]
                            ax.plot(norm_max_times, max_cluster_data["avg"].tolist(), 
                                  color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='Max Range')

                    # Enhanced fill between min and max with better visibility
                    if not min_df.empty and not max_df.empty:
                        merged = pd.merge(
                            min_df[(min_df["datetime"] >= min_time) & (min_df["datetime"] <= max_time)][["datetime", "avg"]],
                            max_df[(max_df["datetime"] >= min_time) & (max_df["datetime"] <= max_time)][["datetime", "avg"]],
                            on="datetime", 
                            suffixes=("_min", "_max")
                        )
                        if not merged.empty:
                            norm_merged_times = [transform_time(t) for t in merged["datetime"]]
                            # Primary shaded area
                            ax.fill_between(
                                norm_merged_times, 
                                merged["avg_min"].tolist(), 
                                merged["avg_max"].tolist(),
                                color=color, 
                                alpha=0.25,
                                label='Min-Max Range'
                            )
                            # Add subtle edge lines for better definition
                            ax.plot(norm_merged_times, merged["avg_min"].tolist(), 
                                  color=color, linestyle=':', linewidth=1, alpha=0.6)
                            ax.plot(norm_merged_times, merged["avg_max"].tolist(), 
                                  color=color, linestyle=':', linewidth=1, alpha=0.6)

                # Add break marks between clusters
                for i in range(len(norm_domains) - 1):
                    # Get the positions of adjacent domains
                    _, right = norm_domains[i]
                    left_next, _ = norm_domains[i+1]

                    # Calculate middle point for the break mark
                    mid = (right + left_next) / 2

                    # Add a break mark (gray band)
                    ax.axvspan(right, left_next, color='lightgray', alpha=0.3, zorder=-1)

                    # Calculate days between clusters
                    end_time = domains[i][1]
                    start_next_time = domains[i+1][0]
                    days_diff = (start_next_time - end_time).total_seconds() / 86400

                    # Add text annotation for the time gap
                    ax.annotate(f"{days_diff:.1f} days", 
                              xy=(mid, 0.02), 
                              xycoords='axes fraction', 
                              ha='center', va='bottom',
                              bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))

                # Set custom tick positions and labels
                tick_positions = []
                tick_labels = []

                # Add ticks for the start and end of each domain
                for i, ((min_t, max_t), (left, right)) in enumerate(zip(domains, norm_domains)):
                    # Add start date
                    tick_positions.append(left)
                    tick_labels.append(min_t.strftime('%m/%d'))

                    # Add end date if different from start date
                    if min_t.date() != max_t.date():
                        tick_positions.append(right)
                        tick_labels.append(max_t.strftime('%m/%d'))

                ax.set_xticks(tick_positions)
                ax.set_xticklabels(tick_labels)

                # Set axis limits
                ax.set_xlim(0, 1)

                # Make sure we don't lose our Y-axis formatting
                ax.grid(True, linestyle='--', alpha=0.3)

                # Add title under the plot
                ax.text(0.5, -0.1, "Time (days with compressed gaps)", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=10)

            else:
                # Just one cluster - plot normally
                ax.plot(avg_df["datetime"], avg_df["avg"], color=color, linewidth=2, alpha=0.8, label=param_name)
                ax.scatter(avg_df["datetime"], avg_df["avg"], color=color, s=30, alpha=0.6, zorder=5)

                # Enhanced min/max visualization
                if not min_df.empty:
                    ax.plot(min_df["datetime"], min_df["avg"], 
                          color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='Min Range')

                if not max_df.empty:
                    ax.plot(max_df["datetime"], max_df["avg"], 
                          color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='Max Range')

                # Enhanced fill between with better visibility
                if not min_df.empty and not max_df.empty:
                    merged = pd.merge(
                        min_df[["datetime", "avg"]],
                        max_df[["datetime", "avg"]],
                        on="datetime", 
                        suffixes=("_min", "_max")
                    )
                    if not merged.empty:
                        # Primary shaded area with better opacity
                        ax.fill_between(
                            merged["datetime"], 
                            merged["avg_min"], 
                            merged["avg_max"], 
                            color=color, 
                            alpha=0.25,
                            label='Min-Max Range'
                        )
                        # Add subtle edge lines for definition
                        ax.plot(merged["datetime"], merged["avg_min"], 
                              color=color, linestyle=':', linewidth=1, alpha=0.6)
                        ax.plot(merged["datetime"], merged["avg_max"], 
                              color=color, linestyle=':', linewidth=1, alpha=0.6)

                # Add trend line
                if len(avg_df) > 3:
                    try:
                        x_numeric = mdates.date2num(avg_df["datetime"])
                        coeffs = np.polyfit(x_numeric, avg_df["avg"], 1)
                        trend_line = np.polyval(coeffs, x_numeric)
                        ax.plot(avg_df["datetime"], trend_line, '--', color=color, alpha=0.7, linewidth=1.5,
                               label=f'Trend (slope: {coeffs[0]:.4f})')
                    except Exception as e:
                        print(f"Error adding trend line: {e}")

                # Format dates appropriately
                if 'datetime' in avg_df.columns and not avg_df.empty:
                    date_range = avg_df["datetime"].max() - avg_df["datetime"].min()
                    if date_range.total_seconds() < 24*3600:  # Less than a day
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
                    elif date_range.total_seconds() < 7*24*3600:  # Less than a week
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                        ax.xaxis.set_major_locator(mdates.DayLocator())
                    else:
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        else:
            # Not enough data - just plot what we have
            ax.plot(avg_df["datetime"], avg_df["avg"], color=color, linewidth=2, alpha=0.8, label=param_name)
            ax.scatter(avg_df["datetime"], avg_df["avg"], color=color, s=30, alpha=0.6, zorder=5)

        # Formatting
        if not subplot:
            if len(clusters) > 1:
                ax.set_xlabel("Date (compressed time scale)", fontweight='bold')
            else:
                ax.set_xlabel("Date/Time", fontweight='bold')
            ax.set_title(f"Trend Analysis: {param_name}", fontweight='bold', pad=20)
        else:
            ax.set_title(param_name, fontweight='bold')

        # Get unit for y-axis label
        unit = df['unit'].iloc[0] if 'unit' in df.columns and not df.empty else ''
        ax.set_ylabel(f"Value ({unit})" if unit else "Value", fontweight='bold')

        # Add y-axis margin for better appearance (100% from min and max)
        # Use min/max of ALL relevant values (avg, min, max) for scaling
        y_candidates = []
        if len(avg_df) > 0:
            y_candidates.append(avg_df["avg"].dropna())
        if len(min_df) > 0:
            y_candidates.append(min_df["avg"].dropna())
        if len(max_df) > 0:
            y_candidates.append(max_df["avg"].dropna())
        if y_candidates:
            y_values = pd.concat(y_candidates)
            y_min = y_values.min()
            y_max = y_values.max()
            y_range = y_max - y_min if y_max != y_min else 1
            margin = y_range * 1.0  # 100% margin above max and below min
            ax.set_ylim(y_min - margin, y_max + margin)

        # Add grid and styling
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_facecolor('#fafafa')

        # Add statistical annotations if not a subplot
        if not subplot and len(avg_df) > 1:
            _add_statistical_annotations(ax, avg_df["avg"])

    except Exception as e:
        print(f"Error plotting parameter {param_name}: {e}")
        # Create a simple error message in the plot
        ax.clear()
        ax.text(0.5, 0.5, f'Error plotting data: {str(e)}', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=10, color='red')
        ax.set_xticks([])
        ax.set_yticks([])

def _add_statistical_annotations(ax, y_data):
    """Add statistical annotations to the plot"""
    try:
        mean_val = y_data.mean()
        std_val = y_data.std()
        # Add horizontal lines for mean and standard deviation bands
        ax.axhline(y=mean_val, color='red', linestyle='-', alpha=0.5, linewidth=1, label=f'Mean: {mean_val:.2f}')
        ax.axhline(y=mean_val + std_val, color='orange', linestyle='--', alpha=0.5, linewidth=1, label=f'±1σ')
        ax.axhline(y=mean_val - std_val, color='orange', linestyle='--', alpha=0.5, linewidth=1)
        # Add legend
        ax.legend(loc='upper right', framealpha=0.9)
    except Exception as e:
        print(f"Error adding statistical annotations: {e}")

def plot_anomaly(widget, anomaly_df: pd.DataFrame, serial: str = None, param: str = None):
    """Plot anomaly overlays on existing trend plots"""
    if anomaly_df.empty:
        return
    # Filter anomalies based on selection
    filtered_anomalies = anomaly_df.copy()
    if serial and serial != "All":
        # Note: anomaly_df might not have serial column, need to adjust based on actual structure
        pass
    if param and param != "All":
        filtered_anomalies = filtered_anomalies[filtered_anomalies['parameter_type'] == param]
    # This function would overlay anomaly points on the existing plot
    # Implementation depends on how the widget's canvas can be accessed
    print(f"Would overlay {len(filtered_anomalies)} anomalies on trend plot")

def plot_stats(widget, stats_df: pd.DataFrame, serial: str = None, param: str = None):
    """Plot statistical overlays on existing trend plots"""
    if stats_df.empty:
        return
    # Filter statistics based on selection
    filtered_stats = stats_df.copy()
    if param and param != "All":
        filtered_stats = filtered_stats[filtered_stats['parameter'] == param]
    # This function would overlay statistical information on the existing plot
    # Implementation depends on how the widget's canvas can be accessed
    print(f"Would overlay statistics for {len(filtered_stats)} parameters on trend plot")

def create_summary_plot(df: pd.DataFrame) -> Figure:
    """Create a comprehensive summary plot for dashboard"""
    PlotUtils.setup_professional_style()
    fig = Figure(figsize=(12, 8))
    fig.suptitle("LINAC Water System Overview", fontsize=16, fontweight='bold')
    if df.empty:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='gray')
        return fig
    # Get unique parameters
    unique_params = df["param"].unique()
    n_params = len(unique_params)
    if n_params == 0:
        return fig
    # Create subplots for each parameter
    n_cols = min(2, n_params)
    n_rows = (n_params + n_cols - 1) // n_cols
    for i, param in enumerate(unique_params):
        ax = fig.add_subplot(n_rows, n_cols, i + 1)
        param_data = df[df["param"] == param]
        if not param_data.empty:
            # Simple histogram of values
            values = param_data["avg"].dropna()
            if len(values) > 0:
                ax.hist(values, bins=20, alpha=0.7, color=f'C{i}')
                ax.set_title(param, fontweight='bold')
                ax.set_xlabel('Value')
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig