#!/usr/bin/env python3
"""
End-to-End Test for Multi-Machine Log Analysis
Demonstrates complete workflow with sample data
"""

import sys
import os
import tempfile
import pandas as pd

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_sample_log_data():
    """Create realistic sample log data for multiple machines"""
    
    # Machine 1: SN123456 (High performance machine)
    machine1_data = []
    for i in range(50):  # Reduced to avoid invalid times
        hour = 10 + i // 60
        minute = i % 60
        machine1_data.extend([
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN123456', 'pumpPressure', 'avg', 205.0 + i*0.1, 1, 'PSI'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN123456', 'magnetronFlow', 'avg', 6.2 + i*0.01, 1, 'L/min'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN123456', 'targetFlow', 'avg', 3.8 + i*0.005, 1, 'L/min'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN123456', 'MLC Bank A 48V', 'avg', 48.1 + i*0.002, 1, 'V'),
        ])
    
    # Machine 2: SN789012 (Standard performance machine)  
    machine2_data = []
    for i in range(40):  # Reduced to avoid invalid times
        hour = 12 + i // 60
        minute = i % 60
        machine2_data.extend([
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN789012', 'pumpPressure', 'avg', 195.0 + i*0.08, 1, 'PSI'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN789012', 'magnetronFlow', 'avg', 5.8 + i*0.008, 1, 'L/min'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN789012', 'targetFlow', 'avg', 3.5 + i*0.003, 1, 'L/min'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN789012', 'MLC Bank B 48V', 'avg', 47.9 + i*0.001, 1, 'V'),
        ])
    
    # Machine 3: SN456789 (Older machine with some issues)
    machine3_data = []
    for i in range(30):  # Reduced to avoid invalid times
        hour = 14 + i // 60  
        minute = i % 60
        machine3_data.extend([
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN456789', 'pumpPressure', 'avg', 185.0 + i*0.15, 1, 'PSI'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN456789', 'magnetronFlow', 'avg', 5.2 + i*0.012, 1, 'L/min'),
            (f'2023-01-01 {hour:02d}:{minute:02d}:00', 'SN456789', 'cityWaterFlow', 'avg', 12.5 + i*0.02, 1, 'L/min'),
        ])
    
    return machine1_data + machine2_data + machine3_data

def test_end_to_end_workflow():
    """Test complete multi-machine workflow"""
    print("🚀 End-to-End Multi-Machine Workflow Test")
    print("=" * 50)
    
    try:
        from database import DatabaseManager
        from machine_manager import MachineManager
        
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        print(f"📁 Created test database: {temp_db.name}")
        
        # Initialize components
        db = DatabaseManager(temp_db.name)
        machine_manager = MachineManager(db)
        print("✓ Components initialized")
        
        # 1. Simulate log file import
        print("\n📥 Step 1: Simulating Multi-Machine Log Import")
        sample_data = create_sample_log_data()
        
        with db.get_connection() as conn:
            for data in sample_data:
                conn.execute("""
                    INSERT INTO water_logs
                    (datetime, serial_number, parameter_type, statistic_type,
                     value, count, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
            conn.commit()
        
        print(f"✓ Imported {len(sample_data)} records from 3 machines")
        
        # 2. Machine Discovery
        print("\n🔍 Step 2: Machine Discovery")
        machines = machine_manager.get_available_machines()
        print(f"✓ Discovered {len(machines)} machines: {machines}")
        
        # 3. Test dropdown population
        print("\n📋 Step 3: Dropdown Population")
        dropdown_options = machine_manager.get_machine_dropdown_options()
        print(f"✓ Dropdown options: {dropdown_options}")
        
        # 4. Test auto-selection
        print("\n🎯 Step 4: Auto-Selection")
        auto_selected = machine_manager.auto_select_machine()
        print(f"✓ Auto-selected: {auto_selected}")
        
        # 5. Test data filtering for each machine
        print("\n📊 Step 5: Data Filtering Analysis")
        
        for machine in machines:
            machine_manager.set_selected_machine(machine)
            filtered_data = machine_manager.get_filtered_data()
            summary = machine_manager.get_machine_summary(machine)
            
            print(f"  📈 {machine}:")
            print(f"    - Records: {len(filtered_data)}")
            print(f"    - Parameters: {summary.get('parameter_count', 0)}")
            print(f"    - Date range: {summary.get('start_date', 'N/A')} to {summary.get('end_date', 'N/A')}")
            
            if len(filtered_data) > 0:
                # Show some parameter statistics
                param_counts = filtered_data['parameter_type'].value_counts()
                print(f"    - Top parameters: {dict(param_counts.head(3))}")
        
        # 6. Test "All Machines" view
        print("\n🌐 Step 6: All Machines View")
        machine_manager.set_selected_machine("All Machines")
        all_filtered = machine_manager.get_filtered_data()
        print(f"✓ All Machines view: {len(all_filtered)} records")
        
        # 7. Simulate dashboard update workflow
        print("\n🎛️ Step 7: Dashboard Workflow Simulation")
        
        # Test single machine selection
        machine_manager.set_selected_machine(machines[0])
        dashboard_data = machine_manager.get_filtered_data()
        if not dashboard_data.empty:
            latest_record = dashboard_data.sort_values('datetime').iloc[-1]
            print(f"✓ Latest record for {machines[0]}:")
            print(f"    - Serial: {latest_record.get('serial_number', 'N/A')}")
            print(f"    - DateTime: {latest_record.get('datetime', 'N/A')}")
            print(f"    - Parameter: {latest_record.get('parameter_type', 'N/A')}")
            print(f"    - Value: {latest_record.get('value', 'N/A')} {latest_record.get('unit', '')}")
        
        print("\n✅ End-to-End Workflow Test Completed Successfully!")
        print("\n📊 Summary:")
        print(f"  - Machines discovered: {len(machines)}")
        print(f"  - Total records processed: {len(sample_data)}")
        
        # Calculate records per machine
        machine_records = []
        for machine in machines:
            machine_manager.set_selected_machine(machine)
            filtered = machine_manager.get_filtered_data()
            machine_records.append(len(filtered))
        
        print(f"  - Records per machine: {machine_records}")
        print(f"  - Dropdown options: {len(dropdown_options)}")
        
        # Cleanup
        os.unlink(temp_db.name)
        return True
        
    except Exception as e:
        print(f"❌ End-to-End test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run end-to-end workflow test"""
    if test_end_to_end_workflow():
        print("\n🎉 Multi-machine functionality is working correctly!")
        return 0
    else:
        print("\n⚠️ End-to-end test failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())