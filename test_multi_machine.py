#!/usr/bin/env python3
"""
Test script for multi-machine log analysis functionality
Tests the machine manager and database integration for multi-machine support.
"""

import sys
import os
import pandas as pd
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_machine_manager():
    """Test basic machine manager functionality"""
    print("🧪 Testing Machine Manager...")
    
    try:
        # Create a temporary database for testing
        from database import DatabaseManager
        from machine_manager import MachineManager
        
        # Create temp database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        # Initialize database and machine manager
        db = DatabaseManager(temp_db.name)
        machine_manager = MachineManager(db)
        
        # Test with empty database
        machines = machine_manager.get_available_machines()
        print(f"  ✓ Empty database: {len(machines)} machines found")
        
        # Create sample test data
        test_data = [
            ('2023-01-01 10:00:00', 'SN123456', 'pumpPressure', 'avg', 200.0, 1, 'PSI'),
            ('2023-01-01 10:05:00', 'SN123456', 'magnetronFlow', 'avg', 6.0, 1, 'L/min'),
            ('2023-01-01 10:00:00', 'SN789012', 'pumpPressure', 'avg', 195.0, 1, 'PSI'),
            ('2023-01-01 10:05:00', 'SN789012', 'targetFlow', 'avg', 3.5, 1, 'L/min'),
        ]
        
        # Insert test data
        print("  📝 Inserting test data...")
        with db.get_connection() as conn:
            for data in test_data:
                conn.execute("""
                    INSERT INTO water_logs
                    (datetime, serial_number, parameter_type, statistic_type,
                     value, count, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
            conn.commit()
        
        # Test machine discovery
        machines = machine_manager.get_available_machines()
        print(f"  ✓ Found {len(machines)} machines: {machines}")
        
        # Test machine selection
        if machines:
            machine_manager.set_selected_machine(machines[0])
            selected = machine_manager.get_selected_machine()
            print(f"  ✓ Selected machine: {selected}")
            
            # Test data filtering
            all_data = db.get_all_logs()
            filtered_data = machine_manager.get_filtered_data(all_data)
            print(f"  ✓ Filtered data: {len(filtered_data)} records for {selected}")
            
            # Test machine summary
            summary = machine_manager.get_machine_summary(selected)
            print(f"  ✓ Machine summary: {summary.get('record_count', 0)} records, {summary.get('parameter_count', 0)} parameters")
        
        # Test dropdown options
        dropdown_options = machine_manager.get_machine_dropdown_options()
        print(f"  ✓ Dropdown options: {dropdown_options}")
        
        # Test auto-selection
        auto_selected = machine_manager.auto_select_machine()
        print(f"  ✓ Auto-selected machine: {auto_selected}")
        
        print("✅ Machine Manager tests passed!")
        
        # Cleanup
        os.unlink(temp_db.name)
        return True
        
    except Exception as e:
        print(f"❌ Machine Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_serial_extraction():
    """Test database serial number extraction"""
    print("\n🧪 Testing Database Serial Number Extraction...")
    
    try:
        from database import DatabaseManager
        
        # Create temp database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        db = DatabaseManager(temp_db.name)
        
        # Test with empty database
        serials = db.get_unique_serial_numbers()
        print(f"  ✓ Empty database: {len(serials)} serial numbers")
        
        # Insert test data with different serial formats
        test_data = [
            ('2023-01-01 10:00:00', 'SN123456', 'param1', 'avg', 100.0, 1, 'unit'),
            ('2023-01-01 10:05:00', 'SN123456', 'param2', 'avg', 200.0, 1, 'unit'),
            ('2023-01-01 10:00:00', 'SN#789012', 'param1', 'avg', 150.0, 1, 'unit'),
            ('2023-01-01 10:05:00', '', 'param3', 'avg', 300.0, 1, 'unit'),  # Empty serial
            ('2023-01-01 10:10:00', 'Unknown', 'param4', 'avg', 400.0, 1, 'unit'),  # Unknown serial
        ]
        
        with db.get_connection() as conn:
            for data in test_data:
                conn.execute("""
                    INSERT INTO water_logs
                    (datetime, serial_number, parameter_type, statistic_type,
                     value, count, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
            conn.commit()
        
        # Test serial extraction
        serials = db.get_unique_serial_numbers()
        expected_serials = ['SN123456', 'SN#789012']  # Should exclude empty and 'Unknown'
        
        print(f"  ✓ Found serial numbers: {serials}")
        print(f"  ✓ Expected: {expected_serials}")
        
        if set(serials) == set(expected_serials):
            print("✅ Database serial extraction tests passed!")
        else:
            print("❌ Serial extraction mismatch")
            return False
        
        # Cleanup
        os.unlink(temp_db.name)
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_machine_scenario():
    """Test behavior with single machine"""
    print("\n🧪 Testing Single Machine Scenario...")
    
    try:
        from database import DatabaseManager
        from machine_manager import MachineManager
        
        # Create temp database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        db = DatabaseManager(temp_db.name)
        machine_manager = MachineManager(db)
        
        # Insert data for single machine
        test_data = [
            ('2023-01-01 10:00:00', 'SN123456', 'param1', 'avg', 100.0, 1, 'unit'),
            ('2023-01-01 10:05:00', 'SN123456', 'param2', 'avg', 200.0, 1, 'unit'),
        ]
        
        with db.get_connection() as conn:
            for data in test_data:
                conn.execute("""
                    INSERT INTO water_logs
                    (datetime, serial_number, parameter_type, statistic_type,
                     value, count, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
            conn.commit()
        
        # Test single machine behavior
        machines = machine_manager.get_available_machines()
        print(f"  ✓ Found {len(machines)} machine(s): {machines}")
        
        dropdown_options = machine_manager.get_machine_dropdown_options()
        print(f"  ✓ Dropdown options for single machine: {dropdown_options}")
        
        auto_selected = machine_manager.auto_select_machine()
        print(f"  ✓ Auto-selected: {auto_selected}")
        
        # For single machine, should auto-select the machine (not "All Machines")
        if len(machines) == 1 and auto_selected == machines[0]:
            print("✅ Single machine scenario tests passed!")
        else:
            print("❌ Single machine auto-selection failed")
            return False
        
        # Cleanup
        os.unlink(temp_db.name)
        return True
        
    except Exception as e:
        print(f"❌ Single machine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all multi-machine tests"""
    print("🚀 HALbasic Multi-Machine Log Analysis Tests")
    print("=" * 50)
    
    tests = [
        test_database_serial_extraction,
        test_machine_manager,
        test_single_machine_scenario,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All multi-machine functionality tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())