"""
Settings Manager for NFC Reader/Writer Application
Handles loading and saving application settings to/from JSON file.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class SettingsManager:
    """Manages application settings with JSON file persistence."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the settings manager.
        
        Args:
            config_dir: Directory where settings file will be stored
        """
        self.config_dir = Path(config_dir)
        self.settings_file = self.config_dir / "app_settings.json"
        self.default_settings = {
            "window": {
                "width": 1000,
                "height": 700,
                "x": 100,
                "y": 100,
                "maximized": False
            },
            "nfc": {
                "read_timeout": 10,
                "write_timeout": 30,
                "auto_connect": True
            },
            "ui": {
                "theme": "default",
                "font_size": 10,
                "show_status_bar": True,
                "show_toolbar": True
            },
            "recent_files": [],
            "tag_database": {
                "path": "data/tags.db",
                "auto_backup": True,
                "backup_count": 5
            },
            "security": {
                "require_password": False,
                "password_hash": "",
                "password_salt": "",
                "session_timeout": 300  # 5 minutes
            }
        }
        self.settings = self.default_settings.copy()
        self.load_settings()
    
    def load_settings(self) -> bool:
        """Load settings from JSON file.
        
        Returns:
            bool: True if settings were loaded successfully, False otherwise
        """
        try:
            if not self.settings_file.exists():
                # Create default settings file if it doesn't exist
                self.config_dir.mkdir(parents=True, exist_ok=True)
                self.save_settings()
                return True
                
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                self._merge_settings(loaded_settings)
                return True
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
    
    def save_settings(self) -> bool:
        """Save current settings to JSON file.
        
        Returns:
            bool: True if settings were saved successfully, False otherwise
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def _merge_settings(self, new_settings: Dict[str, Any]) -> None:
        """Merge loaded settings with defaults.
        
        Args:
            new_settings: Dictionary containing loaded settings
        """
        def merge(dest: Dict[str, Any], source: Dict[str, Any]) -> None:
            for key, value in source.items():
                if key in dest and isinstance(dest[key], dict) and isinstance(value, dict):
                    merge(dest[key], value)
                else:
                    dest[key] = value
        
        merge(self.settings, new_settings)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by dot notation key.
        
        Args:
            key: Dot notation key (e.g., 'ui.theme')
            default: Default value if key is not found
            
        Returns:
            The setting value or default if not found
        """
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """Set a setting value by dot notation key.
        
        Args:
            key: Dot notation key (e.g., 'ui.theme')
            value: Value to set
            save: Whether to save settings to disk after updating
            
        Returns:
            bool: True if successful, False otherwise
        """
        keys = key.split('.')
        current = self.settings
        
        try:
            for k in keys[:-1]:
                if k not in current or not isinstance(current[k], dict):
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
            if save:
                return self.save_settings()
            return True
            
        except Exception as e:
            print(f"Error setting {key}: {e}")
            return False

# Global instance for application-wide use
settings_manager = SettingsManager()
