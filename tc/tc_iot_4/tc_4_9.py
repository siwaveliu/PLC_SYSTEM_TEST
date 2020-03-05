# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import tc_4_1
import subprocess
import config
import time
'''
4.9 实时费控测试
验证多 STA 站点时全网实时费控准确性
'''


def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    plc_tb_ctrl._debug("step1: switch band if needed, wait for net working")
    nw_top, nodes_list = tc_4_1.run(tb, band, False)

    tb.cct.close_port()
    time.sleep(1)

    plc_tb_ctrl._debug("step2: start SimulateConcentrator to read meter")
    mulprocess = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                                   "true",
                                   config.SIMUCCT + "tc_4_9_read.ini"])
    mulprocess.wait()
