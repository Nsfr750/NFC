.. _getting-started:

Getting Started
==============

This guide will help you quickly get started with the NFC Reader/Writer application.

Installation
------------

Prerequisites
~~~~~~~~~~~~
- Python 3.8 or higher
- pip (Python package manager)
- NFC reader hardware
- Required system libraries (see :ref:`prerequisites`)

Windows Installation
~~~~~~~~~~~~~~~~~~~

1. Download the latest release from the `GitHub releases page <https://github.com/Nsfr750/NFC/releases>`_
2. Extract the ZIP file to your preferred location
3. Run ``nfc-reader-writer.exe`` from the extracted folder

Linux Installation
~~~~~~~~~~~~~~~~~

1. Download the latest release from the `GitHub releases page <https://github.com/Nsfr750/NFC/releases>`_
2. Extract the archive:
   .. code-block:: bash

      tar -xzf nfc-reader-writer-linux-x86_64.tar.gz

3. Run the application:
   .. code-block:: bash

      cd nfc-reader-writer-linux-x86_64
      ./nfc-reader-writer

First Run
---------

1. Connect your NFC reader to your computer
2. Launch the NFC Reader/Writer application
3. The application will automatically detect your NFC reader
4. Place an NFC tag near the reader to start reading

Basic Usage
-----------

Reading a Tag
~~~~~~~~~~~~
1. Click the "Read Tag" button or press ``Ctrl+R``
2. Place your NFC tag near the reader
3. The tag data will be displayed in the main window

Writing to a Tag
~~~~~~~~~~~~~~~
1. Click the "Write" button or press ``Ctrl+W``
2. Enter the data you want to write
3. Select the write options
4. Place your NFC tag near the reader
5. Click "Start Writing"

Saving Tag Data
~~~~~~~~~~~~~~
1. Read a tag
2. Click the "Save" button or press ``Ctrl+S``
3. Choose a location and filename
4. Click "Save"

Next Steps
----------
- Learn more about :ref:`advanced-features`
- Check out the :ref:`user-guide` for detailed usage instructions
- Visit the :ref:`troubleshooting` guide if you encounter any issues
