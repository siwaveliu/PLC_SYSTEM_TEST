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
3.2.3.4 STA 的冲突退避测试
验证待测 STA 冲突帧退避间隔是否符合协议规定退避间隔
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
    tc_common.activate_tb(tb, work_band=1)

    meter_addr = '12-34-56-78-90-12'
    tc_common.sta_init(mtr, meter_addr)

    # 配置TB周期性发送中央信标
    plc_tb_ctrl._debug("configure TB to send central beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
    beacon_period = plc_packet_helper.ms_to_ntb(beacon_dict['period'])
    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    # 等待STA1发送关联请求
    plc_tb_ctrl._debug("wait for assoc req")
    stop_time = time.time() + tc_common.calc_timeout(30)
    timeout = stop_time - time.time()
    cnt = 0
    while True:
        result = tb._wait_for_fc_pl_data(tb._check_fc_pl_payload, timeout=timeout)
        timeout = stop_time - time.time()

        if result is not None:
            [timestamp, fc, data] = result
            if ("PLC_MPDU_SOF" == fc.mpdu_type):
                mac_frame = data
                if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_NMM":
                    continue

                nmm_data = mac_frame.msdu.data
                nmm = plc_packet_helper.parse_nmm(nmm_data)
                if nmm is None:
                    continue

                if ("MME_ASSOC_REQ" != nmm.header.mmtype):
                    plc_tb_ctrl._debug("not MME_ASSOC_REQ")
                    continue

                phase = plc_packet_helper.map_phase_str_to_value(nmm.body.phase_0)

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









