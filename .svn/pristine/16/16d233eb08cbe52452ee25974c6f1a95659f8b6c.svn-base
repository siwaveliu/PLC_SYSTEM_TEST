# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，上电初始化；
2. 软件平台模拟集中器，通过串口向待测 CCO-b 下发【设置主节点地址】命令，在收到【确认】
后，再通过串口向待测 CCO-b 下发【添加从节点】命令，将目标网络站点的 MAC 地址下发到 CCO-b
中，等待【确认】；
3. 待测 CCO-b 周期的发送【中央信标帧】， 软件平台模拟 CCO-a 接收 CCO-b 的【中央信标帧】， 软
件平台分别记录收到的第 1 帧和第 2 帧【中央信标帧】信标时间戳 T1、 T2，计算待测 CCO-b【中
央信标帧】周期△T=T2-T1；
4. 软件平台接收到 CCO-b 的第 n 包【中央信标帧】后(n>2)，记录信标时间戳 Tn， 软件平台设置
第 n+1 包【中央信标帧】的预期接收时间 Tnext= Tn+△T，同时软件平台发送该网络的【中央
信标帧】，且信标周期起始时间 Ta=T1;
5. 软件平台接收到 CCO-b 的第 n+1 包【中央信标帧】后,记录信标时间戳 T(n+1)，对比 T(n+1)与
预期接收时间 Tnext；
6. 若 T(n+1) =Tnext，则待测 CC0-b 收到其他网络 CCO 的中央信标后，并未调整自身的 NTB，反
之待测 CC0-b 调整了自身的 NTB；
7. 软件平台模拟未入网 STA 通过透明物理设备向待测 CCO-b 发送【关联请求报文】，查看是否收
到相应的【选择确认报文】以及【关联确认报文】；
8. 若 STA 收到【关联确认报文】，则 STA 入网成功；
9. 待测 CCO-b 周期的发送【中央信标帧】，若【中央信标帧】对新入网的 STA 规划了发现信标时
隙， 软件平台模拟入网 STA 接收 CCO-b 的【中央信标帧】， 软件平台分别记录收到的第 1 帧和
第 2 帧【中央信标帧】信标时间戳 T1、 T2，计算待测 CCO-b【中央信标帧】周期△T=T2-T1；
10.软件平台接收到 CCO-b 的第 n 包【中央信标帧】后(n>2)，记录信标时间戳 Tn， 软件平台设置
第 n+1 包【中央信标帧】的预期接收时间 Tnext= Tn+△T，同时软件平台发送【发现信标帧】，
且信标周期起始时间 Ta=T1;
11.软件平台接收到 CCO-b 的第 n+1 包【中央信标帧】后(n>2)，记录信标时间戳 T（n+1），对比
T(n+1)与预期接收时间 Tnext；
12.若 T(n+1) =Tnext，则待测 CC0-b 收到发现信标后，并未调整自身的 NTB，反之待测 CC0-b 调
整了自身的 NTB。
13.软件平台模拟已入网 STA 在 CSMA 时隙内通过透明物理设备转发未入网 STA 的【关联请求报文】，
查看是否收到相应的【选择确认报文】以及【关联确认报文】；
14.若已入网 STA 收到 CCO-b 发往请求入网的 STA-2 的【关联确认报文】，则 STA-2 入网成功；
15.待测 CCO-b 周期的发送【中央信标帧】，若【中央信标帧】中对 PCO 进行了代理信标时隙的规
划， 软件平台模拟 PCO 接收 CCO-b 的【中央信标帧】， 软件平台分别记录收到的第 1 帧和第 2
帧【中央信标帧】信标时间戳 T1、 T2，计算待测 CCO-b【中央信标帧】周期△T=T2-T1；
16.软件平台接收到 CCO-b 的第 n 包【中央信标帧】后(n>2)，记录信标时间戳 Tn， 软件平台设置
第 n+1 包【中央信标帧】的预期接收时间 Tnext= Tn+△T，同时软件平台发送【代理信标帧】，
且信标周期起始时间 Ta=T1;
17.软件平台接收到 CCO-b 的第 n+1 包【中央信标帧】后(n>2)，记录信标时间戳 T（n+1），对比
T(n+1)与预期接收时间 Tnext；
18.若 T(n+1) =Tnext，则待测 CC0-b 收到代理信标后，并未调整自身的 NTB，反之待测 CC0-b 调
整了自身的 NTB。
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
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)


    #sync the nid and sn between tb and DTU
    tb._configure_proxy('tb_time_config_req.yaml')
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)
    
    
    #wait for beacon from DTU and get delta of beacon send time
    beacon_timestamps = []
    #beacon_timestamp_2 = None
    
    while (len(beacon_timestamps) < 2):
        [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10)
        if beacon_fc.var_region_ver.phase == 1:
            beacon_timestamps.append(timestamp)
            plc_tb_ctrl._debug('beacon with pahse 1 received:{}'.format(timestamp))
            
    
    delta_beacon_sending_time = plc_packet_helper.ntb_diff(beacon_timestamps[0],
                                                           beacon_timestamps[1])
    


    time.sleep(3)
    tb.tb_uart.clear_tb_port_rx_buf()
    
#     
#     beacon_timestamp_n = None
#     #try to receive Nth beacon
#     while beacon_timestamp_n is None:
#         [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10)
#         if beacon_fc.var_region_ver.phase == 1:
#             beacon_timestamp_n = timestamp
#             plc_tb_ctrl._debug('beacon with pahse 1 received:{}'.format(timestamp))
    
         
    while (len(beacon_timestamps) < 4):
        [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10)
        if beacon_fc.var_region_ver.phase == 1:
            beacon_timestamps.append(timestamp)
            plc_tb_ctrl._debug('beacon N with pahse 1 received:{}'.format(timestamp))
        if len(beacon_timestamps) == 3:
            #simulate central beacon coming from another network
            beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
            beacon_dict['num'] = 65535
            beacon_dict['payload']['value']['association_start'] = 1
            tb._configure_beacon(None, beacon_dict)
            
        
        
    delta_beacon_sending_time2 = plc_packet_helper.ntb_diff(beacon_timestamps[2],
                                                           beacon_timestamps[3])
    
    if delta_beacon_sending_time2 > delta_beacon_sending_time:
        difference =  delta_beacon_sending_time2-delta_beacon_sending_time
    else:
        difference =  delta_beacon_sending_time - delta_beacon_sending_time2
        
        
    plc_tb_ctrl._debug("difference is:{}".format(difference))        
    assert difference < plc_packet_helper.us_to_ntb(1000),"difference is too large:{}".format(difference)
            
    #stop beacon sending
    beacon_dict['num'] = 0
    tb._configure_beacon(None, beacon_dict)
    
    
    #send 02-10 associate request
    sta_tei_list = []
    req_dict = tb._load_data_file('nml_assoc_req.yaml')
    for addr in sub_nodes_addr:
        req_dict['body']['mac'] = addr
        
        if '03' in addr:
          req_dict['body']['proxy_tei'][0] = 2
        msdu = plc_packet_helper.build_nmm(req_dict)
        
        #send association request to DUT (mac address is not in the white list)
        tb.mac_head.org_dst_tei = 1
        tb.mac_head.org_src_tei = 0
        tb.mac_head.mac_addr_flag = 1
        tb.mac_head.src_mac_addr = addr
        tb.mac_head.dst_mac_addr = cco_mac

        tb.tb_uart.clear_tb_port_rx_buf()
        
        if '03' in addr:
            tb._send_msdu(msdu, tb.mac_head, src_tei = 2, dst_tei = 1)
        else:
            tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)
        #time.sleep(0.5)
        
        [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)
        nmm.body.mac_sta in sub_nodes_addr
        
        if nmm.body.tei_sta not in sta_tei_list:
            sta_tei_list.append(nmm.body.tei_sta)
            
        beacon_timestamps[:] = []
        while (len(beacon_timestamps) < 2):
             [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10)
             
             if beacon_fc.var_region_ver.phase == 1:
                beacon_timestamps.append(timestamp)
                beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
                plc_tb_ctrl._debug("ncb info:{}".format(beacon_slot_alloc.ncb_info))
            
    
        delta_beacon_sending_time = plc_packet_helper.ntb_diff(beacon_timestamps[0],
                                                           beacon_timestamps[1])
    

#         beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
#         plc_tb_ctrl._debug("ncb info:{}".format(beacon_slot_alloc.ncb_info))
        time.sleep(3)
        tb.tb_uart.clear_tb_port_rx_buf()   
        
        beacon_dict['num'] = 10
        tb._configure_beacon(None, beacon_dict)
        
        
        while (len(beacon_timestamps) < 4):
            [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(10)
            if beacon_fc.var_region_ver.phase == 1:
                beacon_timestamps.append(timestamp)
        
        
        delta_beacon_sending_time2 = plc_packet_helper.ntb_diff(beacon_timestamps[2],
                                                               beacon_timestamps[3])
        
        if delta_beacon_sending_time2 > delta_beacon_sending_time:
            difference =  delta_beacon_sending_time2-delta_beacon_sending_time
        else:
            difference =  delta_beacon_sending_time - delta_beacon_sending_time2
            
        assert difference < plc_packet_helper.us_to_ntb(1000),"difference is too large:{}".format(difference)
        
        beacon_dict['num'] = 0
        tb._configure_beacon(None, beacon_dict)
    
        
    
        
        time.sleep(2)
        

    
    
    cct.close_port()
