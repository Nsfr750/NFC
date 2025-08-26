"""
Session Manager Module

Handles user session management, including timeouts and activity tracking.
"""

import time
import logging
from typing import Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions with configurable timeouts."""
    
    def __init__(self, 
                 timeout_minutes: int = 15,
                 on_timeout: Optional[Callable] = None):
        """Initialize the session manager.
        
        Args:
            timeout_minutes: Number of minutes before session expires due to inactivity
            on_timeout: Callback function to execute when session times out
        """
        self.timeout = timedelta(minutes=timeout_minutes)
        self.on_timeout = on_timeout
        self._last_activity = None
        self._session_active = False
        self._timeout_timer = None
        
    def start_session(self) -> None:
        """Start a new user session."""
        self._session_active = True
        self.update_activity()
        logger.info("New session started")
    
    def end_session(self) -> None:
        """End the current user session."""
        self._session_active = False
        self._last_activity = None
        logger.info("Session ended")
    
    def update_activity(self) -> None:
        """Update the last activity timestamp to now."""
        self._last_activity = datetime.now()
        logger.debug(f"Session activity updated at {self._last_activity}")
    
    def is_session_active(self) -> bool:
        """Check if the session is still active (not timed out)."""
        if not self._session_active or self._last_activity is None:
            return False
            
        time_since_activity = datetime.now() - self._last_activity
        return time_since_activity < self.timeout
    
    def get_remaining_time(self) -> Optional[timedelta]:
        """Get the remaining time until session timeout.
        
        Returns:
            timedelta: Time remaining until timeout, or None if no active session
        """
        if not self._session_active or self._last_activity is None:
            return None
            
        time_elapsed = datetime.now() - self._last_activity
        remaining = self.timeout - time_elapsed
        return max(remaining, timedelta(0))
    
    def check_timeout(self) -> bool:
        """Check if the session has timed out.
        
        Returns:
            bool: True if session has timed out, False otherwise
        """
        if not self._session_active:
            return False
            
        has_timed_out = not self.is_session_active()
        if has_timed_out and self.on_timeout:
            self.on_timeout()
            
        return has_timed_out
    
    def reset_timeout(self, new_timeout_minutes: int = None) -> None:
        """Reset the session timeout duration.
        
        Args:
            new_timeout_minutes: New timeout duration in minutes (optional)
        """
        if new_timeout_minutes is not None:
            self.timeout = timedelta(minutes=new_timeout_minutes)
        self.update_activity()
        logger.info(f"Session timeout reset to {self.timeout}")
    
    def get_session_duration(self) -> Optional[timedelta]:
        """Get the duration of the current session.
        
        Returns:
            timedelta: Duration of the current session, or None if no active session
        """
        if not self._session_active or self._last_activity is None:
            return None
            
        return datetime.now() - (self._last_activity - self.timeout)
