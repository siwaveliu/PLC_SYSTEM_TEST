import serial
import time
import plc_tb_ctrl
import config

class TestDataReader(object):
    def __init__(self):
        self.ser = serial.Serial()
        self.frame = ''
        self.frame_total_len = 0

    def __del__(self):
        pass

    def open_port(self):
        self.ser.port = config.TEST_PORT
        self.ser.baudrate = config.TEST_PORT_BAUDRATE
        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = 0
        self.ser.open()
        plc_tb_ctrl._debug('Open test data reader port')

    def close_port(self):
        plc_tb_ctrl._debug('Close test data reader port')
        self.ser.close()

    def clear_port_rx_buf(self):
        self.ser.reset_input_buffer()

    def send_frame(self, frame):
        plc_tb_ctrl._trace_byte_stream('DL GDW1376P2', frame)
        self.ser.write(frame)

    def read_frame(self, frame_size, timeout=None):
        self.ser.timeout = timeout
        return self.ser.read(frame_size)

if __name__ == '__main__':
    pass
