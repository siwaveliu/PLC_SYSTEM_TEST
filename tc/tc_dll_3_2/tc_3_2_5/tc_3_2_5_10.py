# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import meter
import test_frame_helper
import plc_tb_ctrl
import tc_common


def check_sof(tb, mtr, sof_nid, sack_nid, sof_src_tei, sof_dst_tei,
              sack_src_tei, sack_dst_tei, rx_result, rx_status,meter_addr):

    tb.tb_uart.clear_tb_port_rx_buf()

    # 模拟 CCO 模块发送抄表请求 SOF 帧
    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')
    dl_meter_read_pkt['body']['sn'] = 2
    dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))

    dl_apl_645 = dl_meter_read_pkt['body']['data']
    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = sof_src_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 1
    tb.mac_head.remaining_hop_count = 1

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sof_src_tei, auto_retrans=False)

    result = tb._wait_for_sack(timeout=2)

    # 配置TB自动发送SACK, 第一次错误，第二次正确
    sack_data_list = [
        {"nid":sack_nid, "rx_result":rx_result, "rx_status":rx_status, "dst_tei":sack_dst_tei, "src_tei":sack_src_tei, "rx_pb_num": 1},
        {"nid":sof_nid, "rx_result":rx_result, "rx_status":rx_status, "dst_tei":sof_src_tei, "src_tei":sof_dst_tei, "rx_pb_num": 1},
    ]
    tb._config_sack_auto_reply_ex(sof_dst_tei, sack_data_list)

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

    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_ul('APL_CCT_METER_READ', 10)

    assert fc.var_region_ver.src_tei == sof_src_tei, "src tei is not 1"
    assert fc.var_region_ver.dst_tei == 1, "dst tei is wrong"
    assert fc.nid == sof_nid, "wrong nid"
    assert fc.var_region_ver.broadcast_flag == 0, "broadcast_flag should be 0"
    assert mac_frame_head.tx_type == "PLC_MAC_UNICAST", "should be unicast"
    assert mac_frame_head.org_src_tei == sof_src_tei, "wrong org_src_tei"
    assert mac_frame_head.org_dst_tei == 1, "wrong org_dst_tei"

    if ((sof_nid != sack_nid) or (sof_dst_tei != sack_src_tei)
            or (sof_src_tei != sack_dst_tei)):

        [timestamp, fc, mac_frame_head_2, apm_2] = tb._wait_for_plc_apm_ul('APL_CCT_METER_READ', 10)
        assert 1 == fc.var_region_ver.retrans_flag, "not retrans sof"
        assert mac_frame_head == mac_frame_head_2
        assert apm == apm_2

        [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_ul('APL_CCT_METER_READ', 10, timeout_cb=lambda:None)
        assert apm is None, "APL_CCT_METER_READ should not be received"


'''
3.2.5.10 STA 在发送单播 SOF 帧后，接收到非对应的 SACK 帧能否正确处理测试
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

    tc_common.activate_tb(tb, 1, 0, 1)

    meter_addr = '01-00-00-00-00-00'
    tc_common.sta_init(mtr, meter_addr)

    # 配置TB周期性发送中央信标
    plc_tb_ctrl._debug("configure TB to send central beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    nid = beacon_dict['fc']['nid']
    tb._configure_nw_static_para(nid, beacon_dict['payload']['value']['nw_sn'])

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
    assert beacon_fc.nid == nid, "wrong nid"
    assert beacon_payload.beacon_type == "DISCOVERY_BEACON", "not discovery beacon"

    plc_tb_ctrl._debug("step: nid not match")
    check_sof(tb, mtr, nid, nid+1, sta_tei, 1, 1, sta_tei, 0, 1,meter_addr)

    plc_tb_ctrl._debug("step: dst tei: 0xFFF")
    check_sof(tb, mtr, nid, nid, sta_tei, 1, 1, 0xFFF, 0, 1,meter_addr)

    plc_tb_ctrl._debug("step: dst tei not match")
    check_sof(tb, mtr, nid, nid, sta_tei, 1, 1, sta_tei+10, 0, 1,meter_addr)

    plc_tb_ctrl._debug("step: src tei not match")
    check_sof(tb, mtr, nid, nid, sta_tei, 1, 2, sta_tei, 0, 1,meter_addr)


