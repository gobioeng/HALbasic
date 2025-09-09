from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
        
        self.init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(30000)  # 30 seconds
    
    def init_ui(self):
        """Initialize modern dashboard UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("System Dashboard")
        header.setStyleSheet("font-size: 20px; font-weight: 600; color: #1C1B1F; margin: 10px 0;")
        layout.addWidget(header)
        
        # Metrics row
        metrics_layout = QHBoxLayout()
        
        # Create metric cards
        self.metric_cards = {
            "total_records": MetricCard("Total Records", "0", "records", "#1976D2"),
            "active_machines": MetricCard("Active Machines", "0", "machines", "#388E3C"),
            "avg_temp": MetricCard("Avg Temperature", "0", "°C", "#FF7043"),
            "alerts": MetricCard("Active Alerts", "0", "alerts", "#F44336")
        }
        
        for card in self.metric_cards.values():
            metrics_layout.addWidget(card)
        metrics_layout.addStretch()
        
        layout.addLayout(metrics_layout)
        
        # Machine status section
        status_frame = QGroupBox("Machine Status")
        status_layout = QHBoxLayout(status_frame)
        
        # Create status indicators for available machines
        machines = self.machine_manager.get_available_machines() if self.machine_manager else ["M001", "M002"]
        for machine_id in machines[:6]:  # Show max 6 machines
            indicator = StatusIndicator(machine_id)
            self.status_indicators[machine_id] = indicator
            status_layout.addWidget(indicator)
        status_layout.addStretch()
        
        layout.addWidget(status_frame)
        
        # Charts section
        charts_frame = QGroupBox("Real-time Trends")
        charts_layout = QHBoxLayout(charts_frame)
        
        # Create trend chart
        self.trend_chart = self.create_trend_chart()
        charts_layout.addWidget(self.trend_chart)
        
        layout.addWidget(charts_frame)
        layout.addStretch()
    
    def create_trend_chart(self):
        """Create real-time trend chart"""
        figure = Figure(figsize=(8, 4), dpi=80)
        canvas = FigureCanvas(figure)
        
        ax = figure.add_subplot(111)
        ax.set_title("Temperature Trends (Last 24 Hours)")
        ax.set_xlabel("Time")
        ax.set_ylabel("Temperature (°C)")
        ax.grid(True, alpha=0.3)
        
        figure.tight_layout()
        return canvas
    
    def refresh_dashboard(self):
        """Refresh all dashboard data"""
        try:
            # Update metrics
            stats = self.get_summary_statistics()
            
            self.metric_cards["total_records"].update_value(str(stats.get("total_records", 0)))
            
            if self.machine_manager:
                available_machines = self.machine_manager.get_available_machines()
                self.metric_cards["active_machines"].update_value(str(len(available_machines)))
            else:
                self.metric_cards["active_machines"].update_value("0")
            
            # Update machine status (simulate for now)
            for machine_id, indicator in self.status_indicators.items():
                # In real implementation, check actual machine health
                indicator.update_status("healthy")  # or "warning"/"critical" based on data
                
        except Exception as e:
            print(f"Dashboard refresh error: {e}")
    
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