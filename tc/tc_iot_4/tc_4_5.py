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
    start_time = time.time()
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    plc_tb_ctrl._debug("step1: switch band if needed, wait for net working")
    tc_4_1.run(tb, band, False)

    tb.cct.close_port()

    stop_time = time.time()
    if stop_time - start_time < 3600:
        plc_tb_ctrl._debug("step2: wait for net stable %ds" % (stop_time - start_time))
        time.sleep(stop_time - start_time)

    plc_tb_ctrl._debug("step8: read mr")
    mulprocess = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                                   "true",
                                   config.SIMUCCT + "tc_4_5_read.ini"])
    mulprocess.wait()

    plc_tb_ctrl._debug("step9: multiple mr")

    mulprocess = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                                   "true",
                                   config.SIMUCCT + "tc_4_5_simu.ini"])
    mulprocess.wait()

