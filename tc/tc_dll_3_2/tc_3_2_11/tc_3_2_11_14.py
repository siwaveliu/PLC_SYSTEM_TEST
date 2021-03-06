# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter
import config

'''
1. 选择链路层网络维护测试用例，被测 sta 上电
2. 测试用例通过载波透明接入单元发送发现信标帧，站点能力条目层级是 2。
3. 被测 sta 收到发现信标帧后，发起关联请求报文，申请入网。
4. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致性
评价模块，判断被测 sta 的关联请求报文正确后，通知测试用例。
5. 测试用例通过载波透明接入单元发送关联确认报文。
6. 被测 sta 收到关联确认报文后。
7. 测试用例通过载波透明接入单元发送代理信标报文，代理信标中安排被测 sta 发现信标
时隙。
8. 被测 sta 收到代理信标帧后，根据发现信标时隙发送发现信标，站点能力条目层级是 3。
9. 载波信道侦听单元收到被测 sta 的发现信标报文后，上传给测试台体，再送给一致性评
价模块
10. 测试用例通过载波透明接入单元向被测 sta 发起四级站点关联请求。
11. 被测 sta 接收到关联请求后，转发给二级站点
12. 载波信道侦听单元收到被测 sta 转发的关联请求报文后，上传给测试台体，再送给一致
性评价模块，判断被测 sta 的关联请求报文正确后，通知测试用例。
13. 测试用例通过载波透明接入单元发送二级站点关联请求确认报文。
14. 被测 sta 接收到关联请求确认报文后，转发给四级站点。
15. 载波信道侦听单元收到被测 sta 转发的关联请求确认报文后，上传给测试台体，再送给
一致性评价模块，判断被测 sta 的关联请求报文正确后，通知测试用例。
16. 测试用例通过载波透明接入单元发送二级站点代理信标报文，代理信标中安排被测 sta
代理信标时隙和四级站点发现信标时隙。
17. 被测 sta 收到代理信标帧后，根据代理信标时隙发送代理信标，站点能力条目层级是 3。
18. 载波信道侦听单元收到被测 sta 的代理信标报文后，上传给测试台体，再送给一致性评
价模块
19. 经过一段时间(2 个路由周期)，测试用例通过载波透明接入单元发送二级站点路由请求
报文，最终目的站点为 4 级站点。
20. 被测 sta 收到路由请求报文后，转发路由请求报文
21. 载波信道侦听单元收到被测 sta 的转发的路由请求报文后，上传给测试台体，再送给一
致性评价模块，判断被测 sta 的转发的路由请求报文正确后，通知测试用例。
22. 测试用例通过载波透明接入单元发送四级站点链路确认请求报文
23. 被测 sta 收到链路确认请求报文后，发送链路确认回应报文。
24. 载波信道侦听单元收到被测 sta 的链路确认回应报文后，上传给测试台体，再送给一致
性评价模块，判断被测 sta 的链路确认回应报文正确后，通知测试用例
25. 测试用例通过载波透明接入单元发送四级站点路由回复报文
26. 被测 sta 收到路由回复报文后，转发路由回复报文给二级站点。
27. 载波信道侦听单元收到被测 sta 的转发的路由回复报文后，上传给测试台体，再送给一
致性评价模块，判断被测 sta 的转发的路由回复报文正确后，通知测试用例。
28. 测试用例通过载波透明接入单元发送二级站点路由应答报文，
29. 被测 sta 收到二级站点路由应答报文后，转发路由应答报文给四级站点
30. 载波信道侦听单元收到被测 sta 的路由应答报文后，上传给测试台体，再送给一致性评
价模块
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

    cco_mac = '00-00-C0-A8-01-01'
    meter_addr = '12-34-56-78-90-12'
    tc_common.sta_init(m, meter_addr)

    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data_14.yaml')
    beacon_dict['payload']['value']['association_start'] = 1

    tb._configure_beacon(None, beacon_dict)

    #config nid and nw_sn for sending of mpdu
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_REQ'],15)


    #send associate confirm to STA from a simulated STA( tei = 2, mac = 00-00-00-00-00-01)
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_4.yaml')
    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    asso_cnf_dict['body']['tei_sta'] = 4
    asso_cnf_dict['body']['level'] = 3
    asso_cnf_dict['body']['tei_proxy'] = nmm.body.proxy_tei[0]


    #config the mac header
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = nmm.body.proxy_tei[0]
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = '00-00-00-00-00-14'
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = nmm.body.proxy_tei[0], dst_tei = 0,broadcast_flag = 1)


    #in this proxy beacon, discovering beacon slot is reserved for tei2
    beacon_dict = tb._load_data_file('tb_beacon_data_14_2.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    #wait for discover beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 3
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 3
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 4
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']


    #associate request from a simulated STA which select DUT(tei = 3) as it's proxy
    time.sleep(2)

    #clear rx buffer before next waiting
    tb.tb_uart.clear_tb_port_rx_buf()

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 3
    tb.mac_head.remaining_hop_count = 3
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb._send_nmm('nml_assoc_req_14.yaml', tb.mac_head, src_tei = 0,dst_tei = 4)

    #wait for the relayed associated request coming from DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',15)

    #check the relayed association request
    plc_tb_ctrl._debug('mac in asso req:{}'.format(nmm.body.mac))
    assert nmm.body.mac == '00-00-00-00-00-06'

    tb.tb_uart.clear_tb_port_rx_buf()
    time.sleep(0.5)
    #send associated confirm (for STA level 2) to DUT and hope it can be relayed to the level 2 STA
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_6.yaml')
    asso_cnf_dict['body']['mac_sta'] = nmm.body.mac
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['level'] = 4
    asso_cnf_dict['body']['tei_sta'] = 5
    asso_cnf_dict['body']['tei_proxy'] = 4
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn

    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #config the mac header
    tb.mac_head.org_dst_tei = 4
    tb.mac_head.org_src_tei = 3
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb._send_msdu(msdu, tb.mac_head, src_tei = 3, dst_tei = 4)

    #wait for the relayed association confirm
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_CNF',10)


    assert fc.var_region_ver.src_tei == 4
    assert fc.var_region_ver.broadcast_flag == 1
    assert mac_frame_head.tx_type == 'PLC_LOCAL_BROADCAST'
    assert mac_frame_head.hop_limit == 1
    assert mac_frame_head.remaining_hop_count == 1
    assert mac_frame_head.mac_addr_flag == 1
    assert mac_frame_head.dst_mac_addr == asso_cnf_dict['body']['mac_sta']


    assert 0 == cmp(asso_cnf_dict['body'],nmm.body)


    #proxy beacon with proxy and sta discover beacon is scheduled
    beacon_dict = tb._load_data_file('tb_beacon_data_14_1.yaml')
    tb._configure_beacon(None, beacon_dict,True)

    time.sleep(2)
    tb.tb_uart.clear_tb_port_rx_buf()


    #wait for proxy beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'PROXY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 3
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 3
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_PCO'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 4
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']

    routing_para = plc_packet_helper.get_beacon_routing_parameters(beacon_payload)

    #wait for 2 routing periods
    stop_time = time.time() + routing_para.route_period*2*config.CLOCK_RATE

    while time.time() < stop_time:
    #for ii in range(routing_para.route_period):
        waiting_time = stop_time - time.time()


        ret = tb._wait_for_plc_beacon(waiting_time/float(config.CLOCK_RATE)
                                          ,lambda:None)

        #time.sleep(1*config.CLOCK_RATE)
        if ret is not None:
            plc_tb_ctrl._debug('beacon received!')


    #send meter read request to DUT with a invalid tei
#     tb.tb_uart.clear_tb_port_rx_buf()
#     plc_tb_ctrl._debug("Step 4: simulate CCO to send cct meter read pkt...")
#
#     dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')
#     dl_meter_read_pkt['body']['sn'] = 123
#
#     dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))
#
#     plc_tb_ctrl._debug(dl_meter_read_pkt)
#     #dl_apl_645 = dl_meter_read_pkt['body']['data']
#     msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)
#
#     tb.mac_head.org_dst_tei         = 5  #DUT tei is 3, trig packet routing request
#     tb.mac_head.org_src_tei         = 1
#     tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
#     tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
#     tb.mac_head.mac_addr_flag       = 0
#     tb.mac_head.hop_limit           = 15
#     tb.mac_head.remaining_hop_count = 15
#     tb.mac_head.broadcast_dir       = 1 #downlink broadcast
#
#     tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=2, dst_tei=3, broadcast_flag = 0)

    #send route request to DUT
    route_req = tb._load_data_file("nml_route_req.yaml")
    route_req['body']['data'][0]['tei'] = 5
    msdu = plc_packet_helper.build_nmm(dict_content=route_req)

    tb.mac_head.org_dst_tei         = 5  #DUT tei is 4, trig packet routing request
    tb.mac_head.org_src_tei         = 3
    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_NMM"
    tb.mac_head.tx_type             = 'PLC_MAC_ENTIRE_NW_BROADCAST'
    tb.mac_head.mac_addr_flag       = 0
    tb.mac_head.hop_limit           = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir       = 1 #downlink broadcast
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=3, dst_tei=4, broadcast_flag = 1,auto_retrans=False)


    #wait for route_reqeust relayed by DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ROUTE_REQ',10)
    assert mac_frame_head.tx_type == 'PLC_MAC_ENTIRE_NW_BROADCAST'
    assert mac_frame_head.org_dst_tei == 5
    assert mac_frame_head.hop_limit == 15
    assert mac_frame_head.remaining_hop_count == 14

    sn_in_route_req = nmm.body.sn

    #time.sleep(2)

    #simulate a link confirm request
    link_cnf_req = tb._load_data_file('nml_link_confirm_req.yaml')
    link_cnf_req['body']['sn'] = sn_in_route_req
    #link_cnf_req['body']['confirm_sta_num'] = 5
    link_cnf_req['body']['confirm_sta_list'][0] = 4


    msdu = plc_packet_helper.build_nmm(link_cnf_req)

    #config the mac header
    tb.mac_head.org_dst_tei = 4
    tb.mac_head.org_src_tei = 5
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.msdu_type  = "PLC_MSDU_TYPE_NMM"
    tb._send_msdu(msdu, tb.mac_head, src_tei = 5, dst_tei = 4)


    #wait for link confirm response  from DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_LINK_CONFIRM_RSP',10)
    assert fc.var_region_ver.src_tei == 4
    assert fc.var_region_ver.broadcast_flag == 0
    assert mac_frame_head.tx_type == 'PLC_MAC_UNICAST'

    assert mac_frame_head.org_dst_tei == 5
    assert mac_frame_head.hop_limit == 1
    assert mac_frame_head.remaining_hop_count == 1


    #simulate a route reply packet
    route_reply = tb._load_data_file('nml_route_reply.yaml')
    route_reply['body']['sn'] = sn_in_route_req



    msdu = plc_packet_helper.build_nmm(route_reply)

    #config the mac header
    tb.mac_head.org_dst_tei = 4
    tb.mac_head.org_src_tei = 5
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb._send_msdu(msdu, tb.mac_head, src_tei = 5, dst_tei = 4)


    #wait for route reply packet relayed by DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ROUTE_REPLY',10)
    assert mac_frame_head.tx_type == 'PLC_MAC_UNICAST'
    assert mac_frame_head.org_dst_tei == 3
    assert mac_frame_head.org_src_tei == 4
    assert mac_frame_head.hop_limit == 1
    assert mac_frame_head.remaining_hop_count == 1
    assert nmm.body.sn == sn_in_route_req



    #simulate a route ack from TEI 3 STA
    route_ack = tb._load_data_file('nml_route_ack.yaml')
    route_ack['body']['sn'] = sn_in_route_req
    msdu = plc_packet_helper.build_nmm(route_ack)

    #config the mac header
    tb.mac_head.org_dst_tei = 4
    tb.mac_head.org_src_tei = 3
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb._send_msdu(msdu, tb.mac_head, src_tei = 3, dst_tei = 4)

    #wait for routing ack relayed by DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ROUTE_ACK',10)
    assert nmm.body.sn == sn_in_route_req


    m.close_port()


