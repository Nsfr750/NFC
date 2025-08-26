.. _user-guide:

User Guide
=========

This guide provides detailed information about using the NFC Reader/Writer application.

Interface Overview
-----------------

.. image:: ../images/interface_overview.png
   :alt: NFC Reader/Writer Interface
   :align: center

1. **Menu Bar**: Access all application functions
2. **Toolbar**: Quick access to common functions
3. **Tag Information Panel**: Displays tag details
4. **Data View**: Shows tag data in various formats
5. **Status Bar**: Shows connection status and messages

Reading Tags
------------

Manual Reading
~~~~~~~~~~~~~
1. Click the "Read" button in the toolbar or press ``Ctrl+R``
2. The application will read the tag and display its data

Auto-Reading
~~~~~~~~~~~
1. Enable "Auto-Read" mode from the Settings menu
2. The application will automatically read tags when they are detected

Writing to Tags
---------------

Writing Text
~~~~~~~~~~~
1. Select the "Write" tab
2. Choose "Text" as the content type
3. Enter your text in the editor
4. Click "Write" and follow the on-screen instructions

Writing URLs
~~~~~~~~~~~
1. Select the "Write" tab
2. Choose "URL" as the content type
3. Enter the URL
4. Click "Write" and follow the on-screen instructions

Writing Contact Information
~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Select the "Write" tab
2. Choose "vCard" as the content type
3. Fill in the contact details
4. Click "Write" and follow the on-screen instructions

Managing Tag Database
---------------------

Saving Tags
~~~~~~~~~~
1. Read a tag
2. Click "Save to Database"
3. Enter a name and optional description
4. Click "Save"

Searching Tags
~~~~~~~~~~~~~
1. Open the Database view
2. Use the search bar to find specific tags
3. Click on a tag to view its details

Advanced Features
----------------

Tag Emulation
~~~~~~~~~~~~
1. Enable "Tag Emulation" from the Tools menu
2. Configure the emulation settings
3. The application will act as an NFC tag

Batch Processing
~~~~~~~~~~~~~~~
1. Select "Batch Mode" from the Tools menu
2. Configure the read/write operations
3. Process multiple tags in sequence

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~
- **Tag not detected**: Ensure the tag is properly positioned on the reader
- **Write failed**: Check if the tag is write-protected
- **Connection lost**: Verify the reader is properly connected

For more help, see the :ref:`troubleshooting` guide.

Keyboard Shortcuts
-----------------

+----------------+--------------------------+
| Shortcut       | Action                  |
+================+==========================+
| ``Ctrl+N``     | New Project             |
+----------------+--------------------------+
| ``Ctrl+O``     | Open Project            |
+----------------+--------------------------+
| ``Ctrl+S``     | Save Tag Data           |
+----------------+--------------------------+
| ``Ctrl+R``     | Read Tag                |
+----------------+--------------------------+
| ``Ctrl+W``     | Write to Tag            |
+----------------+--------------------------+
| ``F1``         | Help                    |
+----------------+--------------------------+
