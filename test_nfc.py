import nfc
import ndef

def on_startup(targets):
    print("NFC Reader ready. Please place a tag near the reader...")
    return targets

def on_connect(tag):
    print("\nTag detected!")
    print(f"Type: {tag.type}")
    print(f"ID: {tag.identifier.hex()}")
    
    # Try to read NDEF data if available
    try:
        ndef_data = tag.ndef
        if ndef_data:
            print("\nNDEF Records:")
            for record in ndef_data.records:
                print(f"- {record}")
        else:
            print("No NDEF data found on this tag.")
    except Exception as e:
        print(f"Error reading NDEF data: {e}")
    
    return True

def main():
    print("Initializing NFC reader...")
    
    try:
        # Create an NFC reader instance
        with nfc.ContactlessFrontend('usb') as clf:
            if not clf:
                print("No NFC reader found. Please make sure your reader is connected.")
                return
                
            print("NFC Reader found and ready!")
            print("Press Ctrl+C to exit")
            
            # Start the tag reader
            clf.connect(rdwr={
                'on-startup': on_startup,
                'on-connect': on_connect,
                'beep-on-connect': True,
            })
            
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
