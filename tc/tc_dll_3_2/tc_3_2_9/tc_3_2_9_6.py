# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，上电初始化；
2. 软件平台模拟集中器，通过串口向待测 CCO 下发“设置主节点地址”命令，在收到“确认”
后，向待测 CCO 下发“添加从节点”命令，将目标网络站点的 MAC 地址下发到 CCO 中，等待
“确认”；
1.软件平台模拟不在白名单中的未入网 STA 通过透明物理设备向待测 CCO 发送“关联请求报
文” ，查看是否收到相应的“选择确认帧” ；
（1） 未收到对应的“选择确认帧”，则 fail；
（2） 收到对应的“选择确认帧”，则 pass。
2.同时启动定时器（定时时长 10s）， 软件平台查看定时器溢出前是否收到“关联确认报文”
（结果字段为站点不在白名单中）；
（1） 定时器未溢出，收到正确的“关联确认报文” ，结果为拒绝，原因为不在白名单内，
则 pass；
（2） 定时器未溢出，收到正确的“关联确认报文”，结果为拒绝，但原因错误，则 fail；
（3） 定时器未溢出，收到正确的“关联确认报文”，但结果为成功，则 fail；
（4） 定时器未溢出，收到“关联确认报文”，但报文错误，则 fail；
（5） 定时器溢出，未收到关联确认报文，则 fail；
（6） 其他情况，则 fail。
3.软件平台模拟在白名单中的未入网 STA 通过透明物理设备向待测 CCO 发送“关联请求报
文” ， 查看是否收到相应的“选择确认帧” ；
（1） 未收到对应的“选择确认帧”，则 fail；
（2） 收到对应的“选择确认帧”，则 pass。
4.同时启动定时器（定时时长 10s），查看定时器溢出前是否收到“关联确认报文”（结果字
段为成功）；
（1） 定时器未溢出，收到正确的“关联确认报文”，结果为成功，则 pass；
（2） 定时器未溢出，收到正确的“关联确认报文”，结果为拒绝，则 fail；
（3） 定时器未溢出，收到“关联确认报文”，但报文错误，则 fail；
（4） 定时器溢出，未收到“关联确认报文”，则 fail；
（5） 其他情况，则 fail。
注：所有需要“选择确认帧” 确认的，当没有收到“选择确认帧”，则 fail。 所有的“发现列表
报文”，“心跳检测报文” 等其他本测试例不关心的报文被收到后，直接丢弃，不做判断。
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

    tc_common.set_cco_mac_addr(cct,'00-00-00-00-00-9C')


    #set sub node address
    sub_nodes_addr = ['00-00-00-00-00-01']
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #wait for beacon from DTU
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    #sync the nid and sn between tb and DTU
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)

#     tb._configure_proxy('tb_time_config_req.yaml')
#     tb._configure_nw_static_para(beacon_fc.nid, beacon_payload.nw_sn)

    req_dict = tb._load_data_file('nml_assoc_req.yaml')

    assert req_dict is not None
    #send association request to DTU

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = sub_nodes_addr[0]
    tb.mac_head.dst_mac_addr = '00-00-00-00-00-9C'
    
    req_dict['body']['mac'] = sub_nodes_addr[0]

    msdu = plc_packet_helper.build_nmm(req_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)


    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)


    cnf = nmm.body
    assert cnf.mac_sta == sub_nodes_addr[0]
    assert cnf.result == 'NML_ASSOCIATION_OK' or cnf.result =='NML_ASSOCIATION_KO_RETRY_OK'
    assert cnf.tei_proxy == 1
    
    time.sleep(2)
    
    tb.tb_uart.clear_tb_port_rx_buf()
    
    #associate request coming from a node which is not in white list
    req_dict['body']['mac'] = '00-00-00-00-00-02'
    msdu = plc_packet_helper.build_nmm(req_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)


    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)


    cnf = nmm.body
    assert cnf.mac_sta == '00-00-00-00-00-02'
    assert cnf.result == 'NML_ASSOCIATION_KO_NOT_IN_WL'
  


    cct.close_port()






