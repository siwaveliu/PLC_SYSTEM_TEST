# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import tc_4_1
import time


'''
4.7 搜表功能测试
验证多 STA 站点时搜表准确性和效率
'''

def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    plc_tb_ctrl._debug("step1: switch band if needed, wait for net working")
    nw_top, nodes_list = tc_4_1.run(tb, band)


    plc_tb_ctrl._debug("step6: send 11f5")
    dl_afn11f5_pkt = tb._load_data_file(data_file='afn11f5_dl.yaml')
    dl_afn11f5_pkt['cf']['prm'] = 'MASTER'
    dl_afn11f5_pkt['user_data']['value']['r']['sn'] = 1
    duration = dl_afn11f5_pkt['user_data']['value']['data']['data']['duration']
    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn11f5_pkt)
    assert msdu is not None
    tb.cct.send_frame(msdu)

    plc_tb_ctrl._debug("step7: wait for 06f4 and 06f3")
    start_time = time.time()
    timeout = tc_common.calc_timeout(duration * 60 + 10)
    stop_time = start_time + timeout
    while (True):
        gdw1376p2_frame = tb.cct.wait_for_gdw1376p2_frame(timeout=timeout)
        user_data = gdw1376p2_frame.user_data.value
        dt = concentrator.calc_gdw1376p2_dt(user_data.data.dt1, user_data.data.dt2)
        plc_tb_ctrl._debug("receive afn{:02X}f{}".format(user_data.afn, dt))
        if ((user_data.afn == 0x06) and (4 == dt)): # 06F4 从节点信息及设备类型
            tc_common.send_gdw1376p2_ack(tb.cct, user_data.r.sn)
            afn06f4 = user_data.data.data
            for node in afn06f4.node:
                if node.addr in nodes_list:
                    nodes_list.remove(node.addr)
            if nodes_list.__len__() == 0:
                break
        elif ((user_data.afn == 0x06) and (3 == dt)): # 06F4 路由工况变动信息
            tc_common.send_gdw1376p2_ack(tb.cct, user_data.r.sn)
            if user_data.data.data.type == 'METER_SEARCH_TASK_COMPLETE':
                break

        timeout = stop_time - time.time()


    elapsed_time = round((time.time() - start_time) / 60)
    assert len(nodes_list) == 0, "meter search fail"
    assert elapsed_time == duration, "receive receive 06f3 late"
