# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter

'''
1.连接设备，上电初始化；
2.软件平台模拟入网的 PCO1 通过透明物理设备向待测 STA 设备发送“代理信标”
3.查看被测 STA-2 设备发送“关联请求报文” ，查看是否收到相应的“选择确认报文” ；
（1） 未收到对应的“选择确认帧”，则 fail；
（2） 收到对应的“选择确认帧”，则 pass。
4.软件平台模拟 PCO1 转发的关联确认包给 STA-2。
（1） 未收到对应的“选择确认帧”，则 fail；
（2） 收到对应的“选择确认帧”，则 pass。
5.软件平台收到待测 CCO 发送的“中央信标”后，查看是否对已入网 STA 进行了发现信标
时隙的规划；
(1)进行了发现信标时隙规划， 则 pass；
(2)没有进行了发现信标时隙规划，则 fail。
6.软件平台模拟已入网 STA 在 CSMA 时隙内通过透明物理设备转发未入网 STA 的 “关联请
求报文”，查看是否收到相应的“选择确认报文” ；
(1)未收到对应的“选择确认帧”，则 fail；
(2)收到对应的“选择确认帧”，则 pass。
7.软件平台模拟 PCO1 转发的来自 CCO 的下行“抄表报文”，同时启动定时器（定时时长 10s）。
（1） 在规定的 CSMA 时隙内收到正确的上行“抄表报文”（考察代理主路径标识、
路由总跳数、路由剩余跳数、原始源 MAC 地址、原始目的 MAC 地址是否正确）， 则 pass；
（2） 在规定的 CSMA 时隙收到上行“抄表报文”，但报文错误，则 fail；
（3） 定时器溢出，未收到下行“抄表报文”，则 fail；
（4） 其他情况，则 fail
8. 软件平台模拟 PCO1 转发的来自 CCO 的下行、全网广播“广播校时”，同时启动定时器
（定时时长 10s）。
（1） 在定时器时间内收到正确的被测设备发出的转发“广播校时”， 则 pass；
（2） 其他情况，则 fail。
9. 软件平台模拟 PCO1 发送的下行、代理广播“广播校时”，同时启动定时器（定时时长
10s）。
（1） 在定时器过期后未内收到被测设备发出的转发“广播校时”， 则 pass；
（2） 其他情况，则 fail。
10. 软件平台模拟 PCO1 发送的下行、本地广播“广播校时”，同时启动定时器（定时时长
10s）。
（1） 在定时器时间内未收到被测设备发出的转发“广播校时”， 则 pass；
（2） 其他情况，则 fail。
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

    #tc_common.send_dlt645_reply_frame(m,meter_addr,dis,reply_data,len(reply_data))

    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data_2.yaml')
    beacon_dict['num'] = 65535
    beacon_dict['payload']['value']['association_start'] = 1

    tb._configure_beacon(None, beacon_dict)

    #config nid and nw_sn for sending of mpdu
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_REQ'],15)


    #send associate confirm to STA
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_2.yaml')
    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn

    #config the mac header
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = 2
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 2, dst_tei = 0,broadcast_flag = 1)


    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data_2_2.yaml')
    beacon_dict['num'] = 65535
    beacon_dict['payload']['value']['association_start'] = 1

    tb._configure_beacon(None, beacon_dict,True)



    #wait for discover beacon comming from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the proxy beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 2
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 2
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 3


    # 软件模拟PCO, 发送集中器主动抄表下行报文，单播。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')
    #ul_meter_read_pkt['body']['sn'] = apm.body.sn

    dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))

    plc_tb_ctrl._debug(dl_meter_read_pkt)

    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)

    tb.mac_head.org_dst_tei = 3  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei = 1
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_UNICAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 2
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.broadcast_dir= 1 #downlink broadcast



#     msdu_structure = plc_packet_helper.parse_apm(msdu, True)
#     #
#
#     msdu_structure.body.data[-2] = meter.calc_dlt645_cs8(msdu_structure.body.data)
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=2, dst_tei=3,broadcast_flag = 0)


    #wait for meter read request sent from DUT to meter
    #wait for meter read request
    dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 10)

    #plc_tb_ctrl._debug(dlt645_frame)
    assert dlt645_frame.head.len == 4
    0 == cmp(dlt645_frame,dl_meter_read_pkt['body']['data'])



    #模拟电表发送645应答报文给DUT
    meter_read_rsp = tb._load_data_file(data_file="meter_read_rsp_2.yaml")
    meter_read_rsp['head']['addr'] = meter_addr

    meter_read_rsp['body']['value']['DI0'] = dlt645_frame.body.value.DI0
    meter_read_rsp['body']['value']['DI1'] = dlt645_frame.body.value.DI1
    meter_read_rsp['body']['value']['DI2'] = dlt645_frame.body.value.DI2
    meter_read_rsp['body']['value']['DI3'] = dlt645_frame.body.value.DI3
    dlt645_frame_rsp = meter.build_dlt645_07_frame(dict_content = meter_read_rsp)

#     dlt645_frame_rsp.body.value.DI0 = dlt645_frame.body.value.DI0
#     dlt645_frame_rsp.body.value.DI1 = dlt645_frame.body.value.DI1
#     dlt645_frame_rsp.body.value.DI2 = dlt645_frame.body.value.DI2
#     dlt645_frame_rsp.body.value.DI3 = dlt645_frame.body.value.DI3
    m.send_frame(dlt645_frame_rsp)


    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_ul('APL_CCT_METER_READ',10)
    time.sleep(1)



    # 软件模拟PCO, 发送广播校时，全网广播。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    tb.tb_uart.clear_tb_port_rx_buf()
    time_cali = tb._load_data_file(data_file='apl_time_cali_dl.yaml')
    plc_tb_ctrl._debug(time_cali)

    msdu = plc_packet_helper.build_apm(dict_content=time_cali, is_dl=True)

    tb.mac_head.org_dst_tei = 0xFFF  #DUT tei is 3, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei = 1
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_ENTIRE_NW_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 15
    tb.mac_head.remaining_hop_count = 14
    tb.mac_head.broadcast_dir= 1 #downlink broadcast
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=2, dst_tei=0xFFF,broadcast_flag = 1,auto_retrans=False)


    #wait for relayed message
    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_TIME_CALI',10)
    time.sleep(1)



    # 软件模拟PCO, 发送广播校时，代理广播。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    tb.tb_uart.clear_tb_port_rx_buf()
    time_cali = tb._load_data_file(data_file='apl_time_cali_dl.yaml')
    plc_tb_ctrl._debug(time_cali)

    msdu = plc_packet_helper.build_apm(dict_content=time_cali, is_dl=True)

    tb.mac_head.org_dst_tei = 0xFFF  #DUT tei is 3, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei = 1
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_PROXY_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 15
    tb.mac_head.remaining_hop_count = 14
    tb.mac_head.broadcast_dir= 1 #downlink broadcast
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=2, dst_tei=0xFFF,broadcast_flag = 1,auto_retrans=False)


    #wait for relayed message
    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_TIME_CALI',10,lambda:{None})
    assert apm is None
    time.sleep(1)



    # 软件模拟PCO, 发送广播校时，本地广播。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    tb.tb_uart.clear_tb_port_rx_buf()
    time_cali = tb._load_data_file(data_file='apl_time_cali_dl.yaml')
    plc_tb_ctrl._debug(time_cali)

    msdu = plc_packet_helper.build_apm(dict_content=time_cali, is_dl=True)

    tb.mac_head.org_dst_tei = 0xFFF  #DUT tei is 3, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei = 1
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 1
    tb.mac_head.remaining_hop_count = 1
    tb.mac_head.broadcast_dir= 1 #downlink broadcast
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=2, dst_tei=0xFFF,broadcast_flag = 1,auto_retrans=False)


    #wait for relayed message
    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_TIME_CALI',10,lambda:{None})
    assert apm is None
    time.sleep(1)

    m.close_port()


