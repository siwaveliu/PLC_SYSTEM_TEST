# -- coding: utf-8 --

import os
import os.path
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from construct import *
import time
import plc_packet_helper
import concentrator
import test_frame_helper
#import test_data_reader
import plc_tb_ctrl
import tc_common

band2_test_data_set = [
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 0, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 1, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 2, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 3, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 4, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 5, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 6, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 7, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 8, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 9, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 10, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 11, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 12, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 13, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 14, 'tmi_e': 0},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 1},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 2},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 3},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 4},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 5},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 6},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 10},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 11},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 12},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 13},
    {'band': 2, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 14},
]

def check(tdr,tb, test_data,result_file):
    total_num = 200
    error_rate = 0.1
    fail_times = 0
    total_cnt = 0
    fail_num = total_num*error_rate
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"

    plc_tb_ctrl._debug("step {}".format(test_data))

    ## 配置TB周期性发送中央信标
    #beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    #beacon_dict['num'] = 5
    #beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
    #
    ## 等待5个信标都发送完成
    #time.sleep(20)
    #'''
    #for i in range(5):
    #    plc_tb_ctrl._debug('wait for TX_COMPLETE_IND')
    #    test_frame = tb.tb_uart.wait_for_test_frame("TX_COMPLETE_IND", timeout_assert=False)
    #    #assert test_frame is not None, 'TX_COMPLETE_IND Timeout'
    #'''
    #time.sleep(0.5)
    #tb.tb_uart.clear_tb_port_rx_buf()
    #fail_times = 0
    while total_cnt < total_num:
        if total_cnt%100 == 0:  
            # 停止之前的发送
            tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tx_num=0)
            #每发送100个测试帧，发5个beacon
            beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
            beacon_dict['num'] = 5
            beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
            # 等待5个信标都发送完成
            time.sleep(10)

        #tdr.clear_port_rx_buf()
        if test_data['mpdu_type'] == plc_packet_helper.MAC_MPDU_SOF:
            tx_fc_pl_data = tc_common.send_sof_fc_pl_data(tmi_b=test_data['tmi_b'],
                                                          tmi_e=test_data['tmi_e'],
                                                          pb_num=1, ack_needed=False)
            rx_fc_pl_data = tb._wait_for_fc_pl_data(timeout_cb=lambda:None)
        else:
            tx_fc_pl_data = tc_common.send_sack_fc_pl_data()
            rx_fc_pl_data = tb._wait_for_fc_pl_data(timeout_cb=lambda:None)

        total_cnt += 1
        
        if rx_fc_pl_data is None:
            fail_times += 1
            plc_tb_ctrl._debug("miss")
            continue

        if tx_fc_pl_data['payload']['data'] != rx_fc_pl_data['payload']['data']:
            fail_times += 1
            plc_tb_ctrl._debug("mismatch")
            plc_tb_ctrl._trace_byte_stream("tx", tx_fc_pl_data['payload']['data'])
            plc_tb_ctrl._trace_byte_stream("rx", rx_fc_pl_data['payload']['data'])
        
        plc_tb_ctrl._debug("total: {}, fail: {}".format(total_cnt, fail_times))
        
        if fail_times > fail_num :
            plc_tb_ctrl._debug("fail times exceeds target")
            break
        
        time.sleep(0.05)
    result_file.write("total: {}, fail: {}\n".format(total_cnt, fail_times))
    plc_tb_ctrl._debug("total: {}, fail: {}".format(total_cnt, fail_times))




def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    tc_common.activate_tb(tb, plc_packet_helper.WORK_BAND2, 0, 1)

    band=2
    TONE_MASK_TEST = 0
    plc_tb_ctrl._debug("band: {}".format(band))
    
    #tdr = test_data_reader.TestDataReader()
    #tdr.open_port()
    
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
        tc_common.send_comm_test_command(test_mode_cmd='ENTER_PHY_LOOPBACK_MODE', param=6000)

    output_dir = BuiltIn().get_variable_value('${OUTPUT DIR}')
    timestamp_str = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    filename = 'awgn_result_' + timestamp_str + '.txt'
    meas_file_path = os.path.join(output_dir, filename)
    result_file = open(meas_file_path, 'w')
    tdr = ''
    for test_data in band2_test_data_set:
        result_file.write("*************************************\n")
        result_file.write("band {:d} tmi_b {:d} tmi_e {:d} \n".format(band,int(test_data['tmi_b']),int(test_data['tmi_e'])))
        check(tdr,tb, test_data,result_file)

