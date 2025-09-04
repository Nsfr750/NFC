# Prerequisites

Before you can run the NFC Reader/Writer application, you'll need to ensure your system meets the following requirements:

## System Requirements

### Hardware

- NFC Reader/Writer device (e.g., ACR122U, ACR1252U, or compatible)
- Supported operating system:
  - Windows 10/11 (64-bit)
  - Linux (with PC/SC Lite and CCID support)
  - macOS (with CCID support)

### Software Dependencies

#### Windows

1. Install Python 3.9 or later from [python.org](https://www.python.org/downloads/)
2. Install the latest version of [libusb](https://libusb.info/)
3. Install [PC/SC Drivers](https://pcsclite.apdu.fr/) for your NFC reader
4. Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

#### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    libusb-1.0-0-dev \
    libpcsclite-dev \
    pcscd \
    pcsc-tools \
    libccid \
    swig \
    build-essential
```

#### macOS (using Homebrew)

```bash
brew install python@3.9
brew install libusb
brew install pcsc-lite
brew services start pcscd
```

## Python Environment Setup

1. Create and activate a virtual environment:

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## NFC Reader Configuration

### Windows Configuration

1. Connect your NFC reader
2. Install the appropriate drivers if not automatically detected
3. Verify the device appears in Device Manager under "Smart Card Readers"

### Linux

1. Connect your NFC reader
2. Verify the device is detected:

   ```bash
   lsusb | grep -i nfc
   pcsc_scan
   ```

3. Check the PC/SC daemon is running:

   ```bash
   systemctl status pcscd
   ```

## Verifying Installation

After setup, you can verify your NFC reader is working with:

```bash
python -m nfc
```

## Common Issues

### Reader Not Detected

- Ensure the reader is properly connected and powered
- Check device manager for any driver issues
- Try a different USB port

### Permission Issues (Linux/macOS)

```bash
# Add user to the pcscd group
sudo usermod -a -G pcscd $USER

# Apply group changes (may need to log out/in)
newgrp pcscd
```

### Python Module Import Errors

- Ensure you've activated the virtual environment
- Try reinstalling requirements: `pip install -r requirements.txt --force-reinstall`

For additional help, please check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md) or open an issue on GitHub.
