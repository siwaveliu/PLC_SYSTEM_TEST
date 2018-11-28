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
4. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致性
评价模块。
5. 一致性评价模块判断被测 sta 的关联请求报文正确后，通知测试用例。
6. 测试用例通过载波透明接入单元发送关联确认报文。
7. 被测 sta 收到关联确认报文后。
8. 测试用例通过载波透明接入单元发送中央信标报文，中央信标中安排被测 sta 发现信标
时隙。
9. 被测 sta 收到中央信标帧后，根据中央信标安排的时隙发送发现信标报文。
10. 载波信道侦听单元收到被测 sta 的发现信标报文后，上传给测试台体，再送给一致性评
价模块。
11. 测试用例通过载波透明接入单元发送被测 sta 离线指示报文。
12. 被测 sta 收到离线指示报文后，主动离线。
13. 测试用例按照信标周期通过载波透明接入单元发送中央信标，被测 sta 收到中央信标
好，重新发起关联请求加入网络。
14. 载波信道侦听单元收到被测 sta 的关联请求报文后，上传给测试台体，再送给一致性评
价模块。
15. 一致性评价模块判断被测 sta 的关联请求报文正确后，通知测试用例。
16. 测试用例通过载波透明接入单元发送关联确认报文。
17. 被测 sta 收到关联确认报文后。
18. 测试用例通过载波透明接入单元发送中央信标报文，中央信标中安排被测 sta 发现信标
时隙。
19. 被测 sta 收到中央信标帧后，根据中央信标安排的时隙发送发现信标报文。
20. 载波信道侦听单元收到被测 sta 的发现信标报文后，上传给测试台体，再送给一致性评
价模块。
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
    beacon_dict = tb._load_data_file('tb_beacon_data_7.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    #wait for proxy beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 2
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']




    tb.tb_uart.clear_tb_port_rx_buf()


    #offline request will be sent
    offline_req = tb._load_data_file('nml_offline_ind.yaml')
    offline_req['body']['num'] = 1
    offline_req['body']['mac'][0] = meter_addr
    offline_req['reason'] = 'NML_NM_OFFLINE_REASON_CCO_REQUEST'

    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = 1
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    msdu = plc_packet_helper.build_nmm(offline_req)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0,broadcast_flag = 1)


    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['payload']['value']['association_start'] = 1
    tb._configure_beacon(None, beacon_dict,True)



    #wait for the new associated request
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_REQ'],15)

    #send associated confirm
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0,broadcast_flag = 1)

    #schedule discover beacon for DUT
    beacon_dict = tb._load_data_file('tb_beacon_data_7.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    #wait for proxy beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 2
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']




    m.close_port()


