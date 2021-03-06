# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import concentrator
import test_frame_helper
import plc_tb_ctrl
import tc_common
'''
3.2.2.1 CCO 对全网站点进行时隙规划并在规定时隙发送相应帧测试
验证 CCO 是否能够根据网络拓扑合理规划时隙以及是否在规定时隙内进行相应帧的发送
'''
def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    cct = concentrator.Concentrator()
    cct.open_port()

    tc_common.activate_tb(tb, 1, 0, 1)

    cct.clear_port_rx_buf()

    cco_mac_addr = '00-00-00-00-00-9C'
    tc_common.set_cco_mac_addr(cct, cco_mac_addr)

    sta_mac_addr = ['00-00-00-00-00-01', '00-00-00-00-00-02']
    tc_common.add_sub_node_addr(cct, sta_mac_addr)

    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    beacon_slot_len = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_slot_len)
    offset = plc_packet_helper.ntb_diff(beacon_slot_alloc.beacon_period_start_time,
                                        beacon_fc.var_region_ver.timestamp)
    index = offset / beacon_slot_len
    assert (index >= 0) and (index < 3), "incorrect beacon timestamp"

    tc_common.sync_tb_configurations(tb, beacon_fc.nid, beacon_payload.nw_sn)

    tb.tb_uart.clear_tb_port_rx_buf()

    # STA1入网
    req_dict = tb._load_data_file('nml_assoc_req.yaml')
    assert req_dict is not None

    req_dict['body']['mac'] = sta_mac_addr[0]
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = sta_mac_addr[0]
    tb.mac_head.dst_mac_addr = cco_mac_addr
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"

    msdu = plc_packet_helper.build_nmm(req_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1,auto_retrans=False)

    tb._wait_for_sack(timeout=1)

    [rx_time, fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_CNF',
                                                        'MME_ASSOC_GATHER_IND'],
                                                        timeout=15,
                                                        with_timestamp=True)
    assert fc.var_region_ver.src_tei == 1
    assert mac_head.org_src_tei == 1
    if nmm.header.mmtype == 'MME_ASSOC_CNF':
        assert (nmm.body.result == 'NML_ASSOCIATION_OK') or (nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK'), "assoc fail"
        assert nmm.body.mac_sta == sta_mac_addr[0]
        sta1_tei = nmm.body.tei_sta
    else:
        assert (nmm.body.result == 'ASSOC_GATHER_IND_PERMIT')
        assert nmm.body.sta_num == 1
        assert nmm.body.sta_list[0].addr == sta_mac_addr[0]
        sta1_tei = nmm.body.sta_list[0].tei
    assert nmm.body.level == 1

    beacon_period_start_time = beacon_slot_alloc.beacon_period_start_time
    beacon_period = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_period_len)
    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)
    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                beacon_period_start_time,
                                                beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        rx_time)
    index = offset / beacon_slot_len
    assert (index >= 3), "incorrect sof timestamp"

    # 检查中央信标给STA1分配了发送信标时隙
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15, None, None)
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    assert 1 == beacon_slot_alloc.ncb_slot_num
    assert sta1_tei == beacon_slot_alloc.ncb_info[0].tei
    # 发现信标
    assert 0 == beacon_slot_alloc.ncb_info[0].type

    # STA2通过STA1入网
    req_dict['body']['mac'] = sta_mac_addr[1]
    req_dict['body']['proxy_tei'] = [sta1_tei] + [0 for i in range(4)]
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = sta_mac_addr[1]
    tb.mac_head.dst_mac_addr = cco_mac_addr
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"

    msdu = plc_packet_helper.build_nmm(req_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei=sta1_tei, dst_tei=1,auto_retrans=False)

    tb._wait_for_sack(timeout=1)

    [rx_time, fc, mac_head, nmm] = tb._wait_for_plc_nmm(timeout=15,
                                               mmtype=['MME_ASSOC_CNF'],
                                               with_timestamp=True)
    assert fc.var_region_ver.src_tei == 1
    assert fc.var_region_ver.dst_tei == sta1_tei
    assert mac_head.org_src_tei == 1
    assert (nmm.body.result == 'NML_ASSOCIATION_OK') or (nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK'), "assoc fail"
    assert nmm.body.mac_sta == sta_mac_addr[1]
    assert nmm.body.level == 2
    assert nmm.body.tei_proxy == sta1_tei
    sta2_tei = nmm.body.tei_sta

    beacon_period_start_time = beacon_slot_alloc.beacon_period_start_time
    beacon_period = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_period_len)
    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)
    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                beacon_period_start_time,
                                                beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        rx_time)
    index = offset / beacon_slot_len
    assert (index >= 4), "incorrect sof timestamp"

    # 检查中央信标给STA1分配了代理信标时隙，给STA2分配了发现信标时隙
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15, None, None)
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    assert 2 == beacon_slot_alloc.ncb_slot_num
    assert sta1_tei == beacon_slot_alloc.ncb_info[0].tei
    # 代理信标
    assert 1 == beacon_slot_alloc.ncb_info[0].type
    assert sta2_tei == beacon_slot_alloc.ncb_info[1].tei
    # 发现信标
    assert 0 == beacon_slot_alloc.ncb_info[1].type

    # 模拟集中器AFN13HF1（“监控从节点”命令）启动集中器主动抄表业务，
    # 用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
    dl_afn13f1_pkt = tb._load_data_file(data_file='afn13f1_dl.yaml')
    dl_afn13f1_pkt['user_data']['value']['a']['src'] = cco_mac_addr
    dl_afn13f1_pkt['user_data']['value']['a']['dst'] = sta_mac_addr[1]
    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn13f1_pkt)
    assert msdu is not None
    cct.send_frame(msdu)

    # TODO: 测试规范里要求检查监控从节点上行报文，但如果没有抄表上行报文，
    # CCO怎么发送监控从节点上行报文

    [rx_time, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_CCT_METER_READ', 15)
    assert fc.var_region_ver.src_tei == 1, "src tei is not 1"
    assert fc.var_region_ver.dst_tei == sta1_tei, "dst tei is wrong"
    assert mac_frame_head.org_src_tei == 1, "org src tei is not 1"
    assert mac_frame_head.org_dst_tei == sta2_tei, "org dst tei is wrongs"

    beacon_period_start_time = beacon_slot_alloc.beacon_period_start_time
    beacon_period = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_period_len)
    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)
    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                beacon_period_start_time,
                                                beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        rx_time)
    index = offset / beacon_slot_len
    assert (index >= 5), "incorrect sof timestamp"
