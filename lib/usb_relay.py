from ctypes import *
import time

class UsbRelayDeviceInfo(Structure):
    pass

UsbRelayDeviceInfo._fields_ = [("serial_number", c_char_p),
                               ("device_path", c_char_p),
                               ("type", c_ubyte),
                               ("next", POINTER(UsbRelayDeviceInfo))]

class UsbRelay(object):
    def __init__(self):
        self.usb_relay_device = CDLL('usb_relay_device.dll')
        usb_relay_device_enumerate = self.usb_relay_device.usb_relay_device_enumerate
        usb_relay_device_enumerate.restype = POINTER(UsbRelayDeviceInfo)
        self.device_list = usb_relay_device_enumerate()
        self.curr_device = None

    def __del__(self):
        self.usb_relay_device.usb_relay_device_free_enumerate(self.device_list)

    def init_device(self, serial_number=None):
        if serial_number is None:
            usb_relay_device_open = self.usb_relay_device.usb_relay_device_open
            usb_relay_device_open.restype = c_int
            #print(type(self.device_list))
            self.curr_device = usb_relay_device_open(self.device_list)
        else:
            assert False, "serial number not supported"

    def open(self, *channel):
        if self.curr_device is not None:
            usb_relay_device_open_one_relay_channel = self.usb_relay_device.usb_relay_device_open_one_relay_channel
            usb_relay_device_open_one_relay_channel.restype = c_int
            for c in channel:
                result = usb_relay_device_open_one_relay_channel(self.curr_device, c_int(c))
            return result
        else:
            return 1

    def close(self, *channel):
        if self.curr_device is not None:
            usb_relay_device_close_one_relay_channel = self.usb_relay_device.usb_relay_device_close_one_relay_channel
            usb_relay_device_close_one_relay_channel.restype = c_int
            for c in channel:
                result = usb_relay_device_close_one_relay_channel(self.curr_device, c_int(c))
            return result
        else:
            return 1


