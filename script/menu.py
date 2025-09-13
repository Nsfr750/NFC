from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtCore import Slot, Qt
import time
import sys
import os

# Add the parent directory to the path to import settings_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.settings_manager import settings_manager

from .help_dialog import HelpDialog
from .auth import AuthManager, PasswordDialog

class AppMenu:
    def __init__(self, parent, nfc_thread):
        self.parent = parent
        self.nfc_thread = nfc_thread
        self.auth_manager = AuthManager()
        self.menubar = parent.menuBar()
        self.setup_menus()
    
    def setup_menus(self):
        """Set up all menu items and their actions."""
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_security_menu()
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
        
        # Tag Tools action
        tag_tools_action = QtGui.QAction("Tag &Tools...", self.parent)
        tag_tools_action.triggered.connect(self.show_tag_tools)
        tools_menu.addAction(tag_tools_action)
        
        # Tag Database action
        tag_db_action = QtGui.QAction("Tag &Database...", self.parent)
        tag_db_action.triggered.connect(self.show_tag_database)
        tools_menu.addAction(tag_db_action)
               
        # Add separator
        tools_menu.addSeparator()
        
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
        settings_action.setShortcut("Ctrl+")
        tools_menu.addAction(settings_action)
    
    def create_security_menu(self):
        """Create the Security menu with its actions."""
        security_menu = self.menubar.addMenu("&Security")
        
        # Session submenu
        session_menu = security_menu.addMenu("&Session")
        
        # Lock Session action
        self.lock_action = QtGui.QAction("&Lock Session", self.parent)
        self.lock_action.setShortcut("Ctrl+L")
        self.lock_action.triggered.connect(self.parent.lock_application)
        session_menu.addAction(self.lock_action)
        
        # Session Timeout submenu
        timeout_menu = session_menu.addMenu("&Timeout")
        
        # Timeout actions group
        self.timeout_group = QtGui.QActionGroup(self.parent)
        self.timeout_group.setExclusive(True)
        
        # Add timeout options
        timeouts = [
            ("5 minutes", 5),
            ("15 minutes", 15),
            ("30 minutes", 30),
            ("1 hour", 60),
            ("Never (not recommended)", 0)
        ]
        
        current_timeout = settings_manager.get('security.session_timeout', 15)
        
        for text, minutes in timeouts:
            action = QtGui.QAction(text, self.parent, checkable=True)
            action.setData(minutes)
            if minutes == current_timeout:
                action.setChecked(True)
            action.triggered.connect(self.set_session_timeout)
            self.timeout_group.addAction(action)
            timeout_menu.addAction(action)
        
        # Add separator
        security_menu.addSeparator()
        
        # Change Password action
        change_pw_action = QtGui.QAction("Change &Password...", self.parent)
        change_pw_action.triggered.connect(self.change_password)
        security_menu.addAction(change_pw_action)
        
        # Add separator
        security_menu.addSeparator()
        
        # Password Recovery action
        recovery_action = QtGui.QAction("Password &Recovery...", self.parent)
        recovery_action.triggered.connect(self.show_password_recovery)
        security_menu.addAction(recovery_action)
        
        # Add separator
        security_menu.addSeparator()
        
        # Require Password action
        self.require_pw_action = QtGui.QAction("Require &Password", self.parent, checkable=True)
        self.require_pw_action.setChecked(self.auth_manager.is_password_set())
        self.require_pw_action.triggered.connect(self.toggle_password_protection)
        security_menu.addAction(self.require_pw_action)
    
    def set_session_timeout(self):
        """Handle session timeout change from menu."""
        action = self.sender()
        if action and hasattr(self.parent, 'set_session_timeout'):
            minutes = action.data()
            self.parent.set_session_timeout(minutes)
    
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
        
        # Wiki action
        wiki_action = QtGui.QAction("&WIKI", self.parent)
        wiki_action.triggered.connect(self.open_wiki)
        help_menu.addAction(wiki_action)
        
        # Add separator
        help_menu.addSeparator()
        
        # About action
        about_action = QtGui.QAction("&About", self.parent)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    @Slot()
    def open_wiki(self):
        """Open the GitHub wiki page in the default web browser."""
        import webbrowser
        webbrowser.open("https://github.com/Nsfr750/NFC/wiki")
    
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
        help_dialog = HelpDialog(self.parent)
        help_dialog.exec()
        
    def require_authentication(self, action_name: str) -> bool:
        """Check if authentication is required and verify password if needed.
        
        Args:
            action_name: Name of the action being performed (for messages)
            
        Returns:
            bool: True if authenticated or no auth needed, False if cancelled
        """
        if not self.auth_manager.is_password_set():
            return True
            
        if PasswordDialog.verify_password(self.auth_manager, self.parent):
            return True
            
        QMessageBox.information(
            self.parent,
            "Authentication Required",
            f"You must be authenticated to {action_name}."
        )
        return False
    
    def change_password(self):
        """Show the change password dialog."""
        if PasswordDialog.set_password(self.auth_manager, self.parent):
            self.require_pw_action.setChecked(self.auth_manager.is_password_set())
            QMessageBox.information(
                self.parent,
                "Success",
                "Password updated successfully."
            )
    
    def show_password_recovery(self):
        """Show the password recovery dialog."""
        from .recovery_dialog import RecoveryDialog
        
        if not self.auth_manager.is_password_set():
            QMessageBox.information(
                self.parent,
                "No Password Set",
                "There is no password set up to recover."
            )
            return
            
        dialog = RecoveryDialog(self.auth_manager, self.parent)
        if dialog.exec() == QDialog.Accepted and hasattr(self, 'recovery_success'):
            # If recovery was successful, update the UI accordingly
            self.require_pw_action.setChecked(True)
            QMessageBox.information(
                self.parent,
                "Password Recovered",
                "Your password has been successfully recovered and updated."
            )
    
    def toggle_password_protection(self):
        """Toggle password protection on/off."""
        if self.auth_manager.is_password_set():
            # Verify current password before disabling
            if PasswordDialog.verify_password(self.auth_manager, self.parent):
                self.auth_manager.set_password("")  # Clear password
                self.require_pw_action.setChecked(False)
                QMessageBox.information(
                    self.parent,
                    "Password Protection Disabled",
                    "Password protection has been disabled."
                )
            else:
                self.require_pw_action.setChecked(True)  # Re-check if verification failed
        else:
            # Set a new password
            if PasswordDialog.set_password(self.auth_manager, self.parent):
                self.require_pw_action.setChecked(True)
    
    def show_tag_tools(self):
        """Show the tag tools dialog."""
        if not self.require_authentication("access tag tools"):
            return
            
        try:
            from .tag_tools_dialog import TagToolsDialog
            from .nfc_operations import NfcOperations
            from .tag_database import TagDatabase
            
            nfc_ops = NfcOperations()
            db = TagDatabase()
            dialog = TagToolsDialog(nfc_ops, db, self.parent)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to open Tag Tools: {str(e)}"
            )
    
    def show_tag_database(self):
        """Show the tag database dialog."""
        if not self.require_authentication("access tag database"):
            return
            
        try:
            from .tag_database import TagDatabase
            from .tag_database_dialog import TagDatabaseDialog
            
            db = TagDatabase()
            dialog = TagDatabaseDialog(db, self.parent)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to open Tag Database: {str(e)}"
            )
    
    def show_tag_cloner(self):
        """Show the tag cloner dialog."""
        if not self.require_authentication("use tag cloner"):
            return
            
        from .nfc_operations import NfcOperations
        from .tag_database import TagDatabase
        
        try:
            nfc_ops = NfcOperations()
            db = TagDatabase()
            dialog = TagClonerDialog(nfc_ops, db, self.parent)  # Create this dialog if needed
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to open Tag Cloner: {str(e)}"
            )
        
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
