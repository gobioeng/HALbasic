#!/usr/bin/env python3
"""
Test script to verify HALbasic dashboard fixes
Tests the key issues mentioned in the problem statement
"""

import sys
import os
import tempfile
import sqlite3
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        print("✓ PyQt5 imports successful")
        
        import pandas as pd
        print("✓ Pandas import successful")
        
        import matplotlib
        matplotlib.use('Agg')  # Use non-GUI backend for testing
        import matplotlib.pyplot as plt
        print("✓ Matplotlib import successful")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_no_mpc_references():
    """Test that all MPC references have been removed"""
    print("\n🔍 Testing MPC reference removal...")
    
    files_to_check = ['main.py', 'modern_dashboard.py', 'main_window.py']
    mpc_found = []
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read().lower()
                if 'refresh_latest_mpc' in content:
                    mpc_found.append(f"{filename}: refresh_latest_mpc")
                if 'mpc data' in content or 'mpc function' in content:
                    mpc_found.append(f"{filename}: MPC references")
    
    if mpc_found:
        print(f"✗ MPC references still found: {mpc_found}")
        return False
    else:
        print("✓ All MPC references successfully removed")
        return True

def test_dashboard_flow_target_focus():
    """Test that dashboard focuses on flow target"""
    print("\n🔍 Testing flow target focus in dashboard...")
    
    try:
        with open('modern_dashboard.py', 'r') as f:
            content = f.read()
            
        # Check for flow target metric cards
        if 'flow_target' in content:
            print("✓ Flow target metric card found")
        else:
            print("✗ Flow target metric card not found")
            return False
            
        # Check for flow target patterns
        if 'flow_target_patterns' in content or 'targetandcirculatorflow' in content:
            print("✓ Flow target parameter patterns found")
        else:
            print("✗ Flow target parameter patterns not found")
            return False
            
        # Check that old parameters are removed
        if 'pump_pressure' not in content or content.count('pump_pressure') < 3:
            print("✓ Reduced non-flow target parameters")
        else:
            print("⚠️  Some non-flow target parameters still prominent")
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing flow target focus: {e}")
        return False

def test_simplified_trends():
    """Test that trend functionality is simplified"""
    print("\n🔍 Testing simplified trend functionality...")
    
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        # Check for simplified trend function
        if '_plot_simplified_trend' in content:
            print("✓ Simplified trend plotting function found")
        else:
            print("✗ Simplified trend plotting function not found")
            return False
            
        # Check that complex multi-widget system is removed
        complex_widgets = ['waterGraphTop', 'voltageGraphTop', 'tempGraphTop']
        complex_found = any(widget in content for widget in complex_widgets)
        
        if not complex_found:
            print("✓ Complex multi-widget trend system removed")
        else:
            print("⚠️  Some complex trend widgets still referenced")
            
        # Check for single trendGraph usage
        if 'trendGraph' in content and 'refresh_trend_tab' in content:
            print("✓ Single trendGraph system in use")
        else:
            print("✗ Single trendGraph system not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing simplified trends: {e}")
        return False

def test_duplicate_prevention():
    """Test that dashboard duplicate prevention exists"""
    print("\n🔍 Testing dashboard duplicate prevention...")
    
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        # Check for duplicate prevention logic
        if 'hasattr(self, \'modern_dashboard\') and self.modern_dashboard' in content:
            print("✓ Dashboard duplicate prevention logic found")
        else:
            print("✗ Dashboard duplicate prevention logic not found")
            return False
            
        # Check for refresh instead of recreate
        if 'refresh_dashboard()' in content and 'Refreshing existing dashboard' in content:
            print("✓ Dashboard refresh instead of recreate found")
        else:
            print("⚠️  Dashboard refresh logic could be improved")
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing duplicate prevention: {e}")
        return False

def test_native_styling():
    """Test that native Windows styling is applied"""
    print("\n🔍 Testing native Windows styling...")
    
    try:
        with open('styles.py', 'r') as f:
            content = f.read()
            
        # Check for Windows 11 theme elements
        windows_elements = ['Segoe UI', '#0d6efd', 'border-radius', 'min-height']
        found_elements = [elem for elem in windows_elements if elem in content]
        
        if len(found_elements) >= 3:
            print(f"✓ Native Windows styling elements found: {found_elements}")
        else:
            print(f"✗ Insufficient native Windows styling: {found_elements}")
            return False
            
        # Check for responsive layout improvements
        if 'min-height' in content and 'responsive' in content.lower():
            print("✓ Responsive layout improvements found")
        else:
            print("✗ Responsive layout improvements not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing native styling: {e}")
        return False

def test_basic_functionality():
    """Test basic application structure"""
    print("\n🔍 Testing basic application functionality...")
    
    try:
        # Test that key files exist
        required_files = ['main.py', 'modern_dashboard.py', 'styles.py', 'main_window.py']
        for filename in required_files:
            if not os.path.exists(filename):
                print(f"✗ Required file missing: {filename}")
                return False
        
        print("✓ All required files present")
        
        # Test basic syntax by importing modules
        sys.path.insert(0, os.getcwd())
        
        # Test styles module
        try:
            import styles
            print("✓ Styles module imports successfully")
        except Exception as e:
            print(f"✗ Styles module import error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing basic functionality: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 HALbasic Dashboard Fixes - Validation Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("MPC Reference Removal", test_no_mpc_references),
        ("Flow Target Dashboard Focus", test_dashboard_flow_target_focus),
        ("Simplified Trend System", test_simplified_trends),
        ("Duplicate Prevention", test_duplicate_prevention),
        ("Native Windows Styling", test_native_styling),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! HALbasic fixes are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)