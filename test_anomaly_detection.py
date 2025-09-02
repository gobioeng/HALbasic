#!/usr/bin/env python3
"""
Test script for anomaly detection functionality
Tests the new percentage deviation anomaly detection
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
import numpy as np
from data_analyzer import DataAnalyzer
from database import DatabaseManager

def test_anomaly_detection():
    """Test the anomaly detection functionality"""
    print("🧪 Testing Anomaly Detection Functionality")
    print("=" * 50)
    
    # Create test data
    test_data = []
    base_values = {
        'Cooling Pump Pressure': 200.0,  # Normal value around 200 PSI
        'Mag Flow': 6.0,                 # Normal value around 6 L/min  
        'Flow Target': 3.0,              # Normal value around 3 L/min
    }
    
    # Generate normal data points
    for i in range(50):
        datetime_val = pd.Timestamp.now() - pd.Timedelta(hours=i)
        for param, base_val in base_values.items():
            # Add some normal variation (±1%)
            normal_variation = np.random.normal(0, base_val * 0.01)
            value = base_val + normal_variation
            
            test_data.append({
                'datetime': datetime_val,
                'serial': 'TEST001',
                'param': param,
                'avg': value,
                'min': value - 0.1,
                'max': value + 0.1
            })
    
    # Generate anomalous data points (>2% deviation)
    anomaly_count = 0
    for param, base_val in base_values.items():
        # High anomaly (+5%)
        anomaly_value_high = base_val * 1.05
        test_data.append({
            'datetime': pd.Timestamp.now(),
            'serial': 'TEST001', 
            'param': param,
            'avg': anomaly_value_high,
            'min': anomaly_value_high - 0.1,
            'max': anomaly_value_high + 0.1
        })
        anomaly_count += 1
        
        # Low anomaly (-3%)
        anomaly_value_low = base_val * 0.97
        test_data.append({
            'datetime': pd.Timestamp.now() - pd.Timedelta(minutes=30),
            'serial': 'TEST001',
            'param': param, 
            'avg': anomaly_value_low,
            'min': anomaly_value_low - 0.1,
            'max': anomaly_value_low + 0.1
        })
        anomaly_count += 1
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    print(f"✓ Created test dataset with {len(df)} records")
    print(f"✓ Expected anomalies: {anomaly_count}")
    
    # Test anomaly detection
    analyzer = DataAnalyzer()
    anomalies = analyzer.detect_percentage_deviation_anomalies(df, deviation_threshold=2.0)
    
    print(f"✓ Detected anomalies: {len(anomalies)}")
    
    if len(anomalies) > 0:
        print("\n📊 Detected Anomalies:")
        for _, anomaly in anomalies.iterrows():
            param = anomaly['param']
            value = anomaly['avg']
            print(f"  - {param}: {value:.2f}")
    
    # Test database storage
    print("\n🗄️ Testing Database Storage...")
    db = DatabaseManager("test_anomaly.db")
    
    # Store anomalies
    success = db.store_anomalies(anomalies)
    if success:
        print("✓ Anomalies stored successfully")
        
        # Retrieve anomalies
        retrieved = db.get_anomalies(limit=10)
        print(f"✓ Retrieved {len(retrieved)} anomalies from database")
        
        count = db.get_anomaly_count()
        print(f"✓ Total anomaly count: {count}")
    else:
        print("❌ Failed to store anomalies")
    
    # Clean up test database
    try:
        os.remove("test_anomaly.db")
        print("✓ Cleaned up test database")
    except:
        pass
    
    print("\n🎉 Anomaly detection test completed!")
    
    # Validate results
    if len(anomalies) >= anomaly_count * 0.8:  # Allow some tolerance
        print("✅ TEST PASSED: Anomaly detection working correctly")
        return True
    else:
        print(f"❌ TEST FAILED: Expected ~{anomaly_count} anomalies, got {len(anomalies)}")
        return False

if __name__ == "__main__":
    success = test_anomaly_detection()
    sys.exit(0 if success else 1)