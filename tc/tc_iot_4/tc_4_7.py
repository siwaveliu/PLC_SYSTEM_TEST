# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time


'''
4.7 搜表功能测试
验证多 STA 站点时搜表准确性和效率
'''

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"

    cco_mac_addr      = '00-00-00-00-00-9C'
    cct = concentrator.Concentrator()
    cct.open_port()

    gdw1376p2_frame = cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1)

    plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
    tc_common.set_cco_mac_addr(cct, cco_mac_addr)

    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(cct)

    #set sub node address
    plc_tb_ctrl._debug("add secondary nodes")
    # key is meter address, value is level
    nw_top = {
         cco_mac_addr: 0,
         '00-00-01-68-50-27': 1,
         '00-00-01-63-54-52': 2,
         '00-00-01-63-28-29': 3,
         '00-00-01-70-33-67': 4,
         '00-00-01-61-22-95': 5
    }

    sec_nodes_addr_list = []
    for meter_addr, level in nw_top.iteritems():
        if (level > 0):
            sec_nodes_addr_list.append(meter_addr)

    plc_tb_ctrl._debug(sec_nodes_addr_list)
    tc_common.add_sub_node_addr(cct, sec_nodes_addr_list)

    plc_tb_ctrl._debug("step5: check nw top")
    tc_common.check_nw_top(cct, nw_top)

    plc_tb_ctrl._debug("step6: send 11f5")
    dl_afn11f5_pkt = tb._load_data_file(data_file='afn11f5_dl.yaml')
    dl_afn11f5_pkt['cf']['prm'] = 'MASTER'
    dl_afn11f5_pkt['user_data']['value']['r']['sn'] = 1
    duration = dl_afn11f5_pkt['user_data']['value']['data']['data']['duration']
    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn11f5_pkt)
    assert msdu is not None
    cct.send_frame(msdu)

    plc_tb_ctrl._debug("step7: wait for 06f4 and 06f3")
    start_time = time.time()
    timeout = tc_common.calc_timeout(duration * 60 + 10)
    stop_time = start_time + timeout
    while (True):
        gdw1376p2_frame = cct.wait_for_gdw1376p2_frame(timeout=timeout)

        user_data = gdw1376p2_frame.user_data.value
        dt = concentrator.calc_gdw1376p2_dt(user_data.data.dt1, user_data.data.dt2)
        plc_tb_ctrl._debug("receive afn{:02X}f{}".format(user_data.afn, dt))
        if ((user_data.afn == 0x06) and (4 == dt)): # 06F4 从节点信息及设备类型
            tc_common.send_gdw1376p2_ack(cct, user_data.r.sn)
            afn06f4 = user_data.data.data
            for node in afn06f4.node:
                if node.addr in sec_nodes_addr_list:
                    sec_nodes_addr_list.remove(node.addr)
        elif ((user_data.afn == 0x06) and (3 == dt)): # 06F4 路由工况变动信息
            tc_common.send_gdw1376p2_ack(cct, user_data.r.sn)
            if user_data.data.data.type == 'METER_SEARCH_TASK_COMPLETE':
                break

        timeout = stop_time - time.time()


    elapsed_time = round((time.time() - start_time) / 60)
    assert len(sec_nodes_addr_list) == 0, "meter search fail"
    assert elapsed_time == duration, "receive receive 06f3 late"
