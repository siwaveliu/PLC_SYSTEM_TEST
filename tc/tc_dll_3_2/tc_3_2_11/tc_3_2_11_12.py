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
2. 测试用例通过载波透明接入单元发送发现信标帧，站点能力条目层级是 1。
3. 被测 sta 收到发现信标帧后，发起关联请求报文，申请入网。
4. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致性
评价模块。
5. 一致性评价模块判断被测 sta 的关联请求报文正确后，通知测试用例。
6. 测试用例通过载波透明接入单元发送关联确认报文。
7. 被测 sta 收到关联确认报文后。
8. 测试用例通过载波透明接入单元发送代理信标报文，代理信标中安排被测 sta 发现信标
时隙。
9. 被测 sta 收到代理信标帧后，根据发现信标时隙发送发现信标，站点能力条目层级是 2。
10. 载波信道侦听单元收到被测 sta 的发现信标报文后，上传给测试台体，再送给一致性评
价模块
11. 测试用例通过载波透明接入单元按照发现信标时隙发送发现信标(2 级站点，站点 mac
地址和 TEI 变更)，并设置组网完成。测试用例通过载波透明接入单元按照路由周期发
送发现列表报文(2 级站点)，发现列表中携带一级站点、被测 sta 站点信息。
12. 2 个路由周期后，被测 sta 发送代理变更请求给 2 级站点。
a) 载波信道侦听单元收到被测 sta 的代理变更请求报文后，上传给测试台体，再送给
一致性评价模块，判断转发代理变更请求正确后，通知测试用例。
b) 测试用例通过载波透明接入单元发送 2 级站点代理变更请求确认报文。
c) 被测 sta 收到 2 级站点代理变更请求确认报文后变更相应的路由表项及层级。
d) 测试用例通过载波透明接入单元发送代理信标报文，代理信标中安排被测 sta 发现
信标时隙。
e) 被测 sta 收到代理信标帧后，根据发现信标时隙发送发现信标，站点能力条目层级
是 3。
13. 载波信道侦听单元收到被测 sta 的发现信标报文后，上传给测试台体，再送给一致性评
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
    beacon_dict = tb._load_data_file('tb_beacon_data_12.yaml')
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
    asso_cnf_dict['body']['tei_sta'] = 3
    asso_cnf_dict['body']['level'] = 2
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
    beacon_dict = tb._load_data_file('tb_beacon_data_12_2.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    #wait for discover beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 2
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 2
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 3
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']


    #send the 2nd level discover beacon and 2nd level discover packet periodically
    beacon_dict = tb._load_data_file('tb_beacon_data_12_3.yaml')
    tb._configure_beacon(None, beacon_dict,True)

    routing_period = beacon_dict['payload']['value']['beacon_info']['beacon_item_list'][1]['beacon_item']['route_period']
    stop_time = time.time() + tc_common.calc_timeout(routing_period)

    time.sleep(2)
    tb.tb_uart.clear_tb_port_rx_buf()

    #while time.time() < stop_time:
    for dummy in range(0,3):
        for ii in range(0,10):
            discover_dict = tb._load_data_file('nml_discover_node_list_12.yaml')
            discover_dict['body']['sta_mac_addr'] = '00-00-00-00-00-04'
            discover_dict['body']['cco_mac_addr'] = cco_mac

            routing_period_remain = routing_period-10*ii-2
            discover_dict['body']['route_period_remaining_time'] = routing_period_remain if routing_period_remain>0 else 0


            msdu = plc_packet_helper.build_nmm(discover_dict)
            tb.mac_head.org_dst_tei = 0xFFF
            tb.mac_head.org_src_tei = 4
            tb.mac_head.hop_limit = 1
            tb.mac_head.remaining_hop_count = 1
            tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
            tb._send_msdu(msdu, tb.mac_head, src_tei = 4, dst_tei = 0xFFF,broadcast_flag= 1)

            #time.sleep(routing_period/10)

            ret = tb._wait_for_plc_nmm(['MME_PROXY_CHANGE_REQ'],routing_period/10,lambda:None)
            if ret is not None:
                [fc, mac_frame_head, nmm] = ret
                break
        if ret is not None:
            break
    else:
        assert 0 , 'proxy change request did not be received'


    #check the proxy change request message
    assert nmm.body.tei == 3
    assert nmm.body.proxy_tei[0] == 4
    assert nmm.body.old_proxy == 2


    #send proxy change confirm
    proxy_change_cnf = tb._load_data_file('nml_proxy_change_cnf.yaml')
    proxy_change_cnf['body']['p2p_sn'] = nmm.body.p2p_sn
    msdu = plc_packet_helper.build_nmm(proxy_change_cnf)
    tb.mac_head.org_dst_tei = 3
    tb.mac_head.org_src_tei = 1
    tb.mac_head.hop_limit = 3
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb._send_msdu(msdu, tb.mac_head, src_tei = 4, dst_tei = 3,broadcast_flag= 0)


    #send the 2nd level discover beacon and 2nd level discover packet periodically
    beacon_dict = tb._load_data_file('tb_beacon_data_12_4.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    tb.tb_uart.clear_tb_port_rx_buf()

    #wait for discover beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 3
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 4
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 3
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']


    m.close_port()


