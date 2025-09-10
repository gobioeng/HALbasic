#!/usr/bin/env python3
"""
Test and demo script for the modernized LINAC dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from modern_dashboard import ModernDashboard
from machine_manager import MachineManager
from database import DatabaseManager

class DashboardTestWindow(QMainWindow):
    """Test window for the modernized dashboard"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HALog LINAC Dashboard - Modernized")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize database and machine manager
        try:
            self.db = DatabaseManager()
            self.machine_manager = MachineManager(self.db)
            
            # Auto-select a machine for testing
            available_machines = self.machine_manager.get_available_machines()
            if available_machines:
                print(f"Available machines: {available_machines}")
                # Start with first machine selected
                self.machine_manager.set_selected_machine(available_machines[0])
                print(f"Selected machine: {available_machines[0]}")
            else:
                print("No machines available")
            
        except Exception as e:
            print(f"Error initializing managers: {e}")
            self.db = None
            self.machine_manager = None
        
        # Create the modern dashboard
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        self.dashboard = ModernDashboard(self.machine_manager, self.db, self)
        layout.addWidget(self.dashboard)
        
        self.setCentralWidget(central_widget)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

def test_dashboard_functionality():
    """Test the dashboard functionality"""
    print("🧪 Testing Modern Dashboard Functionality")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create and show the test window
    window = DashboardTestWindow()
    window.show()
    
    print("✅ Dashboard window created and displayed")
    print("📊 Features demonstrated:")
    print("   - Machine selector dropdown")
    print("   - Real-time status indicators")
    print("   - Machine-specific data filtering")
    print("   - Enhanced trend visualization")
    print("   - Modern card-based layout")
    print("   - 30-second auto-refresh")
    print("\n💡 Use the machine selector to switch between machines")
    print("💡 Click 'Compare Machines' to see multi-machine view")
    print("💡 Select different parameters in the trend chart")
    
    # Run the application
    return app.exec_()

if __name__ == "__main__":
    exit_code = test_dashboard_functionality()
    sys.exit(exit_code)