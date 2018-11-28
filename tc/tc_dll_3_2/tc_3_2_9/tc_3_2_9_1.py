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
向待测 CCO 下发“添加从节点”命令，将目标网络站点的 MAC 地址下发到 CCO 中，等待“确
认”；
3. 软件平台收到待测 CCO 发出的“中央信标”后，开启 60s 定时器，对待测 CCO 发送的“网间
协调帧”进行一段时间的统计，验证是否在 A、 B、 C 三个相线上周期性发送（每个相线至少
60 帧）；
（1） 在 A、 B、 C 三个相线一共至少收到 60 个“网间协调帧” ，则 pass；
（2） 其他情况， fail。
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

    #get csma slot configuration
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_payload)
    beacon_slot_total_len = beacon_slot_alloc.beacon_slot_len*(beacon_slot_alloc.ncb_slot_num 
                                                               + beacon_slot_alloc.cb_slot_num)
    csma_slot_start_time = plc_packet_helper.ntb_add(beacon_slot_alloc.beacon_period_start_time,
                                                     plc_packet_helper.ms_to_ntb(beacon_slot_total_len))

    csma_slot_slice_length = plc_packet_helper.ms_to_ntb(
                            beacon_slot_alloc.csma_slot_slice_len*10)
    csma_slot_end_time = plc_packet_helper.ntb_add(beacon_slot_alloc.beacon_period_start_time,
                                                   plc_packet_helper.ms_to_ntb(
                                                       plc_packet_helper.get_beacon_period(beacon_payload)))


    #network negotiation frame statistics
    stop_time = time.time() + tc_common.calc_timeout(60)

    ncf_counter = [0,0,0]

    csma_slot_config = plc_packet_helper.calc_csma_slot_config(beacon_payload)

#     phase_a_number = 0
#     phase_b_number = 0
#     phase_c_number = 0
    ntb_2_seconds = plc_packet_helper.ms_to_ntb(plc_packet_helper.get_beacon_period(beacon_payload))

    while(time.time()< stop_time):
        ret = tb._wait_for_plc_ncf(stop_time-time.time(),lambda:None,None)
        if ret is not None:
            [timestamp, fc] = ret
            #get the last csma slot start time
            while (plc_packet_helper.ntb_diff(csma_slot_start_time,timestamp) > ntb_2_seconds):
                csma_slot_start_time = plc_packet_helper.ntb_add(csma_slot_start_time,ntb_2_seconds)

            csma_offset = plc_packet_helper.ntb_diff(csma_slot_start_time,timestamp)

            csma_slot_index = csma_offset/plc_packet_helper.ms_to_ntb(
                            beacon_slot_alloc.csma_slot_slice_len*10)

            phase = csma_slot_config['slice_list'][csma_slot_index]
            plc_tb_ctrl._debug('got a ncf, phase:{}'.format(phase))
            ncf_counter[phase - 1] += 1
            
  
    
    plc_tb_ctrl._debug('ncf number in 3 phases: {}'.format(ncf_counter))
    assert ncf_counter[0] + ncf_counter[1] + ncf_counter[2] > 60

    cct.close_port()
