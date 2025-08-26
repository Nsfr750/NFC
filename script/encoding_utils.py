"""
Character encoding utilities for NFC Reader/Writer.

This module provides utilities for handling different character encodings
when reading from and writing to NFC tags.
"""
import codecs
from typing import Optional, Tuple, Dict, List

# Common encodings supported by NFC tags
SUPPORTED_ENCODINGS = {
    'utf-8': 'UTF-8',
    'utf-16': 'UTF-16 (Big Endian)',
    'utf-16le': 'UTF-16 (Little Endian)',
    'utf-16be': 'UTF-16 (Big Endian)',
    'latin-1': 'ISO-8859-1 (Latin-1)',
    'ascii': 'ASCII',
    'cp1252': 'Windows-1252',
    'shift_jis': 'Shift-JIS',
    'euc-jp': 'EUC-JP',
    'gbk': 'GBK (Simplified Chinese)',
    'big5': 'Big5 (Traditional Chinese)',
    'euc-kr': 'EUC-KR (Korean)',
    'koi8-r': 'KOI8-R (Cyrillic)',
    'iso-8859-2': 'ISO-8859-2 (Latin-2)',
    'iso-8859-5': 'ISO-8859-5 (Cyrillic)',
    'iso-8859-7': 'ISO-8859-7 (Greek)',
    'iso-8859-8': 'ISO-8859-8 (Hebrew)',
    'iso-8859-9': 'ISO-8859-9 (Turkish)',
    'iso-8859-15': 'ISO-8859-15 (Latin-9)'
}

def detect_encoding(data: bytes, default: str = 'utf-8') -> str:
    """
    Attempt to detect the encoding of the given bytes.
    
    Args:
        data: The bytes to detect encoding for
        default: Default encoding to return if detection fails
        
    Returns:
        Detected or default encoding name
    """
    # Try UTF-8 first (most common for NFC)
    try:
        data.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        pass
    
    # Try UTF-16 with BOM
    if len(data) >= 2:
        if data.startswith(codecs.BOM_UTF16_LE):
            return 'utf-16-le'
        elif data.startswith(codecs.BOM_UTF16_BE):
            return 'utf-16-be'
    
    # Try other common encodings
    for encoding in ['latin-1', 'cp1252', 'ascii']:
        try:
            data.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    
    return default

def decode_data(data: bytes, encoding: Optional[str] = None) -> Tuple[str, str]:
    """
    Decode bytes to text using the specified or detected encoding.
    
    Args:
        data: The bytes to decode
        encoding: Optional encoding to use (None for auto-detect)
        
    Returns:
        Tuple of (decoded_text, used_encoding)
    """
    if not data:
        return "", ""
    
    if not encoding or encoding.lower() == 'auto':
        encoding = detect_encoding(data)
    
    try:
        return data.decode(encoding, errors='replace'), encoding
    except Exception:
        # Fallback to latin-1 which can decode any byte sequence
        return data.decode('latin-1', errors='replace'), 'latin-1'

def encode_data(text: str, encoding: str = 'utf-8') -> bytes:
    """
    Encode text to bytes using the specified encoding.
    
    Args:
        text: The text to encode
        encoding: Encoding to use (default: utf-8)
        
    Returns:
        Encoded bytes
    """
    if not text:
        return b''
    
    try:
        return text.encode(encoding, errors='replace')
    except Exception:
        # Fallback to utf-8 with replacement
        return text.encode('utf-8', errors='replace')

def get_encoding_name(encoding: str) -> str:
    """
    Get a human-readable name for an encoding.
    
    Args:
        encoding: Encoding identifier
        
    Returns:
        Human-readable encoding name
    """
    return SUPPORTED_ENCODINGS.get(encoding.lower(), encoding.upper())

def convert_encoding(text: str, from_encoding: str, to_encoding: str) -> str:
    """
    Convert text from one encoding to another.
    
    Args:
        text: The text to convert
        from_encoding: Source encoding
        to_encoding: Target encoding
        
    Returns:
        Converted text in the target encoding
        
    Raises:
        UnicodeError: If conversion fails
    """
    try:
        # First decode from source encoding to unicode
        decoded = text if isinstance(text, str) else text.decode(from_encoding)
        # Then encode to target encoding and back to unicode to ensure it's valid
        return decoded.encode(to_encoding).decode(to_encoding)
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        raise UnicodeError(f"Failed to convert from {from_encoding} to {to_encoding}: {str(e)}")

def get_supported_encodings() -> List[Dict[str, str]]:
    """
    Get a list of supported encodings with their display names.
    
    Returns:
        List of dicts with 'id' and 'name' keys
    """
    return [{'id': k, 'name': v} for k, v in SUPPORTED_ENCODINGS.items()]
