# -- coding: utf-8 --
import plc_tb_ctrl
import concentrator
import tc_common
import cco_switch_band
import config

'''
4.1 全网组网测试
验证多 STA 站点时组网准确性和效率
'''

def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    node_addr_list_file = u'tc/tc_iot_4/互操作性表架拓扑地址_完整版_树形.txt'
    band = int(band)
    if  band != config.DEFAULT_BAND:
        cco_switch_band.run(tb, tb.cct, band, node_addr_list_file)

    tb.meter_platform_power_reset()

    cco_mac_addr = '00-00-00-00-00-9C'  # type: str
    # cct_other = concentrator.Concentrator(config.CONCENTRATOR_OTHER_PORT)
    # cct_other.open_port()
    # cco_mac_addr_other = '00-00-00-00-00-9D'  # type: str

    gdw1376p2_frame = tb.cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1)

    plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
    tc_common.set_cco_mac_addr(tb.cct, cco_mac_addr)
    tb.cct.mac_addr = cco_mac_addr
    # plc_tb_ctrl._debug("set other CCO addr={}".format(cco_mac_addr_other))
    # tc_common.set_cco_mac_addr(cct_other, cco_mac_addr_other)

    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(tb.cct)

    # plc_tb_ctrl._debug("reset other CCO param area")
    # tc_common.reset_cco_param_area(cct_other)

    #set sub node address
    plc_tb_ctrl._debug("set sub node address to consorting cco, and start the escort net")

    # 启动陪测CCO和STA组网
    # f = open('./互操作性表架拓扑地址_陪测.txt', 'r')
    # addr_list = f.readline()
    # nw_top_other = {cco_mac_addr_other: 0}
    # for l in addr_list:
    #     # key is meter address, value is level
    #     key, value = l.split(':')
    #     nw_top_other[key] = int(value.strip())
    # f.close()
    # sec_nodes_addr_list = []
    # for meter_addr, level in nw_top_other.iteritems():
    #     if (level > 0):
    #         sec_nodes_addr_list.append(meter_addr)
    # plc_tb_ctrl._debug(sec_nodes_addr_list)
    # tc_common.add_sub_node_addr(cct, sec_nodes_addr_list)

    # set sub node address
    plc_tb_ctrl._debug("set sub node address to main cco, and start the main net")
    f = open(node_addr_list_file, 'r')
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
    tc_common.add_sub_node_addr(tb.cct, sec_nodes_addr_list)

    tc_common.check_nw_top(tb.cct, nw_top_main, 3600)










