.. _faq:

Frequently Asked Questions
========================

General
-------

What types of NFC tags are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The application supports all major NFC tag types including:

- NTAG (NTAG213, NTAG215, NTAG216)
- MIFARE Classic (1K, 4K)
- MIFARE Ultralight
- FeliCa
- ISO 14443 Type A & B
- ISO 15693

Is there a limit to the number of tags I can store in the database?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
No, there is no hard limit to the number of tags you can store. The database will grow as needed.

Can I use multiple NFC readers at the same time?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes, the application supports multiple readers. You can select the active reader from the settings menu.

Usage
-----

How do I know if my NFC reader is properly connected?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The status bar at the bottom of the application will show the connection status. A green indicator means the reader is connected and ready.

Why can't I write to my NFC tag?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There could be several reasons:

1. The tag might be read-only or locked
2. The tag might be out of memory
3. The tag might not support the write operation you're trying to perform

Check the tag's specifications and ensure it's not write-protected.

Can I use this application to clone NFC cards?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The application can read and write data to compatible tags, but some security features (like those used in credit cards) cannot be cloned due to encryption and other security measures.

Technical
--------

What programming language is this application written in?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The application is written in Python, with a Qt-based GUI.

Is the source code available?
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes, the application is open source and available on `GitHub <https://github.com/Nsfr750/NFC>`_.

How can I contribute to the project?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can contribute by:

1. Reporting bugs or suggesting features on the `issue tracker <https://github.com/Nsfr750/NFC/issues>`_
2. Submitting pull requests with improvements
3. Improving the documentation
4. Translating the application to other languages

Troubleshooting
--------------

My NFC reader is not being detected
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Ensure the reader is properly connected to your computer
2. Check if the drivers are installed correctly
3. Try a different USB port
4. Restart the application

The application crashes when reading a tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Please report this issue on our `GitHub issues page <https://github.com/Nsfr750/NFC/issues>`_ with the following information:

1. The type of tag you were trying to read
2. The error message (if any)
3. The application version
4. Your operating system version

Performance is slow when reading multiple tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Try these optimizations:
1. Close other applications using the NFC reader
2. Reduce the read delay in settings
3. Update to the latest version of the application

For more help, see the :ref:`troubleshooting` guide.
