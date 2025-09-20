#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NS106 Reader Integration Test Script

This script tests the NS106 reader integration with the NFC application.
"""

import sys
import os
import serial.tools.list_ports
import nfc
import platform
from typing import List, Dict, Any

def test_ns106_detection():
    """Test NS106 reader detection."""
    print("🔍 NS106 Reader Detection Test")
    print("=" * 40)
    
    # Get all serial ports
    ports = serial.tools.list_ports.comports()
    ns106_found = False
    
    for port in ports:
        if port.vid == 0x072F and port.pid == 0x2200:
            ns106_found = True
            print(f"✅ NS106 Reader Found:")
            print(f"   Port: {port.device}")
            print(f"   Description: {port.description}")
            print(f"   Manufacturer: {port.manufacturer or 'Unknown'}")
            print(f"   Product: {port.product or 'Unknown'}")
            print(f"   VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}")
            if port.serial_number:
                print(f"   Serial: {port.serial_number}")
            break
    
    if not ns106_found:
        print("❌ NS106 Reader not found")
        print("   Available serial devices:")
        for port in ports:
            print(f"   - {port.device}: {port.description}")
            if port.vid and port.pid:
                print(f"     VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}")
    
    return ns106_found

def test_nfc_backends():
    """Test NFC backends with NS106 reader."""
    print("\n🔧 NFC Backend Test")
    print("=" * 40)
    
    backends_tested = []
    backends_working = []
    
    # Test USB backend
    try:
        print("Testing USB backend...")
        clf = nfc.ContactlessFrontend('usb')
        backends_working.append('usb')
        print("✅ USB backend working")
        clf.close()
    except Exception as e:
        print(f"❌ USB backend failed: {str(e)}")
    backends_tested.append('usb')
    
    # Test PC/SC backend
    try:
        print("Testing PC/SC backend...")
        clf = nfc.ContactlessFrontend('pcsc')
        backends_working.append('pcsc')
        print("✅ PC/SC backend working")
        clf.close()
    except Exception as e:
        print(f"❌ PC/SC backend failed: {str(e)}")
    backends_tested.append('pcsc')
    
    # Test UART backend
    try:
        print("Testing UART backend...")
        clf = nfc.ContactlessFrontend('uart')
        backends_working.append('uart')
        print("✅ UART backend working")
        clf.close()
    except Exception as e:
        print(f"❌ UART backend failed: {str(e)}")
    backends_tested.append('uart')
    
    # Test direct serial connection if NS106 is found
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid == 0x072F and port.pid == 0x2200:
            try:
                print(f"Testing direct connection to {port.device}...")
                if platform.system() == 'Windows':
                    port_spec = f"com:{port.device}"
                else:
                    port_spec = f"tty:{port.device}"
                
                clf = nfc.ContactlessFrontend(port_spec)
                backends_working.append(f"serial ({port.device})")
                print(f"✅ Direct serial connection working")
                clf.close()
                break
            except Exception as e:
                print(f"❌ Direct serial connection failed: {str(e)}")
    
    return backends_working

def test_tag_detection():
    """Test tag detection with NS106 reader."""
    print("\n🏷️  Tag Detection Test")
    print("=" * 40)
    
    print("Place an NFC tag on the NS106 reader...")
    print("Press Ctrl+C to cancel")
    
    try:
        # Try to connect using the best available backend
        clf = None
        
        # First try USB backend (preferred for NS106)
        try:
            clf = nfc.ContactlessFrontend('usb')
            print("✅ Connected via USB backend")
        except:
            pass
        
        # If USB failed, try PC/SC
        if not clf:
            try:
                clf = nfc.ContactlessFrontend('pcsc')
                print("✅ Connected via PC/SC backend")
            except:
                pass
        
        # If both failed, try direct serial
        if not clf:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port.vid == 0x072F and port.pid == 0x2200:
                    try:
                        if platform.system() == 'Windows':
                            port_spec = f"com:{port.device}"
                        else:
                            port_spec = f"tty:{port.device}"
                        
                        clf = nfc.ContactlessFrontend(port_spec)
                        print(f"✅ Connected via direct serial ({port.device})")
                        break
                    except:
                        pass
        
        if not clf:
            print("❌ Could not connect to any NFC backend")
            return False
        
        # Try to detect a tag
        print("Waiting for tag...")
        tag = clf.sense()
        
        if tag:
            print("✅ Tag detected!")
            print(f"   Type: {type(tag).__name__}")
            print(f"   UID: {tag.identifier.hex()}")
            
            # Try to get more tag information
            if hasattr(tag, 'product'):
                print(f"   Product: {tag.product}")
            if hasattr(tag, 'atqa'):
                print(f"   ATQA: {tag.atqa.hex()}")
            if hasattr(tag, 'sak'):
                print(f"   SAK: {tag.sak.hex()}")
            
            clf.close()
            return True
        else:
            print("❌ No tag detected")
            clf.close()
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️  Test cancelled by user")
        if clf:
            clf.close()
        return False
    except Exception as e:
        print(f"❌ Error during tag detection: {str(e)}")
        if clf:
            clf.close()
        return False

def main():
    """Main test function."""
    print("NS106 Reader Integration Test")
    print("=" * 50)
    
    # Test 1: Detection
    ns106_detected = test_ns106_detection()
    
    # Test 2: Backend compatibility
    working_backends = test_nfc_backends()
    
    # Test 3: Tag detection (only if NS106 is detected and backends work)
    if ns106_detected and working_backends:
        tag_detected = test_tag_detection()
    else:
        print("\n⚠️  Skipping tag detection test (NS106 not detected or no working backends)")
        tag_detected = False
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    print(f"NS106 Detection: {'✅' if ns106_detected else '❌'}")
    print(f"Working Backends: {', '.join(working_backends) if working_backends else '❌ None'}")
    print(f"Tag Detection: {'✅' if tag_detected else '❌'}")
    
    if ns106_detected and working_backends:
        print("\n🎉 NS106 reader integration test completed successfully!")
        print("The NS106 reader should work with your NFC application.")
    else:
        print("\n⚠️  NS106 reader integration test completed with issues.")
        print("Please check the following:")
        if not ns106_detected:
            print("- Ensure the NS106 reader is properly connected")
            print("- Check USB cable and port")
        if not working_backends:
            print("- Install required dependencies: pip install pyserial nfcpy")
            print("- Try running as administrator (Windows)")
            print("- Check device drivers")

if __name__ == "__main__":
    main()
