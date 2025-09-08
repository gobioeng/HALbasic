#!/usr/bin/env python3
"""
Test dashboard data loading and identify missing data issues
"""

import sys
import os
import tempfile
import time
import traceback

# Set QT platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_comprehensive_test_data():
    """Create comprehensive test LINAC data with various parameters"""
    lines = []
    
    # Define realistic parameters
    parameters = [
        ("Water_System_Temp", 23.5, 26.0, 24.7),
        ("Cooling_Flow_Rate", 15.2, 18.9, 17.1),
        ("Pressure_Monitor", 2.1, 2.8, 2.4),
        ("MLC_Bank_A_24V", 23.8, 24.2, 24.0),
        ("MLC_Bank_B_24V", 23.7, 24.3, 24.1),
        ("COL_24V_Monitor", 23.9, 24.1, 24.0),
        ("Room_Humidity", 45.2, 52.8, 49.1),
        ("Fan_Speed_Monitor", 1200, 1350, 1275),
    ]
    
    # Generate data for multiple days
    for day in range(3):
        for hour in range(24):
            for minute in [0, 15, 30, 45]:  # Every 15 minutes
                timestamp = f"2023-01-{day+1:02d} {hour:02d}:{minute:02d}:00"
                serial = f"SN{123456 + day}"  # Different serials for multi-machine
                
                for param_name, min_val, max_val, avg_val in parameters:
                    # Add some variation
                    variation = (hour + minute) * 0.01
                    actual_min = min_val + variation
                    actual_max = max_val + variation  
                    actual_avg = avg_val + variation
                    
                    line = f"{timestamp} {serial} {param_name} count=1, max={actual_max:.3f}, min={actual_min:.3f}, avg={actual_avg:.3f}"
                    lines.append(line)
    
    content = "\n".join(lines)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(content)
        return f.name

def test_database_data_loading():
    """Test database data loading and verify what's being stored"""
    print("=== Testing Database Data Loading ===")
    
    try:
        from database import DatabaseManager
        import pandas as pd
        
        # Create test database
        db = DatabaseManager(":memory:")
        print("✓ Database initialized")
        
        # Check initial state
        summary_stats = db.get_summary_statistics()
        print(f"✓ Initial summary stats: {summary_stats}")
        
        if summary_stats and summary_stats.get('total_records', 0) > 0:
            print("⚠ Database already has data - this should be empty for test")
        
        # Test data insertion
        test_file = create_comprehensive_test_data()
        file_size = os.path.getsize(test_file)
        print(f"✓ Created test file: {file_size:,} bytes")
        
        # Parse and insert data
        from unified_parser import UnifiedParser
        parser = UnifiedParser()
        
        print("Parsing test data...")
        df = parser.parse_linac_file(test_file)
        print(f"✓ Parsed data shape: {df.shape}")
        
        if df.empty:
            print("✗ No data was parsed from test file!")
            return False
        
        print("✓ Sample parsed data:")
        print(df.head())
        print(f"✓ Columns: {list(df.columns)}")
        print(f"✓ Parameter types: {df['param'].unique()[:10] if 'param' in df.columns else 'No param column'}")
        
        # Insert into database
        print("Inserting data into database...")
        records_inserted = db.insert_data_batch(df)
        print(f"✓ Inserted {records_inserted} records")
        
        # Test database retrieval methods
        print("\nTesting database retrieval methods:")
        
        # 1. Test summary statistics
        summary_stats = db.get_summary_statistics()
        print(f"✓ Summary stats: {summary_stats}")
        
        # 2. Test get_all_logs
        try:
            all_logs = db.get_all_logs(chunk_size=1000)
            print(f"✓ get_all_logs() returned {len(all_logs)} records")
        except Exception as e:
            print(f"✗ get_all_logs() failed: {e}")
            try:
                all_logs = db.get_all_logs()
                print(f"✓ get_all_logs() (no chunking) returned {len(all_logs)} records")
            except Exception as e2:
                print(f"✗ get_all_logs() (no chunking) also failed: {e2}")
                return False
        
        # 3. Test get_recent_logs
        try:
            recent_logs = db.get_recent_logs(limit=100)
            print(f"✓ get_recent_logs() returned {len(recent_logs)} records")
        except Exception as e:
            print(f"✗ get_recent_logs() failed: {e}")
        
        # Analyze the data structure
        if not all_logs.empty:
            print(f"\n✓ Data structure analysis:")
            print(f"  Shape: {all_logs.shape}")
            print(f"  Columns: {list(all_logs.columns)}")
            if 'datetime' in all_logs.columns:
                print(f"  Date range: {all_logs['datetime'].min()} to {all_logs['datetime'].max()}")
            if 'param' in all_logs.columns:
                print(f"  Unique parameters: {all_logs['param'].nunique()}")
                print(f"  Parameters: {list(all_logs['param'].unique()[:10])}")
            if 'serial' in all_logs.columns:
                print(f"  Unique serials: {all_logs['serial'].unique()}")
        
        # Clean up
        try:
            os.unlink(test_file)
        except:
            pass
        
        print("✓ Database data loading test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Database data loading test failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_loading_simulation():
    """Test the dashboard loading process like in main.py"""
    print("\n=== Testing Dashboard Loading Simulation ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from database import DatabaseManager
        from unified_parser import UnifiedParser
        import pandas as pd
        
        app = QApplication([])
        
        # Create database with test data
        db = DatabaseManager(":memory:")
        
        # Create and parse test data
        test_file = create_comprehensive_test_data()
        parser = UnifiedParser()
        df = parser.parse_linac_file(test_file)
        records_inserted = db.insert_data_batch(df)
        
        print(f"✓ Test setup: {records_inserted} records in database")
        
        # Simulate dashboard loading steps from main.py
        print("\nSimulating dashboard loading steps:")
        
        # Step 1: Check summary statistics
        summary_stats = db.get_summary_statistics()
        if not summary_stats:
            print("✗ No data available in database (summary_stats is None/empty)")
            return False
        print(f"✓ Step 1 - Summary stats: {summary_stats}")
        
        # Step 2: Load recent data for UI initialization
        try:
            raw_df = db.get_recent_logs(limit=1000)
            print(f"✓ Step 2 - Recent logs: {len(raw_df)} records")
        except (TypeError, AttributeError) as e:
            print(f"⚠ Step 2 - get_recent_logs failed: {e}, trying fallback...")
            try:
                raw_df = db.get_all_logs(chunk_size=1000)
                if len(raw_df) > 1000:
                    raw_df = raw_df.tail(1000)
                print(f"✓ Step 2 - Fallback successful: {len(raw_df)} records")
            except TypeError:
                raw_df = db.get_all_logs()
                if len(raw_df) > 1000:
                    raw_df = raw_df.tail(1000)
                print(f"✓ Step 2 - Final fallback: {len(raw_df)} records")
        
        # Step 3: Check if data is usable
        if raw_df.empty:
            print("✗ Step 3 - Raw data is empty after loading")
            return False
        
        print(f"✓ Step 3 - Data validation passed: {len(raw_df)} records, {list(raw_df.columns)}")
        
        # Step 4: Load full dataset (like after file import)
        try:
            full_df = db.get_all_logs(chunk_size=10000)
            print(f"✓ Step 4 - Full dataset: {len(full_df)} records")
        except TypeError:
            full_df = db.get_all_logs()
            print(f"✓ Step 4 - Full dataset (no chunking): {len(full_df)} records")
        
        # Step 5: Verify data structure for dashboard
        required_columns = ['datetime', 'param', 'avg']
        missing_columns = [col for col in required_columns if col not in full_df.columns]
        
        if missing_columns:
            print(f"✗ Step 5 - Missing required columns: {missing_columns}")
            print(f"  Available columns: {list(full_df.columns)}")
            return False
        
        print(f"✓ Step 5 - Data structure validation passed")
        
        # Clean up
        try:
            os.unlink(test_file)
        except:
            pass
        
        print("✓ Dashboard loading simulation completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Dashboard loading simulation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run dashboard data tests"""
    print("HALog Dashboard Data Loading Tests")
    print("=" * 45)
    
    tests = [
        test_database_data_loading,
        test_dashboard_loading_simulation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 45)
    print("Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All dashboard data tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} dashboard data test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())