#!/usr/bin/env python3
"""
UI Integration Test for Multi-Machine Support
Tests that the UI components are properly created and connected.
"""

import sys
import os
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_ui_components():
    """Test that UI components are properly created"""
    print("🧪 Testing UI Components...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from main_window import Ui_MainWindow
        from PyQt5.QtWidgets import QMainWindow
        
        # Create QApplication (required for Qt widgets)
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # Create main window and UI
        main_window = QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(main_window)
        
        # Test that machine selection combo box was created
        if hasattr(ui, 'cmbMachineSelect'):
            print("  ✓ Machine selection combo box created")
            print(f"  ✓ Combo box font: {ui.cmbMachineSelect.font().family()}")
            print(f"  ✓ Combo box tooltip: '{ui.cmbMachineSelect.toolTip()}'")
            print(f"  ✓ Combo box minimum width: {ui.cmbMachineSelect.minimumWidth()}px")
        else:
            print("  ❌ Machine selection combo box NOT found")
            return False
        
        # Test that other UI elements still exist
        required_elements = ['lblSerial', 'btnRefreshData', 'btnClearDB', 'tabWidget']
        for element in required_elements:
            if hasattr(ui, element):
                print(f"  ✓ {element} exists")
            else:
                print(f"  ❌ {element} missing")
                return False
        
        print("✅ UI Components test passed!")
        return True
        
    except Exception as e:
        print(f"❌ UI Components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_machine_manager_integration():
    """Test integration between machine manager and main application structure"""
    print("\n🧪 Testing Machine Manager Integration...")
    
    try:
        from database import DatabaseManager
        from machine_manager import MachineManager
        
        # Create temp database and add test data
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        db = DatabaseManager(temp_db.name)
        machine_manager = MachineManager(db)
        
        # Test integration methods
        print(f"  ✓ Machine manager created successfully")
        print(f"  ✓ Database connection: {db.db_path}")
        
        # Test that all expected methods exist
        expected_methods = [
            'get_available_machines',
            'get_machine_dropdown_options',
            'set_selected_machine',
            'get_filtered_data',
            'auto_select_machine',
            'get_machine_summary'
        ]
        
        for method in expected_methods:
            if hasattr(machine_manager, method):
                print(f"  ✓ Method '{method}' exists")
            else:
                print(f"  ❌ Method '{method}' missing")
                return False
        
        # Test method calls with empty database
        machines = machine_manager.get_available_machines()
        options = machine_manager.get_machine_dropdown_options()
        auto_selection = machine_manager.auto_select_machine()
        
        print(f"  ✓ Empty DB - Machines: {machines}")
        print(f"  ✓ Empty DB - Options: {options}")
        print(f"  ✓ Empty DB - Auto-selection: {auto_selection}")
        
        print("✅ Machine Manager Integration test passed!")
        
        # Cleanup
        os.unlink(temp_db.name)
        return True
        
    except Exception as e:
        print(f"❌ Machine Manager Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run UI integration tests"""
    print("🚀 HALbasic UI Integration Tests for Multi-Machine Support")
    print("=" * 60)
    
    tests = [
        test_ui_components,
        test_machine_manager_integration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All UI integration tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())