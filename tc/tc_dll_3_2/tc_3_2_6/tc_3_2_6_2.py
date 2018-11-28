# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 被测 CCO 上电；
2. 软件平台模拟集中器，向待测 CCO 下发“设置主节点地址”命令，在收到“确认”后，向待
测 CCO 下发“添加从节点”命令，将 STA 的 MAC 地址下发到 CCO 中，等待“确认”；
3. 软件平台接收到待测 CCO 发出的“中央信标报文”后，模拟第一个 STA 入网，发送“关联请
求报文”；
4. 软件平台收到待测 CCO 发出的“关联确认报文”和中央信标之后，发送“发现信标报文”。
5. 软件平台发送“发现信标报文”之后，模拟第一个入网的 STA 转发待入网 STA 的入网请求。
6. 软件平台收到待测 CCO 的“关联确认报文” 之后,此时，第一个入网的 STA 已转为 PCO，重
复以上步骤，模拟第二个 PCO 入网。（以上步骤目的为了给待测 CCO 构造两个已入网的 PCO
的情况，默认组网过程正常，不作为检查项目）。
7. 第二个 PCO 入网之后， 软件平台模拟集中器，向待测 CCO 下发“集中器主动抄表”；
8. 软件平台收到待测 CCO 发出的“集中器主动抄表 SOF 帧”后，模拟第一个入网的 PCO，发送
代理广播形式的“STA 抄表响应 SOF1” 报文，并设定 10s 的定时器；
9. 10s 定时器到时之前软件平台会收到待测 CCO 上报的响应内容， 软件平台模拟第二个入网的
PCO，发出 SOF2 帧（是第二个 PCO 对 SOF1 帧的代理广播转发），并设定 10s 的定时器。
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
    sub_nodes_addr = map(lambda x: '00-00-00-00-00-' + str(x).zfill(2), range(2,4))
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #wait for beacon from DTU
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    #sync the nid and sn between tb and DTU
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)
    
    #send 02-10 associate request
    sta_tei_list = []
    req_dict = tb._load_data_file('nml_assoc_req.yaml')
    for addr in sub_nodes_addr:
        req_dict['body']['mac'] = addr
        msdu = plc_packet_helper.build_nmm(req_dict)
        
        #send association request to DUT (mac address is not in the white list)
        tb.mac_head.org_dst_tei = 1
        tb.mac_head.org_src_tei = 0
        tb.mac_head.mac_addr_flag = 1
        tb.mac_head.src_mac_addr = addr
        tb.mac_head.dst_mac_addr = cco_mac

        tb.tb_uart.clear_tb_port_rx_buf()
        tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)
        #time.sleep(0.5)
        
        [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)
        nmm.body.mac_sta in sub_nodes_addr
        
        if nmm.body.tei_sta not in sta_tei_list:
            sta_tei_list.append(nmm.body.tei_sta)
        
        time.sleep(1)
    
    


    plc_tb_ctrl._debug('sta list: {}'.format(sta_tei_list))
    # 模拟集中器AFN13HF1（“监控从节点”命令）启动集中器主动抄表业务，
    # 用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
    gdw1376p2_frame = tb._load_data_file('afn13f1_dl.yaml')
    gdw1376p2_frame['user_data']['value']['comm_module_flag'] = 1 #command to sta
    gdw1376p2_frame['user_data']['value']['a']['src'] = cco_mac
    gdw1376p2_frame['user_data']['value']['a']['dst'] = sub_nodes_addr[0]
    
    #frame = concentrator.build_gdw1376p2_frame(data_file='afn13f1_dl.yaml')
    frame = concentrator.build_gdw1376p2_frame(gdw1376p2_frame)
    #frame = concentrator.build_gdw1376p2_frame(data_file='afn13f1_dl.yaml')
    assert frame is not None
    cct.send_frame(frame)
    
    stop_time = time.time() + tc_common.calc_timeout(10)
    while True:
        result = tb._wait_for_fc_pl_data(tb._check_fc_pl_payload, timeout=1)

        if result is not None:
            [timestamp, fc, data] = result
            if ("PLC_MPDU_BEACON" == fc.mpdu_type):
                curr_beacon = data
            elif ("PLC_MPDU_SOF" == fc.mpdu_type):
                mac_frame = data
                if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_APP":
                    continue

                apm_data = mac_frame.msdu.data
                apm = plc_packet_helper.parse_apm(apm_data, True)
                if apm is None:
                    continue

                if ("APL_CCT_METER_READ" != apm.header.id):
                    plc_tb_ctrl._debug("not APL_CCT_METER_READ packet")
                    continue
                else:
                    break;
        assert time.time() < stop_time, "wait APL_CCT_METER_READ timeout"      
        
        
    #send meter read response packet in broadcast mode
    
    
    # 软件模拟STA+电表, 回复抄表上行报文。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    ul_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_ul.yaml')
    ul_meter_read_pkt['body']['sn'] = apm.body.sn
    msdu = plc_packet_helper.build_apm(dict_content=ul_meter_read_pkt, is_dl=False)

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = sta_tei_list[0]
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_PROXY_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 2
    tb.mac_head.remaining_hop_count = 2
    tb.mac_head.broadcast_dir= 2 #uplink broadcast
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=sta_tei_list[0], dst_tei=1,broadcast_flag = 1)
    
    
    #wait for meter read result coming from DUT(CCO)
    # 监控是否能够在n秒内收到CCO 上报的Q／GDW 1376.2 协议AFN13HF1 应答报文
    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x13, dt1=0x01, dt2=0, timeout=10)
    #监控集中器是否能收到待测CCO 转发的抄表上行报文。
    assert frame1376p2 is not None,           "AFN13H F1 not received"


    #simulate a relay of uplink meter read result to CCO
    #tb.mac_head.org_src_tei = sta_tei_list[1]
    tb.mac_head.remaining_hop_count = 1
    #ensure SN is equal to the former one
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=sta_tei_list[1], dst_tei=1,broadcast_flag = 1,sn = tb.mac_head.msdu_sn)


    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x13, dt1=0x01, dt2=0, timeout=10,tm_assert= False)
    #监控集中器是否能收到待测CCO 转发的抄表上行报文。
    assert frame1376p2 is None,           "AFN13H F1 should not be received"


    cct.close_port()
