# -- coding: utf-8 --
# STA 从节点主动注册MAC 地址异常测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter


'''
1. DUT 上电，确保DUT 通过透明转发设备成功入网到软件平台。
2. 软件平台下发【启动从节点注册】命令。
3. 等待10s 后，软件平台下发【查询从节点注册结果】命令（源MAC 地址不匹配）。
4. 等待10s 后，软件平台下发【查询从节点注册结果】命令（目MAC 地址不匹配）。
check:
1. 在步骤3 中，确认DUT 是否不上报注册结果？
2. 在步骤4 中，确认DUT 是否不上报注册结果？
'''
timeout_flag = 0
def timeout_callback():
    global timeout_flag
    timeout_flag = 1
    return

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    global timeout_flag

    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    m = meter.Meter()
    m.open_port()

    cco_mac            = '00-00-C0-A8-01-01'
    meter_addr         = '01-00-00-00-00-00'
    invalid_addr       = '00-00-00-11-22-33'

    beacon_loss        = 0
    beacon_proxy_flag  = 0

    sta_tei            = 2
    apl_sn             = 0x1000

    # 1. DUT 上电，确保DUT 通过透明转发设备成功入网到CN-3 平台。

    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 2. 软件平台下发【启动从节点注册】命令。
    plc_tb_ctrl._debug("Step 2: simulate CCO to send downstream APL NODE REG START pkt...")

    dl_node_reg_start_pkt = tb._load_data_file(data_file='apl_node_reg_start_dl.yaml')
    dl_node_reg_start_pkt['body']['sn']          = apl_sn
    dl_node_reg_start_pkt['body']['reg_para']    = 'START_REG'
    dl_node_reg_start_pkt['body']['must_answer'] = 'NOT_MUST_ANSWER'

    msdu = plc_packet_helper.build_apm(dict_content=dl_node_reg_start_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)
    apl_sn += 1

    tc_common.wait_for_tx_complete_ind(tb)

    # 3. 等待10s 后，软件平台下发【查询从节点注册结果】命令（源MAC 地址不匹配）。
    plc_tb_ctrl._debug("Step 3: Wait 10 seconds and then simulate CCO to send downstream APL NODE REG QUERY pkt with invalid src MAC...")

    time.sleep(10)
    dl_node_reg_query_pkt = tb._load_data_file(data_file='apl_node_reg_query_dl.yaml')
    dl_node_reg_query_pkt['body']['sn']          = apl_sn
    dl_node_reg_query_pkt['body']['reg_para']    = 'QUERY_REG_RESULT'
    dl_node_reg_query_pkt['body']['must_answer'] = 'MUST_ANSWER'
    dl_node_reg_query_pkt['body']['src_mac']     = invalid_addr
    dl_node_reg_query_pkt['body']['dst_mac']     = meter_addr

    msdu = plc_packet_helper.build_apm(dict_content=dl_node_reg_query_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)
    apl_sn += 1

    tc_common.wait_for_tx_complete_ind(tb)

    # 4. 等待10s 后，软件平台下发【查询从节点注册结果】命令（目MAC 地址不匹配）。
    plc_tb_ctrl._debug("Step 4: Wait 10 seconds and then simulate CCO to send downstream APL NODE REG QUERY pkt with invalid dst MAC...")

    time.sleep(10)
    dl_node_reg_query_pkt = tb._load_data_file(data_file='apl_node_reg_query_dl.yaml')
    dl_node_reg_query_pkt['body']['sn']          = apl_sn
    dl_node_reg_query_pkt['body']['reg_para']    = 'QUERY_REG_RESULT'
    dl_node_reg_query_pkt['body']['must_answer'] = 'MUST_ANSWER'
    dl_node_reg_query_pkt['body']['src_mac']     = cco_mac
    dl_node_reg_query_pkt['body']['dst_mac']     = invalid_addr

    msdu = plc_packet_helper.build_apm(dict_content=dl_node_reg_query_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)
    apl_sn += 1

    tc_common.wait_for_tx_complete_ind(tb)

    # check1 在步骤3 中，确认DUT 是否不上报注册结果？
    # check2 在步骤4 中，确认DUT 是否不上报注册结果？

    pkt_id       = 'APL_NODE_REG_QUERY'
    timeout_val  = 10
    stop_time    = time.time() + timeout_val
    while True:

        [timestamp, fc, mac_frame_head, apm] = tc_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 2, timeout_callback)

        if time.time() >= stop_time:
            plc_tb_ctrl._debug("time out, not receive the unexpected upstream pkt APL_NODE_REG_QUERY...")
            break

        if apm is not None:
            plc_tb_ctrl._debug("rx apm = {}".format(apm))

        assert apm is None,    "unexpectedly received the upstream APL_NODE_REG_QUERY pkt err"

    time.sleep(1)

    m.close_port()



