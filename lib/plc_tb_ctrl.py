# -- coding: utf-8 --
import imp
import os.path
import string
import subprocess

import threading
import time
from struct import *

import robot
import yaml
from construct import *
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.running.context import EXECUTION_CONTEXTS

import concentrator
import config
import plc_packet_helper
import plc_tb_uart
import sitrace_logger
import test_frame_helper
import usb_relay

DEFAULT_WAIT_TIME = 10

SITRACE_LOG_START_FLAG = 0xFACE
LOG_ID_PRINTF = 0
LOG_ID_BYTE_DUMP = 1
LOG_ID_WORD_DUMP = 2
LOG_ID_DWORD_DUMP = 4
LOG_ID_BEACON_DL = 5
LOG_ID_INTERLAYER_MSG = 6
LOG_ID_MAC_FRAME_DL = 7
LOG_ID_INTERLAYER_MSG_RX = 8
LOG_ID_MM_DL = 9
LOG_ID_COMMAND = 10
LOG_ID_MAC_FRAME_UL = 11
LOG_ID_BEACON_UL = 12
LOG_ID_MM_UL = 13
LOG_ID_APL_UL = 14
LOG_ID_APL_DL = 15
LOG_ID_CLI_CMD = 16
LOG_ID_MAC_LOG_CHAN_QUALITY = 0x301
LOG_ID_TEST_FRAME_UL = 0xB00
LOG_ID_TEST_FRAME_DL = 0xB01
LOG_ID_TIMESTAMP = 0x701

BC_MSDU_RETRANS_NUM = 3

RST_CHANNEL=3
EVENT_CHANNEL=4

def _debug(s):
    logger.info(s)
    _trace_printf(str(s))

curr_tc_name = ''
curr_tc_dir = ''
output_dir = ''

COMMON_DATA_PATH = u'./tc/common_data'

def _write_log_file(log_id, log_data):
    curr_time = time.time()
    # second to microsecond, then to 1.28us/tick
    curr_time = int(round(curr_time * 1000000 / 1.28)) & 0xFFFFFFFF
    data = pack('HHBBHL', SITRACE_LOG_START_FLAG, log_id, 0, 0, len(log_data), curr_time) + log_data
    if TB_INSTANCE is not None:
        assert isinstance(TB_INSTANCE, PlcSystemTestbench)
        if TB_INSTANCE.detail_log_file is not None:
            TB_INSTANCE.detail_log_file.write(data)
        #TB_INSTANCE.detail_log_file.flush()

def _trace_printf(s):
    if isinstance(s, unicode):
        s = str(s)
    log_data = s + '\x00'
    _write_log_file(LOG_ID_PRINTF, log_data)

def _trace_test_frame_ul(test_frame):
    _write_log_file(LOG_ID_TEST_FRAME_UL, test_frame)

def _trace_test_frame_dl(test_frame):
    _write_log_file(LOG_ID_TEST_FRAME_DL, test_frame)

def _trace_beacon_ul(beacon):
    _write_log_file(LOG_ID_BEACON_UL, beacon)

def _trace_beacon_dl(beacon):
    _write_log_file(LOG_ID_BEACON_DL, beacon)

def _trace_nmm_ul(nmm):
    _write_log_file(LOG_ID_MM_UL, nmm)

def _trace_nmm_dl(nmm):
    _write_log_file(LOG_ID_MM_DL, nmm)

def _trace_apm_ul(apm):
    _write_log_file(LOG_ID_APL_UL, apm)

def _trace_apm_dl(apm):
    _write_log_file(LOG_ID_APL_DL, apm)

def _trace_mac_frame_ul(mac_frame):
    _write_log_file(LOG_ID_MAC_FRAME_UL, mac_frame)

def _trace_mac_frame_dl(mac_frame):
    _write_log_file(LOG_ID_MAC_FRAME_DL, mac_frame)

def _trace_byte_stream(desc, byte_stream):
    _trace_printf("{}: [{}]".format(desc, " ".join("{:02x}".format(ord(i)) for i in byte_stream)))

def _trace_timestamp():
    curr_time = time.localtime()
    trc_timestamp_data = pack("HBBBBBB", curr_time.tm_year, curr_time.tm_mon,
                              curr_time.tm_mday, curr_time.tm_hour, curr_time.tm_min,
                              curr_time.tm_sec, 0)

    _write_log_file(LOG_ID_TIMESTAMP, trc_timestamp_data)


def _wait_until(wait_start_hint, function, wait_time = None, *args):
    if wait_time is None:
        wait_time = DEFAULT_WAIT_TIME
    wait_time *= config.CLOCK_RATE
    stop_time = time.time() + wait_time
    timeout_str = robot.utils.secs_to_timestr(wait_time)
    timeout_error = '{0} timeout'.format(timeout_str)

    _debug(wait_start_hint)
    while True:
        result = function(*args)
        if result is not None:
            _debug('Wait end')
            return result

        if time.time() > stop_time:
            raise AssertionError(timeout_error)

def record_test_status():
    tc_msg = BuiltIn().get_variable_value('${TEST MESSAGE}')
    if tc_msg.strip() != '':
        _trace_printf(tc_msg)
    _trace_printf('TC {} {}'.format(BuiltIn().get_variable_value('${TEST NAME}'), BuiltIn().get_variable_value('${TEST STATUS}')))

    #time.sleep(5)

    assert isinstance(TB_INSTANCE, PlcSystemTestbench), "not PlcSystemTestbench instance"

    _debug('begin 5 seconds waiting before exit...')

    # log可能比较多，还没有及时传给SiTrace，多等一会儿再关闭SiTrace
    time.sleep(5)

    if config.AUTO_LOG:
        TB_INSTANCE._stop_dut_logging()
        TB_INSTANCE._stop_tb_logging()

    # 确保sitrace已关闭，串口已释放
    time.sleep(1)

    TB_INSTANCE._stop_detail_logging()

def init_test():
    assert isinstance(TB_INSTANCE, PlcSystemTestbench), "not PlcSystemTestbench instance"

    TB_INSTANCE._start_detail_logging()

    if config.PHY_AUTO_TEST:
        # make DUT exit test mode
        logger = sitrace_logger.SitraceLogger(True)
        logger.open_port()
        logger.send_cli_cmd("ptst 0 0 0")
        logger.close_port()

    if config.AUTO_LOG:
        TB_INSTANCE._start_dut_logging()
        TB_INSTANCE._start_tb_logging()

    if config.AUTO_RESET:
        # reset DUT
        _debug('Reset DUT')
        if config.DEVICE == "Cortex-M3":
            subprocess.call([config.JLINK_PATH,
                            "-Device",config.DEVICE,
                            "-SelectEmuBySN", config.DUT_JLINK_SN,
                            "-CommanderScript", "jlink_command.txt"])
        else:
            TB_INSTANCE.reset_dut()
            '''
            dut_reset = serial.Serial(config.TB_RESET_PORT,config.TB_RESET_BAUDRATE)
            dut_reset.write('\xA0\x01\x01\xA2')
            time.sleep( 0.2 )
            dut_reset.write('\xA0\x01\x00\xA1')
            '''


    # reset TB
    '''
    _debug('Reset TB')
    subprocess.call([config.JLINK_PATH,
                     "-Device", config.DEVICE,
                     "-SelectEmuBySN", config.TB_JLINK_SN,
                     "-CommanderScript", "jlink_command.txt"])
    time.sleep(2)
    '''

    TB_INSTANCE.set_event_low()

    # TODO: bootloader2 tasks more time to boot
    time.sleep(5)


def __close__(hwnd, pid):
        """
        EnumWindows callback - sends WM_CLOSE to any window
        owned by this process.
        """
        tid, curr_pid = win32process.GetWindowThreadProcessId(hwnd)
        if curr_pid == pid:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

def terminate_process(process):
    process.terminate()
    #win32gui.EnumWindows(__close__, process.pid)

class PlcSystemTestbench(object):
    # only one instance
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        global TB_INSTANCE
        TB_INSTANCE = self

        self.tb_uart = plc_tb_uart.PlcTestbenchUart()
        self._create_log_file()
        self.exp_timer = None
        self._init_param()
        self.usb_relay_device = usb_relay.UsbRelay()
        self.usb_relay_device.init_device(None)

    def _init_param(self):
        self.phase = 1
        self.sta_tei = 1
        self.proxy_tei = 0
        self.msdu_sn = 0
        self.test_frame_sn = 0
        self.mac_head = Container(org_src_tei=1,ver=0,tx_type="PLC_MAC_UNICAST",
            org_dst_tei=0, tx_times_limit=1, msdu_sn=self.msdu_sn,
            msdu_type="PLC_MSDU_TYPE_NMM",proxy_enabled=0,reset_times=0,
            msdu_len=0,remaining_hop_count=1,hop_limit=1,
            mac_addr_flag=0,route_fix_flag=0,broadcast_dir=0,
            nw_org_sn=0,src_mac_addr="",dst_mac_addr=""
            )
        self.fc = Container(nid=0,network_type=0,mpdu_type="PLC_MPDU_SOF",
            var_region_ver=None,crc=0)

    def __del__(self):
        pass

    def run_test(self, tc_name, run_times=1, tc_path=u'./'):
        assert isinstance(tc_name, unicode), 'tc_name should be unicode'
        assert isinstance(run_times, int), 'run_times should be int'

        global curr_tc_name
        global curr_tc_dir

        _trace_printf('===================')
        _trace_printf(tc_name)
        _trace_printf('===================')


        self.tb_uart.close_tb_test_port()
        self.tb_uart.open_tb_test_port()

        self._init_param()
        self._deactivate_tb()

        tc_file_name = tc_name + '.py'
        tc_file_full_path = None
        dst_dir = "plc_system_test"
        s1 = os.getcwd()
        indextmp = string.index(s1, dst_dir)
        indextmp += len(dst_dir) + 1
        tc_path = s1[:indextmp]
        if tc_path[-1] != r'\\':
            tc_path += r"\\"
        _debug(tc_path)
        for dirpath, dirs, files in os.walk(tc_path + u'tc'):
            if tc_file_name in files:
                tc_file_full_path = os.path.join(dirpath, tc_file_name)
                break

        assert tc_file_full_path is not None, '{} not found'.format(tc_name)
        curr_tc_name = tc_name
        curr_tc_dir = dirpath
        tc = imp.load_source(tc_name, tc_file_full_path)

        tc.run(self)

    def run_iot_test(self, tc_name, run_times=1, tc_path=u'./'):
        assert isinstance(tc_name, unicode), 'tc_name should be unicode'
        assert isinstance(run_times, int), 'run_times should be int'

        self.cct = concentrator.Concentrator()
        self.cct.open_port()

        global curr_tc_name
        global curr_tc_dir

        _trace_printf('===================')
        _trace_printf(tc_name)
        _trace_printf('===================')

        self._init_param()
        self.meter_platform_power_determind_reset()
        # 默认情况下关闭陪测cco
        self.meter_platform_power_escort(0)
        tc_file_name = tc_name + '.py'
        tc_file_full_path = None
        dst_dir = "plc_system_test"
        s1 = os.getcwd()
        indextmp = string.index(s1, dst_dir)
        indextmp += len(dst_dir) + 1
        tc_path = s1[:indextmp]
        if tc_path[-1] != r'\\':
           tc_path += r'\\'
        _debug(tc_path)
        for dirpath, dirs, files in os.walk(tc_path + u'tc'):
            if tc_file_name in files:
                tc_file_full_path = os.path.join(dirpath, tc_file_name)
                break

        assert tc_file_full_path is not None, '{} not found'.format(tc_name)
        curr_tc_name = tc_name
        curr_tc_dir = dirpath
        tc = imp.load_source(tc_name, tc_file_full_path)

        band = BuiltIn().get_variable_value("${band}")
        band = band.split(',')
        net = BuiltIn().get_variable_value("${net}")
        if  config.IOT_TOP_LIST_ALL.__contains__(net) == False:
            tmp = '_' + net + ".txt"
            config.IOT_TOP_LIST_ALL += tmp
            config.IOT_TOP_LIST_PROXY += tmp
            config.IOT_TOP_LIST_DYNATIC += tmp
            config.IOT_TOP_LIST_STATIC += tmp
            config.IOT_TOP_LIST_DETERMINAND += tmp
            config.IOT_TOP_LIST_ESCORT += tmp

        # 执行用例
        for b in band:
            tc.run(self, b)

    def _init_uart(self, dev_port_baudrate):
        self.tb_uart.open_tb_test_port()

    def _deinit_uart(self):
        self.tb_uart.close_tb_test_port()

    def _gen_msdu_sn(self):
        self.msdu_sn += 1
        return self.msdu_sn

    def _reset_msdu_sn(self):
        self.msdu_sn = 0

    def _test_send_nmm(self):
        self.fc.var_region_ver = Container(lid=1,dst_tei=10,src_tei=1,
            pb_num=1, frame_len=10, tmi_b=0,encrypt_flag=0,
            retrans_flag=0,broadcast_flag=0,symbol_num=10,
            ver=0,tmi_e=0)
        self._send_nmm("assoc_req.yaml", self.mac_head, self.fc, 520)

    # mac_head: plc_mac_frame_head dictionary
    # fc: plc_mpdu_fc dictionary
    def _send_nmm(self, nmm_fn, mac_head, src_tei, dst_tei, tmi_b=None, tmi_e=None, pb_num=None, ack_needed=True, encrypt_flag=0,
        retrans_flag=0, broadcast_flag=0):

        msdu = plc_packet_helper.build_nmm(data_file = nmm_fn)
        mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"
        self._send_msdu(msdu, mac_head, src_tei, dst_tei, tmi_b=tmi_b, tmi_e=tmi_e, pb_num=pb_num, ack_needed=ack_needed, encrypt_flag=encrypt_flag,
            retrans_flag=retrans_flag, broadcast_flag=broadcast_flag,auto_retrans=False)


    def _send_plc_apm(self, apm_fn, mac_head, src_tei, dst_tei, is_dl=True, tmi_b=None, tmi_e=None, pb_num=None, ack_needed=True, encrypt_flag=0,
        retrans_flag=0, broadcast_flag=0):

        msdu = plc_packet_helper.build_apm(data_file=apm_fn, is_dl=is_dl)
        mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
        self._send_msdu(msdu, mac_head, src_tei, dst_tei, tmi_b=tmi_b, tmi_e=tmi_e, pb_num=pb_num, ack_needed=ack_needed, encrypt_flag=encrypt_flag,
            retrans_flag=retrans_flag, broadcast_flag=broadcast_flag)


    #add a parameter sn. In some case, we need to simulate a relayed packet and we hope the SN should not be changed
    def _send_msdu(self, msdu, mac_head, src_tei, dst_tei, tmi_b=None, tmi_e=None, pb_num=None, ack_needed=True, encrypt_flag=0,
                   retrans_flag=0, broadcast_flag=0, tx_time=0xFFFFFFFF, sn=None, auto_retrans=True):

        tx_cnt = 0
        if (auto_retrans):
            max_tx_times = BC_MSDU_RETRANS_NUM
        else:
            max_tx_times = 1


        mac_head.msdu_len = len(msdu)
        mac_head.msdu_sn = sn if sn is not None else self._gen_msdu_sn()
        mac_head = plc_packet_helper.build_mac_frame_head(dict_content = mac_head)
        crc = plc_packet_helper.calc_crc32(msdu)
        mac_frame = mac_head + msdu + plc_packet_helper.build_mac_frame_crc(crc)

        if (tmi_b is None) and (tmi_e is None):
            self._gen_sof_fc(len(mac_frame), ack_needed, 0, dst_tei, src_tei, encrypt_flag, retrans_flag, broadcast_flag)

        else:
            if (tmi_b is not None) and (tmi_b <= plc_packet_helper.MAX_TMI_BASIC):
                tmi_e = 0

            elif (tmi_e is not None) and (tmi_e <= plc_packet_helper.MAX_TMI_EXT):
                tmi_b = plc_packet_helper.MAX_TMI_BASIC + 1
            else:
                raise AssertionError('invalid tmi_b/tmi_e')

            self._set_sof_fc(ack_needed=ack_needed, lid=0, dst_tei=dst_tei, src_tei=src_tei, pb_num=pb_num, tmi_b=tmi_b, encrypt_flag=encrypt_flag,
                retrans_flag=retrans_flag, broadcast_flag=broadcast_flag, tmi_e=tmi_e)

        pb_size = plc_packet_helper.query_pb_size_by_tmi(self.fc.var_region_ver.tmi_b, self.fc.var_region_ver.tmi_e)

        while (tx_cnt < max_tx_times):
            if (0 == broadcast_flag):
                if 0 == tx_cnt:
                    self.fc.var_region_ver.retrans_flag = 0
                else:
                    self.fc.var_region_ver.retrans_flag = 1

            self._send_mac_frame(mac_frame, self.fc, pb_size, tx_time)
            tx_cnt += 1

            if auto_retrans:
                #we can't wait any msg here, because it may filter messages client need
                _debug('wait for TX_COMPLETE_IND_s')
                test_frame = self.tb_uart.wait_for_test_frame("TX_COMPLETE_IND")
                assert test_frame is not None, 'TX_COMPLETE_IND Timeout'

                if ((0 == broadcast_flag)
                        and ack_needed):

                    result = self._wait_for_sack(timeout=0.1,
                                               timeout_cb=lambda:None,
                                               content_checker=lambda sack_fc: (sack_fc.nid==self.fc.nid)
                                                                               and (sack_fc.var_region_ver.dst_tei==self.fc.var_region_ver.src_tei)
                                                                               and (sack_fc.var_region_ver.src_tei==self.fc.var_region_ver.dst_tei))
                    if result is not None:
                        [sack_time, sack_fc] = result
                        if (0 == sack_fc.var_region_ver.rx_result):
                            break


    # mac_frame: raw data
    def _send_mac_frame(self, mac_frame, fc, pb_size, tx_time=0xFFFFFFFF):
        _trace_mac_frame_ul(mac_frame)
        pb_num = fc.var_region_ver.pb_num
        fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
        if fc is not None:
            fc_pl_data = fc + plc_packet_helper.construct_sof(pb_num, pb_size, mac_frame)
            self._send_fc_pl_data(dict(timestamp=tx_time, pb_size=pb_size, pb_num=pb_num, phase=self.phase, payload=dict(data=fc_pl_data)))

    def _activate_tb(self, fn):
        result = test_frame_helper.build_activate_req(data_file = fn)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        test_frame = self.tb_uart.wait_for_test_frame("ACTIVATE_CNF_CMD")
        assert test_frame is not None, 'ACTIVATE_CNF Timeout'
        assert test_frame.payload.error_code == "ACT_NO_ERROR", 'Wrong error_code {}'.format(test_frame.payload.error_code)

    def _change_band(self, band, tonemask=plc_packet_helper.TONEMASK_INVALID):
        result = test_frame_helper.build_band_config_req(
            dict_content={'band': band,
                          'tonemask': tonemask
            })
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        test_frame = self.tb_uart.wait_for_test_frame("BAND_CONFIG_CNF_CMD")
        assert test_frame is not None, 'BAND_CONFIG_CNF Timeout'
        self._init_band_param(band, tonemask)

    def _deactivate_tb(self):
        result = test_frame_helper.build_deactivate_req()
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        test_frame = self.tb_uart.wait_for_test_frame("DEACTIVATE_CNF_CMD")
        assert test_frame is not None
        #assert test_frame.payload.error_code == "DEACT_NO_ERROR"

    def _read_tb_time(self):
        result = test_frame_helper.build_time_read_req()
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        test_frame = self.tb_uart.wait_for_test_frame("TIME_READ_CNF_CMD")
        assert test_frame is not None
        return test_frame.payload.timestamp

    # configure TB to send beacon
    # fn: data filename
    # return: beacon period start time
    def _configure_beacon(self, fn = None, dict_content = None, update_beacon=False):
        assert (fn == None and dict_content != None) or (fn != None and dict_content == None)

        if fn is not None:
            msg = self._load_data_file(fn)
        else:
            msg = dict_content

        if not update_beacon:
            curr_time = self._read_tb_time()
            tx_time = plc_packet_helper.ntb_add(curr_time, plc_packet_helper.ms_to_ntb(1000))
        else:
            tx_time = 0

        msg['tx_time'] = tx_time
        msg['fc']['var_region_ver']['timestamp'] = tx_time
        msg['payload']['value']['beacon_info']['beacon_item_list'][2]['beacon_item']['beacon_period_start_time'] = tx_time

        result = test_frame_helper.build_beacon_data(dict_content = msg)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        return tx_time

    def _configure_proxy(self, fn):
        result = test_frame_helper.build_time_config_req(data_file=fn)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        test_frame = self.tb_uart.wait_for_test_frame("TIME_CONFIG_CNF_CMD", timeout=30)
        assert test_frame is not None
        return test_frame.payload.timestamp

    def _configure_nw_static_para(self, nid, nw_org_sn):
        '''
        Configure static network paramemters for data transmission
        '''
        self.fc.nid = nid
        self.mac_head.nw_org_sn = nw_org_sn

    def _send_ncf(self, nid, phase, duration, offset, neigh_nid):
        ncf_fc = dict(nid=nid, network_type=0, mpdu_type="PLC_MPDU_NCF", var_region_ver=dict(duration=duration, offset=offset, neigh_nid=neigh_nid, ver=0), crc=0)
        ncf_fc = plc_packet_helper.build_mpdu_fc(dict_content = ncf_fc)
        if ncf_fc is not None:
            self._send_fc_pl_data(dict(timestamp=0xFFFFFFFF, pb_size=0, pb_num=0, phase=phase, payload=dict(data=ncf_fc)))

    # data: fc_pl_data dictionary
    def _send_fc_pl_data(self, data):
        result = test_frame_helper.build_fc_pl_data(dict_content=data)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)

    # data: fc_pl_data dictionary
    def _send_periodic_fc_pl_data(self, data):
        result = test_frame_helper.build_periodic_fc_pl_data(dict_content = data)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)

    @staticmethod
    def _load_data_file(data_file):
        msg = None
        data_file_full_path = os.path.join(curr_tc_dir, data_file)
        if not os.path.exists(data_file_full_path):
            data_file_full_path = os.path.join(COMMON_DATA_PATH, data_file)

        assert os.path.exists(data_file_full_path), '{} not found'.format(data_file_full_path)
        f = open(data_file_full_path)
        data = f.read()
        f.close()
        msg = yaml.load(data)
        return msg

    def _wait_for_fc_pl_data(self, fc_pl_checker=None, timeout=None, timeout_cb=None, *args):
        if timeout is None:
            timeout = plc_tb_uart.DEFAULT_TEST_FRAME_TIMEOUT
        timeout *= config.CLOCK_RATE
        stop_time = time.time() + timeout
        timeout_str = robot.utils.secs_to_timestr(timeout)
        timeout_error = '{0} timeout'.format(timeout_str)
        result = None

        while (result is None):
            timeout = stop_time - time.time()
            try:
                #_debug('trying to get a test frame:{}'.format(timeout))
                #timeout will be multiplied by 2 inside of wait_for_test_frame, so we have to divide it firstly
                test_frame = self.tb_uart.wait_for_test_frame(cf = "FC_PL_DATA", timeout = timeout/float(config.CLOCK_RATE))
                #time.sleep(1)

            except Exception as e:
                _debug("wait for test frame error msg: " + e.message)
                _debug(timeout_error)
                if (timeout_cb is None):
                    raise AssertionError(timeout_error)
                else:
                    timeout_cb()
                    return None


            if fc_pl_checker is not None:
                result = fc_pl_checker(test_frame.payload, *args)
            else:
                result = test_frame.payload

        return result

#         beacon_payload = None
#         result = None
#         while result is None:
#             try:
#                 test_frame = None
#                 test_frame = self.tb_uart.wait_for_test_frame(cf="FC_PL_DATA", timeout=0)
#
#             except:
#                 pass
#
#             if test_frame is not None:
#                 if fc_pl_checker is not None:
#                     result = fc_pl_checker(test_frame.payload, *args)
#                 else:
#                     result = test_frame.payload
#
#             if time.time() > stop_time:
#                 if (timeout_cb is None):
#                     raise AssertionError(timeout_error)
#                 else:
#                     timeout_cb()
#                     break
#         return result


    def _check_plc_beacon_fc_payload(self, fc_pl_data_payload, content_checker=None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [fc, beacon_payload]
        '''

        fc_pl_data = fc_pl_data_payload.payload.data
        beacon_payload = None
        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)
        if (fc is not None) and ("PLC_MPDU_BEACON" == fc.mpdu_type):
            pb_size = fc_pl_data_payload.pb_size
            beacon_payload = plc_packet_helper.get_beacon_payload(fc_pl_data_payload.pb_num, pb_size, fc_pl_data[16:(16+pb_size)])

        if beacon_payload is None:
            return None

        if content_checker is not None:
            result = content_checker(fc, beacon_payload)
            if not result:
                return None

        return [fc_pl_data_payload.timestamp, fc, beacon_payload]

    def _check_fc_pl_payload(self, fc_pl_data_payload):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [timestamp, fc, beacon_payload/mac_frame]
        '''

        fc_pl_data = fc_pl_data_payload.payload.data
        beacon_payload = None
        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)
        result = None
        if (fc is None):
            return None

        if  ("PLC_MPDU_BEACON" == fc.mpdu_type):
            pb_size = fc_pl_data_payload.pb_size
            beacon_payload = plc_packet_helper.get_beacon_payload(fc_pl_data_payload.pb_num, pb_size, fc_pl_data[16:(16+pb_size)])
            if beacon_payload is not None:
                result = [fc_pl_data_payload.timestamp, fc, beacon_payload]

        elif ("PLC_MPDU_SOF" == fc.mpdu_type):
            pb_size = fc_pl_data_payload.pb_size
            pb_num = fc_pl_data_payload.pb_num
            mac_frame = plc_packet_helper.reassemble_mac_frame(pb_num, pb_size, fc_pl_data[16:(16+pb_size*pb_num)])

            if mac_frame is None:
                return None

            valid = plc_packet_helper.check_mac_frame_crc(mac_frame)
            if not valid:
                _debug('Invalid mac frame crc')
                return None

            result = [fc_pl_data_payload.timestamp, fc, mac_frame]
        elif "PLC_MPDU_SACK" == fc.mpdu_type:
            result = [fc_pl_data_payload.timestamp, fc,None]
        elif "PLC_MPDU_NCF" == fc.mpdu_type:
            result = [fc_pl_data_payload.timestamp, fc,None]

        return result

     # wait for beacon
    def _wait_for_plc_beacon(self, timeout = None, timeout_cb = None, content_checker=None):
        _debug('Wait for beacon')
        beacon = self._wait_for_fc_pl_data(self._check_plc_beacon_fc_payload, timeout, timeout_cb, content_checker)
        _debug('Beacon received')

        return beacon

     # wait for sack
    def _wait_for_sack(self, timeout=None, timeout_cb=None, content_checker=None):
        _debug('Wait for sack')
        sack = self._wait_for_fc_pl_data(self._check_plc_fc_sack, timeout, timeout_cb, content_checker)
        if sack is not None:
            _debug('sack received')
        else:
            _debug('sack not received')

        return sack

     # wait for NCF
    def _wait_for_plc_ncf(self, timeout = None, timeout_cb = None, content_checker=None):
        _debug('Wait for ncf')
        ncf = self._wait_for_fc_pl_data(self._check_plc_fc_ncf, timeout, timeout_cb, content_checker)
        _debug('Ncf received')

        return ncf

    def _check_plc_fc_sack(self, fc_pl_data_payload, content_checker=None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [timestamp, fc]
        '''

        fc_pl_data = fc_pl_data_payload.payload.data
        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)
        if (fc is None) or ("PLC_MPDU_SACK" != fc.mpdu_type):
            return None

        if content_checker is not None:
            result = content_checker(fc)
            if not result:
                return None

        return [fc_pl_data_payload.timestamp, fc]

    def _check_plc_fc_ncf(self, fc_pl_data_payload, content_checker=None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [timestamp, fc]
        '''

        fc_pl_data = fc_pl_data_payload.payload.data
        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)
        if (fc is None) or ("PLC_MPDU_NCF" != fc.mpdu_type):
            return None

        if content_checker is not None:
            result = content_checker(fc)
            if not result:
                return None

        return [fc_pl_data_payload.timestamp, fc]

    def _check_plc_nmm(self, fc_pl_data_payload, mmtype=None, with_timestamp=False):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [fc, mac_frame.head, nmm]
        '''

        fc_pl_data = fc_pl_data_payload.payload.data
        pb_size = fc_pl_data_payload.pb_size
        pb_num = fc_pl_data_payload.pb_num

        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)
        mac_frame = None
        if (fc is not None) and ("PLC_MPDU_SOF" == fc.mpdu_type):
            mac_frame = plc_packet_helper.reassemble_mac_frame(pb_num, pb_size, fc_pl_data[16:(16+pb_size*pb_num)])

        if mac_frame is None:
            return None

        valid = plc_packet_helper.check_mac_frame_crc(mac_frame)
        if not valid:
            _debug('Invalid mac frame crc')
            return None

        if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_NMM":
            _debug('Unexpected msdu type')
            return None

        nmm = mac_frame.msdu.value
        #if (mmtype is not None) and (mmtype != nmm.header.mmtype):
        if (mmtype is not None) and not (nmm.header.mmtype in mmtype):
            _debug('Unexpected nmm type:{}'.format(nmm.header.mmtype))
            return None
        if with_timestamp:
            return [fc_pl_data_payload.timestamp, fc, mac_frame.head, nmm]
        else:
            return [fc, mac_frame.head, nmm]


    # wait for specific network management message
    def _wait_for_plc_nmm(self, mmtype=None, timeout=None, timeout_cb=None, with_timestamp=False):
        if mmtype is None:
            _debug('Wait for network management message')
        else:
            _debug('Wait for network management message {}'.format(mmtype))

        result = self._wait_for_fc_pl_data(self._check_plc_nmm, timeout, timeout_cb, mmtype, with_timestamp)

        if result is None:
            _debug('message was not received')
        else:
            _debug('message received')
        return result

    def _check_plc_apm(self, fc_pl_data_payload, msg_id=None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [fc, mac_frame.head, apm]
        '''
        none_result = None

        fc_pl_data = fc_pl_data_payload.payload.data
        pb_size = fc_pl_data_payload.pb_size
        pb_num = fc_pl_data_payload.pb_num

        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)

        mac_frame = None
        if (fc is not None) and ("PLC_MPDU_SOF" == fc.mpdu_type):
            mac_frame = plc_packet_helper.reassemble_mac_frame(pb_num, pb_size, fc_pl_data[16:(16+pb_size*pb_num)])

        if mac_frame is None:
            _debug("mac_frame= None")
            return none_result

        valid = plc_packet_helper.check_mac_frame_crc(mac_frame)
        if not valid:
            _debug("msdu crc error")
            return none_result

        if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_APP":
            _debug("msdu_type not matched: expected=PLC_MSDU_TYPE_APP pkt, actual={}".format(mac_frame.head.msdu_type))
            return none_result

        apm = mac_frame.msdu.value

        if (msg_id is not None) and (msg_id != apm.header.id):
            _debug("msg_id not matched: expected={} actual={}".format(msg_id, apm.header.id))
            return none_result

        return [fc, mac_frame.head, apm]

    def _check_plc_apm_new(self, fc_pl_data_payload, is_dl=True, msg_id=None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [timestamp, fc, mac_frame.head, apm]
        '''
        none_result = None


        if fc_pl_data_payload is None:
            return none_result

        fc_pl_data = fc_pl_data_payload.payload.data
        pb_size = fc_pl_data_payload.pb_size
        pb_num = fc_pl_data_payload.pb_num

        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)
        mac_frame = None
        if (fc is not None) and ("PLC_MPDU_SOF" == fc.mpdu_type):
            mac_frame = plc_packet_helper.reassemble_mac_frame(pb_num, pb_size, fc_pl_data[16:(16+pb_size*pb_num)])

        if mac_frame is None:
            _debug("mac_frame= None")
            return none_result

        valid = plc_packet_helper.check_mac_frame_crc(mac_frame)
        if not valid:
            _debug("msdu crc error")
            return none_result

        if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_APP":
            _debug("msdu_type not matched: expected=PLC_MSDU_TYPE_APP pkt, actual={}".format(mac_frame.head.msdu_type))
            return none_result

        apm_data = mac_frame.msdu.data
        apm = plc_packet_helper.parse_apm(apm_data, is_dl)
        if (msg_id is not None) and (msg_id != apm.header.id):
            _debug("msg_id not matched: expected={} actual={}".format(msg_id, apm.header.id))
            return none_result

        return [fc_pl_data_payload.timestamp, fc, mac_frame.head, apm]

    def _check_plc_apm_dl(self, fc_pl_data_payload, msg_id=None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [timstmap, fc, mac_frame.head, apm_dl]
        '''
        return self._check_plc_apm_new(fc_pl_data_payload, True, msg_id)

    def _check_plc_apm_ul(self, fc_pl_data_payload, msg_id=None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [timestamp, fc, mac_frame.head, apm_ul]
        '''
        return self._check_plc_apm_new(fc_pl_data_payload, False, msg_id)


    # wait for specific application message
    def _wait_for_plc_apm(self, msg_id = None, timeout = None,timeout_cb = None):
        none_result = [None, None, None]

        if msg_id is None:
            _debug('Wait for application message')
        else:
            _debug('Wait for application message {}'.format(msg_id))

        result = self._wait_for_fc_pl_data(self._check_plc_apm, timeout,timeout_cb, msg_id)

        if result == None:
            result = none_result
            _debug('message is not received')
        else:
            _debug('message is received')

        return result

    # wait for specific DL application message
    def _wait_for_plc_apm_dl(self, msg_id = None, timeout=None, timeout_cb=None):
        none_result = [None, None, None, None]

        if msg_id is None:
            _debug('Wait for DL application message')
        else:
            _debug('Wait for DL application message {}'.format(msg_id))

        result = self._wait_for_fc_pl_data(self._check_plc_apm_dl, timeout, timeout_cb, msg_id)
        if result == None:
            result = none_result
            _debug('message is not received')
        else:
            _debug('message is received')
        return result

    # wait for specific UL application message
    def _wait_for_plc_apm_ul(self, msg_id = None, timeout = None,timeout_cb = None):
        none_result = [None, None, None, None]

        if msg_id is None:
            _debug('Wait for UL application message')
        else:
            _debug('Wait for UL application message {}'.format(msg_id))

        result = self._wait_for_fc_pl_data(self._check_plc_apm_ul, timeout, timeout_cb, msg_id)
        if result == None:
            result = none_result
            _debug('message is not received')
        else:
            _debug('message is received')
        return result

    def _create_log_file(self):
        global output_dir

        if EXECUTION_CONTEXTS.current is not None:
            output_file = BuiltIn().get_variable_value('${OUTPUT FILE}')
            (output_dir, output_filename) = os.path.split(output_file)
            (output_filename, ext) = os.path.splitext(output_filename)
            output_dir = os.path.join(output_dir, output_filename)
            # create output folder
            os.mkdir(output_dir)
        else:
            output_dir = ''

        #timestamp_str = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #filename = 'detail_log_' + timestamp_str + '.st'
        #file_path = os.path.join(output_dir, filename)
        #self.detail_log_file = open(file_path, 'wb')
        self.detail_log_file = None
        self.output_dir = output_dir

    def _start_dut_logging(self):
        _debug('start DUT logging')
        if EXECUTION_CONTEXTS.current is not None:
            test_name = BuiltIn().get_variable_value('${TEST NAME}')
        else:
            test_name = ''
        log_filename = 'dut_' + test_name + '.st'
        log_filename = os.path.join(output_dir, log_filename)
        self.dut_log = subprocess.Popen([config.SITRACE_PATH,
                                        "port={},{},n,8,1".format(config.DUT_SITRACE_PORT,
                                                                  config.DUT_SITRACE_BAUDRATE),
                                        "file={}".format(log_filename)])

    def _stop_dut_logging(self):
        _debug('stop DUT logging')
        terminate_process(self.dut_log)
        del self.dut_log

    def _start_tb_logging(self):
        _debug('start TB logging')
        if EXECUTION_CONTEXTS.current is not None:
            test_name = BuiltIn().get_variable_value('${TEST NAME}')
        else:
            test_name = ''
        log_filename = 'tb_' + test_name + '.st'
        log_filename = os.path.join(output_dir, log_filename)
        self.tb_log = subprocess.Popen([config.SITRACE_PATH,
                                        "port={},{},n,8,1".format(config.TB_SITRACE_PORT,
                                                                  config.TB_SITRACE_BAUDRATE),
                                        "file={}".format(log_filename)])


    def _stop_tb_logging(self):
        _debug('stop TB logging')
        terminate_process(self.tb_log)
        del self.tb_log

    def _start_detail_logging(self):
        _debug('start detail logging')
        if EXECUTION_CONTEXTS.current is not None:
            test_name = BuiltIn().get_variable_value('${TEST NAME}')
        else:
            test_name = ''

        filename = 'detail_log_' + test_name + '.st'
        file_path = os.path.join(output_dir, filename)
        self.detail_log_file = open(file_path, 'wb')
        _trace_timestamp()

        _trace_printf('===================')
        _trace_printf(test_name)
        _trace_printf('===================')


    def _stop_detail_logging(self):
        _debug('stop detail logging')
        self.detail_log_file.close()
        self.detail_log_file = None

    def _start_timer(self, interval):
        self.exp_timer = threading.Timer(interval, self._timer_func)
        timeout_str = robot.utils.secs_to_timestr(interval)
        self.error_msg = '{0} timeout'.format(timeout_str)
        self.exp_timer.start()

    def _stop_timer(self):
        if (self.exp_timer is not None):
            self.exp_timer.cancel()

    def _timer_func(self):
        raise AssertionError(self.error_msg)

    def _init_band_param(self, work_band, tonemask):
        self.tonemask_param = plc_packet_helper.init_tonemask_param(work_band, tonemask)

    def _gen_sof_fc(self, data_size, ack_needed=True, lid=1, dst_tei=1, src_tei=0,
        encrypt_flag=0, retrans_flag=0,broadcast_flag=0):

        pb_format = plc_packet_helper.calc_pb_format(self.tonemask_param, plc_packet_helper.MAC_MPDU_SOF, data_size)
        self.fc.mpdu_type = 'PLC_MPDU_SOF'
        frame_len = plc_packet_helper.calc_frame_len(pb_format['sym_num'], ack_needed)

        self.fc.var_region_ver = Container(lid=lid,dst_tei=dst_tei,src_tei=src_tei,
            pb_num=pb_format['pb_num'], frame_len=frame_len, tmi_b=pb_format['tmi_basic_mode'],encrypt_flag=encrypt_flag,
            retrans_flag=retrans_flag, broadcast_flag=broadcast_flag, symbol_num=pb_format['sym_num'],
            ver=0, tmi_e=pb_format['tmi_ext_mode'])


    def _set_sof_fc(self, ack_needed=True, lid=1, dst_tei=1, src_tei=0, pb_num=1, tmi_b=0, encrypt_flag=0,
        retrans_flag=0,broadcast_flag=0,tmi_e=0):

        sym_num = self.tonemask_param.calc_payload_sym_num(tmi_b, tmi_e, pb_num)
        frame_len = plc_packet_helper.calc_frame_len(sym_num, ack_needed)

        self.fc.mpdu_type = 'PLC_MPDU_SOF'
        self.fc.var_region_ver = Container(lid=lid,dst_tei=dst_tei,src_tei=src_tei,
            pb_num=pb_num, frame_len=frame_len, tmi_b=tmi_b,encrypt_flag=encrypt_flag,
            retrans_flag=retrans_flag, broadcast_flag=broadcast_flag, symbol_num=sym_num,
            ver=0, tmi_e=tmi_e)

    #this function is used to config TB to send discover beacon automatically
    #if the sta in sta/proxy beacon list, TB will send disc beacon
    def _config_sta_tei(self,sta_tei,proxy_tei,level,phase,mac_addr):
        dict_content = {
                    'num': 1,
                    'info':[{
                            'sta_tei':sta_tei,
                            'proxy_tei':proxy_tei,
                            'min_succ_rate': 50,
                            'level':level,
                            'proxy_channel_quality':100,
                            'phase':phase,
                            'mac':mac_addr
                        }]
            }

        result = test_frame_helper.build_sta_config_req(dict_content = dict_content)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        test_frame = self.tb_uart.wait_for_test_frame("STA_CONFIG_CNF_CMD", timeout=30)
        assert test_frame is not None
        #return test_frame.payload.timestamp

    def _config_freq_offset(self, freq_offset):
        dict_content = {"freq_offset": freq_offset}
        result = test_frame_helper.build_freq_offset_config_req(dict_content = dict_content)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        test_frame = self.tb_uart.wait_for_test_frame("FREQ_OFFSET_CONFIG_CNF_CMD", timeout=30)
        assert test_frame is not None

    # this function is used to config TB to send SACK automatically
    def _config_sack_tei(self,nid,sta_tei,src_tei,dst_tei,rx_result=0,rx_status=1,
                         rx_pb_num=1):
        fc = dict(mpdu_type='PLC_MPDU_SACK', network_type=0, nid=nid, crc=0)
        sack_var_region_ver = dict(rx_result=rx_result, rx_status=rx_status,
                                   dst_tei=dst_tei, src_tei=src_tei,
                                   rx_pb_num=rx_pb_num, chan_quality=0xFF,
                                   load=0, ext_frame_type=0, ver=0)
        fc['var_region_ver'] = sack_var_region_ver
        dict_content = dict(src_tei=sta_tei, fc=fc)

        result = test_frame_helper.build_sack_config_req(dict_content=dict_content)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        #test_frame = self.tb_uart.wait_for_test_frame("SACK_CONFIG_CNF_CMD", timeout=30)
        #assert test_frame is not None

    def _config_sack_auto_reply_ex(self, sta_tei, sack_data_list=[]):
        dict_content = dict(src_tei=sta_tei, num=len(sack_data_list), fc=[])
        for sack in sack_data_list:
            fc = dict(mpdu_type='PLC_MPDU_SACK', network_type=0, nid=sack["nid"], crc=0)
            sack_var_region_ver = dict(rx_result=sack['rx_result'], rx_status=sack['rx_status'],
                                    dst_tei=sack["dst_tei"], src_tei=sack["src_tei"],
                                    rx_pb_num=sack['rx_pb_num'], chan_quality=0xFF,
                                    load=0, ext_frame_type=0, ver=0)
            fc['var_region_ver'] = sack_var_region_ver
            dict_content['fc'].append(fc)

        result = test_frame_helper.build_sack_config_ex_req(dict_content=dict_content)
        cf = result['cf']
        frame_body = result['body']
        self.tb_uart.send_test_frame(frame_body, cf)
        #test_frame = self.tb_uart.wait_for_test_frame("SACK_CONFIG_CNF_CMD", timeout=30)
        #assert test_frame is not None

    def _gen_test_frame_sn(self):
        self.test_frame_sn += 1

        return self.test_frame_sn

    def reset_dut(self):
        result = self.usb_relay_device.open(RST_CHANNEL)

        assert 0 == result, "close relay fail"
        time.sleep(0.2)

        result = self.usb_relay_device.close(RST_CHANNEL)

        assert 0 == result, "open relay fail"

    def set_event_high(self):
        result = self.usb_relay_device.open(EVENT_CHANNEL)
        assert 0 == result, "open relay fail"


    def set_event_low(self):
        result = self.usb_relay_device.close(EVENT_CHANNEL)
        assert 0 == result, "close relay fail"

    def meter_platform_power_determind_reset(self):
        self.usb_relay_device.open(1, 3)
        time.sleep(5)
        self.tb_uart.close_tb_test_port()
        self.tb_uart.open_tb_test_port()
        _debug("power off all of meters and cco, delay 5s")
        self.usb_relay_device.close(1, 3)
        _debug("power on all of meters and cco. delay 5s for boot")
        time.sleep(5)
        self._deactivate_tb()

    def meter_platform_power_escort(self, status=0):
        '''
        :param status: 0=off;1=on;2=reset,use 5s
        :return: None
        '''
        if status == 0:
            self.usb_relay_device.open(2)
        elif status == 1:
            self.usb_relay_device.close(2)
        elif status == 2:
            self.usb_relay_device.open(2)
            time.sleep(5)
            self.usb_relay_device.close(2)


if __name__ == '__main__':
    pass


