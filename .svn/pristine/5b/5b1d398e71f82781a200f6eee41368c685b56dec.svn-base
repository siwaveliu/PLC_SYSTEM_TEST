import config
from struct import *
import serial

class SitraceLogger(object):
    def __init__(self, is_dut):
        self.ser = serial.Serial()
        self.frame = ''
        self.frame_total_len = 0
        self.START_FLAG = 0xFACE
        self.CLI_LOG_ID = 0x10
        self.CLI_SENDER_ID = 0xFF
        self.CLI_FRAME_HEAD_SIZE = 12
        self.is_dut = is_dut

    def __del__(self):
        pass

    def open_port(self):
        if self.is_dut:
            self.ser.port = config.DUT_SITRACE_PORT
            self.ser.baudrate = config.DUT_SITRACE_BAUDRATE
        else:
            self.ser.port = config.TB_SITRACE_PORT
            self.ser.baudrate = config.TB_SITRACE_BAUDRATE

        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = 0
        self.ser.open()

    def close_port(self):
        self.ser.close()

    def clear_port_rx_buf(self):
        self.ser.reset_input_buffer()

    def send_cli_cmd(self, cmd ):
        cmd_len = len(cmd) + 1
        data = pack('HHBBHL', self.START_FLAG, self.CLI_LOG_ID, 0, self.CLI_SENDER_ID, cmd_len, 0) + cmd + '\x00'
        self.ser.write(data)

if __name__ == '__main__':
    pass
