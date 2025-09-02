"""
Application State Manager for HALbasic
Provides application state management, crash recovery, and fail-safe mechanisms

Author: gobioeng.com
Date: 2025-01-20
"""

import os
import json
import time
import logging
import tempfile
from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
import pickle


class ApplicationState:
    """Application state enumeration"""
    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    CRASHED = "crashed"


class AppStateManager(QObject):
    """
    Professional Application State Manager for HALbasic
    Provides state persistence, crash recovery, and fail-safe mechanisms
    """
    
    # Signals
    state_changed = pyqtSignal(str)  # new_state
    crash_detected = pyqtSignal(str)  # crash_reason
    recovery_completed = pyqtSignal(bool)  # success
    
    def __init__(self, app_name: str = "HALbasic", parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.current_state = ApplicationState.STARTING
        self.state_file = None
        self.heartbeat_timer = None
        self.logger = logging.getLogger(f"{__name__}.AppStateManager")
        
        # Configuration
        self.heartbeat_interval = 5000  # 5 seconds
        self.max_crash_recovery_attempts = 3
        self.crash_recovery_attempts = 0
        
        # State data
        self.state_data = {
            'app_name': app_name,
            'state': self.current_state,
            'last_heartbeat': time.time(),
            'start_time': time.time(),
            'crash_count': 0,
            'last_crash_time': None,
            'last_crash_reason': None,
            'recovery_attempts': 0,
            'user_data': {}
        }
        
        self._initialize_state_management()
    
    def _initialize_state_management(self):
        """Initialize state management system"""
        try:
            # Create state file path
            temp_dir = tempfile.gettempdir()
            self.state_file = os.path.join(temp_dir, f"{self.app_name}_state.json")
            
            # Check for previous crash
            self._check_for_previous_crash()
            
            # Setup heartbeat
            self._setup_heartbeat()
            
            # Update state to ready
            self.set_state(ApplicationState.READY)
            
            self.logger.info("Application state manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize state manager: {e}")
    
    def _check_for_previous_crash(self):
        """Check if the application crashed previously"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    previous_state = json.load(f)
                
                # Check if previous instance was running when it ended
                last_state = previous_state.get('state', '')
                if last_state in [ApplicationState.READY, ApplicationState.BUSY]:
                    # Previous instance didn't shut down cleanly
                    self.logger.warning("Previous application instance crashed")
                    
                    self.state_data['crash_count'] = previous_state.get('crash_count', 0) + 1
                    self.state_data['last_crash_time'] = time.time()
                    self.state_data['last_crash_reason'] = "Unclean shutdown detected"
                    
                    self.crash_detected.emit("Unclean shutdown detected")
                    
                    # Attempt recovery if within limits
                    if self.state_data['crash_count'] <= self.max_crash_recovery_attempts:
                        self._attempt_recovery(previous_state)
                    else:
                        self.logger.error("Maximum crash recovery attempts exceeded")
                else:
                    self.logger.info("Previous instance shutdown cleanly")
            
        except Exception as e:
            self.logger.error(f"Error checking for previous crash: {e}")
    
    def _attempt_recovery(self, previous_state: Dict):
        """Attempt to recover from previous crash"""
        try:
            self.logger.info("Attempting crash recovery")
            self.crash_recovery_attempts += 1
            
            # Restore user data if available
            user_data = previous_state.get('user_data', {})
            if user_data:
                self.state_data['user_data'] = user_data
                self.logger.info("Restored user data from previous session")
            
            # Emit recovery signal
            self.recovery_completed.emit(True)
            self.logger.info("Crash recovery completed successfully")
            
        except Exception as e:
            self.logger.error(f"Crash recovery failed: {e}")
            self.recovery_completed.emit(False)
    
    def _setup_heartbeat(self):
        """Setup heartbeat timer for crash detection"""
        try:
            self.heartbeat_timer = QTimer()
            self.heartbeat_timer.timeout.connect(self._heartbeat)
            self.heartbeat_timer.start(self.heartbeat_interval)
            self.logger.info("Heartbeat timer started")
            
        except Exception as e:
            self.logger.error(f"Failed to setup heartbeat: {e}")
    
    def _heartbeat(self):
        """Update heartbeat timestamp"""
        try:
            self.state_data['last_heartbeat'] = time.time()
            self._save_state()
            
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
    
    def _save_state(self):
        """Save current state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def set_state(self, new_state: str, reason: str = None):
        """
        Set application state
        
        Args:
            new_state: New application state
            reason: Optional reason for state change
        """
        try:
            old_state = self.current_state
            self.current_state = new_state
            self.state_data['state'] = new_state
            
            if reason:
                self.state_data.setdefault('state_reasons', []).append({
                    'timestamp': time.time(),
                    'from_state': old_state,
                    'to_state': new_state,
                    'reason': reason
                })
            
            self._save_state()
            self.state_changed.emit(new_state)
            
            self.logger.info(f"State changed: {old_state} -> {new_state}" + 
                           (f" ({reason})" if reason else ""))
            
        except Exception as e:
            self.logger.error(f"Failed to set state: {e}")
    
    def get_state(self) -> str:
        """Get current application state"""
        return self.current_state
    
    def is_busy(self) -> bool:
        """Check if application is busy"""
        return self.current_state == ApplicationState.BUSY
    
    def is_ready(self) -> bool:
        """Check if application is ready"""
        return self.current_state == ApplicationState.READY
    
    def set_user_data(self, key: str, value: Any):
        """
        Store user data for crash recovery
        
        Args:
            key: Data key
            value: Data value (must be JSON serializable)
        """
        try:
            self.state_data['user_data'][key] = value
            self._save_state()
            
        except Exception as e:
            self.logger.error(f"Failed to set user data: {e}")
    
    def get_user_data(self, key: str, default=None) -> Any:
        """
        Get user data
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.state_data['user_data'].get(key, default)
    
    def clear_user_data(self, key: str = None):
        """
        Clear user data
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        try:
            if key:
                self.state_data['user_data'].pop(key, None)
            else:
                self.state_data['user_data'].clear()
            
            self._save_state()
            
        except Exception as e:
            self.logger.error(f"Failed to clear user data: {e}")
    
    def record_crash(self, reason: str):
        """
        Record application crash
        
        Args:
            reason: Reason for the crash
        """
        try:
            self.state_data['crash_count'] = self.state_data.get('crash_count', 0) + 1
            self.state_data['last_crash_time'] = time.time()
            self.state_data['last_crash_reason'] = reason
            
            self.set_state(ApplicationState.CRASHED, reason)
            self.crash_detected.emit(reason)
            
            self.logger.error(f"Crash recorded: {reason}")
            
        except Exception as e:
            self.logger.error(f"Failed to record crash: {e}")
    
    def get_crash_info(self) -> Dict:
        """Get crash information"""
        return {
            'crash_count': self.state_data.get('crash_count', 0),
            'last_crash_time': self.state_data.get('last_crash_time'),
            'last_crash_reason': self.state_data.get('last_crash_reason'),
            'recovery_attempts': self.crash_recovery_attempts
        }
    
    def get_statistics(self) -> Dict:
        """Get application statistics"""
        current_time = time.time()
        start_time = self.state_data.get('start_time', current_time)
        
        return {
            'app_name': self.app_name,
            'current_state': self.current_state,
            'uptime_seconds': current_time - start_time,
            'crash_count': self.state_data.get('crash_count', 0),
            'last_heartbeat': self.state_data.get('last_heartbeat'),
            'recovery_attempts': self.crash_recovery_attempts,
            'state_file': self.state_file
        }
    
    def shutdown_gracefully(self):
        """Prepare for graceful shutdown"""
        try:
            self.logger.info("Initiating graceful shutdown")
            
            # Stop heartbeat
            if self.heartbeat_timer:
                self.heartbeat_timer.stop()
            
            # Set shutdown state
            self.set_state(ApplicationState.SHUTTING_DOWN, "User initiated shutdown")
            
            # Clean up state file after a brief delay to ensure state is saved
            QTimer.singleShot(100, self._cleanup_state_file)
            
        except Exception as e:
            self.logger.error(f"Error during graceful shutdown: {e}")
    
    def _cleanup_state_file(self):
        """Clean up state file on graceful shutdown"""
        try:
            if self.state_file and os.path.exists(self.state_file):
                os.remove(self.state_file)
                self.logger.info("State file cleaned up")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup state file: {e}")
    
    def create_checkpoint(self, name: str, data: Dict):
        """
        Create a recovery checkpoint
        
        Args:
            name: Checkpoint name
            data: Checkpoint data
        """
        try:
            checkpoint_file = os.path.join(
                tempfile.gettempdir(), 
                f"{self.app_name}_checkpoint_{name}.pkl"
            )
            
            checkpoint_data = {
                'timestamp': time.time(),
                'state': self.current_state,
                'data': data
            }
            
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            
            self.logger.info(f"Checkpoint created: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint {name}: {e}")
    
    def restore_checkpoint(self, name: str) -> Optional[Dict]:
        """
        Restore from a checkpoint
        
        Args:
            name: Checkpoint name
            
        Returns:
            Checkpoint data or None if not found
        """
        try:
            checkpoint_file = os.path.join(
                tempfile.gettempdir(), 
                f"{self.app_name}_checkpoint_{name}.pkl"
            )
            
            if os.path.exists(checkpoint_file):
                with open(checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)
                
                self.logger.info(f"Checkpoint restored: {name}")
                return checkpoint_data.get('data')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to restore checkpoint {name}: {e}")
            return None
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            if hasattr(self, 'heartbeat_timer') and self.heartbeat_timer:
                self.heartbeat_timer.stop()
        except:
            pass