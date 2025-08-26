#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USB Device Management Panel for NFC Reader/Writer
"""

import serial.tools.list_ports
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt, Signal, Slot
import serial

class DevicePanel(QGroupBox):
    """Panel for managing USB serial devices."""
    
    # Signal emitted when device connection status changes
    device_connected = Signal(bool)
    
    def __init__(self, parent=None):
        """Initialize the device panel."""
        super().__init__("USB Device", parent)
        self.serial_port = None
        self.is_connected = False
        self.init_ui()
        self.refresh_ports()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
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
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.port_combo.addItem("No ports found")
            self.connect_btn.setEnabled(False)
        else:
            for port in sorted(ports):
                self.port_combo.addItem(f"{port.device} - {port.description}", port.device)
            self.connect_btn.setEnabled(True)
    
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
            
            # Try to get device info
            self.update_device_info()
            
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to {port}:\n{str(e)}")
    
    def disconnect_device(self):
        """Disconnect from the current serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None
        self.is_connected = False
        self.update_ui_disconnected()
        self.device_connected.emit(False)
    
    def update_device_info(self):
        """Update the device information display."""
        if not self.serial_port or not self.serial_port.is_open:
            self.info_label.setText("No device connected")
            return
        
        try:
            port = self.port_combo.currentText().split(' - ')[0]
            info = f"Connected to: {port}\n"
            info += f"Baudrate: {self.serial_port.baudrate}\n"
            
            # Try to read device info (implement according to your device's protocol)
            # This is a placeholder - modify according to your device's protocol
            try:
                # Example: Send a command to get device info
                # self.serial_port.write(b'\r\n')
                # response = self.serial_port.read_until(b'\n').decode().strip()
                # info += f"Device: {response}"
                pass
            except Exception as e:
                info += "Could not read device info"
            
            self.info_label.setText(info)
            
        except Exception as e:
            self.info_label.setText(f"Error reading device info: {str(e)}")
    
    def update_ui_connected(self):
        """Update UI when device is connected."""
        self.connect_btn.setText("Disconnect")
        self.status_label.setText("Status: Connected")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.port_combo.setEnabled(False)
        self.refresh_btn.setEnabled(False)
    
    def update_ui_disconnected(self):
        """Update UI when device is disconnected."""
        self.connect_btn.setText("Connect")
        self.status_label.setText("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.port_combo.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.info_label.setText("No device connected")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.disconnect_device()
        super().closeEvent(event)

    def get_serial_connection(self):
        """Get the active serial connection.
        
        Returns:
            serial.Serial or None: The active serial connection or None if not connected.
        """
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            return self.serial_port
        return None
