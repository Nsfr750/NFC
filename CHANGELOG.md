# Changelog

All notable changes to the NFC Reader/Writer application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-08-26

### Added

- **Application Locking**: Added ability to lock the application with password protection
- **Session Management**: Implemented session timeout and auto-lock features
- **UI Enhancements**: Improved error handling and user feedback
- **Documentation**: Added CONTRIBUTING.md and PREREQUISITES.md
- **Code Quality**: Added type hints and improved code documentation
- **Type 1 (Topaz) Operations**: Added support for reading and writing Type 1 tags
- **Type 2 (MIFARE Ultralight/NTAG) Operations**: Added support for reading and writing Type 2 tags
- **Type 3 (FeliCa) Operations**: Added support for reading and writing Type 3 tags
- **Type 4 (DESFire) Operations**: Added support for reading and writing Type 4 tags
- **Type 5 (Vicinity/ISO 15693) Operations**: Added support for reading and writing Type 5 tags
- **Type 5 (ISO 15693) Operations**: Enhanced support for ISO 15693 tags
  - Added block-based read/write operations
  - Implemented block locking functionality
  - Added tag information retrieval
  - Improved error handling and input validation
- **Error Handling**: Added specific error messages for unsupported operations across all tag types
- **Documentation**: Added comprehensive documentation of supported operations for each tag type in `docs/supported_operations.md`
- Password recovery system with recovery key generation
- Recovery dialog UI for resetting forgotten passwords

### Changed

- **Documentation**: Updated documentation for new Type 2 operations

### Fixed

- **Type 2 (MIFARE Ultralight/NTAG) Operations**: Fixed bug in Type 2 tag detection
- **Type 5 (ISO 15693) Operations**: Fixed block size validation in write operations
- Fixed issue with application locking functionality
- Resolved password recovery flow issues
- Fixed UI layout problems on high-DPI displays
- Addressed several minor bugs in tag reading/writing operations

## [1.0.1] - 2025-08-26

### Security

- Added password protection for sensitive operations
  - Secure password hashing with PBKDF2 and salt
  - Password change functionality
  - Toggle for enabling/disabling password protection
  - Protected operations include Tag Tools, Tag Database, and Tag Cloner
  - New Security menu for managing authentication settings
  
- **Documentation**: Comprehensive documentation in English and Italian
  - User Guide with detailed instructions
  - API Reference for developers
  - Troubleshooting Guide for common issues
  - FAQ section
  - Contributing Guidelines for open-source collaboration
  - Updated help documentation for new security features
  
- **Documentation Build System**:
  - Sphinx-based documentation with sphinx_rtd_theme
  - Automated build scripts for both English and Italian versions
  - Cross-referencing between documentation sections
  - Search functionality
  - Responsive design for all devices

### Documentation

- Updated README.md with new documentation features
  - Improved installation and setup instructions
  - Added examples and code samples
  - Enhanced navigation and organization

## [1.0.0] - 2025-08-26

### Features

- **Tag Emulation**: Experimental support for emulating various NFC tag types
- **Batch Operations**: Process multiple tags in sequence with automated workflows
- **Custom Commands**: Advanced users can send raw APDU commands to tags
- **Hex View**: Inspect and edit raw tag memory with hex editor
- **Tag Types**: Added support for NTAG 21x series, MIFARE Classic 1K/4K, MIFARE Ultralight, and FeliCa Lite
- **Real-time Monitoring**: Background scanning for tag presence detection
- **Tag Database**: Store and manage known tags with custom metadata
- **Export/Import**: Save and load tag data in multiple formats (JSON, binary, text)
- **Advanced Logging**: Configurable logging with multiple verbosity levels
- **Keyboard Shortcuts**: Quick access to common operations
- **Themes**: Support for light, dark, and system themes
- **Auto-update**: Check for and install application updates
- **Command-line Interface**: Scriptable interface for automation
- **Plugin System**: Extend functionality with custom plugins
- **Tag Analysis**: Detailed tag information and memory analysis
- **NDEF Tools**: Create, edit, and validate NDEF records
- **Tag Cloning**: Duplicate compatible tags with a single click
- **Password Protection**: Secure sensitive operations with password
- **Tag Formatting**: Quick format tags for NDEF usage
- **Custom Record Types**: Support for custom NDEF record types
- **Tag Simulation**: Test applications with virtual tags
- **System Tray**: Minimize to system tray for background operation
- **Auto-save**: Automatic saving of unsaved changes
- **Tag History**: Keep track of recently used tags
- **Statistics**: Usage statistics and operation history
- **Custom Themes**: Create and apply custom UI themes
- **Command Palette**: Quick access to all features
- **Context Help**: Integrated help system with tooltips
- **Tag Comparison**: Compare two tags side by side
- **Character Encoding**: Support for multiple character encodings
- **Writing Presets**: Save and load common write configurations
- **Data Validation**: Custom validation rules for tag data
- **Contactless Payment**: Basic support for payment systems
- **Tag Authentication**: Support for authenticated operations
- **Memory Analysis**: Tools for analyzing tag memory layout
- **Tag Emulation**: Emulate various tag types for testing
- **NFC Forum Types**: Support for NFC Forum tag types 1-5
- **Password Management**: Store and manage tag passwords securely
- **ISO 14443**: Support for Type A and Type B cards
- **Read/Write Protection**: Configure tag access permissions
- **NDEF Support**: Comprehensive NDEF record handling
- **Capacity Info**: Display detailed tag capacity information
- **MIFARE DESFire**: Basic support for DESFire EV1/EV2/EV3
- **Access Control**: Fine-grained control over tag access
- **ISO 7816-4**: Support for ISO 7816-4 commands
- **Tag Initialization**: Tools for initializing new tags
- **NFC Type 1-4**: Support for all standard NFC tag types
- **Tag Detection**: Improved tag presence detection
- **FeliCa Support**: Basic support for Sony FeliCa cards
- **History Tracking**: Track read/write operations
- **ISO 15693**: Support for ISO 15693 tags
- **Performance**: Optimized read/write operations
- **Error Handling**: Comprehensive error handling and recovery
- **Logging**: Detailed operation logging
- **UI/UX**: Improved user interface and experience
- **Accessibility**: Better keyboard navigation and screen reader support
- **Localization**: Support for multiple languages
- **Documentation**: Comprehensive user and developer documentation
- **Testing**: Automated test suite
- **Build System**: Streamlined build and deployment
- **Dependencies**: Updated third-party libraries
- **Security**: Improved security measures
- **Performance**: Optimized performance and reduced memory usage
- **Compatibility**: Improved compatibility with various NFC readers
- **Stability**: General stability improvements and bug fixes

### Improvements

- **Codebase**: Major refactoring for better maintainability and performance
- **UI/UX**: Completely redesigned user interface with modern look and feel
- **Performance**: Optimized tag reading/writing operations
- **Error Handling**: More descriptive error messages and recovery options
- **Documentation**: Updated documentation with new features and improvements
- **Build System**: Simplified build and deployment process
- **Dependencies**: Updated to latest stable versions
- **Code Quality**: Improved code quality and test coverage
- **Security**: Enhanced security measures and best practices
- **Compatibility**: Better support for various NFC readers and tags
- **Stability**: Improved application stability and reliability

### Bug Fixes

- **Tag Detection**: Issues with certain tag types not being detected
- **Memory Leaks**: Fixed memory leaks in NFC operations
- **UI Freezes**: Improved UI responsiveness during operations
- **Error Handling**: Better handling of edge cases and error conditions
- **Compatibility**: Fixed issues with specific NFC readers
- **Performance**: Optimized performance for large tag operations
- **Security**: Addressed security vulnerabilities
- **Localization**: Fixed translation issues
- **Documentation**: Corrected inaccuracies in documentation
- **Build System**: Fixed build issues on various platforms
- **Dependencies**: Resolved compatibility issues with third-party libraries

## [0.1.0] - 2025-08-26

### Initial Release

- Initial public release of NFC Reader/Writer
- Basic tag reading and writing functionality
- Simple text-based UI for tag operations
- Support for common NFC tag types (MIFARE Classic, NTAG, FeliCa)
- Basic NDEF record handling
- Simple settings and configuration
- Basic error handling and user feedback
- Logging system for debugging

---

*Note: This changelog follows the format specified in [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
For more details about the project, see the [README.md](README.md) file.*
