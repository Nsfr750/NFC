.. _troubleshooting:

Troubleshooting Guide
====================

This guide helps you resolve common issues you might encounter while using the NFC Reader/Writer application.

Connection Issues
----------------

NFC Reader Not Detected
~~~~~~~~~~~~~~~~~~~~~~
**Symptoms:**
- The application shows "No reader connected"
- The reader is not listed in the devices menu

**Solutions:**
1. **Check physical connections:**
   - Ensure the reader is properly connected to your computer
   - Try a different USB port
   - If using a USB hub, connect directly to the computer

2. **Verify drivers:**
   - Windows: Check Device Manager for any yellow exclamation marks
   - Linux: Ensure you have the necessary permissions (add your user to the `plugdev` group)
   - Try reinstalling the reader's drivers

3. **Restart services:**
   - Restart the PC/SC service:
     ```bash
     sudo systemctl restart pcscd  # Linux
     net stop "Smart Card" && net start "Smart Card"  # Windows
     ```

4. **Test with other software:**
   - Try using the reader with other NFC software to isolate the issue

Tag Reading Issues
-----------------

Tag Not Detected
~~~~~~~~~~~~~~~
**Symptoms:**
- The reader is detected but no tags are recognized
- "No tag found" message appears

**Solutions:**
1. **Check tag position:**
   - Ensure the tag is properly aligned with the reader's antenna
   - Move the tag around to find the "sweet spot"

2. **Try a different tag:**
   - Test with multiple tags to rule out a defective tag

3. **Check tag type:**
   - Verify that the tag type is supported by your reader
   - Some readers have limited compatibility with certain tag types

4. **Adjust settings:**
   - Increase the read timeout in the application settings
   - Try different read modes if available

Write Failures
-------------

Cannot Write to Tag
~~~~~~~~~~~~~~~~~~
**Symptoms:**
- Write operation fails with an error
- Data is not saved to the tag

**Solutions:**
1. **Check write protection:**
   - Some tags have a write-protection feature that can be locked
   - Check if the tag is read-only

2. **Verify tag capacity:**
   - Ensure the data you're trying to write fits within the tag's capacity
   - Some tags have specific memory layouts and reserved areas

3. **Format issues:**
   - Try formatting the tag before writing
   - Some tags require specific formatting for certain data types

4. **Tag health:**
   - The tag might be damaged or worn out
   - Try with a different tag

Application Issues
----------------

Application Crashes
~~~~~~~~~~~~~~~~~~
**Symptoms:**
- The application closes unexpectedly
- Error messages appear before crashing

**Solutions:**
1. **Check logs:**
   - Look for crash logs in the application's log directory
   - On Windows: `%APPDATA%\NFC Reader Writer\logs`
   - On Linux: `~/.local/share/NFC Reader Writer/logs`

2. **Update the application:**
   - Make sure you're running the latest version
   - Check for updates in the Help menu

3. **Reset settings:**
   - Try resetting the application to default settings
   - Delete the configuration file (backup first if needed)

4. **Check system requirements:**
   - Ensure your system meets the minimum requirements
   - Update your operating system and drivers

Performance Issues
----------------

Slow Tag Reading/Writing
~~~~~~~~~~~~~~~~~~~~~~~
**Symptoms:**
- Operations take longer than expected
- The application becomes unresponsive during operations

**Optimizations:**
1. **Close other applications:**
   - Other applications might be using system resources
   - Close unnecessary programs

2. **Adjust settings:**
   - Reduce the read/write retry count
   - Increase timeouts if you're experiencing timeouts

3. **Check for interference:**
   - Move away from sources of electromagnetic interference
   - Try a different location

4. **Update firmware:**
   - Check if there's a firmware update for your NFC reader
   - Update the reader's firmware if available

Common Error Messages
--------------------

"Reader Not Found"
~~~~~~~~~~~~~~~~~
- Verify the reader is properly connected
- Check if the reader is supported by the application
- Try reinstalling the reader drivers

"Tag Not Supported"
~~~~~~~~~~~~~~~~~~
- Check if the tag type is supported
- Try a different tag
- Some tags might require specific configurations

"Insufficient Memory"
~~~~~~~~~~~~~~~~~~~~
- The tag doesn't have enough space for the operation
- Reduce the amount of data you're trying to write
- Use a tag with larger capacity

Getting Help
-----------

If you're still experiencing issues:

1. **Check the FAQ** section for more solutions
2. **Search the documentation** for specific topics
3. **Report the issue** on our `GitHub Issues <https://github.com/Nsfr750/NFC/issues>`_ page
   - Include the error message
   - Describe what you were doing when the issue occurred
   - Attach relevant log files

For additional support, you can also visit our `Discord server <https://discord.gg/ryqNeuRYjD>`_.
