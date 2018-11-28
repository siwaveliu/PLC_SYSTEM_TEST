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
3.2.5.7 STA 对物理块校验异常的 SOF 帧的处理测试
验证 STA 对物理块校验异常的 SOF 帧的 处理
由于SIWP9006还不能控制PB CRC的对错，只能在STM32开发板上测试本case
'''


# 测试使用的基本TMI模式，依次对应pb_size:72,136,264,520
sof_tmi_config = [14, 4, 12, 9]

def check_sack(tb, sta_tei, nid, tmi_b, pb_num, broadcast_flag, err_pb_index, apl_pkt_sn):
    # 模拟 CCO 模块发送抄表请求 SOF 帧
    plc_tb_ctrl._debug("step11, send cct meter read dl packet")
    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')
    dl_meter_read_pkt['body']['sn'] = apl_pkt_sn
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
    tb.mac_head.msdu_len = len(msdu)
    tb.mac_head.msdu_sn = tb._gen_msdu_sn()

    mac_head = plc_packet_helper.build_mac_frame_head(dict_content=tb.mac_head)

    crc = plc_packet_helper.calc_crc32(msdu)
    mac_frame = mac_head + msdu + plc_packet_helper.build_mac_frame_crc(crc)

    pb_size = plc_packet_helper.query_pb_size_by_tmi(tmi_b, 0)
    sof_fc_pl_data = tc_common.build_sof_fc_pl_data_ex(mac_frame, nid,
                                                       1, sta_tei, tmi_b, 0,
                                                       pb_num, broadcast_flag=broadcast_flag)

    data = list(sof_fc_pl_data['payload']['data'])
    modify_pos = 16 + err_pb_index * pb_size + 55
    data[modify_pos] = chr((ord(data[modify_pos])+1)&0xFF)
    sof_fc_pl_data['payload']['data'] = "".join(data)
    tb._send_fc_pl_data(sof_fc_pl_data)

    # step16: 等SACK
    plc_tb_ctrl._debug("step12, wait for sack")
    [timestamp, fc] = tb._wait_for_sack(timeout=2)
    assert fc.nid == nid, "wrong nid"
    assert fc.mpdu_type == "PLC_MPDU_SACK", "not SACK"
    assert fc.var_region_ver.dst_tei == 1, "wrong dst_tei"
    assert fc.var_region_ver.src_tei == sta_tei, "wrong src_tei"
    status = (~(1 << err_pb_index)) & 0xF
    assert fc.var_region_ver.rx_status == status, "wrong rx_status"
    assert fc.var_region_ver.rx_result == 1, "wrong rx_result"
    assert fc.var_region_ver.rx_pb_num == pb_num, "wrong rx_pb_num"

    ''' TODO: 且一致性模块分析接收“选择确认帧”的时序应满足 SOF 帧对帧长的时间设定。即：
        SOF 帧载荷占用时间 + RIFS(2300us) + SACK 帧占用时间 + CIFS(400us) = SOF 帧长
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
    plc_tb_ctrl._debug("step3-1, configure TB to send central beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    # 等待STA1发送关联请求
    plc_tb_ctrl._debug("step3-2, wait for assoc req")
    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_REQ'], timeout=15)
    assert fc.var_region_ver.dst_tei == 1
    assert mac_head.org_dst_tei == 1
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 1

    # 发送关联确认
    plc_tb_ctrl._debug("step7, send assoc cnf to STA1")
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
    plc_tb_ctrl._debug("step8-1, re-config central beacon which allocates discovery beacon")
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
    plc_tb_ctrl._debug("step8-2, wait for discovery beacon")
    central_beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None, None)
    assert beacon_fc.nid == beacon_dict['fc']['nid'], "wrong nid"
    assert beacon_payload.beacon_type == "DISCOVERY_BEACON", "not discovery beacon"

    sn = 0
    for tmi_b in sof_tmi_config:
        for i in range(4):
            plc_tb_ctrl._debug("pb_num:{},tmi_b:{},broadcast_flag:0".format(4, tmi_b))
            check_sack(tb, sta_tei, beacon_fc.nid, tmi_b, 4, 0, i, sn)
            sn += 1

        for i in range(4):
            plc_tb_ctrl._debug("pb_num:{},tmi_b:{},broadcast_flag:1".format(4, tmi_b))
            check_sack(tb, sta_tei, beacon_fc.nid, tmi_b, 4, 1, i, sn)
            sn += 1


