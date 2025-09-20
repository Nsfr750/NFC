#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for Reader Selection Functionality

This script tests the reader selection dropdown and integration with the NFC thread.
"""

import sys
import os
import logging
from pathlib import Path

# Add the script directory to the path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import QTimer, QDateTime

# Import custom modules
from script.device_panel import DevicePanel
from script.nfc_thread import NFCThread

# Set up basic logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReaderSelectionTestWindow(QMainWindow):
    """Test window for reader selection functionality."""
    
    def __init__(self):
        """Initialize the test window."""
        super().__init__()
        self.nfc_thread = None
        self.init_ui()
        self.setup_nfc_thread()
        self.setup_connections()
        
        logger.info("Reader Selection Test Window initialized")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Reader Selection Test")
        self.setGeometry(100, 100, 600, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create title
        title_label = QLabel("Reader Selection Test")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title_label)
        
        # Create device panel
        self.device_panel = DevicePanel()
        main_layout.addWidget(self.device_panel)
        
        # Create status display
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
        main_layout.addWidget(self.status_label)
        
        # Create test buttons
        test_layout = QVBoxLayout()
        
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_connection_btn)
        
        self.test_reader_info_btn = QPushButton("Get Reader Info")
        self.test_reader_info_btn.clicked.connect(self.test_reader_info)
        test_layout.addWidget(self.test_reader_info_btn)
        
        self.test_detection_btn = QPushButton("Test Auto-Detection")
        self.test_detection_btn.clicked.connect(self.test_auto_detection)
        test_layout.addWidget(self.test_detection_btn)
        
        main_layout.addLayout(test_layout)
        
        # Create log display
        self.log_label = QLabel("Log:")
        self.log_label.setStyleSheet("font-weight: bold; padding: 5px;")
        main_layout.addWidget(self.log_label)
        
        self.log_display = QLabel()
        self.log_display.setStyleSheet("background-color: #2b2b2b; color: #ffffff; padding: 10px; font-family: monospace;")
        self.log_display.setWordWrap(True)
        self.log_display.setAlignment(Qt.AlignTop)
        self.log_display.setMinimumHeight(150)
        main_layout.addWidget(self.log_display)
    
    def setup_nfc_thread(self):
        """Set up the NFC thread."""
        self.nfc_thread = NFCThread()
        self.nfc_thread.start()
        self.log("NFC thread started")
    
    def setup_connections(self):
        """Set up signal connections."""
        # Device panel signals
        self.device_panel.device_connected.connect(self.on_device_connected)
        self.device_panel.reader_type_changed.connect(self.on_reader_type_changed)
        
        # NFC thread signals
        self.nfc_thread.connection_status.connect(self.on_nfc_connection_status)
        self.nfc_thread.error_occurred.connect(self.on_nfc_error)
        self.nfc_thread.reader_info.connect(self.on_reader_info)
    
    def log(self, message):
        """Add a message to the log display."""
        current_text = self.log_display.text()
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        new_text = f"[{timestamp}] {message}\n"
        self.log_display.setText(current_text + new_text)
        
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_device_connected(self, connected):
        """Handle device connection status change."""
        if connected:
            self.status_label.setText("Status: Device Connected")
            self.status_label.setStyleSheet("padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;")
            self.log("✅ Device connected")
            
            # Update NFC thread with selected port and reader type
            serial_conn = self.device_panel.get_serial_connection()
            if serial_conn:
                port_name = serial_conn.port
                self.nfc_thread.set_selected_port(port_name)
                self.log(f"📍 Selected port: {port_name}")
            
            reader_type = self.device_panel.get_selected_reader_type()
            reader_config = self.device_panel.get_reader_config()
            self.nfc_thread.set_reader_type(reader_type, reader_config)
            self.log(f"🔧 Reader type: {reader_type}")
            
            # Restart NFC thread with new parameters
            self.restart_nfc_thread()
        else:
            self.status_label.setText("Status: Device Disconnected")
            self.status_label.setStyleSheet("padding: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")
            self.log("❌ Device disconnected")
            
            # Clear selected port and restart NFC thread
            self.nfc_thread.set_selected_port(None)
            self.restart_nfc_thread()
    
    def on_reader_type_changed(self, reader_type):
        """Handle reader type change."""
        self.log(f"🔄 Reader type changed to: {reader_type}")
        
        # Update NFC thread with new reader type
        reader_config = self.device_panel.get_reader_config()
        self.nfc_thread.set_reader_type(reader_type, reader_config)
        
        # Restart NFC thread with new reader type
        self.restart_nfc_thread()
    
    def on_nfc_connection_status(self, status):
        """Handle NFC connection status updates."""
        self.log(f"📡 NFC Status: {status}")
    
    def on_nfc_error(self, error):
        """Handle NFC errors."""
        self.log(f"⚠️  NFC Error: {error}")
        self.status_label.setText(f"Status: Error - {error}")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")
    
    def on_reader_info(self, info):
        """Handle reader information updates."""
        self.log(f"ℹ️  Reader Info: {info}")
        
        # Update status with reader info
        if info.get('vendor') and info.get('product'):
            status_text = f"Reader: {info['vendor']} {info['product']}"
            if info.get('vid') and info.get('pid'):
                status_text += f" (VID: 0x{info['vid']:04x}, PID: 0x{info['pid']:04x})"
            self.status_label.setText(f"Status: {status_text}")
            self.status_label.setStyleSheet("padding: 10px; background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460;")
    
    def restart_nfc_thread(self):
        """Restart the NFC thread with new parameters."""
        if self.nfc_thread and self.nfc_thread.isRunning():
            self.nfc_thread.stop()
        
        # Start the thread again
        self.nfc_thread.start()
        self.log("🔄 NFC thread restarted with new parameters")
    
    def test_connection(self):
        """Test the current connection."""
        self.log("🧪 Testing connection...")
        
        if self.nfc_thread.is_connected():
            reader_name = self.nfc_thread.get_reader_name()
            self.log(f"✅ Connected to: {reader_name}")
        else:
            self.log("❌ Not connected to any reader")
    
    def test_reader_info(self):
        """Test getting reader information."""
        self.log("🧪 Testing reader info...")
        
        reader_type = self.device_panel.get_selected_reader_type()
        reader_config = self.device_panel.get_reader_config()
        
        self.log(f"Selected reader type: {reader_type}")
        if reader_config:
            self.log(f"Reader config: {reader_config}")
        else:
            self.log("No reader configuration available")
    
    def test_auto_detection(self):
        """Test auto-detection of readers."""
        self.log("🧪 Testing auto-detection...")
        
        # Switch to auto-detect mode
        index = self.device_panel.reader_combo.findData('Auto-Detect')
        if index >= 0:
            self.device_panel.reader_combo.setCurrentIndex(index)
            self.log("🔄 Switched to Auto-Detect mode")
        else:
            self.log("❌ Auto-Detect option not found")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.log("🔚 Closing test application...")
        
        # Stop NFC thread
        if self.nfc_thread:
            self.nfc_thread.stop()
        
        # Disconnect device
        if self.device_panel:
            self.device_panel.disconnect_device()
        
        event.accept()

def main():
    """Main test application entry point."""
    try:
        # Create application
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show test window
        window = ReaderSelectionTestWindow()
        window.show()
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Test application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
