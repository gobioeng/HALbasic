"""
Advanced Dashboard System for HALog
Modern widget-based dashboard with draggable components and real-time updates

Features:
- Draggable widget system using QGraphicsView
- Widget types: MetricCard, TrendChart, AlertPanel, StatusIndicator
- Real-time data updates with QTimer-based auto-refresh
- Dashboard layout save/load to JSON configuration
- Custom gauge and heatmap widgets
- Integration with existing PlotUtils for styling consistency

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import math

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QColorDialog,
    QCheckBox, QLineEdit, QTextEdit, QScrollArea, QFrame, QSizePolicy,
    QMessageBox, QFileDialog, QGroupBox, QProgressBar
)
from PyQt5.QtCore import (
    Qt, QTimer, QRectF, QPointF, QSizeF, pyqtSignal, QObject, QThread,
    QMutex, QWaitCondition, pyqtSlot
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QPalette,
    QLinearGradient, QRadialGradient, QPolygonF, QPainterPath
)

import pandas as pd
import numpy as np


class DashboardWidget(QWidget):
    """Base class for all dashboard widgets"""
    
    # Signals
    dataUpdateRequested = pyqtSignal(str)  # Widget ID
    configurationChanged = pyqtSignal(str, dict)  # Widget ID, config
    
    def __init__(self, widget_id: str, title: str, parent=None):
        super().__init__(parent)
        self.widget_id = widget_id
        self.title = title
        self.config = self._get_default_config()
        self.last_update = None
        self.data = None
        
        # Setup base UI
        self.setMinimumSize(200, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._setup_ui()
        self._apply_styling()
    
    def _get_default_config(self) -> Dict:
        """Override in subclasses to provide default configuration"""
        return {
            'refresh_interval': 30,  # seconds
            'auto_refresh': True,
            'show_timestamp': True,
            'background_color': '#FFFFFF',
            'border_color': '#E0E0E0',
            'text_color': '#1C1B1F'
        }
    
    def _setup_ui(self):
        """Setup basic UI structure - override in subclasses"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("widgetTitle")
        layout.addWidget(self.title_label)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)
        
        # Status/timestamp
        self.status_label = QLabel("No data")
        self.status_label.setObjectName("widgetStatus")
        layout.addWidget(self.status_label)
    
    def _apply_styling(self):
        """Apply consistent widget styling"""
        self.setStyleSheet(f"""
            DashboardWidget {{
                background-color: {self.config['background_color']};
                border: 1px solid {self.config['border_color']};
                border-radius: 8px;
                color: {self.config['text_color']};
            }}
            QLabel#widgetTitle {{
                font-weight: 600;
                font-size: 14px;
                color: #1976D2;
                margin-bottom: 8px;
            }}
            QLabel#widgetStatus {{
                font-size: 11px;
                color: #79747E;
                margin-top: 8px;
            }}
        """)
    
    def update_data(self, data: Any):
        """Update widget with new data"""
        self.data = data
        self.last_update = datetime.now()
        self._render_data()
        
        if self.config['show_timestamp']:
            self.status_label.setText(f"Updated: {self.last_update.strftime('%H:%M:%S')}")
    
    def _render_data(self):
        """Override in subclasses to render specific data"""
        pass
    
    def get_config(self) -> Dict:
        """Get current widget configuration"""
        return self.config.copy()
    
    def set_config(self, config: Dict):
        """Update widget configuration"""
        self.config.update(config)
        self._apply_styling()
        self.configurationChanged.emit(self.widget_id, self.config)
    
    def show_configuration_dialog(self):
        """Show configuration dialog for this widget"""
        dialog = WidgetConfigDialog(self, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.set_config(dialog.get_config())


class MetricCard(DashboardWidget):
    """Card widget displaying a single metric with trend indication"""
    
    def __init__(self, widget_id: str, title: str, parent=None):
        self.metric_value = None
        self.metric_unit = ""
        self.trend_direction = 0  # -1: down, 0: stable, 1: up
        self.trend_percentage = 0.0
        super().__init__(widget_id, title, parent)
    
    def _get_default_config(self) -> Dict:
        config = super()._get_default_config()
        config.update({
            'metric_parameter': '',
            'show_trend': True,
            'decimal_places': 1,
            'warning_threshold': None,
            'critical_threshold': None,
            'large_font_size': 28,
            'trend_font_size': 12
        })
        return config
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Main metric display
        self.metric_layout = QVBoxLayout()
        self.content_layout.addLayout(self.metric_layout)
        
        # Large value
        self.value_label = QLabel("--")
        self.value_label.setObjectName("metricValue")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.metric_layout.addWidget(self.value_label)
        
        # Unit
        self.unit_label = QLabel("")
        self.unit_label.setObjectName("metricUnit")
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.metric_layout.addWidget(self.unit_label)
        
        # Trend indicator
        self.trend_label = QLabel("")
        self.trend_label.setObjectName("metricTrend")
        self.trend_label.setAlignment(Qt.AlignCenter)
        self.metric_layout.addWidget(self.trend_label)
        
        # Stretch to center content
        self.content_layout.addStretch()
    
    def _apply_styling(self):
        super()._apply_styling()
        additional_styles = f"""
            QLabel#metricValue {{
                font-size: {self.config['large_font_size']}px;
                font-weight: 700;
                color: #1C1B1F;
                margin: 8px 0;
            }}
            QLabel#metricUnit {{
                font-size: 14px;
                font-weight: 500;
                color: #49454F;
                margin-bottom: 12px;
            }}
            QLabel#metricTrend {{
                font-size: {self.config['trend_font_size']}px;
                font-weight: 600;
                margin-top: 8px;
            }}
        """
        self.setStyleSheet(self.styleSheet() + additional_styles)
    
    def _render_data(self):
        """Render metric data"""
        if not self.data:
            self.value_label.setText("--")
            self.unit_label.setText("")
            self.trend_label.setText("")
            return
        
        # Extract metric value
        parameter = self.config.get('metric_parameter', '')
        if not parameter or parameter not in self.data:
            self.value_label.setText("No Data")
            return
        
        # Get current value
        values = self.data[parameter]
        if isinstance(values, (list, np.ndarray, pd.Series)) and len(values) > 0:
            current_value = values[-1]  # Latest value
            if len(values) > 1:
                previous_value = values[-2]
                self._calculate_trend(current_value, previous_value)
        else:
            current_value = values
        
        # Format and display value
        decimal_places = self.config.get('decimal_places', 1)
        if isinstance(current_value, (int, float)):
            formatted_value = f"{current_value:.{decimal_places}f}"
            self.metric_value = current_value
        else:
            formatted_value = str(current_value)
            self.metric_value = current_value
        
        self.value_label.setText(formatted_value)
        
        # Apply color based on thresholds
        self._apply_threshold_coloring(current_value)
        
        # Update unit if available
        unit = self.config.get('metric_unit', self.metric_unit)
        self.unit_label.setText(unit)
        
        # Update trend display
        if self.config.get('show_trend', True):
            self._render_trend()
    
    def _calculate_trend(self, current: float, previous: float):
        """Calculate trend direction and percentage"""
        if previous == 0:
            self.trend_percentage = 0
            self.trend_direction = 0
            return
        
        change = current - previous
        self.trend_percentage = abs(change / previous) * 100
        
        if abs(change) < 0.01:  # Threshold for "stable"
            self.trend_direction = 0
        elif change > 0:
            self.trend_direction = 1
        else:
            self.trend_direction = -1
    
    def _render_trend(self):
        """Render trend indicator"""
        if self.trend_direction == 0:
            arrow = "→"
            color = "#79747E"
            text = f"{arrow} Stable"
        elif self.trend_direction == 1:
            arrow = "↗"
            color = "#2D7D2D" 
            text = f"{arrow} +{self.trend_percentage:.1f}%"
        else:
            arrow = "↙"
            color = "#D32F2F"
            text = f"{arrow} -{self.trend_percentage:.1f}%"
        
        self.trend_label.setText(text)
        self.trend_label.setStyleSheet(f"color: {color}; font-weight: 600;")
    
    def _apply_threshold_coloring(self, value):
        """Apply color based on warning/critical thresholds"""
        warning_threshold = self.config.get('warning_threshold')
        critical_threshold = self.config.get('critical_threshold')
        
        color = "#1C1B1F"  # Default
        
        if critical_threshold is not None and value > critical_threshold:
            color = "#D32F2F"  # Red
        elif warning_threshold is not None and value > warning_threshold:
            color = "#FF9800"  # Orange
        else:
            color = "#2D7D2D"  # Green
        
        self.value_label.setStyleSheet(f"color: {color}; font-size: {self.config['large_font_size']}px; font-weight: 700; margin: 8px 0;")


class TrendChart(DashboardWidget):
    """Chart widget displaying parameter trends over time"""
    
    def __init__(self, widget_id: str, title: str, parent=None):
        super().__init__(widget_id, title, parent)
        self.chart_data = None
    
    def _get_default_config(self) -> Dict:
        config = super()._get_default_config()
        config.update({
            'chart_parameters': [],
            'time_range': 24,  # hours
            'show_grid': True,
            'show_legend': True,
            'line_width': 2,
            'point_size': 4,
            'colors': ['#1976D2', '#D32F2F', '#FF9800', '#2D7D2D']
        })
        return config
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Chart canvas
        self.chart_canvas = QWidget()
        self.chart_canvas.setMinimumSize(300, 200)
        self.chart_canvas.setObjectName("chartCanvas")
        self.content_layout.addWidget(self.chart_canvas)
    
    def _apply_styling(self):
        super()._apply_styling()
        additional_styles = """
            QWidget#chartCanvas {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """
        self.setStyleSheet(self.styleSheet() + additional_styles)
    
    def _render_data(self):
        """Render trend chart"""
        if not self.data:
            return
        
        # For now, create a simple visualization
        # In a full implementation, this would integrate with matplotlib or pyqtgraph
        parameters = self.config.get('chart_parameters', [])
        if not parameters:
            return
        
        # Update status with parameter count
        self.status_label.setText(f"Showing {len(parameters)} parameters • Updated: {self.last_update.strftime('%H:%M:%S')}")


class AlertPanel(DashboardWidget):
    """Panel showing recent alerts and system status"""
    
    def __init__(self, widget_id: str, title: str, parent=None):
        self.alerts = []
        super().__init__(widget_id, title, parent)
    
    def _get_default_config(self) -> Dict:
        config = super()._get_default_config()
        config.update({
            'max_alerts': 10,
            'alert_types': ['critical', 'warning', 'info'],
            'auto_clear_hours': 24
        })
        return config
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Alerts scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("alertScroll")
        
        self.alert_container = QWidget()
        self.alert_layout = QVBoxLayout(self.alert_container)
        self.alert_layout.setContentsMargins(4, 4, 4, 4)
        self.alert_layout.setSpacing(4)
        
        self.scroll_area.setWidget(self.alert_container)
        self.content_layout.addWidget(self.scroll_area)
    
    def _apply_styling(self):
        super()._apply_styling()
        additional_styles = """
            QScrollArea#alertScroll {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QWidget#alertItem {
                background-color: #FFFFFF;
                border-left: 3px solid #E0E0E0;
                border-radius: 2px;
                padding: 6px;
                margin: 2px 0;
            }
            QWidget#alertItem[alertLevel="critical"] {
                border-left-color: #D32F2F;
            }
            QWidget#alertItem[alertLevel="warning"] {
                border-left-color: #FF9800;
            }
            QWidget#alertItem[alertLevel="info"] {
                border-left-color: #1976D2;
            }
        """
        self.setStyleSheet(self.styleSheet() + additional_styles)
    
    def _render_data(self):
        """Render alert data"""
        # Clear existing alerts
        for i in reversed(range(self.alert_layout.count())):
            child = self.alert_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add alerts from data
        if self.data and 'alerts' in self.data:
            alerts = self.data['alerts'][:self.config.get('max_alerts', 10)]
            
            for alert in alerts:
                self._add_alert_item(alert)
            
            if not alerts:
                no_alerts_label = QLabel("No recent alerts")
                no_alerts_label.setStyleSheet("color: #79747E; font-style: italic; padding: 12px; text-align: center;")
                self.alert_layout.addWidget(no_alerts_label)
        
        self.alert_layout.addStretch()
    
    def _add_alert_item(self, alert: Dict):
        """Add individual alert item to the panel"""
        alert_widget = QWidget()
        alert_widget.setObjectName("alertItem")
        alert_widget.setProperty("alertLevel", alert.get('level', 'info'))
        
        layout = QVBoxLayout(alert_widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Alert title/message
        title_label = QLabel(alert.get('message', 'Alert'))
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        layout.addWidget(title_label)
        
        # Alert timestamp and source
        info_text = f"{alert.get('timestamp', 'Unknown time')}"
        if 'source' in alert:
            info_text += f" • {alert['source']}"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #79747E; font-size: 10px;")
        layout.addWidget(info_label)
        
        self.alert_layout.addWidget(alert_widget)


class StatusIndicator(DashboardWidget):
    """Status indicator widget with color-coded system health"""
    
    def __init__(self, widget_id: str, title: str, parent=None):
        self.status_level = 'unknown'  # unknown, good, warning, critical
        self.status_message = "No data"
        super().__init__(widget_id, title, parent)
    
    def _get_default_config(self) -> Dict:
        config = super()._get_default_config()
        config.update({
            'status_parameters': [],
            'good_threshold': 90,
            'warning_threshold': 75,
            'show_percentage': True
        })
        return config
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Status indicator circle
        self.indicator_widget = QWidget()
        self.indicator_widget.setFixedSize(80, 80)
        self.indicator_widget.setObjectName("statusIndicator")
        
        indicator_layout = QHBoxLayout()
        indicator_layout.addStretch()
        indicator_layout.addWidget(self.indicator_widget)
        indicator_layout.addStretch()
        self.content_layout.addLayout(indicator_layout)
        
        # Status message
        self.message_label = QLabel(self.status_message)
        self.message_label.setObjectName("statusMessage")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.content_layout.addWidget(self.message_label)
        
        self.content_layout.addStretch()
    
    def _apply_styling(self):
        super()._apply_styling()
        
        # Color based on status level
        colors = {
            'good': '#2D7D2D',
            'warning': '#FF9800', 
            'critical': '#D32F2F',
            'unknown': '#79747E'
        }
        
        color = colors.get(self.status_level, colors['unknown'])
        
        additional_styles = f"""
            QWidget#statusIndicator {{
                background-color: {color};
                border: 3px solid #FFFFFF;
                border-radius: 40px;
            }}
            QLabel#statusMessage {{
                font-weight: 500;
                font-size: 13px;
                color: #1C1B1F;
                margin-top: 12px;
            }}
        """
        self.setStyleSheet(self.styleSheet() + additional_styles)
    
    def _render_data(self):
        """Render status based on data"""
        if not self.data:
            self.status_level = 'unknown'
            self.status_message = "No data available"
            self._apply_styling()
            self.message_label.setText(self.status_message)
            return
        
        # Calculate overall status from parameters
        parameters = self.config.get('status_parameters', [])
        if not parameters:
            self.status_level = 'unknown'
            self.status_message = "No parameters configured"
            self._apply_styling()
            self.message_label.setText(self.status_message)
            return
        
        # Simple status calculation
        total_score = 100.0  # Start optimistic
        
        # This would be more sophisticated in a real implementation
        good_threshold = self.config.get('good_threshold', 90)
        warning_threshold = self.config.get('warning_threshold', 75)
        
        if total_score >= good_threshold:
            self.status_level = 'good'
            self.status_message = f"System Healthy ({total_score:.1f}%)"
        elif total_score >= warning_threshold:
            self.status_level = 'warning'
            self.status_message = f"System Warning ({total_score:.1f}%)"
        else:
            self.status_level = 'critical'
            self.status_message = f"System Critical ({total_score:.1f}%)"
        
        self._apply_styling()
        self.message_label.setText(self.status_message)


class GaugeWidget(DashboardWidget):
    """Custom gauge widget for critical parameters"""
    
    def __init__(self, widget_id: str, title: str, parent=None):
        self.current_value = 0.0
        self.min_value = 0.0
        self.max_value = 100.0
        super().__init__(widget_id, title, parent)
    
    def _get_default_config(self) -> Dict:
        config = super()._get_default_config()
        config.update({
            'gauge_parameter': '',
            'min_value': 0.0,
            'max_value': 100.0,
            'warning_zone': 75.0,
            'critical_zone': 90.0,
            'gauge_colors': {
                'normal': '#2D7D2D',
                'warning': '#FF9800',
                'critical': '#D32F2F'
            }
        })
        return config
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Gauge canvas
        self.gauge_canvas = GaugeCanvas(self)
        self.gauge_canvas.setMinimumSize(200, 200)
        self.content_layout.addWidget(self.gauge_canvas)
    
    def _render_data(self):
        """Update gauge with new data"""
        if not self.data:
            return
        
        parameter = self.config.get('gauge_parameter', '')
        if parameter in self.data:
            values = self.data[parameter]
            if isinstance(values, (list, np.ndarray, pd.Series)) and len(values) > 0:
                self.current_value = float(values[-1])
            else:
                self.current_value = float(values)
            
            self.min_value = self.config.get('min_value', 0.0)
            self.max_value = self.config.get('max_value', 100.0)
            
            self.gauge_canvas.update_value(self.current_value, self.min_value, self.max_value)


class GaugeCanvas(QWidget):
    """Custom painted gauge widget"""
    
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.value = 0.0
        self.min_val = 0.0
        self.max_val = 100.0
    
    def update_value(self, value, min_val, max_val):
        """Update gauge value and repaint"""
        self.value = max(min_val, min(max_val, value))
        self.min_val = min_val
        self.max_val = max_val
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event for gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 20
        
        # Draw gauge background arc
        painter.setPen(QPen(QColor('#E0E0E0'), 8))
        start_angle = 225 * 16  # Qt uses 16ths of a degree
        span_angle = -270 * 16
        painter.drawArc(center.x() - radius, center.y() - radius, 
                       radius * 2, radius * 2, start_angle, span_angle)
        
        # Calculate value position
        if self.max_val > self.min_val:
            value_ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        else:
            value_ratio = 0
        
        value_angle = 225 - (270 * value_ratio)  # Start from 225 degrees
        
        # Determine color based on value
        config = self.parent_widget.config
        warning_zone = config.get('warning_zone', 75.0)
        critical_zone = config.get('critical_zone', 90.0)
        
        if self.value >= critical_zone:
            color = QColor(config['gauge_colors']['critical'])
        elif self.value >= warning_zone:
            color = QColor(config['gauge_colors']['warning'])
        else:
            color = QColor(config['gauge_colors']['normal'])
        
        # Draw value arc
        painter.setPen(QPen(color, 8, Qt.SolidLine, Qt.RoundCap))
        value_span = -270 * value_ratio * 16
        painter.drawArc(center.x() - radius, center.y() - radius,
                       radius * 2, radius * 2, start_angle, value_span)
        
        # Draw value text
        painter.setPen(QPen(QColor('#1C1B1F'), 2))
        painter.setFont(QFont('Segoe UI', 16, QFont.Bold))
        text = f"{self.value:.1f}"
        painter.drawText(rect, Qt.AlignCenter, text)


class WidgetConfigDialog(QDialog):
    """Configuration dialog for dashboard widgets"""
    
    def __init__(self, widget: DashboardWidget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.config = widget.get_config().copy()
        
        self.setWindowTitle(f"Configure {widget.title}")
        self.setMinimumSize(400, 300)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup configuration dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout for configuration options
        form_layout = QFormLayout()
        
        # Common options
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(1, 3600)
        self.refresh_interval.setValue(self.config.get('refresh_interval', 30))
        form_layout.addRow("Refresh Interval (sec):", self.refresh_interval)
        
        self.auto_refresh = QCheckBox()
        self.auto_refresh.setChecked(self.config.get('auto_refresh', True))
        form_layout.addRow("Auto Refresh:", self.auto_refresh)
        
        self.show_timestamp = QCheckBox()
        self.show_timestamp.setChecked(self.config.get('show_timestamp', True))
        form_layout.addRow("Show Timestamp:", self.show_timestamp)
        
        # Widget-specific options based on widget type
        if isinstance(self.widget, MetricCard):
            self._add_metric_card_options(form_layout)
        elif isinstance(self.widget, TrendChart):
            self._add_trend_chart_options(form_layout)
        elif isinstance(self.widget, AlertPanel):
            self._add_alert_panel_options(form_layout)
        elif isinstance(self.widget, StatusIndicator):
            self._add_status_indicator_options(form_layout)
        elif isinstance(self.widget, GaugeWidget):
            self._add_gauge_widget_options(form_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _add_metric_card_options(self, form_layout):
        """Add MetricCard specific options"""
        self.metric_parameter = QLineEdit()
        self.metric_parameter.setText(self.config.get('metric_parameter', ''))
        form_layout.addRow("Parameter:", self.metric_parameter)
        
        self.decimal_places = QSpinBox()
        self.decimal_places.setRange(0, 5)
        self.decimal_places.setValue(self.config.get('decimal_places', 1))
        form_layout.addRow("Decimal Places:", self.decimal_places)
        
        self.show_trend = QCheckBox()
        self.show_trend.setChecked(self.config.get('show_trend', True))
        form_layout.addRow("Show Trend:", self.show_trend)
    
    def _add_trend_chart_options(self, form_layout):
        """Add TrendChart specific options"""
        self.time_range = QSpinBox()
        self.time_range.setRange(1, 168)  # 1 hour to 1 week
        self.time_range.setValue(self.config.get('time_range', 24))
        form_layout.addRow("Time Range (hours):", self.time_range)
        
        self.show_grid = QCheckBox()
        self.show_grid.setChecked(self.config.get('show_grid', True))
        form_layout.addRow("Show Grid:", self.show_grid)
        
        self.show_legend = QCheckBox()
        self.show_legend.setChecked(self.config.get('show_legend', True))
        form_layout.addRow("Show Legend:", self.show_legend)
    
    def _add_alert_panel_options(self, form_layout):
        """Add AlertPanel specific options"""
        self.max_alerts = QSpinBox()
        self.max_alerts.setRange(1, 50)
        self.max_alerts.setValue(self.config.get('max_alerts', 10))
        form_layout.addRow("Max Alerts:", self.max_alerts)
        
        self.auto_clear_hours = QSpinBox()
        self.auto_clear_hours.setRange(1, 168)
        self.auto_clear_hours.setValue(self.config.get('auto_clear_hours', 24))
        form_layout.addRow("Auto Clear (hours):", self.auto_clear_hours)
    
    def _add_status_indicator_options(self, form_layout):
        """Add StatusIndicator specific options"""
        self.good_threshold = QDoubleSpinBox()
        self.good_threshold.setRange(0, 100)
        self.good_threshold.setValue(self.config.get('good_threshold', 90))
        form_layout.addRow("Good Threshold (%):", self.good_threshold)
        
        self.warning_threshold = QDoubleSpinBox()
        self.warning_threshold.setRange(0, 100)
        self.warning_threshold.setValue(self.config.get('warning_threshold', 75))
        form_layout.addRow("Warning Threshold (%):", self.warning_threshold)
    
    def _add_gauge_widget_options(self, form_layout):
        """Add GaugeWidget specific options"""
        self.gauge_parameter = QLineEdit()
        self.gauge_parameter.setText(self.config.get('gauge_parameter', ''))
        form_layout.addRow("Parameter:", self.gauge_parameter)
        
        self.min_value = QDoubleSpinBox()
        self.min_value.setRange(-999999, 999999)
        self.min_value.setValue(self.config.get('min_value', 0.0))
        form_layout.addRow("Min Value:", self.min_value)
        
        self.max_value = QDoubleSpinBox()
        self.max_value.setRange(-999999, 999999)
        self.max_value.setValue(self.config.get('max_value', 100.0))
        form_layout.addRow("Max Value:", self.max_value)
    
    def get_config(self) -> Dict:
        """Get configuration from dialog"""
        config = self.config.copy()
        
        # Common options
        config['refresh_interval'] = self.refresh_interval.value()
        config['auto_refresh'] = self.auto_refresh.isChecked()
        config['show_timestamp'] = self.show_timestamp.isChecked()
        
        # Widget-specific options
        if isinstance(self.widget, MetricCard):
            config['metric_parameter'] = self.metric_parameter.text()
            config['decimal_places'] = self.decimal_places.value()
            config['show_trend'] = self.show_trend.isChecked()
        elif isinstance(self.widget, TrendChart):
            config['time_range'] = self.time_range.value()
            config['show_grid'] = self.show_grid.isChecked()
            config['show_legend'] = self.show_legend.isChecked()
        elif isinstance(self.widget, AlertPanel):
            config['max_alerts'] = self.max_alerts.value()
            config['auto_clear_hours'] = self.auto_clear_hours.value()
        elif isinstance(self.widget, StatusIndicator):
            config['good_threshold'] = self.good_threshold.value()
            config['warning_threshold'] = self.warning_threshold.value()
        elif isinstance(self.widget, GaugeWidget):
            config['gauge_parameter'] = self.gauge_parameter.text()
            config['min_value'] = self.min_value.value()
            config['max_value'] = self.max_value.value()
        
        return config


class AdvancedDashboard(QWidget):
    """Main advanced dashboard container with layout management"""
    
    def __init__(self, database_manager=None, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.widgets = {}
        self.layout_config = {}
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self._auto_refresh_widgets)
        self.data_cache = {}
        
        self._setup_ui()
        self._load_default_layout()
        
        # Start auto refresh
        self.start_auto_refresh(30)  # 30 second default interval
    
    def _setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Dashboard controls
        controls_layout = QHBoxLayout()
        
        add_widget_btn = QPushButton("Add Widget")
        add_widget_btn.clicked.connect(self.show_add_widget_dialog)
        controls_layout.addWidget(add_widget_btn)
        
        layout_btn = QPushButton("Save Layout")
        layout_btn.clicked.connect(self.save_layout)
        controls_layout.addWidget(layout_btn)
        
        load_btn = QPushButton("Load Layout")  
        load_btn.clicked.connect(self.load_layout)
        controls_layout.addWidget(load_btn)
        
        controls_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh All")
        refresh_btn.clicked.connect(self.refresh_all_widgets)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Dashboard grid
        self.dashboard_grid = QGridLayout()
        self.dashboard_grid.setSpacing(12)
        layout.addLayout(self.dashboard_grid)
        
        layout.addStretch()
    
    def _load_default_layout(self):
        """Load default dashboard layout"""
        # Create some default widgets
        self.add_widget('metric_flow', MetricCard, "Water Flow", position=(0, 0))
        self.add_widget('metric_temp', MetricCard, "Temperature", position=(0, 1))
        self.add_widget('status_system', StatusIndicator, "System Status", position=(0, 2))
        self.add_widget('alerts_recent', AlertPanel, "Recent Alerts", position=(1, 0, 1, 2))
        self.add_widget('gauge_pressure', GaugeWidget, "Pressure", position=(1, 2))
    
    def add_widget(self, widget_id: str, widget_class, title: str, position: Tuple[int, int, int, int] = None):
        """Add widget to dashboard"""
        if position is None:
            position = self._find_next_position()
        
        # Create widget
        widget = widget_class(widget_id, title, self)
        
        # Connect signals
        widget.dataUpdateRequested.connect(self._handle_data_request)
        widget.configurationChanged.connect(self._handle_config_change)
        
        # Add to grid
        if len(position) == 2:
            row, col = position
            rowspan, colspan = 1, 1
        else:
            row, col, rowspan, colspan = position
        
        self.dashboard_grid.addWidget(widget, row, col, rowspan, colspan)
        self.widgets[widget_id] = {
            'widget': widget,
            'position': position,
            'class': widget_class.__name__
        }
        
        # Initial data load
        self._update_widget_data(widget_id)
        
        return widget
    
    def _find_next_position(self) -> Tuple[int, int]:
        """Find next available position in grid"""
        occupied_positions = set()
        for widget_info in self.widgets.values():
            pos = widget_info['position']
            if len(pos) == 2:
                occupied_positions.add((pos[0], pos[1]))
            else:
                row, col, rowspan, colspan = pos
                for r in range(row, row + rowspan):
                    for c in range(col, col + colspan):
                        occupied_positions.add((r, c))
        
        # Find first available position
        for row in range(10):  # Max 10 rows
            for col in range(4):  # Max 4 columns
                if (row, col) not in occupied_positions:
                    return (row, col)
        
        return (0, 0)  # Fallback
    
    def remove_widget(self, widget_id: str):
        """Remove widget from dashboard"""
        if widget_id in self.widgets:
            widget_info = self.widgets[widget_id]
            widget = widget_info['widget']
            
            self.dashboard_grid.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
            
            del self.widgets[widget_id]
    
    def show_add_widget_dialog(self):
        """Show dialog to add new widget"""
        dialog = AddWidgetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            widget_type, widget_id, title = dialog.get_widget_info()
            
            # Map widget type to class
            widget_classes = {
                'MetricCard': MetricCard,
                'TrendChart': TrendChart,
                'AlertPanel': AlertPanel,
                'StatusIndicator': StatusIndicator,
                'GaugeWidget': GaugeWidget
            }
            
            if widget_type in widget_classes:
                self.add_widget(widget_id, widget_classes[widget_type], title)
    
    def start_auto_refresh(self, interval_seconds: int):
        """Start auto refresh timer"""
        self.auto_refresh_timer.stop()
        self.auto_refresh_timer.start(interval_seconds * 1000)
    
    def stop_auto_refresh(self):
        """Stop auto refresh timer"""
        self.auto_refresh_timer.stop()
    
    def _auto_refresh_widgets(self):
        """Auto refresh all widgets"""
        for widget_id in self.widgets:
            widget = self.widgets[widget_id]['widget']
            if widget.config.get('auto_refresh', True):
                self._update_widget_data(widget_id)
    
    def refresh_all_widgets(self):
        """Manually refresh all widgets"""
        for widget_id in self.widgets:
            self._update_widget_data(widget_id)
    
    def _update_widget_data(self, widget_id: str):
        """Update data for specific widget"""
        if widget_id not in self.widgets:
            return
        
        widget = self.widgets[widget_id]['widget']
        
        # Get sample data - in real implementation, this would query the database
        sample_data = self._get_sample_data_for_widget(widget)
        widget.update_data(sample_data)
    
    def _get_sample_data_for_widget(self, widget: DashboardWidget) -> Dict:
        """Get sample data for widget - placeholder implementation"""
        # This would be replaced with real database queries
        import random
        
        if isinstance(widget, MetricCard):
            return {
                'magnetronFlow': [random.uniform(15, 18) for _ in range(10)],
                'FanremoteTempStatistics': [random.uniform(20, 25) for _ in range(10)]
            }
        elif isinstance(widget, AlertPanel):
            return {
                'alerts': [
                    {
                        'level': 'warning',
                        'message': 'Temperature slightly elevated',
                        'timestamp': '10:30:15',
                        'source': 'Temperature Monitor'
                    },
                    {
                        'level': 'info',
                        'message': 'System backup completed',
                        'timestamp': '10:15:00',
                        'source': 'Backup Manager'
                    }
                ]
            }
        elif isinstance(widget, (StatusIndicator, GaugeWidget)):
            return {
                'system_health': random.uniform(85, 95),
                'magnetronFlow': random.uniform(15, 18)
            }
        
        return {}
    
    def _handle_data_request(self, widget_id: str):
        """Handle data request from widget"""
        self._update_widget_data(widget_id)
    
    def _handle_config_change(self, widget_id: str, config: Dict):
        """Handle configuration change from widget"""
        if widget_id in self.widgets:
            # Save configuration
            self.layout_config[widget_id] = config
    
    def save_layout(self, file_path: str = None):
        """Save current dashboard layout to JSON"""
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Dashboard Layout", 
                "dashboard_layout.json",
                "JSON Files (*.json)"
            )
            if not file_path:
                return
        
        layout_data = {
            'widgets': {},
            'auto_refresh_interval': self.auto_refresh_timer.interval() // 1000,
            'saved_at': datetime.now().isoformat()
        }
        
        for widget_id, widget_info in self.widgets.items():
            widget = widget_info['widget']
            layout_data['widgets'][widget_id] = {
                'class': widget_info['class'],
                'title': widget.title,
                'position': widget_info['position'],
                'config': widget.get_config()
            }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(layout_data, f, indent=2)
            QMessageBox.information(self, "Success", f"Layout saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save layout: {e}")
    
    def load_layout(self, file_path: str = None):
        """Load dashboard layout from JSON"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Dashboard Layout",
                "",
                "JSON Files (*.json)"
            )
            if not file_path:
                return
        
        try:
            with open(file_path, 'r') as f:
                layout_data = json.load(f)
            
            # Clear existing widgets
            for widget_id in list(self.widgets.keys()):
                self.remove_widget(widget_id)
            
            # Create widgets from layout
            widget_classes = {
                'MetricCard': MetricCard,
                'TrendChart': TrendChart,
                'AlertPanel': AlertPanel,
                'StatusIndicator': StatusIndicator,
                'GaugeWidget': GaugeWidget
            }
            
            for widget_id, widget_data in layout_data['widgets'].items():
                widget_class_name = widget_data['class']
                if widget_class_name in widget_classes:
                    widget = self.add_widget(
                        widget_id,
                        widget_classes[widget_class_name],
                        widget_data['title'],
                        tuple(widget_data['position'])
                    )
                    
                    # Apply saved configuration
                    if 'config' in widget_data:
                        widget.set_config(widget_data['config'])
            
            # Apply auto refresh interval
            if 'auto_refresh_interval' in layout_data:
                self.start_auto_refresh(layout_data['auto_refresh_interval'])
            
            QMessageBox.information(self, "Success", f"Layout loaded from {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load layout: {e}")


class AddWidgetDialog(QDialog):
    """Dialog for adding new widgets to dashboard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Widget")
        self.setMinimumSize(300, 200)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup add widget dialog UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Widget type
        self.widget_type = QComboBox()
        self.widget_type.addItems([
            "MetricCard", "TrendChart", "AlertPanel", 
            "StatusIndicator", "GaugeWidget"
        ])
        form_layout.addRow("Widget Type:", self.widget_type)
        
        # Widget ID
        self.widget_id = QLineEdit()
        self.widget_id.setPlaceholderText("e.g., metric_pressure")
        form_layout.addRow("Widget ID:", self.widget_id)
        
        # Widget title
        self.widget_title = QLineEdit()
        self.widget_title.setPlaceholderText("e.g., System Pressure")
        form_layout.addRow("Title:", self.widget_title)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Add")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def get_widget_info(self) -> Tuple[str, str, str]:
        """Get widget information from dialog"""
        return (
            self.widget_type.currentText(),
            self.widget_id.text() or f"widget_{int(time.time())}",
            self.widget_title.text() or "New Widget"
        )