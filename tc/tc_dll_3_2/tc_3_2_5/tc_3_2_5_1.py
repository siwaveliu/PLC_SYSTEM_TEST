# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import concentrator
import test_frame_helper
import plc_tb_ctrl
import tc_common

# 测试使用的基本TMI模式，依次对应pb_size:72,136,264,520
sof_tmi_config = [14, 4, 11, 10]

'''
3.2.5.1 CCO 对符合标准的 SOF 帧的处理测试
验证 CCO 对符合标准的 SOF 帧的处理
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

    # step2
    cco_mac_addr = '00-00-00-00-00-9C'
    tc_common.set_cco_mac_addr(cct, cco_mac_addr)

    # 添加从节点地址
    meter_addr = '00-00-00-00-00-01'
    tc_common.add_sub_node_addr(cct, [meter_addr])

    # step3
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]
    assert beacon_payload.beacon_type == "CENTRAL_BEACON", "not central beacon"

    tc_common.sync_tb_configurations(tb, beacon_fc.nid, beacon_payload.nw_sn)

    [beacon_fc, curr_beacon] = tb._wait_for_plc_beacon(30)[1:]

    # step4
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = meter_addr
    tb.mac_head.dst_mac_addr = cco_mac_addr
    tb._send_nmm('nml_assoc_req.yaml', tb.mac_head, 0, 1)

    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_CNF', 'MME_ASSOC_GATHER_IND'], timeout=15)
    assert fc.var_region_ver.src_tei == 1
    assert mac_head.org_src_tei == 1
    if nmm.header.mmtype == 'MME_ASSOC_CNF':
        assert (nmm.body.result == 'NML_ASSOCIATION_OK') or (nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK'), "assoc fail"
        assert nmm.body.mac_sta == meter_addr
        sta_tei = nmm.body.tei_sta
    else:
        assert (nmm.body.result == 'ASSOC_GATHER_IND_PERMIT')
        assert nmm.body.sta_num == 1
        assert nmm.body.sta_list[0].addr == meter_addr
        sta_tei = nmm.body.sta_list[0].tei



    # step8
    [beacon_fc, curr_beacon] = tb._wait_for_plc_beacon(30)[1:]
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(curr_beacon)
    assert beacon_slot_alloc.ncb_slot_num == 1, "no ncb slot allocated"
    assert beacon_slot_alloc.ncb_info[0].tei == sta_tei, "discovery/proxy beacon is not allocated"

    # step11
    tb._config_sta_tei(sta_tei, 1, 1, 1, meter_addr)

    # step12
    # 配置TB自动发送SACK
    tb._config_sack_tei(beacon_fc.nid, sta_tei, sta_tei, 1)

    for pb_num in [1, 4]:
        for tmi_b in sof_tmi_config:
            # 模拟集中器AFN13HF1（“监控从节点”命令）启动集中器主动抄表业务，
            # 用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
            frame = concentrator.build_gdw1376p2_frame(data_file='afn13f1_dl.yaml')
            assert frame is not None
            cct.send_frame(frame)

            [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_CCT_METER_READ', 15)
            assert fc.var_region_ver.src_tei == 1, "src tei is not 1"
            assert fc.var_region_ver.dst_tei == sta_tei, "dst tei is wrong"

            dl_meter_read_pkt_sn = apm.body.sn
            ul_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_ul.yaml')
            ul_meter_read_pkt['body']['sn'] = dl_meter_read_pkt_sn
            msdu = plc_packet_helper.build_apm(dict_content=ul_meter_read_pkt, is_dl=False)
            assert msdu is not None, "msdu is None"

            tb.mac_head.org_dst_tei = 1
            tb.mac_head.org_src_tei = sta_tei
            tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
            tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=sta_tei, dst_tei=1,
                        tmi_b=tmi_b, pb_num=pb_num, auto_retrans=False)

            # step16: 等SACK
            [timestamp, fc] = tb._wait_for_sack(timeout=2)
            assert fc.nid == beacon_fc.nid, "wrong nid"
            assert fc.mpdu_type == "PLC_MPDU_SACK", "not SACK"
            assert fc.var_region_ver.dst_tei == sta_tei, "wrong dst_tei"
            assert fc.var_region_ver.src_tei == 1, "wrong src_tei"
            if 1 == pb_num:
                assert fc.var_region_ver.rx_status == 1, "wrong rx_status"
            elif 4 == pb_num:
                assert fc.var_region_ver.rx_status == 0xF, "wrong rx_status"
            assert fc.var_region_ver.rx_result == 0, "wrong rx_result"
            assert fc.var_region_ver.rx_pb_num == pb_num, "wrong rx_pb_num"

            ''' TODO: 且一致性模块分析接收“选择确认帧”的时序应满足 SOF 帧对帧长的时间设定。即：
                SOF 帧载荷占用时间 + RIFS(2300us) + SACK 帧占用时间 + CIFS(400us) = SOF 帧长
            '''










