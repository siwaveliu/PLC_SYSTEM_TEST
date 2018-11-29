# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
from robot.libraries import Dialogs
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import cco_switch_band
import config
import tc_4_1

'''
4.3 站点离线测试
验证多站点时站点离线准确率和效率
'''

def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    node_addr_list_file_dynatic = u'tc/tc_iot_4/互操作性表架拓扑地址_动态_树形.txt'
    nw_top_main = tc_4_1.run(tb, band)

    # 删除动态文件中从节点
    plc_tb_ctrl._debug("set another half of nodes's address to main cco, and start the main net")
    nw_top_main_other, sec_nodes_addr_list = tc_common.read_node_top_list(node_addr_list_file_dynatic, None, True)
    tc_common.del_sub_node_addr(tb.cct, sec_nodes_addr_list)
    # 更新拓扑图
    for key in nw_top_main_other:
        del nw_top_main[key]
    # 检查拓扑图
    tc_common.check_nw_top(tb.cct, nw_top_main, 100)


