# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import tc_4_1


'''
4.9 实时费控测试
验证多 STA 站点时全网实时费控准确性
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
                                 50, [[0x00, 0x00, 0x00, 0x00],
                                      [0x00, 0x00, 0x00, 0x01],
                                      [0x00, 0x00, 0x00, 0x02]]) # 上一次日冻结正向有功电能数据


