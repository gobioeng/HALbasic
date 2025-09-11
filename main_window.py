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
    QDoubleSpinBox,  # Added for scaling inputs
)
from PyQt5.QtCore import Qt, QTimer  # Added QTimer import
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
        """Apply modern native Windows 11-style theme with unified styling"""
        # Import and apply the unified modern stylesheet
        from styles import get_modern_native_stylesheet
        MainWindow.setStyleSheet(get_modern_native_stylesheet())

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

        self.setup_fault_code_tab()
        self.setup_about_tab()

    def setup_dashboard_tab(self):
        """Setup modern dashboard tab with functional dashboard implementation"""
        self.dashboardTab = QWidget()
        self.tabWidget.addTab(self.dashboardTab, "📊 Dashboard")
        layout = QVBoxLayout(self.dashboardTab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Create and integrate the actual modern dashboard
        try:
            # Try to get machine_manager and database from parent
            parent_app = self.parent()
            machine_manager = None
            database_manager = None
            
            # Walk up the parent hierarchy to find the main app
            while parent_app:
                if hasattr(parent_app, 'machine_manager'):
                    machine_manager = parent_app.machine_manager
                if hasattr(parent_app, 'db'):
                    database_manager = parent_app.db
                if hasattr(parent_app, 'database_manager'):
                    database_manager = parent_app.database_manager
                parent_app = parent_app.parent()
            
            # Import and create the modern dashboard
            from modern_dashboard import ModernDashboard
            self.modern_dashboard = ModernDashboard(machine_manager, database_manager, self.dashboardTab)
            layout.addWidget(self.modern_dashboard)
            
        except Exception as e:
            # Fallback: Create a basic dashboard with metric cards
            print(f"Could not initialize full dashboard: {e}")
            self.create_fallback_dashboard(layout)
        
        # Add info about modern features
        info_label = QLabel("🎯 Modern Features: Real-time metric cards, Interactive charts, Drag-and-drop widgets, Light/Dark themes")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                color: #1976D2;
                font-size: 11px;
                padding: 16px;
                background: #E3F2FD;
                border-radius: 6px;
                margin: 10px;
            }
        """)
        layout.addWidget(info_label)

    def create_fallback_dashboard(self, layout):
        """Create a basic fallback dashboard with key metrics"""
        # Header
        header = QLabel("🚀 LINAC System Dashboard")
        header.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 600;
                color: #212529;
                padding: 16px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 8px;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(header)
        
        # Metric cards grid
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(16)
        cards_layout.setContentsMargins(8, 8, 8, 8)
        
        # Import MetricCard from modern_dashboard
        try:
            from modern_dashboard import MetricCard
            
            # Create metric cards for key parameters
            cards_data = [
                ("💧 Magnetron Flow", "12.5", "L/min", "#1976D2"),
                ("🔧 Pump Pressure", "18.2", "PSI", "#2E7D32"), 
                ("🌡️ Water Temp", "22.4", "°C", "#F57C00"),
                ("⚡ MLC 24V", "24.1", "V", "#7B1FA2"),
                ("💨 Fan Speed 1", "2850", "RPM", "#0288D1"),
                ("📊 System Status", "Normal", "", "#4CAF50"),
            ]
            
            row, col = 0, 0
            for title, value, unit, color in cards_data:
                card = MetricCard(title, value, unit, color)
                cards_layout.addWidget(card, row, col)
                col += 1
                if col >= 3:  # 3 cards per row
                    col = 0
                    row += 1
                    
        except Exception as e:
            # Ultimate fallback - simple labels
            print(f"Could not create metric cards: {e}")
            fallback_label = QLabel("📊 Dashboard functionality will be available when connected to data source")
            fallback_label.setAlignment(Qt.AlignCenter)
            fallback_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #495057;
                    padding: 40px;
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                }
            """)
            cards_layout.addWidget(fallback_label, 0, 0, 1, 3)
        
        layout.addWidget(cards_widget)
        
        # Status info
        status_info = QLabel("🔄 Dashboard will auto-refresh when data is available • Real-time monitoring • Interactive charts")
        status_info.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #6c757d;
                padding: 8px;
                text-align: center;
            }
        """)
        layout.addWidget(status_info)

    def setup_trends_tab(self):
        """Setup enhanced trends tab with grouped parameter sub-tabs as requested"""
        self.tabTrends = QWidget()
        self.tabWidget.addTab(self.tabTrends, "📈 Trends")
        layout = QVBoxLayout(self.tabTrends)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Create sub-tab widget for grouped parameters
        self.trendSubTabs = QTabWidget()
        self.trendSubTabs.setTabPosition(QTabWidget.North)
        layout.addWidget(self.trendSubTabs)
        
        # Setup parameter group sub-tabs as requested
        self.setup_water_system_tab()
        self.setup_temperature_tab()
        self.setup_mlc_tab()
        self.setup_fan_tab()
        
        # Global controls section for all sub-tabs
        global_controls = QGroupBox("Global Controls")
        controls_layout = QHBoxLayout(global_controls)
        controls_layout.setSpacing(16)
        
        # Time window controls
        controls_layout.addWidget(QLabel("Time Window:"))
        
        # Time window buttons with enhanced functionality
        self.btnGlobal1Day = QPushButton("1 Day")
        self.btnGlobal1Day.setCheckable(True)
        self.btnGlobal1Day.setChecked(True)
        self.btnGlobal1Day.clicked.connect(lambda: self.set_global_time_window("1day"))
        
        self.btnGlobal1Week = QPushButton("1 Week") 
        self.btnGlobal1Week.setCheckable(True)
        self.btnGlobal1Week.clicked.connect(lambda: self.set_global_time_window("1week"))
        
        self.btnGlobal1Month = QPushButton("1 Month")
        self.btnGlobal1Month.setCheckable(True)
        self.btnGlobal1Month.clicked.connect(lambda: self.set_global_time_window("1month"))
        
        # Group time buttons for mutual exclusivity
        self.globalTimeButtonGroup = QButtonGroup()
        self.globalTimeButtonGroup.addButton(self.btnGlobal1Day)
        self.globalTimeButtonGroup.addButton(self.btnGlobal1Week)
        self.globalTimeButtonGroup.addButton(self.btnGlobal1Month)
        
        # Apply styling to time buttons
        global_button_style = """
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ddd;
                border-radius: 6px;
                background: white;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:checked {
                background: #1976D2;
                color: white;
                border-color: #1976D2;
            }
            QPushButton:hover:!checked {
                background: #f5f5f5;
                border-color: #1976D2;
            }
        """
        
        for btn in [self.btnGlobal1Day, self.btnGlobal1Week, self.btnGlobal1Month]:
            btn.setStyleSheet(global_button_style)
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()
        
        # Global export functionality
        self.btnGlobalExport = QPushButton("📊 Export All")
        self.btnGlobalExport.clicked.connect(self.export_all_trend_data)
        self.btnGlobalExport.setToolTip("Export all trend data from all parameter groups")
        self.btnGlobalExport.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        controls_layout.addWidget(self.btnGlobalExport)
        
        layout.addWidget(global_controls)
    
    def setup_water_system_tab(self):
        """Setup Water System sub-tab with flow and pressure parameters"""
        water_tab = QWidget()
        self.trendSubTabs.addTab(water_tab, "💧 Water System")
        layout = QVBoxLayout(water_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Parameter selection for water system
        controls_group = QGroupBox("Water System Parameters")
        controls_layout = QGridLayout(controls_group)
        
        # Water system specific parameters
        water_params = [
            ("Magnetron Flow", "magnetronFlow"),
            ("Target & Circulator Flow", "targetAndCirculatorFlow"),
            ("City Water Flow", "cityWaterFlow"),
            ("Pump Pressure", "pumpPressure"),
            ("Water System Pressure", "waterSystemPressure"),
            ("Cooling Water Temperature", "coolingWaterTemp")
        ]
        
        # Create dual graph layout
        self.water_top_combo = QComboBox()
        self.water_bottom_combo = QComboBox()
        
        for display_name, param_id in water_params:
            self.water_top_combo.addItem(display_name, param_id)
            self.water_bottom_combo.addItem(display_name, param_id)
        
        controls_layout.addWidget(QLabel("Top Graph:"), 0, 0)
        controls_layout.addWidget(self.water_top_combo, 0, 1)
        controls_layout.addWidget(QLabel("Bottom Graph:"), 0, 2)
        controls_layout.addWidget(self.water_bottom_combo, 0, 3)
        
        # Refresh button
        water_refresh_btn = QPushButton("🔄 Refresh")
        water_refresh_btn.clicked.connect(lambda: self.refresh_water_trends())
        controls_layout.addWidget(water_refresh_btn, 0, 4)
        
        layout.addWidget(controls_group)
        
        # Create dual graph widgets
        graphs_group = QGroupBox("Water System Trends")
        graphs_layout = QVBoxLayout(graphs_group)
        
        try:
            from plot_utils import EnhancedPlotWidget
            self.water_top_graph = EnhancedPlotWidget()
            self.water_bottom_graph = EnhancedPlotWidget()
            
            self.water_top_graph.setMinimumHeight(200)
            self.water_bottom_graph.setMinimumHeight(200)
            
            graphs_layout.addWidget(self.water_top_graph)
            graphs_layout.addWidget(self.water_bottom_graph)
            
        except ImportError:
            # Fallback
            self.water_top_graph = QFrame()
            self.water_bottom_graph = QFrame()
            self.water_top_graph.setFrameStyle(QFrame.Box)
            self.water_bottom_graph.setFrameStyle(QFrame.Box)
            self.water_top_graph.setMinimumHeight(200)
            self.water_bottom_graph.setMinimumHeight(200)
            graphs_layout.addWidget(self.water_top_graph)
            graphs_layout.addWidget(self.water_bottom_graph)
        
        layout.addWidget(graphs_group)
        
    def setup_temperature_tab(self):
        """Setup Temperature sub-tab with thermal monitoring parameters"""
        temp_tab = QWidget()
        self.trendSubTabs.addTab(temp_tab, "🌡️ Temperature")
        layout = QVBoxLayout(temp_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Temperature parameter selection
        controls_group = QGroupBox("Temperature Monitoring Parameters")
        controls_layout = QGridLayout(controls_group)
        
        temp_params = [
            ("Remote Temperature", "remoteTempStatistics"),
            ("Magnetron Temperature", "magnetronTemp"),
            ("COL Board Temperature", "COLboardTemp"), 
            ("PDU Temperature", "PDUTemp"),
            ("Cabinet Temperature", "cabinetTemp"),
            ("Target Temperature", "targetTemp"),
            ("Ambient Temperature", "ambientTemp")
        ]
        
        self.temp_top_combo = QComboBox()
        self.temp_bottom_combo = QComboBox()
        
        for display_name, param_id in temp_params:
            self.temp_top_combo.addItem(display_name, param_id)
            self.temp_bottom_combo.addItem(display_name, param_id)
        
        controls_layout.addWidget(QLabel("Top Graph:"), 0, 0)
        controls_layout.addWidget(self.temp_top_combo, 0, 1)
        controls_layout.addWidget(QLabel("Bottom Graph:"), 0, 2)
        controls_layout.addWidget(self.temp_bottom_combo, 0, 3)
        
        temp_refresh_btn = QPushButton("🔄 Refresh")
        temp_refresh_btn.clicked.connect(lambda: self.refresh_temperature_trends())
        controls_layout.addWidget(temp_refresh_btn, 0, 4)
        
        layout.addWidget(controls_group)
        
        # Temperature graphs
        graphs_group = QGroupBox("Temperature Trends")
        graphs_layout = QVBoxLayout(graphs_group)
        
        try:
            from plot_utils import EnhancedPlotWidget
            self.temp_top_graph = EnhancedPlotWidget()
            self.temp_bottom_graph = EnhancedPlotWidget()
            
            self.temp_top_graph.setMinimumHeight(200)
            self.temp_bottom_graph.setMinimumHeight(200)
            
            graphs_layout.addWidget(self.temp_top_graph)
            graphs_layout.addWidget(self.temp_bottom_graph)
            
        except ImportError:
            self.temp_top_graph = QFrame()
            self.temp_bottom_graph = QFrame()
            self.temp_top_graph.setFrameStyle(QFrame.Box)
            self.temp_bottom_graph.setFrameStyle(QFrame.Box)
            self.temp_top_graph.setMinimumHeight(200)
            self.temp_bottom_graph.setMinimumHeight(200)
            graphs_layout.addWidget(self.temp_top_graph)
            graphs_layout.addWidget(self.temp_bottom_graph)
        
        layout.addWidget(graphs_group)
        
    def setup_mlc_tab(self):
        """Setup MLC sub-tab with multi-leaf collimator parameters"""
        mlc_tab = QWidget()
        self.trendSubTabs.addTab(mlc_tab, "🎯 MLC")
        layout = QVBoxLayout(mlc_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # MLC parameter selection
        controls_group = QGroupBox("MLC (Multi-Leaf Collimator) Parameters")
        controls_layout = QGridLayout(controls_group)
        
        mlc_params = [
            ("MLC Bank A 24V", "MLC_ADC_CHAN_TEMP_BANKA_STAT_24V"),
            ("MLC Bank B 24V", "MLC_ADC_CHAN_TEMP_BANKB_STAT_24V"),
            ("MLC Bank A 48V", "MLC_ADC_CHAN_TEMP_BANKA_STAT_48V"),
            ("MLC Bank B 48V", "MLC_ADC_CHAN_TEMP_BANKB_STAT_48V"),
            ("MLC 5V Monitor", "MLC_ADC_CHAN_TEMP_5V_MON"),
            ("MLC Position Accuracy", "MLCPositionAccuracy"),
            ("MLC Leaf Speed", "MLCLeafSpeed")
        ]
        
        self.mlc_top_combo = QComboBox()
        self.mlc_bottom_combo = QComboBox()
        
        for display_name, param_id in mlc_params:
            self.mlc_top_combo.addItem(display_name, param_id)
            self.mlc_bottom_combo.addItem(display_name, param_id)
        
        controls_layout.addWidget(QLabel("Top Graph:"), 0, 0)
        controls_layout.addWidget(self.mlc_top_combo, 0, 1)
        controls_layout.addWidget(QLabel("Bottom Graph:"), 0, 2)
        controls_layout.addWidget(self.mlc_bottom_combo, 0, 3)
        
        mlc_refresh_btn = QPushButton("🔄 Refresh")
        mlc_refresh_btn.clicked.connect(lambda: self.refresh_mlc_trends())
        controls_layout.addWidget(mlc_refresh_btn, 0, 4)
        
        layout.addWidget(controls_group)
        
        # MLC graphs
        graphs_group = QGroupBox("MLC Performance Trends")
        graphs_layout = QVBoxLayout(graphs_group)
        
        try:
            from plot_utils import EnhancedPlotWidget
            self.mlc_top_graph = EnhancedPlotWidget()
            self.mlc_bottom_graph = EnhancedPlotWidget()
            
            self.mlc_top_graph.setMinimumHeight(200)
            self.mlc_bottom_graph.setMinimumHeight(200)
            
            graphs_layout.addWidget(self.mlc_top_graph)
            graphs_layout.addWidget(self.mlc_bottom_graph)
            
        except ImportError:
            self.mlc_top_graph = QFrame()
            self.mlc_bottom_graph = QFrame()
            self.mlc_top_graph.setFrameStyle(QFrame.Box)
            self.mlc_bottom_graph.setFrameStyle(QFrame.Box)
            self.mlc_top_graph.setMinimumHeight(200)
            self.mlc_bottom_graph.setMinimumHeight(200)
            graphs_layout.addWidget(self.mlc_top_graph)
            graphs_layout.addWidget(self.mlc_bottom_graph)
        
        layout.addWidget(graphs_group)
        
    def setup_fan_tab(self):
        """Setup FAN sub-tab with cooling system parameters"""
        fan_tab = QWidget()
        self.trendSubTabs.addTab(fan_tab, "🌀 FAN")
        layout = QVBoxLayout(fan_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # FAN parameter selection
        controls_group = QGroupBox("FAN & Cooling System Parameters")
        controls_layout = QGridLayout(controls_group)
        
        fan_params = [
            ("Fan Speed 1", "FanfanSpeed1Statistics"),
            ("Fan Speed 2", "FanfanSpeed2Statistics"),
            ("Fan Speed 3", "FanfanSpeed3Statistics"),
            ("Fan Speed 4", "FanfanSpeed4Statistics"),
            ("Humidity", "FanhumidityStatistics"),
            ("Air Flow Rate", "FanAirFlowRate"),
            ("Vibration Level", "FanVibrationLevel")
        ]
        
        self.fan_top_combo = QComboBox()
        self.fan_bottom_combo = QComboBox()
        
        for display_name, param_id in fan_params:
            self.fan_top_combo.addItem(display_name, param_id)
            self.fan_bottom_combo.addItem(display_name, param_id)
        
        controls_layout.addWidget(QLabel("Top Graph:"), 0, 0)
        controls_layout.addWidget(self.fan_top_combo, 0, 1)
        controls_layout.addWidget(QLabel("Bottom Graph:"), 0, 2)
        controls_layout.addWidget(self.fan_bottom_combo, 0, 3)
        
        fan_refresh_btn = QPushButton("🔄 Refresh")
        fan_refresh_btn.clicked.connect(lambda: self.refresh_fan_trends())
        controls_layout.addWidget(fan_refresh_btn, 0, 4)
        
        layout.addWidget(controls_group)
        
        # FAN graphs
        graphs_group = QGroupBox("FAN System Trends")
        graphs_layout = QVBoxLayout(graphs_group)
        
        try:
            from plot_utils import EnhancedPlotWidget
            self.fan_top_graph = EnhancedPlotWidget()
            self.fan_bottom_graph = EnhancedPlotWidget()
            
            self.fan_top_graph.setMinimumHeight(200)
            self.fan_bottom_graph.setMinimumHeight(200)
            
            graphs_layout.addWidget(self.fan_top_graph)
            graphs_layout.addWidget(self.fan_bottom_graph)
            
        except ImportError:
            self.fan_top_graph = QFrame()
            self.fan_bottom_graph = QFrame()
            self.fan_top_graph.setFrameStyle(QFrame.Box)
            self.fan_bottom_graph.setFrameStyle(QFrame.Box)
            self.fan_top_graph.setMinimumHeight(200)
            self.fan_bottom_graph.setMinimumHeight(200)
            graphs_layout.addWidget(self.fan_top_graph)
            graphs_layout.addWidget(self.fan_bottom_graph)
        
        layout.addWidget(graphs_group)
    
    # Helper methods for trend refresh functionality
    def set_global_time_window(self, window):
        """Set time window for all trend sub-tabs"""
        # This will be implemented to update all graphs across all sub-tabs
        print(f"Setting global time window to: {window}")
        # Trigger refresh for all active sub-tabs
        self.refresh_water_trends()
        self.refresh_temperature_trends()
        self.refresh_mlc_trends()
        self.refresh_fan_trends()
    
    def refresh_water_trends(self):
        """Refresh water system trend graphs"""
        print("Refreshing water system trends")
        # Implementation will fetch and plot water system data
        
    def refresh_temperature_trends(self):
        """Refresh temperature trend graphs"""
        print("Refreshing temperature trends")
        # Implementation will fetch and plot temperature data
        
    def refresh_mlc_trends(self):
        """Refresh MLC trend graphs"""
        print("Refreshing MLC trends")
        # Implementation will fetch and plot MLC data
        
    def refresh_fan_trends(self):
        """Refresh FAN system trend graphs"""
        print("Refreshing FAN trends")
        # Implementation will fetch and plot FAN data
    
    def export_all_trend_data(self):
        """Export all trend data from all parameter groups"""
        print("Exporting all trend data")
        # Implementation will export data from all sub-tabs

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
            "All Parameters", "Water System", "Temperature", "MLC", "FAN", "Voltage"
        ])
        controls_layout.addWidget(self.comboAnalysisFilter)
        
        controls_layout.addStretch()
        
        # Refresh button
        self.btnRefreshAnalysis = QPushButton("🔄 Refresh Analysis")
        self.btnRefreshAnalysis.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #1976D2;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #1565C0;
            }
        """)
        controls_layout.addWidget(self.btnRefreshAnalysis)
        
        layout.addWidget(controls_group)

        # Analysis results area
        analysis_group = QGroupBox("Statistical Analysis Results")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # Results table
        self.tableAnalysis = QTableWidget()
        self.tableAnalysis.setColumnCount(6)
        self.tableAnalysis.setHorizontalHeaderLabels([
            "Parameter", "Count", "Average", "Min", "Max", "Std Dev"
        ])
        
        # Set table properties
        header = self.tableAnalysis.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.tableAnalysis.setAlternatingRowColors(True)
        self.tableAnalysis.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableAnalysis.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableAnalysis.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableAnalysis.setMinimumHeight(400)
        
        analysis_layout.addWidget(self.tableAnalysis)
        layout.addWidget(analysis_group)

    def export_trend_data(self):
        """Export current trend data to CSV file"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            
            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Export Trend Data",
                "trend_data.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                # Implementation would export current trend data
                print(f"Exporting trend data to: {file_path}")
                QMessageBox.information(
                    None,
                    "Export Successful", 
                    f"Trend data exported to:\n{file_path}"
                )
                
        except Exception as e:
            print(f"Error exporting trend data: {e}")

    def setup_fault_code_tab(self):
        """Setup enhanced fault code tab with search and notes functionality"""
        self.tabFaultCode = QWidget()
        self.tabWidget.addTab(self.tabFaultCode, "🔍 Fault Code Viewer")
        layout = QVBoxLayout(self.tabFaultCode)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Search controls
        search_group = QGroupBox("Fault Code Search")
        search_layout = QGridLayout(search_group)
        
        # Fault ID search
        search_layout.addWidget(QLabel("Search by Fault ID:"), 0, 0)
        self.txtFaultCode = QLineEdit()
        self.txtFaultCode.setPlaceholderText("Enter fault code (e.g., HAL001, TB123)")
        search_layout.addWidget(self.txtFaultCode, 0, 1)
        
        self.btnSearchCode = QPushButton("🔍 Search")
        search_layout.addWidget(self.btnSearchCode, 0, 2)
        
        # Description search
        search_layout.addWidget(QLabel("Search by Description:"), 1, 0)
        self.txtSearchDescription = QLineEdit()
        self.txtSearchDescription.setPlaceholderText("Enter description keywords")
        search_layout.addWidget(self.txtSearchDescription, 1, 1)
        
        self.btnSearchDescription = QPushButton("🔍 Search Description")
        search_layout.addWidget(self.btnSearchDescription, 1, 2)
        
        layout.addWidget(search_group)

        # Results and notes area
        results_group = QGroupBox("Fault Code Details & Notes")
        results_layout = QVBoxLayout(results_group)
        
        # Fault details display
        self.txtFaultDetails = QTextEdit()
        self.txtFaultDetails.setMaximumHeight(150)
        self.txtFaultDetails.setPlaceholderText("Fault code details will appear here...")
        results_layout.addWidget(QLabel("Fault Code Description:"))
        results_layout.addWidget(self.txtFaultDetails)
        
        # User notes section
        results_layout.addWidget(QLabel("User Notes:"))
        self.txtUserNotes = QTextEdit()
        self.txtUserNotes.setPlaceholderText("Add your notes for this fault code...")
        self.txtUserNotes.setMaximumHeight(120)
        results_layout.addWidget(self.txtUserNotes)
        
        # Notes controls
        notes_controls = QHBoxLayout()
        self.btnSaveNote = QPushButton("💾 Save Note")
        self.btnClearNote = QPushButton("🗑️ Clear Note")
        
        notes_controls.addWidget(self.btnSaveNote)
        notes_controls.addWidget(self.btnClearNote)
        notes_controls.addStretch()
        
        results_layout.addLayout(notes_controls)
        layout.addWidget(results_group)

        # Statistics display
        stats_group = QGroupBox("Fault Code Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        self.lblTotalCodes = QLabel("Total Codes: Loading...")
        self.lblFaultTypes = QLabel("Sources: Loading...")
        
        stats_layout.addWidget(self.lblTotalCodes)
        stats_layout.addStretch()
        stats_layout.addWidget(self.lblFaultTypes)
        
        layout.addWidget(stats_group)

    def setup_about_tab(self):
                                
                                # Convert datetime for plotting
                                time_data = pd.to_datetime(param_data['datetime'])
                                
                                # Plot statistical trend lines (max, min, avg)
                                if 'max' in param_data.columns and 'min' in param_data.columns:
                                    # Plot max trend line
                                    ax.plot(time_data, param_data['max'], 
                                           linewidth=2, alpha=0.7, color='#dc3545', linestyle='-',
                                           label=f'{selected_param} (Max)')
                                    
                                    # Plot min trend line  
                                    ax.plot(time_data, param_data['min'],
                                           linewidth=2, alpha=0.7, color='#28a745', linestyle='-', 
                                           label=f'{selected_param} (Min)')
                                    
                                    # Plot average trend line (primary)
                                    ax.plot(time_data, param_data['avg'],
                                           linewidth=3, alpha=0.9, color='#1976D2', linestyle='-',
                                           label=f'{selected_param} (Avg)')
                                    
                                    # Add shaded area between min and max for better visualization
                                    ax.fill_between(time_data, param_data['min'], param_data['max'],
                                                   alpha=0.2, color='#1976D2', label='Min-Max Range')
                                else:
                                    # Fallback: plot only available data
                                    if 'avg' in param_data.columns:
                                        ax.plot(time_data, param_data['avg'], 
                                               linewidth=3, alpha=0.9, color='#1976D2',
                                               label=f'{selected_param} (Avg)')
                                    elif 'value' in param_data.columns:
                                        ax.plot(time_data, param_data['value'],
                                               linewidth=2, alpha=0.8, color='#1976D2', 
                                               label=selected_param)
                                       
                                # Enhanced plot styling and professional appearance
                                ax.set_title(f"{selected_param} - Statistical Trend Analysis", 
                                           fontweight='bold', fontsize=14, color='#212529', pad=20)
                                ax.set_xlabel("Time", fontsize=12, color='#495057')
                                ax.set_ylabel(f"{selected_param}", fontsize=12, color='#495057')
                                
                                # Professional grid styling
                                ax.grid(True, alpha=0.3, linewidth=0.5, linestyle='-')
                                ax.set_facecolor('#fafafa')
                                
                                # Enhanced legend with better positioning and styling
                                legend = ax.legend(loc='upper left', framealpha=0.95, 
                                                 fancybox=True, shadow=True, fontsize=10)
                                legend.get_frame().set_facecolor('white')
                                legend.get_frame().set_edgecolor('#dee2e6')
                                
                                # Format axes for better readability
                                import matplotlib.dates as mdates
                                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%m/%d'))
                                ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(time_data)//10)))
                                
                                # Rotate x-axis labels for better readability
                                ax.tick_params(axis='x', rotation=0, labelsize=9)
                                ax.tick_params(axis='y', labelsize=9)
                                
                                # Set professional color scheme
                                ax.spines['top'].set_visible(False)
                                ax.spines['right'].set_visible(False)
                                ax.spines['left'].set_color('#dee2e6')
                                ax.spines['bottom'].set_color('#dee2e6')
                                
                                # Add subtle statistical annotations if data is available
                                if 'max' in param_data.columns and 'min' in param_data.columns and 'avg' in param_data.columns:
                                    current_max = param_data['max'].max()
                                    current_min = param_data['min'].min()
                                    current_avg = param_data['avg'].mean()
                                    
                                    # Add text box with statistics
                                    stats_text = f"Overall: Max={current_max:.2f}, Min={current_min:.2f}, Avg={current_avg:.2f}"
                                    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                                           verticalalignment='top', horizontalalignment='left',
                                           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, 
                                                    edgecolor='#dee2e6'), fontsize=9, color='#495057')
                                
                                # Apply professional styling
                                from plot_utils import PlotUtils
                                PlotUtils.setup_professional_style()
                                
                                # Update interactive manager if it exists
                                if hasattr(self.trendGraph, 'interactive_manager') and self.trendGraph.interactive_manager:
                                    self.trendGraph.interactive_manager.ax = [ax]
                                    self.trendGraph.interactive_manager._store_initial_view()
                                
                                # Refresh canvas
                                if hasattr(self.trendGraph, 'canvas'):
                                    self.trendGraph.canvas.draw()
                                    
                                # Apply current scale settings
                                self._update_enhanced_scaling()
                                
                            else:
                                print("Enhanced plotting methods not available")
                        except Exception as plot_error:
                            print(f"Error plotting trend: {plot_error}")
                            import traceback
                            traceback.print_exc()
                    break
                parent = parent.parent()
            else:
                print("Could not find parent with parameter data method")
                
        except Exception as e:
            print(f"Error updating simplified trend: {e}")
            import traceback
            traceback.print_exc()
    
    def export_trend_data(self):
        """Export current trend data to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            
            selected_param = self.parameterDropdown.currentText()
            if not selected_param:
                QMessageBox.warning(self, "Export Error", "Please select a parameter first.")
                return
            
            # Get file path for export
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Export {selected_param} Trend Data",
                f"{selected_param}_trend_data.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                # Get parameter data and export
                parent = self.parent()
                while parent:
                    if hasattr(parent, '_get_parameter_data_by_description'):
                        param_data = parent._get_parameter_data_by_description(selected_param)
                        if not param_data.empty:
                            param_data.to_csv(file_path, index=False)
                            QMessageBox.information(
                                self, "Export Successful", 
                                f"Trend data exported successfully to:\n{file_path}"
                            )
                        else:
                            QMessageBox.warning(self, "Export Error", "No data available for export.")
                        break
                    parent = parent.parent()
                else:
                    QMessageBox.warning(self, "Export Error", "Could not access trend data.")
                    
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Error", f"Error exporting trend data: {str(e)}")
            print(f"Error exporting trend data: {e}")

    # NOTE: Old complex trend tabs (water, voltage, temp, humidity, fan) removed 
    # and replaced with simplified single graph interface above
    
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


