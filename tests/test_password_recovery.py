"""
Test script for password recovery functionality.
"""
import os
import sys
import tempfile
import unittest
import json
from unittest.mock import patch, MagicMock

# Add the script directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import PySide6 components for testing
from PySide6.QtWidgets import QApplication, QMessageBox

# Import the AuthManager and related functions
from script.auth import AuthManager, generate_recovery_key, verify_recovery_key

class TestPasswordRecovery(unittest.TestCase):
    """Test cases for password recovery functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.test_dir.name, 'auth_config.json')
        self.recovery_key_file = os.path.join(self.test_dir.name, 'test_recovery.key')
        
        # Initialize auth manager with test directory
        self.auth_manager = AuthManager(config_dir=self.test_dir.name)
        
    def tearDown(self):
        """Clean up test environment."""
        self.test_dir.cleanup()
    
    def test_generate_recovery_key(self):
        """Test generating a recovery key."""
        # Set up test data
        salt = os.urandom(32)
        password_hash = "test_hash"
        
        # Generate recovery key
        result = generate_recovery_key(salt, password_hash, self.recovery_key_file)
        
        # Verify results
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.recovery_key_file))
        
        # Verify file contents
        with open(self.recovery_key_file, 'r') as f:
            data = f.read()
            self.assertIn('salt', data)
            self.assertIn('recovery_hash', data)
    
    def test_verify_recovery_key_valid(self):
        """Test verifying a valid recovery key."""
        # Set up test data
        salt = os.urandom(32)
        password_hash = "test_hash"
        
        # Generate recovery key
        generate_recovery_key(salt, password_hash, self.recovery_key_file)
        
        # Verify recovery key
        result = verify_recovery_key(self.recovery_key_file, salt, password_hash)
        self.assertTrue(result)
    
    def test_verify_recovery_key_invalid(self):
        """Test verifying an invalid recovery key."""
        # Set up test data
        salt = os.urandom(32)
        password_hash = "test_hash"
        
        # Generate recovery key with different password
        generate_recovery_key(salt, "different_hash", self.recovery_key_file)
        
        # Verify recovery key should fail
        result = verify_recovery_key(self.recovery_key_file, salt, password_hash)
        self.assertFalse(result)
    
    def test_recover_password(self):
        """Test recovering a password using a recovery key."""
        # Set a password and generate a recovery key
        self.auth_manager.set_password("old_password", self.recovery_key_file)
        
        # Simulate password recovery
        new_password = "new_secure_password"
        result = self.auth_manager.recover_password(self.recovery_key_file, new_password)
        
        # Verify results
        self.assertTrue(result)
        self.assertTrue(self.auth_manager.verify_password(new_password))
    
    @patch('PySide6.QtWidgets.QMessageBox')
    def test_recovery_dialog_ui(self, mock_msgbox):
        """Test the recovery dialog UI."""
        from script.recovery_dialog import RecoveryDialog
        
        # Set up mocks
        mock_msgbox.return_value.exec_.return_value = QMessageBox.Ok
        
        # Create and show dialog
        dialog = RecoveryDialog(self.auth_manager)
        
        # Verify UI elements
        self.assertEqual(dialog.windowTitle(), "Password Recovery")
        self.assertTrue(dialog.isVisible())
        
        # Clean up
        dialog.close()
    
    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PySide6.QtWidgets.QMessageBox')
    def test_recovery_flow(self, mock_msgbox, mock_file_dialog):
        """Test the complete password recovery flow."""
        from script.recovery_dialog import RecoveryDialog
        
        # Set up test data
        old_password = "old_password"
        new_password = "new_secure_password"
        
        # Set a password and generate a recovery key
        self.auth_manager.set_password(old_password, self.recovery_key_file)
        
        # Set up mocks
        mock_msgbox.return_value.exec_.return_value = QMessageBox.Ok
        mock_file_dialog.return_value = (self.recovery_key_file, None)
        
        # Create and show recovery dialog
        dialog = RecoveryDialog(self.auth_manager)
        
        # Simulate user input
        dialog.recovery_key_edit.setText(self.recovery_key_file)
        dialog.new_pw_edit.setText(new_password)
        dialog.confirm_pw_edit.setText(new_password)
        
        # Trigger recovery
        dialog.recover_password()
        
        # Verify password was changed
        self.assertTrue(self.auth_manager.verify_password(new_password))
        self.assertFalse(self.auth_manager.verify_password(old_password))
        
        # Verify recovery key was deleted
        self.assertFalse(os.path.exists(self.recovery_key_file))
        
        # Clean up
        dialog.close()

if __name__ == '__main__':
    unittest.main()
