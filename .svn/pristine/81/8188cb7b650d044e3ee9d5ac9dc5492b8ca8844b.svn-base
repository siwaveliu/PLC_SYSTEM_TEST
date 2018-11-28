# -- coding: utf-8 --

from robot.api import logger
from construct import *
import os.path
import time
import plc_packet_helper
import concentrator
import test_frame_helper
import plc_tb_ctrl
import tc_common
import numpy as np
import config
import math
import s_scope
import sitrace_logger

WORK_BAND = 2
TONE_MASK_TEST = 0
AFE_TX_GAIN_DB = -14
DAC_TX_SHIFT = 0
SCOPE_ADDR = 'TCPIP0::{0}::inst0::INSTR'.format(config.SCOPE_IP)
band_test_data_set1 = [
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 0, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 1, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 2, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 3, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 4, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 5, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 6, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 7, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 8, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 9, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 10, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 11, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 12, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 13, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 14, 'tmi_e': 0, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 1, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 2, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 3, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 4, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 5, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 6, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 10, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 11, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 12, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 13, 'pb_nbr': 1},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 14, 'pb_nbr': 1},
]

band_test_data_set2 = [
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 0, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 1, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 2, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 3, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 4, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 5, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 6, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 7, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 8, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 9, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 10, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 11, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 12, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 13, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 14, 'tmi_e': 0, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 1, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 2, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 3, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 4, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 5, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 6, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 10, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 11, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 12, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 13, 'pb_nbr': 2},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 14, 'pb_nbr': 2},
]

band_test_data_set3 = [
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 0, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 1, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 2, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 3, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 4, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 5, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 6, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 7, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 8, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 9, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 10, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 11, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 12, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 13, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 14, 'tmi_e': 0, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 1, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 2, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 3, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 4, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 5, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 6, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 10, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 11, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 12, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 13, 'pb_nbr': 3},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 14, 'pb_nbr': 3},
]

band_test_data_set4 = [
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 0, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 1, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 2, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 3, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 4, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 5, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 6, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 7, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 8, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 9, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 10, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 11, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 12, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 13, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 14, 'tmi_e': 0, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 1, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 2, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 3, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 4, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 5, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 6, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 10, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 11, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 12, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 13, 'pb_nbr': 4},
    {'band': WORK_BAND, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 14, 'pb_nbr': 4},
]

def check(tb, test_data):
    TARGET_SUCC_RATE = 0.1
    packet_num = 20000
    #packet_interval = 50
    beacon_period = 100
    beacon_num = 0
    beacon_interval = 500
    pb_num = int(test_data['pb_nbr'])
    band = int(test_data['band'])
    data_rate_Mbps = []
    frame_period_us_buff = []
    inter_frame_gap_buff = []
    fail_times = 0
    tx_cnt = 0
    rx_cnt = 0
    fail_num = packet_num*TARGET_SUCC_RATE

    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"

    sym_num = tb.tonemask_param.calc_payload_sym_num(tmi_b=test_data['tmi_b'], tmi_e=test_data['tmi_e'], pb_num=pb_num)
    frame_len_ntb = plc_packet_helper.calc_frame_len_ntb(band, sym_num)
    frame_len_ntb_ms = frame_len_ntb / 25.0 / 1000.0
    pb_size = plc_packet_helper.query_pb_size_by_tmi(tmi_b=test_data['tmi_b'], tmi_e=test_data['tmi_e'])
    sof_payload_size = pb_size * pb_num * 8
    loopback_air_min_period_ms = math.ceil((2 * frame_len_ntb_ms + 10.0) / 50.0) * 50
    ppdu_paylaod_Bps = (pb_size * pb_num + 16)*1000.0/loopback_air_min_period_ms
    tb_ser_Bps = config.TB_BAUDRATE/10.0
    packet_interval = loopback_air_min_period_ms * math.ceil(ppdu_paylaod_Bps/tb_ser_Bps+0.5)
    tb_ser_workload = (pb_size * pb_num + 16)*1000.0/packet_interval/tb_ser_Bps
    fail_times = 0
    miss_times = 0
    total_cnt = 0
    beacon_len_ntb = beacon_num * beacon_interval*25000
    beacon_time = (packet_num + beacon_period - 1) / beacon_period * beacon_num * beacon_interval
    timeout = (packet_num * packet_interval + beacon_time) / 1000. + 1
    stop_time = time.time() + timeout * config.CLOCK_RATE
    rx_fc_pl_timeout = (frame_len_ntb / 25.0 / 1000.0 + 5.0) * config.CLOCK_RATE / 1000.0

    plc_tb_ctrl._debug("step {}".format(test_data))
    plc_tb_ctrl._debug("exp total: {}, timeout: {}s, packet_interval :{}ms, tb_ser_workload = {:.2f}".format(packet_num, timeout, packet_interval, tb_ser_workload))

    # 停止之前的发送
    tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tx_num=0)

    # 配置TB周期性发送中央信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0
    init_beacon_wait = 2
    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
    # 等待信标都发送完成
    time.sleep(init_beacon_wait)

    tb.tb_uart.clear_tb_port_rx_buf()
    time.sleep(1)

    # 周期发送sof帧
    tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tmi_b=test_data['tmi_b'], tmi_e=test_data['tmi_e'],
                                                           pb_num=pb_num, ack_needed=False, tx_interval=packet_interval,
                                                           tx_num=packet_num + 1,
                                                           beacon_period=beacon_period, beacon_num=beacon_num,
                                                           beacon_interval=beacon_interval)
    if config.TB_STANDALONE==1:
        tb_sitrace = sitrace_logger.SitraceLogger(False)  # TB
        tb_sitrace.open_port()
        tc_common.tx_gain_control(tb_sitrace, afe_control=config.TB_AFE_TYPE, afe_gain_db=AFE_TX_GAIN_DB, dac_shift=DAC_TX_SHIFT,reg1104='a3d400')
        tb_sitrace.close_port()
    else:
        dut_sitrace = sitrace_logger.SitraceLogger(True)  # DUT
        dut_sitrace.open_port()
        tc_common.tx_gain_control(dut_sitrace, afe_control=config.DUT_AFE_TYPE, afe_gain_db=AFE_TX_GAIN_DB, dac_shift=DAC_TX_SHIFT,reg1104='a3d400')
        dut_sitrace.close_port()
    # 开启示波器频谱测量功能
    scope_differential_en = 0
    scope_channel =  1
    detect_type = 0
    fs = 100E+6
    result = tc_common.tx_psd_measure(tb.scope, band, fs, scope_differential_en, scope_channel,detect_type)
    #result = tc_common.tx_inbandpwr_measure(tb.scope, band, fs=50E+6, differential_en=scope_differential_en, channel=scope_channel)
    psd_upperband = -100
    psd_lowerband = -100
    # 统计和log打印
    logtxt = "{},{},{},{}".format(band, test_data['tmi_b'],test_data['tmi_e'],pb_num)
    if (result != None):
        [pwr_inband, psd_inband, psd_upperband, psd_lowerband] = result
        #[pwr_inband, psd_inband] = result
        psd_outband = max(psd_upperband, psd_lowerband)
        if (psd_inband > -45) or (psd_outband>-75):
            plc_tb_ctrl._debug("FAIL, pwr_inband:{:.1f}dBm, psd_inband:{:.1f}dBm/Hz, psd_upperband:{:.1f}dBm/Hz, psd_lowerband:{:.1f}dBm/Hz".format(pwr_inband, psd_inband, psd_upperband, psd_lowerband))
            logtxt = "FAIL," + logtxt + ",{:.1f},{:.1f},{:.1f},{:.1f}  \n".format(pwr_inband, psd_inband, psd_upperband, psd_lowerband)
        else:
            plc_tb_ctrl._debug("SUCC, pwr_inband:{:.1f}dBm, psd_inband:{:.1f}dBm/Hz, psd_upperband:{:.1f}dBm/Hz, psd_lowerband:{:.1f}dBm/Hz".format(pwr_inband, psd_inband, psd_upperband, psd_lowerband))
            logtxt = "SUCC,"+logtxt+",{:.1f},{:.1f},{:.1f},{:.1f}  \n".format(pwr_inband, psd_inband, psd_upperband, psd_lowerband)
    else:
        plc_tb_ctrl._debug("FAIL, Please check scope connection or hardware condition")
        logtxt = "FAIL,"+logtxt+",0,0,0,0  \n"

    tb.result_file.write(logtxt)
    tb.result_file.flush()



def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    band = WORK_BAND

    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    tc_common.activate_tb(tb, WORK_BAND, 0, 1)

    timestamp_str = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    filename = 'tc2p1p3_result_' + timestamp_str + '.txt'
    meas_file_path = os.path.join(plc_tb_ctrl.output_dir, filename)
    tb.result_file = open(meas_file_path, 'w')
    if config.TB_STANDALONE==1:
        # tb.sitrace = sitrace_logger.SitraceLogger(False)  # TB
        # tb.sitrace.open_port()
        # tc_common.tx_gain_control(tb.sitrace, afe_control=config.TB_AFE_TYPE, afe_gain_db=AFE_TX_GAIN_DB, dac_shift=DAC_TX_SHIFT,reg1104='a3d400')
        # tb.sitrace.close_port()
        logtxt = "TB AFE type:{} (0:Atheros; 1:Weile); SOF Rate:{} (1: 100M; 2:50M); AFE_Tx_Gain:{}db; DAC_Tx_shift:{}  \n".format(config.TB_AFE_TYPE, config.CLOCK_RATE,AFE_TX_GAIN_DB,DAC_TX_SHIFT)
    else:
        # dut_sitrace = sitrace_logger.SitraceLogger(True)  # DUT
        # dut_sitrace.open_port()
        # tc_common.tx_gain_control(dut_sitrace, afe_control=config.DUT_AFE_TYPE, afe_gain_db=AFE_TX_GAIN_DB, dac_shift=DAC_TX_SHIFT,reg1104='a3d400')
        # dut_sitrace.close_port()
        logtxt = "DUT AFE type:{} (0:Atheros; 1:Weile); SOF Rate:{} (1: 100M; 2:50M)  \n".format(config.DUT_AFE_TYPE,config.CLOCK_RATE,AFE_TX_GAIN_DB,DAC_TX_SHIFT)
    tb.result_file.write(logtxt)
    logtxt = "succ, band, tmi_b, tmi_e, pb_nbr, pwr_inband, psd_inband, psd_upperband, psd_lowerband  \n"
    tb.result_file.write(logtxt)

    plc_tb_ctrl._debug("initial scope....")
    tb.scope = s_scope.Scope_Keysight(SCOPE_ADDR)
    plc_tb_ctrl._debug("clear scope status....")
    tb.scope.clear_status()
    plc_tb_ctrl._debug("reset scope....")
    tb.scope.reset()





    plc_tb_ctrl._debug("band: {}".format(band))

    # 在频段0发送20次频段设置命令
    tb._change_band(0)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段1发送20次频段设置命令
    tb._change_band(1)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段2发送20次频段设置命令
    tb._change_band(2)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段3发送20次频段设置命令
    tb._change_band(3)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    tb._change_band(band)

    if(TONE_MASK_TEST==1):
        # 在指定频段发送20次tonemask设置命令
        for i in range(20):
            tc_common.send_comm_test_command(test_mode_cmd='CONFIG_TONEMASK', param=band)
        tb._change_band(band,band)

    # 在指定频段发送20次测试命令帧，进入物理层回传测试模式
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='ENTER_PHY_LOOPBACK_MODE', param=1440)

    for test_data in band_test_data_set1:
        check(tb, test_data)
    for test_data in band_test_data_set2:
        check(tb, test_data)
    for test_data in band_test_data_set3:
        check(tb, test_data)
    for test_data in band_test_data_set4:
        check(tb, test_data)

    tb.result_file.close()
    del tb.scope
    #tb.sitrace.close_port()
