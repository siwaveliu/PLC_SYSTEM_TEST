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
2. 测试用例通过载波透明接入单元发送发现信标帧。
3. 被测 sta 收到发现信标帧后，发起关联请求报文，申请入网。
4. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致性
评价模块。
5. 一致性评价模块判断被测 sta 的关联请求报文正确后，通知测试用例。
6. 测试用例通过载波透明接入单元发送关联确认报文。
7. 被测 sta 收到关联确认报文后。
8. 测试用例通过载波透明接入单元发送代理信标报文，代理信标中安排被测 sta 发现信标
时隙。
9. 被测 sta 收到代理信标帧后，根据发现信标时隙发送发现信标。
10. 载波信道侦听单元收到被测 sta 的发现信标报文后，上传给测试台体，再送给一致性评
价模块
11. 测试用例通过载波透明接入单元按照信标时隙，发送代理信标，其站点能力条目层级
变更为 15 级，连续发送 1 个路由周期。
12. 被测 sta 收到代理信标帧后，主动离线。
13. 测试用例通过载波透明接入单元按照信标时隙，发送代理信标，站点能力条目中 sta 层
级变更为 14 级。
14. 被测 sta 收到代理信标帧后，发起关联请求。
15. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致性
评价模块。
16. 一致性评价模块判断被测 sta 的关联请求报文正确后，通知测试用例。
17. 测试用例通过载波透明接入单元发送关联确认报文。
18. 被测 sta 收到关联确认报文后。
19. 测试用例通过载波透明接入单元发送代理信标报文，代理信标中安排被测 sta 发现信标
时隙。
20. 被测 sta 收到中央信标帧后，根据发现信标时隙发送发现信标。
21. 载波信道侦听单元收到被测 sta 的发现信标报文后，上传给测试台体，再送给一致性评
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
    beacon_dict = tb._load_data_file('tb_beacon_data_11.yaml')
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
    asso_cnf_dict['body']['tei_sta'] = 15
    asso_cnf_dict['body']['level'] = 15
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
    beacon_dict = tb._load_data_file('tb_beacon_data_11_2.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    #wait for discover beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 15
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 14
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 15
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']




    tb.tb_uart.clear_tb_port_rx_buf()

    #DUT's proxy level is changed to 15
    for beacon_item in beacon_dict['payload']['value']['beacon_info']['beacon_item_list']:
        if beacon_item['head'] == 'STATION_CAPABILITY':
           beacon_item['beacon_item']['level'] = 15
        elif beacon_item['head'] == 'ROUTE_PARAM':
            routing_period = beacon_item['beacon_item']['route_period']

    tb._configure_beacon(None, beacon_dict,True)


    #wait for a routing period, in this period, DUT should be offlined
    ret = tb._wait_for_plc_nmm(['MME_ASSOC_REQ'],routing_period,lambda:{None})
    assert ret is None



    #DUT's proxy level is changed to 14
    for beacon_item in beacon_dict['payload']['value']['beacon_info']['beacon_item_list']:
        if beacon_item['head'] == 'STATION_CAPABILITY':
           beacon_item['beacon_item']['level'] = 14

    tb._configure_beacon(None, beacon_dict,True)

    #wait for the new associated request
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_REQ'],15)


    #send associated confirm
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0,broadcast_flag = 1)



    #wait for discover beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 15
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 14
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 15
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']


    m.close_port()


