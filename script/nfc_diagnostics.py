#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFC Diagnostics Script

This script helps diagnose NFC backend issues and provides detailed information
about available readers, backends, and system dependencies.
"""

import sys
import os
import platform
import traceback
from typing import List, Dict, Any

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher."
    return True, f"Python {version.major}.{version.minor}.{version.micro} - OK"

def check_dependencies():
    """Check if required Python packages are installed."""
    dependencies = {
        'nfcpy': 'nfc',
        'PyUSB': 'usb.core',
        'pyserial': 'serial',
        'PySide6': 'PySide6',
        'ndeflib': 'ndef',
    }
    
    results = {}
    for name, module_path in dependencies.items():
        try:
            __import__(module_path)
            results[name] = True
        except ImportError:
            results[name] = False
    
    return results

def check_system_dependencies():
    """Check system-level dependencies."""
    issues = []
    system = platform.system()
    
    if system == 'Windows':
        try:
            import ctypes
            # Check for libusb
            try:
                libusb = ctypes.CDLL('libusb-1.0.dll')
            except:
                issues.append("libusb not found - install from https://libusb.info/")
            
            # Check for PC/SC
            try:
                winscard = ctypes.CDLL('winscard.dll')
            except:
                issues.append("PC/SC not available - install PC/SC drivers")
                
        except ImportError:
            issues.append("ctypes not available")
    
    elif system == 'Linux':
        try:
            import subprocess
            result = subprocess.run(['which', 'pcscd'], capture_output=True, text=True)
            if result.returncode != 0:
                issues.append("pcscd not found - install: sudo apt install pcscd")
            
            result = subprocess.run(['which', 'libusb'], capture_output=True, text=True)
            if result.returncode != 0:
                issues.append("libusb not found - install: sudo apt install libusb-1.0-0-dev")
                
        except Exception as e:
            issues.append(f"Error checking Linux dependencies: {str(e)}")
    
    return issues

def test_nfc_backends():
    """Test available NFC backends."""
    backends = []
    errors = {}
    
    try:
        import nfc
        
        # Test USB backend
        try:
            clf = nfc.ContactlessFrontend('usb')
            backends.append('usb')
            clf.close()
        except Exception as e:
            errors['usb'] = str(e)
        
        # Test PC/SC backend
        try:
            clf = nfc.ContactlessFrontend('pcsc')
            backends.append('pcsc')
            clf.close()
        except Exception as e:
            errors['pcsc'] = str(e)
        
        # Test UART backend
        try:
            clf = nfc.ContactlessFrontend('uart')
            backends.append('uart')
            clf.close()
        except Exception as e:
            errors['uart'] = str(e)
            
    except ImportError:
        errors['nfcpy'] = "nfcpy not installed"
    
    return backends, errors

def test_serial_ports():
    """Test direct connection to detected serial ports."""
    results = []
    
    try:
        import nfc
        import serial.tools.list_ports
        
        # Get all serial ports
        ports = serial.tools.list_ports.comports()
        print(f"   [DEBUG] Found {len(ports)} serial ports")
        
        if not ports:
            results.append({'error': 'No serial ports found'})
            return results
        
        for port in ports:
            print(f"   [DEBUG] Processing port: {port.device}")
            port_result = {
                'port': port.device,
                'description': port.description,
                'success': False,
                'error': None,
                'backend_used': None,
                'device_details': {}
            }
            
            # Collect detailed device information
            if port.vid and port.pid:
                port_result['device_details']['vid_pid'] = f"VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}"
                print(f"   [DEBUG] Device VID/PID: 0x{port.vid:04x}, 0x{port.pid:04x}")
            if port.manufacturer:
                port_result['device_details']['manufacturer'] = port.manufacturer
                print(f"   [DEBUG] Device manufacturer: {port.manufacturer}")
            if port.product:
                port_result['device_details']['product'] = port.product
                print(f"   [DEBUG] Device product: {port.product}")
            if port.serial_number:
                port_result['device_details']['serial_number'] = port.serial_number
                print(f"   [DEBUG] Device serial: {port.serial_number}")
            
            # Try to identify the device type
            known_chips = {
                # Dedicated NFC/RFID readers that might use Arduino-compatible chips
                (0x2341, 0x0043): "Smart Access Control Card Copier (13.56MHz/125KHz/250KHz) - NFC/RFID Reader",
                (0x2341, 0x0010): "NFC/RFID Access Control System",
                (0x2A03, 0x0043): "Encrypted Card Decoder/Access Control System",
                
                # NS106 Dual Frequency RFID/NFC Reader
                (0x072F, 0x2200): "NS106 Dual Frequency RFID/NFC Reader (125KHz/13.56MHz)",
                
                # Common NFC readers
                (0x072F, 0x90CC): "ACR1222L NFC Reader",
                (0x04CC, 0x0531): "PN532 NFC Module",
                (0x054C, 0x06C1): "Sony RC-S380 NFC Reader",
                (0x1D6B, 0x0001): "Linux Foundation NFC Reader",
                (0x165c, 0x0011): "PN532 NFC controller",
                
                # USB-to-Serial chips (for reference)
                (0x1a86, 0x7523): "CH340 USB-to-Serial",
                (0x0403, 0x6001): "FTDI FT232RL",
                (0x10c4, 0xea60): "Silicon Labs CP2102",
                (0x067b, 0x2303): "Prolific PL2303",
                
                # Arduino boards (for reference - less likely to be NFC readers)
                (0x2341, 0x0042): "Arduino Uno",
                (0x2341, 0x0010): "Arduino Mega",
            }
                
            chip_id = (port.vid, port.pid)
            if chip_id in known_chips:
                port_result['device_details']['identified_as'] = known_chips[chip_id]
                print(f"   [DEBUG] Device identified as: {known_chips[chip_id]}")
                
                # Special handling for different types of devices
                if chip_id == (0x2341, 0x0043):
                    port_result['device_details']['note'] = "This is a dedicated Smart Access Control Card Copier device that supports multiple frequencies (13.56MHz/125KHz/250KHz)."
                    port_result['device_details']['recommendation'] = "This device should work as an NFC reader. Try installing libusb and running as administrator."
                    port_result['device_details']['expected_behavior'] = "Should be recognized as a dedicated NFC/RFID reader, not an Arduino."
                elif chip_id == (0x2341, 0x0010):
                    port_result['device_details']['note'] = "This device appears to be an NFC/RFID Access Control System."
                    port_result['device_details']['recommendation'] = "Try connecting with default baud rates."
                elif chip_id == (0x2A03, 0x0043):
                    port_result['device_details']['note'] = "This device appears to be an Encrypted Card Decoder/Access Control System."
                    port_result['device_details']['recommendation'] = "Try connecting with default baud rates."
                elif chip_id == (0x072F, 0x2200):
                    port_result['device_details']['note'] = "This is a NS106 Dual Frequency RFID/NFC Reader that supports both 125KHz and 13.56MHz frequencies."
                    port_result['device_details']['recommendation'] = "This device is CCID and PC/SC compliant. It should work with standard NFC libraries without additional drivers."
                    port_result['device_details']['expected_behavior'] = "Should be recognized as a standard CCID/PCSC device. Try USB or PCSC backend."
                    port_result['device_details']['supported_cards'] = "Supports EM4100, TK4100, T5577 (125KHz) and various 13.56MHz IC cards including UID, FUID, CUID, UFUID cards."
                elif chip_id == (0x072F, 0x90CC):
                    port_result['device_details']['note'] = "This is an ACS ACR1222L NFC Reader."
                    port_result['device_details']['recommendation'] = "This device should work with standard NFC libraries. Try USB or PCSC backend."
            else:
                print(f"   [DEBUG] Device not in known chips database")
            
            # Try different connection formats
            connection_formats = []
            
            if platform.system() == 'Windows':
                connection_formats = [
                    f"com:{port.device}",
                    f"com:{port.device.replace('COM', '')}",
                    port.device
                ]
                
                # Special handling for Arduino-based NFC readers
                if port.vid == 0x2341 and port.pid == 0x0043:
                    print(f"   [DEBUG] Arduino-based device detected - trying additional connection methods")
                    # Try different baud rates for Arduino serial communication
                    connection_formats.extend([
                        f"com:{port.device}:115200",
                        f"com:{port.device}:9600",
                        f"com:{port.device}:19200",
                        f"com:{port.device}:38400",
                        f"com:{port.device}:57600",
                    ])
            else:
                connection_formats = [
                    f"tty:{port.device}",
                    port.device
                ]
                
                # Special handling for Arduino-based NFC readers on Linux/Mac
                if port.vid == 0x2341 and port.pid == 0x0043:
                    print(f"   [DEBUG] Arduino-based device detected - trying additional connection methods")
                    connection_formats.extend([
                        f"tty:{port.device}:115200",
                        f"tty:{port.device}:9600",
                        f"tty:{port.device}:19200",
                        f"tty:{port.device}:38400",
                        f"tty:{port.device}:57600",
                    ])
            
            print(f"   [DEBUG] Trying connection formats: {connection_formats}")
            
            # Try each connection format
            for conn_format in connection_formats:
                try:
                    print(f"   [DEBUG] Trying format: {conn_format}")
                    clf = nfc.ContactlessFrontend(conn_format)
                    if clf:
                        port_result['success'] = True
                        port_result['backend_used'] = conn_format
                        clf.close()
                        print(f"   [DEBUG] Successfully connected using: {conn_format}")
                        break
                except Exception as e:
                    port_result['error'] = str(e)
                    print(f"   [DEBUG] Failed with format {conn_format}: {str(e)}")
                    # Don't continue if we get a "no such device" error - it means the format is wrong
                    if "No such device" in str(e) or "No backend available" in str(e):
                        break
                    continue
            
            results.append(port_result)
            print(f"   [DEBUG] Added port result with {len(port_result['device_details'])} device details")
            
    except ImportError as e:
        results.append({'error': f'Missing dependency: {str(e)}'})
        print(f"   [DEBUG] ImportError: {str(e)}")
    except Exception as e:
        results.append({'error': f'Error testing serial ports: {str(e)}'})
        print(f"   [DEBUG] Exception: {str(e)}")
    
    print(f"   [DEBUG] Returning {len(results)} results")
    return results

def detect_serial_devices():
    """Detect connected serial devices that might be NFC readers."""
    devices = []
    
    try:
        import serial.tools.list_ports
        
        # Get all serial ports
        ports = serial.tools.list_ports.comports()
        
        # Common NFC reader patterns in descriptions
        nfc_patterns = [
            'nfc', 'rfid', 'smart card', 'acr', 'pn532', 'rc-s380',
            'reader', 'contactless', 'proximity', 'identification',
            'dispositivo seriale', 'serial usb', 'usb serial', 'ch340',
            'ftdi', 'cp2102', 'pl2303', 'pn532', 'rc522', 'mfrc522',
            'ns106', 'kadongli', 'dual frequency', '125khz', '13.56mhz',
            'ic/id', 'card copier', 'duplicator', 'programmer'
        ]
        
        for port in ports:
            device_info = {
                'port': port.device,
                'description': port.description,
                'manufacturer': port.manufacturer or 'Unknown',
                'product': port.product or 'Unknown',
                'vid': port.vid if port.vid else None,
                'pid': port.pid if port.pid else None,
                'serial_number': port.serial_number or 'Unknown',
                'type': 'serial'
            }
            
            # Check if it matches known NFC reader patterns
            combined_text = f"{port.description} {port.product} {port.manufacturer}".lower()
            if any(pattern in combined_text for pattern in nfc_patterns):
                device_info['type'] = 'known_nfc'
                devices.append(device_info)
            else:
                # Include all serial devices for manual inspection
                device_info['type'] = 'potential_serial'
                devices.append(device_info)
                
    except ImportError:
        devices.append({'error': 'pyserial not installed'})
    except Exception as e:
        devices.append({'error': f'Error detecting serial devices: {str(e)}'})
    
    return devices

def run_diagnostics():
    """Run comprehensive NFC diagnostics."""
    print("🔍 NFC Diagnostics Tool (ENHANCED VERSION)")
    print("=" * 50)
    
    # Check Python version
    print("\n1. Python Version Check:")
    python_ok, python_msg = check_python_version()
    status = "✅" if python_ok else "❌"
    print(f"   {status} {python_msg}")
    
    # Check dependencies
    print("\n2. Python Dependencies:")
    deps = check_dependencies()
    for dep, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"   {status} {dep}: {'Installed' if installed else 'Missing'}")
    
    # Check system dependencies
    print("\n3. System Dependencies:")
    sys_issues = check_system_dependencies()
    if sys_issues:
        for issue in sys_issues:
            print(f"   ❌ {issue}")
    else:
        print("   ✅ All system dependencies OK")
    
    # Test NFC backends
    print("\n4. NFC Backend Test:")
    backends, errors = test_nfc_backends()
    if backends:
        for backend in backends:
            print(f"   ✅ {backend} backend available")
    else:
        print("   ❌ No NFC backends available")
    
    if errors:
        print("\n   Backend Errors:")
        for backend, error in errors.items():
            print(f"      {backend}: {error}")
    
    # Test serial ports
    print("\n5. Serial Port Test:")
    print("   [DEBUG] Testing serial ports with enhanced detection...")
    serial_results = test_serial_ports()
    print(f"   [DEBUG] Found {len(serial_results)} serial port results")
    
    for result in serial_results:
        if 'error' in result and 'device_details' not in result:
            print(f"   ❌ {result['error']}")
        else:
            status_icon = "✅" if result.get('success', False) else "❌"
            print(f"   {status_icon} {result['port']} ({result['description']})")
            
            # Always show device details if available
            if result.get('device_details'):
                print("      Device Details:")
                for key, value in result['device_details'].items():
                    print(f"         {key}: {value}")
            
            if result.get('success', False):
                print(f"      Backend used: {result['backend_used']}")
            else:
                print(f"      Error: {result.get('error', 'Unknown error')}")
            
            if not result.get('device_details'):
                print("      [DEBUG] No device details found")
    
    # Detect serial devices
    print("\n6. Serial Device Detection:")
    devices = detect_serial_devices()
    if devices:
        for device in devices:
            if 'error' in device:
                print(f"   ❌ {device['error']}")
            else:
                status_icon = "🎯" if device['type'] == 'known_nfc' else "❓"
                print(f"   {status_icon} {device['description']} (Port: {device['port']})")
    else:
        print("   ❌ No serial devices detected")
    
    # Summary and recommendations
    print("\n" + "=" * 50)
    print("📋 Summary and Recommendations:")
    
    if not python_ok:
        print("❌ Please upgrade Python to 3.8 or higher")
    
    missing_deps = [dep for dep, installed in deps.items() if not installed]
    if missing_deps:
        print(f"❌ Install missing dependencies: pip install {' '.join(missing_deps)}")
    
    if sys_issues:
        print("❌ Resolve system dependency issues listed above")
    
    if not backends:
        print("❌ No NFC backends available. Check:")
        print("   • NFC reader is connected")
        print("   • Drivers are installed")
        print("   • Run as administrator (Windows)")
        print("   • Check device permissions (Linux)")
    
    # Check if we found any devices that might need special handling
    nfc_devices = [r for r in serial_results if 'device_details' in r and 
                   any(keyword in r['device_details'].get('identified_as', '').lower() 
                       for keyword in ['nfc', 'rfid', 'access control', 'card copier', 'smart access'])]
    
    if nfc_devices and not backends:
        print("\n🔧 NFC/RFID Device Detected - Special Instructions:")
        print("   A dedicated NFC/RFID device was found but is not working as expected.")
        print("   This could mean:")
        print("   • Missing system dependencies (libusb)")
        print("   • Driver issues or incorrect drivers installed")
        print("   • Permission issues (try running as administrator)")
        print("   • The device needs specific connection parameters")
        print("   • The device may require special software or drivers")
        
        # Show the specific device details
        for device in nfc_devices:
            print(f"   Device: {device['port']} ({device['description']})")
            if 'device_details' in device:
                details = device['device_details']
                if 'identified_as' in details:
                    print(f"   Identified as: {details['identified_as']}")
                if 'note' in details:
                    print(f"   Note: {details['note']}")
                if 'recommendation' in details:
                    print(f"   Recommendation: {details['recommendation']}")
                if 'expected_behavior' in details:
                    print(f"   Expected: {details['expected_behavior']}")
    
    # Check for Arduino devices (separate from NFC devices)
    arduino_devices = [r for r in serial_results if 'device_details' in r and 
                      'arduino' in r['device_details'].get('identified_as', '').lower()]
    
    if arduino_devices and not backends:
        print("\n🔧 Arduino Device Detected - Special Instructions:")
        print("   An Arduino-based device was found but is not working as an NFC reader.")
        print("   This could mean:")
        print("   • The device is a standard Arduino, not an NFC reader")
        print("   • The device needs special NFC firmware")
        print("   • The device requires a specific baud rate or connection method")
        print("   • Try using Arduino IDE to check if NFC firmware is installed")
        print("   • Some NFC readers use Arduino-compatible chips")
        
        # Show the specific Arduino device details
        for device in arduino_devices:
            print(f"   Device: {device['port']} ({device['description']})")
            if 'device_details' in device:
                details = device['device_details']
                if 'identified_as' in details:
                    print(f"   Identified as: {details['identified_as']}")
                if 'recommendation' in details:
                    print(f"   Recommendation: {details['recommendation']}")
    
    # Check serial port test results
    successful_serial_connections = [r for r in serial_results if 'error' not in r and r.get('success', False)]
    if successful_serial_connections:
        print("✅ Direct serial port connection successful!")
        print(f"   Working port: {successful_serial_connections[0]['port']}")
        print(f"   Backend: {successful_serial_connections[0]['backend_used']}")
        print("   The main application should work with this reader.")
    elif serial_results and not any('error' in r for r in serial_results):
        print("❌ Serial port connections failed. This suggests:")
        print("   • The device may not be an NFC reader")
        print("   • The reader may require specific drivers")
        print("   • The reader may use a proprietary protocol")
        print("   • Try running as administrator (Windows)")
    
    if not devices:
        print("❌ No serial devices detected. Check:")
        print("   • Reader is properly connected")
        print("   • USB cable is working")
        print("   • Try a different USB port")
    
    if backends and devices:
        print("✅ NFC setup appears to be working!")
        print("   Try running the main application: python main.py")

if __name__ == "__main__":
    try:
        run_diagnostics()
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostics interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Diagnostics failed with error:")
        print(f"   {str(e)}")
        print(f"\n   Full traceback:")
        print(traceback.format_exc())
