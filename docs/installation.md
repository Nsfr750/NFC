# Installation Guide

This guide provides step-by-step instructions for installing the NFC Tool on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for development installations)
- NFC reader hardware

## Installation Methods

### Method 1: Using pip (Recommended)

```bash
# Clone the repository
git clone https://github.com/Nsfr750/NFC.git
cd NFC

# Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install the package in development mode
pip install -e .
# or install directly
pip install -r requirements.txt
```

### Method 2: From Source

1. Download the latest release from [GitHub](https://github.com/Nsfr750/NFC/releases)
2. Extract the archive
3. Navigate to the project directory
4. Follow the same virtual environment and installation steps as above

## Dependencies

The following dependencies will be installed automatically:

- `pyscard` - For smart card communication
- `cryptography` - For secure operations
- `wand` - For image processing
- `PyQt5` - For the graphical interface
- `pywin32` - Windows-specific functionality (Windows only)

## Verifying the Installation

To verify that the installation was successful, run:

```bash
python -c "import nfctool; print('NFC Tool installed successfully!')"
```

## Updating

To update to the latest version:

```bash
# Navigate to the project directory
cd path/to/NFC

# Pull the latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Uninstallation

To uninstall the NFC Tool:

```bash
# If installed with pip
pip uninstall nfctool

# Remove the virtual environment (if used)
# On Windows:
rmdir /s /q venv
# On Unix or MacOS:
rm -rf venv
```

## Troubleshooting

If you encounter any issues during installation, please check the [Troubleshooting](troubleshooting.md) guide or open an issue on our [GitHub repository](https://github.com/Nsfr750/NFC/issues).
