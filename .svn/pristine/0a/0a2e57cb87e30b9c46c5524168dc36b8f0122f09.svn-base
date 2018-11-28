# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import meter
import test_frame_helper
import plc_tb_ctrl
import tc_common

# 测试使用的基本TMI模式，依次对应pb_size:72,136,264,520
sof_tmi_config = [14, 4, 12, 9]

def check_sack(tb, sta_tei, nid, tmi_b, pb_num, broadcast_flag):
    # 模拟 CCO 模块发送抄表请求 SOF 帧
    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')
    dl_meter_read_pkt['body']['sn'] = 2
    dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))

    dl_apl_645 = dl_meter_read_pkt['body']['data']
    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 1
    tb.mac_head.remaining_hop_count = 1

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei,broadcast_flag=broadcast_flag,
                    tmi_b=tmi_b, pb_num=pb_num, auto_retrans=False)

    # step16: 等SACK
    [timestamp, fc] = tb._wait_for_sack(timeout=2)
    assert fc.nid == nid, "wrong nid"
    assert fc.mpdu_type == "PLC_MPDU_SACK", "not SACK"
    assert fc.var_region_ver.dst_tei == 1, "wrong dst_tei"
    assert fc.var_region_ver.src_tei == sta_tei, "wrong src_tei"
    if 1 == pb_num:
        assert fc.var_region_ver.rx_status == 1, "wrong rx_status"
    elif 4 == pb_num:
        assert fc.var_region_ver.rx_status == 0xF, "wrong rx_status"
    assert fc.var_region_ver.rx_result == 0, "wrong rx_result"
    assert fc.var_region_ver.rx_pb_num == pb_num, "wrong rx_pb_num"

    ''' TODO: 且一致性模块分析接收“选择确认帧”的时序应满足 SOF 帧对帧长的时间设定。即：
        SOF 帧载荷占用时间 + RIFS(2300us) + SACK 帧占用时间 + CIFS(400us) = SOF 帧长
            '''


'''
3.2.5.6 STA 对符合标准的 SOF 帧的处理测试
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

    sta_tei = asso_cnf_dict['body']['tei_sta']

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
    # 增加了一个信标时隙，缩短CSMA时隙避免总时间超过信标周期
    beacon_slot_alloc['csma_slot_info'][1]['slot_len'] = 600
    beacon_slot_len = beacon_slot_alloc['beacon_slot_len']

    tb._configure_beacon(None, beacon_dict, True)

    # 等待STA1的发现信标
    plc_tb_ctrl._debug("wait for discovery beacon")
    central_beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
    assert beacon_fc.nid == beacon_dict['fc']['nid'], "wrong nid"
    assert beacon_payload.beacon_type == "DISCOVERY_BEACON", "not discovery beacon"

    for pb_num in [1, 4]:
        for tmi_b in sof_tmi_config:
            plc_tb_ctrl._debug("pb_num:{},tmi_b:{},broadcast_flag:0".format(pb_num, tmi_b))
            check_sack(tb, sta_tei, beacon_fc.nid, tmi_b, pb_num, 0)

    for pb_num in [1, 4]:
        for tmi_b in sof_tmi_config:
            plc_tb_ctrl._debug("pb_num:{},tmi_b:{},broadcast_flag:1".format(pb_num, tmi_b))
            check_sack(tb, sta_tei, beacon_fc.nid, tmi_b, pb_num, 1)







