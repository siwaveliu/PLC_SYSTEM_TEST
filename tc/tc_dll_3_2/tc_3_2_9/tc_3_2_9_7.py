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
2. 软件平台模拟电表，在收到待测 STA 的读表号请求后，通过串口向其下发表地址；
3. 软件平台模拟 CCO1 通过透明物理设备向待测设备发送“中央信标”；
4. 软件平台的模拟 CCO1 在收到待测 STA 发送的“关联请求报文” 后，通过透明物理设备
向待测 STA 发送“关联确认报文”（拒绝入网，指定重新关联时间 10s），
5. 同时启动定时器 T1（定时时长 10s），定时器 T2（定时时长 20s），查看定时器 T1 溢出
前是否再次收到“关联请求报文”，以及定时器 T1 溢出后定时器 T2 溢出前是否再次收
到“关联请求报文”；
（1） 定时器 T1 未溢出，收到“关联请求报文” ，则 fail；
（2） 定时器 T1 溢出，定时器 T2 未溢出，收到“关联请求报文”，但报文错误，
则 fail；
（3） 定时器 T1 溢出，定时器 T2 未溢出，收到正确的“关联请求报文”，则 pass；
（4） 定时器 T1 溢出，定时器 T2 溢出，未收到“关联请求报文”，则 fail；
（5） 其他情况，则 fail。
6. 软件平台的模拟 CCO1 在收到待测 STA 再次发送的“关联请求报文” 后，通过透明物理
设备向待测 STA 发送“关联确认报文” （拒绝入网，未指定重新关联时间），
7. 软件平台模拟 CCO2 通过透明物理设备向待测设备发送“中央信标”，同时启动定时器
（定时时长 10s），查看软件平台的模拟 CCO2是否收到待测 STA发出的“关联请求报文”；
（1） 定时器未溢出，收到正确的“关联请求报文”，则 pass；
（2） 定时器未溢出，收到“关联请求报文”，但报文错误，则 fail；
（3） 定时器溢出，未收到“关联请求报文”，则 fail；
（4） 其他情况，则 fail。
注：所有需要“选择确认帧” 确认的，当没有收到“选择确认帧”，则 fail。 所有的“发现
列表报文”，“心跳检测报文” 等其他本测试例不关心的报文被收到后，直接丢弃，不做判
断。
注：测试第 7 点之前发送的关联确认帧中的“结果”字段应使用“不在白名单”、“在黑名
单”，明确告之待测 STA 应向其他网络申请关联请求入网。
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

    cco_mac = '00-00-00-00-00-9C'
    meter_addr = '12-34-56-78-90-12'

    tc_common.sta_init(m, meter_addr)

    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1

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
    #reject again
    asso_cnf_dict['body']['retry_times'] = 0
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = dut_proxy_tei, dst_tei = 0,broadcast_flag = 1)



    #simulate CCO2
    beacon_dict['payload']['value']['association_start'] = 1
    beacon_dict['fc']['nid'] += 1
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])
    tb._configure_beacon(None, beacon_dict,True)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',10)
    assert fc.nid == beacon_dict['fc']['nid']
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 1
    assert nmm.body.mac_addr_type == 'MAC_ADDR_TYPE_METER_ADDRESS'



    m.close_port()






