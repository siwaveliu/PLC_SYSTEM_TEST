# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time


'''
4.4 代理变更测试
验证多站点时代理变更的能力
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

    #set sub node address
    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(cct)


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

    plc_tb_ctrl._debug("step4: add secondary nodes")
    plc_tb_ctrl._debug(sec_nodes_addr_list)
    tc_common.add_sub_node_addr(cct, sec_nodes_addr_list, False)

    plc_tb_ctrl._debug("step6: check network top")
    tc_common.check_nw_top(cct, nw_top)

    tc_common.pause_exec("Change attenuation and power down level3 STA, then press OK")

    plc_tb_ctrl._debug("step7: check new nw top")
    nw_top = {
         cco_mac_addr: 0,
         '00-00-01-68-50-27': 1,
         '00-00-01-63-54-52': 2,
         '00-00-01-70-33-67': 3,
         '00-00-01-61-22-95': 4
    }
    # 海思需要700秒将STA3剔除，按照离线（1个心跳周期，即2个路由周期）和脱网（4个心跳周期，即8个路由周期）的条件
    tc_common.check_nw_top(cct, nw_top, timeout=800)

