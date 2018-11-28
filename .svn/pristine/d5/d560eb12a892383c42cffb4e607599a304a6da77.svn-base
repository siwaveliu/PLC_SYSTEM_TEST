# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import meter
import tc_common
import plc_packet_helper
import time

'''
1. 连接设备，将待测 STA 上电初始化；
2. 软件平台模拟电表，在收到待测 STA 的读表号请求后，向其下发表地址；
3. 软件平台模拟 PCO 周期性向待测 STA 设备发送“代理信标” （站点层级 1），同时启
用定时器 15s；
4. 定时时间内软件平台等待待测 STA 向 PCO 发出的“关联请求”报文；
5. 定时时间内软件平台若收不到站点发出的“关联请求”报文，则失败，若是收到，
则调用一致性评价模块，测试协议一致性，若一致则通过，若不一致，则测试不通
过。
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

    #send proxy beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data_7.yaml')
    tb._configure_beacon(None, beacon_dict)
    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm('MME_ASSOC_REQ',15)

    #whether received associated request or not, stop beacon scheduling
    beacon_dict['num'] = 0
    tb._configure_beacon(None, beacon_dict)



    assert fc.var_region_ver.dst_tei == 2
    assert mac_frame_head.org_dst_tei == 1 or mac_frame_head.org_dst_tei == 2
    assert mac_frame_head.hop_limit == 2
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 2
    assert nmm.body.mac_addr_type == 'MAC_ADDR_TYPE_METER_ADDRESS'



    m.close_port()






