import usb.core
import usb.util
import usb.backend.libusb1
from usb.backend import libusb1
from infi.devicemanager import DeviceManager

dm = DeviceManager()
devices = dm.all_devices
for d in devices:
    try:
        print(f'{d.friendly_name} : address: {d.address}, bus: {d.bus_number}, location: {d.location}')
    except Exception:
        pass


# Try to find libusb backend
try:
    backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\windows\\system32\\libusb-1.0.dll")
    if backend is None:
        print("libusb backend not found, trying default backend")
        backend = usb.backend.libusb1.get_backend()
    
    usb_devices = usb.core.find(backend=backend, find_all=True)
    print(f"Found {len(list(usb_devices))} USB devices")
except Exception as e:
    print(f"Error initializing USB backend: {e}")
    usb_devices = []


def enumerate_usb():  # I use a simple function that scans all known USB connections and saves their info in the file
    with open("EnumerateUSBLog.txt", "w") as wf:
        for i, d in enumerate(usb_devices):
            try:
                wf.write(f"USB Device number {i}:\n")
                wf.write(f"Vendor ID: 0x{d.idVendor:04x}, Product ID: 0x{d.idProduct:04x}\n")
                try:
                    if hasattr(d, 'manufacturer') and d.manufacturer:
                        wf.write(f"Manufacturer: {d.manufacturer}\n")
                    if hasattr(d, 'product') and d.product:
                        wf.write(f"Product: {d.product}\n")
                    if hasattr(d, 'serial_number') and d.serial_number:
                        wf.write(f"Serial: {d.serial_number}\n")
                except:
                    pass
                wf.write("\n")
            except NotImplementedError:
                wf.write(f"Device number {i} is busy.\n\n")
            except usb.core.USBError:
                wf.write(f"Device number {i} is either disconnected or not found.\n\n")


def find_device():
    try:
        # Use the same backend as above
        vendor_id = 0x2708
        product_id = 0x0003

        device = usb.core.find(
                idVendor=vendor_id,
                idProduct=product_id,
                backend=backend,
            )

        if device is None:
            print("Device not found")
        else:
            print("Device found")
            print(f"Vendor ID: 0x{device.idVendor:04x}, Product ID: 0x{device.idProduct:04x}")
    except Exception as e:
        print(f"Error finding device: {e}")

# Run the functions
enumerate_usb()
find_device()