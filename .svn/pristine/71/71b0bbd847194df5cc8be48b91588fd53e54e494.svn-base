# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import meter
import tc_common
import plc_packet_helper
import time
import serial

'''
case for do some tests.
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    
    
    ser = serial.Serial()
    ser.port = 'COM10'
    ser.baudrate = 115200
    ser.parity = serial.PARITY_EVEN
    ser.timeout = 0
    ser.open()
    
    for ii in range(512):
        data += str(ii%256) 
    
    while True:
        ser.write(data)
 


    ser.close_port()






