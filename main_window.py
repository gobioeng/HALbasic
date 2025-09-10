from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,  # Added missing import
    QComboBox,
    QAction,
    QMenuBar,
    QFrame,
    QGroupBox,
    QGridLayout,
    QHeaderView,
    QAbstractItemView,
    QSizePolicy,
    QLineEdit,
    QTextEdit,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QFont

# Import enhanced plotting widgets for trend graphs
try:
    from plot_utils import EnhancedPlotWidget
    PLOTTING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced plotting not available: {e}")
    PLOTTING_AVAILABLE = False

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("HALog • Professional LINAC Monitor")
        MainWindow.resize(1400, 900)
        MainWindow.setMinimumSize(1000, 700)

        # Setup menu bar FIRST before anything else
        self.setup_menu_bar(MainWindow)

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(12)
        self.main_layout.setContentsMargins(12, 12, 12, 12)

        # Apply modern native styling
        self.apply_modern_styling(MainWindow)
        self.setup_main_content()

    def apply_modern_styling(self, MainWindow):
        """Apply modern native Windows-style theme with responsive design"""
        MainWindow.setStyleSheet("""
            /* Modern Windows Theme - Native Feel */
            QMainWindow {
                background-color: #f8f9fa;
                color: #212529;
                font-family: 'Segoe UI', 'Microsoft Sans Serif', sans-serif;
                font-size: 9pt;
            }
            
            /* Enhanced Tab Widget - Windows 11 Style */
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 8px;
                margin-top: 4px;
            }
            QTabBar {
                background-color: transparent;
                border: none;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                min-width: 80px;
                border: 1px solid #dee2e6;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #0d6efd;
                border-color: #0d6efd;
                border-bottom: 2px solid #0d6efd;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f8f9fa;
                border-color: #adb5bd;
            }
            
            /* Modern Group Boxes - Card Style */
            QGroupBox {
                font-weight: 600;
                color: #212529;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 20px;
                background-color: white;
                font-size: 10pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 6px 12px;
                background-color: #0d6efd;
                color: white;
                border-radius: 4px;
                font-weight: 600;
            }
            
            /* Modern Buttons - Windows 11 Fluent Style */
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: 1px solid #0d6efd;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 9pt;
                min-width: 80px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
                border-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
                border-color: #0a58ca;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
                border-color: #dee2e6;
            }
            
            /* Secondary Button Style */
            QPushButton#secondaryButton {
                background-color: #6c757d;
                border-color: #6c757d;
            }
            QPushButton#secondaryButton:hover {
                background-color: #5c636a;
                border-color: #5c636a;
            }
            
            /* Success Button Style */
            QPushButton#successButton {
                background-color: #198754;
                border-color: #198754;
            }
            QPushButton#successButton:hover {
                background-color: #157347;
                border-color: #157347;
            }
            
            /* Danger Button Style */
            QPushButton#dangerButton {
                background-color: #dc3545;
                border-color: #dc3545;
            }
            QPushButton#dangerButton:hover {
                background-color: #bb2d3b;
                border-color: #bb2d3b;
            }
            
            /* Modern Input Fields */
            QLineEdit, QTextEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                color: #212529;
                font-size: 9pt;
                selection-background-color: #cfe2ff;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #86b7fe;
                outline: 0;
                box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
            }
            QLineEdit:hover, QTextEdit:hover {
                border-color: #adb5bd;
            }
            
            /* Modern ComboBox */
            QComboBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 6px 12px;
                background-color: white;
                color: #212529;
                font-size: 9pt;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #86b7fe;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-style: solid;
                border-width: 4px 4px 0px 4px;
                border-color: #6c757d transparent transparent transparent;
            }
            
            /* Modern Tables */
            QTableWidget {
                background-color: white;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 9pt;
                selection-background-color: #cfe2ff;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTableWidget::item:selected {
                background-color: #cfe2ff;
                color: #0d6efd;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                color: #495057;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #0d6efd;
                font-weight: 600;
                font-size: 9pt;
            }
            QHeaderView::section:hover {
                background-color: #f8f9fa;
            }
            
            /* Modern Labels */
            QLabel {
                color: #212529;
                font-size: 9pt;
            }
            
            /* Modern Frames */
            QFrame#plotFrame {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                margin: 4px;
                padding: 8px;
            }
            
            /* Modern Progress Bars */
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #e9ecef;
                text-align: center;
                color: #495057;
                font-weight: 500;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #0d6efd;
                border-radius: 4px;
            }
            
            /* Modern Status Bar */
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
                font-size: 8pt;
                padding: 4px;
            }
            
            /* Modern Scrollbars */
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #ced4da;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
            }
        """)

    def setup_menu_bar(self, MainWindow):
        """Setup the menu bar with all menus and actions"""
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # File Menu
        self.menuFile = self.menubar.addMenu("&File")
        self.actionOpen_Log_File = QAction(MainWindow)
        self.actionOpen_Log_File.setObjectName("actionOpen_Log_File")
        self.actionOpen_Log_File.setText("&Open Log File...")
        self.actionOpen_Log_File.setShortcut(QKeySequence("Ctrl+O"))
        self.actionOpen_Log_File.setStatusTip("Open a LINAC log file for analysis")
        self.menuFile.addAction(self.actionOpen_Log_File)
        self.menuFile.addSeparator()
        self.actionExport_Data = QAction(MainWindow)
        self.actionExport_Data.setObjectName("actionExport_Data")
        self.actionExport_Data.setText("&Export Data...")
        self.actionExport_Data.setShortcut(QKeySequence("Ctrl+E"))
        self.actionExport_Data.setStatusTip("Export analysis results")
        self.menuFile.addAction(self.actionExport_Data)
        self.menuFile.addSeparator()
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setText("E&xit")
        self.actionExit.setShortcut(QKeySequence("Ctrl+Q"))
        self.actionExit.setStatusTip("Exit the application")
        self.menuFile.addAction(self.actionExit)

        # Data Menu
        self.menuData = self.menubar.addMenu("&Data")
        self.actionClearAllData = QAction(MainWindow)
        self.actionClearAllData.setObjectName("actionClearAllData")
        self.actionClearAllData.setText("&Clear All Data...")
        self.actionClearAllData.setStatusTip("Clear all imported log data from database")
        self.menuData.addAction(self.actionClearAllData)
        
        self.actionOptimizeDatabase = QAction(MainWindow)
        self.actionOptimizeDatabase.setObjectName("actionOptimizeDatabase")
        self.actionOptimizeDatabase.setText("&Optimize Database")
        self.actionOptimizeDatabase.setStatusTip("Optimize database for better performance")
        self.menuData.addAction(self.actionOptimizeDatabase)

        # Help Menu
        self.menuHelp = self.menubar.addMenu("&Help")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout.setText("&About HALog...")
        self.actionAbout.setStatusTip("About this application")
        self.menuHelp.addAction(self.actionAbout)
        self.actionAbout_Qt = QAction(MainWindow)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.actionAbout_Qt.setText("About &Qt...")
        self.actionAbout_Qt.setStatusTip("About Qt framework")
        self.menuHelp.addAction(self.actionAbout_Qt)

    def setup_main_content(self):
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.tabWidget)
        self.setup_dashboard_tab()
        self.setup_trends_tab()
        self.setup_analysis_tab()
        self.setup_mpc_tab()  # NEW MPC TAB
        self.setup_fault_code_tab()
        self.setup_about_tab()

    def setup_dashboard_tab(self):
        self.dashboardTab = QWidget()
        self.tabWidget.addTab(self.dashboardTab, "📊 Dashboard")
        layout = QVBoxLayout(self.dashboardTab)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("<h2>LINAC Water System Monitor</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # Machine selection header
        machine_header_layout = QHBoxLayout()
        machine_header_layout.setContentsMargins(0, 10, 0, 10)
        
        # Machine selection label and combo box
        machine_label = QLabel("Select Machine:")
        machine_label.setFont(QFont("Calibri", 10))
        machine_label.setAlignment(Qt.AlignVCenter)
        
        self.cmbMachineSelect = QComboBox()
        self.cmbMachineSelect.setFont(QFont("Calibri", 10))
        self.cmbMachineSelect.setMinimumWidth(200)
        self.cmbMachineSelect.setToolTip("Select machine to analyze based on serial number")
        # Style the combo box to match the app theme
        self.cmbMachineSelect.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                background-color: white;
                font-family: Calibri;
                font-size: 10pt;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                margin: 2px;
            }
        """)
        
        machine_header_layout.addStretch()
        machine_header_layout.addWidget(machine_label)
        machine_header_layout.addWidget(self.cmbMachineSelect)
        
        # Add multi-selection button for advanced machine selection
        self.btnMultiMachineSelect = QPushButton("Multi-Select")
        self.btnMultiMachineSelect.setFont(QFont("Calibri", 10))
        self.btnMultiMachineSelect.setMaximumWidth(100)
        self.btnMultiMachineSelect.setToolTip("Select multiple machines for comparison")
        self.btnMultiMachineSelect.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                background-color: white;
                font-family: Calibri;
                font-size: 9pt;
            }
            QPushButton:hover {
                border-color: #2196F3;
                background-color: #F5F5F5;
            }
            QPushButton:pressed {
                background-color: #E3F2FD;
            }
        """)
        machine_header_layout.addWidget(self.btnMultiMachineSelect)
        
        # Add machine comparison button
        self.btnMachineComparison = QPushButton("Compare A vs B")
        self.btnMachineComparison.setFont(QFont("Calibri", 10))
        self.btnMachineComparison.setMaximumWidth(120)
        self.btnMachineComparison.setToolTip("Open detailed comparison dialog between two machines")
        self.btnMachineComparison.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        machine_header_layout.addWidget(self.btnMachineComparison)
        
        machine_header_layout.addStretch()
        
        layout.addLayout(machine_header_layout)
        
        # Add machine database status indicator
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.lblMachineStatus = QLabel("Database: Combined (Legacy Mode)")
        self.lblMachineStatus.setFont(QFont("Calibri", 9))
        self.lblMachineStatus.setStyleSheet("""
            QLabel {
                color: #666666;
                background-color: #F5F5F5;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        status_layout.addWidget(self.lblMachineStatus)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        status_group = QGroupBox("System Status")
        status_layout = QGridLayout(status_group)
        status_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.lblSerial = QLabel("Serial: -")
        self.lblSerial.setWordWrap(True)
        self.lblDate = QLabel("Date: -")
        self.lblDate.setWordWrap(True)
        self.lblDuration = QLabel("Duration: -")
        self.lblDuration.setWordWrap(True)

        status_layout.addWidget(self.lblSerial, 0, 0)
        status_layout.addWidget(self.lblDate, 1, 0)
        status_layout.addWidget(self.lblDuration, 2, 0)
        cards_layout.addWidget(status_group)

        data_group = QGroupBox("Data Summary")
        data_layout = QGridLayout(data_group)
        data_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.lblRecordCount = QLabel("Total Records: 0")
        self.lblRecordCount.setWordWrap(True)
        self.lblParameterCount = QLabel("Parameters: 0")
        self.lblParameterCount.setWordWrap(True)

        data_layout.addWidget(self.lblRecordCount, 0, 0)
        data_layout.addWidget(self.lblParameterCount, 1, 0)
        cards_layout.addWidget(data_group)
        cards_layout.addStretch()

        layout.addLayout(cards_layout)
        layout.addStretch()

    def setup_trends_tab(self):
        self.tabTrends = QWidget()
        self.tabWidget.addTab(self.tabTrends, "📈 Trends")
        layout = QVBoxLayout(self.tabTrends)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create sub-tabs for different parameter groups
        self.trendSubTabs = QTabWidget()
        self.trendSubTabs.setTabPosition(QTabWidget.North)
        layout.addWidget(self.trendSubTabs)

        # Water System tab
        self.setup_water_system_tab()
        
        # Voltages tab
        self.setup_voltages_tab()
        
        # Temperatures tab  
        self.setup_temperatures_tab()
        
        # Humidity tab
        self.setup_humidity_tab()
        
        # Fan Speeds tab (NEW)
        self.setup_fan_speeds_tab()

    def setup_water_system_tab(self):
        self.tabWaterSystem = QWidget()
        self.trendSubTabs.addTab(self.tabWaterSystem, "🌊 Water System")
        layout = QVBoxLayout(self.tabWaterSystem)
        layout.setContentsMargins(16, 16, 16, 16)
        
    def setup_water_system_tab(self):
        self.tabWaterSystem = QWidget()
        self.trendSubTabs.addTab(self.tabWaterSystem, "🌊 Water System")
        layout = QVBoxLayout(self.tabWaterSystem)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Controls group with time scale selection
        controls_group = QGroupBox("Water System Controls")
        controls_main_layout = QVBoxLayout(controls_group)
        
        # Time scale controls row
        time_controls_layout = QHBoxLayout()
        time_controls_layout.addWidget(QLabel("Time Range:"))
        
        # Time scale buttons
        self.btnWaterTime1Day = QPushButton("1 Day")
        self.btnWaterTime1Week = QPushButton("1 Week") 
        self.btnWaterTime1Month = QPushButton("1 Month")
        self.btnWaterTimeCustom = QPushButton("Custom Range")
        
        # Style time scale buttons
        time_buttons = [self.btnWaterTime1Day, self.btnWaterTime1Week, 
                       self.btnWaterTime1Month, self.btnWaterTimeCustom]
        for btn in time_buttons:
            btn.setCheckable(True)
            btn.setMinimumWidth(80)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid #ddd;
                    background: white;
                    border-radius: 4px;
                }
                QPushButton:checked {
                    background: #1976D2;
                    color: white;
                    border-color: #1976D2;
                }
                QPushButton:hover:!checked {
                    background: #f5f5f5;
                }
            """)
            time_controls_layout.addWidget(btn)
        
        # Set default selection
        self.btnWaterTime1Day.setChecked(True)
        
        # Create button group for exclusive selection
        self.waterTimeButtonGroup = QButtonGroup()
        for btn in time_buttons:
            self.waterTimeButtonGroup.addButton(btn)
        
        time_controls_layout.addStretch()
        controls_main_layout.addLayout(time_controls_layout)
        
        # Parameter selection controls row
        param_controls_layout = QHBoxLayout()
        param_controls_layout.setSpacing(12)
        
        # Top graph selector
        param_controls_layout.addWidget(QLabel("Top Graph:"))
        self.comboWaterTopGraph = QComboBox()
        self.comboWaterTopGraph.setMinimumWidth(160)
        self.comboWaterTopGraph.addItems([
            "Mag Flow",  # Remove "Select parameter..." and make first item default
            "Flow Target", 
            "Flow Chiller Water",
            "Pump Pressure"  # Updated to match unified parser
        ])
        # Set default selection to first parameter
        self.comboWaterTopGraph.setCurrentIndex(0)
        param_controls_layout.addWidget(self.comboWaterTopGraph)
        
        # Bottom graph selector
        param_controls_layout.addWidget(QLabel("Bottom Graph:"))
        self.comboWaterBottomGraph = QComboBox()
        self.comboWaterBottomGraph.setMinimumWidth(160)
        self.comboWaterBottomGraph.addItems([
            "Pump Pressure",  # Updated to focus on pump pressure
            "Mag Flow",
            "Flow Target",
            "Flow Chiller Water"
        ])
        # Set default selection to pump pressure
        self.comboWaterBottomGraph.setCurrentIndex(0)
        param_controls_layout.addWidget(self.comboWaterBottomGraph)
        
        self.btnRefreshWater = QPushButton("🔄 Update Graphs")
        self.btnRefreshWater.setObjectName("primaryButton")
        param_controls_layout.addWidget(self.btnRefreshWater)
        param_controls_layout.addStretch()
        
        controls_main_layout.addLayout(param_controls_layout)
        layout.addWidget(controls_group)
        
        # Two graphs layout (top and bottom)
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(12)
        
        # FIXED: Use EnhancedPlotWidget instead of QFrame for graph widgets
        if PLOTTING_AVAILABLE:
            self.waterGraphTop = EnhancedPlotWidget()
            self.waterGraphTop.setMinimumHeight(200)
            self.waterGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.waterGraphTop)
            
            self.waterGraphBottom = EnhancedPlotWidget()
            self.waterGraphBottom.setMinimumHeight(200)
            self.waterGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.waterGraphBottom)
        else:
            # Fallback to QFrame with error message
            self.waterGraphTop = QFrame()
            self.waterGraphTop.setFrameStyle(QFrame.Box)
            self.waterGraphTop.setObjectName("plotFrame")
            self.waterGraphTop.setMinimumHeight(200)
            self.waterGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.waterGraphTop)
            
            self.waterGraphBottom = QFrame()
            self.waterGraphBottom.setFrameStyle(QFrame.Box)
            self.waterGraphBottom.setObjectName("plotFrame")
            self.waterGraphBottom.setMinimumHeight(200)
            self.waterGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.waterGraphBottom)
        
        layout.addWidget(graphs_widget)

    def setup_voltages_tab(self):
        self.tabVoltages = QWidget()
        self.trendSubTabs.addTab(self.tabVoltages, "⚡ Voltages")
        layout = QVBoxLayout(self.tabVoltages)
        layout.setContentsMargins(16, 16, 16, 16)
        
    def setup_voltages_tab(self):
        self.tabVoltages = QWidget()
        self.trendSubTabs.addTab(self.tabVoltages, "⚡ Voltages")
        layout = QVBoxLayout(self.tabVoltages)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Controls group with time scale selection
        controls_group = QGroupBox("Voltage Controls")
        controls_main_layout = QVBoxLayout(controls_group)
        
        # Time scale controls row
        time_controls_layout = QHBoxLayout()
        time_controls_layout.addWidget(QLabel("Time Range:"))
        
        # Time scale buttons
        self.btnVoltageTime1Day = QPushButton("1 Day")
        self.btnVoltageTime1Week = QPushButton("1 Week") 
        self.btnVoltageTime1Month = QPushButton("1 Month")
        self.btnVoltageTimeCustom = QPushButton("Custom Range")
        
        # Style time scale buttons
        voltage_time_buttons = [self.btnVoltageTime1Day, self.btnVoltageTime1Week, 
                               self.btnVoltageTime1Month, self.btnVoltageTimeCustom]
        for btn in voltage_time_buttons:
            btn.setCheckable(True)
            btn.setMinimumWidth(80)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid #ddd;
                    background: white;
                    border-radius: 4px;
                }
                QPushButton:checked {
                    background: #1976D2;
                    color: white;
                    border-color: #1976D2;
                }
                QPushButton:hover:!checked {
                    background: #f5f5f5;
                }
            """)
            time_controls_layout.addWidget(btn)
        
        # Set default selection
        self.btnVoltageTime1Day.setChecked(True)
        
        # Create button group for exclusive selection
        self.voltageTimeButtonGroup = QButtonGroup()
        for btn in voltage_time_buttons:
            self.voltageTimeButtonGroup.addButton(btn)
        
        time_controls_layout.addStretch()
        controls_main_layout.addLayout(time_controls_layout)
        
        # Parameter selection controls row
        param_controls_layout = QHBoxLayout()
        param_controls_layout.setSpacing(12)
        
        # Top graph selector
        param_controls_layout.addWidget(QLabel("Top Graph:"))
        self.comboVoltageTopGraph = QComboBox()
        self.comboVoltageTopGraph.setMinimumWidth(160)
        self.comboVoltageTopGraph.addItems([
            "MLC Bank A 24V",  # Remove "Select parameter..." and make first item default
            "MLC Bank B 24V",
            "COL 48V",
            "MLC Bank A 48V",
            "MLC Bank B 48V",
            "MLC Bank A 5V",
            "MLC Bank B 5V",
            "MLC DISTAL 10V",
            "MLC PROXIMAL 10V",
            "Motor PWR 48V",
            "Motor PWR -48V"
        ])
        # Set default selection to first parameter
        self.comboVoltageTopGraph.setCurrentIndex(0)
        param_controls_layout.addWidget(self.comboVoltageTopGraph)
        
        # Bottom graph selector
        param_controls_layout.addWidget(QLabel("Bottom Graph:"))
        self.comboVoltageBottomGraph = QComboBox()
        self.comboVoltageBottomGraph.setMinimumWidth(160)
        self.comboVoltageBottomGraph.addItems([
            "MLC Bank B 24V",  # Remove "Select parameter..." and set different default
            "MLC Bank A 24V",
            "COL 48V",
            "MLC Bank A 48V", 
            "MLC Bank B 48V",
            "MLC Bank A 5V",
            "MLC Bank B 5V",
            "MLC DISTAL 10V",
            "MLC PROXIMAL 10V",
            "Motor PWR 48V",
            "Motor PWR -48V"
        ])
        # Set default selection to first parameter (different from top graph)
        self.comboVoltageBottomGraph.setCurrentIndex(0)
        param_controls_layout.addWidget(self.comboVoltageBottomGraph)
        
        self.btnRefreshVoltage = QPushButton("🔄 Update Graphs")
        self.btnRefreshVoltage.setObjectName("primaryButton")
        param_controls_layout.addWidget(self.btnRefreshVoltage)
        param_controls_layout.addStretch()
        
        controls_main_layout.addLayout(param_controls_layout)
        layout.addWidget(controls_group)
        
        # Two graphs layout (top and bottom)
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(12)
        
        # FIXED: Use EnhancedPlotWidget instead of QFrame for voltage graph widgets
        if PLOTTING_AVAILABLE:
            self.voltageGraphTop = EnhancedPlotWidget()
            self.voltageGraphTop.setMinimumHeight(200)
            self.voltageGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.voltageGraphTop)
            
            self.voltageGraphBottom = EnhancedPlotWidget()
            self.voltageGraphBottom.setMinimumHeight(200)
            self.voltageGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.voltageGraphBottom)
        else:
            # Fallback to QFrame with error message
            self.voltageGraphTop = QFrame()
            self.voltageGraphTop.setFrameStyle(QFrame.Box)
            self.voltageGraphTop.setObjectName("plotFrame")
            self.voltageGraphTop.setMinimumHeight(200)
            self.voltageGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.voltageGraphTop)
            
            self.voltageGraphBottom = QFrame()
            self.voltageGraphBottom.setFrameStyle(QFrame.Box)
            self.voltageGraphBottom.setObjectName("plotFrame")
            self.voltageGraphBottom.setMinimumHeight(200)
            self.voltageGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.voltageGraphBottom)
        
        layout.addWidget(graphs_widget)

    def setup_temperatures_tab(self):
        self.tabTemperatures = QWidget()
        self.trendSubTabs.addTab(self.tabTemperatures, "🌡️ Temperatures")
        layout = QVBoxLayout(self.tabTemperatures)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Controls
        controls_group = QGroupBox("Temperature Graph Selection")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(12)
        
        # Top graph selector
        controls_layout.addWidget(QLabel("Top Graph:"))
        self.comboTempTopGraph = QComboBox()
        self.comboTempTopGraph.setMinimumWidth(160)
        self.comboTempTopGraph.addItems([
            "Temp Room",  # Remove "Select parameter..." and make first item default
            "Temp PDU",
            "Temp COL Board",
            "Temp Magnetron",
            "Temp Water Tank",
            "Temp MLC Bank A",
            "Temp MLC Bank B"
        ])
        # Set default selection to first parameter
        self.comboTempTopGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboTempTopGraph)
        
        # Bottom graph selector
        controls_layout.addWidget(QLabel("Bottom Graph:"))
        self.comboTempBottomGraph = QComboBox()
        self.comboTempBottomGraph.setMinimumWidth(160)
        self.comboTempBottomGraph.addItems([
            "Temp PDU",  # Remove "Select parameter..." and set different default from top
            "Temp Room", 
            "Temp COL Board",
            "Temp Magnetron",
            "Temp Water Tank",
            "Temp MLC Bank A",
            "Temp MLC Bank B"
        ])
        # Set default selection to first parameter (different from top graph)
        self.comboTempBottomGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboTempBottomGraph)
        
        self.btnRefreshTemp = QPushButton("Update Graphs")
        self.btnRefreshTemp.setObjectName("primaryButton")
        controls_layout.addWidget(self.btnRefreshTemp)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Two graphs layout (top and bottom)
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(12)
        
        # FIXED: Use EnhancedPlotWidget instead of QFrame for temperature graph widgets
        if PLOTTING_AVAILABLE:
            self.tempGraphTop = EnhancedPlotWidget()
            self.tempGraphTop.setMinimumHeight(200)
            self.tempGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.tempGraphTop)
            
            self.tempGraphBottom = EnhancedPlotWidget()
            self.tempGraphBottom.setMinimumHeight(200)
            self.tempGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.tempGraphBottom)
        else:
            # Fallback to QFrame with error message
            self.tempGraphTop = QFrame()
            self.tempGraphTop.setFrameStyle(QFrame.Box)
            self.tempGraphTop.setObjectName("plotFrame")
            self.tempGraphTop.setMinimumHeight(200)
            self.tempGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.tempGraphTop)
            
            self.tempGraphBottom = QFrame()
            self.tempGraphBottom.setFrameStyle(QFrame.Box)
            self.tempGraphBottom.setObjectName("plotFrame")
            self.tempGraphBottom.setMinimumHeight(200)
            self.tempGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.tempGraphBottom)
        
        layout.addWidget(graphs_widget)

    def setup_humidity_tab(self):
        self.tabHumidity = QWidget()
        self.trendSubTabs.addTab(self.tabHumidity, "💧 Humidity")
        layout = QVBoxLayout(self.tabHumidity)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Controls
        controls_group = QGroupBox("Humidity Graph Selection")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(12)
        
        # Top graph selector
        controls_layout.addWidget(QLabel("Top Graph:"))
        self.comboHumidityTopGraph = QComboBox()
        self.comboHumidityTopGraph.setMinimumWidth(160)
        self.comboHumidityTopGraph.addItems([
            "Room Humidity",  # Remove "Select parameter..." and make first item default
            "Temp Room"  # Per requirements: include room temp in humidity tab
        ])
        # Set default selection to first parameter
        self.comboHumidityTopGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboHumidityTopGraph)
        
        # Bottom graph selector
        controls_layout.addWidget(QLabel("Bottom Graph:"))
        self.comboHumidityBottomGraph = QComboBox()
        self.comboHumidityBottomGraph.setMinimumWidth(160)
        self.comboHumidityBottomGraph.addItems([
            "Temp Room",  # Remove "Select parameter..." and set different default
            "Room Humidity"
        ])
        # Set default selection to first parameter (different from top graph)
        self.comboHumidityBottomGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboHumidityBottomGraph)
        
        self.btnRefreshHumidity = QPushButton("Update Graphs")
        self.btnRefreshHumidity.setObjectName("primaryButton")
        controls_layout.addWidget(self.btnRefreshHumidity)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Two graphs layout (top and bottom)
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(12)
        
        # FIXED: Use EnhancedPlotWidget instead of QFrame for humidity graph widgets
        if PLOTTING_AVAILABLE:
            self.humidityGraphTop = EnhancedPlotWidget()
            self.humidityGraphTop.setMinimumHeight(200)
            self.humidityGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.humidityGraphTop)
            
            self.humidityGraphBottom = EnhancedPlotWidget()
            self.humidityGraphBottom.setMinimumHeight(200)
            self.humidityGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.humidityGraphBottom)
        else:
            # Fallback to QFrame with error message
            self.humidityGraphTop = QFrame()
            self.humidityGraphTop.setFrameStyle(QFrame.Box)
            self.humidityGraphTop.setObjectName("plotFrame")
            self.humidityGraphTop.setMinimumHeight(200)
            self.humidityGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.humidityGraphTop)
            
            self.humidityGraphBottom = QFrame()
            self.humidityGraphBottom.setFrameStyle(QFrame.Box)
            self.humidityGraphBottom.setObjectName("plotFrame")
            self.humidityGraphBottom.setMinimumHeight(200)
            self.humidityGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.humidityGraphBottom)
        
        layout.addWidget(graphs_widget)

    def setup_fan_speeds_tab(self):
        self.tabFanSpeeds = QWidget()
        self.trendSubTabs.addTab(self.tabFanSpeeds, "🌀 Fan Speeds")
        layout = QVBoxLayout(self.tabFanSpeeds)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Controls
        controls_group = QGroupBox("Fan Speed Graph Selection")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(12)
        
        # Top graph selector
        controls_layout.addWidget(QLabel("Top Graph:"))
        self.comboFanTopGraph = QComboBox()
        self.comboFanTopGraph.setMinimumWidth(160)
        self.comboFanTopGraph.addItems([
            "Speed FAN 1",  # Remove "Select parameter..." and make first item default
            "Speed FAN 2",
            "Speed FAN 3",
            "Speed FAN 4"
        ])
        # Set default selection to first parameter
        self.comboFanTopGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboFanTopGraph)
        
        # Bottom graph selector
        controls_layout.addWidget(QLabel("Bottom Graph:"))
        self.comboFanBottomGraph = QComboBox()
        self.comboFanBottomGraph.setMinimumWidth(160)
        self.comboFanBottomGraph.addItems([
            "Speed FAN 2",  # Remove "Select parameter..." and set different default
            "Speed FAN 1",
            "Speed FAN 3",
            "Speed FAN 4"
        ])
        # Set default selection to first parameter (different from top graph)
        self.comboFanBottomGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboFanBottomGraph)
        
        self.btnRefreshFan = QPushButton("Update Graphs")
        self.btnRefreshFan.setObjectName("primaryButton")
        controls_layout.addWidget(self.btnRefreshFan)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Two graphs layout (top and bottom)
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(12)
        
        # FIXED: Use EnhancedPlotWidget instead of QFrame for fan speed graph widgets
        if PLOTTING_AVAILABLE:
            self.fanGraphTop = EnhancedPlotWidget()
            self.fanGraphTop.setMinimumHeight(200)
            self.fanGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.fanGraphTop)
            
            self.fanGraphBottom = EnhancedPlotWidget()
            self.fanGraphBottom.setMinimumHeight(200)
            self.fanGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.fanGraphBottom)
        else:
            # Fallback to QFrame with error message
            self.fanGraphTop = QFrame()
            self.fanGraphTop.setFrameStyle(QFrame.Box)
            self.fanGraphTop.setObjectName("plotFrame")
            self.fanGraphTop.setMinimumHeight(200)
            self.fanGraphTop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.fanGraphTop)
            
            self.fanGraphBottom = QFrame()
            self.fanGraphBottom.setFrameStyle(QFrame.Box)
            self.fanGraphBottom.setObjectName("plotFrame")
            self.fanGraphBottom.setMinimumHeight(200)
            self.fanGraphBottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graphs_layout.addWidget(self.fanGraphBottom)
        
        layout.addWidget(graphs_widget)

    def setup_analysis_tab(self):
        self.tabAnalysis = QWidget()
        self.tabWidget.addTab(self.tabAnalysis, "🔬 Analysis")
        layout = QVBoxLayout(self.tabAnalysis)
        layout.setContentsMargins(20, 20, 20, 20)

        # Analysis controls
        controls_group = QGroupBox("Analysis Controls")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(12)
        controls_layout.setContentsMargins(16, 16, 16, 16)
        
        # Parameter filter
        controls_layout.addWidget(QLabel("Filter Parameters:"))
        self.comboAnalysisFilter = QComboBox()
        self.comboAnalysisFilter.setMinimumWidth(150)
        self.comboAnalysisFilter.addItems([
            "All Parameters",
            "Water System",
            "Voltages", 
            "Temperatures",
            "Fan Speeds",
            "Humidity"
        ])
        controls_layout.addWidget(self.comboAnalysisFilter)
        
        # Machine selection for analysis
        controls_layout.addWidget(QLabel("Machine:"))
        self.comboAnalysisMachine = QComboBox()
        self.comboAnalysisMachine.setMinimumWidth(150)
        self.comboAnalysisMachine.addItems(["All Machines"])  # Will be populated dynamically
        controls_layout.addWidget(self.comboAnalysisMachine)
        
        # Refresh button
        self.btnRefreshAnalysis = QPushButton("Refresh Analysis")
        self.btnRefreshAnalysis.setObjectName("primaryButton")
        controls_layout.addWidget(self.btnRefreshAnalysis)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)

        # Enhanced trends analysis table
        trends_group = QGroupBox("Enhanced Parameter Trend Analysis")
        trends_layout = QVBoxLayout(trends_group)

        self.tableTrends = QTableWidget()
        self.tableTrends.setAlternatingRowColors(True)
        self.tableTrends.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableTrends.setColumnCount(8)  # Added one more column
        self.tableTrends.setHorizontalHeaderLabels(
            [
                "Parameter",
                "Group",  # New column for parameter group
                "Statistic",
                "Data Points",
                "Time Span (hrs)",
                "Slope",
                "Direction",
                "Strength",
            ]
        )
        
        # Enhanced column sizing for better display
        header = self.tableTrends.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Parameter - resizable
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Group - fit content
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Statistic - fit content
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Data Points - fit content
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Time Span - fit content
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Slope - stretch
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Direction - fit content
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Strength - fit content
        
        # Set minimum column widths
        header.setMinimumSectionSize(120)
        header.resizeSection(0, 200)  # Parameter column wider
        
        # Enhanced table styling for better readability
        self.tableTrends.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                font-size: 11px;
                selection-background-color: #E3F2FD;
                background-color: #FAFAFA;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #0D47A1;
            }
            QTableWidget::item:alternate {
                background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        # Add scroll policies and minimum height
        self.tableTrends.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableTrends.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableTrends.setMinimumHeight(400)
        
        trends_layout.addWidget(self.tableTrends)
        layout.addWidget(trends_group)

    def setup_mpc_tab(self):
        self.tabMPC = QWidget()
        self.tabWidget.addTab(self.tabMPC, "🔧 MPC")
        layout = QVBoxLayout(self.tabMPC)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("<h2>Machine Performance Check Results</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # MPC data controls
        info_group = QGroupBox("MPC Data Controls")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(16, 16, 16, 16)
        
        # Date selection row
        date_row = QHBoxLayout()
        
        date_label = QLabel("Select Date:")
        date_label.setMinimumWidth(80)
        date_row.addWidget(date_label)
        
        self.comboMPCDate = QComboBox()
        self.comboMPCDate.setMinimumWidth(150)
        self.comboMPCDate.addItem("Select date...")
        date_row.addWidget(self.comboMPCDate)
        
        date_row.addStretch()
        
        # Refresh button
        self.btnRefreshMPC = QPushButton("Load MPC Data")
        self.btnRefreshMPC.setObjectName("primaryButton")
        self.btnRefreshMPC.setMaximumWidth(150)
        date_row.addWidget(self.btnRefreshMPC)
        
        info_layout.addLayout(date_row)
        
        # Status info row
        status_row = QHBoxLayout()
        self.lblLastMPCUpdate = QLabel("Select a date to view MPC data")
        self.lblLastMPCUpdate.setWordWrap(True)
        status_row.addWidget(self.lblLastMPCUpdate)
        status_row.addStretch()
        info_layout.addLayout(status_row)
        
        layout.addWidget(info_group)

        # Results table with responsive design
        results_group = QGroupBox("Latest MPC Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(16, 16, 16, 16)

        self.tableMPC = QTableWidget()
        self.tableMPC.setAlternatingRowColors(True)
        self.tableMPC.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableMPC.setColumnCount(3)  # Simplified: Parameter, Value, Status
        self.tableMPC.setHorizontalHeaderLabels([
            "Parameter",
            "Value", 
            "Status"
        ])
        
        # Set responsive column widths with better text handling
        header = self.tableMPC.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Parameter - allow resize
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)     # Value - fit content
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status - fit content
        
        # Set minimum column widths for parameter names
        header.setMinimumSectionSize(200)  # Minimum width for parameter column
        header.resizeSection(0, 350)  # Increased default width for parameter column
        
        # Enhanced text wrapping and row height management
        self.tableMPC.setWordWrap(True)
        self.tableMPC.setTextElideMode(Qt.ElideNone)
        self.tableMPC.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableMPC.setMinimumHeight(500)  # Increased minimum height
        
        # Enable better text display with automatic row height adjustment
        self.tableMPC.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableMPC.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Enhanced styling for better content handling and visual appeal
        self.tableMPC.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                font-size: 12px;
                line-height: 1.4;
                background-color: #FAFAFA;
                border: 1px solid #DDDDDD;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 10px;
                border: 1px solid #E0E0E0;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #0D47A1;
            }
            QTableWidget::item:alternate {
                background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QScrollBar:vertical {
                background-color: #F0F0F0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #CCCCCC;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #999999;
            }
        """)
        
        results_layout.addWidget(self.tableMPC)
        layout.addWidget(results_group)

        # Enhanced statistics display
        stats_group = QGroupBox("MPC Summary")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setContentsMargins(16, 16, 16, 16)

        # Summary metrics in a grid layout
        metrics_layout = QGridLayout()
        
        self.lblTotalParams = QLabel("Total Parameters: -")
        self.lblPassedParams = QLabel("Passed: -")
        self.lblFailedParams = QLabel("Failed: -")
        self.lblWarningParams = QLabel("Warnings: -")
        
        # Style the summary labels
        for label in [self.lblTotalParams, self.lblPassedParams, self.lblFailedParams, self.lblWarningParams]:
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #F5F5F5;
                    margin: 2px;
                }
            """)
        
        metrics_layout.addWidget(self.lblTotalParams, 0, 0)
        metrics_layout.addWidget(self.lblPassedParams, 0, 1)
        metrics_layout.addWidget(self.lblFailedParams, 0, 2)
        metrics_layout.addWidget(self.lblWarningParams, 0, 3)
        
        stats_layout.addLayout(metrics_layout)
        
        # Additional info
        self.lblMPCStats = QLabel("Load MPC data to view detailed statistics")
        self.lblMPCStats.setWordWrap(True)
        self.lblMPCStats.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.lblMPCStats)

        layout.addWidget(stats_group)

        stats_layout.addStretch()
        layout.addWidget(stats_group)

        # MPC data will be loaded from actual log files when available

    

    def setup_fault_code_tab(self):
        self.tabFaultCode = QWidget()
        self.tabWidget.addTab(self.tabFaultCode, "🔍 Fault Code Viewer")
        layout = QVBoxLayout(self.tabFaultCode)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("<h2>LINAC Fault Code Viewer</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        search_group = QGroupBox("Search Fault Codes")
        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(12)
        search_layout.setContentsMargins(16, 16, 16, 16)

        code_input_layout = QHBoxLayout()
        code_label = QLabel("Enter Fault Code:")
        code_label.setMinimumWidth(120)
        code_input_layout.addWidget(code_label)

        self.txtFaultCode = QLineEdit()
        self.txtFaultCode.setPlaceholderText("e.g., 400027")
        self.txtFaultCode.setMaximumWidth(200)
        code_input_layout.addWidget(self.txtFaultCode)

        self.btnSearchCode = QPushButton("Search Code")
        self.btnSearchCode.setObjectName("primaryButton")
        self.btnSearchCode.setMaximumWidth(120)
        code_input_layout.addWidget(self.btnSearchCode)

        code_input_layout.addStretch()
        search_layout.addLayout(code_input_layout)

        desc_input_layout = QHBoxLayout()
        desc_label = QLabel("Search Description:")
        desc_label.setMinimumWidth(120)
        desc_input_layout.addWidget(desc_label)

        self.txtSearchDescription = QLineEdit()
        self.txtSearchDescription.setPlaceholderText("Enter keywords to search in descriptions...")
        desc_input_layout.addWidget(self.txtSearchDescription)

        self.btnSearchDescription = QPushButton("Search Description")
        self.btnSearchDescription.setObjectName("secondaryButton")
        self.btnSearchDescription.setMaximumWidth(150)
        desc_input_layout.addWidget(self.btnSearchDescription)

        search_layout.addLayout(desc_input_layout)
        layout.addWidget(search_group)

        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(16, 16, 16, 16)

        self.txtFaultResult = QTextEdit()
        self.txtFaultResult.setReadOnly(True)
        self.txtFaultResult.setMinimumHeight(150)
        self.txtFaultResult.setPlaceholderText("Search results will appear here...")
        results_layout.addWidget(self.txtFaultResult)

        # Add HAL and TB Description text boxes
        descriptions_layout = QHBoxLayout()
        descriptions_layout.setSpacing(12)
        
        # HAL Description box
        hal_group = QGroupBox("HAL Description")
        hal_layout = QVBoxLayout(hal_group)
        hal_layout.setContentsMargins(8, 8, 8, 8)
        
        self.txtHALDescription = QTextEdit()
        self.txtHALDescription.setReadOnly(True)
        self.txtHALDescription.setMaximumHeight(120)
        self.txtHALDescription.setPlaceholderText("HAL fault description will appear here...")
        hal_layout.addWidget(self.txtHALDescription)
        
        # TB Description box
        tb_group = QGroupBox("TB Description")
        tb_layout = QVBoxLayout(tb_group)
        tb_layout.setContentsMargins(8, 8, 8, 8)
        
        self.txtTBDescription = QTextEdit()
        self.txtTBDescription.setReadOnly(True)
        self.txtTBDescription.setMaximumHeight(120)
        self.txtTBDescription.setPlaceholderText("TB fault description will appear here...")
        tb_layout.addWidget(self.txtTBDescription)
        
        descriptions_layout.addWidget(hal_group)
        descriptions_layout.addWidget(tb_group)
        
        results_layout.addLayout(descriptions_layout)
        
        # Add User Notes section
        notes_group = QGroupBox("User Notes")
        notes_layout = QVBoxLayout(notes_group)
        notes_layout.setContentsMargins(8, 8, 8, 8)
        
        # Note display area
        self.txtUserNote = QTextEdit()
        self.txtUserNote.setMaximumHeight(100)
        self.txtUserNote.setPlaceholderText("Add your own notes about this fault code here...")
        notes_layout.addWidget(self.txtUserNote)
        
        # Note controls
        note_controls_layout = QVBoxLayout()
        note_controls_layout.setSpacing(8)
        
        # Machine selection for notes (when fault exists in both databases)
        machine_selection_layout = QHBoxLayout()
        machine_selection_layout.setSpacing(12)
        
        machine_selection_label = QLabel("Applies to:")
        machine_selection_label.setStyleSheet("font-weight: 500; color: #333;")
        machine_selection_layout.addWidget(machine_selection_label)
        
        self.note_machine_group = QButtonGroup()
        
        self.rbNoteBoth = QRadioButton("Both Machines")
        self.rbNoteBoth.setChecked(True)  # Default selection
        self.note_machine_group.addButton(self.rbNoteBoth, 0)
        machine_selection_layout.addWidget(self.rbNoteBoth)
        
        self.rbNoteHAL = QRadioButton("HAL Only")
        self.note_machine_group.addButton(self.rbNoteHAL, 1)
        machine_selection_layout.addWidget(self.rbNoteHAL)
        
        self.rbNoteTB = QRadioButton("TB Only")
        self.note_machine_group.addButton(self.rbNoteTB, 2)
        machine_selection_layout.addWidget(self.rbNoteTB)
        
        machine_selection_layout.addStretch()
        note_controls_layout.addLayout(machine_selection_layout)
        
        # Button row
        button_row_layout = QHBoxLayout()
        button_row_layout.setSpacing(8)
        
        self.btnSaveNote = QPushButton("Save Note")
        self.btnSaveNote.setObjectName("primaryButton")
        self.btnSaveNote.setMaximumWidth(100)
        button_row_layout.addWidget(self.btnSaveNote)
        
        self.btnClearNote = QPushButton("Clear Note")
        self.btnClearNote.setObjectName("secondaryButton")
        self.btnClearNote.setMaximumWidth(100)
        button_row_layout.addWidget(self.btnClearNote)
        
        button_row_layout.addStretch()
        
        # Note info label
        self.lblNoteInfo = QLabel("")
        self.lblNoteInfo.setStyleSheet("color: #666; font-size: 11px;")
        button_row_layout.addWidget(self.lblNoteInfo)
        
        note_controls_layout.addLayout(button_row_layout)
        
        notes_layout.addLayout(note_controls_layout)
        
        results_layout.addWidget(notes_group)
        layout.addWidget(results_group)

        stats_group = QGroupBox("Fault Code Statistics")
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setContentsMargins(16, 16, 16, 16)

        self.lblTotalCodes = QLabel("Total Codes: Loading...")
        self.lblTotalCodes.setWordWrap(True)
        stats_layout.addWidget(self.lblTotalCodes)

        self.lblFaultTypes = QLabel("Types: Loading...")
        self.lblFaultTypes.setWordWrap(True)
        stats_layout.addWidget(self.lblFaultTypes)

        stats_layout.addStretch()
        layout.addWidget(stats_group)

        layout.addStretch()

    def setup_about_tab(self):
        self.tabAbout = QWidget()
        self.tabWidget.addTab(self.tabAbout, "ℹ️ About")
        layout = QVBoxLayout(self.tabAbout)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        logo_label = QLabel("🏥")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px; margin: 20px;")
        layout.addWidget(logo_label)

        app_info = QLabel(
            "<h2>Gobioeng HALog 0.0.1 beta</h2>"
            "<p>A professional LINAC water system monitoring application</p>"
            "<p>Developed by <b>gobioeng.com</b></p>"
            "<p><a href='https://gobioeng.com'>gobioeng.com</a></p>"
            "<p>© 2025 Gobioeng. All rights reserved.</p>"
        )
        app_info.setAlignment(Qt.AlignCenter)
        app_info.setOpenExternalLinks(True)
        app_info.setWordWrap(True)
        layout.addWidget(app_info)
        layout.addStretch()


class MultiMachineSelectionDialog(QDialog):
    """Dialog for selecting multiple machines with color indicators"""
    
    def __init__(self, available_machines, selected_machines=None, machine_manager=None, parent=None):
        super().__init__(parent)
        self.available_machines = available_machines
        self.selected_machines = selected_machines or []
        self.machine_manager = machine_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI with color indicators"""
        self.setWindowTitle("Select Machines for Analysis")
        self.setModal(True)
        self.resize(450, 550)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h3>Multi-Machine Selection</h3>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions with color info
        instructions = QLabel(
            "Select one or more machines to analyze. "
            "Each machine will be displayed with its assigned color in trend graphs. "
            "Colors are assigned consistently across all visualizations."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin: 10px 0; padding: 5px; background: #f8f9fa; border-radius: 4px;")
        layout.addWidget(instructions)
        
        # Machine list with checkboxes and color indicators
        self.machine_list = QListWidget()
        self.machine_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 5px;
                background: white;
            }
            QListWidget::item {
                padding: 2px;
                border-bottom: 1px solid #F0F0F0;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
                border-radius: 4px;
            }
        """)
        
        # Add machines to list with color indicators
        for machine in self.available_machines:
            item = QListWidgetItem()
            
            # Create container widget for checkbox and color indicator
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            
            # Get machine color from manager
            machine_color = '#1976D2'  # Default color
            if self.machine_manager:
                try:
                    machine_color = self.machine_manager.get_machine_color(machine)
                except:
                    pass
            
            # Color indicator (colored circle)
            color_label = QLabel("●")
            color_label.setStyleSheet(f"color: {machine_color}; font-size: 16px; font-weight: bold;")
            color_label.setFixedWidth(20)
            container_layout.addWidget(color_label)
            
            # Checkbox with machine name
            checkbox = QCheckBox(f"Machine: {machine}")
            checkbox.setFont(QFont("Calibri", 10))
            
            if machine in self.selected_machines:
                checkbox.setChecked(True)
                
            container_layout.addWidget(checkbox)
            container_layout.addStretch()
            
            # Store color info for later reference
            checkbox.machine_color = machine_color
            checkbox.machine_id = machine
            
            item.setSizeHint(container.sizeHint())
            self.machine_list.addItem(item)
            self.machine_list.setItemWidget(item, container)
        
        layout.addWidget(self.machine_list)
        
        # Selection info panel
        self.selection_info = QLabel()
        self.update_selection_info()
        self.selection_info.setStyleSheet("""
            background: #e3f2fd; 
            border: 1px solid #2196f3; 
            border-radius: 4px; 
            padding: 8px; 
            margin: 5px 0;
            font-weight: bold;
        """)
        layout.addWidget(self.selection_info)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Select All / None buttons
        btn_select_all = QPushButton("Select All")
        btn_select_all.clicked.connect(self.select_all)
        btn_select_all.setToolTip("Select all available machines")
        
        btn_select_none = QPushButton("Clear All")
        btn_select_none.clicked.connect(self.select_none)
        btn_select_none.setToolTip("Clear all machine selections")
        
        btn_compare = QPushButton("Compare Selected")
        btn_compare.clicked.connect(self.compare_selected)
        btn_compare.setToolTip("Open comparison view for selected machines")
        
        button_layout.addWidget(btn_select_all)
        button_layout.addWidget(btn_select_none)
        button_layout.addWidget(btn_compare)
        button_layout.addStretch()
        
        # OK/Cancel buttons
        btn_ok = QPushButton("Apply Selection")
        btn_ok.setObjectName("primaryButton")
        btn_ok.clicked.connect(self.accept)
        btn_ok.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background-color: #1976D2;
            }
        """)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        # Connect checkbox changes to update selection info
        for i in range(self.machine_list.count()):
            item = self.machine_list.item(i)
            container = self.machine_list.itemWidget(item)
            checkbox = container.findChild(QCheckBox)
            if checkbox:
                checkbox.stateChanged.connect(self.update_selection_info)
                
    def update_selection_info(self):
        """Update the selection information panel"""
        selected = self.get_selected_machines()
        count = len(selected)
        
        if count == 0:
            self.selection_info.setText("No machines selected")
            self.selection_info.setStyleSheet("background: #ffecb3; border: 1px solid #ff9800; border-radius: 4px; padding: 8px; margin: 5px 0;")
        elif count == 1:
            self.selection_info.setText(f"Selected: {selected[0]} (single machine mode)")
            self.selection_info.setStyleSheet("background: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 8px; margin: 5px 0;")
        else:
            machine_list = ", ".join(selected[:3])
            if count > 3:
                machine_list += f" (+{count-3} more)"
            self.selection_info.setText(f"Selected: {machine_list} (multi-machine comparison mode)")
            self.selection_info.setStyleSheet("background: #e3f2fd; border: 1px solid #2196f3; border-radius: 4px; padding: 8px; margin: 5px 0; font-weight: bold;")
    
    def select_all(self):
        """Select all machines"""
        for i in range(self.machine_list.count()):
            item = self.machine_list.item(i)
            container = self.machine_list.itemWidget(item)
            checkbox = container.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(True)
        self.update_selection_info()
    
    def select_none(self):
        """Deselect all machines"""
        for i in range(self.machine_list.count()):
            item = self.machine_list.item(i)
            container = self.machine_list.itemWidget(item)
            checkbox = container.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(False)
        self.update_selection_info()
        
    def compare_selected(self):
        """Open comparison view for selected machines (placeholder for now)"""
        selected = self.get_selected_machines()
        if len(selected) < 2:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Selection Required",
                "Please select at least 2 machines to compare."
            )
        else:
            # For now, just accept the dialog - actual comparison would be handled by parent
            self.accept()
    
    def get_selected_machines(self):
        """Get list of selected machine IDs"""
        selected = []
        for i in range(self.machine_list.count()):
            item = self.machine_list.item(i)
            container = self.machine_list.itemWidget(item)
            checkbox = container.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                # Extract machine ID from text "Machine: ID"
                machine_id = checkbox.text().replace("Machine: ", "")
                selected.append(machine_id)
        return selected
    
    def get_machine_color_mapping(self):
        """Get mapping of selected machines to their colors"""
        color_mapping = {}
        for i in range(self.machine_list.count()):
            item = self.machine_list.item(i)
            container = self.machine_list.itemWidget(item)
            checkbox = container.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                machine_id = checkbox.text().replace("Machine: ", "")
                color_mapping[machine_id] = getattr(checkbox, 'machine_color', '#1976D2')
        return color_mapping


class MachineComparisonDialog(QDialog):
    """Machine comparison dialog with side-by-side analysis"""
    
    def __init__(self, machine_manager, parent=None):
        super().__init__(parent)
        self.machine_manager = machine_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the comparison dialog UI"""
        self.setWindowTitle("Machine A vs Machine B Comparison")
        self.setModal(True)
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h3>🔄 Machine Comparison Analysis</h3>")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin: 10px 0; color: #1976D2;")
        layout.addWidget(title)
        
        # Selection panel
        selection_panel = self.create_selection_panel()
        layout.addWidget(selection_panel)
        
        # Comparison content (tabbed interface)
        self.comparison_tabs = QTabWidget()
        
        # Charts tab
        self.charts_tab = self.create_charts_tab()
        self.comparison_tabs.addTab(self.charts_tab, "📊 Charts")
        
        # Statistics tab  
        self.statistics_tab = self.create_statistics_tab()
        self.comparison_tabs.addTab(self.statistics_tab, "📈 Statistics")
        
        # Export tab
        self.export_tab = self.create_export_tab()
        self.comparison_tabs.addTab(self.export_tab, "📄 Export")
        
        layout.addWidget(self.comparison_tabs)
        
        # Button panel
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Comparison")
        refresh_btn.clicked.connect(self.refresh_comparison)
        refresh_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; }")
        
        export_btn = QPushButton("📊 Export Report")
        export_btn.clicked.connect(self.export_comparison_report)
        export_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px 16px; border-radius: 4px; }")
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def create_selection_panel(self):
        """Create the machine and parameter selection panel"""
        panel = QGroupBox("Selection")
        layout = QHBoxLayout(panel)
        
        # Machine A selector
        layout.addWidget(QLabel("Machine A:"))
        self.machine_a_combo = QComboBox()
        self.machine_a_combo.addItem("Select Machine A...")
        if self.machine_manager:
            for machine in self.machine_manager.get_available_machines():
                self.machine_a_combo.addItem(machine)
        self.machine_a_combo.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.machine_a_combo)
        
        # VS indicator
        vs_label = QLabel("🆚")
        vs_label.setStyleSheet("font-size: 20px; color: #FF5722; font-weight: bold;")
        layout.addWidget(vs_label)
        
        # Machine B selector
        layout.addWidget(QLabel("Machine B:"))
        self.machine_b_combo = QComboBox()
        self.machine_b_combo.addItem("Select Machine B...")
        if self.machine_manager:
            for machine in self.machine_manager.get_available_machines():
                self.machine_b_combo.addItem(machine)
        self.machine_b_combo.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.machine_b_combo)
        
        # Parameter selector
        layout.addWidget(QLabel("Parameter:"))
        self.parameter_combo = QComboBox()
        self.parameter_combo.addItem("Select Parameter...")
        # Add common LINAC parameters
        parameters = [
            "magnetronFlow", "magnetronTemp", "targetAndCirculatorFlow",
            "FanremoteTempStatistics", "FanhumidityStatistics",
            "MLC_ADC_CHAN_TEMP_BANKA_STAT_24V", "MLC_ADC_CHAN_TEMP_BANKB_STAT_24V"
        ]
        self.parameter_combo.addItems(parameters)
        self.parameter_combo.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.parameter_combo)
        
        return panel
        
    def create_charts_tab(self):
        """Create the charts comparison tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Side-by-side plots
        from PyQt5.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Machine A plot
        machine_a_frame = QGroupBox("Machine A")
        machine_a_layout = QVBoxLayout(machine_a_frame)
        
        # Try to import the enhanced plot widget
        try:
            from plot_utils import EnhancedPlotWidget
            self.machine_a_plot = EnhancedPlotWidget()
            machine_a_layout.addWidget(self.machine_a_plot)
        except ImportError:
            machine_a_layout.addWidget(QLabel("Enhanced plotting not available"))
            self.machine_a_plot = None
            
        splitter.addWidget(machine_a_frame)
        
        # Machine B plot  
        machine_b_frame = QGroupBox("Machine B")
        machine_b_layout = QVBoxLayout(machine_b_frame)
        
        try:
            from plot_utils import EnhancedPlotWidget
            self.machine_b_plot = EnhancedPlotWidget()
            machine_b_layout.addWidget(self.machine_b_plot)
        except ImportError:
            machine_b_layout.addWidget(QLabel("Enhanced plotting not available"))
            self.machine_b_plot = None
            
        splitter.addWidget(machine_b_frame)
        
        layout.addWidget(splitter)
        
        return tab
        
    def create_statistics_tab(self):
        """Create the statistics comparison tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Statistics table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(3)
        self.stats_table.setHorizontalHeaderLabels(["Statistic", "Machine A", "Machine B"])
        
        # Style the table
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        layout.addWidget(self.stats_table)
        
        # Comparison summary
        self.comparison_summary = QTextEdit()
        self.comparison_summary.setMaximumHeight(150)
        self.comparison_summary.setReadOnly(True)
        self.comparison_summary.setPlaceholderText("Statistical comparison summary will appear here...")
        layout.addWidget(self.comparison_summary)
        
        return tab
        
    def create_export_tab(self):
        """Create the export options tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout(export_group)
        
        self.export_data_cb = QCheckBox("Export raw comparison data")
        self.export_data_cb.setChecked(True)
        export_layout.addWidget(self.export_data_cb)
        
        self.export_stats_cb = QCheckBox("Export statistical summary")
        self.export_stats_cb.setChecked(True)
        export_layout.addWidget(self.export_stats_cb)
        
        self.export_charts_cb = QCheckBox("Export comparison charts")
        self.export_charts_cb.setChecked(False)
        export_layout.addWidget(self.export_charts_cb)
        
        layout.addWidget(export_group)
        
        # Export preview
        self.export_preview = QTextEdit()
        self.export_preview.setReadOnly(True)
        self.export_preview.setPlaceholderText("Export preview will appear here...")
        layout.addWidget(self.export_preview)
        
        return tab
        
    def on_selection_changed(self):
        """Handle selection changes"""
        self.refresh_comparison()
        
    def refresh_comparison(self):
        """Refresh the comparison display"""
        try:
            machine_a = self.machine_a_combo.currentText()
            machine_b = self.machine_b_combo.currentText()
            parameter = self.parameter_combo.currentText()
            
            if (machine_a == "Select Machine A..." or 
                machine_b == "Select Machine B..." or
                parameter == "Select Parameter..." or
                not self.machine_manager):
                return
            
            # Get comparison data from machine manager
            comparison_data = self.machine_manager.get_machine_comparison_data(
                machine_a, machine_b, parameter
            )
            
            # Update charts
            self.update_comparison_charts(comparison_data)
            
            # Update statistics table
            self.update_statistics_table(comparison_data)
            
            # Update comparison summary
            self.update_comparison_summary(comparison_data)
            
            # Update export preview
            self.update_export_preview(comparison_data)
            
        except Exception as e:
            print(f"Error refreshing comparison: {e}")
            
    def update_comparison_charts(self, comparison_data):
        """Update the comparison charts"""
        try:
            if not self.machine_a_plot or not self.machine_b_plot:
                return
                
            # Plot Machine A data
            machine_a_data = comparison_data.get('machine1', {}).get('data')
            if machine_a_data is not None and not machine_a_data.empty:
                self.machine_a_plot.plot_parameter_trends(
                    machine_a_data, 
                    comparison_data.get('parameter', 'Parameter'),
                    f"Machine A: {comparison_data['machine1']['id']}"
                )
            
            # Plot Machine B data
            machine_b_data = comparison_data.get('machine2', {}).get('data')
            if machine_b_data is not None and not machine_b_data.empty:
                self.machine_b_plot.plot_parameter_trends(
                    machine_b_data,
                    comparison_data.get('parameter', 'Parameter'), 
                    f"Machine B: {comparison_data['machine2']['id']}"
                )
                
        except Exception as e:
            print(f"Error updating comparison charts: {e}")
            
    def update_statistics_table(self, comparison_data):
        """Update the statistics comparison table"""
        try:
            self.stats_table.setRowCount(0)
            
            machine1_stats = comparison_data.get('machine1', {}).get('stats', {})
            machine2_stats = comparison_data.get('machine2', {}).get('stats', {})
            
            if not machine1_stats or not machine2_stats:
                return
                
            # Define statistics to show
            stats_to_show = [
                ('Mean', 'mean'),
                ('Std Deviation', 'std'),
                ('Minimum', 'min'),
                ('Maximum', 'max'),
                ('Data Points', 'count')
            ]
            
            self.stats_table.setRowCount(len(stats_to_show))
            
            for row, (stat_name, stat_key) in enumerate(stats_to_show):
                # Statistic name
                self.stats_table.setItem(row, 0, QTableWidgetItem(stat_name))
                
                # Machine A value
                value_a = machine1_stats.get(stat_key, 'N/A')
                if isinstance(value_a, (int, float)):
                    value_a = f"{value_a:.3f}" if stat_key != 'count' else f"{int(value_a)}"
                self.stats_table.setItem(row, 1, QTableWidgetItem(str(value_a)))
                
                # Machine B value
                value_b = machine2_stats.get(stat_key, 'N/A')
                if isinstance(value_b, (int, float)):
                    value_b = f"{value_b:.3f}" if stat_key != 'count' else f"{int(value_b)}"
                self.stats_table.setItem(row, 2, QTableWidgetItem(str(value_b)))
                
        except Exception as e:
            print(f"Error updating statistics table: {e}")
            
    def update_comparison_summary(self, comparison_data):
        """Update the comparison summary text"""
        try:
            summary_text = f"<h4>Comparison Summary</h4>"
            
            # Basic comparison info
            machine1_id = comparison_data.get('machine1', {}).get('id', 'N/A')
            machine2_id = comparison_data.get('machine2', {}).get('id', 'N/A')
            parameter = comparison_data.get('parameter', 'N/A')
            
            summary_text += f"<p><b>Parameter:</b> {parameter}</p>"
            summary_text += f"<p><b>Machine A:</b> {machine1_id}</p>"
            summary_text += f"<p><b>Machine B:</b> {machine2_id}</p>"
            
            # Statistical comparison
            comparison_stats = comparison_data.get('comparison_stats', {})
            if comparison_stats:
                mean_diff = comparison_stats.get('mean_difference', 0)
                summary_text += f"<p><b>Mean Difference:</b> {mean_diff:.3f}</p>"
                
                # Correlation if available
                correlation = comparison_data.get('correlation')
                if correlation is not None:
                    summary_text += f"<p><b>Correlation:</b> {correlation:.3f}</p>"
                    
                    # Interpretation
                    if abs(correlation) > 0.8:
                        summary_text += "<p>🟢 <b>Strong correlation:</b> Machines show very similar patterns</p>"
                    elif abs(correlation) > 0.5:
                        summary_text += "<p>🟡 <b>Moderate correlation:</b> Machines show somewhat similar patterns</p>"
                    else:
                        summary_text += "<p>🔴 <b>Weak correlation:</b> Machines show different patterns</p>"
            
            self.comparison_summary.setHtml(summary_text)
            
        except Exception as e:
            print(f"Error updating comparison summary: {e}")
            
    def update_export_preview(self, comparison_data):
        """Update the export preview"""
        try:
            preview_text = "Comparison Export Preview:\n\n"
            
            if self.export_data_cb.isChecked():
                preview_text += "✓ Raw comparison data will be included\n"
                
            if self.export_stats_cb.isChecked():
                preview_text += "✓ Statistical summary will be included\n"
                
            if self.export_charts_cb.isChecked():
                preview_text += "✓ Comparison charts will be included\n"
                
            preview_text += f"\nMachines: {comparison_data.get('machine1', {}).get('id', 'N/A')} vs {comparison_data.get('machine2', {}).get('id', 'N/A')}\n"
            preview_text += f"Parameter: {comparison_data.get('parameter', 'N/A')}\n"
            
            self.export_preview.setPlainText(preview_text)
            
        except Exception as e:
            print(f"Error updating export preview: {e}")
            
    def export_comparison_report(self):
        """Export the comparison report"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            
            # Get export file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Comparison Report",
                f"machine_comparison_{self.machine_a_combo.currentText()}_vs_{self.machine_b_combo.currentText()}.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not file_path:
                return
                
            # Get current comparison data
            machine_a = self.machine_a_combo.currentText()
            machine_b = self.machine_b_combo.currentText()
            parameter = self.parameter_combo.currentText()
            
            if (machine_a == "Select Machine A..." or 
                machine_b == "Select Machine B..." or
                parameter == "Select Parameter..."):
                QMessageBox.warning(self, "Export Error", "Please select machines and parameter before exporting.")
                return
                
            # Use machine manager to export comparison data
            if self.machine_manager:
                export_df = self.machine_manager.export_machine_comparison(
                    [machine_a, machine_b], [parameter]
                )
                
                if not export_df.empty:
                    export_df.to_csv(file_path, index=False)
                    QMessageBox.information(
                        self, "Export Successful", 
                        f"Comparison report exported successfully to:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(self, "Export Error", "No data available for export.")
            else:
                QMessageBox.warning(self, "Export Error", "Machine manager not available.")
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Error", f"Error exporting report: {str(e)}")
            print(f"Error exporting comparison report: {e}")


