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
3.2.1.2 CCO 通过代理组网过程中的中央信标测试
验证 CCO 能否成功发出中央信标，接收并解析来自 PCO1 的代理信标和来自 STA2 的 关
联请求。
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

    tc_common.sync_tb_configurations(tb, beacon_fc.nid, beacon_payload.nw_sn)

    stop_time = time.time() + tc_common.calc_timeout(120)
    next_phase = 1
    beacon_period_num = 0
    last_beacon_period_cnt = 0
    last_beacon_period_len = 0
    last_beacon_period_start_time = 0
    phase_a_beacon_payload = None
    while beacon_period_num < 10:
        plc_tb_ctrl._debug("period: {}, phase: {}".format(beacon_period_num, next_phase))

        [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None,
            lambda beacon_fc,beacon_payload: beacon_fc.var_region_ver.phase == next_phase)

        assert beacon_payload.beacon_type == 'CENTRAL_BEACON', 'not central beacon'
        assert beacon_payload.association_start == 1
        assert beacon_payload.cco_mac_addr == cco_mac_addr
        tolerance = plc_packet_helper.us_to_ntb(500 + (next_phase - 1) * 1500) # TODO: 波特率限制导致信标发送时间过长
        # 检查接收时间是否与发送时间一致
        assert plc_packet_helper.check_ntb(beacon_fc.var_region_ver.timestamp, timestamp, -tolerance, tolerance)

        if next_phase == 1:
            phase_a_beacon_payload = beacon_payload
            beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
            beacon_slot_len = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_slot_len)
            # 检查A相信标的发送时间，应落在A相时隙内
            assert plc_packet_helper.check_ntb(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp,
                0, beacon_slot_len)
            if beacon_period_num > 0:
                # 检查信标周期的开始时间是否符合信标周期
                assert (last_beacon_period_cnt + 1) == beacon_payload.beacon_period_counter
                diff = plc_packet_helper.ntb_diff(last_beacon_period_start_time, beacon_slot_alloc.beacon_period_start_time)
                tolerance = plc_packet_helper.ms_to_ntb(10)
                assert plc_packet_helper.check_ntb(diff, last_beacon_period_len, -tolerance, tolerance)
            last_beacon_period_start_time = beacon_slot_alloc.beacon_period_start_time
            last_beacon_period_cnt = beacon_payload.beacon_period_counter
            last_beacon_period_len = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_period_len)
            next_phase = 2
        elif 2 == next_phase:
            # 检查B相信标的发送时间，应落在B相时隙内
            assert plc_packet_helper.check_ntb(last_beacon_period_start_time, beacon_fc.var_region_ver.timestamp,
                beacon_slot_len, beacon_slot_len * 2)
            assert 0 == cmp(phase_a_beacon_payload, beacon_payload)
            next_phase = 3
        elif 3 == next_phase:
            # 检查C相信标的发送时间，应落在C相时隙内
            assert plc_packet_helper.check_ntb(last_beacon_period_start_time, beacon_fc.var_region_ver.timestamp,
                beacon_slot_len * 2, beacon_slot_len * 3)
            assert 0 == cmp(phase_a_beacon_payload, beacon_payload)
            next_phase = 1
            beacon_period_num += 1
        else:
            assert False

        assert time.time() < stop_time

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
    tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)

    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_CNF', 'MME_ASSOC_GATHER_IND'])
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

    tb.tb_uart.clear_tb_port_rx_buf()

    # 检查中央信标给STA1分配了发送信标时隙
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
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
    tb._send_msdu(msdu, tb.mac_head, src_tei = sta1_tei, dst_tei = 1)

    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype='MME_ASSOC_CNF')
    assert fc.var_region_ver.src_tei == 1
    assert fc.var_region_ver.dst_tei == sta1_tei
    assert mac_head.org_src_tei == 1
    assert (nmm.body.result == 'NML_ASSOCIATION_OK') or (nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK'), "assoc fail"
    assert nmm.body.mac_sta == sta_mac_addr[1]
    assert nmm.body.level == 2
    assert nmm.body.tei_proxy == sta1_tei
    sta2_tei = nmm.body.tei_sta

    tb.tb_uart.clear_tb_port_rx_buf()

    # 检查中央信标给STA1分配了代理信标时隙，给STA2分配了发现信标时隙
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    assert 2 == beacon_slot_alloc.ncb_slot_num
    assert sta1_tei == beacon_slot_alloc.ncb_info[0].tei
    # 代理信标
    assert 1 == beacon_slot_alloc.ncb_info[0].type
    assert sta2_tei == beacon_slot_alloc.ncb_info[1].tei
    # 发现信标
    assert 0 == beacon_slot_alloc.ncb_info[1].type

