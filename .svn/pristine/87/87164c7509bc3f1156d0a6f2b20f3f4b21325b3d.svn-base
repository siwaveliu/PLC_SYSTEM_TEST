# -- coding: utf-8 --
# STA 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter
import plc_packet_helper


'''
1. 连接设备，上电初始化。
2. 软件平台模拟CCO 对入网请求的STA 进行处理，确定站点入网成功。
3. 软件平台模拟电表，在收到被测STA 请求读表号后，向其下发电表地址信息。
4. 软件平台模拟CCO 向被测STA 启动集中器主动抄表业务 ，发送SOF 帧（抄表报文下行），
   用于点抄STA 所在设备的特定数据项（ DL/T645-2007 规约虚拟电表000000000001）当前时间。
5. 软件平台模拟电表向被测STA 返回抄读数据项，收到其返回的S0F 帧（抄表报文上行）。
6. 在虚拟电表的TTL 串口监控是否收STA 转发的数据报文，如在n 秒内未收到 ，则指示STA 抄表下行转发失败。
   如在n 秒内收到，则指示STA 下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前时间报文。
7. 软件平台监控是否能够在n 秒内收到STA 转发的电表当前时间报文，如未收到，则指示STA 抄表上行转发失败，
   如收到数据与电表应答报文不同，则指示STA 抄表上行转发数据错误，否则指示STA 抄表上行转发数据成功，
   此测试流程结束，最终结论为此项测试通过。
check:
1. 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
2. 测试STA 转发上行抄表数据时其报文端口号是否为0x11；
3. 测试STA 转发上行抄表数据时其报文ID 是否为0x0001（集中器主动抄表）；
4. 测试STA 转发上行抄表数据时其报文控制字是否为0；
5. 测试STA 转发上行抄表数据时其协议版本号是否为1；
6. 测试STA 转发上行抄表数据时其报文头长度是否符合在0-64 范围内；
7. 测试STA 转发上行抄表数据时其应答状态是否为0（正常）；
8. 测试STA 转发上行抄表数据时其转发数据的规约类型是否为2（DL/T645-07））；
9. 测试STA 转发上行抄表数据时其报文序号是否与下行报文序号一致；
10. 测试STA 转发上行抄表数据时其选项字是否为1（方向位：上行）；
11. 测试STA 转发上行抄表数据时其数据（DATA）是否为DL/T645 规约报文；
12. 测试STA 上行转发数据是否与电能表应答报文相同。
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
    meter_addr         = '00-00-00-00-00-01'
    beacon_loss        = 0
    beacon_proxy_flag  = 0

    sta_tei            = 2
    apl_sn             = 1

    # 1. 连接设备，上电初始化。
    # 2. 软件平台模拟CCO 对入网请求的STA 进行处理，确定站点入网成功。
    # 3. 软件平台模拟电表，在收到被测STA 请求读表号后，向其下发电表地址信息。

    plc_tb_ctrl._debug("Step 1, 2, 3: Wait for system to finish network connecting...")

    plc_tb_ctrl._debug("activate tb")
    tc_common.activate_tb(tb,work_band = 1)

    #wait for meter read request
    plc_tb_ctrl._debug("wait for meter read request")
    dlt645_frame = m.wait_for_dlt645_frame(dir = 'REQ_FRAME', timeout = 30)

    assert dlt645_frame is not None
    assert dlt645_frame.head.addr.upper() == 'AA-AA-AA-AA-AA-AA'
    if dlt645_frame.head.code == "ADDR_READ":
        assert dlt645_frame.head.len == 0
        #prepare reply frame for meter read request
        plc_tb_ctrl._debug("send reply to meter read request")
        tc_common.send_dlt645_addr_read_reply_frame(m, meter_addr)
    elif dlt645_frame.head.code == "DATA_READ":
        assert dlt645_frame.head.len == 4
        reply_data = [1,2,3,4]
        reply_data = [d + 0x33 for d in reply_data]
        dis = [dlt645_frame.body.value.DI0,
               dlt645_frame.body.value.DI1,
               dlt645_frame.body.value.DI2,
               dlt645_frame.body.value.DI3]
        tc_common.send_dlt645_reply_frame(m, meter_addr, dis, reply_data, len(reply_data))
    else:
        assert False, "unexpected 645 code"

    band=0

    # 在频段0发送20次频段设置命令
    tb._change_band(0)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段1发送20次频段设置命令
    tb._change_band(1)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    tb._change_band(band)

    # 配置TB周期性发送中央信标
    plc_tb_ctrl._debug("configure TB to send central beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    # 等待STA1发送关联请求
    plc_tb_ctrl._debug("wait for assoc req")
    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_REQ'], timeout=50)
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
    asso_cnf_dict['body']['random_num'] = nmm.body.rand_num
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

    # 4. 软件平台模拟CCO 向被测STA 启动集中器主动抄表业务 ，发送SOF 帧（抄表报文下行），
    #    用于点抄STA 所在设备的特定数据项（ DL/T645-2007 规约虚拟电表000000000001）当前时间。

    plc_tb_ctrl._debug("Step 4: simulate CCO to send cct meter read pkt...")

    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')

    succ_cnt = 0
    for i in range(100):
        plc_tb_ctrl._debug("send mr req")

        apl_sn += 1

        dl_meter_read_pkt['body']['sn'] = apl_sn

        dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))

        #plc_tb_ctrl._debug(dl_meter_read_pkt)
        dl_apl_645 = dl_meter_read_pkt['body']['data']
        msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)

        m.clear_port_rx_buf()

        tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
        tb.mac_head.org_src_tei         = 1
        tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
        tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
        tb.mac_head.mac_addr_flag       = 0
        tb.mac_head.hop_limit           = 15
        tb.mac_head.remaining_hop_count = 15
        tb.mac_head.broadcast_dir       = 0 #downlink broadcast

        tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, tmi_b=i%15, tmi_e=0, pb_num=1)

        tc_common.wait_for_tx_complete_ind(tb)

        # 5. 软件平台模拟电表向被测STA 返回抄读数据项，收到其返回的S0F 帧（抄表报文上行）。
        # 6. 在虚拟电表的TTL 串口监控是否收STA 转发的数据报文，如在n 秒内未收到 ，则指示STA 抄表下行转发失败。
        #    如在n 秒内收到，则指示STA 下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前时间报文。
        plc_tb_ctrl._debug("wait dlt645 frame")

        dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 2)
    #    plc_tb_ctrl._debug("645 pkt rx by meter: {}".format(dlt645_frame))

        if dlt645_frame is not None:
            #plc_tb_ctrl._debug(dlt645_frame)
            assert dlt645_frame.head.len == 4,            "645 pkt head len err"
            succ_cnt += 1
            plc_tb_ctrl._debug("dlt645 received")
            #time.sleep(10)
        else:
            plc_tb_ctrl._debug("dlt645 NOT received")


        tb.tb_uart.clear_tb_port_rx_buf()



    plc_tb_ctrl._debug("total: {}, succ: {}".format(100, succ_cnt))

'''
    # check 1. 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst = []
    dl_mtr_645_str = meter.build_dlt645_07_frame(dict_content=dlt645_frame)
    tc_common.convert_str2lst(dl_mtr_645_str, dl_mtr_645_lst)

    if dl_mtr_645_lst != dl_apl_645:
        plc_tb_ctrl._debug(dl_apl_645)
        plc_tb_ctrl._debug(dl_mtr_645_lst)
        #assert 0,  "STA -> Meter - 645 packet err"



    # prepare reply frame for meter read request
    reply_data = [1,2,3,4]
    dis = [dlt645_frame.body.value.DI0,
           dlt645_frame.body.value.DI1,
           dlt645_frame.body.value.DI2,
           dlt645_frame.body.value.DI3]

    ul_mtr_645_lst = []
    ul_mtr_645_str = tc_common.send_dlt645_reply_frame(m,meter_addr,dis,reply_data,len(reply_data))

    tc_common.convert_str2lst(ul_mtr_645_str, ul_mtr_645_lst)
    plc_tb_ctrl._debug("645 pkt lst in upstream meter : {}".format(ul_mtr_645_lst))

    # 7. 软件平台监控是否能够在n 秒内收到STA 转发的电表当前时间报文，如未收到，则指示STA 抄表上行转发失败，
    #    如收到数据与电表应答报文不同，则指示STA 抄表上行转发数据错误，否则指示STA 抄表上行转发数据成功，
    #    此测试流程结束，最终结论为此项测试通过。
    plc_tb_ctrl._debug("Step 7: simulate CCO to receive the CCT METER READ reply from STA, with the meter data forwarded...")

#    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_ul('APL_CCT_METER_READ',10)

    pkt_id = 'APL_CCT_METER_READ'
    [timestamp, fc, mac_frame_head, apm] = tc_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 10)

    plc_tb_ctrl._debug("rx apl cct meter read: {}".format(apm))

    ul_apl_645 = apm.body.data
    # check 2. 测试STA 转发上行抄表数据时其报文端口号是否为0x11；
    assert apm.header.port              == 0x11,                 "pkt header port id err"
    # check 3. 测试STA 转发上行抄表数据时其报文ID 是否为0x0001（集中器主动抄表）；
    assert apm.header.id                == pkt_id,               "pkt header packet id err"
    # check 4. 测试STA 转发上行抄表数据时其报文控制字是否为0；
    assert apm.header.ctrl_word         == 0,                    "pkt header ctrl word err"
    # check 5. 测试STA 转发上行抄表数据时其协议版本号是否为1；
    assert apm.body.proto_ver           == 'PROTO_VER1',         "pkt body proto ver err"
    # check 6. 测试STA 转发上行抄表数据时其报文头长度是否符合在0-64 范围内；
    assert apm.body.hdr_len              < 64,                   "pkt body hdr len err"
    # check 7. 测试STA 转发上行抄表数据时其应答状态是否为0（正常）；
    assert apm.body.rsp_status          == 'NORMAL_ACK',         "pkt body rsp status err"
    # check 8. 测试STA 转发上行抄表数据时其转发数据的规约类型是否为2（DL/T645-07））；
    assert apm.body.data_proto_type     == 'PROTO_DLT645_2007',  "pkt body data proto type err"
    # check 9. 测试STA 转发上行抄表数据时其报文序号是否与下行报文序号一致；
    assert apm.body.sn                  ==  apl_sn,              "pkt body sn err"
    # check 10. 测试STA 转发上行抄表数据时其选项字是否为1（方向位：上行）；
    assert apm.body.dir_bit             == 'UL',                 "pkt body directrion bit err"

    # check 11. 测试STA 转发上行抄表数据时其数据（DATA）是否为DL/T645 规约报文；
    # check 12. 测试STA 上行转发数据是否与电能表应答报文相同。
#    plc_tb_ctrl._debug("645 pkt in upstream apl : {}".format(ul_apl_645))
#    plc_tb_ctrl._debug("645 pkt in upstream meter : {}".format(ul_mtr_645_lst))

    assert cmp(ul_apl_645, ul_mtr_645_lst) == 0,                 "pkt body data - 645 pkt err"

    time.sleep(1)

    m.close_port()
'''


