
#!/usr/bin/env python3
"""
Test script to verify data parsing and database functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_parser import UnifiedParser
from database import DatabaseManager
import pandas as pd

def test_parsing():
    """Test the parsing functionality"""
    print("🧪 Testing Data Parsing...")
    
    parser = UnifiedParser()
    
    # Test with sample data
    test_files = ['data/sample_halog_data.txt', 'data/shortdata.txt']
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n📄 Testing with: {file_path}")
            
            df = parser.parse_linac_file(file_path)
            
            if not df.empty:
                print(f"✅ Parsed {len(df)} records")
                print(f"📊 Columns: {list(df.columns)}")
                print(f"🏷️  Parameters found: {df['parameter_type'].unique()}")
                print(f"📈 Statistics: {df['statistic_type'].unique()}")
                
                # Show sample data
                print("\n📋 Sample records:")
                print(df.head(3).to_string())
                
                # Test database insertion
                db = DatabaseManager("test_halog.db")
                records_inserted = db.insert_data_batch(df)
                print(f"💾 Inserted {records_inserted} records to database")
                
                # Test retrieval
                retrieved_df = db.get_all_logs()
                print(f"🔍 Retrieved {len(retrieved_df)} records from database")
                print(f"📊 Retrieved columns: {list(retrieved_df.columns)}")
                
                if not retrieved_df.empty:
                    print(f"🏷️  Retrieved parameters: {retrieved_df['param'].unique()}")
                
                break
            else:
                print(f"❌ No data parsed from {file_path}")
        else:
            print(f"❌ File not found: {file_path}")

if __name__ == "__main__":
    test_parsing()
