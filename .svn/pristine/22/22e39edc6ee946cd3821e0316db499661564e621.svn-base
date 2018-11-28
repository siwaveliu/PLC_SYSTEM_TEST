# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter

'''
1. 连接设备，上电初始化；
2. 软件平台模拟电表，在收到待测未入网 STA 的读表号请求后，通过串口向其下发表地址；
3. 软件平台模拟 PCO 通过透明物理设备向待测未入网 STA 设备发送【代理信标帧】，规划 CSMA
时隙（Ts~Te）， 软件平台记录本平台的【代理信标帧】的信标时间戳 T1，设置待测 STA 发送的【关
联请求】预期接收时间段△Tr 为（T1+Ts） ~（T1+Te),同时启动定时器（定时时长 10s），查看是
否在规定的 CSMA 时隙收到待测 STA 发出的【关联请求】报文；
4. 若软件平台在定时器时长内收到 STA 的【关联请求】，记录软件平台实际接收时间 TR,对比△
Tr 与 TR，若 TR 不在△Tr 范围内，则未入网 STA 收到代理信标后，不会调整自身的 NTB，反之未
入网 STA 收到代理信标后，会调整自身的 NTB；
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
    beacon_dict = tb._load_data_file('tb_beacon_data_2_2.yaml')
    beacon_dict['cfg_csma_flag'] = 1
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1

    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)
    beacon_period = plc_packet_helper.ms_to_ntb(beacon_dict['period'])
    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)

    #config nid and nw_sn for sending of mpdu
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])



    # 等待STA1发送关联请求
    plc_tb_ctrl._debug("wait for assoc req")
    stop_time = time.time() + tc_common.calc_timeout(30)
    while True:
        assert time.time() < stop_time, "30s timeout"

        result = tb._wait_for_fc_pl_data(tb._check_fc_pl_payload, timeout=1, timeout_cb=lambda:None)

        if result is not None:
            [timestamp, fc, data] = result
            if ("PLC_MPDU_SOF" == fc.mpdu_type):
                sof_start_time = timestamp
                mac_frame = data
                if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_NMM":
                    continue

                nmm_data = mac_frame.msdu.data
                nmm = plc_packet_helper.parse_nmm(nmm_data)
                if nmm is None:
                    continue

                if ("MME_ASSOC_REQ" != nmm.header.mmtype):
                    plc_tb_ctrl._debug("not MME_ASSOC_REQ")
                    continue

                phase = plc_packet_helper.map_phase_str_to_value(nmm.body.phase_0)

                beacon_period_cnt = 0
                while not plc_packet_helper.ntb_inside_range(sof_start_time,
                                                             beacon_period_start_time,
                                                             beacon_period_end_time):
                    beacon_period_start_time = beacon_period_end_time
                    beacon_period_end_time = plc_packet_helper.ntb_add(beacon_period_start_time, beacon_period)
                    beacon_period_cnt += 1

                curr_beacon = beacon_dict['payload']['value']
                curr_beacon['beacon_info']['beacon_item_list'][2]['beacon_item']['beacon_period_start_time'] = beacon_period_start_time
                frame_len = fc.var_region_ver.frame_len * 10
                sof_end_time = plc_packet_helper.ntb_add(sof_start_time, plc_packet_helper.us_to_ntb(frame_len))
                correct_time = plc_packet_helper.check_sof_time(sof_start_time, sof_end_time, phase, curr_beacon)
                assert correct_time, "wrong sof rx time"

                break



    m.close_port()


