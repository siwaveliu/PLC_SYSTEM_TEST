# -- coding: utf-8 --
# STA 在规定时间内抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter
import config


'''
1. 连接设备，上电初始化。
2. 软件平台模拟电表，在收到被测STA 请求读表号后，通过串口向其下发电表地址信息。
3. 软件平台模拟CCO 对入网请求的STA 进行处理，确定站点入网成功，完成组网。
4. 软件平台模拟CCO 向被测STA 启动路由主动抄表业务（路由重启），依次发送2 条SOF
帧（路由主动抄表下行报文1 和路由主动抄表下行报文2），设置设备超时时间为
1000ms, 用于抄读 STA 所在设备的特定数据项（DL/T645-2007 规约虚拟电表
000000000001）正向有功总电能数据项。
5. 软件平台模拟电表在收到下行抄表报文1 后在1000ms 时间内响应，并组织路由主动抄
表上行1 报文回复CCO(测试平台)。
6. 软件平台模拟电表在收到下行抄表报文2 后响应时长超过1000ms，向被测STA 返回抄
读数据项，检查是否不会组织路由主动抄表上行报文2 回复CCO。
7. 在虚拟电表的TTL 串口监控是否收到STA 转发的数据报文，如在n 秒内未收到，则指
示STA 抄表下行转发失败。如在n 秒内收到，则指示STA 下行转发数据成功，虚拟电
表针对数据报文进行解析并应答电表当前时间报文。
8. 测试平台监控是否能够在n 秒内收到STA 转发的电表当前时间报文，如未收到，则指
示STA 抄表上行转发失败，如收到数据与电表应答报文不同，则指示STA 抄表上行转
发数据错误，否则指示STA 抄表上行转发数据成功，此测试流程结束，最终结论为此
项测试通过。
check:
1. 验证设备超时时间是否设置成功
'''
#timeout_flag = 0
def timeout_callback():
#    global timeout_flag
#    timeout_flag = 1
    plc_tb_ctrl._debug("time out callback is called")
    return

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """

    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"

    m = meter.Meter()
    m.open_port()

    cco_mac            = '00-00-C0-A8-01-01'
    meter_addr         = '01-00-00-00-00-00'
    beacon_loss        = 0
    beacon_proxy_flag  = 0
    sta_tei            = 2
    apl_sn             = 0x1000

    # 1. 连接设备，上电初始化。
    # 2. 软件平台模拟电表，在收到被测STA 请求读表号后，通过串口向其下发电表地址信息。
    # 3. 软件平台模拟CCO 对入网请求的STA 进行处理，确定站点入网成功，完成组网。

    plc_tb_ctrl._debug("Step 1, 2, 3: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 4. 软件平台模拟CCO 向被测STA 启动路由主动抄表业务（路由重启），
    #    依次发送2 条SOF帧（路由主动抄表下行报文1 和路由主动抄表下行报文2），设置设备超时时间为1000ms,
    #    用于抄读 STA 所在设备的特定数据项（DL/T645-2007 规约虚拟电表000000000001）正向有功总电能数据项。
    plc_tb_ctrl._debug("Step 4: simulate CCO to send 2 downstream route meter read pkts, with device timeout 1 second...")

    # 第一个报文
    plc_tb_ctrl._debug("Step 4.1: send the 1st downstream route meter read pkts...")

    dev_timeout = 1000       # unit: ms
    apl_sn1     = apl_sn
    dl_meter_read_pkt = tb._load_data_file(data_file='apl_route_meter_read_dl.yaml')
    dl_meter_read_pkt['body']['sn']       = apl_sn1
    dl_meter_read_pkt['body']['exp_time'] = dev_timeout/100        # the unit of 'exp_time' is 100ms
    dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))

#    plc_tb_ctrl._debug(dl_meter_read_pkt)
    dl_apl_645 = dl_meter_read_pkt['body']['data']
    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)

    tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei         = 1
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0,auto_retrans=False)

    tc_common.wait_for_tx_complete_ind(tb)

    # 第二个报文
    plc_tb_ctrl._debug("Step 4.2: send the 2nd downstream route meter read pkts...")

    apl_sn2     = apl_sn + 0x100
    dl_meter_read_pkt['body']['sn'] = apl_sn2
#    plc_tb_ctrl._debug(dl_meter_read_pkt)
    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0,auto_retrans=False)

    tc_common.wait_for_tx_complete_ind(tb)

    # 5. 软件平台模拟电表在收到下行抄表报文1后 在1000ms 时间内响应，并组织路由主动抄表上行1 报文回复CCO(测试平台)。
    # 7. 在虚拟电表的TTL 串口监控是否收到STA 转发的数据报文，如在n 秒内未收到，则指示STA 抄表下行转发失败。
    #    如在n 秒内收到，则指示STA 下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前时间报文。
    plc_tb_ctrl._debug("Step 5, 7: simulate meter to receive and ack the 1st route meter read pkt, before 1 second timeout...")

    dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 10)

    plc_tb_ctrl._debug(dlt645_frame)
    assert dlt645_frame.head.len == 4,            "645 pkt head len err"

    # check 1. 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst = []
    dl_mtr_645_str = meter.build_dlt645_07_frame(dict_content=dlt645_frame)
    tc_common.convert_str2lst(dl_mtr_645_str, dl_mtr_645_lst)

    assert cmp(dl_mtr_645_lst, dl_apl_645) == 0,  "STA -> Meter - 645 packet err"

    # meter ack
    reply_data = [1,2,3,4]
    dis = [dlt645_frame.body.value.DI0,
           dlt645_frame.body.value.DI1,
           dlt645_frame.body.value.DI2,
           dlt645_frame.body.value.DI3]

    ul_mtr_645_lst = []
    ul_mtr_645_str = tc_common.send_dlt645_reply_frame(m,meter_addr,dis,reply_data,len(reply_data))

    tc_common.convert_str2lst(ul_mtr_645_str, ul_mtr_645_lst)

    # 6. 软件平台模拟电表在收到下行抄表报文2后 响应时长超过1000ms，向被测STA 返回抄读数据项，
    #    检查是否不会组织路由主动抄表上行报文2 回复CCO。
    # 7. 在虚拟电表的TTL 串口监控是否收到STA 转发的数据报文，如在n 秒内未收到，则指示STA 抄表下行转发失败。
    #    如在n 秒内收到，则指示STA 下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前时间报文。
    plc_tb_ctrl._debug("Step 6, 7: simulate meter to receive and ack the 2nd route meter read pkt, after 1 second timeout...")

    dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 10)
    plc_tb_ctrl._debug(dlt645_frame)
    assert dlt645_frame.head.len == 4,            "645 pkt head len err"
    # check 1. 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst = []
    dl_mtr_645_str = meter.build_dlt645_07_frame(dict_content=dlt645_frame)
    tc_common.convert_str2lst(dl_mtr_645_str, dl_mtr_645_lst)

    assert cmp(dl_mtr_645_lst, dl_apl_645) == 0,  "STA -> Meter - 645 packet err"

    # meter ack
    time.sleep(2)  # 延时1000ms, 这里使用2秒是因为FPGA目前降频一半。
    tc_common.send_dlt645_reply_frame(m,meter_addr,dis,reply_data,len(reply_data))

    # 8. 测试平台监控是否能够在n 秒内收到STA 转发的电表当前时间报文，如未收到，则指示STA 抄表上行转发失败，
    #    如收到数据与电表应答报文不同，则指示STA 抄表上行转发数据错误，否则指示STA 抄表上行转发数据成功，
    #    此测试流程结束，最终结论为此项测试通过。
    plc_tb_ctrl._debug("Step 8: simulate CCO to receive the 1st route meter read ack...")

    pkt_id = 'APL_ROUTE_METER_READ'
    [timestamp, fc, mac_frame_head, apm] = tc_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 10)

    assert apm is not None,                                          "upstream APL_ROUTE_METER_READ is not received err"
    ul_apl_645 = apm.body.data
    # check 2. 测试STA 转发上行抄表数据时其报文端口号是否为0x11；
    assert apm.header.port                 == 0x11,                   "pkt header port id err"
    # check 3. 测试STA 转发上行抄表数据时其报文ID 是否为0x0002（路由主动抄表）；
    assert apm.header.id                   == pkt_id,                 "pkt header packet id err"
    # check 4. 测试STA 转发上行抄表数据时其报文控制字是否为0；
    assert apm.header.ctrl_word            == 0,                      "pkt header ctrl word err"
    # check 5. 测试STA 转发上行抄表数据时其协议版本号是否为1；
    assert apm.body.proto_ver              == 'PROTO_VER1',           "pkt body proto ver err"
    # check 6. 测试STA 转发上行抄表数据时其报文头长度是否符合在0-64 范围内；
    assert apm.body.hdr_len                 < 64,                     "pkt body hdr len err"
    # check 7. 测试STA 转发上行抄表数据时其应答状态是否为0（正常）；
    assert apm.body.rsp_status             == 'NORMAL_ACK',           "pkt body rsp status err"
    # check 8. 测试STA 转发上行抄表数据时其转发数据的规约类型是否为1（DL/T645-97）或2（DL/T645-07））；
    prot_type = apm.body.data_proto_type
    assert (prot_type == 'PROTO_DLT645_2007') or (prot_type == 'PROTO_DLT645_1997'),    "pkt body data proto type err"
    # check 9. 测试STA 转发上行抄表数据时其报文序号是否与下行报文序号一致；
    assert apm.body.sn                     ==  apl_sn1,               "pkt body sn err"
    # check 10. 测试STA 转发上行抄表数据时其选项字是否为1（方向位：上行）；
    assert apm.body.dir_bit                == 'UL',                   "pkt body directrion bit err"

    # check 11. 测试STA 转发上行抄表数据时其数据（DATA）是否为DL/T645 规约报文；
    # check 12. 测试STA 上行转发数据是否与电能表应答报文相同。
    assert cmp(ul_apl_645, ul_mtr_645_lst) == 0,                      "pkt body - 645 pkt err"

    # check. 报文2的上行APL应答报文不应被收到

    timeout_val  = 5
    stop_time    = time.time() + timeout_val
    while True:

        [timestamp, fc, mac_frame_head, apm] = tc_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 2, timeout_callback)

        if time.time() >= stop_time:
            plc_tb_ctrl._debug("time out, not receive the unexpected pkt(the ack of the 2nd APL route meter read)...")
            break

        if apm is not None:
            assert apm.body.sn != apl_sn2,    "unexpectedly received the 2nd APL_ROUTE_METER_READ pkt err"
            if apm.body.sn == apl_sn1:
                plc_tb_ctrl._debug("drop the duplicated upstream pkt APL_ROUTE_METER_READ with sn={}...".format(apm.body.sn))

    time.sleep(1)

    m.close_port()



