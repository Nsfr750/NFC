"""
Settings dialog for NFC Reader/Writer application preferences.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QDialogButtonBox, QCheckBox, QSpinBox, QComboBox,
                             QLineEdit, QFileDialog, QLabel, QGroupBox, QTabWidget,
                             QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont
import os
import json
from pathlib import Path
from script.settings_manager import settings_manager

class SettingsDialog(QDialog):
    """Dialog for application settings and preferences."""
    
    # Signal emitted when settings are saved
    settings_saved = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Settings")
        self.setMinimumSize(700, 500)
        
        # Initialize settings
        self.current_settings = {}
        
        # Initialize UI
        self.init_ui()
        
        # Load saved settings
        self.load_settings()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add tabs
        self.tabs.addTab(self.create_general_tab(), "General")
        self.tabs.addTab(self.create_nfc_tab(), "NFC")
        self.tabs.addTab(self.create_interface_tab(), "Interface")
        self.tabs.addTab(self.create_advanced_tab(), "Advanced")
        
        main_layout.addWidget(self.tabs)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.confirm_restore_defaults)
        
        main_layout.addWidget(button_box)
    
    def create_general_tab(self):
        """Create the General settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Auto-save settings
        auto_save_group = QGroupBox("Auto-save")
        auto_save_layout = QFormLayout()
        
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setSuffix(" minutes")
        
        auto_save_layout.addRow(self.auto_save_checkbox)
        auto_save_layout.addRow("Auto-save interval:", self.auto_save_interval)
        auto_save_group.setLayout(auto_save_layout)
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout()
        
        self.load_last_session = QCheckBox("Load last session on startup")
        self.check_updates = QCheckBox("Check for updates on startup")
        
        startup_layout.addWidget(self.load_last_session)
        startup_layout.addWidget(self.check_updates)
        startup_group.setLayout(startup_layout)
        
        # Add to main layout
        layout.addWidget(auto_save_group)
        layout.addWidget(startup_group)
        layout.addStretch()
        
        return tab
    
    def create_nfc_tab(self):
        """Create the NFC settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Reader settings
        reader_group = QGroupBox("Reader Settings")
        reader_layout = QFormLayout()
        
        self.reader_timeout = QSpinBox()
        self.reader_timeout.setRange(1, 60)
        self.reader_timeout.setSuffix(" seconds")
        
        self.auto_connect = QCheckBox("Automatically connect to reader on startup")
        self.beep_on_read = QCheckBox("Beep on successful read")
        
        reader_layout.addRow("Read timeout:", self.reader_timeout)
        reader_layout.addRow(self.auto_connect)
        reader_layout.addRow(self.beep_on_read)
        reader_group.setLayout(reader_layout)
        
        # Writer settings
        writer_group = QGroupBox("Writer Settings")
        writer_layout = QFormLayout()
        
        self.verify_after_write = QCheckBox("Verify data after writing")
        self.auto_lock = QCheckBox("Lock tag after writing")
        self.retry_count = QSpinBox()
        self.retry_count.setRange(0, 10)
        self.retry_count.setSpecialValueText("No retry")
        
        writer_layout.addRow(self.verify_after_write)
        writer_layout.addRow(self.auto_lock)
        writer_layout.addRow("Retry count on write failure:", self.retry_count)
        writer_group.setLayout(writer_layout)
        
        # Add to main layout
        layout.addWidget(reader_group)
        layout.addWidget(writer_group)
        layout.addStretch()
        
        return tab
    
    def create_interface_tab(self):
        """Create the Interface settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Display settings
        display_group = QGroupBox("Display")
        display_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark", "Dark Blue"])
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix(" pt")
        
        self.show_toolbar = QCheckBox("Show toolbar")
        self.show_statusbar = QCheckBox("Show status bar")
        
        display_layout.addRow("Theme:", self.theme_combo)
        display_layout.addRow("Font size:", self.font_size)
        display_layout.addRow(self.show_toolbar)
        display_layout.addRow(self.show_statusbar)
        display_group.setLayout(display_layout)
        
        # Text editor settings
        editor_group = QGroupBox("Text Editor")
        editor_layout = QFormLayout()
        
        self.word_wrap = QCheckBox("Word wrap")
        self.line_numbers = QCheckBox("Show line numbers")
        self.highlight_current_line = QCheckBox("Highlight current line")
        self.tab_width = QSpinBox()
        self.tab_width.setRange(1, 8)
        self.tab_width.setSuffix(" spaces")
        
        editor_layout.addRow(self.word_wrap)
        editor_layout.addRow(self.line_numbers)
        editor_layout.addRow(self.highlight_current_line)
        editor_layout.addRow("Tab width:", self.tab_width)
        editor_group.setLayout(editor_layout)
        
        # Add to main layout
        layout.addWidget(display_group)
        layout.addWidget(editor_group)
        layout.addStretch()
        
        return tab
    
    def create_advanced_tab(self):
        """Create the Advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging settings
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout()
        
        self.log_level = QComboBox()
        self.log_level.addItems(["Debug", "Info", "Warning", "Error", "Critical"])
        
        self.log_to_file = QCheckBox("Save logs to file")
        
        self.log_file_path = QLineEdit()
        self.log_file_path.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_log_file)
        
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_file_path)
        log_path_layout.addWidget(browse_btn)
        
        logging_layout.addRow("Log level:", self.log_level)
        logging_layout.addRow(self.log_to_file)
        logging_layout.addRow("Log file:", log_path_layout)
        logging_group.setLayout(logging_layout)
        
        # Database settings
        db_group = QGroupBox("Database")
        db_layout = QVBoxLayout()
        
        self.db_auto_cleanup = QCheckBox("Enable automatic database cleanup")
        self.db_cleanup_days = QSpinBox()
        self.db_cleanup_days.setRange(1, 365)
        self.db_cleanup_days.setSuffix(" days")
        
        db_cleanup_layout = QHBoxLayout()
        db_cleanup_layout.addWidget(QLabel("Keep history for:"))
        db_cleanup_layout.addWidget(self.db_cleanup_days)
        db_cleanup_layout.addStretch()
        
        db_cleanup_group = QGroupBox()
        db_cleanup_group.setCheckable(True)
        db_cleanup_group.setChecked(False)
        db_cleanup_group.setLayout(db_cleanup_layout)
        
        db_layout.addWidget(self.db_auto_cleanup)
        db_layout.addWidget(db_cleanup_group)
        db_group.setLayout(db_layout)
        
        # Add to main layout
        layout.addWidget(logging_group)
        layout.addWidget(db_group)
        layout.addStretch()
        
        # Connect signals
        self.db_auto_cleanup.toggled.connect(db_cleanup_group.setEnabled)
        
        return tab
    
    def browse_log_file(self):
        """Open a file dialog to select log file location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Log File",
            self.log_file_path.text() or "",
            "Log Files (*.log);;All Files (*)"
        )
        
        if file_path:
            self.log_file_path.setText(file_path)
    
    def load_settings(self):
        """Load settings from settings manager."""
        try:
            # General
            self.auto_save_checkbox.setChecked(settings_manager.get('auto_save.enabled', True))
            self.auto_save_interval.setValue(settings_manager.get('auto_save.interval', 5))
            self.load_last_session.setChecked(settings_manager.get('startup.load_last_session', True))
            self.check_updates.setChecked(settings_manager.get('startup.check_updates', True))
            
            # NFC
            self.reader_timeout.setValue(settings_manager.get('nfc.reader_timeout', 10))
            self.auto_connect.setChecked(settings_manager.get('nfc.auto_connect', False))
            self.beep_on_read.setChecked(settings_manager.get('nfc.beep_on_read', True))
            self.verify_after_write.setChecked(settings_manager.get('nfc.verify_after_write', True))
            self.auto_lock.setChecked(settings_manager.get('nfc.auto_lock', False))
            self.retry_count.setValue(settings_manager.get('nfc.retry_count', 1))
            
            # Interface
            self.theme_combo.setCurrentText(settings_manager.get('interface.theme', 'System'))
            self.font_size.setValue(settings_manager.get('interface.font_size', 10))
            self.show_toolbar.setChecked(settings_manager.get('interface.show_toolbar', True))
            self.show_statusbar.setChecked(settings_manager.get('interface.show_statusbar', True))
            self.word_wrap.setChecked(settings_manager.get('editor.word_wrap', True))
            self.line_numbers.setChecked(settings_manager.get('editor.line_numbers', True))
            self.highlight_current_line.setChecked(settings_manager.get('editor.highlight_current_line', True))
            self.tab_width.setValue(settings_manager.get('editor.tab_width', 4))
            
            # Advanced
            self.log_level.setCurrentText(settings_manager.get('logging.level', 'Info'))
            self.log_to_file.setChecked(settings_manager.get('logging.to_file', False))
            self.log_file_path.setText(settings_manager.get('logging.file_path', 'nfc_reader.log'))
            self.db_auto_cleanup.setChecked(settings_manager.get('database.auto_cleanup', False))
            self.db_cleanup_days.setValue(settings_manager.get('database.cleanup_days', 30))
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def get_current_settings(self):
        """Get all current settings as a dictionary."""
        settings = {
            # General
            'auto_save': {
                'enabled': self.auto_save_checkbox.isChecked(),
                'interval': self.auto_save_interval.value()
            },
            'startup': {
                'load_last_session': self.load_last_session.isChecked(),
                'check_updates': self.check_updates.isChecked()
            },
            
            # NFC
            'nfc': {
                'reader_timeout': self.reader_timeout.value(),
                'auto_connect': self.auto_connect.isChecked(),
                'beep_on_read': self.beep_on_read.isChecked(),
                'verify_after_write': self.verify_after_write.isChecked(),
                'auto_lock': self.auto_lock.isChecked(),
                'retry_count': self.retry_count.value()
            },
            
            # Interface
            'interface': {
                'theme': self.theme_combo.currentText(),
                'font_size': self.font_size.value(),
                'show_toolbar': self.show_toolbar.isChecked(),
                'show_statusbar': self.show_statusbar.isChecked()
            },
            
            # Editor
            'editor': {
                'word_wrap': self.word_wrap.isChecked(),
                'line_numbers': self.line_numbers.isChecked(),
                'highlight_current_line': self.highlight_current_line.isChecked(),
                'tab_width': self.tab_width.value()
            },
            
            # Logging
            'logging': {
                'level': self.log_level.currentText(),
                'to_file': self.log_to_file.isChecked(),
                'file_path': self.log_file_path.text()
            },
            
            # Database
            'database': {
                'auto_cleanup': self.db_auto_cleanup.isChecked(),
                'cleanup_days': self.db_cleanup_days.value()
            }
        }
        
        return settings
    
    def save_settings(self):
        """Save settings to settings manager and emit signal."""
        try:
            # Get current settings
            settings = self.get_current_settings()
            
            # Save to settings manager
            for section, section_data in settings.items():
                for key, value in section_data.items():
                    settings_manager.set(f"{section}.{key}", value)
            
            # Save settings to file
            if not settings_manager.save_settings():
                raise Exception("Failed to save settings to file")
            
            # Emit signal with settings
            self.settings_saved.emit(settings)
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def confirm_restore_defaults(self):
        """Show confirmation dialog before restoring defaults."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?\n\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.restore_defaults()
    
    def restore_defaults(self):
        """Restore all settings to their default values."""
        # Clear all settings
        self.settings.clear()
        
        # Reload default settings
        self.load_settings()
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Defaults Restored",
            "All settings have been restored to their default values.",
            QMessageBox.Ok
        )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec())
