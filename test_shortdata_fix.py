#!/usr/bin/env python3
"""
Test script to verify shortdata import fix with proper tabs
"""

import sys
import os
import tempfile
from unified_parser import UnifiedParser

def test_shortdata_parsing():
    """Test that shortdata parsing and DataFrame conversion works"""
    
    # Create test data with actual tab characters
    test_lines = [
        "2024-08-01\t10:00:00\tTB\tSN# 001\tmagnetronFlow: count=60, max=12.1, min=10.8, avg=11.5\tTB\tTB\tTB",
        "2024-08-01\t10:00:05\tTB\tSN# 001\tFanfanSpeed1Statistics: count=60, max=2850, min=2750, avg=2800\tTB\tTB\tTB",
        "2024-08-01\t10:00:10\tTB\tSN# 001\tFanhumidityStatistics: count=60, max=46.2, min=44.8, avg=45.5\tTB\tTB\tTB"
    ]
    test_data = "\n".join(test_lines)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_data)
        temp_file = f.name
    
    try:
        # Test parsing
        parser = UnifiedParser()
        result = parser.parse_short_data_file(temp_file)
        
        print("=== Parsing Test ===")
        print(f"Success: {result.get('success', False)}")
        print(f"Parameters found: {result.get('total_parameters', 0)}")
        
        if result.get('parameters'):
            print("Sample parameter:", result['parameters'][0])
        
        # Test DataFrame conversion
        df = parser.convert_short_data_to_dataframe(result)
        print(f"\n=== DataFrame Conversion Test ===")
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Unique parameters: {len(df['parameter_type'].unique()) if not df.empty else 0}")
        
        # Check analysis compatibility
        print(f"\n=== Analysis Compatibility ===")
        has_required_cols = all(col in df.columns for col in ['datetime', 'parameter_type', 'statistic_type', 'value'])
        print(f"Has required columns for analysis: {has_required_cols}")
        
        if has_required_cols and not df.empty:
            print("✅ Shortdata import fix successful!")
            
            # Show sample data for analysis
            avg_data = df[df['statistic_type'] == 'avg'].head(3)
            print(f"\nSample avg data for analysis:")
            for _, row in avg_data.iterrows():
                print(f"  {row['parameter_type']}: {row['value']} at {row['datetime']}")
                
            return True
        else:
            print("❌ Missing required columns or empty DataFrame")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        os.unlink(temp_file)

if __name__ == "__main__":
    success = test_shortdata_parsing()
    sys.exit(0 if success else 1)