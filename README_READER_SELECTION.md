# Reader Selection Functionality

This document describes the new reader selection functionality added to the NFC Reader/Writer application.

## Overview

The reader selection feature allows users to choose from different types of NFC readers and automatically configures the application to work with the selected reader type. This includes:

- **Dropdown Menu**: A user-friendly dropdown in the Device Panel to select reader types
- **Auto-Detection**: Automatic detection of connected readers based on VID/PID
- **Smart Filtering**: Port filtering based on selected reader type
- **Dynamic Configuration**: Automatic backend and connection parameter configuration
- **Enhanced NFC Thread**: Updated NFC thread to handle different reader types

## Supported Reader Types

### 1. Auto-Detect
- **Description**: Automatically detects the reader type
- **Backend**: Tries all available backends (USB → PC/SC → UART)
- **VID/PID**: None specific, tries all available devices
- **Use Case**: When you're unsure about your reader type or want automatic detection

### 2. ACR122U
- **Description**: ACS ACR122U NFC Reader
- **Backend**: PC/SC (preferred)
- **VID/PID**: 0x072F:0x2200
- **Use Case**: ACS ACR122U and compatible readers

### 3. PN532
- **Description**: NXP PN532 NFC Reader
- **Backend**: USB
- **VID/PID**: 0x2341:0x0043, 0x0403:0x6001
- **Use Case**: PN532-based readers and breakout boards

### 4. NS106
- **Description**: Kadongli NS106 Dual Frequency Reader
- **Backend**: USB
- **VID/PID**: 0x072F:0x2200
- **Use Case**: Kadongli NS106 readers (125KHz and 13.56MHz)

### 5. RC522
- **Description**: MFRC522 RFID Reader
- **Backend**: UART
- **VID/PID**: 0x2341:0x0043
- **Use Case**: Arduino-based MFRC522 readers

### 6. PC/SC
- **Description**: Generic PC/SC Reader
- **Backend**: PC/SC
- **VID/PID**: None specific
- **Use Case**: Any PC/SC compliant reader

## How It Works

### 1. Reader Selection
- Users select a reader type from the dropdown menu in the Device Panel
- The selection immediately updates the available ports list, filtering for compatible devices
- Reader-specific information is displayed (description, backend, expected VID/PID)

### 2. Port Filtering
- When a specific reader type is selected, only ports matching the reader's VID/PID are shown
- For "Auto-Detect" mode, all available ports are shown
- This helps users quickly identify the correct port for their reader

### 3. Dynamic Configuration
- The NFC thread is automatically configured based on the selected reader type
- Connection parameters are optimized for each reader type
- Backends are tried in the optimal order for each reader

### 4. Connection Process
1. User selects reader type from dropdown
2. Available ports are filtered based on selection
3. User selects a port and clicks "Connect"
4. NFC thread is restarted with new configuration
5. Connection is attempted using reader-specific parameters

## Implementation Details

### Device Panel Changes
- Added `READER_TYPES` dictionary with reader configurations
- Added reader type dropdown with descriptions
- Added port filtering based on VID/PID
- Added reader information display
- Added signals for reader type changes

### NFC Thread Changes
- Added `set_reader_type()` and `set_selected_port()` methods
- Added `get_connection_params()` for reader-specific connection strategies
- Enhanced `run()` method to use reader-specific parameters
- Added `get_reader_info()` for detailed reader information

### Main Application Changes
- Added signal handlers for reader type changes
- Added NFC thread restart logic
- Enhanced status updates with reader information

## Testing

### Test Script
A comprehensive test script is provided at `script/test_reader_selection.py`:

```bash
python script/test_reader_selection.py
```

The test script includes:
- Reader selection dropdown
- Connection status display
- Test buttons for various functions
- Real-time logging
- Reader information display

### Test Cases
1. **Reader Type Selection**: Test changing reader types
2. **Port Filtering**: Verify ports are filtered correctly
3. **Connection Test**: Test connection with different readers
4. **Auto-Detection**: Test automatic reader detection
5. **Reader Information**: Test reader info retrieval

## Troubleshooting

### Common Issues

#### 1. No Compatible Ports Found
**Cause**: No devices matching the selected reader type's VID/PID
**Solution**: 
- Try "Auto-Detect" mode
- Check if reader is properly connected
- Verify reader drivers are installed

#### 2. Connection Failed
**Cause**: Backend or connection parameters not suitable for reader
**Solution**:
- Try "Auto-Detect" mode
- Check reader compatibility
- Verify drivers and dependencies

#### 3. Reader Not Detected
**Cause**: Reader VID/PID not in database
**Solution**:
- Use "Auto-Detect" mode
- Add reader VID/PID to `READER_TYPES` dictionary
- Check device manager for correct VID/PID

### Adding New Reader Types

To add support for a new reader type:

1. **Add to READER_TYPES dictionary** in `device_panel.py`:
```python
'NEW_READER': {
    'description': 'New Reader Description',
    'vid_pid': [(0xVID, 0xPID)],  # Add actual VID/PID
    'backend': 'usb'  # or 'pcsc', 'uart'
}
```

2. **Update NFC thread** if special connection logic is needed
3. **Test** with the test script

## Dependencies

The reader selection functionality requires:
- `pyserial` - For serial port detection and communication
- `nfcpy` - For NFC operations
- `PySide6` - For GUI components

Install dependencies:
```bash
pip install pyserial nfcpy PySide6
```

## Future Enhancements

Planned improvements:
1. **Custom Reader Configuration**: Allow users to add custom reader types
2. **Reader Profiles**: Save and load reader configurations
3. **Advanced Settings**: Fine-tune connection parameters
4. **Reader Diagnostics**: Enhanced diagnostic tools for specific readers
5. **Firmware Updates**: Support for reader firmware updates

## Contributing

To contribute to the reader selection functionality:

1. Test with different reader types
2. Report issues with specific readers
3. Add new reader types to the database
4. Improve connection strategies
5. Enhance error messages and diagnostics

## License

This functionality is part of the NFC Reader/Writer application and is licensed under GPLv3.
