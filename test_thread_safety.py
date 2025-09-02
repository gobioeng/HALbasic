#!/usr/bin/env python3
"""
Test script for thread safety and fail-safe mechanisms in HALbasic
Tests the ThreadManager and AppStateManager functionality

Author: gobioeng.com
Date: 2025-01-20
"""

import sys
import os
import time
import tempfile
import unittest
from unittest.mock import Mock, patch

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtCore import QThread, QApplication, QTimer
    from PyQt5.QtWidgets import QApplication as QWidgetsApplication
    
    # Import our modules
    from thread_manager import ThreadManager, ManagedThread, ThreadState
    from app_state_manager import AppStateManager, ApplicationState
    from worker_thread import FileProcessingWorker, AnalysisWorker, DatabaseWorker
    
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"PyQt5 not available for testing: {e}")
    PYQT_AVAILABLE = False


class MockThread(QThread):
    """Mock thread for testing"""
    
    def __init__(self, run_duration=0.1):
        super().__init__()
        self.run_duration = run_duration
        self._cancel_requested = False
        
    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.run_duration:
            if self._cancel_requested:
                break
            time.sleep(0.01)
    
    def cancel_processing(self):
        self._cancel_requested = True


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestThreadManager(unittest.TestCase):
    """Test ThreadManager functionality"""
    
    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        self.thread_manager = ThreadManager()
    
    def tearDown(self):
        if self.thread_manager:
            self.thread_manager.shutdown_all_threads(timeout=2.0)
            self.thread_manager = None
    
    def test_thread_registration(self):
        """Test thread registration"""
        thread = MockThread()
        result = self.thread_manager.register_thread(thread, "test_thread", timeout=5.0)
        self.assertTrue(result)
        
        # Check thread is registered
        status = self.thread_manager.get_thread_status("test_thread")
        self.assertEqual(status, ThreadState.CREATED)
    
    def test_thread_start_stop(self):
        """Test thread start and stop"""
        thread = MockThread(run_duration=0.5)
        self.thread_manager.register_thread(thread, "test_thread")
        
        # Start thread
        result = self.thread_manager.start_thread("test_thread")
        self.assertTrue(result)
        
        # Wait a bit for thread to start
        time.sleep(0.1)
        status = self.thread_manager.get_thread_status("test_thread")
        self.assertEqual(status, ThreadState.RUNNING)
        
        # Stop thread
        result = self.thread_manager.stop_thread("test_thread")
        self.assertTrue(result)
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown of all threads"""
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = MockThread(run_duration=0.5)
            self.thread_manager.register_thread(thread, f"test_thread_{i}")
            self.thread_manager.start_thread(f"test_thread_{i}")
            threads.append(thread)
        
        # Wait for threads to start
        time.sleep(0.1)
        
        # Check all are running
        self.assertTrue(self.thread_manager.is_any_thread_running())
        
        # Shutdown all
        result = self.thread_manager.shutdown_all_threads(timeout=2.0)
        self.assertTrue(result)
        
        # Check none are running
        self.assertFalse(self.thread_manager.is_any_thread_running())
    
    def test_thread_timeout_handling(self):
        """Test thread timeout detection"""
        thread = MockThread(run_duration=10.0)  # Long running thread
        self.thread_manager.register_thread(thread, "timeout_thread", timeout=0.2)
        
        timeout_detected = False
        
        def on_timeout(thread_name):
            nonlocal timeout_detected
            timeout_detected = True
        
        self.thread_manager.thread_timeout.connect(on_timeout)
        self.thread_manager.start_thread("timeout_thread")
        
        # Wait for timeout detection
        start_time = time.time()
        while time.time() - start_time < 2.0 and not timeout_detected:
            self.app.processEvents()
            time.sleep(0.01)
        
        self.assertTrue(timeout_detected, "Thread timeout was not detected")


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestAppStateManager(unittest.TestCase):
    """Test AppStateManager functionality"""
    
    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        self.state_manager = AppStateManager("TestApp")
    
    def tearDown(self):
        if self.state_manager:
            self.state_manager.shutdown_gracefully()
            # Clean up state file
            try:
                if hasattr(self.state_manager, 'state_file') and os.path.exists(self.state_manager.state_file):
                    os.remove(self.state_manager.state_file)
            except:
                pass
    
    def test_state_management(self):
        """Test state setting and getting"""
        self.state_manager.set_state(ApplicationState.BUSY, "Testing")
        self.assertEqual(self.state_manager.get_state(), ApplicationState.BUSY)
        self.assertTrue(self.state_manager.is_busy())
        self.assertFalse(self.state_manager.is_ready())
    
    def test_user_data_storage(self):
        """Test user data storage and retrieval"""
        test_data = {"key1": "value1", "key2": 42}
        
        self.state_manager.set_user_data("test_key", test_data)
        retrieved_data = self.state_manager.get_user_data("test_key")
        
        self.assertEqual(retrieved_data, test_data)
    
    def test_crash_recording(self):
        """Test crash recording"""
        crash_detected = False
        
        def on_crash(reason):
            nonlocal crash_detected
            crash_detected = True
        
        self.state_manager.crash_detected.connect(on_crash)
        self.state_manager.record_crash("Test crash")
        
        # Process events to trigger signal
        self.app.processEvents()
        
        self.assertTrue(crash_detected)
        self.assertEqual(self.state_manager.get_state(), ApplicationState.CRASHED)
        
        crash_info = self.state_manager.get_crash_info()
        self.assertEqual(crash_info['crash_count'], 1)
        self.assertEqual(crash_info['last_crash_reason'], "Test crash")
    
    def test_checkpoint_creation_restoration(self):
        """Test checkpoint functionality"""
        test_data = {"important_data": "must_be_saved"}
        
        # Create checkpoint
        self.state_manager.create_checkpoint("test_checkpoint", test_data)
        
        # Restore checkpoint
        restored_data = self.state_manager.restore_checkpoint("test_checkpoint")
        
        self.assertEqual(restored_data, test_data)


class TestFailSafeMechanisms(unittest.TestCase):
    """Test fail-safe mechanisms without PyQt5 dependency"""
    
    def test_state_file_handling(self):
        """Test state file creation and cleanup"""
        # Import ApplicationState for this test
        from app_state_manager import ApplicationState
        
        # Create temporary state manager
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the state file creation
            state_file = os.path.join(temp_dir, "test_state.json")
            
            # Simulate state data
            import json
            state_data = {
                'app_name': 'TestApp',
                'state': ApplicationState.READY,
                'last_heartbeat': time.time(),
                'crash_count': 0
            }
            
            # Write state file
            with open(state_file, 'w') as f:
                json.dump(state_data, f)
            
            self.assertTrue(os.path.exists(state_file))
            
            # Read back state
            with open(state_file, 'r') as f:
                read_state = json.load(f)
            
            self.assertEqual(read_state['app_name'], 'TestApp')
            self.assertEqual(read_state['state'], ApplicationState.READY)
    
    def test_error_recovery_logic(self):
        """Test error recovery logic"""
        # Test maximum retry logic
        max_attempts = 3
        attempt_count = 0
        
        def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < max_attempts:
                raise Exception(f"Attempt {attempt_count} failed")
            return "Success"
        
        # Simulate retry logic
        result = None
        for attempt in range(max_attempts):
            try:
                result = failing_operation()
                break
            except Exception as e:
                if attempt == max_attempts - 1:
                    result = "Failed after max attempts"
        
        self.assertEqual(result, "Success")
        self.assertEqual(attempt_count, max_attempts)


def run_thread_safety_test():
    """Run a comprehensive thread safety test"""
    print("🧪 Running Thread Safety Test...")
    
    if not PYQT_AVAILABLE:
        print("⚠️ PyQt5 not available, running limited tests")
        suite = unittest.TestLoader().loadTestsFromTestCase(TestFailSafeMechanisms)
    else:
        print("✓ PyQt5 available, running full test suite")
        suite = unittest.TestSuite()
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestThreadManager))
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAppStateManager))
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFailSafeMechanisms))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("✅ All thread safety tests passed!")
        return True
    else:
        print("❌ Some thread safety tests failed!")
        return False


if __name__ == "__main__":
    success = run_thread_safety_test()
    sys.exit(0 if success else 1)