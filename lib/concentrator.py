import serial
import time
import robot
from formats import *
from construct import *
import binary_helper
import plc_tb_ctrl
import config


GDW1376P2_FRAME_HEAD_SIZE = gdw1376p2.gdw1376p2_head.sizeof()
GDW1376P2_FRAME_TAIL_SIZE = gdw1376p2.gdw1376p2_tail.sizeof()
DEFAULT_GDW1376P2_FRAME_TIMEOUT = 10
START_CHAR = '\x68'

def build_gdw1376p2_frame(dict_content = None, data_str = None, data_file = None):
    data = binary_helper.build(gdw1376p2.gdw1376p2.build, "fail to build gdw1376p2 frame", dict_content, data_file, data_str)
    if data is not None:
        cs = calc_gdw1376p2_cs8(data)
        frame_len = len(data)
        # update len and cs field
        data = gdw1376p2.gdw1376p2.parse(data)
        data.head.len = frame_len
        data.tail.cs = cs
        data = gdw1376p2.gdw1376p2.build(data)
    return data

def parse_gdw1376p2_frame(raw_data):
    return binary_helper.parse(gdw1376p2.gdw1376p2.parse, "fail to parse gdw1376p2 frame", raw_data)

# frame: entire gdw1376p2 frame
def calc_gdw1376p2_cs8(frame):
    cs = 0
    # remove frame head and tail
    data = frame[GDW1376P2_FRAME_HEAD_SIZE:(-1*GDW1376P2_FRAME_TAIL_SIZE)]
    for d in data:
        cs = (cs + ord(d)) & 0xFF

    return cs

def calc_gdw1376p2_dt(dt1, dt2):
    dt = dt2 * 8
    for i in range(8):
        if (0 != (dt1 & 1)):
            dt += i + 1
            break
        dt1 >>= 1

    return dt

class Concentrator(object):
    def __init__(self, portname=config.CONCENTRATOR_PORT):
        self.ser = serial.Serial()
        self.ser.port = portname
        self.frame = ''
        self.frame_total_len = 0
        self.mac_addr = '' # type: str

    def __del__(self):
        pass

    def open_port(self):
        self.ser.baudrate = config.CONCENTRATOR_BAUDRATE
        self.ser.parity = serial.PARITY_EVEN
        self.ser.timeout = 0
        self.ser.open()
        plc_tb_ctrl._debug('Open concentrator port')

    def close_port(self):
        plc_tb_ctrl._debug('Close concentrator port')
        self.ser.close()

    def clear_port_rx_buf(self):
        self.ser.reset_input_buffer()
        self.frame = ''
        self.frame_total_len = 0

    def send_frame(self, frame):
        plc_tb_ctrl._trace_byte_stream('DL GDW1376P2', frame)
        self.ser.write(frame)

    def read_gdw1376p2_frame_head(self, ser):
        if (len(self.frame) == 0):
            start_char = ser.read(1)
            if (len(start_char) < 1):
                return None

            if (START_CHAR != start_char):
                return None

            self.frame = start_char

        if (len(self.frame) >= 1) and (len(self.frame) < GDW1376P2_FRAME_HEAD_SIZE):
            remaining_head_len = GDW1376P2_FRAME_HEAD_SIZE - len(self.frame)
            temp = ser.read(remaining_head_len)
            self.frame += temp
            if len(temp) < remaining_head_len:
                return None
            self.update_gdw1376p2_frame_total_len()

    def update_gdw1376p2_frame_total_len(self):
        frame_head = self.frame
        self.frame_total_len = 0
        try:
            frame_head = gdw1376p2.gdw1376p2_head.parse(frame_head)
            self.frame_total_len = frame_head.len
        except Exception as e:
            plc_tb_ctrl._debug(e.message)
            plc_tb_ctrl._debug('invalid gdw1376p2 frame head')
            # find the new frame start position
            new_start = self.frame.find(START_CHAR, 1)
            if new_start > 0:
                self.frame = self.frame[new_start:]
                if (len(self.frame) >= GDW1376P2_FRAME_HEAD_SIZE):
                    self.update_gdw1376p2_frame_total_len()
            else:
                self.frame = ''

    def read_gdw1376p2_frame(self):
        result = None

        # receive frame head
        if (len(self.frame) < GDW1376P2_FRAME_HEAD_SIZE):
            self.read_gdw1376p2_frame_head(self.ser)

        # receive frame body and frame tail
        if (len(self.frame) >= GDW1376P2_FRAME_HEAD_SIZE) and (len(self.frame) < self.frame_total_len):
            remaining_payload_len = self.frame_total_len - len(self.frame)
            frame_body_tail = self.ser.read(remaining_payload_len)
            self.frame += frame_body_tail

        # check frame
        if (len(self.frame) >= GDW1376P2_FRAME_HEAD_SIZE) and (len(self.frame) == self.frame_total_len):
            try:
                frame = gdw1376p2.gdw1376p2.parse(self.frame)
                cs = calc_gdw1376p2_cs8(self.frame)
                assert frame.tail.cs == cs, "check sum error"
                result = frame
                plc_tb_ctrl._trace_byte_stream('UL GDW1376P2', self.frame)
                self.frame = ''
            except Exception as e:
                plc_tb_ctrl._debug(e.message)
                plc_tb_ctrl._debug("Invalid frame: [{}]".format(" ".join("{:02x}".format(ord(i)) for i in self.frame)))
                # find the new frame start position
                new_start = self.frame.find(START_CHAR, 1)
                if new_start > 0:
                    self.frame = self.frame[new_start:]
                    if (len(self.frame) >= GDW1376P2_FRAME_HEAD_SIZE):
                        self.update_gdw1376p2_frame_total_len()
                else:
                    self.frame = ''
        return result


    # timeout: wait for x seconds
    def wait_for_gdw1376p2_frame(self, dir = "UL", afn = None, dt1 = None, dt2 = None, timeout = None, tm_assert=True):
        if  afn is not None:
            afn = hex(afn)
        if dt1 is not None:
            dt1 = hex(dt1)
        if dt2 is not None:
            dt2 = hex(dt2)
        plc_tb_ctrl._debug('Wait for gdw1376p2 frame. DIR={}, AFN={},DT1={},DT2={}'.format(dir, afn, dt1, dt2))

        result = None
        if timeout is None:
            timeout = DEFAULT_GDW1376P2_FRAME_TIMEOUT
        timeout *= config.CLOCK_RATE
        stop_time = time.time() + timeout
        timeout_str = robot.utils.secs_to_timestr(timeout)
        timeout_error = '{0} timeout'.format(timeout_str)
        while result is None:
            frame = self.read_gdw1376p2_frame()
            if (frame is not None):
                if (dir is not None) and (frame.cf.dir != dir):
                    plc_tb_ctrl._debug("Exp dir: {}, Recv: {} ".format(dir, frame.cf.dir))
                    continue
                tmp = hex(frame.user_data.value.afn)
                if (afn is not None) and (tmp != afn):
                    plc_tb_ctrl._debug("Exp afn: {}, Recv: {} ".format(afn, frame.user_data.value.afn))
                    continue
                tmp = hex(frame.user_data.value.data.dt1)
                if (dt1 is not None) and (tmp != dt1):
                    plc_tb_ctrl._debug("Exp dt1: {}, Recv: {} ".format(dt1, frame.user_data.value.data.dt1))
                    continue
                tmp = hex(frame.user_data.value.data.dt2)
                if (dt2 is not None) and (tmp != dt2):
                    plc_tb_ctrl._debug("Exp dt2: {}, Recv: {} ".format(dt2, frame.user_data.value.data.dt2))
                    continue

                result = frame

            if time.time() > stop_time:
                if tm_assert is True:
                    raise AssertionError(timeout_error)
                else:
                    return None

        if result is not None:
            plc_tb_ctrl._debug('Received')

        return result



if __name__ == '__main__':
    pass
