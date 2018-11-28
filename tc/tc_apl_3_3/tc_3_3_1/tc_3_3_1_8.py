# -- coding: utf-8 --
# STA通过集中器主动并发抄表测试（多个STA抄读同一数据项的645帧）
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter


'''
1. 连接设备，上电初始化。
2. 软件平台模拟电表，在收到被测STA请求读表号后，向其下发电表地址信息。
3. 软件模拟CCO对入网请求的STA进行处理，确定站点入网成功，完成组网。
4. 软件模拟CCO向被测STA启动集中器主动并发抄表业务，发送SOF帧（抄表报文下行），
   用于抄读 STA 所在设备（DL/T645-2007规约虚拟电表000000000001）的多个特定数据项
   (读当前正向有功总电能、读日期和星期、读时间)。
5. 被测STA收到下行抄表报文后分别读取下挂电能表的当前正向有功总电能、日期和星期、时间，
   待测STA以规定的时间频率与电能表之间进行交互。
6. 软件平台模拟电能表向被测STA分别返回抄读数据项，待测STA组织S0F帧（抄表报文上行）回复CCO。
7. 在虚拟电表的TTL串口监控是否收STA转发的数据报文，如在n秒内未收到，则指示STA抄表下行转发失败。
   如在n秒内收到，则指示STA下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前报文。
8. 测试平台监控是否能够在n秒内收到STA转发的电表当前时间报文，如未收到，则指示STA抄表上行转发失败，
   如收到数据与电表应答报文不同，则指示STA抄表上行转发数据错误，否则指示STA抄表上行转发数据成功，
   此测试流程结束，最终结论为此项测试通过。
check:
1. 测试STA转发下行抄表数据时是否与CCO下发的数据报文相同；
2. 测试STA转发上行抄表数据时其报文端口号是否为0x11；
3. 测试STA转发上行抄表数据时其报文ID是否为0x0003（集中器主动并发抄表）；
4. 测试STA转发上行抄表数据时其报文控制字是否为0；
5. 测试STA转发上行抄表数据时其协议版本号是否为1；
6. 测试STA转发上行抄表数据时其报文头长度是否符合在0-64范围内；
7. 测试STA转发上行抄表数据时其应答状态是否为0（正常）；
8. 测试STA转发上行抄表数据时其转发数据的规约类型是否为1（DL/T645-97）或2（DL/T645-07）；
9. 测试STA 转发上行抄表数据时其报文序号是否与CCO 下行报文序号一致；
10. 测试STA 转发上行抄表数据时其报文应答状态是否为1（对应报文有应答）；
11. 测试STA 转发上行抄表数据时其数据（DATA）是否为多条DL/T645 规约报文，其中表地址须一致。
'''

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

    # 4. 软件模拟CCO向被测STA启动集中器主动并发抄表业务，发送SOF帧（抄表报文下行），
    #    用于抄读 STA 所在设备（DL/T645-2007规约虚拟电表000000000001）的多个特定数据项
    #    (读当前正向有功总电能、读日期和星期、读时间)。
    plc_tb_ctrl._debug("Step 4: simulate CCO to send simu-meter-read downstream packet, with 3 DLT645 pkt(read power, read date and read time)...")
    plc_tb_ctrl._debug("Step 4: simulate CCO to send simu-meter-read downstream packet, with 3 DLT645 pkt(read power, read date and read time)...")

    dl_meter_read_pkt_dict = tb._load_data_file(data_file='apl_cct_simu_meter_read_dl_empty.yaml')

    dlt645_1           = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                          0x11, 0x04, 0x33, 0x33, 0x34, 0x33, 0x00, 0x16,]    # [DI3,DI2,DI1,DI0] = [0,1,0,0] 正向有功总电能

    dlt645_2           = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                          0x11, 0x04, 0x34, 0x34, 0x33, 0x37, 0x00, 0x16,]    # [DI3,DI2,DI1,DI0] = [4,0,1,1] 日期和星期

    dlt645_3           = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                          0x11, 0x04, 0x35, 0x34, 0x33, 0x37, 0x00, 0x16,]    # [DI3,DI2,DI1,DI0] = [4,0,1,2] 时间

    dlt645_1[-2]       = meter.calc_dlt645_cs8(map(chr,dlt645_1))
    dlt645_2[-2]       = meter.calc_dlt645_cs8(map(chr,dlt645_2))
    dlt645_3[-2]       = meter.calc_dlt645_cs8(map(chr,dlt645_3))

    dlt645_1_size      = len(dlt645_1)
    dlt645_2_size      = len(dlt645_2)
    dlt645_3_size      = len(dlt645_3)
    data_len           = dlt645_1_size + dlt645_2_size + dlt645_3_size

    dl_meter_read_pkt_dict['body']['sn']         = apl_sn
    dl_meter_read_pkt_dict['body']['data_len']   = data_len
    dl_meter_read_pkt_dict['body']['data'].extend(dlt645_1)
    dl_meter_read_pkt_dict['body']['data'].extend(dlt645_2)
    dl_meter_read_pkt_dict['body']['data'].extend(dlt645_3)

    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt_dict, is_dl=True)

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

    # 5. 被测STA收到下行抄表报文后分别读取下挂电能表的当前正向有功总电能、日期和星期、时间，
    #    待测STA以规定的时间频率与电能表之间进行交互。
    # 6. 软件平台模拟电能表向被测STA分别返回抄读数据项，待测STA组织S0F帧（抄表报文上行）回复CCO。
    # 7. 在虚拟电表的TTL串口监控是否收STA转发的数据报文，如在n秒内未收到，则指示STA抄表下行转发失败。
    #    如在n秒内收到，则指示STA下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前报文。
    plc_tb_ctrl._debug("Step 5,6,7: simulate meter to receive and ack the Read Power, Read Date and Read Time cmds ...")

    # 接收第一个电表报文 - “正向有功总电能”
    plc_tb_ctrl._debug("Step 5.1: simulate meter to receive the Read Power cmd...")
    dlt645_frame_1 = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 10)
    plc_tb_ctrl._debug(dlt645_frame_1)
    assert dlt645_frame_1.head.len == 4,            "645 pkt 1 head len err"
    # CHECK 1.1 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst_1 = []
    dl_mtr_645_str_1 = meter.build_dlt645_07_frame(dict_content=dlt645_frame_1)
    tc_common.convert_str2lst(dl_mtr_645_str_1, dl_mtr_645_lst_1)
    assert cmp(dl_mtr_645_lst_1, dlt645_1) == 0,    "STA -> Meter - 645 packet 1 err"

    # 应答第一个电表报文 - “正向有功总电能”
    plc_tb_ctrl._debug("Step 6.1: simulate meter to ack the Read Power cmd...")
    reply_data = [1,2,3,4]
    dis = [dlt645_frame_1.body.value.DI0,
           dlt645_frame_1.body.value.DI1,
           dlt645_frame_1.body.value.DI2,
           dlt645_frame_1.body.value.DI3]
    rx_meter_addr = dlt645_frame_1.head.addr

    ul_mtr_645_lst_1 = []
    ul_mtr_645_str_1 = tc_common.send_dlt645_reply_frame(m,rx_meter_addr,dis,reply_data,len(reply_data))

    tc_common.convert_str2lst(ul_mtr_645_str_1, ul_mtr_645_lst_1)

    # 接收第二个电表报文 - “日期和星期”
    plc_tb_ctrl._debug("Step 5.2: simulate meter to receive the Read Date cmd...")
    dlt645_frame_2 = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 10)
    plc_tb_ctrl._debug(dlt645_frame_2)
    assert dlt645_frame_2.head.len == 4,            "645 pkt 2 head len err"
    # CHECK 1.2 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst_2 = []
    dl_mtr_645_str_2 = meter.build_dlt645_07_frame(dict_content=dlt645_frame_2)
    tc_common.convert_str2lst(dl_mtr_645_str_2, dl_mtr_645_lst_2)
    assert cmp(dl_mtr_645_lst_2, dlt645_2) == 0,    "STA -> Meter - 645 packet 2 err"

    # 应答第二个电表报文 - “日期和星期”
    plc_tb_ctrl._debug("Step 6.2: simulate meter to ack the Read Date cmd...")
    reply_data = [5,6,7,8]
    dis = [dlt645_frame_2.body.value.DI0,
           dlt645_frame_2.body.value.DI1,
           dlt645_frame_2.body.value.DI2,
           dlt645_frame_2.body.value.DI3]
    rx_meter_addr = dlt645_frame_2.head.addr

    ul_mtr_645_lst_2 = []
    ul_mtr_645_str_2 = tc_common.send_dlt645_reply_frame(m,rx_meter_addr,dis,reply_data,len(reply_data))

    tc_common.convert_str2lst(ul_mtr_645_str_2, ul_mtr_645_lst_2)

    # 接收第三个电表报文 - “时间”
    plc_tb_ctrl._debug("Step 5.3: simulate meter to receive the Read Time cmd...")
    dlt645_frame_3 = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 10)
    plc_tb_ctrl._debug(dlt645_frame_3)
    assert dlt645_frame_3.head.len == 4,            "645 pkt 3 head len err"
    # CHECK 1.2 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst_3 = []
    dl_mtr_645_str_3 = meter.build_dlt645_07_frame(dict_content=dlt645_frame_3)
    tc_common.convert_str2lst(dl_mtr_645_str_3, dl_mtr_645_lst_3)
    assert cmp(dl_mtr_645_lst_3, dlt645_3) == 0,    "STA -> Meter - 645 packet 3 err"

    # 应答第三个电表报文 - “时间”
    plc_tb_ctrl._debug("Step 6.1: simulate meter to ack the Read Time cmd...")
    reply_data = [9,10,11,12]
    dis = [dlt645_frame_3.body.value.DI0,
           dlt645_frame_3.body.value.DI1,
           dlt645_frame_3.body.value.DI2,
           dlt645_frame_3.body.value.DI3]
    rx_meter_addr = dlt645_frame_3.head.addr

    ul_mtr_645_lst_3 = []
    ul_mtr_645_str_3 = tc_common.send_dlt645_reply_frame(m,rx_meter_addr,dis,reply_data,len(reply_data))

    tc_common.convert_str2lst(ul_mtr_645_str_3, ul_mtr_645_lst_3)

    # 8. 测试平台监控是否能够在n秒内收到STA转发的电表当前时间报文，如未收到，则指示STA抄表上行转发失败，
    #    如收到数据与电表应答报文不同，则指示STA抄表上行转发数据错误，否则指示STA抄表上行转发数据成功，
    #    此测试流程结束，最终结论为此项测试通过。
    plc_tb_ctrl._debug("Step 8: simulate CCO to receive the simu-meter-read upstream reply forwarded by STA ...")
    pkt_id = 'APL_CCT_SIMU_METER_READ'
    [timestamp, fc, mac_frame_head, apm] = tc_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 10)

    assert apm is not None,                                          "upstream APL_CCT_SIMU_METER_READ is not received err"
    ul_apl_645 = apm.body.data
    # check 2. 测试STA 转发上行抄表数据时其报文端口号是否为0x11；
    assert apm.header.port                 == 0x11,                   "pkt header port id err"
    # check 3. 测试STA 转发上行抄表数据时其报文ID 是否为0x0003（集中器主动并发抄表）；
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
    assert apm.body.sn                     ==  apl_sn,               "pkt body sn err"
    # check 10. 测试STA 转发上行抄表数据时其报文应答状态是否为1（对应报文有应答）； - 应该是每个bit对应一个抄表应答报文
    assert apm.body.pkt_rsp_status         == 7,                      "pkt body directrion bit err"

    # check 11. 测试STA 转发上行抄表数据时其数据（DATA）是否为多条DL/T645 规约报文，其中表地址须一致。
    ul_mtr_645_lst = []
    ul_mtr_645_lst.extend(ul_mtr_645_lst_1)
    ul_mtr_645_lst.extend(ul_mtr_645_lst_2)
    ul_mtr_645_lst.extend(ul_mtr_645_lst_3)
    assert cmp(ul_apl_645, ul_mtr_645_lst) == 0,                      "pkt body - 645 pkt err"

    time.sleep(1)

    m.close_port()


