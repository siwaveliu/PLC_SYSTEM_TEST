# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter

'''
1. 选择链路层单网络组网测试用例，被测 sta 上电
2. 测试用例通过载波透明接入单元发送中央信标帧。
3. 被测 sta 收到中央信标帧后，发起关联请求报文，申请入网。
4. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致性
评价模块，判断被测 sta 的关联请求报文正确后，通知测试用例。
5. 测试用例通过载波透明接入单元发送关联确认报文。
6. 被测 sta 收到关联确认报文后。
7. 测试用例通过载波透明接入单元发送中央信标报文，中央信标中安排被测 sta 发现信标
时隙。
8. 被测 sta 收到中央信标帧后，根据中央信标安排的时隙发送发现信标报文。
9. 测试用例通过载波透明接入单元发送过零 NTB 采集指示报文。
10. 被测 sta 采集过零 NTB，发送过零 NTB 告知报文。
11. 载波信道侦听单元收到被测 sta 的过零 NTB 告知报文后，上传给测试台体，再送给一
致性评价模块。
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
    beacon_dict = tb._load_data_file('tb_beacon_data_16.yaml')
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
    asso_cnf_dict['body']['tei_sta'] = 2
    asso_cnf_dict['body']['level'] = 1
    asso_cnf_dict['body']['tei_proxy'] = nmm.body.proxy_tei[0]


    #config the mac header
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = nmm.body.proxy_tei[0]
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0,broadcast_flag = 1)


    #in this proxy beacon, discovering beacon slot is reserved for tei2
    beacon_dict = tb._load_data_file('tb_beacon_data_16_2.yaml')
    tb._configure_beacon(None, beacon_dict,True)



    #wait for discover beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 2
    assert beacon_payload.nw_sn == beacon_dict['payload']['value']['nw_sn']


    #send the 2nd level discover beacon and 2nd level discover packet periodically
    zerocross_colleting_req = tb._load_data_file('nml_zero_cross_ntb_collect_ind.yaml')
    zerocross_colleting_req['body']['tei'] = 2
    zerocross_colleting_req['body']['type'] = 'ZERO_CROSS_COLLECT_TYPE_SINGLE'
    zerocross_colleting_req['body']['num'] = 10

    #config the mac header
    tb.mac_head.org_dst_tei = 2
    tb.mac_head.org_src_tei = 1
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    msdu = plc_packet_helper.build_nmm(zerocross_colleting_req)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 2,broadcast_flag = 0)

    #wait for zero cross collect response packet coming from DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ZERO_CROSS_NTB_REPORT'],15)

    assert nmm is not None
    assert nmm.body.tei == 2
    assert nmm.body.num == 10


    m.close_port()


