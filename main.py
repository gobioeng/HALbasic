"""
Gobioeng HALog 0.0.1 beta
Professional LINAC Water System Monitor
Company: gobioeng.com
Created: 2025-08-20 22:58:39 UTC
Updated: 2025-08-27 15:08:00 UTC
"""

import sys
import os
import time
from pathlib import Path
import traceback

# Define APP_VERSION globally so it's accessible everywhere
APP_VERSION = "0.0.1"

# Track startup time
startup_begin = time.time()

# Global module cache to prevent duplicate imports
_module_cache = {}


def lazy_import(module_name):
    """Lazy import a module only when needed"""
    if module_name in _module_cache:
        return _module_cache[module_name]
    try:
        if "." in module_name:
            parent_module, child_module = module_name.split(".", 1)
            parent = __import__(parent_module)
            module = getattr(
                __import__(parent_module, fromlist=[child_module]), child_module
            )
        else:
            module = __import__(module_name)
        _module_cache[module_name] = module
        return module
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")
        raise


def setup_environment():
    """Setup environment with minimal imports"""
    os.environ["PYTHONOPTIMIZE"] = "2"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["NUMEXPR_MAX_THREADS"] = "8"

    # Set application path
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent.absolute()
    os.chdir(app_dir)
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

    # Configure warnings
    import warnings

    warnings.filterwarnings("ignore")

    # Ensure assets directory exists
    assets_dir = app_dir / "assets"
    if not assets_dir.exists():
        assets_dir.mkdir(exist_ok=True)
        print(f"Created assets directory: {assets_dir}")

    # Ensure application icon exists
    try:
        from resource_helper import ensure_app_icon

        ensure_app_icon()
    except Exception as e:
        print(f"Warning: Could not ensure app icon: {e}")


def test_icon_loading():
    """
    Test function to verify icon loading
    Debugging utility for Gobioeng HALog
    """
    from resource_helper import load_splash_icon, resource_path
    import os

    print("=== Icon Loading Test ===")

    # Check available files
    icon_files = [
        "halogo_256.png",
        "halogo_256.ico", 
        "halogo_100.png",
        "halogo_100.ico",
        "halogo.png",
        "halogo.ico",
    ]

    print("Available icon files:")
    for icon_file in icon_files:
        path = resource_path(icon_file)
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        print(f"  {icon_file}: {'✓' if exists else '✗'} ({path}) - {size} bytes")

    # Test loading
    print("\nTesting icon loading...")
    icon = load_splash_icon(100)  # Back to 100px for better arrangement
    if icon and not icon.isNull():
        print(f"✓ Icon loaded successfully: {icon.size()}")
    else:
        print("✗ Icon loading failed")

    print("=== End Test ===")


class HALogApp:
    """
    Gobioeng HALog Application with optimized startup
    Professional LINAC Water System Monitor - gobioeng.com
    """

    def __init__(self):
        self.splash = None
        self.window = None
        self.splash_progress = 0
        self.min_splash_time = 2000  # Reduced for better UX
        self.load_times = {}
        self.app_version = APP_VERSION
        self.status_label = None
        self.progress_bar = None

    def create_splash(self):
        """
        Create minimalistic splash screen using the new design
        """
        from splash_screen import MinimalisticSplashScreen
        
        self.splash = MinimalisticSplashScreen(self.app_version)
        self.splash.show()
        
        # Keep references for compatibility with existing update methods
        self.progress_bar = self.splash.progress_bar
        self.status_label = self.splash.status_label
        
        return self.splash

    def update_splash_progress(self, value, message=None):
        """Update splash progress using the new splash screen"""
        if not self.splash:
            return
        
        if hasattr(self.splash, 'update_status'):
            self.splash.update_status(message or "", value)
        elif self.progress_bar:
            self.progress_bar.setValue(value)
            if message and self.status_label:
                self.status_label.setText(message)

    def create_main_window(self):
        """Create professional main application window"""
        start_window = time.time()
        QtWidgets = lazy_import("PyQt5.QtWidgets")
        QtCore = lazy_import("PyQt5.QtCore")
        QtGui = lazy_import("PyQt5.QtGui")

        self.update_splash_progress(30, "Loading interface...")

        # Import resources first to ensure icon is available
        try:
            from resource_helper import get_app_icon

            app_icon = get_app_icon()
        except Exception as e:
            print(f"Warning: Could not load app icon: {e}")
            app_icon = None

        # Import main components
        from main_window import Ui_MainWindow
        from database import DatabaseManager

        # Pre-optimize pandas if used
        try:
            import pandas as pd

            pd.set_option("compute.use_numexpr", True)
        except Exception as e:
            print(f"Warning: Could not configure pandas: {e}")

        # Set numpy thread control
        try:
            os.environ["OMP_NUM_THREADS"] = str(min(8, os.cpu_count() or 4))
            os.environ["MKL_NUM_THREADS"] = str(min(8, os.cpu_count() or 4))
            os.environ["NUMEXPR_NUM_THREADS"] = str(min(8, os.cpu_count() or 4))
        except Exception as e:
            print(f"Warning: Could not configure threading: {e}")

        self.update_splash_progress(50, "Preparing interface components...")

        class HALogMaterialApp(QtWidgets.QMainWindow):
            """
            Main Gobioeng HALog Application Window
            Professional LINAC Log Analysis System - gobioeng.com
            """

            def __init__(self, parent=None):
                super().__init__(parent)

                # FIRST: Create the UI
                self.ui = Ui_MainWindow()
                self.ui.setupUi(self)

                # SECOND: Set window properties
                self.setWindowTitle(
                    f"HALog {APP_VERSION} • Professional LINAC Monitor • gobioeng.com"
                )
                if app_icon:
                    self.setWindowIcon(app_icon)

                # THIRD: Apply modern native styling
                try:
                    from styles import get_modern_native_stylesheet, apply_responsive_layout
                    self.setStyleSheet(get_modern_native_stylesheet())
                    apply_responsive_layout(self)
                    print("✓ Modern native styles applied")
                except Exception as e:
                    print(f"Warning: Could not load modern styles: {e}")
                    # Fallback to basic styling
                    self.apply_professional_styles()

                # FOURTH: Initialize actions AFTER UI is created
                self._init_actions()

                # FIFTH: Initialize database and components
                try:
                    # Use enhanced database manager with backup support
                    self.db = DatabaseManager()  # No path needed - uses backup manager's path
                    import pandas as pd

                    self.df = pd.DataFrame()

                    # Initialize unified parser for fault codes and other data
                    from unified_parser import UnifiedParser
                    self.fault_parser = UnifiedParser()

                    # Initialize fault notes manager
                    from fault_notes_manager import FaultNotesManager
                    self.fault_notes_manager = FaultNotesManager()

                    # Load fault code databases from core data directory
                    hal_fault_path = os.path.join(os.path.dirname(__file__), 'data', 'HALfault.txt')
                    tb_fault_path = os.path.join(os.path.dirname(__file__), 'data', 'TBFault.txt')

                    # Load fault codes from both databases using the unified method
                    hal_loaded = self.fault_parser.load_fault_codes_from_file(hal_fault_path, 'hal')
                    if hal_loaded:
                        print("✓ HAL fault codes loaded successfully")

                    # Load TB fault codes using the unified method
                    tb_loaded = self.fault_parser.load_fault_codes_from_file(tb_fault_path, 'tb')
                    if tb_loaded:
                        print("✓ TB fault codes loaded successfully")

                    self._initialize_fault_code_tab()

                    # Initialize short data parser for enhanced parameters
                    self.shortdata_parser = self.fault_parser  # Use same unified parser instance
                    self.shortdata_parameters = self.shortdata_parser.parse_short_data_file(
                        os.path.join(os.path.dirname(__file__), 'data', 'shortdata.txt')
                    )
                    self._initialize_trend_controls()

                    # Setup UI components with lazy loading
                    self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
                    self._optimize_database()

                    # Defer expensive dashboard loading until first needed
                    self._dashboard_loaded = False
                    self._trend_controls_initialized = False
                    
                    # Load dashboard data in background after UI is ready
                    QtCore.QTimer.singleShot(100, self._deferred_initialization)

                except Exception as e:
                    print(f"Error initializing database: {e}")
                    traceback.print_exc()

                # Setup memory monitoring with longer interval
                self.memory_timer = QtCore.QTimer()
                self.memory_timer.timeout.connect(self._update_memory_usage)
                self.memory_timer.start(60000)  # Reduced frequency from 30s to 60s

                # Setup branding in status bar
                self._setup_branding()
                
            def _deferred_initialization(self):
                """Perform expensive initialization operations in background with startup optimization"""
                try:
                    # Initialize startup performance manager
                    from startup_performance_manager import StartupPerformanceManager
                    self.performance_manager = StartupPerformanceManager()
                    
                    # Record startup time
                    startup_time = time.time() - startup_begin
                    self.performance_manager.record_startup_time(startup_time)
                    
                    # Check if data reprocessing is needed
                    data_sources = [
                        os.path.join(os.path.dirname(__file__), 'data', 'HALfault.txt'),
                        os.path.join(os.path.dirname(__file__), 'data', 'TBFault.txt'),
                        self.db.db_path  # Include database in checksum
                    ]
                    
                    # Only load dashboard if data changed or not cached
                    if self.performance_manager.should_reprocess_data(data_sources):
                        print("📊 Loading dashboard data (data changes detected)...")
                        self.load_dashboard()
                        
                        # Cache the results
                        dashboard_data = self._get_dashboard_data_for_caching()
                        self.performance_manager.mark_data_processed(data_sources, dashboard_data)
                    else:
                        print("⚡ Using cached dashboard data (startup optimization)")
                        cached_data = self.performance_manager.get_cached_processing_results()
                        if cached_data:
                            self._load_dashboard_from_cache(cached_data)
                        else:
                            # Fallback to normal loading
                            self.load_dashboard()
                    
                    self._dashboard_loaded = True
                    
                    # Display performance report
                    performance_report = self.performance_manager.get_startup_report()
                    print(performance_report)
                    
                except Exception as e:
                    print(f"Error during deferred initialization: {e}")
                    # Fallback to normal dashboard loading
                    try:
                        self.load_dashboard()
                        self._dashboard_loaded = True
                    except Exception as fallback_error:
                        print(f"Fallback dashboard loading failed: {fallback_error}")
                        
            def _get_dashboard_data_for_caching(self) -> dict:
                """Extract dashboard data for caching"""
                try:
                    return {
                        "dashboard_loaded": True,
                        "data_summary": self.db.get_summary_statistics(),
                        "cached_at": time.time()
                    }
                except Exception as e:
                    print(f"Error extracting dashboard data: {e}")
                    return {}
                    
            def _load_dashboard_from_cache(self, cached_data: dict):
                """Load dashboard from cached data"""
                try:
                    print("⚡ Loading dashboard from cache...")
                    # Use cached data to populate dashboard
                    # This is a simplified implementation - in a real app, you'd restore UI state
                    pass
                except Exception as e:
                    print(f"Error loading dashboard from cache: {e}")
                try:
                    print("🚀 Starting deferred initialization for better performance...")
                    
                    # Load dashboard data
                    if not self._dashboard_loaded:
                        self.load_dashboard()
                        self._dashboard_loaded = True
                    
                    # Initialize trend controls
                    if not self._trend_controls_initialized:
                        self._initialize_trend_controls()
                        self._trend_controls_initialized = True

                    # Load sample data if database is empty (deferred to background)
                    QtCore.QTimer.singleShot(500, self._check_and_load_sample_data)
                    
                    print("✓ Deferred initialization completed")
                except Exception as e:
                    print(f"Error in deferred initialization: {e}")
                    
            def _check_and_load_sample_data(self):
                """Check and load sample data in background"""
                try:
                    if hasattr(self, 'db') and self.db:
                        record_count = self.db.get_record_count()
                        if record_count == 0:
                            print("📋 No data in database, loading sample data for demonstration...")
                            sample_file = os.path.join(os.path.dirname(__file__), 'test_complete_shortdata.txt')
                            if os.path.exists(sample_file):
                                self._process_sample_shortdata(sample_file)
                                print("✓ Sample data loaded for trend analysis")
                except Exception as e:
                    print(f"Note: Could not load sample data: {e}")

            def apply_professional_styles(self):
                """Apply comprehensive professional styling with VISIBLE MENU BAR"""
                material_stylesheet = """
                /* Professional Global Styles */
                QMainWindow {
                    background-color: #FAFAFA;
                    color: #1C1B1F;
                    font-family: 'Segoe UI', 'Roboto', 'Google Sans', 'Helvetica Neue', Arial, sans-serif;
                    font-size: 13px;
                    font-weight: 400;
                    line-height: 1.4;
                }

                /* HIGHLY VISIBLE Professional Menu Bar - FORCED VISIBILITY */

                /* OPTIMIZED Professional Tab Widget */
                QTabWidget {
                    border: none;
                    background-color: transparent;
                }
                QTabWidget::pane {
                    border: none;
                    background-color: #FFFFFF;
                    border-radius: 12px;
                    margin-top: 8px;
                }
                QTabBar {
                    background-color: transparent;
                }
                QTabBar::tab {
                    background-color: transparent;
                    color: #79747E;
                    padding: 12px 20px;
                    margin-right: 2px;
                    border-radius: 8px 8px 0px 0px;
                    font-weight: 500;
                    font-size: 13px;
                    min-width: 100px;
                    border: none;
                }
                QTabBar::tab:selected {
                    background-color: #FFFFFF;
                    color: #1976D2;
                    font-weight: 600;
                    border-bottom: 2px solid #1976D2;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #F7F2FA;
                    color: #1C1B1F;
                }

                /* OPTIMIZED Professional Cards (Group Boxes) */
                QGroupBox {
                    font-weight: 600;
                    color: #1C1B1F;
                    border: none;
                    border-radius: 12px;
                    margin-top: 24px;
                    padding-top: 20px;
                    background-color: #FFFFFF;
                    font-size: 14px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 20px;
                    top: 8px;
                    padding: 8px 16px;
                    background-color: #E8F5E8;
                    color: #006A6B;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 8px;
                    margin-top: -12px;
                }

                /* OPTIMIZED Professional Buttons */
                QPushButton {
                    background-color: #1976D2;
                    color: #FFFFFF;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 13px;
                    min-width: 100px;
                    min-height: 16px;
                    letter-spacing: 0.1px;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #E0E0E0;
                    color: #9E9E9E;
                }

                /* Danger Button */
                QPushButton#dangerButton {
                    background-color: #D32F2F;
                }
                QPushButton#dangerButton:hover {
                    background-color: #C62828;
                }
                QPushButton#dangerButton:pressed {
                    background-color: #B71C1C;
                }

                /* Success Button */
                QPushButton#successButton {
                    background-color: #388E3C;
                }
                QPushButton#successButton:hover {
                    background-color: #2E7D32;
                }
                QPushButton#successButton:pressed {
                    background-color: #1B5E20;
                }

                /* OPTIMIZED Professional Combo Boxes */
                QComboBox {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    background-color: #FAFAFA;
                    color: #1C1B1F;
                    min-width: 120px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QComboBox:focus {
                    border: 2px solid #1976D2;
                    background-color: #FFFFFF;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                }
                QComboBox::down-arrow {
                    border: none;
                    width: 0px;
                    height: 0px;
                }

                /* OPTIMIZED Professional Table Headers */
                QHeaderView::section {
                    background-color: #1976D2;
                    color: #FFFFFF;
                    padding: 8px 6px;
                    border: none;
                    font-weight: 600;
                    font-size: 12px;
                    border-radius: 0px;
                }

                /* OPTIMIZED Professional Tables */
                QTableWidget {
                    background-color: #FFFFFF;
                    alternate-background-color: #F8F9FA;
                    border: none;
                    border-radius: 8px;
                    gridline-color: #E0E0E0;
                    font-size: 12px;
                }
                QTableWidget::item {
                    padding: 6px 8px;
                    border-bottom: 1px solid #F0F0F0;
                }
                QTableWidget::item:selected {
                    background-color: #E3F2FD;
                    color: #1976D2;
                }

                /* OPTIMIZED Professional Labels */
                QLabel {
                    color: #1C1B1F;
                    font-size: 13px;
                    font-weight: 500;
                }
                QLabel#titleLabel {
                    color: #1976D2;
                    font-size: 24px;
                    font-weight: 700;
                    margin: 16px 0;
                }
                QLabel#subtitleLabel {
                    color: #49454F;
                    font-size: 16px;
                    font-weight: 500;
                    margin: 8px 0;
                }
                QLabel#captionLabel {
                    color: #79747E;
                    font-size: 11px;
                    font-weight: 400;
                }

                /* OPTIMIZED Professional Plot Frames */
                QFrame#plotFrame {
                    border: none;
                    border-radius: 12px;
                    background-color: #FFFFFF;
                    margin: 8px;
                    padding: 12px;
                }

                /* OPTIMIZED Professional Progress Bars */
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    background-color: #E0E0E0;
                    text-align: center;
                    color: #1C1B1F;
                    font-weight: 600;
                    height: 8px;
                }
                QProgressBar::chunk {
                    background-color: #1976D2;
                    border-radius: 4px;
                }

                /* OPTIMIZED Professional Status Bar */
                QStatusBar {
                    background-color: #FFFFFF;
                    border-top: 1px solid #E0E0E0;
                    color: #79747E;
                    font-size: 11px;
                    padding: 4px;
                }
                """

                self.setStyleSheet(material_stylesheet)

            def _init_actions(self):
                """Initialize all UI actions including MENU ACTIONS - COMPREHENSIVE CONNECTION"""
                try:
                    print("Connecting menu actions...")

                    # VERIFY MENU ITEMS EXIST
                    if not hasattr(self.ui, "actionOpen_Log_File"):
                        print("ERROR: actionOpen_Log_File not found in UI!")
                        return
                    if not hasattr(self.ui, "actionExit"):
                        print("ERROR: actionExit not found in UI!")
                        return
                    if not hasattr(self.ui, "actionAbout"):
                        print("ERROR: actionAbout not found in UI!")
                        return
                    if not hasattr(self.ui, "actionRefresh"):
                        print("ERROR: actionRefresh not found in UI!")
                        return

                    # MAIN MENU ACTIONS - FILE MENU
                    self.ui.actionOpen_Log_File.triggered.connect(self.import_log_file)
                    self.ui.actionExit.triggered.connect(self.close)
                    print("✓ File menu actions connected")

                    # VIEW MENU ACTIONS
                    self.ui.actionRefresh.triggered.connect(self.load_dashboard)
                    print("✓ View menu actions connected")

                    # DATA MENU ACTIONS
                    if hasattr(self.ui, "actionClearAllData"):
                        self.ui.actionClearAllData.triggered.connect(self.clear_all_data)
                        print("✓ Clear data action connected")

                    if hasattr(self.ui, "actionOptimizeDatabase"):
                        self.ui.actionOptimizeDatabase.triggered.connect(self.optimize_database)
                        print("✓ Optimize database action connected")

                    # HELP MENU ACTIONS
                    self.ui.actionAbout.triggered.connect(self.show_about_dialog)
                    print("✓ Help menu actions connected")

                    # OPTIONAL MENU ACTIONS (if they exist)
                    if hasattr(self.ui, "actionExport_Data"):
                        self.ui.actionExport_Data.triggered.connect(self.export_data)
                        print("✓ Export action connected")

                    if hasattr(self.ui, "actionSettings"):
                        self.ui.actionSettings.triggered.connect(self.show_settings)
                        print("✓ Settings action connected")

                    if hasattr(self.ui, "actionAbout_Qt"):
                        self.ui.actionAbout_Qt.triggered.connect(
                            lambda: QtWidgets.QApplication.aboutQt()
                        )
                        print("✓ About Qt action connected")

                    # BUTTON ACTIONS
                    self.ui.btnClearDB.clicked.connect(self.clear_database)
                    self.ui.btnRefreshData.clicked.connect(self.load_dashboard)

                    # Legacy trend controls (keep for backward compatibility)
                    if hasattr(self.ui, 'comboTrendSerial'):
                        self.ui.comboTrendSerial.currentIndexChanged.connect(self.update_trend)
                    if hasattr(self.ui, 'comboTrendParam'):
                        self.ui.comboTrendParam.currentIndexChanged.connect(self.update_trend)

                    # NEW TREND SUB-TAB ACTIONS
                    if hasattr(self.ui, 'btnRefreshWater'):
                        self.ui.btnRefreshWater.clicked.connect(lambda: self.refresh_trend_tab('flow'))
                    if hasattr(self.ui, 'btnRefreshVoltage'):
                        self.ui.btnRefreshVoltage.clicked.connect(lambda: self.refresh_trend_tab('voltage'))
                    if hasattr(self.ui, 'btnRefreshTemp'):
                        self.ui.btnRefreshTemp.clicked.connect(lambda: self.refresh_trend_tab('temperature'))
                    if hasattr(self.ui, 'btnRefreshHumidity'):
                        self.ui.btnRefreshHumidity.clicked.connect(lambda: self.refresh_trend_tab('humidity'))
                    if hasattr(self.ui, 'btnRefreshFan'):
                        self.ui.btnRefreshFan.clicked.connect(lambda: self.refresh_trend_tab('fan_speed'))

                    # NEW TREND DROPDOWN CHANGE EVENTS (auto-update on selection)
                    if hasattr(self.ui, 'comboWaterTopGraph'):
                        self.ui.comboWaterTopGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('flow'))
                    if hasattr(self.ui, 'comboWaterBottomGraph'):
                        self.ui.comboWaterBottomGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('flow'))
                    if hasattr(self.ui, 'comboVoltageTopGraph'):
                        self.ui.comboVoltageTopGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('voltage'))
                    if hasattr(self.ui, 'comboVoltageBottomGraph'):
                        self.ui.comboVoltageBottomGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('voltage'))
                    if hasattr(self.ui, 'comboTempTopGraph'):
                        self.ui.comboTempTopGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('temperature'))
                    if hasattr(self.ui, 'comboTempBottomGraph'):
                        self.ui.comboTempBottomGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('temperature'))
                    if hasattr(self.ui, 'comboHumidityTopGraph'):
                        self.ui.comboHumidityTopGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('humidity'))
                    if hasattr(self.ui, 'comboHumidityBottomGraph'):
                        self.ui.comboHumidityBottomGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('humidity'))
                    if hasattr(self.ui, 'comboFanTopGraph'):
                        self.ui.comboFanTopGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('fan_speed'))
                    if hasattr(self.ui, 'comboFanBottomGraph'):
                        self.ui.comboFanBottomGraph.currentIndexChanged.connect(lambda: self.refresh_trend_tab('fan_speed'))
                    print("✓ Trend dropdown change events connected")

                    # MPC TAB ACTIONS - Single date selection
                    if hasattr(self.ui, 'btnRefreshMPC'):
                        self.ui.btnRefreshMPC.clicked.connect(self.refresh_latest_mpc)

                        # Connect MPC date selection dropdown
                        if hasattr(self.ui, 'comboMPCDate'):
                            self.ui.comboMPCDate.currentIndexChanged.connect(self.refresh_latest_mpc)

                    # ANALYSIS TAB ACTIONS - Enhanced controls
                    if hasattr(self.ui, 'btnRefreshAnalysis'):
                        self.ui.btnRefreshAnalysis.clicked.connect(self.update_analysis_tab)
                    if hasattr(self.ui, 'comboAnalysisFilter'):
                        self.ui.comboAnalysisFilter.currentIndexChanged.connect(self._filter_analysis_results)

                    # FAULT CODE TAB ACTIONS
                    if hasattr(self.ui, 'btnSearchCode'):
                        self.ui.btnSearchCode.clicked.connect(self.search_fault_code)
                        print("✓ Fault code search button connected")

                    if hasattr(self.ui, 'btnSearchDescription'):
                        self.ui.btnSearchDescription.clicked.connect(self.search_fault_description)
                        print("✓ Fault description search button connected")

                    if hasattr(self.ui, 'txtFaultCode'):
                        self.ui.txtFaultCode.returnPressed.connect(self.search_fault_code)
                        print("✓ Fault code input Enter key connected")

                    if hasattr(self.ui, 'txtSearchDescription'):
                        self.ui.txtSearchDescription.returnPressed.connect(self.search_fault_description)
                        print("✓ Fault description input Enter key connected")

                    # FAULT CODE NOTES ACTIONS
                    if hasattr(self.ui, 'btnSaveNote'):
                        self.ui.btnSaveNote.clicked.connect(self.save_fault_note)
                        print("✓ Save fault note button connected")

                    if hasattr(self.ui, 'btnClearNote'):
                        self.ui.btnClearNote.clicked.connect(self.clear_fault_note)
                        print("✓ Clear fault note button connected")

                    print("✓ Button actions connected")

                    print("✓ ALL ACTIONS CONNECTED SUCCESSFULLY")

                except Exception as e:
                    print(f"ERROR connecting actions: {e}")
                    traceback.print_exc()

            def export_data(self):
                """Export data functionality (placeholder)"""
                QtWidgets.QMessageBox.information(
                    self,
                    "Export Data",
                    "Export functionality will be implemented in a future version.",
                )

            def show_settings(self):
                """Show settings dialog (placeholder)"""
                QtWidgets.QMessageBox.information(
                    self,
                    "Settings",
                    "Settings dialog will be implemented in a future version.",
                )

            def _initialize_fault_code_tab(self):
                """Initialize the fault code tab with statistics"""
                try:
                    if not hasattr(self, 'fault_parser'):
                        return

                    stats = self.fault_parser.get_fault_code_statistics()

                    if hasattr(self.ui, 'lblTotalCodes'):
                        # Calculate breakdown by source (fixed to use correct source names)
                        hal_codes = sum(1 for code_info in self.fault_parser.fault_codes.values() if code_info.get('source') == 'hal')
                        tb_codes = sum(1 for code_info in self.fault_parser.fault_codes.values() if code_info.get('source') == 'tb')
                        self.ui.lblTotalCodes.setText(f"Total Codes: {stats['total_codes']} (HAL: {hal_codes}, TB: {tb_codes})")

                    if hasattr(self.ui, 'lblFaultTypes'):
                        sources_text = f"Sources: {', '.join(stats['sources'])}"
                        self.ui.lblFaultTypes.setText(sources_text)

                    print(f"✓ Fault code tab initialized with {stats['total_codes']} codes")

                except Exception as e:
                    print(f"Error initializing fault code tab: {e}")

            def _initialize_trend_controls(self):
                """Initialize the trend controls with available parameters from database"""
                try:
                    if not hasattr(self, 'df') or self.df.empty:
                        print("⚠️ No database data available for trend controls")
                        return

                    # Get unique serial numbers from database
                    if 'serial_number' in self.df.columns:
                        serial_numbers = sorted(list(set(self.df['serial_number'].astype(str).unique())))
                    elif 'serial' in self.df.columns:
                        serial_numbers = sorted(list(set(self.df['serial'].astype(str).unique())))
                    elif 'Serial' in self.df.columns:
                        serial_numbers = sorted(list(set(self.df['Serial'].astype(str).unique())))
                    else:
                        serial_numbers = ['All']

                    # Get all available parameters from database
                    param_column = None
                    possible_param_columns = ['parameter_type', 'param', 'Parameter']
                    for col in possible_param_columns:
                        if col in self.df.columns:
                            param_column = col
                            break

                    if not param_column:
                        print(f"⚠️ No parameter column found. Available columns: {list(self.df.columns)}")
                        return

                    all_params = list(self.df[param_column].unique())
                    print(f"🔧 Initializing trend controls with {len(all_params)} parameters")
                    print(f"🔧 Sample parameters: {all_params[:5]}")

                    # Since your data shows COL parameters, let's categorize them properly
                    flow_params = []
                    voltage_params = []
                    temp_params = []
                    humidity_params = []
                    fan_params = []

                    for param in all_params:
                        param_str = str(param)
                        param_lower = param_str.lower()

                        # For COL parameters, categorize them as voltage by default
                        if param_str.upper().startswith('COL'):
                            voltage_params.append(param)
                        elif any(keyword in param_lower for keyword in ['flow', 'pump', 'water', 'magnetron']):
                            flow_params.append(param)
                        elif any(keyword in param_lower for keyword in ['volt', '_v_', '24v', '48v', '5v', 'bank', 'adc']):
                            voltage_params.append(param)
                        elif any(keyword in param_lower for keyword in ['temp', 'temperature']):
                            temp_params.append(param)
                        elif any(keyword in param_lower for keyword in ['humidity', 'humid']):
                            humidity_params.append(param)
                        elif any(keyword in param_lower for keyword in ['fan', 'speed']):
                            fan_params.append(param)
                        else:
                            # Default unknown parameters to voltage category for display
                            voltage_params.append(param)

                    # Populate dropdown controls with actual parameters
                    dropdown_configs = [
                        ('comboWaterTopGraph', flow_params),
                        ('comboWaterBottomGraph', flow_params),
                        ('comboVoltageTopGraph', voltage_params),
                        ('comboVoltageBottomGraph', voltage_params),
                        ('comboTempTopGraph', temp_params),
                        ('comboTempBottomGraph', temp_params),
                        ('comboHumidityTopGraph', humidity_params),
                        ('comboHumidityBottomGraph', humidity_params),
                        ('comboFanTopGraph', fan_params),
                        ('comboFanBottomGraph', fan_params),
                    ]

                    for combo_name, params in dropdown_configs:
                        if hasattr(self.ui, combo_name):
                            combo = getattr(self.ui, combo_name)
                            combo.clear()
                            combo.addItem("Select parameter...")
                            if params:
                                # Use simplified names for display - show all parameters
                                for param in params:
                                    display_name = self._get_display_name_for_param(param)
                                    combo.addItem(display_name)

                    print(f"✓ Trend controls populated:")
                    print(f"  - Flow parameters: {len(flow_params)}")
                    print(f"  - Voltage parameters: {len(voltage_params)}")
                    print(f"  - Temperature parameters: {len(temp_params)}")
                    print(f"  - Humidity parameters: {len(humidity_params)}")
                    print(f"  - Fan parameters: {len(fan_params)}")

                    # Initialize default trend graphs after controls are setup
                    QtCore.QTimer.singleShot(200, self._initialize_default_trend_displays)

                except Exception as e:
                    print(f"Error initializing trend controls: {e}")
                    import traceback
                    traceback.print_exc()

            def _get_display_name_for_param(self, param_name):
                """Convert raw parameter name to user-friendly display name"""
                param_lower = param_name.lower()

                if 'magnetronflow' in param_lower:
                    return "Mag Flow"
                elif 'targetandcirculatorflow' in param_lower:
                    return "Flow Target"
                elif 'citywaterflow' in param_lower:
                    return "Flow Chiller Water"
                elif 'remotetemp' in param_lower:
                    return "Temp Room"
                elif 'humidity' in param_lower:
                    return "Room Humidity"
                elif 'magnetrontemp' in param_lower:
                    return "Temp Magnetron"
                elif 'banka' in param_lower and '24v' in param_lower:
                    return "MLC Bank A 24V"
                elif 'bankb' in param_lower and '24v' in param_lower:
                    return "MLC Bank B 24V"
                elif 'speed1' in param_lower or 'fan1' in param_lower:
                    return "Speed FAN 1"
                elif 'speed2' in param_lower or 'fan2' in param_lower:
                    return "Speed FAN 2"
                elif 'speed3' in param_lower or 'fan3' in param_lower:
                    return "Speed FAN 3"
                elif 'speed4' in param_lower or 'fan4' in param_lower:
                    return "Speed FAN 4"
                else:
                    # Return shortened version of original name
                    if len(param_name) > 50:
                        return param_name.split('::')[-1] if '::' in param_name else param_name[:50] + '...'
                    return param_name

            def refresh_trend_tab(self, group_name):
                """Refresh trend data for specific parameter group with new dropdown structure"""
                try:
                    # Ensure full data is loaded for trend analysis
                    self._ensure_full_data_loaded()
                    
                    # Check if we have any data available in the database
                    if not hasattr(self, 'df') or self.df.empty:
                        print(f"⚠️ No data available in database for {group_name}")
                        return

                    # Get the appropriate combo boxes and graph widgets based on group
                    top_combo = None
                    bottom_combo = None
                    graph_top = None
                    graph_bottom = None

                    if group_name == 'flow':  # Water System
                        top_combo = getattr(self.ui, 'comboWaterTopGraph', None)
                        bottom_combo = getattr(self.ui, 'comboWaterBottomGraph', None)
                        graph_top = getattr(self.ui, 'waterGraphTop', None)
                        graph_bottom = getattr(self.ui, 'waterGraphBottom', None)
                    elif group_name == 'voltage':
                        top_combo = getattr(self.ui, 'comboVoltageTopGraph', None)
                        bottom_combo = getattr(self.ui, 'comboVoltageBottomGraph', None)
                        graph_top = getattr(self.ui, 'voltageGraphTop', None)
                        graph_bottom = getattr(self.ui, 'voltageGraphBottom', None)
                    elif group_name == 'temperature':
                        top_combo = getattr(self.ui, 'comboTempTopGraph', None)
                        bottom_combo = getattr(self.ui, 'comboTempBottomGraph', None)
                        graph_top = getattr(self.ui, 'tempGraphTop', None)
                        graph_bottom = getattr(self.ui, 'tempGraphBottom', None)
                    elif group_name == 'humidity':
                        top_combo = getattr(self.ui, 'comboHumidityTopGraph', None)
                        bottom_combo = getattr(self.ui, 'comboHumidityBottomGraph', None)
                        graph_top = getattr(self.ui, 'humidityGraphTop', None)
                        graph_bottom = getattr(self.ui, 'humidityGraphBottom', None)
                    elif group_name == 'fan_speed':
                        top_combo = getattr(self.ui, 'comboFanTopGraph', None)
                        bottom_combo = getattr(self.ui, 'comboFanBottomGraph', None)
                        graph_top = getattr(self.ui, 'fanGraphTop', None)
                        graph_bottom = getattr(self.ui, 'fanGraphBottom', None)

                    if not all([top_combo, bottom_combo, graph_top, graph_bottom]):
                        print(f"⚠️ Dropdown or graph widgets not found for {group_name}")
                        return

                    # Get selected parameters from dropdowns
                    selected_top_param = top_combo.currentText() if top_combo.currentIndex() > 0 else None
                    selected_bottom_param = bottom_combo.currentText() if bottom_combo.currentIndex() > 0 else None

                    # If no parameters selected, use default ones for this group
                    if not selected_top_param or selected_top_param == "Select parameter...":
                        if group_name == 'flow':
                            selected_top_param = "Mag Flow"
                        elif group_name == 'voltage':
                            selected_top_param = "MLC Bank A 24V"
                        elif group_name == 'temperature':
                            selected_top_param = "Temp Room"
                        elif group_name == 'humidity':
                            selected_top_param = "Room Humidity"
                        elif group_name == 'fan_speed':
                            selected_top_param = "Speed FAN 1"

                    if not selected_bottom_param or selected_bottom_param == "Select parameter...":
                        if group_name == 'flow':
                            selected_bottom_param = "Flow Chiller Water"
                        elif group_name == 'voltage':
                            selected_bottom_param = "MLC Bank B 24V"
                        elif group_name == 'temperature':
                            selected_bottom_param = "Temp Magnetron"
                        elif group_name == 'humidity':
                            selected_bottom_param = "Temp Room"  # Fallback if only humidity param available
                        elif group_name == 'fan_speed':
                            selected_bottom_param = "Speed FAN 2"

                    print(f"🔄 Refreshing {group_name} trends - Top: {selected_top_param}, Bottom: {selected_bottom_param}")

                    # Import plotting utilities
                    from utils_plot import PlotUtils
                    import pandas as pd

                    # Plot top graph
                    if selected_top_param and selected_top_param != "Select parameter...":
                        data_top = self._get_parameter_data_by_description(selected_top_param)
                        if not data_top.empty:
                            PlotUtils._plot_parameter_data_single(graph_top, data_top, selected_top_param)
                        else:
                            PlotUtils._plot_parameter_data_single(graph_top, pd.DataFrame(), f"No data available for {selected_top_param}")
                    else:
                        PlotUtils._plot_parameter_data_single(graph_top, pd.DataFrame(), "Select a parameter from dropdown")

                    # Plot bottom graph
                    if selected_bottom_param and selected_bottom_param != "Select parameter...":
                        data_bottom = self._get_parameter_data_by_description(selected_bottom_param)
                        if not data_bottom.empty:
                            PlotUtils._plot_parameter_data_single(graph_bottom, data_bottom, selected_bottom_param)
                        else:
                            PlotUtils._plot_parameter_data_single(graph_bottom, pd.DataFrame(), f"No data available for {selected_bottom_param}")
                    else:
                        PlotUtils._plot_parameter_data_single(graph_bottom, pd.DataFrame(), "Select a parameter from dropdown")

                    print(f"✓ Successfully refreshed {group_name} trends")

                except Exception as e:
                    print(f"❌ Error refreshing {group_name} trends: {e}")
                    import traceback
                    traceback.print_exc()

            def _get_parameter_data_by_description(self, parameter_description):
                """Optimized parameter data retrieval with caching and minimal logging"""
                try:
                    if not hasattr(self, 'df') or self.df.empty:
                        return pd.DataFrame()

                    # Cache parameter column lookup
                    if not hasattr(self, '_param_column_cache'):
                        param_column = None
                        possible_param_columns = ['parameter_type', 'param', 'Parameter']
                        for col in possible_param_columns:
                            if col in self.df.columns:
                                param_column = col
                                break
                        self._param_column_cache = param_column

                    param_column = self._param_column_cache
                    if not param_column:
                        return pd.DataFrame()

                    # Cache available parameters 
                    if not hasattr(self, '_all_params_cache'):
                        self._all_params_cache = self.df[param_column].unique()

                    all_params = self._all_params_cache

                    # Cache parameter mapping for faster lookups
                    if not hasattr(self, '_param_mapping_cache'):
                        self._param_mapping_cache = {
                            "Mag Flow": "magnetronFlow",
                            "Flow Target": "targetAndCirculatorFlow", 
                            "Flow Chiller Water": "cityWaterFlow",
                            "Temp Room": "FanremoteTempStatistics",
                            "Room Humidity": "FanhumidityStatistics", 
                            "Temp Magnetron": "magnetronTemp",
                            "Temp COL Board": "COLboardTemp",
                            "Temp PDU": "PDUTemp",
                            "MLC Bank A 24V": "MLC_ADC_CHAN_TEMP_BANKA_STAT_24V",
                            "MLC Bank B 24V": "MLC_ADC_CHAN_TEMP_BANKB_STAT_24V",
                            "MLC Bank A 48V": "MLC_ADC_CHAN_TEMP_BANKA_STAT_48V",
                            "MLC Bank B 48V": "MLC_ADC_CHAN_TEMP_BANKB_STAT_48V",
                            "COL 24V Monitor": "COL_ADC_CHAN_TEMP_24V_MON",
                            "Speed FAN 1": "FanfanSpeed1Statistics",
                            "Speed FAN 2": "FanfanSpeed2Statistics",
                            "Speed FAN 3": "FanfanSpeed3Statistics", 
                            "Speed FAN 4": "FanfanSpeed4Statistics",
                        }

                    # Fast parameter lookup
                    target_param = self._param_mapping_cache.get(parameter_description)
                    selected_param = None

                    if target_param and target_param in all_params:
                        selected_param = target_param
                    else:
                        # Fallback to first available parameter
                        if len(all_params) > 0:
                            selected_param = all_params[0]

                    if not selected_param:
                        return pd.DataFrame()

                    # Fast data filtering with minimal processing
                    param_data = self.df[self.df[param_column] == selected_param]
                    if param_data.empty:
                        return pd.DataFrame()

                    # Quick value column detection
                    value_column = 'avg' if 'avg' in param_data.columns else 'average' if 'average' in param_data.columns else 'avg_value'
                    if value_column not in param_data.columns:
                        return pd.DataFrame()

                    # Minimal result preparation
                    result_df = pd.DataFrame({
                        'datetime': param_data['datetime'],
                        'avg': param_data[value_column],
                        'parameter_name': [parameter_description] * len(param_data)
                    })

                    # Add min/max if available
                    if 'Min' in param_data.columns:
                        result_df['min_value'] = param_data['Min']
                    if 'Max' in param_data.columns:
                        result_df['max_value'] = param_data['Max']

                    return result_df.sort_values('datetime')

                except Exception as e:
                    return pd.DataFrame()

            def refresh_latest_mpc(self):
                """Load and display MPC results from database with single date selection"""
                try:
                    print("🔄 Loading MPC data from database...")

                    # Update available dates in dropdown
                    self._populate_mpc_date_dropdown()

                    # Get selected date
                    selected_date = None
                    if hasattr(self.ui, 'comboMPCDate') and self.ui.comboMPCDate.currentIndex() > 0:
                        selected_date = self.ui.comboMPCDate.currentText()

                    # Get MPC data for selected date
                    mpc_data = self._get_mpc_data_for_date(selected_date)

                    if not mpc_data:
                        # Show helpful message about what data is needed
                        QtWidgets.QMessageBox.information(
                            self, "No MPC Data",
                            "No machine performance data available.\n\n"
                            "Import log files containing machine performance parameters "
                            "(magnetron flow, temperature readings, voltage levels, etc.) "
                            "to enable MPC analysis."
                        )
                        return

                    # Update the last update info
                    if hasattr(self.ui, 'lblLastMPCUpdate'):
                        from datetime import datetime
                        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        date_info = f" (Date: {selected_date})" if selected_date else ""
                        self.ui.lblLastMPCUpdate.setText(f"Last MPC Update: {update_time}{date_info}")

                    # Update the MPC table with data
                    self._populate_mpc_table(mpc_data)

                    print("✅ MPC data loaded successfully")

                except Exception as e:
                    print(f"❌ Error loading MPC data: {e}")
                    import traceback
                    traceback.print_exc()
                    QtWidgets.QMessageBox.critical(
                        self, "MPC Load Error",
                        f"Error loading MPC data: {str(e)}"
                    )

            def _populate_mpc_date_dropdown(self):
                """Populate MPC date selection dropdown with available dates from database"""
                try:
                    if not hasattr(self, 'df') or self.df.empty:
                        print("No data available for MPC date selection")
                        return

                    # Get unique dates from the database
                    unique_dates = sorted(self.df['datetime'].dt.date.unique(), reverse=True)
                    date_strings = [date.strftime('%Y-%m-%d') for date in unique_dates]

                    # Update date dropdown
                    if hasattr(self.ui, 'comboMPCDate'):
                        current_date = self.ui.comboMPCDate.currentText()
                        self.ui.comboMPCDate.blockSignals(True)
                        self.ui.comboMPCDate.clear()
                        self.ui.comboMPCDate.addItem("Select date...")
                        self.ui.comboMPCDate.addItems(date_strings)

                        # Restore selection if it still exists
                        if current_date in date_strings:
                            index = self.ui.comboMPCDate.findText(current_date)
                            if index >= 0:
                                self.ui.comboMPCDate.setCurrentIndex(index)

                        self.ui.comboMPCDate.blockSignals(False)

                    print(f"Updated MPC date dropdown with {len(date_strings)} dates")

                except Exception as e:
                    print(f"Error populating MPC date dropdown: {e}")

            def _get_mpc_data_for_date(self, selected_date=None):
                """Get MPC data for a specific date"""
                try:
                    if not hasattr(self, 'df') or self.df.empty:
                        return None

                    # Define key MPC parameters to monitor
                    mpc_params = [
                        'magnetronFlow', 'magnetronTemp', 'targetAndCirculatorFlow', 'targetAndCirculatorTemp',
                        'FanremoteTempStatistics', 'FanhumidityStatistics',
                        'FanfanSpeed1Statistics', 'FanfanSpeed2Statistics', 'FanfanSpeed3Statistics', 'FanfanSpeed4Statistics',
                        'MLC_ADC_CHAN_TEMP_BANKA_STAT_24V', 'MLC_ADC_CHAN_TEMP_BANKB_STAT_24V'
                    ]

                    import pandas as pd
                    results = []

                    for param in mpc_params:
                        param_data = self.df[self.df['param'] == param]

                        if param_data.empty:
                            continue

                        # Get description from parser mapping if available
                        description = param
                        if hasattr(self, 'parser') and hasattr(self.parser, 'parameter_mapping'):
                            mapping = self.parser.parameter_mapping.get(param, {})
                            description = mapping.get('description', param)

                        value = "NA"
                        status = "NA"

                        # Get data for selected date
                        if selected_date:
                            date_data = param_data[param_data['datetime'].dt.date == pd.to_datetime(selected_date).date()]
                            if not date_data.empty:
                                avg_value = date_data['avg'].iloc[-1] if 'avg' in date_data.columns else date_data['average'].iloc[-1] if 'average' in date_data.columns else 0
                                value = f"{avg_value:.2f}"
                                
                                # Simple status check based on reasonable ranges
                                try:
                                    val = float(avg_value)
                                    if 'flow' in param.lower() and (val < 0 or val > 100):
                                        status = "WARNING"
                                    elif 'temp' in param.lower() and (val < 0 or val > 80):
                                        status = "WARNING"
                                    elif 'speed' in param.lower() and (val < 0 or val > 5000):
                                        status = "WARNING"
                                    elif 'volt' in param.lower() or '24v' in param.lower() and (val < 20 or val > 28):
                                        status = "WARNING"
                                    else:
                                        status = "PASS"
                                except:
                                    status = "CHECK"
                        else:
                            # If no date selected, use latest available data
                            if not param_data.empty:
                                latest_data = param_data.iloc[-1]
                                avg_value = latest_data['avg'] if 'avg' in latest_data else latest_data['average'] if 'average' in latest_data else 0
                                value = f"{avg_value:.2f}"
                                status = "PASS"

                        results.append({
                            'parameter': description,
                            'value': value,
                            'status': status
                        })

                    return results if results else None

                except Exception as e:
                    print(f"Error getting MPC data for date: {e}")
                    import traceback
                    traceback.print_exc()
                    return None

            def _populate_mpc_table(self, mpc_data):
                """Populate MPC table with data"""
                try:
                    from PyQt5 import QtGui
                    from PyQt5.QtWidgets import QTableWidgetItem, QLabel
                    from PyQt5.QtCore import Qt

                    if not mpc_data:
                        self.ui.tableMPC.setRowCount(0)
                        return

                    self.ui.tableMPC.setRowCount(len(mpc_data))

                    for row, data in enumerate(mpc_data):
                        # Parameter name
                        param_item = QLabel(data['parameter'])
                        param_item.setWordWrap(True)
                        param_item.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        param_item.setMargin(5)
                        self.ui.tableMPC.setCellWidget(row, 0, param_item)

                        # Value
                        value_item = QTableWidgetItem(data['value'])
                        if data['value'] == "NA":
                            value_item.setBackground(Qt.lightGray)
                        value_item.setTextAlignment(Qt.AlignCenter)
                        self.ui.tableMPC.setItem(row, 1, value_item)

                        # Status with color coding
                        status_item = QLabel(data['status'])
                        status_item.setAlignment(Qt.AlignCenter)

                        if data['status'] == "PASS":
                            status_item.setStyleSheet("color: #1B5E20; font-weight: 600; background-color: #E8F5E8; padding: 6px; border-radius: 6px;")
                        elif data['status'] == "FAIL":
                            status_item.setStyleSheet("color: #B71C1C; font-weight: 600; background-color: #FFEBEE; padding: 6px; border-radius: 6px;")
                        elif data['status'] == "WARNING":
                            status_item.setStyleSheet("color: #E65100; font-weight: 600; background-color: #FFF3E0; padding: 6px; border-radius: 6px;")
                        elif data['status'] == "NA":
                            status_item.setStyleSheet("color: #616161; font-weight: 600; background-color: #F5F5F5; padding: 6px; border-radius: 6px;")
                        else:
                            status_item.setStyleSheet("color: #1976D2; font-weight: 600; background-color: #E3F2FD; padding: 6px; border-radius: 6px;")

                        self.ui.tableMPC.setCellWidget(row, 2, status_item)

                    # Resize rows to fit content
                    self.ui.tableMPC.resizeRowsToContents()

                    # Update statistics
                    self._update_mpc_statistics(mpc_data)

                except Exception as e:
                    print(f"Error populating MPC table: {e}")
                    import traceback
                    traceback.print_exc()

            def _update_mpc_statistics(self, mpc_data):
                """Update MPC statistics based on data"""
                try:
                    if not mpc_data:
                        return

                    total = len(mpc_data)
                    passed = sum(1 for item in mpc_data if item['status'] == 'PASS')
                    failed = sum(1 for item in mpc_data if item['status'] == 'FAIL')
                    warnings = sum(1 for item in mpc_data if item['status'] == 'WARNING')
                    na_count = sum(1 for item in mpc_data if item['status'] == 'NA')

                    # Update statistics labels if they exist
                    if hasattr(self.ui, 'lblTotalParams'):
                        self.ui.lblTotalParams.setText(f"Total Parameters: {total}")
                    if hasattr(self.ui, 'lblPassedParams'):
                        self.ui.lblPassedParams.setText(f"Passed: {passed}")
                    if hasattr(self.ui, 'lblFailedParams'):
                        self.ui.lblFailedParams.setText(f"Failed: {failed}")
                    if hasattr(self.ui, 'lblWarningParams'):
                        self.ui.lblWarningParams.setText(f"Warnings: {warnings}")

                    # Calculate pass rate excluding NA values
                    evaluated = total - na_count
                    pass_rate = (passed / evaluated * 100) if evaluated > 0 else 0

                    print(f"MPC Statistics: {passed}/{evaluated} passed ({pass_rate:.1f}%), {warnings} warnings, {failed} failed, {na_count} NA")

                except Exception as e:
                    print(f"Error updating MPC statistics: {e}")

            def compare_mpc_results(self):
                """Legacy function - kept for backward compatibility"""
                # This function is no longer needed but kept to avoid errors
                print("⚠️ MPC comparison function deprecated - using latest MPC data display instead")
                self.refresh_latest_mpc()

            def search_fault_code(self):
                """Search for fault code by code number"""
                try:
                    code = self.ui.txtFaultCode.text().strip()
                    if not code:
                        self.ui.txtFaultResult.setText("Please enter a fault code to search.")
                        return

                    # Search in both databases using the unified parser
                    result = self.fault_parser.search_fault_code(code)

                    if result['found']:
                        # Format result for display
                        formatted_result = f"""
✅ Fault Code Found

Code: {result['code']}
Database Source: {result.get('database_description', 'Unknown')}
Type: {result.get('type', 'Unknown')}
Description: {result['description']}
Source: {result.get('source', 'unknown')} database
                        """.strip()

                        self.ui.txtFaultResult.setText(formatted_result)

                        # Update individual description boxes based on source
                        if hasattr(self.ui, 'txtHALDescription'):
                            if result.get('source') == 'uploaded':
                                self.ui.txtHALDescription.setText(result['description'])
                            else:
                                self.ui.txtHALDescription.setText("No HAL description available for this code")

                        if hasattr(self.ui, 'txtTBDescription'):
                            if result.get('source') == 'tb':
                                self.ui.txtTBDescription.setText(result['description'])
                            else:
                                self.ui.txtTBDescription.setText("No TB description available for this code")
                        
                        # Load and display existing note for this fault code
                        self._load_fault_note(code)
                    else:
                        self.ui.txtFaultResult.setText(f"❌ Fault code '{code}' not found in the loaded databases.\n\nLoaded databases: {', '.join(self.fault_parser.get_fault_code_statistics()['sources'])}")

                        # Clear individual description boxes
                        if hasattr(self.ui, 'txtHALDescription'):
                            self.ui.txtHALDescription.setText("Fault code not found")
                        if hasattr(self.ui, 'txtTBDescription'):
                            self.ui.txtTBDescription.setText("Fault code not found")
                        
                        # Clear notes area
                        self._clear_fault_note_display()

                except Exception as e:
                    error_msg = f"❌ Error searching fault code: {str(e)}"
                    self.ui.txtFaultResult.setText(error_msg)
                    print(f"Error in fault code search: {e}")
                    import traceback
                    traceback.print_exc()

            def search_fault_description(self):
                """Search for fault codes by description keywords"""
                try:
                    search_term = self.ui.txtSearchDescription.text().strip()
                    if not search_term:
                        self.ui.txtFaultResult.setText("Please enter keywords to search in descriptions.")
                        return

                    results = self.fault_parser.search_description(search_term)

                    if results:
                        formatted_results = f"🔍 Found {len(results)} fault codes matching '{search_term}':\n\n"

                        for fault_code, fault_data in results[:10]:  # Limit to first 10 results
                            source = fault_data.get('source', 'unknown')
                            db_name = 'HAL' if source == 'uploaded' else 'TB' if source == 'tb' else source.upper()
                            description = fault_data.get('description', 'No description')

                            # Truncate long descriptions
                            if len(description) > 100:
                                description = description[:97] + "..."

                            formatted_results += f"Code: {fault_code} ({db_name})\nDescription: {description}\n\n"

                        if len(results) > 10:
                            formatted_results += f"... and {len(results) - 10} more results. Please refine your search."

                        self.ui.txtFaultResult.setText(formatted_results)

                        # Clear individual description boxes for description search
                        if hasattr(self.ui, 'txtHALDescription'):
                            self.ui.txtHALDescription.setText("Multiple results found - use specific fault code search")
                        if hasattr(self.ui, 'txtTBDescription'):
                            self.ui.txtTBDescription.setText("Multiple results found - use specific fault code search")
                        
                        # Clear notes area for multiple results
                        self._clear_fault_note_display()
                    else:
                        self.ui.txtFaultResult.setText(f"❌ No fault codes found matching '{search_term}' in the loaded databases.\n\nSearched in: {', '.join(self.fault_parser.get_fault_code_statistics()['sources'])}")
                        
                        # Clear notes area for no results
                        self._clear_fault_note_display()

                except Exception as e:
                    error_msg = f"❌ Error searching fault descriptions: {str(e)}"
                    self.ui.txtFaultResult.setText(error_msg)
                    print(f"Error in fault description search: {e}")
                    import traceback
                    traceback.print_exc()

            def save_fault_note(self):
                """Save the note for the current fault code"""
                try:
                    # Get the current fault code from the search field
                    fault_code = self.ui.txtFaultCode.text().strip()
                    if not fault_code:
                        QtWidgets.QMessageBox.warning(
                            self, "No Fault Code", 
                            "Please search for a fault code first before saving a note."
                        )
                        return
                    
                    # Get the note text
                    note_text = self.ui.txtUserNote.toPlainText().strip()
                    if not note_text:
                        QtWidgets.QMessageBox.warning(
                            self, "Empty Note", 
                            "Please enter some text before saving the note."
                        )
                        return
                    
                    # Save the note
                    success = self.fault_notes_manager.save_note(fault_code, note_text)
                    if success:
                        self._update_note_info(fault_code)
                        QtWidgets.QMessageBox.information(
                            self, "Note Saved", 
                            f"Note for fault code {fault_code} has been saved successfully."
                        )
                    else:
                        QtWidgets.QMessageBox.critical(
                            self, "Save Error", 
                            "Failed to save the note. Please try again."
                        )
                        
                except Exception as e:
                    print(f"Error saving fault note: {e}")
                    QtWidgets.QMessageBox.critical(
                        self, "Error", 
                        f"An error occurred while saving the note: {str(e)}"
                    )

            def clear_fault_note(self):
                """Clear the note for the current fault code"""
                try:
                    # Get the current fault code from the search field
                    fault_code = self.ui.txtFaultCode.text().strip()
                    if not fault_code:
                        QtWidgets.QMessageBox.warning(
                            self, "No Fault Code", 
                            "Please search for a fault code first."
                        )
                        return
                    
                    # Confirm deletion
                    reply = QtWidgets.QMessageBox.question(
                        self, "Confirm Clear Note", 
                        f"Are you sure you want to delete the note for fault code {fault_code}?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No
                    )
                    
                    if reply == QtWidgets.QMessageBox.Yes:
                        success = self.fault_notes_manager.delete_note(fault_code)
                        if success:
                            self.ui.txtUserNote.clear()
                            self._update_note_info(fault_code)
                            QtWidgets.QMessageBox.information(
                                self, "Note Cleared", 
                                f"Note for fault code {fault_code} has been deleted."
                            )
                        else:
                            QtWidgets.QMessageBox.critical(
                                self, "Delete Error", 
                                "Failed to delete the note. Please try again."
                            )
                        
                except Exception as e:
                    print(f"Error clearing fault note: {e}")
                    QtWidgets.QMessageBox.critical(
                        self, "Error", 
                        f"An error occurred while clearing the note: {str(e)}"
                    )

            def _load_fault_note(self, fault_code: str):
                """Load and display the note for a specific fault code"""
                try:
                    note_data = self.fault_notes_manager.get_note(fault_code)
                    if note_data:
                        self.ui.txtUserNote.setText(note_data.get('note', ''))
                        self._update_note_info(fault_code, note_data)
                    else:
                        self.ui.txtUserNote.clear()
                        self._update_note_info(fault_code)
                        
                except Exception as e:
                    print(f"Error loading fault note for {fault_code}: {e}")
                    self.ui.txtUserNote.clear()
                    self._update_note_info(fault_code)

            def _clear_fault_note_display(self):
                """Clear the note display area"""
                try:
                    if hasattr(self.ui, 'txtUserNote'):
                        self.ui.txtUserNote.clear()
                    if hasattr(self.ui, 'lblNoteInfo'):
                        self.ui.lblNoteInfo.setText("")
                except Exception as e:
                    print(f"Error clearing fault note display: {e}")

            def _update_note_info(self, fault_code: str, note_data=None):
                """Update the note information label"""
                try:
                    if not hasattr(self.ui, 'lblNoteInfo'):
                        return
                        
                    if note_data is None:
                        note_data = self.fault_notes_manager.get_note(fault_code)
                    
                    if note_data:
                        created_date = note_data.get('created_date', '')
                        last_modified = note_data.get('last_modified', '')
                        author = note_data.get('author', 'User')
                        
                        # Parse dates for display
                        try:
                            from datetime import datetime
                            if last_modified:
                                mod_date = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                                date_str = mod_date.strftime('%Y-%m-%d %H:%M')
                                info_text = f"Note by {author}, last modified: {date_str}"
                            else:
                                info_text = f"Note by {author}"
                        except:
                            info_text = f"Note by {author}"
                        
                        self.ui.lblNoteInfo.setText(info_text)
                    else:
                        total_notes = self.fault_notes_manager.get_notes_count()
                        self.ui.lblNoteInfo.setText(f"No note for this fault code. Total notes: {total_notes}")
                        
                except Exception as e:
                    print(f"Error updating note info: {e}")

            def _optimize_database(self):
                """Apply database optimizations"""
                try:
                    if hasattr(self, "db"):
                        self.db.optimize_for_reading()
                except Exception as e:
                    print(f"Database optimization error: {e}")

            def _update_memory_usage(self):
                """Monitor memory usage and perform cleanup when needed"""
                try:
                    import psutil
                    import gc

                    process = psutil.Process()
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)

                    # Update status bar with memory usage
                    if hasattr(self, "memory_label"):
                        self.memory_label.setText(f"Memory: {memory_mb:.1f} MB")
                    else:
                        self.memory_label = QtWidgets.QLabel(
                            f"Memory: {memory_mb:.1f} MB"
                        )
                        self.statusBar().addPermanentWidget(self.memory_label)

                    # Perform memory cleanup if usage is high
                    if memory_mb > 500:
                        print(f"🧹 High memory usage detected ({memory_mb:.1f} MB), performing cleanup...")
                        
                        # Clear old cache entries
                        if hasattr(self, '_data_cache'):
                            # Remove cache entries older than 10 minutes
                            current_time = time.time()
                            old_keys = [
                                key for key, value in self._data_cache.items()
                                if isinstance(value, dict) and 
                                current_time - value.get('timestamp', 0) > 600
                            ]
                            for key in old_keys:
                                del self._data_cache[key]
                            if old_keys:
                                print(f"🧹 Cleared {len(old_keys)} old cache entries")
                        
                        # Clear tab cache if it gets too large
                        if hasattr(self, '_tab_cache') and len(self._tab_cache) > 20:
                            self._tab_cache.clear()
                            print("🧹 Cleared tab cache")
                        
                        # Force garbage collection
                        collected = gc.collect()
                        print(f"🧹 Garbage collection freed {collected} objects")
                        
                        # Check memory again after cleanup
                        new_memory_mb = process.memory_info().rss / (1024 * 1024)
                        print(f"🧹 Memory after cleanup: {new_memory_mb:.1f} MB (saved {memory_mb - new_memory_mb:.1f} MB)")

                except Exception as e:
                    print(f"Error in memory monitoring: {e}")

            def _setup_branding(self):
                """Setup branding elements in the status bar"""
                try:
                    # Create status bar with branding
                    status_bar = self.statusBar()
                    status_bar.setStyleSheet("""
                        QStatusBar {
                            background-color: #f8f9fa;
                            color: #6c757d;
                            border-top: 1px solid #dee2e6;
                            font-size: 11px;
                        }
                        QStatusBar::item {
                            border: none;
                        }
                    """)

                    # Add branding label on the left
                    self.branding_label = QtWidgets.QLabel("Developed by gobioeng.com")
                    self.branding_label.setStyleSheet("""
                        QLabel {
                            color: #6c757d;
                            font-size: 11px;
                            padding: 2px 8px;
                        }
                    """)
                    status_bar.addWidget(self.branding_label)

                    # Add stretch to push memory info to the right
                    status_bar.addWidget(QtWidgets.QLabel(), 1)  # Stretch

                    print("✓ Branding setup complete")

                except Exception as e:
                    print(f"Error setting up branding: {e}")

            def show_about_dialog(self):
                """Show professional about dialog"""
                try:
                    from about_dialog import AboutDialog

                    about_dialog = AboutDialog(self)
                    about_dialog.exec_()
                except ImportError as e:
                    print(f"Failed to load about dialog: {e}")
                    QtWidgets.QMessageBox.about(
                        self,
                        "Gobioeng HALog",
                        "HALog 0.0.1 beta\nProfessional LINAC Log Analysis System\nDeveloped by gobioeng.com\n© 2025 gobioeng.com",
                    )

            def load_dashboard(self):
                """Load dashboard with professional optimizations and lazy loading"""
                try:
                    if not hasattr(self, "db"):
                        print("Database not initialized")
                        return

                    # First, load only summary data for faster startup
                    start_time = time.time()
                    
                    # Load metadata only initially for fast startup
                    summary_stats = self.db.get_summary_statistics()
                    if not summary_stats:
                        print("⚠️ No data available in database")
                        return
                    
                    # Load only a sample of recent data for UI initialization (last 1000 records)
                    try:
                        self.df = self.db.get_recent_logs(limit=1000)
                    except (TypeError, AttributeError):
                        # Fallback: Load minimal data for UI setup
                        try:
                            self.df = self.db.get_all_logs(chunk_size=1000)
                            if len(self.df) > 1000:
                                self.df = self.df.tail(1000)  # Keep only last 1000 for startup
                        except TypeError:
                            self.df = self.db.get_all_logs()
                            if len(self.df) > 1000:
                                self.df = self.df.tail(1000)

                    # Mark that we have partial data loaded
                    self._full_data_loaded = False
                    self._mark_data_updated()
                    
                    load_time = time.time() - start_time
                    print(f"⚡ Dashboard quick-loaded with {len(self.df)} sample records in {load_time:.2f}s")

                    if not self.df.empty:
                        # Find correct column names dynamically
                        serial_col = None
                        param_col = None
                        for col in self.df.columns:
                            if col in ['serial', 'serial_number']:
                                serial_col = col
                            elif col in ['param', 'parameter_type', 'parameter_name']:
                                param_col = col

                        latest = self.df.sort_values("datetime").iloc[-1]

                        # Display serial using correct column
                        if serial_col:
                            self.ui.lblSerial.setText(f"Serial: {latest[serial_col]}")
                        else:
                            self.ui.lblSerial.setText("Serial: Unknown")

                        self.ui.lblDate.setText(f"Date: {latest['datetime'].date()}")

                        dt_min = self.df["datetime"].min()
                        dt_max = self.df["datetime"].max()
                        duration = dt_max - dt_min

                        self.ui.lblDuration.setText(f"Duration: {duration}")
                        self.ui.lblRecordCount.setText(
                            f"Total Records: {len(self.df):,}"
                        )

                        # Count unique parameters using correct column
                        if param_col:
                            unique_params = self.df[param_col].nunique()
                            self.ui.lblParameterCount.setText(
                                f"Parameters: {unique_params}"
                            )
                        else:
                            self.ui.lblParameterCount.setText("Parameters: 0")

                        print(f"✓ Dashboard updated - Records: {len(self.df):,}, Parameters: {unique_params if param_col else 0}")
                    else:
                        self.ui.lblSerial.setText("Serial: No data imported")
                        self.ui.lblDate.setText("Date: No data imported")
                        self.ui.lblDuration.setText("Duration: No data imported")
                        self.ui.lblRecordCount.setText("Total Records: 0")
                        self.ui.lblParameterCount.setText("Parameters: 0")
                        print("⚠️ Dashboard shows no data - import log files first")

                    # Update UI components
                    self.update_trend_combos()
                    self.update_data_table()
                    self.update_analysis_tab()

                    # Initialize trend graphs with default parameters only if we have data
                    if not self.df.empty:
                        QtCore.QTimer.singleShot(300, self._refresh_all_trends)
                        QtCore.QTimer.singleShot(200, self.refresh_latest_mpc)

                except Exception as e:
                    print(f"Error loading dashboard: {e}")
                    traceback.print_exc()
                    
            def _ensure_full_data_loaded(self):
                """Load full dataset when needed for analysis"""
                if hasattr(self, '_full_data_loaded') and self._full_data_loaded:
                    return  # Already loaded
                    
                try:
                    print("📊 Loading full dataset for analysis...")
                    start_time = time.time()
                    
                    # Load all data now
                    try:
                        self.df = self.db.get_all_logs(chunk_size=10000)
                    except TypeError:
                        self.df = self.db.get_all_logs()
                    
                    self._full_data_loaded = True
                    load_time = time.time() - start_time
                    print(f"✅ Full dataset loaded: {len(self.df)} records in {load_time:.2f}s")
                    
                except Exception as e:
                    print(f"Error loading full data: {e}")
                    traceback.print_exc()

            def _refresh_all_trends(self):
                """Refresh all trend graphs with default data"""
                try:
                    print(f"🔄 Refreshing all trend graphs with {len(self.df)} records...")

                    if self.df.empty:
                        print("⚠️ No data available for trend graphs")
                        return

                    # Refresh each trend group with default parameters
                    trend_groups = ['flow', 'voltage', 'temperature', 'humidity', 'fan_speed']

                    for group in trend_groups:
                        try:
                            print(f"  Refreshing {group} trends...")
                            self.refresh_trend_tab(group)
                        except Exception as e:
                            print(f"  Error refreshing {group} trends: {e}")

                    print("✅ All trend graphs refreshed")

                except Exception as e:
                    print(f"Error refreshing trends: {e}")

            def clear_all_data(self):
                """Clear all imported data from the database"""
                try:
                    reply = QtWidgets.QMessageBox.question(
                        self,
                        "Clear All Data",
                        "Are you sure you want to clear all imported log data?\n\n"
                        "This action cannot be undone and will remove:\n"
                        "• All imported machine log data\n"
                        "• All file import history\n"
                        "• All trend and analysis data\n\n"
                        "Note: This will NOT affect the original log files.",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No
                    )

                    if reply == QtWidgets.QMessageBox.Yes:
                        if not hasattr(self, 'db'):
                            QtWidgets.QMessageBox.warning(self, "Error", "Database not initialized")
                            return

                        # Clear the database
                        self.db.clear_all()

                        # Clear UI data
                        import pandas as pd
                        if hasattr(self, 'df'):
                            self.df = pd.DataFrame()

                        # Refresh UI
                        self.load_dashboard()

                        QtWidgets.QMessageBox.information(
                            self,
                            "Data Cleared",
                            "All data has been successfully cleared from the database."
                        )

                        print("✅ All data cleared successfully")

                except Exception as e:
                    print(f"Error clearing data: {e}")
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Clear Data Error",
                        f"Error clearing data: {str(e)}"
                    )

            def optimize_database(self):
                """Optimize the database for better performance"""
                try:
                    if not hasattr(self, 'db'):
                        QtWidgets.QMessageBox.warning(self, "Error", "Database not initialized")
                        return

                    # Show progress dialog
                    progress = QtWidgets.QProgressDialog(
                        "Optimizing database...", None, 0, 100, self
                    )
                    progress.setWindowTitle("Database Optimization")
                    progress.setWindowModality(QtCore.Qt.WindowModal)
                    progress.show()
                    progress.setValue(25)
                    QtWidgets.QApplication.processEvents()

                    # Get database size before optimization
                    size_before = self.db.get_database_size()

                    progress.setValue(50)
                    progress.setLabelText("Running VACUUM operation...")
                    QtWidgets.QApplication.processEvents()

                    # Optimize database
                    self.db.vacuum_database()

                    progress.setValue(75)
                    progress.setLabelText("Applying reading optimizations...")
                    QtWidgets.QApplication.processEvents()

                    # Apply reading optimizations
                    self.db.optimize_for_reading()

                    progress.setValue(100)
                    QtWidgets.QApplication.processEvents()

                    # Get database size after optimization
                    size_after = self.db.get_database_size()
                    size_saved = size_before - size_after
                    size_saved_mb = size_saved / (1024 * 1024) if size_saved > 0 else 0

                    progress.close()

                    QtWidgets.QMessageBox.information(
                        self,
                        "Database Optimized",
                        f"Database optimization completed successfully.\n\n"
                        f"Space saved: {size_saved_mb:.2f} MB\n"
                        f"Database should now perform better for queries and analysis."
                    )

                    print(f"✅ Database optimized - saved {size_saved_mb:.2f} MB")

                except Exception as e:
                    print(f"Error optimizing database: {e}")
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Optimization Error",
                        f"Error optimizing database: {str(e)}"
                    )

            def update_trend_combos(self):
                """Update trend combo boxes with professional styling"""
                try:
                    if hasattr(self, "df") and not self.df.empty:
                        # Find correct column names dynamically
                        serial_col = None
                        param_col = None

                        for col in self.df.columns:
                            if col in ['serial', 'serial_number']:
                                serial_col = col
                            elif col in ['param', 'parameter_type', 'parameter_name']:
                                param_col = col

                        if serial_col:
                            serials = sorted(set(map(str, self.df[serial_col].unique())))
                        else:
                            serials = []

                        if param_col:
                            params = sorted(set(map(str, self.df[param_col].unique())))
                        else:
                            params = []
                    else:
                        serials = []
                        params = []

                    # Check if the UI elements exist before accessing them
                    if hasattr(self.ui, 'comboTrendSerial'):
                        self.ui.comboTrendSerial.blockSignals(True)
                        self.ui.comboTrendSerial.clear()
                        self.ui.comboTrendSerial.addItems(["All"] + serials)
                        self.ui.comboTrendSerial.blockSignals(False)

                    if hasattr(self.ui, 'comboTrendParam'):
                        self.ui.comboTrendParam.blockSignals(True)
                        self.ui.comboTrendParam.clear()
                        self.ui.comboTrendParam.addItems(["All"] + params)
                        self.ui.comboTrendParam.blockSignals(False)

                    self.update_trend()
                except Exception as e:
                    print(f"Error updating trend combos: {e}")

            def update_data_table(self, page_size=None):
                """Update data table with optimized performance for large datasets"""
                try:
                    from PyQt5.QtWidgets import QTableWidgetItem
                    from PyQt5.QtCore import Qt
                    import pandas as pd
                    
                    if not hasattr(self, "df") or self.df.empty:
                        self.ui.tableData.setRowCount(0)
                        self.ui.lblTableInfo.setText("No data available")
                        return

                    # Smart page sizing based on dataset size
                    if page_size is None:
                        total_records = len(self.df)
                        if total_records > 50000:
                            page_size = 500   # Very large datasets: show only 500 rows
                        elif total_records > 10000:
                            page_size = 1000  # Large datasets: show 1000 rows  
                        elif total_records > 1000:
                            page_size = 2000  # Medium datasets: show 2000 rows
                        else:
                            page_size = total_records  # Small datasets: show all

                    # Use cached sorted data if available and not stale
                    cache_key = 'sorted_data_table'
                    if (hasattr(self, '_data_cache') and 
                        cache_key in self._data_cache and 
                        self._data_cache[cache_key]['timestamp'] > getattr(self, '_last_data_update', 0)):
                        display_df = self._data_cache[cache_key]['data']
                        param_col = self._data_cache[cache_key]['param_col']
                        print("📋 Using cached sorted data for table (performance optimization)")
                    else:
                        print(f"🔍 DataFrame columns: {list(self.df.columns)}")
                        print(f"🔍 DataFrame shape: {self.df.shape}")

                        # Find parameter column
                        param_col = None
                        for col in ['param', 'parameter_type', 'parameter_name']:
                            if col in self.df.columns:
                                param_col = col
                                break
                        
                        print(f"🔍 Using parameter column: '{param_col}'")

                        if not param_col:
                            self.ui.tableData.setRowCount(0)
                            self.ui.lblTableInfo.setText("No parameter column found")
                            return

                        # Sort by parameter name, then by datetime (newest first) - expensive operation
                        print("📋 Sorting data for table display...")
                        df_sorted = self.df.sort_values([param_col, 'datetime'], ascending=[True, False])
                        display_df = df_sorted.iloc[:page_size]
                        
                        # Cache the sorted result
                        if not hasattr(self, '_data_cache'):
                            self._data_cache = {}
                        self._data_cache[cache_key] = {
                            'data': display_df,
                            'param_col': param_col,
                            'timestamp': time.time()
                        }

                    # Find column mappings with better fallbacks (cached)
                    if not hasattr(self, '_column_mapping_cache'):
                        serial_col = None
                        avg_col = None
                        min_col = None 
                        max_col = None
                        
                        # Map columns
                        for col in self.df.columns:
                            col_lower = col.lower()
                            if col_lower in ['serial', 'serial_number']:
                                serial_col = col
                            elif col_lower in ['avg', 'average', 'avg_value']:
                                avg_col = col
                            elif col_lower in ['min', 'min_value', 'minimum']:
                                min_col = col
                            elif col_lower in ['max', 'max_value', 'maximum']:
                                max_col = col
                        
                        self._column_mapping_cache = {
                            'serial_col': serial_col,
                            'avg_col': avg_col,
                            'min_col': min_col,
                            'max_col': max_col
                        }
                    
                    # Use cached column mappings
                    serial_col = self._column_mapping_cache['serial_col']
                    avg_col = self._column_mapping_cache['avg_col']
                    min_col = self._column_mapping_cache['min_col']
                    max_col = self._column_mapping_cache['max_col']

                    # Set table size and headers (match main_window.py which expects 7 columns)
                    self.ui.tableData.setRowCount(len(display_df))
                    self.ui.tableData.setColumnCount(7)
                    self.ui.tableData.setHorizontalHeaderLabels([
                        "DateTime",
                        "Serial", 
                        "Parameter",
                        "Average",
                        "Min",
                        "Max",
                        "Diff (Max-Min)"
                    ])

                    # Optimize table population with batch updates
                    self.ui.tableData.setSortingEnabled(False)  # Disable sorting during updates
                    self.ui.tableData.setUpdatesEnabled(False)  # Disable updates during population

                    # Populate table rows with optimized performance
                    for row_idx, (_, row) in enumerate(display_df.iterrows()):
                        try:
                            # DateTime
                            dt_str = row["datetime"].strftime("%Y-%m-%d %H:%M:%S") if pd.notna(row["datetime"]) else "N/A"
                            dt_item = QTableWidgetItem(dt_str)
                            dt_item.setFlags(dt_item.flags() & ~Qt.ItemIsEditable)
                            self.ui.tableData.setItem(row_idx, 0, dt_item)

                            # Serial Number
                            serial_value = "Unknown"
                            if serial_col and pd.notna(row[serial_col]):
                                serial_value = str(row[serial_col])
                            serial_item = QTableWidgetItem(serial_value)
                            serial_item.setFlags(serial_item.flags() & ~Qt.ItemIsEditable)
                            self.ui.tableData.setItem(row_idx, 1, serial_item)

                            # Parameter Name (use enhanced name)
                            raw_param = str(row[param_col])
                            display_param = self._get_enhanced_parameter_name(raw_param)
                            param_item = QTableWidgetItem(display_param)
                            param_item.setToolTip(f"Raw parameter: {raw_param}")  # Show raw name in tooltip
                            param_item.setFlags(param_item.flags() & ~Qt.ItemIsEditable)
                            self.ui.tableData.setItem(row_idx, 2, param_item)

                            # Average value
                            avg_value = 0.0
                            if avg_col and pd.notna(row[avg_col]):
                                try:
                                    avg_value = float(row[avg_col])
                                except (ValueError, TypeError):
                                    avg_value = 0.0
                            avg_item = QTableWidgetItem(f"{avg_value:.4f}")
                            avg_item.setFlags(avg_item.flags() & ~Qt.ItemIsEditable)
                            self.ui.tableData.setItem(row_idx, 3, avg_item)

                            # Min value
                            min_value = 0.0
                            if min_col and pd.notna(row[min_col]):
                                try:
                                    min_value = float(row[min_col])
                                except (ValueError, TypeError):
                                    min_value = 0.0
                            min_item = QTableWidgetItem(f"{min_value:.4f}")
                            min_item.setFlags(min_item.flags() & ~Qt.ItemIsEditable)
                            self.ui.tableData.setItem(row_idx, 4, min_item)

                            # Max value
                            max_value = 0.0
                            if max_col and pd.notna(row[max_col]):
                                try:
                                    max_value = float(row[max_col])
                                except (ValueError, TypeError):
                                    max_value = 0.0
                            max_item = QTableWidgetItem(f"{max_value:.4f}")
                            max_item.setFlags(max_item.flags() & ~Qt.ItemIsEditable)
                            self.ui.tableData.setItem(row_idx, 5, max_item)

                            # Difference (Max - Min)
                            diff_value = max_value - min_value
                            diff_item = QTableWidgetItem(f"{diff_value:.4f}")
                            diff_item.setFlags(diff_item.flags() & ~Qt.ItemIsEditable)
                            self.ui.tableData.setItem(row_idx, 6, diff_item)

                        except Exception as e:
                            print(f"Error processing row {row_idx}: {e}")
                            # Fill row with N/A values if there's an error
                            for col_idx in range(7):
                                if not self.ui.tableData.item(row_idx, col_idx):
                                    placeholder_item = QTableWidgetItem("N/A")
                                    placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsEditable)
                                    self.ui.tableData.setItem(row_idx, col_idx, placeholder_item)

                    # Re-enable table updates and sorting
                    self.ui.tableData.setUpdatesEnabled(True)
                    self.ui.tableData.setSortingEnabled(True)

                    # Auto-resize columns to content (only if not done recently)
                    if not hasattr(self, '_last_column_resize') or time.time() - self._last_column_resize > 30:
                        self.ui.tableData.resizeColumnsToContents()
                        self._last_column_resize = time.time()

                    # Update info label
                    total_records = len(self.df)
                    showing_records = len(display_df)
                    unique_params = self.df[param_col].nunique()

                    self.ui.lblTableInfo.setText(
                        f"Showing {showing_records:,} of {total_records:,} records | "
                        f"Unique Parameters: {unique_params} | Sorted by parameter name, then date"
                    )

                    print(f"✓ Data table updated: {showing_records:,} records displayed with {unique_params} unique parameters")

                except Exception as e:
                    print(f"Error updating data table: {e}")
                    import traceback
                    traceback.print_exc()
                    self.ui.lblTableInfo.setText("Error loading data table")

            def update_analysis_tab(self):
                """Update analysis tab with professional progress"""
                try:
                    if not hasattr(self, "df") or self.df.empty:
                        self.ui.tableTrends.setRowCount(0)
                        return

                    if len(self.df) > 10000:
                        try:
                            from worker_thread import AnalysisWorker
                            from analyzer_data import DataAnalyzer

                            progress_dialog = QtWidgets.QProgressDialog(
                                "Analyzing data...", "Cancel", 0, 100, self
                            )
                            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
                            progress_dialog.setMinimumDuration(0)
                            progress_dialog.setValue(0)
                            progress_dialog.show()

                            analyzer = DataAnalyzer()
                            worker = AnalysisWorker(analyzer, self.df)

                            worker.analysis_progress.connect(
                                lambda p, m: progress_dialog.setValue(p)
                            )
                            worker.analysis_finished.connect(
                                lambda results: self._display_analysis_results(
                                    results, progress_dialog
                                )
                            )
                            worker.analysis_error.connect(
                                lambda msg: self._handle_analysis_error(
                                    msg, progress_dialog
                                )
                            )

                            progress_dialog.canceled.connect(worker.cancel_analysis)
                            worker.start()
                        except Exception as e:
                            print(f"Error creating analysis worker: {e}")
                            self._direct_analysis()
                    else:
                        self._direct_analysis()

                except Exception as e:
                    print(f"Error updating analysis tab: {e}")
                    traceback.print_exc()

            def _direct_analysis(self):
                """Perform analysis directly without worker"""
                try:
                    from analyzer_data import DataAnalyzer

                    analyzer = DataAnalyzer()

                    analysis_df = self.df.copy()

                    if (
                        "param" in analysis_df.columns
                        and "parameter_type" not in analysis_df.columns
                    ):
                        analysis_df["parameter_type"] = analysis_df["param"]

                    if "statistic_type" not in analysis_df.columns:
                        if "stat_type" in analysis_df.columns:
                            analysis_df["statistic_type"] = analysis_df["stat_type"]
                        else:
                            analysis_df["statistic_type"] = "avg"

                    if (
                        "avg" in analysis_df.columns
                        and "value" not in analysis_df.columns
                    ):
                        analysis_df["value"] = analysis_df["avg"]

                    try:
                        trends_df = analyzer.calculate_advanced_trends(analysis_df)
                        self._populate_trends_table(trends_df)
                    except Exception as e:
                        print(f"Error calculating trends: {e}")
                        import pandas as pd

                        empty_trends = pd.DataFrame(
                            columns=[
                                "parameter_type",
                                "statistic_type",
                                "data_points",
                                "time_span_hours",
                                "trend_slope",
                                "trend_direction",
                                "trend_strength",
                            ]
                        )
                        self._populate_trends_table(empty_trends)

                except Exception as e:
                    print(f"Error in direct analysis: {e}")
                    traceback.print_exc()

            def _display_analysis_results(self, results, progress_dialog=None):
                """Display analysis results after worker completes"""
                try:
                    if progress_dialog:
                        progress_dialog.setValue(100)
                        progress_dialog.close()

                    if "trends" in results:
                        self._populate_trends_table(results["trends"])
                except Exception as e:
                    print(f"Error displaying analysis results: {e}")

            def _handle_analysis_error(self, error_message, progress_dialog=None):
                """Handle analysis errors from worker thread"""
                try:
                    if progress_dialog:
                        progress_dialog.close()

                    QtWidgets.QMessageBox.warning(
                        self,
                        "Analysis Error",
                        f"Error during data analysis: {error_message}",
                    )
                except Exception as e:
                    print(f"Error handling analysis error: {e}")

            def _populate_trends_table(self, trends_df):
                """Populate trends table with enhanced analysis results"""
                try:
                    from PyQt5 import QtGui

                    if trends_df.empty:
                        self.ui.tableTrends.setRowCount(0)
                        return

                    self.ui.tableTrends.setRowCount(len(trends_df))
                    for i, (_, row) in enumerate(trends_df.iterrows()):
                        # Enhanced parameter name display
                        param_name = str(row.get("parameter_type", ""))
                        enhanced_name = self._get_enhanced_parameter_name(param_name)

                        param_item = QtWidgets.QTableWidgetItem(enhanced_name)
                        param_item.setToolTip(f"Original: {param_name}")  # Show original name in tooltip
                        self.ui.tableTrends.setItem(i, 0, param_item)

                        # Parameter group
                        group = self._get_parameter_group(param_name)
                        group_item = QtWidgets.QTableWidgetItem(group)
                        self.ui.tableTrends.setItem(i, 1, group_item)

                        # Other columns
                        self.ui.tableTrends.setItem(
                            i, 2, QtWidgets.QTableWidgetItem(str(row.get("statistic_type", "")))
                        )
                        self.ui.tableTrends.setItem(
                            i, 3, QtWidgets.QTableWidgetItem(str(row.get("data_points", "")))
                        )
                        self.ui.tableTrends.setItem(
                            i, 4, QtWidgets.QTableWidgetItem(f"{row.get('time_span_hours', 0):.1f}")
                        )

                        # Slope with color coding
                        slope = row.get('trend_slope', 0)
                        slope_item = QtWidgets.QTableWidgetItem(f"{slope:.4f}")
                        if slope > 0.01:
                            slope_item.setBackground(QtGui.QColor(255, 200, 200))  # Light red for increasing
                        elif slope < -0.01:
                            slope_item.setBackground(QtGui.QColor(200, 255, 200))  # Light green for decreasing
                        self.ui.tableTrends.setItem(i, 5, slope_item)

                        # Direction with icons
                        direction = str(row.get("trend_direction", ""))
                        if direction.lower() == "increasing":
                            direction = "📈 Increasing"
                        elif direction.lower() == "decreasing":
                            direction = "📉 Decreasing"
                        elif direction.lower() == "stable":
                            direction = "➡️ Stable"
                        self.ui.tableTrends.setItem(i, 6, QtWidgets.QTableWidgetItem(direction))

                        # Strength with color coding
                        strength = str(row.get("trend_strength", ""))
                        strength_item = QtWidgets.QTableWidgetItem(strength)
                        if strength.lower() == "strong":
                            strength_item.setBackground(QtGui.QColor(255, 255, 200))  # Light yellow
                        elif strength.lower() == "weak":
                            strength_item.setBackground(QtGui.QColor(240, 240, 240))  # Light gray
                        self.ui.tableTrends.setItem(i, 7, strength_item)

                    # Ensure proper row heights
                    self.ui.tableTrends.resizeRowsToContents()

                except Exception as e:
                    print(f"Error populating trends table: {e}")

            def _get_enhanced_parameter_name(self, param_name):
                """Map original parameter names to enhanced display names using parser mapping"""
                try:
                    # Try to get the enhanced name from the parser mapping first
                    from unified_parser import UnifiedParser
                    parser = UnifiedParser()

                    # Check if this parameter has a mapping with description
                    if param_name in parser.parameter_mapping:
                        description = parser.parameter_mapping[param_name].get('description', param_name)
                        if description != param_name:
                            return description

                    # Fallback to hardcoded mapping for compatibility
                    parameter_name_mapping = {
                        # Water System
                        "magnetronFlow": "Mag Flow",
                        "targetAndCirculatorFlow": "Flow Target",
                        "cityWaterFlow": "Flow Chiller Water",
                        "pumpPressure": "Cooling Pump Pressure",

                        # Voltages
                        "MLC_ADC_CHAN_TEMP_BANKA_STAT_48V": "MLC Bank A 48V",
                        "MLC_ADC_CHAN_TEMP_BANKB_STAT_48V": "MLC Bank B 48V",
                        "MLC_ADC_CHAN_TEMP_BANKA_STAT_24V": "MLC Bank A 24V",
                        "MLC_ADC_CHAN_TEMP_BANKB_STAT_24V": "MLC Bank B 24V",
                        "COL_ADC_CHAN_TEMP_24V_MON": "COL 24V Monitor",
                        "COL_ADC_CHAN_TEMP_5V_MON": "COL 5V Monitor",

                        # Temperatures
                        "magnetronTemp": "Temp Magnetron",
                        "colBoardTemp": "Temp COL Board",
                        "pduTemp": "Temp PDU",
                        "FanremoteTempStatistics": "Temp Room",
                        "waterTankTemp": "Temp Water Tank",

                        # Fan Speeds
                        "FanfanSpeed1Statistics": "Speed FAN 1",
                        "FanfanSpeed2Statistics": "Speed FAN 2",
                        "FanfanSpeed3Statistics": "Speed FAN 3",
                        "FanfanSpeed4Statistics": "Speed FAN 4",
                        "FanSpeed1Statistics": "Speed FAN 1",
                        "FanSpeed2Statistics": "Speed FAN 2",

                        # Humidity
                        "FanhumidityStatistics": "Room Humidity",
                    }

                    # Return enhanced name if mapping exists, otherwise return original
                    return parameter_name_mapping.get(param_name, param_name)

                except Exception as e:
                    print(f"Error getting enhanced parameter name for '{param_name}': {e}")
                    return param_name

            def _get_parameter_group(self, param_name):
                """Determine parameter group for categorization"""
                param_lower = param_name.lower()

                if any(term in param_lower for term in ['flow', 'pressure', 'pump']):
                    return "Water System"
                elif any(term in param_lower for term in ['volt', '_v_', '24v', '48v', '5v', 'mlc_adc', 'col_adc']):
                    return "Voltages"
                elif any(term in param_lower for term in ['temp', 'temperature']):
                    return "Temperatures"
                elif any(term in param_lower for term in ['fan', 'speed']):
                    return "Fan Speeds"
                elif any(term in param_lower for term in ['humidity']):
                    return "Humidity"
                else:
                    return "Other"

            def _filter_analysis_results(self):
                """Filter analysis results based on selected group"""
                try:
                    if not hasattr(self, 'comboAnalysisFilter'):
                        return

                    selected_filter = self.ui.comboAnalysisFilter.currentText()

                    if selected_filter == "All Parameters":
                        # Show all rows
                        for row in range(self.ui.tableTrends.rowCount()):
                            self.ui.tableTrends.setRowHidden(row, False)
                    else:
                        # Hide rows that don't match the filter
                        filter_mapping = {
                            "Water System": "Water System",
                            "Voltages": "Voltages",
                            "Temperatures": "Temperatures",
                            "Fan Speeds": "Fan Speeds",
                            "Humidity": "Humidity"
                        }

                        target_group = filter_mapping.get(selected_filter, "")

                        for row in range(self.ui.tableTrends.rowCount()):
                            group_item = self.ui.tableTrends.item(row, 1)  # Group is column 1
                            if group_item:
                                group_text = group_item.text()
                                should_hide = (target_group != group_text)
                                self.ui.tableTrends.setRowHidden(row, should_hide)

                except Exception as e:
                    print(f"Error filtering analysis results: {e}")

            def on_tab_changed(self, index):
                """Handle tab changes with enhanced performance optimization and caching"""
                try:
                    # Initialize enhanced tab cache if not exists
                    if not hasattr(self, '_enhanced_tab_cache'):
                        self._enhanced_tab_cache = {}
                    
                    # Track last data modification time to know when to refresh
                    if not hasattr(self, '_last_data_update'):
                        self._last_data_update = 0
                    
                    current_time = time.time()
                    tab_name = f"tab_{index}"
                    
                    # Use performance manager for caching if available
                    if hasattr(self, 'performance_manager'):
                        cached_tab_data = self.performance_manager.get_cached_tab_data(tab_name, max_age_seconds=300)
                        if cached_tab_data and not self._data_updated_since_cache():
                            print(f"⚡ Using cached data for tab {index} (enhanced performance optimization)")
                            return
                    
                    # Ensure components are initialized before trying to update
                    if not getattr(self, '_dashboard_loaded', False) and index in [0, 2, 3]:
                        print("📊 Loading dashboard data on first access...")
                        self.load_dashboard()
                        self._dashboard_loaded = True
                        
                    if not getattr(self, '_trend_controls_initialized', False) and index == 1:
                        print("📈 Initializing trend controls on first access...")
                        self._initialize_trend_controls()
                        self._trend_controls_initialized = True
                    
                    # Only update if tab hasn't been cached or data has been updated
                    should_update = (
                        tab_name not in self._enhanced_tab_cache or 
                        self._enhanced_tab_cache[tab_name] < self._last_data_update or
                        current_time - self._enhanced_tab_cache.get(tab_name, 0) > 300  # Force refresh every 5 minutes
                    )
                    
                    if should_update:
                        print(f"🔄 Updating tab {index} data...")
                        tab_data = None
                        
                        if index == 1:  # Trends tab
                            self.update_trend()
                            tab_data = {"type": "trend", "updated_at": current_time}
                        elif index == 2:  # Data Table tab
                            self.update_data_table()
                            tab_data = {"type": "data_table", "updated_at": current_time}
                        elif index == 3:  # Analysis tab
                            self.update_analysis_tab()
                            tab_data = {"type": "analysis", "updated_at": current_time}
                        
                        # Update cache timestamp
                        self._enhanced_tab_cache[tab_name] = current_time
                        
                        # Cache tab data in performance manager
                        if hasattr(self, 'performance_manager') and tab_data:
                            self.performance_manager.optimize_tab_caching({tab_name: tab_data})
                    else:
                        print(f"✅ Using cached data for tab {index} (performance optimization)")
                        
                except Exception as e:
                    print(f"Error handling tab change: {e}")
                    traceback.print_exc()
                    
            def _data_updated_since_cache(self) -> bool:
                """Check if data has been updated since last cache"""
                try:
                    if not hasattr(self, '_last_data_update'):
                        return True
                    
                    # Check database modification time if available
                    if hasattr(self, 'db') and hasattr(self.db, 'db_path'):
                        if os.path.exists(self.db.db_path):
                            db_mtime = os.path.getmtime(self.db.db_path)
                            return db_mtime > self._last_data_update
                    
                    return False
                except Exception as e:
                    print(f"Error checking data update status: {e}")
                    return True  # Safe default
                    
            def _mark_data_updated(self):
                """Mark that data has been updated to invalidate tab cache"""
                self._last_data_update = time.time()
                if hasattr(self, '_enhanced_tab_cache'):
                    self._enhanced_tab_cache.clear()
                if hasattr(self, '_tab_cache'):
                    self._tab_cache.clear()
                    
                # Clear performance manager cache too
                if hasattr(self, 'performance_manager'):
                    self.performance_manager.clear_cache("performance")

            def update_trend(self):
                """Update trend visualization with professional styling - Legacy compatibility"""
                try:
                    if not hasattr(self, "df") or self.df.empty:
                        return

                    # Check if legacy trend controls exist
                    if hasattr(self.ui, 'comboTrendSerial') and hasattr(self.ui, 'comboTrendParam'):
                        serial = self.ui.comboTrendSerial.currentText()
                        param = self.ui.comboTrendParam.currentText()

                        if serial == "All" and param == "All":
                            df_trend = self.df
                        else:
                            import numpy as np

                            mask = np.ones(len(self.df), dtype=bool)
                            if serial and serial != "All":
                                mask &= self.df["serial"] == serial
                            if param and param != "All":
                                mask &= self.df["param"] == param
                            df_trend = self.df[mask]

                        from utils_plot import plot_trend

                        # Check if legacy plotWidget exists
                        if hasattr(self.ui, 'plotWidget'):
                            if len(df_trend) > 10000:
                                print(f"Downsampling large trend data: {len(df_trend)} points")
                                plot_trend(self.ui.plotWidget, df_trend)
                            else:
                                plot_trend(self.ui.plotWidget, df_trend)
                        else:
                            print("Legacy plotWidget not found - using new trend system")
                    else:
                        # If legacy controls don't exist, initialize default trend displays for new system
                        print("Initializing trend displays with new system")
                        self._initialize_default_trend_displays()

                except Exception as e:
                    print(f"Error updating trend: {e}")
                    traceback.print_exc()

            def _initialize_default_trend_displays(self):
                """Initialize default trend displays to show graphs at startup"""
                try:
                    print("🔄 Initializing default trend displays...")
                    # Check if we have shortdata_parser available
                    if hasattr(self, 'shortdata_parser') and self.shortdata_parser:
                        # Initialize each trend group with default displays
                        trend_groups = ['flow', 'voltage', 'temperature', 'humidity', 'fan_speed']
                        for group in trend_groups:
                            try:
                                self.refresh_trend_tab(group)
                                print(f"  ✓ {group} trend initialized")
                            except Exception as e:
                                print(f"  ⚠️ Failed to initialize {group} trend: {e}")
                    else:
                        print("  ⚠️ Shortdata parser not available for trend initialization")
                except Exception as e:
                    print(f"Error initializing default trend displays: {e}")

            def _initialize_default_trends(self):
                """Initialize default trend displays for the new trend tab system"""
                try:
                    # Trigger refresh for each trend tab group to show default graphs
                    trend_groups = ['flow', 'voltage', 'temperature', 'humidity', 'fan_speed']
                    for group in trend_groups:
                        self.refresh_trend_tab(group)
                except Exception as e:
                    print(f"Error initializing default trends: {e}")

            def import_log_file(self):
                """MAIN LOG FILE IMPORT FUNCTION - Enhanced with multi-file selection and progress dialog"""
                print("🔥 LOG FILE IMPORT TRIGGERED!")
                try:
                    # Enable multi-file selection
                    file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
                        self,
                        "Open LINAC Log Files (Select Multiple Files)",
                        "",
                        "Log Files (*.txt *.log);;Text Files (*.txt);;All Files (*)",
                    )

                    if not file_paths:
                        print("No files selected")
                        return

                    print(f"Selected {len(file_paths)} file(s):")
                    for file_path in file_paths:
                        print(f"  - {file_path}")

                    # Create progress dialog for multi-file upload
                    from progress_dialog import ProgressDialog
                    
                    self.progress_dialog = ProgressDialog(self)
                    self.progress_dialog.setWindowTitle(f"Processing {len(file_paths)} LINAC Log Files")
                    self.progress_dialog.setModal(True)
                    self.progress_dialog.show()
                    self.progress_dialog.set_phase("uploading", 0)
                    QtWidgets.QApplication.processEvents()

                    # Process files sequentially with proper memory management
                    total_records_imported = 0
                    successful_imports = 0
                    
                    for i, file_path in enumerate(file_paths):
                        try:
                            file_size = os.path.getsize(file_path)
                            filename = os.path.basename(file_path)
                            
                            # Update progress for current file
                            file_progress = int((i / len(file_paths)) * 100)
                            self.progress_dialog.update_progress(
                                file_progress, 
                                f"Processing file {i+1}/{len(file_paths)}: {filename}",
                                i, len(file_paths)
                            )
                            QtWidgets.QApplication.processEvents()
                            
                            # Check if user cancelled
                            if self.progress_dialog.wasCanceled():
                                print("Multi-file upload cancelled by user")
                                return
                            
                            print(f"Processing file {i+1}/{len(file_paths)}: {filename} ({file_size} bytes)")

                            filename_lower = filename.lower()

                            # Check if it's a shortdata file (sample only)
                            if 'shortdata' in filename_lower:
                                print(f"⚠️ Treating {filename} as sample data only (not permanently stored)")
                                self._process_sample_shortdata(file_path)
                                successful_imports += 1
                            # Check if it's a fault file that should be filtered and stored permanently
                            elif 'tbfault' in filename_lower or 'halfault' in filename_lower:
                                print(f"🔍 Processing fault file with filtering: {filename}")
                                if file_size < 5 * 1024 * 1024:
                                    records = self._import_small_file_filtered(file_path)
                                else:
                                    records = self._import_large_file_filtered(file_path, file_size)
                                if records > 0:
                                    total_records_imported += records
                                    successful_imports += 1
                            else:
                                # Regular machine log file - import all data for MPC, trend, analysis
                                print(f"📊 Processing machine log file: {filename}")
                                if file_size < 5 * 1024 * 1024:
                                    records = self._import_small_file_single(file_path)
                                else:
                                    records = self._import_large_file_single(file_path, file_size)
                                if records > 0:
                                    total_records_imported += records
                                    successful_imports += 1
                                    
                            # Update progress after each file
                            completed_progress = int(((i + 1) / len(file_paths)) * 85)  # Leave 15% for finalization
                            self.progress_dialog.update_progress(
                                completed_progress,
                                f"Completed {filename} - {successful_imports}/{i+1} files processed successfully"
                            )
                            QtWidgets.QApplication.processEvents()
                            
                            # Force garbage collection between files
                            import gc
                            gc.collect()
                            
                        except Exception as e:
                            print(f"Error processing file {os.path.basename(file_path)}: {e}")
                            # Continue with next file even if current one fails
                            continue
                    
                    # Finalization phase
                    self.progress_dialog.set_phase("finalizing", 85)
                    self.progress_dialog.update_progress(90, "Refreshing database and UI components...")
                    QtWidgets.QApplication.processEvents()

                    # Final UI update after all files processed
                    if successful_imports > 0:
                        try:
                            self.df = self.db.get_all_logs(chunk_size=10000)
                        except TypeError:
                            self.df = self.db.get_all_logs()
                        
                        # Update progress during UI refresh
                        self.progress_dialog.update_progress(92, "Loading dashboard...")
                        QtWidgets.QApplication.processEvents()
                        self.load_dashboard()
                        
                        self.progress_dialog.update_progress(94, "Initializing trend controls...")
                        QtWidgets.QApplication.processEvents()
                        self._initialize_trend_controls()
                        self.update_trend_combos()
                        
                        self.progress_dialog.update_progress(96, "Updating data tables...")
                        QtWidgets.QApplication.processEvents()
                        self.update_data_table()
                        self.update_analysis_tab()

                        self.progress_dialog.update_progress(98, "Finalizing trends and analysis...")
                        QtWidgets.QApplication.processEvents()

                        # Initialize default trend displays
                        QtCore.QTimer.singleShot(500, self._refresh_all_trends)

                        # Initialize MPC tab with new data
                        QtCore.QTimer.singleShot(300, self.refresh_latest_mpc)

                        # Mark as complete and close progress dialog
                        self.progress_dialog.mark_complete()
                        QtCore.QTimer.singleShot(1000, self.progress_dialog.close)  # Close after 1 second

                        QtWidgets.QMessageBox.information(
                            self,
                            "Multi-File Import Successful",
                            f"Successfully processed {successful_imports}/{len(file_paths)} files.\n\n"
                            f"Total records imported: {total_records_imported:,}\n"
                            f"Dashboard, trends, and analysis tabs have been updated.",
                        )
                    else:
                        self.progress_dialog.close()
                        QtWidgets.QMessageBox.warning(
                            self,
                            "Import Warning",
                            "No files were successfully processed.\n\n"
                            "Please check that the files contain valid LINAC log data."
                        )

                except Exception as e:
                    # Close progress dialog if it exists
                    if hasattr(self, 'progress_dialog') and self.progress_dialog:
                        self.progress_dialog.close()
                    
                    print(f"Error in import_log_file: {e}")
                    traceback.print_exc()
                    QtWidgets.QMessageBox.critical(
                        self, "Import Error", f"Error importing log file: {str(e)}"
                    )

            def _import_small_file_single(self, file_path):
                """Import single small log file and return record count"""
                try:
                    from unified_parser import UnifiedParser
                    parser = UnifiedParser()
                    
                    print(f"Parsing {os.path.basename(file_path)}...")
                    df = parser.parse_linac_file(file_path)
                    
                    if df.empty:
                        print(f"No valid data found in {os.path.basename(file_path)}")
                        return 0
                    
                    print(f"✓ Data cleaned: {len(df)} records ready for database")
                    
                    # Insert data in batch with timing
                    import time
                    start_time = time.time()
                    records_inserted = self.db.insert_data_batch(df)
                    end_time = time.time()
                    
                    # Calculate and display performance metrics
                    duration = end_time - start_time
                    records_per_sec = records_inserted / duration if duration > 0 else 0
                    
                    print(f"Batch insert completed: {records_inserted} records in {duration:.2f}s ({records_per_sec:.1f} records/sec)")
                    
                    # Insert file metadata
                    filename = os.path.basename(file_path)
                    parsing_stats_json = "{}"
                    self.db.insert_file_metadata(
                        filename=filename,
                        file_size=os.path.getsize(file_path),
                        records_imported=records_inserted,
                        parsing_stats=parsing_stats_json,
                    )
                    
                    return records_inserted
                    
                except Exception as e:
                    print(f"Error importing {os.path.basename(file_path)}: {e}")
                    return 0

            def _import_large_file_single(self, file_path, file_size):
                """Import single large log file and return record count"""
                try:
                    from unified_parser import UnifiedParser
                    parser = UnifiedParser()
                    
                    print(f"Parsing large file {os.path.basename(file_path)}...")
                    df = parser.parse_linac_file(file_path, chunk_size=5000)
                    
                    if df.empty:
                        print(f"No valid data found in {os.path.basename(file_path)}")
                        return 0
                    
                    print(f"✓ Data cleaned: {len(df)} records ready for database")
                    
                    # Insert data in optimized batches with timing
                    import time
                    start_time = time.time()
                    records_inserted = self.db.insert_data_batch(df, batch_size=500)
                    end_time = time.time()
                    
                    # Calculate and display performance metrics
                    duration = end_time - start_time
                    records_per_sec = records_inserted / duration if duration > 0 else 0
                    
                    print(f"Batch insert completed: {records_inserted} records in {duration:.2f}s ({records_per_sec:.1f} records/sec)")
                    
                    # Insert file metadata
                    filename = os.path.basename(file_path)
                    parsing_stats_json = "{}"
                    self.db.insert_file_metadata(
                        filename=filename,
                        file_size=file_size,
                        records_imported=records_inserted,
                        parsing_stats=parsing_stats_json,
                    )
                    
                    return records_inserted
                    
                except Exception as e:
                    print(f"Error importing {os.path.basename(file_path)}: {e}")
                    return 0

            def _import_small_file(self, file_path):
                """Import small log file with professional progress"""
                try:
                    from progress_dialog import ProgressDialog

                    from progress_dialog import ProgressDialog

                    self.progress_dialog = ProgressDialog(self)
                    self.progress_dialog.setWindowTitle("Processing LINAC Log File")
                    self.progress_dialog.setModal(True)
                    self.progress_dialog.show()

                    # Ensure dialog stays on top and visible
                    self.progress_dialog.set_window_flags(
                        self.progress_dialog.windowFlags() | Qt.WindowStaysOnTopHint
                    )
                    self.progress_dialog.update_progress(10, "Reading file...")
                    QtWidgets.QApplication.processEvents()

                    from unified_parser import UnifiedParser

                    parser = UnifiedParser()

                    self.progress_dialog.update_progress(30, "Processing data...")
                    QtWidgets.QApplication.processEvents()

                    df = parser.parse_linac_file(file_path)

                    self.progress_dialog.update_progress(70, "Saving to database...")
                    QtWidgets.QApplication.processEvents()

                    records_inserted = self.db.insert_data_batch(df)

                    self.progress_dialog.update_progress(90, "Finalizing...")
                    QtWidgets.QApplication.processEvents()

                    filename = os.path.basename(file_path)
                    parsing_stats_json = "{}"

                    self.db.insert_file_metadata(
                        filename=filename,
                        file_size=os.path.getsize(file_path),
                        records_imported=records_inserted,
                        parsing_stats=parsing_stats_json,
                    )

                    self.progress_dialog.setValue(100)
                    self.progress_dialog.close()

                    try:
                        self.df = self.db.get_all_logs(chunk_size=10000)
                    except TypeError:
                        self.df = self.db.get_all_logs()

                    # Mark data as updated for cache invalidation
                    self._mark_data_updated()

                    # Force complete refresh of all UI components
                    self.load_dashboard()
                    self._initialize_trend_controls()
                    self.update_trend_combos()
                    self.update_data_table()
                    self.update_analysis_tab()

                    # Initialize default trend displays
                    QtCore.QTimer.singleShot(500, self._refresh_all_trends)

                    # Initialize MPC tab with new data
                    QtCore.QTimer.singleShot(300, self.refresh_latest_mpc)

                    # Show success message only once
                    if not hasattr(self, '_import_success_shown'):
                        self._import_success_shown = True
                        QtWidgets.QMessageBox.information(
                            self,
                            "Import Successful",
                            f"Successfully imported {records_inserted:,} records.\n\n"
                            f"Dashboard, trends, and analysis tabs have been updated.\n"
                            f"Total records now available: {len(self.df):,}",
                        )
                        # Reset flag after a delay
                        QtCore.QTimer.singleShot(2000, lambda: delattr(self, '_import_success_shown'))

                    import gc
                    del df
                    gc.collect()

                except Exception as e:
                    print(f"Error in import_small_file: {e}")
                    traceback.print_exc()
                    QtWidgets.QMessageBox.critical(
                        self, "Import Error", f"Error importing log file: {str(e)}"
                    )

            def _import_large_file(self, file_path, file_size):
                """Import large log file with enhanced progress phases"""
                try:
                    from progress_dialog import ProgressDialog

                    self.progress_dialog = ProgressDialog(self)
                    self.progress_dialog.setWindowTitle("Processing LINAC Log File")
                    self.progress_dialog.show()
                    self.progress_dialog.set_phase("uploading", 0)
                    QtWidgets.QApplication.processEvents()

                    # Start with uploading phase
                    self.progress_dialog.set_phase("uploading", 0)
                    QtWidgets.QApplication.processEvents()

                    from worker_thread import FileProcessingWorker

                    self.worker = FileProcessingWorker(file_path, file_size, self.db)
                    self.worker.chunk_size = 5000

                    # Simple progress handling
                    def handle_progress_update(percentage, status_message="", lines_processed=0, total_lines=0, bytes_processed=0, total_bytes=0):
                        # Convert to integer and update
                        progress_value = max(0, min(100, int(percentage)))
                        self.progress_dialog.update_progress(progress_value, status_message)
                        QtWidgets.QApplication.processEvents()

                    self.worker.progress_update.connect(handle_progress_update)
                    self.worker.status_update.connect(
                        lambda msg: self.progress_dialog.setLabelText(msg)
                    )
                    self.worker.finished.connect(self.on_file_processing_finished)
                    self.worker.error.connect(self.on_file_processing_error)

                    # Handle cancel button
                    self.progress_dialog.canceled.connect(self.worker.cancel_processing)

                    # Start processing
                    self.worker.start()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Processing Error",
                        f"Error initializing file processing: {str(e)}",
                    )
                    traceback.print_exc()

            def _process_sample_shortdata(self, file_path):
                """Process shortdata as sample data and populate DataFrame for analysis"""
                try:
                    import pandas as pd
                    print(f"📋 Processing shortdata as sample: {os.path.basename(file_path)}")

                    # Parse shortdata for trend analysis
                    from unified_parser import UnifiedParser

                    parser = UnifiedParser()
                    parsed_data = parser.parse_short_data_file(file_path)

                    if parsed_data and parsed_data.get('success'):
                        # Convert parsed data to DataFrame format for analysis
                        df_converted = parser.convert_short_data_to_dataframe(parsed_data)

                        if not df_converted.empty:
                            # Store DataFrame for analysis and trends
                            self.df = df_converted
                            print(f"✓ DataFrame populated with {len(df_converted)} records")

                            # Store in memory for trend controls
                            self.shortdata_parameters = parsed_data
                            self.shortdata_parser = parser

                            # Initialize trend controls with the parsed data
                            self._initialize_trend_controls()

                            # Update analysis tab to show the new data
                            self.update_analysis_tab()

                            # Refresh all UI components with the new data
                            self.load_dashboard()
                            self._initialize_trend_controls()
                            self.update_trend_combos()
                            self.update_data_table()
                            self.update_analysis_tab()

                            # Initialize default trend displays
                            QtCore.QTimer.singleShot(500, self._refresh_all_trends)

                            print(f"✓ Shortdata processed successfully for trend analysis and analysis tab")
                            QtWidgets.QMessageBox.information(
                                self,
                                "Sample Data Loaded",
                                f"Shortdata loaded successfully!\n\n"
                                f"Parameters available: {len(parsed_data.get('parameters', []))}\n"
                                f"Records for analysis: {len(df_converted)}\n"
                                f"Unique parameters: {len(df_converted['parameter_type'].unique()) if not df_converted.empty else 0}\n\n"
                                f"Data is now available in:\n"
                                f"• Dashboard tab (system status)\n"
                                f"• Trend tab graphs\n"
                                f"• Data Table tab\n"
                                f"• Analysis tab statistics"
                            )
                        else:
                            print("⚠️ DataFrame conversion failed - no data available")
                            QtWidgets.QMessageBox.warning(
                                self,
                                "Import Warning",
                                "Shortdata file was processed but no data could be converted for analysis.\n"
                                "Please check the file format."
                            )
                    else:
                        print("⚠️ No data extracted from shortdata file")
                        QtWidgets.QMessageBox.warning(
                            self,
                            "Import Error",
                            "No valid data could be extracted from the shortdata file.\n"
                            "Please check the file format."
                        )

                except Exception as e:
                    print(f"Error processing shortdata: {e}")
                    traceback.print_exc()
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Import Error",
                        f"Error processing shortdata file: {str(e)}"
                    )

            def _import_small_file_filtered(self, file_path):
                """Import small log file with TB/HALfault filtering"""
                try:
                    from progress_dialog import ProgressDialog

                    self.progress_dialog = ProgressDialog(self)
                    self.progress_dialog.setWindowTitle("Processing Filtered Log File")
                    self.progress_dialog.show()
                    self.progress_dialog.set_phase("uploading", 10)
                    QtWidgets.QApplication.processEvents()

                    # Read file and filter for TB/HALfault entries only
                    filtered_lines = []
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line_lower = line.lower()
                            if 'tb' in line_lower or 'halfault' in line_lower or 'hal fault' in line_lower:
                                filtered_lines.append(line)

                    progress_dialog.setValue(30)
                    QtWidgets.QApplication.processEvents()

                    print(f"Filtered {len(filtered_lines)} relevant lines from file")

                    if filtered_lines:
                        # Create temporary filtered file
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                            temp_file.writelines(filtered_lines)
                            temp_path = temp_file.name

                        progress_dialog.setValue(50)
                        QtWidgets.QApplication.processEvents()

                        # Parse the filtered data
                        from unified_parser import UnifiedParser
                        parser = UnifiedParser()
                        df = parser.parse_linac_file(temp_path)

                        progress_dialog.setValue(70)
                        QtWidgets.QApplication.processEvents()

                        # Insert only the filtered data
                        records_inserted = self.db.insert_data_batch(df)

                        progress_dialog.setValue(90)
                        QtWidgets.QApplication.processEvents()

                        # Clean up temporary file
                        os.unlink(temp_path)

                        # Store metadata
                        filename = os.path.basename(file_path) + " (TB/HALfault filtered)"
                        parsing_stats_json = f'{{"filtered_lines": {len(filtered_lines)}, "total_records": {records_inserted}}}'

                        self.db.insert_file_metadata(
                            filename=filename,
                            file_size=len(''.join(filtered_lines)),
                            records_imported=records_inserted,
                            parsing_stats=parsing_stats_json,
                        )

                        progress_dialog.setValue(100)
                        progress_dialog.close()

                        # Refresh data
                        try:
                            self.df = self.db.get_all_logs(chunk_size=10000)
                        except TypeError:
                            self.df = self.db.get_all_logs()
                        self.load_dashboard()

                        QtWidgets.QMessageBox.information(
                            self,
                            "Import Successful",
                            f"Successfully imported {records_inserted:,} filtered records (TB/HALfault only).",
                        )
                    else:
                        progress_dialog.close()
                        QtWidgets.QMessageBox.information(
                            self,
                            "No Relevant Data",
                            "No TB or HALfault entries found in the selected file.",
                        )

                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self, "Processing Error", f"An error occurred: {str(e)}"
                    )
                    traceback.print_exc()

            def _import_large_file_filtered(self, file_path, file_size):
                """Import large log file with TB/HALfault filtering"""
                try:
                    from progress_dialog import ProgressDialog

                    self.progress_dialog = ProgressDialog(self)
                    self.progress_dialog.setWindowTitle("Processing Large Filtered Log File")
                    self.progress_dialog.show()
                    self.progress_dialog.set_phase("uploading", 0)
                    QtWidgets.QApplication.processEvents()

                    # Process file in chunks for large files
                    chunk_size = 1024 * 1024  # 1MB chunks
                    filtered_lines = []
                    processed_bytes = 0

                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break

                            processed_bytes += len(chunk.encode('utf-8'))
                            progress = min(50, int((processed_bytes / file_size) * 50))
                            self.progress_dialog.setValue(progress)
                            QtWidgets.QApplication.processEvents()

                            if self.progress_dialog.wasCanceled():
                                return

                            # Filter lines in chunk
                            lines = chunk.split('\n')
                            for line in lines:
                                line_lower = line.lower()
                                if 'tb' in line_lower or 'halfault' in line_lower or 'hal fault' in line_lower:
                                    filtered_lines.append(line + '\n')

                    print(f"Filtered {len(filtered_lines)} relevant lines from large file")
                    self.progress_dialog.setValue(60)
                    QtWidgets.QApplication.processEvents()

                    if filtered_lines:
                        # Process filtered data
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                            temp_file.writelines(filtered_lines)
                            temp_path = temp_file.name

                        self.progress_dialog.setValue(70)
                        QtWidgets.QApplication.processEvents()

                        # Use existing large file processing for filtered data
                        from unified_parser import UnifiedParser
                        parser = UnifiedParser()
                        df = parser.parse_linac_file(temp_path)

                        self.progress_dialog.setValue(85)
                        QtWidgets.QApplication.processEvents()

                        records_inserted = self.db.insert_data_batch(df)

                        # Clean up
                        os.unlink(temp_path)

                        # Store metadata
                        filename = os.path.basename(file_path) + " (TB/HALfault filtered)"
                        parsing_stats_json = f'{{"filtered_lines": {len(filtered_lines)}, "total_records": {records_inserted}}}'

                        self.db.insert_file_metadata(
                            filename=filename,
                            file_size=len(''.join(filtered_lines)),
                            records_imported=records_inserted,
                            parsing_stats=parsing_stats_json,
                        )

                        self.progress_dialog.setValue(100)
                        self.progress_dialog.close()

                        # Refresh data
                        try:
                            self.df = self.db.get_all_logs(chunk_size=10000)
                        except TypeError:
                            self.df = self.db.get_all_logs()
                        self.load_dashboard()

                        QtWidgets.QMessageBox.information(
                            self,
                            "Import Successful",
                            f"Successfully imported {records_inserted:,} filtered records (TB/HALfault only).",
                        )
                    else:
                        self.progress_dialog.close()
                        QtWidgets.QMessageBox.information(
                            self,
                            "No Relevant Data",
                            "No TB or HALfault entries found in the selected file.",
                        )

                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self, "Processing Error", f"An error occurred: {str(e)}"
                    )
                    traceback.print_exc()

            def clear_database(self):
                """Clear database with professional confirmation"""
                try:
                    reply = QtWidgets.QMessageBox.question(
                        self,
                        "Confirm Clear Database",
                        "Are you sure you want to clear all data?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No,
                    )

                    if reply == QtWidgets.QMessageBox.Yes:
                        progress_dialog = QtWidgets.QProgressDialog(
                            "Clearing database...", "", 0, 100, self
                        )
                        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
                        progress_dialog.setCancelButton(None)
                        progress_dialog.setValue(10)
                        progress_dialog.show()
                        QtWidgets.QApplication.processEvents()

                        self.db.clear_all()

                        progress_dialog.setValue(50)
                        QtWidgets.QApplication.processEvents()

                        import pandas as pd

                        self.df = pd.DataFrame()

                        progress_dialog.setValue(70)
                        QtWidgets.QApplication.processEvents()

                        self.load_dashboard()

                        progress_dialog.setValue(100)
                        progress_dialog.close()

                        QtWidgets.QMessageBox.information(
                            self, "Database", "Data cleared successfully."
                        )

                        import gc

                        gc.collect()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self, "Database Error", f"An error occurred: {str(e)}"
                    )
                    traceback.print_exc()

            def on_file_processing_finished(self, records_count, parsing_stats):
                """Handle completion of file processing"""
                try:
                    # Mark progress dialog as complete and close it
                    if hasattr(self, "progress_dialog") and self.progress_dialog:
                        self.progress_dialog.mark_complete()
                        self.progress_dialog.close()
                        self.progress_dialog = None

                    print(f"🎯 File processing finished: {records_count} records inserted")
                    print(f"📊 Parsing stats: {parsing_stats}")

                    if records_count > 0:
                        # Get fresh data from database
                        print("🔄 Refreshing data from database...")
                        try:
                            self.df = self.db.get_all_logs(chunk_size=10000)
                            print(f"✓ Database loaded: {len(self.df)} total records")

                            # Check what data we actually have
                            if not self.df.empty:
                                print(f"📋 Data preview:")
                                print(f"  Columns: {list(self.df.columns)}")
                                print(f"  Shape: {self.df.shape}")
                                print(f"  Date range: {self.df['datetime'].min()} to {self.df['datetime'].max()}")
                                print(f"  Unique parameters: {self.df['param'].nunique() if 'param' in self.df.columns else 'N/A'}")
                                print(f"  Sample parameters: {list(self.df['param'].unique()[:5]) if 'param' in self.df.columns else 'N/A'}")
                            else:
                                print("⚠️ DataFrame is empty after database load")

                        except TypeError:
                            self.df = self.db.get_all_logs()
                            print(f"✓ Database loaded (no chunking): {len(self.df)} total records")

                        # Force complete refresh of all UI components
                        print("🔄 Refreshing UI components...")
                        self.load_dashboard()
                        self._initialize_trend_controls()
                        self.update_trend_combos()
                        self.update_data_table()
                        self.update_analysis_tab()

                        # Initialize default trend displays
                        QtCore.QTimer.singleShot(500, self._refresh_all_trends)

                        # Initialize MPC tab with new data
                        QtCore.QTimer.singleShot(300, self.refresh_latest_mpc)

                        QtWidgets.QMessageBox.information(
                            self,
                            "Import Successful",
                            f"Successfully imported {records_count:,} records.\n\n"
                            f"Dashboard, trends, and analysis tabs have been updated.\n"
                            f"Total records available: {len(self.df):,}",
                        )

                        print(f"File processing completed: {parsing_stats}")
                        print(f"✓ UI refreshed with {len(self.df)} total records")
                    else:
                        print("⚠️ No records were inserted into database")
                        QtWidgets.QMessageBox.warning(
                            self,
                            "Import Warning",
                            "No valid log entries found in the selected file.\n\n"
                            "Please check that the file contains valid LINAC log data with the expected format:\n"
                            "- Parameters with count=N, max=N.N, min=N.N, avg=N.N format\n"
                            "- Valid date/time stamps\n"
                            "- Serial number information",
                        )

                    if hasattr(self, "worker"):
                        self.worker.deleteLater()
                        self.worker = None
                except Exception as e:
                    print(f"Error handling file processing completion: {e}")
                    traceback.print_exc()

            def on_file_processing_error(self, error_message):
                """Handle errors during file processing"""
                try:
                    if hasattr(self, "progress_dialog") and self.progress_dialog:
                        self.progress_dialog.close()

                    QtWidgets.QMessageBox.critical(
                        self, "Processing Error", f"An error occurred: {error_message}"
                    )

                    if hasattr(self, "worker"):
                        self.worker.deleteLater()
                        self.worker = None
                except Exception as e:
                    print(f"Error handling file processing error: {e}")
                    traceback.print_exc()

            def closeEvent(self, event):
                """Clean up resources when closing application"""
                try:
                    if hasattr(self, "memory_timer"):
                        self.memory_timer.stop()

                    if hasattr(self, "db"):
                        try:
                            self.db.vacuum_database()
                        except:
                            pass

                    import gc

                    gc.collect()

                    print("Window close event: cleaning up resources")
                    event.accept()
                except Exception as e:
                    print(f"Error during application close: {e}")
                    event.accept()

        self.window = HALogMaterialApp()
        self.update_splash_progress(80, "Finalizing interface...")
        self.load_times["window_creation"] = time.time() - start_window
        return self.window

    def run(self):
        """Run the HALog application"""
        try:
            # Create and show splash screen
            self.update_splash_progress(10, "Initializing environment...")
            setup_environment()
            self.update_splash_progress(25, "Loading GUI framework...")
            QtWidgets = lazy_import("PyQt5.QtWidgets")
            QtCore = lazy_import("PyQt5.QtCore")
            QtGui = lazy_import("PyQt5.QtGui")

            # Create application with professional settings
            app = QtWidgets.QApplication(sys.argv)
            app.setApplicationName("Gobioeng HALog")
            app.setApplicationVersion(APP_VERSION)
            app.setOrganizationName("gobioeng.com")

            # Set professional font
            try:
                font = QtGui.QFont("Segoe UI", 9)  # Slightly smaller for better data focus
                app.setFont(font)
            except:
                pass

            # Create HALog app instance and splash
            halog_app = HALogApp()
            self.update_splash_progress(40, "Creating splash screen...")
            splash = halog_app.create_splash()
            self.load_times["splash_creation"] = time.time() - startup_begin

            # Create main window
            self.update_splash_progress(60, "Loading main interface...")
            window = halog_app.create_main_window()
            self.load_times["window_creation"] = time.time() - startup_begin

            # Finalize startup
            self.update_splash_progress(90, "Finalizing HALog...")

            # Schedule window display with smooth transition
            def finish_startup():
                if splash:
                    splash.close()
                window.show()
                window.raise_()
                window.activateWindow()

            QtCore.QTimer.singleShot(600, finish_startup)  # Faster for better UX

            # Log startup timing
            total_time = time.time() - startup_begin
            print(f"🚀 Gobioeng HALog startup: {total_time:.3f}s")
            print(f"   Developed by gobioeng.com")
            print(f"   Professional LINAC Water System Monitor Complete")

            # Run application
            sys.exit(app.exec_())

        except Exception as e:
            print(f"Error in startup: {e}")
            traceback.print_exc()

            # Try to show error dialog
            try:
                from PyQt5.QtWidgets import QApplication, QMessageBox

                app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
                QMessageBox.critical(
                    None,
                    "Startup Error",
                    f"Error starting Gobioeng HALog: {str(e)}\n\nDeveloped by gobioeng.com\n\n{traceback.format_exc()}",
                )
            except:
                pass

            sys.exit(1)


def main():
    """
    Main entry point for HALog application
    Developer: gobioeng.com - Professional LINAC Log Analysis System
    """
    try:
        # Setup optimized environment first
        setup_environment()

        # Create Qt Application with enhanced configuration
        QtWidgets = lazy_import("PyQt5.QtWidgets")
        QtCore = lazy_import("PyQt5.QtCore")
        QtGui = lazy_import("PyQt5.QtGui")

        # Professional Qt Application Settings - Updated for better performance
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("HALog")
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName("gobioeng.com")
        app.setOrganizationDomain("gobioeng.com")

        # Set application icon
        try:
            from resource_helper import get_app_icon

            app_icon = get_app_icon()
            if app_icon:
                app.setWindowIcon(app_icon)
        except Exception as e:
            print(f"Warning: Could not set application icon: {e}")

        # Professional styling with optimized processing
        app.setStyleSheet(
            """
            QApplication {
                font-family: 'Segoe UI', 'Roboto', 'Google Sans', Arial, sans-serif;
                font-size: 11px;
                font-weight: 400;
            }
        """
        )

        print(f"🔥 HALog Starting...")
        print(f"📱 Application: HALog {APP_VERSION}")
        print(f"🏢 Developer: gobioeng.com")

        # Initialize and show HALog application
        halog_app = HALogApp()
        halog_app.run()

        # Application cleanup
        startup_time = time.time() - startup_begin
        print(f"🏁 HALog application closed (Startup time: {startup_time:.2f}s)")

        return app.exec_()

    except Exception as e:
        print(f"❌ Critical error in main: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    print("🔥 HALog Starting...")

    try:
        setup_environment()

        QtWidgets = lazy_import("PyQt5.QtWidgets")

        # Create QApplication with improved error handling
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("HALog")
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName("gobioeng.com")

        # Initialize and run application
        halog_app = HALogApp()
        exit_code = halog_app.run()
        sys.exit(exit_code)

    except Exception as e:
        print(f"❌ Critical error starting HALog: {e}")
        print("This application requires a desktop environment with Qt support.")
        print("For Replit deployment, consider creating a web-based version.")
        sys.exit(1)