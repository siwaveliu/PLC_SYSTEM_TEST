# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
from robot.libraries import Dialogs
import concentrator
import config
import plc_tb_ctrl
import tc_common
import cco_switch_band
'''
4.2 站点入网测试
验证多站点时新增站点入网的准确率和效率
1) 添加第一批从节点, 检查入网是否完成
2) 添加第二批从节点，并上电，检查入网是否完成
'''

def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    node_addr_list_file_static = u'tc/tc_iot_4/互操作性表架拓扑地址_静态_树形.txt'
    node_addr_list_file_dynatic = u'tc/tc_iot_4/互操作性表架拓扑地址_动态_树形.txt'
    band = int(band)
    if  band != config.DEFAULT_BAND:
        cco_switch_band.run(tb, tb.cct, band)

    tb.meter_platform_power_reset()

    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(tb.cct)

    # 等待CCO上电
    tb.cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1)
    # 设置主节点地址
    cco_mac_addr      = '00-00-00-00-00-9C'
    plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
    tc_common.set_cco_mac_addr(tb.cct, cco_mac_addr)
    tb.cct.mac_addr = cco_mac_addr

    # 添加先入网的从节点
    plc_tb_ctrl._debug("set half of nodes's address to main cco, and start the main net")
    f = open(node_addr_list_file_static, 'r')
    addr_list = f.readlines()
    nw_top_main = {cco_mac_addr: 0}
    for l in addr_list:
        # key is meter address, value is level
        key, value = l.split(':')
        nw_top_main[key] = int(value.strip())
    f.close()
    sec_nodes_addr_list = []
    for meter_addr, level in nw_top_main.iteritems():
        if (level > 0):
            sec_nodes_addr_list.append(meter_addr)
    tc_common.add_sub_node_addr(tb.cct, sec_nodes_addr_list)

    # 添加后入网的从节点
    plc_tb_ctrl._debug("set another half of nodes's address to main cco, and start the main net")
    f = open(node_addr_list_file_dynatic, 'r')
    addr_list = f.readlines()
    nw_top_main_other = {}
    for l in addr_list:
        # key is meter address, value is level
        key, value = l.split(':')
        nw_top_main_other[key] = int(value.strip())
        nw_top_main[key] = int(value.strip())
    f.close()
    sec_nodes_addr_list = []
    for meter_addr, level in nw_top_main_other.iteritems():
        sec_nodes_addr_list.append(meter_addr)
    tc_common.add_sub_node_addr(tb.cct, sec_nodes_addr_list)

    tc_common.check_nw_top(tb.cct, nw_top_main, 500)

    # Dialogs.pause_execution("Add new secondary nodes")



