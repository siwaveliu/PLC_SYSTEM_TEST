# -- coding: utf-8 --

import os
import os.path
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from construct import *
import time
import config
import sitrace_logger
import plc_packet_helper
import test_data_reader
import test_frame_helper
import plc_tb_ctrl
import tc_common
import fadding
import siggen

def int2bin(n, count=24):
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

band0_test_data_set = [
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 0, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 1, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 2, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 3, 'tmi_e': 0},
    {'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 4, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 5, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 6, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 7, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 8, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 9, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 10, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 11, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 12, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 13, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 14, 'tmi_e': 0},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 1},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 2},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 3},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 4},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 5},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 6},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 10},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 11},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 12},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 13},
    #{'band': 0, 'mpdu_type': plc_packet_helper.MAC_MPDU_SOF, 'tmi_b': 15, 'tmi_e': 14},
]

def check(tdr, tb, test_data,result_file):
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"

    TARGET_SUCC_RATE = 0.9
    packet_num = 200
    packet_interval = 250
    beacon_period = 100    
    beacon_num = 5
    beacon_interval = 1000


    plc_tb_ctrl._debug("step {}".format(test_data))

    corr_cnt = 0
    total_cnt = 0
    beacon_time = (packet_num + beacon_period - 1) / beacon_period * beacon_num * beacon_interval
    timeout = (packet_num * packet_interval + beacon_time) / 1000. + 1
    stop_time = time.time() + timeout
    plc_tb_ctrl._debug("exp total: {}, timeout: {}s".format(packet_num,timeout))
    
    
    # TB_cli = SitraceLogger(False)
    # 正向频偏测试
    succ_rate = 0
    current_sco = -10
    sco_step = -10
    
    while succ_rate < TARGET_SUCC_RATE:
        # TB侧调整频偏和NTB
        #TB_cli.open_port()
        #current_sco_quan = "0x{:x}".format(int(float(current_sco)*1e-6*2**22))
        #TB_cli.send_cli_cmd("memwrite 32 0x5007001c 0x200000a0\r\n");
        #TB_cli.send_cli_cmd("memwrite 32 0x50070018 0x00000000\r\n");
        #TB_cli.send_cli_cmd("memwrite 32 0x50071254 0x0\r\n")
        #TB_cli.send_cli_cmd("memwrite 32 0x50071250 0x0\r\n")
        #plc_tb_ctrl._debug("add sco: {} ppm".format(current_sco))
        #TB_cli.send_cli_cmd("memwrite 32 0x50071254 0x" + "{:x}".format(int(('1'+int2bin(8000,16)),2))+"\r\n")
        #TB_cli.send_cli_cmd("memwrite 32 0x50071250 " +current_sco_quan + "\r\n")
        
        tb._config_freq_offset(current_sco)
        plc_tb_ctrl._debug("add sco: {} ppm".format(current_sco))
        if total_cnt%100 == 0:  
            # 停止之前的发送
            tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tx_num=0)
            #每发送100个测试帧，发5个beacon
            beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
            beacon_dict['num'] = 5
            beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
            # 等待5个信标都发送完成
            time.sleep(10*config.CLOCK_RATE)

        tdr.clear_port_rx_buf()
        if test_data['mpdu_type'] == plc_packet_helper.MAC_MPDU_SOF:
            tx_fc_pl_data = tc_common.send_sof_fc_pl_data(tmi_b=test_data['tmi_b'],
                                                          tmi_e=test_data['tmi_e'],
                                                          pb_num=1, ack_needed=False)
        else:
            tx_fc_pl_data = tc_common.send_sack_fc_pl_data()
        data_len = len(tx_fc_pl_data['payload']['data'])
        plc_tb_ctrl._trace_byte_stream("tx data", tx_fc_pl_data['payload']['data'])
        frame = tdr.read_frame(data_len, 1)

        total_cnt += 1
        #plc_tb_ctrl._trace_byte_stream("tx", tx_fc_pl_data['payload']['data'])
        #plc_tb_ctrl._trace_byte_stream("rx", frame)
        if frame == tx_fc_pl_data['payload']['data']:
            corr_cnt += 1
        succ_rate = float(corr_cnt) / packet_num
        plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
        ##assert time.time() < stop_time, "{}s timeout, total: {}, correct: {}".format(timeout, total_cnt,corr_cnt)
        
        #判断接收结果，调整频偏      
        if succ_rate < TARGET_SUCC_RATE :
            if total_cnt == packet_num :
                if sco_step==10:
                    plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    result_file.write("current_sco: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    sco_step = 1
                    current_sco -=9
                    succ_rate = float(corr_cnt) / packet_num
                    corr_cnt = 0
                    total_cnt = 0
                else:
                    plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    result_file.write("current_sco: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    sco_step = 1
                    current_sco -=10
                    succ_rate = float(corr_cnt) / packet_num
                    corr_cnt = 0
                    total_cnt = 0
                    break;
        else : #test under current current_sco passed
            plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
            result_file.write("current_sco: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_sco, total_cnt, corr_cnt, succ_rate))
            corr_cnt = 0
            total_cnt = 0
            succ_rate = float(corr_cnt) / packet_num
            plc_tb_ctrl._debug("sco {}".format(current_sco))
            # TB侧调整频偏和NTB
            current_sco += sco_step
    
"""
    packet_num = 100
    corr_cnt = 0
    total_cnt = 0
    # 负向频偏测试
    succ_rate = 0
    current_sco = -10
    sco_step = -10
    while succ_rate < TARGET_SUCC_RATE:
        # TB侧调整频偏和NTB
        tb._config_freq_offset(current_sco)
        plc_tb_ctrl._debug("add sco: {} ppm".format(current_sco))
        if total_cnt%100 == 0:  
            # 停止之前的发送
            tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tx_num=0)
            #每发送100个测试帧，发5个beacon
            beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
            beacon_dict['num'] = 5
            beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
            # 等待5个信标都发送完成
            time.sleep(10*config.CLOCK_RATE)
            
        tdr.clear_port_rx_buf()
        if test_data['mpdu_type'] == plc_packet_helper.MAC_MPDU_SOF:
            tx_fc_pl_data = tc_common.send_sof_fc_pl_data(tmi_b=test_data['tmi_b'],
                                                          tmi_e=test_data['tmi_e'],
                                                          pb_num=1, ack_needed=False)
        else:
            tx_fc_pl_data = tc_common.send_sack_fc_pl_data()
        data_len = len(tx_fc_pl_data['payload']['data'])
        plc_tb_ctrl._trace_byte_stream("tx data", tx_fc_pl_data['payload']['data'])
        frame = tdr.read_frame(data_len, 1)

        total_cnt += 1
        #plc_tb_ctrl._trace_byte_stream("tx", tx_fc_pl_data['payload']['data'])
        #plc_tb_ctrl._trace_byte_stream("rx", frame)
        if frame == tx_fc_pl_data['payload']['data']:
            corr_cnt += 1
        succ_rate = float(corr_cnt) / packet_num
        plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
        ##assert time.time() < stop_time, "{}s timeout, total: {}, correct: {}".format(timeout, total_cnt,corr_cnt)
        
        #判断接收结果，调整程控衰减器        
        if succ_rate < TARGET_SUCC_RATE :
            if packet_num==total_cnt:
                if sco_step==-10:
                    plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    result_file.write("current_sco: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    sco_step = -1
                    current_sco +=9
                    succ_rate = float(corr_cnt) / packet_num
                    corr_cnt = 0
                    total_cnt = 0
                else:
                    plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    result_file.write("current_sco: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_sco, total_cnt, corr_cnt, succ_rate))
                    succ_rate = float(corr_cnt) / packet_num
                    corr_cnt = 0
                    total_cnt = 0
                    break;
        else : #test under current current_sco passed
            plc_tb_ctrl._debug("current_sco: {}, total: {}, correct: {}, succ_rate:{}".format(current_sco, total_cnt, corr_cnt, succ_rate))
            result_file.write("current_sco: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_sco, total_cnt, corr_cnt, succ_rate))
            corr_cnt = 0
            total_cnt = 0
            succ_rate = float(corr_cnt) / packet_num
            current_sco += sco_step        
"""


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

    band=1
    TONE_MASK_TEST = 0
    plc_tb_ctrl._debug("band: {}, TONE_MASK: {}".format(band,TONE_MASK_TEST))

    #初始化程控衰减器，关闭噪声源
    current_fad = 0
    fadding.set_fadding(current_fad)

    # 在频段0发送20次频段设置命令
    tb._change_band(0)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段1发送20次频段设置命令
    tb._change_band(1)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)
    
    if config.TB_MPW==0:
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
    
    # 在指定频段发送20次测试命令帧，进入物理层透传测试模式
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='ENTER_PHY_TRANS_MODE', param=60*24)


    output_dir = BuiltIn().get_variable_value('${OUTPUT DIR}')
    timestamp_str = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    filename = 'awgn_result_' + timestamp_str + '.txt'
    meas_file_path = os.path.join(output_dir, filename)
    result_file = open(meas_file_path, 'w')
    
    for test_data in band0_test_data_set:
        result_file.write("*************************************\n")
        result_file.write("band {:d} tmi_b {:d} tmi_e {:d} \n".format(band,int(test_data['tmi_b']),int(test_data['tmi_e'])))
        check(tdr, tb, test_data,result_file)
    result_file.close()

