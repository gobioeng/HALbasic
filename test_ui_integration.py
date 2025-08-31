#!/usr/bin/env python3
"""
Test UI integration workflow for shortdata import
This simulates the UI flow without needing the actual GUI
"""

import sys
import os
import tempfile
import pandas as pd
from unittest.mock import Mock

# Add the project directory to path
sys.path.insert(0, '/home/runner/work/halog/halog')

def test_ui_integration():
    """Test the complete UI integration workflow"""
    
    print("=== Testing UI Integration Workflow ===")
    
    # Create comprehensive test data
    test_lines = [
        "2024-08-01\t10:00:00\tTB\tSN# 001\tmagnetronFlow: count=60, max=12.1, min=10.8, avg=11.5\tTB\tTB\tTB",
        "2024-08-01\t10:00:05\tTB\tSN# 001\tmagnetronFlow: count=60, max=12.3, min=10.9, avg=11.7\tTB\tTB\tTB",
        "2024-08-01\t10:00:10\tTB\tSN# 001\tFanfanSpeed1Statistics: count=60, max=2850, min=2750, avg=2800\tTB\tTB\tTB",
        "2024-08-01\t10:00:15\tTB\tSN# 001\tFanfanSpeed1Statistics: count=60, max=2860, min=2760, avg=2810\tTB\tTB\tTB",
        "2024-08-01\t10:00:20\tTB\tSN# 001\tFanhumidityStatistics: count=60, max=46.2, min=44.8, avg=45.5\tTB\tTB\tTB",
        "2024-08-01\t10:00:25\tTB\tSN# 001\tFanhumidityStatistics: count=60, max=46.4, min=45.0, avg=45.7\tTB\tTB\tTB",
        "2024-08-01\t10:00:30\tTB\tSN# 001\tMLC_ADC_CHAN_TEMP_BANKA_STAT: count=60, max=24.2, min=23.8, avg=24.0\tTB\tTB\tTB",
        "2024-08-01\t10:00:35\tTB\tSN# 001\tMLC_ADC_CHAN_TEMP_BANKA_STAT: count=60, max=24.3, min=23.9, avg=24.1\tTB\tTB\tTB"
    ]
    test_data = "\n".join(test_lines)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_data)
        temp_file = f.name
    
    try:
        # 1. Simulate file import detection (shortdata.txt file)
        print("1. File import detection...")
        filename = os.path.basename(temp_file)
        is_shortdata = 'shortdata' in filename.lower() or 'short' in filename.lower()
        print(f"   File: {filename}")
        print(f"   Detected as shortdata: {is_shortdata}")
        
        # 2. Simulate the parsing and conversion workflow
        print("\n2. Parsing and conversion...")
        from unified_parser import UnifiedParser
        
        parser = UnifiedParser()
        parsed_data = parser.parse_short_data_file(temp_file)
        df_converted = parser.convert_short_data_to_dataframe(parsed_data)
        
        print(f"   Parsing success: {parsed_data.get('success', False)}")
        print(f"   Parameters parsed: {parsed_data.get('total_parameters', 0)}")
        print(f"   DataFrame records: {len(df_converted)}")
        
        # 3. Simulate populating self.df (what happens in _process_sample_shortdata)
        print("\n3. DataFrame population...")
        mock_app = Mock()
        mock_app.df = df_converted
        mock_app.shortdata_parameters = parsed_data
        mock_app.shortdata_parser = parser
        
        print(f"   self.df populated: {not mock_app.df.empty}")
        print(f"   Available parameters: {list(mock_app.df['parameter_type'].unique())}")
        
        # 4. Test trend control initialization 
        print("\n4. Trend controls initialization...")
        groups = parsed_data.get('grouped_parameters', {})
        for group_name, params in groups.items():
            if params:
                param_names = [p.get('parameter_name', 'Unknown') for p in params]
                unique_params = list(set(param_names))
                print(f"   {group_name}: {len(unique_params)} unique parameters")
                print(f"     Examples: {unique_params[:3]}")
        
        # 5. Test analysis capability
        print("\n5. Analysis functionality...")
        from analyzer_data import DataAnalyzer
        
        analyzer = DataAnalyzer()
        
        # Test if the DataFrame has required columns for analysis
        required_cols = ['datetime', 'parameter_type', 'statistic_type', 'value']
        has_required = all(col in mock_app.df.columns for col in required_cols)
        print(f"   Has required columns: {has_required}")
        
        if has_required:
            trends_df = analyzer.calculate_advanced_trends(mock_app.df)
            print(f"   Trends calculated: {len(trends_df)}")
            
            if not trends_df.empty:
                print("   Trend analysis results:")
                for _, row in trends_df.iterrows():
                    param = row.get('parameter_type', 'Unknown')
                    direction = row.get('trend_direction', 'Unknown')
                    points = row.get('data_points', 0)
                    print(f"     {param}: {direction} ({points} data points)")
        
        # 6. Test parameter mapping for trend dropdowns
        print("\n6. Parameter mapping for dropdowns...")
        parameter_mapping = parser.parameter_mapping
        
        mapped_params = []
        for param_type in mock_app.df['parameter_type'].unique():
            if param_type in parameter_mapping:
                description = parameter_mapping[param_type].get('description', param_type)
                mapped_params.append(f"{param_type} -> {description}")
            else:
                mapped_params.append(f"{param_type} -> (no mapping)")
        
        print("   Parameter mappings:")
        for mapping in mapped_params:
            print(f"     {mapping}")
        
        # 7. Test graph data availability
        print("\n7. Graph data availability...")
        avg_data = mock_app.df[mock_app.df['statistic_type'] == 'avg']
        grouped_for_graphs = avg_data.groupby('parameter_type')
        
        print("   Data available for graphing:")
        for param_type, group in grouped_for_graphs:
            time_range = group['datetime'].max() - group['datetime'].min()
            print(f"     {param_type}: {len(group)} points over {time_range}")
        
        print("\n✅ UI Integration Test Successful!")
        print("\nSummary:")
        print(f"- File parsing: ✅ {parsed_data.get('total_parameters', 0)} parameters")
        print(f"- DataFrame conversion: ✅ {len(df_converted)} records")
        print(f"- Analysis compatibility: ✅ {len(trends_df) if 'trends_df' in locals() else 0} trends")
        print(f"- Parameter groups: ✅ {len([g for g in groups.values() if g])} non-empty groups")
        print(f"- Graph data: ✅ {len(grouped_for_graphs)} parameter types")
        
        return True
        
    except Exception as e:
        print(f"❌ UI Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        os.unlink(temp_file)

if __name__ == "__main__":
    success = test_ui_integration()
    sys.exit(0 if success else 1)