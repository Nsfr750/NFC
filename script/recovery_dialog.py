"""
Password recovery dialog for the NFC Reader/Writer application.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, 
    QLabel, QMessageBox, QHBoxLayout, QFileDialog
)
from PySide6.QtCore import Qt, Signal

class RecoveryDialog(QDialog):
    """Dialog for recovering a forgotten password using a recovery key."""
    
    recovery_success = Signal(str)  # Signal emitted with new password when recovery is successful
    
    def __init__(self, auth_manager, parent=None):
        """Initialize the recovery dialog.
        
        Args:
            auth_manager: AuthManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.recovery_key_path = None
        self.setWindowTitle("Password Recovery")
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and instructions
        layout.addWidget(QLabel("<h3>Password Recovery</h3>"))
        layout.addWidget(QLabel(
            "If you've forgotten your password, you can recover it using a recovery key. "
            "Please provide the recovery key file you saved when setting up your password."
        ))
        
        # Recovery key file selection
        key_layout = QHBoxLayout()
        self.key_path_edit = QLineEdit()
        self.key_path_edit.setPlaceholderText("Select recovery key file...")
        self.key_path_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_recovery_key)
        
        key_layout.addWidget(self.key_path_edit)
        key_layout.addWidget(browse_btn)
        
        layout.addLayout(key_layout)
        
        # New password fields
        layout.addWidget(QLabel("New Password:"))
        self.new_pw_edit = QLineEdit()
        self.new_pw_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_pw_edit)
        
        layout.addWidget(QLabel("Confirm New Password:"))
        self.confirm_pw_edit = QLineEdit()
        self.confirm_pw_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_pw_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.recover_btn = QPushButton("Recover Password")
        self.recover_btn.clicked.connect(self.recover_password)
        self.recover_btn.setEnabled(False)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.recover_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # Connect signals
        self.new_pw_edit.textChanged.connect(self.validate_inputs)
        self.confirm_pw_edit.textChanged.connect(self.validate_inputs)
    
    def browse_recovery_key(self):
        """Open a file dialog to select the recovery key file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Recovery Key File",
            "",
            "Recovery Key (*.recovery);;All Files (*)"
        )
        
        if file_path:
            self.recovery_key_path = file_path
            self.key_path_edit.setText(file_path)
            self.validate_inputs()
    
    def validate_inputs(self):
        """Validate the input fields and enable/disable the recover button."""
        has_key = bool(self.recovery_key_path and os.path.exists(self.recovery_key_path))
        has_password = bool(self.new_pw_edit.text())
        passwords_match = (self.new_pw_edit.text() == self.confirm_pw_edit.text())
        
        self.recover_btn.setEnabled(has_key and has_password and passwords_match)
    
    def recover_password(self):
        """Attempt to recover the password using the recovery key."""
        try:
            # Load the recovery key
            with open(self.recovery_key_path, 'r') as f:
                recovery_data = json.load(f)
                
            # Verify the recovery key format
            if not all(k in recovery_data for k in ['salt', 'recovery_hash']):
                QMessageBox.critical(self, "Error", "Invalid recovery key format.")
                return
                
            # Get the new password
            new_password = self.new_pw_edit.text()
            
            # Set the new password using the auth manager
            if self.auth_manager.set_password(new_password):
                # Delete the recovery key after successful recovery
                try:
                    os.remove(self.recovery_key_path)
                except Exception as e:
                    logger.warning(f"Failed to delete recovery key: {e}")
                
                QMessageBox.information(
                    self,
                    "Password Recovered",
                    "Your password has been successfully reset.\n\n"
                    "The recovery key has been deleted for security reasons. "
                    "Please create a new one in the settings if desired."
                )
                
                self.recovery_success.emit(new_password)
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to set new password. Please try again."
                )
                
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Invalid recovery key file.")
        except Exception as e:
            logger.error(f"Password recovery failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during password recovery: {str(e)}"
            )


def generate_recovery_key(salt: bytes, password_hash: str, output_path: str) -> bool:
    """Generate a recovery key file for password recovery.
    
    Args:
        salt: The password salt
        password_hash: The hashed password
        output_path: Path to save the recovery key file
        
    Returns:
        bool: True if the recovery key was generated successfully, False otherwise
    """
    try:
        # Create a recovery key with the same salt as the password
        recovery_data = {
            'salt': salt.hex(),
            'recovery_hash': hashlib.sha256(
                (salt.hex() + password_hash).encode()
            ).hexdigest()
        }
        
        # Save the recovery key to a file
        with open(output_path, 'w') as f:
            json.dump(recovery_data, f)
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate recovery key: {e}")
        return False


def verify_recovery_key(recovery_key_path: str, salt: bytes, password_hash: str) -> bool:
    """Verify if a recovery key is valid.
    
    Args:
        recovery_key_path: Path to the recovery key file
        salt: The stored password salt
        password_hash: The stored password hash
        
    Returns:
        bool: True if the recovery key is valid, False otherwise
    """
    try:
        with open(recovery_key_path, 'r') as f:
            recovery_data = json.load(f)
            
        # Verify the recovery key format
        if not all(k in recovery_data for k in ['salt', 'recovery_hash']):
            return False
            
        # Verify the recovery hash
        expected_hash = hashlib.sha256(
            (salt.hex() + password_hash).encode()
        ).hexdigest()
        
        return recovery_data['recovery_hash'] == expected_hash
        
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        logger.error(f"Invalid recovery key: {e}")
        return False
    except Exception as e:
        logger.error(f"Error verifying recovery key: {e}")
        return False
