#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Logging utilities for NFC Reader/Writer
"""

import os
import logging
from datetime import datetime
from pathlib import Path

class DailyRotatingFileHandler(logging.FileHandler):
    def __init__(self, log_dir, base_filename, mode='a', encoding='utf-8', delay=False):
        self.log_dir = Path(log_dir)
        self.base_filename = base_filename
        self.current_date = datetime.now().date()
        
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up the initial log file
        self._set_log_file()
        
        # Initialize the parent class with the current log file
        super().__init__(self.current_log_file, mode, encoding, delay)
    
    def _get_log_file_name(self, date):
        """Generate log file name with date."""
        return self.log_dir / f"{self.base_filename}_{date.strftime('%Y%m%d')}.log"
    
    def _set_log_file(self):
        """Set the current log file based on the current date."""
        self.current_date = datetime.now().date()
        self.current_log_file = self._get_log_file_name(self.current_date)
    
    def _should_rollover(self):
        """Check if we should roll over to a new log file."""
        return datetime.now().date() > self.current_date
    
    def emit(self, record):
        """Eit a record, rolling over to a new file if the date has changed."""
        if self._should_rollover():
            self.close()
            self._set_log_file()
            self.stream = self._open()
        super().emit(record)

def setup_logging(log_dir="logs"):
    """
    Configure logging to both console and file with daily log rotation.
    
    Args:
        log_dir (str): Directory to store log files
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_format)
    
    # File handler with daily rotation
    file_handler = DailyRotatingFileHandler(
        log_dir=log_dir,
        base_filename="nfc_reader",
        encoding='utf-8'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Return the path to the current log file
    return str(file_handler.current_log_file)

def log_error(error_message, exc_info=None):
    """Log an error message with optional exception info."""
    logging.error(error_message, exc_info=exc_info)

def log_info(message):
    """Log an info message."""
    logging.info(message)

def log_warning(message):
    """Log a warning message."""
    logging.warning(message)

def log_debug(message):
    """Log a debug message."""
    logging.debug(message)
