from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtCore import Slot, Qt
import time

from .help_dialog import HelpDialog

class AppMenu:
    def __init__(self, parent, nfc_thread):
        self.parent = parent
        self.nfc_thread = nfc_thread
        self.menubar = parent.menuBar()
        self.setup_menus()
    
    def setup_menus(self):
        """Set up all menu items and their actions."""
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_help_menu()
        
    def create_view_menu(self):
        """Create the View menu with its actions."""
        self.view_menu = self.menubar.addMenu("&View")
        
        # Statistics action
        stats_action = QtGui.QAction("&Statistics...", self.parent)
        stats_action.triggered.connect(self.parent.show_statistics)
        self.view_menu.addAction(stats_action)
    
    def create_file_menu(self):
        """Create the File menu with its actions."""
        file_menu = self.menubar.addMenu("&File")
        
        # Exit action
        exit_action = QtGui.QAction("E&xit", self.parent)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(exit_action)
    
    def create_edit_menu(self):
        """Create the Edit menu with its actions."""
        edit_menu = self.menubar.addMenu("&Edit")
        
        # Clear log action
        clear_action = QtGui.QAction("&Clear Log", self.parent)
        clear_action.triggered.connect(self.parent.clear_log)
        edit_menu.addAction(clear_action)
        
        # Add separator
        edit_menu.addSeparator()
        
        # Toggle read/write mode
        self.read_mode_action = QtGui.QAction("Read Mode", self.parent, checkable=True)
        self.read_mode_action.setChecked(True)
        self.read_mode_action.triggered.connect(self.toggle_read_write_mode)
        edit_menu.addAction(self.read_mode_action)
    
    def create_tools_menu(self):
        """Create the Tools menu with its actions."""
        tools_menu = self.menubar.addMenu("&Tools")
        
        # Format tag action
        format_action = QtGui.QAction("&Format Tag", self.parent)
        format_action.triggered.connect(self.format_tag)
        tools_menu.addAction(format_action)
        
        # Add separator
        tools_menu.addSeparator()
        
        # Emulate tag action
        emulate_action = QtGui.QAction("&Emulate Tag...", self.parent)
        emulate_action.triggered.connect(self.emulate_tag)
        tools_menu.addAction(emulate_action)
        
        # Add separator
        tools_menu.addSeparator()
        
        # Settings action
        settings_action = QtGui.QAction("&Settings...", self.parent)
        settings_action.triggered.connect(self.show_settings)
        settings_action.setShortcut("Ctrl+,")
        tools_menu.addAction(settings_action)
    
    def create_help_menu(self):
        """Create the Help menu with its actions."""
        help_menu = self.menubar.addMenu("&Help")
        
        # Help action
        help_action = QtGui.QAction("&Help", self.parent)
        help_action.setShortcut(Qt.Key_F1)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        # Add separator
        help_menu.addSeparator()
        
        # About action
        about_action = QtGui.QAction("&About", self.parent)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    @Slot()
    def toggle_read_write_mode(self, checked):
        """Toggle between read and write modes."""
        if checked:
            self.read_mode_action.setText('Read Mode')
            self.parent.statusBar().showMessage('Switched to Read Mode')
            self.nfc_thread.read_mode = True
        else:
            self.read_mode_action.setText('Write Mode')
            self.parent.statusBar().showMessage('Switched to Write Mode')
            self.nfc_thread.read_mode = False
    
    @Slot()
    def show_help(self):
        """Show the help dialog."""
        dialog = HelpDialog(self.parent)
        dialog.exec_()
        
    def show_about(self):
        """Show the about dialog."""
        from .about import show_about_dialog
        show_about_dialog(self.parent)
    
    @Slot()
    def format_tag(self):
        """Handle tag formatting."""
        # This is a placeholder that can be connected to actual formatting functionality
        # when the NFC thread's format_tag method is implemented
        QMessageBox.information(self.parent, "Format Tag", 
                              "Place the tag near the reader to format it.")
        # TODO: Implement actual tag formatting
        # success, message = self.nfc_thread.format_tag()
        # if success:
        #     QMessageBox.information(self.parent, "Success", message)
        # else:
        #     QMessageBox.warning(self.parent, "Error", message)
    
    def show_settings(self):
        """Show the settings dialog."""
        self.parent.show_settings()
        
    def emulate_tag(self):
        """Show the tag emulation dialog."""
        try:
            from .emulation_dialog import EmulationDialog
            dialog = EmulationDialog(self.parent)
            if dialog.exec():
                # Handle successful emulation
                self.parent.statusBar().showMessage("Tag emulation started", 3000)
        except ImportError as e:
            self.parent.show_error("Error", f"Failed to import emulation dialog: {str(e)}")
        except Exception as e:
            self.parent.show_error("Error", f"Failed to start tag emulation: {str(e)}")
