# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import time
import config

'''
cco 切频段
'''

def run(tb, cct, band, addrfilepath, *channel):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    node_addr_list_file = addrfilepath
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(cct, concentrator.Concentrator), "cct type is not concentrator"
    cco_mac_addr = cct.mac_addr  # type: str
    tc_common.wait_cco_power_on(tb, cct, *channel)
    plc_tb_ctrl._debug("read default band")
    r_band = tc_common.read_cco_band(cct)
    plc_tb_ctrl._debug("default Band: " + str(r_band))
    if  r_band != band:
        plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
        tc_common.set_cco_mac_addr(cct, cco_mac_addr)

        plc_tb_ctrl._debug("reset CCO param area")
        tc_common.reset_cco_param_area(cct)

        #set sub node address
        plc_tb_ctrl._debug("set sub node address to consorting cco, and start the escort net")

        # set sub node address
        plc_tb_ctrl._debug("set sub node address to main cco, and start the main net")
        nw_top_main, sec_nodes_addr_list = tc_common.read_node_top_list(node_addr_list_file, cco_mac_addr, False)

        tc_common.add_sub_node_addr(cct, sec_nodes_addr_list)

        tc_common.check_nw_top(cct, nw_top_main, 800)

        tc_common.write_cco_band(cct, band)
        plc_tb_ctrl._debug("wait for cco switch band")
        tc_common.activate_tb(tb, band)
        tb._change_band(band)
        wait = True
        starttime = time.time()
        endtime = starttime.__add__(10 * 60)
        while wait:
            if endtime < time.time():
                break
            payload = tb._wait_for_plc_beacon(endtime - time.time())[2]
            plc_tb_ctrl._debug(payload.cco_mac_addr)
            # if payload.cco_mac_addr == cco_mac_addr:
            wait = False
        assert wait == False, 'cco switch band timeout'
        plc_tb_ctrl._debug("switch Band elapse: {:.2f}".format(time.time() - starttime) )
        tc_common.check_nw_top(cct, nw_top_main, 60)
        return True
    else:
        return False






