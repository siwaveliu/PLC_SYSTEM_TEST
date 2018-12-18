# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import concentrator
import plc_tb_ctrl
import tc_4_1
import tc_common
import subprocess
import config
import time
'''
4.5 全网抄表测试
验证多 STA 站点时全网抄表效率和准确性
1. 点抄STA3
2. 并发抄表STA1~3
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

    plc_tb_ctrl._debug("step7: get meter read max exp time")
    mr_max_exp_time = tc_common.read_mr_max_exp_time(tb.cct) + 5

    plc_tb_ctrl._debug("step8: single mr")
    tc_common.exec_cct_mr_single(tb, tb.cct, tb.cct.mac_addr,
                                 nodes_list, mr_max_exp_time,
                                 50, [0x00, 0x00, 0x00, 0x00]) # 上一次日冻结正向有功电能数据
    tb.cct.close_port()
    time.sleep(1)
    plc_tb_ctrl._debug("step9: multiple mr")

    mulprocess = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                                   "true",
                                   config.SIMUCCT + "tc_4_5.ini"])
    mulprocess.wait()

