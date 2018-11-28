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
6. 被测 CCO 发送中央信标，应该安排发现信标时隙、代理站点发现列表周期、发现站点
发现列表周期、路由周期、信标周期等参数。
7. 载波信道侦听单元收到被测 cco 的中央信标后，上传给测试台体，再送给一致性评价
模块。
8. 测试用例根据中央信标的时隙和路由周期安排，通过载波透明接入单元发送发现信标
报文、发现列表报文。
9. 测试台体通过串口删除 CCO 白名单
10. 被测 cco 白名单变更生效后，发送离线指示报文。
11. 载波信道侦听单元收到被测 cco 的离线指示报文后，上传给测试台体，再送给一致性
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
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    #sync the nid and sn between tb and DTU
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)
    
    #check beacon payload
    assert beacon_payload.cco_mac_addr == '00-00-00-00-00-9C'
    
    for item in beacon_payload.beacon_info.beacon_item_list:
        if item.head == 'ROUTE_PARAM':
            route_period = item.beacon_item.route_period
            discover_period = item.beacon_item.sta_discovery_period
            
    assert route_period is not None
    assert discover_period is not None
    
#     tb._configure_proxy('tb_time_config_req.yaml')
#     tb._configure_nw_static_para(beacon_fc.nid, beacon_payload.nw_sn)

    #send association request to DTU
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb._send_nmm('nml_assoc_req.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)


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

    
    #remove the STA from white list 
    tc_common.del_sub_node_addr(cct, sub_nodes_addr)
    
    
    #expect a offline nmm message is sent out from DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_OFFLINE_IND',10)
    
    assert sub_nodes_addr[0] in nmm.body.mac
                  
    cct.close_port()



# def _check_plc_beacon_or_nmm(fc_pl_data_payload, mmtype = None):
#         '''
#         Args:
#             fc_pl_data_payload: plc_test_frame.fc_pl_data
# 
#         Return:
#             [fc, beacon_payload]
#         '''
#         pb_size = fc_pl_data_payload.pb_size
#         pb_num = fc_pl_data_payload.pb_num
#         fc_pl_data = fc_pl_data_payload.payload.data
#         beacon_payload = None
#         mac_frame = None
#         fc = fc_pl_data[0:16]
#         fc = plc_packet_helper.parse_mpdu_fc(fc)
#         
#         if (fc is not None):
#             if ("PLC_MPDU_BEACON" == fc.mpdu_type):
#                 pb_size = fc_pl_data_payload.pb_size
#                 beacon_payload = plc_packet_helper.get_beacon_payload(fc_pl_data_payload.pb_num, pb_size, fc_pl_data[16:(16+pb_size)])
#             elif ("PLC_MPDU_SOF" == fc.mpdu_type):
#                 mac_frame = plc_packet_helper.reassemble_mac_frame(pb_num, pb_size, fc_pl_data[16:(16+pb_size*pb_num)])
#                 
#         if (beacon_payload is None) and (mac_frame is None):
#             return None
# 
#         if beacon_payload is not None:
#             return ['beacon',fc_pl_data_payload.timestamp, fc, beacon_payload]
#     
#         elif mac_frame is not None:
#             valid = plc_packet_helper.check_mac_frame_crc(mac_frame)
#             if not valid:
#                 _debug('Invalid mac frame crc')
#                 return None
#     
#             if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_NMM":
#                 _debug('Unexpected msdu type')
#                 return None
#     
#             nmm = mac_frame.msdu.value
#             #if (mmtype is not None) and (mmtype != nmm.header.mmtype):
#             if (mmtype is not None) and not (nmm.header.mmtype in mmtype):
#                 _debug('Unexpected nmm type')
#                 return None
#     
#             return ['nmm',fc, mac_frame.head, nmm]


