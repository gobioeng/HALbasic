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
    QMenu,
    QLineEdit,
    QTextEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Gobioeng HALog 0.0.1 beta")
        MainWindow.resize(1200, 800)
        MainWindow.setMinimumSize(800, 600)

        # Setup menu bar FIRST before anything else
        self.setup_menu_bar(MainWindow)

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(16)
        self.main_layout.setContentsMargins(16, 16, 16, 16)

        self.setup_main_content()

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

        # View Menu
        self.menuView = self.menubar.addMenu("&View")
        self.actionRefresh = QAction(MainWindow)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionRefresh.setText("&Refresh")
        self.actionRefresh.setShortcut(QKeySequence("F5"))
        self.actionRefresh.setStatusTip("Refresh all data")
        self.menuView.addAction(self.actionRefresh)

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
        self.setup_data_table_tab()
        self.setup_analysis_tab()
        self.setup_mpc_tab()  # NEW MPC TAB
        self.setup_fault_code_tab()
        self.setup_about_tab()

    def setup_dashboard_tab(self):
        self.tabDashboard = QWidget()
        self.tabWidget.addTab(self.tabDashboard, "📊 Dashboard")
        layout = QVBoxLayout(self.tabDashboard)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("<h2>LINAC Water System Monitor</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

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

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btnClearDB = QPushButton("Clear All Data")
        self.btnClearDB.setObjectName("dangerButton")
        self.btnClearDB.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.btnRefreshData = QPushButton("Refresh Data")
        self.btnRefreshData.setObjectName("successButton")
        self.btnRefreshData.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        button_layout.addWidget(self.btnClearDB)
        button_layout.addWidget(self.btnRefreshData)
        button_layout.addStretch()

        layout.addLayout(button_layout)
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
        
        # Controls
        controls_group = QGroupBox("Water System Graph Selection")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(12)
        
        # Top graph selector
        controls_layout.addWidget(QLabel("Top Graph:"))
        self.comboWaterTopGraph = QComboBox()
        self.comboWaterTopGraph.setMinimumWidth(160)
        self.comboWaterTopGraph.addItems([
            "Mag Flow",  # Remove "Select parameter..." and make first item default
            "Flow Target", 
            "Flow Chiller Water",
            "Cooling Pump Pressure"
        ])
        # Set default selection to first parameter
        self.comboWaterTopGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboWaterTopGraph)
        
        # Bottom graph selector
        controls_layout.addWidget(QLabel("Bottom Graph:"))
        self.comboWaterBottomGraph = QComboBox()
        self.comboWaterBottomGraph.setMinimumWidth(160)
        self.comboWaterBottomGraph.addItems([
            "Flow Target",  # Remove "Select parameter..." and set different default
            "Mag Flow",
            "Flow Chiller Water", 
            "Cooling Pump Pressure"
        ])
        # Set default selection to first parameter (different from top graph)
        self.comboWaterBottomGraph.setCurrentIndex(0)
        controls_layout.addWidget(self.comboWaterBottomGraph)
        
        self.btnRefreshWater = QPushButton("Update Graphs")
        self.btnRefreshWater.setObjectName("primaryButton")
        controls_layout.addWidget(self.btnRefreshWater)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Two graphs layout (top and bottom)
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(12)
        
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
        
        # Controls
        controls_group = QGroupBox("Voltage Graph Selection")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(12)
        
        # Top graph selector
        controls_layout.addWidget(QLabel("Top Graph:"))
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
        controls_layout.addWidget(self.comboVoltageTopGraph)
        
        # Bottom graph selector
        controls_layout.addWidget(QLabel("Bottom Graph:"))
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
        controls_layout.addWidget(self.comboVoltageBottomGraph)
        
        self.btnRefreshVoltage = QPushButton("Update Graphs")
        self.btnRefreshVoltage.setObjectName("primaryButton")
        controls_layout.addWidget(self.btnRefreshVoltage)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Two graphs layout (top and bottom)
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setSpacing(12)
        
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

    def setup_data_table_tab(self):
        self.tabDataTable = QWidget()
        self.tabWidget.addTab(self.tabDataTable, "📋 Data Table")
        layout = QVBoxLayout(self.tabDataTable)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lblTableInfo = QLabel("No data available")
        self.lblTableInfo.setWordWrap(True)
        layout.addWidget(self.lblTableInfo)

        self.tableData = QTableWidget()
        self.tableData.setColumnCount(7)
        self.tableData.setHorizontalHeaderLabels(
            [
                "DateTime",
                "Serial",
                "Parameter",
                "Average",
                "Min",
                "Max",
                "Diff (Max-Min)",
            ]
        )
        self.tableData.setAlternatingRowColors(True)
        self.tableData.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableData.horizontalHeader().setStretchLastSection(True)
        self.tableData.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableData.verticalHeader().setVisible(False)
        self.tableData.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableData.setWordWrap(True)
        
        # Add scroll policies and improved styling
        self.tableData.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableData.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableData.setMinimumHeight(400)
        
        # Enhanced styling for data table
        self.tableData.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                font-size: 11px;
                background-color: #FAFAFA;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
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
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        layout.addWidget(self.tableData)

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

        header_label = QLabel("<h2>Latest Machine Performance Check Results</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        
        # Date selection controls for MPC comparison
        date_group = QGroupBox("Date Selection for Comparison")
        date_layout = QHBoxLayout(date_group)
        date_layout.setSpacing(16)
        date_layout.setContentsMargins(16, 16, 16, 16)
        
        # Date A selection
        date_a_label = QLabel("Date A:")
        date_a_label.setMinimumWidth(80)
        date_layout.addWidget(date_a_label)
        
        self.comboMPCDateA = QComboBox()
        self.comboMPCDateA.setMinimumWidth(200)
        self.comboMPCDateA.addItem("Select Date A...")
        date_layout.addWidget(self.comboMPCDateA)
        
        date_layout.addSpacing(20)
        
        # Date B selection  
        date_b_label = QLabel("Date B:")
        date_b_label.setMinimumWidth(80)
        date_layout.addWidget(date_b_label)
        
        self.comboMPCDateB = QComboBox()
        self.comboMPCDateB.setMinimumWidth(200)
        self.comboMPCDateB.addItem("Select Date B...")
        date_layout.addWidget(self.comboMPCDateB)
        
        date_layout.addStretch()
        layout.addWidget(date_group)

        # Data info and refresh controls
        info_group = QGroupBox("MPC Data Status")
        info_layout = QHBoxLayout(info_group)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(16, 16, 16, 16)
        
        # Last update info
        self.lblLastMPCUpdate = QLabel("Last MPC Data: Loading...")
        self.lblLastMPCUpdate.setWordWrap(True)
        info_layout.addWidget(self.lblLastMPCUpdate)
        
        # Refresh button
        self.btnRefreshMPC = QPushButton("Refresh Latest Data")
        self.btnRefreshMPC.setObjectName("primaryButton")
        self.btnRefreshMPC.setMaximumWidth(200)
        info_layout.addWidget(self.btnRefreshMPC)
        
        info_layout.addStretch()
        layout.addWidget(info_group)

        # Results table with responsive design
        results_group = QGroupBox("Latest MPC Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(16, 16, 16, 16)

        self.tableMPC = QTableWidget()
        self.tableMPC.setAlternatingRowColors(True)
        self.tableMPC.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableMPC.setColumnCount(4)  # Updated for comparison: Parameter, Date A, Date B, Status
        self.tableMPC.setHorizontalHeaderLabels([
            "Parameter",
            "Date A Result", 
            "Date B Result",
            "Status"
        ])
        
        # Set responsive column widths with better text handling
        header = self.tableMPC.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Parameter - allow resize
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)     # Date A - fit content
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)     # Date B - fit content
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status - fit content
        
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

        # Load sample MPC data AFTER creating all UI elements
        self._populate_sample_mpc_data()

    def _populate_sample_mpc_data(self):
        """Populate sample MPC data for demonstration with NA handling"""
        # Sample MPC check categories and parameters
        mpc_data = [
            # Geometric Checks
            ("Geometry", "Isocenter Radius (mm)", "0.8", "0.9", "PASS"),
            ("Geometry", "Gantry Accuracy (°)", "0.1", "0.2", "PASS"), 
            ("Geometry", "Collimator Accuracy (°)", "0.1", "0.1", "PASS"),
            ("Geometry", "Couch Accuracy (°)", "0.3", "0.4", "PASS"),
            ("Geometry", "Laser Alignment (mm)", "0.5", "0.8", "PASS"),
            
            # Dosimetric Checks
            ("Dosimetry", "Beam Output Constancy (%)", "0.2", "0.3", "PASS"),
            ("Dosimetry", "Beam Uniformity (%)", "1.2", "1.5", "PASS"),
            ("Dosimetry", "Center Shift (mm)", "0.3", "0.4", "PASS"),
            ("Dosimetry", "Energy Constancy (%)", "0.5", "0.8", "PASS"),
            ("Dosimetry", "Dose Rate Constancy (%)", "0.8", "1.0", "PASS"),
            
            # MLC Checks
            ("MLC", "Leaf Position Accuracy (mm)", "0.5", "0.7", "PASS"),
            ("MLC", "Leaf Speed Constancy (%)", "1.0", "1.2", "PASS"),
            ("MLC", "Leaf Gap Width (mm)", "0.1", "0.1", "PASS"),
            
            # Imaging Checks  
            ("Imaging", "Image Quality Score", "95", "93", "PASS"),
            ("Imaging", "Contrast Resolution (%)", "2.1", "2.3", "PASS"),
            ("Imaging", "Spatial Resolution (lp/mm)", "0.8", "0.8", "PASS"),
            
            # Example with missing data
            ("Geometry", "Long Parameter Name That Needs Wrapping to Show Full Text", "NA", "0.5", "NA"),
            ("Dosimetry", "Missing Data Example", "NA", "NA", "NA"),
        ]

        self.tableMPC.setRowCount(len(mpc_data))
        
        for row, (category, param, date_a, date_b, status) in enumerate(mpc_data):
            # Parameter name with category - improved text wrapping
            param_item = QLabel(f"<b>[{category}]</b><br>{param}")
            param_item.setWordWrap(True)
            param_item.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            param_item.setMargin(5)
            self.tableMPC.setCellWidget(row, 0, param_item)
            
            # Date A result - handle NA values
            date_a_display = "NA" if date_a == "NA" or not date_a else date_a
            date_a_item = QTableWidgetItem(date_a_display)
            if date_a_display == "NA":
                date_a_item.setBackground(Qt.lightGray)
            self.tableMPC.setItem(row, 1, date_a_item)
            
            # Date B result - handle NA values 
            date_b_display = "NA" if date_b == "NA" or not date_b else date_b
            date_b_item = QTableWidgetItem(date_b_display)
            if date_b_display == "NA":
                date_b_item.setBackground(Qt.lightGray)
            self.tableMPC.setItem(row, 2, date_b_item)
            
            # Status with enhanced color coding and styling - handle NA values
            status_display = "NA" if status == "NA" or not status else status
            status_item = QLabel(status_display)
            if status_display == "PASS":
                status_item.setStyleSheet("""
                    color: white; 
                    font-weight: bold; 
                    background-color: #4CAF50; 
                    border-radius: 4px; 
                    padding: 6px 12px;
                """)
            elif status_display == "FAIL":
                status_item.setStyleSheet("""
                    color: white; 
                    font-weight: bold; 
                    background-color: #F44336; 
                    border-radius: 4px; 
                    padding: 6px 12px;
                """)
            elif status_display == "NA":
                status_item.setStyleSheet("""
                    color: #666666; 
                    font-weight: bold; 
                    background-color: #E0E0E0; 
                    border-radius: 4px; 
                    padding: 6px 12px;
                """)
            else:
                status_item.setStyleSheet("""
                    color: white; 
                    font-weight: bold; 
                    background-color: #FF9800; 
                    border-radius: 4px; 
                    padding: 6px 12px;
                """)
            status_item.setAlignment(Qt.AlignCenter)
            self.tableMPC.setCellWidget(row, 3, status_item)

        # Update statistics with NA handling
        total_checks = len(mpc_data)
        passed_checks = sum(1 for _, _, _, _, status in mpc_data if status == "PASS")
        na_checks = sum(1 for _, _, _, _, status in mpc_data if status == "NA")
        
        if total_checks > 0:
            pass_rate = (passed_checks / (total_checks - na_checks)) * 100 if (total_checks - na_checks) > 0 else 0
            self.lblMPCStats.setText(
                f"Total Checks: {total_checks} | Passed: {passed_checks} | NA: {na_checks} | "
                f"Pass Rate: {pass_rate:.1f}% (excluding NA)"
            )
        else:
            self.lblMPCStats.setText("No MPC data available")
        
        # Resize rows to fit content after populating
        self.tableMPC.resizeRowsToContents()

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
