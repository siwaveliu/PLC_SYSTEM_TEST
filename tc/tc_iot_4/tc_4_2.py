# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
from robot.libraries import Dialogs
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time


'''
4.2 站点入网测试
验证多站点时新增站点入网的准确率和效率
1) 添加第一批从节点, 检查入网是否完成
2) 添加第二批从节点，并上电，检查入网是否完成
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

    # key is meter address, value is level
    nw_top = {
         cco_mac_addr: 0,
         '00-00-01-68-50-27': 1,
         '00-00-01-63-54-52': 2,
         '00-00-01-63-28-29': 3,
    }

    sec_nodes_addr_list1 = []
    for meter_addr, level in nw_top.iteritems():
        if (level > 0):
            sec_nodes_addr_list1.append(meter_addr)

    plc_tb_ctrl._debug("step4: add secondary nodes")
    plc_tb_ctrl._debug(sec_nodes_addr_list1)
    tc_common.add_sub_node_addr(cct, sec_nodes_addr_list1)

    plc_tb_ctrl._debug("step6: check network top")
    tc_common.check_nw_top(cct, nw_top)

    Dialogs.pause_execution("Add new secondary nodes")

    plc_tb_ctrl._debug("step7: add new secondary nodes")
    # key is meter address, value is level
    nw_top = {
         cco_mac_addr: 0,
         '00-00-01-68-50-27': 1,
         '00-00-01-63-54-52': 2,
         '00-00-01-63-28-29': 3,
         '00-00-01-70-33-67': 4,
         '00-00-01-61-22-95': 5
    }

    sec_nodes_addr_list2 = []
    for meter_addr, level in nw_top.iteritems():
        if ((level > 0) and (meter_addr not in sec_nodes_addr_list1)):
            sec_nodes_addr_list2.append(meter_addr)

    plc_tb_ctrl._debug(sec_nodes_addr_list2)
    tc_common.add_sub_node_addr(cct, sec_nodes_addr_list2)

    Dialogs.pause_execution("Power on new STA then press OK")

    plc_tb_ctrl._debug("step8: check new network top")
    tc_common.check_nw_top(cct, nw_top)


