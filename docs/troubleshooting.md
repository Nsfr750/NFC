# Troubleshooting Guide

This guide helps you resolve common issues you might encounter while using the NFC Tool.

## Common Issues

### NFC Reader Not Detected
- **Symptom**: The application doesn't detect any NFC reader
- **Solutions**:
  1. Ensure the reader is properly connected to your computer
  2. Install the latest drivers for your NFC reader
  3. Restart the application
  4. Try a different USB port
  5. Check if the reader is recognized by your operating system

### Cannot Read Tags
- **Symptom**: The reader is detected but can't read tags
- **Solutions**:
  1. Make sure the tag is placed correctly on the reader
  2. Try a different NFC tag
  3. Check if the tag is compatible with your reader
  4. Ensure the tag is not damaged
  5. Try increasing the read timeout in settings

### Authentication Issues
- **Symptom**: Unable to log in or unexpected logouts
- **Solutions**:
  1. Check your username and password
  2. Use the password recovery option if needed
  3. Clear the application cache
  4. Check if your account is locked (too many failed attempts)

## Error Messages

### "Reader Not Found"
- **Cause**: No compatible NFC reader is connected
- **Solution**: Connect a supported NFC reader and try again

### "Tag Not Supported"
- **Cause**: The NFC tag type is not supported
- **Solution**: Use a different type of NFC tag (e.g., NTAG213, NTAG215, NTAG216)

### "Write Failed"
- **Cause**: Unable to write to the tag
- **Solutions**:
  1. Make sure the tag is not read-only
  2. Check if the tag has enough memory
  3. Try a different tag

## Log Files

Application logs can be found in the following location:
- Windows: `%APPDATA%\NFC Tool\logs\`
- Linux: `~/.config/nfc-tool/logs/`
- macOS: `~/Library/Application Support/NFC Tool/logs/`

## Getting Help

If you can't resolve your issue:
1. Check the [FAQ](faq.md)
2. Search the [GitHub Issues](https://github.com/Nsfr750/NFC/issues)
3. Create a new issue with:
   - Steps to reproduce the problem
   - Screenshots if applicable
   - Log files (remove any sensitive information)

## Known Issues

- Some NFC readers may require additional drivers on Windows
- Performance may vary depending on the tag type and reader model
- Certain operations might not be supported on all platforms
