from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class MetricCard(QFrame):
    """Modern metric display card"""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", color: str = "#1976D2"):
        super().__init__()
        self.setFixedSize(200, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 12px; font-weight: 500;")
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #1C1B1F; font-size: 24px; font-weight: 600;")
        
        # Unit
        unit_label = QLabel(unit)
        unit_label.setStyleSheet("color: #666; font-size: 11px;")
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(unit_label)
        layout.addStretch()
    
    def update_value(self, value: str):
        self.value_label.setText(value)


class StatusIndicator(QFrame):
    """Machine status indicator with color coding"""
    
    def __init__(self, machine_id: str):
        super().__init__()
        self.machine_id = machine_id
        self.setFixedSize(150, 60)
        self.status = "unknown"  # unknown, healthy, warning, critical
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Status dot
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #ccc; font-size: 20px;")
        
        # Machine info
        info_layout = QVBoxLayout()
        machine_label = QLabel(f"Machine {machine_id}")
        machine_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        
        self.status_label = QLabel("Unknown")
        self.status_label.setStyleSheet("font-size: 10px; color: #666;")
        
        info_layout.addWidget(machine_label)
        info_layout.addWidget(self.status_label)
        
        layout.addWidget(self.status_dot)
        layout.addLayout(info_layout)
        
        self.update_status("healthy")  # Default to healthy
    
    def update_status(self, status: str):
        self.status = status
        colors = {
            "healthy": "#4CAF50",
            "warning": "#FF9800", 
            "critical": "#F44336",
            "unknown": "#9E9E9E"
        }
        
        self.status_dot.setStyleSheet(f"color: {colors.get(status, '#9E9E9E')}; font-size: 20px;")
        self.status_label.setText(status.title())


class ModernDashboard(QWidget):
    """Modern dashboard with widgets and real-time updates"""
    
    def __init__(self, machine_manager, database_manager, parent=None):
        super().__init__(parent)
        self.machine_manager = machine_manager
        self.db = database_manager
        self.metric_cards = {}
        self.status_indicators = {}
        self.machine_selector = None
        self.comparison_mode = False
        
        self.init_ui()
        
        # Auto-refresh timer (every 30 seconds for efficiency)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(30000)  # 30 seconds
    
    def init_ui(self):
        """Initialize modern dashboard UI"""
        # Check if widget already has a layout
        if self.layout() is None:
            layout = QVBoxLayout(self)
        else:
            layout = self.layout()
        
        # Header with machine selector and refresh button
        header_layout = QHBoxLayout()
        header = QLabel("LINAC Water System Monitor Dashboard")
        header.setStyleSheet("font-size: 18px; font-weight: 600; color: #1C1B1F; margin: 10px 0;")
        header_layout.addWidget(header)
        
        # Machine selector section
        if self.machine_manager:
            available_machines = self.machine_manager.get_available_machines()
            if len(available_machines) > 1:
                machine_label = QLabel("Machine:")
                machine_label.setStyleSheet("font-weight: 500; margin-right: 5px;")
                header_layout.addWidget(machine_label)
                
                self.machine_selector = QComboBox()
                self.machine_selector.addItem("All Machines")
                for machine_id in available_machines:
                    self.machine_selector.addItem(f"Machine {machine_id}")
                
                self.machine_selector.currentTextChanged.connect(self.on_machine_selection_changed)
                self.machine_selector.setStyleSheet("""
                    QComboBox {
                        padding: 6px 12px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background: white;
                        font-weight: 500;
                        min-width: 120px;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 5px solid #666;
                        margin-right: 10px;
                    }
                """)
                header_layout.addWidget(self.machine_selector)
            
            # Machine comparison toggle
            if len(available_machines) > 1:
                compare_btn = QPushButton("📊 Compare Machines")
                compare_btn.clicked.connect(self.toggle_comparison_mode)
                compare_btn.setStyleSheet("""
                    QPushButton {
                        padding: 6px 12px;
                        background: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-weight: 500;
                        margin-left: 10px;
                    }
                    QPushButton:hover {
                        background: #1976D2;
                    }
                """)
                header_layout.addWidget(compare_btn)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_dashboard)
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #1565C0;
            }
        """)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Check if we have data
        stats = self.get_summary_statistics()
        has_data = stats.get("total_records", 0) > 0
        
        if has_data:
            self._create_dashboard_with_data(layout, stats)
        else:
            # No data available - show import prompt
            self._create_no_data_ui(layout)
            
        layout.addStretch()
    
    def _create_no_data_ui(self, layout):
        """Create UI for when no data is available"""
        # Show basic metric cards with zero values
        metrics_layout = QHBoxLayout()
        
        self.metric_cards = {
            "total_records": MetricCard("Total Records", "0", "", "#1976D2"),
            "active_machines": MetricCard("Active Machines", "0", "machines", "#388E3C"),
            "parameters": MetricCard("Parameters", "0", "types", "#FF7043"),
            "status": MetricCard("Status", "No Data", "", "#FF9800")
        }
        
        for card in self.metric_cards.values():
            metrics_layout.addWidget(card)
        metrics_layout.addStretch()
        
        layout.addLayout(metrics_layout)
        
        # No data prompt
        no_data_frame = QFrame()
        no_data_frame.setStyleSheet("background: #f5f5f5; border: 2px dashed #ccc; border-radius: 8px;")
        no_data_layout = QVBoxLayout(no_data_frame)
        no_data_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("📁")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        text_label = QLabel("No data available. Import log files to view dashboard.")
        text_label.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        text_label.setAlignment(Qt.AlignCenter)
        
        import_btn = QPushButton("📥 Import Log Files")
        import_btn.clicked.connect(self._trigger_import)
        import_btn.setStyleSheet("padding: 12px 24px; background: #1976D2; color: white; border: none; border-radius: 6px; font-weight: 500;")
        
        no_data_layout.addWidget(icon_label)
        no_data_layout.addWidget(text_label)
        no_data_layout.addWidget(import_btn)
        no_data_layout.setContentsMargins(40, 40, 40, 40)
        
        layout.addWidget(no_data_frame)
    
    def _trigger_import(self):
        """Trigger file import from parent application"""
        try:
            # Find the parent HALogMaterialApp and call import
            parent = self.parent()
            while parent:
                if hasattr(parent, 'import_log_file'):
                    parent.import_log_file()
                    break
                parent = parent.parent()
            else:
                print("Could not find parent with import_log_file method")
        except Exception as e:
            print(f"Error triggering import: {e}")
    
    def create_trend_chart(self, parameter=None):
        """Create real-time trend chart with machine separation"""
        figure = Figure(figsize=(12, 5), dpi=80)
        canvas = FigureCanvas(figure)
        
        ax = figure.add_subplot(111)
        
        try:
            if self.machine_manager:
                # Get current data
                data = self.machine_manager.get_filtered_data()
                selected_machine = self.machine_manager.get_selected_machine()
                
                if not data.empty:
                    # Use selected parameter or default
                    if not parameter:
                        # Use first available parameter
                        available_params = data['parameter_type'].unique()
                        parameter = available_params[0] if len(available_params) > 0 else None
                    
                    if parameter:
                        # Filter by parameter and get average values
                        param_data = data[
                            (data['parameter_type'] == parameter) & 
                            (data['statistic_type'] == 'avg')
                        ].copy()
                        
                        if not param_data.empty:
                            # Convert datetime
                            param_data['datetime'] = pd.to_datetime(param_data['datetime'])
                            param_data = param_data.sort_values('datetime')
                            
                            # Create machine-specific colors
                            machine_colors = {
                                '2123': '#1f77b4',
                                '2207': '#ff7f0e', 
                                '2350': '#2ca02c'
                            }
                            
                            if selected_machine and selected_machine != "All Machines":
                                # Single machine view
                                machine_data = param_data[param_data['serial_number'] == selected_machine]
                                if not machine_data.empty:
                                    color = machine_colors.get(selected_machine, '#1f77b4')
                                    ax.plot(machine_data['datetime'], machine_data['value'], 
                                           color=color, linewidth=2, alpha=0.8, 
                                           label=f'Machine {selected_machine}')
                                    ax.fill_between(machine_data['datetime'], machine_data['value'], 
                                                   alpha=0.1, color=color)
                            else:
                                # Multi-machine view with distinct lines
                                for machine_id in param_data['serial_number'].unique():
                                    machine_data = param_data[param_data['serial_number'] == machine_id]
                                    if not machine_data.empty:
                                        color = machine_colors.get(machine_id, '#666666')
                                        ax.plot(machine_data['datetime'], machine_data['value'], 
                                               color=color, linewidth=2, alpha=0.8,
                                               label=f'Machine {machine_id}')
                            
                            # Get unit for y-axis label
                            unit = param_data['unit'].iloc[0] if 'unit' in param_data.columns else ""
                            
                            ax.set_title(f"{parameter} - Real-time Trends", fontsize=14, fontweight='600')
                            ax.set_xlabel("Time", fontsize=12)
                            ax.set_ylabel(f"{parameter} ({unit})", fontsize=12)
                            ax.legend(loc='upper right', framealpha=0.9)
                            ax.grid(True, alpha=0.3)
                            
                            # Format x-axis for better readability
                            import matplotlib.dates as mdates
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
                            figure.autofmt_xdate()
                            
                        else:
                            ax.text(0.5, 0.5, f'No data available for {parameter}', 
                                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
                    else:
                        ax.text(0.5, 0.5, 'No parameters available', 
                               ha='center', va='center', transform=ax.transAxes, fontsize=12)
                else:
                    ax.text(0.5, 0.5, 'No data available for selected machine', 
                           ha='center', va='center', transform=ax.transAxes, fontsize=12)
            else:
                ax.text(0.5, 0.5, 'Machine manager not available', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                       
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating chart: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            print(f"Error creating trend chart: {e}")
        
        if not ax.get_title():
            ax.set_title("System Trends - Select Parameter", fontsize=14, fontweight='600')
            ax.set_xlabel("Time")
            ax.set_ylabel("Value")
            ax.grid(True, alpha=0.3)
        
        figure.tight_layout()
        return canvas
    
    def refresh_dashboard(self):
        """Refresh all dashboard data with optimized performance"""
        try:
            # Clear the current layout content and rebuild
            self.clear_layout()
            self.init_ui()
            
        except Exception as e:
            print(f"Dashboard refresh error: {e}")
    
    def clear_layout(self):
        """Clear all widgets from the layout"""
        if self.layout():
            while self.layout().count():
                child = self.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self._clear_sublayout(child.layout())
    
    def _clear_sublayout(self, layout):
        """Helper method to clear nested layouts"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_sublayout(child.layout())
    
    def get_summary_statistics(self):
        """Get summary statistics from database"""
        try:
            if hasattr(self.db, 'get_summary_statistics'):
                return self.db.get_summary_statistics()
            elif hasattr(self.db, 'get_record_count'):
                return {"total_records": self.db.get_record_count()}
            else:
                return {"total_records": 0}
        except Exception as e:
            print(f"Error getting summary statistics: {e}")
            return {"total_records": 0}
    
    def _create_dashboard_with_data(self, layout, stats):
        """Create dashboard UI when data is available"""
        # Metrics row
        metrics_layout = QHBoxLayout()
        
        # Create metric cards with actual data
        machines_count = len(self.machine_manager.get_available_machines()) if self.machine_manager else 0
        selected_machine = self.machine_manager.get_selected_machine() if self.machine_manager else None
        
        # Get current machine-specific data if a machine is selected
        if selected_machine and selected_machine != "All Machines":
            machine_data = self.machine_manager.get_filtered_data()
            machine_records = len(machine_data) if not machine_data.empty else 0
            machine_params = len(machine_data['parameter_type'].unique()) if not machine_data.empty else 0
            title_suffix = f" (Machine {selected_machine})"
            status_text = f"Machine {selected_machine} Active"
        else:
            machine_records = stats.get('total_records', 0)
            machine_params = stats.get('unique_parameters', 0)
            title_suffix = " (All Machines)"
            status_text = "System Operational"
        
        self.metric_cards = {
            "total_records": MetricCard(f"Records{title_suffix}", f"{machine_records:,}", "", "#1976D2"),
            "active_machines": MetricCard("Available Machines", str(machines_count), "units", "#388E3C"),
            "parameters": MetricCard(f"Parameters{title_suffix}", str(machine_params), "types", "#FF7043"),
            "status": MetricCard("Status", status_text, "", "#4CAF50" if machine_records > 0 else "#FF9800")
        }
        
        for card in self.metric_cards.values():
            metrics_layout.addWidget(card)
        metrics_layout.addStretch()
        
        layout.addLayout(metrics_layout)
        
        # Machine status section (show when multiple machines available)
        if machines_count > 1:
            status_frame = QGroupBox("Machine Status Overview")
            status_frame.setStyleSheet("""
                QGroupBox {
                    font-weight: 600;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                }
            """)
            status_layout = QHBoxLayout(status_frame)
            
            # Create status indicators for available machines
            machines = self.machine_manager.get_available_machines() if self.machine_manager else []
            for machine_id in machines[:6]:  # Show max 6 machines
                indicator = StatusIndicator(machine_id)
                # Update status based on data availability
                machine_summary = self._get_machine_status(machine_id)
                if machine_summary.get('record_count', 0) > 0:
                    if machine_summary.get('record_count', 0) > 100:
                        indicator.update_status("healthy")
                    else:
                        indicator.update_status("warning")
                else:
                    indicator.update_status("critical")
                
                self.status_indicators[machine_id] = indicator
                status_layout.addWidget(indicator)
            status_layout.addStretch()
            
            layout.addWidget(status_frame)
        
        # Charts section with enhanced trend visualization
        charts_frame = QGroupBox("Real-time System Trends")
        charts_frame.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        charts_layout = QVBoxLayout(charts_frame)
        
        # Chart controls
        chart_controls = QHBoxLayout()
        param_label = QLabel("Parameter:")
        param_label.setStyleSheet("font-weight: 500;")
        chart_controls.addWidget(param_label)
        
        self.param_selector = QComboBox()
        # Get available parameters from current data
        if self.machine_manager:
            data = self.machine_manager.get_filtered_data()
            if not data.empty:
                params = sorted(data['parameter_type'].unique())
                self.param_selector.addItems(params)
            else:
                self.param_selector.addItems(["No parameters available"])
        
        self.param_selector.currentTextChanged.connect(self.update_trend_chart)
        self.param_selector.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                min-width: 150px;
            }
        """)
        chart_controls.addWidget(self.param_selector)
        chart_controls.addStretch()
        
        charts_layout.addLayout(chart_controls)
        
        # Create trend chart
        self.trend_chart = self.create_trend_chart()
        charts_layout.addWidget(self.trend_chart)
        
        layout.addWidget(charts_frame)
    
    def on_machine_selection_changed(self, text):
        """Handle machine selection change"""
        if not self.machine_manager:
            return
            
        try:
            if text == "All Machines":
                self.machine_manager.set_selected_machine("All Machines")
            else:
                # Extract machine ID from "Machine XXXX" format
                machine_id = text.replace("Machine ", "")
                self.machine_manager.set_selected_machine(machine_id)
            
            # Refresh dashboard to show new machine data
            self.refresh_dashboard()
            
        except Exception as e:
            print(f"Error changing machine selection: {e}")
    
    def toggle_comparison_mode(self):
        """Toggle between single machine and comparison mode"""
        self.comparison_mode = not self.comparison_mode
        if self.comparison_mode:
            self._show_comparison_view()
        else:
            self.refresh_dashboard()
    
    def _show_comparison_view(self):
        """Show machine comparison interface"""
        # This would open a separate comparison dialog or modify the current view
        # For now, just refresh to show all machines
        if self.machine_selector:
            self.machine_selector.setCurrentText("All Machines")
    
    def _get_machine_status(self, machine_id):
        """Get status information for a specific machine"""
        try:
            if self.machine_manager and hasattr(self.machine_manager, 'single_machine_db'):
                smdb = self.machine_manager.single_machine_db
                if smdb:
                    return smdb.get_machine_summary(machine_id)
            return {'record_count': 0}
        except Exception as e:
            print(f"Error getting machine status for {machine_id}: {e}")
            return {'record_count': 0}
    
    def update_trend_chart(self):
        """Update trend chart when parameter selection changes"""
        if hasattr(self, 'trend_chart') and hasattr(self, 'param_selector'):
            selected_param = self.param_selector.currentText()
            if selected_param and selected_param != "No parameters available":
                # Update the chart with new parameter data
                self.trend_chart = self.create_trend_chart(selected_param)
                # You would need to replace the chart in the layout here
                # For now, we'll just refresh the dashboard
                self.refresh_dashboard()