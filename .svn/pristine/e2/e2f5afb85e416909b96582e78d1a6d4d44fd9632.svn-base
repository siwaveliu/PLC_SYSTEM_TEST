# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import test_data_reader
import test_frame_helper
import plc_tb_ctrl
import tc_common

band0_test_data_set = [
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 0, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 1, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 2, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 3, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 4, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 5, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 6, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 7, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 8, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 9, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 10, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 11, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 12, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 13, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 14, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 1},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 2},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 3},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 4},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 5},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 6},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 10},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 11},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 12},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 13},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 14},
]

def check(tdr, tb, test_data):
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"

    TARGET_SUCC_RATE = 0.1
    packet_num = 200
    packet_interval = 500
    beacon_period = 100
    beacon_interval = 1000

    plc_tb_ctrl._debug("step {}".format(test_data))
	
    # 配置TB周期性发送中央信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 5
    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    # 等待5个信标都发送完成
    time.sleep(10)
    
    # 停止之前的发送
    tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tx_num=0)

    time.sleep(2)
    tdr.clear_port_rx_buf()
    '''
    if test_data['mpdu_type'] == plc_packet_helper.MAC_MPDU_SOF:
        tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tmi_b=test_data['tmi_b'],
                                                        tmi_e=test_data['tmi_e'],
                                                        pb_num=1, ack_needed=False, tx_num=packet_num)
    else:
        tx_fc_pl_data = tc_common.send_periodic_sack_fc_pl_data()
    data_len = len(tx_fc_pl_data['payload']['data'])
    '''
    corr_cnt = 0
    total_cnt = 0
    beacon_time = (packet_num + beacon_period - 1) / beacon_period * 5 * beacon_interval
    timeout = (packet_num * packet_interval + beacon_time) / 1000. + 1
    stop_time = time.time() + timeout
    #plc_tb_ctrl._trace_byte_stream("tx data", tx_fc_pl_data['payload']['data'])
    succ_rate = 0
    plc_tb_ctrl._debug("exp total: {}, timeout: {}s".format(packet_num,timeout))
	
    while succ_rate < TARGET_SUCC_RATE :
        tdr.clear_port_rx_buf()	
        if test_data['mpdu_type'] == plc_packet_helper.MAC_MPDU_SOF:
            tx_fc_pl_data = tc_common.send_sof_fc_pl_data(tmi_b=test_data['tmi_b'],
                                                          tmi_e=test_data['tmi_e'],
                                                          pb_num=3, ack_needed=False)
        else:
            tx_fc_pl_data = tc_common.send_sack_fc_pl_data()			
        data_len = len(tx_fc_pl_data['payload']['data'])			
        frame = tdr.read_frame(data_len, 1)
		
        #if len(frame) == data_len:
        total_cnt += 1
        plc_tb_ctrl._trace_byte_stream("tx", tx_fc_pl_data['payload']['data'])
        plc_tb_ctrl._trace_byte_stream("rx", frame)
        if frame == tx_fc_pl_data['payload']['data']:
            corr_cnt += 1

        succ_rate = float(corr_cnt) / packet_num
        '''
        assert time.time() < stop_time, "{}s timeout, total: {}, correct: {}".format(timeout, total_cnt,corr_cnt)
        assert total_cnt < packet_num, "total: {}, correct: {}, succ_rate:{}".format(total_cnt, corr_cnt,succ_rate)
        '''
        if time.time() > stop_time :
            plc_tb_ctrl._debug("RX TIMEOUT")
            break 

    plc_tb_ctrl._debug("total: {}, correct: {}, succ_rate:{}".format(total_cnt, corr_cnt, succ_rate))

def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    tc_common.activate_tb(tb, plc_packet_helper.WORK_BAND0, 0, 1)

    tdr = test_data_reader.TestDataReader()
    tdr.open_port()

    band=2
    TONE_MASK_TEST = 1
    plc_tb_ctrl._debug("band: {}".format(band))
	
    # 在频段0发送20次频段设置命令
    tb._change_band(0)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段1发送20次频段设置命令
    tb._change_band(1)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段0发送20次频段设置命令
    tb._change_band(2)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段1发送20次频段设置命令
    tb._change_band(3)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    tb._change_band(band)
	
    if(TONE_MASK_TEST==1):
        # 在指定频段发送20次tonemask设置命令
        for i in range(20):
            tc_common.send_comm_test_command(test_mode_cmd='CONFIG_TONEMASK', param=band)
        tb._change_band(band,band)
	
    # 在指定频段发送20次测试命令帧，进入物理层透传测试模式
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='ENTER_PHY_TRANS_MODE', param=30)

    for test_data in band0_test_data_set:
        check(tdr, tb, test_data)

