#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Help Dialog for NFC Reader/Writer
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                             QDialogButtonBox, QLabel)
from PySide6.QtCore import Qt
import os

class HelpDialog(QDialog):
    """Help dialog displaying application documentation."""
    
    def __init__(self, parent=None):
        """Initialize the help dialog."""
        super().__init__(parent)
        self.setWindowTitle("Help - NFC Reader/Writer")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Help content
        help_text = """
        <h2>NFC Reader/Writer - Help</h2>
        
        <h3>Getting Started</h3>
        <p>Welcome to NFC Reader/Writer. This application allows you to read from and write to NFC tags.</p>
        
        <h3>Connecting a Device</h3>
        <ol>
            <li>Connect your NFC reader/writer device via USB</li>
            <li>Select the correct port from the USB Device panel</li>
            <li>Click "Connect" to establish the connection</li>
        </ol>
        
        <h3>Reading NFC Tags</h3>
        <ol>
            <li>Ensure a device is connected</li>
            <li>Click the "Read" button in the toolbar</li>
            <li>Hold an NFC tag near the reader</li>
            <li>Tag data will appear in the log area</li>
        </ol>
        
        <h3>Writing to NFC Tags</h3>
        <ol>
            <li>Ensure a device is connected</li>
            <li>Click the "Write" button in the toolbar</li>
            <li>Enter the text you want to write in the input field</li>
            <li>Hold an NFC tag near the reader</li>
            <li>The application will write the data and verify the write</li>
        </ol>
        
        <h3>Keyboard Shortcuts</h3>
        <ul>
            <li><b>Ctrl+R</b>: Start reading tags</li>
            <li><b>Ctrl+W</b>: Start writing to tags</li>
            <li><b>Ctrl+Q</b>: Quit application</li>
            <li><b>F1</b>: Show this help</li>
        </ul>
        
        <h3>Troubleshooting</h3>
        <p>If you experience issues:</p>
        <ul>
            <li>Ensure the device is properly connected</li>
            <li>Check that no other application is using the device</li>
            <li>Try disconnecting and reconnecting the device</li>
            <li>Restart the application if problems persist</li>
        </ul>
        
        <p>For additional support, please visit our 
        <a href="https://github.com/Nsfr750/NFC-Reader-App">GitHub repository</a>.</p>
        """
        
        # Create help text display
        help_display = QTextEdit()
        help_display.setReadOnly(True)
        help_display.setHtml(help_text)
        help_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        """)
        
        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        
        # Add widgets to layout
        layout.addWidget(help_display)
        layout.addWidget(button_box)
        
        # Set focus to the close button
        button_box.button(QDialogButtonBox.Close).setFocus()
