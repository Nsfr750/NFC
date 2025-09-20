#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFC Thread for handling NFC operations
"""

import nfc
import logging
from PySide6.QtCore import QThread, Signal, QObject
from typing import Optional, Dict, Any
import serial.tools.list_ports

logger = logging.getLogger(__name__)

class NFCThread(QThread):
    """Thread for handling NFC operations."""
    
    # Signals
    tag_detected = Signal(object)  # Emits tag object when detected
    connection_status = Signal(str)  # Emits connection status messages
    error_occurred = Signal(str)  # Emits error messages
    reader_info = Signal(dict)  # Emits reader information
    
    def __init__(self, parent=None):
        """Initialize the NFC thread."""
        super().__init__(parent)
        self.clf = None
        self.running = False
        self.reader_type = 'Auto-Detect'
        self.reader_config = None
        self.selected_port = None
    
    def set_reader_type(self, reader_type: str, reader_config: Optional[Dict[str, Any]] = None):
        """Set the reader type and configuration.
        
        Args:
            reader_type: The type of reader to use
            reader_config: Configuration dictionary for the reader
        """
        self.reader_type = reader_type
        self.reader_config = reader_config
        logger.info(f"Reader type set to: {reader_type}")
    
    def set_selected_port(self, port: Optional[str]):
        """Set the selected serial port.
        
        Args:
            port: The serial port to use or None for auto-detection
        """
        self.selected_port = port
        logger.info(f"Selected port set to: {port}")
    
    def connect_to_reader(self) -> bool:
        """Connect to the NFC reader based on the selected type.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Close any existing connection
            if self.clf:
                self.clf.close()
                self.clf = None
            
            # Get connection parameters based on reader type
            connection_params = self.get_connection_params()
            
            if not connection_params:
                self.error_occurred.emit("No valid connection parameters for selected reader type")
                return False
            
            # Try to connect
            self.connection_status.emit(f"Connecting to {self.reader_type} reader...")
            
            for backend, target in connection_params:
                try:
                    if target:
                        clf = nfc.ContactlessFrontend(f"{backend}:{target}")
                    else:
                        clf = nfc.ContactlessFrontend(backend)
                    
                    # Test the connection
                    if clf:
                        self.clf = clf
                        self.connection_status.emit(f"Successfully connected to {self.reader_type} reader via {backend}")
                        
                        # Get reader info
                        reader_info = self.get_reader_info()
                        self.reader_info.emit(reader_info)
                        
                        return True
                        
                except Exception as e:
                    logger.debug(f"Connection attempt failed for {backend}:{target}: {str(e)}")
                    continue
            
            self.error_occurred.emit(f"Failed to connect to {self.reader_type} reader with all available methods")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to reader: {str(e)}")
            self.error_occurred.emit(f"Connection error: {str(e)}")
            return False
    
    def get_connection_params(self) -> list:
        """Get connection parameters based on the selected reader type.
        
        Returns:
            list: List of (backend, target) tuples to try
        """
        if self.reader_type == 'Auto-Detect':
            # Try all available backends
            return [
                ('usb', None),
                ('pcsc', None),
                ('uart', None)
            ]
        
        if not self.reader_config:
            return []
        
        backend = self.reader_config.get('backend', 'usb')
        vid_pid_list = self.reader_config.get('vid_pid', [])
        
        connection_params = []
        
        if backend == 'auto':
            # Try all backends
            connection_params.extend([
                ('usb', None),
                ('pcsc', None),
                ('uart', None)
            ])
        elif backend == 'usb':
            if self.selected_port:
                # Try direct USB connection to selected port
                connection_params.append(('usb', self.selected_port))
            else:
                # Try general USB connection
                connection_params.append(('usb', None))
        elif backend == 'pcsc':
            connection_params.append(('pcsc', None))
        elif backend == 'uart':
            if self.selected_port:
                # Try direct UART connection to selected port
                connection_params.append(('uart', self.selected_port))
            else:
                # Try to find compatible serial ports
                ports = serial.tools.list_ports.comports()
                for port in ports:
                    if vid_pid_list:
                        for vid, pid in vid_pid_list:
                            if port.vid == vid and port.pid == pid:
                                connection_params.append(('uart', port.device))
                                break
                    else:
                        connection_params.append(('uart', port.device))
        
        return connection_params
    
    def get_reader_info(self) -> Dict[str, Any]:
        """Get information about the connected reader.
        
        Returns:
            dict: Dictionary containing reader information
        """
        info = {
            'reader_type': self.reader_type,
            'backend': None,
            'device': None,
            'vendor': None,
            'product': None,
            'vid': None,
            'pid': None
        }
        
        try:
            if self.clf:
                # Try to get reader information from the clf object
                if hasattr(self.clf, 'device'):
                    info['device'] = str(self.clf.device)
                
                # Try to determine the backend being used
                if hasattr(self.clf, 'transport'):
                    transport = self.clf.transport
                    if hasattr(transport, 'path'):
                        info['backend'] = transport.path.split(':')[0]
                
                # Try to get USB device information
                if self.selected_port:
                    ports = serial.tools.list_ports.comports()
                    for port in ports:
                        if port.device == self.selected_port:
                            info.update({
                                'vendor': port.manufacturer,
                                'product': port.product,
                                'vid': port.vid,
                                'pid': port.pid
                            })
                            break
                
                # If no specific port selected, try to find by VID:PID
                if self.reader_config and self.reader_config.get('vid_pid'):
                    vid_pid_list = self.reader_config['vid_pid']
                    ports = serial.tools.list_ports.comports()
                    for port in ports:
                        if port.vid and port.pid:
                            for vid, pid in vid_pid_list:
                                if port.vid == vid and port.pid == pid:
                                    info.update({
                                        'vendor': port.manufacturer,
                                        'product': port.product,
                                        'vid': port.vid,
                                        'pid': port.pid
                                    })
                                    break
            
        except Exception as e:
            logger.error(f"Error getting reader info: {str(e)}")
        
        return info
    
    def run(self):
        """Main thread loop for NFC operations."""
        self.running = True
        
        # Connect to the reader
        if not self.connect_to_reader():
            self.running = False
            return
        
        self.connection_status.emit("NFC thread started. Waiting for tags...")
        
        try:
            while self.running:
                if not self.clf:
                    # Try to reconnect
                    if not self.connect_to_reader():
                        self.msleep(1000)  # Wait before retry
                        continue
                
                try:
                    # Try to sense a tag
                    tag = self.clf.sense(remote_target=None)
                    
                    if tag:
                        logger.info(f"Tag detected: {tag}")
                        self.tag_detected.emit(tag)
                        
                        # Wait a bit before sensing again
                        self.msleep(500)
                    else:
                        # No tag detected, wait before retrying
                        self.msleep(100)
                        
                except Exception as e:
                    logger.error(f"Error during tag sensing: {str(e)}")
                    self.error_occurred.emit(f"Tag sensing error: {str(e)}")
                    
                    # Try to reconnect
                    if self.clf:
                        try:
                            self.clf.close()
                        except:
                            pass
                        self.clf = None
                    
                    self.msleep(1000)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Error in NFC thread: {str(e)}")
            self.error_occurred.emit(f"Thread error: {str(e)}")
        
        finally:
            # Clean up
            if self.clf:
                try:
                    self.clf.close()
                except:
                    pass
                self.clf = None
            
            self.connection_status.emit("NFC thread stopped")
    
    def stop(self):
        """Stop the NFC thread."""
        self.running = False
        self.wait()
    
    def is_connected(self) -> bool:
        """Check if the NFC reader is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.clf is not None
    
    def get_reader_name(self) -> str:
        """Get the name of the connected reader.
        
        Returns:
            str: Reader name or description
        """
        if not self.reader_config:
            return self.reader_type
        
        return self.reader_config.get('description', self.reader_type)
