"""
Tag History Dialog for NFC Reader/Writer application.

This module provides a dialog to view and manage the version history of NFC tags.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QHeaderView, QTextEdit, QSplitter, QMessageBox)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QTextCursor

class TagHistoryDialog(QDialog):
    """Dialog to display and manage tag version history."""
    
    def __init__(self, tag_id: str, parent=None):
        """Initialize the tag history dialog.
        
        Args:
            tag_id: The ID of the tag to show history for
            parent: Parent widget
        """
        super().__init__(parent)
        self.tag_id = tag_id
        self.setWindowTitle(f"Tag History - {tag_id}")
        self.setMinimumSize(800, 600)
        
        # Import here to avoid circular imports
        from script.tag_database import tag_db
        self.tag_db = tag_db
        
        # Set up the UI
        self.init_ui()
        
        # Load the tag history
        self.load_history()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create a splitter for the layout
        splitter = QSplitter(Qt.Vertical)
        
        # History table (top)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Version", "Date", "Type", "Size"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Data view (bottom)
        self.data_view = QTextEdit()
        self.data_view.setReadOnly(True)
        self.data_view.setFontFamily("Courier New")
        
        # Add widgets to splitter
        splitter.addWidget(self.history_table)
        splitter.addWidget(self.data_view)
        splitter.setSizes([300, 300])
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        self.restore_button = QPushButton("Restore This Version")
        self.restore_button.clicked.connect(self.restore_version)
        self.restore_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete This Version")
        self.delete_button.clicked.connect(self.delete_version)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.restore_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        # Add widgets to main layout
        layout.addWidget(splitter)
        layout.addLayout(button_layout)
        
        # Store the current selection
        self.current_selection = None
    
    def load_history(self):
        """Load the tag history from the database."""
        history = self.tag_db.get_tag_history(self.tag_id)
        
        self.history_table.setRowCount(len(history))
        
        for row, record in enumerate(history):
            # Version
            version_item = QTableWidgetItem(str(record.metadata.get('version', row + 1)))
            version_item.setData(Qt.UserRole, record)
            
            # Date
            try:
                date = QDateTime.fromString(record.updated_at, Qt.ISODate)
                date_str = date.toString("yyyy-MM-dd hh:mm:ss")
            except (ValueError, TypeError):
                date_str = str(record.updated_at)
            
            # Size
            size = len(record.data) if record.data else 0
            size_str = f"{size} bytes"
            
            # Add items to the table
            self.history_table.setItem(row, 0, version_item)
            self.history_table.setItem(row, 1, QTableWidgetItem(date_str))
            self.history_table.setItem(row, 2, QTableWidgetItem(record.tag_type or "Unknown"))
            self.history_table.setItem(row, 3, QTableWidgetItem(size_str))
        
        # Select the first row if available
        if self.history_table.rowCount() > 0:
            self.history_table.selectRow(0)
    
    def on_selection_changed(self):
        """Handle selection changes in the history table."""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            self.current_selection = None
            self.data_view.clear()
            self.restore_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
        
        # Get the selected record
        row = selected_items[0].row()
        version_item = self.history_table.item(row, 0)
        record = version_item.data(Qt.UserRole)
        self.current_selection = record
        
        # Display the data
        self.display_record_data(record)
        
        # Enable/disable buttons
        self.restore_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def display_record_data(self, record):
        """Display the data from a record in the text view."""
        if not record:
            self.data_view.clear()
            return
        
        # Format the data for display
        text = f"=== Tag ID: {record.tag_id} ===\n"
        text += f"Type: {record.tag_type or 'Unknown'}\n"
        text += f"Updated: {record.updated_at}\n"
        text += f"Size: {len(record.data or '')} bytes\n"
        
        # Add metadata if available
        if record.metadata:
            text += "\n=== Metadata ===\n"
            for key, value in record.metadata.items():
                if key != 'version':  # Skip version as it's shown in the table
                    text += f"{key}: {value}\n"
        
        # Add the actual data
        text += "\n=== Data ===\n"
        text += record.data or "[No data]"
        
        # Update the view
        self.data_view.setPlainText(text)
        self.data_view.moveCursor(QTextCursor.Start)
    
    def restore_version(self):
        """Restore the selected version as the current version."""
        if not self.current_selection:
            return
        
        reply = QMessageBox.question(
            self, 'Confirm Restore',
            'Are you sure you want to restore this version?\n'
            'This will make it the current version of the tag.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Store the record as the current version
            self.tag_db.store_tag(
                tag_id=self.current_selection.tag_id,
                tag_type=self.current_selection.tag_type,
                data=self.current_selection.data,
                metadata=self.current_selection.metadata
            )
            
            # Reload the history to show the new current version
            self.load_history()
            
            QMessageBox.information(
                self, 'Version Restored',
                'The selected version has been restored as the current version.'
            )
    
    def delete_version(self):
        """Delete the selected version from history."""
        if not self.current_selection:
            return
        
        # Don't allow deleting the only version
        if self.history_table.rowCount() <= 1:
            QMessageBox.warning(
                self, 'Cannot Delete',
                'Cannot delete the only version of a tag.'
            )
            return
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            'Are you sure you want to delete this version?\n'
            'This action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # In a real implementation, we would delete the version from the database
            # For now, we'll just show a message
            QMessageBox.information(
                self, 'Not Implemented',
                'Version deletion is not yet implemented in this version.'
            )
            # TODO: Implement version deletion in the database
            # self.tag_db.delete_version(self.current_selection.id)
            # self.load_history()
