# Supported NFC Operations

This document outlines the supported operations for each NFC tag type in the NFC Reader/Writer application.

## Type 1 (Topaz/Jewel)

### Supported Operations

- **Read**: Read data from the tag
- **Write**: Write data to the tag (limited to user memory)

### Limitations

- No support for formatting
- Limited memory size (typically 96 bytes user memory)

## Type 2 (MIFARE Ultralight/NTAG)

### Supported Operations

- **Read**: Read data from the tag
- **Write**: Write data to the tag
- **Format**: Reset the tag to factory state

### NTAG Variants

- NTAG213: 144 bytes user memory
- NTAG215: 504 bytes user memory
- NTAG216: 888 bytes user memory

## Type 3 (FeliCa)

### Supported Operations

- **Read**: Read data from the tag
- **Write**: Write data to the tag

### Features

- Support for multiple services
- Block-level access control
- Fast data transfer

## Type 4 (DESFire)

### Supported Operations

- **Read**: Read data from files
- **Write**: Write data to files
- **Format**: Format the entire tag
- **Application Management**:
  - Create applications
  - Delete applications
  - Select applications

### Security Features

- AES, 3K3DES, and DES authentication
- File-level access rights
- Support for multiple applications

## Type 5 (ISO 15693/Vicinity)

### Supported Operations

- **Read**: Read blocks from the tag
- **Write**: Write blocks to the tag
- **Lock Block**: Permanently lock blocks

### Features

- Long read range (up to 1.5m)
- Block-based memory access
- Support for extended commands

## Common Operations

### Authentication

- MIFARE Classic: Key A/B authentication
- DESFire: AES/3K3DES/DES authentication

### Memory Operations

- Read single/multiple blocks
- Write single/multiple blocks
- Lock blocks (where supported)

### Utility

- Get tag information
- Check operation support
- Format tags (where supported)

## Unsupported Operations

- Low-level RF operations
- Proprietary commands not part of the NFC Forum specifications
- Operations requiring special hardware features not present in the reader

## Error Handling

The application provides detailed error messages for unsupported operations, including:

- Unsupported tag type
- Unsupported operation for the current tag
- Authentication failures
- Memory access violations

## Notes

- Some operations may require authentication first
- Formatting a tag will erase all data
- Write operations may be limited by the tag's memory protection settings
