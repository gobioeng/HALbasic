from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QTabWidget,
    QWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import platform


class AboutDialog(QDialog):
    """
    Professional about dialog with comprehensive application information
    Developed by Tanmay Pandey - gobioeng.com
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Auto-detect version from main module
        self.app_version = self._get_app_version()
        self.setupUI()
    
    def _get_app_version(self):
        """Auto-detect application version"""
        try:
            # Try to import version from main module
            import main
            if hasattr(main, 'APP_VERSION'):
                return main.APP_VERSION
        except ImportError:
            pass
        
        # Fallback to default version
        return "0.0.1"

    def setupUI(self):
        """Setup the about dialog UI"""
        self.setWindowTitle("About HALog")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header section
        header_layout = QHBoxLayout()

        # Logo placeholder
        logo_label = QLabel("🏥")
        logo_label.setStyleSheet("font-size: 48px; color: #2c3e50;")
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)

        # Application info
        app_info_layout = QVBoxLayout()

        app_name = QLabel("HALog – LINAC Log Analyzer")
        app_name.setFont(QFont("Arial", 16, QFont.Bold))
        app_name.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        app_info_layout.addWidget(app_name)

        version_label = QLabel(f"Version {self.app_version}")
        version_label.setFont(QFont("Arial", 10))
        version_label.setStyleSheet("color: #7f8c8d;")
        app_info_layout.addWidget(version_label)

        developer_label = QLabel("Developed by: Tanmay Pandey")
        developer_label.setFont(QFont("Arial", 10))
        developer_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        app_info_layout.addWidget(developer_label)

        company_label = QLabel("Organization: gobioeng.com")
        company_label.setFont(QFont("Arial", 10))
        company_label.setStyleSheet("color: #7f8c8d;")
        app_info_layout.addWidget(company_label)

        header_layout.addLayout(app_info_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Tab widget for different information sections
        tab_widget = QTabWidget()

        # About tab
        about_tab = self.create_about_tab()
        tab_widget.addTab(about_tab, "About")

        # Features tab
        features_tab = self.create_features_tab()
        tab_widget.addTab(features_tab, "Features")

        # System info tab
        system_tab = self.create_system_info_tab()
        tab_widget.addTab(system_tab, "System")

        layout.addWidget(tab_widget)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

        # Apply professional styling
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3498db;
            }
        """
        )

    def create_about_tab(self):
        """Create the about tab content with proper developer attribution"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        description = QTextBrowser()
        description.setHtml(
            """
        <h3>LINAC Log Analysis System</h3>
        <p>HALog is a professional desktop application designed for monitoring and analyzing 
        machine log, water system parameters from Linear Accelerator (LINAC) medical devices.</p>
        
        <h4>Key Capabilities:</h4>
        <ul>
            <li><b>Advanced Log Parsing:</b> Intelligent parsing of complex LINAC log files with 
            unified parameter mapping</li>
            <li><b>Real-time Analysis:</b> Comprehensive statistical analysis and anomaly detection</li>
            <li><b>Professional Visualization:</b> Interactive trend charts and data visualization</li>
            <li><b>Data Quality Assessment:</b> Automated quality scoring and validation</li>
        </ul>
        
        <h4>Developer Information:</h4>
        <p><b>Lead Developer:</b> Tanmay Pandey</p>
        <p><b>Company:</b> gobioeng.com</p>
        <p>Tanmay Pandey specializes in biomedical engineering solutions, providing innovative 
        software tools for LINAC and other medical device troubleshooting and monitoring.
        Explore biomedical engineering resources, news, career opportunities, and expert
        insights for students, educators, and job seekers.</p>
        
        <p><b>Website:</b> <a href="https://www.gobioeng.com">gobioeng.com</a></p>
        <p><b>Support:</b> For technical support and inquiries, please visit our website.</p>
        
        <hr>
        <p><i>© 2025 Tanmay Pandey / gobioeng.com. All rights reserved.</i></p>
        """
        )
        description.setOpenExternalLinks(True)
        description.setStyleSheet("border: none; background: transparent;")

        layout.addWidget(description)
        return widget

    def create_features_tab(self):
        """Create the features tab content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        features = QTextBrowser()
        features.setHtml(
            """
        <h3>Enhanced Features</h3>
        
        <h4>🔍 Unified Parameter Mapping</h4>
        <ul>
            <li><b>Pump Pressure:</b> Cooling pump high statistics monitoring</li>
            <li><b>Magnetron Flow:</b> Unified magnetron cooling flow analysis</li>
            <li><b>Target & Circulator Flow:</b> Target and circulator flow tracking</li>
            <li><b>City Water Flow:</b> City water supply flow monitoring</li>
        </ul>
        
        <h4>📊 Advanced Analytics</h4>
        <ul>
            <li><b>Statistical Analysis:</b> Comprehensive statistics with confidence intervals</li>
            <li><b>Trend Analysis:</b> Time series analysis and pattern recognition</li>
        </ul>
        
        <h4>⚡ Performance Enhancements</h4>
        <ul>
            <li><b>Lazy Loading:</b> Chunked processing for large log files</li>
            <li><b>Progress Tracking:</b> Real-time progress with ETA calculations</li>
            <li><b>Background Processing:</b> Responsive UI during heavy operations</li>
            <li><b>Memory Optimization:</b> Efficient memory usage for large datasets</li>
        </ul>
        
        <h4>🎨 Professional Interface</h4>
        <ul>
            <li><b>Interactive Charts:</b> Advanced data visualization</li>
            <li><b>Tabbed Interface:</b> Organized workspace for different analyses</li>
            <li><b>Responsive Layout:</b> Adaptive interface for different screen sizes</li>
        </ul>
        
        <h4>👨‍💻 Development Excellence</h4>
        <p>This application showcases the technical expertise of <b>Tanmay Pandey</b> in:</p>
        <ul>
            <li><b>PyQt5 Development:</b> Professional desktop application architecture</li>
            <li><b>Data Processing:</b> Advanced parsing and analytics algorithms</li>
            <li><b>Performance Optimization:</b> Memory-efficient large file handling</li>
            <li><b>User Experience:</b> Intuitive and responsive interface design</li>
        </ul>
        """
        )
        features.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(features)
        return widget

    def create_system_info_tab(self):
        """Create the system information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        system_info = QTextBrowser()
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        try:
            import PyQt5.QtCore

            qt_version = PyQt5.QtCore.QT_VERSION_STR
            pyqt_version = PyQt5.QtCore.PYQT_VERSION_STR
        except:
            qt_version = "Unknown"
            pyqt_version = "Unknown"
        try:
            import pandas as pd

            pandas_version = pd.__version__
        except:
            pandas_version = "Not available"
        try:
            import numpy as np

            numpy_version = np.__version__
        except:
            numpy_version = "Not available"
        try:
            import matplotlib

            matplotlib_version = matplotlib.__version__
        except:
            matplotlib_version = "Not available"

        system_info.setHtml(
            f"""
        <h3>System Information</h3>
        <h4>Application Details</h4>
        <table>
            <tr><td><b>Application:</b></td><td>Gobioeng HALog</td></tr>
            <tr><td><b>Version:</b></td><td>0.0.1 beta</td></tr>
            <tr><td><b>Developer:</b></td><td>Tanmay Pandey</td></tr>
            <tr><td><b>Company:</b></td><td>gobioeng.com</td></tr>
            <tr><td><b>Build Date:</b></td><td>2025-08-22</td></tr>
            <tr><td><b>Architecture:</b></td><td>{platform.machine()}</td></tr>
        </table>
        <h4>System Environment</h4>
        <table>
            <tr><td><b>Operating System:</b></td><td>{platform.system()} {platform.release()}</td></tr>
            <tr><td><b>Platform:</b></td><td>{platform.platform()}</td></tr>
            <tr><td><b>Processor:</b></td><td>{platform.processor()}</td></tr>
        </table>
        <h4>Python Environment</h4>
        <table>
            <tr><td><b>Python Version:</b></td><td>{python_version}</td></tr>
            <tr><td><b>Qt Version:</b></td><td>{qt_version}</td></tr>
            <tr><td><b>PyQt5 Version:</b></td><td>{pyqt_version}</td></tr>
        </table>
        <h4>Dependencies</h4>
        <table>
            <tr><td><b>Pandas:</b></td><td>{pandas_version}</td></tr>
            <tr><td><b>NumPy:</b></td><td>{numpy_version}</td></tr>
            <tr><td><b>Matplotlib:</b></td><td>{matplotlib_version}</td></tr>
        </table>
        <h4>Technical Credits</h4>
        <table>
            <tr><td><b>Lead Developer:</b></td><td>Tanmay Pandey</td></tr>
            <tr><td><b>UI Framework:</b></td><td>PyQt5</td></tr>
            <tr><td><b>Data Processing:</b></td><td>Pandas, NumPy</td></tr>
            <tr><td><b>Visualization:</b></td><td>Matplotlib</td></tr>
        </table>
        """
        )
        system_info.setStyleSheet(
            """
            border: none; 
            background: transparent;
            QTextBrowser table { border-collapse: collapse; width: 100%; }
            QTextBrowser td { padding: 4px 8px; border-bottom: 1px solid #eee; }
            QTextBrowser tr:nth-child(even) { background-color: #f9f9f9; }
        """
        )
        layout.addWidget(system_info)
        return widget
