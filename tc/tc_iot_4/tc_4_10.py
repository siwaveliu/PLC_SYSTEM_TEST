# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import subprocess
import time
import config
import tc_4_1
import InitWholeNetCCO
'''
4.10 多网络综合测试
验证在多网络条件下，每一个网络的抄表效率和准确性
'''
CONCENTRATOR_OTHER_PORT = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6']  # type: list
MUL_NET_NUM = 6


def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is not plc_tb_ctrl.PlcSystemTestbench"
    band = int(band)
    tc_4_1.run(tb, band, False)
    plc_tb_ctrl._debug("step1: switch band if needed.")
    tb.cct.close_port()
    InitWholeNetCCO.run(tb, 6, band, True)
    # 多网络点抄
    process_list = []
    plc_tb_ctrl._debug("step8: read mr -------------------------------------------------")
    for i in range(MUL_NET_NUM):
        m1 = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                               "true",
                               config.SIMUCCT + "tc_4_10_read_6_{}.ini".format(str(i + 1))])
        process_list.append(m1)
        time.sleep(5)

    for i in range(MUL_NET_NUM):
        process_list[i].wait()

    # 多网络点抄
    plc_tb_ctrl._debug("step9: multiple mr")
    process_list = []
    for i in range(MUL_NET_NUM):
        m1 = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                               "true",
                               config.SIMUCCT + "tc_4_10_simu_6_{}.ini".format(str(i + 1))])
        process_list.append(m1)
        time.sleep(5)

    for i in range(MUL_NET_NUM):
        process_list[i].wait()
