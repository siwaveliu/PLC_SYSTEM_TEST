# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import meter
import test_frame_helper
import plc_tb_ctrl
import tc_common

'''
3.2.1.5 STA 多级站点入网过程中的代理信标测试
验证 STA 能否成功发出代理信标和发现信标
'''
def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    mtr = meter.Meter()
    mtr.open_port()

    tc_common.activate_tb(tb,work_band = 1)

    meter_addr = '12-34-56-78-90-12'
    tc_common.sta_init(mtr, meter_addr)

    # 配置TB周期性发送中央信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    # 等待STA1发送关联请求
    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_REQ'], timeout=30)
    assert fc.var_region_ver.dst_tei == 1
    assert mac_head.org_dst_tei == 1
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 1

    # 发送关联确认
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf.yaml')
    assert asso_cnf_dict is not None

    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = 1
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"

    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0, broadcast_flag=1, ack_needed=False)

    # 修改TB发送的中央信标, 添加发现信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_slot_alloc['ncb_slot_num'] = 1
    beacon_slot_alloc['ncb_info'] = [dict(type=0, tei = 2)]
    beacon_slot_len = beacon_slot_alloc['beacon_slot_len']

    tb._configure_beacon(None, beacon_dict)

    # 等待STA1的发现信标
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
    assert beacon_fc.var_region_ver.src_tei == 2
    sta_capability = plc_packet_helper.get_beacon_sta_capability(beacon_payload)
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    tolerance = plc_packet_helper.us_to_ntb(700)
    assert plc_packet_helper.check_ntb(timestamp, beacon_fc.var_region_ver.timestamp, -tolerance, tolerance), \
           "Beacon time incorrect. RX: {}, TX: {}, Tolerance: {}".format(timestamp, beacon_fc.var_region_ver.timestamp, tolerance)
    offset = plc_packet_helper.ntb_diff(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp)
    exp_offset = plc_packet_helper.ms_to_ntb(beacon_slot_len * 3)
    assert plc_packet_helper.check_ntb(exp_offset, offset, 0, tolerance), \
            "Beacon offfset incorrect. Exp: {}, Real: {}".format(exp_offset, offset)

    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert sta_capability.proxy_tei == 1
    assert sta_capability.sta_tei == 2
    assert sta_capability.level == 1
    assert sta_capability.role == 'STA_ROLE_STATION'

    # 模拟二级站点STA2发送关联请求给STA1
    req_dict = tb._load_data_file('nml_assoc_req.yaml')
    assert req_dict is not None
    sta2_mac_addr = '00-00-00-00-00-05'
    req_dict['body']['mac'] = sta2_mac_addr
    req_dict['body']['proxy_tei'] = [2, 0, 0, 0, 0]
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.hop_limit = 2
    tb.mac_head.remaining_hop_count = 2
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = sta2_mac_addr
    tb.mac_head.dst_mac_addr = cco_mac
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"

    msdu = plc_packet_helper.build_nmm(req_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 2)

    # 等待STA1转发关联请求
    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_REQ'])
    assert fc.var_region_ver.src_tei == 2
    assert fc.var_region_ver.dst_tei == 1
    assert mac_head.org_dst_tei == 1
    cmp(nmm, req_dict)

    # 发送STA2的关联确认给STA1
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf.yaml')
    assert asso_cnf_dict is not None

    asso_cnf_dict['body']['mac_sta'] = sta2_mac_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['level'] = 2
    asso_cnf_dict['body']['tei_sta'] = 3
    asso_cnf_dict['body']['tei_proxy'] = 2
    tb.mac_head.org_dst_tei = 2
    tb.mac_head.org_src_tei = 1
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = sta2_mac_addr
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"

    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 2)

    # 等待STA1转发关联确认
    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_CNF'])
    assert fc.var_region_ver.broadcast_flag == 1, "invalid broadcast_flag"
    assert fc.var_region_ver.src_tei == 2, "invalid src tei"
    assert fc.var_region_ver.dst_tei == 0xFFF, "invalid dst tei"
    assert mac_head.tx_type == "PLC_LOCAL_BROADCAST", "invalid tx type"
    assert mac_head.org_src_tei == 2, "invalid org src tei"

    cmp(nmm, asso_cnf_dict)

    # 修改TB发送的中央信标, 添加发现信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_slot_alloc['ncb_slot_num'] = 2
    beacon_slot_alloc['ncb_info']= [dict(type=1, tei=2), dict(type=0, tei=3)]
    beacon_slot_len = beacon_slot_alloc['beacon_slot_len']

    tb._configure_beacon(None, beacon_dict, True)

    # 等待STA1的代理信标
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
    assert beacon_fc.var_region_ver.src_tei == 2
    sta_capability = plc_packet_helper.get_beacon_sta_capability(beacon_payload)
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    tolerance = plc_packet_helper.us_to_ntb(700)
    assert plc_packet_helper.check_ntb(timestamp, beacon_fc.var_region_ver.timestamp, -tolerance, tolerance)
    offset = plc_packet_helper.ntb_diff(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp)
    assert plc_packet_helper.check_ntb(plc_packet_helper.ms_to_ntb(beacon_slot_len * 3), offset, 0, tolerance)
    assert beacon_payload.beacon_type == 'PROXY_BEACON'
    assert sta_capability.proxy_tei == 1
    assert sta_capability.sta_tei == 2
    assert sta_capability.level == 1
    assert sta_capability.role == 'STA_ROLE_PCO'
