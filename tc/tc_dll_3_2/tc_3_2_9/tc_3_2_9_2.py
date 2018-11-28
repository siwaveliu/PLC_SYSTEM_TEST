# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，上电初始化；
2. 软件平台模拟集中器通过串口向待测 CCO 下发“设置主节点地址”命令，在收到“确认”
后，向待测 CCO 下发“添加从节点”命令，将目标网络站点的 MAC 地址下发到 CCO 中，
等待“确认”；
3. 软件平台收到待测 CCO 发送的“网间协调帧”后，通过物理透明平台向待测 CCO 发送正
常的“网间协调帧”，同时启动定时器（定时时长 10s），查看定时器溢出前是否收到待
测 CCO 发出正常的“网间协调帧”且其中携带模拟 CCO 的 NID 信息。
（1） 定时器未溢出，收到正确的“网间协调帧”（携带模拟 CCO 的 NID） ，则 pass；
（2） 定时器溢出，收到过“网间协调帧”（但未携带模拟 CCO 的 NID），则 fail；
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
    sub_nodes_addr = map(lambda x: '00-00-00-00-00-' + str(x).zfill(2), range(2,4))
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
    neighbor_nid = 0xFF 
    #tb._send_ncf(beacon_fc.nid,'PHASE_A',1000,0,0xFF)  
    tb._send_ncf(0xFF,1,1000,0,0)     
    
    
    stop_time = time.time() + tc_common.calc_timeout(10)
    while(time.time()< stop_time):
        [timestamp, fc] = tb._wait_for_plc_ncf(10)
        if fc.var_region_ver.neigh_nid == 0xFF:
            break;
           
  
    else:
        assert 0, "no valid NCF is received"
    
    
    cct.close_port()
