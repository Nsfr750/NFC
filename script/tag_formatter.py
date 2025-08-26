"""
Tag formatting utilities for NFC tag data.

This module provides functionality to format and parse NFC tag data
using custom templates and patterns.
"""
import re
from typing import Dict, List, Optional, Union, Any, Pattern
from dataclasses import dataclass
import json
import os

@dataclass
class TagFormat:
    """Represents a custom tag format with name and pattern."""
    name: str
    pattern: str
    description: str = ""
    template: str = "{data}"  # Default template just returns the data as-is
    
    def format(self, data: Any) -> str:
        """Format data using the template.
        
        Args:
            data: Data to format (usually a string or dict)
            
        Returns:
            Formatted string
        """
        if isinstance(data, str):
            return self.template.format(data=data)
        elif isinstance(data, dict):
            return self.template.format(**data)
        return str(data)
    
    def match(self, text: str) -> Optional[Dict[str, str]]:
        """Check if text matches the pattern and extract groups.
        
        Args:
            text: Text to match against the pattern
            
        Returns:
            Dict of named groups if matched, None otherwise
        """
        match = re.match(self.pattern, text, re.DOTALL)
        if match:
            return match.groupdict()
        return None

class TagFormatter:
    """Manages custom tag formats and provides formatting utilities."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the tag formatter.
        
        Args:
            config_dir: Directory to store format configurations
        """
        self.config_dir = config_dir
        self.formats: Dict[str, TagFormat] = {}
        self._load_formats()
        
        # Add some default formats if none exist
        if not self.formats:
            self._add_default_formats()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists."""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _get_formats_file(self) -> str:
        """Get the path to the formats configuration file."""
        return os.path.join(self.config_dir, "tag_formats.json")
    
    def _load_formats(self) -> None:
        """Load formats from the configuration file."""
        formats_file = self._get_formats_file()
        if not os.path.exists(formats_file):
            return
            
        try:
            with open(formats_file, 'r', encoding='utf-8') as f:
                formats_data = json.load(f)
                self.formats = {
                    name: TagFormat(
                        name=name,
                        pattern=data.get('pattern', ''),
                        description=data.get('description', ''),
                        template=data.get('template', '{data}')
                    )
                    for name, data in formats_data.items()
                }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading tag formats: {e}")
    
    def _save_formats(self) -> None:
        """Save formats to the configuration file."""
        self._ensure_config_dir()
        formats_file = self._get_formats_file()
        
        try:
            with open(formats_file, 'w', encoding='utf-8') as f:
                formats_data = {
                    name: {
                        'pattern': fmt.pattern,
                        'description': fmt.description,
                        'template': fmt.template
                    }
                    for name, fmt in self.formats.items()
                }
                json.dump(formats_data, f, indent=2)
        except IOError as e:
            print(f"Error saving tag formats: {e}")
    
    def _add_default_formats(self) -> None:
        """Add some default useful formats."""
        default_formats = [
            TagFormat(
                name="url",
                pattern=r'^https?://\S+$',
                description="Web URL",
                template="{data}"
            ),
            TagFormat(
                name="vcard",
                pattern=r'^BEGIN:VCARD\n.*\nEND:VCARD$',
                description="vCard contact information",
                template="{data}"
            ),
            TagFormat(
                name="wifi",
                pattern=r'^WIFI:S:(?P<ssid>[^;]+);T:(?P<type>[^;]+);P:(?P<password>[^;]+);;$',
                description="WiFi network credentials",
                template="SSID: {ssid}\nType: {type}\nPassword: {password}"
            ),
            TagFormat(
                name="json",
                pattern=r'^\s*\{.*\}\s*$',
                description="JSON data",
                template="{data}"
            )
        ]
        
        for fmt in default_formats:
            self.formats[fmt.name] = fmt
        
        self._save_formats()
    
    def add_format(self, name: str, pattern: str, template: str, 
                  description: str = "") -> None:
        """Add a new format.
        
        Args:
            name: Unique name for the format
            pattern: Regular expression pattern to match the format
            template: Template for formatting the data
            description: Optional description of the format
        """
        self.formats[name] = TagFormat(
            name=name,
            pattern=pattern,
            template=template,
            description=description
        )
        self._save_formats()
    
    def remove_format(self, name: str) -> bool:
        """Remove a format by name.
        
        Args:
            name: Name of the format to remove
            
        Returns:
            True if the format was removed, False if not found
        """
        if name in self.formats:
            del self.formats[name]
            self._save_formats()
            return True
        return False
    
    def format_data(self, data: str, format_name: Optional[str] = None) -> str:
        """Format data using the specified format.
        
        Args:
            data: Data to format
            format_name: Name of the format to use. If None, will try to detect.
            
        Returns:
            Formatted string
        """
        # If format is specified, use it
        if format_name and format_name in self.formats:
            return self.formats[format_name].format(data)
        
        # Otherwise try to detect the format
        if not format_name:
            for fmt in self.formats.values():
                if fmt.match(data):
                    return fmt.format(data)
        
        # Default formatting
        return str(data)
    
    def detect_format(self, data: str) -> Optional[TagFormat]:
        """Detect the format of the given data.
        
        Args:
            data: Data to analyze
            
        Returns:
            Matching TagFormat or None if no match found
        """
        for fmt in self.formats.values():
            if fmt.match(data):
                return fmt
        return None

# Global instance for easy access
tag_formatter = TagFormatter()
