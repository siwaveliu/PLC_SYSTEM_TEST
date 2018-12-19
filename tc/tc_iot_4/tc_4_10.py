# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import tc_4_1
from threading import Thread
import time

'''
4.10 多网络综合测试
验证在多网络条件下，每一个网络的抄表效率和准确性
'''


def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    plc_tb_ctrl._debug("step1: switch band if needed, wait for net working")
    nw_top, nodes_list = tc_4_1.run(tb, band)
    # nodes_list = ["0-0-0-0-1-1", "0-0-0-0-1-2", "0-0-0-0-1-3", "0-0-0-0-1-4"]
    plc_tb_ctrl._debug("step7: get meter read max exp time")
    mr_max_exp_time = tc_common.read_mr_max_exp_time(tb.cct) + 5
    tb.usb_relay_device = None
    plc_tb_ctrl._debug("step8: single mr")
    # tc_common.exec_cct_mr_single(tb, tb.cct, tb.cct.mac_addr,
    #                              nodes_list, mr_max_exp_time,
    #                              50, [[0x00, 0x00, 0x00, 0x00]]) # 上一次日冻结正向有功电能数据
    p1 = Thread(target=tc_common.exec_cct_mr_single, name="p1", args=(tb, tb.cct, tb.cct.mac_addr,
                                                                       nodes_list, mr_max_exp_time,
                                                                       50, [[0x00, 0x00, 0x00, 0x00]]))
    p1.start()
    while p1.is_alive():
        time.sleep(1)
    tb.cct.close_port()
