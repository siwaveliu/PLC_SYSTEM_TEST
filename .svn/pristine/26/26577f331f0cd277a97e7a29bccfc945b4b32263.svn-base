import os.path
import sys
import serial
import time
import ctypes
import robot
import plc_packet_helper
import test_frame_helper
import plc_tb_ctrl
import config
from formats import *

START_CHAR = '\xED'
TEST_FRAME_HEAD_SIZE = test_frame_helper.get_test_frame_head_size()
TEST_FRAME_TAIL_SIZE = test_frame_helper.get_test_frame_tail_size()
TEST_FRAME_EXTRA_SIZE = 4
DEFAULT_TEST_FRAME_TIMEOUT = 10


class PlcTestbenchUart(object):
    def __init__(self):
        self.tb_ser = serial.Serial()
        self.test_frame = ''
        self.test_frame_total_len = 0

    def __del__(self):
        pass

    def open_tb_test_port(self):
        # open testbench port
        self.tb_ser.port = config.TB_PORT
        self.tb_ser.baudrate = config.TB_BAUDRATE
        self.tb_ser.timeout = 0
        self.tb_ser.open()
        plc_tb_ctrl._debug('Open TB port')

    def close_tb_test_port(self):
        plc_tb_ctrl._debug('Close TB port')
        self.tb_ser.close()

    def clear_tb_port_rx_buf(self):
        self.tb_ser.reset_input_buffer()

    def send_test_frame(self, test_frame_body, cf):
        total_len = len(test_frame_body) + TEST_FRAME_HEAD_SIZE + TEST_FRAME_TAIL_SIZE
        frame_head = test_frame_helper.build_head(total_len, cf, plc_tb_ctrl.TB_INSTANCE._gen_test_frame_sn())
        frame_tail = test_frame_helper.build_tail(0)
        test_frame = frame_head + test_frame_body + frame_tail
        self.tb_ser.write(test_frame)
        plc_tb_ctrl._trace_test_frame_ul(test_frame)

    def read_test_frame_head(self, ser):
        if (len(self.test_frame) == 0):
            start_char = ser.read(1)
            if (len(start_char) < 1):
                return None

            if (START_CHAR != start_char):
                return None

            self.test_frame = start_char

        if (len(self.test_frame) >= 1) and (len(self.test_frame) < TEST_FRAME_HEAD_SIZE):
            remaining_head_len = TEST_FRAME_HEAD_SIZE - len(self.test_frame)
            temp = ser.read(remaining_head_len)
            self.test_frame += temp
            if len(temp) < remaining_head_len:
                return None
            self.update_test_frame_total_len()

    def update_test_frame_total_len(self):
        frame_head = test_frame_helper.parse_test_frame_head(self.test_frame)
        if frame_head is None:
            plc_tb_ctrl._debug("Invalid test frame head: [{}]".format(" ".join("{:02x}".format(ord(i)) for i in self.test_frame)))
            # find the new frame start position
            new_start = self.test_frame.find(START_CHAR, 1)
            if new_start > 0:
                self.test_frame = self.test_frame[new_start:]
                if (len(self.test_frame) >= TEST_FRAME_HEAD_SIZE):
                    self.update_test_frame_total_len()
            else:
                self.test_frame = ''
        else:
            self.test_frame_total_len = frame_head.len + TEST_FRAME_EXTRA_SIZE

    def read_test_frame(self):
        result = None

        # receive frame head
        if (len(self.test_frame) < TEST_FRAME_HEAD_SIZE):
            self.read_test_frame_head(self.tb_ser)

        # receive frame body and frame tail
        if (len(self.test_frame) >= TEST_FRAME_HEAD_SIZE) and (len(self.test_frame) < self.test_frame_total_len):
            remaining_payload_len = self.test_frame_total_len - len(self.test_frame)
            test_frame_body_tail = self.tb_ser.read(remaining_payload_len)
            self.test_frame += test_frame_body_tail

        # check frame
        if (len(self.test_frame) >= TEST_FRAME_HEAD_SIZE) and (len(self.test_frame) == self.test_frame_total_len):
            try:
                result = test_frame_helper.parse_test_frame(self.test_frame)
                assert result is not None, 'parse test frame error'
                plc_tb_ctrl._trace_test_frame_dl(self.test_frame)
                self.test_frame = ''
            except:
                plc_tb_ctrl._debug("Invalid test frame: [{}]".format(" ".join("{:02x}".format(ord(i)) for i in self.test_frame)))
                # find the new frame start position
                new_start = self.test_frame.find(START_CHAR, 1)
                if new_start > 0:
                    self.test_frame = self.test_frame[new_start:]
                    if (len(self.test_frame) >= TEST_FRAME_HEAD_SIZE):
                        self.update_test_frame_total_len()
                else:
                    self.test_frame = ''
        return result


    # timeout: wait for x seconds
    def wait_for_test_frame(self, cf = None, timeout = None, timeout_assert = True):
        result = None

        if (self.test_frame != '' or self.test_frame_total_len != 0):
            plc_tb_ctrl._trace_byte_stream("clear test frame", self.test_frame)
            self.test_frame = ''
            self.test_frame_total_len = 0

        if timeout is None:
            timeout = DEFAULT_TEST_FRAME_TIMEOUT
        timeout *= config.CLOCK_RATE
        stop_time = time.time() + timeout

        while True:
            test_frame = self.read_test_frame()
            if (test_frame is not None):

                if "FC_PL_DATA" == test_frame.head.cf:
                    fc_pl_data_payload = test_frame.payload
                    fc_pl_data = fc_pl_data_payload.payload.data
                    fc = fc_pl_data[0:16]
                    fc = plc_packet_helper.parse_mpdu_fc(fc)

                    if (fc is not None):
                        if ("PLC_MPDU_BEACON" == fc.mpdu_type):
                            pb_size = fc_pl_data_payload.pb_size
                            end_pos = pb_size - plc_mpdu.PLC_PB_CRC_SIZE - plc_beacon.PLC_BEACON_CRC_SIZE
                            plc_tb_ctrl._trace_beacon_dl(fc_pl_data[16:(16+end_pos)])
                        elif ("PLC_MPDU_SOF" == fc.mpdu_type):
                            pb_num = fc_pl_data_payload.pb_num
                            pb_size = fc_pl_data_payload.pb_size
                            raw_data = plc_packet_helper.check_mac_frame(pb_num, pb_size, fc_pl_data[16:(16+pb_size*pb_num)])
                            if raw_data is not None:
                                plc_tb_ctrl._trace_mac_frame_dl(raw_data)
                        else:
                            pass

                if (cf is None) or (cf == test_frame.head.cf):
                    result = test_frame
                    break
                else:
                    #plc_tb_ctrl._debug(test_frame)
                    plc_tb_ctrl._debug("Unexpected frame: " + test_frame.head.cf)

            if (stop_time is not None) and time.time() > stop_time:
                if timeout_assert == False:
                    return result
                timeout_str = robot.utils.secs_to_timestr(timeout)
                timeout_error = '{0} timeout'.format(timeout_str)
                raise AssertionError(timeout_error)

        return result

if __name__ == '__main__':
    pass
