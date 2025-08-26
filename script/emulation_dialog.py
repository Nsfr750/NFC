"""
Emulation dialog for NFC tag emulation.

This module provides a dialog for configuring and controlling NFC tag emulation.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QCheckBox, QSpinBox, QMessageBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor
import json

class EmulationDialog(QDialog):
    """Dialog for configuring and controlling NFC tag emulation."""
    
    # Signal emitted when emulation should start
    start_emulation = Signal(dict, str)  # ndef_data, tag_type
    
    # Signal emitted when emulation should stop
    stop_emulation = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NFC Tag Emulation")
        self.setMinimumSize(600, 500)
        
        # Initialize UI
        self.init_ui()
        
        # Emulation state
        self._is_emulating = False
        
        # Set up connections
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Text tab
        self.text_tab = QWidget()
        self.setup_text_tab()
        self.tab_widget.addTab(self.text_tab, "Text")
        
        # URI tab
        self.uri_tab = QWidget()
        self.setup_uri_tab()
        self.tab_widget.addTab(self.uri_tab, "URI")
        
        # Smart Poster tab
        self.smart_poster_tab = QWidget()
        self.setup_smart_poster_tab()
        self.tab_widget.addTab(self.smart_poster_tab, "Smart Poster")
        
        # Raw NDEF tab
        self.raw_tab = QWidget()
        self.setup_raw_tab()
        self.tab_widget.addTab(self.raw_tab, "Raw NDEF")
        
        layout.addWidget(self.tab_widget)
        
        # Tag type selection
        tag_type_group = QGroupBox("Tag Type")
        tag_type_layout = QHBoxLayout()
        
        self.tag_type_combo = QComboBox()
        self.tag_type_combo.addItems([
            "Type 1 Tag",
            "Type 2 Tag",
            "Type 3 Tag",
            "Type 4 Tag",
            "MIFARE Classic",
            "MIFARE Ultralight"
        ])
        self.tag_type_combo.setCurrentText("Type 4 Tag")
        
        tag_type_layout.addWidget(QLabel("Emulate as:"))
        tag_type_layout.addWidget(self.tag_type_combo)
        tag_type_layout.addStretch()
        tag_type_group.setLayout(tag_type_layout)
        
        layout.addWidget(tag_type_group)
        
        # Status display
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Emulation")
        self.start_button.setStyleSheet("QPushButton { padding: 8px 16px; font-weight: bold; }")
        
        self.stop_button = QPushButton("Stop Emulation")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("QPushButton { padding: 8px 16px; }")
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def setup_text_tab(self):
        """Set up the text tab."""
        layout = QVBoxLayout()
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to emulate...")
        self.text_input.setAcceptRichText(False)
        
        # Encoding selection
        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel("Encoding:"))
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems([
            "UTF-8",
            "UTF-16 (Big Endian)",
            "UTF-16 (Little Endian)",
            "ISO-8859-1 (Latin-1)",
            "ASCII",
            "Windows-1252",
            "Shift-JIS",
            "EUC-JP",
            "GBK (Simplified Chinese)",
            "Big5 (Traditional Chinese)",
            "EUC-KR (Korean)",
            "KOI8-R (Cyrillic)",
            "ISO-8859-2 (Latin-2)",
            "ISO-8859-5 (Cyrillic)",
            "ISO-8859-7 (Greek)",
            "ISO-8859-8 (Hebrew)",
            "ISO-8859-9 (Turkish)",
            "ISO-8859-15 (Latin-9)"
        ])
        self.encoding_combo.setCurrentText("UTF-8")
        
        encoding_layout.addWidget(self.encoding_combo)
        encoding_layout.addStretch()
        
        layout.addLayout(encoding_layout)
        layout.addWidget(self.text_input)
        
        self.text_tab.setLayout(layout)
    
    def setup_uri_tab(self):
        """Set up the URI tab."""
        layout = QFormLayout()
        
        # URI input
        self.uri_input = QLineEdit()
        self.uri_input.setPlaceholderText("https://example.com")
        
        # URI type
        self.uri_type_combo = QComboBox()
        self.uri_type_combo.addItems([
            "http://www.",
            "https://www.",
            "http://",
            "https://",
            "tel:",
            "mailto:",
            "sms:",
            "smsto:",
            "geo:",
            "nfc:",
            "urn:",
            "custom"
        ])
        self.uri_type_combo.setCurrentText("https://www.")
        
        layout.addRow("URI Type:", self.uri_type_combo)
        layout.addRow("URI:", self.uri_input)
        
        # Custom URI type
        self.custom_uri_type = QLineEdit()
        self.custom_uri_type.setPlaceholderText("Enter custom URI type (e.g., custom:)")
        self.custom_uri_type.setVisible(False)
        layout.addRow("", self.custom_uri_type)
        
        # Connect signals
        self.uri_type_combo.currentTextChanged.connect(self.on_uri_type_changed)
        
        self.uri_tab.setLayout(layout)
    
    def setup_smart_poster_tab(self):
        """Set up the smart poster tab."""
        layout = QFormLayout()
        
        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        
        # URI
        self.poster_uri_input = QLineEdit()
        self.poster_uri_input.setPlaceholderText("https://example.com")
        
        # Action
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "Default Action",
            "Open for Editing",
            "Open for Viewing",
            "Execute/Launch",
            "Open Browser"
        ])
        
        # Language
        self.language_input = QLineEdit("en")
        
        layout.addRow("Title:", self.title_input)
        layout.addRow("URI:", self.poster_uri_input)
        layout.addRow("Action:", self.action_combo)
        layout.addRow("Language:", self.language_input)
        
        self.smart_poster_tab.setLayout(layout)
    
    def setup_raw_tab(self):
        """Set up the raw NDEF tab."""
        layout = QVBoxLayout()
        
        # Raw NDEF input
        self.raw_ndef_input = QTextEdit()
        self.raw_ndef_input.setPlaceholderText(
            "Enter NDEF records in JSON format, e.g.:\n"
            "[\n"
            '  {\n"type": "text",\n"text": "Hello, NFC!"\n  },\n'
            '  {\n"type": "uri",\n"uri": "https://example.com"\n  }\n'
            "]"
        )
        self.raw_ndef_input.setAcceptRichText(False)
        
        # Format button
        format_btn = QPushButton("Format JSON")
        format_btn.clicked.connect(self.format_json)
        
        layout.addWidget(QLabel("NDEF Records (JSON format):"))
        layout.addWidget(self.raw_ndef_input)
        layout.addWidget(format_btn, 0, Qt.AlignRight)
        
        self.raw_tab.setLayout(layout)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.start_button.clicked.connect(self.on_start_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)
    
    def on_uri_type_changed(self, text):
        """Handle changes to the URI type combo box."""
        self.custom_uri_type.setVisible(text == "custom")
    
    def format_json(self):
        """Format the JSON in the raw NDEF input."""
        try:
            text = self.raw_ndef_input.toPlainText().strip()
            if not text:
                return
                
            # Parse and pretty-print JSON
            data = json.loads(text)
            formatted = json.dumps(data, indent=2)
            self.raw_ndef_input.setPlainText(formatted)
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "Invalid JSON",
                f"Failed to parse JSON: {e}"
            )
    
    def on_start_clicked(self):
        """Handle start emulation button click."""
        try:
            # Get the current tab index
            tab_index = self.tab_widget.currentIndex()
            
            # Prepare NDEF data based on the current tab
            ndef_data = None
            
            if tab_index == 0:  # Text tab
                text = self.text_input.toPlainText().strip()
                if not text:
                    QMessageBox.warning(self, "Error", "Please enter some text to emulate.")
                    return
                
                encoding = self.encoding_combo.currentText().split()[0].lower()  # Get encoding name
                ndef_data = {
                    "type": "text",
                    "text": text,
                    "encoding": encoding
                }
                
            elif tab_index == 1:  # URI tab
                uri = self.uri_input.text().strip()
                if not uri:
                    QMessageBox.warning(self, "Error", "Please enter a URI to emulate.")
                    return
                
                uri_type = self.uri_type_combo.currentText()
                if uri_type == "custom":
                    uri_type = self.custom_uri_type.text().strip()
                
                # Add the URI type if not already present
                if not uri.startswith(uri_type):
                    uri = uri_type + uri
                
                ndef_data = {
                    "type": "uri",
                    "uri": uri
                }
                
            elif tab_index == 2:  # Smart Poster tab
                title = self.title_input.text().strip()
                uri = self.poster_uri_input.text().strip()
                
                if not title and not uri:
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "Please enter at least a title or a URI for the smart poster."
                    )
                    return
                
                action_map = {
                    "Default Action": None,
                    "Open for Editing": "edit",
                    "Open for Viewing": "view",
                    "Execute/Launch": "exec",
                    "Open Browser": "browse"
                }
                
                action = action_map.get(self.action_combo.currentText())
                language = self.language_input.text().strip() or "en"
                
                ndef_data = {
                    "type": "smart-poster",
                    "title": title,
                    "uri": uri,
                    "action": action,
                    "language": language
                }
                
            elif tab_index == 3:  # Raw NDEF tab
                raw_text = self.raw_ndef_input.toPlainText().strip()
                if not raw_text:
                    QMessageBox.warning(self, "Error", "Please enter NDEF records in JSON format.")
                    return
                
                try:
                    ndef_data = json.loads(raw_text)
                    if not isinstance(ndef_data, list):
                        ndef_data = [ndef_data]
                except json.JSONDecodeError as e:
                    QMessageBox.warning(
                        self,
                        "Invalid JSON",
                        f"Failed to parse NDEF records: {e}"
                    )
                    return
            
            if ndef_data is not None:
                # Get the selected tag type
                tag_type = self.tag_type_combo.currentText().lower().replace(" ", "")
                
                # Emit the start signal with the NDEF data and tag type
                self.start_emulation.emit(ndef_data, tag_type)
                
                # Update UI
                self._is_emulating = True
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.status_label.setText("Status: Emulating tag...")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start emulation: {str(e)}"
            )
    
    def on_stop_clicked(self):
        """Handle stop emulation button click."""
        self.stop_emulation.emit()
        self._is_emulating = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Ready")
        self.status_label.setStyleSheet("font-weight: bold;")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self._is_emulating:
            reply = QMessageBox.question(
                self,
                "Stop Emulation",
                "Emulation is still active. Do you want to stop it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.on_stop_clicked()
            else:
                event.ignore()
                return
        
        event.accept()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = EmulationDialog()
    dialog.show()
    
    sys.exit(app.exec())
