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
3.2.2.2 STA/PCO 在规定时隙发送相应帧测试
验证 STA/PCO 是否能够在中央信标指定的时隙内完成信标帧以及 SOF 帧的发送
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

    tc_common.activate_tb(tb, work_band=1)

    meter_addr = '12-34-56-78-90-12'
    tc_common.sta_init(mtr, meter_addr)

    # 配置TB周期性发送中央信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_slot_len = plc_packet_helper.ms_to_ntb(beacon_slot_alloc['beacon_slot_len'])
    beacon_period = plc_packet_helper.ms_to_ntb(beacon_slot_alloc['beacon_period_len'])
    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    tb._config_sack_tei(beacon_dict['fc']['nid'], 1, 1, 0,
                        rx_result=0, rx_status=0x1)

    # 等待STA1发送关联请求
    [rx_time, fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_REQ'], timeout=15, with_timestamp=True)
    assert fc.var_region_ver.dst_tei == 1
    assert mac_head.org_dst_tei == 1
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 1

    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                beacon_period_start_time,
                                                beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        rx_time)
    index = offset / beacon_slot_len
    assert (index >= 3), "incorrect sof timestamp"

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

    result = None
    result = tb._wait_for_plc_beacon(15, timeout_cb=lambda:None)
    assert result == None, "beacon should not be received"

    tb._config_sack_tei(beacon_dict['fc']['nid'], 1, 1, 2,
                        rx_result=0, rx_status=0x1)

    # 修改TB发送的中央信标, 添加发现信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_slot_alloc['ncb_slot_num'] = 1
    beacon_slot_alloc['ncb_info'] = [dict(type=0, tei = 2)]

    tb._configure_beacon(None, beacon_dict, True)

    # 等待STA1的发现信标
    [rx_time, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
    assert beacon_fc.var_region_ver.src_tei == 2
    sta_capability = plc_packet_helper.get_beacon_sta_capability(beacon_payload)
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert sta_capability.proxy_tei == 1
    assert sta_capability.sta_tei == 2
    assert sta_capability.level == 1
    assert sta_capability.role == 'STA_ROLE_STATION'

    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                beacon_period_start_time,
                                                beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        beacon_fc.var_region_ver.timestamp)
    index = offset / beacon_slot_len
    assert 3 == index, "incorrect beacon timestamp"

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

    #tb._wait_for_sack(timeout=1)

    # 等待STA1转发关联请求
    [rx_time, fc, mac_head, nmm] = tb._wait_for_plc_nmm(timeout=15, mmtype=['MME_ASSOC_REQ'], with_timestamp=True)
    assert fc.var_region_ver.src_tei == 2
    assert fc.var_region_ver.dst_tei == 1
    assert mac_head.org_dst_tei == 1
    cmp(nmm, req_dict)
    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                 beacon_period_start_time,
                                                 beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        rx_time)
    index = offset / beacon_slot_len
    assert index >= 4, "incorrect sof timestamp"

    # 模拟CCO发送STA2的关联确认给STA1
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

    #tb._wait_for_sack(timeout=1)

    # 等待STA1转发关联确认
    [rx_time, fc, mac_head, nmm] = tb._wait_for_plc_nmm(timeout=15, mmtype=['MME_ASSOC_CNF'], with_timestamp=True)
    assert fc.var_region_ver.broadcast_flag == 1, "invalid broadcast_flag"
    assert fc.var_region_ver.src_tei == 2, "invalid src tei"
    assert fc.var_region_ver.dst_tei == 0xFFF, "invalid dst tei"
    assert mac_head.tx_type == "PLC_LOCAL_BROADCAST", "invalid tx type"
    assert mac_head.org_src_tei == 2, "invalid org src tei"
    cmp(nmm, asso_cnf_dict)

    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                 beacon_period_start_time,
                                                 beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        rx_time)
    index = offset / beacon_slot_len
    assert index >= 4, "incorrect sof timestamp"

    time.sleep(1)
    tb.tb_uart.clear_tb_port_rx_buf()

    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15, None, None)
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON', "beacon type should still be discovery beacon"

    # 修改TB发送的中央信标, 一级站点改为发送代理信标
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_slot_alloc['ncb_slot_num'] = 2
    beacon_slot_alloc['ncb_info']= [dict(type=1, tei=2), dict(type=0, tei=3)]

    tb._configure_beacon(None, beacon_dict, True)

    # 等待STA1的代理信标
    wait_time = 10
    while wait_time != 0:
        [rx_time, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
        if beacon_payload.beacon_type == 'PROXY_BEACON':
            break
        wait_time -= 1
        
    assert beacon_fc.var_region_ver.src_tei == 2
    sta_capability = plc_packet_helper.get_beacon_sta_capability(beacon_payload)
    assert beacon_payload.beacon_type == 'PROXY_BEACON'
    assert sta_capability.proxy_tei == 1
    assert sta_capability.sta_tei == 2
    assert sta_capability.level == 1
    assert sta_capability.role == 'STA_ROLE_PCO'

    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                beacon_period_start_time,
                                                beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        beacon_fc.var_region_ver.timestamp)
    index = offset / beacon_slot_len
    assert 3 == index, "incorrect beacon timestamp"

    # 模拟 CCO 模块发送抄表请求 SOF 帧
    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')
    dl_meter_read_pkt['body']['sn'] = 2
    dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))

    dl_apl_645 = dl_meter_read_pkt['body']['data']
    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = 2  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 1
    tb.mac_head.remaining_hop_count = 1

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=2,auto_retrans=False)

    # step16: 等SACK
    [timestamp, fc] = tb._wait_for_sack(timeout=2)
    assert fc.var_region_ver.dst_tei == 1, "wrong dst_tei"
    assert fc.var_region_ver.src_tei == 2, "wrong src_tei"
    assert fc.var_region_ver.rx_status == 1, "wrong rx_status"
    assert fc.var_region_ver.rx_result == 0, "wrong rx_result"
    assert fc.var_region_ver.rx_pb_num == 1, "wrong rx_pb_num"

    #wait for meter read request
    plc_tb_ctrl._debug("wait for meter read request")
    dlt645_frame = mtr.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 10)
    assert dlt645_frame.head.code == "DATA_READ", "not data read command"
    assert dlt645_frame.body.value.DI0 == 0x33, "DI0 should be 0x33"
    assert dlt645_frame.body.value.DI1 == 0x33, "DI1 should be 0x33"
    assert dlt645_frame.body.value.DI2 == 0x34, "DI2 should be 0x34"
    assert dlt645_frame.body.value.DI3 == 0x34, "DI3 should be 0x34"
    dis = [dlt645_frame.body.value.DI0,
           dlt645_frame.body.value.DI1,
           dlt645_frame.body.value.DI2,
           dlt645_frame.body.value.DI3]
    # 比较这个645报文
    dlt645_frame = meter.build_dlt645_07_frame(dict_content=dlt645_frame)
    dlt645_frame = [ord(c) for c in dlt645_frame]
    if dlt645_frame != dl_meter_read_pkt['body']['data']:
        plc_tb_ctrl._debug("rx 645 frame: {}".format(dlt645_frame))
        plc_tb_ctrl._debug("tx 645 frame: {}".format(dl_meter_read_pkt['body']['data']))
        assert False, "dlt645 not same"

    reply_data = [0xA5, 0x38, 0x33, 0x39, 0x53, 0x39, 0x37, 0x4B]
    tc_common.send_dlt645_reply_frame(mtr, meter_addr, dis, reply_data, len(reply_data))

    [rx_time, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_ul('APL_CCT_METER_READ', 15)

    while not plc_packet_helper.ntb_inside_range(rx_time,
                                                beacon_period_start_time,
                                                beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    offset = plc_packet_helper.ntb_diff(beacon_period_start_time,
                                        rx_time)
    index = offset / beacon_slot_len
    assert index >= 5, "incorrect sof timestamp"