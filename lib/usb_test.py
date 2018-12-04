import usb_relay
import time

i = 0
usb = usb_relay.UsbRelay()
usb.init_device(None)
while True:
    i += 1
    print("the [" + str(i) + '] times')
    # usb.close(1,2,3,4,5,6)
    usb.open(1)
    print("power off all of meters and cco, delay 5s")
    time.sleep(5)
    usb.close(1)
    print("power on all of meters and cco. delay 5s for boot")
    time.sleep(5)

usb = None