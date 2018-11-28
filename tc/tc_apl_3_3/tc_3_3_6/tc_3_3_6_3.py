# -- coding: utf-8 --
# STA 在线升级流程测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter
import tc_upg_common



'''
1. 系统完成组网过程。
2. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
3. 软件平台模拟CCO 下发开始升级报文，查看是否能在规定时间内收到开始升级应答报文。
4. 软件平台模拟CCO 下发传输文件数据报文(单播转广播)，查看是否能在规定时间收到待测STA 发送的广播传输文件数据报文。
5. 软件平台模拟CCO 下发传输文件数据报文(单播)，升级块大小默认为最大400 字节，下同。
6. 假定待下发传输文件数据报文总数为N 包，软件平台在完成30%*N,60%*N,100%*N 包传输文件数据报文下发后，
   模拟CCO 下发查询站点升级状态报文，查看是否能在规定时间内收到查询站点升级状态应答报文，
   30%，60%时查询块状态使用的块数为实际发送的块数，100%时使用0XFFFF 查询所有的块状态。
7. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
8. 软件平台在完成所有传输文件数据报文下发后，模拟CCO 下发执行升级报文，并设定试运行时间和复位时间，等待STA 复位。
9. 等待系统完成组网过程。
10. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息报文，
   且文件长度和CRC 是否与下发的更新文件一致。
check:
1. 检测STA(空闲态)能否在接收到查询站点信息报文后回复查询站点信息应答报文
2. 检测STA(空闲态)能否在接收到开始升级报文后回复开始升级应答报文
3. 检测STA(接收进行态)能否在接收到传输文件数据报文(单播转广播)时广播发送传输文件数据报文。
4. 检测STA(接收进行态)能否在接收到查询站点升级状态报文时回复查询站点升级状态应答报文。
5. 检测STA(升级完成态)在接收到执行升级报文后是否在规定时间间隔完成复位。复位时间间隔起始点为CCO发送执行升级报文的时间，
   终止点为STA 下挂虚拟电表收到STA下发的首个645 数据报文时间。
6. 检测STA 复位并重新组网完成后，能否在接收到查询站点信息报文后回复查询站点信息应答报文，
   且文件长度和CRC 是否与下发的更新文件一致。
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

    beacon_loss        = 0
    beacon_proxy_flag  = 0

    sta_tei            = 2

    tc_upg_common.apl_upg_record_clear()

    sp_param = tc_upg_common.sp_param_st()
    ge_param = tc_upg_common.ge_param_st()

    ge_param.tb_inst = tb
    ge_param.sta_tei = sta_tei
    ge_param.cco_mac = cco_mac
    ge_param.sta_mac = meter_addr


    plc_tb_ctrl._debug("firmware_length ={}, firmware_crc ={}".format(tc_upg_common.firmware_length, tc_upg_common.firmware_crc))

    # 1. 系统完成组网过程。
    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 2.  软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。

    plc_tb_ctrl._debug("Step 2: simulate CCO to send Query Station Information packet")

    sp_param.pkt_id         = 'APL_STATE_INFO_QUERY'
    sp_param.blk_id         = 0
    sp_param.sent_blk_num   = None
    sp_param.out_order_flag = 0
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
    # check 1. 检测STA(空闲态)能否在接收到查询站点信息报文后回复查询站点信息应答报文

    # 3.  软件平台模拟CCO 下发开始升级报文，查看是否能在规定时间内收到开始升级应答报文。
    plc_tb_ctrl._debug("Step 3: simulate CCO to send Start Upgrade packet")

    sp_param.pkt_id = 'APL_UPGRADE_START'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
    # check 2. 检测STA(空闲态)能否在接收到开始升级报文后回复开始升级应答报文

    # 4.  软件平台模拟CCO 下发传输文件数据报文(单播转广播)，查看是否能在规定时间收到待测STA 发送的广播传输文件数据报文。
    plc_tb_ctrl._debug("Step 4: simulate CCO to send Transfer File Data packet - uni-cast to broadcast")

    sp_param.pkt_id = 'APL_DATA_TRANSFER_BC'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
    # check 3. 检测STA(接收进行态)能否在接收到传输文件数据报文(单播转广播)时广播发送传输文件数据报文。

    # 5.  软件平台模拟CCO 下发传输文件数据报文(单播)，升级块大小默认为最大400 字节，下同。
    # 6.  假定待下发传输文件数据报文总数为N 包，软件平台在完成30%*N,60%*N,100%*N 包传输文件数据报文下发后，
    #     模拟CCO 下发查询站点升级状态报文，查看是否能在规定时间内收到查询站点升级状态应答报文，
    #     30%，60%时查询块状态使用的块数为实际发送的块数，100%时使用0XFFFF 查询所有的块状态。
    plc_tb_ctrl._debug("Step 5: simulate CCO to send Transfer File Data packet - uni-cast only")
    plc_tb_ctrl._debug("Step 6: simulate CCO to insert Query STA Upgrade State pkt in 30%, 60%, 100% progress of File Data packet transferring")
    blk_num      = tc_upg_common.apl_upg_blk_num
    temp_blk_id  = blk_num / 3
    j            = 0
    for i in range (blk_num):
        if i == temp_blk_id:
            j += 1
            time.sleep(1)
            plc_tb_ctrl._debug("Step 6.{}: simulate CCO to insert Query STA Upgrade State pkt after {} File Data pkts were sent".format(j, temp_blk_id))
            sp_param.pkt_id         = 'APL_UPGRADE_STATE_QUERY'
            sp_param.sent_blk_num   = i # 按照实际发送数据块数量查询
            tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
            temp_blk_id  <<= 1

        sp_param.pkt_id       = 'APL_DATA_TRANSFER'
        sp_param.blk_id       = i
        sp_param.sent_blk_num = None
        tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    time.sleep(1)

    plc_tb_ctrl._debug("Step 6.3: simulate CCO to insert Query STA Upgrade State pkt after {} File Data pkts were sent".format(temp_blk_id))
    sp_param.pkt_id         = 'APL_UPGRADE_STATE_QUERY'
    sp_param.sent_blk_num   = None     # 本参数为None, 则查询所有数据块
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
    # check 4. 检测STA(接收进行态)能否在接收到查询站点升级状态报文时回复查询站点升级状态应答报文。

    # 7.  软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
    plc_tb_ctrl._debug("Step 7: simulate CCO to send Query Station Information packet")
    sp_param.pkt_id         = 'APL_STATE_INFO_QUERY'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

#    time.sleep(1)  # Later better to add some PEER upgrade state auto-check and wait mechanism

    # 8.  软件平台在完成所有传输文件数据报文下发后，模拟CCO 下发执行升级报文，并设定试运行时间和复位时间，等待STA 复位。
    plc_tb_ctrl._debug("Step 8: simulate CCO to send Execute Upgrade packet, and wait for STA to reset")
    sp_param.pkt_id         = 'APL_UPGRADE_EXEC'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
#    m.clear_port_rx_buf()

    # 9.  等待系统完成组网过程。
    time_to_rst = tc_upg_common.apl_upg_time_to_rst * tc_upg_common.upg_clock_rate
    plc_tb_ctrl._debug("Step 9: Wait for system to finish network connecting, about {} seconds...".format(time_to_rst))
    time.sleep(time_to_rst)

    need_tb_active = False
    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag, need_tb_active)

    # check 5. 检测STA(升级完成态)在接收到执行升级报文后是否在规定时间间隔完成复位。
    #     复位时间间隔起始点为CCO 发送执行升级报文的时间，终止点为STA 下挂虚拟电表收到STA下发的首个645 数据报文时间。

    # 10. 软件平台模拟CCO 下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息报文，
    #     且文件长度和CRC 是否与下发的更新文件一致。
    time_to_tr_timeout  = tc_upg_common.apl_upg_try_running_time * tc_upg_common.upg_clock_rate
    plc_tb_ctrl._debug("Wait for STA to pass try running time, about {} seconds...".format(time_to_tr_timeout))
    time.sleep(time_to_tr_timeout)

    plc_tb_ctrl._debug("Step 10: simulate CCO to send Query Station Information packet")
    sp_param.pkt_id         = 'APL_STATE_INFO_QUERY'
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)

    assert tc_upg_common.apl_upg_is_new_image_ok(),       'STA current running image is not the downloaded image err'
    # check 6. 检测STA 复位并重新组网完成后，能否在接收到查询站点信息报文后回复查询站点信息应答报文，
    #     且文件长度和CRC 是否与下发的更新文件一致。

    time.sleep(1)

    m.close_port()



