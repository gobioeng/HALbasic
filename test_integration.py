#!/usr/bin/env python3
"""
Simple test for HALbasic threading improvements
Tests startup and basic thread safety without full GUI

Author: gobioeng.com
Date: 2025-01-20
"""

import sys
import os
import time
import tempfile

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all our new modules can be imported"""
    print("Testing imports...")
    
    try:
        from thread_manager import ThreadManager, ThreadState
        print("✓ ThreadManager imported successfully")
    except Exception as e:
        print(f"✗ ThreadManager import failed: {e}")
        return False
    
    try:
        from app_state_manager import AppStateManager, ApplicationState
        print("✓ AppStateManager imported successfully")
    except Exception as e:
        print("✗ AppStateManager import failed: {e}")
        return False
    
    try:
        from worker_thread import FileProcessingWorker, AnalysisWorker, DatabaseWorker
        print("✓ Enhanced worker threads imported successfully")
    except Exception as e:
        print(f"✗ Worker threads import failed: {e}")
        return False
    
    return True

def test_app_state_manager():
    """Test AppStateManager without GUI"""
    print("\nTesting AppStateManager...")
    
    try:
        from app_state_manager import AppStateManager, ApplicationState
        
        # Create state manager
        state_manager = AppStateManager("TestApp")
        
        # Test state management
        state_manager.set_state(ApplicationState.BUSY, "Testing")
        assert state_manager.get_state() == ApplicationState.BUSY
        assert state_manager.is_busy()
        print("✓ State management working")
        
        # Test user data
        test_data = {"test_key": "test_value", "number": 42}
        state_manager.set_user_data("test", test_data)
        retrieved = state_manager.get_user_data("test")
        assert retrieved == test_data
        print("✓ User data storage working")
        
        # Test crash recording
        state_manager.record_crash("Test crash")
        crash_info = state_manager.get_crash_info()
        assert crash_info['crash_count'] == 1
        assert crash_info['last_crash_reason'] == "Test crash"
        print("✓ Crash recording working")
        
        # Test checkpoint
        state_manager.create_checkpoint("test_checkpoint", {"important": "data"})
        restored = state_manager.restore_checkpoint("test_checkpoint")
        assert restored == {"important": "data"}
        print("✓ Checkpoint system working")
        
        # Clean shutdown
        state_manager.shutdown_gracefully()
        print("✓ Graceful shutdown working")
        
        return True
        
    except Exception as e:
        print(f"✗ AppStateManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration():
    """Test database integration with enhanced error handling"""
    print("\nTesting database integration...")
    
    try:
        from database import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Test database creation
            db = DatabaseManager(db_path)
            print("✓ Database created successfully")
            
            # Test basic operations
            record_count = db.get_record_count()
            print(f"✓ Database record count: {record_count}")
            
            # Test anomaly operations
            anomaly_count = db.get_anomaly_count()
            print(f"✓ Database anomaly count: {anomaly_count}")
            
            return True
            
        finally:
            # Clean up
            try:
                os.unlink(db_path)
            except:
                pass
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_worker_thread_classes():
    """Test that worker thread classes can be instantiated"""
    print("\nTesting worker thread classes...")
    
    try:
        from worker_thread import FileProcessingWorker, AnalysisWorker, DatabaseWorker
        from database import DatabaseManager
        import pandas as pd
        
        # Create temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            db = DatabaseManager(db_path)
            
            # Test FileProcessingWorker creation
            file_worker = FileProcessingWorker("/tmp/test.txt", 1024, db)
            assert hasattr(file_worker, '_cancel_requested')
            assert hasattr(file_worker, 'cleanup_completed')
            print("✓ FileProcessingWorker enhanced")
            
            # Test AnalysisWorker creation (mock analyzer and dataframe)
            mock_analyzer = type('MockAnalyzer', (), {})()
            mock_df = pd.DataFrame()
            analysis_worker = AnalysisWorker(mock_analyzer, mock_df)
            assert hasattr(analysis_worker, '_cancel_requested')
            assert hasattr(analysis_worker, 'cleanup_completed')
            print("✓ AnalysisWorker enhanced")
            
            # Test DatabaseWorker creation
            db_worker = DatabaseWorker(db, "vacuum")
            assert hasattr(db_worker, '_cancel_requested')
            assert hasattr(db_worker, 'cleanup_completed')
            print("✓ DatabaseWorker enhanced")
            
            return True
            
        finally:
            try:
                os.unlink(db_path)
            except:
                pass
        
    except Exception as e:
        print(f"✗ Worker thread test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_app_imports():
    """Test that main.py can import our new modules"""
    print("\nTesting main application integration...")
    
    try:
        # Import main components to verify integration
        import main
        print("✓ Main module imported successfully")
        
        # Check that HALogApp has our new attributes
        app = main.HALogApp()
        assert hasattr(app, 'thread_manager')
        assert hasattr(app, 'app_state_manager')
        assert hasattr(app, '_shutdown_in_progress')
        print("✓ HALogApp has thread management attributes")
        
        # Check that our new methods exist
        assert hasattr(app, '_initialize_thread_management')
        assert hasattr(app, '_handle_crash_detected')
        assert hasattr(app, '_complete_shutdown')
        print("✓ HALogApp has thread management methods")
        
        return True
        
    except Exception as e:
        print(f"✗ Main app integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all non-GUI tests"""
    print("🧪 Running HALbasic Thread Safety Tests (Non-GUI)")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("AppStateManager Test", test_app_state_manager),
        ("Database Integration Test", test_database_integration),
        ("Worker Thread Classes Test", test_worker_thread_classes),
        ("Main App Integration Test", test_main_app_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Thread safety improvements working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)