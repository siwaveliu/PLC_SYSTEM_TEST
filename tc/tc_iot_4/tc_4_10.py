# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import subprocess
import time
import config
import cco_switch_band
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

    plc_tb_ctrl._debug("step1: switch band if needed.")
    tb.cct.mac_addr =  '00-12-34-56-78-90'

    cct_other = concentrator.Concentrator(config.CONCENTRATOR_OTHER_PORT)
    cct_other.open_port()
    cct_other.mac_addr = '00-12-34-56-78-91'

    band = int(band)
    cco_switch_band.run(tb, tb.cct, band, config.IOT_TOP_LIST_2_1, 1, 3)
    # 在脚本启动的通用入口，默认会关闭陪测得cco
    tb._deactivate_tb()
    cco_switch_band.run(tb, cct_other, band, config.IOT_TOP_LIST_2_2, 2)
    # 关闭串口
    tb.cct.close_port()
    cct_other.close_port()
    # 待测CCO复位
    plc_tb_ctrl._debug("reset determinand cco")
    tb.meter_platform_power_tested_reset()
    # 陪测的CCO复位
    tb.meter_platform_power_escort(2)

    plc_tb_ctrl._debug("step8: read mr")
    m1 = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                          "true",
                          config.SIMUCCT + "tc_4_10_read_2_1.ini"])
    m2 = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                          "true",
                          config.SIMUCCT + "tc_4_10_read_2_2.ini"])

    m1.wait()
    m2.wait()

    plc_tb_ctrl._debug("step9: multiple mr")
    m1 = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                          "true",
                          config.SIMUCCT + "tc_4_10_simu_2_1.ini"])
    m2 = subprocess.Popen([config.SIMUCCT + "SimulatedConcentrator.exe",
                          "true",
                          config.SIMUCCT + "tc_4_10_simu_2_2.ini"])
    m1.wait()
    m2.wait()