
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
import sitrace_logger

WORK_BAND = 2
TONE_MASK_TEST = 0
AFE_TX_GAIN_DB = -14	# atheros: -14,  weile: 0
DAC_TX_SHIFT = 0
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
    packet_num = 500
    #packet_interval = 50
    beacon_period = 100
    beacon_num = 5
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
    # if beacon_num>0:
    #     beacon_dict['num'] = 5
    #     init_beacon_wait = 20
    # else:
    #     beacon_dict['num'] = 5
    #     init_beacon_wait = 5*2*config.CLOCK_RATE
    beacon_dict['num'] = 0
    init_beacon_wait = 2
    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    # 等待5个信标都发送完成
    time.sleep(init_beacon_wait)

    tb.tb_uart.clear_tb_port_rx_buf()
    time.sleep(1)
    tb_sitrace = sitrace_logger.SitraceLogger(False)  # TB
    tb_sitrace.open_port()
    if test_data['mpdu_type'] == plc_packet_helper.MAC_MPDU_SOF:
        tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tmi_b=test_data['tmi_b'], tmi_e=test_data['tmi_e'],
                                                        pb_num=pb_num, ack_needed=False, tx_interval = packet_interval, tx_num=packet_num+1,
                                                        beacon_period=beacon_period, beacon_num=beacon_num,beacon_interval=beacon_interval)
    else:
        tx_fc_pl_data = tc_common.send_periodic_sack_fc_pl_data()

    tc_common.tx_gain_control(tb_sitrace, afe_control=config.TB_AFE_TYPE, afe_gain_db=AFE_TX_GAIN_DB,
                              dac_shift=DAC_TX_SHIFT, reg1104='a3d400')

    rx_fc_pl_data = tx_fc_pl_data
    tx_ppdu_end_time_last = 0
    rx_ppdu_start_time_last = 0
    succ_flag = True
    tx_period = 0
    rx_period = 0
    assert_flag = 0
    while tx_cnt <= packet_num :
        #test_frame = tb.tb_uart.wait_for_test_frame(cf="TX_COMPLETE_IND",timeout=packet_interval/1000.0)
        #test_frame = tb.tb_uart.wait_for_test_frame(cf="TX_COMPLETE_IND")
        test_frame = tb.tb_uart.wait_for_test_frame()
        if ("TX_COMPLETE_IND" == test_frame.head.cf):
            tx_ppdu_end_time = test_frame['payload']['timestamp']
            tx_cnt += 1
            if tx_cnt>1:
                tx_period = ((tx_ppdu_end_time - tx_ppdu_end_time_last + 0x100000000) & 0xFFFFFFFF)
                tx_diff = int((tx_period / 25.0 + 2000) / (packet_interval * 1000.0))-1
                if (tx_diff>0):
                    assert_flag = 1
                    plc_tb_ctrl._debug("TX_COMPLETE_IND missing {} times".format(tx_diff))
                    break
            tx_ppdu_end_time_last = tx_ppdu_end_time
            if (tx_cnt<=packet_num):
                plc_tb_ctrl._debug("Tx#{},".format(tx_cnt) + "tx_ppdu_end_time: {}, ".format(tx_ppdu_end_time) + ", tx_period: {}us".format(tx_period / 25.0))
                if (tx_cnt%beacon_period)==0 and beacon_num>0:
                    tx_ppdu_end_time_last = tx_ppdu_end_time_last + beacon_len_ntb
            continue
        elif ("FC_PL_DATA" == test_frame.head.cf):
            rx_fc_pl_data = test_frame.payload
            rx_cnt += 1
            rx_ppdu_start_time = rx_fc_pl_data['timestamp']
            if rx_cnt>1:
                rx_period = ((rx_ppdu_start_time - rx_ppdu_start_time_last + 0x100000000) & 0xFFFFFFFF)
                rx_diff = int((rx_period / 25.0 + 2000) / (packet_interval * 1000.0))-1
                if rx_diff > 0:
                    # miss_times += 1
                    # for i in range(rx_diff):
                    #     data_rate_Mbps.append(0)
                    plc_tb_ctrl._debug("rx miss cnt: {}".format(miss_times) + ",rx_diff: {}".format(rx_diff))
            rx_ppdu_start_time_last = rx_ppdu_start_time
            if (tx_cnt%beacon_period)==0 and beacon_num>0:
                rx_ppdu_start_time_last += beacon_len_ntb
        else:
            continue

        plc_tb_ctrl._debug("Rx#{},".format(rx_cnt) + "Tx#{},".format(tx_cnt) + "tx_ppdu_end_time: {}, ".format(
            tx_ppdu_end_time) + "rx_ppdu_start_time: {}".format(rx_ppdu_start_time) + ", tx_period: {}us".format(
            tx_period / 25.0) + ",rx_period: {}us".format(rx_period / 25.0))

        inter_frame_gap = ((rx_ppdu_start_time - tx_ppdu_end_time + 0x100000000) & 0xFFFFFFFF)
        inter_frame_gap_buff.append(inter_frame_gap)
        frame_period =  inter_frame_gap + frame_len_ntb
        frame_period_us = frame_period/25.0
        frame_period_us_buff.append(frame_period_us)
        inter_frame_gap_us = inter_frame_gap/25.0 + 100.0
        plc_tb_ctrl._debug("frame+IFS: {}us".format(frame_period_us) + ", IFS: {}us".format(inter_frame_gap/25.0))

        if tx_fc_pl_data['payload']['data'] != rx_fc_pl_data['payload']['data']:
            fail_times += 1
            plc_tb_ctrl._debug("mismatch")
            plc_tb_ctrl._trace_byte_stream("tx", tx_fc_pl_data['payload']['data'])
            plc_tb_ctrl._trace_byte_stream("rx", rx_fc_pl_data['payload']['data'])
            data_rate_Mbps.append(0)
        else:
            if inter_frame_gap_us<400.0:
                plc_tb_ctrl._debug("inter frame gap is less than 400us")
                data_rate_Mbps.append(0)
            else:
                data_rate_Mbps.append(sof_payload_size / frame_period_us*1000.0)
        # if (miss_times+fail_times) > fail_num :
        #     plc_tb_ctrl._debug("fail times exceeds target")
        #     succ_flag = False
        #     break
    tx_cnt = tx_cnt - 1
    plc_tb_ctrl._trace_byte_stream("tx data", tx_fc_pl_data['payload']['data'])
    tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tx_num=0)
    miss_times = packet_num - rx_cnt
    if (miss_times>0):
        for i in range(miss_times):
            data_rate_Mbps.append(0)

    if (miss_times + fail_times) > fail_num:
        succ_flag = False
    if (rx_cnt==0) and (assert_flag==0):
        assert_flag = 1
        plc_tb_ctrl._debug("LOOPBACK RX FAIL, PLEASE CHECK CABLE CONNECTION OR DUT's STATUS")

    if assert_flag == 1:
        logtxt = "ASSERT,{},{},{},{},{:.2f},{},{},{},{:.1f},{:.1f},{:.1f},{:.1f}  \n".format(band, test_data['tmi_b'],test_data['tmi_e'],
                                                                                      pb_num, 1.0,tx_cnt, fail_times, miss_times,0, 0,0,0)
    else:
        narray = np.array(data_rate_Mbps)
        rate_meas = np.mean(narray)
        narray = np.array(frame_period_us_buff)
        frame_period_us_meas = np.mean(narray)
        narray = np.array(inter_frame_gap_buff)
        inter_frame_gap_mean = np.mean(narray)

        rate_ideal = sof_payload_size / (frame_len_ntb/25.0+300.0) * 1000.0

        logtxt = "{},{},{},{},{:.2f},{},{},{},{:.1f},{:.1f},{:.1f},{:.1f}  \n".format(band, test_data['tmi_b'], test_data['tmi_e'],
                                                                    pb_num, (miss_times + fail_times + 0.0) / tx_cnt,
                                                                    tx_cnt, fail_times, miss_times, frame_period_us_meas,
                                                                    inter_frame_gap_mean / 25.0, rate_meas,rate_ideal)
        if succ_flag:
            plc_tb_ctrl._debug("SUCC: tx_cnt: {}, fail_cnt: {}, miss_cnt:{}, rate_meas:{:.1f}Kbps, rate_ideal: {:.1f}Kbps".format(tx_cnt, fail_times, miss_times,rate_meas,rate_ideal))
            logtxt = "SUCC,"+logtxt
        else:
            plc_tb_ctrl._debug("FAIL: tx_cnt: {}, fail_cnt: {}, miss_cnt:{}, rate_meas:{:.1f}Kbps, rate_ideal: {:.1f}Kbps".format(tx_cnt, fail_times, miss_times, rate_meas, rate_ideal))
            logtxt = "FAIL," + logtxt

    tb.result_file.write(logtxt)
    tb.result_file.flush()
    tb_sitrace.close_port()


def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """


    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    tc_common.activate_tb(tb, WORK_BAND, 0, 1)

    timestamp_str = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    filename = 'tc2p7p3_result_' + timestamp_str + '.txt'
    meas_file_path = os.path.join(plc_tb_ctrl.output_dir, filename)
    tb.result_file = open(meas_file_path, 'w')
    logtxt = "succ, band, tmi_b, tmi_e, pb_nbr, total_cnt, per, fail_cnt, miss_cnt, " \
             "frame_duration, IFS, rate_meas, rate_ideal  \n"
    tb.result_file.write(logtxt)

    band = WORK_BAND

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
