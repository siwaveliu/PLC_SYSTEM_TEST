# -- coding: utf-8 --
# STA 对应用数据内容非645 格式的校时消息处理测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter


'''
1. 软件平台选择组网用例，待测设备STA 上电；
2. 组网用例通过透明物理设备模拟CCO 发送组网相关帧，配合待测STA 和模拟电表，组建一级网络；
3. 软件平台选择广播校时测试用例；
4. 测试用例通过透明物理设备模拟CCO 发送非645 格式, 且非698.45 格式的广播校时SOF
帧；并启动定时器（3S）；
5. 在定时器耗尽前，若模拟电表未接收到该帧，则在定时器耗尽后，将接收结果送给一致性
评价模块；若接收到非645 格式且非698.45 格式帧，则测试失败。
6. 一致性评价模块判断测试结果。
check:
1、验证STA 可以正确处理应用数据不符合DL/T645-2007 格式且非698.45 格式的广播校时消息。
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    global timeout_flag

    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    m = meter.Meter()
    m.open_port()

    cco_mac            = '00-00-C0-A8-01-01'
    meter_addr         = '01-00-00-00-00-00'
    invalid_addr       = '00-00-00-11-22-33'

    beacon_loss        = 0
    beacon_proxy_flag  = 0

    sta_tei            = 2
    apl_sn             = 0x1000

    # 1. 软件平台选择组网用例，待测设备STA 上电；
    # 2. 组网用例通过透明物理设备模拟CCO 发送组网相关帧，配合待测STA 和模拟电表，组建一级网络；

    plc_tb_ctrl._debug("Step 1, 2: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 3. 软件平台选择广播校时测试用例；
    # 4. 测试用例通过透明物理设备模拟CCO 发送非645 格式, 且非698.45 格式的广播校时SOF帧；并启动定时器（3S）；
    plc_tb_ctrl._debug("Step 3, 4: simulate CCO to send downstream APL TIME CALI pkt with invalid content, and start 3-seconds-timout timer...")

    dl_time_cali_pkt = tb._load_data_file(data_file='apl_time_cali_dl.yaml')
    dl_time_cali_pkt['body']['sn']  = apl_sn

    # make the data field not valid 645 format pkt
    dl_time_cali_pkt['body']['data'][0]  = 0
    dl_time_cali_pkt['body']['data'][7]  = 0

    dl_time_cali_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_time_cali_pkt['body']['data']))
    dl_apl_645 = dl_time_cali_pkt['body']['data']
    msdu = plc_packet_helper.build_apm(dict_content=dl_time_cali_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)

    tc_common.wait_for_tx_complete_ind(tb)

#    timeout_val = 3
#    stop_time = time.time() + timeout_val

    # 5. 在定时器耗尽前，若模拟电表未接收到该帧，则在定时器耗尽后，将接收结果送给一致性评价模块；
    #    若接收到非645 格式且非698.45 格式帧，则测试失败。

    plc_tb_ctrl._debug("Step 5: simulate METER to receive the TIME CALI packet...")

    dlt645_frame = m.wait_for_dlt645_frame(code = 'TIME_CAL', dir = 'REQ_FRAME', timeout = 10)
    # 6. 一致性评价模块判断测试结果。
    plc_tb_ctrl._debug("Step 6: check whether the 645 packet in payload of APL TIME CALI pkt sent by CCO is not forwarded out...")
    assert dlt645_frame is None,               "received unexpected time_cali 645 pkt err"


#    dl_mtr_645_lst = []
#    dl_mtr_645_str = meter.build_dlt645_07_frame(dict_content=dlt645_frame)
#    tc_common.convert_str2lst(dl_mtr_645_str, dl_mtr_645_lst)

#    assert cmp(dl_mtr_645_lst, dl_apl_645) == 0,  "STA -> Meter - 645 packet err"

    time.sleep(1)

    m.close_port()



