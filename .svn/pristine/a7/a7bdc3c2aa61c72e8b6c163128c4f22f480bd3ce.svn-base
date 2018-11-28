# -- coding: utf-8 --

import os
import os.path
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from construct import *
import time
import config
import plc_packet_helper
import test_data_reader
import test_frame_helper
import plc_tb_ctrl
import tc_common
import fadding
import siggen
import sitrace_logger
import collections
import tonemask_narrow

current_fad = 0
NARROW_SOURCE = '0p5m'
if config.TB_AFE_TYPE:
	AFE_TX_GAIN_DB = 0	# atheros: -20,  weile: 0
else:
	AFE_TX_GAIN_DB = -20	# atheros: -20,  weile: 0
DAC_TX_SHIFT = 0
test_narrow = config.DUT_SIWAVE

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

def check(tdr, tb, test_data,result_file,siggen_plc):
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"

    TARGET_SUCC_RATE = 0.9
    packet_num = 200
    packet_interval = 250
    beacon_period = 100    
    beacon_num = 5
    beacon_interval = 1000
    current_fad = 0
    fadding_step = 10
    fadding_stage = 0
    fadding_ceil = 60

    plc_tb_ctrl._debug("step {}".format(test_data))
    
    # 停止之前的发送
    tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tx_num=0)
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 5
    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
    # 等待5个信标都发送完成
    time.sleep(10*config.CLOCK_RATE)
    
    corr_cnt = 0
    total_cnt = 0
    beacon_time = (packet_num + beacon_period - 1) / beacon_period * beacon_num * beacon_interval
    timeout = (packet_num * packet_interval + beacon_time) / 1000. + 1
    stop_time = time.time() + timeout
    succ_rate = 0
    plc_tb_ctrl._debug("exp total: {}, timeout: {}s".format(packet_num,timeout))
    
    fadding.set_fadding(current_fad)
    tb_sitrace = sitrace_logger.SitraceLogger(False)  # TB
    tb_sitrace.open_port()
    tc_common.tx_gain_control(tb_sitrace, afe_control=config.TB_AFE_TYPE, afe_gain_db=AFE_TX_GAIN_DB,dac_shift=DAC_TX_SHIFT, reg1104='a3d400')
    tb_sitrace.close_port()
    if test_narrow:
        
        dut_sitrace = sitrace_logger.SitraceLogger(True)  # DUT
        dut_sitrace.open_port()
        
        narrow_mask_file = "tonemask_narrow_b2_"+ NARROW_SOURCE +".txt"
        ###parameters ：tone_mask_file,ValidCarrierNum,band,narrow_f,afe_type
        tonemask_b2 = tonemask_narrow.ToneMaskConfig(narrow_mask_file,89,2,NARROW_SOURCE,config.DUT_AFE_TYPE)
        tonemask_b2.run()
        
        #plc_tb_ctrl._debug('memwrite 32 0x5007001C 0x200020a0\r\n')
        
        #dut_sitrace.send_cli_cmd('memwrite 32 0x5007001c 0x200020a0\r\n')
        if tonemask_b2.sync_ce_tm_enable:
            for cmd in tonemask_b2.add_A000_static_para:
                dut_sitrace.send_cli_cmd(cmd)
                plc_tb_ctrl._debug(cmd)
            time.sleep(2)
            
            for cmd in tonemask_b2.add_5007_static_para:
                dut_sitrace.send_cli_cmd(cmd)
                plc_tb_ctrl._debug(cmd)
            time.sleep(2) 
            
            for cmd in tonemask_b2.add_5007_tonemask:
                dut_sitrace.send_cli_cmd(cmd)
                plc_tb_ctrl._debug(cmd)
            time.sleep(2)
            
        for cmd in tonemask_b2.reg_narrow:
            dut_sitrace.send_cli_cmd(cmd)
            plc_tb_ctrl._debug(cmd)
        time.sleep(2)
        
        dut_sitrace.close_port()

    siggen_plc.arb_on(0)
    while succ_rate < TARGET_SUCC_RATE:
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
            '''
            tx_fc_pl_data = tc_common.send_periodic_sof_fc_pl_data(tmi_b=test_data['tmi_b'], tmi_e=test_data['tmi_e'],
                                                        pb_num=1, ack_needed=False, tx_interval = packet_interval, tx_num=packet_num+1,
                                                        beacon_period=beacon_period, beacon_num=beacon_num,beacon_interval=beacon_interval)
            '''
        else:
            tx_fc_pl_data = tc_common.send_sack_fc_pl_data()
        data_len = len(tx_fc_pl_data['payload']['data'])
        #plc_tb_ctrl._trace_byte_stream("tx data", tx_fc_pl_data['payload']['data'])
        frame = tdr.read_frame(data_len, 1)

        total_cnt += 1
        #plc_tb_ctrl._trace_byte_stream("tx", tx_fc_pl_data['payload']['data'])
        #plc_tb_ctrl._trace_byte_stream("rx", frame)
        if frame == tx_fc_pl_data['payload']['data']:
            corr_cnt += 1

        succ_rate = float(corr_cnt) / packet_num
        plc_tb_ctrl._debug("Fadding: {}, total: {}, correct: {}, succ_rate:{}".format(current_fad, total_cnt, corr_cnt, succ_rate))
        ##assert time.time() < stop_time, "{}s timeout, total: {}, correct: {}".format(timeout, total_cnt,corr_cnt)

        #判断接收结果，调整程控衰减器        
        if succ_rate < TARGET_SUCC_RATE :
            if total_cnt == packet_num : #fail at current fadding value
                if fadding_stage == 0 and current_fad != 0 : #
                    plc_tb_ctrl._debug("Fadding: {}, total: {}, correct: {}, succ_rate:{}".format(current_fad, total_cnt, corr_cnt, succ_rate))
                    result_file.write("Fadding: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_fad, total_cnt, corr_cnt, succ_rate))
                    corr_cnt = 0
                    total_cnt = 0
                    succ_rate = float(corr_cnt) / packet_num
                    fadding_ceil = current_fad
                    current_fad -= fadding_step
                    fadding_stage = 1
                    fadding_step = 1
                    fadding.set_fadding(current_fad)
                else :
                    plc_tb_ctrl._debug("Fadding: {}, total: {}, correct: {}, succ_rate:{}".format(current_fad, total_cnt, corr_cnt, succ_rate))
                    result_file.write("Fadding: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_fad, total_cnt, corr_cnt, succ_rate))
                    corr_cnt = 0
                    total_cnt = 0
                    succ_rate = float(corr_cnt) / packet_num
                    current_fad = 0
                    fadding_step = 10
                    fadding_stage = 0
                    fadding.set_fadding(current_fad)
                    break
            #else : continue on testing
        else : #test under current fadding passed
            plc_tb_ctrl._debug("Fadding: {}, total: {}, correct: {}, succ_rate:{}".format(current_fad, total_cnt, corr_cnt, succ_rate))
            result_file.write("Fadding: {}, total: {}, correct: {}, succ_rate:{}\n".format(current_fad, total_cnt, corr_cnt, succ_rate))
            corr_cnt = 0
            total_cnt = 0
            succ_rate = float(corr_cnt) / packet_num
            current_fad += fadding_step
            fadding.set_fadding(current_fad) 
            plc_tb_ctrl._debug("fadding {}".format(current_fad))       

def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    
    narrow function test by hanxiongchuan
    
    """
    
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    tc_common.activate_tb(tb, plc_packet_helper.WORK_BAND0, 0, 1)

    tdr = test_data_reader.TestDataReader()
    tdr.open_port()
    
    band=2
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
        tc_common.send_comm_test_command(test_mode_cmd='ENTER_PHY_TRANS_MODE', param=60000)

    # 设置信号发生器
    SG_ADDR = siggen.SG_ADDR
    WV_FORM = 'nrw_'+NARROW_SOURCE+'hz_fs100_iq'
    RF_SOURCE = config.RF_SOURCE
    SOF_VERSION = config.SOF_VERSION
    logger.info(siggen.SG_ADDR)
    
    if RF_SOURCE:
        plc_tb_ctrl._debug("RF out")
        #CENTER_FREQ = SOF_VERSION/2
        CENTER_FREQ = 3
        LEVEL = -20
        SAMPLE_RATE = SOF_VERSION
        siggen_config_rf(SG_ADDR,WV_FORM,SAMPLE_RATE,CENTER_FREQ,LEVEL)
    else:
        plc_tb_ctrl._debug("IQ out")
        SAMPLE_RATE = 200/config.CLOCK_RATE
        siggen_plc = siggen_config(SG_ADDR,WV_FORM,SAMPLE_RATE)
        
    siggen_plc.arb_off()
    
    output_dir = BuiltIn().get_variable_value('${OUTPUT DIR}')
    timestamp_str = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    filename = 'narrow_result_' + timestamp_str + '_'+NARROW_SOURCE+'_tone.txt'
    meas_file_path = os.path.join(output_dir, filename)
    result_file = open(meas_file_path, 'w')        
    for test_data in band0_test_data_set:
        result_file.write("*************************************\n")
        result_file.write("band {:d} tmi_b {:d} tmi_e {:d} \n".format(int(band),int(test_data['tmi_b']),int(test_data['tmi_e'])))
        check(tdr, tb, test_data,result_file,siggen_plc)
    result_file.close()    
    tdr.close_port()
        
def siggen_config(SG_ADDR,WV_FORM,SAMPLE_RATE):
    siggen_plc = siggen.SigGen_Keysight(SG_ADDR)
    siggen_plc.reset()
    siggen_plc.delete_all_waveform()
    siggen_plc.load_waveform(WV_FORM)
    siggen_plc.set_arb_sample_rate(SAMPLE_RATE/2)
    siggen_plc.set_alc(0)
    siggen_plc.play_waveform()
    siggen_plc.arb_on(0)
    siggen_plc.enable_modu_attn(0)
    siggen_plc.enable_iq_attn(0)
    return siggen_plc
    
def siggen_config_rf(SG_ADDR,WV_FORM,SAMPLE_RATE,CENTER_FREQ,LEVEL):
    siggen_plc = siggen.SigGen_Keysight(SG_ADDR)
    siggen_plc.reset()
    #siggen_plc.delete_all_waveform()
    #siggen_plc.load_waveform(WV_FORM)
    siggen_plc.set_arb_sample_rate(SAMPLE_RATE)
    siggen_plc.set_freq(CENTER_FREQ)
    siggen_plc.set_amplitude(LEVEL)
    siggen_plc.set_alc(1)
    siggen_plc.rf_on()

def write_reg_tonemask(tone_mask_file):
    add_5007 = []
    add_base = 0x500710C0
    add_cur = add_base - 4
    strc = ''
    fp_obj = open(tone_mask_file)
    for line in fp_obj.readlines():
        strc += str(int(line.strip(), 2) ^ 1)

    ss = ''
    ss1 = []
    for i in range(0, int(512 / 32)):
        for j in range(0, 32):
            ss += strc[j + i * 32]
        ss = ss[::-1]
        add_cur += 4
        add_str = hex(add_cur)
        s = '{:x}'.format(int(ss, 2))
        cmd_str_tone = 'memwrite 32 ' + add_str + ' 0x' + s
        add_5007.append(cmd_str_tone + '\r\n')
        ss1.append(s)
        ss = ''
    return add_5007
