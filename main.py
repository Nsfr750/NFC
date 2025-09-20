#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFC Reader/Writer Application
Copyright 2025 Nsfr750
"""

import sys
import os
import nfc
import time
import logging
from PySide6 import QtGui
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QTextEdit, QLineEdit, QLabel, 
                             QMessageBox, QMenuBar, QMenu, QToolBar, QStatusBar,
                             QFileDialog, QInputDialog, QDialog, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                             QTabWidget, QFormLayout, QComboBox, QCheckBox, QGroupBox,
                             QSizePolicy, QSpacerItem, QFrame, QScrollArea, QDockWidget)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QSettings, QByteArray, QMimeData, QUrl
from PySide6.QtGui import QAction, QIcon, QPixmap, QTextCursor, QFont, QColor, QDragEnterEvent, QDropEvent
import sys
import os
import logging
import json
import time
import platform
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple, Union

# Import local modules
from script.version import __version__, APP_NAME, APP_DESCRIPTION, AUTHOR, LICENSE
from script.device_panel import DevicePanel
from script.emulation_dialog import EmulationDialog
from script.encoding_utils import detect_encoding, convert_encoding, SUPPORTED_ENCODINGS
from script.statistics import StatisticsManager
from script.tag_formatter import TagFormatter
from script.statistics_dialog import StatisticsDialog
from script.tag_database import TagDatabase, TagRecord
from script.tag_history_dialog import TagHistoryDialog
from script.progress_dialog import ProgressDialog
from script.settings_dialog import SettingsDialog
from script.menu import AppMenu
from script.toolbar import AppToolBar
from script.nfc_manager import NFCManager

# Initialize database and statistics
tag_db = TagDatabase()
stats_manager = StatisticsManager()

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(APP_NAME)

class NFCThread(QThread):
    """Thread for handling NFC operations with support for different tag types and error handling."""
    
    # Signals
    tag_detected = Signal(dict)  # Emits dict with tag info
    tag_read_progress = Signal(int, int)  # Emits (current, total) for read progress
    tag_write_progress = Signal(int, int)  # Emits (current, total) for write progress
    error_occurred = Signal(str, str)  # Emits (error_level, message)
    reader_status = Signal(str)  # Emits reader connection status
    
    # Chunk size for reading/writing (in bytes)
    CHUNK_SIZE = 1024  # 1KB chunks for read/write operations
    
    # Timeout for operations (in seconds)
    OPERATION_TIMEOUT = 30
    
    # Supported tag types with their memory sizes (in bytes)
    SUPPORTED_TYPES = {
        'NFC Forum Type 1': {'type': 'nfc.ntag.ntag21x', 'size': 96},
        'NFC Forum Type 2': {'type': 'nfc.ntag.ntag21x', 'size': 48},
        'NFC Forum Type 3': {'type': 'nfc.felica', 'size': 8192},
        'NFC Forum Type 4': {'type': 'nfc.iso14443.4a', 'size': 32768},
        'MIFARE Classic': {'type': 'nfc.mifare.classic', 'size': 1024},
        'MIFARE Ultralight': {'type': 'nfc.mifare.ultralight', 'size': 64},
        'MIFARE DESFire': {'type': 'nfc.mifare.desfire', 'size': 8192},
        'FeliCa': {'type': 'nfc.felica', 'size': 8192},
        'ISO 14443-4': {'type': 'nfc.iso14443.4a', 'size': 32768},
        'ISO 15693': {'type': 'nfc.iso15693', 'size': 2048},
        'ISO 18092': {'type': 'nfc.iso18092', 'size': 2048},
        'Jewel': {'type': 'nfc.jewel', 'size': 64},
        'Topaz': {'type': 'nfc.topaz', 'size': 64},
    }
    
    # Default memory size for unknown tag types (4KB)
    DEFAULT_TAG_SIZE = 4096
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.write_data = None
        self.read_mode = True
        self.clf = None
        self.current_tag = None
        self.reader_type = None
        self.reader_config = None
        self.selected_port = None
        self._init_logging()
    
    def _init_logging(self):
        """Initialize logging for the NFC thread."""
        from script.logging_utils import setup_logging
        self.log_file = setup_logging()
        self.logger = logging.getLogger('NFCThread')
    
    def stop(self):
        """Stop the NFC thread and clean up resources."""
        self.running = False
        if hasattr(self, 'clf') and self.clf:
            try:
                self.clf.close()
            except Exception as e:
                logging.error(f"Error closing NFC reader: {str(e)}")
        self.wait(2000)  # Wait up to 2 seconds for thread to finish
        
    def _check_system_dependencies(self):
        """Check if required system dependencies are available."""
        issues = []
        warnings = []
        
        # Check for pyserial (primary detection method) - REQUIRED
        try:
            import serial.tools.list_ports
        except ImportError:
            issues.append("pyserial not installed - run: pip install pyserial")
        
        # Check for libusb on Windows (fallback for USB backend) - OPTIONAL
        if platform.system() == 'Windows':
            try:
                import ctypes
                libusb = ctypes.CDLL('libusb-1.0.dll')
            except:
                warnings.append("libusb not found - USB backend may not work (install from https://libusb.info/)")
        
        # Check for PC/SC on Windows (fallback for PC/SC backend) - OPTIONAL
        if platform.system() == 'Windows':
            try:
                import ctypes
                winscard = ctypes.CDLL('winscard.dll')
            except:
                warnings.append("PC/SC not available - PC/SC backend may not work (install PC/SC drivers)")
        
        return issues, warnings
    
    def _get_available_backends(self):
        """Get list of available NFC backends."""
        backends = []
        
        # Test USB backend
        try:
            clf = nfc.ContactlessFrontend()
            backends.append('usb')
            clf.close()
        except:
            pass
        
        # Test PC/SC backend
        try:
            clf = nfc.ContactlessFrontend('pcsc')
            backends.append('pcsc')
            clf.close()
        except:
            pass
        
        # Test UART backend (for serial readers)
        try:
            clf = nfc.ContactlessFrontend('uart')
            backends.append('uart')
            clf.close()
        except:
            pass
        
        return backends
    
    def _get_reader_status(self):
        """Check if NFC reader is properly connected with enhanced diagnostics."""
        try:
            # First check system dependencies
            dependency_issues, warnings = self._check_system_dependencies()
            
            # Only fail on required dependencies (pyserial)
            if dependency_issues:
                return (
                    "System dependencies missing:\n\n"
                    + "\n".join(f"• {issue}" for issue in dependency_issues)
                    + "\n\nPlease install the missing dependencies and restart the application."
                )
            
            # Check for available backends
            available_backends = self._get_available_backends()
            if not available_backends:
                return (
                    "No NFC backends available.\n\n"
                    "This typically means:\n"
                    "1. pyserial is not installed or not working\n"
                    "2. NFC reader drivers are not installed\n"
                    "3. Insufficient permissions to access serial devices\n\n"
                    "Solutions:\n"
                    "• Install pyserial: pip install pyserial\n"
                    "• Install drivers for your NFC reader\n"
                    "• Run as administrator (Windows)\n"
                    "• Check device permissions (Linux)"
                )
            
            # Check for serial devices using pyserial
            try:
                import serial.tools.list_ports
                ports = serial.tools.list_ports.comports()
                
                if not ports:
                    status_msg = (
                        f"No serial devices detected.\n\n"
                        f"Available backends: {', '.join(available_backends)}\n\n"
                        f"Common solutions:\n"
                        f"1. Ensure your NFC reader is properly connected\n"
                        f"2. Check if the device is recognized by your OS\n"
                        f"3. Install required drivers if needed\n"
                        f"4. Try a different USB port\n"
                        f"5. Check device manager (Windows) or dmesg (Linux)"
                    )
                    
                    # Add warnings if any
                    if warnings:
                        status_msg += f"\n\nWarnings:\n" + "\n".join(f"• {warning}" for warning in warnings)
                    
                    return status_msg
                
                # Look for NFC readers among serial devices
                nfc_patterns = [
                    'nfc', 'rfid', 'smart card', 'acr', 'pn532', 'rc-s380',
                    'reader', 'contactless', 'proximity', 'identification',
                    'dispositivo seriale', 'serial usb', 'usb serial', 'ch340',
                    'ftdi', 'cp2102', 'pl2303', 'pn532', 'rc522', 'mfrc522'
                ]
                
                found_readers = []
                all_devices = []
                
                for port in ports:
                    combined_text = f"{port.description} {port.product} {port.manufacturer}".lower()
                    
                    # Create detailed device info
                    device_details = []
                    if port.vid and port.pid:
                        device_details.append(f"VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}")
                    if port.manufacturer:
                        device_details.append(f"Manufacturer: {port.manufacturer}")
                    if port.product:
                        device_details.append(f"Product: {port.product}")
                    if port.serial_number:
                        device_details.append(f"Serial: {port.serial_number}")
                    
                    details_str = f" ({', '.join(device_details)})" if device_details else ""
                    
                    if any(pattern in combined_text for pattern in nfc_patterns):
                        found_readers.append(
                            f"{port.description} (Port: {port.device}){details_str}"
                        )
                    else:
                        all_devices.append(
                            f"{port.description} (Port: {port.device}){details_str}"
                        )
                
                if not found_readers:
                    # Try to identify the device type based on VID/PID
                    device_identification = []
                    for port in ports:
                        if port.vid and port.pid:
                            # Common USB-to-serial chip identifiers
                            known_chips = {
                                (0x1a86, 0x7523): "CH340 USB-to-Serial",
                                (0x0403, 0x6001): "FTDI FT232RL",
                                (0x10c4, 0xea60): "Silicon Labs CP2102",
                                (0x067b, 0x2303): "Prolific PL2303",
                                (0x165c, 0x0011): "PN532 NFC controller",
                                (0x072f, 0x2200): "NS106 Dual Frequency RFID/NFC Reader",
                                (0x072f, 0x90cc): "ACS ACR1222L NFC Reader",
                                (0x054c, 0x06c3): "Sony RC-S380 NFC reader",
                            }
                            
                            chip_id = (port.vid, port.pid)
                            if chip_id in known_chips:
                                device_identification.append(
                                    f"{port.device}: {known_chips[chip_id]}"
                                )
                    
                    status_msg = (
                        f"No NFC readers detected among serial devices.\n\n"
                        f"Available backends: {', '.join(available_backends)}\n"
                        f"Found serial devices ({len(ports)} total):\n"
                        f"\n".join(f"• {device}" for device in all_devices[:5])  # Show first 5
                        + (f"\n• ... and {len(all_devices)-5} more" if len(all_devices) > 5 else "")
                    )
                    
                    if device_identification:
                        status_msg += f"\n\nDevice Identification:\n"
                        for ident in device_identification:
                            status_msg += f"• {ident}\n"
                    
                    status_msg += (
                        f"\n\nIf your NFC reader is listed above, try connecting to it manually."
                        f"\n\nTip: Many NFC readers appear as generic USB-Serial devices."
                        f" Try connecting to the device port directly in the application."
                    )
                    
                    # Add warnings if any
                    if warnings:
                        status_msg += f"\n\nWarnings:\n" + "\n".join(f"• {warning}" for warning in warnings)
                    
                    return status_msg
                
                # If we found readers, return None (success) but log warnings
                if warnings:
                    for warning in warnings:
                        logging.warning(f"Optional dependency warning: {warning}")
                
                return None
                
            except ImportError:
                return "pyserial not available - install with: pip install pyserial"
            except Exception as e:
                return f"Error checking serial devices: {str(e)}\n\n{traceback.format_exc()}"
            
        except ImportError as e:
            return f"Required libraries not available: {str(e)}\n\nInstall with: pip install pyserial"
        except Exception as e:
            return f"Error checking devices: {str(e)}\n\n{traceback.format_exc()}"
    
    def run(self):
        """Main thread loop for NFC operations with enhanced backend detection."""
        self.running = True
        self.logger.info("NFC thread started")
        
        # Initialize variables
        clf = None
        used_backend = None
        
        # Check for common issues before initializing the reader
        reader_status = self._get_reader_status()
        if reader_status:
            self.error_occurred.emit("NFC Reader Not Found", reader_status)
            return
        
        # Determine connection strategy based on reader type and port
        connection_attempts = []
        
        if self.reader_type and self.reader_type != 'Auto-Detect':
            # Use reader-specific connection strategy
            if self.reader_config:
                backend = self.reader_config.get('backend', 'usb')
                vid_pid_list = self.reader_config.get('vid_pid', [])
                
                if backend == 'usb' and self.selected_port:
                    # Try direct USB connection to selected port
                    connection_attempts.append(('usb', self.selected_port))
                elif backend == 'pcsc':
                    connection_attempts.append(('pcsc', None))
                elif backend == 'uart' and self.selected_port:
                    # Try direct UART connection to selected port
                    connection_attempts.append(('uart', self.selected_port))
                elif backend == 'uart':
                    # Try to find compatible serial ports by VID:PID
                    try:
                        import serial.tools.list_ports
                        ports = serial.tools.list_ports.comports()
                        for port in ports:
                            if vid_pid_list:
                                for vid, pid in vid_pid_list:
                                    if port.vid == vid and port.pid == pid:
                                        connection_attempts.append(('uart', port.device))
                                        break
                    except ImportError:
                        pass
        
        # If no reader-specific strategy, try the selected port directly
        if self.selected_port and not connection_attempts:
            try:
                port_spec = f"tty:{self.selected_port}" if platform.system() != 'Windows' else f"com:{self.selected_port}"
                connection_attempts.append(('serial', self.selected_port))
            except:
                pass
        
        # If no specific attempts, try general backends
        if not connection_attempts:
            connection_attempts = [
                ('usb', None),
                ('pcsc', None),
                ('uart', None)
            ]
        
        # Try each connection attempt
        for backend, target in connection_attempts:
            try:
                if backend == 'serial':
                    port_spec = f"tty:{target}" if platform.system() != 'Windows' else f"com:{target}"
                    self.logger.info(f"Trying NFC reader on {port_spec}")
                    clf = nfc.ContactlessFrontend(port_spec)
                    used_backend = f"serial ({target})"
                elif backend == 'usb':
                    if target:
                        self.logger.info(f"Trying NFC reader on USB target: {target}")
                        clf = nfc.ContactlessFrontend(f"usb:{target}")
                    else:
                        self.logger.info("Trying NFC reader on USB backend")
                        clf = nfc.ContactlessFrontend()
                    used_backend = "usb"
                elif backend == 'pcsc':
                    self.logger.info("Trying NFC reader on PC/SC backend")
                    clf = nfc.ContactlessFrontend('pcsc')
                    used_backend = "pcsc"
                elif backend == 'uart':
                    if target:
                        self.logger.info(f"Trying NFC reader on UART target: {target}")
                        clf = nfc.ContactlessFrontend(f"uart:{target}")
                    else:
                        self.logger.info("Trying NFC reader on UART backend")
                        clf = nfc.ContactlessFrontend('uart')
                    used_backend = "uart"
                
                if clf:
                    self.logger.info(f"Successfully initialized NFC reader using {used_backend}")
                    break
                    
            except Exception as e:
                self.logger.debug(f"Failed to connect using {backend}:{target}: {str(e)}")
                continue
        
        # If no connection method worked, show error
        if not clf:
            error_msg = (
                "Could not initialize any NFC backend.\n\n"
                "Please ensure:\n"
                "1. Your NFC reader is properly connected\n"
                "2. Required drivers are installed\n"
                "3. You have sufficient permissions\n\n"
                "Try running the NFC Diagnostics tool for more information."
            )
            self.error_occurred.emit("NFC Initialization Failed", error_msg)
            return
        
        try:
            self.clf = clf
            self.reader_status.emit("connected")
            self.logger.info(f"NFC reader connected using {used_backend} backend")
            
            while self.running:
                try:
                    tag = self.clf.connect(
                        rdwr={
                            'on-connect': self.on_connect,
                            'on-discover': self.on_discover,
                            'on-release': self.on_release,
                            'beep-on-connect': False,
                            'targets': ['106A', '106B', '212F', '424F']
                        },
                        terminate=lambda: not self.running
                    )
                    if tag and self.running:
                        time.sleep(1)  # Prevent multiple rapid reads
                except nfc.clf.CommunicationError as e:
                    self.logger.warning(f"Communication error: {str(e)}")
                    self.error_occurred.emit("Communication Error", f"NFC communication error: {str(e)}")
                except Exception as e:
                    self.logger.error(f"Unexpected error in NFC loop: {str(e)}")
                    if self.running:
                        self.error_occurred.emit("NFC Error", f"Unexpected error: {str(e)}")
                    time.sleep(2)  # Wait before retrying
                    
        except KeyboardInterrupt:
            self.logger.info("NFC thread interrupted by user")
        except Exception as e:
            self.logger.error(f"Fatal error in NFC thread: {str(e)}")
            self.error_occurred.emit("NFC Thread Error", f"Fatal error: {str(e)}")
        finally:
            if clf:
                try:
                    clf.close()
                except:
                    pass
            self.reader_status.emit("disconnected")
            self.logger.info("NFC thread stopped")
    
    def on_discover(self, tag):
        """Called when a tag is discovered."""
        self.current_tag = tag
        tag_type = self.SUPPORTED_TYPES.get(tag.type, tag.type)
        self.logger.info(f"Tag detected: {tag_type} ({tag.identifier.hex()})")
        return True
    
    def on_release(self, tag):
        """Called when a tag is released."""
        self.logger.debug(f"Tag released: {tag.identifier.hex()}")
        self.current_tag = None
    
    def on_connect(self, tag):
        """Handle tag connection and dispatch to appropriate handler."""
        try:
            self.current_tag = tag
            
            # Check if tag is readable
            if not tag or not hasattr(tag, 'ndef') or not hasattr(tag, 'type'):
                self.error_occurred.emit(
                    "Unsupported Tag",
                    "The tag is not supported or may be damaged.\n\n"
                    "Supported tag types include:\n"
                    "- MIFARE Classic 1K/4K\n"
                    "- NTAG203/210/213/215/216\n"
                    "- MIFARE Ultralight\n"
                    "- ISO 14443-4 (Type 4) tags"
                )
                return False
                
            tag_info = self._get_tag_info(tag)
            
            if not tag_info:
                self.error_occurred.emit(
                    "Unsupported Tag Type",
                    f"Tag type '{tag.type}' is not supported.\n\n"
                    "This application supports the following tag types:\n"
                    "- MIFARE Classic (1K/4K)\n"
                    "- NTAG (203/210/213/215/216)\n"
                    "- MIFARE Ultralight\n"
                    "- FeliCa\n"
                    f"\nDetected tag type: {tag.type}"
                )
                return False
            
            if self.read_mode:
                self.read_tag(tag, tag_info)
            elif self.write_data:
                self.write_tag(tag, tag_info)
            else:
                self.tag_detected.emit(tag_info)
                
            return True
            
        except nfc.tag.TagCommandError as e:
            self.logger.error(f"Tag command error: {str(e)}")
            self.error_occurred.emit("ERROR", f"Tag error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error in on_connect: {str(e)}", exc_info=True)
            self.error_occurred.emit("ERROR", f"Operation failed: {str(e)}")
            return False
    
    def _parse_ndef_record(self, record):
        """Parse an NDEF record into a readable format."""
        record_info = {
            'type': record.type,
            'name': record.name,
            'tnf': str(record.tnf),
            'payload': record.data.hex(),
            'size': len(record.data)
        }
        
        try:
            if record.type == 'text':
                record_info['data'] = record.text
                record_info['language'] = record.language if hasattr(record, 'language') else 'en'
                record_info['encoding'] = 'UTF-8' if hasattr(record, 'encoding') and record.encoding == 'utf-8' else 'UTF-16'
            
            elif record.type == 'uri':
                record_info['uri'] = record.uri
            
            elif record.type == 'mime':
                record_info['mime_type'] = record.mime_type
                record_info['data'] = record.data.decode('utf-8', errors='replace')
            
            elif record.type == 'external':
                record_info['domain'] = record.domain
                record_info['type'] = record.type
                record_info['data'] = record.data.decode('utf-8', errors='replace')
            
            elif record.type == 'smart-poster':
                record_info['title'] = record.title
                record_info['uri'] = record.uri
                if hasattr(record, 'action'):
                    record_info['action'] = str(record.action)
            
            return record_info
            
        except Exception as e:
            self.logger.warning(f"Error parsing NDEF record: {str(e)}")
            return record_info
    
    def read_tag(self, tag, tag_info):
        """Read data from an NFC tag with enhanced NDEF support and record statistics."""
        
        rt_time = time.time()
        try:
            # Read NDEF message if available
            ndef_data = None
            data_size = 0
            if tag.ndef:
                try:
                    ndef_data = tag.ndef.message.pretty()
                    if ndef_data:
                        data_size = len(ndef_data.encode('utf-8'))
                except Exception as e:
                    self.logger.warning(f"Error reading NDEF data: {str(e)}")
                    raise  # Re-raise to be caught by the outer try-except
            
            # Get tag information
            tag_info['ndef'] = ndef_data
            tag_info['size'] = data_size
            
            # Read NDEF records
            if tag.ndef:
                for record in tag.ndef.records:
                    record_info = self._parse_ndef_record(record)
                    tag_info['records'].append(record_info)
            
            # Record successful read operation
            record_operation(
                operation_type='read',
                tag_type=str(tag.type) if hasattr(tag, 'type') else 'unknown',
                success=True,
                data_size=data_size,
                duration=time.time() - start_time
            )
            
            return {
                'success': True,
                'data': ndef_data,
                'size': data_size,
                'read_time': time.time() - start_time,
                'tag_type': str(tag.type)
            }
            
        except Exception as e:
            self.logger.error(f"Error reading tag: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'read_time': time.time() - start_time
            }
    
    def _is_tag_lockable(self, tag):
        """Check if the tag supports locking."""
        # Check for common tag types that support locking
        if hasattr(tag, 'is_protected') and callable(tag.is_protected):
            return True
        if hasattr(tag, 'protect') and callable(tag.protect):
            return True
        if hasattr(tag, 'memory') and hasattr(tag.memory, 'protect'):
            return True
        return False
    
    def _is_tag_locked(self, tag):
        """Check if the tag is locked."""
        try:
            if hasattr(tag, 'is_protected') and callable(tag.is_protected):
                return tag.is_protected()
            if hasattr(tag, 'memory') and hasattr(tag.memory, 'is_locked'):
                return tag.memory.is_locked()
            return False
        except Exception as e:
            self.logger.warning(f"Error checking if tag is locked: {str(e)}")
            return False
    
    def write_tag(self, tag, text):
        """Write text to an NFC tag with verification and locking support and record statistics."""
        start_time = time.time()
        try:
            if not tag.ndef:
                error_msg = "Tag is not NDEF formatted"
                self.error_occurred.emit("ERROR", error_msg)
                record_operation(
                    operation_type='write',
                    tag_type=str(tag.type) if hasattr(tag, 'type') else 'unknown',
                    success=False,
                    data_size=0,
                    duration=time.time() - start_time,
                    error=error_msg
                )
                return False
                
            # Format the text using the tag formatter if needed
            formatted_text = tag_formatter.format_data(text)
            data_size = len(formatted_text.encode('utf-8'))
                
            # Create a new NDEF message with a text record
            record = ndef.TextRecord(formatted_text)
            tag.ndef.records = [record]
            
            # Record successful write operation
            record_operation(
                operation_type='write',
                tag_type=str(tag.type) if hasattr(tag, 'type') else 'unknown',
                success=True,
                data_size=data_size,
                duration=time.time() - start_time
            )
            
            return True
            
        except Exception as e:
            error_msg = f"Error writing to tag: {e}"
            self.error_occurred.emit("ERROR", error_msg)
            record_operation(
                operation_type='write',
                tag_type=str(tag.type) if 'tag' in locals() and hasattr(tag, 'type') else 'unknown',
                success=False,
                data_size=len(text.encode('utf-8')) if text else 0,
                duration=time.time() - start_time,
                error=error_msg
            )
            return False
    
    def lock_tag(self, tag, permanent=False):
        """
        Lock the tag to prevent further writes.
        
        Args:
            tag: The NFC tag to lock
            permanent: If True, lock permanently (irreversible)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self._is_tag_lockable(tag):
                return False, "Tag does not support locking"
                
            if self._is_tag_locked(tag):
                return True, "Tag is already locked"
                
            # Handle different tag types
            if hasattr(tag, 'protect') and callable(tag.protect):
                tag.protect(True, permanent=permanent)
                return True, "Tag locked successfully"
                
            elif hasattr(tag, 'memory') and hasattr(tag.memory, 'lock'):
                tag.memory.lock(permanent=permanent)
                return True, "Tag locked successfully"
                
            return False, "Locking not supported on this tag type"
            
        except Exception as e:
            error_msg = f"Error locking tag: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def write_tag(self, tag, tag_info):
        """Write data to an NFC tag with verification and locking support."""
        try:
            # Check if tag is locked
            if self._is_tag_locked(tag):
                raise Exception("Cannot write to a locked tag")
                
            if not tag.ndef:
                if hasattr(tag, 'format'):
                    tag.format()
                    tag_info['formatted'] = True
                else:
                    raise Exception("Tag is not NDEF formattable")
            
            # Parse the write data to determine record type
            if isinstance(self.write_data, dict):
                # Handle structured write data
                if self.write_data.get('type') == 'text':
                    record = ndef.TextRecord(
                        self.write_data.get('text', ''),
                        self.write_data.get('language', 'en'),
                        self.write_data.get('encoding', 'utf-8')
                    )
                elif self.write_data.get('type') == 'uri':
                    record = ndef.UriRecord(self.write_data.get('uri', ''))
                elif self.write_data.get('type') == 'mime':
                    record = ndef.MimeRecord(
                        self.write_data.get('mime_type', 'text/plain'),
                        self.write_data.get('data', b'').encode('utf-8')
                    )
                else:
                    # Default to text record
                    record = ndef.TextRecord(str(self.write_data))
            else:
                # Fallback to simple text record
                record = ndef.TextRecord(str(self.write_data))
            
            # Write the record
            tag.ndef.records = [record]
            
            # Verify write
            if tag.ndef.records:
                if hasattr(record, 'text'):
                    verify_data = tag.ndef.records[0].text
                    expected_data = record.text
                elif hasattr(record, 'uri'):
                    verify_data = tag.ndef.records[0].uri
                    expected_data = record.uri
                else:
                    verify_data = tag.ndef.records[0].data
                    expected_data = record.data
                
                if verify_data != expected_data:
                    raise Exception("Failed to verify written data")
            
            # Update tag info with the written record
            record_info = self._parse_ndef_record(record)
            record_info['id'] = 'written_record'
            tag_info['records'].append(record_info)
            
            # Handle locking if requested
            if hasattr(self, 'lock_after_write') and self.lock_after_write:
                success, msg = self.lock_tag(tag, permanent=self.permanent_lock)
                if success:
                    tag_info['locked'] = True
                    self.logger.info(f"Tag locked after write: {msg}")
                else:
                    self.logger.warning(f"Failed to lock tag after write: {msg}")
            
            self.tag_detected.emit(tag_info)
            self.logger.info(f"Successfully wrote to tag: {tag_info['id']}")
            
        except Exception as e:
            self.logger.error(f"Error writing to tag: {str(e)}", exc_info=True)
            raise
    
    def format_tag(self, tag):
        """Format the tag (if supported)."""
        try:
            if hasattr(tag, 'format'):
                tag.format()
                return True, "Tag formatted successfully"
            return False, "Tag does not support formatting"
        except Exception as e:
            return False, f"Error formatting tag: {str(e)}"

class NFCApp(QMainWindow):
    """Main application window for NFC Reader/Writer."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFC Reader/Writer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        # Initialize logging
        self._init_logging()
        self.logger = logging.getLogger('NFCApp')
        
        # Initialize NFC thread and manager
        self.nfc_thread = NFCThread()
        self.nfc_manager = NFCManager(self.nfc_thread)
        
        # Connect signals
        self.nfc_thread.tag_detected.connect(self.handle_tag_detected)
        self.nfc_thread.error_occurred.connect(self.show_error)
        self.nfc_thread.reader_status.connect(self.update_reader_status)
        self.nfc_thread.tag_read_progress.connect(self.update_read_progress)
        self.nfc_thread.tag_write_progress.connect(self.update_write_progress)
        
        # Set window title with version
        self.setWindowTitle(f"NFC Reader/Writer")
        
        # Initialize UI
        self.init_ui()
        
        # Initialize menu and toolbar
        self.menu = AppMenu(self, self.nfc_thread)
        self.toolbar = AppToolBar(self, self.nfc_thread)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # Initialize device panel
        self.device_panel = DevicePanel()
        self.device_dock = QDockWidget("USB Device", self)
        self.device_dock.setWidget(self.device_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.device_dock)
        
        # Connect device panel signals (after device panel is created)
        self.device_panel.device_connected.connect(self.on_device_connection_changed)
        self.device_panel.reader_type_changed.connect(self.on_reader_type_changed)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        self.status_label = QLabel("Status: Ready")
        self.statusBar().addPermanentWidget(self.status_label)
        
    def lock_application(self):
        """Lock the application, requiring authentication to continue."""
        # Save the current state
        self.was_reading = self.nfc_thread.read_mode
        
        # Stop any ongoing operations
        self.nfc_thread.stop()
        
        # Show lock screen or dialog
        from script.auth import LoginDialog
        dialog = LoginDialog("Application Locked", "Enter your password to unlock", self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            # Restore previous state
            if self.was_reading:
                self.start_reading()
            return True
        return False
        
    def init_ui(self):
        """Initialize the main UI components."""
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Create tag info group
        tag_group = QGroupBox("Tag Information")
        tag_layout = QFormLayout()
        
        # Tag type
        self.tag_type_label = QLabel("Type: Not detected")
        tag_layout.addRow("Type:", self.tag_type_label)
        
        # Tag UID
        self.tag_uid_label = QLabel("UID: Not detected")
        tag_layout.addRow("UID:", self.tag_uid_label)
        
        # Tag size
        self.tag_size_label = QLabel("Size: 0 bytes")
        tag_layout.addRow("Size:", self.tag_size_label)
        
        # Tag data display
        self.tag_data_edit = QTextEdit()
        self.tag_data_edit.setReadOnly(True)
        self.tag_data_edit.setPlaceholderText("Tag data will appear here...")
        tag_layout.addRow(self.tag_data_edit)
        
        tag_group.setLayout(tag_layout)
        
        # Create action buttons
        button_layout = QHBoxLayout()
        
        self.read_button = QPushButton("Read Tag")
        self.read_button.clicked.connect(self.start_reading)
        button_layout.addWidget(self.read_button)
        
        self.write_button = QPushButton("Write to Tag")
        self.write_button.clicked.connect(self.start_writing)
        button_layout.addWidget(self.write_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)
        
        # Add widgets to main layout
        self.layout.addWidget(tag_group)
        self.layout.addLayout(button_layout)
        
        # Set initial button states
        self.read_button.setEnabled(True)
        self.write_button.setEnabled(False)
        
    def _init_logging(self):
        """Initialize application-wide logging."""
        from script.logging_utils import setup_logging
        self.log_file = setup_logging()
        logging.info("NFC Reader/Writer application started")
    
    def log(self, message, level="INFO"):
        """Log a message to the application's status bar and log file."""
        if hasattr(self, 'logger'):
            if level == "ERROR":
                self.logger.error(message)
            elif level == "WARNING":
                self.logger.warning(message)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Tag info group
        tag_group = QGroupBox("Tag Information")
        tag_layout = QVBoxLayout()
        
        # Tag ID and Type
        info_layout = QHBoxLayout()
        self.tag_id_label = QLabel("Tag ID: Not detected")
        self.tag_type_label = QLabel("Type: -") 
        info_layout.addWidget(self.tag_id_label)
        info_layout.addStretch()
        info_layout.addWidget(self.tag_type_label)
        tag_layout.addLayout(info_layout)
        
        # Tag data display
        self.tag_data_display = QTextEdit()
        self.tag_data_display.setReadOnly(True)
        self.tag_data_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
        """)
        tag_layout.addWidget(self.tag_data_display)
        tag_group.setLayout(tag_layout)
        
        # Log group
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        log_layout.addWidget(self.log_display)
        log_group.setLayout(log_layout)
        
        # Add groups to main layout
        layout.addWidget(tag_group, 40)  # 40% of space
        layout.addWidget(log_group, 60)  # 60% of space
    
    def handle_tag_detected(self, tag_info):
        """Handle a detected NFC tag with enhanced NDEF and locking support."""
        # Get extended tag info from NFC manager
        tag_info.update(self.nfc_manager.get_tag_info())
        
        # Update UI based on tag capabilities
        self.update_ui_for_tag(tag_info)
        try:
            # Store the current tag info for potential operations
            self.current_tag_info = tag_info
            
            # Update tag info
            tag_type = tag_info['type']
            if 'ndef_capacity' in tag_info:
                tag_type += f" (NDEF: {len(tag_info.get('records', []))}/{tag_info['ndef_capacity']} bytes)"
            
            self.tag_id_label.setText(f"Tag ID: {tag_info['id']}")
            self.tag_type_label.setText(f"Type: {tag_type}")
            
            # Format tag data for display
            tag_data = []
            tag_data.append(f"<b>Tag ID:</b> {tag_info['id']}")
            tag_data.append(f"<b>Type:</b> {tag_info['type']}")
            
            # Add NDEF information if available
            if 'ndef_capacity' in tag_info:
                tag_data.append(f"<b>NDEF Capacity:</b> {tag_info['ndef_capacity']} bytes")
                tag_data.append(f"<b>NDEF Writeable:</b> {'Yes' if tag_info.get('ndef_writeable', False) else 'No'}")
            
            tag_data.append(f"<b>Writable:</b> {'Yes' if tag_info['writable'] else 'No'}")
            tag_data.append(f"<b>Formatted:</b> {'Yes' if tag_info['formatted'] else 'No'}")
            
            # Add locking information
            if tag_info.get('lockable', False):
                lock_status = 'Locked' if tag_info.get('locked', False) else 'Unlocked'
                tag_data.append(f"<b>Lock Status:</b> {lock_status}")
            
            if 'memory_capacity' in tag_info:
                tag_data.append(f"<b>Memory:</b> {tag_info['memory_capacity']} bytes")
            
            # Display NDEF records if available
            if tag_info.get('records'):
                tag_data.append("\n<b>NDEF Records:</b>")
                for i, record in enumerate(tag_info['records'], 1):
                    record_type = record.get('type', 'unknown')
                    record_name = record.get('name', f'Record {i}')
                    
                    tag_data.append(f"\n  {i}. <b>{record_name}</b> ({record_type})")
                    
                    # Format record data based on type
                    if record_type == 'text':
                        tag_data.append(f"     Text: {record.get('data', '')}")
                        if 'language' in record:
                            tag_data.append(f"     Language: {record['language']}")
                    elif record_type == 'uri':
                        tag_data.append(f"     URI: {record.get('uri', '')}")
                    elif record_type == 'mime':
                        tag_data.append(f"     MIME Type: {record.get('mime_type', '')}")
                        tag_data.append(f"     Data: {record.get('data', '')}")
                    elif record_type == 'smart-poster':
                        tag_data.append(f"     Title: {record.get('title', '')}")
                        tag_data.append(f"     URI: {record.get('uri', '')}")
                        if 'action' in record:
                            tag_data.append(f"     Action: {record['action']}")
                    else:
                        tag_data.append(f"     Data: {record.get('data', '')}")
                    
                    if 'size' in record:
                        tag_data.append(f"     Size: {record['size']} bytes")
            
            self.tag_data_display.setHtml("\n".join(tag_data))
            
            # Update UI based on tag capabilities
            self.update_ui_for_tag(tag_info)
            
            # Log the operation
            self.log(f"Tag detected: {tag_info['type']} ({tag_info['id']})")
            
        except Exception as e:
            self.logger.error(f"Error handling tag: {str(e)}", exc_info=True)
            self.show_error("ERROR", f"Failed to process tag: {str(e)}")
    
    def update_ui_for_tag(self, tag_info):
        """Update UI elements based on the current tag's capabilities."""
        # Enable/disable write button based on tag state
        can_write = tag_info.get('writable', False) and not tag_info.get('locked', False)
        self.toolbar.set_write_enabled(can_write)
        
        # Update lock button state
        if tag_info.get('lockable', False):
            if tag_info.get('locked', False):
                self.toolbar.set_lock_button_state('locked')
            else:
                self.toolbar.set_lock_button_state('unlocked')
        else:
            self.toolbar.set_lock_button_state('unsupported')
        
    # Menu-related methods have been moved to script/menu.py
    
    def show_error(self, level, message):
        """Show an error message in the UI and log it."""
        if level == "ERROR":
            QMessageBox.critical(self, "Error", message)
        elif level == "WARNING":
            QMessageBox.warning(self, "Warning", message)
        else:
            QMessageBox.information(self, "Information", message)
            
        # Update status bar
        self.statusBar().showMessage(f"{level}: {message}", 5000)  # Show for 5 seconds
        self.log(message, level)
    
    def start_reading(self):
        """Start reading from the NFC tag with MIFARE authentication support."""
        if not hasattr(self, 'nfc_manager') or not self.nfc_manager:
            self.show_error("ERROR", "NFC manager not initialized")
            return
            
        # Check if we have a current tag
        if not hasattr(self, 'current_tag_info') or not self.current_tag_info:
            self.show_error("WARNING", "No tag detected. Please place a tag near the reader.")
            return
            
        # For MIFARE Classic tags, authenticate first
        if (self.nfc_manager.nfc_ops.current_tag and 
            self.nfc_manager.nfc_ops.current_tag['type'] in [
                'MIFARE_CLASSIC_1K', 
                'MIFARE_CLASSIC_4K'
            ]):
            # Try to authenticate with default key (FF FF FF FF FF FF)
            if not self.nfc_manager.authenticate_mifare(4):  # First block of sector 1
                self.show_error("ERROR", "MIFARE authentication failed. The tag may be locked or use a different key.")
                return
        
        # Start reading
        self.nfc_thread.read_mode = True
        self.nfc_thread.write_data = None
        self.statusBar().showMessage("Reading tag...", 3000)
        self.log("Started reading NFC tag")
    
    def start_writing(self, text=None):
        """Prepare to write to NFC tags with MIFARE authentication support."""
        if not hasattr(self, 'nfc_manager') or not self.nfc_manager:
            self.show_error("ERROR", "NFC manager not initialized")
            return
            
        # Get text from input if not provided
        if text is None:
            text = getattr(self, 'text_input', None)
            if text:
                text = text.text().strip()
                
        if not text:
            QMessageBox.warning(self, "Error", "Please enter some text to write to the tag.")
            return
            
        # Check if we have a current tag
        if not hasattr(self, 'current_tag_info') or not self.current_tag_info:
            self.show_error("WARNING", "No tag detected. Please place a tag near the reader.")
            return
            
        # For MIFARE Classic tags, authenticate first
        if (self.nfc_manager.nfc_ops.current_tag and 
            self.nfc_manager.nfc_ops.current_tag['type'] in [
                'MIFARE_CLASSIC_1K', 
                'MIFARE_CLASSIC_4K'
            ]):
            # Try to authenticate with default key (FF FF FF FF FF FF)
            if not self.nfc_manager.authenticate_mifare(4):  # First block of sector 1
                self.show_error("ERROR", "MIFARE authentication failed. The tag may be locked or use a different key.")
                return
        
        # Start writing
        self.nfc_thread.read_mode = False
        self.nfc_thread.write_data = text
        self.statusBar().showMessage("Ready to write to tag...", 3000)
        self.log(f"Ready to write to NFC tag: {text[:50]}..." if len(text) > 50 else text)
    
    def show_statistics(self):
        """Show the statistics dialog."""
        dialog = StatisticsDialog(stats_manager, self)
        dialog.exec()
        
    def update_tag_list(self, filter_text: str = None):
        """Update the tag list with recent tags from the database."""
        try:
            # Show loading indicator
            if self.progress_dialog:
                self.progress_dialog.set_status("Loading tag list...")
                self.progress_dialog.progress_bar.setRange(0, 0)  # Indeterminate
            
            # Get all tags (or filtered tags) in a separate thread
            def load_tags():
                try:
                    if filter_text:
                        tags = tag_db.search_tags(filter_text)
                    else:
                        tags = tag_db.get_all_tags()
                    
                    # Update UI in the main thread
                    self.update_tag_list_ui.emit(tags)
                    
                except Exception as e:
                    error_msg = f"Error loading tags: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.log_signal.emit(error_msg, "ERROR")
                finally:
                    # Close progress dialog if open
                    if self.progress_dialog:
                        self.progress_dialog.close()
                        self.progress_dialog = None
            
            # Use QThreadPool for background loading
            from PySide6.QtCore import QRunnable, QThreadPool
            
            class LoadTagsTask(QRunnable):
                def __init__(self, func):
                    super().__init__()
                    self.func = func
                
                def run(self):
                    self.func()
            
            QThreadPool.globalInstance().start(LoadTagsTask(load_tags))
            
        except Exception as e:
            error_msg = f"Error updating tag list: {str(e)}"
            self.log(error_msg, level="ERROR")
            logger.error(error_msg, exc_info=True)
            
            # Close progress dialog if open
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
    
    def update_tag_list_ui(self, tags):
        """Update the tag list UI with the provided tags."""
        try:
            # Clear the table
            self.tag_table.setRowCount(len(tags))
            
            # Add tags to the table
            for row, tag in enumerate(tags):
                # Tag ID (shortened)
                tag_id = tag.tag_id[:12] + '...' if len(tag.tag_id) > 12 else tag.tag_id
                self.tag_table.setItem(row, 0, QTableWidgetItem(tag_id))
                self.tag_table.item(row, 0).setData(Qt.UserRole, tag.tag_id)  # Store full ID
                
                # Tag type
                self.tag_table.setItem(row, 1, QTableWidgetItem(tag.tag_type or 'Unknown'))
                
                # Last updated
                try:
                    date = datetime.fromisoformat(tag.updated_at)
                    date_str = date.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    date_str = str(tag.updated_at)
                self.tag_table.setItem(row, 2, QTableWidgetItem(date_str))
            
            # Resize columns to contents
            self.tag_table.resizeColumnsToContents()
            
        except Exception as e:
            error_msg = f"Error updating tag list UI: {str(e)}"
            self.log(error_msg, level="ERROR")
            logger.error(error_msg, exc_info=True)
    
    def filter_tags(self):
        """Filter the tag list based on search text."""
        filter_text = self.tag_search.text().strip()
        self.update_tag_list(filter_text)
    
    def on_tag_double_clicked(self, item):
        """Handle double-click on a tag in the list."""
        row = item.row()
        tag_id = self.tag_table.item(row, 0).data(Qt.UserRole)
        tag = tag_db.get_tag(tag_id)
        
        if tag:
            self.text_input.setText(tag.data)
            self.log(f"Loaded tag {tag_id[:8]}...")
    
    def view_tag_history(self):
        """Show the tag history dialog for the selected tag."""
        selected_items = self.tag_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Tag Selected", "Please select a tag to view its history.")
            return
        
        row = selected_items[0].row()
        tag_id = self.tag_table.item(row, 0).data(Qt.UserRole)
        
        dialog = TagHistoryDialog(tag_id, self)
        dialog.exec()
    
    def manage_tags(self):
        """Open the tag management dialog."""
        # For now, just show a message
        QMessageBox.information(
            self, 
            "Tag Management", 
            "Tag management features will be implemented in a future version."
        )
    
    def toggle_tag_list_visibility(self):
        """Toggle the visibility of the tag list dock widget."""
        self.tag_list_dock.setVisible(self.toggle_tag_list_action.isChecked())
    
    def _generate_tag_id(self, data: str) -> str:
        """Generate a unique ID for a tag based on its content."""
        import hashlib
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.settings_saved.connect(self.apply_settings)
        dialog.exec()
    
    def apply_settings(self, settings):
        """Apply settings from the settings dialog."""
        # Apply interface settings
        if 'interface' in settings:
            # Apply theme if changed
            if 'theme' in settings['interface']:
                self.apply_theme(settings['interface']['theme'])
            
            # Apply font size
            if 'font_size' in settings['interface']:
                font = self.font()
                font.setPointSize(settings['interface']['font_size'])
                self.setFont(font)
            
            # Toggle toolbar and status bar visibility
            if hasattr(self, 'toolbar') and 'show_toolbar' in settings['interface']:
                self.toolbar.setVisible(settings['interface']['show_toolbar'])
            
            if hasattr(self, 'statusBar') and 'show_statusbar' in settings['interface']:
                self.statusBar().setVisible(settings['interface']['show_statusbar'])
        
        # Apply editor settings if available
        if hasattr(self, 'text_editor') and 'editor' in settings:
            editor = self.text_editor
            editor_settings = settings['editor']
            
            if 'word_wrap' in editor_settings:
                editor.setLineWrapMode(editor.WidgetWidth if editor_settings['word_wrap'] else editor.NoWrap)
            
            if 'line_numbers' in editor_settings:
                # Assuming you have a line number area widget
                if hasattr(self, 'line_number_area'):
                    self.line_number_area.setVisible(editor_settings['line_numbers'])
            
            if 'highlight_current_line' in editor_settings:
                editor.highlightCurrentLine(editor_settings['highlight_current_line'])
            
            if 'tab_width' in editor_settings:
                # Set tab stop width (multiply by font metrics for better accuracy)
                metrics = editor.fontMetrics()
                editor.setTabStopDistance(metrics.horizontalAdvance(' ') * editor_settings['tab_width'])
        
        # Apply logging settings
        if 'logging' in settings:
            log_level = settings['logging'].get('level', 'INFO').upper()
            logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
            
            # Configure file logging if enabled
            if settings['logging'].get('to_file', True):
                log_file = settings['logging'].get('file_path', 'nfc_reader.log')
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                logging.getLogger().addHandler(file_handler)
            
        # Apply NFC settings
        if 'nfc' in settings and hasattr(self, 'nfc_thread'):
            # Update NFC reader timeout
            if 'reader_timeout' in settings['nfc']:
                self.nfc_thread.reader_timeout = settings['nfc']['reader_timeout']
                
            # Update auto-connect setting
            if 'auto_connect' in settings['nfc'] and hasattr(self, 'device_panel'):
                self.device_panel.auto_connect = settings['nfc']['auto_connect']
            
        self.log("Settings applied successfully")
        
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application."""
        # This is a basic implementation. You might want to use a stylesheet or a proper theming system.
        if theme_name == "Dark":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QTextEdit, QLineEdit, QComboBox, QSpinBox, QListWidget, QTableWidget {
                    background-color: #3d3d3d;
                    color: #e0e0e0;
                    border: 1px solid #555;
                }
                QMenuBar, QToolBar {
                    background-color: #3d3d3d;
                    color: #e0e0e0;
                }
                QMenuBar::item:selected, QToolBar::item:selected {
                    background-color: #555;
                }
            """)
        elif theme_name == "Light":
            self.setStyleSheet("""
                QMainWindow, QDialog, QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QTextEdit, QLineEdit, QComboBox, QSpinBox, QListWidget, QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                }
            """)
        else:  # System or default
            self.setStyleSheet("")  # Reset to system style
    
    def clear_log(self):
        """Clear the log display."""
        self.log_display.clear()
    
    def apply_settings(self, settings):
        """Apply settings from the settings dialog.
        
        Args:
            settings (dict): Dictionary containing all settings
        """
        try:
            # Apply interface settings
            if 'interface' in settings:
                # Apply theme if changed
                if 'theme' in settings['interface']:
                    self.apply_theme(settings['interface']['theme'])
                
                # Apply font size
                if 'font_size' in settings['interface']:
                    font = self.font()
                    font.setPointSize(settings['interface']['font_size'])
                    self.setFont(font)
                
                # Toggle toolbar and status bar visibility
                if hasattr(self, 'toolbar'):
                    self.toolbar.setVisible(settings['interface'].get('show_toolbar', True))
                
                if hasattr(self, 'statusBar'):
                    self.statusBar().setVisible(settings['interface'].get('show_statusbar', True))
            
            # Apply logging settings
            if 'logging' in settings:
                log_level = settings['logging'].get('level', 'INFO').upper()
                logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
                
                # Configure file logging if enabled
                if settings['logging'].get('to_file', False):
                    log_file = settings['logging'].get('file_path', 'nfc_reader.log')
                    file_handler = logging.FileHandler(log_file)
                    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                    logging.getLogger().addHandler(file_handler)
            
            # Apply NFC settings
            if 'nfc' in settings and hasattr(self, 'nfc_thread'):
                # Update NFC reader timeout
                if 'reader_timeout' in settings['nfc']:
                    self.nfc_thread.reader_timeout = settings['nfc']['reader_timeout']
                
                # Update auto-connect setting
                if 'auto_connect' in settings['nfc'] and hasattr(self, 'device_panel'):
                    self.device_panel.auto_connect = settings['nfc']['auto_connect']
            
            self.log("Settings applied successfully")
            
        except Exception as e:
            self.log(f"Error applying settings: {str(e)}", level="ERROR")
            QMessageBox.critical(self, "Settings Error", f"Failed to apply settings: {str(e)}")
    
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application."""
        try:
            if theme_name == "Dark":
                self.setStyleSheet("""
                    QMainWindow, QDialog, QWidget {
                        background-color: #2d2d2d;
                        color: #e0e0e0;
                    }
                    QTextEdit, QLineEdit, QComboBox, QSpinBox, QListWidget, QTableWidget {
                        background-color: #3d3d3d;
                        color: #e0e0e0;
                        border: 1px solid #555;
                    }
                    QMenuBar, QToolBar {
                        background-color: #3d3d3d;
                        color: #e0e0e0;
                    }
                    QMenuBar::item:selected, QToolBar::item:selected {
                        background-color: #555;
                    }
                """)
            elif theme_name == "Light":
                self.setStyleSheet("""
                    QMainWindow, QDialog, QWidget {
                        background-color: #f0f0f0;
                        color: #000000;
                    }
                    QTextEdit, QLineEdit, QComboBox, QSpinBox, QListWidget, QTableWidget {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #ccc;
                    }
                """)
            else:  # System or default
                self.setStyleSheet("")  # Reset to system style
                
        except Exception as e:
            self.log(f"Error applying theme: {str(e)}", level="ERROR")
    
    def closeEvent(self, event):
        """Handle application close event."""
        self.log("Application shutting down...")
        self.nfc_thread.stop()
        self.device_panel.disconnect_device()
        logging.shutdown()
        event.accept()
    
    def update_reader_status(self, status):
        """Update the status bar with reader connection status."""
        if status == "connected":
            self.statusBar().showMessage("NFC reader connected", 3000)
            self.status_label.setText("Status: Reader connected")
            self.log("NFC reader connected")
        else:
            self.statusBar().showMessage("NFC reader disconnected", 3000)
            self.status_label.setText("Status: Reader disconnected")
            self.log("NFC reader disconnected", "WARNING")
    
    def on_device_connection_changed(self, connected):
        """Handle device connection status changes."""
        if connected:
            self.statusBar().showMessage("Device connected", 3000)
            self.status_label.setText("Status: Device connected")
            self.log("USB device connected")
            
            # Start NFC thread if not already running
            if not self.nfc_thread.isRunning():
                self.nfc_thread.start()
        else:
            self.statusBar().showMessage("Device disconnected", 3000)
            self.status_label.setText("Status: Device disconnected")
            self.log("USB device disconnected", "WARNING")
            
            # Stop NFC operations but keep the thread running
            if hasattr(self.nfc_thread, 'clf') and self.nfc_thread.clf:
                self.nfc_thread.clf.close()
    
    def on_reader_type_changed(self, reader_type):
        """Handle reader type changes."""
        self.log(f"Reader type changed to: {reader_type}")
        
        # Update NFC thread with new reader type
        if hasattr(self, 'device_panel'):
            reader_config = self.device_panel.get_reader_config()
            self.nfc_thread.set_reader_type(reader_type, reader_config)
            
            # Restart NFC thread with new reader type
            if self.nfc_thread.isRunning():
                self.nfc_thread.stop()
            self.nfc_thread.start()
    
    def start_reading(self):
        """Start reading NFC tags."""
        self.nfc_thread.read_mode = True
        self.nfc_thread.write_data = None
        self.statusBar().showMessage("Ready to read tags...", 3000)
        self.log("Ready to read NFC tags")
    
    def start_writing(self, text):
        """Prepare to write to NFC tags."""
        self.nfc_thread.write_data = text
        self.nfc_thread.read_mode = False
        self.statusBar().showMessage("Ready to write - place a writable tag near the reader")
        
    def update_read_progress(self, current: int, total: int) -> None:
        """Update the read progress in the status bar.
        
        Args:
            current: Current number of bytes read
            total: Total number of bytes to read
        """
        if total > 0:
            percent = (current / total) * 100
            self.statusBar().showMessage(f"Reading: {current}/{total} bytes ({percent:.1f}%)")
            
    def update_write_progress(self, current: int, total: int) -> None:
        """Update the write progress in the status bar.
        
        Args:
            current: Current number of bytes written
            total: Total number of bytes to write
        """
        if total > 0:
            percent = (current / total) * 100
            self.statusBar().showMessage(f"Writing: {current}/{total} bytes ({percent:.1f}%)")
            
    def start_writing(self, text):
        """Prepare to write to NFC tags."""
        if not text.strip():
            self.show_error("WARNING", "No text to write")
            return
            
        self.nfc_thread.read_mode = False
        self.nfc_thread.write_data = text
        self.statusBar().showMessage("Ready to write to tags...", 3000)
        self.log(f"Ready to write to NFC tags: {text[:50]}..." if len(text) > 50 else text)

    def run_diagnostics(self):
        """Run NFC diagnostics and show results in a dialog."""
        try:
            from script.nfc_diagnostics import run_diagnostics as run_nfc_diagnostics
            
            # Create a dialog to show diagnostics results
            dialog = QDialog(self)
            dialog.setWindowTitle("NFC Diagnostics")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout()
            
            # Create text area for diagnostics output
            text_area = QTextEdit()
            text_area.setReadOnly(True)
            text_area.setFont(QtGui.QFont("Consolas", 9))
            
            # Add buttons
            button_layout = QHBoxLayout()
            
            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(lambda: self._refresh_diagnostics(text_area))
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(refresh_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            layout.addWidget(QLabel("NFC Diagnostics Results:"))
            layout.addWidget(text_area)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # Run initial diagnostics
            self._refresh_diagnostics(text_area)
            
            dialog.exec()
            
        except ImportError:
            QMessageBox.warning(self, "Diagnostics Error", 
                              "NFC diagnostics module not found. Please ensure script/nfc_diagnostics.py exists.")
        except Exception as e:
            QMessageBox.critical(self, "Diagnostics Error", 
                               f"Failed to run NFC diagnostics: {str(e)}")
    
    def _refresh_diagnostics(self, text_area):
        """Refresh diagnostics results in the text area."""
        try:
            import io
            import sys
            from script.nfc_diagnostics import run_diagnostics
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                run_diagnostics()
                output = captured_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            text_area.setPlainText(output)
            
        except Exception as e:
            text_area.setPlainText(f"Error running diagnostics: {str(e)}\n\n{traceback.format_exc()}")

def main():
    # Set application metadata
    app = QApplication(sys.argv)
    app.setApplicationName("NFC Reader/Writer")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Nsfr750")
    app.setOrganizationDomain("github.com/Nsfr750")
    
    # Enable high DPI scaling - use modern attributes
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Set modern style for better appearance
    app.setStyle('Fusion')
    
    # Create and show main window
    window = NFCApp()
    window.show()
    
    # Log application start
    window.log(f"{APP_NAME} v{__version__} started")
    window.log(f"Copyright {AUTHOR} - {LICENSE}")
    
    # Start the NFC reader thread
    window.nfc_thread.start()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
