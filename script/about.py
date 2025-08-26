#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
About dialog for NFC Reader/Writer Application
"""

from PySide6.QtWidgets import (QMessageBox, QVBoxLayout, QHBoxLayout, 
                             QLabel, QWidget)
from PySide6 import QtGui, QtCore
import os

from script.version import __version__, APP_NAME, APP_DESCRIPTION, AUTHOR, LICENSE

def show_about_dialog(parent):
    """Show the about dialog with application information and logo."""
    # Create a custom dialog
    msg = QMessageBox(parent)
    msg.setWindowTitle("About NFC Reader/Writer")
    
    # Set application icon if available
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
    if os.path.exists(icon_path):
        msg.setWindowIcon(QtGui.QIcon(icon_path))
        
        # Create a widget for custom content
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(5)  # Minimal spacing between logo and text
        
        # Add logo (96x96)
        logo_label = QLabel()
        pixmap = QtGui.QPixmap(icon_path).scaled(
            96, 96, 
            QtCore.Qt.KeepAspectRatio, 
            QtCore.Qt.SmoothTransformation
        )
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.addWidget(logo_label, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        
        # Add text content with minimal styling
        about_text = f"""
        <div style="margin: 0; padding: 0; text-align: left;">
            <h2 style="margin: 0 0 5px 0; padding: 0; font-size: 14pt;">{APP_NAME}</h2>
            <p style="margin: 0 0 3px 0; padding: 0;">Version: {__version__}</p>
            <p style="margin: 0 0 10px 0; padding: 0; font-size: 9pt;">{APP_DESCRIPTION}</p>
            <p style="margin: 0 0 3px 0; padding: 0; font-size: 9pt;">© 2025 {AUTHOR}. All rights reserved.</p>
            <p style="margin: 0 0 3px 0; padding: 0; font-size: 9pt;">Licensed under {LICENSE}</p>
            <p style="margin: 5px 0 3px 0; padding: 0;">
                <a href='https://github.com/Nsfr750' style="text-decoration: none; color: #0066cc;">GitHub</a> | 
                <a href='https://discord.gg/ryqNeuRYjD' style="text-decoration: none; color: #0066cc;">Discord</a>
            </p>
        </div>
        """
        
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        
        text_label = QLabel(about_text)
        text_label.setTextFormat(QtCore.Qt.RichText)
        text_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        text_label.setOpenExternalLinks(True)
        text_label.setStyleSheet("QLabel { margin: 0; padding: 0; }")
        
        text_layout.addWidget(text_label)
        text_layout.addStretch()
        
        layout.addWidget(text_widget, 1)
        
        # Set the custom widget as the main widget
        msg.layout().setContentsMargins(10, 10, 10, 10)  # Add some padding around the dialog
        msg.layout().addWidget(widget, 0, 0, 1, msg.layout().columnCount())
    else:
        # Fallback to simple text if no logo
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p>Version: {__version__}</p>
        <p>{APP_DESCRIPTION}</p>
        <p>© 2025 {AUTHOR}. All rights reserved.</p>
        <p>Licensed under {LICENSE}</p>
        <p>GitHub: <a href='https://github.com/Nsfr750'>Nsfr750</a></p>
        <p>Discord: <a href='https://discord.gg/ryqNeuRYjD'>Join our community</a></p>
        """
        msg.setText(about_text)
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
    
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setDefaultButton(QMessageBox.Ok)
    
    return msg.exec_()
