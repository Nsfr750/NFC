"""
NFC Reader/Writer - Core Functionality

This package contains the core functionality for the NFC Reader/Writer application,
including NFC operations, authentication, and user interface components.
"""

# Import core components
from .nfc_operations import NfcOperations
from .auth import AuthManager, PasswordDialog
from .recovery_dialog import RecoveryDialog

# Define package version
__version__ = '1.1.0'
