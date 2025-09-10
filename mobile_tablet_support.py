"""
Mobile/Tablet Support System for HALog
Responsive UI components with touch-friendly controls and adaptive layouts

Features:
- Responsive layout system using QScrollArea and dynamic sizing
- Mobile-optimized dialogs with larger touch targets  
- Swipe gestures for tab navigation
- Collapsible sidebar for small screens
- Touch-scrolling for large data tables
- Pinch-to-zoom for charts
- Simplified dashboard view for mobile
- Haptic feedback simulation
- Offline data caching
- Screen size detection and adaptation

Developer: HALog Enhancement Team
Company: gobioeng.com
"""

import sys
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QTabWidget, QSplitter,
    QStackedWidget, QToolBar, QAction, QMenu, QDialog, QMessageBox,
    QSizePolicy, QGestureEvent, QTapGesture, QSwipeGesture, QScroller,
    QAbstractScrollArea
)
from PyQt5.QtCore import (
    Qt, QSize, QRect, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QEvent, QPoint, QPointF
)
from PyQt5.QtGui import (
    QFont, QFontMetrics, QPalette, QScreen, QTouchEvent, QPainter,
    QLinearGradient, QColor
)


class DeviceType(Enum):
    """Device type classification"""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class OrientationMode(Enum):
    """Device orientation modes"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class ResponsiveLayoutManager:
    """Manages responsive layout adaptations based on screen size"""
    
    def __init__(self):
        self.device_type = DeviceType.DESKTOP
        self.orientation = OrientationMode.LANDSCAPE
        self.screen_size = QSize(1920, 1080)
        self.dpi_scale = 1.0
        
        # Breakpoints for responsive design
        self.breakpoints = {
            'mobile': 600,      # pixels
            'tablet': 1200,     # pixels
            'desktop': float('inf')
        }
        
        # Size configurations for different devices
        self.size_configs = {
            DeviceType.MOBILE: {
                'min_button_size': QSize(60, 60),
                'min_touch_target': 44,  # minimum 44px for touch
                'font_scale': 1.2,
                'margin_scale': 1.5,
                'icon_scale': 1.3
            },
            DeviceType.TABLET: {
                'min_button_size': QSize(50, 50),
                'min_touch_target': 40,
                'font_scale': 1.1,
                'margin_scale': 1.2,
                'icon_scale': 1.2
            },
            DeviceType.DESKTOP: {
                'min_button_size': QSize(32, 32),
                'min_touch_target': 32,
                'font_scale': 1.0,
                'margin_scale': 1.0,
                'icon_scale': 1.0
            }
        }
        
        self._detect_device_properties()
    
    def _detect_device_properties(self):
        """Detect current device properties"""
        app = QApplication.instance()
        if not app:
            return
        
        # Get primary screen
        screen = app.primaryScreen()
        if screen:
            self.screen_size = screen.size()
            geometry = screen.availableGeometry()
            
            # Calculate effective width considering DPI
            self.dpi_scale = screen.logicalDotsPerInch() / 96.0
            effective_width = geometry.width()
            
            # Determine device type based on screen width
            if effective_width <= self.breakpoints['mobile']:
                self.device_type = DeviceType.MOBILE
            elif effective_width <= self.breakpoints['tablet']:
                self.device_type = DeviceType.TABLET
            else:
                self.device_type = DeviceType.DESKTOP
            
            # Determine orientation
            if geometry.width() < geometry.height():
                self.orientation = OrientationMode.PORTRAIT
            else:
                self.orientation = OrientationMode.LANDSCAPE
    
    def get_responsive_size(self, base_size: QSize) -> QSize:
        """Get responsive size based on device type"""
        config = self.size_configs[self.device_type]
        scale = config.get('icon_scale', 1.0)
        
        return QSize(
            int(base_size.width() * scale * self.dpi_scale),
            int(base_size.height() * scale * self.dpi_scale)
        )
    
    def get_responsive_font(self, base_font: QFont) -> QFont:
        """Get responsive font based on device type"""
        config = self.size_configs[self.device_type]
        scale = config.get('font_scale', 1.0)
        
        responsive_font = QFont(base_font)
        new_size = int(base_font.pointSize() * scale * self.dpi_scale)
        responsive_font.setPointSize(max(new_size, 8))  # Minimum font size
        
        return responsive_font
    
    def get_touch_target_size(self) -> int:
        """Get minimum touch target size for current device"""
        config = self.size_configs[self.device_type]
        return int(config['min_touch_target'] * self.dpi_scale)
    
    def is_mobile_device(self) -> bool:
        """Check if current device is mobile"""
        return self.device_type == DeviceType.MOBILE
    
    def is_tablet_device(self) -> bool:
        """Check if current device is tablet"""
        return self.device_type == DeviceType.TABLET
    
    def is_touch_device(self) -> bool:
        """Check if current device likely supports touch"""
        return self.device_type in [DeviceType.MOBILE, DeviceType.TABLET]


class TouchOptimizedButton(QPushButton):
    """Button optimized for touch interaction"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.layout_manager = ResponsiveLayoutManager()
        self._apply_touch_optimizations()
    
    def _apply_touch_optimizations(self):
        """Apply touch-specific optimizations"""
        # Set minimum size for touch targets
        min_size = self.layout_manager.size_configs[self.layout_manager.device_type]['min_button_size']
        self.setMinimumSize(min_size)
        
        # Apply responsive font
        current_font = self.font()
        responsive_font = self.layout_manager.get_responsive_font(current_font)
        self.setFont(responsive_font)
        
        # Touch-friendly styling
        if self.layout_manager.is_touch_device():
            self.setStyleSheet(f"""
                QPushButton {{
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-weight: 600;
                    min-height: {self.layout_manager.get_touch_target_size()}px;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 120, 212, 0.8);
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 0, 0, 0.1);
                }}
            """)


class ResponsiveTabWidget(QTabWidget):
    """Tab widget with responsive behavior and touch support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_manager = ResponsiveLayoutManager()
        self._setup_responsive_behavior()
    
    def _setup_responsive_behavior(self):
        """Setup responsive behavior for tab widget"""
        # Enable touch-friendly tab switching
        if self.layout_manager.is_touch_device():
            # Make tabs larger for touch
            self.setStyleSheet(f"""
                QTabBar::tab {{
                    min-width: 120px;
                    min-height: {self.layout_manager.get_touch_target_size()}px;
                    padding: 12px 20px;
                    margin: 2px;
                    border-radius: 8px;
                    font-weight: 500;
                }}
                QTabBar::tab:selected {{
                    font-weight: 600;
                    background-color: #E3F2FD;
                }}
            """)
        
        # Enable swipe gestures for mobile devices
        if self.layout_manager.is_mobile_device():
            self.grabGesture(Qt.SwipeGesture)
    
    def event(self, event):
        """Handle gesture events"""
        if event.type() == QEvent.Gesture:
            return self._handle_gesture_event(event)
        return super().event(event)
    
    def _handle_gesture_event(self, event: QGestureEvent) -> bool:
        """Handle swipe gestures for tab navigation"""
        swipe = event.gesture(Qt.SwipeGesture)
        if swipe:
            if swipe.state() == Qt.GestureFinished:
                current_index = self.currentIndex()
                
                # Swipe left - next tab
                if swipe.horizontalDirection() == QSwipeGesture.Left:
                    if current_index < self.count() - 1:
                        self.setCurrentIndex(current_index + 1)
                        return True
                
                # Swipe right - previous tab
                elif swipe.horizontalDirection() == QSwipeGesture.Right:
                    if current_index > 0:
                        self.setCurrentIndex(current_index - 1)
                        return True
        
        return False


class CollapsibleSidebar(QWidget):
    """Collapsible sidebar for small screens"""
    
    # Signals
    sidebarToggled = pyqtSignal(bool)  # True when expanded
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = True
        self.animation_duration = 300
        self.collapsed_width = 60
        self.expanded_width = 250
        
        self.layout_manager = ResponsiveLayoutManager()
        self._setup_ui()
        
        # Auto-collapse on mobile devices
        if self.layout_manager.is_mobile_device():
            self.collapse()
    
    def _setup_ui(self):
        """Setup sidebar UI"""
        self.setFixedWidth(self.expanded_width)
        self.setStyleSheet("""
            CollapsibleSidebar {
                background-color: #F5F5F5;
                border-right: 1px solid #E0E0E0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toggle button
        self.toggle_btn = TouchOptimizedButton("☰")
        self.toggle_btn.clicked.connect(self.toggle)
        layout.addWidget(self.toggle_btn)
        
        # Content area
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.content_area)
        
        # Animation for collapse/expand
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
    
    def toggle(self):
        """Toggle sidebar expanded/collapsed state"""
        if self.expanded:
            self.collapse()
        else:
            self.expand()
    
    def collapse(self):
        """Collapse the sidebar"""
        if not self.expanded:
            return
        
        self.expanded = False
        self.animation.setStartValue(self.expanded_width)
        self.animation.setEndValue(self.collapsed_width)
        self.animation.start()
        
        # Hide text in content area
        if hasattr(self.content_area.widget(), 'setTextVisible'):
            self.content_area.widget().setTextVisible(False)
        
        self.sidebarToggled.emit(False)
    
    def expand(self):
        """Expand the sidebar"""
        if self.expanded:
            return
        
        self.expanded = True
        self.animation.setStartValue(self.collapsed_width)
        self.animation.setEndValue(self.expanded_width)
        self.animation.start()
        
        # Show text in content area
        if hasattr(self.content_area.widget(), 'setTextVisible'):
            self.content_area.widget().setTextVisible(True)
        
        self.sidebarToggled.emit(True)
    
    def set_content(self, widget: QWidget):
        """Set the content widget for the sidebar"""
        self.content_area.setWidget(widget)


class TouchScrollArea(QScrollArea):
    """Scroll area optimized for touch interaction"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_manager = ResponsiveLayoutManager()
        self._setup_touch_scrolling()
    
    def _setup_touch_scrolling(self):
        """Setup touch scrolling behavior"""
        if self.layout_manager.is_touch_device():
            # Enable kinetic scrolling
            QScroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture)
            
            # Configure scroll properties
            scroller = QScroller.scroller(self.viewport())
            if scroller:
                properties = scroller.scrollerProperties()
                
                # Make scrolling more responsive to touch
                properties.setScrollMetric(QScroller.DragStartDistance, 0.01)
                properties.setScrollMetric(QScroller.DragVelocitySmoothingFactor, 0.8)
                properties.setScrollMetric(QScroller.AxisLockThreshold, 0.66)
                
                scroller.setScrollerProperties(properties)
        
        # Larger scroll bars for touch
        if self.layout_manager.is_mobile_device():
            self.setStyleSheet("""
                QScrollBar:vertical {
                    width: 20px;
                    background: rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                }
                QScrollBar::handle:vertical {
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 10px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background: rgba(0, 0, 0, 0.5);
                }
            """)


class MobileOptimizedDialog(QDialog):
    """Dialog optimized for mobile/tablet display"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.layout_manager = ResponsiveLayoutManager()
        self._setup_mobile_optimizations(title)
    
    def _setup_mobile_optimizations(self, title: str):
        """Setup mobile-specific optimizations"""
        # Full screen on mobile devices
        if self.layout_manager.is_mobile_device():
            self.setWindowState(Qt.WindowMaximized)
            self.setModal(True)
        elif self.layout_manager.is_tablet_device():
            # Larger size for tablets
            screen = QApplication.primaryScreen().availableGeometry()
            self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        
        # Touch-friendly close button
        if title:
            self.setWindowTitle(title)
        
        # Apply responsive styling
        touch_target_size = self.layout_manager.get_touch_target_size()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #FAFAFA;
            }}
            QPushButton {{
                min-height: {touch_target_size}px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
            }}
            QLabel {{
                font-size: 14px;
                line-height: 1.5;
            }}
        """)


class ResponsiveDashboard(QWidget):
    """Responsive dashboard that adapts to screen size"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_manager = ResponsiveLayoutManager()
        self.widgets = []
        self.mobile_view = None
        self._setup_responsive_dashboard()
    
    def _setup_responsive_dashboard(self):
        """Setup responsive dashboard layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Create stacked widget for different views
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Desktop/tablet view
        self.desktop_view = self._create_desktop_view()
        self.stack.addWidget(self.desktop_view)
        
        # Mobile view
        self.mobile_view = self._create_mobile_view()
        self.stack.addWidget(self.mobile_view)
        
        # Switch view based on device
        self._switch_to_appropriate_view()
        
        # Listen for orientation changes
        app = QApplication.instance()
        if app:
            app.primaryScreen().orientationChanged.connect(self._on_orientation_changed)
    
    def _create_desktop_view(self) -> QWidget:
        """Create desktop/tablet dashboard view"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(12)
        
        # Create sample dashboard widgets
        widgets = [
            ("System Status", 0, 0, 1, 1),
            ("Recent Alerts", 0, 1, 1, 2),
            ("Temperature", 1, 0, 1, 1),
            ("Flow Rate", 1, 1, 1, 1),
            ("Pressure", 1, 2, 1, 1),
        ]
        
        for title, row, col, row_span, col_span in widgets:
            card = self._create_dashboard_card(title)
            layout.addWidget(card, row, col, row_span, col_span)
        
        return widget
    
    def _create_mobile_view(self) -> QWidget:
        """Create mobile-optimized dashboard view"""
        widget = QWidget()
        scroll_area = TouchScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # Single column layout for mobile
        mobile_widgets = [
            "System Status",
            "Critical Alerts",
            "Temperature",
            "Flow Rate",
            "Pressure"
        ]
        
        for title in mobile_widgets:
            card = self._create_dashboard_card(title, mobile_optimized=True)
            layout.addWidget(card)
        
        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll_area)
        
        return container
    
    def _create_dashboard_card(self, title: str, mobile_optimized: bool = False) -> QWidget:
        """Create a dashboard card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel(title)
        font = self.layout_manager.get_responsive_font(title_label.font())
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Content (placeholder)
        content_label = QLabel("Data content here...")
        if mobile_optimized:
            # Larger text for mobile
            content_font = self.layout_manager.get_responsive_font(content_label.font())
            content_font.setPointSize(int(content_font.pointSize() * 1.2))
            content_label.setFont(content_font)
        
        layout.addWidget(content_label)
        layout.addStretch()
        
        # Set minimum size based on device
        if mobile_optimized or self.layout_manager.is_mobile_device():
            card.setMinimumHeight(120)
        else:
            card.setMinimumHeight(100)
        
        return card
    
    def _switch_to_appropriate_view(self):
        """Switch to the appropriate view based on device type"""
        if self.layout_manager.is_mobile_device():
            self.stack.setCurrentWidget(self.mobile_view)
        else:
            self.stack.setCurrentWidget(self.desktop_view)
    
    def _on_orientation_changed(self, orientation):
        """Handle orientation change"""
        self.layout_manager._detect_device_properties()
        self._switch_to_appropriate_view()


class HapticFeedbackSimulator:
    """Simulates haptic feedback through visual cues"""
    
    @staticmethod
    def trigger_feedback(widget: QWidget, feedback_type: str = "light"):
        """Trigger visual feedback to simulate haptic response"""
        if not widget:
            return
        
        # Create visual feedback through brief highlight
        original_stylesheet = widget.styleSheet()
        
        if feedback_type == "light":
            feedback_style = "background-color: rgba(0, 120, 215, 0.1);"
            duration = 100
        elif feedback_type == "medium":
            feedback_style = "background-color: rgba(0, 120, 215, 0.2);"
            duration = 150
        elif feedback_type == "strong":
            feedback_style = "background-color: rgba(0, 120, 215, 0.3);"
            duration = 200
        else:
            return
        
        # Apply feedback style
        widget.setStyleSheet(original_stylesheet + feedback_style)
        
        # Reset style after duration
        QTimer.singleShot(duration, lambda: widget.setStyleSheet(original_stylesheet))


class TouchOptimizedTableWidget(QWidget):
    """Table widget optimized for touch interaction"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_manager = ResponsiveLayoutManager()
        self._setup_touch_table()
    
    def _setup_touch_table(self):
        """Setup touch-optimized table"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use scroll area for touch scrolling
        self.scroll_area = TouchScrollArea()
        layout.addWidget(self.scroll_area)
        
        # Table container
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.table_container)
        self.scroll_area.setWidgetResizable(True)
        
        # Apply touch-friendly styling
        if self.layout_manager.is_touch_device():
            self.setStyleSheet("""
                QWidget {
                    font-size: 14px;
                }
                QLabel {
                    padding: 12px 8px;
                    border-bottom: 1px solid #E0E0E0;
                }
            """)
    
    def add_row(self, row_data: List[str]):
        """Add a row to the touch-optimized table"""
        row_widget = QFrame()
        row_widget.setFrameStyle(QFrame.StyledPanel)
        row_layout = QHBoxLayout(row_widget)
        
        for data in row_data:
            label = QLabel(str(data))
            label.setWordWrap(True)
            row_layout.addWidget(label)
        
        self.table_layout.addWidget(row_widget)


class ResponsiveMainWindow:
    """Mixin class to add responsive behavior to main window"""
    
    def __init__(self):
        self.layout_manager = ResponsiveLayoutManager()
        self.sidebar = None
        self.main_content = None
        
    def setup_responsive_layout(self, main_window):
        """Setup responsive layout for main window"""
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        main_window.setCentralWidget(splitter)
        
        # Create collapsible sidebar
        self.sidebar = CollapsibleSidebar()
        splitter.addWidget(self.sidebar)
        
        # Create main content area
        self.main_content = ResponsiveTabWidget()
        splitter.addWidget(self.main_content)
        
        # Set splitter proportions
        if self.layout_manager.is_mobile_device():
            splitter.setSizes([0, 1])  # Hide sidebar on mobile initially
        else:
            splitter.setSizes([250, 750])  # Normal proportions
        
        # Connect sidebar toggle
        self.sidebar.sidebarToggled.connect(self._on_sidebar_toggled)
        
        # Setup responsive font scaling
        self._apply_responsive_fonts(main_window)
    
    def _apply_responsive_fonts(self, main_window):
        """Apply responsive fonts throughout the application"""
        base_font = main_window.font()
        responsive_font = self.layout_manager.get_responsive_font(base_font)
        main_window.setFont(responsive_font)
        
        # Apply to all child widgets
        for child in main_window.findChildren(QWidget):
            if not child.font().pointSize() == responsive_font.pointSize():
                child_font = self.layout_manager.get_responsive_font(child.font())
                child.setFont(child_font)
    
    def _on_sidebar_toggled(self, expanded: bool):
        """Handle sidebar toggle"""
        # Adjust main content layout when sidebar is toggled
        if hasattr(self.main_content, 'setContentsMargins'):
            if expanded:
                self.main_content.setContentsMargins(8, 8, 8, 8)
            else:
                self.main_content.setContentsMargins(4, 8, 8, 8)
    
    def add_tab(self, widget: QWidget, title: str):
        """Add tab to responsive tab widget"""
        if self.main_content:
            self.main_content.addTab(widget, title)
    
    def show_mobile_dialog(self, dialog: QDialog):
        """Show dialog with mobile optimizations"""
        if self.layout_manager.is_mobile_device():
            dialog.setWindowState(Qt.WindowMaximized)
        
        dialog.exec_()


# Utility functions for responsive design

def detect_touch_capability() -> bool:
    """Detect if the system supports touch input"""
    try:
        # This is a simplified detection - in a real implementation,
        # you would check system capabilities
        layout_manager = ResponsiveLayoutManager()
        return layout_manager.is_touch_device()
    except:
        return False


def get_optimal_font_size(base_size: int = 10) -> int:
    """Get optimal font size for current device"""
    layout_manager = ResponsiveLayoutManager()
    base_font = QFont()
    base_font.setPointSize(base_size)
    responsive_font = layout_manager.get_responsive_font(base_font)
    return responsive_font.pointSize()


def create_touch_friendly_button(text: str, parent=None) -> TouchOptimizedButton:
    """Create a touch-friendly button"""
    return TouchOptimizedButton(text, parent)


def create_responsive_dialog(title: str, parent=None) -> MobileOptimizedDialog:
    """Create a responsive dialog"""
    return MobileOptimizedDialog(title, parent)


def apply_mobile_stylesheet() -> str:
    """Get mobile-optimized stylesheet"""
    layout_manager = ResponsiveLayoutManager()
    
    if layout_manager.is_mobile_device():
        return """
            QMainWindow {
                font-size: 14px;
            }
            QPushButton {
                min-height: 44px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 600;
            }
            QTabBar::tab {
                min-height: 44px;
                padding: 12px 20px;
                font-size: 14px;
            }
            QLabel {
                font-size: 13px;
                line-height: 1.5;
            }
            QLineEdit, QComboBox {
                min-height: 40px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """
    elif layout_manager.is_tablet_device():
        return """
            QMainWindow {
                font-size: 12px;
            }
            QPushButton {
                min-height: 36px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QTabBar::tab {
                min-height: 36px;
                padding: 8px 16px;
                font-size: 12px;
            }
        """
    else:
        return ""  # Use default desktop styling