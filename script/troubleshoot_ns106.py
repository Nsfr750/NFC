#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NS106 Reader Troubleshooting Script

This script helps troubleshoot NS106 reader connection issues.
"""

import sys
import os
import subprocess
import platform
import serial.tools.list_ports
from typing import List, Dict, Any

def check_dependencies():
    """Check if required dependencies are installed."""
    print("📦 Checking Dependencies")
    print("=" * 40)
    
    dependencies = [
        ('pyserial', 'serial'),
        ('nfcpy', 'nfc'),
        ('libusb', 'usb.core'),
        ('libusb-win32', 'usb'),
    ]
    
    missing_deps = []
    
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {dep_name} - Installed")
        except ImportError:
            print(f"❌ {dep_name} - Missing")
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Install them with:")
        print("pip install pyserial nfcpy")
        if platform.system() == 'Windows':
            print("You may also need to install libusb-win32 or Zadig")
    else:
        print("✅ All required dependencies are installed")
    
    return len(missing_deps) == 0

def check_usb_devices():
    """Check all USB devices and look for NS106."""
    print("\n🔌 USB Device Analysis")
    print("=" * 40)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial devices found")
        return False
    
    print(f"Found {len(ports)} serial device(s):")
    ns106_found = False
    
    for i, port in enumerate(ports, 1):
        print(f"\nDevice {i}:")
        print(f"  Port: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Manufacturer: {port.manufacturer or 'Unknown'}")
        print(f"  Product: {port.product or 'Unknown'}")
        
        if port.vid and port.pid:
            print(f"  VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}")
            
            # Check if this is NS106
            if port.vid == 0x072F and port.pid == 0x2200:
                print("  🎯 This is the NS106 reader!")
                ns106_found = True
            else:
                # Identify common devices
                if port.vid == 0x2341 and port.pid == 0x0043:
                    print("  📝 This is an Arduino device")
                elif port.vid == 0x0403 and port.pid == 0x6001:
                    print("  📝 This is an FTDI device")
                elif port.vid == 0x046D and port.pid == 0xC52B:
                    print("  📝 This is a Logitech device")
                else:
                    print("  📝 Unknown device type")
        
        if port.serial_number:
            print(f"  Serial: {port.serial_number}")
        if port.hwid:
            print(f"  HWID: {port.hwid}")
    
    return ns106_found

def check_nfc_libusb():
    """Check NFC library and libusb compatibility."""
    print("\n🔧 NFC Library and libusb Check")
    print("=" * 40)
    
    try:
        import nfc
        print("✅ nfcpy library imported successfully")
        
        # Check available backends
        try:
            clf = nfc.ContactlessFrontend('usb')
            print("✅ USB backend available")
            clf.close()
        except Exception as e:
            print(f"❌ USB backend failed: {str(e)}")
        
        try:
            clf = nfc.ContactlessFrontend('pcsc')
            print("✅ PC/SC backend available")
            clf.close()
        except Exception as e:
            print(f"❌ PC/SC backend failed: {str(e)}")
            
    except ImportError:
        print("❌ nfcpy library not installed")
        return False
    
    # Check libusb
    try:
        import usb.core
        print("✅ libusb (PyUSB) available")
        
        # List all USB devices
        devices = usb.core.find(find_all=True)
        print(f"Found {len(list(devices))} USB devices")
        
        # Look for NS106 specifically
        ns106_devices = usb.core.find(idVendor=0x072F, idProduct=0x2200, find_all=True)
        ns106_list = list(ns106_devices)
        if ns106_list:
            print(f"✅ Found {len(ns106_list)} NS106 device(s) via libusb")
            return True
        else:
            print("❌ NS106 not found via libusb")
            
    except ImportError:
        print("❌ PyUSB not installed")
    except Exception as e:
        print(f"❌ libusb error: {str(e)}")
    
    return False

def check_system_info():
    """Check system information that might affect NFC."""
    print("\n💻 System Information")
    print("=" * 40)
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    
    # Check if running as admin (Windows)
    if platform.system() == 'Windows':
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            print(f"Administrator privileges: {'✅ Yes' if is_admin else '❌ No'}")
            if not is_admin:
                print("⚠️  Try running as administrator for better device access")
        except:
            print("❌ Could not check administrator privileges")

def provide_recommendations():
    """Provide troubleshooting recommendations."""
    print("\n🛠️  Troubleshooting Recommendations")
    print("=" * 40)
    
    print("1. 🔌 Physical Connection:")
    print("   - Ensure NS106 reader is properly connected via USB")
    print("   - Try a different USB port")
    print("   - Try a different USB cable")
    
    print("\n2. 📦 Software Dependencies:")
    print("   - Install required packages:")
    print("     pip install pyserial nfcpy")
    print("   - For Windows, you may need:")
    print("     pip install pyusb")
    
    print("\n3. 🔧 Driver Issues (Windows):")
    print("   - Open Device Manager")
    print("   - Look for NS106 reader under 'Universal Serial Bus devices'")
    print("   - If it has a yellow exclamation mark:")
    print("     * Right-click and select 'Update driver'")
    print("     * Choose 'Browse my computer for drivers'")
    print("     * Select 'Let me pick from a list'")
    print("     * Choose 'USB Composite Device' or 'CCID device'")
    
    print("\n4. 🔄 Alternative: Zadig Tool:")
    print("   - Download Zadig: https://zadig.akeo.ie/")
    print("   - Run Zadig as administrator")
    print("   - Select NS106 reader from the dropdown")
    print("   - Install libusb-win32 or WinUSB driver")
    
    print("\n5. 🧪 Test with Different Backends:")
    print("   - Try running: python -m nfc.clf")
    print("   - This will show available NFC readers")
    
    print("\n6. 📱 Check Device Compatibility:")
    print("   - Ensure your NS106 reader is not counterfeit")
    print("   - Some clones may have different VID/PID")
    print("   - Check device documentation for correct identifiers")

def main():
    """Main troubleshooting function."""
    print("NS106 Reader Troubleshooting Assistant")
    print("=" * 50)
    
    # Run all checks
    deps_ok = check_dependencies()
    ns106_found = check_usb_devices()
    nfc_ok = check_nfc_libusb()
    check_system_info()
    
    # Summary
    print("\n📊 Troubleshooting Summary")
    print("=" * 40)
    print(f"Dependencies: {'✅ OK' if deps_ok else '❌ Issues'}")
    print(f"NS106 Detected: {'✅ Yes' if ns106_found else '❌ No'}")
    print(f"NFC Library: {'✅ Working' if nfc_ok else '❌ Issues'}")
    
    if ns106_found and nfc_ok:
        print("\n🎉 NS106 reader should be working!")
        print("Try running the main application again.")
    else:
        print("\n⚠️  Issues detected that need to be resolved.")
        provide_recommendations()

if __name__ == "__main__":
    main()
