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

    node_addr_list_file_static = config.IOT_TOP_LIST_STATIC
    node_addr_list_file_dynatic = config.IOT_TOP_LIST_DYNATIC
    band = int(band)
    if  band != config.DEFAULT_BAND:
        cco_switch_band.run(tb, tb.cct, band)
        config.DEFAULT_BAND = band
    tb.meter_platform_power_reset()

    # 确认CCO已经激活
    res = None
    for i in range(3):
        tb.meter_platform_power_reset()
        res = tb.cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1, tm_assert=False)
        if  res is None:
            continue
        else:
            break
    assert res is not None, "wait 03H_F10 failed, check cco device"
    # 设置主节点地址
    cco_mac_addr      = '00-00-00-00-00-9C'
    plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
    tc_common.set_cco_mac_addr(tb.cct, cco_mac_addr)
    tb.cct.mac_addr = cco_mac_addr

    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(tb.cct)

    # 添加先入网的从节点
    plc_tb_ctrl._debug("set half of nodes's address to main cco, and start the main net")
    nw_top_main, sec_nodes_addr_list =tc_common.read_node_top_list(node_addr_list_file_static, cco_mac_addr, True)
    tc_common.add_sub_node_addr(tb.cct, sec_nodes_addr_list)
    # 检查拓扑图
    tc_common.check_nw_top(tb.cct, nw_top_main, 500)

    # 添加后入网的从节点
    plc_tb_ctrl._debug("set another half of nodes's address to main cco, and start the main net")
    nw_top_main_other, sec_nodes_addr_list = tc_common.read_node_top_list(node_addr_list_file_dynatic, None, True)
    tc_common.add_sub_node_addr(tb.cct, sec_nodes_addr_list)
    # 更新拓扑图
    nw_top_main.update(nw_top_main_other)
    # 检查新的拓扑图
    tc_common.check_nw_top(tb.cct, nw_top_main, 500)

    # Dialogs.pause_execution("Add new secondary nodes")



