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
        *channel: 互操作性表架的电源通道
    """
    node_addr_list_file = addrfilepath
    if node_addr_list_file is None:
        node_addr_list_file = config.IOT_TOP_LIST_ALL
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(cct, concentrator.Concentrator), "cct type is not concentrator"
    cco_mac_addr = cct.mac_addr  # type: str
    tc_common.wait_cco_power_on(tb, cct, *channel)
    tb._deactivate_tb()
    plc_tb_ctrl._debug("read default band")
    r_band = tc_common.read_cco_band(cct)
    plc_tb_ctrl._debug("default Band: " + str(r_band))
    if  r_band != band:
        plc_tb_ctrl._debug("default Band: {} is different target: {}".format(r_band, band))
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

        tc_common.check_nw_top(cct, nw_top_main, 1800)

        tc_common.write_cco_band(cct, band)
        plc_tb_ctrl._debug("wait for cco switch band")
        tb._change_band(band)
        wait = True
        starttime = time.time()
        endtime = starttime.__add__(1000000 * 300)
        plc_tb_ctrl._debug("starttime:{} ;end time:{}".format(starttime, endtime))
        while wait:
            if endtime < time.time():
                break
            payload = tb._wait_for_plc_beacon(10, timeout_cb=timeout_function)
            if payload is not None:
                bc_payload = payload[2]
                plc_tb_ctrl._debug("CCO BEACON addr:{}".format(bc_payload.cco_mac_addr))
                if bc_payload.cco_mac_addr == cco_mac_addr:
                    wait = False
                    break
        assert wait == False, 'cco switch band timeout'
        plc_tb_ctrl._debug("switch Band: {};elapse: {:.2f}".format(band, time.time() - starttime) )
        tc_common.check_nw_top(cct, nw_top_main, 60)
        plc_tb_ctrl._debug("sleep for sta switch band: {:.2f}s".format(300 - (time.time() - starttime)))
        time.sleep(300 - (time.time() - starttime))
        tb._deactivate_tb()
        return True
    else:
        plc_tb_ctrl._debug("default Band: {} is same target: {}".format(r_band, band))
        return False

def timeout_function():
    pass





