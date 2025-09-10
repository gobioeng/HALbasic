#!/usr/bin/env python3
"""
Test script to verify machine discovery fixes and add sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_machine_database import SingleMachineDatabaseManager
from machine_manager import MachineManager
from database import DatabaseManager

def test_machine_discovery_fix():
    """Test the machine discovery fix with sample data"""
    print("🔧 Testing Machine Discovery Fix")
    print("=" * 50)
    
    # Initialize single machine database manager
    smdb = SingleMachineDatabaseManager()
    
    # Add sample data for testing
    print("1. Adding sample data to machine databases...")
    smdb.add_sample_data_for_testing()
    
    # Test machine discovery
    print("\n2. Testing machine discovery...")
    available_machines = smdb.discover_available_machines()
    print(f"✓ Discovered machines: {available_machines}")
    
    if len(available_machines) == 0:
        print("❌ No machines discovered - discovery still failing")
        return False
    
    # Test machine manager integration
    print("\n3. Testing machine manager integration...")
    try:
        db = DatabaseManager()
        mm = MachineManager(db)
        machines_from_manager = mm.get_available_machines()
        print(f"✓ Machine manager found: {machines_from_manager}")
        
        if len(machines_from_manager) > 0:
            # Test machine selection
            mm.set_selected_machine(machines_from_manager[0])
            print(f"✓ Successfully selected machine: {machines_from_manager[0]}")
            
            # Test data filtering
            filtered_data = mm.get_filtered_data()
            print(f"✓ Filtered data shape: {filtered_data.shape if not filtered_data.empty else 'Empty'}")
        
    except Exception as e:
        print(f"❌ Machine manager test failed: {e}")
        return False
    
    # Test database switching
    print("\n4. Testing database switching...")
    for machine_id in available_machines[:2]:  # Test first two machines
        success = smdb.switch_to_machine(machine_id)
        if success:
            summary = smdb.get_machine_summary(machine_id)
            print(f"✓ Machine {machine_id}: {summary.get('record_count', 0)} records")
        else:
            print(f"❌ Failed to switch to machine {machine_id}")
            return False
    
    print("\n✅ All machine discovery tests passed!")
    return True

def verify_dashboard_data():
    """Verify data is available for dashboard testing"""
    print("\n🎯 Verifying Dashboard Data Availability")
    print("=" * 50)
    
    try:
        smdb = SingleMachineDatabaseManager()
        machines = smdb.discover_available_machines()
        
        total_records = 0
        for machine_id in machines:
            if smdb.switch_to_machine(machine_id):
                summary = smdb.get_machine_summary(machine_id)
                records = summary.get('record_count', 0)
                total_records += records
                print(f"Machine {machine_id}: {records} records")
        
        print(f"\nTotal records across all machines: {total_records}")
        
        if total_records > 0:
            print("✅ Dashboard has data to display")
            return True
        else:
            print("❌ No data available for dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying dashboard data: {e}")
        return False

if __name__ == "__main__":
    print("🧪 HALog Machine Discovery & Dashboard Data Test")
    print("=" * 60)
    
    # Run tests
    discovery_ok = test_machine_discovery_fix()
    dashboard_ok = verify_dashboard_data()
    
    if discovery_ok and dashboard_ok:
        print("\n🎉 All tests passed! Ready for dashboard modernization.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)