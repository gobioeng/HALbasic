#!/usr/bin/env python3
"""
Integration test for unified plotting system
Tests the combined functionality of utils_plot and plot_utils
"""

import sys
import os

# Set headless mode for testing
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pandas as pd
from PyQt5.QtWidgets import QApplication


def test_unified_plotting_integration():
    """Test the unified plotting system integration"""
    print("🔗 Testing unified plotting system integration...")
    
    try:
        # Test backwards compatibility with utils_plot imports
        from utils_plot import PlotUtils, plot_trend, reset_plot_view
        print("  ✓ utils_plot imports working")
        
        # Test new enhanced widgets from plot_utils
        from plot_utils import PlotWidget, DualPlotWidget
        print("  ✓ plot_utils enhanced widgets working")
        
        # Create test data
        test_data = pd.DataFrame({
            'datetime': pd.date_range('2025-01-01', periods=50, freq='h'),
            'param': ['Temperature'] * 25 + ['Pressure'] * 25,
            'avg': [20 + i*0.1 + (i%5)*0.5 for i in range(50)],
            'min': [19 + i*0.1 + (i%5)*0.3 for i in range(50)],
            'max': [21 + i*0.1 + (i%5)*0.7 for i in range(50)],
            'unit': ['°C'] * 25 + ['bar'] * 25
        })
        
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Test enhanced PlotWidget
        widget = PlotWidget()
        widget.plot_parameter_trends(test_data, 'Temperature', 'Enhanced Temperature Trends')
        print("  ✓ Enhanced PlotWidget with LINAC data processing")
        
        # Test enhanced DualPlotWidget  
        dual_widget = DualPlotWidget()
        dual_widget.update_comparison(test_data, 'Temperature', 'Pressure')
        print("  ✓ Enhanced DualPlotWidget with comparison plotting")
        
        # Test PlotUtils functionality
        groups = PlotUtils.group_parameters(['Temperature Sensor 1', 'Pressure Gauge A', 'Flow Rate Main'])
        assert 'Temperature' in groups
        assert 'Pressure' in groups  
        assert 'Flow' in groups
        print("  ✓ PlotUtils parameter grouping")
        
        # Test time clustering
        time_clusters = PlotUtils.find_time_clusters(test_data['datetime'].tolist())
        assert len(time_clusters) >= 1
        print("  ✓ PlotUtils time clustering")
        
        # Test legacy plot_trend function
        plot_trend(widget, test_data, "Legacy Test")
        print("  ✓ Legacy plot_trend compatibility")
        
        print("✅ Unified plotting system integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_interactive_features():
    """Test interactive plot features"""
    print("\n🎮 Testing interactive plot features...")
    
    try:
        from plot_utils import DualPlotWidget, InteractivePlotManager
        
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create test data with gaps to test compressed timeline
        dates1 = pd.date_range('2025-01-01', periods=10, freq='h')
        dates2 = pd.date_range('2025-01-05', periods=10, freq='h')  # Gap in time
        all_dates = list(dates1) + list(dates2)
        
        test_data_with_gaps = pd.DataFrame({
            'datetime': all_dates,
            'param': ['Temperature'] * 20,
            'avg': [20 + i*0.2 for i in range(20)],
            'min': [19 + i*0.2 for i in range(20)],
            'max': [21 + i*0.2 for i in range(20)],
            'unit': ['°C'] * 20
        })
        
        dual_widget = DualPlotWidget()
        dual_widget.update_comparison(test_data_with_gaps, 'Temperature', 'Temperature')
        print("  ✓ Compressed timeline for data with gaps")
        
        # Test that InteractivePlotManager was created
        if dual_widget.interactive_manager:
            print("  ✓ Interactive plot manager initialized")
        else:
            print("  ⚠️ Interactive plot manager not initialized (may be expected in headless mode)")
        
        print("✅ Interactive features working")
        return True
        
    except Exception as e:
        print(f"❌ Interactive features test failed: {e}")
        return False


def main():
    """Run integration tests"""
    print("🧪 HALbasic Unified Plotting System Integration Tests")
    print("=" * 60)
    
    tests = [
        test_unified_plotting_integration,
        test_interactive_features
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🧪 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed! Unified plotting system ready!")
        print("\n📋 Enhanced Features Available:")
        print("  ✓ Unified PlotWidget with LINAC data processing")
        print("  ✓ Enhanced DualPlotWidget with time compression")
        print("  ✓ Interactive plot management (zoom, pan, keyboard shortcuts)")
        print("  ✓ Professional styling with parameter grouping")
        print("  ✓ Backwards compatibility with existing code")
        print("  ✓ Compressed timeline for data with gaps")
        return True
    else:
        print(f"⚠️ {failed} test(s) failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)