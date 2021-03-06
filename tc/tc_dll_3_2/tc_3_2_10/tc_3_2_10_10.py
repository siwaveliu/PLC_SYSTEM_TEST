# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import meter
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，将待测 STA 上电初始化；
2. 软件平台模拟电表，在收到待测 STA 的读表号请求后，向其下发表地址；
3. 软件平台模拟 PCO 周期性向待测 STA 设备发送“代理信标” 帧，收到“关联请求”
帧后，回复“关联确认” 帧，使站点入网成功；
4. 软件平台模拟 PCO 发送安排站点发送发现信标时隙的“代理信标”帧，启动定时时
间 15s,定时时间内软件平台若收不到站点发出的“发现信标”报文，则失败，若是
收到，则调用一致性评价模块，测试协议一致性，若不通过，则输出不通过；
5. 软件平台模拟 STA 发送“关联请求”，启动定时时间 15s,定时时间内收不到待测 STA
转发的“关联请求” 帧，则不通过，若收到，则调用一致性评价模块，测试协议一
致性，若不通过，则输出不通过；
6. 软件平台模拟 PCO 发送“关联确认”，启动定时时间 10s，定时时间内收不到待测 STA
转发的“关联确认”帧，则不通过，若收到，则调用一致性评价模块，测试协议一
致性，不通过则输出不通过，一致则测试通过。
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

    #send center beacon periodically
    #proxy_tei = 14
    beacon_dict = tb._load_data_file('tb_beacon_data_10.yaml')
    tb._configure_beacon(None, beacon_dict)

    #config nid and nw_sn for sending of mpdu
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])


    pco_mac = beacon_dict['payload']['value']['beacon_info']['beacon_item_list'][0]['beacon_item']['mac']
    pco_tei = beacon_dict['fc']['var_region_ver']['src_tei']
    pco_level = beacon_dict['payload']['value']['beacon_info']['beacon_item_list'][0]['beacon_item']['level']
    sta_tei = 5

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',15)


    #send associate confirm to STA
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_9.yaml')
    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    asso_cnf_dict['body']['level'] = pco_level + 1
    asso_cnf_dict['body']['tei_sta'] = sta_tei
    asso_cnf_dict['body']['tei_proxy'] = pco_tei

    #config the mac header
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = pco_tei
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = pco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head,
                  src_tei = pco_tei,
                  dst_tei = 0,
                  broadcast_flag = 1)


    #sleep 2 seconds for this beacon period to complete, and begin new beacon scheduling
    #in this central beacon, discovering beacon slot is reserved for tei2
    #time.sleep(2)
    beacon_dict = tb._load_data_file('tb_beacon_data_10_2.yaml')
    beacon_dict['payload']['value']['beacon_info']['beacon_item_list'][2]['beacon_item']['ncb_info'][1]['tei'] = sta_tei

    tb._configure_beacon(None, beacon_dict,True)

    #wait for discovering beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == pco_level + 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == pco_tei
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == sta_tei



    #send association request to DUT (mac address is not in the white list)
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = pco_level + 2
    tb.mac_head.remaining_hop_count = pco_level + 2
#     tb.mac_head.src_mac_addr = '1-2-3-4-5-6'
#     tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb._send_nmm('nml_assoc_req_10.yaml', tb.mac_head, src_tei = 0,dst_tei = sta_tei)

    #wait for the relayed associated request coming from DUT
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',15)



    time.sleep(0.5)
    #send associated confirm (for STA level 2) to DUT and hope it can be relayed to the level 2 STA
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_9.yaml')
    asso_cnf_dict['body']['mac_sta'] = nmm.body.mac
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['level'] = pco_level + 2
    asso_cnf_dict['body']['tei_sta'] = sta_tei + 1
    asso_cnf_dict['body']['tei_proxy'] = sta_tei
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn

    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #config the mac header
    tb.mac_head.org_dst_tei = sta_tei
    tb.mac_head.org_src_tei = pco_tei
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb._send_msdu(msdu, tb.mac_head, src_tei = pco_tei, dst_tei = sta_tei)

    #wait for the relayed association confirm
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_CNF',10)


    assert fc.var_region_ver.src_tei == sta_tei
    assert fc.var_region_ver.broadcast_flag == 1
    assert mac_frame_head.tx_type == 'PLC_LOCAL_BROADCAST'
    assert mac_frame_head.hop_limit == 1
    assert mac_frame_head.remaining_hop_count == 1
    assert mac_frame_head.mac_addr_flag == 1
    assert mac_frame_head.dst_mac_addr == asso_cnf_dict['body']['mac_sta']


    assert 0 == cmp(asso_cnf_dict['body'],nmm.body)






    m.close_port()






