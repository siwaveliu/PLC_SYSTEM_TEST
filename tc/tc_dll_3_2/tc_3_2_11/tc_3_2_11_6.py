# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter

'''
1. 选择链路层网络维护测试用例，被测 sta 上电
2. 测试用例通过载波透明接入单元发送中央信标帧。
3. 被测 sta 收到中央信标帧后，发起关联请求报文，申请入网。
4. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致150
性评价模块。
5. 一致性评价模块判断被测 sta 的关联请求报文正确后，通知测试用例。
6. 测试用例通过载波透明接入单元发送关联确认报文。
7. 被测 sta 收到关联确认报文后。
8. 测试用例通过载波透明接入单元发送中央信标报文，中央信标中安排被测 sta 发现信
标时隙，路由周期为 20s，发现站点发现列表周期为 2s。
9. 被测 sta 收到中央信标帧后，根据发现信标时隙发送发现信标。
10. 测试用例通过载波透明接入单元模拟二级站点关联请求报文给被测 sta， 载波信道侦
听单元收到被测 sta 转发的关联请求报文后，上传给测试台体，再送给一致性评价模
块。
11. 测试用例通过载波透明接入单元发送二级站点关联确认报文给被测 sta。
12. 被测 sta 收到二级站点关联确认报文后，转发二级站点关联确认报文。
13. 载波信道侦听单元收到被测 sta 转发的二级站点关联确认报文后，上传给测试台体，
再送给一致性评价模块。
14. 测试用例通过载波透明接入单元发送中央信标，中央信标中安排被测 sta 代理信标时
隙，二级站点发现信标时隙，路由周期为 20s，代理站点发现列表周期为 2s，发现站
点发现列表周期为 2s。
15. 被测 sta 收到中央信标后，发送代理信标。
16. 载波信道侦听单元收到被测 sta 的代理信标后，上传给测试台体，再送给一致性评价
模块。
17. 测试用例通过载波透明接入单元发送发现信标报文。
18. 测试用例按照代理站点发现列表周期通过载波透明接入单元发送 CCO 发现列表报
文。
19. 被测 sta 按照代理站点发现列表周期发送发现列表报文
20. 测试用例通过载波透明接入单元按照发现站点发现列表周期发送发现列表报文。
21. 被测 sta 按照 1/8 路由周期发送心跳检测报文，按照 4 个路由周期发送通信成功率上
报报文。
22. 载波信道侦听单元收到被测 sta 的发现列表报文、心跳检测报文、通信成功率上报报
文后，上传给测试台体，再送给一致性评价模块，在一个路由周期内应接收到多个被
测 sta 发现列表报文，一个路由周期内应受到多个心跳检测报文， 4 个路由周期至少
收到一次通信成功率上报报文
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
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 65535
    beacon_dict['payload']['value']['cco_mac_addr'] = cco_mac
    beacon_dict['payload']['value']['association_start'] = 1

    tb._configure_beacon(None, beacon_dict)

    #config nid and nw_sn for sending of mpdu
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    #set TB to reply SACK automatically
    #tb._config_sack_tei(beacon_dict['fc']['nid'],1,2)


    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_REQ'],15)


    #send associate confirm to STA
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_6.yaml')
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


    #in this central beacon, discovering beacon slot is reserved for tei2
    beacon_dict = tb._load_data_file('tb_beacon_data_6.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    time.sleep(2)

    #clear rx buffer before next waiting
    tb.tb_uart.clear_tb_port_rx_buf()

    #simulate another STA which is going to associate with network by discover beacon
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 2
    tb.mac_head.remaining_hop_count = 2
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb._send_nmm('nml_assoc_req_6.yaml', tb.mac_head, src_tei = 0,dst_tei = 2)

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
    asso_cnf_dict['body']['level'] = 2
    asso_cnf_dict['body']['tei_sta'] = 3
    asso_cnf_dict['body']['tei_proxy'] = 2
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn

    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #config the mac header
    tb.mac_head.org_dst_tei = 2
    tb.mac_head.org_src_tei = 1
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 2)

    #wait for the relayed association confirm
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_CNF',10)


    assert fc.var_region_ver.src_tei == 2
    assert fc.var_region_ver.broadcast_flag == 1
    assert mac_frame_head.tx_type == 'PLC_LOCAL_BROADCAST'
    assert mac_frame_head.hop_limit == 1
    assert mac_frame_head.remaining_hop_count == 1
    assert mac_frame_head.mac_addr_flag == 1
    assert mac_frame_head.dst_mac_addr == asso_cnf_dict['body']['mac_sta']


    assert 0 == cmp(asso_cnf_dict['body'],nmm.body)


    #central beacon with proxy and sta discover beacon is scheduled
    beacon_dict = tb._load_data_file('tb_beacon_data_6_2.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    #wait for proxy beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the proxy beacon
    assert beacon_payload.beacon_type == 'PROXY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_PCO'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 2



    #get sta discover packet sending period
    for beacon_item in beacon_dict['payload']['value']['beacon_info']['beacon_item_list']:
        if beacon_item['head'] == 'ROUTE_PARAM':
            route_period = beacon_item['beacon_item']['route_period']




    succ_report = 0
    sent_dnl_msg_num = 0
    #recv_discover_node_list = [0]
    discover_packet_num = 0

    plc_tb_ctrl._debug('begin to do discover packet statistics')

    #loop for 4 routing period
    for ii in range(0,4):
        route_period_remaining_time = 20
        recv_discover_node_list = [discover_packet_num/3] #each discover packet would be sent 3 times

        heart_beat_num = 0
        discover_packet_num = 0# clear discover packet received in last routing period

        sent_dnl_msg_num = 0 if ii==0 else route_period/2


        #while(time.time() < cur_time + sta_discovery_period*10):
        for kk in range(0,route_period/2):

            #route_period_remaining_time -= 2

            #send CCO discover packet and sta discover packet periodically
            discover_dict = tb._load_data_file('nml_discover_node_list_6.yaml')
            discover_dict['body']['sta_mac_addr'] = cco_mac
            discover_dict['body']['cco_mac_addr'] = cco_mac
            discover_dict['body']['route_period_remaining_time'] = route_period_remaining_time-2*kk
            discover_dict['body']['sent_dnl_msg_num'] = sent_dnl_msg_num
            discover_dict['body']['recv_discover_node_list'] = recv_discover_node_list


            msdu = plc_packet_helper.build_nmm(discover_dict)
            tb.mac_head.org_dst_tei = 0xFFF
            tb.mac_head.org_src_tei = 1
            tb.mac_head.hop_limit = 1
            tb.mac_head.remaining_hop_count = 1
            tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
            tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0xFFF,broadcast_flag= 1)




            discover_dict = tb._load_data_file('nml_discover_node_list_6_2.yaml')
            discover_dict['body']['sta_mac_addr'] = '00-00-00-00-00-06'
            discover_dict['body']['cco_mac_addr'] = cco_mac
            discover_dict['body']['route_period_remaining_time'] = route_period_remaining_time-2*kk
            discover_dict['body']['sent_dnl_msg_num'] = sent_dnl_msg_num
            discover_dict['body']['recv_discover_node_list'] = recv_discover_node_list

            msdu = plc_packet_helper.build_nmm(discover_dict)
#             tb.mac_head.org_dst_tei = 0xFFF
            tb.mac_head.org_src_tei = 3
#             tb.mac_head.hop_limit = 1
#             tb.mac_head.remaining_hop_count = 1
#             tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
            tb._send_msdu(msdu, tb.mac_head, src_tei = 3, dst_tei = 0xFFF,broadcast_flag= 1)

            #wait 2 seconds and check the nmm received
            cur_time = time.time()
            while(time.time() < cur_time + tc_common.calc_timeout(2)):
                ret = tb._wait_for_plc_nmm(['MME_DISCOVER_NODE_LIST','MME_HEARTBEAT_REPORT','MME_SUCC_RATE_REPORT'],
                                           0.5,
                                           (lambda:None))
                if ret is not None:

                    [fc, mac_frame_head, nmm] = ret
                    plc_tb_ctrl._debug('nmm type received:{}'.format(nmm.header.mmtype))

                    if nmm.header.mmtype == 'MME_DISCOVER_NODE_LIST':
                        discover_packet_num += 1
                    elif nmm.header.mmtype == 'MME_HEARTBEAT_REPORT':
                        heart_beat_num += 1
                    else:
                        succ_report += 1


        assert  heart_beat_num/5 > 1
        assert  discover_packet_num > 1

        plc_tb_ctrl._debug('routing period:{0} heart beat:{1} discover:{2}'.format(
                        ii,heart_beat_num,discover_packet_num))
    assert succ_report >= 1

    m.close_port()

