# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 选择链路层网络维护测试用例，被测 cco 上电，通过串口给 CCO 加载白名单。
2. 载波信道侦听单元收到被测试 cco 的中央信标后，上传给测试台体，再送给一致性评
价模块。一致性评价模块判断被测 cco 的中央信标正确后，通知测试用例。
3. 测试用例通过载波透明接入单元发起关联请求报文，申请入网。
4. 被测 cco 收到关联请求报文后，回复关联确认报文。
5. 载波信道侦听单元收到被测 cco 的关联确认报文后，上传给测试台体，再送给一致性
评价模块。一致性评价模块判断被测 cco 的关联确认报文正确后，通知测试用例。
6. 测试用例依据关联确认报文 mac 帧头发送类型字段判断是否回复选择确认帧。
7. 被测 CCO 发送中央信标，应该安排发现信标时隙、代理站点发现列表周期（1/10 路由
周期）、发现站点发现列表周期（1/10 路由周期）、路由周期（20~420s）、信标周期（1~10s）
等参数。
8. 载波信道侦听单元收到被测 cco 的中央信标后，上传给测试台体，再送给一致性评价
模块。
9. 测试用例根据中央信标的时隙和路由周期安排，通过载波透明接入单元发送发现信标
报文、发现列表报文。
10. 测试用例停止发送任何报文，持续 10.5 个路由周期。
11. 载波信道侦听单元收到被测 cco 的信标帧后，上传给测试台体，再送给一致性评价模
块。
12. 在测试用例停止发送任何报文 10.5 个路由周期后，测试用例通过载波透明接入单元发
送发现列表报文
13. 被测 cco 收到发现列表报文后，发送离线指示报文。
14. 载波信道侦听单元收到被测 cco 的离线指示报文后，上传给测试台体，再送给一致性
评价模块。
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
    sub_nodes_addr = ['00-00-00-00-00-01']
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #wait for beacon from DTU
    route_period = tc_common.get_cco_route_period_from_beacon(tb,cco_mac,60)
    assert route_period
#     tb._configure_proxy('tb_time_config_req.yaml')
#     tb._configure_nw_static_para(beacon_fc.nid, beacon_payload.nw_sn)

    #send association request to DTU
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb._send_nmm('nml_assoc_req.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 30)


    cnf = nmm.body
    assert cnf.mac_sta == sub_nodes_addr[0]
    assert cnf.result == 'NML_ASSOCIATION_OK' or cnf.result =='NML_ASSOCIATION_KO_RETRY_OK'
    assert cnf.tei_proxy == 1
    
    
    tb._config_sta_tei(cnf.tei_sta,cnf.tei_proxy,cnf.level,'PLC_PHASE_A',cnf.mac_sta)
    
    
    
    #wait for beacon from DTU
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]
    
    #beacon should include discover beacon scheduling
    assert beacon_payload.beacon_type == 'CENTRAL_BEACON'
    beacon_item_num = beacon_payload.beacon_info.item_num
    beacon_item_list = beacon_payload.beacon_info.beacon_item_list
    
    for item in beacon_item_list:
        if item.head == 'STATION_CAPABILITY':
            pass
        elif item.head == 'ROUTE_PARAM':
            assert item.beacon_item.route_period > 0
            assert item.beacon_item.pco_discovery_period > 0
            assert item.beacon_item.sta_discovery_period > 0
            sta_discovery_period = item.beacon_item.sta_discovery_period 

        elif item.head == 'BAND_CHANGE':
            pass
        else:
            assert item.head == 'SLOT_ALLOC'
            assert item.beacon_item.cb_slot_num == 3
            assert item.beacon_item.ncb_slot_num >= 1
            assert cnf.tei_sta in [ncb_info_item.tei for ncb_info_item in item.beacon_item.ncb_info]
#         flag = 0
#         for sta_info in ind.sta_list:
#             flag |= sta_info.addr == sub_nodes_addr[0]
# 
#         #ensure sub node's address is in the list
#         assert flag == 1

    #wait for discover packet comming from DUT(CCO), discover packet only begin to send after 
    #network established completely
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_DISCOVER_NODE_LIST',route_period)
    
    assert nmm.body.tei == 1
    assert nmm.body.sta_mac_addr == cco_mac
#     assert nmm.body.station_num == 1        
#     assert nmm.body.recv_discover_node_list[0] == cnf.tei_sta

    
    
    #send discover packet in order for CCO to add this STA to it's neighbor list 
    discover_dict = tb._load_data_file('nml_discover_node_list_3.yaml')
    discover_dict['body']['sta_mac_addr'] = sub_nodes_addr[0]
    discover_dict['body']['cco_mac_addr'] = cco_mac
    discover_dict['body']['route_period_remaining_time'] = route_period


    msdu = plc_packet_helper.build_nmm(discover_dict)
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 2
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb._send_msdu(msdu, tb.mac_head, src_tei = 2, dst_tei = 1,broadcast_flag= 1) 
   
   
    #stop to send all packets include beacon
    tb._config_sta_tei(0,cnf.tei_proxy,cnf.level,'PLC_PHASE_A',cnf.mac_sta) 

    #wait 10.5 beacon periods and exhaust all messges received
    plc_tb_ctrl._debug('route_period1 = {}'.format(route_period))
    cur_time = time.time()
    next_period_time = cur_time + route_period
    period_num = 1
    while period_num <= 11:
        route_period = tc_common.get_cco_route_period_from_beacon(tb,cco_mac,60)
        assert route_period
        plc_tb_ctrl._debug('period_num = {} route_period = {}'.format(period_num,route_period))
        if time.time()>= next_period_time:
            next_period_time = time.time() + route_period
            period_num += 1
            if period_num == 11:
                next_period_time = time.time() + route_period //2
#while(time.time() < cur_time + tc_common.calc_timeout(route_period*10.5)):
#    offline_msg = tb._wait_for_plc_nmm('MME_OFFLINE_IND',2,lambda:{None})
#   if offline_msg is not None:
#       plc_tb_ctrl._debug('offline indication received!')
#       assert 0
#time.sleep(2)  
    
    
    #send discover packet 
    discover_dict = tb._load_data_file('nml_discover_node_list_3.yaml')
    discover_dict['body']['sta_mac_addr'] = sub_nodes_addr[0]
    discover_dict['body']['cco_mac_addr'] = cco_mac
    discover_dict['body']['route_period_remaining_time'] = route_period


    msdu = plc_packet_helper.build_nmm(discover_dict)
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 2
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb._send_msdu(msdu, tb.mac_head, src_tei = 2, dst_tei = 1,broadcast_flag= 1,auto_retrans=False)  

    #expect a offline nmm message is sent out from DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_OFFLINE_IND',10)
    
    assert sub_nodes_addr[0] in nmm.body.mac
                  
    cct.close_port()




