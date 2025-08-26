"""
Progress dialog for long-running NFC operations.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QProgressBar, 
                             QLabel, QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer

class ProgressDialog(QDialog):
    """A dialog that shows progress for NFC operations."""
    
    def __init__(self, title="Operation in Progress", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
        # Auto-close timer
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.accept)
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Button box
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_box.addStretch()
        button_box.addWidget(self.cancel_button)
        
        layout.addLayout(button_box)
    
    def update_progress(self, current, total):
        """Update the progress bar and status."""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.status_label.setText(f"Processed {current} of {total} bytes ({percent}%)")
        else:
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
    
    def set_status(self, message):
        """Update the status message."""
        self.status_label.setText(message)
    
    def auto_close(self, delay_ms=2000):
        """Automatically close the dialog after a delay."""
        self.auto_close_timer.start(delay_ms)
    
    def closeEvent(self, event):
        """Handle the close event."""
        self.auto_close_timer.stop()
        super().closeEvent(event)
