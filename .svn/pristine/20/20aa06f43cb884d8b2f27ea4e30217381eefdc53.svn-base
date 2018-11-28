import serial
import time
from formats import *
from construct import *
import binary_helper
import plc_tb_ctrl
import config


# dlt645_07.dlt645_07_tail.sizeof() would trigger assertion, hardcode here
DLT645_07_FRAME_HEAD_SIZE = 10
DLT645_07_FRAME_TAIL_SIZE = dlt645_07.dlt645_07_tail.sizeof()
DEFAULT_METER_FRAME_TIMEOUT = 10
START_CHAR = '\x68'

def build_dlt645_frame_head(code, data_len, addr = None, dir = 'REQ_FRAME', reply_flag = "NORMAL_REPLY", more_flag = "NO_MORE_DATA"):
    if addr is None:
        addr = 'AA-AA-AA-AA-AA-AA'
    frame_head = dict(addr=addr, code=code, more_flag=more_flag, reply_flag=reply_flag, dir=dir, len=data_len)
    return dlt645_07.dlt645_07_head.build(frame_head)

def build_dlt645_frame_tail(cs):
    frame_tail = {"cs": cs}
    return dlt645_07.dlt645_07_tail.build(frame_tail)

def build_dlt645_07_frame(dict_content = None, data_str = None, data_file = None):
    data = binary_helper.build(dlt645_07.dlt645_07.build, "fail to build dlt645_07 frame", dict_content, data_file, data_str)
    if data is not None:
        cs = calc_dlt645_cs8(data)
        data = dlt645_07.dlt645_07.parse(data)
        data.tail.cs = cs
        data = dlt645_07.dlt645_07.build(data)
    return data

def parse_dlt645_07_frame(frame):
    parsed_data = None
    try:
        parsed_data = dlt645_07.dlt645_07.parse(frame)
    except Exception as e:
        plc_tb_ctrl._debug(e.message)

    return parsed_data

def calc_dlt645_07_frame_len(frame):
    frame_len = (DLT645_07_FRAME_HEAD_SIZE
                + frame.body.length
                + DLT645_07_FRAME_TAIL_SIZE)

    return frame_len

# frame: entire dlt645 frame
def calc_dlt645_cs8(frame):
    cs = 0
    # remove frame tail
    data = frame[:(-1*DLT645_07_FRAME_TAIL_SIZE)]
    for d in data:
        cs = (cs + ord(d)) & 0xFF

    return cs

class Meter(object):
    def __init__(self):
        self.ser = serial.Serial()
        self.frame = ''
        self.frame_total_len = 0

    def __del__(self):
        pass

    def open_port(self):
        self.ser.port = config.METER_PORT
        self.ser.baudrate = config.METER_BAUDRATE
        self.ser.parity = serial.PARITY_EVEN
        self.ser.timeout = 0
        self.ser.open()
        plc_tb_ctrl._debug('Open meter port')

    def close_port(self):
        plc_tb_ctrl._debug('Close meter port')
        self.ser.close()

    def clear_port_rx_buf(self):
        self.ser.reset_input_buffer()

    def send_frame(self, frame):
        self.ser.write(frame)
        plc_tb_ctrl._trace_byte_stream("send 645: ", frame)

    def read_dlt645_frame_head(self, ser):
        if (len(self.frame) == 0):
            start_char = ser.read(1)
            if (len(start_char) < 1):
                return None

            if (START_CHAR != start_char):
                #plc_tb_ctrl._debug('invalid dlt645 start char:{}'.format())
                return None

            self.frame = start_char

        if (len(self.frame) >= 1) and (len(self.frame) < DLT645_07_FRAME_HEAD_SIZE):
            remaining_head_len = DLT645_07_FRAME_HEAD_SIZE - len(self.frame)
            temp = ser.read(remaining_head_len)
            self.frame += temp
            if len(temp) < remaining_head_len:
                return None
            self.update_dlt645_frame_total_len()

    def update_dlt645_frame_total_len(self):
        frame_head = self.frame
        self.frame_total_len = 0
        try:
            frame_head = dlt645_07.dlt645_07_head.parse(frame_head)
            self.frame_total_len = frame_head.len + DLT645_07_FRAME_HEAD_SIZE + DLT645_07_FRAME_TAIL_SIZE
        except Exception as e:
            plc_tb_ctrl._debug(e.message)
            plc_tb_ctrl._debug('invalid dlt645 frame head')
            # find the new frame start position
            new_start = self.frame.find(START_CHAR, 1)
            if new_start > 0:
                self.frame = self.frame[new_start:]
                if (len(self.frame) >= DLT645_07_FRAME_HEAD_SIZE):
                    self.update_dlt645_frame_total_len()
            else:
                self.frame = ''


    def read_dlt645_07_frame(self):
        result = None

        # receive frame head
        if (len(self.frame) < DLT645_07_FRAME_HEAD_SIZE):
            self.read_dlt645_frame_head(self.ser)

        # receive frame body and frame tail
        if (len(self.frame) >= DLT645_07_FRAME_HEAD_SIZE) and (len(self.frame) < self.frame_total_len):
            remaining_payload_len = self.frame_total_len - len(self.frame)
            frame_body_tail = self.ser.read(remaining_payload_len)
            self.frame += frame_body_tail

        # check frame
        if (len(self.frame) >= DLT645_07_FRAME_HEAD_SIZE) and (len(self.frame) == self.frame_total_len):
            try:
                frame = dlt645_07.dlt645_07.parse(self.frame)
                cs = calc_dlt645_cs8(self.frame)
                assert frame.tail.cs == cs, "check sum error"
                result = frame
                self.frame = ''
            except:
                plc_tb_ctrl._debug("Invalid frame: [{}]".format(" ".join("{:02x}".format(ord(i)) for i in self.frame)))

                #for exception case,we beleive this is a 'bad' frame, so wait for next change to get a 'good' one
                #there are two types of req frame would be sent by STA, 645_97 or 645_07
                # find the new frame start position
                # new_start = self.frame.find(START_CHAR, 1)
                # if new_start > 0:
                #     self.frame = self.frame[new_start:]
                #     if (len(self.frame) >= DLT645_07_FRAME_HEAD_SIZE):
                #         self.update_dlt645_frame_total_len()
                # else:
                #     self.frame = ''
                self.frame = ''
        return result


    # timeout: wait for x seconds
    def wait_for_dlt645_frame(self, code = None, dir = None, reply_flag = None, more_flag = None, timeout = None):
        result = None
        if timeout is None:
            timeout = DEFAULT_METER_FRAME_TIMEOUT
        timeout *= config.CLOCK_RATE
        stop_time = time.time() + timeout
        while result is None:
            frame = self.read_dlt645_07_frame()
            if (frame is not None):
                if (code is not None) and (frame.head.code != code):
                    plc_tb_ctrl._debug("Exp code: {}, Recv: {} ".format(code, frame.head.code))
                    continue

                if (dir is not None) and (frame.head.dir != dir):
                    plc_tb_ctrl._debug("Exp dir: {}, Recv: {} ".format(dir, frame.head.dir))
                    continue

                if (reply_flag is not None) and (frame.head.reply_flag != reply_flag):
                    plc_tb_ctrl._debug("Exp reply_flag: {}, Recv: {} ".format(reply_flag, frame.head.reply_flag))
                    continue

                if (more_flag is not None) and (frame.head.more_flag != more_flag):
                    plc_tb_ctrl._debug("Exp more_flag: {}, Recv: {} ".format(more_flag, frame.head.more_flag))
                    continue

                result = frame

            if time.time() > stop_time:
                break

        return result



if __name__ == '__main__':
    pass
