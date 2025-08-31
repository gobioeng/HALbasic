"""
HALog 0.0.1 - Professional LINAC Log Analysis
Optimized for fast startup and efficient processing
Company: gobioeng.com
"""

import sys
import os
import time
from pathlib import Path

APP_VERSION = "0.0.1"
startup_begin = time.time()

def setup_environment():
    """Minimal environment setup"""
    os.environ.update({
        "PYTHONOPTIMIZE": "2",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NUMEXPR_MAX_THREADS": "4"
    })

    app_dir = Path(__file__).parent.absolute()
    os.chdir(app_dir)
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

class HALogApp:
    """Optimized HALog Application"""

    def __init__(self):
        self.window = None

    def create_window(self):
        """Create main window with minimal splash"""
        from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem, QProgressDialog
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont, QPixmap
        from main_window import Ui_MainWindow
        from database import DatabaseManager
        from unified_parser import UnifiedParser
        import pandas as pd
        import traceback

        class HALogMainWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.ui = Ui_MainWindow()
                self.ui.setupUi(self)

                # Initialize core components
                self.db = DatabaseManager("halog_water.db")
                self.parser = UnifiedParser()
                self.df = pd.DataFrame()

                # Load fault codes
                self._load_fault_codes()

                # Setup UI
                self.setWindowTitle(f"HALog {APP_VERSION} - LINAC Monitor")
                self._connect_actions()
                self._apply_styles()
                self.load_dashboard()

            def _load_fault_codes(self):
                """Load fault code databases"""
                try:
                    hal_path = os.path.join('data', 'HALfault.txt')
                    tb_path = os.path.join('data', 'TBFault.txt')

                    if os.path.exists(hal_path):
                        self.parser.load_fault_codes_from_uploaded_file(hal_path)
                    if os.path.exists(tb_path):
                        self.parser.load_fault_codes_from_uploaded_file(tb_path)

                    self._update_fault_stats()
                except Exception as e:
                    print(f"Warning: Could not load fault codes: {e}")

            def _update_fault_stats(self):
                """Update fault code statistics"""
                try:
                    stats = self.parser.get_fault_code_statistics()
                    if hasattr(self.ui, 'lblTotalCodes'):
                        self.ui.lblTotalCodes.setText(f"Total Codes: {stats['total_codes']}")
                except Exception:
                    pass

            def _connect_actions(self):
                """Connect UI actions"""
                try:
                    # Menu actions
                    if hasattr(self.ui, 'actionOpen_Log_File'):
                        self.ui.actionOpen_Log_File.triggered.connect(self.import_file)
                    if hasattr(self.ui, 'actionExit'):
                        self.ui.actionExit.triggered.connect(self.close)
                    if hasattr(self.ui, 'actionRefresh'):
                        self.ui.actionRefresh.triggered.connect(self.load_dashboard)
                    if hasattr(self.ui, 'actionAbout'):
                        self.ui.actionAbout.triggered.connect(self.show_about)
                    if hasattr(self.ui, 'actionClearAllData'):
                        self.ui.actionClearAllData.triggered.connect(self.clear_data)

                    # Button actions
                    if hasattr(self.ui, 'btnClearDB'):
                        self.ui.btnClearDB.clicked.connect(self.clear_data)
                    if hasattr(self.ui, 'btnRefreshData'):
                        self.ui.btnRefreshData.clicked.connect(self.load_dashboard)

                    # Fault code search
                    if hasattr(self.ui, 'btnSearchCode'):
                        self.ui.btnSearchCode.clicked.connect(self.search_fault_code)
                    if hasattr(self.ui, 'btnSearchDescription'):
                        self.ui.btnSearchDescription.clicked.connect(self.search_description)

                    # Tab changes
                    if hasattr(self.ui, 'tabWidget'):
                        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

                except Exception as e:
                    print(f"Error connecting actions: {e}")

            def _apply_styles(self):
                """Apply minimal professional styles"""
                self.setStyleSheet("""
                    QMainWindow {
                        background-color: #f5f5f5;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 12px;
                    }
                    QTabWidget::pane {
                        border: 1px solid #ccc;
                        background: white;
                    }
                    QTabBar::tab {
                        padding: 8px 16px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected {
                        background: white;
                        border-bottom: 2px solid #0078d4;
                    }
                    QPushButton {
                        background: #0078d4;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background: #106ebe;
                    }
                    QGroupBox {
                        font-weight: bold;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        margin-top: 8px;
                        padding-top: 8px;
                    }
                """)

            def import_file(self):
                """Import log file with simple progress"""
                try:
                    from PyQt5.QtWidgets import QProgressDialog
                    from PyQt5.QtCore import QThread, pyqtSignal

                    file_path, _ = QFileDialog.getOpenFileName(
                        self, "Select Log File", "", "Log Files (*.log *.txt);;All Files (*.*)"
                    )

                    if not file_path:
                        return

                    # Simple progress dialog
                    progress = QProgressDialog("Processing file...", "Cancel", 0, 100, self)
                    progress.setWindowModality(Qt.WindowModal)
                    progress.show()

                    # Process file
                    progress.setValue(25)
                    QApplication.processEvents()

                    df = self.parser.parse_linac_file(file_path)

                    progress.setValue(75)
                    QApplication.processEvents()

                    if not df.empty:
                        records = self.db.insert_data_batch(df)
                        progress.setValue(100)
                        progress.close()

                        # Refresh UI
                        self.load_dashboard()

                        QMessageBox.information(
                            self, "Import Complete",
                            f"Successfully imported {records:,} records!"
                        )
                    else:
                        progress.close()
                        QMessageBox.warning(self, "Import Failed", "No data found in file.")

                except Exception as e:
                    if 'progress' in locals():
                        progress.close()
                    QMessageBox.critical(self, "Import Error", f"Error: {str(e)}")

            def load_dashboard(self):
                """Load dashboard data"""
                try:
                    self.df = self.db.get_all_logs()

                    if not self.df.empty:
                        latest = self.df.sort_values("datetime").iloc[-1]
                        self.ui.lblSerial.setText(f"Serial: {latest.get('serial', 'Unknown')}")
                        self.ui.lblDate.setText(f"Date: {latest['datetime'].date()}")
                        self.ui.lblRecordCount.setText(f"Records: {len(self.df):,}")

                        if 'param' in self.df.columns:
                            unique_params = self.df['param'].nunique()
                            self.ui.lblParameterCount.setText(f"Parameters: {unique_params}")
                    else:
                        self.ui.lblSerial.setText("Serial: No data")
                        self.ui.lblDate.setText("Date: No data")
                        self.ui.lblRecordCount.setText("Records: 0")
                        self.ui.lblParameterCount.setText("Parameters: 0")

                    self.update_data_table()

                    # Refresh trends if on trends tab
                    if hasattr(self.ui, 'tabWidget') and self.ui.tabWidget.currentIndex() == 1:
                        self._setup_trend_connections()

                except Exception as e:
                    print(f"Error loading dashboard: {e}")

            def update_data_table(self):
                """Update data table with basic pagination"""
                try:
                    if not hasattr(self, 'df') or self.df.empty:
                        self.ui.tableData.setRowCount(0)
                        return

                    # Show first 500 records for performance
                    display_df = self.df.head(500)

                    self.ui.tableData.setRowCount(len(display_df))
                    self.ui.tableData.setColumnCount(6)
                    self.ui.tableData.setHorizontalHeaderLabels([
                        "DateTime", "Serial", "Parameter", "Average", "Min", "Max"
                    ])

                    for i, (_, row) in enumerate(display_df.iterrows()):
                        items = [
                            str(row.get('datetime', '')),
                            str(row.get('serial', '')),
                            str(row.get('param', '')),
                            f"{row.get('avg', ''):.3f}" if pd.notna(row.get('avg', '')) else '',
                            f"{row.get('min', ''):.3f}" if pd.notna(row.get('min', '')) else '',
                            f"{row.get('max', ''):.3f}" if pd.notna(row.get('max', '')) else ''
                        ]

                        for j, item in enumerate(items):
                            self.ui.tableData.setItem(i, j, QTableWidgetItem(item))

                    # Auto-resize columns
                    self.ui.tableData.resizeColumnsToContents()

                except Exception as e:
                    print(f"Error updating table: {e}")

            def search_fault_code(self):
                """Search for fault code"""
                try:
                    if not hasattr(self.ui, 'txtFaultCode'):
                        return

                    code = self.ui.txtFaultCode.text().strip()
                    if not code:
                        return

                    result = self.parser.search_fault_code(code)

                    if result and result.get('found'):
                        html = f"""
                        <div style='background: #d4edda; padding: 12px; border-radius: 4px;'>
                            <h3 style='color: #155724; margin: 0;'>✅ Code Found</h3>
                            <p><b>Code:</b> {code}</p>
                            <p><b>Description:</b> {result['description']}</p>
                            <p><b>Source:</b> {result['source']}</p>
                        </div>
                        """
                    else:
                        html = f"""
                        <div style='background: #f8d7da; padding: 12px; border-radius: 4px;'>
                            <h3 style='color: #721c24; margin: 0;'>❌ Code Not Found</h3>
                            <p>Code <b>{code}</b> not found in database.</p>
                        </div>
                        """

                    self.ui.txtFaultResult.setHtml(html)

                except Exception as e:
                    print(f"Error searching fault code: {e}")

            def search_description(self):
                """Search fault codes by description"""
                try:
                    if not hasattr(self.ui, 'txtSearchDescription'):
                        return

                    term = self.ui.txtSearchDescription.text().strip()
                    if not term:
                        return

                    results = self.parser.search_description(term)

                    if results:
                        html = f"<h3>Found {len(results)} results:</h3>"
                        for code, data in results[:5]:  # Show first 5
                            html += f"""
                            <div style='border: 1px solid #ccc; padding: 8px; margin: 4px 0;'>
                                <b>Code:</b> {code}<br>
                                <b>Description:</b> {data['description']}
                            </div>
                            """
                    else:
                        html = f"<p>No results found for '{term}'</p>"

                    self.ui.txtFaultResult.setHtml(html)

                except Exception as e:
                    print(f"Error searching description: {e}")

            def clear_data(self):
                """Clear all data"""
                try:
                    from PyQt5.QtWidgets import QMessageBox

                    reply = QMessageBox.question(
                        self, "Clear Data", "Clear all imported data?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        self.db.clear_all()
                        self.df = pd.DataFrame()
                        self.load_dashboard()
                        QMessageBox.information(self, "Success", "Data cleared successfully.")

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error clearing data: {e}")

            def show_about(self):
                """Show about dialog"""
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.about(
                    self, "HALog",
                    f"HALog {APP_VERSION}\nProfessional LINAC Monitor\nDeveloped by gobioeng.com"
                )

            def on_tab_changed(self, index):
                """Handle tab changes"""
                try:
                    if index == 1:  # Data table
                        self.update_data_table()
                        self._setup_trend_connections()
                except Exception:
                    pass

            def _setup_trend_connections(self):
                """Setup connections for trend tab widgets"""
                try:
                    # Limit data size for performance
                    if len(self.df) > 1000:
                        print(f"Large dataset detected ({len(self.df)} records). Using sample for trends.")
                        # Use latest 1000 records for better performance
                        self.df_trends = self.df.tail(1000).copy()
                    else:
                        self.df_trends = self.df.copy()
                    
                    # Populate dropdowns with available parameters
                    self._populate_parameter_dropdowns()
                    
                    # Connect Update Graphs button (this exists in the UI)
                    if hasattr(self.ui, 'btnUpdateGraphs'):
                        self.ui.btnUpdateGraphs.clicked.connect(self._refresh_water_graphs)
                    
                    # Connect dropdown changes
                    if hasattr(self.ui, 'comboWaterTopGraph'):
                        self.ui.comboWaterTopGraph.currentIndexChanged.connect(self._refresh_water_graphs)
                    if hasattr(self.ui, 'comboWaterBottomGraph'):
                        self.ui.comboWaterBottomGraph.currentIndexChanged.connect(self._refresh_water_graphs)

                    # Setup analysis tab
                    self._setup_analysis_tab()

                    # Don't plot initial graphs automatically to prevent freezing
                    print("Trend connections setup complete. Select parameters to view graphs.")

                except Exception as e:
                    print(f"Error setting up trend connections: {e}")

            def _populate_parameter_dropdowns(self):
                """Populate dropdown menus with available parameters"""
                try:
                    # Use limited dataset for dropdown population
                    df_to_use = getattr(self, 'df_trends', self.df)
                    
                    if df_to_use.empty:
                        return

                    # Get unique parameters from data
                    parameters = sorted(df_to_use['param'].unique()) if 'param' in df_to_use.columns else []
                    
                    # Filter by categories
                    water_params = [p for p in parameters if any(word in p.lower() for word in ['flow', 'pressure', 'pump', 'water', 'mag', 'target', 'chiller', 'cooling'])]
                    voltage_params = [p for p in parameters if any(word in p.lower() for word in ['voltage', '24v', '48v', '5v', 'mlc', 'col'])]
                    temp_params = [p for p in parameters if any(word in p.lower() for word in ['temp', 'temperature'])]
                    humidity_params = [p for p in parameters if any(word in p.lower() for word in ['humidity', 'humid'])]
                    fan_params = [p for p in parameters if any(word in p.lower() for word in ['fan', 'speed'])]

                    # Populate dropdowns
                    if hasattr(self.ui, 'comboWaterTopGraph'):
                        self.ui.comboWaterTopGraph.clear()
                        self.ui.comboWaterTopGraph.addItems([''] + water_params)
                        if water_params:
                            self.ui.comboWaterTopGraph.setCurrentText(water_params[0])

                    if hasattr(self.ui, 'comboWaterBottomGraph'):
                        self.ui.comboWaterBottomGraph.clear()
                        self.ui.comboWaterBottomGraph.addItems([''] + water_params)
                        if len(water_params) > 1:
                            self.ui.comboWaterBottomGraph.setCurrentText(water_params[1])

                except Exception as e:
                    print(f"Error populating dropdowns: {e}")

            def _setup_analysis_tab(self):
                """Setup analysis tab functionality"""
                try:
                    # Connect refresh analysis button
                    if hasattr(self.ui, 'btnRefreshAnalysis'):
                        self.ui.btnRefreshAnalysis.clicked.connect(self._refresh_analysis)
                    
                    # Initial analysis
                    self._refresh_analysis()

                except Exception as e:
                    print(f"Error setting up analysis: {e}")

            def _refresh_analysis(self):
                """Refresh analysis results"""
                try:
                    if self.df.empty:
                        return

                    from analyzer_data import DataAnalyzer
                    analyzer = DataAnalyzer()

                    # Calculate comprehensive statistics
                    stats_df = analyzer.calculate_comprehensive_statistics(self.df)
                    
                    # Update analysis table
                    if hasattr(self.ui, 'tableAnalysis') and not stats_df.empty:
                        self.ui.tableAnalysis.setRowCount(len(stats_df))
                        self.ui.tableAnalysis.setColumnCount(8)
                        self.ui.tableAnalysis.setHorizontalHeaderLabels([
                            "Parameter", "Group", "Statistic", "Data Points", 
                            "Time Span (hrs)", "Slope", "Direction", "Strength"
                        ])

                        for i, (_, row) in enumerate(stats_df.iterrows()):
                            items = [
                                str(row.get('parameter', '')),
                                str(row.get('group', '')),
                                str(row.get('statistic_type', '')),
                                str(row.get('count', '')),
                                str(row.get('time_span_hours', '')),
                                str(row.get('trend_slope', '')),
                                str(row.get('trend_direction', '')),
                                str(row.get('trend_strength', ''))
                            ]

                            for j, item in enumerate(items):
                                self.ui.tableAnalysis.setItem(i, j, QTableWidgetItem(item))

                except Exception as e:
                    print(f"Error refreshing analysis: {e}")

            def _refresh_current_tab_graphs(self):
                """Refresh graphs for the currently active tab"""
                try:
                    if hasattr(self.ui, 'trendSubTabs'):
                        current_index = self.ui.trendSubTabs.currentIndex()
                        if current_index == 0:  # Water System
                            self._refresh_water_graphs()
                        elif current_index == 1:  # Voltages
                            self._refresh_voltage_graphs()
                        elif current_index == 2:  # Temperatures
                            self._refresh_temp_graphs()
                        elif current_index == 3:  # Humidity
                            self._refresh_humidity_graphs()
                        elif current_index == 4:  # Fan Speeds
                            self._refresh_fan_graphs()
                except Exception as e:
                    print(f"Error refreshing current tab graphs: {e}")

            def _refresh_water_graphs(self):
                """Refresh water system graphs"""
                try:
                    # Use limited dataset for plotting
                    df_to_use = getattr(self, 'df_trends', self.df)
                    
                    if df_to_use.empty:
                        print("No data available for plotting")
                        return

                    top_param = self.ui.comboWaterTopGraph.currentText()
                    bottom_param = self.ui.comboWaterBottomGraph.currentText()
                    
                    # Validate parameters
                    if not top_param or top_param == "":
                        print("No top parameter selected")
                        return
                        
                    print(f"Plotting water graphs: Top={top_param}, Bottom={bottom_param}")

                    self._plot_parameter_graphs(top_param, bottom_param, 
                                               self.ui.waterGraphTop, self.ui.waterGraphBottom, df_to_use)
                except Exception as e:
                    print(f"Error refreshing water graphs: {e}")
                    import traceback
                    traceback.print_exc()

            def _refresh_voltage_graphs(self):
                """Refresh voltage graphs"""
                try:
                    df_to_use = getattr(self, 'df_trends', self.df)
                    if df_to_use.empty:
                        return

                    top_param = self.ui.comboVoltageTopGraph.currentText()
                    bottom_param = self.ui.comboVoltageBottomGraph.currentText()

                    self._plot_parameter_graphs(top_param, bottom_param,
                                               self.ui.voltageGraphTop, self.ui.voltageGraphBottom, df_to_use)
                except Exception as e:
                    print(f"Error refreshing voltage graphs: {e}")

            def _refresh_temp_graphs(self):
                """Refresh temperature graphs"""
                try:
                    df_to_use = getattr(self, 'df_trends', self.df)
                    if df_to_use.empty:
                        return

                    top_param = self.ui.comboTempTopGraph.currentText()
                    bottom_param = self.ui.comboTempBottomGraph.currentText()

                    self._plot_parameter_graphs(top_param, bottom_param,
                                               self.ui.tempGraphTop, self.ui.tempGraphBottom, df_to_use)
                except Exception as e:
                    print(f"Error refreshing temperature graphs: {e}")

            def _refresh_humidity_graphs(self):
                """Refresh humidity graphs"""
                try:
                    df_to_use = getattr(self, 'df_trends', self.df)
                    if df_to_use.empty:
                        return

                    top_param = self.ui.comboHumidityTopGraph.currentText()
                    bottom_param = self.ui.comboHumidityBottomGraph.currentText()

                    self._plot_parameter_graphs(top_param, bottom_param,
                                               self.ui.humidityGraphTop, self.ui.humidityGraphBottom, df_to_use)
                except Exception as e:
                    print(f"Error refreshing humidity graphs: {e}")

            def _refresh_fan_graphs(self):
                """Refresh fan speed graphs"""
                try:
                    df_to_use = getattr(self, 'df_trends', self.df)
                    if df_to_use.empty:
                        return

                    top_param = self.ui.comboFanTopGraph.currentText()
                    bottom_param = self.ui.comboFanBottomGraph.currentText()

                    self._plot_parameter_graphs(top_param, bottom_param,
                                               self.ui.fanGraphTop, self.ui.fanGraphBottom, df_to_use)
                except Exception as e:
                    print(f"Error refreshing fan graphs: {e}")

            def _plot_parameter_graphs(self, top_param, bottom_param, top_widget, bottom_widget, data_source=None):
                """Plot graphs for specified parameters"""
                try:
                    from utils_plot import PlotUtils
                    from PyQt5.QtWidgets import QApplication

                    # Use provided data source or default to main df
                    df_to_use = data_source if data_source is not None else self.df
                    
                    # Process events to keep UI responsive
                    QApplication.processEvents()

                    # Filter data for parameters with size limits
                    top_data = pd.DataFrame()
                    bottom_data = pd.DataFrame()
                    
                    if top_param and top_param != "":
                        filtered_top = df_to_use[df_to_use['param'] == top_param].copy()
                        # Limit to last 500 points for performance
                        if len(filtered_top) > 500:
                            filtered_top = filtered_top.tail(500)
                        top_data = filtered_top
                    
                    if bottom_param and bottom_param != "":
                        filtered_bottom = df_to_use[df_to_use['param'] == bottom_param].copy()
                        # Limit to last 500 points for performance
                        if len(filtered_bottom) > 500:
                            filtered_bottom = filtered_bottom.tail(500)
                        bottom_data = filtered_bottom

                    print(f"Plotting: Top={top_param} ({len(top_data)} points), Bottom={bottom_param} ({len(bottom_data)} points)")

                    # Process events before clearing
                    QApplication.processEvents()

                    # Properly clear existing layouts and widgets
                    self._clear_widget_layout(top_widget)
                    self._clear_widget_layout(bottom_widget)
                    
                    # Process events after clearing
                    QApplication.processEvents()

                    # Create dual graph plot only if we have data
                    if not top_data.empty or not bottom_data.empty:
                        canvas, _ = PlotUtils.create_dual_graph_plot(
                            top_widget,
                            top_data if not top_data.empty else None,
                            bottom_data if not bottom_data.empty else None,
                            title_top=f"{top_param}" if top_param else "No Data",
                            title_bottom=f"{bottom_param}" if bottom_param else "No Data"
                        )
                        print("Graphs plotted successfully")
                    else:
                        print("No data to plot")

                except Exception as e:
                    print(f"Error plotting parameter graphs: {e}")
                    import traceback
                    traceback.print_exc()

            def _clear_widget_layout(self, widget):
                """Properly clear a widget's layout and all child widgets"""
                try:
                    # Process any pending deletions first
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    
                    # Clear all child widgets first
                    for child in widget.findChildren(object):
                        if hasattr(child, 'deleteLater') and child != widget:
                            child.deleteLater()
                    
                    # Process deletions
                    QApplication.processEvents()
                    
                    # Handle layout
                    layout = widget.layout()
                    if layout is not None:
                        # Remove all items from layout
                        while layout.count():
                            item = layout.takeAt(0)
                            if item.widget():
                                item.widget().deleteLater()
                            elif item.layout():
                                item.layout().deleteLater()
                        
                        # Delete the layout itself
                        layout.deleteLater()
                    
                    # Process final deletions
                    QApplication.processEvents()
                            
                except Exception as e:
                    print(f"Error clearing widget layout: {e}")


        return HALogMainWindow()

def main():
    try:
        setup_environment()

        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QFont

        app = QApplication(sys.argv)
        app.setApplicationName("HALog")
        app.setApplicationVersion(APP_VERSION)

        # Set font
        font = QFont("Segoe UI", 9)
        app.setFont(font)

        # Create and show window
        halog_app = HALogApp()
        window = halog_app.create_window()
        window.show()

        # Startup complete
        total_time = time.time() - startup_begin
        print(f"HALog started in {total_time:.2f}s")

        return app.exec_()

    except Exception as e:
        print(f"Startup error: {e}")
        # Attempt to show error message if QApplication is available
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            if not QApplication.instance():
                app = QApplication(sys.argv)
            else:
                app = QApplication.instance()
            QMessageBox.critical(None, "Startup Error", f"Error starting HALog: {str(e)}")
        except Exception as e_msgbox:
            print(f"Could not display error message box: {e_msgbox}")
        return 1

if __name__ == "__main__":
    sys.exit(main())