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
3.2.1.6 STA 在收到中央信标后发送发现信标的周期性和合法性测试
验证STA能否正确解析 CCO发出的中央信标，并按照时隙安排成功发出正确的发现信标
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

    plc_tb_ctrl._debug("activate tb")
    tc_common.activate_tb(tb,work_band = 1)

    meter_addr = '12-34-56-78-90-12'
    tc_common.sta_init(mtr, meter_addr)

    # 配置TB周期性发送中央信标
    plc_tb_ctrl._debug("configure TB to send central beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    # 等待STA1发送关联请求
    plc_tb_ctrl._debug("wait for assoc req")
    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_REQ'], timeout=30)
    assert fc.var_region_ver.dst_tei == 1
    assert mac_head.org_dst_tei == 1
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 1

    # 发送关联确认
    plc_tb_ctrl._debug("send assoc cnf to STA1")
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
    plc_tb_ctrl._debug("re-config central beacon which allocates discovery beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_slot_alloc['ncb_slot_num'] = 1
    beacon_slot_alloc['ncb_info'] = [dict(type=0, tei = 2)]
    beacon_slot_len = beacon_slot_alloc['beacon_slot_len']

    tb._configure_beacon(None, beacon_dict)

    # 等待STA1的发现信标
    plc_tb_ctrl._debug("wait for discovery beacon")
    stop_time = time.time() + tc_common.calc_timeout(20)
    beacon_cnt = 0
    central_beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_period_cnt = -1
    while beacon_cnt < 2:
        [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)

        assert time.time() < stop_time, "wait for beacon timeout"

        if beacon_period_cnt == beacon_payload.beacon_period_counter:
            continue

        beacon_period_cnt = beacon_payload.beacon_period_counter

        assert beacon_fc.var_region_ver.src_tei == 2
        assert beacon_fc.nid == beacon_dict['fc']['nid']

        sta_capability = plc_packet_helper.get_beacon_sta_capability(beacon_payload)
        beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
        tolerance = plc_packet_helper.us_to_ntb(700)
        assert plc_packet_helper.check_ntb(timestamp, beacon_fc.var_region_ver.timestamp, -tolerance, tolerance), \
            "Beacon time incorrect. RX: {}, TX: {}, Tolerance: {}".format(timestamp, beacon_fc.var_region_ver.timestamp, tolerance)
        offset = plc_packet_helper.ntb_diff(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp)
        exp_offset = plc_packet_helper.ms_to_ntb(beacon_slot_len * 3)
        assert plc_packet_helper.check_ntb(exp_offset,offset,  0, tolerance), \
                "Beacon offfset incorrect. Exp: {}, Real: {}".format(exp_offset, offset)

        assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
        assert beacon_payload.beacon_use_flag == beacon_dict['payload']['value']['beacon_use_flag'], \
               "wrong beacon use flag"
        assert beacon_payload.association_start == beacon_dict['payload']['value']['association_start']
        assert beacon_payload.network_org_flag == beacon_dict['payload']['value']['network_org_flag']
        assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']
        assert beacon_payload.cco_mac_addr == cco_mac, \
               "Wrong cco mac addr {}, {}".format(beacon_payload.cco_mac_addr, cco_mac)

        assert sta_capability.proxy_tei == 1
        assert sta_capability.sta_tei == 2
        assert sta_capability.level == 1
        assert sta_capability.role == 'STA_ROLE_STATION'

        assert beacon_slot_alloc['ncb_slot_num'] == central_beacon_slot_alloc['ncb_slot_num']
        assert beacon_slot_alloc['csma_phase_num'] == central_beacon_slot_alloc['csma_phase_num']
        assert beacon_slot_alloc['cb_slot_num'] == central_beacon_slot_alloc['cb_slot_num']
        assert beacon_slot_alloc['pb_slot_num'] == central_beacon_slot_alloc['pb_slot_num']
        assert beacon_slot_alloc['beacon_slot_len'] == central_beacon_slot_alloc['beacon_slot_len']
        assert beacon_slot_alloc['csma_slot_slice_len'] == central_beacon_slot_alloc['csma_slot_slice_len']
        assert beacon_slot_alloc['bind_csma_slot_phase_num'] == central_beacon_slot_alloc['bind_csma_slot_phase_num']
        assert beacon_slot_alloc['tdma_slot_len'] == central_beacon_slot_alloc['tdma_slot_len']
        assert beacon_slot_alloc['tdma_slot_lid'] == central_beacon_slot_alloc['tdma_slot_lid']
        assert beacon_slot_alloc['beacon_period_len'] == central_beacon_slot_alloc['beacon_period_len']
        assert 0 == cmp(beacon_slot_alloc['csma_slot_info'],
                        central_beacon_slot_alloc['csma_slot_info'])

        beacon_cnt += 1


