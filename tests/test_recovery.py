"""
Simple test script for password recovery functionality.
"""
import os
import sys
import tempfile
import json
from pathlib import Path

# Add the script directory to the path
sys.path.append(str(Path(__file__).parent))

# Import the AuthManager and related functions
from script.auth import AuthManager, generate_recovery_key, verify_recovery_key

# Import PySide6 components for testing
from PySide6.QtWidgets import QApplication, QMessageBox

def test_recovery_flow():
    """Test the password recovery flow."""
    print("Starting password recovery test...")
    
    # Create a test directory
    test_dir = tempfile.TemporaryDirectory()
    print(f"Using temporary directory: {test_dir.name}")
    
    try:
        # Initialize auth manager
        auth_manager = AuthManager(config_dir=test_dir.name)
        
        # Test recovery key generation and verification
        print("\n=== Testing recovery key generation ===")
        salt = os.urandom(32)
        password_hash = "test_hash"
        recovery_key_path = os.path.join(test_dir.name, "recovery.key")
        
        # Generate recovery key
        print(f"Generating recovery key at: {recovery_key_path}")
        result = generate_recovery_key(salt, password_hash, recovery_key_path)
        print(f"Recovery key generation {'succeeded' if result else 'failed'}")
        
        # Verify recovery key
        print("\n=== Testing recovery key verification ===")
        is_valid = verify_recovery_key(recovery_key_path, salt, password_hash)
        print(f"Recovery key verification: {'valid' if is_valid else 'invalid'}")
        
        # Test password recovery
        print("\n=== Testing password recovery ===")
        old_password = "old_password"
        new_password = "new_secure_password"
        
        # Set initial password and generate recovery key
        print(f"Setting initial password: {old_password}")
        auth_manager.set_password(old_password, recovery_key_path)
        
        # Verify password was set
        print("Verifying initial password...")
        if auth_manager.verify_password(old_password):
            print("✓ Initial password verified")
        else:
            print("✗ Failed to verify initial password")
            return False
        
        # Recover password
        print(f"\nRecovering password to: {new_password}")
        recovery_success = auth_manager.recover_password(recovery_key_path, new_password)
        print(f"Password recovery {'succeeded' if recovery_success else 'failed'}")
        
        if recovery_success:
            # Verify new password works
            print("Verifying new password...")
            if auth_manager.verify_password(new_password):
                print("✓ New password verified")
            else:
                print("✗ Failed to verify new password")
                return False
            
            # Verify old password no longer works
            print("Verifying old password is no longer valid...")
            if not auth_manager.verify_password(old_password):
                print("✓ Old password is no longer valid")
            else:
                print("✗ Old password is still valid")
                return False
            
            # Verify recovery key was deleted
            if not os.path.exists(recovery_key_path):
                print("✓ Recovery key was deleted after use")
            else:
                print("✗ Recovery key was not deleted after use")
                return False
            
            print("\n✅ All tests passed!")
            return True
        else:
            print("✗ Password recovery failed")
            return False
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        test_dir.cleanup()
        print("\nCleaned up temporary files.")

if __name__ == "__main__":
    # Create QApplication instance if needed
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Run the test
    success = test_recovery_flow()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
