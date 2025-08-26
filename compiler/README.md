# Build Instructions for NFC Reader/Writer

## Prerequisites

### Common Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- GCC/make (for building some dependencies on Linux)

### Linux Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv build-essential libusb-1.0-0-dev libpcsclite-dev pcscd

# Fedora
sudo dnf install -y python3-pip python3-virtualenv gcc make libusb1-devel pcsc-lite-devel pcsc-lite-ccid
```

### Windows Dependencies

- [Python 3.8+](https://www.python.org/downloads/windows/)
- [7-Zip](https://www.7-zip.org/) (for creating the final package)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (for building some dependencies)

## Building from Source

### Linux Build

1. Clone the repository and navigate to the compiler directory:

   ```bash
   git clone https://github.com/Nsfr750/NFC.git
   cd NFC/compiler
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install build dependencies:

   ```bash
   pip install -r ../requirements.txt
   ```

4. Make the build script executable and run it:

   ```bash
   chmod +x pyinstaller_build_linux.py
   python3 pyinstaller_build_linux.py
   ```

5. Create a distributable package:

   ```bash
   cd ..
   tar -czvf nfc-reader-writer-linux-x86_64.tar.gz -C dist/linux .
   ```

### Windows Build

1. Clone the repository and navigate to the compiler directory:

   ```cmd
   git clone https://github.com/Nsfr750/NFC.git
   cd NFC\compiler
   ```

2. Create and activate a virtual environment:

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install build dependencies:

   ```cmd
   pip install -r ..\requirements.txt
   ```

4. Run the build script:

   ```cmd
   python pyinstaller_build_win.py
   ```

5. Create a distributable package using 7-Zip:

   ```cmd
   cd ..
   7z a -t7z nfc-reader-writer-windows-x86_64.7z dist\windows\*
   ```

## Troubleshooting

### Common Issues

#### Linux

- **PC/SC not found**: Ensure `pcscd` service is running:

  ```bash
  sudo systemctl start pcscd
  sudo systemctl enable pcscd
  ```

- **USB permissions**: Add your user to the `plugdev` group:

  ```bash
  sudo usermod -aG plugdev $USER
  ```

#### Windows

- **Build tools not found**: Install Visual Studio Build Tools with "Desktop development with C++" workload
- **7-Zip not found**: Add 7-Zip to your system PATH or use the full path to 7z.exe

## Distribution

The final packages will be created in the project root directory:

- Linux: `nfc-reader-writer-linux-x86_64.tar.gz`
- Windows: `nfc-reader-writer-windows-x86_64.7z`

These packages contain all necessary files to run the application. Users can extract them and run the executable directly.
