# -- coding: utf-8 --
# STA 试运行机制（STA 升级后无法入网）
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter
import random
import tc_upg_common


'''
1. 执行测试用例2.1 正常升级步骤1~8。
2. STA 复位后 模拟CCO 不发送中央信标使STA 处于未入网状态。
3. 等待试运行时间结束，观察STA 是否发生复位。
4. 模拟CCO 正常发送中央信标，等待系统完成组网过程。
5. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息报文，
   且文件长度和CRC 是否与未升级前文件一致。
check:
1. 检测STA 在试运行失败后是否在设定的试运行时间完成复位操作。
2. 监测STA 在在试运行失败后是否切换至未升级前状态。
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"

    m = meter.Meter()
    m.open_port()

    cco_mac            = '00-00-C0-A8-01-01'
    meter_addr         = '12-34-56-78-90-12'
    sta_tei            = 2
    beacon_loss        = 0
    beacon_proxy_flag  = 0

    tc_upg_common.apl_upg_record_clear()

    sp_param = tc_upg_common.sp_param_st()
    ge_param = tc_upg_common.ge_param_st()

    ge_param.tb_inst = tb
    ge_param.sta_tei = sta_tei
    ge_param.cco_mac = cco_mac
    ge_param.sta_mac = meter_addr


    # 1.1 系统完成组网过程。
    plc_tb_ctrl._debug("Step 1.1: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 1.2.  软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。

    plc_tb_ctrl._debug("Step 1.2: simulate CCO to send Query Station Information packet")

    sp_param.pkt_id         = 'APL_STATE_INFO_QUERY'
    sp_param.blk_id         = 0
    sp_param.sent_blk_num   = None
    sp_param.out_order_flag = 0
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # record the old firmware size and crc
    old_file_crc  = []
    old_file_size = []
    old_file_crc.extend (tc_upg_common.apl_upg_dev_info[3]['value'])
    old_file_size.extend(tc_upg_common.apl_upg_dev_info[4]['value'])

    # 1.3.  软件平台模拟CCO 下发开始升级报文，查看是否能在规定时间内收到开始升级应答报文。
    plc_tb_ctrl._debug("Step 1.3: simulate CCO to send Start Upgrade packet")

    sp_param.pkt_id = 'APL_UPGRADE_START'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 1.4.  软件平台模拟CCO 下发传输文件数据报文(单播转广播)，查看是否能在规定时间收到待测STA 发送的广播传输文件数据报文。
    plc_tb_ctrl._debug("Step 1.4: simulate CCO to send Transfer File Data packet - uni-cast to broadcast")

    sp_param.pkt_id = 'APL_DATA_TRANSFER_BC'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 1.5.  软件平台模拟CCO 下发传输文件数据报文(单播)，升级块大小默认为最大400 字节，下同。
    # 1.6.  假定待下发传输文件数据报文总数为N 包，软件平台在完成30%*N,60%*N,100%*N 包传输文件数据报文下发后，
    #       模拟CCO 下发查询站点升级状态报文，查看是否能在规定时间内收到查询站点升级状态应答报文，
    #       30%，60%时查询块状态使用的块数为实际发送的块数，100%时使用0XFFFF 查询所有的块状态。
    plc_tb_ctrl._debug("Step 1.5: simulate CCO to send Transfer File Data packet - uni-cast only")
    plc_tb_ctrl._debug("Step 1.6: simulate CCO to insert Query STA Upgrade State pkt in 30%, 60%, 100% progress of File Data packet transferring")
    blk_num      = tc_upg_common.apl_upg_blk_num
    temp_blk_id  = blk_num / 3
    j            = 0
    for i in range (blk_num):
        if i == temp_blk_id:
            j += 1
            time.sleep(1)
            plc_tb_ctrl._debug("Step 1.6.{}: simulate CCO to insert Query STA Upgrade State pkt after {} File Data pkts were sent".format(j, temp_blk_id))
            sp_param.pkt_id         = 'APL_UPGRADE_STATE_QUERY'
            sp_param.sent_blk_num   = i # 按照实际发送数据块数量查询
            tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
            temp_blk_id  <<= 1

        sp_param.pkt_id       = 'APL_DATA_TRANSFER'
        sp_param.blk_id       = i
        sp_param.sent_blk_num = None
        tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    plc_tb_ctrl._debug("Step 1.6.3: simulate CCO to insert Query STA Upgrade State pkt after {} File Data pkts were sent".format(temp_blk_id))

    time.sleep(1)
    sp_param.pkt_id         = 'APL_UPGRADE_STATE_QUERY'
    sp_param.sent_blk_num   = None     # 本参数为None, 则查询所有数据块
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 1.7.  软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
    plc_tb_ctrl._debug("Step 1.7: simulate CCO to send Query Station Information packet")
    sp_param.pkt_id         = 'APL_STATE_INFO_QUERY'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    time.sleep(1)  # Later better to add some PEER upgrade state auto-check and wait mechanism

    # 1.8.  软件平台在完成所有传输文件数据报文下发后，模拟CCO 下发执行升级报文，并设定试运行时间和复位时间，等待STA 复位。
    plc_tb_ctrl._debug("Step 1.8: simulate CCO to send Execute Upgrade packet, and wait for STA to reset")
    sp_param.pkt_id         = 'APL_UPGRADE_EXEC'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 2. STA 复位后 模拟CCO 不发送中央信标使STA 处于未入网状态。
    time_to_rst = tc_upg_common.apl_upg_time_to_rst
    plc_tb_ctrl._debug("Step 2: after about {} seconds, simulate CCO to NOT send beacon, and make STA keep NO network connection...".format(time_to_rst))
    time.sleep(time_to_rst)
    beacon_loss = 1
    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 3. 等待试运行时间结束，观察STA 是否发生复位。
    try_running_time = tc_upg_common.apl_upg_try_running_time * tc_upg_common.upg_clock_rate
    plc_tb_ctrl._debug("Step 3: wait until try-running time {} seconds elapsed, and to observe whether STA Reset happens".format(try_running_time))
    time.sleep(try_running_time)
    # check 1. 检测STA 在试运行失败后是否在设定的试运行时间完成复位操作

    # 4. 模拟CCO 正常发送中央信标，等待系统完成组网过程。
    plc_tb_ctrl._debug("Step 4: simulate CCO to send beacon, and let STA finish the network connection")

    beacon_loss = 0
    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 5. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息报文，
    #    且文件长度和CRC 是否与未升级前文件一致。
    plc_tb_ctrl._debug("Step 5: simulate CCO to send Query Station Information packet")
    sp_param.pkt_id         = 'APL_STATE_INFO_QUERY'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    new_file_crc  = tc_upg_common.apl_upg_dev_info[3]['value']
    new_file_size = tc_upg_common.apl_upg_dev_info[4]['value']
    assert 0 == cmp(old_file_crc, new_file_crc),      "firmware crc is not the original one err"
    assert 0 == cmp(old_file_size, new_file_size),    "firmware size is not the original one err"
    # check 2. 监测STA 在在试运行失败后是否切换至未升级前状态。

    time.sleep(1)

    m.close_port()



