# NFC Reader/Writer Application

A powerful PySide6-based application for reading from and writing to various types of NFC tags with advanced features and a user-friendly interface.

## ✨ Features

- **Multi-tag Support**: Comprehensive support for various NFC tag types including:
  - NTAG (NTAG213, NTAG215, NTAG216)
  - MIFARE Classic (1K, 4K)
  - MIFARE Ultralight
  - FeliCa (Sony)
  - ISO 14443 Type A/B cards

- **NDEF Operations**:
  - Read and write NDEF records
  - Create and manage multiple NDEF records
  - Support for various NDEF record types (Text, URI, Smart Poster, etc.)
  - Hex view for raw data inspection

- **Tag Management**:
  - Read tag information (UID, memory layout, capabilities)
  - Write data to tags with validation
  - Lock tags to prevent unauthorized writes
  - Format tags for NDEF usage

- **User Interface**:
  - Modern, responsive design with sphinx_rtd_theme
  - Light/Dark/System theme support
  - Real-time tag detection and status updates
  - Detailed tag information panel
  - Log viewer with filtering options
  - Comprehensive documentation in English and Italian

- **Advanced Features**:
  - Tag emulation mode (experimental)
  - Batch operations for processing multiple tags
  - Custom command execution
  - Logging system with multiple verbosity levels
  - API documentation for developers
  - Troubleshooting guide for common issues
  - Contributing guidelines for open-source collaboration

## 🚀 Requirements

- Python 3.8 or higher
- Supported NFC Reader/Writer hardware:
  - ACR122U
  - PN532 (via USB/UART)
  - PC/SC compatible readers
- Windows 10/11 or Linux with PC/SC support
- Required Python packages (see `requirements.txt`)

## 📖 Documentation

Comprehensive documentation is available in both English and Italian, including:

- User Guide
- API Reference
- Troubleshooting Guide
- FAQ
- Contributing Guidelines

To build the documentation locally:

```bash
# Install documentation requirements
pip install -r requirements-docs.txt

# Build English documentation
cd docs/ENG
make html

# Build Italian documentation
cd ../ITA
make html
```

The documentation will be available in the `_build/html` directory of each language folder.

## 📦 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Nsfr750/NFC.git
   cd NFC
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install PC/SC drivers if not already installed:
   - Windows: Install [CCID drivers](https://ccid.apdu.fr/)
   - Linux: Install `pcscd` and `libpcsclite-dev` packages

5. Run the application:

   ```bash
   python main.py
   ```

## 🛠️ Building from Source

To build a standalone executable:

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Build the application:

   ```bash
   python ./compiler/pyinstaller_build_win.py
   ```
   or
   ```bash
   python ./compiler/pyinstaller_build_linux.py
   ```

3. The executable will be available in the `dist/windows` or `dist/linux` directory.

## 🚀 Usage

### Basic Operations

1. **Connect your NFC reader**
   - The application will automatically detect supported devices
   - Connection status is shown in the status bar

2. **Read a tag**
   - Place an NFC tag near the reader
   - Tag information will be displayed in the main window
   - View detailed memory layout in the hex editor

3. **Write to a tag**
   - Navigate to the "Write" tab
   - Select the record type (Text, URI, etc.)
   - Enter your content and click "Write to Tag"

4. **Lock a tag**
   - Use the "Lock" button to prevent further writes
   - Some tags support permanent locking (be careful!)

### 🛠️ Advanced Features

- **Tag Emulation**: Emulate an NFC tag (experimental)
- **Custom Commands**: Send raw APDU commands to the tag
- **Memory View**: Inspect and edit raw tag memory
- **Logging**: View detailed operation logs with filtering options

### ⚙️ Settings

Access settings via `Tools > Settings` or press `Ctrl+,`:

- **General**:
  - Auto-connect on startup
  - Language selection
  - Check for updates

- **NFC**:
  - Reader timeout
  - Auto-read on tag detection
  - Beep on tag detection

- **Interface**:
  - Theme (Light/Dark/System)
  - Font size and family
  - Window behavior

- **Advanced**:
  - Logging level
  - Custom commands
  - Developer options

### ⌨️ Keyboard Shortcuts

| Shortcut       | Action                     |
|----------------|----------------------------|
| `Ctrl+N`       | New project                |
| `Ctrl+O`       | Open file                  |
| `Ctrl+S`       | Save current data          |
| `Ctrl+Shift+S` | Save as...                 |
| `Ctrl+R`       | Read tag                   |
| `Ctrl+W`       | Write to tag               |
| `Ctrl+E`       | Erase tag                  |
| `Ctrl+L`       | Lock tag                   |
| `Ctrl+,`       | Open settings              |
| `F1`           | Show help                  |
| `F5`           | Refresh tag                |
| `Ctrl+Q`       | Quit application           |

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Report bugs by opening an issue
2. Suggest new features or improvements
3. Submit pull requests
4. Improve documentation
5. Share your feedback and ideas

Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📝 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## 👤 Author

- **Nsfr750**
  - Email: nsfr750@yandex.com
  - GitHub: [@Nsfr750](https://github.com/Nsfr750)
  - Discord: [Join our community](https://discord.gg/ryqNeuRYjD)

## 💖 Support

If you find this project useful, please consider supporting its development:

- [Become a Patron](https://www.patreon.com/Nsfr750)
- [Donate via PayPal](https://paypal.me/3dmega)
- Donate Monero:

  ```text
  47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF
  ```

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.

## 📋 TODO

Check out our [TO_DO.md](TO_DO.md) file for planned features and known issues.

## 📞 Contact

For support, feature requests, or questions, please open an issue on [GitHub](https://github.com/Nsfr750/NFC/issues) or join our [Discord server](https://discord.gg/ryqNeuRYjD).
