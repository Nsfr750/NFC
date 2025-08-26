"""
Authentication and password management for sensitive operations.
"""
import os
import hashlib
import json
import logging
from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, 
    QLabel, QMessageBox, QCheckBox, QFileDialog,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QSettings
from .password_strength import PasswordStrengthMeter, PasswordValidator
from pathlib import Path

# Add these imports at the top of auth.py
import time
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)

class AuthManager:
    """Handles password hashing, verification, and brute force protection."""
    
    # Brute force protection settings
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = 300  # 5 minutes in seconds
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the authentication manager."""
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "auth_config.json"
        self.attempts_file = self.config_dir / "login_attempts.json"
        self.salt = None
        self.password_hash = None
        self._load_config()
        self._ensure_attempts_file()
        
    def _ensure_attempts_file(self):
        """Ensure the login attempts file exists."""
        if not self.attempts_file.exists():
            with open(self.attempts_file, 'w') as f:
                json.dump({"attempts": 0, "last_attempt": None, "locked_until": None}, f)
    
    def _load_attempts(self):
        """Load login attempts data."""
        try:
            with open(self.attempts_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading login attempts: {e}")
            return {"attempts": 0, "last_attempt": None, "locked_until": None}
    
    def _save_attempts(self, attempts_data):
        """Save login attempts data."""
        try:
            with open(self.attempts_file, 'w') as f:
                json.dump(attempts_data, f)
        except Exception as e:
            logger.error(f"Error saving login attempts: {e}")
    
    def is_locked_out(self):
        """Check if the account is locked due to too many failed attempts."""
        attempts_data = self._load_attempts()
        locked_until = attempts_data.get("locked_until")
        
        if locked_until:
            locked_until = datetime.fromisoformat(locked_until)
            if datetime.now() < locked_until:
                return True, locked_until
            else:
                # Reset if lockout period has passed
                self._reset_attempts()
                return False, None
        return False, None
    
    def _reset_attempts(self):
        """Reset the failed login attempts counter."""
        self._save_attempts({
            "attempts": 0,
            "last_attempt": None,
            "locked_until": None
        })
    
    def record_failed_attempt(self):
        """Record a failed login attempt."""
        attempts_data = self._load_attempts()
        now = datetime.now().isoformat()
        
        attempts = attempts_data.get("attempts", 0) + 1
        locked_until = None
        
        if attempts >= self.MAX_ATTEMPTS:
            locked_until = (datetime.now() + timedelta(seconds=self.LOCKOUT_DURATION)).isoformat()
        
        self._save_attempts({
            "attempts": attempts,
            "last_attempt": now,
            "locked_until": locked_until
        })
    
    def verify_password(self, password: str) -> tuple[bool, str]:
        """
        Verify a password against the stored hash.
        
        Args:
            password: The password to verify
            
        Returns:
            tuple: (success, message)
        """
        # Check if account is locked
        is_locked, until = self.is_locked_out()
        if is_locked:
            remaining = (until - datetime.now()).seconds // 60 + 1
            return False, f"Account locked. Try again in {remaining} minutes."
        
        # Verify password
        if not self.password_hash:
            return False, "No password set"
            
        hashed = self._hash_password(password)
        if hashed == self.password_hash:
            # Reset attempts on successful login
            self._reset_attempts()
            return True, "Authentication successful"
        else:
            # Record failed attempt
            self.record_failed_attempt()
            attempts_remaining = self.MAX_ATTEMPTS - self._load_attempts().get("attempts", 0)
            
            if attempts_remaining <= 0:
                return False, "Too many failed attempts. Account locked for 5 minutes."
            return False, f"Invalid password. {attempts_remaining} attempts remaining."
    
    def _load_config(self) -> None:
        """Load the authentication configuration."""
        try:
            if not self.config_file.exists():
                return
                
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.salt = bytes.fromhex(config.get('salt', ''))
                self.password_hash = config.get('password_hash', '')
        except Exception as e:
            print(f"Error loading auth config: {e}")
    
    def _save_config(self) -> None:
        """Save the authentication configuration."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({
                    'salt': self.salt.hex() if self.salt else '',
                    'password_hash': self.password_hash or ''
                }, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving auth config: {e}")
            
    def is_password_set(self) -> bool:
        """Check if a password is currently set.
        
        Returns:
            bool: True if a password is set (both hash and salt exist), False otherwise
        """
        return bool(self.password_hash and self.salt)
        
    def _generate_recovery_key(self, password: str, salt: bytes, 
                            password_hash: str, output_path: str) -> bool:
        """Generate a recovery key file.
        
        Args:
            password: The password to generate recovery for
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
                json.dump(recovery_data, f, indent=2)
                
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
    def _hash_password(self, password: str, salt: bytes = None) -> Tuple[bytes, str]:
        """Hash a password with a salt.
        
        Args:
            password: The password to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            tuple: (salt, hashed_password)
        """
        if salt is None:
            salt = os.urandom(32)  # 256-bit salt
            
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,  # Number of iterations
            dklen=32  # Length of the derived key
        )
        
        return salt, key.hex()
    
    def set_password(self, password: str, recovery_key_path: str = None) -> bool:
        """Set a new password and optionally generate a recovery key.
        
        Args:
            password: The new password to set
            recovery_key_path: Optional path to save a recovery key
            
        Returns:
            bool: True if the password was set successfully, False otherwise
        """
        if not password:
            return False
            
        self.salt, self.password_hash = self._hash_password(password)
        
        # Generate recovery key if requested
        if recovery_key_path:
            if not generate_recovery_key(self.salt, self.password_hash, recovery_key_path):
                logger.error("Failed to generate recovery key")
                return False
                
        self._save_config()
        return True
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash.
        
        Args:
            password: The password to verify
            
        Returns:
            bool: True if the password is correct, False otherwise
        """
        if not self.password_hash or not self.salt:
            return False
            
        _, key = self._hash_password(password, self.salt)
        return key == self.password_hash
        
    def recover_password(self, recovery_key_path: str, new_password: str) -> bool:
        """Recover a forgotten password using a recovery key.
        
        Args:
            recovery_key_path: Path to the recovery key file
            new_password: The new password to set
            
        Returns:
            bool: True if password was successfully recovered and set, False otherwise
        """
        try:
            # Verify the recovery key
            if not verify_recovery_key(recovery_key_path, self.salt, self.password_hash):
                logger.error("Invalid recovery key")
                return False
                
            # Set the new password
            if not self.set_password(new_password):
                logger.error("Failed to set new password")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Password recovery failed: {e}")
            return False
    
    def is_password_set(self) -> bool:
        """Check if a password is set."""
        return bool(self.password_hash and self.salt)


class PasswordDialog(QDialog):
    """Dialog for entering or setting a password."""
    
    verified = Signal()
    
    def __init__(self, auth_manager: AuthManager, mode: str = 'verify', parent=None, allow_recovery: bool = True):
        """Initialize the password dialog.
        
        Args:
            auth_manager: AuthManager instance
            mode: 'verify', 'set', or 'change' password
            parent: Parent widget
            allow_recovery: Whether to show the forgot password option
        """
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.mode = mode
        self.allow_recovery = allow_recovery
        self.setWindowTitle("Authentication Required")
        self.setMinimumWidth(350)
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        if self.mode == 'set':
            title = "Set Password"
            message = "Set a password to protect sensitive operations."
        elif self.mode == 'change':
            title = "Change Password"
            message = "Enter your current password and set a new one."
        else:
            title = "Authentication Required"
            message = "Please enter your password to continue."
        
        # Title and message
        layout.addWidget(QLabel(f"<h3>{title}</h3>"))
        layout.addWidget(QLabel(message))
        
        # Current password field (for changing password)
        if self.mode == 'change' and self.auth_manager.is_password_set():
            layout.addWidget(QLabel("Current Password:"))
            self.current_pw_edit = QLineEdit()
            self.current_pw_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.current_pw_edit)
            
        # New password field
        if self.mode in ['set', 'change']:
            layout.addWidget(QLabel("New Password:" if self.mode == 'change' else "Password:"))
            self.new_pw_edit = QLineEdit()
            self.new_pw_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.new_pw_edit)
            
            # Password strength meter
            self.strength_meter = PasswordStrengthMeter()
            layout.addWidget(self.strength_meter)
            
            # Connect password field to strength meter
            self.new_pw_edit.textChanged.connect(self.update_password_strength)
            
            # Confirm password field
            layout.addWidget(QLabel("Confirm Password:"))
            self.confirm_pw_edit = QLineEdit()
            self.confirm_pw_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.confirm_pw_edit)
        else:
            # For verify mode
            layout.addWidget(QLabel("Password:"))
            self.new_pw_edit = QLineEdit()
            self.new_pw_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.new_pw_edit)
        
        # Show password checkbox
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_cb)
        
        # Buttons
        button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.verify)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)
        layout.addLayout(button_box)
        
        # Forgot password link (only in verify mode)
        if self.mode == 'verify' and self.allow_recovery:
            self.forgot_btn = QPushButton("Forgot Password?")
            self.forgot_btn.setStyleSheet("text-align: left; color: #0066cc; border: none;")
            self.forgot_btn.setCursor(Qt.PointingHandCursor)
            self.forgot_btn.clicked.connect(self.show_recovery_dialog)
            layout.addWidget(self.forgot_btn)
        
        # Dialog properties
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(350)
    
    def toggle_password_visibility(self, checked: bool) -> None:
        """Toggle password visibility."""
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.new_pw_edit.setEchoMode(mode)
        self.confirm_pw_edit.setEchoMode(mode)
        if hasattr(self, 'current_pw_edit'):
            self.current_pw_edit.setEchoMode(mode)
    
    def update_password_strength(self, password: str) -> None:
        """Update the password strength meter based on the current password."""
        if hasattr(self, 'strength_meter') and self.strength_meter is not None:
            self.strength_meter.update_strength(password)
    
    def verify(self) -> None:
        """Verify the entered password."""
        try:
            if self.mode in ['set', 'change']:
                # Verify current password if changing
                if self.mode == 'change' and self.auth_manager.is_password_set():
                    current_pw = self.current_pw_edit.text()
                    success, message = self.auth_manager.verify_password(current_pw)
                    if not success:
                        QMessageBox.warning(self, "Error", message)
                        return
                
                # Verify new password
                new_pw = self.new_pw_edit.text()
                confirm_pw = self.confirm_pw_edit.text()
                
                if not new_pw:
                    QMessageBox.warning(self, "Error", "Password cannot be empty.")
                    return
                    
                if new_pw != confirm_pw:
                    QMessageBox.warning(self, "Error", "Passwords do not match.")
                    return
                    
                # Check password strength
                if hasattr(self, 'strength_meter') and self.strength_meter is not None:
                    strength = self.strength_meter.validator.calculate_strength(new_pw)
                    if strength < 60:  # Minimum strength threshold
                        reply = QMessageBox.warning(
                            self,
                            "Weak Password",
                            "The password you entered is weak. Are you sure you want to use it?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        if reply == QMessageBox.No:
                            return
                
                # Ask if user wants to generate a recovery key
                if self.mode == 'set':
                    reply = QMessageBox.question(
                        self,
                        "Generate Recovery Key",
                        "Would you like to generate a recovery key?\n\n"
                        "This key will allow you to reset your password if you forget it. "
                        "Keep it in a safe place.",
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Cancel:
                        return
                        
                    recovery_key_path = None
                    if reply == QMessageBox.Yes:
                        # Let user choose where to save the recovery key
                        file_path, _ = QFileDialog.getSaveFileName(
                            self,
                            "Save Recovery Key",
                            "nfc_reader_recovery_key.recovery",
                            "Recovery Key (*.recovery);;All Files (*)"
                        )
                        
                        if not file_path:
                            QMessageBox.warning(self, "Warning", "Password not set. Recovery key file not selected.")
                            return
                            
                        recovery_key_path = file_path
                
                # Set new password with optional recovery key
                if self.auth_manager.set_password(new_pw, recovery_key_path if 'recovery_key_path' in locals() else None):
                    if recovery_key_path:
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Password set successfully.\n\n"
                            f"Recovery key saved to:\n{recovery_key_path}\n\n"
                            "Keep this file in a safe place. You will need it to recover your password "
                            "if you forget it."
                        )
                    else:
                        QMessageBox.information(self, "Success", "Password set successfully.")
                        
                    self.verified.emit()
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to set password.")
            
            else:  # verify mode
                password = self.new_pw_edit.text()
                if self.auth_manager.verify_password(password):
                    self.verified.emit()
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Incorrect password.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def show_recovery_dialog(self) -> None:
        """Show the password recovery dialog."""
        from .recovery_dialog import RecoveryDialog
        
        recovery_dialog = RecoveryDialog(self.auth_manager, self)
        recovery_dialog.recovery_success.connect(self.on_recovery_success)
        recovery_dialog.exec_()
        
    def on_recovery_success(self, new_password: str) -> None:
        """Handle successful password recovery.
        
        Args:
            new_password: The new password that was set
        """
        # Update the UI with the new password
        self.new_pw_edit.setText(new_password)
        
        # Auto-submit the form
        if self.mode == 'verify':
            self.verify()
    
    @staticmethod
    def verify_password(auth_manager: 'AuthManager', parent=None) -> bool:
        """Show password verification dialog.
        
        Returns:
            bool: True if password was verified, False otherwise
        """
        if not auth_manager.is_password_set():
            return True
            
        dialog = PasswordDialog(auth_manager, 'verify', parent)
        result = dialog.exec_()
        return result == QDialog.Accepted
    
    @staticmethod
    def set_password(auth_manager: 'AuthManager', parent=None) -> bool:
        """Show set password dialog.
        
        Returns:
            bool: True if password was set, False otherwise
        """
        dialog = PasswordDialog(
            auth_manager, 
            'change' if auth_manager.is_password_set() else 'set',
            parent
        )
        result = dialog.exec_()
        return result == QDialog.Accepted
