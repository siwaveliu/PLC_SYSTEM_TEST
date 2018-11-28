# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，上电初始化；
2. 软件平台模拟集中器，通过串口向待测 CCO 下发“设置主节点地址”命令，在收到“确
认”后，向待测 CCO 下发“添加从节点”命令，将目标网络站点的 MAC 地址下发到 CCO
中，等待“确认”；
3. 软件平台收到待测 CCO 发送的“网间协调帧”后，向待测 CCO 周期发送（周期时长 0.5s）
发送带宽冲突的“网间协调帧”（不携带待测 CCO 的 NID），同时启动定时器（定时时长
10s），多轮交互，查看定时器溢出前是否收到待测 CCO 发出的“网间协调帧”并且已
做出退避；
（1） 定时器未溢出，收到了正确的“网间协调帧”，且已做出退避，则 pass；
（2） 定时器溢出，收到过“网间协调帧”，但未做出退避，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”，则 fail；
（4） 其他情况，则 fail。
4. 软件平台收到待测 CCO 发送的“网间协调帧”后，通过透明物理设备向待测 CCO 周期
发送（周期时长 0.5s） 带宽冲突的“网间协调帧”（携带待测 CCO 的 NID && 模拟 CCO
的带宽先结束），同时启动定时器（定时时长 10s），多轮交互，查看定时器溢出前是否
收到待测 CCO 发出的“网间协调帧”并且已做出退避；
（1） 定时器未溢出，收到了正确的“网间协调帧”，且已做出退避，则 pass；
（2） 定时器溢出，收到过“网间协调帧”，但未做出退避，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”，则 fail；
（4） 其他情况，则 fail。
5. 软件平台收到待测 CCO 发送的“网间协调帧”后，通过透明物理设备向待测 CCO 周期
发送（周期时长 0.5s） 带宽冲突的“网间协调帧”（携带待测 CCO 的 NID && 模拟 CCO
的带宽后结束），同时启动定时器（定时时长 10s），查看定时器溢出前是否收到待测
CCO 发出的“网间协调帧”并且未做出退避；
（1） 定时器未溢出，收到的所有正确的“网间协调帧”，且未做出退避，则 pass；
（2） 定时器溢出，收到过一个“网间协调帧”进行了退避操作，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”，则 fail；
（4） 其他情况，则 fail。
6. 软件平台收到待测 CCO 发送的“网间协调帧”后，通过透明物理设备向待测 CCO 周期
发送（周期时长 0.5s） 带宽冲突的“网间协调帧”（携带待测 CCO 的 NID && 模拟 CCO
的带宽和待测 CCO 的带宽同时结束 && 模拟 CCO 的 NID 较小），同时启动定时器（定时
时长 10s），多轮交互，查看定时器溢出前是否收到待测 CCO 发出的“网间协调帧”并
且已做出退避；
（1） 定时器未溢出，收到了正确的“网间协调帧”，且已做出退避，则 pass；
（2） 定时器溢出，收到过“网间协调帧”，但未做出退避，则 fail；
（3） 定时器溢出，未收到任何“网间协调帧”，则 fail；
（4） 其他情况，则 fail。
7. 软件平台收到待测 CCO 发送的“网间协调帧”后，向待测 CCO 周期发送（周期时长 0.5s）
带宽冲突的“网间协调帧”（携带待测 CCO 的 NID && 模拟 CCO 的带宽和待测 CCO 的带
宽同时结束 && 模拟 CCO 的 NID 较大），同时启动定时器（定时时长 10s），查看定时器
溢出前是否收到待测 CCO 发出的“网间协调帧”并且未做出退避；
（1） 定时器未溢出，收到的所有正确的“网间协调帧”，且未做出退避，则 pass；
（2） 定时器溢出，收到过一个“网间协调帧”进行了退避操作，则 fail；
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
    
    get_tb_time_delta_ms = 100


    #wait for beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)


    #sync the nid and sn between tb and DTU
    tb._configure_proxy('tb_time_config_req.yaml')
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)
    
    
    
    #wait for the first NCF
    [timestamp, fc] = tb._wait_for_plc_ncf(30)
    
    
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)
    
    
    #get beacon start time and tb current time to calculate the distance to the next beacon
    #boundary
    beacon_start_time = plc_packet_helper.get_beacon_period_start_time(beacon_payload)
    slot_configurations = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)

    
    #simulate another network and send NCF to DUT
    #phase indicates on which phase tb should send this NCF
    #bandwidth confliction
    neighbor_nid = beacon_fc.nid + 1 
    #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
#     tb._send_ncf(neighbor_nid,1,1000,bandwidth_offset,0)     

    
    
  
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):
        #send simulated ncf
        
        
        cur_tb_time = tb._read_tb_time()
        
        presumed_ncf_sent_time = cur_tb_time + plc_packet_helper.ms_to_ntb(get_tb_time_delta_ms)
        #which phase we are in currently, we need find phase A (1) CSMA slot 
        while not plc_packet_helper.check_sof_time(presumed_ncf_sent_time, 
                                         presumed_ncf_sent_time + plc_packet_helper.ms_to_ntb(5), 
                                         1, 
                                         beacon_payload):
            #step is CSMA slot slice length
            presumed_ncf_sent_time += plc_packet_helper.ms_to_ntb(5)#slot_configurations.csma_slot_slice_len*10)
    

        
        
        #reserve 50ms margin 
        #plc_packet_helper.ntb_add(beacon_start_time, plc_packet_helper.ms_to_ntb(-50))
        
        #get the next beacon start boundary
        while plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time) < 0:
            beacon_start_time += plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
            
        bandwidth_offset = plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time)
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        plc_tb_ctrl._debug('beacon start time:{} ncf sent time:{} cur time:{}'.format(beacon_start_time,
                                                                        presumed_ncf_sent_time,
                                                                        tb._read_tb_time()))
        

        
        #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
        tb._send_ncf(neighbor_nid,1,1000,plc_packet_helper.ntb_to_ms(bandwidth_offset),0)    
        
        
        
        [timestamp, fc] = tb._wait_for_plc_ncf(2)
        
        plc_tb_ctrl._debug('duration:{}'.format(fc.var_region_ver.duration))
        timestamp += plc_packet_helper.ms_to_ntb(fc.var_region_ver.offset)
        
        ntb_diff = plc_packet_helper.ntb_diff(beacon_start_time,timestamp)
        
        plc_tb_ctrl._debug('duration:{} offset:{} diff:{}'.format(fc.var_region_ver.duration,
                                                                  fc.var_region_ver.offset,
                                                                  ntb_diff))
        if plc_packet_helper.ntb_inside_range(ntb_diff, 
                                              plc_packet_helper.ms_to_ntb(-10), 
                                              plc_packet_helper.ms_to_ntb(10)):
            continue
        else:
            break
        

        
        #whether the DUT has adjusted it's beacon start time
    else:
        assert 0, "no renegotiation happens"
        
        
    time.sleep(2)
    tb.tb_uart.clear_tb_port_rx_buf()
    #wait for new beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)
    #beacon_fc.var_region_ver.phase == 1
    #resynch the nid and sn   
    tb._configure_proxy('tb_time_config_req.yaml')     
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)  
    
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)
    
    beacon_start_time = plc_packet_helper.get_beacon_period_start_time(beacon_payload)     
    
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):
        cur_tb_time = tb._read_tb_time()
        
        presumed_ncf_sent_time = cur_tb_time + plc_packet_helper.ms_to_ntb(get_tb_time_delta_ms)
        #which phase we are in currently, we need find phase A (1) CSMA slot 
        while not plc_packet_helper.check_sof_time(presumed_ncf_sent_time, 
                                         presumed_ncf_sent_time + plc_packet_helper.ms_to_ntb(5), 
                                         1, 
                                         beacon_payload):
            #step is CSMA slot slice length
            presumed_ncf_sent_time += plc_packet_helper.ms_to_ntb(5)#slot_configurations.csma_slot_slice_len*10)
    

        
        
        #reserve 50ms margin 
        #plc_packet_helper.ntb_add(beacon_start_time, plc_packet_helper.ms_to_ntb(-50))
        
        #get the next beacon start boundary
        while plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time) < 0:
            beacon_start_time += plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
            
        bandwidth_offset = plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time)
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        plc_tb_ctrl._debug('beacon start time:{} ncf sent time:{} cur time:{}'.format(beacon_start_time,
                                                                        presumed_ncf_sent_time,
                                                                        tb._read_tb_time()))
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
        #neighbor network can see DUT's network and neighbor network bandwidth end firstly
        tb._send_ncf(neighbor_nid,1,40,plc_packet_helper.ntb_to_ms(bandwidth_offset),beacon_fc.nid)    
        
        
        
        [timestamp, fc] = tb._wait_for_plc_ncf(2)
        
        plc_tb_ctrl._debug('duration:{}'.format(fc.var_region_ver.duration))
        timestamp += plc_packet_helper.ms_to_ntb(fc.var_region_ver.offset)
        
        ntb_diff = plc_packet_helper.ntb_diff(beacon_start_time,timestamp)
        
        plc_tb_ctrl._debug('duration:{} offset:{} diff:{}'.format(fc.var_region_ver.duration,
                                                                  fc.var_region_ver.offset,
                                                                  ntb_diff))
        if plc_packet_helper.ntb_inside_range(ntb_diff, 
                                              plc_packet_helper.ms_to_ntb(-10), 
                                              plc_packet_helper.ms_to_ntb(10)):
            continue
        else:
            break
        

        
        #whether the DUT has adjusted it's beacon start time
    else:
        assert 0, "no renegotiation happens2"
     
     
    #-------------------------------------------------------------------------------
    #NCF with neighbor nid equals to DUTs' nid and bandwidth end after DUT's bandwidth
    #wait for new beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)
    #resynch the nid and sn        
    tb._configure_proxy('tb_time_config_req.yaml')     
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn) 
    
    time.sleep(2)
    
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):
        
        tb.tb_uart.clear_tb_port_rx_buf() 
    
        [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)  
    
        beacon_start_time = plc_packet_helper.get_beacon_period_start_time(beacon_payload) 
    
        #send simulated ncf
        cur_tb_time = tb._read_tb_time()
        
        presumed_ncf_sent_time = cur_tb_time + plc_packet_helper.ms_to_ntb(get_tb_time_delta_ms)
        #which phase we are in currently, we need find phase A (1) CSMA slot 
        while not plc_packet_helper.check_sof_time(presumed_ncf_sent_time, 
                                         presumed_ncf_sent_time + plc_packet_helper.ms_to_ntb(5), 
                                         1, 
                                         beacon_payload):
            #step is CSMA slot slice length
            presumed_ncf_sent_time += plc_packet_helper.ms_to_ntb(5)#slot_configurations.csma_slot_slice_len*10)
    

        
        
        #reserve 50ms margin 
        #plc_packet_helper.ntb_add(beacon_start_time, plc_packet_helper.ms_to_ntb(-50))
        
        #get the next beacon start boundary
        while plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time) < 0:
            beacon_start_time += plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
            
        bandwidth_offset = plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time)
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        plc_tb_ctrl._debug('beacon start time:{} ncf sent time:{} cur time:{}'.format(beacon_start_time,
                                                                        presumed_ncf_sent_time,
                                                                        tb._read_tb_time()))
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
        #neighbor network can see DUT's network and neighbor network bandwidth end firstly
        tb._send_ncf(neighbor_nid,1,100,plc_packet_helper.ntb_to_ms(bandwidth_offset),beacon_fc.nid)    
        

        [timestamp, fc] = tb._wait_for_plc_ncf(2)
        

        timestamp += plc_packet_helper.ms_to_ntb(fc.var_region_ver.offset)
        
        ntb_diff = plc_packet_helper.ntb_diff(beacon_start_time,timestamp)
        
        ntb_diff %= plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
        plc_tb_ctrl._debug('timestamp:{} fc:{} ntb_diff:{}'.format(timestamp,fc,ntb_diff))
        
        almost_zero = plc_packet_helper.ntb_inside_range(ntb_diff, 
                                              plc_packet_helper.ms_to_ntb(-10), 
                                              plc_packet_helper.ms_to_ntb(10))
                                              
        almost_up_boundary = plc_packet_helper.ntb_inside_range(ntb_diff, 
                                              plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload)-10), 
                                              plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload)))
         
        assert  almost_zero or almost_up_boundary, 'renegotiation happens3'                              
            

 
     #-------------------------------------------------------------------------------
    #NCF with neighbor nid equals to DUTs' nid and bandwidth end at the same time as 
    #DUT's bandwidth ending, neighbor nid < DUT's nid
    #wait for new beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)
    #resynch the nid and sn        
    tb._configure_proxy('tb_time_config_req.yaml')     
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)  
    
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)  
    
    beacon_start_time = plc_packet_helper.get_beacon_period_start_time(beacon_payload)   
    
    neighbor_nid = beacon_fc.nid - 1  
    
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):
        #send simulated ncf
        cur_tb_time = tb._read_tb_time()
        
        presumed_ncf_sent_time = cur_tb_time + plc_packet_helper.ms_to_ntb(get_tb_time_delta_ms)
        #which phase we are in currently, we need find phase A (1) CSMA slot 
        while not plc_packet_helper.check_sof_time(presumed_ncf_sent_time, 
                                         presumed_ncf_sent_time + plc_packet_helper.ms_to_ntb(5), 
                                         1, 
                                         beacon_payload):
            #step is CSMA slot slice length
            presumed_ncf_sent_time += plc_packet_helper.ms_to_ntb(5)#slot_configurations.csma_slot_slice_len*10)
    

        
        
        #reserve 50ms margin 
        #plc_packet_helper.ntb_add(beacon_start_time, plc_packet_helper.ms_to_ntb(-50))
        
        #get the next beacon start boundary
        while plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time) < 0:
            beacon_start_time += plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
            
        bandwidth_offset = plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time)
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        plc_tb_ctrl._debug('beacon start time:{} ncf sent time:{} cur time:{}'.format(beacon_start_time,
                                                                        presumed_ncf_sent_time,
                                                                        tb._read_tb_time()))
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
        #neighbor network can see DUT's network and neighbor network bandwidth end firstly
        tb._send_ncf(neighbor_nid,1,65,plc_packet_helper.ntb_to_ms(bandwidth_offset),beacon_fc.nid)    
        
        
        

        [timestamp, fc] = tb._wait_for_plc_ncf(2)
        
        plc_tb_ctrl._debug('duration:{}'.format(fc.var_region_ver.duration))
        timestamp += plc_packet_helper.ms_to_ntb(fc.var_region_ver.offset)
        
        ntb_diff = plc_packet_helper.ntb_diff(beacon_start_time,timestamp)
        
        ntb_diff %= plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
        plc_tb_ctrl._debug('duration:{} offset:{} diff:{}'.format(fc.var_region_ver.duration,
                                                                  fc.var_region_ver.offset,
                                                                  ntb_diff))
        if plc_packet_helper.ntb_inside_range(ntb_diff, 
                                              plc_packet_helper.ms_to_ntb(-10), 
                                              plc_packet_helper.ms_to_ntb(10)):
            continue
        else:
            break;
            
    else:
        assert 0, "no renegotiation happens4"
        
        
        
     #-------------------------------------------------------------------------------
    #NCF with neighbor nid equals to DUTs' nid and bandwidth end at the same time as 
    #DUT's bandwidth ending, neighbor nid > DUT's nid
    #wait for new beacon from DTU
    [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)
    #resynch the nid and sn        
    tb._configure_proxy('tb_time_config_req.yaml')     
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)  
    
#     [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)  
#     
#     beacon_start_time = plc_packet_helper.get_beacon_period_start_time(beacon_payload)     
    
    neighbor_nid = beacon_fc.nid + 1  
    
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):
        
        tb.tb_uart.clear_tb_port_rx_buf() 
    
        [timestamp,beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30,None,lambda fc,payload:fc.var_region_ver.phase == 1)  
    
        beacon_start_time = plc_packet_helper.get_beacon_period_start_time(beacon_payload) 
        #send simulated ncf
        cur_tb_time = tb._read_tb_time()
        
        presumed_ncf_sent_time = cur_tb_time + plc_packet_helper.ms_to_ntb(get_tb_time_delta_ms)
        #which phase we are in currently, we need find phase A (1) CSMA slot 
        while not plc_packet_helper.check_sof_time(presumed_ncf_sent_time, 
                                         presumed_ncf_sent_time + plc_packet_helper.ms_to_ntb(5), 
                                         1, 
                                         beacon_payload):
            #step is CSMA slot slice length
            presumed_ncf_sent_time += plc_packet_helper.ms_to_ntb(5)#slot_configurations.csma_slot_slice_len*10)
    

        
        
        #reserve 50ms margin 
        #plc_packet_helper.ntb_add(beacon_start_time, plc_packet_helper.ms_to_ntb(-50))
        
        #get the next beacon start boundary
        while plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time) < 0:
            beacon_start_time += plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
            
        bandwidth_offset = plc_packet_helper.ntb_diff(presumed_ncf_sent_time, beacon_start_time)
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        plc_tb_ctrl._debug('beacon start time:{} ncf sent time:{} cur time:{}'.format(beacon_start_time,
                                                                        presumed_ncf_sent_time,
                                                                        tb._read_tb_time()))
        
        #simulate another network and send NCF to DUT
        #phase indicates on which phase tb should send this NCF
        #bandwidth confliction
        
        #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
        #neighbor network can see DUT's network and neighbor network bandwidth end firstly
        tb._send_ncf(neighbor_nid,1,65,plc_packet_helper.ntb_to_ms(bandwidth_offset),beacon_fc.nid)    
        
        
        
     
        [timestamp, fc] = tb._wait_for_plc_ncf(2)
        
        plc_tb_ctrl._debug('duration:{}'.format(fc.var_region_ver.duration))
        timestamp += plc_packet_helper.ms_to_ntb(fc.var_region_ver.offset)
        
        ntb_diff = plc_packet_helper.ntb_diff(beacon_start_time,timestamp)
        
        ntb_diff %= plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))
        
        plc_tb_ctrl._debug('duration:{} offset:{} diff:{}'.format(fc.var_region_ver.duration,
                                                                  fc.var_region_ver.offset,
                                                                  ntb_diff))
        
        almost_zero = plc_packet_helper.ntb_inside_range(ntb_diff, 
                                              plc_packet_helper.ms_to_ntb(-10), 
                                              plc_packet_helper.ms_to_ntb(10))
                                              
        almost_up_boundary = plc_packet_helper.ntb_inside_range(ntb_diff, 
                                              plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload)-10), 
                                              plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload)))
         
        assert  almost_zero or almost_up_boundary, 'renegotiation happens5'


            
    cct.close_port()
