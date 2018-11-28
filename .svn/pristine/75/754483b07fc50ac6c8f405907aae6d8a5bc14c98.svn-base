# -- coding: utf-8 --
# STA 查询站点信息测试
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
2. 软件平台模拟CCO 乱序信息元素下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
check:
1. 检测STA 处于空闲态能否在接收到查询站点信息报文后正确回复查询站点信息应答报文
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

    # 1. 系统完成组网过程。
    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 2. 软件平台模拟CCO 乱序信息元素下发查询站点信息报文，查看是否能在规定时间内收到查询站点信息应答报文。
    plc_tb_ctrl._debug("Step 2: simulate CCO to send Query Station Information packet, with info list out-of-orde")

    sp_param.pkt_id         = 'APL_STATE_INFO_QUERY'
    sp_param.blk_id         = 0
    sp_param.sent_blk_num   = None
    sp_param.out_order_flag = 1
    tc_upg_common.apl_upg_cco_single_tx_rx(ge_param, sp_param)
    # check 1. 检测STA 处于空闲态能否在接收到查询站点信息报文后正确回复查询站点信息应答报文

    time.sleep(1)

    m.close_port()



