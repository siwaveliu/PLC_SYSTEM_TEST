# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time


'''
4.10 多网络综合测试
验证在多网络条件下，每一个网络的抄表效率和准确性
'''

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"

    cco_mac_addr      = '00-00-00-00-00-9C'
    cct = concentrator.Concentrator()
    cct.open_port()

    gdw1376p2_frame = cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1)

    plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
    tc_common.set_cco_mac_addr(cct, cco_mac_addr)

    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(cct)

    #set sub node address
    plc_tb_ctrl._debug("add secondary nodes")
    # key is meter address, value is level
    nw_top = {
         cco_mac_addr: 0,
         '00-00-01-68-50-27': 1,
         '00-00-01-63-54-52': 2,
         '00-00-01-63-28-29': 3,
         '00-00-01-70-33-67': 4,
         '00-00-01-61-22-95': 5
    }

    sec_nodes_addr_list = []
    for meter_addr, level in nw_top.iteritems():
        if (level > 0):
            sec_nodes_addr_list.append(meter_addr)

    plc_tb_ctrl._debug(sec_nodes_addr_list)
    tc_common.add_sub_node_addr(cct, sec_nodes_addr_list)

    plc_tb_ctrl._debug("step6: check nw top")
    tc_common.check_nw_top(cct, nw_top)

    plc_tb_ctrl._debug("step7: get meter read max exp time")
    mr_max_exp_time = tc_common.read_mr_max_exp_time(cct) + 5

    plc_tb_ctrl._debug("step8: single mr")
    tc_common.exec_cct_mr_single(tb, cct, cco_mac_addr,
                                 sec_nodes_addr_list[2], mr_max_exp_time,
                                 10, [0x01, 0x01, 0x06, 0x05]) # 上一次日冻结正向有功电能数据

    plc_tb_ctrl._debug("step9: multiple mr")
    di_list = [
        [0x01, 0x01, 0x06, 0x05], #上一次日冻结正向有功电能数据
        [0x01, 0x00, 0x06, 0x05], # （上 1 次）日冻结时间
        [0x00, 0x00, 0x00, 0x00], # 当前组合有功总电能
    ]
    tc_common.exec_cct_mr_multiple(tb, cct, cco_mac_addr,
                                   sec_nodes_addr_list[0:3], 90, 10,
                                   di_list)


    assert False, "not verified yet"
