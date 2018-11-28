# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter

'''
1. 连接设备，上电初始化；
2. 软件平台模拟电表，在收到待测未入网 STA 的读表号请求后，通过串口向其下发表地址；
3. 软件平台模拟 CCO 通过透明物理设备向待测未入网 STA 设备发送【中央信标帧】，规划 CSMA
时隙（Ts~Te）， 软件平台记录本平台的【中央信标帧】的信标时间戳 T1，设置待测 STA 发送
的【关联请求】预期接收时间段△Tr 为（T1+Ts） ~（T1+Te),同时启动定时器（定时时长 10s），
查看是否在规定的 CSMA 时隙收到待测 STA 发出的【关联请求】报文；
4. 若软件平台在定时器时长内收到 STA 的【关联请求】，记录软件平台实际接收时间 TR,对比△
Tr 与 TR，若 TR 不在△Tr 范围内，则未入网 STA 收到中央信标后，不会调整自身的 NTB，反之
未入网 STA 收到中央信标后，会调整自身的 NTB；
5. 软件平台模拟 CCO 向请求入网 STA 设备发送【选择确认】以及【关联确认帧】，若 STA 收到【关
联确认帧】后，则 STA 请求入网成功；
6. 软件平台模拟 CCO 向待测入网 STA 设备发送【中央信标帧】， 规划发现信标时隙， 设置待测 STA
在发现信标时隙(Ts~Tn)内发送【发现信标帧】， 软件平台记录【中央信标帧】的信标时间戳
T1，设置【发现信标帧】预期接收时间段△Tr 为（T1+Ts） ~（T1+Tn),同时启动定时器（定时
时长 10s） ;
7. 若软件平台在定时器时长内收到入网 STA 的【发现信标帧】，记录软件平台实际接收时间 TR
与【发现信标帧】信标时间戳 T2,对比△Tr 与 TR、△Tr 与 T2，若 TR、 T2 均在△Tr 范围内，
则已入网 STA 在收到中央信标后，调整了自身的 NTB 与中央信标的时间戳同步，反之， STA 并
未调整自身的 NTB 与中央信标的时间戳同步；
8. 软件平台模拟未入网 STA-2 发起【关联请求】，由已入网 STA 转发【关联请求】， 软件平台模拟
CCO 接收已入网 STA 转发的【关联请求】，并发送【选择确认】以及【关联确认】给 PCO， PCO
转发【关联确认】给 STA-2， STA-2 请求入网成功；
9. 软件平台模拟 CCO 向待测 PCO 设备发送【中央信标帧】，规划代理信标时隙和发现信标时隙，
设置待测 PCO 在代理信标时隙(Ts~Tn)内发送【代理信标帧】， 软件平台记录【中央信标帧】的
信标时间戳 T1，设置【代理信标帧】预期接收时间段△Tr 为（T1+Ts） ~（T1+Tn),同时启动定
时器（定时时长 10s） ;
10. 若软件平台在定时器时长内收到 PCO 的【代理信标帧】，记录软件平台实际接收时间 TR 与【代
理信标帧】信标时间戳 T2,对比△Tr 与 TR、△Tr 与 T2，若 TR、 T2 均在△Tr 范围内，则 PCO
收到中央信标后，调整了自身的 NTB 与中央信标的时间戳同步， 反之， PCO 并未调整自身的 NTB
与中央信标的时间戳同步；
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    m = meter.Meter()
    m.open_port()

    tc_common.activate_tb(tb,work_band = 1)

    meter_addr = '12-34-56-78-90-12'
    tc_common.sta_init(m, meter_addr)

    timing_delta_allowed = 1000 #unit: us

    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['cfg_csma_flag'] = 1
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1

    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
    beacon_period = plc_packet_helper.ms_to_ntb(beacon_dict['period'])
    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    #config nid and nw_sn for sending of mpdu
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])



    # 等待STA1发送关联请求
    plc_tb_ctrl._debug("wait for assoc req")
    stop_time = time.time() + tc_common.calc_timeout(30)
    while True:
        assert time.time() < stop_time, "30s timeout"

        result = tb._wait_for_fc_pl_data(tb._check_fc_pl_payload, timeout=1, timeout_cb=lambda:None)

        if result is not None:
            [timestamp, fc, data] = result
            if ("PLC_MPDU_SOF" == fc.mpdu_type):
                sof_start_time = timestamp
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

                beacon_period_cnt = 0
                while not plc_packet_helper.ntb_inside_range(sof_start_time,
                                                             beacon_period_start_time,
                                                             beacon_period_end_time):
                    beacon_period_start_time = beacon_period_end_time
                    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)
                    beacon_period_cnt += 1

                curr_beacon = beacon_dict['payload']['value']
                curr_beacon['beacon_info']['beacon_item_list'][2]['beacon_item']['beacon_period_start_time'] = beacon_period_start_time
                frame_len = fc.var_region_ver.frame_len * 10
                sof_end_time = plc_packet_helper.ntb_add(sof_start_time, plc_packet_helper.us_to_ntb(frame_len))
                correct_time = plc_packet_helper.check_sof_time(sof_start_time, sof_end_time, phase, curr_beacon)
                assert correct_time, "wrong sof rx time"

                break


    #send associate confirm to STA
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_2.yaml')
    asso_cnf_dict['body']['level'] = 1
    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn

    #config the mac header
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = 1
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0,broadcast_flag = 1)


    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data_2.yaml')
    beacon_dict['num'] = 65535
    beacon_dict['payload']['value']['association_start'] = 1

    tb._configure_beacon(None, beacon_dict,True)



    #wait for discover beacon comming from DUT
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)
    #check parameters inside the proxy beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 2

    #which beacon period are we now?
    while not plc_packet_helper.ntb_inside_range(timestamp,
                                             beacon_period_start_time,
                                             beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)
        beacon_period_cnt += 1

    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    first_ncb_start_time = beacon_period_start_time + plc_packet_helper.ms_to_ntb(3*beacon_slot_alloc.beacon_slot_len)
    first_ncb_end_time = beacon_period_start_time + plc_packet_helper.ms_to_ntb(4*beacon_slot_alloc.beacon_slot_len)

    #allow 0.5ms timing delta
    first_ncb_start_time = plc_packet_helper.ntb_add(first_ncb_start_time,-plc_packet_helper.us_to_ntb(timing_delta_allowed))
    first_ncb_end_time = plc_packet_helper.ntb_add(first_ncb_end_time,plc_packet_helper.us_to_ntb(timing_delta_allowed))


    assert plc_packet_helper.ntb_inside_range(timestamp,
                                             first_ncb_start_time,
                                             first_ncb_end_time), 'beacon start:{}, ncb start:{} ncb end:{} ts:{}'.format(
                                             beacon_period_start_time,
                                             first_ncb_start_time,
                                             first_ncb_end_time,
                                             timestamp)



    #simulate another STA send association request to DUT
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.hop_limit = 2
    tb.mac_head.remaining_hop_count = 2
    tb.mac_head.src_mac_addr = '01-02-03-04-05-06'
    tb.mac_head.dst_mac_addr = cco_mac
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb._send_nmm('nml_assoc_req_2.yaml', tb.mac_head, src_tei = 0,dst_tei = 2)

    #wait for the relayed associated request coming from DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',15)
    assert nmm is not None


    time.sleep(2)
    tb.tb_uart.clear_tb_port_rx_buf()
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_2_2.yaml')
    asso_cnf_dict['body']['mac_sta'] = '01-02-03-04-05-06'
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn

    #config the mac header
    tb.mac_head.org_dst_tei = 2
    tb.mac_head.org_src_tei = 1
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei =2,broadcast_flag = 0)



    #send beacon periodically, in this beacon there has proxy and discover beacon scheduling
    beacon_dict = tb._load_data_file('tb_beacon_data_2_3.yaml')
    beacon_dict['num'] = 65535
    beacon_dict['payload']['value']['association_start'] = 1

    tb._configure_beacon(None, beacon_dict,True)


    #wait for discover beacon comming from DUT
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)
    #check parameters inside the proxy beacon
    assert beacon_payload.beacon_type == 'PROXY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_PCO'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 2

    #which beacon period are we now?
    while not plc_packet_helper.ntb_inside_range(timestamp,
                                             beacon_period_start_time,
                                             beacon_period_end_time):
        beacon_period_start_time = beacon_period_end_time
        beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)
        beacon_period_cnt += 1

    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    first_ncb_start_time = beacon_period_start_time + plc_packet_helper.ms_to_ntb(3*beacon_slot_alloc.beacon_slot_len)
    first_ncb_end_time = beacon_period_start_time + plc_packet_helper.ms_to_ntb(4*beacon_slot_alloc.beacon_slot_len)


    #allow 0.5ms timing delta
    first_ncb_start_time = plc_packet_helper.ntb_add(first_ncb_start_time,-plc_packet_helper.us_to_ntb(timing_delta_allowed))
    first_ncb_end_time = plc_packet_helper.ntb_add(first_ncb_end_time,plc_packet_helper.us_to_ntb(timing_delta_allowed))

    assert plc_packet_helper.ntb_inside_range(timestamp,
                                             first_ncb_start_time,
                                             first_ncb_end_time)

    m.close_port()


