# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，上电初始化；
2. 软件平台模拟集中器通过串口向待测 CCO 下发“设置主节点地址”命令，在收到“确认”后，
向待测 CCO 下发“添加从节点”命令，将目标网络站点的 MAC 地址下发到 CCO 中，等待“确认”；
3. 软件平台收到待测 CCO 发送的“网间协调帧”后，向待测 CCO 发送 NID 冲突的“网间协调帧”，
同时启动定时器（定时时长 10s），查看定时器溢出前是否收到待测 CCO 发出的“网间协调帧”
并且 NID 已经正确协调；
（1） 定时器未溢出，收到了正确的“网间协调帧”，且 NID 已正确协调，则 pass；
（2） 定时器溢出，收到过“网间协调帧”，但 NID 未正确协调，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”，则 fail；
（4） 其他情况，则 fail。
4. 平台发送关联请求,组网完成后,软件平台模拟 STA 通过透明物理设备向待测 CCO 发送多轮“网
络冲突上报报文”（邻居网络 CCO 的 MAC 地址较大），同时启动定时器（定时时长 10s），查看
定时器溢出前是否收到待测 CCO 发出的“网间协调帧”并且 NID 已经正确协调。
（1） 定时器未溢出，收到了正确的“网间协调帧”，且 NID 已正确协调，则 pass；
（2） 定时器溢出，收到过“网间协调帧”，但 NID 未正确协调，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”， 则 fail；
（4） 其他情况，则 fail。
5. 平台在上一步 NID 变更后,以新的 NID 重新发起关联请求,组网完成后.软件平台模拟 STA 通过
透明物理设备向待测 CCO 发送多轮“网络冲突上报报文”（邻居网络 CCO 的 MAC 地址较小），同
时启动 30 分钟定时器，查看定时器溢出前是否收到待测 CCO 发出的“网间协调帧”并且 NID
仍然保持不变；
（1） 定时器未溢出，收到的所有的“网间协调帧”，其 NID 保持不变，则 pass；
（2） 定时器溢出，收到过一个“网间协调帧”的 NID 发生改变，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”，则 fail；
（4） 其他情况，则 fail。
6. 定时器溢出后，启动一个新的定时器（定时时长 2s），查看定时器溢出前是否收到待测 CCO 发
出的“网间协调帧”并且 NID 已经正确协调。
（1） 定时器未溢出，收到了正确的“网间协调帧”，且 NID 已正确协调，则 pass；
（2） 定时器溢出，收到过“网间协调帧”，但 NID 未正确协调，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”，则 fail；
（4） 其他情况，则 fail。
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
    sub_nodes_addr = map(lambda x: '00-00-00-00-00-' + str(x).zfill(2), range(2,3))
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #wait for beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)


    #sync the nid and sn between tb and DTU
    tb._configure_proxy('tb_time_config_req.yaml')
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)
    
    
    #wait for the first NCF
    [timestamp, fc] = tb._wait_for_plc_ncf(30)
    
    
    #simulate another network and send NCF to DUT
    #phase indicates on which phase tb should send this NCF
    #nid confliction
    neighbor_nid = beacon_fc.nid 
    #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
    tb._send_ncf(neighbor_nid,1,1000,0,0)     
    
    
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):
        [timestamp, fc] = tb._wait_for_plc_ncf(10)
        if fc.nid != neighbor_nid:
            break;
    else:
        assert 0, "no valid NCF is received"
        
        
    #wait for new beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)
    #resynch the nid and sn        
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
            
        
       
    time.sleep(2)
    old_nid = fc.nid
    
    
    #it's time to send network conflict packet with a bigger cco mac address
    nw_conflict = tb._load_data_file('nml_nw_conflict_report.yaml')
    nw_conflict['body']['cco_mac'] = '00-00-00-00-00-9D'
    nw_conflict['body']['nids'][0] = old_nid
        
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):

        
        msdu = plc_packet_helper.build_nmm(nw_conflict)
        #send association request to DUT (mac address is not in the white list)
        tb.mac_head.org_dst_tei = 1
        tb.mac_head.org_src_tei = sta_tei_list[0]
        tb.mac_head.mac_addr_flag = 0
        tb.mac_head.src_mac_addr = addr
        tb.mac_head.dst_mac_addr = cco_mac
    
        tb.tb_uart.clear_tb_port_rx_buf()
        
        tb._send_msdu(msdu, tb.mac_head, src_tei = sta_tei_list[0], dst_tei = 1)
        
        [timestamp, fc] = tb._wait_for_plc_ncf(10)
        if fc.nid != old_nid:
            break;
    
    else:
        assert 0,"nid did not changed after network conflict packet received"
    
   
    #wait for new beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)
    #resynch the nid and sn        
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)  
    
    
    
    #reassociate
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

        #tb.tb_uart.clear_tb_port_rx_buf()
        
        tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)
        #time.sleep(0.5)
        
        [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)
        nmm.body.mac_sta in sub_nodes_addr
        
        if nmm.body.tei_sta not in sta_tei_list:
            sta_tei_list.append(nmm.body.tei_sta)
    

    #it's time to send network conflict packet with a bigger cco mac address
    nw_conflict = tb._load_data_file('nml_nw_conflict_report.yaml')
    nw_conflict['body']['cco_mac'] = '00-00-00-00-00-9B'
    nw_conflict['body']['nids'][0] = beacon_fc.nid
    msdu = plc_packet_helper.build_nmm(nw_conflict)
        
        
    #wait for network establishing to be acomplished 
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)
    while beacon_payload.network_org_flag != 1:
        [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)      
    
    
    #last 30 minutes
    tb.tb_uart.clear_tb_port_rx_buf()
    stop_time = time.time() + tc_common.calc_timeout(60)
    conflict_num = 0
    received_ncf_num = 0
    while(time.time()< stop_time):

        
        
        #send nw conflict to DUT (cco mac address is smaller)
        tb.mac_head.org_dst_tei = 1
        tb.mac_head.org_src_tei = sta_tei_list[0]
        tb.mac_head.mac_addr_flag = 0
        tb.mac_head.src_mac_addr = addr
        tb.mac_head.dst_mac_addr = cco_mac
    

        
        tb._send_msdu(msdu, tb.mac_head, src_tei = sta_tei_list[0], dst_tei = 1)
        conflict_num += 1
        plc_tb_ctrl._debug('conflict packet sent:{}'.format(conflict_num))
        
        ret = tb._wait_for_plc_ncf(0.5, lambda:None)
        while ret is not None:
            [timestamp, fc]  = ret
            received_ncf_num += 1
            if fc.nid != beacon_fc.nid:
               assert 0,"nid changed after network conflict packet received"
            else:
               break
           
            ret = tb._wait_for_plc_ncf(0.5,lambda:None)
            
        #time.sleep(2)
        
    assert received_ncf_num > 0
    
    #tb.tb_uart.clear_tb_port_rx_buf()
    stop_time = time.time() + tc_common.calc_timeout(2)
    nid_changed = 0
    
    while(time.time()< stop_time and nid_changed == 0):
        #send nw conflict to DUT (cco mac address is smaller)
        tb.mac_head.org_dst_tei = 1
        tb.mac_head.org_src_tei = sta_tei_list[0]
        tb.mac_head.mac_addr_flag = 0
        tb.mac_head.src_mac_addr = addr
        tb.mac_head.dst_mac_addr = cco_mac
    

        
        tb._send_msdu(msdu, tb.mac_head, src_tei = sta_tei_list[0], dst_tei = 1)
        conflict_num += 1
        plc_tb_ctrl._debug('conflict packet sent2:{}'.format(conflict_num))
        
        ret = tb._wait_for_plc_ncf(0.5, lambda:None)
        while ret is not None:
            [timestamp, fc]  = ret
            if fc.nid != beacon_fc.nid:
               nid_changed = 1
               break;
            ret = tb._wait_for_plc_ncf(0.5, lambda:None)   
    


    assert nid_changed == 1 ,"nid should change in the last 2 seconds"
            
    cct.close_port()
