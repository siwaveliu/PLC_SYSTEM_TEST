# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import time


'''
cco 切频段
'''

def run(tb, cct, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    node_addr_list_file = u'tc/tc_iot_4/互操作性表架拓扑地址_完整版_树形.txt'
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(cct, concentrator.Concentrator), "cct type is not concentrator"
    cco_mac_addr = '00-00-00-00-00-9E'  # type: str

    cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1)

    plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
    tc_common.set_cco_mac_addr(cct, cco_mac_addr)
    cct.mac_addr = cco_mac_addr

    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(cct)

    #set sub node address
    plc_tb_ctrl._debug("set sub node address to consorting cco, and start the escort net")

    # set sub node address
    plc_tb_ctrl._debug("set sub node address to main cco, and start the main net")
    f = open(node_addr_list_file,'r')
    addr_list = f.readlines()
    nw_top_main = { cco_mac_addr : 0}
    for l in addr_list:
        # key is meter address, value is level
        key, value = l.split(':')
        nw_top_main[key] = int(value.strip())
    f.close()
    sec_nodes_addr_list = []
    for meter_addr, level in nw_top_main.iteritems():
        if (level > 0):
            sec_nodes_addr_list.append(meter_addr)
    plc_tb_ctrl._debug(sec_nodes_addr_list)
    tc_common.add_sub_node_addr(cct, sec_nodes_addr_list)

    tc_common.check_nw_top(cct, nw_top_main, 800)

    r_band = tc_common.read_cco_band(cct)
    plc_tb_ctrl._debug("default Band: " + str(r_band))

    if  r_band != band:
        tc_common.write_cco_band(cct, band)
        plc_tb_ctrl._debug("wait for cco switch band")
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






