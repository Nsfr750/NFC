#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFC Operations Module

This module provides functionality for:
- MIFARE Classic 1K/4K authentication
- NFC Forum Tag Types 1-5 support
- Contactless smart card operations
"""

import logging
from enum import Enum, auto
from typing import Optional, Union, Tuple, Dict, Any, List

# Set up logging
logger = logging.getLogger(__name__)

class TagType(Enum):
    """Enumeration of supported NFC tag types according to NFC Forum specifications."""
    # NFC Forum Tag Types
    TYPE_1_TOPAS = auto()        # Type 1 (Topaz, Jewel)
    TYPE_2_MIFARE_ULTRALIGHT = auto()  # Type 2 (MIFARE Ultralight, NTAG)
    TYPE_3_FELICA = auto()       # Type 3 (FeliCa)
    TYPE_4_DESFIRE = auto()      # Type 4 (DESFire, ISO 14443-4)
    TYPE_5_VICINITY = auto()     # Type 5 (Vicinity, ISO 15693)
    
    # Additional MIFARE types for backward compatibility
    MIFARE_ULTRALIGHT = auto()   # Alias for TYPE_2_MIFARE_ULTRALIGHT
    MIFARE_CLASSIC_1K = auto()   # MIFARE Classic 1K
    MIFARE_CLASSIC_4K = auto()   # MIFARE Classic 4K
    
    # NTAG variants (Type 2)
    NTAG_213 = auto()
    NTAG_215 = auto()
    NTAG_216 = auto()
    
    # Other types for backward compatibility
    DESFIRE = auto()             # Alias for TYPE_4_DESFIRE
    FELICA = auto()              # Alias for TYPE_3_FELICA
    JEWEL = auto()               # Alias for TYPE_1_TOPAS
    TOPAZ = auto()               # Alias for TYPE_1_TOPAS
    
    UNKNOWN = auto()

class NfcOperations:
    """Main class for NFC operations."""
    
    def __init__(self, reader=None):
        """Initialize NFC operations with an optional reader instance."""
        self.reader = reader
        self.authenticated = False
        self.current_tag = None
        
    def connect(self, port: Optional[str] = None, baudrate: int = 115200) -> bool:
        """Connect to the NFC reader."""
        try:
            # Implementation for connecting to the reader
            # This is a placeholder - actual implementation depends on the reader's API
            if port is None:
                # Auto-detect port if not specified
                pass
            return True
        except Exception as e:
            logger.error(f"Failed to connect to reader: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the NFC reader."""
        self.authenticated = False
        self.current_tag = None
        
    def detect_tag(self) -> Optional[Dict[str, Any]]:
        """Detect and identify the NFC tag.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing tag information including:
                - type (TagType): The detected tag type
                - uid (str): Tag UID in hex format (colon-separated)
                - atqa (str): Answer To Request A (2 bytes hex)
                - sak (str): Select Acknowledge (1 byte hex)
                - ats (str): Answer To Select (variable length hex)
                - memory_size (int): Tag memory size in bytes (0 if variable/unknown)
                - is_iso14443a (bool): Whether tag is ISO 14443-A compatible
                - is_iso15693 (bool): Whether tag is ISO 15693 (Type 5) compatible
        """
        try:
            if self.reader is None:
                logger.error("No reader available")
                return None
                
            # Try to detect the tag using the reader
            tag_info = self._detect_tag_type()
            if not tag_info:
                return None
                
            # Update current tag
            self.current_tag = tag_info
            return tag_info
            
        except Exception as e:
            logger.error(f"Error detecting tag: {e}", exc_info=True)
            return None
            
    def _detect_tag_type(self) -> Optional[Dict[str, Any]]:
        """Internal method to detect and identify the tag type."""
        try:
            # Get basic tag information
            atqa = self._get_atqa()  # Answer To Request A
            sak = self._get_sak()    # Select Acknowledge
            uid = self._get_uid()    # Tag UID
            ats = self._get_ats()    # Answer To Select (for Type 4 tags)
            
            # Default tag info
            tag_info = {
                'type': TagType.UNKNOWN,
                'uid': uid,
                'atqa': atqa,
                'sak': sak,
                'ats': ats,
                'memory_size': 0,
                'is_iso14443a': False,
                'is_iso15693': False
            }
            
            # Detect tag type based on SAK and ATQA
            if atqa and sak:
                # Type 1 (Topaz)
                if self._is_type1_tag(sak, atqa):
                    tag_info.update({
                        'type': TagType.TYPE_1_TOPAS,
                        'memory_size': 96,  # 96 bytes user memory
                        'is_iso14443a': True
                    })
                # Type 2 (MIFARE Ultralight, NTAG)
                elif self._is_type2_tag(sak, atqa):
                    # Further detect specific Type 2 variants
                    if self._is_ntag21x(uid):
                        if self._is_ntag213():
                            tag_info.update({
                                'type': TagType.NTAG_213,
                                'memory_size': 180
                            })
                        elif self._is_ntag215():
                            tag_info.update({
                                'type': TagType.NTAG_215,
                                'memory_size': 540
                            })
                        elif self._is_ntag216():
                            tag_info.update({
                                'type': TagType.NTAG_216,
                                'memory_size': 888
                            })
                    else:
                        # Generic MIFARE Ultralight
                        tag_info.update({
                            'type': TagType.TYPE_2_MIFARE_ULTRALIGHT,
                            'memory_size': 64
                        })
                    tag_info['is_iso14443a'] = True
                # Type 3 (FeliCa)
                elif self._is_type3_tag(sak, atqa):
                    tag_info.update({
                        'type': TagType.TYPE_3_FELICA,
                        'memory_size': 0  # Variable size
                    })
                # Type 4 (DESFire, ISO 14443-4)
                elif self._is_type4_tag(sak, atqa):
                    tag_info.update({
                        'type': TagType.TYPE_4_DESFIRE,
                        'memory_size': 0,  # Variable size
                        'is_iso14443a': True
                    })
                # MIFARE Classic
                elif self._is_mifare_classic(sak, atqa):
                    if self._is_mifare_4k():
                        tag_info.update({
                            'type': TagType.MIFARE_CLASSIC_4K,
                            'memory_size': 4096
                        })
                    else:
                        tag_info.update({
                            'type': TagType.MIFARE_CLASSIC_1K,
                            'memory_size': 1024
                        })
                    tag_info['is_iso14443a'] = True
            
            # Check for Type 5 (ISO 15693)
            elif self._is_type5_tag():
                tag_info.update({
                    'type': TagType.TYPE_5_VICINITY,
                    'memory_size': 0,  # Variable size
                    'is_iso15693': True
                })
            
            return tag_info
            
        except Exception as e:
            logger.error(f"Error in tag type detection: {e}", exc_info=True)
            return None
    
    # Helper methods for tag type detection
    def _get_atqa(self) -> str:
        """Get ATQA (Answer To Request A) from the tag."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return "00 00"
    
    def _get_sak(self) -> str:
        """Get SAK (Select Acknowledge) from the tag."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return "00"
    
    def _get_uid(self) -> str:
        """Get UID from the tag."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return "00:00:00:00"
    
    def _get_ats(self) -> str:
        """Get ATS (Answer To Select) from the tag (Type 4)."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return ""
    
    def _is_type1_tag(self, sak: str, atqa: str) -> bool:
        """Check if tag is Type 1 (Topaz)."""
        # Type 1 tags have ATQA=00 04 and SAK=00
        return atqa == "00 04" and sak == "00"
    
    def _is_type2_tag(self, sak: str, atqa: str) -> bool:
        """Check if tag is Type 2 (MIFARE Ultralight, NTAG)."""
        # Type 2 tags have ATQA=00 44 and SAK=00
        return atqa == "00 44" and sak == "00"
    
    def _is_type3_tag(self, sak: str, atqa: str) -> bool:
        """Check if tag is Type 3 (FeliCa)."""
        # FeliCa tags have ATQA=00 03 and SAK=01
        return atqa == "00 03" and sak == "01"
    
    def _is_type4_tag(self, sak: str, atqa: str) -> bool:
        """Check if tag is Type 4 (ISO 14443-4)."""
        # Type 4 tags have SAK=20
        return sak == "20"
    
    def _is_type5_tag(self) -> bool:
        """Check if tag is Type 5 (ISO 15693)."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return False
    
    def _is_mifare_classic(self, sak: str, atqa: str) -> bool:
        """Check if tag is MIFARE Classic."""
        # MIFARE Classic tags have ATQA=00 04 and SAK=08/18/28/38
        return atqa == "00 04" and sak in ["08", "18", "28", "38"]
    
    def _is_mifare_4k(self) -> bool:
        """Check if MIFARE Classic tag is 4K."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return False
    
    def _is_ntag21x(self, uid: str) -> bool:
        """Check if tag is NTAG21x series."""
        # NTAG21x tags have UID starting with 04:04
        return uid.startswith("04:04")
    
    def _is_ntag213(self) -> bool:
        """Check if tag is NTAG213."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return False
    
    def _is_ntag215(self) -> bool:
        """Check if tag is NTAG215."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return False
    
    def _is_ntag216(self) -> bool:
        """Check if tag is NTAG216."""
        # Implementation depends on the reader's API
        # This is a placeholder - replace with actual implementation
        return False
    
    # Type 2 (MIFARE Ultralight/NTAG) Operations
    def read_type2_tag(self) -> Optional[bytes]:
        """Read all data from a Type 2 (MIFARE Ultralight/NTAG) tag.
        
        Returns:
            Optional[bytes]: Tag data or None if read fails
        """
        if not self._is_type2_tag(self._get_sak(), self._get_atqa()):
            logger.error("Not a Type 2 (MIFARE Ultralight/NTAG) tag")
            return None
            
        try:
            # Read the first page to determine tag type and memory size
            page0 = self._read_type2_page(0)
            if not page0:
                logger.error("Failed to read page 0")
                return None
                
            # Determine tag type and memory size
            is_ntag = self._is_ntag21x(self._get_uid())
            
            # Read all available pages
            data = bytearray()
            page = 0
            
            while True:
                page_data = self._read_type2_page(page)
                if not page_data:
                    break
                    
                data.extend(page_data)
                page += 1
                
                # Stop if we've reached the end of the tag's memory
                if is_ntag and page >= 0xE3:  # NTAG216 has 231 pages max
                    break
                elif not is_ntag and page >= 0x10:  # Standard Ultralight has 16 pages
                    break
                    
            return bytes(data)
            
        except Exception as e:
            logger.error(f"Error reading Type 2 tag: {e}", exc_info=True)
            return None
    
    def _read_type2_page(self, page: int) -> Optional[bytes]:
        """Read a single page from a Type 2 tag.
        
        Args:
            page: Page number
            
        Returns:
            Optional[bytes]: Page data (4 bytes) or None if read fails
        """
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return 4 bytes of data from the specified page
            return b'\x00' * 4
        except Exception as e:
            logger.error(f"Error reading Type 2 page {page:02X}: {e}")
            return None
    
    def write_type2_tag(self, data: bytes, start_page: int = 4) -> bool:
        """Write data to a Type 2 (MIFARE Ultralight/NTAG) tag.
        
        Args:
            data: Data to write
            start_page: Starting page number (default: 4 to skip system area)
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not self._is_type2_tag(self._get_sak(), self._get_atqa()):
            logger.error("Not a Type 2 (MIFARE Ultralight/NTAG) tag")
            return False
            
        if not isinstance(data, (bytes, bytearray)):
            logger.error("Data must be bytes or bytearray")
            return False
            
        # Check if this is an NTAG21x tag
        is_ntag = self._is_ntag21x(self._get_uid())
        
        # Get tag capacity
        if is_ntag:
            # Read NTAG version to determine exact model
            version = self._read_ntag_version()
            if version:
                if version.get('vendor_id') == 0x04 and version.get('type') == 0x04:
                    if version.get('subtype') == 0x0F:  # NTAG216
                        max_pages = 0xE3  # 231 pages (924 bytes)
                    elif version.get('subtype') == 0x11:  # NTAG215
                        max_pages = 0x86  # 135 pages (540 bytes)
                    else:  # NTAG213
                        max_pages = 0x2B  # 45 pages (180 bytes)
                else:
                    max_pages = 0x2B  # Default to NTAG213 if version read fails
            else:
                max_pages = 0x2B  # Default to NTAG213 if version read fails
        else:
            # Standard MIFARE Ultralight
            max_pages = 0x10  # 16 pages (64 bytes)
        
        # Check if data exceeds available space
        max_data_length = (max_pages - start_page) * 4
        if len(data) > max_data_length:
            logger.warning(f"Data exceeds tag capacity, truncating to {max_data_length} bytes")
            data = data[:max_data_length]
        
        # Pad data to multiple of 4 bytes
        padded_data = data.ljust((len(data) + 3) // 4 * 4, b'\x00')
        
        try:
            # Write data in 4-byte pages
            for i in range(0, len(padded_data), 4):
                page = start_page + (i // 4)
                if page >= max_pages:
                    break
                    
                page_data = padded_data[i:i+4]
                if not self._write_type2_page(page, page_data):
                    logger.error(f"Failed to write page {page:02X}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error writing Type 2 tag: {e}", exc_info=True)
            return False
    
    def _write_type2_page(self, page: int, data: bytes) -> bool:
        """Write a single page to a Type 2 tag.
        
        Args:
            page: Page number
            data: 4 bytes of data to write
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not isinstance(data, (bytes, bytearray)) or len(data) != 4:
            logger.error("Data must be exactly 4 bytes")
            return False
            
        # Check if page is in writable range
        if page < 0 or (self._is_ntag21x(self._get_uid()) and page >= 0xE3) or (not self._is_ntag21x(self._get_uid()) and page >= 0x10):
            logger.error(f"Invalid page number: {page:02X}")
            return False
            
        # Check if page is write-protected
        if page < 4:  # System area is read-only
            logger.warning(f"Page {page:02X} is in read-only system area")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should write 4 bytes to the specified page
            return True
            
        except Exception as e:
            logger.error(f"Error writing Type 2 page {page:02X}: {e}")
            return False
    
    def _read_ntag_version(self) -> Optional[Dict[str, int]]:
        """Read NTAG version information.
        
        Returns:
            Optional[Dict[str, int]]: Dictionary containing version information or None if read fails
        """
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return a dictionary with version information
            return {
                'vendor_id': 0x04,  # NXP
                'type': 0x04,       # NTAG
                'subtype': 0x0F,    # NTAG216
                'major': 0x01,      # Major version
                'minor': 0x00       # Minor version
            }
        except Exception as e:
            logger.error(f"Error reading NTAG version: {e}")
            return None
    
    # Type 3 (FeliCa) Operations
    def read_type3_tag(self) -> Optional[Dict[str, Any]]:
        """Read data from a Type 3 (FeliCa) tag.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing tag data or None if read fails
        """
        if not self._is_type3_tag(self._get_sak(), self._get_atqa()):
            logger.error("Not a Type 3 (FeliCa) tag")
            return None
            
        try:
            # Get system code and IDm (Manufacturer ID)
            system_code = self._felica_get_system_code()
            idm = self._felica_get_idm()
            
            if not system_code or not idm:
                logger.error("Failed to get FeliCa system code or IDm")
                return None
                
            # Get service list
            services = self._felica_get_service_list(system_code)
            if not services:
                logger.warning("No services found on FeliCa tag")
                return {
                    'system_code': system_code.hex(),
                    'idm': idm.hex(),
                    'services': [],
                    'blocks': {}
                }
                
            # Read all blocks from all services
            blocks_data = {}
            for service in services:
                # Get number of blocks for this service
                block_count = self._felica_get_block_count(service)
                if block_count == 0:
                    continue
                    
                # Read all blocks for this service
                service_blocks = {}
                for block_num in range(block_count):
                    block_data = self._felica_read_block(service, block_num)
                    if block_data is not None:
                        service_blocks[f"block_{block_num:02X}"] = block_data.hex()
                        
                if service_blocks:
                    blocks_data[service.hex()] = service_blocks
                    
            return {
                'system_code': system_code.hex(),
                'idm': idm.hex(),
                'services': [s.hex() for s in services],
                'blocks': blocks_data
            }
            
        except Exception as e:
            logger.error(f"Error reading FeliCa tag: {e}", exc_info=True)
            return None
    
    def write_type3_tag(self, service_code: bytes, block_data: Dict[int, bytes]) -> bool:
        """Write data to a Type 3 (FeliCa) tag.
        
        Args:
            service_code: 2-byte service code to write to
            block_data: Dictionary mapping block numbers to data (16 bytes per block)
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not self._is_type3_tag(self._get_sak(), self._get_atqa()):
            logger.error("Not a Type 3 (FeliCa) tag")
            return False
            
        if not isinstance(service_code, bytes) or len(service_code) != 2:
            logger.error("Service code must be 2 bytes")
            return False
            
        if not isinstance(block_data, dict):
            logger.error("Block data must be a dictionary")
            return False
            
        try:
            # Verify the service exists
            system_code = self._felica_get_system_code()
            services = self._felica_get_service_list(system_code)
            
            if service_code not in services:
                logger.error(f"Service {service_code.hex()} not found on tag")
                return False
                
            # Write each block
            for block_num, data in block_data.items():
                if not isinstance(data, bytes) or len(data) != 16:
                    logger.warning(f"Skipping invalid block {block_num}: must be 16 bytes")
                    continue
                    
                if not self._felica_write_block(service_code, block_num, data):
                    logger.error(f"Failed to write block {block_num}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error writing to FeliCa tag: {e}", exc_info=True)
            return False
    
    # FeliCa Helper Methods
    def _felica_get_system_code(self) -> Optional[bytes]:
        """Get the system code from a FeliCa tag."""
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return 2-byte system code
            return b'\x88\xB4'  # Common system code for FeliCa Lite-S
        except Exception as e:
            logger.error(f"Error getting FeliCa system code: {e}")
            return None
    
    def _felica_get_idm(self) -> Optional[bytes]:
        """Get the IDm (Manufacturer ID) from a FeliCa tag."""
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return 8-byte IDm
            return b'\x01\x02\x03\x04\x05\x06\x07\x08'
        except Exception as e:
            logger.error(f"Error getting FeliCa IDm: {e}")
            return None
    
    def _felica_get_service_list(self, system_code: bytes) -> List[bytes]:
        """Get the list of services available on a FeliCa tag."""
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return a list of 2-byte service codes
            return [
                b'\x00\x09',  # NDEF service
                b'\x00\x0B'   # System service
            ]
        except Exception as e:
            logger.error(f"Error getting FeliCa service list: {e}")
            return []
    
    def _felica_get_block_count(self, service_code: bytes) -> int:
        """Get the number of blocks for a specific service."""
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return the number of blocks for the given service
            return 16  # Default block count for NDEF service
        except Exception as e:
            logger.error(f"Error getting block count for service {service_code.hex()}: {e}")
            return 0
    
    def _felica_read_block(self, service_code: bytes, block_num: int) -> Optional[bytes]:
        """Read a block from a FeliCa tag."""
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return 16 bytes of data from the specified block
            return bytes([(block_num + i) % 256 for i in range(16)])
        except Exception as e:
            logger.error(f"Error reading block {block_num}: {e}")
            return None
    
    def _felica_write_block(self, service_code: bytes, block_num: int, data: bytes) -> bool:
        """Write a block to a FeliCa tag."""
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should write 16 bytes of data to the specified block
            return True
        except Exception as e:
            logger.error(f"Error writing block {block_num}: {e}")
            return False
    
    # Type 4 (DESFire) Operations
    def desfire_connect(self) -> bool:
        """Establish a connection to a DESFire tag.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if not self._is_type4_tag(self._get_sak(), self._get_atqa()):
            logger.error("Not a Type 4 (DESFire) tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should establish a connection to the DESFire tag
            self._desfire_connected = True
            return True
        except Exception as e:
            logger.error(f"Error connecting to DESFire tag: {e}")
            self._desfire_connected = False
            return False
    
    def desfire_disconnect(self) -> None:
        """Disconnect from a DESFire tag."""
        self._desfire_connected = False
    
    def desfire_authenticate(self, key_number: int = 0, key: bytes = None) -> bool:
        """Authenticate with a DESFire tag.
        
        Args:
            key_number: Key number to use for authentication (0-13)
            key: 16-byte AES key (or 24-byte for 3K3DES, 16/24/32-byte for AES)
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should authenticate with the specified key
            return True
        except Exception as e:
            logger.error(f"DESFire authentication failed: {e}")
            return False
    
    def desfire_get_applications(self) -> List[bytes]:
        """Get list of application IDs on the DESFire tag.
        
        Returns:
            List[bytes]: List of 3-byte application IDs
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return []
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return a list of application IDs (3 bytes each)
            return [b'\x00\x00\x00']  # Default application
        except Exception as e:
            logger.error(f"Failed to get DESFire applications: {e}")
            return []
    
    def desfire_select_application(self, app_id: bytes) -> bool:
        """Select an application on the DESFire tag.
        
        Args:
            app_id: 3-byte application ID to select
            
        Returns:
            bool: True if application was selected successfully, False otherwise
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should select the specified application
            self._current_application = app_id
            return True
        except Exception as e:
            logger.error(f"Failed to select DESFire application: {e}")
            return False
    
    def desfire_get_files(self) -> Dict[int, Dict[str, Any]]:
        """Get list of files in the current application.
        
        Returns:
            Dict[int, Dict[str, Any]]: Dictionary mapping file numbers to file info
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return {}
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return a dictionary of file information
            return {
                0: {
                    'type': 'standard',
                    'size': 32,
                    'access_rights': b'\x00\x00',
                    'settings': b'\x00'
                }
            }
        except Exception as e:
            logger.error(f"Failed to get DESFire files: {e}")
            return {}
    
    def desfire_read_file(self, file_number: int, offset: int = 0, length: int = None) -> Optional[bytes]:
        """Read data from a file on the DESFire tag.
        
        Args:
            file_number: File number to read from
            offset: Offset to start reading from
            length: Number of bytes to read (None for all remaining)
            
        Returns:
            Optional[bytes]: File data or None if read fails
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return None
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should read the specified file data
            return b'DESFire File Data'  # Example data
        except Exception as e:
            logger.error(f"Failed to read DESFire file {file_number}: {e}")
            return None
    
    def desfire_write_file(self, file_number: int, data: bytes, offset: int = 0) -> bool:
        """Write data to a file on the DESFire tag.
        
        Args:
            file_number: File number to write to
            data: Data to write
            offset: Offset to start writing at
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return False
            
        if not isinstance(data, (bytes, bytearray)):
            logger.error("Data must be bytes or bytearray")
            return False
            
        try:
            is_supported, error_message = self._is_operation_supported('write', TagType.DESFIRE)
            if not is_supported:
                logger.error(error_message)
                return False
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should write the data to the specified file
            return True
        except Exception as e:
            logger.error(f"Failed to write to DESFire file {file_number}: {e}")
            return False
    
    def desfire_create_application(self, app_id: bytes, key_settings: bytes, 
                                 num_keys: int = 1, key_type: str = 'AES') -> bool:
        """Create a new application on the DESFire tag.
        
        Args:
            app_id: 3-byte application ID
            key_settings: Key settings byte
            num_keys: Number of keys in the application
            key_type: Type of keys ('AES', '3K3DES', 'DES')
            
        Returns:
            bool: True if application was created successfully, False otherwise
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should create a new application with the specified settings
            return True
        except Exception as e:
            logger.error(f"Failed to create DESFire application: {e}")
            return False
    
    def desfire_delete_application(self, app_id: bytes) -> bool:
        """Delete an application from the DESFire tag.
        
        Args:
            app_id: 3-byte application ID to delete
            
        Returns:
            bool: True if application was deleted successfully, False otherwise
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should delete the specified application
            return True
        except Exception as e:
            logger.error(f"Failed to delete DESFire application: {e}")
            return False
    
    def desfire_format_picc(self) -> bool:
        """Format the DESFire tag (delete all applications and data).
        
        Returns:
            bool: True if format was successful, False otherwise
        """
        if not self._desfire_connected:
            logger.error("Not connected to a DESFire tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should format the entire tag
            return True
        except Exception as e:
            logger.error(f"Failed to format DESFire tag: {e}")
            return False
    
    # Type 5 (ISO 15693) Operations
    def iso15693_connect(self) -> bool:
        """Establish a connection to an ISO 15693 (Type 5) tag.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if not self._is_type5_tag():
            logger.error("Not a Type 5 (ISO 15693) tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should establish a connection to the ISO 15693 tag
            self._iso15693_connected = True
            self._iso15693_uid = self._iso15693_get_uid()
            return True
        except Exception as e:
            logger.error(f"Error connecting to ISO 15693 tag: {e}")
            self._iso15693_connected = False
            return False
    
    def iso15693_disconnect(self) -> None:
        """Disconnect from an ISO 15693 tag."""
        self._iso15693_connected = False
        self._iso15693_uid = None
    
    def iso15693_read_blocks(self, start_block: int, num_blocks: int = 1) -> Optional[bytes]:
        """Read one or more blocks from an ISO 15693 tag.
        
        Args:
            start_block: Starting block number
            num_blocks: Number of blocks to read (default: 1)
            
        Returns:
            Optional[bytes]: Block data or None if read fails
        """
        if not self._iso15693_connected:
            logger.error("Not connected to an ISO 15693 tag")
            return None
            
        if num_blocks < 1:
            logger.error("Number of blocks must be at least 1")
            return None
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should read the specified blocks (typically 4 bytes per block)
            return b'\x00' * (num_blocks * 4)  # 4 bytes per block
        except Exception as e:
            logger.error(f"Failed to read ISO 15693 blocks: {e}")
            return None
    
    def iso15693_write_blocks(self, start_block: int, data: bytes) -> bool:
        """Write data to one or more blocks on an ISO 15693 tag.
        
        Args:
            start_block: Starting block number
            data: Data to write (must be a multiple of block size, typically 4 bytes)
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not self._iso15693_connected:
            logger.error("Not connected to an ISO 15693 tag")
            return False
            
        if not isinstance(data, (bytes, bytearray)):
            logger.error("Data must be bytes or bytearray")
            return False
            
        if len(data) % 4 != 0:  # ISO 15693 typically uses 4-byte blocks
            logger.error("Data length must be a multiple of 4")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should write the data to the specified blocks
            return True
        except Exception as e:
            logger.error(f"Failed to write ISO 15693 blocks: {e}")
            return False
    
    def iso15693_lock_block(self, block_number: int) -> bool:
        """Permanently lock a block on an ISO 15693 tag.
        
        Args:
            block_number: Block number to lock
            
        Returns:
            bool: True if block was locked successfully, False otherwise
        """
        if not self._iso15693_connected:
            logger.error("Not connected to an ISO 15693 tag")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should lock the specified block
            return True
        except Exception as e:
            logger.error(f"Failed to lock ISO 15693 block {block_number}: {e}")
            return False
    
    def iso15693_get_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the ISO 15693 tag.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing tag information or None if failed
        """
        if not self._iso15693_connected:
            logger.error("Not connected to an ISO 15693 tag")
            return None
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return a dictionary with tag information
            return {
                'uid': self._iso15693_uid.hex() if self._iso15693_uid else None,
                'block_size': 4,  # Typically 4 bytes per block
                'total_blocks': 64,  # Example: 256 bytes total (64 blocks * 4 bytes)
                'dsfid': 0x00,  # Data Storage Format Identifier
                'afi': 0x00,    # Application Family Identifier
                'ic_ref': 0x00  # IC Reference
            }
        except Exception as e:
            logger.error(f"Failed to get ISO 15693 tag info: {e}")
            return None
    
    def _iso15693_get_uid(self) -> Optional[bytes]:
        """Get the UID of the ISO 15693 tag."""
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return the 8-byte UID of the tag
            return b'\x01\x02\x03\x04\x05\x06\x07\x08'
        except Exception as e:
            logger.error(f"Failed to get ISO 15693 UID: {e}")
            return None
    
    # Type 1 (Topaz) Operations
    def read_type1_tag(self) -> Optional[bytes]:
        """Read all data from a Type 1 (Topaz) tag.
        
        Returns:
            Optional[bytes]: Tag data or None if read fails
        """
        if not self._is_type1_tag(self._get_sak(), self._get_atqa()):
            logger.error("Not a Type 1 (Topaz) tag")
            return None
            
        try:
            # Type 1 tags have 16 pages of 8 bytes each (128 bytes total)
            # First 16 bytes are reserved for system information
            data = bytearray()
            
            # Read all pages (0x00 to 0x0F)
            for page in range(0x10):
                page_data = self._read_type1_page(page)
                if page_data is None:
                    logger.error(f"Failed to read page {page}")
                    return None
                data.extend(page_data)
                
            return bytes(data)
            
        except Exception as e:
            logger.error(f"Error reading Type 1 tag: {e}", exc_info=True)
            return None
    
    def _read_type1_page(self, page: int) -> Optional[bytes]:
        """Read a single page from a Type 1 tag.
        
        Args:
            page: Page number (0x00-0x0F)
            
        Returns:
            Optional[bytes]: Page data (8 bytes) or None if read fails
        """
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should return 8 bytes of data from the specified page
            return b'\x00' * 8
        except Exception as e:
            logger.error(f"Error reading Type 1 page {page:02X}: {e}")
            return None
    
    def write_type1_tag(self, data: bytes) -> bool:
        """Write data to a Type 1 (Topaz) tag.
        
        Args:
            data: Data to write (up to 112 bytes for user data)
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not self._is_type1_tag(self._get_sak(), self._get_atqa()):
            logger.error("Not a Type 1 (Topaz) tag")
            return False
            
        if not isinstance(data, (bytes, bytearray)):
            logger.error("Data must be bytes or bytearray")
            return False
            
        # Ensure data doesn't exceed available user space (112 bytes)
        if len(data) > 112:
            logger.warning("Data exceeds Type 1 tag capacity, truncating to 112 bytes")
            data = data[:112]
        
        # Pad data to multiple of 8 bytes
        padded_data = data.ljust((len(data) + 7) // 8 * 8, b'\x00')
        
        try:
            # Write to user memory (pages 0x04-0x0F)
            for i in range(0, len(padded_data), 8):
                page = 0x04 + (i // 8)
                if page > 0x0F:  # Shouldn't happen due to padding
                    break
                    
                page_data = padded_data[i:i+8]
                if not self._write_type1_page(page, page_data):
                    logger.error(f"Failed to write page {page:02X}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error writing Type 1 tag: {e}", exc_info=True)
            return False
    
    def _write_type1_page(self, page: int, data: bytes) -> bool:
        """Write a single page to a Type 1 tag.
        
        Args:
            page: Page number (0x00-0x0F)
            data: 8 bytes of data to write
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not isinstance(data, (bytes, bytearray)) or len(data) != 8:
            logger.error("Data must be exactly 8 bytes")
            return False
            
        if page < 0 or page > 0x0F:
            logger.error(f"Invalid page number: {page:02X}")
            return False
            
        try:
            # Implementation depends on the reader's API
            # This is a placeholder - replace with actual implementation
            # Should write 8 bytes to the specified page
            return True
            
        except Exception as e:
            logger.error(f"Error writing Type 1 page {page:02X}: {e}")
            return False
    
    def mifare_authenticate(self, block: int, key_type: str = 'A', key: bytes = None) -> bool:
        """
        Authenticate with a MIFARE Classic tag.
        
        Args:
            block: Block number to authenticate
            key_type: 'A' or 'B' key type
            key: 6-byte authentication key (default: FF FF FF FF FF FF)
            
        Returns:
            bool: True if authentication was successful
        """
        if key is None:
            key = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # Default key
            
        try:
            # Implementation for MIFARE authentication
            # This is a placeholder - actual implementation depends on the reader's API
            logger.info(f"Authenticating block {block} with key type {key_type}")
            self.authenticated = True
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.authenticated = False
            return False
    
    def read_block(self, block: int) -> Optional[bytes]:
        """Read a block from the tag."""
        if not self.authenticated:
            logger.warning("Not authenticated. Please authenticate first.")
            return None
            
        try:
            # Implementation for reading a block
            return b'\x00' * 16  # Return dummy data
        except Exception as e:
            logger.error(f"Failed to read block {block}: {e}")
            return None
    
    def write_block(self, block: int, data: bytes) -> bool:
        """Write data to a block on the tag."""
        if not self.authenticated:
            logger.warning("Not authenticated. Please authenticate first.")
            return False
            
        try:
            # Implementation for writing a block
            return True
        except Exception as e:
            logger.error(f"Failed to write block {block}: {e}")
            return False
    
    def get_tag_info(self) -> Dict[str, Any]:
        """Get detailed information about the current tag."""
        if self.current_tag is None:
            return {
                'status': 'No tag detected',
                'type': 'Unknown',
                'uid': '',
                'memory_size': 0,
                'supports_mifare': False
            }
            
        return {
            'status': 'Ready',
            'type': self.current_tag.get('type', 'Unknown'),
            'uid': self.current_tag.get('uid', ''),
            'memory_size': self._get_tag_size(),
            'supports_mifare': self.current_tag.get('type') in [TagType.MIFARE_CLASSIC_1K, TagType.MIFARE_CLASSIC_4K]
        }
    
    def is_operation_supported(self, operation: str, tag_type: Optional[TagType] = None) -> Tuple[bool, str]:
        """Check if an operation is supported for the specified tag type.
        
        Args:
            operation: Name of the operation to check (e.g., 'read', 'write', 'format')
            tag_type: Optional tag type to check against. If None, uses current_tag['type']
            
        Returns:
            Tuple[bool, str]: (is_supported, error_message)
        """
        if tag_type is None:
            if not self.current_tag:
                return False, "No tag is currently selected. Please place a tag on the reader."
            tag_type = self.current_tag.get('type')
            if not tag_type:
                return False, "Could not determine tag type. Please try again."
        
        # Define supported operations per tag type with detailed error messages
        supported_ops = {
            TagType.TYPE_1_TOPAS: {
                'read': "Read operations are supported for Type 1 (Topaz) tags",
                'write': "Write operations are supported for Type 1 (Topaz) tags",
                'format': "Formatting is not supported for Type 1 (Topaz) tags"
            },
            TagType.TYPE_2_MIFARE_ULTRALIGHT: {
                'read': "Read operations are supported for Type 2 (MIFARE Ultralight/NTAG) tags",
                'write': "Write operations are supported for Type 2 (MIFARE Ultralight/NTAG) tags",
                'format': "Formatting is supported for Type 2 (MIFARE Ultralight/NTAG) tags"
            },
            TagType.MIFARE_CLASSIC_1K: {
                'read': "Read operations are supported for MIFARE Classic 1K tags",
                'write': "Write operations are supported for MIFARE Classic 1K tags",
                'format': "Formatting is supported for MIFARE Classic 1K tags"
            },
            TagType.MIFARE_CLASSIC_4K: {
                'read': "Read operations are supported for MIFARE Classic 4K tags",
                'write': "Write operations are supported for MIFARE Classic 4K tags",
                'format': "Formatting is supported for MIFARE Classic 4K tags"
            },
            TagType.TYPE_3_FELICA: {
                'read': "Read operations are supported for Type 3 (FeliCa) tags",
                'write': "Write operations are supported for Type 3 (FeliCa) tags",
                'format': "Formatting is not supported for Type 3 (FeliCa) tags"
            },
            TagType.TYPE_4_DESFIRE: {
                'read': "Read operations are supported for Type 4 (DESFire) tags",
                'write': "Write operations are supported for Type 4 (DESFire) tags",
                'format': "Formatting is supported for Type 4 (DESFire) tags",
                'create_app': "Application creation is supported for DESFire tags",
                'delete_app': "Application deletion is supported for DESFire tags"
            },
            TagType.TYPE_5_VICINITY: {
                'read': "Read operations are supported for Type 5 (ISO 15693) tags",
                'write': "Write operations are supported for Type 5 (ISO 15693) tags",
                'lock_block': "Block locking is supported for Type 5 (ISO 15693) tags"
            },
            # Aliases
            TagType.JEWEL: {
                'read': "Read operations are supported for Type 1 (Topaz/Jewel) tags",
                'write': "Write operations are supported for Type 1 (Topaz/Jewel) tags"
            },
            TagType.TOPAZ: {
                'read': "Read operations are supported for Type 1 (Topaz) tags",
                'write': "Write operations are supported for Type 1 (Topaz) tags"
            },
            TagType.DESFIRE: {
                'read': "Read operations are supported for Type 4 (DESFire) tags",
                'write': "Write operations are supported for Type 4 (DESFire) tags",
                'format': "Formatting is supported for Type 4 (DESFire) tags"
            },
            TagType.FELICA: {
                'read': "Read operations are supported for Type 3 (FeliCa) tags",
                'write': "Write operations are supported for Type 3 (FeliCa) tags"
            },
            TagType.MIFARE_ULTRALIGHT: {
                'read': "Read operations are supported for MIFARE Ultralight/NTAG tags",
                'write': "Write operations are supported for MIFARE Ultralight/NTAG tags"
            }
        }
        
        # Check if the tag type is supported
        if tag_type not in supported_ops:
            supported_types = ", ".join([t.name for t in supported_ops.keys()])
            return False, f"Unsupported tag type: {tag_type.name if hasattr(tag_type, 'name') else tag_type}.\nSupported types: {supported_types}"
        
        # Check if the operation is supported for this tag type
        if operation not in supported_ops[tag_type]:
            supported = ", ".join(supported_ops[tag_type].keys())
            return False, (
                f"Operation '{operation}' is not supported for {tag_type.name if hasattr(tag_type, 'name') else tag_type} tags.\n"
                f"Supported operations: {supported}"
            )
            
        return True, supported_ops[tag_type][operation]
    
    def _get_tag_size(self) -> int:
        """Get the memory size of the current tag in bytes.
        
        Returns:
            int: Memory size in bytes, or 0 if size is variable/unknown
        """
        if self.current_tag is None:
            return 0
            
        tag_type = self.current_tag.get('type')
        
        # NFC Forum Tag Types
        sizes = {
            # Type 1 (Topaz, Jewel) - 96 bytes user memory, 16 bytes per page
            TagType.TYPE_1_TOPAS: 96,
            TagType.JEWEL: 96,     # Alias
            TagType.TOPAZ: 96,     # Alias
            
            # Type 2 (MIFARE Ultralight, NTAG) - variable sizes
            TagType.TYPE_2_MIFARE_ULTRALIGHT: 64,  # MIFARE Ultralight
            TagType.MIFARE_ULTRALIGHT: 64,         # Alias
            TagType.NTAG_213: 180,  # 144 bytes user memory
            TagType.NTAG_215: 540,  # 504 bytes user memory
            TagType.NTAG_216: 888,  # 888 bytes user memory
            
            # Type 3 (FeliCa) - variable size
            TagType.TYPE_3_FELICA: 0,  # Variable size
            TagType.FELICA: 0,         # Alias
            
            # Type 4 (DESFire, ISO 14443-4) - variable size
            TagType.TYPE_4_DESFIRE: 0,  # Variable size, typically 2KB-8KB
            TagType.DESFIRE: 0,         # Alias
            
            # Type 5 (Vicinity, ISO 15693) - variable size
            TagType.TYPE_5_VICINITY: 0,  # Variable size
            
            # MIFARE Classic (not part of NFC Forum standard but widely used)
            TagType.MIFARE_CLASSIC_1K: 1024,  # 16 sectors, 4 blocks per sector, 16 bytes per block
            TagType.MIFARE_CLASSIC_4K: 4096,  # 40 sectors, 16 blocks per sector, 16 bytes per block
        }
        
        return sizes.get(tag_type, 0)

# Example usage
if __name__ == "__main__":
    nfc = NfcOperations()
    if nfc.connect():
        print("Connected to NFC reader")
        tag = nfc.detect_tag()
        if tag:
            print(f"Detected tag: {tag}")
            if tag['type'] in [TagType.MIFARE_CLASSIC_1K, TagType.MIFARE_CLASSIC_4K]:
                if nfc.mifare_authenticate(4):  # Authenticate sector 1
                    data = nfc.read_block(4)
                    print(f"Block 4 data: {data}")
    nfc.disconnect()
