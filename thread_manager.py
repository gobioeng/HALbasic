"""
Professional Thread Manager for HALbasic
Provides fail-safe thread lifecycle management and recovery mechanisms

Author: gobioeng.com
Date: 2025-01-20
"""

import time
import threading
from typing import Dict, List, Optional, Callable
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, QMutex, QMutexLocker
import logging


class ThreadState:
    """Thread state enumeration"""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    FINISHING = "finishing"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    ERROR = "error"
    TIMEOUT = "timeout"


class ManagedThread:
    """Wrapper for QThread with enhanced monitoring and control"""
    
    def __init__(self, thread: QThread, name: str, timeout: float = 30.0):
        self.thread = thread
        self.name = name
        self.timeout = timeout
        self.state = ThreadState.CREATED
        self.start_time = None
        self.error_message = None
        self.cleanup_callbacks: List[Callable] = []
        self.mutex = QMutex()
        
    def add_cleanup_callback(self, callback: Callable):
        """Add cleanup callback to be called when thread finishes"""
        with QMutexLocker(self.mutex):
            self.cleanup_callbacks.append(callback)
    
    def set_state(self, state: str):
        """Thread-safe state setter"""
        with QMutexLocker(self.mutex):
            self.state = state
            if state == ThreadState.STARTING:
                self.start_time = time.time()
    
    def get_state(self) -> str:
        """Thread-safe state getter"""
        with QMutexLocker(self.mutex):
            return self.state
    
    def is_timed_out(self) -> bool:
        """Check if thread has exceeded timeout"""
        with QMutexLocker(self.mutex):
            if self.start_time and self.state == ThreadState.RUNNING:
                return time.time() - self.start_time > self.timeout
            return False
    
    def execute_cleanup(self):
        """Execute all cleanup callbacks"""
        with QMutexLocker(self.mutex):
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    logging.error(f"Error in cleanup callback for thread {self.name}: {e}")


class ThreadManager(QObject):
    """
    Professional Thread Manager for HALbasic
    Provides centralized thread lifecycle management with fail-safe mechanisms
    """
    
    # Signals
    thread_started = pyqtSignal(str)  # thread_name
    thread_finished = pyqtSignal(str)  # thread_name
    thread_error = pyqtSignal(str, str)  # thread_name, error_message
    thread_timeout = pyqtSignal(str)  # thread_name
    all_threads_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.threads: Dict[str, ManagedThread] = {}
        self.mutex = QMutex()
        self.shutdown_requested = False
        self.max_shutdown_wait = 10.0  # Maximum time to wait for shutdown
        
        # Setup monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_threads)
        self.monitor_timer.start(1000)  # Check every second
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def register_thread(self, thread: QThread, name: str, timeout: float = 30.0) -> bool:
        """
        Register a thread for management
        
        Args:
            thread: QThread instance to manage
            name: Unique name for the thread
            timeout: Maximum runtime in seconds
            
        Returns:
            bool: True if successfully registered
        """
        try:
            with QMutexLocker(self.mutex):
                if name in self.threads:
                    self.logger.warning(f"Thread {name} already registered, replacing")
                
                managed_thread = ManagedThread(thread, name, timeout)
                self.threads[name] = managed_thread
                
                # Connect thread signals for monitoring
                thread.started.connect(lambda: self._on_thread_started(name))
                thread.finished.connect(lambda: self._on_thread_finished(name))
                
                # Add error handling if available
                if hasattr(thread, 'error'):
                    thread.error.connect(lambda msg: self._on_thread_error(name, msg))
                
                self.logger.info(f"Thread {name} registered successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to register thread {name}: {e}")
            return False
    
    def start_thread(self, name: str) -> bool:
        """
        Start a managed thread
        
        Args:
            name: Name of the thread to start
            
        Returns:
            bool: True if successfully started
        """
        try:
            with QMutexLocker(self.mutex):
                if name not in self.threads:
                    self.logger.error(f"Thread {name} not registered")
                    return False
                
                managed_thread = self.threads[name]
                if managed_thread.thread.isRunning():
                    self.logger.warning(f"Thread {name} is already running")
                    return False
                
                managed_thread.set_state(ThreadState.STARTING)
                managed_thread.thread.start()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start thread {name}: {e}")
            return False
    
    def stop_thread(self, name: str, force: bool = False) -> bool:
        """
        Stop a managed thread gracefully
        
        Args:
            name: Name of the thread to stop
            force: If True, use terminate() as last resort
            
        Returns:
            bool: True if successfully stopped
        """
        try:
            with QMutexLocker(self.mutex):
                if name not in self.threads:
                    self.logger.warning(f"Thread {name} not found for stopping")
                    return True
                
                managed_thread = self.threads[name]
                thread = managed_thread.thread
                
                if not thread.isRunning():
                    self.logger.info(f"Thread {name} is not running")
                    return True
                
                managed_thread.set_state(ThreadState.FINISHING)
                
                # Try graceful cancellation first
                if hasattr(thread, 'cancel_processing'):
                    thread.cancel_processing()
                elif hasattr(thread, 'cancel_analysis'):
                    thread.cancel_analysis()
                elif hasattr(thread, '_cancel_requested'):
                    thread._cancel_requested = True
                
                # Wait for graceful shutdown
                if thread.wait(3000):  # Wait 3 seconds
                    self.logger.info(f"Thread {name} stopped gracefully")
                    return True
                
                # Force termination if requested and graceful failed
                if force:
                    self.logger.warning(f"Force terminating thread {name}")
                    thread.terminate()
                    if thread.wait(2000):  # Wait 2 more seconds
                        self.logger.info(f"Thread {name} force terminated")
                        return True
                    else:
                        self.logger.error(f"Thread {name} failed to terminate")
                        return False
                
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping thread {name}: {e}")
            return False
    
    def get_thread_status(self, name: str) -> Optional[str]:
        """Get the current status of a thread"""
        with QMutexLocker(self.mutex):
            if name in self.threads:
                return self.threads[name].get_state()
            return None
    
    def get_all_thread_status(self) -> Dict[str, str]:
        """Get status of all threads"""
        with QMutexLocker(self.mutex):
            return {name: mt.get_state() for name, mt in self.threads.items()}
    
    def is_any_thread_running(self) -> bool:
        """Check if any threads are running"""
        with QMutexLocker(self.mutex):
            return any(mt.thread.isRunning() for mt in self.threads.values())
    
    def shutdown_all_threads(self, timeout: float = None) -> bool:
        """
        Shutdown all threads gracefully
        
        Args:
            timeout: Maximum time to wait for shutdown
            
        Returns:
            bool: True if all threads stopped within timeout
        """
        if timeout is None:
            timeout = self.max_shutdown_wait
            
        self.logger.info("Initiating graceful shutdown of all threads")
        self.shutdown_requested = True
        
        try:
            # Get list of running threads
            with QMutexLocker(self.mutex):
                running_threads = [
                    name for name, mt in self.threads.items()
                    if mt.thread.isRunning()
                ]
            
            if not running_threads:
                self.logger.info("No threads running, shutdown complete")
                self.all_threads_finished.emit()
                return True
            
            # Request graceful shutdown for all threads
            for name in running_threads:
                self.stop_thread(name, force=False)
            
            # Wait for all threads to finish
            start_time = time.time()
            while time.time() - start_time < timeout:
                if not self.is_any_thread_running():
                    self.logger.info("All threads shutdown gracefully")
                    self.all_threads_finished.emit()
                    return True
                time.sleep(0.1)
            
            # Force shutdown remaining threads
            self.logger.warning("Timeout reached, forcing shutdown of remaining threads")
            with QMutexLocker(self.mutex):
                remaining_threads = [
                    name for name, mt in self.threads.items()
                    if mt.thread.isRunning()
                ]
            
            for name in remaining_threads:
                self.stop_thread(name, force=True)
            
            # Final check
            final_wait = 3.0
            start_time = time.time()
            while time.time() - start_time < final_wait:
                if not self.is_any_thread_running():
                    self.logger.info("All threads shutdown (some forced)")
                    self.all_threads_finished.emit()
                    return True
                time.sleep(0.1)
            
            self.logger.error("Failed to shutdown all threads")
            return False
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False
    
    def cleanup_finished_threads(self):
        """Remove finished threads from management"""
        with QMutexLocker(self.mutex):
            finished_threads = []
            for name, managed_thread in self.threads.items():
                if not managed_thread.thread.isRunning():
                    finished_threads.append(name)
                    # Execute cleanup callbacks
                    managed_thread.execute_cleanup()
            
            for name in finished_threads:
                del self.threads[name]
                self.logger.info(f"Cleaned up finished thread: {name}")
    
    def add_thread_cleanup_callback(self, thread_name: str, callback: Callable):
        """Add cleanup callback for a specific thread"""
        with QMutexLocker(self.mutex):
            if thread_name in self.threads:
                self.threads[thread_name].add_cleanup_callback(callback)
    
    def _monitor_threads(self):
        """Monitor threads for timeouts and issues"""
        if self.shutdown_requested:
            return
            
        try:
            with QMutexLocker(self.mutex):
                for name, managed_thread in list(self.threads.items()):
                    # Check for timeouts
                    if managed_thread.is_timed_out():
                        self.logger.warning(f"Thread {name} has timed out")
                        managed_thread.set_state(ThreadState.TIMEOUT)
                        self.thread_timeout.emit(name)
                        
                        # Attempt to stop timed out thread
                        try:
                            self.stop_thread(name, force=True)
                        except Exception as e:
                            self.logger.error(f"Error stopping timed out thread {name}: {e}")
                    
                    # Check for zombie threads
                    elif (managed_thread.get_state() == ThreadState.RUNNING and 
                          not managed_thread.thread.isRunning()):
                        self.logger.warning(f"Zombie thread detected: {name}")
                        managed_thread.set_state(ThreadState.ERROR)
                        self._on_thread_error(name, "Thread became zombie")
                        
        except Exception as e:
            self.logger.error(f"Error in thread monitoring: {e}")
    
    def _on_thread_started(self, name: str):
        """Handle thread started event"""
        with QMutexLocker(self.mutex):
            if name in self.threads:
                self.threads[name].set_state(ThreadState.RUNNING)
        
        self.logger.info(f"Thread {name} started")
        self.thread_started.emit(name)
    
    def _on_thread_finished(self, name: str):
        """Handle thread finished event"""
        with QMutexLocker(self.mutex):
            if name in self.threads:
                managed_thread = self.threads[name]
                if managed_thread.get_state() != ThreadState.TIMEOUT:
                    managed_thread.set_state(ThreadState.FINISHED)
        
        self.logger.info(f"Thread {name} finished")
        self.thread_finished.emit(name)
        
        # Schedule cleanup
        QTimer.singleShot(1000, self.cleanup_finished_threads)
    
    def _on_thread_error(self, name: str, error_message: str):
        """Handle thread error event"""
        with QMutexLocker(self.mutex):
            if name in self.threads:
                self.threads[name].set_state(ThreadState.ERROR)
                self.threads[name].error_message = error_message
        
        self.logger.error(f"Thread {name} error: {error_message}")
        self.thread_error.emit(name, error_message)
    
    def get_statistics(self) -> Dict:
        """Get thread manager statistics"""
        with QMutexLocker(self.mutex):
            stats = {
                'total_threads': len(self.threads),
                'running_threads': sum(1 for mt in self.threads.values() if mt.thread.isRunning()),
                'thread_states': {}
            }
            
            for state in [ThreadState.CREATED, ThreadState.STARTING, ThreadState.RUNNING,
                         ThreadState.FINISHING, ThreadState.FINISHED, ThreadState.CANCELLED,
                         ThreadState.ERROR, ThreadState.TIMEOUT]:
                count = sum(1 for mt in self.threads.values() if mt.get_state() == state)
                if count > 0:
                    stats['thread_states'][state] = count
            
            return stats
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            if hasattr(self, 'monitor_timer'):
                self.monitor_timer.stop()
            self.shutdown_all_threads(timeout=5.0)
        except:
            pass