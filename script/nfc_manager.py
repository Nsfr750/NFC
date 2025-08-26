#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFC Manager Module

This module provides a unified interface for NFC operations,
integrating with both the existing NFCThread and new NfcOperations.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from .nfc_operations import NfcOperations, TagType

logger = logging.getLogger(__name__)

class NFCManager:
    """Manages NFC operations and integrates with the UI."""
    
    def __init__(self, nfc_thread):
        """Initialize the NFC manager with an existing NFC thread."""
        self.nfc_thread = nfc_thread
        self.nfc_ops = NfcOperations()
        self.current_tag = None
        self._init_signals()
    
    def _init_signals(self):
        """Connect signals between NFC thread and operations."""
        self.nfc_thread.tag_detected.connect(self._on_tag_detected)
        self.nfc_thread.error_occurred.connect(self._on_error)
    
    def _on_tag_detected(self, tag_info: Dict[str, Any]) -> None:
        """Handle tag detection from the NFC thread."""
        self.current_tag = tag_info
        tag_type = self._map_tag_type(tag_info.get('type', ''))
        
        # Update NFC operations with the detected tag
        self.nfc_ops.current_tag = {
            'type': tag_type,
            'uid': tag_info.get('uid', ''),
            'atqa': tag_info.get('atqa', ''),
            'sak': tag_info.get('sak', '')
        }
        
        # Log the detection
        logger.info(f"Tag detected: {tag_type.name if tag_type else 'Unknown'}, UID: {tag_info.get('uid', 'N/A')}")
    
    def _on_error(self, level: str, message: str) -> None:
        """Handle errors from the NFC thread."""
        logger.log(getattr(logging, level.upper(), logging.ERROR), message)
    
    def _map_tag_type(self, tag_type: str) -> TagType:
        """Map NFC thread tag types to NfcOperations tag types."""
        type_mapping = {
            'nfc.mifare.classic': TagType.MIFARE_CLASSIC_1K,  # Will be updated to 4K if needed
            'nfc.mifare.ultralight': TagType.MIFARE_ULTRALIGHT,
            'nfc.ntag.ntag21x': TagType.NTAG_213,  # Default to NTAG213, can be updated
            'nfc.felica': TagType.FELICA,
            'nfc.iso14443.4a': TagType.UNKNOWN,  # Could be Type 4
            'nfc.iso15693': TagType.UNKNOWN,     # Could be Type 5
            'nfc.jewel': TagType.JEWEL,
            'nfc.topaz': TagType.TOPAZ
        }
        return type_mapping.get(tag_type.lower(), TagType.UNKNOWN)
    
    def get_tag_info(self) -> Dict[str, Any]:
        """Get information about the current tag."""
        if not self.current_tag:
            return {'status': 'No tag detected'}
        
        tag_info = self.nfc_ops.get_tag_info()
        
        # Add additional info from NFC thread if available
        if self.current_tag:
            tag_info.update({
                'formatted_uid': self.current_tag.get('formatted_uid', ''),
                'atqa': self.current_tag.get('atqa', ''),
                'sak': self.current_tag.get('sak', ''),
                'type_name': self.current_tag.get('type', 'Unknown')
            })
        
        return tag_info
    
    def authenticate_mifare(self, block: int, key_type: str = 'A', key: bytes = None) -> bool:
        """Authenticate with a MIFARE Classic tag."""
        if not self.current_tag:
            logger.warning("No tag detected for authentication")
            return False
            
        if not self.nfc_ops.current_tag or self.nfc_ops.current_tag['type'] not in [TagType.MIFARE_CLASSIC_1K, TagType.MIFARE_CLASSIC_4K]:
            logger.warning("Current tag does not support MIFARE authentication")
            return False
            
        return self.nfc_ops.mifare_authenticate(block, key_type, key)
    
    def read_block(self, block: int) -> Optional[bytes]:
        """Read a block from the current tag."""
        if not self.current_tag:
            logger.warning("No tag detected for reading")
            return None
            
        return self.nfc_ops.read_block(block)
    
    def write_block(self, block: int, data: bytes) -> bool:
        """Write data to a block on the current tag."""
        if not self.current_tag:
            logger.warning("No tag detected for writing")
            return False
            
        return self.nfc_ops.write_block(block, data)
    
    def format_tag(self) -> bool:
        """Format the current tag if supported."""
        if not self.current_tag:
            logger.warning("No tag detected for formatting")
            return False
            
        # Implementation depends on tag type
        if self.nfc_ops.current_tag['type'] in [TagType.MIFARE_ULTRALIGHT, TagType.NTAG_213, TagType.NTAG_215, TagType.NTAG_216]:
            # For NTAG and Ultralight, we can write 0x00 to all user memory
            return self._format_ntag()
        elif self.nfc_ops.current_tag['type'] in [TagType.MIFARE_CLASSIC_1K, TagType.MIFARE_CLASSIC_4K]:
            # For MIFARE Classic, we need to authenticate and write to each sector
            return self._format_mifare_classic()
        else:
            logger.warning(f"Formatting not supported for tag type: {self.nfc_ops.current_tag['type']}")
            return False
    
    def _format_ntag(self) -> bool:
        """Format an NTAG or Ultralight tag by writing zeros to user memory."""
        # Implementation for NTAG/Ultralight formatting
        # This is a simplified example - actual implementation should handle error cases
        try:
            # Get tag size from the current tag info
            tag_size = self.nfc_ops._get_tag_size()
            
            # Write zeros to all user-accessible memory
            block_size = 4  # NTAG/Ultralight blocks are 4 bytes
            for block in range(4, tag_size // block_size):  # Skip manufacturer block
                if not self.write_block(block, b'\x00' * block_size):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error formatting NTAG/Ultralight: {e}")
            return False
    
    def _format_mifare_classic(self) -> bool:
        """Format a MIFARE Classic tag by writing zeros to all sectors."""
        # Implementation for MIFARE Classic formatting
        # This is a simplified example - actual implementation should handle error cases
        try:
            # For MIFARE Classic 1K: 16 sectors, 4 blocks per sector, 16 bytes per block
            # For MIFARE Classic 4K: 40 sectors, 4 blocks per sector, 16 bytes per block
            is_4k = (self.nfc_ops.current_tag['type'] == TagType.MIFARE_CLASSIC_4K)
            num_sectors = 40 if is_4k else 16
            
            for sector in range(num_sectors):
                # Skip sector trailer blocks (last block of each sector)
                blocks_per_sector = 4
                for block in range(blocks_per_sector - 1):  # Skip sector trailer
                    block_num = (sector * blocks_per_sector) + block
                    if not self.authenticate_mifare(block_num):
                        logger.warning(f"Failed to authenticate sector {sector}")
                        continue
                    if not self.write_block(block_num, b'\x00' * 16):
                        logger.warning(f"Failed to write block {block_num}")
                        continue
            return True
        except Exception as e:
            logger.error(f"Error formatting MIFARE Classic: {e}")
            return False
