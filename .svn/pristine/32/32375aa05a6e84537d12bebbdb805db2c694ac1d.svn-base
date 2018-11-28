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
3.2.3.2 CCO 的冲突退避测试
验证待测 CCO 冲突帧退避间隔是否符合协议规定退避间隔
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

    # 添加从节点地址
    meter_addr = '00-00-00-00-00-01'
    tc_common.add_sub_node_addr(cct, [meter_addr])

    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    tc_common.sync_tb_configurations(tb, beacon_fc.nid, beacon_payload.nw_sn)

    [beacon_fc, curr_beacon] = tb._wait_for_plc_beacon(30)[1:]

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb._send_nmm('nml_assoc_req.yaml', tb.mac_head, 0, 1)

    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_CNF', 'MME_ASSOC_GATHER_IND'])
    assert fc.var_region_ver.src_tei == 1
    assert mac_head.org_src_tei == 1
    if nmm.header.mmtype == 'MME_ASSOC_CNF':
        assert (nmm.body.result == 'NML_ASSOCIATION_OK') or (nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK'), "assoc fail"
        assert nmm.body.mac_sta == '00-00-00-00-00-01'
    else:
        assert (nmm.body.result == 'ASSOC_GATHER_IND_PERMIT')
        assert nmm.body.sta_num == 1
        assert nmm.body.sta_list[0].addr == '00-00-00-00-00-01'

    # 模拟集中器AFN13HF1（“监控从节点”命令）启动集中器主动抄表业务，
    # 用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
    frame = concentrator.build_gdw1376p2_frame(data_file='afn13f1_dl.yaml')
    assert frame is not None
    cct.send_frame(frame)

    stop_time = time.time() + tc_common.calc_timeout(10)
    cnt = 0
    while True:
        assert time.time() < stop_time, "10s timeout"

        result = tb._wait_for_fc_pl_data(tb._check_fc_pl_payload, timeout=1)

        if result is not None:
            [timestamp, fc, data] = result
            if ("PLC_MPDU_SOF" == fc.mpdu_type):
                mac_frame = data
                if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_APP":
                    continue

                apm_data = mac_frame.msdu.data
                apm = plc_packet_helper.parse_apm(apm_data, True)
                if apm is None:
                    continue

                if ("APL_CCT_METER_READ" != apm.header.id):
                    plc_tb_ctrl._debug("not APL_CCT_METER_READ packet")
                    continue

                frame_len = fc.var_region_ver.frame_len * 10

                if 0 == cnt:
                    assert fc.var_region_ver.retrans_flag == 0, "wrong retrans flag"
                else:
                    assert fc.var_region_ver.retrans_flag == 1, "wrong retrans flag"

                    diff = plc_packet_helper.ntb_diff(last_rx_time, timestamp)
                    diff = plc_packet_helper.ntb_to_us(diff)
                    assert diff > 400, "wrong interval"

                last_rx_time = timestamp

                cnt += 1

                if cnt > 3:
                    break









