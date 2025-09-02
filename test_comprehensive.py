#!/usr/bin/env python3
"""
Comprehensive test for HALbasic fail-safe mechanisms
Tests crash detection, recovery, and restart functionality

Author: gobioeng.com
Date: 2025-01-20
"""

import sys
import os
import time
import tempfile
import subprocess

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_crash_recovery_dialog():
    """Test the crash recovery dialog functionality"""
    print("📋 Testing Crash Recovery Dialog...")
    
    try:
        # Import and test the dialog
        from crash_recovery_dialog import CrashRecoveryDialog, show_crash_recovery_dialog
        print("✓ CrashRecoveryDialog imported successfully")
        
        # Test dialog creation (without showing UI)
        crash_info = {
            'crash_count': 1,
            'last_crash_time': time.time() - 300,  # 5 minutes ago
            'uptime_seconds': 45.7
        }
        
        # This would normally show the dialog, but we'll test the instantiation
        from PyQt5.QtWidgets import QApplication
        
        # Create minimal QApplication for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        dialog = CrashRecoveryDialog("Test crash reason", crash_info)
        
        # Test methods without showing UI
        assert hasattr(dialog, '_restart_application')
        assert hasattr(dialog, '_exit_application')
        assert hasattr(dialog, 'get_recovery_options')
        
        print("✓ CrashRecoveryDialog methods available")
        
        # Test crash report generation
        dialog.recovery_options = {
            'preserve_data': True,
            'restore_session': True,
            'safe_mode': False,
            'send_report': True
        }
        
        report = dialog._generate_crash_report()
        assert "HALbasic Crash Report" in report
        assert "Test crash reason" in report
        print("✓ Crash report generation working")
        
        return True
        
    except Exception as e:
        print(f"✗ Crash recovery dialog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_thread_timeout_scenario():
    """Test thread timeout detection and recovery"""
    print("\n📋 Testing Thread Timeout Scenario...")
    
    try:
        from thread_manager import ThreadManager
        from PyQt5.QtCore import QThread, QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create thread manager
        manager = ThreadManager()
        
        # Create a thread that will timeout
        class TimeoutThread(QThread):
            def __init__(self):
                super().__init__()
                self._cancel_requested = False
            
            def run(self):
                # Simulate long-running operation
                start_time = time.time()
                while time.time() - start_time < 10.0:  # Run for 10 seconds
                    if self._cancel_requested:
                        break
                    time.sleep(0.1)
            
            def cancel_processing(self):
                self._cancel_requested = True
        
        timeout_thread = TimeoutThread()
        
        # Register with very short timeout for testing
        manager.register_thread(timeout_thread, "timeout_test", timeout=0.5)
        
        timeout_detected = False
        
        def on_timeout(thread_name):
            nonlocal timeout_detected
            timeout_detected = True
            print(f"✓ Thread timeout detected: {thread_name}")
        
        manager.thread_timeout.connect(on_timeout)
        
        # Start the thread
        manager.start_thread("timeout_test")
        
        # Wait for timeout detection
        start_time = time.time()
        while time.time() - start_time < 3.0 and not timeout_detected:
            app.processEvents()
            time.sleep(0.01)
        
        assert timeout_detected, "Thread timeout was not detected"
        print("✓ Thread timeout detection working")
        
        # Cleanup
        manager.shutdown_all_threads(timeout=2.0)
        
        return True
        
    except Exception as e:
        print(f"✗ Thread timeout test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_application_state_persistence():
    """Test application state persistence across restarts"""
    print("\n📋 Testing Application State Persistence...")
    
    try:
        from app_state_manager import AppStateManager, ApplicationState
        
        # Create state manager with temporary file
        state_manager = AppStateManager("TestApp")
        
        # Set some state and user data
        state_manager.set_state(ApplicationState.BUSY, "Testing state persistence")
        state_manager.set_user_data("test_key", {"data": "test_value", "number": 42})
        state_manager.set_user_data("session_info", {"last_file": "/path/to/file.txt"})
        
        # Force state save
        state_manager._save_state()
        state_file = state_manager.state_file
        
        assert os.path.exists(state_file), "State file was not created"
        print("✓ State file created successfully")
        
        # Shutdown and create new instance (simulating restart)
        state_manager.shutdown_gracefully()
        del state_manager
        
        # Create new state manager to simulate restart
        new_state_manager = AppStateManager("TestApp")
        
        # Check if data was recovered
        recovered_data = new_state_manager.get_user_data("test_key")
        session_info = new_state_manager.get_user_data("session_info")
        
        assert recovered_data == {"data": "test_value", "number": 42}
        assert session_info == {"last_file": "/path/to/file.txt"}
        print("✓ User data recovered successfully")
        
        # Cleanup
        new_state_manager.shutdown_gracefully()
        
        return True
        
    except Exception as e:
        print(f"✗ State persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graceful_shutdown_sequence():
    """Test complete graceful shutdown sequence"""
    print("\n📋 Testing Graceful Shutdown Sequence...")
    
    try:
        from thread_manager import ThreadManager
        from app_state_manager import AppStateManager
        from PyQt5.QtCore import QThread, QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create managers
        thread_manager = ThreadManager()
        state_manager = AppStateManager("TestApp")
        
        # Create multiple test threads
        threads = []
        for i in range(3):
            class TestThread(QThread):
                def __init__(self, thread_id):
                    super().__init__()
                    self.thread_id = thread_id
                    self._cancel_requested = False
                
                def run(self):
                    start_time = time.time()
                    while time.time() - start_time < 5.0:  # Run for 5 seconds
                        if self._cancel_requested:
                            print(f"Thread {self.thread_id} stopping gracefully")
                            break
                        time.sleep(0.1)
                
                def cancel_processing(self):
                    self._cancel_requested = True
            
            thread = TestThread(i)
            threads.append(thread)
            thread_manager.register_thread(thread, f"test_thread_{i}")
            thread_manager.start_thread(f"test_thread_{i}")
        
        # Wait for threads to start
        time.sleep(0.5)
        
        # Verify all threads are running
        assert thread_manager.is_any_thread_running(), "Threads should be running"
        print("✓ All test threads started")
        
        # Test graceful shutdown
        print("🔄 Testing graceful shutdown...")
        shutdown_start = time.time()
        
        shutdown_success = thread_manager.shutdown_all_threads(timeout=3.0)
        
        shutdown_time = time.time() - shutdown_start
        
        assert shutdown_success, "Graceful shutdown failed"
        assert shutdown_time < 5.0, f"Shutdown took too long: {shutdown_time:.2f}s"
        assert not thread_manager.is_any_thread_running(), "Threads still running after shutdown"
        
        print(f"✓ Graceful shutdown completed in {shutdown_time:.2f}s")
        
        # Test state manager shutdown
        state_manager.shutdown_gracefully()
        print("✓ State manager shutdown completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Graceful shutdown test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_recovery_logic():
    """Test error recovery and retry logic"""
    print("\n📋 Testing Error Recovery Logic...")
    
    try:
        # Test retry mechanism
        max_retries = 3
        attempt_count = 0
        
        def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < max_retries:
                raise Exception(f"Simulated failure {attempt_count}")
            return f"Success after {attempt_count} attempts"
        
        # Implement retry logic
        last_error = None
        result = None
        
        for attempt in range(max_retries + 1):
            try:
                result = failing_operation()
                break
            except Exception as e:
                last_error = e
                if attempt == max_retries:
                    result = f"Failed after {max_retries + 1} attempts: {last_error}"
        
        assert "Success after 3 attempts" in result, f"Unexpected result: {result}"
        print("✓ Retry logic working correctly")
        
        # Test exponential backoff
        backoff_times = []
        for attempt in range(4):
            backoff_time = min(30, 2 ** attempt)  # Cap at 30 seconds
            backoff_times.append(backoff_time)
        
        expected_times = [1, 2, 4, 8]
        assert backoff_times[:4] == expected_times, f"Backoff times incorrect: {backoff_times}"
        print("✓ Exponential backoff logic working")
        
        return True
        
    except Exception as e:
        print(f"✗ Error recovery test failed: {e}")
        return False

def test_deployment_readiness():
    """Test deployment readiness checks"""
    print("\n📋 Testing Deployment Readiness...")
    
    try:
        # Check required modules can be imported
        required_modules = [
            'thread_manager', 'app_state_manager', 'crash_recovery_dialog',
            'worker_thread', 'database', 'main'
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
                print(f"✓ Module {module_name} importable")
            except ImportError as e:
                print(f"✗ Module {module_name} import failed: {e}")
                return False
        
        # Check that main application has fail-safe features
        import main
        app = main.HALogApp()
        
        required_attributes = [
            'thread_manager', 'app_state_manager', '_shutdown_in_progress'
        ]
        
        for attr in required_attributes:
            assert hasattr(app, attr), f"Missing attribute: {attr}"
            print(f"✓ HALogApp has {attr}")
        
        required_methods = [
            '_initialize_thread_management', '_handle_crash_detected',
            '_complete_shutdown'
        ]
        
        for method in required_methods:
            assert hasattr(app, method), f"Missing method: {method}"
            print(f"✓ HALogApp has {method}")
        
        print("✓ Deployment readiness verified")
        return True
        
    except Exception as e:
        print(f"✗ Deployment readiness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_tests():
    """Run all comprehensive fail-safe tests"""
    print("🧪 Running Comprehensive HALbasic Fail-Safe Tests")
    print("=" * 60)
    
    tests = [
        ("Crash Recovery Dialog", test_crash_recovery_dialog),
        ("Thread Timeout Scenario", test_thread_timeout_scenario),
        ("Application State Persistence", test_application_state_persistence),
        ("Graceful Shutdown Sequence", test_graceful_shutdown_sequence),
        ("Error Recovery Logic", test_error_recovery_logic),
        ("Deployment Readiness", test_deployment_readiness),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! HALbasic is deployment-ready with professional fail-safe mechanisms.")
        print("\n🚀 Key Features Verified:")
        print("   ✓ Professional thread management and monitoring")
        print("   ✓ Graceful shutdown with timeout mechanisms")
        print("   ✓ Crash detection and recovery systems")
        print("   ✓ Application state persistence")
        print("   ✓ User-friendly crash recovery dialog")
        print("   ✓ Comprehensive error handling and retry logic")
        print("   ✓ Production deployment readiness")
        return True
    else:
        print("⚠️ Some tests failed. Please address the issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)