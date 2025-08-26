"""
Tag Tools Dialog

Provides a user interface for tag management tools including backup/restore
and tag cloning functionality.
"""
import os
import logging
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox, QTabWidget,
                             QGroupBox, QFormLayout, QLineEdit, QProgressBar, QWidget)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from .tag_database import TagDatabase
from .tag_cloner import TagCloner, format_tag_info
from .nfc_operations import NfcOperations

logger = logging.getLogger(__name__)

class BackupRestoreTab(QWidget):
    """Tab for database backup and restore operations."""
    
    def __init__(self, db: TagDatabase, parent=None):
        """Initialize the backup/restore tab.
        
        Args:
            db: TagDatabase instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Backup section
        backup_group = QGroupBox("Backup Database")
        backup_layout = QVBoxLayout()
        
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setPlaceholderText("Select backup location...")
        self.backup_path_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_backup_location)
        
        backup_btn = QPushButton("Create Backup")
        backup_btn.clicked.connect(self.create_backup)
        
        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.addWidget(self.backup_path_edit)
        backup_btn_layout.addWidget(browse_btn)
        
        backup_layout.addLayout(backup_btn_layout)
        backup_layout.addWidget(backup_btn)
        backup_group.setLayout(backup_layout)
        
        # Restore section
        restore_group = QGroupBox("Restore Database")
        restore_layout = QVBoxLayout()
        
        self.restore_path_edit = QLineEdit()
        self.restore_path_edit.setPlaceholderText("Select backup file...")
        self.restore_path_edit.setReadOnly(True)
        
        restore_browse_btn = QPushButton("Browse...")
        restore_browse_btn.clicked.connect(self.browse_restore_file)
        
        restore_btn = QPushButton("Restore from Backup")
        restore_btn.clicked.connect(self.restore_backup)
        
        restore_btn_layout = QHBoxLayout()
        restore_btn_layout.addWidget(self.restore_path_edit)
        restore_btn_layout.addWidget(restore_browse_btn)
        
        restore_layout.addLayout(restore_btn_layout)
        restore_layout.addWidget(restore_btn)
        restore_group.setLayout(restore_layout)
        
        # Add sections to main layout
        layout.addWidget(backup_group)
        layout.addWidget(restore_group)
        layout.addStretch()
    
    def browse_backup_location(self):
        """Open a dialog to select backup location."""
        default_path = os.path.join(os.path.expanduser("~"), "nfc_tag_backup.db")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Backup As", default_path, "SQLite Database (*.db);;All Files (*)")
        
        if path:
            self.backup_path_edit.setText(path)
    
    def browse_restore_file(self):
        """Open a dialog to select a backup file."""
        default_path = os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", default_path, "SQLite Database (*.db);;All Files (*)")
        
        if path:
            self.restore_path_edit.setText(path)
    
    def create_backup(self):
        """Create a backup of the database."""
        backup_path = self.backup_path_edit.text().strip()
        if not backup_path:
            QMessageBox.warning(self, "Error", "Please select a backup location")
            return
        
        try:
            success = self.db.backup_database(backup_path)
            if success:
                QMessageBox.information(self, "Success", 
                    f"Backup created successfully at:\n{backup_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to create backup")
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to create backup: {str(e)}")
    
    def restore_backup(self):
        """Restore the database from a backup."""
        backup_path = self.restore_path_edit.text().strip()
        if not backup_path:
            QMessageBox.warning(self, "Error", "Please select a backup file")
            return
        
        if not os.path.exists(backup_path):
            QMessageBox.warning(self, "Error", "Backup file does not exist")
            return
        
        # Confirm restore
        reply = QMessageBox.question(
            self, "Confirm Restore",
            "WARNING: This will replace your current database with the backup.\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                success = self.db.restore_database(backup_path)
                if success:
                    QMessageBox.information(self, "Success", 
                        "Database restored successfully. Please restart the application.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore backup")
            except Exception as e:
                logger.error(f"Error restoring backup: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to restore backup: {str(e)}")


class TagClonerTab(QWidget):
    """Tab for tag cloning operations."""
    
    def __init__(self, nfc_ops: NfcOperations, db: TagDatabase, parent=None):
        """Initialize the tag cloner tab.
        
        Args:
            nfc_ops: NfcOperations instance
            db: TagDatabase instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.nfc_ops = nfc_ops
        self.db = db
        self.tag_cloner = TagCloner(nfc_ops, db)
        self.source_tag = None
        self.target_tag = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Source tag section
        source_group = QGroupBox("Source Tag")
        source_layout = QVBoxLayout()
        
        self.source_info = QLabel("No tag selected")
        self.source_info.setWordWrap(True)
        self.source_info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        source_btn = QPushButton("Read Source Tag")
        source_btn.clicked.connect(self.read_source_tag)
        
        source_layout.addWidget(self.source_info)
        source_layout.addWidget(source_btn)
        source_group.setLayout(source_layout)
        
        # Target tag section
        target_group = QGroupBox("Target Tag")
        target_layout = QVBoxLayout()
        
        self.target_info = QLabel("No tag selected")
        self.target_info.setWordWrap(True)
        self.target_info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        target_btn = QPushButton("Read Target Tag")
        target_btn.clicked.connect(self.read_target_tag)
        
        target_layout.addWidget(self.target_info)
        target_layout.addWidget(target_btn)
        target_group.setLayout(target_layout)
        
        # Clone button
        self.clone_btn = QPushButton("Clone Tag")
        self.clone_btn.setEnabled(False)
        self.clone_btn.clicked.connect(self.clone_tags)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        
        # Add widgets to layout
        layout.addWidget(source_group)
        layout.addWidget(target_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.clone_btn)
        layout.addStretch()
    
    def read_source_tag(self):
        """Read the source tag."""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Scan source tag...")
        
        # Read tag in a separate thread to keep UI responsive
        def read_thread():
            try:
                if not self.nfc_ops.connect():
                    self.update_status("Error: Could not connect to NFC reader", error=True)
                    return
                
                # Read tag information
                tag_info = self.nfc_ops.get_tag_info()
                if not tag_info:
                    self.update_status("Error: Could not read tag information", error=True)
                    return
                
                # Read tag data
                tag_data = self.tag_cloner.read_tag_data(tag_info)
                if tag_data:
                    tag_info['data'] = tag_data
                    self.source_tag = tag_info
                    self.update_source_info(tag_info)
                    self.update_status("Source tag read successfully")
                    self.update_clone_button()
                else:
                    self.update_status("Error: Could not read tag data", error=True)
                
            except Exception as e:
                self.update_status(f"Error: {str(e)}", error=True)
                logger.error(f"Error reading source tag: {str(e)}")
            finally:
                self.nfc_ops.disconnect()
        
        # Start the reading process in a separate thread
        import threading
        thread = threading.Thread(target=read_thread, daemon=True)
        thread.start()
    
    def read_target_tag(self):
        """Read the target tag."""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Scan target tag...")
        
        # Read tag in a separate thread to keep UI responsive
        def read_thread():
            try:
                if not self.nfc_ops.connect():
                    self.update_status("Error: Could not connect to NFC reader", error=True)
                    return
                
                # Read tag information
                tag_info = self.nfc_ops.get_tag_info()
                if not tag_info:
                    self.update_status("Error: Could not read tag information", error=True)
                    return
                
                self.target_tag = tag_info
                self.update_target_info(tag_info)
                self.update_status("Target tag detected")
                self.update_clone_button()
                
            except Exception as e:
                self.update_status(f"Error: {str(e)}", error=True)
                logger.error(f"Error reading target tag: {str(e)}")
            finally:
                self.nfc_ops.disconnect()
        
        # Start the reading process in a separate thread
        import threading
        thread = threading.Thread(target=read_thread, daemon=True)
        thread.start()
    
    def clone_tags(self):
        """Clone data from source to target tag."""
        if not self.source_tag or not self.target_tag:
            return
        
        # Confirm clone operation
        reply = QMessageBox.question(
            self, "Confirm Clone",
            "WARNING: This will overwrite the target tag's data.\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Cloning tag data...")
        self.clone_btn.setEnabled(False)
        
        # Clone in a separate thread to keep UI responsive
        def clone_thread():
            try:
                result = self.tag_cloner.clone_tag(self.source_tag, self.target_tag)
                
                if result.success:
                    self.update_status("Tag cloned successfully!")
                    self.progress_bar.setValue(100)
                    
                    # Update target tag info
                    self.update_target_info(result.target_tag)
                    
                    # Show success message
                    QMessageBox.information(
                        self, "Success",
                        f"Tag cloned successfully!\n\n"
                        f"Source: {result.source_tag.get('id')}\n"
                        f"Target: {result.target_tag.get('id')}\n"
                        f"Bytes copied: {result.bytes_copied}")
                else:
                    self.update_status(f"Error: {result.message}", error=True)
                    QMessageBox.critical(self, "Error", result.message)
                
            except Exception as e:
                error_msg = f"Error during cloning: {str(e)}"
                self.update_status(error_msg, error=True)
                logger.error(error_msg, exc_info=True)
                QMessageBox.critical(self, "Error", error_msg)
            finally:
                self.clone_btn.setEnabled(True)
        
        # Start the cloning process in a separate thread
        import threading
        thread = threading.Thread(target=clone_thread, daemon=True)
        thread.start()
    
    def update_source_info(self, tag_info):
        """Update the source tag information display."""
        info = format_tag_info(tag_info)
        self.source_info.setText(info)
    
    def update_target_info(self, tag_info):
        """Update the target tag information display."""
        info = format_tag_info(tag_info)
        self.target_info.setText(info)
    
    def update_status(self, message, error=False):
        """Update the status bar with a message."""
        self.progress_bar.setFormat(message)
        if error:
            self.progress_bar.setStyleSheet("QProgressBar { color: red; }")
        else:
            self.progress_bar.setStyleSheet("")
    
    def update_clone_button(self):
        """Enable/disable the clone button based on tag availability."""
        self.clone_btn.setEnabled(
            self.source_tag is not None and 
            self.target_tag is not None and
            self.source_tag.get('id') != self.target_tag.get('id')
        )


class TagToolsDialog(QDialog):
    """Main dialog for tag management tools."""
    
    def __init__(self, nfc_ops: NfcOperations, db: TagDatabase, parent=None):
        """Initialize the tag tools dialog.
        
        Args:
            nfc_ops: NfcOperations instance
            db: TagDatabase instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.nfc_ops = nfc_ops
        self.db = db
        self.setWindowTitle("Tag Management Tools")
        self.setMinimumSize(600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.backup_tab = BackupRestoreTab(self.db)
        self.clone_tab = TagClonerTab(self.nfc_ops, self.db)
        
        self.tab_widget.addTab(self.backup_tab, "Backup/Restore")
        self.tab_widget.addTab(self.clone_tab, "Tag Cloner")
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        # Add widgets to layout
        layout.addWidget(self.tab_widget)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
    
    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        # Reset UI when dialog is shown
        if hasattr(self.clone_tab, 'reset_ui'):
            self.clone_tab.reset_ui()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    # Create dummy instances for testing
    nfc_ops = NfcOperations()
    db = TagDatabase()
    
    # Show the dialog
    dialog = TagToolsDialog(nfc_ops, db)
    dialog.show()
    
    sys.exit(app.exec())
