# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import meter
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，上电初始化；
2. 软件平台模拟电表，在收到待测 STA 的读表号请求后，向其下发表地址；
3. 软件平台模拟 CCO 向待测设备发送“中央信标”；
4. 软件平台模拟 CCO 在收到待测 STA 发送的“关联请求报文” 后，向待测 STA 发送“关
联确认报文” （拒绝入网，指定重新关联时间 10s），
5. 同时启动定时器 T1（定时时长 10s），定时器 T2（定时时长 20s）查看定时器溢出时是
否再次收到“关联请求报文”；
（1） 定时器 T1 未溢出，收到“关联请求报文” ，则 fail；
（2） 定时器 T1 溢出，定时器 T2 未溢出，收到报文，但报文错误，则 fail；
（3） 定时器 T1 溢出，定时器 T2 未溢出，收到正确的“关联请求报文”，则 pass；
（4） 定时器 T1 溢出，定时器 T2 溢出，未收到“关联请求报文”，则 fail；
（5） 其他情况，则 fail。
（6） 软件平台模拟 CCO 在收到待测 STA 再次发送的“关联请求报文” 后，通过透
明物理设备向待测 STA 发送“关联确认报文” （允许入网），
6. 软件平台模拟 CCO 通过透明物理设备向待测 STA 发送“中央信标”，安排其发送“发现
信标”，同时启动定时器（定时时长 10s），查看是否收到待测 STA 发送的“发现信标”
以确定其已经成功入网；
（1） 若在规定时隙内收到正确的“发现信标” ，则 pass；
（2） 若在规定时隙内收到错误的“发现信标” ，则 fail；
（3） 若在规定时隙未收到“发现信标” ，则 fail；
（4） 其他情况，则 fail。
注：所有需要“选择确认帧” 确认的，当没有收到“选择确认帧”，则 fail。 所有的“发现
列表报文”，“心跳检测报文” 等其他本测试例不关心的报文被收到后，直接丢弃，不做判
断。
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

    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1

    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])
    tb._configure_beacon(None, beacon_dict)

    #how long should we wait

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',15)
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 1
    assert nmm.body.mac_addr_type == 'MAC_ADDR_TYPE_METER_ADDRESS'

    #send associate confirm to DUT, reject and re association time is 10 seconds
    time.sleep(2)
    tb.tb_uart.clear_tb_port_rx_buf()
    dut_tei = 2
    dut_level = 1
    dut_proxy_tei = 1
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf.yaml')
    asso_cnf_dict['body']['level'] = dut_level
    asso_cnf_dict['body']['tei_sta'] = dut_tei
    asso_cnf_dict['body']['tei_proxy'] = dut_proxy_tei
    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    asso_cnf_dict['body']['result'] = 'NML_ASSOCIATION_KO_UNKNOW'
    asso_cnf_dict['body']['retry_times'] = 10*1000

    #config the mac header
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = 1
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = dut_proxy_tei, dst_tei = 0,broadcast_flag = 1)
    ret = tb._wait_for_plc_nmm('MME_ASSOC_REQ',10,lambda:None)
    assert ret is None

    #in the following 10 seconds, we expect another association request
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',10)

    time.sleep(2)
    tb.tb_uart.clear_tb_port_rx_buf()
    #accept
    asso_cnf_dict['body']['retry_times'] = 0
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    asso_cnf_dict['body']['result'] = 'NML_ASSOCIATION_OK'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = dut_proxy_tei, dst_tei = 0,broadcast_flag = 1)



    #simulate CCO2
    beacon_dict = tb._load_data_file('tb_beacon_data_8.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    #beacon_dict['fc']['nid'] += 1
    #tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])
    tb._configure_beacon(None, beacon_dict,True)

    #wait for discover beacon comming from DUT
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10)
    #check parameters inside the proxy beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == dut_level
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == dut_proxy_tei
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == dut_tei



    m.close_port()






