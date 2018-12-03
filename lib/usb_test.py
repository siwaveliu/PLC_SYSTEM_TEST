import usb_relay
import time

usb = usb_relay.UsbRelay()
usb.init_device(None)
# usb.close(1,2,3,4,5,6)
usb.open(1,2,3,4,5,6)
print("power off all of meters and cco, delay 5s")
time.sleep(3)
usb.close(1,2,3,4,5,6)
print("power on all of meters and cco. delay 5s for boot")
time.sleep(3)
usb.open(1,2,3,4,5,6)
print("power off all of meters and cco, delay 5s")
time.sleep(3)
usb.close(1,2,3,4,5,6)
print("power on all of meters and cco. delay 5s for boot")
usb = None