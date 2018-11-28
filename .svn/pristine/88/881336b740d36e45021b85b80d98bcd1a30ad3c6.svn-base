# -- coding: utf-8 --
# STA 处理通信测试帧测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter


'''
1. 连接设备，将待测STA连接在特定相线，上电初始化；
2. 软件平台模拟电表，在收到待测STA的读表号请求后，通过串口向其下发表地址；
3. 软件平台模拟CCO通过透明物理设备向待测STA设备发送“中央信标”，在收到待测STA发出的“关联请求”后，向其发送“关联确认”，令其入网；
4. 软件平台模拟CCO通过透明物理设备向待测STA设备发送“通信测试帧”（目的地址非待测STA），同时启动定时器（定时时长2s），定时器溢出前，查看是否不会收到待测STA从串口发出的通信测试数据；
5. 软件平台模拟CCO通过透明物理设备向待测STA设备发送正确的“通信测试帧”，同时启动定时器（定时时长2s），定时器溢出前，查看是否能够收到待测STA从串口发出的通信测试数据；
注：所有需要“选择确认帧”确认的，当没有收到“选择确认帧”，则fail。所有的本测试例不关心的报文被收到后，直接丢弃，不做判断。
check:
1. STA在收到通信测试帧（目的站点非自身）后，是否不会通过串口发出通信测试数据；
2. CCO在收到异常的“本地通信模块报文通信测试”376.2报文后，是否不会发出“通信测试命令”宽带PLC应用层报文并通过串口发送“否认”376.2报文；
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
    invalid_tei        = sta_tei + 0x10
    apl_sn             = 0x1000

    # 1. 连接设备，将待测STA连接在特定相线，上电初始化；
    # 2. 软件平台(电能表)模拟电表，在收到待测STA请求读表号后，向其下发电表地址信息()。
    # 3. 软件平台模拟CCO通过透明物理设备向待测STA设备发送“中央信标”，
    #    在收到待测STA发出的“关联请求”后，向其发送“关联确认”，令其入网；
    plc_tb_ctrl._debug("Step 1, 2, 3: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 4. 软件平台模拟CCO通过透明物理设备向待测STA设备发送“通信测试帧”（目的地址非待测STA），
    #    同时启动定时器（定时时长2s），定时器溢出前，查看是否不会收到待测STA从串口发出的通信测试数据；
    plc_tb_ctrl._debug("Step 4: simulate CCO to send Comm Test pkt to STA, with dst addr is not STA...")

    dl_event_report_pkt = tb._load_data_file(data_file='apl_comm_test_dl.yaml')

    dl_event_report_pkt['body']['test_mode_cmd']  = 'ENTER_NON_TEST_MODE'
#    dl_event_report_pkt['body']['length']       = 0
#    dl_event_report_pkt['body']['data']         = []

    dl_event_report_pkt['body']['data'][-2]       = meter.calc_dlt645_cs8(map(chr,dl_event_report_pkt['body']['data']))
    plc_tb_ctrl._debug(dl_event_report_pkt)
    dl_apl_645 = dl_event_report_pkt['body']['data']

    msdu = plc_packet_helper.build_apm(dict_content=dl_event_report_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = invalid_tei  # DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1        # downlink broadcast

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=invalid_tei, broadcast_flag = 0)

    tc_common.wait_for_tx_complete_ind(tb)

    # 同时启动定时器（定时时长2s），定时器溢出前，查看是否不会收到待测STA从串口发出的通信测试数据；
    dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 2)

    # check 1. STA在收到通信测试帧（目的站点非自身）后，是否不会通过串口发出通信测试数据；
    assert dlt645_frame is None,          'received unexpected 645 pkt err'

    # 5. 软件平台模拟CCO通过透明物理设备向待测STA设备发送正确的“通信测试帧”，
    #    同时启动定时器（定时时长2s），定时器溢出前，查看是否能够收到待测STA从串口发出的通信测试数据；
    plc_tb_ctrl._debug("Step 5: simulate CCO to send valid Comm Test pkt to STA, check whether STA will send Comm Test data out in 2 seconds...")

    tb.mac_head.org_dst_tei         = sta_tei  # DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1        # downlink broadcast

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)
    #    同时启动定时器（定时时长2s），定时器溢出前，查看是否能够收到待测STA从串口发出的通信测试数据；
    dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 2)
    plc_tb_ctrl._debug(dlt645_frame)
    assert dlt645_frame.head.len == 4,            "645 pkt head len err"

    # check . 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst = []
    dl_mtr_645_str = meter.build_dlt645_07_frame(dict_content=dlt645_frame)
    tc_common.convert_str2lst(dl_mtr_645_str, dl_mtr_645_lst)
    assert cmp(dl_mtr_645_lst, dl_apl_645) == 0,  "STA -> Meter - 645 packet err"

    time.sleep(1)

    m.close_port()



