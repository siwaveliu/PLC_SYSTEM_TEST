# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import time
import concentrator
import plc_tb_ctrl
import tc_4_1
import tc_common
import config
'''
4.4 代理变更测试
验证多站点时代理变更的能力
'''


def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    node_addr_list_file_proxy = config.IOT_TOP_LIST_PROXY
    tc_4_1.run(tb, band)
    # 等待改变拓扑
    tc_common.pause_exec("Change attenuation and power down level3 STA, then press OK")
    # 关闭代理层级
    tb.usb_relay_device.open(3)
    nw_top_main, sec_node_list = tc_common.read_node_top_list(node_addr_list_file_proxy, None, True)
    plc_tb_ctrl._debug("wait 700s for top change")
    time.sleep(800)
    tc_common.check_nw_top(tb.cct, nw_top_main, 200)
    tb.usb_relay_device.close(3)
    # 恢复改变的拓扑
    tc_common.pause_exec("reset attenuation and power on level3 STA, then press OK")