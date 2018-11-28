# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import concentrator
import test_frame_helper
import plc_tb_ctrl
import tc_common


def check_sof(tb, cct, sof_nid, sack_nid, sta_tei, sack_src_tei, dst_tei, rx_result, rx_status):
    # step12
    # 配置TB自动发送SACK
    tb._config_sack_tei(sack_nid, sta_tei, sack_src_tei, dst_tei,
                        rx_result=rx_result, rx_status=rx_status)

    # 模拟集中器AFN13HF1（“监控从节点”命令）启动集中器主动抄表业务，
    # 用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
    frame = concentrator.build_gdw1376p2_frame(data_file='afn13f1_dl.yaml')
    assert frame is not None
    cct.send_frame(frame)

    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_CCT_METER_READ', 15)
    assert fc.var_region_ver.src_tei == 1, "src tei is not 1"
    assert fc.var_region_ver.dst_tei == sta_tei, "dst tei is wrong"
    assert fc.nid == sof_nid, "wrong nid"
    assert fc.var_region_ver.broadcast_flag == 0, "broadcast_flag should be 0"

    assert mac_frame_head.tx_type == "PLC_MAC_UNICAST", "should be unicast"

    if (sof_nid == sack_nid)  and (0 == rx_result) and (dst_tei == 1) and (sta_tei == sack_src_tei):
        [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_CCT_METER_READ', 15, timeout_cb=lambda:None)
        assert apm is None, "APL_CCT_METER_READ should not be received"
    else:
        [timestamp, fc, mac_frame_head_2, apm_2] = tb._wait_for_plc_apm_dl('APL_CCT_METER_READ', 15)
        assert 1 == fc.var_region_ver.retrans_flag, "not retrans sof"
        assert mac_frame_head == mac_frame_head_2
        assert apm == apm_2



'''
3.2.5.5 CCO 在发送单播 SOF 帧后，接收非对应的 SACK 帧后能否正确处理测试
验证CCO在发送单播sof帧后，接收非对应的SACK帧后能否正确处理
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

    # nid不匹配的SACK，CCO重传
    check_sof(tb, cct, beacon_fc.nid, beacon_fc.nid + 1, sta_tei,
              sta_tei, 1, 0, 1)

    '''
    TODO: 前一个抄表没有应答，按目前的实现, CCO会对下一个立即会失败，而不是触发新的抄表请求
    '''

    time.sleep(tc_common.calc_timeout(70))
    tb.tb_uart.clear_tb_port_rx_buf()

    # 类型 2 主要参数：
    # 网络标识正确，接收结果=0，接收状态=所有物理块接收成功;目的 TEI=0xfff；
    # 源 TEI= 对应 SOF 的目的 TEI，接收物理块个数=对应 SOF 帧个数。
    # CCO重传
    check_sof(tb, cct, beacon_fc.nid, beacon_fc.nid, sta_tei,
              sta_tei, 0xFFF, 0, 1)

    time.sleep(tc_common.calc_timeout(70))
    tb.tb_uart.clear_tb_port_rx_buf()

    # 类型 3 主要参数：
    # 网络标识正确，接收结果=0，接收状态=所有物理块接收成功;目的 TEI！ =1 且不为0xfff
    # 源 TEI=对应 SOF 的目的 TEI，接收物理块个数=对应 SOF 帧个数。
    # CCO重传
    check_sof(tb, cct, beacon_fc.nid, beacon_fc.nid, sta_tei, sta_tei, 10, 0, 1)

    time.sleep(tc_common.calc_timeout(70))
    tb.tb_uart.clear_tb_port_rx_buf()

    # 类型 4 主要参数：
    # 网络标识正确，接收结果=0，接收状态=所有物理块接收成功;目的 TEI = 1，源 TEI!=
    # 对应 SOF 帧的目的 TEI；接收物理块个数=对应 SOF 帧个数。
    # CCO重传
    check_sof(tb, cct, beacon_fc.nid, beacon_fc.nid, sta_tei, sta_tei + 10, 1, 0, 1)

