# User Guide

This guide provides detailed instructions on how to use the NFC Tool effectively.

## Table of Contents
- [User Interface Overview](#user-interface-overview)
- [Reading NFC Tags](#reading-nfc-tags)
- [Writing to NFC Tags](#writing-to-nfc-tags)
- [Authentication](#authentication)
- [Settings](#settings)
- [Logs](#logs)

## User Interface Overview

The NFC Tool features a clean, intuitive interface with the following main components:

1. **Menu Bar** - Access all application functions
2. **Toolbar** - Quick access to common operations
3. **Status Bar** - Displays connection status and messages
4. **Main Workspace** - Displays tag information and operation results

## Reading NFC Tags

1. Connect your NFC reader
2. Click the "Read" button or press `Ctrl+R`
3. Bring an NFC tag close to the reader
4. The tag data will be displayed in the main workspace

## Writing to NFC Tags

1. Select "Write" from the menu or press `Ctrl+W`
2. Choose the data type to write:
   - Text
   - URL
   - Contact (vCard)
   - Custom data
3. Enter the data in the provided fields
4. Click "Write" and bring the tag close to the reader
5. Wait for the success confirmation

## Authentication

The NFC Tool includes a secure authentication system:

- **Login**: Enter your username and password
- **Password Recovery**: Use the "Forgot Password" feature
- **User Roles**: Different access levels (Admin, User, Guest)

## Settings

Access settings by clicking the gear icon or pressing `Ctrl+,`

### General
- Language selection
- Theme (Light/Dark)
- Start with system

### NFC Reader
- Auto-detect reader
- Manual reader selection
- Read/write timeout settings

### Security
- Auto-lock timeout
- Password requirements
- Session management

## Logs

View application logs for troubleshooting:

1. Click on "View" > "Logs"
2. Filter logs by:
   - Date/Time
   - Log level (Info, Warning, Error)
   - Module
3. Export logs for support

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New tag operation |
| `Ctrl+O` | Open saved tag data |
| `Ctrl+S` | Save current tag data |
| `Ctrl+P` | Print tag information |
| `F1` | Help |
| `F5` | Refresh tag data |

## Advanced Features

### Batch Operations
- Read multiple tags in sequence
- Write common data to multiple tags
- Import/export tag data in various formats

### Tag Formatting
- Format tags (erases all data)
- Lock tags to prevent writing
- Set read-only areas

### Scripting
- Create custom scripts for automation
- Schedule tag operations
- Integrate with other applications

## Troubleshooting

Common issues and solutions are available in the [Troubleshooting](troubleshooting.md) guide.
