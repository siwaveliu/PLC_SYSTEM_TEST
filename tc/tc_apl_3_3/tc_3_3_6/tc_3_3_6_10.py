# -- coding: utf-8 --
# STA 无效报文处理机制
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter
import tc_upg_common



'''
1. 系统完成组网过程。STA 处于空闲态。
2. 软件平台模拟CCO 下发传输文件报文10 个，该报文为无效报文。
3. 软件平台模拟CCO 下发执行升级报文，该报文为无效报文。
4. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
5. 软件平台模拟CCO 下发开始升级报文，查看是否能在规定时间内收到开始升级应答报文。
6. 软件平台模拟CCO 下发开始升级报文，查看是否能在规定时间内收到开始升级应答报文。此报文为重复无效报文。
7. 假定待下发传输文件数据报文总数为N 包，软件平台模拟CCO 下发传输文件数据报文(单播)，升级块大小默认为最大400 字节，下同。
8. 软件平台在完成30%*N 包传输文件数据报文下发后，模拟CCO 下发开始升级报文，此报文为无效报文。
9. 软件平台在完成60%*N 包传输文件数据报文下发后，模拟CCO 下发执行升级报文，此报文为无效报文。
10. 软件平台在完成所有传输文件数据报文下发后模拟CCO 下发查询站点升级状态报文，查看是否能在规定时间内收到查询站点升级状态应答报文。
11. 软件平台模拟CCO 下发序号为（1~10/N）的传输文件数据报文，此报文为重复无效报文。
12. 模拟CCO 下发执行升级报文，并设定试运行时间和复位时间，等待STA 复位。
13. 等待系统完成组网过程。
14. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息报文，且文件长度和CRC 是否与下发的更新文件一致。
check:
1. CCO 在接收到无效报文时不影响完成正常升级流程。
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
    tc_upg_common.apl_upg_cco_load_firmware()

    sp_param = tc_upg_common.sp_param_st()
    ge_param = tc_upg_common.ge_param_st()

    ge_param.tb_inst = tb
    ge_param.sta_tei = sta_tei
    ge_param.cco_mac = cco_mac
    ge_param.sta_mac = meter_addr

    # 1. 系统完成组网过程。STA 处于空闲态。
    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 2. 软件平台模拟CCO 下发传输文件报文10 个，该报文为无效报文。
    plc_tb_ctrl._debug("Step 2: simulate CCO to send 10 Transfer File Data packets (invalid pkts)")
    for i in range (10):
        sp_param.pkt_id       = 'APL_DATA_TRANSFER'
        sp_param.blk_id       = i
        tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 3. 软件平台模拟CCO 下发执行升级报文，该报文为无效报文。
    plc_tb_ctrl._debug("Step 3: simulate CCO to send Execute Upgrade packet (invalid pkts)")
    sp_param.pkt_id           = 'APL_UPGRADE_EXEC'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 4. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
    plc_tb_ctrl._debug("Step 4: simulate CCO to send Query Station Information packet")

    sp_param.pkt_id           = 'APL_STATE_INFO_QUERY'
    sp_param.blk_id           = 0
    sp_param.sent_blk_num     = None
    sp_param.out_order_flag   = 0
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 5. 软件平台模拟CCO 下发开始升级报文，查看是否能在规定时间内收到开始升级应答报文。
    plc_tb_ctrl._debug("Step 5: simulate CCO to send Start Upgrade packet")

    sp_param.pkt_id           = 'APL_UPGRADE_START'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 6. 软件平台模拟CCO 下发开始升级报文，查看是否能在规定时间内收到开始升级应答报文。此报文为重复无效报文。
    plc_tb_ctrl._debug("Step 6: simulate CCO to send Start Upgrade packet (duplicated invalid pkt)")

    sp_param.pkt_id           = 'APL_UPGRADE_START'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 清空记录的bitmap，以便后续步骤验证
    tc_upg_common.apl_upg_bitmap = [0 for i in range((tc_upg_common.apl_upg_dft_blk_num + 7)/8)]

    # 7. 假定待下发传输文件数据报文总数为N 包，软件平台模拟CCO 下发传输文件数据报文(单播)，升级块大小默认为最大400 字节，下同。
    # 8. 软件平台在完成30%*N 包传输文件数据报文下发后，模拟CCO 下发开始升级报文，此报文为无效报文。
    # 9. 软件平台在完成60%*N 包传输文件数据报文下发后，模拟CCO 下发执行升级报文，此报文为无效报文。
    plc_tb_ctrl._debug("Step 7: simulate CCO to send Transfer File Data packet")
    blk_num      = tc_upg_common.apl_upg_blk_num
    temp_blk_id  = blk_num / 3
    for i in range (blk_num):
        if i == temp_blk_id:
            plc_tb_ctrl._debug("Step 8: simulate CCO to insert Start Upgrade packet (invalid) when File Data packets is transferring in 30% progress")
            sp_param.pkt_id   = 'APL_UPGRADE_START'
            tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

        if i == (temp_blk_id << 1):
            plc_tb_ctrl._debug("Step 9: simulate CCO to insert Execute Upgrade packet (invalid) when File Data packets is transferring in 60% progress")
            sp_param.pkt_id = 'APL_UPGRADE_EXEC'
            tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

        sp_param.pkt_id       = 'APL_DATA_TRANSFER'
        sp_param.blk_id       = i
        tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 10. 软件平台在完成所有传输文件数据报文下发后模拟CCO 下发查询站点升级状态报文，查看是否能在规定时间内收到查询站点升级状态应答报文。
    time.sleep(1)
    plc_tb_ctrl._debug("Step 10: simulate CCO to send Query STA Upgrade State pkt")
    sp_param.pkt_id           = 'APL_UPGRADE_STATE_QUERY'
    sp_param.sent_blk_num     = None     # 本参数为None, 则查询所有数据块
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 11. 软件平台模拟CCO 下发序号为（1~10/N）的传输文件数据报文，此报文为重复无效报文。
    temp_blk_id  = blk_num / 10
    plc_tb_ctrl._debug("Step 11: simulate CCO to send 1~{} Transfer File Data packets (invalid pkts)".format(temp_blk_id))
    for i in range (temp_blk_id):
        sp_param.pkt_id       = 'APL_DATA_TRANSFER'
        sp_param.blk_id       = i
        tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

#    time.sleep(1)  # Later better to add some PEER upgrade state auto-check and wait mechanism

    # 12. 模拟CCO 下发执行升级报文，并设定试运行时间和复位时间，等待STA 复位。
    plc_tb_ctrl._debug("Step 12: simulate CCO to send Execute Upgrade packet, and wait for STA to reset")
    sp_param.pkt_id           = 'APL_UPGRADE_EXEC'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    # 13. 等待系统完成组网过程。
    time_to_rst = tc_upg_common.apl_upg_time_to_rst * tc_upg_common.upg_clock_rate
    plc_tb_ctrl._debug("Step 13: Wait for system to finish network connecting, about {} seconds...".format(time_to_rst))
    time.sleep(time_to_rst)
    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 14. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息报文，
    #     且文件长度和CRC 是否与下发的更新文件一致。
    time_to_tr_timeout  = tc_upg_common.apl_upg_try_running_time * tc_upg_common.upg_clock_rate
    plc_tb_ctrl._debug("Wait for STA to pass try running time, about {} seconds...".format(time_to_tr_timeout))
    time.sleep(time_to_tr_timeout)
    
    plc_tb_ctrl._debug("Step 14: simulate CCO to send Query Station Information packet")
    sp_param.pkt_id          = 'APL_STATE_INFO_QUERY'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    assert tc_upg_common.apl_upg_is_new_image_ok(),       'STA current running image is not the downloaded image err'

    # check 1. CCO 在接收到无效报文时不影响完成正常升级流程。

    time.sleep(1)

    m.close_port()



