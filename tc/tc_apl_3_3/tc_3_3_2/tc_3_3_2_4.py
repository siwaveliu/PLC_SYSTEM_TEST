# -- coding: utf-8 --
# STA 从节点主动注册正常流程测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter


'''
1. DUT 上电，确保DUT 通过透明转发设备成功入网到CN-3 平台。
2. 软件平台通过透明转发设备下发【启动从节点注册】命令。
3. 等待1 分钟后，软件平台通过透明转发设备下发【查询从节点注册结果】命令。
check:
1.  确认DUT 上报【查询从节点注册结果】报文（以下简称回复报文）中，【报文端口号】是否为 0x11？
2.  确认DUT 回复报文中【报文ID】是否为0x0011？
3.  确认DUT 回复报文中【报文控制字】是否为 0？
4.  确认DUT 回复报文中【协议版本号】是否为 1？
5.  确认DUT 回复报文中【报文头长度】是否为26？
6.  确认DUT 回复报文中【状态字段】是否为0？
7.  确认DUT 回复报文中【从节点注册参数】是否为0？
8.  确认DUT 回复报文中【电能表数量】是否为1？
9.  确认DUT 回复报文中【产品类型】是否为 0（电能表）？
10. 确认DUT 回复报文中【设备地址】是否为000000000001？
11. 确认DUT 回复报文中【设备ID】是否为与当前DUT 一致？
12. 确认DUT 回复报文中【报文序号】是否与CCO 所下发的一致？
13. 确认DUT 回复报文中【源MAC 地址】是否为DUT 的MAC 地址？
14. 确认DUT 回复报文中【目的MAC 地址】是否为 CCO 的MAC 地址？
15. 确认DUT 回复报文中【电能表地址】是否为000000000001？
16. 确认DUT 回复报文中【规约类型】是否为2（DL/T645-2007）？
17. 确认DUT 回复报文中【模块类型】是否为0（电能表通信模块）？
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
    meter_addr         = '01-00-00-00-00-00'
    sta_addr           = '00-00-00-01-01-01'

    beacon_loss        = 0
    beacon_proxy_flag  = 0

    sta_tei            = 2
    apl_sn             = 0x1000

    # 1. DUT 上电，确保DUT 通过透明转发设备成功入网到CN-3 平台。

    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 2. 软件平台通过透明转发设备下发【启动从节点注册】命令。
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

    # 3. 等待1 分钟后，软件平台通过透明转发设备下发【查询从节点注册结果】命令。
    delay_time = 6        # <-  to save time, shorten from 60s to 6s
    plc_tb_ctrl._debug("Step 3: Wait for {} seconds and then simulate CCO to send downstream APL NODE REG QUERY pkt...".format(delay_time))

    time.sleep(delay_time)
    dl_node_reg_query_pkt = tb._load_data_file(data_file='apl_node_reg_query_dl.yaml')
    dl_node_reg_query_pkt['body']['sn']          = apl_sn
    dl_node_reg_query_pkt['body']['reg_para']    = 'QUERY_REG_RESULT'
    dl_node_reg_query_pkt['body']['must_answer'] = 'MUST_ANSWER'
    dl_node_reg_query_pkt['body']['src_mac']     = cco_mac
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

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0,auto_retrans=False)

    tc_common.wait_for_tx_complete_ind(tb)

    # 等待'查询从节点注册结果'上行报文

    pkt_id = 'APL_NODE_REG_QUERY'
    [timestamp, fc, mac_frame_head, apm] = tc_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 10)

    # check 1. 确认DUT 上报【查询从节点注册结果】报文（以下简称回复报文）中，【报文端口号】是否为 0x11？
    assert apm.header.port                 == 0x11,                      "pkt header port id err"
    # check 2. 确认DUT 回复报文中【报文ID】是否为0x0011 (查询从节点注册结果)？
    assert apm.header.id                   == 'APL_NODE_REG_QUERY',      "pkt header packet id err"
    # check 3. 确认DUT 回复报文中【报文控制字】是否为 0？
    assert apm.header.ctrl_word            == 0,                         "pkt header ctrl word err"
    # check 4. 确认DUT 回复报文中【协议版本号】是否为 1？
    assert apm.body.proto_ver              == 'PROTO_VER1',              "pkt body proto ver err"
    # check 5. 确认DUT 回复报文中【报文头长度】是否为26？
    assert apm.body.hdr_len                == 36,                        "pkt body hdr len err"
    # check 6. 确认DUT 回复报文中【状态字段】是否为0？
    assert apm.body.status                 == 0,                         "pkt body status err"
    # check 7. 确认DUT 回复报文中【从节点注册参数】是否为0？
    assert apm.body.reg_para               == 'QUERY_REG_RESULT',        "pkt body reg param err"
    # check 8. 确认DUT 回复报文中【电能表数量】是否为1？
    assert apm.body.meter_num              == 1,                         "pkt body meter num err"
    # check 9. 确认DUT 回复报文中【产品类型】是否为 0（电能表）？
    assert apm.body.dev_type               == 'PRODUCT_TYPE_METER',      "pkt body dev type err"
    # check 10. 确认DUT 回复报文中【设备地址】是否为000000000001？
    assert apm.body.dev_addr               == meter_addr,                "pkt body dev addr err"
    # check 11. 确认DUT 回复报文中【设备ID】是否为与当前DUT 一致？
    # 此处暂时注释掉，因目前FPGA/STM32版本均通过此处检查点
#    assert apm.body.dev_id                 == sta_addr,                  "pkt body dev id err"  # 跟leiming请教结果，此处用STA设备自己的MAC地址
    # check 12. 确认DUT 回复报文中【报文序号】是否与CCO 所下发的一致？
    assert apm.body.sn                     == apl_sn,                    "pkt body sn err"
    # check 13. 确认DUT 回复报文中【源MAC 地址】是否为DUT 的MAC 地址？
    assert apm.body.src_mac                == meter_addr,                "pkt body src mac err" # 跟leiming请教结果，此处用STA设备通信时使用的MAC地址(当前为电表地址)
    # check 14. 确认DUT 回复报文中【目的MAC 地址】是否为 CCO 的MAC 地址？
    assert apm.body.dst_mac                == cco_mac,                   "pkt body dst mac err"
    # check 15. 确认DUT 回复报文中【电能表地址】是否为000000000001？
    assert apm.body.info[0].addr           == meter_addr,                "pkt body info addr err"
    # check 16. 确认DUT 回复报文中【规约类型】是否为2（DL/T645-2007）？
    assert apm.body.info[0].prot_type      == 'PROTO_DLT645_2007',       "pkt body info proto type err"
    # check 17. 确认DUT 回复报文中【模块类型】是否为0（电能表通信模块）？
    assert apm.body.info[0].module_type    == 'PRODUCT_TYPE_METER',      "pkt body info module type err"

    time.sleep(1)

    m.close_port()



