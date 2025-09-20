#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USB Device Management Panel for NFC Reader/Writer
"""

import serial.tools.list_ports
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QMessageBox,
                             QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
import serial

class DevicePanel(QGroupBox):
    """Panel for managing USB serial devices."""
    
    # Signal emitted when device connection status changes
    device_connected = Signal(bool)
    
    # Signal emitted when reader type changes
    reader_type_changed = Signal(str)
    
    # Supported reader types with their configurations
    READER_TYPES = {
        'Auto-Detect': {
            'description': 'Automatically detect the reader type',
            'vid_pid': None,
            'backend': 'auto'
        },
        'ACR122U': {
            'description': 'ACS ACR122U NFC Reader',
            'vid_pid': [(0x072F, 0x2200)],  # VID:PID for ACR122U
            'backend': 'pcsc'
        },
        'PN532': {
            'description': 'NXP PN532 NFC Reader',
            'vid_pid': [(0x2341, 0x0043), (0x0403, 0x6001)],  # Common PN532 VID:PID
            'backend': 'usb'
        },
        'NS106': {
            'description': 'Kadongli NS106 Dual Frequency Reader',
            'vid_pid': [(0x072F, 0x2200)],  # VID:PID for NS106
            'backend': 'usb'
        },
        'RC522': {
            'description': 'MFRC522 RFID Reader',
            'vid_pid': [(0x2341, 0x0043)],  # Common Arduino-based RC522
            'backend': 'uart'
        },
        'PC/SC': {
            'description': 'Generic PC/SC Reader',
            'vid_pid': None,
            'backend': 'pcsc'
        }
    }
    
    def __init__(self, parent=None):
        """Initialize the device panel."""
        super().__init__("USB Device", parent)
        self.serial_port = None
        self.is_connected = False
        self.current_reader_type = 'Auto-Detect'
        self.init_ui()
        self.refresh_ports()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Reader type selection
        reader_layout = QHBoxLayout()
        reader_layout.addWidget(QLabel("Reader Type:"))
        
        self.reader_combo = QComboBox()
        self.reader_combo.setMinimumWidth(200)
        for reader_type, config in self.READER_TYPES.items():
            self.reader_combo.addItem(f"{reader_type} - {config['description']}", reader_type)
        self.reader_combo.currentTextChanged.connect(self.on_reader_type_changed)
        reader_layout.addWidget(self.reader_combo)
        
        layout.addLayout(reader_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        port_layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Refresh available ports")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(port_layout)
        
        # Connection status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Connection button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        # Device info
        self.info_label = QLabel("No device connected")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Reader-specific info
        self.reader_info_label = QLabel("")
        self.reader_info_label.setWordWrap(True)
        self.reader_info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.reader_info_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Update reader info
        self.update_reader_info()
    
    def on_reader_type_changed(self, reader_type):
        """Handle reader type selection change."""
        self.current_reader_type = reader_type
        self.reader_type_changed.emit(reader_type)
        self.update_reader_info()
        self.refresh_ports()  # Refresh ports to filter by reader type
    
    def update_reader_info(self):
        """Update the reader-specific information display."""
        if self.current_reader_type in self.READER_TYPES:
            config = self.READER_TYPES[self.current_reader_type]
            info_text = f"Reader: {config['description']}\n"
            info_text += f"Backend: {config['backend']}"
            
            if config['vid_pid']:
                vid_pid_text = ", ".join([f"VID: 0x{vid:04x}, PID: 0x{pid:04x}" for vid, pid in config['vid_pid']])
                info_text += f"\nExpected IDs: {vid_pid_text}"
            
            self.reader_info_label.setText(info_text)
        else:
            self.reader_info_label.setText("")
    
    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            self.port_combo.addItem("No ports found")
            self.connect_btn.setEnabled(False)
            return
        
        # Filter ports based on selected reader type
        filtered_ports = self.filter_ports_by_reader_type(ports)
        
        if not filtered_ports:
            self.port_combo.addItem("No compatible ports found")
            self.connect_btn.setEnabled(False)
        else:
            for port in sorted(filtered_ports, key=lambda p: p.device):
                display_text = f"{port.device} - {port.description}"
                if port.vid and port.pid:
                    display_text += f" (VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x})"
                self.port_combo.addItem(display_text, port.device)
            self.connect_btn.setEnabled(True)
    
    def filter_ports_by_reader_type(self, ports):
        """Filter ports based on the selected reader type."""
        if self.current_reader_type == 'Auto-Detect':
            # Return all ports for auto-detect
            return ports
        
        if self.current_reader_type not in self.READER_TYPES:
            return ports
        
        config = self.READER_TYPES[self.current_reader_type]
        if not config['vid_pid']:
            # No specific VID:PID filtering needed
            return ports
        
        # Filter by VID:PID
        filtered_ports = []
        for port in ports:
            if port.vid and port.pid:
                for vid, pid in config['vid_pid']:
                    if port.vid == vid and port.pid == pid:
                        filtered_ports.append(port)
                        break
        
        return filtered_ports
    
    @Slot()
    def toggle_connection(self):
        """Toggle connection to the selected serial port."""
        if self.is_connected:
            self.disconnect_device()
        else:
            self.connect_device()
    
    def connect_device(self):
        """Connect to the selected serial port."""
        if self.port_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Error", "No port selected")
            return
        
        port = self.port_combo.currentData()
        if not port:
            QMessageBox.warning(self, "Error", "Invalid port selection")
            return
        
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=115200,  # Default baudrate, can be made configurable
                timeout=1
            )
            self.is_connected = True
            self.update_ui_connected()
            self.device_connected.emit(True)
            
            # Update device info
            selected_port = None
            for p in serial.tools.list_ports.comports():
                if p.device == port:
                    selected_port = p
                    break
            
            if selected_port:
                device_info = f"Connected to: {selected_port.description}\n"
                device_info += f"Port: {selected_port.device}\n"
                if selected_port.manufacturer:
                    device_info += f"Manufacturer: {selected_port.manufacturer}\n"
                if selected_port.product:
                    device_info += f"Product: {selected_port.product}\n"
                if selected_port.vid and selected_port.pid:
                    device_info += f"VID: 0x{selected_port.vid:04x}, PID: 0x{selected_port.pid:04x}\n"
                if selected_port.serial_number:
                    device_info += f"Serial: {selected_port.serial_number}"
                
                self.info_label.setText(device_info)
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to {port}: {str(e)}")
            self.is_connected = False
            self.update_ui_disconnected()
    
    def disconnect_device(self):
        """Disconnect from the current serial port."""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except Exception as e:
                logging.error(f"Error closing serial port: {str(e)}")
        
        self.serial_port = None
        self.is_connected = False
        self.update_ui_disconnected()
        self.device_connected.emit(False)
        self.info_label.setText("No device connected")
    
    def update_device_info(self):
        """Update the device information display."""
        if self.is_connected and self.serial_port:
            # Get current port info
            port_name = self.serial_port.port
            try:
                for port in serial.tools.list_ports.comports():
                    if port.device == port_name:
                        device_info = f"Device: {port.description}\n"
                        device_info += f"Port: {port.device}\n"
                        if port.manufacturer:
                            device_info += f"Manufacturer: {port.manufacturer}\n"
                        if port.product:
                            device_info += f"Product: {port.product}\n"
                        if port.vid and port.pid:
                            device_info += f"VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}\n"
                        if port.serial_number:
                            device_info += f"Serial: {port.serial_number}"
                        
                        self.info_label.setText(device_info)
                        break
            except Exception as e:
                self.info_label.setText(f"Connected to {port_name}\nError getting device info: {str(e)}")
        else:
            self.info_label.setText("No device connected")
    
    def update_ui_connected(self):
        """Update UI when device is connected."""
        self.status_label.setText("Status: Connected")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.connect_btn.setText("Disconnect")
        self.port_combo.setEnabled(False)
        self.reader_combo.setEnabled(False)
        self.refresh_btn.setEnabled(False)
    
    def update_ui_disconnected(self):
        """Update UI when device is disconnected."""
        self.status_label.setText("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.connect_btn.setText("Connect")
        self.port_combo.setEnabled(True)
        self.reader_combo.setEnabled(True)
        self.refresh_btn.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.disconnect_device()
        super().closeEvent(event)
    
    def get_serial_connection(self):
        """Get the active serial connection.
        
        Returns:
            serial.Serial or None: The active serial connection or None if not connected.
        """
        return self.serial_port
    
    def get_selected_reader_type(self):
        """Get the currently selected reader type.
        
        Returns:
            str: The selected reader type.
        """
        return self.current_reader_type
    
    def get_reader_config(self):
        """Get the configuration for the selected reader type.
        
        Returns:
            dict: The reader configuration or None if not found.
        """
        return self.READER_TYPES.get(self.current_reader_type)
