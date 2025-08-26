"""
Smart Card Operations Module

This module provides functionality for working with contactless smart cards
using ISO 14443-4 and ISO 7816-4 standards.
"""

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Dict, Any, Tuple, Union

# Initialize logger
logger = logging.getLogger(__name__)

class SmartCardError(Exception):
    """Base exception for smart card related errors."""
    pass

class APDUCommand:
    """Class representing an APDU command for smart card communication."""
    
    def __init__(self, cla: int, ins: int, p1: int = 0, p2: int = 0, data: bytes = b"", le: Optional[int] = None):
        """Initialize an APDU command.
        
        Args:
            cla: Class byte
            ins: Instruction byte
            p1: Parameter 1
            p2: Parameter 2
            data: Command data
            le: Expected response length (None for no length specified)
        """
        self.cla = cla
        self.ins = ins
        self.p1 = p1
        self.p2 = p2
        self.data = data
        self.le = le
    
    def to_bytes(self) -> bytes:
        """Convert the APDU command to bytes."""
        apdu = bytes([self.cla, self.ins, self.p1, self.p2])
        
        if not self.data and self.le is None:
            return apdu
            
        if not self.data:
            return apdu + bytes([self.le])
            
        if len(self.data) <= 255 and self.le is None:
            return apdu + bytes([len(self.data)]) + self.data
            
        if len(self.data) <= 255:
            return apdu + bytes([len(self.data)]) + self.data + bytes([self.le])
            
        # Extended length APDU (not fully implemented)
        raise SmartCardError("Extended length APDUs not yet implemented")

class SmartCard:
    """Class for managing communication with a contactless smart card."""
    
    def __init__(self, tag):
        """Initialize with a connected NFC tag."""
        self.tag = tag
        self.logger = logging.getLogger(f'{__name__}.SmartCard')
        self._select_application(None)  # Select MF by default
    
    def _select_application(self, aid: Optional[bytes]) -> bool:
        """Select an application by AID.
        
        Args:
            aid: Application ID to select (None for MF)
            
        Returns:
            bool: True if selection was successful
        """
        try:
            if aid is None:
                # Select MF
                apdu = APDUCommand(0x00, 0xA4, 0x00, 0x0C).to_bytes()
            else:
                # Select by AID
                apdu = APDUCommand(0x00, 0xA4, 0x04, 0x0C, aid).to_bytes()
                
            response, sw1, sw2 = self.transmit(apdu)
            return sw1 == 0x90 and sw2 == 0x00
            
        except Exception as e:
            self.logger.error(f"Error selecting application: {str(e)}")
            return False
    
    def transmit(self, apdu: bytes) -> Tuple[bytes, int, int]:
        """Transmit an APDU command to the card.
        
        Args:
            apdu: APDU command bytes
            
        Returns:
            tuple: (response_data, sw1, sw2)
        """
        try:
            if not hasattr(self.tag, 'transceive'):
                raise SmartCardError("Tag does not support direct APDU communication")
                
            # Send APDU and get response
            response = self.tag.transceive(apdu)
            
            # Extract status words and response data
            if len(response) >= 2:
                sw1 = response[-2]
                sw2 = response[-1]
                data = response[:-2] if len(response) > 2 else b''
                return data, sw1, sw2
                
            raise SmartCardError("Invalid response from card")
            
        except Exception as e:
            self.logger.error(f"APDU transmission error: {str(e)}")
            raise SmartCardError(f"APDU transmission failed: {str(e)}")
    
    def read_binary(self, offset: int, length: int) -> bytes:
        """Read binary data from the card.
        
        Args:
            offset: Offset to read from
            length: Number of bytes to read
            
        Returns:
            bytes: Data read from the card
        """
        try:
            # READ BINARY APDU
            p1 = (offset >> 8) & 0xFF
            p2 = offset & 0xFF
            apdu = APDUCommand(0x00, 0xB0, p1, p2, le=length).to_bytes()
            
            data, sw1, sw2 = self.transmit(apdu)
            
            if sw1 == 0x90 and sw2 == 0x00:
                return data
                
            raise SmartCardError(f"Read failed with status {sw1:02X}{sw2:02X}")
            
        except Exception as e:
            self.logger.error(f"Error reading binary data: {str(e)}")
            raise
    
    def write_binary(self, offset: int, data: bytes) -> bool:
        """Write binary data to the card.
        
        Args:
            offset: Offset to write to
            data: Data to write
            
        Returns:
            bool: True if write was successful
        """
        try:
            # WRITE BINARY APDU
            p1 = (offset >> 8) & 0xFF
            p2 = offset & 0xFF
            apdu = APDUCommand(0x00, 0xD0, p1, p2, data).to_bytes()
            
            _, sw1, sw2 = self.transmit(apdu)
            
            if sw1 == 0x90 and sw2 == 0x00:
                return True
                
            raise SmartCardError(f"Write failed with status {sw1:02X}{sw2:02X}")
            
        except Exception as e:
            self.logger.error(f"Error writing binary data: {str(e)}")
            raise
    
    def get_card_info(self) -> Dict[str, Any]:
        """Get information about the smart card.
        
        Returns:
            dict: Card information including ATR, AID, and other details
        """
        info = {
            'type': 'ISO 14443-4 Smart Card',
            'atr': getattr(self.tag, 'atr', b'').hex() if hasattr(self.tag, 'atr') else 'N/A',
            'uid': getattr(self.tag, 'identifier', b'').hex() if hasattr(self.tag, 'identifier') else 'N/A',
            'applications': []
        }
        
        # Try to get ATR if available
        if hasattr(self.tag, 'atr') and self.tag.atr:
            atr = self.tag.atr
            info['atr'] = atr.hex()
            
            # Simple ATR parsing (simplified)
            if len(atr) >= 2:
                info['protocol'] = f"ISO 14443-{4 if atr[0] & 0x10 else 3}"
        
        return info
