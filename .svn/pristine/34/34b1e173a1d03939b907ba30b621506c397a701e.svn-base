# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，上电初始化；
2. 软件平台模拟集中器，通过串口向待测 CCO 下发“设置主节点地址”命令，在收到“确
认”后，再通过串口向待测 CCO 下发“添加从节点”命令，将目标网络站点的 MAC 地址
下发到 CCO 中，等待“确认”；
3. 软件平台收到待测 CCO 发送的“中央信标”后，查看其是否在规定的中央信标时隙内发
出的；
(1)在中央信标时隙发出“中央信标”， 则 pass；
(2)其他情况，则 fail。
4. 软件平台模拟未入网 STA 通过透明物理设备向待测 CCO 设备发送“关联请求报文” ，查
看是否收到相应的“选择确认报文” ；
(1)未收到对应的“选择确认帧”，则 fail；
(2)收到对应的“选择确认帧”，则 pass。
5. 同时启动定时器（定时时长 10s），查看是否在规定的 CSMA 时隙内收到待测 CCO 发出的
“关联确认报文”；
(1)在规定 CSMA 时隙收到正确“关联确认报文”， 则 pass；
(2)在规定 CSMA 时隙收到“关联确认报文”，但报文错误，则 fail；
(3)定时器溢出，未收到“关联确认报文”，则 fail；
(4)其他情况，则 fail。
6. 软件平台收到待测 CCO 发送的“中央信标”后，查看是否对已入网 STA 进行了发现信标
时隙的规划；
(1)进行了发现信标时隙规划， 则 pass；
(2)没有进行了发现信标时隙规划，则 fail。
7. 软件平台模拟已入网 STA 在 CSMA 时隙内通过透明物理设备转发未入网 STA 的 “关联请
求报文”，查看是否收到相应的“选择确认报文” ；
(1)未收到对应的“选择确认帧”，则 fail；
(2)收到对应的“选择确认帧”，则 pass。
8. 同时启动定时器（定时时长 10s），查看是否在规定的 CSMA 时隙内收到待测 CCO 发出的
“关联确认报文”；
(1)在规定 CSMA 时隙收到正确“关联确认报文”，则 pass；
(2)在规定 CSMA 时隙收到“关联确认报文”，但报文错误，则 fail；
(3)定时器溢出，未收到“关联确认报文”，则 fail；
(4)其他情况，则 fail。
9. 软件平台收到待测 CCO 发送的“中央信标”后，查看是否对新入网的 STA-2 进行了发现
信标时隙的规划，是否对虚拟 PCO-1 进行了代理信标时隙的规划。
(1)对 STA-2 进行发现信标时隙的规划且对 PCO-1 进行了代理信标时隙的规划，则 pass；
(2)未对 STA-2 进行发现信标时隙的规划或未对 PCO-1 进行了代理信标时隙的规划， 则
fail；
(3)其他情况，则 fail；
10.TCN-3 平台模拟未入网 STA-1 通过透明物理设备向待测 CCO 设备发送“关联请求报文” ，
查看是否收到相应的“选择确认报文” ；
(1)未收到对应的“选择确认帧”，则 fail；
(2)收到对应的“选择确认帧”，则 pass。
11.同时启动定时器（定时时长 10s），查看是否在规定的 CSMA 时隙内收到待测 CCO 发出的
“关联确认报文”；
（1） 在规定 CSMA 时隙收到正确“关联确认报文”， 则 pass；
（2） 在规定 CSMA 时隙收到“关联确认报文”，但报文错误，则 fail；
（3） 定时器溢出，未收到“关联确认报文”，则 fail；
（4） 其他情况，则 fail。
12.软件平台模拟集中器通过串口向待测 CCO 发送目标站点为 STA-2 的“监控从节点”命令，
同时启动定时器（定时时长 10s），查看是否收到“监控从节点”上行报文；
(1)定时器溢出前，收到正确“监控从节点” 上行报文， 则 pass；
(2)定时器溢出， 未收到正确“监控从节点” 上行报文， 则 fail；
(3)其他情况，则 fail。
13.软件平台查看是否在规定的 CSMA 时隙内收到正确的下行“抄表报文”；
(1)在规定的 CSMA 时隙内收到正确的下行“抄表报文”（考察代理主路径标识、路由总
跳数、路由剩余跳数、原始源 MAC 地址、原始目的 MAC 地址是否正确）， 则 pass；
(2)在规定的 CSMA 时隙收到下行“抄表报文”，但报文错误，则 fail；
(3)定时器溢出，未收到下行“抄表报文”，则 fail；
(4)其他情况，则 fail。
14.软件平台模拟 STA-2 经 PCO 转发向待测 CCO 发送上行“抄表报文”命令。
（1） 在规定的 CSMA 时隙内收到正确的上行“抄表报文”并上报集中器， 则 pass；
（2） 其他情况，则 fail。
15.软件平台模拟集中器通过串口向待测 CCO 发送目标站点为 PCO1 的“监控从节点”命令，
同时启动定时器（定时时长 10s），查看是否收到“监控从节点”上行报文；
（1） 定时器溢出前，收到正确“监控从节点” 上行报文， 则 pass；
（2） 定时器溢出， 未收到正确“监控从节点” 上行报文， 则 fail；
（3） 其他情况，则 fail。
16.软件平台查看是否在规定的 CSMA 时隙内收到正确的下行“抄表报文”；
（1） 在规定的 CSMA 时隙内收到正确的下行“抄表报文”（考察代理主路径标识、
路由总跳数、路由剩余跳数、原始源 MAC 地址、原始目的 MAC 地址是否正确）， 则 pass；
（2） 在规定的 CSMA 时隙收到下行“抄表报文”，但报文错误，则 fail；
（3） 定时器溢出，未收到下行“抄表报文”，则 fail；
（4） 其他情况，则 fail。
17.软件平台模拟 PCO1 向待测 CCO 发送上行“抄表报文”命令。
（1） 在规定的 CSMA 时隙内收到正确的上行“抄表报文”并上报集中器， 则 pass；
（2） 其他情况，则 fail。
18.软件平台模拟 STA-1 向待测 CCO 发送上行、本地广播、应用层为“事件上报报文”命令，
同时启动定时器（定时时长 10s）。
（1） 在规定的 CSMA 时隙内收到正确的上行“事件上报报文”并上报集中器， 则
pass；
（2） 其他情况，则 fail。
19.软件平台模拟 PCO1 向待测 CCO 发送下行、代理广播、应用层为“事件上报报文”命令，
同时启动定时器（定时时长 10s）。
（1） 定时器超时后集中器未收到“事件上报报文”， 则 pass；
（2） 其他情况，则 fail。
20.软件平台模拟 STA-2 向待测 CCO 发送上行、全网广播、应用层为“事件上报报文”
命令，同时启动定时器（定时时长 10s）。
（1） 在规定的 CSMA 时隙内收到正确的上行“事件上报报文”并上报集中器，超时
也未发现 CCO 转发广播帧， 则 pass；
（2） 其他情况，则 fail。
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    cct = concentrator.Concentrator()
    cct.open_port()

    tc_common.activate_tb(tb,work_band = 1)

    cco_mac = '00-00-00-00-00-9C'
    tc_common.set_cco_mac_addr(cct,cco_mac)


    #set sub node address
    sub_nodes_addr = map(lambda x: '00-00-00-00-00-' + str(x).zfill(2), range(2,5))
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #wait for beacon from DTU
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    #sync the nid and sn between tb and DTU
    tb._configure_proxy('tb_time_config_req.yaml')
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)


#     next_phase = 1
#     beacon_period_num = 0
#     last_beacon_period_cnt = 0
#     last_beacon_period_len = 0
#     last_beacon_period_start_time = 0
#     phase_a_beacon_payload = None

    #while beacon_period_num < 10:
    for ii in range(0,3):
        #plc_tb_ctrl._debug("period: {}, phase: {}".format(beacon_period_num, next_phase))

#         [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10, None,
#             lambda beacon_fc,beacon_payload: beacon_fc.var_region_ver.phase == next_phase)

        [timestamp, beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10)

        assert beacon_payload.beacon_type == 'CENTRAL_BEACON', 'not central beacon'
        assert beacon_payload.association_start == 1
        assert beacon_payload.cco_mac_addr == cco_mac, "{},{}".format(beacon_payload.cco_mac_addr, cco_mac_addr)
        tolerance = plc_packet_helper.us_to_ntb(500) # TODO: 波特率限制导致信标发送时间过长
        # 检查接收时间是否与发送时间一致, TODO
        assert plc_packet_helper.check_ntb(beacon_fc.var_region_ver.timestamp, timestamp, -tolerance, tolerance)

        cur_phase = beacon_fc.var_region_ver.phase
        beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
        beacon_slot_len = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_slot_len)

        plc_tb_ctrl._debug('beacon phase:{}'.format(cur_phase))

        if cur_phase == 1:
            #phase_a_beacon_payload = beacon_payload

            # 检查A相信标的发送时间，应落在A相时隙内
            assert plc_packet_helper.check_ntb(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp,
                0, beacon_slot_len)
#             if beacon_period_num > 0:
#                 # 检查信标周期的开始时间是否符合信标周期
#                 assert (last_beacon_period_cnt + 1) == beacon_payload.beacon_period_counter
#                 diff = plc_packet_helper.ntb_diff(last_beacon_period_start_time, beacon_slot_alloc.beacon_period_start_time)
#                 tolerance = plc_packet_helper.ms_to_ntb(10) # TODO: CCO会在10ms内调整信标周期
#                 assert plc_packet_helper.check_ntb(diff, last_beacon_period_len, -tolerance, tolerance), "{},{},{}".format(diff, last_beacon_period_len, tolerance)
#             last_beacon_period_start_time = beacon_slot_alloc.beacon_period_start_time
#             last_beacon_period_cnt = beacon_payload.beacon_period_counter
#             last_beacon_period_len = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_period_len)
            #next_phase = 2
        elif 2 == cur_phase:
            # 检查B相信标的发送时间，应落在B相时隙内
            assert plc_packet_helper.check_ntb(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp,
                beacon_slot_len, beacon_slot_len * 2), "{},beacon_slot_len:{}".format(
                    plc_packet_helper.ntb_diff(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp), beacon_slot_len)
            #assert 0 == cmp(phase_a_beacon_payload, beacon_payload)
            #next_phase = 3
        elif 3 == cur_phase:
            # 检查C相信标的发送时间，应落在C相时隙内
            assert plc_packet_helper.check_ntb(beacon_slot_alloc.beacon_period_start_time, beacon_fc.var_region_ver.timestamp,
                beacon_slot_len * 2, beacon_slot_len * 3)
            #assert 0 == cmp(phase_a_beacon_payload, beacon_payload)
            #next_phase = 1
            #beacon_period_num += 1
        else:
            assert False


    #send 02-10 associate request
    sta_tei_list = []
    req_dict = tb._load_data_file('nml_assoc_req.yaml')
    for addr in sub_nodes_addr:
        req_dict['body']['mac'] = addr

        if '04' in addr:
            req_dict['body']['proxy_tei'][0] = 2
        msdu = plc_packet_helper.build_nmm(req_dict)

        #send association request to DUT (mac address is not in the white list)
        tb.mac_head.org_dst_tei = 1
        tb.mac_head.org_src_tei = 0
        tb.mac_head.mac_addr_flag = 1
        tb.mac_head.src_mac_addr = addr
        tb.mac_head.dst_mac_addr = cco_mac

        tb.tb_uart.clear_tb_port_rx_buf()
        tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)
        #time.sleep(0.5)

        [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)
        nmm.body.mac_sta in sub_nodes_addr

        if nmm.body.tei_sta not in sta_tei_list:
            sta_tei_list.append(nmm.body.tei_sta)


         #wait for beacon from DTU,it should include tei2's discover beacon
        [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

        #check parameters inside the central beacon
        beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
        beacon_slot_len = plc_packet_helper.ms_to_ntb(beacon_slot_alloc.beacon_slot_len)
        assert beacon_payload.beacon_type == 'CENTRAL_BEACON'
        #assert beacon_slot_alloc.ncb_slot_num == 1
        plc_tb_ctrl._debug('tei list:{0} ncb info:{1}'.format(sta_tei_list,beacon_slot_alloc.ncb_info))
        assert set(sta_tei_list) <= set([ncb_info.tei for ncb_info in beacon_slot_alloc.ncb_info])


        time.sleep(2)



    proxy_tei = sta_tei_list[0]
    cur_sta_tei = sta_tei_list[2]

    # 模拟集中器AFN13HF1（“监控从节点”命令）启动集中器主动抄表业务，
    # 用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
    # 点抄 tei=4的level=2的STA节点
    gdw1376p2_frame = tb._load_data_file('afn13f1_dl.yaml')
    gdw1376p2_frame['user_data']['value']['comm_module_flag'] = 1 #command to sta
    gdw1376p2_frame['user_data']['value']['a']['src'] = cco_mac
    gdw1376p2_frame['user_data']['value']['a']['dst'] = sub_nodes_addr[2]

    plc_tb_ctrl._debug(gdw1376p2_frame)

    #frame = concentrator.build_gdw1376p2_frame(data_file='afn13f1_dl.yaml')
    frame = concentrator.build_gdw1376p2_frame(gdw1376p2_frame)
    assert frame is not None
    cct.send_frame(frame)

    stop_time = time.time() + tc_common.calc_timeout(10)
    while True:
        result = tb._wait_for_fc_pl_data(tb._check_fc_pl_payload, timeout=1)

        if result is not None:
            [timestamp, fc, data] = result
            if ("PLC_MPDU_BEACON" == fc.mpdu_type):
                curr_beacon = data
            elif ("PLC_MPDU_SOF" == fc.mpdu_type):
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
                else:
                    break;
        assert time.time() < stop_time, "wait APL_CCT_METER_READ timeout"

    assert mac_frame.head.org_src_tei == 1
    assert mac_frame.head.tx_type == 'PLC_MAC_UNICAST', "tx_type:{}".format(mac_frame.head.tx_type)
    assert mac_frame.head.org_dst_tei == cur_sta_tei
    assert mac_frame.head.mac_addr_flag == 0
    assert fc.var_region_ver.dst_tei == proxy_tei
    #send meter read response packet in broadcast mode


    # 软件模拟STA2+电表, 回复抄表上行报文。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    ul_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_ul.yaml')
    ul_meter_read_pkt['body']['sn'] = apm.body.sn
    msdu = plc_packet_helper.build_apm(dict_content=ul_meter_read_pkt, is_dl=False)

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = cur_sta_tei
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 2
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.broadcast_dir= 0
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=proxy_tei, dst_tei=1,broadcast_flag = 0)


    #wait for meter read result coming from DUT(CCO)
    # 监控是否能够在n秒内收到CCO 上报的Q／GDW 1376.2 协议AFN13HF1 应答报文
    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x13, dt1=0x01, dt2=0, timeout=10)
    #监控集中器是否能收到待测CCO 转发的抄表上行报文。
    assert frame1376p2 is not None,           "AFN13H F1 not received"


    time.sleep(2)

    cur_sta_tei = proxy_tei
    #simulate a meter read from cco to pco(tei = 2)
    gdw1376p2_frame['user_data']['value']['comm_module_flag'] = 1 #command to sta
    gdw1376p2_frame['user_data']['value']['a']['src'] = cco_mac
    gdw1376p2_frame['user_data']['value']['a']['relay_addr'] = None
    gdw1376p2_frame['user_data']['value']['a']['dst'] = sub_nodes_addr[0]


    tb.tb_uart.clear_tb_port_rx_buf()
    #frame = concentrator.build_gdw1376p2_frame(data_file='afn13f1_dl.yaml')
    frame = concentrator.build_gdw1376p2_frame(gdw1376p2_frame)
    assert frame is not None
    cct.send_frame(frame)


    stop_time = time.time() + tc_common.calc_timeout(10)
    while True:
        result = tb._wait_for_fc_pl_data(tb._check_fc_pl_payload, timeout=1)

        if result is not None:
            [timestamp, fc, data] = result
            if ("PLC_MPDU_BEACON" == fc.mpdu_type):
                curr_beacon = data
            elif ("PLC_MPDU_SOF" == fc.mpdu_type):
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
                else:
                    break;
        assert time.time() < stop_time, "wait APL_CCT_METER_READ timeout"

    assert mac_frame.head.org_src_tei == 1
    assert mac_frame.head.tx_type == 'PLC_MAC_UNICAST'
    assert mac_frame.head.org_dst_tei == cur_sta_tei
    assert mac_frame.head.mac_addr_flag == 0
    assert fc.var_region_ver.dst_tei == cur_sta_tei
    #send meter read response packet in broadcast mode


    # 软件模拟STA2+电表, 回复抄表上行报文。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    ul_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_ul.yaml')
    ul_meter_read_pkt['body']['sn'] = apm.body.sn
    msdu = plc_packet_helper.build_apm(dict_content=ul_meter_read_pkt, is_dl=False)

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = cur_sta_tei
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.broadcast_dir= 0
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=proxy_tei, dst_tei=1,broadcast_flag = 0)


    #wait for meter read result coming from DUT(CCO)
    # 监控是否能够在n秒内收到CCO 上报的Q／GDW 1376.2 协议AFN13HF1 应答报文
    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x13, dt1=0x01, dt2=0, timeout=10)
    #监控集中器是否能收到待测CCO 转发的抄表上行报文。
    assert frame1376p2 is not None,           "AFN13H F1 not received"


    time.sleep(2)

    cur_sta_tei = sta_tei_list[1]
    ul_event_report_pkt = tb._load_data_file(data_file='apl_event_report_ul.yaml')
    #ul_event_report_pkt['body']['sn'] = apm.body.sn
    msdu = plc_packet_helper.build_apm(dict_content=ul_event_report_pkt, is_dl=False)

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = cur_sta_tei
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.broadcast_dir= 2
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=cur_sta_tei, dst_tei=1,broadcast_flag = 0)


    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x06, dt1=0x10, dt2=0, timeout=10)
    #监控集中器是否能收到待测CCO 转发的时间上报上行报文。
    assert frame1376p2 is not None,           "AFN13H F1 not received"


    time.sleep(2)

    #proxy broadcast event report packet, downlink
    cur_sta_tei = proxy_tei
    ul_event_report_pkt = tb._load_data_file(data_file='apl_event_report_ul.yaml')
    #ul_event_report_pkt['body']['sn'] = apm.body.sn
    msdu = plc_packet_helper.build_apm(dict_content=ul_event_report_pkt, is_dl=True)

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = cur_sta_tei
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_PROXY_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.broadcast_dir= 1 #downlink
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=cur_sta_tei, dst_tei=1,broadcast_flag = 0)


    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x06, dt1=0x10, dt2=0, timeout=10,tm_assert = False)
    #监控集中器是否能收到待测CCO 转发的时间上报上行报文。
    assert frame1376p2 is None


    #sta1 global broadcast event report packet, uplink
    cur_sta_tei = sta_tei_list[2]
    ul_event_report_pkt = tb._load_data_file(data_file='apl_event_report_ul.yaml')
    #ul_event_report_pkt['body']['sn'] = apm.body.sn
    msdu = plc_packet_helper.build_apm(dict_content=ul_event_report_pkt, is_dl=True)

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = cur_sta_tei
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_ENTIRE_NW_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 2
    tb.mac_head.remaining_hop_count = 2
    tb.mac_head.broadcast_dir= 2 #uplink
    tb.tb_uart.clear_tb_port_rx_buf()
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=cur_sta_tei, dst_tei=0xFFF,broadcast_flag = 1)


    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x06, dt1=0x10, dt2=0, timeout=10,tm_assert = False)
    #监控集中器是否能收到待测CCO 转发的时间上报上行报文。
    assert frame1376p2 is  not None


    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_ul('APL_EVENT_REPORT',10)

    cct.close_port()
